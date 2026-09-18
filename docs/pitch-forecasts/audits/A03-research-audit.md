**C04 — Verdict:** The 42% probability for the 36% bucket is plausible, but its supporting derivation is not audit-ready.  
**Reviewed vector:** held 26%; 36% 42%; ≥36.5% 5%; softer/lower 24%; absent 3%.  
**Question fidelity:** Correct event and object; uncommon numeric wording remains incompletely classified.  
**Must change first:** Correct the historical-raise claim, distinguish positive cushion from rounding tolerance, and reconcile the published conditionals.  
**Disposition:** Revise the justification and joint distribution; this audit does not establish that 42% itself is materially wrong.

**C09 — Verdict:** The 40% probability of “up” is defensible as judgment, but not as the claimed independently corroborated estimate.  
**Reviewed vector:** down 28%; approximately flat 27%; up 40%; absent 5%.  
**Question fidelity:** Correct event and margin object; the historical classification sometimes mistakes EBITDA-dollar wording for margin wording.  
**Must change first:** Rebuild the reference class with one next-quarter observation per print and regenerate conditionals after the final adjustments.  
**Disposition:** Retain substantial uncertainty between all three directional outcomes; the arithmetic does not force an “up” sentence.

## Scope and verified results

Read-only audit of both research logs, forecast JSONs, all supplied datasets, market snapshots, and the cited underlying guidance, margin, consensus and reaction files. Both folders’ `datasets/` and `sources/` are byte-identical.

The supplied Monte Carlo was executed **in memory after removing its final file-writing statement**. Both raw vectors reproduced exactly:

| Calculation | Reproduced result |
|---|---|
| C04 raw MC, a/b/c/d/e | 0.186060 / 0.352978 / 0.053988 / 0.386825 / 0.020150 |
| C09 raw MC, a/b/c/d | 0.302613 / 0.218548 / 0.428478 / 0.050363 |
| Internal FY26 margin | Mean 35.7372%; SD 0.5324pp |
| Numeric-floor November rule | Exact 2/2; November type rule 4/5 |
| November FY cushion | Ledger: +0.77/+0.90/+0.10pp, mean +0.59pp |
| November Q4 actual minus sentence-implied margin | Mean +2.8684pp, n=3 |
| Historical November Street-direction matches | 3/3, using properly dated pre-guide LSEG observations |
| Quarterly guide classified as met | W1: 13/14; W2: 9/10 |
| Both final MC vectors | Sum to 1; no option triggers the ≤2% MC gate |

