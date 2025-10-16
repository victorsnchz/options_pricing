from dataclasses import dataclass
from datetime import datetime
import numpy as np
from scipy.stats import norm

from src.exercise import EuropeanExercise, AmericanExercise
from src.option import Option
from src.direction import Direction
from src.payoff import VanillaPayoff, Direction, PayoffContext
from src.pricers.base import Pricer
from src.pricers.types import Market, Greeks
from src.pricers.factory import PricerFactory, PricerType
from src.pricers.time_utils import year_fraction, basis_mapping


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

    def is_supported(self, option: Option, market: Market) -> bool:

        is_vanilla_european = ( isinstance(option.exercise, EuropeanExercise) 
                               and isinstance(option.payoff, VanillaPayoff) 
                               )
        
        is_vanilla_american_call_no_div = ( isinstance(option.exercise, AmericanExercise) 
                                    and isinstance(option.payoff, VanillaPayoff) 
                                    and isinstance(option.direction, Direction.CALL)
                                    and market.div == 0.0
                                    )

        return (
            is_vanilla_european or is_vanilla_american_call_no_div
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

        d1 = ( np.log(params.S / params.K)
              + (params.r - params.q + 0.5 * params.sigma**2) * params.tau
              ) / sig_sqrt_t 
        
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

        value = (bs_params.S * bs_qtys.disc_q * norm.cdf(bs_qtys.d1)
                     - bs_params.K * bs_qtys.disc_r * norm.cdf(bs_qtys.d2)
                    )

        if bs_params.is_call:
            return value
        
        return value - bs_params.S * bs_qtys.disc_q + bs_params.K * bs_qtys.disc_r
        
    def greeks(self, option: Option, market: Market) -> Greeks:

        bs_params = self.get_bs_inputs(option, market)

        if bs_params.tau == 0.0 or bs_params.sigma == 0.0:
            return Greeks(delta = None, gamma = None, vega = None, theta = None, rho = None)
        
        bs_qtys = self.compute_bs_quantities(bs_params)
        
        if bs_params.is_call:

            delta = bs_qtys.disc_q * norm.cdf(bs_qtys.d1)
            
            theta = ( -(bs_params.S * bs_params.sigma 
                        * bs_qtys.disc_q * norm.pdf(bs_qtys.d1)) / (2 * np.sqrt(bs_params.tau))
                        - bs_params.r * bs_params.K * bs_qtys.disc_r * norm.cdf(bs_qtys.d2)
                        + bs_params.q * bs_params.S * bs_qtys.disc_q * norm.cdf(bs_qtys.d1)
                     ) / basis_mapping[market.basis]
            
            rho   =  bs_params.K * bs_params.tau * bs_qtys.disc_r * norm.cdf(bs_qtys.d2) / 100
        
        else:
            
            delta = bs_qtys.disc_q * (norm.cdf(bs_qtys.d1) - 1.0)
            
            theta = ( -(bs_params.S * bs_params.sigma 
                        * bs_qtys.disc_q * norm.pdf(bs_qtys.d1)) / (2 * np.sqrt(bs_params.tau))
                        + bs_params.r * bs_params.K * bs_qtys.disc_r * norm.cdf(bs_qtys.d2)
                        - bs_params.q * bs_params.S * bs_qtys.disc_q * norm.cdf(bs_qtys.d1)
                     ) / basis_mapping[market.basis]
            
            rho = -bs_params.K * bs_params.tau * bs_qtys.disc_r * norm.cdf(bs_qtys.d2) / 100

        gamma = (bs_qtys.disc_q * norm.pdf(bs_qtys.d1)) / (bs_params.S * bs_qtys.sig_sqrt_t)
        vega  = bs_qtys.disc_q * bs_params.S * norm.pdf(bs_qtys.d1) * np.sqrt(bs_params.tau) / 100

        return Greeks(delta, gamma, vega, theta, rho)


    def price_and_greeks(self, option: Option, market: Market) -> tuple[float, Greeks]:
        return self._price_impl(option, market), self.greeks(option, market)
    
@PricerFactory.register(PricerType.BLACK_SCHOLES)
def _make_black_scholes(**kw) -> Pricer:
    return BlackScholesPricer()