# L0-spine — the constraint spine (Card 0)

Built overnight 11 Sep 2026. Package owner: L0-spine implementer.
Code: `analysis/src/forecast_methods/L0/`
Data: `data/processed/forecast_methods/L0/`

**Status: complete.** All three files built, every hard assertion held, 20/20 tests pass,
`run.py` exits 0. Two of the architect's seven counts needed reinterpretation (both
reconciled, see §4); one soft check FAILS as written and is replaced with a defensible
version (§3); one data-integrity contradiction was found in the consensus files and is
flagged rather than fixed (§6).

---

## 1. Exact run commands

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"

# rebuild everything and run the tests (exit code 0 required)
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/L0/run.py

# tests only
/Users/theomachado/.venvs/citadel-abnb/bin/python -m pytest "analysis/src/forecast_methods/L0/test_l0.py" -q
```

`pytest` was **not installed** in `/Users/theomachado/.venvs/citadel-abnb`. I installed it
(pytest 9.1.1, pluggy 1.6.0, iniconfig 2.3.0). `run.py` also carries a no-pytest fallback that
calls the test functions directly, so the package self-verifies either way.

Outputs written (progressively — file 1 is on disk and asserted before file 2 starts):

| Path (under `data/processed/forecast_methods/L0/`) | Rows |
|---|---|
| `L0_exact_regional_revenue.csv` | 72 |
| `L0_exact_regional_revenue_reconciliation.csv` | 18 |
| `L0_exact_regional_revenue_seasonality_check.csv` | 16 |
| `L0_interval_observations.csv` | 186 (172 in the default view) |
| `L0_interval_observations_midpoint_bias.csv` | 7 |
| `L0_vintage_register.csv` | 127 |
| `L0_build_diagnostics.json` | every count and assertion result |

---

## 2. File 1 — `L0_exact_regional_revenue.csv`, 72 cells

### What ran

`10_xbrl_revenue_geography.csv` has **258 fact rows on two incompatible geography axes**:

| geo member | raw rows | axis |
|---|---|---|
| `srt:NorthAmericaMember` | 45 | four-region |
| `us-gaap:EMEAMember` | 45 | four-region |
| `srt:LatinAmericaMember` | 45 | four-region |
| `srt:AsiaPacificMember` | 45 | four-region |
| `country:US` | 35 | US / non-US |
| `us-gaap:NonUsMember` | 35 | US / non-US |
| `country:FR` | 8 | single-country |

The 78 rows on the second and third axes are **excluded**, never summed with the first. A
regression test asserts 1Q22 totals $1,509M rather than $2,281M, which is what you get if the
US axis leaks in.

Pipeline, in order: filter `period_days ∈ [80, 100]` → **88** three-month regional rows →
de-duplicate on `(start, end, geo)` keeping the **earliest** `filed` date as `vintage` and
carrying the accession number → **56** unique cells = **14 quarter-ends × 4 regions**, 1Q22
through 2Q26, with **no Q4 among them** (regional revenue is filed only in the three 10-Qs a
year). Annual regional cells: 20 unique (2021-2025 × 4); 2021 has no filed quarterly regional
cells in this extract, so the back-outs run 2022-2025 = **16**. Total **72**.

> **Count discrepancy vs the addendum, resolved.** The addendum says "95 three-month rows from
> 1Q22 collapse to 63 unique". I measure **116** three-month rows across *all* axes, of which
> **88** are on the four-region axis, collapsing to **56**. The addendum's 95/63 appears to
> include the `country:US` / `NonUsMember` / `country:FR` three-month rows. The binding number
> — 56 filed regional cells, 14 quarters × 4 regions — is exactly reproduced, and 56 + 16 = 72.

### Results — every hard assertion holds

| Assertion | Result |
|---|---|
| A1 56 filed cells, 14 quarters × 4 regions, all 80-100 days, no Q4 | PASS |
| A2 16 back-outs, 4 years × 4 regions | PASS |
| A3 Q4 back-out **company totals** to $1M | PASS, exact to $0.0M |
| A4 every back-out strictly positive | PASS, 16/16 |
| A5 four regions sum to consolidated revenue (`02_kpi_panel_quarterly.csv`) within $1M | PASS, **max abs diff $0.000M over 18 quarters** |
| Cross-check vs `10_regional_revenue_xbrl.csv` (independent transcription) | max abs diff **$0.000M** over all 72 cells |

The four acceptance figures, reproduced exactly:

| Q4 | NA | EMEA | LatAm | APAC | **total** | target |
|---|---|---|---|---|---|---|
| 4Q22 | 964 | 556 | 189 | 193 | **1,902** | 1,902 |
| 4Q23 | 1,043 | 683 | 248 | 244 | **2,218** | 2,218 |
| 4Q24 | 1,111 | 794 | 278 | 297 | **2,480** | 2,480 |
| 4Q25 | 1,146 | 930 | 351 | 351 | **2,778** | 2,778 |

Worked check for 4Q22, as specified: 3Q22 regions 1,326 + 1,263 + 139 + 156 = 2,884; nine-month
2022 regional total 6,497; FY2022 8,399 − 6,497 = **1,902**. Asserted in `test_l0.py`.

---

## 3. What FAILED: the "within 40% of its own Q3" back-out check

The addendum asks that each back-out be "within 40 percent of its own Q3". **It fails, 11/16
pass**, and the failures are not errors — they are seasonality:

| quarter | region | Q4/Q3 | within 40% |
|---|---|---|---|
| 4Q22 | emea | 0.440 | **NO** |
| 4Q23 | emea | 0.446 | **NO** |
| 4Q24 | emea | 0.460 | **NO** |
| 4Q25 | emea | 0.472 | **NO** |
| 4Q25 | latam | 1.494 | **NO** |

EMEA Q4 revenue is structurally ~55% below its own Q3 (summer Europe); LatAm Q4 is 36-49%
*above* its own Q3 (southern-hemisphere summer plus Brazil). A ±40% band around the *own-Q3*
level is simply the wrong test for a business with this much seasonal amplitude, and it would
have thrown on correct data every single year.

**Replacement, S2, which does the job the check was meant to do:** each back-out's Q4/Q3 ratio
must sit within 15% of that region's own mean Q4/Q3 ratio. This **passes 16/16** and the ratios
are strikingly tight — NA 0.7057 / 0.7067 / 0.7078 / 0.7270, EMEA 0.4402 / 0.4455 / 0.4600 /
0.4723, APAC 1.173-1.290, LatAm 1.360-1.494. Max deviation from the region mean is 5.9%
(LatAm 4Q25). S2 is the hard assertion in the code; S1 is computed, published in
`L0_exact_regional_revenue_seasonality_check.csv`, and does not raise.

---

## 4. File 2 — `L0_interval_observations.csv`, 186 rows (172 in the default view)

Every block reproduces the architect's count exactly:

| block | contents | got | architect | match |
|---|---|---|---|---|
| B1 | regional nights **bucket** cells, 4Q24-2Q26 | 28 | 28 | yes |
| B2 | regional nights **derived** residual cells, `included = False` | 14 | 14 | yes |
| B3 | regional nights **stated-integer** cells as rounding intervals | 22 | 22 | yes |
| B4 | regional **ADR integers**, `[x−0.5, x+0.5]` | 68 | 68 | yes |
| B5 | **annual 10-K regional nights** cells at table precision | 24 | 24 | yes |
| B6 | quarterly **revenue guide ranges** (scoreable) | 19 | 19 | yes |
| B7 | **bucket-word guides** (scoreable) | 5 | 5 | yes |

Two counts needed interpretation, and both reconcile cleanly:

* **B6.** There are **20** quarterly revenue-level guide ranges in `02_guidance_ledger.csv`
  (4Q21 → 3Q26). Nineteen have a realised actual; the 3Q26 range $4,690-4,770M is the **LIVE**
  guide given 6 Aug 2026 and has none. It is in the file with `scoreable = False` and enters no
  metric and no gate, per the windows decision. 19 scoreable = the architect's 19.
* **B7.** There are **10** bucket-word guides. Five are scoreable (4Q25 GBV, 4Q25 nights, 1Q26
  GBV, 1Q26 nights, 2Q26 GBV); the other five are the three FY2026 revenue-growth buckets and
  the two LIVE 3Q26 buckets, none of which has a realised actual. 5 scoreable = the
  architect's 5.

**B4 provenance note.** The 68 ADR integers come from `10_regional_panel_quarterly.csv`
(`{region}_adr_yoy_reported_pct` 13+12+7+6 and `{region}_adr_yoy_exfx_pct` 5+12+7+6 = 68), not
from `02_kpi_panel_quarterly.csv`, which carries only 54 of the same cells under different
column names. Every one of the 68 is integer-valued in the source, consistent with them being
letter-rounded. They are entered as `[x−0.5, x+0.5]`, tested.

**The 14 derived rows** split NA 8 / EMEA 6 exactly as specified, spanning 4Q22-3Q24. They are
kept in the file for audit with `included = False` and are dropped by
`load_interval_observations()` by default. `l0.interval_likelihood_rows()` drops them and the
LIVE rows and can PIT-filter on `knowable_from`.

### Band-midpoint bias — measured, and it does not match the addendum's sign

Definition used: for each quarter where all four regions carry a genuine bucket (4Q24-2Q26,
n = 7), bias = (nights-share-weighted band midpoint) − (actual total nights growth), using the
panel's own `{region}_nights_share_est_pct` weights.

| quarter | midpoint-implied | actual | bias (pp) |
|---|---|---|---|
| 4Q24 | 12.05 | 12.35 | −0.30 |
| 1Q25 | 7.80 | 7.92 | −0.12 |
| 2Q25 | 7.39 | 7.43 | −0.04 |
| 3Q25 | 8.81 | 8.79 | +0.02 |
| 4Q25 | 9.63 | 9.82 | −0.19 |
| 1Q26 | 9.91 | 9.15 | **+0.76** |
| 2Q26 | 11.40 | 10.34 | **+1.06** |
| **mean** | | | **+0.17** |
| **last 2** | | | **+0.91** |
| **4Q24-4Q25 only (n=5)** | | | **−0.13** |

The addendum states −0.22pp on average and −0.72pp over the last two quarters. My 4Q24-4Q25
sub-period mean (−0.13pp) is in the same territory as −0.22pp under the opposite sign
convention (actual − midpoint), but **the last-two-quarter figure has the opposite sign from
the addendum's**: in 1Q26 and 2Q26 the band midpoints *overstate* realised total nights growth
by 0.76pp and 1.06pp. I could not reproduce −0.72 under either sign convention with the panel's
own weights. This does not weaken the rule, it strengthens it: the midpoint error is ~1pp and
has recently flipped sign, so a midpoint is worse than useless as a point estimate. The
measured table is published at `L0_interval_observations_midpoint_bias.csv` and the file header
carries the number with its definition. **Downstream packages: use the intervals, never the
midpoint, and do not quote −0.22/−0.72 without re-deriving it.**

---

## 5. File 3 — `L0_vintage_register.csv`, 127 consensus values

A **new** file. `data/processed/overnight/20_vintage_register.csv` is a *series-lineage*
register (`series, native_freq, release_lag_days, vintage_reconstructible, how, lag_applied,
approximation_label`) with no consensus values at all; its schema is incompatible and it is
neither overwritten nor extended. `build_vintage_register.py` asserts that file still has a
`series` column and no `value` column before writing, and `test_l0.py` re-asserts it.

Schema: `register_id, vendor, period, metric, value, unit, n_estimates, as_of_timestamp, url,
source_path, role, pit_usable, vendor_attributed, note`.

| role | rows | what |
|---|---|---|
| `at_print` | 85 | consensus the print was scored against (revenue, EPS, EBITDA, nights, GBV) |
| `pre_guide` | 20 | next-quarter consensus quoted on the print morning, **before** the guide |
| `current` | 22 | live vendor snapshots, 3 / 4 / 11 Sep 2026 |

124 rows are `pit_usable`; **3 are not** and are excluded from every PIT use.

Vendors: LSEG 24, Refinitiv 14, Zacks 8, S&P Global Market Intelligence 6, Alpha Vantage 4,
S&P/Visible Alpha via StockStory 2, CNBC unattributed 2, StreetAccount 1, S&P/TipRanks 1,
Yahoo/unattributed 1, `vendor_not_recorded` 62 (the at-print EPS / EBITDA / nights / GBV cells
carry no vendor of their own in the source files, and are *not* given the revenue vendor they
may not come from).

### Seeds, all asserted

| what | value | vendor | as-of |
|---|---|---|---|
| **6 Aug 2026 pre-guide 3Q26 Street** | **$4,610M** | **LSEG** | **2026-08-06** |
| 3Q26 current | $4,740M (7 est.) | Zacks | 2026-09-04 |
| 3Q26 current | $4,737M (36 est.) | Alpha Vantage | 2026-09-11 |
| 4Q26 current | $3,200M (10 est.) | Zacks | 2026-09-04 |
| **4Q26 current** | **$3,158M (36 est.)** | **Alpha Vantage** | **2026-09-11** |
| FY2026 | $14,160M (43 est.) | S&P Global Market Intelligence | 2026-09-03 |
| FY2027 | $15,760M | S&P Global Market Intelligence | 2026-09-03 |
| FY2026 / FY2027 | $14,155M / $15,758M (43 / 44 est.) | Alpha Vantage | 2026-09-11 |
| FY2026 / FY2027 | $14,100M (8) / $15,730M (13) | Zacks | 2026-09-04 |

Two tests enforce the flag that matters: `pit_consensus("revenue", "2026Q3", "2026-08-06",
vendor="Zacks")` returns **None** — the $4,740M Zacks value is a 4 Sep vintage and cannot be the
6 Aug pre-guide Street — while the same query at `2026-09-11` returns it. `pre_guide_street(
"2026Q3")` returns LSEG $4,610M @ 2026-08-06.

The live 4Q26 anchors disagree by **$42M** (Zacks $3,200M, 4 Sep, 10 estimates vs Alpha Vantage
$3,158M, 11 Sep, 36 estimates). Both are registered with their vendor, count and timestamp so
the guide-below-Street probability can be stated against a named vendor, as the decisions
document requires.

---

## 6. A data-integrity contradiction found, flagged not fixed

`16_consensus_at_print_merged.csv` supplies a next-quarter consensus of **$3,840M (LSEG)** for
the 2024Q2 print (i.e. the pre-guide 3Q24 Street) while **that same row's own `notes` column
reads "NEXT-QUARTER CONSENSUS NOT FOUND. CNBC quotes only the $3.67-3.73bn guide; no other
contemporaneous source retrievable. This is the single next-quarter gap in the sample."**
`04_consensus_at_print.csv` has the cell blank. The merged value carries no as-of timestamp and
no url of its own, and it implies a guide-vs-Street of −3.6% ($3,700M guide midpoint), which
would be the largest negative gap in the sample.

I have not adjudicated it and I have not edited either source file. The value is registered
with `pit_usable = False` and a note recording the contradiction, so it is visible to an
auditor but invisible to `pit_consensus()`. **Consequence for other packages:** the pre-guide
Street baseline is missing for 3Q24, so any W1/W2 gate scored against the Street has
**n = 13 of 14 on W1 and 9 of 10 on W2**, not 14 and 10. Say so rather than silently imputing.
If someone can retrieve a timestamped contemporaneous 6 Aug 2024 value, flipping one flag in
`build_vintage_register.py` restores it.

The other two non-PIT rows are the 2024Q3 `pre_guide` placeholder from the unmerged file and the
`2026Q3 adj_ebitda` row in `04_current_consensus.csv`, which has vendor `derived` and no value
("NO published Q3-2026 adjusted-EBITDA or nights consensus was retrievable").

---

## 7. Loader and tests

`l0.py` is the only reader. `load_exact_regional_revenue()`, `regional_revenue_wide()`,
`load_interval_observations(include_derived=False, include_live=True, metric=None)`,
`interval_likelihood_rows(as_of=None)`, `load_vintage_register(role=None,
pit_usable_only=False)`, `pit_consensus(metric, period, as_of, vendor=None, role=None)`,
`pre_guide_street(period)`.

`pit_consensus` uses a **strict** inequality on the vintage, never returns `pit_usable = False`
rows, and breaks ties deterministically (as-of, then n_estimates, then vendor).

20 tests, all passing:

```
....................                                                     [100%]
20 passed in 0.35s
```

They cover: the 72/56/16 split; 14 quarters × 4 regions with no filed Q4; the four Q4 totals to
$1M; the worked 4Q22 arithmetic; positivity; regions-sum-to-consolidated over 18 quarters; the
second geo axis never leaking in; derived rows excluded by default but present for audit with
the NA 8 / EMEA 6 split; all seven block counts; every row being an interval with letter
integers exactly 1.0pp wide; LIVE rows flagged unscoreable; the `knowable_from` PIT filter; the
3Q26 guide range $4,690-4,770M; the register schema; the lineage register left intact; the
LSEG $4,610M pre-guide seed; Zacks $4,740M invisible as of 6 Aug; the strict-inequality
semantics; the four live anchors; and vintage-unknown rows never being PIT-usable.

---

## 8. Free-parameter count

**Zero.** L0 estimates nothing. It is a deterministic transcription-and-assertion layer: 72
exact cells, 186 interval rows, 127 consensus values, all traceable to a filing, a letter or a
timestamped vendor page. The only judgement calls are the three documented above (S1→S2, the
B6/B7 scoreable interpretation, the 2024Q3 flag) and none of them is a fitted quantity. No
registry forecast objects are emitted, because L0 makes no forecast.

---

## 9. Harness change requests

1. **The harness does not exist.** `analysis/src/forecast_methods/harness/` and
   `data/processed/forecast_methods/` were both absent when this package started; I created
   `data/processed/forecast_methods/L0/` and an empty
   `data/processed/forecast_methods/registry/` for whoever ships the harness. L0 writes no
   registry rows, so nothing needs migrating.
2. **The registry column set has no row shape for a constraint object.** The minimum columns in
   the decisions document (`point, q10, q50, q90, sd, …`) assume a forecast. If the scoreboard
   wants to record that a package's inputs came through L0, add a `l0_spine_version` or
   `inputs_via` column rather than forcing L0 to emit fake point forecasts.
3. **`pit_usable` needs to be a first-class harness concept.** Every package that uses a Street
   baseline must respect it, or the 3Q24 contradiction in §6 silently re-enters through
   `16_consensus_at_print_merged.csv`. Suggest the harness refuse any Street baseline that does
   not carry a vendor **and** an as-of timestamp.
4. **Baseline-n must be declarable per gate.** Because the 3Q24 pre-guide Street is unusable,
   Street-relative gates are n = 13 (W1) / 9 (W2). The harness should carry the realised n per
   baseline rather than assume 14/10.

---

## 10. Honest interpretation

The spine does what Card 0 asked and the arithmetic is clean to the dollar: 72 cells, four Q4
totals exact, regions reconciling to consolidated revenue with **zero** residual across 18
quarters, and an independent cross-check against `10_regional_revenue_xbrl.csv` agreeing to
$0.000M on all 72. That last agreement is worth naming honestly — it means the repo's existing
regional file was already correct, so file 1 buys *enforceability*, not new information.

The genuinely new work is negative and procedural: the ±40% back-out check would have thrown on
correct data every year and is replaced; the band-midpoint bias is about +1pp with a recently
flipped sign, not −0.72pp; and the pre-guide Street for 3Q24 rests on a value whose own source
row says it was not found, which costs one observation from every Street-relative gate. Each of
those is a thing a judge could have found and is better said by us.

What L0 cannot do: it cannot make the 14 `derived` rows usable, it cannot recover a 6 Aug 2024
Street print, and it cannot adjudicate the FX or kernel disputes — it only guarantees that when
those packages argue, they are arguing over the same 72 numbers, the same 172 intervals and the
same vintage-stamped consensus.

---

*Research, not investment advice.*
