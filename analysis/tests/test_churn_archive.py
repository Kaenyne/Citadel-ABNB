import csv
from datetime import date
import gzip
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from acquire_churn_archive import MONTHS, KEEP, inspect_capture, select_snapshots
from measure_churn_archive import geographic_exclusions, measure, persistent_ids
from execute_listing_churn import terminal_state


def row(identifier,permit=""):
    return dict(id=identifier,host_id="h",room_type="Entire home/apt",minimum_nights="2",
                number_of_reviews_ltm="5",license=permit,latitude="32.8",longitude="-117.2",bedrooms="2")


def snap(day,rows,flag=False):
    return dict(start=day,month=day[:7],complete=date.fromisoformat(day),country="United States",
                ids={r["id"] for r in rows},records={r["id"]:r for r in rows},coverage_flag=flag)


def globals_for(snapshots):
    result={m:set() for m in MONTHS}
    for s in snapshots: result[s["month"]].update(s["ids"])
    return result


class SelectionTests(unittest.TestCase):
    def test_require_common_endpoints_and_choose_last_in_month(self):
        data=[dict(link="a",country="United States",dataRoot="https://data.insideairbnb.com/x/",publishDate=d)
              for d in ("2025-09-01","2025-09-20","2025-12-12","2026-06-15","2026-08-30")]
        data.append(dict(link="b",country="United States",dataRoot="https://data.insideairbnb.com/y/",publishDate="2026-06-15"))
        selected,inventory=select_snapshots(data)
        self.assertEqual([r["publishDate"] for r in selected],["2025-09-20","2025-12-12","2026-06-15"])
        self.assertFalse(inventory[1]["acquisition_eligible"])

    def test_wrong_source_domain_rejected(self):
        with self.assertRaises(ValueError): select_snapshots([dict(dataRoot="https://example.com/")])

    def test_duplicate_ids_rejected_before_compact_is_published(self):
        with tempfile.TemporaryDirectory() as folder:
            source=Path(folder)/"raw.gz";compact=Path(folder)/"compact.gz"
            with gzip.open(source,"wt",encoding="utf-8",newline="") as h:
                writer=csv.DictWriter(h,fieldnames=(*KEEP,"source","last_scraped"));writer.writeheader()
                for _ in range(2): writer.writerow(dict(**row("1"),source="city scrape",last_scraped="2025-09-02"))
            with self.assertRaises(ValueError): inspect_capture(source,compact,"2025-09-01")
            self.assertFalse(compact.exists())


class MeasurementTests(unittest.TestCase):
    def test_nested_geography_removed_without_removing_its_ids_from_larger_market(self):
        owners={str(i):["small","large"] if i<9 else ["small"] if i==9 else ["large"] for i in range(20)}
        owners["overlap"]=["large","adjacent"]
        nested,duplicates,_=geographic_exclusions(owners,{"small":10,"large":20,"adjacent":10})
        self.assertEqual(nested,{"small":"large"})
        self.assertEqual(duplicates,{"overlap"})

    def test_overlap_excluded_and_presence_in_other_market_retained(self):
        ss=[snap("2025-09-15",[row("1"),row("2"),row("3")]),snap("2025-12-15",[]),snap("2026-06-20",[])]
        gp=globals_for(ss);gp["2026-06"].add("2")
        result,_=measure("test",ss,gp,{"1"},gp["2025-09"])
        self.assertEqual(result[0]["baseline_ids"],2)
        self.assertEqual(result[0]["missing_ids"],1)
        self.assertEqual(result[0]["same_id_observed_elsewhere_at_endpoint"],1)
        self.assertEqual(result[0]["persistent_90"],1)

    def test_positive_in_partial_march_resets_december_clock(self):
        ss=[snap("2025-09-15",[row("1")]),snap("2025-12-15",[]),snap("2026-03-30",[row("1")],True),snap("2026-06-20",[])]
        result,_=measure("test",ss,globals_for(ss),set(),{"1"})
        self.assertEqual(result[0]["persistent_90"],0)
        self.assertTrue(result[0]["persistence_eligible"])

    def test_unavailable_followup_rate_not_zero(self):
        ss=[snap("2025-09-15",[row("1")]),snap("2025-12-15",[],True),snap("2026-03-30",[]),snap("2026-06-20",[])]
        result,_=measure("test",ss,globals_for(ss),set(),{"1"})
        self.assertFalse(result[0]["persistence_eligible"])
        self.assertIsNone(result[0]["persistent_90_rate"])
        self.assertEqual(result[0]["id_attrition"],1)

    def test_global_existing_baseline_id_cannot_be_new_replacement(self):
        ss=[snap("2025-09-15",[row("1","STR-00123L")]),snap("2025-12-15",[]),snap("2026-06-20",[row("2","STR-00123L")])]
        result,aliases=measure("test",ss,globals_for(ss),set(),{"1","2"})
        self.assertEqual(aliases,{})
        self.assertEqual(result[0]["alternative_id_candidates"],0)

    def test_set_persistence_matches_individual_state_machine(self):
        # Exhaust all 3-state histories for three post-baseline observations.
        import itertools
        days=["2025-09-15","2025-12-15","2026-03-15","2026-06-20"]
        for history in itertools.product((True,False,None),repeat=3):
            states=(True,*history)
            ss=[snap(d,[row("1")] if state is True else [],state is None) for d,state in zip(days,states)]
            valid=[not s["coverage_flag"] for s in ss]
            got,_=persistent_ids({"1"},ss,globals_for(ss),valid)
            expected=terminal_state([(date.fromisoformat(d),state) for d,state in zip(days,states)])
            self.assertEqual("1" in got,expected["status"]=="persistent_absence",history)

    def test_march_sensitivity_changes_negatives_not_positives(self):
        ss=[snap("2025-09-15",[row("1")]),snap("2025-12-15",[row("1")]),snap("2026-03-15",[]),snap("2026-06-20",[])]
        result,_=measure("test",ss,globals_for(ss),set(),{"1"})
        self.assertEqual(result[0]["persistent_90"],1)
        self.assertEqual(result[1]["persistent_90"],0)


if __name__=="__main__": unittest.main()
