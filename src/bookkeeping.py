import enum


class OptionType(enum.Enum):
    CALL = 1
    PUT = -1

class ExerciseType(enum.Enum):
    EUROPEAN = enum.auto()
    AMERICAN = enum.auto()
    BERMUDAN = enum.auto()

class PayoffType(enum.Enum):
    VANILLA = enum.auto()
    ASIAN = enum.auto()
    BARRIER = enum.auto()

class PricerType(enum.Enum):
    BlackScholesPricer = enum.auto()
    MonteCarloPricer = enum.auto()

