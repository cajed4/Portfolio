# Prop Trading System — ES / NQ / GC

A key-levels + volume trading system, built algorithmic-first with a discretionary overlay,
targeting futures prop-firm evaluations (Topstep/Apex/TPT-style, via Tradovate/Rithmic/ProjectX)
now, with a path to live trading later.

## Scope (locked in for phase 1)

- **Instruments:** NQ (Nasdaq 100), GC (Gold) — and their micros (MNQ, MGC) for evaluation-
  account position sizing. (ES was in the original scope; dropped — see `docs/strategy_framework.md`.)
- **Core edge:** key levels (prior session/day/week high-low, VWAP, session opens) combined with
  volume behavior (volume profile POC/VAH/VAL, high-volume nodes, volume climax/exhaustion) —
  computed algorithmically, used both to drive automated signals and to inform discretionary
  trade decisions.
- **Path:** data pipeline → analytics (key levels + volume) → backtesting → paper/sim →
  prop-firm eval (algo assist + discretionary) → live.

## Why this architecture

Everything downstream (backtests, live signals, discretionary charts) depends on having clean,
consistent historical + real-time bar/tick data for NQ and GC. So phase 1 is entirely the
data pipeline: pull historical data, normalize it into one schema, store it efficiently, and
build the ingestion path so real-time can be swapped in later without changing anything upstream.

## Data vendor strategy

Futures data vendors split into two jobs — **historical backfill** and **live streaming** — and
we don't need to pay for both on day one:

| Stage | Recommendation | Why |
|---|---|---|
| Historical backfill (now) | [Databento](https://databento.com) `GLBX.MDP3` (CME Globex), pay-as-you-go historical | No monthly commitment; buy exactly the ES/NQ/GC date ranges needed to build and validate the key-level/volume logic. Clean, point-in-time-correct data, official CME feed. |
| Live data (later, once strategy is validated) | Databento Standard plan (~$179/mo) **or** whatever data your prop firm's platform provides (Tradovate/Rithmic/ProjectX) | Live CME pay-as-you-go was discontinued industry-wide, so live data is a subscription regardless of vendor. If your funded/eval account's platform already includes usable real-time data, that can replace a separate live subscription. |
| Execution (live, later) | Rithmic (via your prop firm) or Tradovate API | Most futures prop firms (Topstep/TopstepX, Apex, Alpha Futures, TPT, MyFundedFutures, Tradeify, etc.) route automation through Tradovate, Rithmic, or ProjectX. Confirm each firm's current automation rules before connecting a bot — most restrict fully-autonomous HFT/tick-scalping/martingale, not swing-style key-level automation. |

This means: build and validate everything against Databento historical data now (cheap, no
recurring cost); only pay for a live feed once the key-level/volume logic actually backtests
well and you're ready for sim/eval trading.

## Directory layout

```
data_pipeline/
  ingest/       # pulls raw data from a provider (Databento first; Rithmic/Tradovate later)
  transform/    # normalizes raw provider data into the canonical bar/tick schema
  storage/      # reads/writes the canonical Parquet data lake
analytics/       # key-level detection + volume profile computation (the algorithmic core)
backtest/         # event-driven backtester that consumes analytics signals
strategy/         # signal/rule definitions (algo + discretionary-assist) and prop-firm risk rules
execution/         # broker/execution adapters (stubbed until sim/live phase)
config/            # instrument specs, prop-firm rule presets, vendor credentials (.env, gitignored)
notebooks/         # exploratory analysis
tests/             # unit tests
```

## Status

Phase 1 (data pipeline) scaffolded:
- [x] Project structure
- [x] Canonical bar schema
- [x] Databento historical ingest script (needs your API key)
- [x] Parquet-based storage layer (partitioned by symbol/date)
- [ ] Pull first real NQ/GC historical dataset and validate

Phase 2 (key-level & volume analytics) in progress:
- [x] Key levels (prior day/week high-low, session open, 06:00/10:00/14:00 ET anchor opens)
- [x] Volume profile (POC, VAH/VAL, HVN/LVN)
- [x] Rejection block detection
- [x] Reaction/outcome study engine (rejection vs. sweep vs. acceptance vs. inconclusive) with a
  per-level-type summary — `backtest/run_reaction_study.py`. Try it now on synthetic data with
  `python -m scripts.demo_reaction_study`; running it for real needs Phase 1's historical data.
- [ ] Volume Cumulation, absorption, options-derived (GEX) levels — need data sources not yet
  wired up (see `docs/strategy_framework.md` §9)
- [ ] Zone clustering for stacked levels

See `docs/roadmap.md` for the full phased plan and `docs/strategy_framework.md` for the trading
logic this analytics layer implements.
