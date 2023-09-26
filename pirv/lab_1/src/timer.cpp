//
// Created by user on 9/25/23.
//

#include "timer.h"
#include <omp.h>
#include <iostream>

void Timer::start() {
    _start = omp_get_wtime();
}

double Timer::getElapsedTime() const {
    double elapsed_time = omp_get_wtime() - _start;
    std::cout << "Elapsed time: " << elapsed_time << std::endl;
    return omp_get_wtime() - _start;
}
