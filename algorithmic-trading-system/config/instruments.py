"""
Instrument specs for phase-1 focus: NQ, GC (and their micros). ES was in scope originally but
has been dropped from the strategy focus — see docs/strategy_framework.md.

`root` is the Databento/CME root symbol used for continuous-contract requests.
`tick_size` / `tick_value` are per 1 contract (mini); micro contracts are 1/10th size/value
for NQ, and 1/10th for GC micro (MGC) as well (10 oz vs 100 oz).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Instrument:
    root: str            # CME root symbol, e.g. "NQ"
    micro_root: str       # Micro contract root, e.g. "MNQ"
    name: str
    exchange: str = "CME" # GC/NQ are both CME Globex (NQ on CME, GC on COMEX, both on GLBX.MDP3)
    tick_size: float = 0.0
    tick_value_per_contract: float = 0.0  # dollar value of 1 tick, full-size contract
    session_tz: str = "America/Chicago"   # CME/COMEX pit timezone for session-boundary logic


INSTRUMENTS = {
    "NQ": Instrument(
        root="NQ", micro_root="MNQ", name="E-mini Nasdaq-100",
        tick_size=0.25, tick_value_per_contract=5.00,
    ),
    "GC": Instrument(
        root="GC", micro_root="MGC", name="Gold (COMEX)",
        tick_size=0.10, tick_value_per_contract=10.00,
    ),
}
