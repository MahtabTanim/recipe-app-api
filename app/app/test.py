"""
Sample tests for calculate module
"""

from django.test import SimpleTestCase
from . import calc


class CalcTests(SimpleTestCase):
    def test_calc_add(self):
        res = calc.add(5, 7)
        self.assertEqual(res, 12)

    def test_calc_sub(self):
        """Test subtracting y from x"""
        res = calc.subtract(5, 7)
        self.assertEqual(res, 2)
