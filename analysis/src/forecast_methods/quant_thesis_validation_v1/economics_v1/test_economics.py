"""Edge and economic invariant checks; no historical parameter estimation."""
import importlib.util
import math
import unittest
from datetime import date
from pathlib import Path

SPEC=importlib.util.spec_from_file_location('q7_economic_bridge',Path(__file__).with_name('run.py'))
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class EconomicsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inp, cls.annual, cls.vals, cls.comp, _=M.load_inputs()
        cls.rows={r['year']:r for r in cls.annual if r['scenario']==M.CASE}

    def test_independent_annual_controls(self):
        checks=M.reconcile(self.inp,self.annual,self.vals)
        self.assertGreater(len(checks),500)
        self.assertTrue(all(x['passes'] for x in checks))

    def test_endpoint_boundary_reconciles_committed_balances(self):
        r26,r27=self.rows[2026],self.rows[2027]
        for at,r in ((date(2026,12,31),r26),(date(2027,12,31),r27)):
            cash,shares,_=M.endpoint(at,r26,r27,16.5)
            self.assertAlmostEqual(cash,r['net_cash'],places=8)
            self.assertAlmostEqual(shares,r['shares'],places=8)
        with self.assertRaises(ValueError):
            M.endpoint(date(2028,1,1),r26,r27,16.5)

    def test_one_quarter_does_not_create_future_earnings(self):
        r=self.rows[2027]
        x=M.impact(r,self.inp['inputs']['2027'],self.inp['globals'],0.,.5,'proportional')
        self.assertTrue(all(abs(v)<1e-9 for v in x.values()))

    def test_sbc_cash_issuance_and_earnings_are_distinct(self):
        r=self.rows[2027];i=self.inp['inputs']['2027'];g=self.inp['globals']
        fixed=M.impact(r,i,g,20.,0.,'fixed')
        prop=M.impact(r,i,g,20.,0.,'proportional')
        self.assertAlmostEqual(fixed['fcf_gap_usdm'],prop['fcf_gap_usdm'])
        self.assertLess(prop['net_income_gap_usdm'],fixed['net_income_gap_usdm'])
        self.assertGreater(prop['net_issuance_gap_m'],0.)
        self.assertAlmostEqual(prop['retained_corporate_cash_gap_usdm'],prop['fcf_gap_usdm']-prop['withholding_gap_usdm'])
        self.assertAlmostEqual(prop['sbc_gap_usdm'],prop['withholding_gap_usdm']+r['price']*prop['net_issuance_gap_m'])

    def test_fully_offset_core_cash_cost_does_not_become_positive_operating_profit(self):
        r=self.rows[2026]
        x=M.impact(r,self.inp['inputs']['2026'],self.inp['globals'],20.,1.,'fixed')
        self.assertAlmostEqual(x['operating_income_gap_usdm'],0.,places=8)
        self.assertLess(x['fcf_gap_usdm'],0.)

    def test_margin_cap_protects_counterfactual(self):
        r=dict(self.rows[2027]);r['adj_uncapped']=r['revenue']*.6;r['adj_ebitda']=r['revenue']*.38
        x=M.impact(r,self.inp['inputs']['2027'],self.inp['globals'],20.,0.,'fixed')
        self.assertAlmostEqual(x['adj_ebitda_gap_usdm'],20*.38,places=8)

    def test_bad_inputs_are_rejected(self):
        with self.assertRaises(ValueError):M.positive(0,'shares')
        with self.assertRaises(ValueError):M.finite(math.nan,'input')
        with self.assertRaises(ValueError):M.impact(self.rows[2027],self.inp['inputs']['2027'],self.inp['globals'],1.,.3,'fixed')
        with self.assertRaises(ValueError):M.run(M.BASE/'another_package')


if __name__=='__main__':unittest.main()
