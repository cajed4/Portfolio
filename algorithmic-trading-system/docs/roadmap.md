# Roadmap

## Phase 1 — Data pipeline (current)
- Canonical schema for OHLCV bars + volume, consistent across instruments and providers.
- Historical ingest from Databento (`GLBX.MDP3`) for NQ, GC (continuous + specific contracts).
- Parquet data lake, partitioned by `symbol/date`, queryable with DuckDB/pandas/polars.
- Data quality checks: session boundaries, contract roll handling, gap detection.

## Phase 2 — Key-level & volume analytics (in progress)
- [x] Key levels: prior day/week high-low, session open, anchor-time opens (06:00/10:00/14:00 ET)
  — `analytics/key_levels.py`. VWAP function exists but is excluded from the current reaction
  study by instruction.
- [x] Volume profile: POC, Value Area High/Low, high/low volume nodes — `analytics/volume_profile.py`.
- [x] Rejection blocks (last opposing candle(s) before an impulsive move) — `analytics/rejection_blocks.py`.
- [x] Reaction/outcome engine: for a given level, detect every touch and classify it as
  rejection / sweep / acceptance / inconclusive, plus per-level-type summary statistics —
  `analytics/level_reaction_study.py`, orchestrated per-day in `backtest/run_reaction_study.py`.
  Validated end-to-end on synthetic data via `scripts/demo_reaction_study.py`; running it for
  real requires real NQ/GC historical data (Phase 1's Databento ingest, not yet pulled).
- [ ] Volume Cumulation, absorption, and options-derived levels (GEX/DEX/vanna/charm) — these
  need order-flow/DOM and options-chain data this repo doesn't ingest yet (see
  docs/strategy_framework.md §9); not part of the current OHLCV-only reaction study.
- [ ] Zone clustering (§7 of the framework) for stacked/overlapping levels — not yet built; the
  current study tests each level type independently.

## Phase 3 — Backtesting
- Event-driven backtester over the Parquet data lake.
- Metrics tuned for prop-firm evaluation: max drawdown (trailing), daily loss, consistency
  (no single day > X% of total profit), win rate, expectancy, R-multiple distribution.
- Parameterize prop-firm rule presets (Topstep, Apex, etc.) so a backtest can simulate "would
  this have passed this specific firm's eval."

## Phase 4 — Paper / sim trading
- Real-time data feed wired into the same analytics layer used in backtest (no logic
  duplication).
- Discretionary-assist mode: live dashboard showing key levels + volume state, alerts, no
  auto-execution.
- Algo-assist mode: semi-automated (confirm-to-execute) signals.

## Phase 5 — Prop firm evaluation (live-simulated capital)
- Connect execution adapter (Tradovate or Rithmic API, via the prop firm's supported platform).
- Enforce prop-firm risk rules programmatically (kill-switch on daily loss / trailing drawdown).
- Run in sim/eval accounts; track against pass criteria.

## Phase 6 — Live trading
- Swap execution adapter to a live/funded account once eval is passed and the system has a
  track record.
- Ongoing: monitoring, logging, re-validation as market regime shifts.

## Open decisions to revisit later
- Which specific prop firm(s) to target (affects platform: Tradovate vs Rithmic vs ProjectX,
  and which automation rules apply).
- Contract size: micros (MES/MNQ/MGC) vs minis, based on account size and risk rules.
- How much of the discretionary layer becomes a UI/dashboard vs. just alerts.
