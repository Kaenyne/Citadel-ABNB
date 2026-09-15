import importlib.util
import math
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("ge_integration",Path(__file__).with_name("run.py"))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


class ConversionTest(unittest.TestCase):
    def test_q2_requires_q1_not_same_quarter(self):
        x={"2026Q4":24000.0,"2027Q1":32000.0,"2027Q2":999999.0}
        r=m.conversion("2027Q2",x,.14,.02)
        self.assertAlmostEqual(r["revenue_musd"],(32000*2/3+24000/3)*.14)
        x["2027Q2"]=1.0
        self.assertEqual(r,m.conversion("2027Q2",x,.14,.02))
        del x["2027Q1"]
        with self.assertRaisesRegex(ValueError,"2027Q1"):m.conversion("2027Q2",x,.14,.02)

    def test_cushion_changes_guide_not_revenue(self):
        x={"2026Q2":27200.0,"2026Q3":26000.0}
        a=m.conversion("2026Q4",x,.12,0)
        b=m.conversion("2026Q4",x,.12,.04)
        self.assertEqual(a["revenue_musd"],b["revenue_musd"])
        self.assertAlmostEqual(a["implied_guide_musd"]/1.04,b["implied_guide_musd"])

    def test_rejects_missing_invalid_and_out_of_scope(self):
        x={"2026Q2":27200.0,"2026Q3":26000.0}
        for lam,c in [(float("nan"),.02),(0,.02),(.12,-1)]:
            with self.assertRaises(ValueError):m.conversion("2026Q4",x,lam,c)
        with self.assertRaises(ValueError):m.conversion("2028Q1",x,.12,.02)

    def test_four_quarters_and_preserved_reference(self):
        d=m.prepare()
        self.assertEqual([x["quarter"] for x in d["forecast"]],m.TARGETS)
        self.assertTrue(all(abs(x["difference_musd"])<1e-7 for x in d["preservation"]))
        self.assertTrue(math.isfinite(d["forecast"][-1]["implied_guide_musd"]))
        self.assertEqual(d["forecast"][0]["guide_kind"],"already_issued_diagnostic")


if __name__=="__main__":unittest.main()
