import csv, hashlib, importlib.util, json, sys, unittest
from pathlib import Path
from pypdf import PdfReader
PKG=Path(__file__).resolve().parents[1]
ROOT=PKG.parents[3]
sys.path.insert(0,str(PKG))
spec=importlib.util.spec_from_file_location('l4_review_v2',PKG/'run.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
DATA=ROOT/'data/processed/forecast_methods/lane4_review_v2/review_v2'
OUT=ROOT/'deck/drafts/lane4_v2/review_v2'
class IntegrityTests(unittest.TestCase):
 def test_pages_and_visible_limits(self):
  memo=PdfReader(str(OUT/'review_memo.pdf'));self.assertEqual(len(memo.pages),2)
  text=' '.join(' '.join(p.extract_text() for p in memo.pages).split())
  for label in ['18.322','3,105.419','1.1654','1.0155','256/365','182.87','Cushion changes the guide only','no established executable edge']:
   self.assertIn(label,text)
  self.assertEqual(len(PdfReader(str(OUT/'accepted_L3_exhibits.pdf')).pages),3)
 def test_source_manifest_still_matches(self):
  for r in json.loads((DATA/'input_manifest.json').read_text()):
   self.assertEqual(m.sha(ROOT/r['path']),r['sha256'])
 def test_complete_ledger(self):
  rows=m.read_csv(OUT/'source_assumption_ledger.csv')
  l3=[r for r in rows if r['row_id'].startswith('L3-')]
  self.assertEqual(len(l3),1187);self.assertEqual(len({r['row_id'] for r in rows}),len(rows))
  self.assertTrue(all(r['units'] and r['quarter'] for r in rows if r['row_id'].startswith('MODEL-')))
  self.assertTrue(any(r['row_id'].startswith('CASH-') for r in rows))
 def test_original_card_unsigned_and_missing(self):
  c=json.loads((OUT/'unsigned_card.json').read_text());self.assertEqual(c['adoption'],'UNSIGNED')
  self.assertEqual(len(c['rules']),12)
  for r in c['rules']:
   self.assertIsNone(r['observed_value']);self.assertIn('FAIL W1/W2',r['conversion_status'])
  guide=next(r for r in c['rules'] if r['id']=='L4v2-C02')
  self.assertIn('never scored as guide surprise',guide['score'])
 def test_decision_continuity_and_no_adoption(self):
  ds=m.read_csv(OUT/'decision_register.csv');self.assertEqual(len(ds),13)
  self.assertTrue(all(r['adoption']=='UNSIGNED' for r in ds))
  d=next(r for r in ds if r['decision_id']=='L4v2-D13')
  self.assertIn('Original team D-01',d['object']);self.assertIn('OPEN',d['status'])
 def test_charts_exact_bytes(self):
  for n in ['01_seasonal_conversion','02_weight_identification','03_chronological_validation']:
   for suffix in ['.png','.svg']:
    self.assertEqual(m.sha(OUT/(n+suffix)),m.sha(m.SOURCE/'bundle/payload/conversion'/(n+suffix)))
 def test_no_guide_expectation_imputation(self):
  rows=m.read_csv(OUT/'same_basis_expectations.csv')
  x=m.one(rows,scenario='review_with_k',quarter='2026Q4',vendor_family='LSEG family',consensus_as_of_timestamp='2026-09-13T15:20Z')
  self.assertEqual(float(x['revenue_consensus_musd']),3161.02149)
  self.assertIn('unavailable',x['guide_expectations_status'])
  with self.assertRaises(ValueError):m.one(rows,scenario='review_with_k',quarter='2026Q4')
if __name__=='__main__':unittest.main()
