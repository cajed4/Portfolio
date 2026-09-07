//
// Created by Owner on 10/13/25.
//

#ifndef SEAT_ASSIGNMENT_H
#define SEAT_ASSIGNMENT_H

#include <string>

class SeatAssignment {
public:
    SeatAssignment(const std::string& name, int seatNumber);

    std::string getName() const;
    int getSeatNumber() const;

private:
    std::string customerName_;
    int seatNumber_;
};

#endif // SEAT_ASSIGNMENT_H
