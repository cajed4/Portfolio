"""
Canonical bar schema used everywhere downstream (analytics, backtest, live).

Every provider-specific ingest script must normalize its output into a DataFrame with exactly
these columns before it gets written to the data lake. This is what lets us swap data vendors
(Databento now, Rithmic/Tradovate later) without touching analytics or backtest code.
"""

import pandas as pd

CANONICAL_COLUMNS = [
    "ts_event",     # UTC timestamp, bar open time (pandas Timestamp, tz-aware UTC)
    "symbol",       # canonical root, e.g. "ES", "NQ", "GC"
    "contract",     # actual traded contract, e.g. "ESZ5"
    "open",
    "high",
    "low",
    "close",
    "volume",
    "trade_count",  # number of trades in the bar, if available (else NaN)
]

DTYPES = {
    "symbol": "category",
    "contract": "category",
    "open": "float64",
    "high": "float64",
    "low": "float64",
    "close": "float64",
    "volume": "int64",
    "trade_count": "float64",
}


def empty_canonical_frame() -> pd.DataFrame:
    df = pd.DataFrame(columns=CANONICAL_COLUMNS)
    df["ts_event"] = pd.to_datetime(df["ts_event"], utc=True)
    return df.astype(DTYPES)


def validate(df: pd.DataFrame) -> None:
    """Raise if a DataFrame doesn't match the canonical schema. Call this before writing."""
    missing = set(CANONICAL_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing canonical columns: {missing}")
    if not isinstance(df["ts_event"].dtype, pd.DatetimeTZDtype):
        raise ValueError("ts_event must be tz-aware (UTC)")
    if (df["high"] < df["low"]).any():
        raise ValueError("Found bars where high < low")
    if (df["volume"] < 0).any():
        raise ValueError("Found negative volume")
