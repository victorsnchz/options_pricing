import dataclasses

from src.exercise import Exercise
from src.payoff import Payoff, PayoffContext
from src.direction import Direction


@dataclasses.dataclass(frozen = True, slots = True)
class Option:
    
    strike: float
    exercise: Exercise
    payoff: Payoff

    def payoff_value(self, context: PayoffContext) -> float: 
        return self.payoff.value(self.strike, context)
    
    @property
    def direction(self) -> Direction:
        return self.payoff.direction