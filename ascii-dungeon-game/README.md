# ASCII Dungeon Game

A single-file C++ terminal game built for a university AI/Data Structures course assignment.
Renders a grid-based dungeon crawler in the terminal: procedurally placed monsters, save points,
a resource-collection loop, and a pursuing enemy with independent movement/attack cooldowns.

## What it demonstrates

- Object-oriented design (a `Game` class encapsulating state, rendering, and turn logic)
- 2D grid simulation and coordinate/collision handling (`Position`, bounds checks, pathing)
- Independent entity AI (a chasing enemy with separate move/attack cooldown timers)
- Procedural placement of monsters, items, and save points on a grid
- Turn-based game loop with win/lose conditions and persistent stats (HP, gold, determination)

## Build & run

Requires a C++20 compiler and CMake.

```bash
cmake -S . -B build
cmake --build build
./build/AI_TextBasedAdventuregame_HW_Final
```

## Tech

C++20, standard library only (`<vector>`, `<queue>`, `<algorithm>`) — no external dependencies.
