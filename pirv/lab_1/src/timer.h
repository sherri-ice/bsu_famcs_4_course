//
// Created by user on 9/25/23.
//

#ifndef LAB1_TIMER_H
#define LAB1_TIMER_H


class Timer {
private:
    double _start = 0.;

public:
    void start();
    double getElapsedTime() const;

};


#endif //LAB1_TIMER_H
