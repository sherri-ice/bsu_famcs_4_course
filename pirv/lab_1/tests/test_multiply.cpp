#include <gtest/gtest.h>
#include "../src/matrix.h"
#include "../src/timer.h"

TEST(MatrixMultiplication, LinearMultiply) {
    // Test case 1: 2x2 matrices
    Matrix A(2, 2, {{1, 2}, {3, 4}});
    Matrix B(2, 2, {{2, 0}, {1, 2}});
    Matrix result = A.linearMultiply(B, LaunchMode::kSequential);
    Matrix expected(2, 2, {{4, 4}, {10, 8}});
    EXPECT_EQ(result.getMatrix(), expected.getMatrix());

    // Test case 2: 3x3 matrices with parallel outer
    Matrix C(3, 3, {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}});
    Matrix D(3, 3, {{9, 8, 7}, {6, 5, 4}, {3, 2, 1}});
    Matrix result2 = C.linearMultiply(D, LaunchMode::kParallelInner);
    Matrix expected2(3, 3, {{30, 24, 18}, {84, 69, 54}, {138, 114, 90}});
    EXPECT_EQ(result2.getMatrix(), expected2.getMatrix());
}

TEST(MatrixMultiplication, BlockMultiply) {
    // Test case 1: 2x2 matrices with block size 2
    Matrix A(2, 2, {{1, 2}, {3, 4}});
    Matrix B(2, 2, {{2, 0}, {1, 2}});
    Matrix result = A.blockMultiply(B, 2, LaunchMode::kSequential);
    Matrix expected(2, 2, {{4, 4}, {10, 8}});
    EXPECT_EQ(result.getMatrix(), expected.getMatrix());

    // Test case 2: 3x3 matrices with block size 1 and parallel inner
    Matrix C(3, 3, {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}});
    Matrix D(3, 3, {{9, 8, 7}, {6, 5, 4}, {3, 2, 1}});
    Matrix result2 = C.blockMultiply(D, 1, LaunchMode::kParallelInner);
    Matrix expected2(3, 3, {{30, 24, 18}, {84, 69, 54}, {138, 114, 90}});
    EXPECT_EQ(result2.getMatrix(), expected2.getMatrix());
}