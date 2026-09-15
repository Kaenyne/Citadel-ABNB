"""Source-integrity attacks, missingness and accounting-contract tests."""
import csv
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

PACKAGE=Path(__file__).parent
def load(name):
    spec=importlib.util.spec_from_file_location('_lane4_sources_v2_test_'+name,PACKAGE/(name+'.py'))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
p=load('run')
e=load('eligibility')
SNAP=p.ROOT/'data/processed/forecast_methods/lane4_sources_v2/snapshot_v1'


class IntegrityTests(unittest.TestCase):
    def test_exact_binding(self):
        self.assertEqual(p.binding_match(b'abc\n',p.sha(b'abc\n')),'exact')

    def test_newline_difference_is_explicit(self):
        self.assertEqual(p.binding_match(b'a\nb\n',p.sha(b'a\r\nb\r\n')),'expected_CRLF_actual_LF')
        self.assertEqual(p.binding_match(b'a\r\nb\r\n',p.sha(b'a\nb\n')),'expected_LF_actual_CRLF')

    def test_non_newline_content_mismatch_rejected(self):
        for value in (b'changed',b'\xff\xfe',b'a\rb'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                p.binding_match(value,p.sha(b'a\nb'))

    def test_unsafe_paths_rejected(self):
        for path in ('../x','/x','C:/x','folder\\x','folder/../../x'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                p.safe_relative(path)

    def test_write_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'a'
            p.bytes_new(path,b'original')
            with self.assertRaises(FileExistsError):
                p.bytes_new(path,b'replaced')
            self.assertEqual(path.read_bytes(),b'original')

    def test_bundle_manifest_inventory_and_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            manifest={}
            for i in range(108):
                data=f'file{i}\n'.encode()
                (root/f'{i}.txt').write_bytes(data)
                manifest[f'{i}.txt']=p.sha(data)
            raw=json.dumps(manifest).encode()
            (root/'SHA256SUMS.json').write_bytes(raw)
            with patch.object(p,'EXPECTED_MANIFEST',p.sha(raw)):
                self.assertEqual(len(p.verify_bundle(root)),108)
                (root/'nested').mkdir()
                (root/'nested/SHA256SUMS.json').write_text('{}')
                with self.assertRaisesRegex(ValueError,'inventory'):
                    p.verify_bundle(root)
                (root/'nested/SHA256SUMS.json').unlink()
                (root/'0.txt').write_text('tamper')
                with self.assertRaisesRegex(ValueError,'checksum'):
                    p.verify_bundle(root)

    def test_actual_bundle_and_32_committed_bindings(self):
        self.assertEqual(len(p.verify_bundle(SNAP/'bundle')),108)
        bindings=p.acceptance_bindings(SNAP/'bundle')
        self.assertEqual(len(bindings),32)
        self.assertTrue(all(r['git_binding_status']=='exact' for r in bindings))

    def test_missing_committed_object_rejected(self):
        with self.assertRaises(ValueError):
            p.object_bytes(p.RESEARCH_COMMIT,['a_path_that_does_not_exist_L4_integrity_test'])

    def test_existing_extraction_destination_rejected(self):
        with self.assertRaises(FileExistsError):
            p.extract(SNAP,Path('unused'))


class AccountingTests(unittest.TestCase):
    def test_missing_nonfinite_never_zero(self):
        for value in (None,'','nan','inf','-inf'):
            with self.subTest(value=value),self.assertRaises(ValueError):
                e.number(value)
        self.assertEqual(e.number('0'),0)

    def test_prehedge_identity_and_unchanged_hedge(self):
        contract=dict(certified_prehedge=True,matching_baseline=True,matching_cohort_denominator=True)
        self.assertAlmostEqual(e.prehedge_transform(1000,100,120,.95,**contract),975)
        self.assertAlmostEqual(e.prehedge_transform(1000,100,100,.95,**contract),955)
        self.assertNotEqual(e.prehedge_transform(1000,100,100,.95,**contract),.95*1000)

    def test_each_unmatched_contract_blocks_application(self):
        for field in ('certified_prehedge','matching_baseline','matching_cohort_denominator'):
            contract=dict(certified_prehedge=True,matching_baseline=True,matching_cohort_denominator=True)
            contract[field]=False
            with self.subTest(field=field),self.assertRaises(ValueError):
                e.prehedge_transform(1000,100,100,.95,**contract)

    def test_missing_hedge_or_invalid_prehedge_denominator_rejected(self):
        contract=dict(certified_prehedge=True,matching_baseline=True,matching_cohort_denominator=True)
        for inputs in ((1000,None,100,.95),(1000,100,None,.95),(100,100,100,.95),(1000,100,100,0)):
            with self.subTest(inputs=inputs),self.assertRaises(ValueError):
                e.prehedge_transform(*inputs,**contract)

    def test_all1187_dispositions_preserve_source_fields(self):
        source=p.read_csv(SNAP/'bundle/l4_inputs.csv')
        classified=e.dispositions(SNAP/'bundle')
        self.assertEqual(len(classified),1187)
        self.assertEqual(len({r['row_id'] for r in classified}),1187)
        for before,after in zip(source,classified):
            self.assertEqual(before,{k:after[k] for k in before})
            self.assertIn(after['integration_disposition'],e.DISPOSITIONS)
            self.assertTrue(after['disposition_reason'] and after['eligibility_reason'])

    def test_unknown_schema_rejected_and_fee_null_preserved(self):
        for row in ({'package':'new','metric':'x'},{'package':'cohort_fx','metric':'new'},
                    {'package':'fee_panel','metric':'fee_theta_log','value':'0'}):
            with self.subTest(row=row),self.assertRaises(ValueError):
                e.classify(row)
        row={'package':'fee_panel','metric':'fee_theta_log','value':''}
        self.assertEqual(e.classify(row)[1],'unavailable')

    def test_all180_source_identities_and_isolated_diagnostics(self):
        checks,diagnostics=e.source_arithmetic(SNAP/'bundle')
        self.assertEqual(len(checks),180)
        self.assertEqual(len(diagnostics),4)
        self.assertTrue(all(r['result']=='PASS' for r in checks))
        self.assertTrue(all(r['m_pre']=='' and r['H_usd']=='' and r['financial_application']=='ineligible' for r in diagnostics))

    def test_baseline_coverage_and_missing_fx_not_zero(self):
        status=json.loads((SNAP/'accounting_eligibility.json').read_text())
        rows=p.read_csv(SNAP/'cohort_baseline_compatibility.csv')
        self.assertEqual(len(rows),15)
        self.assertEqual(sum(r['reported_kernel_identity_match']=='True' for r in rows),5)
        self.assertEqual(sum(r['quarter_coverage']=='NO_SOURCE_TARGET' for r in rows),10)
        self.assertTrue(all(r['H_usd']=='' and r['H_new_usd']=='' for r in rows))
        self.assertIsNone(status['estimated_incremental_fx_musd'])
        self.assertFalse(status['central_fx_financial_eligibility'])

    def test_current_audit_cannot_overwrite(self):
        with self.assertRaises(FileExistsError):
            e.audit(SNAP)


if __name__=='__main__':
    unittest.main()
