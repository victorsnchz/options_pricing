import dataclasses
from abc import ABC, abstractmethod
from typing import final
from scipy.optimize import brentq

from src.option import Option
from src.pricers.types import Market

class Pricer(ABC):

    @abstractmethod
    def is_supported(self, option: Option, market: Market) -> bool: ...

    def validate_option_priceable(self, option: Option, market: Market) -> None:

        if not self.is_supported(option, market):
            raise NotImplementedError(
                f"{self.__class__.__name__} cannot price "
                f"{option.exercise.__class__.__name__} option "
                f"with {option.payoff.__class__.__name__} payoff."
            )

    @abstractmethod
    def is_valid_market_data(self, market: Market) -> bool: ...

    @final
    def price(self, option: Option, market: Market) -> float:
        self.validate_option_priceable(option, market)
        return self._price_impl(option, market)
    
    @abstractmethod
    def _price_impl(option, market) -> float: ...

    def implied_vol(self, option: Option, market: Market, target_price: float, *,
                    vol_min = 1e-6, vol_max = 10.0, tol: float = 1e-7, 
                    max_iter = 100) -> float: 
        
        def objective(vol: float) -> float:
            m = dataclasses.replace(market, vol=vol)
            return self.price(option, m) - target_price
        
        return brentq(objective, vol_min, vol_max, xtol=tol, maxiter=max_iter)