from dataclasses import dataclass
from datetime import datetime
import numpy as np

from src.exercise import EuropeanExercise
from src.payoff import VanillaPayoff
from src.pricers.base import Pricer
from src.pricers.types import Market
from src.option import Option
from src.pricers.time_utils import year_fraction

class BlackScholesPricer(Pricer):

    def is_supported(self, option: Option) -> bool:
        return (
            isinstance(option.exercise, EuropeanExercise) and 
            isinstance(option.payoff, VanillaPayoff) 
        )

    def _price_impl(self, option: Option, market: Market) -> float:
        
        if market.today is None:
            raise ValueError("BlackScholesPrices: Market.today is required to " +
                             "compute time to expiry.")
        if market.vol is None:
          raise ValueError("BlackScholesPrices: Market.vol is required.")

        S = market.spot
        K = option.strike
        r = market.rate
        q = market.div
        sigma = market.vol
        tau = max(0.0, year_fraction(market.day, option.exercise.expiry, market.basis))

        if option 


    def _price_impl_call(self, S: float, K: float, tau: datetime, r: float, q: float): ...

    def _price_impl_put(self, S: float, K: float, tau: datetime, r: float, q: float):
        price = self._price_impl_call(S, K, tau, r, q) + K * np.exp(-r*tau) - S
                 
