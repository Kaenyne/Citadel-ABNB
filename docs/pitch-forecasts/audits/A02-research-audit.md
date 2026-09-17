**C02 — Original vector: (a–e) = (0.21, 0.19, 0.39, 0.17, 0.04).**  
**Verdict:** Plausible judgment, but the evidence does not establish 39% for “high single digits.”  
**First fix:** Correct the historical comparison objects and derive all three Q3 branches from one distribution.  
**Main uncertainty:** Management’s choice between a bucket and directional language; “moderate” resolves (d) even at relatively strong growth.  
**Audit comparison:** **(0.17, 0.18, 0.30, 0.30, 0.05)**; assumptions and derivation below.

**C03 — Original vector: (a–e) = (0.37, 0.18, 0.28, 0.08, 0.09).**  
**Verdict:** A 37% raise probability remains plausible, but its claimed consensus anchor is incorrectly constructed.  
**First fix:** Remove the whole-year application of quarterly kappa and restore the omitted November disclosure opportunity.  
**Main uncertainty:** Whether management retains a floor, converts it to a point, or omits the now-redundant annual sentence.  
**Audit comparison:** **(0.35, 0.19, 0.21, 0.10, 0.15)**; explicitly judgmental, not a fitted replacement.

## Scope and verification

Reviewed both revision-1 logs, forecast JSONs, datasets, saved source snapshots, and the underlying repository files. Matched all **17 next-quarter nights quotations and three FY revenue quotations** to their original saved shareholder letters. Recomputed the guidance counts, cushions, quarterly kappa, distribution arithmetic, and relevant consensus values.

Both submitted vectors sum to **1.00**. Both decomposition scripts reproduce their stored outputs when their file-writing blocks are removed. The reproduction script below ran successfully using the repository’s `python`; `py -3.13` was inaccessible. No repository files were changed, no scorers were run, and neither prohibited raw-data folder was opened.

