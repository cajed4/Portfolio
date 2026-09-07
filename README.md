# Amare Johnson — Portfolio

Computer Science student (University of Detroit Mercy) and builder who works across full-stack
web development, applied AI/data work, and quantitative trading systems. This repo collects the
projects that best show how I think and build, from a from-scratch algorithmic trading system to
data-structures coursework.

## About

- Junior, Computer Science, University of Detroit Mercy
- AI Data Annotation Contractor at Handshake AI — evaluating and labeling model outputs
  (rubric-based grading, video/text annotation) for training data quality
- Founder, AJ's Vending — running a small vending machine business since 2022
- 8+ years of hands-on PC hardware experience
- Comfortable across C++, JavaScript/Node.js/Express, SQL/PostgreSQL, React, and Python

## Projects

### Trading & Quantitative Systems

**[Algorithmic Trading System](./algorithmic-trading-system)**
A key-levels + volume-profile trading system for NQ/GC futures, built algorithmic-first with a
discretionary overlay for futures prop-firm evaluations. Includes a Databento-backed data
pipeline with a partitioned Parquet lake, key-level and volume-profile analytics, a rejection/
sweep/acceptance reaction-study engine, an event-driven backtester, and unit tests.
**Stack:** Python, Parquet, Databento API, pytest.

### Software Engineering / Data Structures

**[Theater Seat Scheduler](./theater-seat-scheduler)**
A seating-management system for a multi-class theater (regular + priority seating), built around
a custom stack for seat allocation and queues for waitlisting. Clean multi-file OOP design across
`Seats`, `SeatAssignment`, and `SeatScheduler`.
**Stack:** C++17, CMake.

**[ASCII Dungeon Game](./ascii-dungeon-game)**
A grid-based terminal dungeon crawler: procedurally placed monsters and items, an independently
moving pursuing enemy with its own AI cooldowns, and a full turn-based game loop with win/lose
conditions.
**Stack:** C++20, CMake.

---

More projects — a TradingView Pine Script indicator (KLSR: key-level sweep & rejection
detection) and a food-bank website redesign from a research co-op — are being added next.

## Contact

- Email: cajed4@gmail.com
- GitHub: this profile

## License

Code in this repository is available under the [MIT License](./LICENSE) unless a project's own
subfolder states otherwise.
