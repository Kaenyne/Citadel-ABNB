import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))
SPEC = importlib.util.spec_from_file_location("lane4_review_runner", PACKAGE / "run.py")
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class ReviewIntegrity(unittest.TestCase):
    def test_cash_flow_and_sbc_are_separate(self):
        row = dict(adj_ebitda=100, interest_income=10, interest_expense=5,
                   cash_taxes=15, d_unearned=3, wc_resid=-2, capex=6,
                   fcf=85, sbc=20, sbc_adj_fcf=65)
        m.validate_financial_row(row)
        row["fcf"] = 105  # Adding SBC a second time must fail.
        with self.assertRaises(ValueError):
            m.validate_financial_row(row)

    def test_ev_equity_per_share_units_reconcile(self):
        row = dict(exit_multiple=10, fy27_ebitda_musd=100, fy27_net_cash_musd=50,
                   fy27_shares_m=100, enterprise_value_musd=1000,
                   equity_value_musd=1050, value_per_share=10.5)
        m.validate_valuation_row(row)
        row["equity_value_musd"] = 1000  # Omitting net cash must fail.
        with self.assertRaises(ValueError):
            m.validate_valuation_row(row)

    def test_snapshot_is_new_and_byte_identical(self):
        with tempfile.TemporaryDirectory() as folder:
            source, target = Path(folder) / "source", Path(folder) / "snapshot"
            source.mkdir()
            (source / "input.csv").write_bytes(b"x,y\r\n1,2\r\n")
            manifest = []
            m.snapshot(source, target, ["input.csv"], manifest)
            self.assertEqual((source / "input.csv").read_bytes(), (target / "input.csv").read_bytes())
            self.assertEqual(manifest[0]["sha256"], m.digest(target / "input.csv"))
            with self.assertRaises(FileExistsError):
                m.snapshot(source, target, ["input.csv"], [])

    def test_duplicate_or_missing_scenario_refused(self):
        with self.assertRaises(ValueError):
            m.one([dict(scenario="a"), dict(scenario="a")], scenario="a")
        with self.assertRaises(ValueError):
            m.one([dict(scenario="a")], scenario="b")

    def test_unavailable_numbers_not_zero_filled(self):
        for value in ("", None, "NaN", "inf"):
            with self.assertRaises((ValueError, TypeError)):
                m.num({"point": value}, "point")


if __name__ == "__main__":
    unittest.main()
