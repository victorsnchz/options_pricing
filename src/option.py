from abc import ABC
import dataclasses
import datetime

from src.bookkeeping import OptionType, PayoffType, ExerciseType

@dataclasses.dataclass(frozen = True)
class Option(ABC):

    expiry: datetime.date
    strike: float
    
    payoff_type: PayoffType
    exercise_type: ExerciseType

@dataclasses.dataclass(frozen = True)
class Put(Option):
    pass

@dataclasses.dataclass(frozen = True)
class Call(Option):
    pass

    