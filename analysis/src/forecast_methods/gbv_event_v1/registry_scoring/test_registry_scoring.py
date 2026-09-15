"""Meaningful availability, formula, and no-historical-change checks."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
import pandas as pd

spec=importlib.util.spec_from_file_location("ge_registry_scoring",Path(__file__).with_name("run.py"))
R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
MODEL=R.ROOT/"data/processed/forecast_methods/gbv_event_v1/integration_v2/model.json"
OUT=R.ROOT/"data/processed/forecast_methods/gbv_event_v1/scoring_v1"

class Tests(unittest.TestCase):
    def setUp(self):self.model=json.loads(MODEL.read_text())

    def test_only_unknown_guides_registered_and_horizons_are_calendar_quarters(self):
        f=R.rows_from_model(self.model)
        self.assertEqual(len(f),7)
        self.assertEqual(f[f.target=="guide_mid"].quarter.tolist(),["2026Q4","2027Q1","2027Q2"])
        for r in f.itertuples():
            self.assertEqual(r.horizon_q,pd.Period(r.quarter,freq="Q").ordinal-pd.Period(r.vintage_date,freq="Q").ordinal)
        self.assertTrue(f.q50.eq(f.point).all())

    def test_stale_or_inconsistent_input_fails(self):
        bad=copy.deepcopy(self.model);bad["forecast"][3]["revenue_musd"]+=1
        with self.assertRaises(ValueError):R.rows_from_model(bad)
        bad=copy.deepcopy(self.model);bad["forecast"][0]["guide_kind"]="conditional_future_guide"
        with self.assertRaises(ValueError):R.rows_from_model(bad)
        bad=copy.deepcopy(self.model);bad["forecast"][2]["lambda_n_train"]=99
        with self.assertRaises(ValueError):R.rows_from_model(bad)

    def test_existing_registration_is_never_overwritten(self):
        with self.assertRaises(FileExistsError):
            R.run(MODEL,OUT/"must_not_be_created", "register")
        self.assertFalse((OUT/"must_not_be_created").exists())

    def test_registry_files_equal_model_without_quantile_claims(self):
        expected=R.rows_from_model(self.model)
        for obj,z in expected.groupby("object"):
            stored=pd.read_csv(R.ROOT/f"data/processed/forecast_methods/registry/{R.METHOD}__{obj}.csv")
            self.assertEqual(len(stored),len(z))
            for row in stored.itertuples():
                source=z[z.quarter==row.quarter].iloc[0]
                self.assertAlmostEqual(row.point,source.point,places=9)
                self.assertEqual(row.n_params,5)
            self.assertTrue(stored[["q05","q10","q25","q75","q90","q95","sd"]].isna().all().all())

    def test_all_scorer_results_identical_and_frozen_files_preserved(self):
        paths=[OUT/(stage+"_"+fmt)/"scoreboard.csv" for stage in ["before","after"] for fmt in ["format_1_0","format_1_1"]]
        baseline=pd.read_csv(paths[0])
        for path in paths[1:]:self.assertEqual(R.comparison(baseline,pd.read_csv(path),"test"),[])
        receipt=json.loads((OUT/"receipt.json").read_text())
        self.assertEqual(receipt["historical_score_changes"],0)
        self.assertEqual(receipt["registry_rows"],7)
        for row in pd.read_csv(OUT/"preservation.csv").itertuples():
            self.assertTrue(row.unchanged);self.assertEqual(R.sha(R.ROOT/row.path),row.before)

if __name__=="__main__":unittest.main(verbosity=2)
