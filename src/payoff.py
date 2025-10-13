import dataclasses
from abc import ABC, abstractmethod
import enum
from typing import Protocol
from src.direction import Direction

@dataclasses.dataclass(frozen=True)
class PayoffContext:
    spot: float
    path: tuple[float] | None = None

    def __post_init__(self):
        
        if not type(self.spot) == float: 
            raise TypeError(f'spot must be float not {type(self.spot)}')
        
        if self.spot <  0: 
            raise ValueError(f'spot value must be positive')
        
        if self.path is not None and not type(self.path) == tuple:
            raise TypeError(f'path must be a tuple')
        
        if self.path is not None and not all(isinstance(x, float) for x in self.path):
            raise TypeError(f'all elements in path must be of type float')
        
        if self.path is not None and not all(x >= 0 for x in self.path):
            raise ValueError(f'all values in path must be positive')

@dataclasses.dataclass(frozen=True)
class Payoff(ABC):
    direction: Direction  # CALL or PUT

    @abstractmethod
    def value(self, strike: float, ctx: PayoffContext) -> float:
        ...

@dataclasses.dataclass(frozen=True, slots=True)
class VanillaPayoff(Payoff):

    def value(self, strike: float, ctx: PayoffContext) -> float: 
        return max(0.0, self.direction.value * (ctx.spot - strike))
    
@dataclasses.dataclass(frozen=True, slots=True)
class AsianArithmeticPayoff(Payoff):

    # can now implement independently more payoffs at wills

    def value(self, strike: float, ctx: PayoffContext) -> float: 
        pass

"""
***************************************************************************************
Factory
***************************************************************************************
"""


class PayoffType(enum.Enum):
    VANILLA = enum.auto()
    ASIAN_ARITHMETIC = enum.auto()
    #TODO 
    #BARRIER = enum.auto() -> wrapper around another payoff 
    #ASIAN_GEOMETRIC = enum.auto()
    #LOOKBACK = enum.auto()
    #DIGITAL = enum.auto()

class _PayoffCtor(Protocol):
    def __call__(self, **kwds)-> Payoff: ...

class PayoffFactory:

    _registry: dict[PayoffType, _PayoffCtor] = {}

    @classmethod
    def register(cls, key: PayoffType):
        def _decorator(ctor: _PayoffCtor):
            cls._registry[key] = ctor
            return ctor
        return _decorator
    
    @classmethod
    def create(cls, kind: PayoffType, /, direction: Direction, **kwargs) -> Payoff:
        try:
            ctor = cls._registry[kind]
        except KeyError as e:
            raise ValueError(f"Unsupported PayoffType: {kind!r}") from e
            
        try: 
            return ctor(direction = direction, **kwargs)
        except TypeError as e:
            raise ValueError(f"Error constructing {kind.name}: {e}") from None
       
@PayoffFactory.register(PayoffType.VANILLA)
def _make_vanilla(*, direction: Direction, **kwargs) -> Payoff:
    return VanillaPayoff(direction=direction)