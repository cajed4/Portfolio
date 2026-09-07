# Theater Seat Scheduler

A C++ seating-management system built for a data structures course: checks customers into a
theater with two seat classes (regular and priority "Avenger" seating), assigns/releases seats,
and reports live occupancy.

## What it demonstrates

- Custom stack (`ChairStack`) used as the seat-allocation pool for each seating class
- Queues for waitlisting customers when a class is full
- Multi-file C++ design: `Seats`, `SeatAssignment`, and `SeatScheduler` each own a single
  responsibility, composed together in `main.cpp`
- Clean check-in/check-out flow with reporting

## Build & run

Requires a C++17 compiler and CMake.

```bash
cmake -S . -B build
cmake --build build
./build/HW3
```

## Tech

C++17, standard library only (`<queue>`, `<vector>`) — no external dependencies.
