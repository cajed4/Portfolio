//
// Created by Owner on 10/12/25.
//


#ifndef HW3_SEATS_H
#define HW3_SEATS_H

#include <vector>


class ChairStack {
public:
    ChairStack(int capacity);
    ~ChairStack();

    void push(int chair);   // Add a chair to the top
    int pop();              // Remove and return top chair
    int top() const;        // Peek at top chair
    bool isEmpty() const;

private:
    std::vector<int> chairs;
    int maxCapacity;
};

#endif // HW3_SEATS_H
