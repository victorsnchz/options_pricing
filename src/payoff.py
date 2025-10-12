import dataclasses
from abc import ABC, abstractmethod
from direction import Direction

@dataclasses.dataclass(frozen=True)
class PayoffContext:
    spot: float
    path: tuple[float] | None = None

@dataclasses.dataclass(frozen=True)
class Payoff(ABC):
    direction: Direction  # CALL or PUT

    @abstractmethod
    def value(self, strike: float, ctx: PayoffContext) -> float:
        ...

@dataclasses.dataclass(frozen=True, slots=True)
class Vanilla(Payoff):

    def value(self, strike: float, ctx: PayoffContext) -> float: 
        return max(0.0, self.direction.value * (strike - ctx.spot))
    
@dataclasses.dataclass(frozen=True, slots=True)
class AsianArithmeticPayoff(Payoff):

    # can now implement independently more payoffs at wills

    def value(self, strike: float, ctx: PayoffContext) -> float: 
        pass
    
