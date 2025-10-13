import unittest
import sys

sys.path.append('src')
from src.payoff import PayoffFactory, Direction, PayoffType, VanillaPayoff

class TestPayoffFactory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.factory = PayoffFactory()

    def test_make_vanilla(self):
        
        direction = Direction.CALL
        payoff = self.factory.create(PayoffType.VANILLA, direction)
        self.assertTrue(isinstance(payoff, VanillaPayoff))

if __name__ == '__main__':
    unittest.main()