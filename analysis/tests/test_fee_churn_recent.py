import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from extend_fee_churn_recent import interval_counts


class RecentCountsTest(unittest.TestCase):
    def test_positive_anywhere_refutes_absence(self):
        result = interval_counts({"a", "b", "c"}, {"b", "c", "external"})
        self.assertEqual(result["missing_ids"], 1)
        self.assertIsNone(result["reobserved_next_vintage"])
        self.assertIsNone(result["still_missing_next_vintage"])

    def test_returns_only_count_previously_missing_baseline_members(self):
        result = interval_counts({"a", "b", "c", "d"}, {"b"}, {"a", "b", "new"})
        self.assertEqual(result["reobserved_next_vintage"], 1)
        self.assertEqual(result["still_missing_next_vintage"], 2)
        self.assertEqual(result["disappearance_rate"], .75)

    def test_empty_followup_is_distinct_from_unobserved_followup(self):
        result = interval_counts({"a"}, set(), set())
        self.assertEqual(result["reobserved_next_vintage"], 0)
        self.assertEqual(result["still_missing_next_vintage"], 1)
        with self.assertRaises(ValueError):
            interval_counts(set(), {"a"})


if __name__ == "__main__":
    unittest.main()
