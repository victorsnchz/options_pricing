from dataclasses import dataclass
import datetime as dt
import numpy as np


@dataclass(frozen = True, slots = True)
class Market:
    spot: float
    rate: float = 0.0
    today: dt.date | None = None
    div: float = 0.0
    vol: float | None = None
    basis: str = 'ACT/365'

    def __post_init__(self) -> None:

        if not np.isfinite(self.spot) or self.spot <= 0:
            raise ValueError(f"Invalid spot value: {self.spot}")
        
        if self.vol is not None and (not np.isfinite(self.vol) or self.vol < 0):
            raise ValueError(f"Invalid vol value: {self.vol}")
        
        


@dataclass(frozen=True, slots = True)
class Greeks:
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float