"""
Pull historical OHLCV bars for NQ, GC from Databento (CME Globex MDP 3.0 / GLBX.MDP3),
normalize to the canonical schema, and write into the local Parquet data lake.

Setup:
    pip install databento
    export DATABENTO_API_KEY=db-xxxxxxxxxxxxxxxx   # from https://databento.com/portal/keys

Usage:
    python -m data_pipeline.ingest.databento_historical \
        --symbols ES NQ GC \
        --start 2024-01-01 --end 2024-03-01 \
        --schema ohlcv-1m

Notes:
- Uses Databento's continuous-contract front-month symbology (e.g. "ES.c.0") so contract
  rolls are handled by Databento rather than by us. The actual traded contract per bar is
  still recorded in the `contract` column via the returned instrument definitions.
- This hits Databento's historical (pay-as-you-go) endpoint, which is billed per query — start
  with a small date range to validate the pipeline before pulling a large backfill.
- Cost estimate before pulling a large range: use client.metadata.get_cost(...) (see Databento
  docs) so you don't get a surprise bill.
"""

import argparse
import os

import pandas as pd

from config.instruments import INSTRUMENTS
from data_pipeline.storage.lake import DataLake
from data_pipeline.transform.schema import CANONICAL_COLUMNS, DTYPES

DATASET = "GLBX.MDP3"


def _get_client():
    try:
        import databento as db
    except ImportError as e:
        raise SystemExit(
            "The 'databento' package isn't installed. Run: pip install databento --break-system-packages"
        ) from e

    api_key = os.environ.get("DATABENTO_API_KEY")
    if not api_key:
        raise SystemExit(
            "Set DATABENTO_API_KEY in your environment (get one at https://databento.com/portal/keys)"
        )
    return db.Historical(api_key)


def fetch_symbol(client, symbol: str, start: str, end: str, schema: str = "ohlcv-1m") -> pd.DataFrame:
    """Fetch one instrument's continuous-front-month bars and normalize to canonical schema."""
    if symbol not in INSTRUMENTS:
        raise ValueError(f"Unknown symbol {symbol!r}; add it to config/instruments.py first")

    continuous_symbol = f"{symbol}.c.0"  # front month, continuous, volume-based roll

    data = client.timeseries.get_range(
        dataset=DATASET,
        symbols=[continuous_symbol],
        stype_in="continuous",
        schema=schema,
        start=start,
        end=end,
    )
    df = data.to_df()

    if df.empty:
        return df

    out = pd.DataFrame({
        "ts_event": pd.to_datetime(df.index if "ts_event" not in df.columns else df["ts_event"], utc=True),
        "symbol": symbol,
        "contract": df["symbol"] if "symbol" in df.columns else continuous_symbol,
        "open": df["open"].astype(float),
        "high": df["high"].astype(float),
        "low": df["low"].astype(float),
        "close": df["close"].astype(float),
        "volume": df["volume"].astype("int64"),
        "trade_count": df["trade_count"].astype(float) if "trade_count" in df.columns else float("nan"),
    })
    return out[CANONICAL_COLUMNS].astype(DTYPES | {"ts_event": out["ts_event"].dtype})


def run(symbols: list[str], start: str, end: str, schema: str, lake_root: str, overwrite: bool):
    client = _get_client()
    lake = DataLake(lake_root)

    for symbol in symbols:
        print(f"Fetching {symbol} {start} -> {end} ({schema}) from Databento...")
        df = fetch_symbol(client, symbol, start, end, schema)
        if df.empty:
            print(f"  No data returned for {symbol}; skipping.")
            continue

        df["date"] = df["ts_event"].dt.date.astype(str)
        for date, day_df in df.groupby("date"):
            day_df = day_df.drop(columns=["date"])
            path = lake.write_day(symbol, date, day_df, overwrite=overwrite)
            print(f"  Wrote {len(day_df)} bars -> {path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--symbols", nargs="+", default=["NQ", "GC"])
    parser.add_argument("--start", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="YYYY-MM-DD")
    parser.add_argument("--schema", default="ohlcv-1m", help="Databento schema, e.g. ohlcv-1m, ohlcv-1h")
    parser.add_argument("--lake-root", default="data/lake")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    run(args.symbols, args.start, args.end, args.schema, args.lake_root, args.overwrite)


if __name__ == "__main__":
    main()
