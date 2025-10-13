from typing import Protocol
from dataclasses import dataclass
from abc import ABC
import enum

from src.pricers.base import Pricer

"""
Pricers more complex items than exercise rules or payoffs, split modules differently
"""
class PricerType(enum.Enum):
      BLACK_SCHOLES = enum.auto()
      BINARY_TREE = enum.auto()
      MONTE_CARLO = enum.auto()

@dataclass(frozen=True)
class _PricesCtor(Protocol):
    def __call__(self, **kwargs) -> Pricer: ...

class PricerFactory(ABC):
        
        _registry: dict[PricerType, _PricesCtor] = {}
        
        @classmethod
        def register(cls, key: PricerType):
            def _decorator(ctor: _PricesCtor):
                cls._registry[key] = ctor
                return ctor
            return _decorator
        
        @classmethod
        def create(cls, kind: PricerType, /, **kwargs) -> Pricer:
            try:
                return cls._registry[kind](**kwargs)
            except KeyError as e:
                if kind not in cls._registry:
                    raise ValueError(f"Unsupported ExerciseType: {kind!r}") from e
                else:
                    raise ValueError(f"Missing parameter for {kind.name}: {e}") from None