//
// Created by user on 9/25/23.
//

#ifndef LAB1_MATRIX_H
#define LAB1_MATRIX_H

#include <vector>

enum LaunchMode {
    kSequential,
    kParallelOuter,
    kParallelInner
};

class Matrix {

private:
    int _n;
    int _m;
    std::vector<int> _matrix;
    int _random_start = -100;
    int _random_end = 100;

public:
    Matrix(int n, int m);

    explicit Matrix(int n,  int m, const std::vector<std::vector<int>>& matrix);

    explicit Matrix(int n,  int m, const std::vector<int>& matrix);

    const std::vector<int> &getMatrix() const;

    void fillMatrixWithRandom();

    int getN() const;

    int getM() const;

    void printMatrix() const;

    Matrix linearMultiply(const Matrix& B, const LaunchMode& launch_mode);

    Matrix blockMultiply(const Matrix& B, int block_size, const LaunchMode& launch_mode);

    virtual ~Matrix();

};


#endif //LAB1_MATRIX_H