The September conference transcript was absent at its cited local raw path, but its online counterpart was accessible and corroborates the attributed remarks about margins, investment capacity and forthcoming announcements. It does not quantify Q4 launch spending. [September 8 conference transcript](https://stockanalysis.com/stocks/abnb/transcripts/739626-goldman-sachs-communacopia-technology-conference-2026/)

`py -3.13` was unavailable; the repository’s `python` worked. No files were written, no scorers were run, and neither prohibited raw-data directory was opened. Impact tables are not applicable to these C questions.

## Findings

References below use:

- **C04 log:** `docs/pitch-forecasts/questions/fy26-margin-sentence/research-log.md`
- **C09 log:** `docs/pitch-forecasts/questions/q4-margin-direction-sentence/research-log.md`
- **A03 datasets:** `docs/pitch-forecasts/questions/fy26-margin-sentence/datasets/`
- **Margin data:** `data/processed/margin_build/`

No critical silent change to the question’s event or conditionality was established.

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A03-01 | C09 | major | C09 log:31–32, 75, 81; `quarterly_margin_sentence_ledger.csv` | “21 of 21” next-quarter disclosures and the recent 8/10 down-family count use an invalid denominator. The copied dataset includes the **2Q25 guide for 4Q25**, a two-quarter-ahead observation. It also overlooks the 4Q21 print’s lack of a quarterly margin sentence. | Filtered `02_guidance_ledger.csv` to exact EBITDA-margin metrics and independently calculated target-minus-print horizon; joined to all print opportunities in `abnb_guidance_reaction_panel.csv`. Read the 4Q21 letter: its Q1 outlook gives EBITDA dollars, not a quarterly margin sentence. | **20/21** prints since 2Q21 contain a next-quarter margin sentence. Among those 20: down family **11**, flat **1**, up family **8**. Since the 2Q24 print: down **7/9**, flat **1/9**, up **1/9**. November remains **5/5 disclosed**, with three up-family and two down. |
| A03-02 | C04 | major | C04 log:45, 96, 101 | The claimed reaction-panel evidence for “two mid-year raises,” both with `fy_margin_raised=1`, is false. The broader claim that mid-year strengthening first appeared in 2026 also depends on ignoring qualitative changes. | `abnb_guidance_reaction_panel.csv`: **1Q26 = `first`, raised=0**, delta=0; **2Q26 = `raised`, raised=1**, delta=0.5. Original letters change FY22 from in-line to expansion and FY23 from broadly in-line to modestly higher. | Say **May introduced a 35% numeric floor; August raised it to 35.5%**. The panel’s 0/8 prior coded raises reproduces, but it is not 0/8 qualitative upgrades. Recalculate the “spent cushion” adjustment under a consistent definition. |
| A03-03 | C04 | major | C04 log:90, 96 | The disclosure reference class is selected partly on the outcome: “any November with an FY margin sentence” cannot estimate whether that sentence will be given. “3/3 with an FY margin guide in force” omits FY22. | The guidance ledger contains a 2Q22 FY2022 margin-expansion guide; `05_guide_language_pattern.csv` and the 3Q22 letter contain no FY margin sentence at November. | Separate **2/2 numeric-floor conversions** from **3/4 November disclosures in FY2022–25 with a pre-existing FY margin outlook**. The latter is less comparable to 2026, but it prevents calling disclosure automatic. |
| A03-04 | C04 | major | C04 log:54, 101; model `tol`, `condA`; §7 tolerance sensitivity | Positive historical realised cushions are used to justify a **negative required cushion**. With `tol=+0.15`, an internal 35.85% supports a 36% sentence. That is rounding optimism, not “36% with any cushion.” “Zero tolerance” also does not require the claimed 0.9pp cushion. | Code uses `fy >= 36 - tol`. Historical actual-minus-November-guide cushions are all positive. Holding other assumptions fixed, setting tolerance to **−0.10** gives raw P(b) about **21.7%**, versus **35.3%** at +0.15; tolerance zero gives **26.8%**. | Model rounding tolerance and desired positive cushion separately. Label their distributions as judgment: realised errors do not identify management’s internal forecast. Correct the sensitivity labels before blending. These alternatives are diagnostics, not automatic replacement forecasts. |
| A03-05 | C04, C09 | major | Both forecast JSONs: `conditionals`; C04 log:112–113; C09 log:95 | Published conditionals do not belong to the final marginal distributions. The saved joint is the **raw MC joint**, before the hold/soften reassignment and wording haircut. | At the stated P(C01)=0.80, C04 gives **0.8×0.33 + 0.2×0.56 = 0.376**, not 0.42. C09 gives **(0.296, 0.254, 0.400, 0.050)**, not its final vector. Reweighting the raw joint’s individual C04 rows to final C04 weights gives C09 **(0.2600, 0.2177, 0.4719, 0.0504)**. | Publish one final joint distribution and derive every marginal and conditional from it. For illustration, retaining P(C01)=0.80 and P(b\|not below)=0.56 requires **P(b\|below)=0.385** to obtain C04=0.42. |
| A03-06 | C04, C09 | major | Both logs §5; forecast JSONs `anchor_source`, `estimate_vectors` | These are not three independent estimates. The anchor is an internal prior using the same November history, budget identity and consensus inputs as the other estimates. No external probability anchor has been established. | Read M3 and WS05 notes and traced the shared inputs. C04’s base rate and anchor both center P(b)=0.55. C09’s original 60/40 prior is manually redistributed to 50/10/35/5; its supposed “un-priced remainder” does not exist—the original prior already sums to one. | Mark **`NOT_INDEPENDENTLY_DERIVED`** and distinguish internal-prior comparison from external anchoring. A dated LSEG margin level is a genuine external input, but its conversion into wording probabilities is an additional subjective model. |
| A03-07 | C04, C09 | major | C04 log:101; C09 log:86 | The stated information asymmetry versus the September 14 priors is overstated. “Spent mid-year cushion,” the low Q4 comparison and budget arithmetic were already considered. | WS05 explicitly gives the spent-cushion argument in its 35% alternative branch, mentions the 28.3% Q4 base, and computes approximately 36% → Q4 approximately 30.9%. M3 also discusses the Street and Q3/Q4 trade-off. | Identify the newly introduced input as the **C01 distribution and its assumed cost transmission**. Remove claims that previously considered information independently justifies the departure. |
| A03-08 | C04, C09 | major | C04 log:48, 54; C09 log:33, 43; model `q3_margin`, `bias`, `band` | Realised margins versus directional bounds do not identify management’s internal forecast, wording bias or flat-language band. The Q3 distribution also puts substantial weight above a ceiling used elsewhere to reject bullish cases. | W2’s −0.1936pp mean, −0.9395pp median and 4/10 positive observations reproduce as **actual y/y margin changes**. W1’s corresponding mean is **+0.4726pp**. The supplied Q3 normal places **44.53%** above 50.085%. The 1Q26/2Q26 actual outcomes do not reveal internal expectations when those sentences were issued. | Separate actual-outcome uncertainty, management-expectation uncertainty and wording choice. Label the 0.3pp bias, 0.6pp flat band and Q3 distribution as uncalibrated assumptions; show sensitivities. Do not infer a measured internal “conservative tilt” from the pooled signed y/y changes. |
| A03-09 | C04, C09 | major | C04 log:97; C09 log:38, 72; model hold/soften assignment | “Hold and cut” changes C04’s sentence label without changing Q4 costs, margin or C09’s direction. The line build’s removal of Q4 spending is also a floor-preserving assumption, not independent evidence that spending will disappear. | Replaying the stated revised split gives C04 approximately **(0.3034, 0.3530, 0.0540, 0.2694, 0.0202)**, while the existing code leaves Q4 economic draws untouched. `40_short_case_summary.csv` shows the proposed **$176.709M** cut moves Q4 margin from **23.5886% to 29.5467%**. | Implement the cost intervention before generating both sentences, or label the reassignment as a discretionary wording override without claiming a funded cut. Distinguish a held floor under uncertainty from an actually restored budget. |
| A03-10 | C09 | major | C09 log:37, 72, 86, 115 | “Approximately 36% all but forces up” turns conditional budget arithmetic into a language implication. C04(b) also includes 35.75% implied outcomes and floor language, not only a 36% point. | `23_card_budget_identity.csv` gives Q4 **30.1247%** at FY36/Q3 49.94, but **29.0023%** at FY35.75. At the same revenue path, FY36 and Q4=28.3% coexist when Q3 margin is **51.1471%**. The supplied MC itself assigns only 69.4% up conditional on raw C04(b). | State the Q3, revenue and sentence-type conditions. Use the budget identity as a dependency constraint, not a resolution rule. Read the actual Q4 sentence independently. |
| A03-11 | C04, C09 | major | C09 log:35; C04 log:38, 43; consensus anchor descriptions | The LSEG figures mix different panels/fields and hide observation age. The 28.90% figure is a ratio of consensus dollar means, not the separately reported margin-consensus field. | `03_current_consensus.csv`, 4Q26/LSEG: EBITDA **$913.68388M**, revenue **$3,161.81627M**, counts **36/37**, ratio **28.897437%**; `lseg_margin_mean_pct` **28.05833%**. Both dollar observations are dated **2026-09-07**, retrieved into the September 11 row. `23_vs_consensus.csv` agrees. The $3,158M figure belongs to the separate L0 revenue anchor. | Preserve vendor, field, observation date and capture date together. Explain why the ratio is preferred over the separately reported margin field before using its positive y/y sign. The **0.8389pp** EBITDA-dispersion conversion assumes fixed revenue; it is neither a predictive margin SD nor a measured analyst-margin SD. |
| A03-12 | C04 | major | `QUESTIONS.md:97`; C04 log:26 | The option set and adopted conventions are not exhaustive for unusual numerical guidance. Examples include an exact 36.25% point or a 35.6% floor. This is an inherited registry ambiguity, not an established silent redefinition by the forecaster. | Compared the literal 35.75–36.24 band, ≥36.5 bucket and specified softer/lower forms with the conventions. The model avoids the gap by emitting half-point levels. | Have the registry owner define the remaining numeric cases and apply that convention consistently. Until then, identify explicit resolution-ambiguity mass rather than calling the classification complete. |
| A03-13 | C04 | minor | A03 datasets `fy_margin_guide_ledger.csv` | The purported FY EBITDA-margin ledger includes two FCF-minus-EBITDA-margin spread rows and drops the metric identifiers needed to detect this. | Copied file: **22 rows**, including two Free Cash Flow quotes at value 2. Exact EBITDA-margin filtering of the source ledger gives **20 rows**. | Rebuild with exact metric membership; retain `guide_id`, `metric` and units. This does not invalidate the correctly reproduced 2/2 November result. |
| A03-14 | C04, C09 | minor | Quarterly dataset, 3Q25→4Q25 row; C04 claim18; `M3_slightly_magnitude.csv` | The 3Q25 “flat-to-down slightly” phrase describes EBITDA **dollars**; the margin clause says “decline.” This contaminates the three-observation “slightly” magnitude statistic. | Read the original 3Q25 letter and compared the sentence with both CSV classifications. Removing 4Q25 leaves **n=2**, mean absolute margin change **0.96034pp**, versus the contaminated **1.49124pp, n=3**. | Classify the margin clause separately. Use the two-case statistic with its small-sample limitation; retain the three-case result only as a documented rejected extraction. |
| A03-15 | C04, C09 | minor | Claims about market absence; `sources/polymarket_search_airbnb.json`; Kalshi snapshots | “No market exists” is stronger than the saved search coverage. “Volume null” overlooks populated liquidity fields. | Polymarket’s Airbnb response has **`hasMore=true`, `totalResults=190`**, but only five saved events. Kalshi stores a 3,000-event scan summary and only the first event page. Its Q3 >148M market has **`volume_fp=428.14`**; >146M has **998.66**. Quoted bids/asks and fetch timestamps reproduce. | Say **“none found in the saved searches.”** Complete pagination before asserting absence. Report the populated volume field with its units and distinguish fetch time from the older `updated_time`; the latter alone does not prove the quotes are stale. |
| A03-16 | C04, C09 | minor | Both query logs; `sources/web_search_log.md` | The claimed final 72-hour check is not documented as time-restricted, and its subject is broad stock news rather than the decisive guidance/spending variable. | Saved query is “Airbnb ABNB this week”; no date filter is recorded, and the log acknowledges an older result. No raw Investing.com or Yahoo fetch snapshot is present, only a narrative transcription. | Record the actual date restriction, result publication dates and fetched pages. Treat “no new guidance found” as a limited search result, not confirmation of a fresh consensus or spending outlook. |
| A03-17 | C04, C09 | minor | Both logs §8; forecast JSONs `monitoring` | Several proposed updates cease to be probability vectors unless unspecified options absorb the difference. | C04’s “b +4, d −3” adds one point; C09’s “c +5, a −3” adds two. “a +3 per launch” has neither a funding rule nor a dependence adjustment. | Specify complete probability transfers or regenerate the joint distribution after each update. Prevent correlated launch announcements from accumulating independent probability increments. |
| A03-18 | C04 | minor | C04 log:89 | The ≥36.7% internal-margin probability is quoted as approximately 8%, but 8% belongs to ≥36.5%. | Same seeded MC: **P(FY≥36.5)=7.6798%**, **P(FY≥36.7)=3.6448%**, **P(FY≥36.9)=1.5365%**. | Correct the threshold/probability pair and distinguish the convention branch’s 36.9% condition from the rounding branch. |
| A03-19 | C04 | minor | C04 log:114 | The claimed approximately 0.05 expected log-score cost of reallocating two points into tails is not supported; the claimed worst-case probability floor is also incorrect. | Under the stated final vector, moving one point each from b into c/e costs **0.002745 nats** in expected log score; moving both points into e costs **0.005167 nats**. Splitting them leaves e=4%, not 5%. | Specify the exact alternative vector and assumed true distribution, or remove the numerical scoring claim. |
| A03-20 | C09 | minor | C09 log:31, 3Q21 realised comparison | The +12.2pp figure is presented as the realised Q4 y/y expansion; it is the excess over the guided comparison. | `02_guidance_ledger.csv`, 3Q21→4Q21: `actual=24.10`, `comparator_value=11.9`, `distance_from_mid=12.20`. | Report **+24.1pp realised y/y**, versus the approximately +11.9pp comparison; **+12.2pp** is the amount above that comparison. The up-family classification remains correct. |

## C04 — what the log does well and should keep

Keep the exact distinction between a retained **floor** and an “approximately” **point**, including the fact that “approximately 35.5%” resolves as softer language. Keep the original-letter quotations, the explicit rejection of withdrawn M3 LIVE values, and the raw-versus-judgmental decomposition distinction.

The narrow floor-plus-50bp precedent and the thin FY26 budget cushion are both supported. The strongest opposing cases should remain explicit: the **2/2 conversion precedent** favors 36%, while the card’s **35.7266% FY estimate** and uncertain spending make that conversion financially nontrivial. Neither establishes management’s internal expectation.

## C09 — what the log does well and should keep

Keep the distinction between EBITDA dollars and margin, the correctly dated historical Street comparisons, and the 2024 precedent showing that an FY raise can coexist with Q4 margin decline. The **5/5 November disclosure** finding survives.

Keep the competing cost-timing explanations. Q3-specific investment favors Q4 recovery; continued AI or launch spending favors decline. The current evidence does not identify the split, and the forecast should preserve that uncertainty.

## Independent comparison forecasts

These are independent syntheses of the same evidence, **not independent evidence or externally anchored market probabilities**. Their spreads, wording bands and residual allocations are judgmental.

| Question | a | b | c | d | e |
|---|---:|---:|---:|---:|---:|
| **C04** — held / 36% / ≥36.5% / softer-lower / absent | **30%** | **39%** | **6%** | **22%** | **3%** |
| **C09** — down / flat / up / absent | **29%** | **25%** | **41%** | **5%** | — |

**C04 derivation:** A deliberately broad FY-margin distribution, Normal(35.7266%, 0.60pp), assigns 26.69% above 36.10%; blending that affordability check 75% with the 2/2 rule’s Laplace estimate of 75% at 25% weight gives **38.77%** for b.  
Allocate the remainder judgmentally to retaining the floor, softer wording and small higher/absent tails; the 0.10pp cushion requirement is an explicit scenario assumption, not an estimated management rule.

**C09 derivation:** Center expected Q4 margin at the midpoint of the line build’s 28.3% and LSEG’s ratio-implied 28.8974%, use a judgmental 1.8pp predictive SD, and reserve 5% for no sentence.  
A ±0.6pp qualitative flat band around the question’s 28.3% base produces **29.33% down / 24.48% flat / 41.19% up / 5% absent**, rounded above; an actual numeric guide must instead follow the question’s literal midpoint rule.

## Reproduction script

Save as `docs/pitch-forecasts/audits/A03-reproduce.py` and run from the repository root:

```powershell
python docs/pitch-forecasts/audits/A03-reproduce.py
```

The script uses only the standard library and pandas. It recomputes the historical counts and financial identities, and checks the saved probabilities; it does not execute the file-writing Monte Carlo.

```python
from pathlib import Path
from statistics import NormalDist
import json
import math
import re

import pandas as pd

ROOT = Path.cwd()
if not (ROOT / "docs/pitch-forecasts/QUESTIONS.md").exists():
    ROOT = Path(__file__).resolve().parents[3]


def read(rel):
    return pd.read_csv(ROOT / rel, comment="#")


def ordinal(q):
    m = re.fullmatch(r"([1-4])Q(\d{2})", q)
    if not m:
        raise ValueError(q)
    return (2000 + int(m[2])) * 4 + int(m[1])


def family(quote):
    text = quote.lower()
    # 3Q25: "flat-to-down slightly" describes dollars, not margin.
    if "and for adjusted ebitda margin" in text:
        text = text[text.index("and for adjusted ebitda margin"):]
    if "flat to down" in text or "at or slightly below" in text:
        return "flat_to_down"
    if "in-line to modestly higher" in text:
        return "flat_to_up"
    if "approximately flat" in text:
        return "flat"
    if any(word in text for word in ("decline", "lower", "down")):
        return "down"
    return "up"


def counts(frame):
    mapped = frame.family.replace(
        {"flat_to_down": "down", "flat_to_up": "up"}
    )
    return mapped.value_counts().reindex(
        ["down", "flat", "up", "none"], fill_value=0
    ).to_dict()


ledger = read("data/processed/overnight/02_guidance_ledger.csv")
margin = ledger[ledger.metric.isin([
    "adj_ebitda_margin_pct", "adj_ebitda_margin_yoy_pts"
])].copy()
fy = margin[margin.target_period.str.startswith("FY")].copy()

base = ROOT / "docs/pitch-forecasts/questions"
d4 = base / "fy26-margin-sentence"
d9 = base / "q4-margin-direction-sentence"

copied = pd.read_csv(d4 / "datasets/fy_margin_guide_ledger.csv")
print("FY EBITDA-margin rows:", len(fy))
print("Copied rows / FCF rows:", len(copied),
      int(copied.quote.str.contains("Free Cash Flow", case=False).sum()))

quarterly = margin[
    margin.target_period.str.fullmatch(r"[1-4]Q\d{2}")
].copy()
quarterly["horizon_check"] = [
    ordinal(t) - ordinal(p)
    for t, p in zip(quarterly.target_period, quarterly.print_quarter)
]
q = quarterly[
    (quarterly.horizon_check == 1)
    & (quarterly.print_date >= "2021-08-12")
].copy()
q["family"] = q.quote.map(family)
print("Exact next-quarter sentences:", len(q),
      q.family.value_counts().to_dict())

reaction = read("data/processed/abnb_guidance_reaction_panel.csv")
calendar = reaction[
    reaction.print_date >= "2021-08-12"
][["quarter", "print_date"]]
calendar = calendar.merge(
    q[["print_quarter", "family"]],
    left_on="quarter", right_on="print_quarter",
    how="left", validate="one_to_one"
)
calendar["family"] = calendar.family.fillna("none")
print("All print opportunities:", len(calendar), counts(calendar))
print("No quarterly sentence:",
      calendar.loc[calendar.family == "none", "quarter"].tolist())

recent = q[q.print_date >= "2024-08-06"]
nov = q[pd.to_datetime(q.print_date).dt.month == 11]
print("Since 2Q24:", len(recent), counts(recent))
print("Novembers:", len(nov), counts(nov))
for start in ["1Q23", "1Q24"]:
    w = q[q.target_period.map(ordinal).between(
        ordinal(start), ordinal("2Q26")
    )]
    print("Target window", start, "through 2Q26:", len(w), counts(w))

mid = reaction[
    pd.to_datetime(reaction.print_date).dt.month.isin([5, 8])
    & (reaction.print_date >= "2022-01-01")
]
print("Midyear actions:", mid[
    ["quarter", "fy_margin_action", "fy_margin_raised"]
].to_dict("records"))
pre = mid[mid.print_date < "2026-01-01"]
print("Pre-2026 coded raises:",
      int((pre.fy_margin_raised == 1).sum()), "/", len(pre))

novfy = fy[pd.to_datetime(fy.print_date).dt.month == 11]
rule_results = []
for row in novfy.itertuples():
    earlier = fy[
        (fy.target_period == row.target_period)
        & (fy.print_date < row.print_date)
    ].sort_values("print_date")
    if earlier.empty:
        continue
    previous = earlier.iloc[-1]
    if (previous.metric == "adj_ebitda_margin_pct"
            and previous.guide_type == "floor"
            and pd.notna(previous.value_low)):
        predicted = previous.value_low + 0.5
        rule_results.append({
            "print": row.print_quarter,
            "predicted": predicted,
            "stated": row.value_mid,
            "exact": abs(predicted - row.value_mid) < 1e-9,
        })
print("Numeric-floor November rule:", rule_results)
print("Exact matches:",
      sum(r["exact"] for r in rule_results), "/", len(rule_results))
print("Ledger November cushions:",
      (novfy.actual - novfy.value_mid).tolist())
print("Mean ledger November cushion:",
      (novfy.actual - novfy.value_mid).mean())
print("FY2022 pre-November guide:",
      fy.loc[fy.print_quarter == "2Q22", "quote"].tolist())

m3 = "data/processed/margin_build/M3_guide_policy_margin/"
back = read(m3 + "M3_guide_forecast_november_backtest.csv")
print("November type hits:", int(back.type_hit.sum()), "/", len(back))
cushion = read(m3 + "M3_cushion_history.csv")
print("Cushions by bucket:", cushion.groupby("bucket").cushion_pp.agg(
    ["count", "mean"]
).to_dict("index"))

features = read("data/processed/predictive/04_print_features.csv")
for start in ["2023Q1", "2024Q1"]:
    w = features[features.print_quarter.between(start, "2026Q2")]
    print("Realised window", start, "n", len(w),
          "guide met", int(w.margin_guide_met.sum()),
          "yoy mean/median/positive",
          w.margin_yoy_pts.mean(), w.margin_yoy_pts.median(),
          int((w.margin_yoy_pts > 0).sum()))

slightly = read(m3 + "M3_slightly_magnitude.csv")
s = slightly[
    (slightly.adverb == "slightly")
    & slightly.realised_yoy_pp.notna()
]
print("Stored slightly:", len(s), s.realised_yoy_pp.abs().mean())
s = s[s.quarter != "2025Q4"]
print("Margin-only slightly:", len(s), s.realised_yoy_pp.abs().mean())

bt = read(m3 + "M3_q4_implied_backtest.csv")
bt = bt[bt.rev4_source == "guide_mid"].copy()
bt["recomputed_q4"] = 100 * (
    bt.fy_sentence_level_pct / 100 * (bt.ytd_rev + bt.rev4)
    - bt.ytd_ebitda
) / bt.rev4
print("Historical identity maximum error:",
      (bt.recomputed_q4 - bt.q4_margin_implied_pct).abs().max())
print("Q4 actual minus November-implied:",
      len(bt), (bt.q4_margin_actual_pct - bt.recomputed_q4).mean())
print("Pre-November Street:", bt[
    ["quarter", "street_q4_margin_pct", "seasonal_naive_q4_margin_pct"]
].to_dict("records"))
direction = bt.quarter.map({
    "2023Q4": 1, "2024Q4": -1, "2025Q4": -1
})
matches = (
    (bt.street_q4_margin_pct - bt.seasonal_naive_q4_margin_pct)
    * direction > 0
)
print("Street direction matches:", int(matches.sum()), "/", len(bt))
actuals = pd.Series(
    [bt.iloc[0].seasonal_naive_q4_margin_pct]
    + bt.q4_margin_actual_pct.tolist()
)
print("2022-25 Q4 mean/sample SD:", actuals.mean(), actuals.std())

cons = read(
    "data/processed/margin_build/03_consensus_pit/"
    "03_current_consensus.csv"
)
row = cons[(cons.period == "4Q26") & (cons.vendor == "LSEG")].iloc[0]
print("Current LSEG fields:", row[[
    "as_of_row_date", "ebitda_obs_date", "revenue_obs_date",
    "ebitda_mean", "revenue_mean", "ebitda_n", "revenue_n",
    "implied_margin_pct", "lseg_margin_mean_pct"
]].to_dict())
print("Ratio margin:", 100 * row.ebitda_mean / row.revenue_mean)
print("EBITDA dispersion / fixed revenue:",
      100 * row.ebitda_sd / row.revenue_mean)

bridge = read("data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv")
r3 = bridge.loc[bridge.quarter == "3Q26", "revenue_musd"].iloc[0]
r4 = bridge.loc[bridge.quarter == "4Q26", "revenue_musd"].iloc[0]
print("Live identity multipliers:", (6286 + r3 + r4) / r4, -r3 / r4)
print("FY36/Q4 28.3 requires Q3 margin:",
      100 * (0.36 * (6286 + r3 + r4) - 1780 - 0.283 * r4) / r3)
print("Bridge implied Q4 guide:", r4 / 1.0388)

f4 = json.loads(
    (d4 / "forecasts/2026-09-17-forecast.json").read_text(encoding="utf-8")
)
f9 = json.loads(
    (d9 / "forecasts/2026-09-17-forecast.json").read_text(encoding="utf-8")
)
print("Final sums:",
      sum(f4["final"]["vector"].values()),
      sum(f9["final"]["vector"].values()))
c4, c9, p = f4["conditionals"], f9["conditionals"], 0.80
print("C04 b implied by published conditionals:",
      p * c4["p_b_given_q4_guide_below_street"]
      + (1-p) * c4["p_b_given_q4_guide_not_below"])
print("C09 implied by published conditionals:", {
    k: p * c9["given_q4_guide_below_street"][k]
       + (1-p) * c9["given_q4_guide_not_below"][k]
    for k in "abcd"
})

joint = json.loads(
    (d4 / "datasets/mc_joint_and_conditionals.json").read_text(
        encoding="utf-8")
)["joint_C04xC09"]
v4 = dict(zip("abcde", f4["final"]["vector"].values()))
print("Raw joint reweighted to final C04:", {
    b: sum(
        v4[a] * joint[a+b] / sum(joint[a+c] for c in "abcd")
        for a in "abcde"
    )
    for b in "abcd"
})

source = json.loads(
    (d4 / "sources/polymarket_search_airbnb.json").read_text(
        encoding="utf-8")
)
print("Polymarket pagination:", source["pagination"])
kalshi = json.loads(
    (d4 / "sources/kalshi_KXABNB_markets.json").read_text(
        encoding="utf-8")
)
for market in kalshi["markets"]:
    if market["ticker"].endswith(("148000000", "146000000")):
        print("Kalshi saved liquidity:", {
            k: market.get(k)
            for k in ["ticker", "volume", "volume_fp",
                      "yes_bid_dollars", "yes_ask_dollars"]
        })

old = [.26, .42, .05, .24, .03]
for new in [[.26, .40, .06, .24, .04],
            [.26, .40, .05, .24, .05]]:
    print("Expected log cost, nats:",
          sum(a * math.log(a/b) for a, b in zip(old, new)))

print("Independent C04 affordability blend:",
      .25 * .75 + .75 * (
          1 - NormalDist(35.72661108582304, .6).cdf(36.1)
      ))
distribution = NormalDist((28.3 + row.implied_margin_pct) / 2, 1.8)
print("Independent C09 before rounding:", [
    .95 * distribution.cdf(27.7),
    .95 * (distribution.cdf(28.9) - distribution.cdf(27.7)),
    .95 * (1 - distribution.cdf(28.9)),
    .05,
])
print("No files written.")
```