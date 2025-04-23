from abc import ABC, abstractmethod

import dateutil.relativedelta
from src.bookkeeping import OptionType, ExerciseType, PayoffType, PricerType
from src.option import Option, Put, Call

import dateutil
from scipy import stats
import datetime
import numpy as np

class Pricer(ABC):
    @classmethod
    def can_price(cls, option) -> bool:
        """Check if pricer supports this specific option."""
        raise NotImplementedError

    @abstractmethod
    def calculate_value(self) -> float:
        """Return option price given set of parameters."""
        pass

class BlackScholesPricer(Pricer):
    @classmethod
    def can_price(cls, option: Option):
        return (
                option.exercise_type == ExerciseType.EUROPEAN 
                and option.payoff_type == PayoffType.VANILLA
                )

    _norm_cdf = stats.norm(0, 1).cdf
    _norm_pdf = stats.norm(0, 1).pdf

    def _d1(self, S, K, T, r, sigma):
        return (np.log(S / K) + (r + 0.5 * sigma**2 ) / (sigma * np.sqrt(T) ))

    def _d2(self, S, K, T, r, sigma):
        return self._d1(S, K, T, r, sigma) - sigma * np.sqrt(T)

    def calculate_value(self, option: Option,  
                        S: float, r: float,
                        sigma: float,
                        t0: datetime.date = datetime.date.today()
                        ):

        """ Compute fair value of a vanilla European option with payoff max(K-S, 0) at 
            expiry under BS model. 
            
            Parameters
            ----------

            option : Option 
                    Option-contract specifications

            S : float
                Underlying-asset spot price.

            r : float
                Risk-free rate assumed constant to expiry.

            sigma : float
                    of underlying-asset price-process.   
            
            t0 : datetime.datetime
                 Date from which to compute time-to-expiry.

            Returns
            -------
            put_value : float
                        Fair present value of the option.
        
        """
        
        delta_t = dateutil.relativedelta.relativedelta(option.expiry, t0)
        T = delta_t.years + delta_t.months / 12 + delta_t.days / 365.2425

        K = option.strike


        if type(option) == Put:
            self._put_value(option, S, K, T, r, sigma)

        return self._call_value(option, S, K, T, r, sigma)

    def _put_value(self, option: Option, S: float, K: float, r: float, T: float, 
                   sigma: float) -> float:
        
        """ Compute fair value of a vanilla European put option with payoff max(K-S, 0) at expiry 
            under BS model. 
            
            Parameters
            ----------
            S : float
                Value of underling asset.
            
            K : float
                Option-strike price.
            
            T: float
                Time-to-expiry in years.
            
            r : float
                Risk-free rate assumed constant until expiry.

            sigma : float
                    Volatility of underlying asset price-process.
            
            Returns
            -------
            put_value : float
                        Fair present value of the put-option.
        
        """
        
        return (
                np.exp(-r * T) * K * self._norm_cdf(-self._d2(S, K, T, r, sigma))
                - S * self._norm_cdf(-self._d1(S, K, T, r, sigma))
                )
    
    def _call_value(self, option: Option, S: float, K: float, r: float, T: float, 
                   sigma: float) -> float:
        

        """ Compute fair value of a vanilla European call option with payoff max(K-S, 0) at expiry 
            under BS model. 
            
            Parameters
            ----------
            S : float
                Value of underling asset.
            
            K : float
                Option-strike price.
            
            T: float
                Time-to-expiry in years.
            
            r : float
                Risk-free rate assumed constant until expiry.

            sigma : float
                    Volatility of underlying asset price-process.
            
            Returns
            -------
            put_value : float
                        Fair present value of the call-option.
        
        """
        
        return (
                S * self._norm_cdf(self._d1(S, K, T, r, sigma)) - 
                K * np.exp(-r * T) * self._norm_cdf(self._d2(S, K, T, r, sigma))  
                )

class MonteCarloPricer(Pricer):
    @classmethod
    def can_price(cls, option):
        return (
                option.exercise in (ExerciseType.AMERICAN, ExerciseType.BERMUDAN)  
                and option.payoff in (PayoffType.ASIAN, PayoffType.BARRIER)
                )
    
    def calculate_value(self):
        pass

class FiniteDifferencePricer(Pricer):
    pass

class BinomialTreePricer(Pricer):
    pass

class FourierPricer(Pricer):
    pass
    

class PricerFactory:
    _pricers = {
        PricerType.MonteCarloPricer: MonteCarloPricer,
        PricerType.BlackScholesPricer: BlackScholesPricer
    }

    @classmethod
    def get_pricer(cls, pricer_type: PricerType, option: Option):
        
        if pricer_type not in cls._pricers:
            raise NotImplementedError(f'{pricer_type} not implement yet.')
        
        pricer_cls = cls._pricers[pricer_type]()

        if pricer_cls.can_price(option): return pricer_cls
        raise ValueError(f'No pricer found for {option}')