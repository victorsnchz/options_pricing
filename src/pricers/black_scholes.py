from dataclasses import dataclass, field
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

    # quantities place-holders, will be over-written by post_init
    sig_sqrt_t: float = field(init=False)
    d1: float = field(init=False)
    d2: float = field(init=False)
    disc_q: float = field(init=False)
    disc_r: float = field(init=False)


    def __post_init__(self):

        sig_sqrt_t = self.sigma * np.sqrt(self.tau)

        d1 = d2 = 0.0
        
        if self.tau >=0 and sig_sqrt_t > 0 and self.K > 0:

            d1 = ( np.log(self.S / self.K)
                + (self.r - self.q + 0.5 * self.sigma**2) * self.tau
                ) / sig_sqrt_t 
            
            d2 = d1 - sig_sqrt_t
            
        disc_q, disc_r = np.exp(-self.q * self.tau), np.exp(-self.r * self.tau)

        object.__setattr__(self, 'sig_sqrt_t', sig_sqrt_t)
        object.__setattr__(self, 'd1', d1)
        object.__setattr__(self, 'd2', d2)
        object.__setattr__(self, 'disc_q', disc_q)
        object.__setattr__(self, 'disc_r', disc_r)

class BlackScholesPricer(Pricer):

    def is_supported(self, option: Option, market: Market) -> bool:

        is_vanilla_european = ( isinstance(option.exercise, EuropeanExercise) 
                               and isinstance(option.payoff, VanillaPayoff) 
                               )
        
        is_vanilla_american_call_no_div = ( isinstance(option.exercise, AmericanExercise) 
                                    and isinstance(option.payoff, VanillaPayoff) 
                                    and option.direction == Direction.CALL
                                    and market.div == 0.0
                                    )

        return (
            is_vanilla_european or is_vanilla_american_call_no_div
        )
    
    def is_valid_market_data(self, market) -> bool:
        
        if market.vol is None:
            raise ValueError(f'Must provide a volatility value for ' + 
                             'Black-Scholes model.')

    def get_bs_inputs(self, option: Option, market: Market) -> BSParameters:

        """
        TODO    
        is this really usefeul?
        make an abstract model_params class -> all pricers use option + mkt to instantiate
        their own model_params dataclasss?
        delegate checks to model_params?

        """
        
        S = float(market.spot)
        K = float(option.strike)
        r = float(market.rate)
        q = float(market.div)
        tau = max(0.0, year_fraction(market.today, option.exercise.expiry, market.basis))
        is_call = (option.direction is Direction.CALL)
        sigma = float(market.vol)

        return BSParameters(S, K, r, q, tau, is_call, sigma)

    def _price_impl(self, option: Option, market: Market) -> float:
        
        bs_params = self.get_bs_inputs(option, market)

        # "immediate" exercise
        if bs_params.tau == 0.0 or bs_params.sigma == 0.0: 
            return option.payoff.value(bs_params.K, 
                                       PayoffContext(spot=bs_params.S))

        value = (bs_params.S * bs_params.disc_q * norm.cdf(bs_params.d1)
                     - bs_params.K * bs_params.disc_r * norm.cdf(bs_params.d2)
                    )

        if bs_params.is_call:
            return value
        
        return value - bs_params.S * bs_params.disc_q + bs_params.K * bs_params.disc_r
        
    def greeks(self, option: Option, market: Market) -> Greeks:

        bs_params = self.get_bs_inputs(option, market)

        if bs_params.tau == 0.0 or bs_params.sigma == 0.0:
            return Greeks(delta = None, gamma = None, vega = None, theta = None, rho = None)
        
        if bs_params.is_call:

            delta = bs_params.disc_q * norm.cdf(bs_params.d1)
            
            theta = ( -(bs_params.S * bs_params.sigma 
                        * bs_params.disc_q * norm.pdf(bs_params.d1)) / (2 * np.sqrt(bs_params.tau))
                        - bs_params.r * bs_params.K * bs_params.disc_r * norm.cdf(bs_params.d2)
                        + bs_params.q * bs_params.S * bs_params.disc_q * norm.cdf(bs_params.d1)
                     ) / basis_mapping[market.basis]
            
            rho   =  bs_params.K * bs_params.tau * bs_params.disc_r * norm.cdf(bs_params.d2) / 100
        
        else:
            
            delta = bs_params.disc_q * (norm.cdf(bs_params.d1) - 1.0)
            
            theta = ( -(bs_params.S * bs_params.sigma 
                        * bs_params.disc_q * norm.pdf(bs_params.d1)) / (2 * np.sqrt(bs_params.tau))
                        + bs_params.r * bs_params.K * bs_params.disc_r * norm.cdf(bs_params.d2)
                        - bs_params.q * bs_params.S * bs_params.disc_q * norm.cdf(bs_params.d1)
                     ) / basis_mapping[market.basis]
            
            rho = -bs_params.K * bs_params.tau * bs_params.disc_r * norm.cdf(bs_params.d2) / 100

        gamma = (bs_params.disc_q * norm.pdf(bs_params.d1)) / (bs_params.S * bs_params.sig_sqrt_t)
        vega  = bs_params.disc_q * bs_params.S * norm.pdf(bs_params.d1) * np.sqrt(bs_params.tau) / 100

        return Greeks(delta, gamma, vega, theta, rho)

    def price_and_greeks(self, option: Option, market: Market) -> tuple[float, Greeks]:
        return self._price_impl(option, market), self.greeks(option, market)
    
@PricerFactory.register(PricerType.BLACK_SCHOLES)
def _make_black_scholes(**kw) -> Pricer:
    return BlackScholesPricer()