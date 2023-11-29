#include <iostream>
#include <iomanip>
#include <vector>
#include <random>
#include <cmath>
#include <memory>
#include <mpi.h>
#include <algorithm>

void print_matrix(const float* matrix, int dim) {
    for (int i = 0; i < dim; i++) {
        for (int j = 0; j < dim; j++) {
            std::cout << std::setw(10) << matrix[i * dim + j] << " ";
        }
        std::cout << std::endl;
    }
    std::cout << std::endl;
}

std::unique_ptr<float[]> generateDiagonallyDominantMatrix(int dim) {
    std::unique_ptr<float[]> matrix = std::make_unique<float[]>(dim * dim);

    // Filling the matrix with values
    for (int i = 0; i < dim; ++i) {
        for (int j = 0; j < dim; ++j) {
            if (i == j) {
                matrix[i * dim + j] = 100.0;  // Diagonal elements
            }
            else {
                matrix[i * dim + j] = (2.0 * i + j) / 100000.0;
            }
        }
    }

    return matrix;
}

int main(int argc, char* argv[]) {
    // Initialize MPI
    MPI_Init(&argc, &argv);

    // Get the total number of tasks
    int num_tasks = 1;
    MPI_Comm_size(MPI_COMM_WORLD, &num_tasks);

    // Calculate the number of rows mapped to each process
    // Assumes this divides evenly
    const int dim = 256;
    const int n_rows = dim / num_tasks;

    // Get the task ID
    int task_id;
    MPI_Comm_rank(MPI_COMM_WORLD, &task_id);
    const int start_row = task_id * n_rows;
    const int end_row = start_row + n_rows;

    // Matrix - Only initialized in rank 0
    std::unique_ptr<float[]> matrix;

    // Each process will store a chunk of the matrix
    auto m_chunk = std::make_unique<float[]>(dim * n_rows);

    // Each process will receive a pivot row each iteration
    auto pivot_row = std::make_unique<float[]>(dim);

    // Vector b - Only initialized in rank 0
    std::unique_ptr<float[]> b_vector;

    // Each process will store a chunk of the vector b
    auto b_chunk = std::make_unique<float[]>(n_rows);

    // Only rank 0 create/initializes the matrix and vector b
    if (task_id == 0) {
        // Create a random number generator
        std::mt19937 mt(123);
        std::uniform_real_distribution<float> dist(1.0f, 10.0f);

        // Create a matrix
        matrix = generateDiagonallyDominantMatrix(dim);

        // print_matrix(matrix.get(), dim);

        // Create a vector b
        b_vector = std::make_unique<float[]>(dim);
        std::fill(b_vector.get(), b_vector.get() + dim, 1.0f);

        for (int i = 0; i < dim; ++i) {
            std::cout << b_vector[i] << std::endl;
        }
    }

    // Collect start time in rank 0
    double start;
    if (task_id == 0) {
        start = MPI_Wtime();
    }

    // Before doing anything, send parts of the matrix and vector b to each process
    MPI_Scatter(matrix.get(), dim * n_rows, MPI_FLOAT, m_chunk.get(),
        dim * n_rows, MPI_FLOAT, 0, MPI_COMM_WORLD);
    MPI_Scatter(b_vector.get(), n_rows, MPI_FLOAT, b_chunk.get(),
        n_rows, MPI_FLOAT, 0, MPI_COMM_WORLD);

    // Store requests for non-blocking sends
    std::vector<MPI_Request> requests(num_tasks);

    // Perform Gaussian elimination
    for (int row = 0; row < end_row; row++) {
        // See if this process is responsible for the pivot calculation
        auto mapped_rank = row / n_rows;

        // If the row is mapped to this rank...
        if (task_id == mapped_rank) {
            // Calculate the row in the local matrix
            auto local_row = row % n_rows;

            // Get the value of the pivot
            auto pivot = m_chunk[local_row * dim + row];

            // Divide the rest of the row by the pivot
            for (int col = row; col < dim; col++) {
                m_chunk[local_row * dim + col] /= pivot;
            }
            b_chunk[local_row] /= pivot;

            // Send the pivot row and b_chunk to the other processes
            for (int i = mapped_rank + 1; i < num_tasks; i++) {
                MPI_Isend(m_chunk.get() + dim * local_row, dim, MPI_FLOAT, i, 0,
                    MPI_COMM_WORLD, &requests[i]);
                MPI_Isend(b_chunk.get() + local_row, 1, MPI_FLOAT, i, 1,
                    MPI_COMM_WORLD, &requests[i + num_tasks]);
            }

            // Eliminate for the local rows
            for (int elim_row = local_row + 1; elim_row < n_rows; elim_row++) {
                // Get the scaling factor for elimination
                auto scale = m_chunk[elim_row * dim + row];

                // Remove the pivot
                for (int col = row; col < dim; col++) {
                    m_chunk[elim_row * dim + col] -=
                        m_chunk[local_row * dim + col] * scale;
                }
                b_chunk[elim_row] -= b_chunk[local_row] * scale;
            }

            // Check if there are any outstanding messages
            for (int i = mapped_rank + 1; i < num_tasks; i++) {
                MPI_Wait(&requests[i], MPI_STATUS_IGNORE);
                MPI_Wait(&requests[i + num_tasks], MPI_STATUS_IGNORE);
            }
        }
        else {
            // Receive pivot row and b_chunk
            MPI_Recv(pivot_row.get(), dim, MPI_FLOAT, mapped_rank, 0, MPI_COMM_WORLD,
                MPI_STATUS_IGNORE);
            MPI_Recv(b_chunk.get(), n_rows, MPI_FLOAT, mapped_rank, 1, MPI_COMM_WORLD,
                MPI_STATUS_IGNORE);

            // Skip rows that have been fully processed
            for (int elim_row = 0; elim_row < n_rows; elim_row++) {
                // Get the scaling factor for elimination
                auto scale = m_chunk[elim_row * dim + row];

                // Remove the pivot
                for (int col = row; col < dim; col++) {
                    m_chunk[elim_row * dim + col] -= pivot_row[col] * scale;
                    b_chunk[elim_row] -= pivot_row[col] * scale;
                }
            }
        }
    }

    // Gather the final results into rank 0
    MPI_Gather(m_chunk.get(), n_rows * dim, MPI_FLOAT, matrix.get(), n_rows * dim,
        MPI_FLOAT, 0, MPI_COMM_WORLD);
    MPI_Gather(b_chunk.get(), n_rows, MPI_FLOAT, b_vector.get(), n_rows,
        MPI_FLOAT, 0, MPI_COMM_WORLD);

    // Solve for x in Ax = b using back substitution
    if (task_id == 0) {
        for (int row = dim - 1; row >= 0; row--) {
            for (int i = 0; i < num_tasks; i++) {
                if (i != 0) {
                    MPI_Send(matrix.get() + row * dim, dim, MPI_FLOAT, i, 2,
                        MPI_COMM_WORLD);
                }
            }

            for (int i = dim - 1; i > row; i--) {
                b_vector[row] -= matrix[row * dim + i] * b_vector[i];
            }

            for (int i = 1; i < num_tasks; i++) {
                MPI_Recv(b_chunk.get(), n_rows, MPI_FLOAT, i, 2, MPI_COMM_WORLD,
                    MPI_STATUS_IGNORE);
                for (int j = 0; j < n_rows; j++) {
                    b_vector[row] -= matrix[row * dim + start_row + j] * b_chunk[j];
                }
            }
        }

        double end = MPI_Wtime();
        std::cout << "Time: " << end - start << " seconds\n";

        // Print the result
        // print_matrix(matrix.get(), dim);
        std::cout << "Solution x:\n";
        for (int i = 0; i < dim; i++) {
            std::cout << "x[" << i << "] = " << b_vector[i] << std::endl;
        }
        std::cout << "Time: " << end - start << " seconds\n";
    }

    // Finish our MPI work
    MPI_Finalize();

    return 0;
}
