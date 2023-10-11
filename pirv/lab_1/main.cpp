//
// Created by katerina on 9/25/23.
//

#include <iostream>

#include "src/matrix.h"
#include "src/timer.h"


void make_test(int n1, int n2, const LaunchMode& launch_mode, int block_size = 1) {
   Matrix A = Matrix(n1, n1);
   Matrix B = Matrix(n2, n2);

   Timer timer = Timer();
   timer.start();
   if (block_size == 1) {
       A.linearMultiply(B, launch_mode);
   } else {
       A.blockMultiply(B, block_size, launch_mode);
   }
   timer.getElapsedTime();

}

int main() {
    Matrix A(2, 2, {{1, 2}, {3, 4}});
    Matrix B(2, 2, {{2, 0}, {1, 2}});
    Matrix result = A.linearMultiply(B, LaunchMode::kSequential);
    result.printMatrix();
    Matrix expected(2, 2, {{4, 4}, {10, 8}});
    expected.printMatrix();

    return 0;
}