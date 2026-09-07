"""Check planning magnitudes and invalid-input behavior, not achieved power."""
import importlib.util
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'src/hotel_statistical_design.py'
SPEC = importlib.util.spec_from_file_location('hotel_statistical_design', SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class StatisticalDesignTests(unittest.TestCase):
    def test_known_normal_approximation(self):
        self.assertEqual(MODULE.hotels_per_group(0.10, 1.0), 1570)
        self.assertEqual(MODULE.hotels_per_group(0.20, 1.0), 393)
        self.assertLessEqual(MODULE.minimum_detectable_effect(1570, 1.0), 0.10)

    def test_more_variation_and_smaller_effect_need_more_hotels(self):
        self.assertGreater(MODULE.hotels_per_group(0.1, 1.5), MODULE.hotels_per_group(0.1, 1.0))
        self.assertGreater(MODULE.hotels_per_group(0.05, 1.0), MODULE.hotels_per_group(0.1, 1.0))
        self.assertLess(MODULE.minimum_detectable_effect(1000, 1), MODULE.minimum_detectable_effect(100, 1))

    def test_invalid_inputs_are_not_silently_zeroed(self):
        for effect, cv in [(0,1),(-0.1,1),(0.1,0),(float('nan'),1),(0.1,float('inf'))]:
            with self.assertRaises(ValueError):
                MODULE.hotels_per_group(effect, cv)
        for alpha, power in [(0,.8),(.05,1),(.05,.5),(1,.8)]:
            with self.assertRaises(ValueError):
                MODULE.hotels_per_group(.1,1,alpha,power)
        with self.assertRaises(ValueError):
            MODULE.minimum_detectable_effect(1,1)


if __name__ == '__main__':
    unittest.main()
