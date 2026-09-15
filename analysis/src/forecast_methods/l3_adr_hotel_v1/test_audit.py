"""Contract tests for analytical failure modes, separate from source reproduction."""
import importlib.util
from pathlib import Path
import unittest
import tempfile
import numpy as np
import pandas as pd

spec = importlib.util.spec_from_file_location("audit", Path(__file__).with_name("run.py"))
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def test_existing_output_is_rejected_without_touching_sentinel(self):
        with tempfile.TemporaryDirectory() as td:
            sentinel = Path(td) / "sentinel.txt"
            sentinel.write_text("preserve", encoding="utf-8")
            with self.assertRaises(FileExistsError):
                audit.run(td)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve")
            self.assertEqual([p.name for p in Path(td).iterdir()], ["sentinel.txt"])

    def test_pairwise_alignment_excludes_missing_and_infinite(self):
        r = audit.paired_score([1, 2, 3, 4], [2, np.nan, np.inf, 5], [3, 4, 5, 6])
        self.assertEqual(r["n"], 2)
        self.assertAlmostEqual(r["ratio_vs_naive"], .5)

    def test_zero_benchmark_is_unavailable_not_a_win(self):
        r = audit.paired_score([1, 2], [1, 3], [1, 2])
        self.assertTrue(np.isnan(r["ratio_vs_naive"]))
        self.assertEqual(r["baseline_status"], "zero_or_missing_rmse")

    def test_intervals_include_boundaries(self):
        r = audit.paired_score([2, 2, 2, 2], [1.5, 2.5, 1, 3], [1, 1, 3, 3], .5)
        self.assertAlmostEqual(r["rmse_pp"], np.sqrt(.125))
        self.assertAlmostEqual(r["ratio_vs_naive"], np.sqrt(.5))

    def test_shape_mismatch_and_negative_width_rejected(self):
        with self.assertRaises(ValueError):
            audit.paired_score([1], [1, 2], [1])
        with self.assertRaises(ValueError):
            audit.paired_score([1], [1], [1], -.5)

    def test_all_missing_remains_missing(self):
        r = audit.paired_score([np.nan], [2], [1])
        self.assertEqual(r["n"], 0)
        self.assertTrue(np.isnan(r["rmse_pp"]))

    def test_complete_quarter_only(self):
        d = pd.DataFrame({"month": ["2026-01", "2026-02", "2026-03", "2026-04"], "cpi": [1,2,3,9], "bea": [1,np.nan,3,9]})
        q = audit.complete_quarters(d).set_index("quarter")
        self.assertEqual(q.loc["2026Q1", "cpi"], 2)
        self.assertEqual(q.loc["2026Q1", "bea_months"], 2)
        self.assertTrue(np.isnan(q.loc["2026Q1", "bea"]))
        self.assertTrue(np.isnan(q.loc["2026Q2", "cpi"]))

    def test_duplicate_month_rejected(self):
        with self.assertRaises(ValueError):
            audit.complete_quarters(pd.DataFrame({"month": ["2026-01", "2026-01"], "x": [1,2]}))

    def test_date_leakage_rejected(self):
        audit.check_information_date("2026-09-13")
        for d in ["2026-09-14", None]:
            with self.assertRaises(ValueError):
                audit.check_information_date(d)

    def row(self):
        return dict(quarter="2026Q3", metric="adr_reported_yoy", scenario="s", value=3., lower=2., upper=4.,
                    units="percentage_points", information_date="2026-09-13", evidence_status="scenario",
                    source_reference="source.csv", treatment="replacement", baseline_replaced="same-quarter ADR",
                    embedded_fx="already embedded", limitations="do not add FX again")

    def test_adapter_requires_replacement_and_fx_metadata(self):
        audit.validate_adapter(pd.DataFrame([self.row()]))
        for field in ["baseline_replaced", "embedded_fx", "limitations"]:
            row = self.row(); row[field] = ""
            with self.assertRaises(ValueError):
                audit.validate_adapter(pd.DataFrame([row]))

    def test_duplicate_adapter_key_rejected(self):
        with self.assertRaises(ValueError):
            audit.validate_adapter(pd.DataFrame([self.row(), self.row()]))

    def test_contemporaneous_revenue_cannot_be_exported_as_forecast(self):
        row = self.row(); row["metric"] = "revenue_musd_same_q_take"
        with self.assertRaises(ValueError):
            audit.validate_adapter(pd.DataFrame([row]))

    def test_bad_bounds_rejected(self):
        row = self.row(); row["lower"] = 5
        with self.assertRaises(ValueError):
            audit.validate_adapter(pd.DataFrame([row]))


if __name__ == "__main__":
    unittest.main()
