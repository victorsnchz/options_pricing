import unittest
import sys

sys.path.append('src')
from src.payoff import PayoffFactory, Direction, PayoffType, VanillaPayoff, PayoffContext

class TestPayoffFactory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.factory = PayoffFactory()

    def test_make_vanilla(self):
        
        direction = Direction.CALL
        payoff = self.factory.create(PayoffType.VANILLA, direction)
        self.assertTrue(isinstance(payoff, VanillaPayoff))

class TestPayoffVanilla(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.factory = PayoffFactory()
        cls.payoff_context = PayoffContext(100.0, None)

    def test_value_call_vanilla(self):
        
        direction = Direction.CALL
        payoff = self.factory.create(PayoffType.VANILLA, direction)

        self.assertEqual(payoff.value(strike=100.0, ctx = self.payoff_context), 0)
        self.assertEqual(payoff.value(strike=101.0, ctx = self.payoff_context), 0)
        self.assertEqual(payoff.value(strike=99.0, ctx = self.payoff_context), 1.0)


if __name__ == '__main__':
    unittest.main()