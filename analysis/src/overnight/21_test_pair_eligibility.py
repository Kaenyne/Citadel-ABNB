"""21_test_pair_eligibility.py -- fixture test for audit finding A04 (Inside Airbnb partial-snapshot contamination).

Reads:  nothing on disk. Builds a synthetic 2-city dump series in memory and calls the real functions
        `add_scope_flags`, `scope_as_of` and `add_pair_eligibility` from analysis/src/inside_airbnb_supply_panel.py,
        plus `pair_row` on synthetic listing frames.
Writes: nothing. Prints PASS/FAIL per check; exit status 1 if any check fails.

Claim under test: a partial Inside Airbnb dump (a scrape covering a subset of the city) must not create an
apparent market-exit signal. The fixture reproduces the shape of the real Paris 2026-03-21 dump: a city with a
stable ~86,000-listing base whose one partial dump holds 38,000 of the same listings and nothing else. Raw
retention against that dump is ~44%; the eligibility policy must mark the pair ineligible under BOTH the
retrospective and the point-in-time classification, and the clean retention series must show no exit.

Run: py -3.13 analysis/src/overnight/21_test_pair_eligibility.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "analysis/src"))
import inside_airbnb_supply_panel as ia  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {name}{('  -- ' + detail) if detail else ''}")
    if not cond:
        FAILS.append(name)


# --------------------------------------------------------------------------------- fixture: listing frames
def listings(ids, dump_date, city="fixtureville", price=100.0, reviews=10, basis="listed_nightly"):
    """Minimal listing frame with the columns pair_row/clean_price touch."""
    n = len(ids)
    return pd.DataFrame({
        "id": np.asarray(ids, dtype="int64"),
        "host_id": np.asarray(ids, dtype="int64") % 500,
        "city": city, "dump_date": dump_date, "price_basis": basis,
        "room_type": "Entire home/apt",
        "price": float(price),
        "number_of_reviews_ltm": float(reviews),
        "calculated_host_listings_count": 1.0,
        "host_is_superhost": pd.Series([True] * n, dtype="object"),
        "minimum_nights": 2.0,
    })


# A city scraped quarterly at a stable size, with one partial dump in Mar 2026 that holds a strict subset.
BASE = 86_000
SUBSET = 38_000
DUMPS = {
    "2025-03-03": list(range(BASE)),                       # full
    "2025-06-06": list(range(1_000, BASE + 1_000)),        # full, normal churn
    "2025-09-12": list(range(2_000, BASE + 2_000)),        # full
    "2025-12-13": list(range(3_000, BASE + 3_000)),        # full
    "2026-03-21": list(range(3_000, 3_000 + SUBSET)),      # PARTIAL: subset of the same city, nothing removed
    "2026-06-16": list(range(4_000, BASE + 4_000)),        # full again -- proves nothing actually exited
}
FRAMES = {d: listings(ids, d) for d, ids in DUMPS.items()}

snaps = pd.DataFrame([dict(city="fixtureville", region="EMEA", dump_date=d, listings=len(ids))
                      for d, ids in DUMPS.items()])

pairs = []
dates = sorted(DUMPS)
for i, d in enumerate(dates):
    tb = pd.Timestamp(d)
    cands = [x for x in dates[:i] if 270 <= (tb - pd.Timestamp(x)).days <= 460]
    if cands:
        best = min(cands, key=lambda x: abs((tb - pd.Timestamp(x)).days - 365))
        pairs.append(dict(city="fixtureville", region="EMEA", pair_type="year_ago", date_a=best, date_b=d,
                          **ia.pair_row(FRAMES[best], FRAMES[d])))
pairs = pd.DataFrame(pairs)

s = ia.add_scope_flags(snaps)
p = ia.add_pair_eligibility(pairs, s)
p["pair"] = p.date_a.dt.strftime("%Y-%m-%d") + " -> " + p.date_b.dt.strftime("%Y-%m-%d")
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 30)
print(p[["pair", "ids_a", "ids_b", "retention", "partial_scope_a", "partial_scope_b", "pair_eligible",
         "exclusion_reason", "pair_eligible_pit", "exclusion_reason_pit", "retention_clean"]].to_string(index=False))
print()

partial = p[p.date_b == pd.Timestamp("2026-03-21")]
clean = p[p.pair_eligible]

# 1. the fixture really does look like a mass exit if the flags are ignored
check("fixture reproduces an apparent mass exit in the raw pair table",
      len(partial) == 1 and partial.retention.iloc[0] < 0.50,
      f"raw retention {partial.retention.iloc[0]:.1%} on the partial dump")

# 2. the snapshot classification catches the partial dump both ways
row = s[s.dump_date == pd.Timestamp("2026-03-21")].iloc[0]
check("partial dump flagged retrospectively", bool(row.partial_scope), f"scope_vs_peer {row.scope_vs_peer:.2f}")
check("partial dump flagged point-in-time (trailing window only)", bool(row.partial_scope_pit),
      f"scope_vs_peer_pit {row.scope_vs_peer_pit:.2f}")

# 3. the pair carries both endpoint flags and a reason
check("pair table carries both endpoint scope flags",
      {"partial_scope_a", "partial_scope_b", "partial_scope_a_pit", "partial_scope_b_pit"} <= set(p.columns))
check("contaminated pair is ineligible with a reason",
      (not bool(partial.pair_eligible.iloc[0])) and partial.exclusion_reason.iloc[0] == "partial_scope_b",
      f"reason '{partial.exclusion_reason.iloc[0]}'")
check("contaminated pair is also ineligible point-in-time",
      not bool(partial.pair_eligible_pit.iloc[0]), f"reason '{partial.exclusion_reason_pit.iloc[0]}'")

# 4. the raw row survives (nothing deleted) but the clean series is null
check("raw pair row preserved", partial.retention.notna().iloc[0] and partial.ids_b.iloc[0] == SUBSET)
check("clean retention is null on the contaminated pair", bool(partial.retention_clean.isna().iloc[0]))
check("clean matched-review series is null on the contaminated pair",
      bool(partial.matched_reviews_ltm_chg_clean.isna().iloc[0]))
check("clean price series is null on the contaminated pair",
      bool(partial.lfl_price_chg_median_clean.isna().iloc[0]) and not bool(partial.price_pair_eligible.iloc[0]))

# 5. THE CLAIM: no apparent market exit survives the filter
check("no exit signal in the clean retention series",
      bool(clean.retention_clean.min() > 0.90),
      f"min clean retention {clean.retention_clean.min():.1%} over {len(clean)} eligible pairs "
      f"vs {p.retention.min():.1%} raw")
check("every full-scope pair stays eligible", len(clean) == len(p) - 1)

# 6. a real exit is still detected: same city, but half the listings genuinely disappear from a FULL-scope dump
real = dict(DUMPS)
real["2026-06-16"] = list(range(4_000, 4_000 + BASE // 2)) + list(range(900_000, 900_000 + BASE // 2))
rframes = {d: listings(ids, d) for d, ids in real.items()}
rsnaps = pd.DataFrame([dict(city="fixtureville", region="EMEA", dump_date=d, listings=len(v)) for d, v in real.items()])
rp = pd.DataFrame([dict(city="fixtureville", region="EMEA", pair_type="year_ago", date_a="2025-06-06", date_b="2026-06-16",
                        **ia.pair_row(rframes["2025-06-06"], rframes["2026-06-16"]))])
rp = ia.add_pair_eligibility(rp, ia.add_scope_flags(rsnaps))
check("a genuine 50% exit at unchanged scope is NOT filtered out",
      bool(rp.pair_eligible.iloc[0]) and rp.retention_clean.iloc[0] < 0.55,
      f"clean retention {rp.retention_clean.iloc[0]:.1%}")

# 7. point-in-time flag cannot be revised by a later scrape
half = s[s.dump_date <= pd.Timestamp("2026-03-21")]
r_early = ia.add_scope_flags(snaps[pd.to_datetime(snaps.dump_date) <= pd.Timestamp("2026-03-21")])
check("point-in-time flag is identical whether or not later dumps exist",
      bool(r_early[r_early.dump_date == pd.Timestamp("2026-03-21")].partial_scope_pit.iloc[0]) ==
      bool(row.partial_scope_pit),
      "later scrapes cannot revise a frozen classification")
r_early_retro = bool(r_early[r_early.dump_date == pd.Timestamp("2026-03-21")].partial_scope.iloc[0])
print(f"note   retrospective flag on 2026-03-21 with only prior dumps: {r_early_retro}; with all dumps: {bool(row.partial_scope)} "
      f"(equal here, but the retrospective rule is revisable in general -- use *_pit for replay)")

# 8. a RUN of consecutive partial dumps hides itself from a short trailing window (the real Nashville Feb-May
#    2026 shape: five partial dumps in a row, each normal beside its neighbours). The long trailing lookback in
#    the point-in-time rule must still catch it.
run = {"2025-03-15": BASE, "2025-06-19": BASE, "2025-09-23": BASE,
       "2025-12-27": SUBSET, "2026-01-22": SUBSET, "2026-02-25": SUBSET, "2026-03-28": SUBSET, "2026-04-25": SUBSET}
rsn = pd.DataFrame([dict(city="runville", region="NA", dump_date=d, listings=n) for d, n in run.items()])
rs = ia.add_scope_flags(rsn)
last = rs[rs.dump_date == pd.Timestamp("2026-04-25")].iloc[0]
check("a run of partial dumps escapes the SHORT point-in-time window (documents why the long one exists)",
      not bool(last.partial_scope_pit), f"scope_vs_peer_pit {last.scope_vs_peer_pit:.2f}")
check("the long-lookback point-in-time rule catches the run",
      bool(last.partial_scope_pit_long), f"scope_vs_peer_pit_long {last.scope_vs_peer_pit_long:.2f}")
rpair = pd.DataFrame([dict(city="runville", region="NA", pair_type="year_ago", date_a="2025-03-15", date_b="2026-04-25",
                           ids_a=BASE, ids_b=SUBSET, matched=SUBSET, retention=SUBSET / BASE,
                           matched_reviews_ltm_chg=0.10, lfl_price_chg_median=np.nan,
                           price_comparable=False, matched_priced_entire=0)])
rpair = ia.add_pair_eligibility(rpair, rs)
check("pair ending on a hidden partial dump is ineligible point-in-time",
      not bool(rpair.pair_eligible_pit.iloc[0]), f"reason '{rpair.exclusion_reason_pit.iloc[0]}'")

print()
if FAILS:
    print(f"{len(FAILS)} check(s) FAILED: {', '.join(FAILS)}")
    sys.exit(1)
print("all checks passed")
