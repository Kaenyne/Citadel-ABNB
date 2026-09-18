"""Economic identity, missing-history, and point-in-time safety tests."""
import unittest
import numpy as np
import pandas as pd
import run as core
import diagnostics


class QuantContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.panel,cls.calendar=core.load_inputs()

    def fixture(self):
        rows=core.features(self.panel,[3,4])
        rows=rows[rows.quarter>="2023Q1"].reset_index(drop=True)
        phi=np.array([.45,.35,.15,.05]);lam,pred=core.scale_fit(rows,phi)
        return rows,{"phi":phi,"lambda":lam,"prediction":pred}

    def test_same_matrix_forward_backward_and_residual(self):
        rows,fit=self.fixture();a=core.allocation(rows,fit,[3,4])
        self.assertTrue((a.allocated_revenue_musd>=0).all())
        np.testing.assert_allclose(a.effective_forward_fee_per_net_gbv*a.reported_booking_quarter_gbv_musd,a.allocated_revenue_musd)
        np.testing.assert_allclose(a.backward_share*a.allocated_column_musd,a.allocated_revenue_musd)
        np.testing.assert_allclose(a.actual_revenue_attribution_share*a.actual_revenue_musd,a.allocated_revenue_musd)
        for _,g in a.groupby("quarter"):
            self.assertAlmostEqual(g.backward_share.sum(),1)
            self.assertAlmostEqual(g.actual_revenue_attribution_share.sum()+g.unallocated_residual_share.iloc[0],1)

    def test_tail_separates_distinct_booking_denominators(self):
        rows,fit=self.fixture();a=core.allocation(rows,fit,[3,4])
        tail=a[a.lag>=3]
        self.assertEqual(set(tail.lag),{3,4})
        for _,d in tail.groupby("quarter"):
            self.assertAlmostEqual(d.effective_forward_fee_per_net_gbv.iloc[0],d.effective_forward_fee_per_net_gbv.iloc[1])
            # Equal coefficient does not imply equal dollars when denominators differ.
            ratio=d.allocated_revenue_musd.iloc[0]/d.allocated_revenue_musd.iloc[1]
            self.assertAlmostEqual(ratio,d.reported_booking_quarter_gbv_musd.iloc[0]/d.reported_booking_quarter_gbv_musd.iloc[1])

    def test_actual_scale_and_covariance_identity(self):
        rows,fit=self.fixture();a=core.allocation(rows,fit,[3,4],True)
        self.assertLess(a.column_residual_musd.abs().max(),1e-8)
        _,_,check=core.temporal_stats(a)
        self.assertLess(check.reconciliation_error_musd2.abs().max(),1e-7)

    def test_unprinted_current_and_lag1_are_poison_invariant(self):
        origin=pd.Timestamp("2025-08-06")
        known=self.panel[self.panel.print_date<=origin]
        latest=known.quarter.max();target=core.qshift(latest,2)
        poisoned=self.panel.copy()
        poisoned.loc[poisoned.print_date>origin,["gbv_musd","revenue_musd"]]*=100
        for q in [core.qshift(latest,1),target]:
            self.assertEqual(core.forecast_gbv(self.panel,q,origin),core.forecast_gbv(poisoned,q,origin))
        original=core.features(known,[3,4])
        changed=core.features(poisoned[poisoned.print_date<=origin],[3,4])
        pd.testing.assert_frame_equal(original,changed)

    def test_missing_unprinted_lag1_is_error_not_realized_fill(self):
        known=self.panel[self.panel.quarter<="2025Q2"]
        with self.assertRaises(ValueError):core.baseline_forecast(known,"2025Q4")

    def test_forecast_rejects_already_printed_target(self):
        with self.assertRaises(ValueError):core.forecast_gbv(self.panel,"2023Q1","2025-12-01")

    def test_lags_do_not_fill_missing_prehistory(self):
        short=self.panel.head(4)
        self.assertTrue(core.features(short,[3,4]).empty)

    def test_fractional_lp_bounds_really_normalize(self):
        rows,_=self.fixture();rows=rows[rows.season==4].reset_index(drop=True)
        z,a,b=core.lp_problem(rows,list(range(5)),.01)
        lo,hi=core.ratio_bounds(z,a,b,0,np.array([1,0,0,0,0]))
        self.assertLessEqual(lo[0],hi[0]+1e-8)
        for value,beta in [lo,hi]:
            self.assertTrue((a@beta<=b+1e-7).all())
            self.assertAlmostEqual(value,z[0,0]*beta[0]/(z[0]@beta),places=7)

    def test_flight_vintage_excludes_future_commit(self):
        f=diagnostics.flight_source();origin=pd.Timestamp("2024-08-08")
        a=diagnostics.eligible_flight(f,origin,"2024Q2")
        f.loc[f.commit_date>origin,"eu40_flt_da_yoy"]*=10000
        b=diagnostics.eligible_flight(f,origin,"2024Q2")
        self.assertEqual(a.eu40_flt_da_yoy,b.eu40_flt_da_yoy)
        self.assertLessEqual(a.commit_date,origin)

    def test_forward_row_censoring_is_explicit(self):
        rows,fit=self.fixture();a=core.allocation(rows,fit,[3,4],True);a.insert(0,"window","W1")
        summary=diagnostics.forward_rows(a)
        latest=summary[summary.booking_quarter==a.booking_quarter.max()].iloc[0]
        self.assertTrue(latest.right_censored)
        self.assertEqual(latest.tail_beyond4,"unobserved")

    def test_same_day_late_flight_commit_is_refused(self):
        f=diagnostics.flight_source();origin=pd.Timestamp("2024-08-08")
        selected=diagnostics.eligible_flight(f,origin,"2024Q2")
        poisoned=f.copy()
        ix=poisoned.quarter==selected.quarter
        poisoned.loc[ix,"committed_utc"]=pd.Timestamp("2024-08-08T23:59:59Z")
        poisoned.loc[ix,"commit_date"]=origin
        alternative=diagnostics.eligible_flight(poisoned,origin,"2024Q2")
        self.assertNotEqual(alternative.quarter,selected.quarter)


if __name__=="__main__":unittest.main()
