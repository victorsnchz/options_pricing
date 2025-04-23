from abc import ABC
import dataclasses

from src.bookkeeping import Payoff

@dataclasses(frozen = True)
class Payoff(ABC):
    pass

@dataclasses.dataclass(frozen=True)
class Vanilla(Payoff):
    pass

@dataclasses.dataclass(frozen=True)
class Asian(Payoff):
    pass

@dataclasses.dataclass(frozen=True)
class Barrier(Payoff):
    pass