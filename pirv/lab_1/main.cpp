//
// Created by katerina on 9/25/23.
//

#include <iostream>
#include <fstream>

#include "src/matrix.h"
#include "src/timer.h"


auto make_test(int n1, int n2, const LaunchMode& launch_mode, int block_size = 1) {
   Matrix A = Matrix(n1, n1);
   Matrix B = Matrix(n2, n2);

   Timer timer = Timer();
   timer.start();
   if ((block_size == 1) || (block_size == n1)) {
       A.linearMultiply(B, launch_mode);
   } else {
       A.blockMultiply(B, block_size, launch_mode);
   }
   auto time = timer.getElapsedTime();
   return time;
}

int main() {
    std::vector<int> sizes({200, 500, 1500});
    std::vector<int> block_sizes({1, 2, 5, 10, 15, 20, 50, 100, 200, 500});

    std::ofstream output_file("sequence_report.txt");

    for (auto& n: sizes) {
        for (auto& r: block_sizes) {
            auto time = make_test(n, n, LaunchMode::kSequential, r);
            output_file << n << ' ' << r << ' ' << time << std::endl;
        }
    }

    std::ofstream output_file_2("parallel_inner_report.txt");

    for (auto& n: sizes) {
        for (auto& r: block_sizes) {
            auto time = make_test(n, n, LaunchMode::kParallelInner, r);
            output_file_2 << n << ' ' << r << ' ' << time << std::endl;
        }
    }

    std::ofstream output_file_3("parallel_outer_report.txt");

    for (auto& n: sizes) {
        for (auto& r: block_sizes) {
            auto time = make_test(n, n, LaunchMode::kParallelOuter, r);
            output_file_3 << n << ' ' << r << ' ' << time << std::endl;
        }
    }
    return 0;
}