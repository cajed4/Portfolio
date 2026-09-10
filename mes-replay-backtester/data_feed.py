"""
data_feed.py — where the candles come from.

The whole point of this file: your strategy should NEVER care where bars
come from. Today it's yfinance. Later it could be Databento or IBKR.
Swap the feed, everything else stays the same.

JS comparison: think of DataFeed like an interface / abstract class.
Python doesn't force interfaces, but we use a base class with
NotImplementedError to get the same effect.
"""

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


class DataFeed:
    """Base class. Every feed must return a DataFrame of OHLCV bars
    with a timezone-aware DatetimeIndex in US/Eastern."""

    def get_bars(self, symbol: str, interval: str, period: str) -> pd.DataFrame:
        raise NotImplementedError  # like an abstract method in TypeScript


class YFinanceFeed(DataFeed):
    """Pulls delayed MES data from Yahoo Finance and caches it to CSV
    so you don't hammer Yahoo every time you re-run a backtest.

    Limits to know about:
      interval="1m"  -> only ~7 days of history
      interval="5m"  -> ~60 days
      interval="15m" -> ~60 days
      interval="1h"  -> ~2 years
    """

    def __init__(self, cache_dir: str = "data_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def get_bars(self, symbol: str = "MES=F", interval: str = "5m",
                 period: str = "60d", max_cache_age_hours: float = 12) -> pd.DataFrame:
        cache_file = self.cache_dir / f"{symbol.replace('=','')}_{interval}_{period}.csv"

        # Use the cache if it's fresh enough
        if cache_file.exists():
            age = datetime.now() - datetime.fromtimestamp(cache_file.stat().st_mtime)
            if age < timedelta(hours=max_cache_age_hours):
                print(f"[feed] using cached data ({cache_file.name}, {age.seconds//60} min old)")
                return self._load_cache(cache_file)

        print(f"[feed] downloading {symbol} {interval} bars ({period}) from Yahoo...")
        import yfinance as yf  # imported here so the module works offline too
        df = yf.download(symbol, interval=interval, period=period,
                         progress=False, auto_adjust=False)

        if df.empty:
            raise RuntimeError("Yahoo returned no data — check ticker/interval/period.")

        # yfinance sometimes returns MultiIndex columns like ('Close','MES=F')
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df.index = pd.to_datetime(df.index, utc=True).tz_convert("US/Eastern")
        df.index.name = "Time"

        df.to_csv(cache_file)
        print(f"[feed] got {len(df)} bars, cached to {cache_file.name}")
        return df

    @staticmethod
    def _load_cache(cache_file: Path) -> pd.DataFrame:
        df = pd.read_csv(cache_file, index_col="Time", parse_dates=True)
        df.index = pd.to_datetime(df.index, utc=True).tz_convert("US/Eastern")
        return df


class SyntheticFeed(DataFeed):
    """Fake-but-realistic MES bars for testing the pipeline without internet.
    Random walk around 6000 with session-like volatility. Great for making
    sure the replay engine + strategy wiring works before real data."""

    def get_bars(self, symbol: str = "MES=F", interval: str = "5m",
                 period: str = "5d", seed: int = 42) -> pd.DataFrame:
        import numpy as np
        rng = np.random.default_rng(seed)

        days = int(period.rstrip("d"))
        idx = pd.date_range(end=pd.Timestamp.now(tz="US/Eastern").floor("5min"),
                            periods=days * 24 * 12, freq="5min", tz="US/Eastern")

        price = 6000.0
        rows = []
        for _ in idx:
            drift = rng.normal(0, 2.5)            # ~2.5 pt stdev per 5-min bar
            o = price
            c = price + drift
            hi = max(o, c) + abs(rng.normal(0, 1.0))
            lo = min(o, c) - abs(rng.normal(0, 1.0))
            rows.append((round(o, 2), round(hi, 2), round(lo, 2), round(c, 2),
                         int(abs(rng.normal(3000, 1200)))))
            price = c

        df = pd.DataFrame(rows, columns=["Open", "High", "Low", "Close", "Volume"], index=idx)
        df.index.name = "Time"
        return df
