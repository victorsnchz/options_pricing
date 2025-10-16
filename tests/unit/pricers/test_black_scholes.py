import unittest
import sys
from datetime import date
import numpy as np

sys.path.append('src')

from src.pricers.black_scholes import BlackScholesPricer
from src import option, exercise, payoff
from src.pricers import types

""""
Control test order
"""
def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    # Choose the class order explicitly:
    for cls in (TestPriceInputs, TestBSParams, TestAtmVanillaCall, TestAtmVanillaPut):
        suite.addTests(loader.loadTestsFromTestCase(cls))
    return suite

class TestPriceInputs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pricer = BlackScholesPricer()
        cls.market = types.Market(100, 0, date(2025, 12, 31), 0, 1)

    def test_invalid_exercise(self):

        bermudan_exercise = exercise.ExerciseFactory.create(exercise.ExerciseType.BERMUDAN,
                                                        dates=(date(2025, 11, 30), )
                                                        )

        vanilla_payoff = payoff.PayoffFactory.create( payoff.PayoffType.VANILLA,
                                             direction=payoff.Direction.CALL
                                             )

        bermudan_vanilla_option = option.Option(strike = 100.0, 
                                          exercise = bermudan_exercise,
                                          payoff = vanilla_payoff
                                          )

        with self.assertRaises(NotImplementedError):
            self.pricer.price(bermudan_vanilla_option, self.market)

    @unittest.skip("need to implement more payoff schemes")        
    def test_invalid_payoff(self):

        eu_exercise = exercise.EuropeanExercise(expiry=date(2025, 11, 30))

        asian_payoff = payoff.AsianArithmeticPayoff(direction=payoff.Direction.CALL)

        amer_vanilla_option = option.Option(strike = 100.0, 
                                          exercise = eu_exercise,
                                          payoff = asian_payoff
                                          )

        with self.assertRaises(NotImplementedError):
            self.pricer.price(amer_vanilla_option, self.market)

    def test_invalid_amer_call_option_non_zero_div(self):

        amer_exercise = exercise.ExerciseFactory.create(exercise.ExerciseType.AMERICAN,
                                                        start=date(2025, 10, 30),
                                                        expiry=date(2025, 11, 30)
                                                        )

        vanilla_payoff = payoff.PayoffFactory.create( payoff.PayoffType.VANILLA,
                                             direction=payoff.Direction.CALL
                                             )

        eu_vanilla_option = option.Option(strike = 100.0, 
                                          exercise = amer_exercise,
                                          payoff = vanilla_payoff
                                          )
        
        market_non_zero_div = types.Market(100, 0, date(2025, 12, 31), 0.5, 1)

        with self.assertRaises(NotImplementedError):
            self.pricer.price(eu_vanilla_option, market_non_zero_div)

    def test_invalid_amer_put_option(self):

        amer_exercise = exercise.ExerciseFactory.create(exercise.ExerciseType.AMERICAN,
                                                        start=date(2025, 10, 30),
                                                        expiry=date(2025, 11, 30)
                                                        )

        vanilla_payoff = payoff.PayoffFactory.create( payoff.PayoffType.VANILLA,
                                             direction=payoff.Direction.PUT
                                             )

        eu_vanilla_option = option.Option(strike = 100.0, 
                                          exercise = amer_exercise,
                                          payoff = vanilla_payoff
                                          )

        with self.assertRaises(NotImplementedError):
            self.pricer.price(eu_vanilla_option, self.market)
        
    def test_valid_eu_call_option(self):

        eu_exercise = exercise.ExerciseFactory.create(exercise.ExerciseType.EUROPEAN,
                                                        expiry=date(2025, 11, 30)
                                                        )

        vanilla_payoff = payoff.PayoffFactory.create( payoff.PayoffType.VANILLA,
                                             direction=payoff.Direction.CALL
                                             )

        eu_vanilla_option = option.Option(strike = 100.0, 
                                          exercise = eu_exercise,
                                          payoff = vanilla_payoff
                                          )
        
        self.pricer.price(eu_vanilla_option, self.market)

    def test_valid_amer_call_option(self):

        amer_exercise = exercise.ExerciseFactory.create(exercise.ExerciseType.AMERICAN,
                                                        start=date(2025, 10, 30),
                                                        expiry=date(2025, 11, 30)
                                                        )

        vanilla_payoff = payoff.PayoffFactory.create( payoff.PayoffType.VANILLA,
                                             direction=payoff.Direction.CALL
                                             )

        eu_vanilla_option = option.Option(strike = 100.0, 
                                          exercise = amer_exercise,
                                          payoff = vanilla_payoff
                                          )
        
        self.pricer.price(eu_vanilla_option, self.market)

