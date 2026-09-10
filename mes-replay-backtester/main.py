"""
main.py — wire everything together and run a replay.

Usage:
    python main.py              # real MES data from Yahoo (needs internet)
    python main.py --synthetic  # fake data, for testing the pipeline
"""

import sys

from data_feed import YFinanceFeed, SyntheticFeed
from strategy import ICCStrategy
from replay import ReplayEngine, report


def main():
    use_synthetic = "--synthetic" in sys.argv

    # 1. Pick a feed — this is the ONLY line that changes when you
    #    upgrade to Databento / IBKR later.
    feed = SyntheticFeed() if use_synthetic else YFinanceFeed()

    # 2. Get bars. 5m x 60d is the sweet spot for yfinance.
    bars = feed.get_bars(symbol="MES=F", interval="5m", period="60d" if not use_synthetic else "5d")
    print(f"Loaded {len(bars)} bars: {bars.index[0]}  ->  {bars.index[-1]}\n")

    # 3. Run the replay
    engine = ReplayEngine(strategy=ICCStrategy(), contracts=1)
    trades = engine.run(bars)

    # 4. See how the strategy actually did
    report(trades, contracts=engine.contracts)


if __name__ == "__main__":
    main()
