"""21_pair_eligibility_delta.py -- before/after table for audit finding A04 (WS21, 7 Sep 2026).

Reads:  data/processed/inside_airbnb_like_for_like.csv        rebuilt pair table (has pair_eligible / exclusion_reason)
        data/processed/inside_airbnb_city_snapshots.csv       rebuilt snapshot table (has both coverage flags)
Writes: data/processed/overnight/21_pair_eligibility_delta.csv   one row per year-ago pair: the retention that was
            published before the fix, the status it now carries, why, and the coverage of both endpoints
        data/processed/overnight/21_retention_by_city_delta.csv  per city: mean year-ago retention on ALL pairs
            (what the old charts showed) vs on eligible pairs only, and the same for matched reviews LTM

Note: `retention` itself is unchanged by the fix -- the arithmetic was always right for the ids in the two dumps.
What changes is whether a pair is allowed to carry a market interpretation. "old retention" is therefore the
number the pre-fix retention/reviews charts plotted for that pair; "new status" is eligible / excluded.

Run: py -3.13 analysis/src/overnight/21_pair_eligibility_delta.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PROC = ROOT / "data/processed"
OUT = PROC / "overnight"
OUT.mkdir(parents=True, exist_ok=True)

p = pd.read_csv(PROC / "inside_airbnb_like_for_like.csv", parse_dates=["date_a", "date_b"])
ya = p[p.pair_type == "year_ago"].copy()

ya["pair"] = ya.date_a.dt.strftime("%Y-%m-%d") + " -> " + ya.date_b.dt.strftime("%Y-%m-%d")
ya["old_status"] = "plotted as market retention"          # pre-fix: every year-ago pair went on the chart
ya["old_retention"] = ya.retention
ya["new_status"] = ya.pair_eligible.map({True: "eligible", False: "excluded"})
ya["new_status_pit"] = ya.pair_eligible_pit.map({True: "eligible", False: "excluded"})
ya["status_changed"] = ~ya.pair_eligible

cols = ["city", "region", "pair", "date_a", "date_b", "days_apart", "ids_a", "ids_b", "matched",
        "old_retention", "old_status", "new_status", "exclusion_reason", "retention_clean",
        "new_status_pit", "exclusion_reason_pit", "status_changed",
        "scope_vs_peer_a", "scope_vs_peer_b", "partial_scope_a", "partial_scope_b",
        "scope_vs_peer_b_pit", "scope_vs_peer_b_pit_long", "span_min_vs_max_listings", "span_step_warning",
        "matched_reviews_ltm_chg", "matched_reviews_ltm_chg_clean",
        "price_comparable", "matched_priced_entire", "lfl_price_chg_median", "price_pair_eligible",
        "lfl_price_chg_median_clean"]
d = ya[cols].sort_values(["city", "date_b"])
d.round(4).to_csv(OUT / "21_pair_eligibility_delta.csv", index=False)

g = ya.groupby("city")
city = pd.DataFrame({
    "pairs_all": g.retention.size(),
    "pairs_eligible": g.pair_eligible.sum(),
    "pairs_excluded": (~g.pair_eligible.apply(lambda s: s)).groupby(ya.city).sum() if False else g.pair_eligible.apply(lambda s: (~s).sum()),
    "retention_mean_all": g.retention.mean(),
    "retention_mean_eligible": g.apply(lambda x: x.loc[x.pair_eligible, "retention"].mean(), include_groups=False),
    "retention_min_all": g.retention.min(),
    "retention_min_eligible": g.apply(lambda x: x.loc[x.pair_eligible, "retention"].min(), include_groups=False),
    "matched_reviews_yoy_mean_all": g.matched_reviews_ltm_chg.mean(),
    "matched_reviews_yoy_mean_eligible": g.apply(lambda x: x.loc[x.pair_eligible, "matched_reviews_ltm_chg"].mean(), include_groups=False),
    "pairs_eligible_pit": g.pair_eligible_pit.sum(),
})
city["retention_mean_delta_pts"] = (city.retention_mean_eligible - city.retention_mean_all) * 100
city["matched_reviews_yoy_delta_pts"] = (city.matched_reviews_yoy_mean_eligible - city.matched_reviews_yoy_mean_all) * 100
city = city.reset_index()
city.round(4).to_csv(OUT / "21_retention_by_city_delta.csv", index=False)

pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
print(f"year-ago pairs {len(ya)}; excluded retrospectively {int((~ya.pair_eligible).sum())}; "
      f"excluded point-in-time {int((~ya.pair_eligible_pit).sum())}")
print(f"mean retention on all pairs {ya.retention.mean():.4f} -> on eligible pairs {ya.loc[ya.pair_eligible, 'retention'].mean():.4f}")
print(f"min  retention on all pairs {ya.retention.min():.4f} -> on eligible pairs {ya.loc[ya.pair_eligible, 'retention'].min():.4f}")
print(f"mean matched reviews LTM y/y {ya.matched_reviews_ltm_chg.mean():+.4f} -> eligible {ya.loc[ya.pair_eligible, 'matched_reviews_ltm_chg'].mean():+.4f}")
print()
print(city[["city", "pairs_all", "pairs_excluded", "pairs_eligible_pit", "retention_mean_all", "retention_mean_eligible",
            "retention_mean_delta_pts", "retention_min_all", "retention_min_eligible",
            "matched_reviews_yoy_mean_all", "matched_reviews_yoy_mean_eligible"]].to_string(index=False))
print()
print("EXCLUDED PAIRS")
print(d.loc[~d.status_changed.eq(False), ["city", "pair", "ids_a", "ids_b", "old_retention", "new_status",
                                          "exclusion_reason", "scope_vs_peer_b"]].to_string(index=False))
print()
paris = d[(d.city == "paris") & (d.pair == "2025-03-03 -> 2026-03-21")]
print("ACCEPTANCE CHECK -- Paris 3 Mar 2025 vs 21 Mar 2026:")
print(paris[["ids_a", "ids_b", "old_retention", "new_status", "exclusion_reason", "retention_clean",
             "new_status_pit", "scope_vs_peer_b"]].to_string(index=False))
print()
print("SPAN-STEP WARNINGS (eligible pairs that still straddle a listing-count step; coverage change and genuine")
print("contraction are not separable from listing counts alone -- carry the warning on any slide):")
w = d[d.span_step_warning & d.new_status.eq("eligible")]
print(w[["city", "pair", "ids_a", "ids_b", "old_retention", "span_min_vs_max_listings", "new_status_pit"]].to_string(index=False))
print(f"\nwrote {OUT / '21_pair_eligibility_delta.csv'} and {OUT / '21_retention_by_city_delta.csv'}")