class TestBSParams(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pricer = BlackScholesPricer()
        cls.market = types.Market(spot=100, 
                                  rate = .05, 
                                  today = date(2025, 12, 1), 
                                  div = .0, 
                                  vol = .25)

        eu_exercise = exercise.EuropeanExercise(expiry=date(2025, 12, 31))
        
        vanilla_payoff = payoff.VanillaPayoff(direction=payoff.Direction.CALL)
        
        cls.vanilla_eu_call = option.Option(100, eu_exercise, vanilla_payoff)


    def test_000_bs_inputs(self):
        bs_params = self.pricer.get_bs_inputs(self.vanilla_eu_call,
                                                                    self.market)
        
        self.assertEqual(bs_params.S, 100)
        self.assertEqual(bs_params.K, 100)
        self.assertEqual(bs_params.r, .05)
        self.assertEqual(bs_params.q, .0)
        self.assertEqual(bs_params.sigma, .25)
        self.assertEqual(bs_params.tau, 30/365)
        self.assertTrue(bs_params.is_call)

    def test_001_bs_quantities(self):
        

        bs_params = self.pricer.get_bs_inputs(self.vanilla_eu_call, self.market)
        
        bs_qtys = self.pricer.compute_bs_quantities(bs_params)
        
        self.assertEqual(bs_qtys.sig_sqrt_t, np.sqrt(30/365)*bs_params.sigma)

class TestAtmVanillaCall(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pricer = BlackScholesPricer()
        cls.market = types.Market(spot=100, 
                                  rate = .05, 
                                  today = date(2025, 12, 1), 
                                  div = .0, 
                                  vol = .25)
        
        cls.vanilla_payoff = payoff.VanillaPayoff(direction=payoff.Direction.CALL)


    def test_value(self):

        eu_exercise = exercise.EuropeanExercise(expiry=date(2025, 12, 31))
        vanilla_eu_call = option.Option(100, eu_exercise, self.vanilla_payoff)
        
        value = self.pricer.price(vanilla_eu_call, self.market)

        self.assertAlmostEqual(value, 3.063, places = 3)

    def test_greeks(self):

        eu_exercise = exercise.EuropeanExercise(expiry=date(2025, 12, 31))
        vanilla_eu_call = option.Option(100, eu_exercise, self.vanilla_payoff)

        greeks = self.pricer.greeks(vanilla_eu_call, self.market)

        self.assertAlmostEqual(greeks.delta, .537, places=2)
        self.assertAlmostEqual(greeks.gamma, .055, places=2)
        self.assertAlmostEqual(greeks.vega, .114, places=2)
        self.assertAlmostEqual(greeks.theta, -.054, places=2)
        self.assertAlmostEqual(greeks.rho, .042, places=2)


    def test_implied_vol(self):

        eu_exercise = exercise.EuropeanExercise(expiry=date(2025, 12, 31))
        vanilla_eu_call = option.Option(100, eu_exercise, self.vanilla_payoff)

        iv = self.pricer.implied_vol(vanilla_eu_call, self.market, target_price=3)
        self.assertAlmostEqual(.2445, iv, places=3)


class TestAtmVanillaPut(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pricer = BlackScholesPricer()
        cls.market = types.Market(spot=100, 
                                  rate = .05, 
                                  today = date(2025, 12, 1), 
                                  div = .0, 
                                  vol = .25)
        
        cls.vanilla_payoff = payoff.VanillaPayoff(direction=payoff.Direction.PUT)


    def test_value(self):

        eu_exercise = exercise.EuropeanExercise(expiry=date(2025, 12, 31))
        vanilla_eu_put = option.Option(100, eu_exercise, self.vanilla_payoff)
        
        value = self.pricer.price(vanilla_eu_put, self.market)

        self.assertAlmostEqual(value, 2.652, places = 3)

    def test_greeks(self):

        eu_exercise = exercise.EuropeanExercise(expiry=date(2025, 12, 31))
        vanilla_eu_put = option.Option(100, eu_exercise, self.vanilla_payoff)

        greeks = self.pricer.greeks(vanilla_eu_put, self.market)

        self.assertAlmostEqual(greeks.delta, -.463, places=2)
        self.assertAlmostEqual(greeks.gamma, .055, places=2)
        self.assertAlmostEqual(greeks.vega, .114, places=2)
        self.assertAlmostEqual(greeks.theta, -.041, places=2)
        self.assertAlmostEqual(greeks.rho, -.041, places=2)

    def test_implied_vol(self):

        eu_exercise = exercise.EuropeanExercise(expiry=date(2025, 12, 31))
        vanilla_eu_put = option.Option(100, eu_exercise, self.vanilla_payoff)

        iv = self.pricer.implied_vol(vanilla_eu_put, self.market, target_price=3)
        self.assertAlmostEqual(.2805, iv, places=
                               3)




    

if __name__ == '__main__':
    unittest.main(verbosity = 2)