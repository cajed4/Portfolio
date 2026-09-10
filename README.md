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

**[MES Replay Backtester](./mes-replay-backtester)**
A Python backtesting engine for futures strategies with a clean, replaceable-layer architecture —
a data feed, a strategy, and a bar-by-bar replay/execution engine, each hidden behind a small
contract. Enforces real risk rules in code (no-lookahead simulation, single-position limit,
post-loss cooldown, session-window entries) rather than relying on discipline.
**Stack:** Python, pandas, yfinance.

**[KLSR — Key Level Sweep & Rejection](./klsr-key-level-sweep-rejection)**
A TradingView indicator tracking 39 key market levels (session, daily/weekly/monthly/quarterly/
yearly opens and ranges) and flagging sweep vs. rejection reactions at each one, with bar-window
clustering to merge repeated reactions at the same level.
**Stack:** Pine Script v6.

### Web Development

**[TCV Food Bank Redesign](./tcv-food-bank-redesign)**
A front-end redesign mockup for a food bank's public website, built during a research co-op to
improve accessibility and mobile responsiveness — semantic ARIA-labeled markup, a responsive
hamburger nav, and a full page of service sections.
**Stack:** HTML5, CSS3.

**[Shopping Cart API](./shopping-cart-api)**
A REST API for a shopping cart system backed by a serverless Postgres database, using
parameterized tagged-template SQL for safety.
**Stack:** Node.js, Express 5, PostgreSQL (Neon).

**[Stocks Portfolio App](./stocks-portfolio-app)**
A framework-free single-page app for browsing users and their stock portfolios, built entirely
with vanilla DOM APIs.
**Stack:** HTML5, CSS3, JavaScript (ES6+).

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

## Contact
- Email: cajed4@gmail.com

## License

Code in this repository is available under the [MIT License](./LICENSE) unless a project's own
subfolder states otherwise.
