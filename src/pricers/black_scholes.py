from dataclasses import dataclass
from datetime import datetime
import numpy as np
from scipy.stats import norm

from src.exercise import EuropeanExercise
from src.payoff import VanillaPayoff, Direction, PayoffContext
from src.pricers.base import Pricer
from src.pricers.types import Market, Greeks
from src.option import Option
from src.pricers.time_utils import year_fraction
from src.pricers.factory import PricerFactory, PricerType

@dataclass(frozen = True, slots = True)
class BSParameters:
    S: float
    K: float
    r: float
    q: float
    tau: float
    is_call: bool
    sigma: float | None = None

@dataclass(frozen = True, slots = True)
class BSQtys:
    sig_sqrt_t: float
    d1: float
    d2: float
    disc_q: float
    disc_r: float

class BlackScholesPricer(Pricer):

    def is_supported(self, option: Option) -> bool:
        return (
            isinstance(option.exercise, EuropeanExercise) and 
            isinstance(option.payoff, VanillaPayoff) 
        )
    
    def get_bs_inputs(self, option: Option, market: Market) -> BSParameters:

        if market.today is None:
            raise ValueError("BlackScholesPricer: Market.today is required to compute time to expiry.")
        if market.vol is None:
            raise ValueError("BlackScholesPricer: Market.vol is required.")
        

        S = float(market.spot)
        K = float(option.strike)
        r = float(market.rate)
        q = float(market.div)
        tau = max(0.0, year_fraction(market.today, option.exercise.expiry, market.basis))
        is_call = (option.direction is Direction.CALL)
        sigma = float(market.vol)

        return BSParameters(S, K, r, q, tau, is_call, sigma)
    
    def compute_bs_quantities(self, params: BSParameters) -> BSQtys:
        
        sig_sqrt_t = params.sigma * np.sqrt(params.tau)

        d1 = (np.log(params.S / params.K) + 
              (params.r - params.q + 0.5 * params.sigma * params.sigma) 
              * params.tau) / sig_sqrt_t
        
        d2 = d1 - sig_sqrt_t
        
        disc_q, disc_r = np.exp(-params.q * params.tau), np.exp(-params.r * params.tau)

        return BSQtys(sig_sqrt_t, d1, d2, disc_q, disc_r)

    def _price_impl(self, option: Option, market: Market) -> float:
        
        bs_params = self.get_bs_inputs(option, market)

        # "immediate" exercise
        if bs_params.tau == 0.0 or bs_params.sigma == 0.0: 
            return option.payoff.value(bs_params.K, 
                                       PayoffContext(spot=bs_params.S))
        
        bs_qtys = self.compute_bs_quantities(bs_params)

        if bs_params.is_call:
            value = (bs_params.S * bs_qtys.disc_q * norm.cdf(bs_qtys.d1)
                     - bs_params.K * bs_qtys.disc_r * norm.cdf(bs_qtys.d2)
                    )
        else:
            value = (bs_params.K * bs_qtys.disc_r * norm.cdf(-bs_qtys.d2) 
                     - bs_params.S * bs_qtys.disc_q * norm.cdf(-bs_qtys.d1)
                    )
        
        return value
        
    def greeks(self, option: Option, market: Market) -> Greeks:

        S, K, r, q, sigma, tau, is_call = self.get_bs_inputs(option, market)

        if tau == 0.0 or sigma == 0.0:
            return Greeks(delta = None, gamma = None, vega = None, theta = None, rho = None)
        
        sig_sqrt_t, d1, d2, disc_q, disc_r = self.compute_bs_quantities(S, K, tau, r, q, sigma)
        
        if is_call:
            delta = disc_q * norm.cdf(d1)
            theta = (-S * disc_q * norm.pdf(d1) * sigma / (2.0 * np.sqrt(tau))
                     - r * K * disc_r * norm.cdf(d2)
                     + q * S * disc_q * norm.cdf(d1))
            rho   =  K * tau * disc_r * norm.cdf(d2)
        else:
            delta = disc_q * (norm.cdf(d1) - 1.0)
            theta = (-S * disc_q * norm.pdf(d1) * sigma / (2.0 * np.sqrt(tau))
                     + r * K * disc_r * norm.cdf(d2)
                     - q * S * disc_q * norm.cdf(d1))
            rho   = -K * tau * disc_r * norm.cdf(d2)

        gamma = (disc_q * norm.pdf(d1)) / (S * sig_sqrt_t)
        vega  = S * disc_q * norm.cdf(d1) * np.sqrt(tau)

        return Greeks(delta, gamma, vega, theta, rho)


    def price_and_greeks(self, option: Option, market: Market) -> tuple[float, Greeks]:
        return self._price_impl(option, market), self.greeks(option, market)
    
@PricerFactory.register(PricerType.BLACK_SCHOLES)
def _make_black_scholes(**kw) -> Pricer:
    return BlackScholesPricer()