"""
Volume profile: distribution of traded volume across price, computed from canonical-schema
OHLCV bars. This is the core "volume" half of the key-levels + volume edge.

Since we're working from bar data (not raw ticks) by default, each bar's volume is split
evenly across the price ticks it spans (open-high-low-close range) rather than assigned to a
single price — a standard approximation. If tick-level or per-price trade data becomes
available later (e.g. via Databento's `mbp-1`/`trades` schemas or Rithmic), swap in exact
per-trade allocation for more precision.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class VolumeProfileResult:
    profile: pd.Series          # index = price level, value = volume at that level
    poc: float                  # point of control: price level with the most volume
    value_area_high: float
    value_area_low: float
    total_volume: int


def compute_volume_profile(
    bars: pd.DataFrame,
    tick_size: float,
    value_area_pct: float = 0.70,
) -> VolumeProfileResult:
    """
    bars: canonical-schema DataFrame (needs open/high/low/close/volume) for the window to
          profile (e.g. one session, one week, or a rolling lookback).
    tick_size: instrument tick size (e.g. 0.25 for ES/NQ, 0.10 for GC) — sets price-bucket
               resolution.
    value_area_pct: fraction of total volume to include in the value area (70% is standard).
    """
    if bars.empty:
        raise ValueError("compute_volume_profile got an empty bars DataFrame")

    buckets: dict[float, float] = {}

    for row in bars.itertuples():
        lo = round(row.low / tick_size) * tick_size
        hi = round(row.high / tick_size) * tick_size
        levels = np.arange(lo, hi + tick_size, tick_size)
        if len(levels) == 0:
            levels = np.array([lo])
        vol_per_level = row.volume / len(levels)
        for lvl in levels:
            lvl = round(lvl, 8)
            buckets[lvl] = buckets.get(lvl, 0.0) + vol_per_level

    profile = pd.Series(buckets).sort_index()
    total_volume = profile.sum()

    poc = profile.idxmax()

    # Value area: expand out from POC, alternating sides, until value_area_pct of volume is covered.
    sorted_by_vol = profile.sort_values(ascending=False)
    cumulative = 0.0
    included_prices = []
    for price, vol in sorted_by_vol.items():
        included_prices.append(price)
        cumulative += vol
        if cumulative >= total_volume * value_area_pct:
            break

    value_area_high = max(included_prices)
    value_area_low = min(included_prices)

    return VolumeProfileResult(
        profile=profile,
        poc=float(poc),
        value_area_high=float(value_area_high),
        value_area_low=float(value_area_low),
        total_volume=int(total_volume),
    )


def high_volume_nodes(result: VolumeProfileResult, top_n: int = 5) -> pd.Series:
    """Return the top-N highest-volume price levels (potential support/resistance)."""
    return result.profile.sort_values(ascending=False).head(top_n)


def low_volume_nodes(result: VolumeProfileResult, top_n: int = 5) -> pd.Series:
    """Return the lowest-volume price levels within the traded range (potential breakout zones —
    price tends to move quickly through areas the market didn't spend much time/volume in)."""
    return result.profile.sort_values(ascending=True).head(top_n)
