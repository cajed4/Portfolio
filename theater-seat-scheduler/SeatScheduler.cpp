//
// Created by Owner on 10/14/25.

#include "SeatScheduler.h"
#include <iostream>
#include <algorithm>

SeatScheduler::SeatScheduler(int numRegular, int numAvenger)
    : totalRegular_(numRegular),
      totalAvenger_(numAvenger),
      regularSeats_(numRegular),
      avengerSeats_(numAvenger)
{
    // Push regular seats so 1 is on top
    for (int i = numRegular; i >= 1; --i) regularSeats_.push(i);
    // Push avenger seats so top is first seat number after regular seats
    for (int i = numRegular + numAvenger; i > numRegular; --i) avengerSeats_.push(i);
}

// Found npos on google: it's a static member constant value
// with the greatest possible value for an element, which ai helped me figure out.
bool SeatScheduler::isAvengerName(const std::string& name) const {
    return name.find('*') != std::string::npos;


}

void SeatScheduler::assignSeatTo(const std::string& name, int seat) {
    seated_.push_back(SeatAssignment(name, seat));
}


void SeatScheduler::enterCustomer(const std::string& name) {
    bool isAvenger = isAvengerName(name);

    if (isAvenger) {
        // Try to assign avenger seat
        if (!avengerSeats_.isEmpty()) {
            int seat = avengerSeats_.pop();
            assignSeatTo(name, seat);
        } else {
            // Add to avenger queue
            avengerQueue_.push(name);
        }
    } else {
        // Try to assign regular seat
        if (!regularSeats_.isEmpty()) {
            int seat = regularSeats_.pop();
            assignSeatTo(name, seat);
        } else {
            // Add to regular queue
            regularQueue_.push(name);
        }
    }
}


void SeatScheduler::exitCustomer(const std::string& name) {
    // Find the customer in the seated vector
    auto it = std::find_if(seated_.begin(), seated_.end(),
        [&](const SeatAssignment& s){ return s.getName() == name; });

    if (it == seated_.end()) return; // Customer not found

    int freedSeat = it->getSeatNumber();
    seated_.erase(it); // Remove customer from seated vector
    bool freedIsRegular = (freedSeat <= totalRegular_);

    // Assign seat based on priority
    if (freedIsRegular) {
        if (!avengerQueue_.empty()) {
            // Avengers waiting have highest priority
            assignSeatTo(avengerQueue_.front(), freedSeat);
            avengerQueue_.pop();
        } else if (!regularQueue_.empty()) {
            // Then assign to regular queue
            assignSeatTo(regularQueue_.front(), freedSeat);
            regularQueue_.pop();
        } else {
            // No one waiting, push back to regular seats stack
            regularSeats_.push(freedSeat);
        }
    } else { // Freed seat is an Avenger seat
        if (!avengerQueue_.empty()) {
            assignSeatTo(avengerQueue_.front(), freedSeat);
            avengerQueue_.pop();
        } else {
            // Only push back to Avenger stack if no Avengers waiting
            avengerSeats_.push(freedSeat);
        }
    }
}
void SeatScheduler::report() const {
    std::cout << "SHAWARMA SEATING REPORT\n";

    // Print seated customers
    for (const auto& s : seated_) {
        std::cout << s.getName() << " is sitting at seat #"
                  << s.getSeatNumber() << "\n";
    }

    std::cout << "AVAILABLE SEATS\n";

    // Print regular seats
    std::cout << "REGULAR SEATS\n";
    if (regularSeats_.isEmpty()) {
        std::cout << "No seats available.\n";
    } else {
        ChairStack temp = regularSeats_;
        std::vector<int> seats;
        while (!temp.isEmpty()) {
            seats.push_back(temp.pop());
        }
        // Print in reverse order (bottom to top)
        for (auto it = seats.rbegin(); it != seats.rend(); ++it) {
            std::cout << *it << "\n";
        }
    }
// I found rend under a template: which is typically an iterator one past the reverse-end of the sequence
    // I used it above to reverse the seats in the statement

    // Print avenger seats
    std::cout << "AVENGER SEATS\n";
    if (avengerSeats_.isEmpty()) {
        std::cout << "No seats available.\n";
    } else {
        ChairStack temp = avengerSeats_;
        std::vector<int> seats;
        while (!temp.isEmpty()) {
            seats.push_back(temp.pop());
        }
        // Print in reverse order (bottom to top)
        for (auto it = seats.rbegin(); it != seats.rend(); ++it) {
            std::cout << *it << "\n";
        }
    }

    std::cout << "QUEUE STATUS\n";

    // Print regular queue
    std::cout << "REGULAR QUEUE\n";
    if (regularQueue_.empty()) {
        std::cout << "There is no one waiting...\n";
    } else {
        std::queue<std::string> temp = regularQueue_;
        while (!temp.empty()) {
            std::cout << temp.front() << "\n";
            temp.pop();
        }
    }

    // Print avenger queue
    std::cout << "AVENGER QUEUE\n";
    if (avengerQueue_.empty()) {
        std::cout << "There is no one waiting...\n";
    } else {
        std::queue<std::string> temp = avengerQueue_;
        while (!temp.empty()) {
            std::cout << temp.front() << "\n";
            temp.pop();
        }
    }

    std::cout << "----------------------------------\n";
}

