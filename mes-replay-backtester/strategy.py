"""
strategy.py — your ICC logic lives here.

The contract is simple: the replay engine hands you a DataFrame of all
bars up to "now" (no peeking into the future!), and you return a Signal
or None.

>>> REPLACE the placeholder logic in ICCStrategy.evaluate() with your
>>> Phase 1 ICC rules. The interface (Signal in, bars out) stays the same.
"""

from dataclasses import dataclass


@dataclass
class Signal:
    """What the strategy tells the trader. Like a plain JS object,
    but with declared fields — dataclasses give you the constructor,
    repr, and equality for free."""
    direction: str        # "LONG" or "SHORT"
    entry: float          # entry price (close of signal bar)
    stop: float           # stop-loss price
    target: float         # take-profit price
    reason: str = ""      # human-readable note for the trade log


class ICCStrategy:
    """Indication -> Correction -> Continuation.

    PLACEHOLDER LOGIC (replace with yours):
      Indication:   a strong bar (range > threshold) in one direction
      Correction:   the next 1-2 bars pull back against it
      Continuation: a bar closing back beyond the indication bar's extreme

    Stops/targets: fixed 10-pt stop (your rule), 2R target by default.
    """

    STOP_POINTS = 10.0     # your fixed 10-point stop
    RR = 2.0               # reward:risk multiple for the target
    INDICATION_MIN_RANGE = 4.0   # pts; tune this

    def evaluate(self, bars) -> Signal | None:
        if len(bars) < 4:
            return None

        # Last 4 bars: indication, correction, correction/continuation, current
        window = bars.iloc[-4:]
        ind, corr, cont, cur = (window.iloc[0], window.iloc[1],
                                window.iloc[2], window.iloc[3])

        ind_range = ind["High"] - ind["Low"]
        if ind_range < self.INDICATION_MIN_RANGE:
            return None

        bullish_ind = ind["Close"] > ind["Open"]

        if bullish_ind:
            # Correction: pullback bar(s) that stay above indication low
            corrected = corr["Close"] < corr["Open"] and corr["Low"] > ind["Low"]
            # Continuation: close back above the indication high
            continued = corrected and cur["Close"] > ind["High"]
            if continued:
                entry = float(cur["Close"])
                return Signal(
                    direction="LONG",
                    entry=entry,
                    stop=entry - self.STOP_POINTS,
                    target=entry + self.STOP_POINTS * self.RR,
                    reason=f"ICC long: ind range {ind_range:.2f}, cont close {entry:.2f}",
                )
        else:
            corrected = corr["Close"] > corr["Open"] and corr["High"] < ind["High"]
            continued = corrected and cur["Close"] < ind["Low"]
            if continued:
                entry = float(cur["Close"])
                return Signal(
                    direction="SHORT",
                    entry=entry,
                    stop=entry + self.STOP_POINTS,
                    target=entry - self.STOP_POINTS * self.RR,
                    reason=f"ICC short: ind range {ind_range:.2f}, cont close {entry:.2f}",
                )

        return None
