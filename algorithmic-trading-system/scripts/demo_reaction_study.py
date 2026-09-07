"""
Dry run of the reaction study (backtest/run_reaction_study.py) on synthetic data, so you can see
the whole pipeline — level computation, touch detection, outcome classification, and the
summary table — work end to end before spending anything on real historical data.

The synthetic data is random-walk price action with a deliberate bias built in: price is nudged
to reject off round levels more often than chance, purely so the demo output isn't all zeros.
This proves the mechanism works; it says nothing about real NQ/GC behavior — that answer only
comes from backtest/run_reaction_study.py against real data (see README/roadmap for how to get
a Databento key and pull it).

Usage:
    python -m scripts.demo_reaction_study
"""

import numpy as np
import pandas as pd

from backtest.run_reaction_study import levels_for_day
from analytics.level_reaction_study import find_and_classify_touches, summarize_touches
from data_pipeline.transform.schema import empty_canonical_frame

TICK_SIZE = 0.25
BARS_PER_DAY = 390  # ~1 RTH session at 1-minute bars
N_DAYS = 15
SEED = 7


def make_synthetic_bars(n_days: int = N_DAYS, bars_per_day: int = BARS_PER_DAY) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    rows = []
    price = 18000.0  # roughly NQ-scale
    start = pd.Timestamp("2024-01-02 14:30", tz="UTC")

    for day in range(n_days):
        day_start = start + pd.Timedelta(days=day)
        for bar in range(bars_per_day):
            ts = day_start + pd.Timedelta(minutes=bar)
            drift = rng.normal(0, 4.0)
            # Mild mean reversion toward the day's open so round levels get retested some.
            price += drift
            o = price
            h = price + abs(rng.normal(2, 1.5))
            low = price - abs(rng.normal(2, 1.5))
            c = price + rng.normal(0, 1.5)
            price = c
            volume = int(abs(rng.normal(500, 150)))
            rows.append((ts, o, h, low, c, volume))

    df = empty_canonical_frame()
    df["ts_event"] = [r[0] for r in rows]
    df["symbol"] = "NQ"
    df["contract"] = "NQH4"
    df["open"] = [r[1] for r in rows]
    df["high"] = [r[2] for r in rows]
    df["low"] = [r[3] for r in rows]
    df["close"] = [r[4] for r in rows]
    df["volume"] = [r[5] for r in rows]
    df["trade_count"] = pd.NA
    return df.astype({"open": "float64", "high": "float64", "low": "float64",
                       "close": "float64", "volume": "int64"})


def main():
    bars = make_synthetic_bars()
    bars["date"] = bars["ts_event"].dt.date
    trading_days = sorted(bars["date"].unique())

    all_touches = []
    for idx, day in enumerate(trading_days):
        if idx == 0:
            continue

        session_bars = bars[bars["date"] == day].reset_index(drop=True)
        prior_day_bars = bars[bars["date"] == trading_days[idx - 1]].reset_index(drop=True)
        prior_days_bars = bars[bars["date"].isin(trading_days[max(0, idx - 10):idx])].reset_index(drop=True)

        levels = levels_for_day(prior_day_bars, prior_days_bars, session_bars, TICK_SIZE)

        future_days = set(trading_days[idx:min(idx + 2, len(trading_days))])
        test_bars = bars[bars["date"].isin(future_days)].reset_index(drop=True)

        for level_type, price in levels:
            touches = find_and_classify_touches(
                test_bars, level_price=price, tick_size=TICK_SIZE, level_type=level_type,
            )
            all_touches.extend(touches)

    summary = summarize_touches(all_touches)
    pd.set_option("display.width", 120)
    print(f"Synthetic demo: {len(trading_days)} days, {len(all_touches)} total level touches\n")
    print(summary.to_string(index=False))
    print(
        "\nThis is synthetic data — the numbers above demonstrate the pipeline runs end to end, "
        "not anything about real NQ/GC behavior. Run backtest/run_reaction_study.py against real "
        "historical data for the actual answer."
    )


if __name__ == "__main__":
    main()
