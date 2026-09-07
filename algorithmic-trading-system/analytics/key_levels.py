"""
Key-level detection from canonical-schema OHLCV bars.

Levels computed here are the "algorithmic" backbone of the discretionary key-level trading
approach: prior session/day/week extremes, session/anchor-time opens, and (optionally) VWAP.
Volume-derived levels (POC, value area, high/low volume nodes) live in volume_profile.py —
combine both to get the full key-levels + volume picture for a given session.

Note: the first reaction-testing pass (see backtest/run_reaction_study.py) covers prior day/
week high-low, session open, the anchor-time opens below, POC/VAH/VAL/HVN/LVN, and rejection
blocks — VWAP is intentionally excluded from that first pass, per instruction, even though the
function stays here for later use.
"""

from dataclasses import dataclass, field

import pandas as pd

# Default anchor times (as HH:MM, America/New_York) traders commonly watch as intraday "opens" —
# in addition to the regular session/RTH open. 18:00 previous day is the Globex/"true day" open;
# 06:00, 10:00, and 14:00 ET are the ones currently in scope for the reaction study.
DEFAULT_ANCHOR_TIMES = ["06:00", "10:00", "14:00"]
ANCHOR_TZ = "America/New_York"


@dataclass
class KeyLevels:
    prior_day_high: float
    prior_day_low: float
    prior_day_close: float
    session_open: float
    session_vwap: float
    prior_week_high: float | None = None
    prior_week_low: float | None = None
    anchor_opens: dict = field(default_factory=dict)  # e.g. {"06:00": 5123.25, "10:00": 5130.0}
    extra: dict = field(default_factory=dict)


def anchor_time_opens(
    bars: pd.DataFrame,
    anchor_times: list[str] = DEFAULT_ANCHOR_TIMES,
    tz: str = ANCHOR_TZ,
) -> pd.DataFrame:
    """
    For each trading day present in `bars` (canonical schema, tz-aware UTC ts_event) and each
    HH:MM anchor time, find the open price of the first bar at/after that time (in `tz`) and
    return one row per (date, anchor_time, open_price). A day missing a given anchor time
    (e.g. no bars trading yet that early) is simply omitted for that anchor.

    This is the general form of "6am/10am/2pm open" as a key level: the anchor is a time of
    day, not tied to any single session-open definition, so it works the same way regardless of
    which exchange session the bar happens to fall in.
    """
    if bars.empty:
        return pd.DataFrame(columns=["date", "anchor_time", "anchor_open"])

    local_ts = bars["ts_event"].dt.tz_convert(tz)
    local_date = local_ts.dt.date
    local_time = local_ts.dt.strftime("%H:%M")

    rows = []
    for date, day_mask in local_date.groupby(local_date).groups.items():
        day_bars = bars.loc[day_mask]
        day_local_time = local_time.loc[day_mask]
        for anchor in anchor_times:
            at_or_after = day_bars.loc[day_local_time >= anchor]
            if at_or_after.empty:
                continue
            first_bar = at_or_after.iloc[0]
            rows.append({"date": date, "anchor_time": anchor, "anchor_open": float(first_bar["open"])})

    return pd.DataFrame(rows, columns=["date", "anchor_time", "anchor_open"])


def session_vwap(bars: pd.DataFrame) -> pd.Series:
    """Running VWAP within a single session's bars. Returns a Series aligned to `bars.index`."""
    typical_price = (bars["high"] + bars["low"] + bars["close"]) / 3.0
    cum_pv = (typical_price * bars["volume"]).cumsum()
    cum_vol = bars["volume"].cumsum().replace(0, pd.NA)
    return cum_pv / cum_vol


def compute_key_levels(
    daily_bars: pd.DataFrame,
    current_session_bars: pd.DataFrame,
) -> KeyLevels:
    """
    daily_bars: one row per prior trading day (needs high/low/close), most recent last.
                Used for prior-day and prior-week high/low/close.
    current_session_bars: intraday bars for the session in progress (needs open/high/low/
                close/volume, in chronological order). Used for session open and running VWAP.
    """
    if daily_bars.empty:
        raise ValueError("compute_key_levels needs at least one prior daily bar")
    if current_session_bars.empty:
        raise ValueError("compute_key_levels needs at least one current-session bar")

    prior_day = daily_bars.iloc[-1]
    vwap_series = session_vwap(current_session_bars)

    levels = KeyLevels(
        prior_day_high=float(prior_day["high"]),
        prior_day_low=float(prior_day["low"]),
        prior_day_close=float(prior_day["close"]),
        session_open=float(current_session_bars.iloc[0]["open"]),
        session_vwap=float(vwap_series.iloc[-1]),
    )

    if len(daily_bars) >= 5:
        last_week = daily_bars.iloc[-5:]
        levels.prior_week_high = float(last_week["high"].max())
        levels.prior_week_low = float(last_week["low"].min())

    return levels


def distance_to_levels(price: float, levels: KeyLevels, tick_size: float) -> dict[str, float]:
    """Distance (in ticks) from `price` to each key level — useful for signal thresholds like
    'flag when within N ticks of prior day high with rising relative volume'."""
    named = {
        "prior_day_high": levels.prior_day_high,
        "prior_day_low": levels.prior_day_low,
        "prior_day_close": levels.prior_day_close,
        "session_open": levels.session_open,
        "session_vwap": levels.session_vwap,
    }
    if levels.prior_week_high is not None:
        named["prior_week_high"] = levels.prior_week_high
    if levels.prior_week_low is not None:
        named["prior_week_low"] = levels.prior_week_low

    return {name: (price - lvl) / tick_size for name, lvl in named.items()}
