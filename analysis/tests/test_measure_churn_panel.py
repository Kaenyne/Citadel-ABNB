from collections import Counter
from datetime import date
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from measure_churn_panel import endpoint_aliases, measure_market, pool_rates, permit_key


def record(identifier,permit="STR-00123L, 123456",**kwargs):
    return dict(id=identifier,license=permit,room_type="Entire home/apt",bedrooms="2",
                latitude="32.8",longitude="-117.2",host_id="host1",minimum_nights="2",
                number_of_reviews_ltm="10",**kwargs)


def snap(day,rows,partial=False):
    return dict(start=day,complete=date.fromisoformat(day),partial=partial,
                ids={r["id"] for r in rows},records={r["id"]:r for r in rows})


class AliasTests(unittest.TestCase):
    def test_unique_matching_permit_is_candidate(self):
        a,b=record("1"),record("2")
        self.assertEqual(endpoint_aliases({"1":a},{"2":b}),{"1":"2"})

    def test_different_bedroom_or_geography_rejected(self):
        a,b=record("1"),record("2")
        for change in ({"bedrooms":"3"},{"latitude":"34.0"},{"bedrooms":""}):
            self.assertEqual(endpoint_aliases({"1":a},{"2":{**b,**change}}),{})

    def test_ambiguous_permit_rejected(self):
        self.assertEqual(endpoint_aliases({"1":record("1"),"3":record("3")},{"2":record("2")}),{})
        self.assertEqual(endpoint_aliases({"1":record("1")},{"2":record("2"),"3":record("3")}),{})

    def test_existing_baseline_id_is_not_new_replacement(self):
        a={"1":record("1"),"2":record("2","STR-00456L")}
        self.assertEqual(endpoint_aliases(a,{"2":record("2")}),{})

    def test_exemption_and_placeholder_rejected(self):
        for x in ("Exempt","Pending 123456","000000","None","123"):
            self.assertEqual(permit_key(x),"")


class PanelTests(unittest.TestCase):
    def test_insufficient_maturation_is_unidentified_not_zero_rate(self):
        snapshots=[snap("2025-09-01",[record("1")]),snap("2025-12-01",[],True),
                   snap("2026-06-15",[]),snap("2026-08-15",[])]
        rows,_,_=measure_market("nashville",snapshots,"all_listings")
        for r in rows:
            self.assertTrue(r["pair_eligible"])
            self.assertFalse(r["persistence_eligible"])
            self.assertIsNone(r["persistent_90_rate"])
            self.assertEqual(r["id_attrition"],1)

    def test_partial_positive_resets_clock(self):
        snapshots=[snap("2025-09-01",[record("1")]),snap("2025-12-01",[]),
                   snap("2026-04-15",[record("1")],True),snap("2026-08-15",[])]
        rows,_,_=measure_market("chicago",snapshots,"all_listings")
        self.assertEqual(rows[0]["persistent_90"],0)
        self.assertEqual(rows[0]["pending_90"],1)
        self.assertEqual(rows[0]["ids_reobserved_after_gap"],1)

    def test_austin_partial_baseline_excluded(self):
        snapshots=[snap("2025-09-01",[record("1")],True),snap("2025-12-01",[]),snap("2026-08-15",[])]
        rows,_,_=measure_market("austin",snapshots,"all_listings")
        self.assertFalse(rows[0]["pair_eligible"])
        self.assertIsNone(pool_rates(rows,"all_eligible_markets","all_listings","team_flags","id_attrition"))

    def test_weighted_pool_uses_counts_and_excludes_invalid_market(self):
        common=dict(cohort="all_listings",policy="team_flags",region="Europe",country="test",
                    interval_days=340,pair_eligible=True,persistence_eligible=True,persistent_90=0)
        rows=[dict(**common,market="a",baseline_ids=100,missing_ids=10),
              dict(**common,market="b",baseline_ids=900,missing_ids=450),
              dict(**{**common,"pair_eligible":False},market="c",baseline_ids=1000,missing_ids=900)]
        p=pool_rates(rows,"all_eligible_markets","all_listings","team_flags","id_attrition")
        self.assertEqual(p["baseline_ids"],1000)
        self.assertAlmostEqual(p["listing_weighted_rate"],.46)
        self.assertAlmostEqual(p["equal_market_weighted_rate"],.30)
        self.assertEqual(p["markets"],2)

    def test_replacement_is_separate_from_raw_id_attrition(self):
        snapshots=[snap("2025-09-01",[record("1")]),snap("2025-12-01",[]),snap("2026-08-15",[record("2")])]
        rows,_,_=measure_market("san-diego",snapshots,"all_listings")
        self.assertEqual(rows[0]["missing_ids"],1)
        self.assertEqual(rows[0]["alternative_id_candidates"],1)
        self.assertEqual(rows[0]["persistent_90_after_candidate_screen"],0)


if __name__=="__main__":
    unittest.main()
