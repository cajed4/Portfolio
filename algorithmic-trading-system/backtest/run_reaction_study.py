"""
Runs the framework's §10 research question #1 for real: "which key levels have what reaction?"

For each trading day in the data lake, computes every OHLCV-derived level type (prior day/week
high-low, session open, anchor-time opens at 06:00/10:00/14:00 ET, POC/VAH/VAL/HVN/LVN, and
rejection blocks), then runs each level through the touch/outcome engine
(analytics/level_reaction_study.py) against the following day(s) of price action, and prints a
per-level-type summary table: touch count, reaction rate (rejection+sweep), sweep rate,
acceptance rate, and average pierce/resolution stats.

VWAP and GEX/cumulation/absorption are intentionally excluded from this pass — VWAP by
instruction, the other three because they need data this repo doesn't have wired up yet (see
docs/strategy_framework.md §9).

Usage (once real data is in the lake — see data_pipeline/ingest/databento_historical.py):
    python -m backtest.run_reaction_study --symbol NQ --start 2024-01-01 --end 2024-06-01

Without real data yet, run scripts/demo_reaction_study.py instead — it generates synthetic
multi-day bars so you can see the full pipeline run end to end before paying for historical data.
"""

import argparse

import pandas as pd

from analytics.key_levels import DEFAULT_ANCHOR_TIMES, anchor_time_opens
from analytics.level_reaction_study import find_and_classify_touches, summarize_touches
from analytics.rejection_blocks import detect_rejection_blocks
from analytics.volume_profile import compute_volume_profile, high_volume_nodes
from config.instruments import INSTRUMENTS
from data_pipeline.storage.lake import DataLake


def levels_for_day(
    prior_day_bars: pd.DataFrame,
    prior_days_bars: pd.DataFrame,
    session_bars: pd.DataFrame,
    tick_size: float,
) -> list[tuple[str, float]]:
    """Compute every OHLCV-derived level for one trading day, given the prior day's bars (for
    high/low/close), a longer prior window (for prior-week high/low and the volume profile), and
    the day-of bars (for session open, anchor opens, and rejection blocks detected intraday).
    Returns a flat list of (level_type, price) pairs — some level types can appear more than
    once in a day if there are multiple rejection blocks."""
    levels: list[tuple[str, float]] = []

    if not prior_day_bars.empty:
        levels.append(("prior_day_high", float(prior_day_bars["high"].max())))
        levels.append(("prior_day_low", float(prior_day_bars["low"].min())))
        levels.append(("prior_day_close", float(prior_day_bars.iloc[-1]["close"])))

    if len(prior_days_bars) >= 1:
        levels.append(("prior_week_high", float(prior_days_bars["high"].max())))
        levels.append(("prior_week_low", float(prior_days_bars["low"].min())))

    if not session_bars.empty:
        levels.append(("session_open", float(session_bars.iloc[0]["open"])))

        anchors = anchor_time_opens(session_bars, anchor_times=DEFAULT_ANCHOR_TIMES)
        for _, row in anchors.iterrows():
            levels.append((f"anchor_open_{row['anchor_time']}", float(row["anchor_open"])))

    if not prior_days_bars.empty:
        vp = compute_volume_profile(prior_days_bars, tick_size=tick_size)
        levels.append(("poc", vp.poc))
        levels.append(("value_area_high", vp.value_area_high))
        levels.append(("value_area_low", vp.value_area_low))
        for price in high_volume_nodes(vp, top_n=3).index:
            levels.append(("hvn", float(price)))

        # Only the most recent few blocks are live, relevant levels for the day ahead — the
        # lookback window can span many days, and detect_rejection_blocks finds one every time
        # the impulse condition trips, which without a cap would make the level (and touch-test)
        # count grow with the lookback length instead of staying roughly constant per day.
        recent_blocks = detect_rejection_blocks(prior_days_bars.reset_index(drop=True))[-5:]
        for block in recent_blocks:
            mid = (block.high + block.low) / 2
            levels.append((f"rejection_block_{'bull' if block.direction > 0 else 'bear'}", mid))

    return levels


def run(symbol: str, start: str, end: str, lake_root: str, lookback_days: int) -> pd.DataFrame:
    if symbol not in INSTRUMENTS:
        raise ValueError(f"Unknown symbol {symbol!r}; add it to config/instruments.py first")
    tick_size = INSTRUMENTS[symbol].tick_size

    lake = DataLake(lake_root)
    all_bars = lake.read_range(symbol, start, end)
    if all_bars.empty:
        raise SystemExit(
            f"No data found for {symbol} between {start} and {end} in {lake_root}. "
            "Pull historical data first with data_pipeline/ingest/databento_historical.py, "
            "or try scripts/demo_reaction_study.py for a synthetic-data dry run."
        )

    all_bars["date"] = all_bars["ts_event"].dt.date
    trading_days = sorted(all_bars["date"].unique())

    all_touches = []
    for idx, day in enumerate(trading_days):
        if idx == 0:
            continue  # need at least one prior day

        session_bars = all_bars[all_bars["date"] == day].reset_index(drop=True)
        prior_day = trading_days[idx - 1]
        prior_day_bars = all_bars[all_bars["date"] == prior_day].reset_index(drop=True)

        lookback_start_idx = max(0, idx - lookback_days)
        lookback_days_set = set(trading_days[lookback_start_idx:idx])
        prior_days_bars = all_bars[all_bars["date"].isin(lookback_days_set)].reset_index(drop=True)

        levels = levels_for_day(prior_day_bars, prior_days_bars, session_bars, tick_size)

        # Test each level against this session's bars plus a little runway into the next day,
        # if available, so a touch late in the session still has room to resolve.
        future_idx = min(idx + 2, len(trading_days))
        future_days = set(trading_days[idx:future_idx])
        test_bars = all_bars[all_bars["date"].isin(future_days)].reset_index(drop=True)

        for level_type, price in levels:
            touches = find_and_classify_touches(
                test_bars, level_price=price, tick_size=tick_size, level_type=level_type,
            )
            all_touches.extend(touches)

    return summarize_touches(all_touches)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--symbol", required=True, choices=list(INSTRUMENTS.keys()))
    parser.add_argument("--start", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="YYYY-MM-DD")
    parser.add_argument("--lake-root", default="data/lake")
    parser.add_argument("--lookback-days", type=int, default=20,
                         help="How many prior days feed the volume profile / prior-week levels.")
    args = parser.parse_args()

    summary = run(args.symbol, args.start, args.end, args.lake_root, args.lookback_days)
    pd.set_option("display.width", 120)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
