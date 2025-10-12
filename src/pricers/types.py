from dataclasses import dataclass
import datetime as dt


@dataclass(frozen = True, slots = True)
class Market:
    spot: float
    rate: float
    div: float = 0.0
    vol: float | None = None
    today: dt.date

