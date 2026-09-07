//
// Created by Owner on 10/13/25.
//

#include "SeatAssignment.h"

SeatAssignment::SeatAssignment(const std::string& name, int seatNumber)
    : customerName_(name), seatNumber_(seatNumber) {}

std::string SeatAssignment::getName() const {
    return customerName_;
}

int SeatAssignment::getSeatNumber() const {
    return seatNumber_;
}