The live Kalshi contract fetch failed; market findings therefore use the saved timestamped responses. The live [Airbnb events page](https://investors.airbnb.com/events-and-presentations/default.aspx) exposed empty event sections, which does not independently establish that its dynamically loaded calendar contains no event. Snippet-only sell-side and recency claims remain uncorroborated and receive no weight in my comparison forecasts.

In the table, `C02/log` and `C03/log` mean the respective `research-log.md` files under `docs/pitch-forecasts/questions/q4-nights-bucket/` and `fy26-revenue-guide-language/`. Claim numbers and section references identify exact fields.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix (with the recomputed number where available) |
|---|---|---|---|---|---|---|
| A02-01 | C03 | major | C03/log claim 10; §5 anchor; JSON `estimates.anchor_source` | Quarterly kappa is applied to the **entire FY consensus**, including already reported revenue. It also measures consensus at the quarter’s eventual print, not necessarily the November pre-guide consensus. The resulting “Street-implied FY guide” is not a measured annual anchor. | Recomputed kappa from L0 at-print rows matched to quarterly guidance: **0.603954%, n=12**, trailing-eight **0.515673%**. The underlying observations are quarterly. `$14,189.55705 / 1.006 = $14,104.92749`, reproducing the faulty construction. | Remove the annual deflation. Merely applying the same assumed 0.6% adjustment to Q4 gives **$14,170.70 / +15.764%**, or **$14,173.28 / +15.785%** using the quarterly consensus sum. These are illustrative repairs, not validated guidance anchors. The correction crosses the log’s important 15.5% rounding boundary. |
| A02-02 | C02 | major | C02/log claim 1; §5 base rate; `datasets/nights_descriptor_vs_printed_and_comp.csv`, 4Q24 row; `decomposition.py` pending-row exclusion | “Stable” at the 4Q24 print compares next-quarter growth with **1Q24 excluding Leap Day**, not with just-printed 4Q24 growth. Also, excluding the pending 2Q26 guide is inappropriate when studying an already-observed **descriptor**, rather than its eventual accuracy. | Original 4Q24 letter and ledger quote specify 1Q24. Driver history gives **1Q24 +9.496%**, versus **4Q24 +12.348%**; excluding Leap Day further lowers the comparator. The 2Q26 bucket midpoint is already known: **11% versus +10.342% printed**. The 1Q23 “below revenue growth” comparison requires a separate inference; its revenue-guide upper bound is below just-printed nights growth, so “down” remains supportable. | Corrected counts across all **17** observable descriptors: **down 10, stable 4, up 3**. Resolved-only: **10/4/2, n=16**. By print-quarter window: **W1 9/2/3, n=14; W2 6/2/2, n=10**. A strict sample excluding both indirect comparators gives **8/4/3, n=15**. |
| A02-03 | C02 | major | C02/log §5 decomposition; JSON `conditioning`; `datasets/decomposition.py`, `pQ3` | The **0.38/0.42/0.20** Q3 branch probabilities are hard-coded, not derived from the cited error distribution. A normal distribution centered at 9.5–9.6 with SD 1.48 cannot put 42% in the one-point interval 9–10. | Under **N(9.5, 1.48²)**, the branches ≥10 / 9–10 / <9 are **0.367743 / 0.264515 / 0.367743**. At mean 9.6 they are **0.393476 / 0.263934 / 0.342590**. Maximum possible one-point interval mass at this normal SD is **26.4515%**. | Supply the actual empirical or explicitly assumed predictive distribution. Holding the log’s conditional vectors fixed and using N(9.5,1.48²) produces **(0.199291, 0.168516, 0.382322, 0.216194, 0.033677)** before final adjustments. A nonnormal distribution could differ, but must be shown. |
| A02-04 | C03 | major | C03/log claims 2–4; §5 base rate | The November reference class selects the three years containing an annual point sentence, omitting **2022**, when an existing FY margin guide disappeared from the letter. Margin-point conversion is also not a direct observation of a **≥1-point revenue raise**. | `05_guide_language_pattern.csv` records November FY sentence types: **2021 none, 2022 none, 2023 approx_yoy, 2024 approx, 2025 approx**. The 2Q22 letter contains an FY2022 margin guide; the 3Q22 letter does not. The two numeric-floor conversions are **+0.5pp**, not +1pp. | Report **3/4 November letter conversions when a same-year FY guide existed**, alongside the recent-regime **3/3** and numeric-floor **2/2** sensitivities. FY revenue updates are **2/2 raises**, but there are **zero prior November updates of this revenue line**. Treat the 45% base-rate vector as an analogical judgment, not an empirical MC frequency. |
| A02-05 | C02, C03 | major | C02/log claims 14–15; C03/log claim 14; both anchor descriptions | “Quotes only, no trade/no volume” results from reading absent legacy fields. This is used to dismiss contrary market evidence. The claim that the quarterly and annual ladders are “mutually inconsistent” is also not established by subtracting their medians. | Saved `kalshi_market_KXABNB-26NOVNEB-148000000_20260917T025502Z.json` contains **`volume_fp="428.14"`**, **`open_interest_fp="423.14"`**, bid **0.50**, ask **0.55**, alongside `liquidity_dollars="0.0000"`. The other saved contracts also contain positive fractional volume fields. | Describe a thin adjacent market with reported trading activity; do not infer no trading from a zero liquidity field. Preserve the mandated team-conditioned forecast, but retain this as contrary evidence. A bearish implied Q4 is not a logical contradiction, and marginal medians need not add. |
| A02-06 | C02, C03 | major | Both logs §5; both `datasets/decomposition.py`, `base`/`anchor` assignments | The claimed three estimates are not independently calculated probability estimates. Their common assumptions manufacture much of their agreement. The market/consensus **levels** are real; the probability vectors attributed to them are hand assignments. | C02’s anchor vector is a literal dictionary, while its base rate assumes a **2:1** split of down-descriptors between (c)/(d). Its decomposition has three judgmental five-option conditional vectors. C03’s base and anchor vectors are literal dictionaries; its decomposition depends on chosen format and rounding weights. | Keep `NOT_INDEPENDENTLY_DERIVED`, and explicitly label these as **dependent judgmental constructions**. Show the level-to-language mapping and vary it. The six-/seven-point final–anchor differences are not evidence of independent agreement. |
| A02-07 | C03 | major | C03/log claim 7, “80% band 3,156–3,201”; claim 9 distribution | The bridge’s min/max conversion envelope is mislabeled an **80% predictive interval**. The later FY SD additionally assumes independent Q3-print and Q4-guide errors without stating that assumption. | `analysis/src/h1_to_h2_bridge_v3.py:436`–437 calculates `revenue_low/high` using **min/max historical conversion**, with lagged GBV fixed. It exactly reproduces **$3,156.008–3,201.217M**. `math.hypot(40,80)` establishes the zero-correlation assumption. | Rename the interval a historical-conversion envelope. Label the $40M/$80M SDs as assumptions and include shared-demand dependence. At correlation **0.5**, FY SD becomes **0.864554pp**, versus **0.730681pp**; decomposition (d) rises from **0.090801 to 0.110137**. |
| A02-08 | C02 | major | C02/log claims 3–4; §4 cushion reasoning; §5 anchor | Five successful nights/GBV bucket rows are treated as stronger evidence for a general nights cushion than the sample warrants. Realized forecast errors are also conflated with management deliberately subtracting a fixed cushion from expected growth or Street estimates. | Ledger recomputation: **5/5 above the top**, but only **three print events** and **two nights observations**. Nights actual-minus-midpoint values are **+4.82pp and +1.15pp**; above-top values **+3.82pp and +0.15pp**. These are not five independent nights tests or a measured 1–3pp policy. | Keep the observed conservatism, with n and clustering explicit. Treat “Street minus 1–3 points” as a sensitivity assumption. Do not claim it identifies management’s expectation or a stable cushion. |
| A02-09 | C02 | major | C02/log §6, `P(bucket ≥ "around 10", a+b)` and `P(descriptor at or below "high single digits", c+d)` | These ordinal summaries silently turn language categories into numerical growth thresholds. Option (d) includes **any bucket-free moderation**, while option (b) includes “similar to Q3” whenever Q3 is below 10%, without a lower bound. | Re-read C02’s registry definition. The saved 3Q23 letter uses “moderate”; its call says a few points below Q3’s **13.541%**. The language category does not impose a ≤9% growth ceiling. | Report literal unions **P(a or b)=0.40**, **P(c or d)=0.56**. Carry directional-only and explicit low-growth subcategories separately into scenario synthesis. |
| A02-10 | C03 | major | C03/log §6, “(d) … short case’s ‘FY26 floor weakened’ leg” | The downstream coherence note substitutes **revenue** guidance for the **margin** floor in X01. | `QUESTIONS.md`, X01, defines that short-case leg as **“FY26 margin floor weakened.”** C03 resolves revenue language; C04 resolves margin guidance. | Remove this mapping. C03(d) may correlate with C04(d), but it cannot satisfy the X01 margin trigger. Supply a joint assumption if using their correlation. |
| A02-11 | C02 | minor | C02/log claim 8 and freshness/source attribution | The claimed **8.5–10.0** nowcast band matches the pitch brief but not the cited nowcast source. The discrepancy is not acknowledged. | `docs/q3nowcast/SYNTHESIS.md:9`, `:19`, `:40` state **8.5–11.0**; `h2_bridge_v3_rebased_lines.csv` also carries **8.5–11.0**. | Preserve the brief’s imposed conditioning convention, but distinguish it from the source’s published band. Explain how either “band” relates to the predictive error distribution; neither alone specifies probabilities. |
| A02-12 | C02 | minor | C02/log claim 18; §4 directional-format row | Two supporting counts are wrong: reaction-panel down-directions and “12 of 16 pre-2025” directional guides. | `abnb_guidance_reaction_panel.csv` has **8 negative, 6 zero, 3 positive, 6 missing**, not 9 negative. The selected nights ledger has **14 directional/17 total**, with **11/11 before 2025**. | Correct both counts and state the window. The reaction panel is a derived encoding of the same letters, not independent corroboration. |
| A02-13 | C02 | minor | C02/log claim 13, “45th percentile” | Position within the high–low range is mislabeled as an analyst percentile. | `E_street_distribution_vs_team.csv` calls the field `team_position_pct_of_range`: **(132.7−130)/(136−130)=45%**. No individual-estimate ranks are supplied. | Say **45% of the way from the minimum to maximum**, not 45th percentile. |
| A02-14 | C03 | minor | C03/log claims 6–7; consensus provenance | Quarterly revenue consensus uses the EBITDA contributor count. The source’s observation date is also omitted from the freshness discussion. | `03_current_consensus.csv`: Q3/Q4 **revenue_n=37**, **ebitda_n=36**. Revenue means are **$4,744.32212M / $3,161.81627M**; FY26 **$14,189.55705M, n=44**. Rows are dated **September 11**, with revenue observation dates **September 7**. | Use the metric-specific n and preserve both dates. Cite this provenance file/note alongside the copied summary. Do not treat a later copy or model-publication date as a refreshed consensus observation. |
| A02-15 | C02, C03 | minor | Both logs §6; JSON `leading_option_ci` | “Credible ranges” are extrema of selected sensitivity cases, with no stated probability coverage or distribution over assumptions. | Both logs explicitly derive their intervals from §7 scenario spans. No posterior or coverage calculation is supplied. | Rename them **sensitivity ranges**, or specify a genuine second-order uncertainty model and coverage level. |
| A02-16 | C02 | minor | C02/log §6, concentration of (a) in Q3≥10 branch | The stated **80%** concentration does not reproduce, and the published joint statement refers to the decomposition rather than an explicitly adjusted final joint distribution. | **0.38×0.42 / 0.2116 = 75.4253%**. The final vector also shifts mass from the decomposition. | Report **75.4% under the original tree**, and provide the final joint table before X01 consumes it. |

## C02 — what the log does well and should keep

Keep the letter-over-call hierarchy, the distinction between directional moderation and explicit low growth, and the omission branch. The original-letter checks support all 17 quoted nights descriptors. The November directional count **3 down / 4 observations** reproduces.

Keep the adopted Q4 input **8.12%** from `h2_bridge_v3_rebased_lines.csv` and the separately labeled RNPL scenario **7.61%** from `docs/rnpl-short-audit/00_SYNTHESIS.md`. They are alternative assumptions, not independent confirmations. The conditional-tree arithmetic and reported sensitivity calculations reproduce.

The strongest case against the modal “high single digits” forecast is that management can express a broadly similar economic outlook through bucket-free moderation, resolving (d). Conversely, a strong October can produce the 3Q24-style acceleration language. Neither requires the RNPL thesis to be entirely right or wrong.

## C03 — what the log does well and should keep

Keep the explicit distinction between FY language and the sum of quarterly revenue figures. FY25 revenue **$12,241M**, H1 FY26 **$6,286M**, and the log’s implied annual mean **$14,166M / +15.7258%** reproduce.

The quarterly revenue evidence also reproduces: **19/19 midpoint beats**, including **14/14 in W1 and 10/10 in W2**; trailing-eight mean cushion **1.856743%**; Q4 mean **3.850965%, n=5**, and last-three mean **3.041893%, n=3**. November margin-point beats are **77/90/10bp**, mean **59bp**, but remain margin analogies.

Keep the Street-centered and B2 sensitivity cases: they reproduce and reveal that the leading option depends materially on the economic center and rounding convention. The strongest counterargument is that favorable annual arithmetic does not force a revenue-language raise: retaining the floor or omitting a redundant sentence can convey the same underlying outlook.

## Independent comparison forecasts

These are independently constructed **audit judgments using the verified repository inputs**, not blind second forecasts or validated statistical estimates. Both retain the original question’s option labels.

| Question | (a) | (b) | (c) | (d) | (e) |
|---|---:|---:|---:|---:|---:|
| C02 | **0.17** | **0.18** | **0.30** | **0.30** | **0.05** |
| C03 | **0.35** | **0.19** | **0.21** | **0.10** | **0.15** |

**C02 derivation, line 1:** Assign explicit-bucket/directional/omission probabilities **0.60/0.35/0.05**; conditional explicit-bucket vector **(0.20,0.15,0.50,0.15,0)**, reflecting the 8.12% Q4 baseline and uncertain conservatism.  
**C02 derivation, line 2:** Within directional language, assign **60% moderation** and **40% stable/up**, splitting the latter across (a)/(b) using **P(Q3≥10)=0.367743** from the explicitly assumed N(9.5,1.48²) distribution; the mixture is **(0.171484,0.178516,0.30,0.30,0.05)**.

**C03 derivation, line 1:** Use **$6,286 + $4,804.0355 + $3,178.1078/(1+3.041893%) = $14,174.3227M**, or **15.7938%**, with a judgmental **$110M aggregate SD** and equal weights on nearest-integer and round-down wording.  
**C03 derivation, line 2:** Assign numeric/descriptive/omission probabilities **0.50/0.35/0.15**; descriptive conditional vector **(0.25,0.55,0.10,0.10,0)** gives **(0.346856,0.192500,0.209775,0.100869,0.15)**.

No deterministic inequality links the C02 and C03 marginals. Their shared demand and management-language drivers require a joint model for scenario aggregation. Neither question requires an R/B impact table, and neither final vector triggers the MC ≤2% gate.

## Reproduction script

Save as `docs/pitch-forecasts/audits/A02-reproduce.py` and run from the repository root:

`python docs/pitch-forecasts/audits/A02-reproduce.py`

```python
"""A02 read-only audit reproduction.
Dependencies: Python standard library and pandas. No writes or network calls.
"""
from pathlib import Path
from math import erf, sqrt
import json
import re
import html
import pandas as pd

ROOT = Path.cwd()
if not (ROOT / "data/processed/overnight/02_guidance_ledger.csv").exists():
    ROOT = next(
        p for p in Path(__file__).resolve().parents
        if (p / "data/processed/overnight/02_guidance_ledger.csv").exists()
    )


def read(path):
    return pd.read_csv(ROOT / path, comment="#")


def show(label, value):
    print("\n" + label)
    print(value.to_string(index=False)
          if isinstance(value, pd.DataFrame) else value)


def key(q):
    return (2000 + int(q[-2:])) * 4 + int(q[0]) - 1


def period(q):
    return "20" + q[-2:] + "Q" + q[0]


def phi(z):
    return 0.5 * (1 + erf(z / sqrt(2)))


def vector(values):
    return dict(zip("abcde", [round(float(x), 6) for x in values]))


ledger = read("data/processed/overnight/02_guidance_ledger.csv")
history = read(
    "data/processed/abnb_driver_history_quarterly.csv"
).set_index("quarter")

nights = ledger[
    (ledger.metric == "nights_yoy_pct")
    & (ledger.horizon_quarters == 1)
].copy()
nights["key"] = nights.print_quarter.map(key)
nights = nights.sort_values("key")
nights["printed_growth"] = nights.print_quarter.map(
    history.nights_m_yoy_pct
)

# Verify ledger quotations against original saved letters.
def normalize(s):
    return re.sub("[^a-z0-9]", "", s.lower())


fy_revenue = ledger[
    (ledger.metric == "revenue_yoy_pct")
    & ledger.target_period.str.startswith("FY")
].copy()

for _, row in pd.concat([nights, fy_revenue]).iterrows():
    raw = (ROOT / row.source_file).read_text(
        encoding="utf-8", errors="replace"
    )
    text = html.unescape(re.sub("<[^>]+>", " ", raw))
    assert normalize(row.quote) in normalize(text), row.guide_id

show("Original-letter quote checks", len(nights) + len(fy_revenue))

# 1Q23 compares nights with next-quarter revenue growth.
# Its revenue-guide upper bound is below just-printed nights growth.
r23 = ledger[
    (ledger.print_quarter == "1Q23")
    & (ledger.metric == "revenue_usd_m")
].iloc[0]
upper23 = 100 * (
    r23.value_high / history.loc["2Q22", "revenue_musd"] - 1
)
assert upper23 < history.loc["1Q23", "nights_m_yoy_pct"]

# 4Q24 compares with 1Q24 EXCLUDING Leap Day, not printed 4Q24.
assert (
    history.loc["1Q24", "nights_m_yoy_pct"] - 1
    < history.loc["4Q24", "nights_m_yoy_pct"]
)


def classify(row):
    if row.guide_type == "bucket":
        delta = row.value_mid - row.printed_growth
        return (
            "down" if delta < -0.5
            else "up" if delta > 0.5
            else "stable"
        )
    if row.print_quarter == "4Q24":
        return "down"
    return {
        "below": "down",
        "below_revenue_growth": "down",
        "above": "up",
        "stable": "stable",
        "approx": "stable",
    }[row.direction]


nights["class"] = nights.apply(classify, axis=1)
show("Corrected descriptor classes", nights[
    ["print_quarter", "guide_type", "direction",
     "printed_growth", "class"]
])

for label, sample in [
    ("all observable guides", nights),
    ("resolved target quarters only", nights[nights.actual.notna()]),
    ("W1: print quarter 1Q23+", nights[nights.key >= key("1Q23")]),
    ("W2: print quarter 1Q24+", nights[nights.key >= key("1Q24")]),
    (
        "direct-comparison-only sensitivity",
        nights[~nights.print_quarter.isin(["1Q23", "4Q24"])],
    ),
]:
    show(label, {
        "n": len(sample),
        **sample["class"].value_counts().to_dict(),
    })

show("Format counts, all 17",
     nights.guide_type.value_counts().to_dict())
show("Format counts, print before 2025",
     nights[nights.key < key("1Q25")]
     .guide_type.value_counts().to_dict())
show("November nights classes",
     nights[nights.print_quarter.str.startswith("3Q")]
     ["class"].value_counts().to_dict())

reaction = read("data/processed/abnb_guidance_reaction_panel.csv")
show("Reaction-panel direction counts",
     reaction.nq_nights_dir.value_counts(dropna=False).to_dict())

vol = ledger[
    (ledger.guide_type == "bucket")
    & ledger.metric.isin(["nights_yoy_pct", "gbv_yoy_pct"])
    & ledger.actual.notna()
].copy()
vol["beat_mid_pp"] = vol.actual - vol.value_mid
vol["beat_top_pp"] = vol.actual - vol.value_high
show("Resolved volume buckets", vol[
    ["print_quarter", "metric", "actual",
     "beat_mid_pp", "beat_top_pp"]
])
show("Volume sample dependence", {
    "rows": len(vol),
    "print_events": vol.print_quarter.nunique(),
    "above_top": int((vol.actual > vol.value_high).sum()),
    "nights_rows": int((vol.metric == "nights_yoy_pct").sum()),
})

rev = ledger[
    (ledger.metric == "revenue_usd_m")
    & (ledger.guide_type == "range")
    & ledger.actual.notna()
].copy()
rev["key"] = rev.target_period.map(key)
rev = rev.sort_values("key")
rev["cushion_pct"] = 100 * (rev.actual / rev.value_mid - 1)

for label, sample in [
    ("all", rev),
    ("W1 target 1Q23+", rev[rev.key >= key("1Q23")]),
    ("W2 target 1Q24+", rev[rev.key >= key("1Q24")]),
]:
    show("Revenue beats " + label, {
        "n": len(sample),
        "above_mid": int((sample.actual > sample.value_mid).sum()),
        "above_top": int((sample.actual > sample.value_high).sum()),
    })

t8 = rev.tail(8).cushion_pct
show("Trailing-eight cushion mean/median/sample SD",
     (t8.mean(), t8.median(), t8.std()))

q4 = rev[rev.target_period.str.startswith("4Q")]
show("Q4 cushions", q4[["target_period", "cushion_pct"]])
show("Q4 mean/median/last-three mean", (
    q4.cushion_pct.mean(),
    q4.cushion_pct.median(),
    q4.tail(3).cushion_pct.mean(),
))

fy_revenue["key"] = fy_revenue.print_quarter.map(key)
fy_revenue = fy_revenue.sort_values("key")
fy_revenue["change"] = (
    fy_revenue.groupby("target_period").value_mid.diff()
)
show("FY revenue guide updates", fy_revenue[
    ["print_quarter", "target_period", "value_mid", "change"]
])
show("Revenue raises/updates", (
    int((fy_revenue.change > 0).sum()),
    int(fy_revenue.change.notna().sum()),
))

margin = read(
    "data/processed/margin_build/05_mgmt_statements_v2/"
    "05_guide_language_pattern.csv"
)
nov = margin[
    margin.is_november.astype(str).str.lower().eq("true")
]
show("All November margin sentences", nov[
    ["print", "fy_sentence_type", "actual_minus_guide_bp",
     "q4_actual_minus_implied_pts"]
])
show("November point beats: n/mean bp", (
    int(nov.actual_minus_guide_bp.notna().sum()),
    nov.actual_minus_guide_bp.mean(),
))
eligible = nov[
    nov["print"].isin(["3Q22", "3Q23", "3Q24", "3Q25"])
]
show("November letters with an existing same-year FY guide", {
    "n": len(eligible),
    "approx_point": int(
        eligible.fy_sentence_type.str.startswith("approx").sum()
    ),
    "omitted": int(eligible.fy_sentence_type.eq("none").sum()),
})

# Recompute quarterly kappa from L0's named at-print vintage rows.
vintages = read(
    "data/processed/forecast_methods/L0/L0_vintage_register.csv"
)
ap = vintages[
    vintages.register_id.eq("AP-" + vintages.period + "-revenue")
]
rev["period"] = rev.target_period.map(period)
pairs = rev.merge(ap, on="period")
pairs["kappa_pct"] = 100 * (pairs.value / pairs.value_mid - 1)
lseg = pairs[pairs.vendor == "LSEG"].sort_values("key")
show("L0 quarterly kappa: n/mean/sample SD/trailing-eight mean", (
    len(lseg),
    lseg.kappa_pct.mean(),
    lseg.kappa_pct.std(),
    lseg.tail(8).kappa_pct.mean(),
))

current = read(
    "data/processed/margin_build/03_consensus_pit/"
    "03_current_consensus.csv"
)
current = current[
    (current.vendor == "LSEG")
    & current.period.isin(["3Q26", "4Q26", "FY26"])
].set_index("period")
show("Actual consensus provenance", current.reset_index()[
    ["period", "as_of_row_date", "revenue_obs_date",
     "revenue_mean", "revenue_n", "revenue_sd", "revenue_high"]
])

fy25 = history.loc[
    ["1Q25", "2Q25", "3Q25", "4Q25"], "revenue_musd"
].sum()
h1 = history.loc[["1Q26", "2Q26"], "revenue_musd"].sum()
annual = current.loc["FY26", "revenue_mean"]
q4street = current.loc["4Q26", "revenue_mean"]

for label, total in [
    ("log: deflate entire FY", annual / 1.006),
    (
        "illustrative: deflate only Q4",
        annual - q4street + q4street / 1.006,
    ),
    (
        "quarter-sum version",
        h1 + current.loc["3Q26", "revenue_mean"]
        + q4street / 1.006,
    ),
]:
    show(label, {
        "musd": total,
        "growth_pct": 100 * (total / fy25 - 1),
    })

bridge = read(
    "data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv"
).set_index("quarter")
b4 = bridge.loc["4Q26"]
show("Bridge range is fixed-GBV conversion extrema", (
    1000 * b4.lagged_gbv_busd * b4.conversion_min,
    1000 * b4.lagged_gbv_busd * b4.conversion_max,
))
show("Bridge points",
     bridge.reset_index()[["quarter", "revenue_musd"]])

# Distribution assumptions are explicit; not fitted here.
cond = [
    [.42, .20, .28, .08, .02],
    [.10, .22, .50, .15, .03],
    [.05, .10, .40, .40, .05],
]


def mix(weights):
    return [
        sum(weights[j] * cond[j][i] for j in range(3))
        for i in range(5)
    ]


show("C02 original decomposition", vector(mix([.38, .42, .20])))
for mu in [9.5, 9.6]:
    bins = [
        1 - phi((10 - mu) / 1.48),
        phi((10 - mu) / 1.48) - phi((9 - mu) / 1.48),
        phi((9 - mu) / 1.48),
    ]
    show("C02 normal bins " + str(mu), bins)
    show("C02 repaired-bin tree " + str(mu), vector(mix(bins)))

show("Maximum one-point interval mass under SD 1.48",
     2 * phi(.5 / 1.48) - 1)
show("Original P(Q3 >=10 | C02=a)",
     .38 * .42 / mix([.38, .42, .20])[0])

paths = read("data/processed/q3nowcast/E/backtest_wf_paths.csv")
errors = paths[
    (paths.feature == "GLOBAL|yoy_all|w_equal")
    & (paths.lag == 0)
    & (paths.target == "nights_yoy")
    & (paths.window == "2023Q1+")
]
show("Reviews error sample: n/RMSE/naive RMSE/mean/sample SD", (
    len(errors),
    sqrt(errors.err_feature.pow(2).mean()),
    sqrt(errors.err_naive.pow(2).mean()),
    errors.err_feature.mean(),
    errors.err_feature.std(),
))


def c03(q3m=4795, q3s=40, q4m=3085, q4s=80, rho=0):
    mu = h1 + q3m + q4m
    sd = sqrt(q3s*q3s + q4s*q4s + 2*rho*q3s*q4s)

    def below(rate):
        return phi((fy25*(1+rate/100)-mu)/sd)

    a = (.5*(1-below(15.5)) + .5*(1-below(16))) / 1.02
    c = (
        .5*(below(15.5)-below(14.5))
        + .5*(below(16)-below(15))
    ) / 1.02
    d = (.5*below(14.5) + .5*below(15)) / 1.02
    return {
        "fy_mean": mu,
        "growth_pct": 100*(mu/fy25-1),
        "sd_pp": 100*sd/fy25,
        "p_ge16": 1-below(16),
        "vector": vector([
            .55*a+.35*.30,
            .55*.02/1.02+.35*.45,
            .55*c+.35*.15,
            .55*d+.35*.10,
            .10,
        ]),
    }


show("C03 original", c03())
show("C03 Street-centred", c03(q3m=4744, q3s=30))
show("C03 B2 guide", c03(q4m=3161, q4s=117))
show("C03 positive-correlation sensitivity", c03(rho=.5))

questions = ROOT / "docs/pitch-forecasts/questions"
for slug in ["q4-nights-bucket", "fy26-revenue-guide-language"]:
    f = json.loads(
        (questions/slug/"forecasts/2026-09-17-forecast.json")
        .read_text(encoding="utf-8")
    )
    assert abs(sum(f["final"]["vector"].values()) - 1) < 1e-12

market = json.loads(
    (
        questions/"q4-nights-bucket/sources/"
        "kalshi_market_KXABNB-26NOVNEB-148000000_20260917T025502Z.json"
    ).read_text(encoding="utf-8")
)["market"]
show("Kalshi stored fields", {
    k: market.get(k) for k in [
        "volume", "volume_fp",
        "open_interest", "open_interest_fp",
        "liquidity_dollars", "yes_bid_dollars", "yes_ask_dollars",
    ]
})

# Audit comparisons: judgmental weights, NOT fitted estimates.
p10 = 1 - phi((10-9.5)/1.48)
explicit = [.20, .15, .50, .15, 0]
directional = [.40*p10, .40*(1-p10), 0, .60, 0]
own02 = [
    .60*explicit[i] + .35*directional[i]
    + (.05 if i == 4 else 0)
    for i in range(5)
]
show("Audit C02 unrounded", vector(own02))

mu = (
    h1
    + bridge.loc["3Q26", "revenue_musd"]
    + b4.revenue_musd/(1+q4.tail(3).cushion_pct.mean()/100)
)


def below(rate):
    return phi((fy25*(1+rate/100)-mu)/110)


a = .5*(1-below(15.5)) + .5*(1-below(16))
d = .5*below(14.5) + .5*below(15)
own03 = [
    .50*a+.35*.25,
    .35*.55,
    .50*(1-a-d)+.35*.10,
    .50*d+.35*.10,
    .15,
]
show("Audit C03 unrounded", {
    "mean_musd": mu,
    "vector": vector(own03),
})
```