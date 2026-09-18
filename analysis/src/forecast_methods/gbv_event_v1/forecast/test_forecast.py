"""Independent algebra, saved-ledger, and all-origin future-input checks."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("ge_forecast",HERE/"run.py")
R=importlib.util.module_from_spec(spec);sys.modules[spec.name]=R;spec.loader.exec_module(R)
OUT=R.ROOT/"data/processed/forecast_methods/gbv_event_v1/forecast_v1/results_v1"


class AlgebraTests(unittest.TestCase):
    def test_no_change_zero_attribution(self):
        np.testing.assert_allclose(R.shapley([100,.1,.98],[100,.1,.98]),0,atol=1e-12)

    def test_only_one_changed_factor_receives_error(self):
        for j in range(3):
            old=np.array([100,.1,.98]);new=old.copy();new[j]*=1.2
            expected=np.zeros(3);expected[j]=np.prod(new)-np.prod(old)
            np.testing.assert_allclose(R.shapley(old,new),expected,atol=1e-12)

    def test_symmetric_interaction_allocation(self):
        # Equal changes in exchangeable coordinates share the whole interaction equally.
        np.testing.assert_allclose(R.shapley([1,1,1],[2,2,2]),[7/3]*3,atol=1e-12)

    def test_nan_rejected_and_interval_not_full_guide_range(self):
        with self.assertRaises(ValueError):R.shapley([1,1,np.nan],[2,2,2])
        self.assertEqual(R.interval_error(102,100),1.5)
        self.assertEqual(R.interval_error(100.3,100),0)


class SavedArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.events=pd.read_csv(OUT/"per_event_decomposition.csv")

    def test_all_events_reconcile_directly_to_source_forecast_minus_guide(self):
        z=self.events
        np.testing.assert_allclose(z[R.FACTORS].sum(axis=1),z.point_musd-z.value_mid,atol=1e-8,rtol=0)
        np.testing.assert_allclose(z[R.FACTORS].sum(axis=1)+z.ROUND,z.error_interval_musd,atol=1e-8,rtol=0)
        self.assertEqual(len(z),12)
        self.assertEqual(len(z[z.quarter>="2024Q1"]),10)

    def test_oracle_changes_input_not_estimator_and_revenue_target_is_separate(self):
        z=self.events
        np.testing.assert_allclose(z.oracle_gbv_guide_musd,z.actual_base_musd*z.lambda_pct/100/z.cushion_divisor,atol=1e-8,rtol=0)
        np.testing.assert_allclose(z.candidate_revenue_raw_error_musd,z.revenue_point_musd-z.actual_revenue_musd,atol=1e-8,rtol=0)
        self.assertTrue((z.oracle_status.str.startswith("ex_post")).all())

    def test_covariance_needed_and_variance_mse_identities_hold(self):
        for win,start in [("W1","2023Q1"),("W2","2024Q1")]:
            z=self.events[self.events.quarter>=start]
            x=z[R.FACTORS].to_numpy();cov=np.cov(x,rowvar=False,ddof=0)
            self.assertAlmostEqual(float(cov.sum()),float(np.var(z.error_raw_musd)),places=7)
            self.assertGreater(abs(float(cov.sum()-np.trace(cov))),1000)
            self.assertAlmostEqual(float(np.var(z.error_raw_musd)+np.mean(z.error_raw_musd)**2),float(np.mean(z.error_raw_musd**2)),places=8)

    def test_temporal_ledgers_and_failed_verdict_preserved(self):
        timing=pd.read_csv(OUT/"timing_checks.csv")
        self.assertEqual(len(timing),617)
        self.assertTrue((pd.to_datetime(timing.available_date)<pd.to_datetime(timing.origin_date)).all())
        summary=json.loads((OUT/"forecast_audit.json").read_text())
        self.assertEqual(summary["forecast_verdict"],"FAIL")
        self.assertEqual(summary["new_fits"],0)
        self.assertTrue(pd.read_csv(OUT/"reproduction_comparison.csv").exact_bytes.all())

    def test_saved_manifest_and_deletion_rows(self):
        manifest=json.loads((OUT/"output_manifest.json").read_text())
        for rel,sha in manifest.items():self.assertEqual(R.digest((OUT/rel).read_bytes()),sha,rel)
        deletion=pd.read_csv(OUT/"paired_event_deletion.csv")
        self.assertEqual(len(deletion),44)
        self.assertFalse(deletion.refit.any())


class AllOriginIndependenceTests(unittest.TestCase):
    def test_future_value_poisoning_at_every_frozen_origin(self):
        source=R.ROOT.parent/"quant-thesis-validation-v1"
        n=int(os.environ.get("GIT_CONFIG_COUNT","0"))
        os.environ["GIT_CONFIG_COUNT"]=str(n+1)
        os.environ[f"GIT_CONFIG_KEY_{n}"]="safe.directory"
        os.environ[f"GIT_CONFIG_VALUE_{n}"]=str(source).replace("\\","/")
        s=importlib.util.spec_from_file_location("ge_original_prospective",source/R.SCRIPT)
        old=importlib.util.module_from_spec(s);sys.modules[s.name]=old;s.loader.exec_module(old)
        src=old.load_sources();k0,baseline=old.load_apis()
        qs=pd.read_csv(OUT/"pre_event_forecasts.csv").quarter.unique()
        def signature(result):
            return pd.DataFrame(result["predictions"])[["method","status","point_musd"]].to_json(double_precision=15)
        for q in qs:
            d=old.origin(q,src.sessions)["origin_date"]
            changed=copy.deepcopy(src)
            changed.panel.loc[changed.panel.print_date>=d,["gbv_musd","revenue_musd"]]=9e12
            changed.cushions.loc[changed.cushions.print_date>=d,"actual"]=8e12
            changed.guides.loc[changed.guides.print_date>=d,["value_low","value_high","value_mid"]]*=1e6
            self.assertEqual(signature(old.forecast_one(q,src,k0,baseline)),signature(old.forecast_one(q,changed,k0,baseline)),q)
        self.assertEqual(len(qs),21)


if __name__=="__main__":unittest.main(verbosity=2)
