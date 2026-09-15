"""Information-set and semantic adversarial checks for the frozen protocol."""
from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("quant_prospective_run",HERE/"run.py")
import sys
R=importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name]=R
SPEC.loader.exec_module(R)


class InformationSetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=R.load_sources()
        cls.k0,cls.baseline=R.load_apis()

    def forecasts(self,q,src=None):
        return R.forecast_one(q,src or self.src,self.k0,self.baseline)

    def signature(self,result):
        f=pd.DataFrame(result["predictions"])
        return f[["method","status","point_musd"]].to_json(double_precision=15)

    def test_poison_future_gbv_revenue_guides_and_cushion(self):
        q="2025Q1";src=copy.deepcopy(self.src)
        d=R.origin(q,src.sessions)["origin_date"]
        src.panel.loc[src.panel.print_date>=d,["gbv_musd","revenue_musd"]]=9e12
        src.cushions.loc[src.cushions.print_date>=d,"actual"]=8e12
        mask=src.guides.print_date>=d
        src.guides.loc[mask,["value_low","value_high","value_mid"]]*=1e6
        self.assertEqual(self.signature(self.forecasts(q)),self.signature(self.forecasts(q,src)))

    def test_missing_and_duplicate_publication_metadata_fail(self):
        src=copy.deepcopy(self.src);src.panel.loc[0,"print_date"]=None
        with self.assertRaisesRegex(ValueError,"publication date"):
            self.forecasts("2025Q1",src)
        src=copy.deepcopy(self.src)
        src.panel=pd.concat([src.panel,src.panel.iloc[[0]]],ignore_index=True)
        with self.assertRaisesRegex(ValueError,"duplicate"):
            self.forecasts("2025Q1",src)

    def test_same_day_observation_refused(self):
        src=copy.deepcopy(self.src);q="2025Q1";d=R.origin(q,src.sessions)["origin_date"]
        latest=src.panel[src.panel.print_date<d].quarter.max()
        src.panel.loc[src.panel.quarter==latest,"print_date"]=d
        result=self.forecasts(q,src)
        self.assertNotIn(latest,{r["input_quarter"] for r in result["panel_inputs"]})
        self.assertTrue(all(r["available_date"]<d for r in result["panel_inputs"]))

    def test_unknown_current_lag_is_forecast_never_training_row(self):
        q="2025Q1";result=self.forecasts(q)
        lag1=[x for x in result["gbv_inputs"] if x["lag"]==1][0]
        self.assertEqual(lag1["kind"],"reconstructed_latest_observed_yoy_persistence")
        self.assertNotIn(R.shift(q,-1),{x["input_quarter"] for x in result["panel_inputs"]})
        self.assertNotIn(R.shift(q,-1),{x["training_quarter"] for x in result["lambda_training"]})

    def test_already_issued_target_guide_rejected(self):
        q="2025Q1";src=copy.deepcopy(self.src);d=R.origin(q,src.sessions)["origin_date"]
        src.guides.loc[src.guides.quarter==q,"print_date"]=d-timedelta(days=1)
        with self.assertRaisesRegex(ValueError,"already available"):
            self.forecasts(q,src)

    def test_first_guide_survives_later_revision(self):
        raw=R.read_git(R.FILES["guides"])
        original=R.first_guides(raw)
        rev=raw[(raw.metric=="revenue_usd_m")&(raw.guide_type=="range")].iloc[[-1]].copy()
        rev["print_date"]="2026-09-01";rev["guide_id"]="synthetic_revision"
        rev[["value_low","value_high","value_mid"]]*=10
        new=R.first_guides(pd.concat([raw,rev],ignore_index=True))
        pd.testing.assert_frame_equal(original,new)

    def test_seasonal_gbv_missing_abstains_without_zero_growth_fallback(self):
        src=copy.deepcopy(self.src);q="2025Q1"
        src.panel=src.panel[src.panel.quarter!=R.shift(q,-5)]
        result=self.forecasts(q,src)
        candidate=[r for r in result["predictions"] if r["method"]==R.METHODS[0]][0]
        self.assertEqual(candidate["status"],"abstain")
        self.assertIn("anchor",candidate["reason"])

    def test_session_cutoff_weekend_and_stale_calendar(self):
        got=R.origin("2026Q4",self.src.sessions)
        self.assertEqual(str(got["anchor_date"]),"2026-09-13")
        self.assertEqual(str(got["origin_date"]),"2026-09-11")
        self.assertEqual(got["origin_close"],"2026-09-11T16:00:00-04:00")
        with self.assertRaises(R.MissingInput):
            R.origin("2026Q4",[d for d in self.src.sessions if str(d)<"2026-09-01"])

    def test_nominal_guide_uses_project_midpoint_interval_not_full_range(self):
        q="2024Q3";mid=float(self.src.guides.set_index("quarter").loc[q,"value_mid"])
        pred=pd.DataFrame([dict(quarter=q,method=R.METHODS[0],status="forecast",point_musd=mid+10)])
        e=R.errors_frame(pred,self.src).iloc[0]
        self.assertEqual(e.error_raw_musd,10)
        self.assertEqual(e.error_interval_musd,9.5)
        self.assertTrue(e.value_low<e.point_musd<e.value_high)

    def test_live_missing_target_remains_missing_error(self):
        pred=pd.DataFrame([dict(quarter="2026Q4",method=R.METHODS[0],status="forecast",point_musd=3000)])
        e=R.errors_frame(pred,self.src).iloc[0]
        self.assertTrue(np.isnan(e.error_raw_musd))
        self.assertTrue(np.isnan(e.error_interval_musd))

    def test_all_three_matching_preserves_pair_only_cell(self):
        rows=[]
        for q in ("2023Q1","2024Q1","2025Q1"):
            for method in R.METHODS:
                if q=="2023Q1" and method==R.METHODS[1]:continue
                rows.append(dict(quarter=q,method=method,error_interval_musd=10.,error_raw_musd=10.5,
                                 year=int(q[:4]),season=int(q[-1])))
        score,paired,deleted,slices,coverage,matched=R.score_tables(pd.DataFrame(rows))
        self.assertNotIn("2023Q1",matched["W1"])
        self.assertTrue(any(r["quarter"]=="2023Q1" and r["scope"]=="pair" and r["baseline"]==R.METHODS[2] for r in paired))

    def test_calibration_excludes_unpublished_future_guide_error(self):
        predictions=[];errors=[]
        qs=[str(q) for q in pd.period_range("2023Q1","2025Q1",freq="Q")]
        for i,q in enumerate(qs):
            d=R.origin(q,self.src.sessions)["origin_date"]
            predictions.append(dict(quarter=q,method=R.METHODS[0],status="forecast",point_musd=2000,origin_date=d))
            errors.append(dict(quarter=q,method=R.METHODS[0],point_musd=2000,value_mid=2010+i))
        preds=pd.DataFrame(predictions);e=pd.DataFrame(errors)
        b,c,_=R.intervals(e,preds,self.src)
        poisoned=e.copy();poisoned.loc[poisoned.quarter=="2025Q1","value_mid"]=1e15
        b2,c2,_=R.intervals(poisoned,preds,self.src)
        pd.testing.assert_frame_equal(b[["quarter","lo_musd","hi_musd"]],b2[["quarter","lo_musd","hi_musd"]])
        self.assertTrue(all(row["target_guide_available_date"]<row["origin_date"] for row in c))

    def test_existing_output_directory_refused_before_loading(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileExistsError):
                R.run(Path(tmp))


if __name__=="__main__":
    unittest.main(verbosity=2)
