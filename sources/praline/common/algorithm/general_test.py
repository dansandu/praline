from praline.common.algorithm.general import cartesian_product
from unittest import TestCase


class GeneralTest(TestCase):
    def test_cartesian_product(self):
        result = cartesian_product([['a', 'b', 'c'], ['1', '2'], ['A', 'B']])

        expected_result = [
            ['a', '1', 'A'],
            ['b', '1', 'A'],
            ['c', '1', 'A'],
            ['a', '2', 'A'],
            ['b', '2', 'A'],
            ['c', '2', 'A'],
            ['a', '1', 'B'],
            ['b', '1', 'B'],
            ['c', '1', 'B'],
            ['a', '2', 'B'],
            ['b', '2', 'B'],
            ['c', '2', 'B']
        ]

        self.assertEqual(result, expected_result)
