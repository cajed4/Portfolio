# MES Replay Backtester

A Python backtesting engine for futures trading strategies, built around a clean, replaceable-layer architecture: a data feed, a strategy, and a replay/execution engine, each hidden behind a small contract so any one piece can be swapped without touching the others.

## What it does

- Pulls historical MES (Micro E-mini S&P 500) 5-minute bars from Yahoo Finance, or generates synthetic seeded random-walk data for pipeline testing without network access
- Walks through bars one at a time with **no lookahead** — the strategy only ever sees the past and present, never the future, so results can't be accidentally curve-fit
- Simulates paper trades: entries, stop/target exits, and a conservative "stop hit first" assumption when a single bar touches both
- Enforces real trading-plan risk rules in code rather than relying on discipline: only one open position at a time, a 15-minute cooldown after a loss (anti-revenge-trading), and entries restricted to defined session windows (NY Open 9:30–11:30 AM ET, Tokyo 7:00–11:00 PM ET)
- Reports trade count, win rate, net P&L (points and dollars), average win/loss, and a per-session breakdown

## Architecture

```
 data_feed.py          replay.py               strategy.py
┌─────────────┐   ┌───────────────────┐   ┌─────────────────┐
│ YFinanceFeed │──▶│   ReplayEngine    │──▶│   ICCStrategy   │
│ SyntheticFeed│   │  (bar-by-bar loop │◀──│ evaluate(bars)  │
└─────────────┘   │  + paper trading) │   │ returns Signal  │
     bars          └───────────────────┘   └─────────────────┘
                            │
                            ▼
                     report() → stats
```

- **`data_feed.py`** — answers "what did the market do?" Exposes a `DataFeed` base class with a single `get_bars()` contract, implemented by `YFinanceFeed` (live delayed data, with a 12-hour CSV cache) and `SyntheticFeed` (deterministic fake data for testing).
- **`strategy.py`** — answers "should a trade be taken right now?" `ICCStrategy.evaluate()` implements a placeholder Indication → Correction → Continuation pattern (a strong directional bar, a pullback that respects its extreme, then a close beyond it), returning a `Signal` dataclass or `None`.
- **`replay.py`** — the engine. Walks bars in order, manages open positions, applies the session/cooldown/single-position risk rules, and builds the trade log.
- **`main.py`** — wires the three layers together (~30 lines) and prints the final report.

See [architecture.md](./architecture.md) for the full design writeup, including the growth path (porting real strategy rules, parameter sweeps, upgrading to a live broker feed).

## Usage

```bash
python main.py              # real MES data from Yahoo (needs internet)
python main.py --synthetic  # synthetic data, for testing the pipeline
```

## Tech

Python, pandas, yfinance

## Status

The engine, risk-rule enforcement, and reporting are complete; `ICCStrategy` currently runs placeholder pattern logic pending the full strategy rules.
