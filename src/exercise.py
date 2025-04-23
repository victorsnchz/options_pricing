from abc import ABC
import dataclasses

from src.bookkeeping import Exercise

@dataclasses(frozen = True)
class Exercise(ABC):
    pass

def factory():
    pass
