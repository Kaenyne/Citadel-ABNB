import importlib.util
from pathlib import Path
import sys
import unittest

SPEC = importlib.util.spec_from_file_location("lane4_card_scoring", Path(__file__).resolve().parents[1] / "scoring.py")
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)


class CardRules(unittest.TestCase):
    def setUp(self):
        self.base = (2 * 27200 + 29200) / 3
        self.warn = self.base * 17.09 / 100
        self.escalate = self.base * 16.93 / 100

    def alarm(self, x):
        return m.lambda_alarm(x, self.base, 17.09, 16.93)

    def test_integer_warning_boundary_is_ambiguous(self):
        self.assertEqual(self.alarm(m.Interval.reported(4762, 1)), "AMBIGUOUS")
        self.assertEqual(self.alarm(m.Interval.reported(4763, 1)), "NO ALARM")

    def test_integer_escalation_boundary_is_ambiguous(self):
        self.assertEqual(self.alarm(m.Interval.reported(4718, 1)), "AMBIGUOUS")
        self.assertEqual(self.alarm(m.Interval.reported(4717, 1)), "ESCALATE")
        self.assertEqual(self.alarm(m.Interval.reported(4719, 1)), "WARN")

    def test_exact_thresholds_are_inclusive(self):
        self.assertEqual(self.alarm(m.Interval(self.warn, self.warn)), "NO ALARM")
        self.assertEqual(self.alarm(m.Interval(self.escalate, self.escalate)), "WARN")

    def test_missing_input_is_absent(self):
        self.assertEqual(self.alarm(None), "ABSENT")
        self.assertEqual(m.conditional_refutation(None, None, None), "ABSENT")

    def test_growth_uses_both_rounding_intervals(self):
        result = m.growth(m.Interval.reported(7570, 1), m.Interval.reported(7209, 1))
        self.assertLess(result.low, 5)
        self.assertGreater(result.high, 5)
        self.assertEqual(m.band_membership(result, 5, 11), "AMBIGUOUS")

    def test_zero_or_negative_denominator_rejected(self):
        with self.assertRaises(ValueError):
            m.ratio(m.Interval(1, 2), m.Interval(0, 1))

    def test_invalid_intervals_rejected(self):
        for a, b in [(2, 1), (float("nan"), 2), (1, float("inf"))]:
            with self.assertRaises(ValueError):
                m.Interval(a, b)

    def test_refutation_gap_strictly_above_minus_eight(self):
        self.assertEqual(m.conditional_refutation(m.Interval(17.1, 17.2), m.Interval(-8, -7), "at_least_low"), "INCONCLUSIVE")
        self.assertEqual(m.conditional_refutation(m.Interval(17.1, 17.2), m.Interval(-7.99, -7), "at_least_low"), "PROPOSED REFUTATION CONDITION MET")

    def test_refutation_requires_all_three(self):
        self.assertEqual(m.conditional_refutation(m.Interval(17, 17.2), m.Interval(-7, -6), "at_least_low"), "INCONCLUSIVE")
        self.assertEqual(m.conditional_refutation(m.Interval(17.1, 17.2), m.Interval(-7, -6), "ambiguous"), "INCONCLUSIVE")

    def test_phrase_not_implicitly_mapped(self):
        with self.assertRaises(ValueError):
            m.conditional_refutation(m.Interval(17.1, 17.2), m.Interval(-7, -6), 10.0)

    def test_overlapping_comparisons_not_directional(self):
        self.assertEqual(m.versus(m.Interval(3100, 3150), m.Interval(3149, 3151)), "OVERLAPS")


if __name__ == "__main__":
    unittest.main()
