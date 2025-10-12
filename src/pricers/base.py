from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import final
from src.option import Option

from src.pricers.types import Market

@dataclass
class Pricer(ABC):

    @abstractmethod
    def is_supported(self, option: Option) -> bool: ...

    def validate_option_priceable(self, option: Option) -> None:

        if not self.is_supported(option):
            raise NotImplementedError(
                f"{self.__class__.__name__} cannot price "
                f"{option.exercise.__class__.__name__} option "
                f"with {option.payoff.__class__.__name__} payoff."
            )

    @final
    def price(self, option: Option, market: Market) -> float:
        self.validate_option_priceable(option)
        return self._price_impl(option, market)
    
    @abstractmethod
    def _price_impl(option, market) -> float: ...