//
// Created by user on 9/26/23.
//
#include <gtest/gtest.h>
#include "../src/matrix.h"

TEST(CreationTest, CreateFromMatrix) {
    Matrix A = Matrix(3, 3, {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}});
    auto actual = A.getMatrix();
    ASSERT_EQ(actual.size(), 9);

    for (int i = 0; i < actual.size(); ++i) {
        EXPECT_EQ(actual[i], i + 1);
    }

}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}