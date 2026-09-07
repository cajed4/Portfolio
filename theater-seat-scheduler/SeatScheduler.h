//
// Created by Owner on 10/13/25.
//

#ifndef SEAT_SCHEDULER_H
#define SEAT_SCHEDULER_H

#include <string>
#include <queue>
#include <vector>
#include "Seats.h"
#include "SeatAssignment.h"

class SeatScheduler {
public:
    SeatScheduler(int numRegular, int numAvenger);

    void enterCustomer(const std::string& name);
    void exitCustomer(const std::string& name);
    void report() const;

private:
    int totalRegular_;
    int totalAvenger_;
    ChairStack regularSeats_;
    ChairStack avengerSeats_;
    std::queue<std::string> regularQueue_;
    std::queue<std::string> avengerQueue_;
    std::vector<SeatAssignment> seated_;

    bool isAvengerName(const std::string& name) const;
    void assignSeatTo(const std::string& name, int seat);
};  // <-- DON'T FORGET THIS SEMICOLON!

#endif // SEAT_SCHEDULER_H
