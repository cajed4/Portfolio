"""
Rejection block detection from canonical-schema OHLCV bars.

Definition (per docs/strategy_framework.md §2): the last opposing candle(s) before a strong,
impulsive move — last down-close candle(s) before a sharp rally (bullish block, acts as support
on a retest), or last up-close candle(s) before a sharp drop (bearish block, acts as resistance).

This is a first-pass, readable implementation (a plain per-bar loop, not vectorized) — fine for
the reaction study's scale (single-instrument daily/intraday bars), but worth vectorizing if this
ever needs to run over full tick-level history.
"""

from dataclasses import dataclass

import pandas as pd


@dataclass
class RejectionBlock:
    start_idx: int          # index into the bars DataFrame where the block starts
    end_idx: int             # index where the block ends (inclusive)
    high: float
    low: float
    direction: int            # +1 = bullish block (support), -1 = bearish block (resistance)
    impulse_move_ticks: float  # size of the impulsive move that followed, in price units (not ticks)


def detect_rejection_blocks(
    bars: pd.DataFrame,
    lookahead_bars: int = 3,
    impulse_multiple: float = 2.0,
    atr_period: int = 14,
) -> list[RejectionBlock]:
    """
    bars: canonical-schema OHLCV, chronological order, reset index (0..n-1).
    lookahead_bars: how many bars after a candidate candle to measure the "impulsive move" over.
    impulse_multiple: a move must be at least this many multiples of the rolling average bar
                      range to count as impulsive.
    atr_period: window for the rolling average range (a simple ATR proxy).

    Returns one RejectionBlock per detected impulse, each with the contiguous opposite-colored
    candle(s) immediately preceding it merged into a single zone (high/low of the block).
    """
    if len(bars) < atr_period + lookahead_bars + 1:
        return []

    bars = bars.reset_index(drop=True)
    bar_range = (bars["high"] - bars["low"]).astype(float)
    avg_range = bar_range.rolling(atr_period, min_periods=1).mean()

    blocks: list[RejectionBlock] = []
    n = len(bars)

    i = atr_period
    while i < n - lookahead_bars:
        entry_open = bars.loc[i + 1, "open"]
        exit_close = bars.loc[i + lookahead_bars, "close"]
        impulse_move = float(exit_close - entry_open)
        threshold = impulse_multiple * avg_range.loc[i]

        if threshold > 0 and abs(impulse_move) >= threshold:
            direction = 1 if impulse_move > 0 else -1
            candle_is_opposite = (
                bars.loc[i, "close"] < bars.loc[i, "open"] if direction > 0
                else bars.loc[i, "close"] > bars.loc[i, "open"]
            )

            if candle_is_opposite:
                # Extend backward while candles stay the same opposite color.
                start = i
                while start > 0:
                    prev_opposite = (
                        bars.loc[start - 1, "close"] < bars.loc[start - 1, "open"] if direction > 0
                        else bars.loc[start - 1, "close"] > bars.loc[start - 1, "open"]
                    )
                    if not prev_opposite:
                        break
                    start -= 1

                block_slice = bars.loc[start:i]
                blocks.append(RejectionBlock(
                    start_idx=int(start),
                    end_idx=int(i),
                    high=float(block_slice["high"].max()),
                    low=float(block_slice["low"].min()),
                    direction=direction,
                    impulse_move_ticks=impulse_move,
                ))
                # Skip past this impulse so we don't re-detect overlapping blocks inside it.
                i += lookahead_bars
                continue
        i += 1

    return blocks
