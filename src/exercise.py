from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime as dt
from src.bookkeeping import ExerciseType
from typing import Protocol

# TODO
# make business days adjustments


class Exercise(ABC):
    
    @abstractmethod
    def can_exercise(self, t: dt.date) -> bool: ...

    @abstractmethod
    def exercise_dates(self) -> tuple[dt.date, ...]: ...

    pass

@dataclass(frozen=True, slots = True)
class EuropeanExercise(Exercise):
    
    expiry: dt.date

    # could make case that t >= expiry?
    def can_exercise(self, t: dt.date) -> bool : return t == self.expiry

    def exercise_dates(self) -> tuple[dt.dates, ...] : return (self.expiry,)

@dataclass(frozen=True, slots = True)
class AmericanExercise(Exercise):
    
    start: dt.date
    expiry: dt.date

    # could make case that t >= expiry? then only start required, expiry not 
    # stricly enforced...
    def can_exercise(self, t: dt.date) -> bool: return self.start <= t <= self.expiry
    
    def exercise_dates(self) -> tuple[dt.dates, ...]: 
        return tuple(dt.date.fromordinal(o) for o in range(self.start.toordinal(), 
                                                           self.expiry.toordinal()+1))
    
@dataclass(fronze=True, slots=True)
class BermudanExercise(Exercise):
    
    dates: tuple[dt.date,... ]

    def can_exercise(self, t) -> bool: return t in set(self.dates)
    
    def exercise_dates(self) -> tuple[dt.date, ...]:
        return self.dates

# TODO
"""
spend more time reading docs to proprely understand 
- Protocol
- register decorator 
"""

class _ExerciseCtor(Protocol):
    def __call__(self, **kwargs) -> Exercise: ...

class ExerciseFactory:

    _registry = dict[ExerciseType, _ExerciseCtor] = {}

    @classmethod
    def register(cls, key: ExerciseType):
        def _decorator(ctor: _ExerciseCtor):
            cls._registry[key] = ctor
            return ctor
        return _decorator
    
    @classmethod
    #interestimg technique: / forces lhs arguments to be position and rhs to be 
    # keywords ! so no confusion between kind passed and dict of arguments expected by 
    # specific exercise rule
    def create(cls, kind: ExerciseType, /, **kwargs) -> Exercise:
        try:
            return cls._registry[kind](**kwargs)
        except KeyError as e:
            if kind not in cls._registry:
                raise ValueError(f"Unsupported ExerciseType: {kind!r}") from e
            else:
                raise ValueError(f"Missing parameter for {kind.name}: {e}") from None
        
@ExerciseFactory.register(ExerciseType.EUROPEAN)
def _make_euro(**kw) -> Exercise:
    return EuropeanExercise(expiry=kw['expiry'])

@ExerciseFactory.register(ExerciseType.AMERICAN)
def _make_amer(**kw) -> Exercise:
    return AmericanExercise(start=kw['start'], expiry=kw['expiry'])

@ExerciseFactory.register(ExerciseType.BERMUDAN)
def _make_euro(**kw) -> Exercise:
    ds = tuple(kw['dates'])
    return BermudanExercise(dates=ds)

__all__ = [
    'Exercise',
    "EuropeanExercise", 
    "AmericanExercise",
    "BermudanExercise",
    "ExerciseFactory"
]