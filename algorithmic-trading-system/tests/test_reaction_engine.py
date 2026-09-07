import pandas as pd
import pytest

from analytics.key_levels import anchor_time_opens
from analytics.level_reaction_study import Outcome, find_and_classify_touches, summarize_touches
from analytics.rejection_blocks import detect_rejection_blocks
from data_pipeline.transform.schema import empty_canonical_frame

TICK = 0.25


def _bars_from_ohlc(ohlc: list[tuple[float, float, float, float]], start="2024-01-02 14:30", freq="1min"):
    """ohlc: list of (open, high, low, close) tuples, one per bar."""
    n = len(ohlc)
    df = empty_canonical_frame()
    df["ts_event"] = pd.date_range(start, periods=n, freq=freq, tz="UTC")
    df["symbol"] = "NQ"
    df["contract"] = "NQH4"
    df["open"] = [o for o, h, low, c in ohlc]
    df["high"] = [h for o, h, low, c in ohlc]
    df["low"] = [low for o, h, low, c in ohlc]
    df["close"] = [c for o, h, low, c in ohlc]
    df["volume"] = 100
    df["trade_count"] = pd.NA
    return df.astype({"open": "float64", "high": "float64", "low": "float64",
                       "close": "float64", "volume": "int64"})


# ---- level_reaction_study ----

def test_rejection_outcome():
    level = 100.0
    # Approach from above, touch, bounce hard back up, never really piercing below.
    ohlc = [
        (102, 102.5, 101.5, 102),   # establishes "above" side
        (101.5, 101.5, 100.2, 100.4),  # touches (low within tolerance of 100)
        (100.4, 103, 100.3, 102.8),   # reverses away, well above (final close after window)
    ] + [(103, 103.5, 102.8, 103.2)] * 10  # holds well above through the lookahead window
    bars = _bars_from_ohlc(ohlc)

    touches = find_and_classify_touches(
        bars, level_price=level, tick_size=TICK, level_type="test_level",
        tolerance_ticks=2, pierce_ticks=3, reversal_ticks=8, lookahead_bars=10,
    )
    assert len(touches) == 1
    assert touches[0].outcome == Outcome.REJECTION


def test_sweep_outcome():
    level = 100.0
    ohlc = [
        (102, 102.5, 101.5, 102),
        (101.5, 101.6, 98.5, 99.0),   # pierces well below (low=98.5 -> ~6 ticks beyond)
    ] + [(102.5, 103, 102, 102.8)] * 10  # then reverses back well above by end of window
    bars = _bars_from_ohlc(ohlc)

    touches = find_and_classify_touches(
        bars, level_price=level, tick_size=TICK, level_type="test_level",
        tolerance_ticks=2, pierce_ticks=3, reversal_ticks=8, lookahead_bars=10,
    )
    assert len(touches) == 1
    assert touches[0].outcome == Outcome.SWEEP
    assert touches[0].max_pierce_ticks >= 3


def test_acceptance_outcome():
    level = 100.0
    ohlc = [
        (102, 102.5, 101.5, 102),
        (101.5, 101.6, 99.5, 99.6),  # pierces below
    ] + [(99.0, 99.2, 98.5, 98.8)] * 10  # stays well below for the rest of the window
    bars = _bars_from_ohlc(ohlc)

    touches = find_and_classify_touches(
        bars, level_price=level, tick_size=TICK, level_type="test_level",
        tolerance_ticks=2, pierce_ticks=3, reversal_ticks=8, acceptance_hold_bars=3,
        lookahead_bars=10,
    )
    assert len(touches) == 1
    assert touches[0].outcome == Outcome.ACCEPTANCE


