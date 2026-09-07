import shutil
from pathlib import Path

import pandas as pd
import pytest

from analytics.key_levels import compute_key_levels, session_vwap
from analytics.volume_profile import compute_volume_profile
from data_pipeline.storage.lake import DataLake
from data_pipeline.transform.schema import empty_canonical_frame, validate

TEST_LAKE_ROOT = "data/_test_lake"


@pytest.fixture(autouse=True)
def clean_lake():
    yield
    shutil.rmtree(TEST_LAKE_ROOT, ignore_errors=True)


def _make_bars(n=10, start_price=100.0):
    ts = pd.date_range("2024-01-02 14:30", periods=n, freq="1min", tz="UTC")
    df = empty_canonical_frame()
    df["ts_event"] = ts
    df["symbol"] = "ES"
    df["contract"] = "ESH4"
    df["open"] = [start_price + i * 0.25 for i in range(n)]
    df["high"] = df["open"] + 0.5
    df["low"] = df["open"] - 0.5
    df["close"] = df["open"] + 0.25
    df["volume"] = [100 + i * 10 for i in range(n)]
    df["trade_count"] = pd.NA
    return df.astype({"open": "float64", "high": "float64", "low": "float64",
                       "close": "float64", "volume": "int64"})


def test_schema_validates_good_frame():
    df = _make_bars()
    validate(df)  # should not raise


def test_schema_rejects_high_less_than_low():
    df = _make_bars()
    df.loc[0, "high"] = df.loc[0, "low"] - 1
    with pytest.raises(ValueError):
        validate(df)


def test_lake_write_and_read_round_trip():
    lake = DataLake(TEST_LAKE_ROOT)
    df = _make_bars()
    lake.write_day("ES", "2024-01-02", df)

    read_back = lake.read_range("ES", "2024-01-02", "2024-01-02")
    assert len(read_back) == len(df)
    assert read_back["symbol"].iloc[0] == "ES"


def test_lake_refuses_overwrite_by_default():
    lake = DataLake(TEST_LAKE_ROOT)
    df = _make_bars()
    lake.write_day("ES", "2024-01-02", df)
    with pytest.raises(FileExistsError):
        lake.write_day("ES", "2024-01-02", df)
    lake.write_day("ES", "2024-01-02", df, overwrite=True)  # should not raise


def test_volume_profile_poc_and_value_area():
    df = _make_bars(n=20)
    result = compute_volume_profile(df, tick_size=0.25)
    assert result.total_volume == df["volume"].sum()
    assert result.value_area_low <= result.poc <= result.value_area_high


def test_key_levels_and_vwap():
    daily = pd.DataFrame({
        "high": [101.0, 102.0, 103.5],
        "low": [99.0, 100.0, 101.0],
        "close": [100.5, 101.5, 102.5],
    })
    session = _make_bars(n=5, start_price=102.0)

    levels = compute_key_levels(daily, session)
    assert levels.prior_day_high == 103.5
    assert levels.prior_day_low == 101.0
    assert levels.session_open == session.iloc[0]["open"]

    vwap = session_vwap(session)
    assert vwap.iloc[-1] > 0
