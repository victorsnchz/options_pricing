from dataclasses import dataclass
import datetime as dt


@dataclass(frozen = True, slots = True)
class Market:
    spot: float
    rate: float
    today: dt.date
    div: float = 0.0
    vol: float | None = None
    basis: str = 'ACT/365'

@dataclass(frozen=True, slots = True)
class Greeks:
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float