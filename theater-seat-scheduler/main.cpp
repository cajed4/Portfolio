//
// Created by Owner on 10/12/25.
// Main program for theater seating management
//

#include <fstream>
#include <iostream>
#include <string>
#include <limits>
#include "SeatScheduler.h"

int main() {
    SeatScheduler scheduler(5, 2);  // 5 regular, 2 avenger seats

    scheduler.enterCustomer("Alice");
    scheduler.enterCustomer("Bob");
    scheduler.enterCustomer("Charlie");
    scheduler.enterCustomer("Avenger_Diana*");

    scheduler.report();  // Print the report

    scheduler.exitCustomer("Alice");

    scheduler.report();  // Print updated report

    return 0;
}
