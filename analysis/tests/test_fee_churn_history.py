from datetime import date
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from measure_fee_churn_history import pair_measure, cohort_ids, balanced_markets
from summarize_fee_churn import economic_scenarios, summarize


def snap(day, ids, flag=False):
    return dict(month=day[:7], complete=date.fromisoformat(day), ids=set(ids), flag=flag)


class FeeChurnTests(unittest.TestCase):
    def test_new_period_resets_denominator(self):
        a, b = snap("2025-09-01", "ab"), snap("2025-10-01", "bc")
        result = pair_measure(a, b, [], a["ids"], {"2025-10": b["ids"]}, "coverage_screen", [a, b])
        self.assertEqual(result["baseline_ids"], 2)
        self.assertEqual(result["missing_ids"], 1)
        self.assertEqual(result["disappearance_rate"], .5)
        self.assertIsNone(result["persistent_90_rate"])

    def test_partial_end_is_unknown_not_zero_or_churn(self):
        a, b = snap("2025-09-01", "ab"), snap("2025-10-01", "b", True)
        result = pair_measure(a, b, [], a["ids"], {"2025-10": b["ids"]}, "coverage_screen", [a, b])
        self.assertFalse(result["eligible"])
        self.assertIsNone(result["disappearance_rate"])
        self.assertIsNone(result["missing_ids"])

    def test_reappearance_in_partial_capture_refutes_persistence(self):
        a, b = snap("2025-09-01", "ab"), snap("2025-10-01", "")
        c, d = snap("2025-11-01", "a", True), snap("2026-01-03", "")
        result = pair_measure(a, b, [c, d], a["ids"], {s["month"]:s["ids"] for s in [a,b,c,d]}, "coverage_screen", [a,b,c,d])
        self.assertEqual(result["missing_ids"], 2)
        self.assertEqual(result["persistent_90_ids"], 1)
        self.assertEqual(result["reobserved_by_confirmation"], 1)

    def test_return_after_confirmation_does_not_change_90_day_result(self):
        a, b = snap("2025-09-01", "a"), snap("2025-10-01", "")
        c, d = snap("2026-01-03", ""), snap("2026-01-25", "a")
        result = pair_measure(a, b, [c,d], a["ids"], {"2025-09":a["ids"],"2025-10":set(),"2026-01":d["ids"]}, "coverage_screen", [a,b,c,d])
        self.assertEqual(result["confirmation_date"], "2026-01-03")
        self.assertEqual(result["persistent_90_ids"], 1)

    def test_followup_outside_max_window_is_censored(self):
        a, b, c = snap("2025-09-01", "a"), snap("2025-10-01", ""), snap("2026-03-01", "")
        result = pair_measure(a, b, [c], a["ids"], {"2025-10":set()}, "coverage_screen", [a,b,c])
        self.assertFalse(result["persistence_eligible"])

    def test_other_market_positive_prevents_false_disappearance(self):
        a, b = snap("2025-09-01", "a"), snap("2025-10-01", "")
        result = pair_measure(a,b,[],a["ids"],{"2025-10":{"a"}},"coverage_screen",[a,b])
        self.assertEqual(result["missing_ids"], 0)

    def test_portfolio_uses_full_starting_inventory(self):
        records = {str(i):dict(host_id="host",room_type="Entire home/apt",minimum_nights="2",number_of_reviews_ltm="1" if i==0 else "0") for i in range(5)}
        self.assertEqual(cohort_ids(records,"reviewed_str_homes","five_plus"), {"0"})
        self.assertEqual(cohort_ids(records,"reviewed_str_homes","one"), set())

    def test_invalid_order_fails(self):
        a = snap("2025-09-01", "a")
        with self.assertRaises(ValueError):
            pair_measure(a,a,[],a["ids"],{"2025-09":a["ids"]},"coverage_screen",[a])

    def test_balanced_panel_requires_each_period_and_clean_preperiod(self):
        intervals=[("2025-09","2025-10"),("2025-10","2025-11")]
        rows=[]
        for market in ("complete","partial","late"):
            for a,b in intervals:
                if market=="partial" and b=="2025-11":continue
                rows.append(dict(panel="monthly",cohort="all_listings",portfolio="all",policy="coverage_screen",eligible=True,market=market,start_month=a,end_month=b,event_timing="straddles_rollout" if market=="late" else "before"))
        self.assertEqual(balanced_markets(rows,"monthly",intervals,True),{"complete"})

    def test_fixed_weights_do_not_confuse_market_mix_with_rate_change(self):
        periods=[("2025-09","2025-10"),("2025-10","2025-11"),("2025-11","2025-12"),("2025-12","2026-01")]
        rows=[]
        for i,(a,b) in enumerate(periods):
            for market,rate in (("a",.1),("b",.2)):
                n=900 if i and market=="a" else 100
                rows.append(dict(panel="monthly",cohort="all_listings",portfolio="all",policy="coverage_screen",eligible="True",market=market,start_month=a,end_month=b,baseline_ids=str(n),missing_ids=str(int(n*rate)),disappearance_rate=str(rate),normalized_30d_rate=str(rate),baseline_review_total=str(n),missing_baseline_reviews=str(n*rate),interval_days="30"))
        meta={"market_sets":{name:(["a","b"] if name=="balanced_event" else []) for name in ("balanced_event","balanced_broad","balanced_pre_quarters","same_season")}}
        result,_=summarize(rows,meta)
        chosen=[r for r in result if r["series"]=="balanced_event"]
        self.assertEqual(len(chosen),4)
        self.assertTrue(all(abs(r["fixed_market_weighted_rate"]-.15)<1e-10 for r in chosen))
        self.assertAlmostEqual(chosen[1]["observed_rate"],.11)

    def test_fee_economics_preserves_payout_and_balances_cash(self):
        ledger={"economic_example":{"old_booking_subtotal":100,"old_host_fee":.03,"illustrative_old_guest_fee":.15,"new_host_fee":.155},
                "sources":[{"id":"FEE-04","revenue_usd_m":3608,"adjusted_ebitda_usd_m":1261}],
                "materiality_scenario":{"affected_share_of_counterfactual_booking_value":.5,"incremental_churn_rates":[.05],"booking_value_recaptured_within_airbnb":[.5,1],"relative_lost_listing_productivity":1,"time_exposure_in_period":1,"incremental_contribution_margin":.7,"relative_take_rate_changes":[0]}}
        economics,scenarios=economic_scenarios(ledger)
        self.assertAlmostEqual(economics[2]["host_payout"],97)
        self.assertAlmostEqual(economics[1]["host_payout_change_pct"],-12.8865979381443)
        for row in economics:
            self.assertAlmostEqual(row["guest_total"],row["host_payout"]+row["platform_fee"])
        self.assertAlmostEqual(scenarios[0]["revenue_change"],-.0125)
        self.assertAlmostEqual(scenarios[1]["revenue_change"],0)


if __name__ == "__main__":
    unittest.main()
