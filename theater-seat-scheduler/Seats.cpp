//
// Created by Owner on 10/12/25.
//

#include "Seats.h"
#include <stdexcept>

ChairStack::ChairStack(int capacity) : maxCapacity(capacity) {
    if (capacity < 0) throw std::invalid_argument("Capacity must be non-negative");
    chairs.reserve(capacity);
}

ChairStack::~ChairStack() = default;

void ChairStack::push(int chair) {
    if ((int)chairs.size() >= maxCapacity)
        throw std::runtime_error("ChairStack::push - stack full");
    chairs.push_back(chair);
}

int ChairStack::pop() {
    if (chairs.empty()) throw std::runtime_error("ChairStack::pop - stack empty");
    int topChair = chairs.back();
    chairs.pop_back();
    return topChair;
}

int ChairStack::top() const {
    if (chairs.empty()) throw std::runtime_error("ChairStack::top - stack empty");
    return chairs.back();
}

bool ChairStack::isEmpty() const {
    return chairs.empty();
}
