from typing import Protocol
from dataclasses import dataclass

from src.pricers.base import Pricer

"""
Pricers more complex items than exercise rules or payoffs, split modules differently
"""

@dataclass(frozen=True)
class _PricesCtor(Protocol):
    def __call__(self, **kwargs) -> Pricer: ...

class Pricer:
        pass