"""Test analytical failure modes using explicitly synthetic aggregate counts."""

from copy import deepcopy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from audit_listing_churn_inputs import audit


class ChurnAuditTests(unittest.TestCase):
    def setUp(self):
        self.snapshots = [
            {"city": "synthetic", "dump_date": "2024-01-01", "listings": "100", "partial_scope": "False"},
            {"city": "synthetic", "dump_date": "2025-01-01", "listings": "110", "partial_scope": "False"},
        ]
        self.pairs = [{
            "city": "synthetic", "pair_type": "year_ago", "date_a": "2024-01-01",
            "date_b": "2025-01-01", "days_apart": "366", "ids_a": "100", "ids_b": "110",
            "matched": "80", "exits": "20", "gross_adds": "30", "retention": "0.8000",
            "new_share_b": "0.2727",
        }]

    def test_counts_rates_and_unknown_destinations(self):
        rows, _ = audit(self.snapshots, self.pairs)
        self.assertEqual(rows[0]["interval_id_absence_rate"], 0.2)
        self.assertEqual(rows[0]["net_listing_change_rate"], 0.1)
        self.assertEqual(rows[0]["coverage_screen"], "review_required_no_endpoint_flag")
        self.assertIsNone(rows[0]["property_churn_rate"])
        self.assertIsNone(rows[0]["sale_share"])

    def test_partial_scope_is_rejected_not_measured_as_churn(self):
        self.snapshots[0]["partial_scope"] = "True"
        rows, summary = audit(self.snapshots, self.pairs)
        self.assertEqual(rows[0]["coverage_screen"], "reject_flagged_scope")
        self.assertEqual(summary["latest_pairs_with_endpoint_scope_flag"], 1)

    def test_stock_flow_error_fails(self):
        self.pairs[0]["exits"] = "19"
        with self.assertRaises(ValueError):
            audit(self.snapshots, self.pairs)

    def test_duplicate_snapshot_fails(self):
        with self.assertRaises(ValueError):
            audit(self.snapshots + [deepcopy(self.snapshots[0])], self.pairs)

    def test_duplicate_pair_fails(self):
        with self.assertRaises(ValueError):
            audit(self.snapshots, self.pairs * 2)

    def test_wrong_interval_fails(self):
        self.pairs[0]["days_apart"] = "365"
        with self.assertRaises(ValueError):
            audit(self.snapshots, self.pairs)

    def test_missing_snapshot_fails(self):
        with self.assertRaises(KeyError):
            audit(self.snapshots[:1], self.pairs)

    def test_zero_denominator_is_undefined(self):
        self.snapshots[0]["listings"] = "0"
        self.pairs[0].update(ids_a="0", matched="0", exits="0", gross_adds="110", retention="", new_share_b="1")
        rows, _ = audit(self.snapshots, self.pairs)
        self.assertIsNone(rows[0]["interval_id_absence_rate"])
        self.assertEqual(rows[0]["coverage_screen"], "undefined_zero_baseline")

    def test_ambiguous_scope_flag_fails(self):
        self.snapshots[0]["partial_scope"] = "unknown"
        with self.assertRaises(ValueError):
            audit(self.snapshots, self.pairs)

    def test_nonfinite_retention_fails(self):
        self.pairs[0]["retention"] = "NaN"
        with self.assertRaises(ValueError):
            audit(self.snapshots, self.pairs)


if __name__ == "__main__":
    unittest.main()
