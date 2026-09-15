import sys
import unittest
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

sys.path.insert(0,str(Path(__file__).resolve().parent))
import run
import fetch


class NclhTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel=run.load_panel()

    def test_no_target_quarter_deposit_or_future_target_influence(self):
        q=pd.Period("2024Q2",freq="Q")
        asof=self.panel.loc[q-1,"published_at"]
        p=self.panel.copy()
        original=run.features(p,q,asof)[0]
        p.loc[q:,run.ATS]=1e15
        p.loc[q:,run.TARGETS[0]]=1e15
        self.assertTrue(np.array_equal(original,run.features(p,q,asof)[0]))
        self.assertTrue(run.training(p,run.TARGETS[0],asof).equals(run.training(self.panel,run.TARGETS[0],asof)))

    def test_unavailable_lag_rejected(self):
        q=pd.Period("2024Q2",freq="Q")
        asof=self.panel.loc[q-1,"published_at"]-pd.Timedelta(seconds=1)
        with self.assertRaisesRegex(ValueError,"unavailable"):
            run.features(self.panel,q,asof)

    def test_calendar_lag_missing_not_shifted(self):
        q=pd.Period("2024Q2",freq="Q")
        p=self.panel.drop(q-2)
        with self.assertRaisesRegex(ValueError,"Missing lagged"):
            run.features(p,q,self.panel.loc[q-1,"published_at"])

    def test_zero_negative_missing_denominator_rejected(self):
        q=pd.Period("2024Q2",freq="Q")
        for bad in (0,-1,np.nan):
            p=self.panel.copy();p.loc[q-1,run.ATS]=bad
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,"positive"):
                run.features(p,q,p.loc[q-1,"published_at"])

    def test_training_excludes_covid_lags_and_flags_reopening(self):
        t=run.training(self.panel,run.TARGETS[0],pd.Timestamp("2026-09-13",tz="UTC"))
        self.assertIn("2022Q4",set(t.quarter))
        self.assertFalse(any(x.startswith(("2020","2021")) for x in t.quarter))
        self.assertFalse(any(x in set(t.quarter) for x in ("2022Q1","2022Q2","2022Q3")))
        s=run.training(self.panel,run.TARGETS[0],pd.Timestamp("2026-09-13",tz="UTC"),True)
        self.assertNotIn("2022Q4",set(s.quarter))

    def test_known_source_publications(self):
        self.assertEqual(len(self.panel),46)
        self.assertEqual(self.panel.loc["2025Q4","published_at"],pd.Timestamp("2026-03-02T11:30:00Z"))
        self.assertEqual(self.panel.loc["2026Q2","published_at"],pd.Timestamp("2026-07-30T10:30:00Z"))

    def test_first_column_small_current_value_kept(self):
        self.assertAlmostEqual(self.panel.loc["2021Q1",run.TARGETS[0]],.166)
        self.assertAlmostEqual(self.panel.loc["2023Q4","net_yield_usd_per_capacity_day"],243.27)
        self.assertTrue(pd.isna(self.panel.loc["2020Q2","capacity_days"]))

    def test_revenue_identity_metric_units(self):
        p=self.panel
        self.assertTrue(np.allclose(p.total_revenue_usd_m,p.passenger_ticket_revenue_usd_m+p.onboard_other_revenue_usd_m,atol=.002))
        self.assertAlmostEqual(p.loc["2025Q4","total_revenue_usd_m"],2244.400)
        self.assertAlmostEqual(p.loc["2025Q4",run.ATS],3200.593)

    def test_fit_recovery_and_simplex(self):
        # Constant ATS by season, exactly proportional revenues: weights are
        # non-identifiable but any valid fit must recover predictions exactly.
        t=pd.DataFrame([dict(season=s,actual=100+s,x1=200,x2=200,x3=200) for _ in range(3) for s in range(1,5)])
        loss,w,lam=run.fit_kernel(t)
        self.assertAlmostEqual(loss,0)
        self.assertAlmostEqual(w.sum(),1)
        self.assertTrue((w>=0).all())
        self.assertTrue(np.allclose(lam,np.arange(101,105)/200))
        self.assertEqual(len(run.GRID),66)

    def test_insufficient_seasons_rejected(self):
        t=pd.DataFrame([dict(season=1,actual=100,x1=100,x2=90,x3=80)]*10)
        with self.assertRaisesRegex(ValueError,"two per season"):
            run.fit_kernel(t)

    def test_publication_precision(self):
        s=BeautifulSoup('<time class="date" datetime="2020-02-20T07:00:00">February 20, 2020 7:00am EST</time>',"html.parser")
        value,precision,_=fetch.publication(s)
        self.assertEqual(value,"2020-02-20T07:00:00-05:00")
        self.assertEqual(precision,"issuer_clock_timezone")
        s=BeautifulSoup('<time class="date" datetime="2020-02-20">February 20, 2020</time>',"html.parser")
        value,precision,_=fetch.publication(s)
        self.assertEqual(value,"2020-02-21T04:59:59+00:00")

    def test_strict_hurdles(self):
        # Construct exact ratio of .6 (must fail); .599 passes.
        rows=[]
        for q in ("2023Q1","2024Q1"):
            for model,pred in (("seasonal_naive",110),("kernel_simplex",106),("kernel_below",105.99)):
                rows.append(dict(metric="m",scenario="s",quarter=q,model=model,prediction=pred,actual=100))
        scores=run.score(pd.DataFrame(rows))
        self.assertFalse(scores[scores.model=="kernel_simplex"].forecast_hurdle_pass.any())
        self.assertTrue(scores[scores.model=="kernel_below"].forecast_hurdle_pass.all())

    def assert_bad_observation_rejected(self, mutate, message):
        obs=pd.read_csv(run.INPUT/"observations.csv")
        mutate(obs)
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)
            obs.to_csv(path/"observations.csv",index=False)
            with self.assertRaisesRegex(ValueError,message):
                run.load_panel(path)

    def test_nextday_boundary_rejected(self):
        self.assert_bad_observation_rejected(lambda d:d.loc.__setitem__((d.quarter=="2026Q2","published_at"),"2026-09-14T00:00:00Z"),"Future")

    def test_missing_single_metric_timestamp_rejected(self):
        self.assert_bad_observation_rejected(lambda d:d.loc.__setitem__(((d.quarter=="2024Q2")&(d.metric==run.ATS),"published_at"),""),"per-row")

    def test_infinite_matching_revenue_identity_rejected(self):
        self.assert_bad_observation_rejected(lambda d:d.loc.__setitem__(((d.quarter=="2024Q2")&d.metric.isin(run.TARGETS),"value"),np.inf),"Nonfinite")

    def test_nonhex_source_hash_rejected(self):
        self.assert_bad_observation_rejected(lambda d:d.loc.__setitem__((0,"source_sha256"),"z"*64),"provenance")

    def test_whitespace_source_rejected(self):
        self.assert_bad_observation_rejected(lambda d:d.loc.__setitem__((0,"source_reference"),"   "),"provenance")

    def test_wrong_metric_units_rejected(self):
        self.assert_bad_observation_rejected(lambda d:d.loc.__setitem__((0,"units"),"USD"),"unit mismatch")


if __name__=="__main__":
    unittest.main()
