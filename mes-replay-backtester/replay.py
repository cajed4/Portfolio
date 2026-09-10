"""
replay.py — steps through historical bars one at a time, as if they were
arriving live, and runs your strategy + paper trader on each one.

Key honesty rule: on bar N, the strategy only ever sees bars[0..N].
No looking ahead. That's what makes a replay result trustworthy.

Built-in rules from your trading plan:
  - fixed stop/target from the Signal (10-pt stop)
  - 15-minute cooldown after a LOSING trade
  - one open position at a time
  - session filters (only trade NY Open / Tokyo windows)
"""

from dataclasses import dataclass, field
from datetime import time, timedelta

import pandas as pd

from strategy import Signal

MES_POINT_VALUE = 5.0  # $5 per point per contract


@dataclass
class Trade:
    direction: str
    entry_time: pd.Timestamp
    entry: float
    stop: float
    target: float
    reason: str
    exit_time: pd.Timestamp | None = None
    exit: float | None = None
    result: str | None = None      # "WIN" / "LOSS"
    pnl_points: float = 0.0
    pnl_dollars: float = 0.0


@dataclass
class Session:
    """A tradeable window in US/Eastern time."""
    name: str
    start: time
    end: time

    def contains(self, ts: pd.Timestamp) -> bool:
        t = ts.time()
        if self.start <= self.end:
            return self.start <= t <= self.end
        # window that crosses midnight (e.g. Tokyo from ET perspective)
        return t >= self.start or t <= self.end


# Your two sessions, in Eastern time:
NY_OPEN = Session("NY Open", time(9, 30), time(11, 30))
TOKYO = Session("Tokyo", time(19, 0), time(23, 0))


@dataclass
class ReplayEngine:
    strategy: object
    contracts: int = 1
    cooldown_minutes: int = 15
    sessions: list = field(default_factory=lambda: [NY_OPEN, TOKYO])

    trades: list = field(default_factory=list)
    _open: Trade | None = None
    _cooldown_until: pd.Timestamp | None = None

    def run(self, bars: pd.DataFrame, warmup: int = 10) -> list[Trade]:
        for i in range(warmup, len(bars)):
            now = bars.index[i]
            bar = bars.iloc[i]

            # 1) Manage an open position first
            if self._open:
                self._check_exit(now, bar)

            # 2) Look for a new entry
            if self._open is None and self._can_trade(now):
                visible = bars.iloc[: i + 1]        # <- no future bars!
                signal = self.strategy.evaluate(visible)
                if signal:
                    self._enter(now, signal)

        # Close anything still open at the last price (flat at end of data)
        if self._open:
            last = bars.iloc[-1]
            self._exit(bars.index[-1], float(last["Close"]), forced=True)

        return self.trades

    # ---------- internals ----------

    def _can_trade(self, now: pd.Timestamp) -> bool:
        if self._cooldown_until and now < self._cooldown_until:
            return False
        return any(s.contains(now) for s in self.sessions)

    def _enter(self, now: pd.Timestamp, sig: Signal):
        self._open = Trade(
            direction=sig.direction, entry_time=now, entry=sig.entry,
            stop=sig.stop, target=sig.target, reason=sig.reason,
        )
        print(f"  ENTER {sig.direction:5s} @ {sig.entry:.2f}  "
              f"stop {sig.stop:.2f} / tgt {sig.target:.2f}  [{now}]")

    def _check_exit(self, now: pd.Timestamp, bar):
        t = self._open
        if t.direction == "LONG":
            # Conservative: if a bar touches both stop and target,
            # assume the stop hit first.
            if bar["Low"] <= t.stop:
                self._exit(now, t.stop)
            elif bar["High"] >= t.target:
                self._exit(now, t.target)
        else:  # SHORT
            if bar["High"] >= t.stop:
                self._exit(now, t.stop)
            elif bar["Low"] <= t.target:
                self._exit(now, t.target)

    def _exit(self, now: pd.Timestamp, price: float, forced: bool = False):
        t = self._open
        t.exit_time, t.exit = now, price
        sign = 1 if t.direction == "LONG" else -1
        t.pnl_points = sign * (price - t.entry)
        t.pnl_dollars = t.pnl_points * MES_POINT_VALUE * self.contracts
        t.result = "WIN" if t.pnl_points > 0 else "LOSS"
        if forced:
            t.result += " (forced flat)"

        print(f"  EXIT  {t.direction:5s} @ {price:.2f}  "
              f"{t.pnl_points:+.2f} pts (${t.pnl_dollars:+.2f})  {t.result}  [{now}]")

        self.trades.append(t)
        self._open = None

        # 15-minute break after a loss — your anti-revenge-trading rule
        if t.pnl_points <= 0:
            self._cooldown_until = now + timedelta(minutes=self.cooldown_minutes)
            print(f"  ⏸  cooldown until {self._cooldown_until.time()} ET")


def report(trades: list[Trade], contracts: int = 1):
    if not trades:
        print("\nNo trades taken. Loosen INDICATION_MIN_RANGE or widen sessions.")
        return

    wins = [t for t in trades if t.pnl_points > 0]
    losses = [t for t in trades if t.pnl_points <= 0]
    total_pts = sum(t.pnl_points for t in trades)
    total_usd = sum(t.pnl_dollars for t in trades)

    print("\n" + "=" * 52)
    print("REPLAY RESULTS")
    print("=" * 52)
    print(f"Trades:      {len(trades)}  ({len(wins)} wins / {len(losses)} losses)")
    print(f"Win rate:    {len(wins) / len(trades) * 100:.1f}%")
    print(f"Net P&L:     {total_pts:+.2f} pts  = ${total_usd:+.2f} "
          f"({contracts} contract{'s' if contracts > 1 else ''})")
    if wins:
        print(f"Avg win:     {sum(t.pnl_points for t in wins)/len(wins):+.2f} pts")
    if losses:
        print(f"Avg loss:    {sum(t.pnl_points for t in losses)/len(losses):+.2f} pts")

    # Per-session breakdown
    print("-" * 52)
    for s in (NY_OPEN, TOKYO):
        st = [t for t in trades if s.contains(t.entry_time)]
        if st:
            pts = sum(t.pnl_points for t in st)
            w = sum(1 for t in st if t.pnl_points > 0)
            print(f"{s.name:8s}: {len(st)} trades, {w} wins, {pts:+.2f} pts")
    print("=" * 52)
