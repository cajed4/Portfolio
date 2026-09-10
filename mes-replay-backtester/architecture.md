# MES Replay System — Architecture

## Overview

The MES Replay System is a Python program that tests the ICC (Indication, Correction, Continuation) trading strategy against historical market data as if that data were arriving live. It simulates the full lifecycle of a trading session: fetching candles, evaluating each new bar for a setup, entering paper trades, managing stops and targets, enforcing risk rules, and reporting results. The design goal is that each concern lives in its own module, so any single piece — most importantly the data source and the strategy logic — can be replaced without rewriting the rest of the program.

The program is organized into four modules. `data_feed.py` is responsible for producing candles. `strategy.py` decides when a trade should be taken. `replay.py` simulates the passage of time and the execution of trades. `main.py` wires the three together and runs the show. Data flows in one direction through these layers: the feed produces bars, the engine walks through them and hands slices to the strategy, the strategy returns signals, and the engine converts signals into simulated trades and finally into a performance report.

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

## The data layer (`data_feed.py`)

The data layer answers exactly one question: what did the market do? It exposes a base class, `DataFeed`, whose single method `get_bars()` returns a pandas DataFrame of OHLCV candles indexed by a timezone-aware timestamp in US/Eastern. This base class plays the role that an interface would play in TypeScript: it defines the contract that every concrete feed must honor, and it raises `NotImplementedError` if a subclass forgets to implement it.

Two concrete feeds exist today. `YFinanceFeed` downloads delayed MES data (`MES=F`) from Yahoo Finance and normalizes it: it flattens Yahoo's occasional MultiIndex columns, keeps only the Open, High, Low, Close, and Volume columns, and converts the index to Eastern time so that session logic downstream can reason about market hours directly. It also caches every download to a CSV file in `data_cache/` and reuses that file for up to twelve hours, which makes repeated backtest runs instant and avoids hammering Yahoo's servers. `SyntheticFeed` generates a seeded random walk with realistic MES-like volatility. It exists purely so the rest of the pipeline can be tested without an internet connection, and so that bugs in the engine can be separated from surprises in real data.

Because the contract is just "return a properly shaped DataFrame," upgrading to a professional data source later — Databento for official CME data, or a broker API like Interactive Brokers for true real-time bars — means writing one new subclass and changing one line in `main.py`. Nothing else in the program knows or cares where candles come from.

## The strategy layer (`strategy.py`)

The strategy layer answers a different question: given everything the market has done up to this moment, should a trade be taken right now? It defines two things. The first is `Signal`, a dataclass that acts as the message passed from strategy to engine. A signal carries a direction (LONG or SHORT), an entry price, a stop price, a target price, and a human-readable reason string that ends up in the trade log. Using a dataclass here — Python's equivalent of a typed object literal in JavaScript — means the constructor, string representation, and equality checks all come for free.

The second is `ICCStrategy`, whose `evaluate()` method receives a DataFrame of bars and returns either a `Signal` or `None`. The current implementation is a deliberate placeholder: it looks at the last four candles for a strong indication bar, a corrective pullback that respects the indication bar's extreme, and a continuation close beyond it. Stops are fixed at 10 points per the trading plan, and targets default to two times the risk. This placeholder is meant to be replaced by the real Phase 1 ICC rules; the only thing that must be preserved is the contract itself — bars in, signal or nothing out. As long as that holds, the strategy can grow arbitrarily sophisticated (multi-timeframe confirmation, session-specific parameters, volatility filters) without the engine changing at all.

## The engine layer (`replay.py`)

The engine is the heart of the system. `ReplayEngine.run()` walks through the historical bars one index at a time, and on each bar it does two things in a fixed order. First, if a position is open, it checks whether that bar's high or low touched the stop or the target and exits accordingly. Second, if no position is open and trading is currently allowed, it slices the DataFrame up to and including the current bar and hands that slice to the strategy.

That slice — `bars.iloc[:i + 1]` — is the single most important line in the program. It guarantees the strategy can only ever see the past and the present, never the future. This is what separates an honest replay from an accidentally curve-fit one: a strategy that peeks even one bar ahead will produce beautiful, meaningless results. The engine also makes a conservative assumption when a single bar touches both the stop and the target: it assumes the stop was hit first. Real intrabar sequencing is unknowable from OHLC data alone, so the engine deliberately errs against the strategy rather than for it.

The engine also encodes the risk rules from the trading plan directly, so they cannot be forgotten or bypassed. Only one position may be open at a time. After any losing trade, a 15-minute cooldown timestamp is set, and no new entries are evaluated until it expires — the anti-revenge-trading rule, enforced in code rather than by willpower. Entries are only permitted inside defined session windows, represented by the `Session` dataclass, which knows how to test whether a timestamp falls inside its window, including windows that cross midnight. Two sessions are configured to match the live trading plan: NY Open from 9:30 to 11:30 AM Eastern, and Tokyo from 7:00 to 11:00 PM Eastern.

Every completed trade is recorded as a `Trade` dataclass carrying its direction, entry and exit times and prices, point and dollar P&L (at $5 per point per MES contract), and outcome. When the replay ends, any position still open is force-closed at the last price so results are always computed flat. The `report()` function then aggregates the trade list into a summary: trade count, win rate, net P&L in points and dollars, average win and loss, and a per-session breakdown that reveals whether the strategy behaves differently during NY Open versus Tokyo hours.

## The composition layer (`main.py`)

The entry point is intentionally thin — about thirty lines. It selects a feed (synthetic if the `--synthetic` flag is passed, Yahoo otherwise), requests bars, constructs a `ReplayEngine` with an `ICCStrategy`, runs the replay, and prints the report. Its brevity is the proof that the architecture works: because each layer hides its complexity behind a small contract, composing them takes almost no code. It is also the only file that knows about all three layers at once, which makes it the natural place to later add configuration such as command-line parameters for interval, period, contract count, or session selection.

## Design principles and growth path

Three principles run through the whole design. Separation of concerns means the feed knows nothing about trading, the strategy knows nothing about execution, and the engine knows nothing about ICC — each module can be understood, tested, and replaced in isolation. Honest simulation means the no-lookahead slice and the stop-first assumption are structural guarantees, not conventions. Rules as code means the cooldown, session filters, and single-position constraint are enforced by the engine itself, mirroring the discipline of the live trading plan.

The intended growth path follows the layers. Porting the real Phase 1 ICC logic touches only `strategy.py`. Adding a parameter sweep — testing many indication thresholds or reward-to-risk ratios in one run — wraps the engine in a loop inside `main.py`. Upgrading from delayed Yahoo data to Databento or a live broker feed touches only `data_feed.py`. And because a live feed satisfies the same `get_bars()` contract as a historical one, the eventual jump from replaying the past to forward-testing in real time is an extension of this architecture rather than a rewrite of it.
