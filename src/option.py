from abc import ABC, abstractmethod
import dataclasses

from src.exercise import Exercise
from src.payoff import Payoff, PayoffContext, Direction


@dataclasses.dataclass(frozen = True, slots = True)
class Option(ABC):
    
    strike: float
    exercise: Exercise
    payoff: Payoff

    @abstractmethod
    def payoff_value(self, context: PayoffContext) -> float: 
        return self.payoff.value(self.strike, context)
    
    @property
    def direction(self) -> Direction:
        return self.payoff.direction