import copy, importlib.util, os, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('l4model',HERE/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class ModelTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.d=m.prepare(Path(os.environ.get('L4_REVENUE_DIR',str(m.ROOT/'data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1'))))
 def test_legacy_reproduction(self):
  r=m.replicate_legacy();self.assertAlmostEqual(r['ebitda_lens'],180.876286,places=3);self.assertAlmostEqual(r['six_lens_mean'],156.786845,places=3)
 def test_cash_and_share_roll(self):
  d=self.d;g=d['globals'];a=d['cases'][0]['annual'][0]
  self.assertAlmostEqual(a['net_cash'],g['net_cash_2q26']+a['fcf']-d['h1']['fcf']-(a['buybacks']-d['h1']['buybacks'])-(a['withholding']-d['h1']['withholding']))
  expected=g['shares_2q26']-(a['buybacks']-d['h1']['buybacks'])/a['price']+(a['sbc']-d['h1']['sbc'])/a['price']*(1-g['withholding_pct'])
  self.assertAlmostEqual(a['shares'],expected)
 def test_no_double_da(self):
  for c in self.d['cases']:
   for a in c['annual']:self.assertAlmostEqual(a['op_income'],a['adj_ebitda']-a['sbc']-a['addbacks'])
 def test_operating_identity_and_k0_cost_proxy(self):
  cs={c['scenario']:c for c in self.d['cases']}
  for q in [2,3]:
   self.assertEqual(cs['k0_conditional']['quarters'][q]['nights'],cs['review_with_k']['quarters'][q]['nights'])
   self.assertNotEqual(cs['k0_conditional']['quarters'][q]['gbv'],cs['review_with_k']['quarters'][q]['gbv'])
 def test_sensitivities_and_actuals(self):
  base,down,up=self.d['cases'][0],self.d['cases'][-2],self.d['cases'][-1]
  for c in [down,up]:self.assertEqual(c['quarters'][:2],base['quarters'][:2])
  self.assertLess(down['valuation']['value_per_share'],base['valuation']['value_per_share']);self.assertGreater(up['valuation']['value_per_share'],base['valuation']['value_per_share'])
  self.assertIsNone(base['adjustment']);self.assertEqual(down['adjustment'],-.01)
 def test_bad_dcf_rates_rejected(self):
  with self.assertRaises(ValueError):m.dcf_factor(.09,.105,.105)
 def test_impossible_share_count_rejected(self):
  d=self.d;i=copy.deepcopy(d['inputs']);i['2026']['buybacks']=1e9
  with self.assertRaises(ValueError):m.build_financial(d['cases'][0]['quarters'],i,d['globals'],d['fy25'],d['h1'],d['nb_cost'])
if __name__=='__main__':unittest.main()
