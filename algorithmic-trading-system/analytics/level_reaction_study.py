"""
Core engine for the reaction study (framework §10, question 1: "which key levels have what
reaction?"). Given a single price level and a run of bars, finds every time price touches that
level and classifies what happened next: REJECTION, SWEEP, ACCEPTANCE, or INCONCLUSIVE.

This module only knows about one level at a time. backtest/run_reaction_study.py is what wires
this up to real data: computing every level type for every day (analytics/key_levels.py,
volume_profile.py, rejection_blocks.py) and running each one through find_and_classify_touches,
then summarize_touches to get the per-level-type statistics the framework's research plan calls
for.
"""

from dataclasses import dataclass
from enum import Enum

import pandas as pd


class Outcome(str, Enum):
    REJECTION = "rejection"     # approached, never meaningfully pierced, reversed away
    SWEEP = "sweep"              # pierced through, then reversed back
    ACCEPTANCE = "acceptance"    # pierced through and stayed beyond (continuation/breakout)
    INCONCLUSIVE = "inconclusive"  # none of the above resolved within the lookahead window


@dataclass
class LevelTouch:
    level_type: str
    level_price: float
    touch_idx: int           # index into the bars DataFrame of the first touching bar
    touch_time: pd.Timestamp
    approach_side: str        # "above" or "below" — which side price was on before the touch
    outcome: Outcome
    max_pierce_ticks: float    # furthest price went beyond the level, in ticks (through direction)
    final_reversal_ticks: float  # how far price ended up back on the original side, in ticks
    bars_to_resolve: int


def _side_of(price: float, level_price: float, tolerance: float) -> str | None:
    if price > level_price + tolerance:
        return "above"
    if price < level_price - tolerance:
        return "below"
    return None  # inside the tolerance band — not clearly on either side


def find_and_classify_touches(
    bars: pd.DataFrame,
    level_price: float,
    tick_size: float,
    level_type: str = "level",
    tolerance_ticks: float = 2.0,
    pierce_ticks: float = 3.0,
    reversal_ticks: float = 8.0,
    acceptance_hold_bars: int = 5,
    lookahead_bars: int = 20,
) -> list[LevelTouch]:
    """
    bars: canonical-schema OHLCV, chronological, reset index (0..n-1), single instrument.
    level_price: the price level to test.
    tick_size: instrument tick size, used to convert the tick-based thresholds below to price.
    tolerance_ticks: how close price must get to count as "touching" the level.
    pierce_ticks: how far beyond the level price must go (past the touch) to count as a real
                  pierce, rather than just grazing the tolerance band.
    reversal_ticks: how far back on the original side price must end up, by the end of the
                    lookahead window, to count as a confirmed reversal.
    acceptance_hold_bars: how many of the final bars in the lookahead window must stay beyond
                          the level (by at least pierce_ticks) for it to count as "acceptance"
                          rather than a sweep that just hasn't reversed yet.
    lookahead_bars: how many bars after the touch to evaluate the outcome over.
    """
    if bars.empty:
        return []

    bars = bars.reset_index(drop=True)
    tolerance = tolerance_ticks * tick_size
    n = len(bars)

    touches: list[LevelTouch] = []
    prior_side: str | None = None
    i = 0
    while i < n:
        row = bars.loc[i]
        touching = row["low"] - tolerance <= level_price <= row["high"] + tolerance

        if touching and prior_side is not None:
            window_end = min(i + lookahead_bars, n - 1)
            window = bars.loc[i:window_end]

            if prior_side == "above":
                # through direction is downward past the level
                pierce_amounts = (level_price - window["low"]) / tick_size
                final_close = window.iloc[-1]["close"]
                reversal_amount = (final_close - level_price) / tick_size  # positive = back above
                held_beyond = ((level_price - window["close"].tail(acceptance_hold_bars)) / tick_size
                               >= pierce_ticks)
            else:
                pierce_amounts = (window["high"] - level_price) / tick_size
                final_close = window.iloc[-1]["close"]
                reversal_amount = (level_price - final_close) / tick_size  # positive = back below
                held_beyond = ((window["close"].tail(acceptance_hold_bars) - level_price) / tick_size
                               >= pierce_ticks)

            max_pierce = float(pierce_amounts.max())
            pierced = max_pierce >= pierce_ticks
            reversed_ = reversal_amount >= reversal_ticks
            sustained = bool(held_beyond.all()) and len(held_beyond) > 0

            if pierced and reversed_:
                outcome = Outcome.SWEEP
            elif not pierced and reversed_:
                outcome = Outcome.REJECTION
            elif pierced and sustained and not reversed_:
                outcome = Outcome.ACCEPTANCE
            else:
                outcome = Outcome.INCONCLUSIVE

            touches.append(LevelTouch(
                level_type=level_type,
                level_price=level_price,
                touch_idx=i,
                touch_time=row["ts_event"],
                approach_side=prior_side,
                outcome=outcome,
                max_pierce_ticks=max_pierce,
                final_reversal_ticks=float(reversal_amount),
                bars_to_resolve=window_end - i,
            ))

            # Jump past this touch's resolution window before looking for the next touch, so one
            # extended interaction isn't double-counted as many touches.
            i = window_end + 1
            prior_side = _side_of(final_close, level_price, tolerance) or prior_side
            continue

        side = _side_of(row["close"], level_price, tolerance)
        if side is not None:
            prior_side = side
        i += 1

    return touches


def summarize_touches(touches: list[LevelTouch]) -> pd.DataFrame:
    """Aggregate a list of LevelTouch records into per-level-type statistics: touch count, and
    the rate of each outcome, plus average pierce/reversal magnitude. This is the table that
    answers "which key levels have what reaction" once run over real historical data."""
    if not touches:
        return pd.DataFrame(columns=[
            "level_type", "touches", "rejection_rate", "sweep_rate", "acceptance_rate",
            "inconclusive_rate", "reaction_rate", "avg_max_pierce_ticks", "avg_bars_to_resolve",
        ])

    df = pd.DataFrame([{
        "level_type": t.level_type,
        "outcome": t.outcome.value,
        "max_pierce_ticks": t.max_pierce_ticks,
        "bars_to_resolve": t.bars_to_resolve,
    } for t in touches])

    def _summarize_group(group: pd.DataFrame) -> pd.Series:
        n = len(group)
        counts = group["outcome"].value_counts()
        rejection = counts.get(Outcome.REJECTION.value, 0)
        sweep = counts.get(Outcome.SWEEP.value, 0)
        acceptance = counts.get(Outcome.ACCEPTANCE.value, 0)
        inconclusive = counts.get(Outcome.INCONCLUSIVE.value, 0)
        return pd.Series({
            "touches": n,
            "rejection_rate": rejection / n,
            "sweep_rate": sweep / n,
            "acceptance_rate": acceptance / n,
            "inconclusive_rate": inconclusive / n,
            "reaction_rate": (rejection + sweep) / n,  # framework's "did the level hold" rate
            "avg_max_pierce_ticks": group["max_pierce_ticks"].mean(),
            "avg_bars_to_resolve": group["bars_to_resolve"].mean(),
        })

    summary = df.groupby("level_type", group_keys=True).apply(_summarize_group, include_groups=False)
    return summary.reset_index().sort_values("touches", ascending=False).reset_index(drop=True)
