//
// Created by user on 9/25/23.
//

#include <cstdlib>
#include <ctime>
#include <iostream>
#include <random>
#include "matrix.h"

// A function to return a seeded random number generator.
inline std::mt19937 &generator() {
    // the generator will only be seeded once (per thread) since it's static
    static thread_local std::mt19937 gen(std::random_device{}());
    return gen;
}

template<typename T, std::enable_if_t<std::is_integral_v<T>> * = nullptr>
T my_rand(T min, T max) {
    std::uniform_int_distribution<T> dist(min, max);
    return dist(generator());
}


Matrix::Matrix(int n, int m) : _n(n), _m(m) {
    _matrix = std::vector<int>(_n * _m, 0);
}

Matrix::~Matrix() = default;

int Matrix::getN() const {
    return _n;
}

int Matrix::getM() const {
    return _m;
}

void Matrix::fillMatrixWithRandom() {
    for (int i = 0; i < _n; ++i) {
        for (int j = 0; j < _m; ++j) {
            _matrix[i * _m + j] = my_rand(_random_start, _random_end);
        }
    }
}

void Matrix::printMatrix() const {
    std::cout << "Matrix: " << std::endl;
    for (int i = 0; i < _n; ++i) {
        for (int j = 0; j < _m; ++j) {
            std::cout << _matrix[i * _m + j] << ' ';
        }
        std::cout << std::endl;
    }
}

Matrix Matrix::linearMultiply(const Matrix &B, const LaunchMode &launch_mode) {
    int n1 = _n;
    int n2 = _m;
    int n3 = B.getM();

    std::vector<int> result(n1 * n3);

#pragma omp parallel for if (launch_mode == LaunchMode::kParallelOuter)
    for (int i = 0; i < n1; i++) {
#pragma omp parallel for if (launch_mode == LaunchMode::kParallelInner)
        for (int j = 0; j < n3; j++) {
            for (int k = 0; k < n2; k++) {
                result[i * n3 + j] += _matrix[i * n2 + k] * B.getMatrix()[i * n3 + j];
            }
        }
    }
    return Matrix(n1, n3, result);
}

Matrix Matrix::blockMultiply(const Matrix &B, int block_size, const LaunchMode &launch_mode) {
    int n = _n;
    int m = _m;
    int p = B.getM();

    std::vector<int> C(n * p, 0);

#pragma omp parallel for if (launch_mode == LaunchMode::kParallelOuter)
    for (int i = 0; i < n; i += block_size) {
#pragma omp parallel for if (launch_mode == LaunchMode::kParallelInner)
        for (int j = 0; j < p; j += block_size) {
            for (int k = 0; k < m; k += block_size) {
                for (int ii = i; ii < std::min(i + block_size, n); ++ii) {
                    for (int jj = j; jj < std::min(j + block_size, p); ++jj) {
                        for (int kk = k; kk < std::min(k + block_size, m); ++kk) {
                            C[ii * p + jj] += _matrix[ii * m + kk] * B.getMatrix()[kk * p + jj];
                        }
                    }
                }
            }
        }
    }
    return Matrix(n, p, C);
}


Matrix::Matrix(int n, int m, const std::vector<std::vector<int>> &matrix) : _n(n), _m(m) {
    _matrix = std::vector<int>(n * m, 0);
    for (int i = 0; i < _n; ++i) {
        for (int j = 0; j < _m; ++j) {
            _matrix[i * _m + j] = matrix[i][j];
        }
    }
}

const std::vector<int> &Matrix::getMatrix() const {
    return _matrix;
}

Matrix::Matrix(int n, int m, const std::vector<int> &matrix) : _n(n), _m(m), _matrix(matrix) {

}

