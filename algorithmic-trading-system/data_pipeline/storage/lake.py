"""
Parquet data lake: local, partitioned by symbol/date. No server to run, cheap, and DuckDB/
pandas/polars can all query it directly — good fit for a solo/small-team prop-trading build
before there's any reason to run a real database.

Layout on disk:
    <root>/<symbol>/<YYYY-MM-DD>.parquet

Each file holds one canonical-schema DataFrame (see transform/schema.py) for one symbol/day.
"""

from pathlib import Path

import pandas as pd

from data_pipeline.transform.schema import validate


class DataLake:
    def __init__(self, root: str | Path = "data/lake"):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, symbol: str, date: str) -> Path:
        return self.root / symbol / f"{date}.parquet"

    def write_day(self, symbol: str, date: str, df: pd.DataFrame, overwrite: bool = False) -> Path:
        """Write one symbol/day of canonical bars. `date` is 'YYYY-MM-DD'."""
        validate(df)
        path = self._path(symbol, date)
        if path.exists() and not overwrite:
            raise FileExistsError(f"{path} already exists; pass overwrite=True to replace it")
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(path, index=False)
        return path

    def read_range(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Read and concatenate all daily files for a symbol between two dates (inclusive)."""
        symbol_dir = self.root / symbol
        if not symbol_dir.exists():
            return pd.DataFrame()

        dates = pd.date_range(start_date, end_date, freq="D")
        frames = []
        for d in dates:
            path = self._path(symbol, d.strftime("%Y-%m-%d"))
            if path.exists():
                frames.append(pd.read_parquet(path))

        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True).sort_values("ts_event").reset_index(drop=True)

    def available_dates(self, symbol: str) -> list[str]:
        symbol_dir = self.root / symbol
        if not symbol_dir.exists():
            return []
        return sorted(p.stem for p in symbol_dir.glob("*.parquet"))