def test_inconclusive_outcome():
    level = 100.0
    # Grazes the level and just chops sideways near it — no clean pierce, no clean reversal.
    ohlc = [
        (102, 102.5, 101.5, 102),
        (101.0, 101.1, 99.9, 100.0),
    ] + [(100.0, 100.3, 99.8, 100.1)] * 10
    bars = _bars_from_ohlc(ohlc)

    touches = find_and_classify_touches(
        bars, level_price=level, tick_size=TICK, level_type="test_level",
        tolerance_ticks=2, pierce_ticks=3, reversal_ticks=8, lookahead_bars=10,
    )
    assert len(touches) == 1
    assert touches[0].outcome == Outcome.INCONCLUSIVE


def test_summarize_touches_rates():
    touches = find_and_classify_touches(
        _bars_from_ohlc([
            (102, 102.5, 101.5, 102),
            (101.5, 101.5, 100.2, 100.4),
            (100.4, 103, 100.3, 102.8),
        ] + [(103, 103.5, 102.8, 103.2)] * 10),
        level_price=100.0, tick_size=TICK, level_type="prior_day_low",
        tolerance_ticks=2, pierce_ticks=3, reversal_ticks=8, lookahead_bars=10,
    )
    summary = summarize_touches(touches)
    assert len(summary) == 1
    row = summary.iloc[0]
    assert row["level_type"] == "prior_day_low"
    assert row["touches"] == 1
    assert row["rejection_rate"] == 1.0
    assert row["reaction_rate"] == 1.0


def test_summarize_touches_empty():
    summary = summarize_touches([])
    assert summary.empty
    assert list(summary.columns) == [
        "level_type", "touches", "rejection_rate", "sweep_rate", "acceptance_rate",
        "inconclusive_rate", "reaction_rate", "avg_max_pierce_ticks", "avg_bars_to_resolve",
    ]


# ---- rejection_blocks ----

def test_detect_rejection_blocks_finds_bullish_block():
    # 14 flat/noisy candles to fill the ATR window, one down-close candle, then a sharp rally.
    flat = [(100 + 0.01 * i, 100.2 + 0.01 * i, 99.8 + 0.01 * i, 100.1 + 0.01 * i) for i in range(14)]
    down_candle = (101, 101.1, 100.5, 100.6)   # close < open -> bearish candle = the rejection block
    rally = [(100.6, 103, 100.6, 102.8), (102.8, 106, 102.8, 105.5), (105.5, 109, 105.5, 108.7)]
    ohlc = flat + [down_candle] + rally
    bars = _bars_from_ohlc(ohlc)

    blocks = detect_rejection_blocks(bars, lookahead_bars=3, impulse_multiple=2.0, atr_period=14)
    assert len(blocks) >= 1
    block = blocks[0]
    assert block.direction == 1  # bullish block acting as support
    assert block.low <= 100.6 <= block.high


def test_detect_rejection_blocks_empty_when_too_short():
    bars = _bars_from_ohlc([(100, 100.5, 99.5, 100.2)] * 5)
    assert detect_rejection_blocks(bars) == []


# ---- anchor_time_opens ----

def test_anchor_time_opens_basic():
    # Bars every 30 min starting 05:30 America/New_York (== 10:30 UTC in winter) through the day.
    bars = _bars_from_ohlc(
        [(100 + i, 100.5 + i, 99.5 + i, 100.2 + i) for i in range(20)],
        start="2024-01-02 10:30",  # UTC; America/New_York is UTC-5 in January -> 05:30 local
        freq="30min",
    )
    result = anchor_time_opens(bars, anchor_times=["06:00", "10:00"], tz="America/New_York")
    assert set(result["anchor_time"]) <= {"06:00", "10:00"}
    assert len(result) > 0
    # The 06:00 open should be the first bar at/after 06:00 local time.
    row_0600 = result[result["anchor_time"] == "06:00"].iloc[0]
    assert row_0600["anchor_open"] == pytest.approx(100.0 + 1)  # second bar (05:30 -> 06:00 local)


def test_anchor_time_opens_empty_bars():
    result = anchor_time_opens(empty_canonical_frame())
    assert result.empty
