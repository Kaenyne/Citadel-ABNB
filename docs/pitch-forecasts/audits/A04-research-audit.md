**C05 — submitted vector: (a 8%, b 12%, c 7%, d 73%).**  
Defensible as written: plausible direction, insufficient support for the precise vector.  
First fix: recode the disclosure matrix before using its return-after-gap rate.  
Next fix: repair the bundle bridge and distinguish bundle attribution from RNPL alone.  
Disposition: retain “not quantified” as modal; revise the supporting analysis.

**C06 — submitted vector: (a 15%, b 24%, c 31%, d 30%).**  
Defensible as written: the simulation reproduces, but its restrictive assumptions do not follow from disclosure.  
First fix: remove or independently substantiate the Q3 seasonal share penalty.  
Next fix: treat the starting share, expansion size and wording probabilities as judgmental inputs.  
Disposition: increase uncertainty around the ≥25% outcome; retain an explicit non-disclosure branch.

**C07 — submitted probability: 20%, interval 12–32%.**  
Defensible as written: not until its resolution conventions match the registered question.  
First fix: count qualifying quantified negative lap effects and explicit declines in net benefit.  
Next fix: rebuild the decomposition across all qualifying metrics, including Q4 effects.  
Disposition: revise the event definition before recalibrating the probability.

## Scope and verification

Audit date: **2026-09-17**. No files were written. The `py -3.13` launcher was inaccessible; the repo’s `python` interpreter successfully ran the reproduction below.

Paths in the findings table are relative to `docs/pitch-forecasts/questions/`; **C05**, **C06** and **C07** denote their respective question folders. References to log lines use the revision-1 files reviewed.

All **57 locally sourced quotes in the 60-row RNPL ledger** matched their source files after normalization. The remaining three ledger rows depend on earlier external retrievals. Live SEC retrieval succeeded for the [3Q25 10-Q](https://www.sec.gov/Archives/edgar/data/1559720/000155972025000030/abnb-20250930.htm) and [1Q26 10-Q](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000014/abnb-20260331.htm), corroborating the reported progression from no named RNPL disclosure to deferred-payment timing discussion. Current market quotes and the claimed absence of September RNPL news were not independently refreshed.

The headline MC vectors sum to **1.00**. C07 does not trigger the extreme-probability gate. The related saved forecasts satisfy **R03 = 0.07 ≤ min(C06a = 0.15, R01 = 0.42)**. These are C questions, so R/B impact tables and EV calculations are not required.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A04-01 | C07 | critical | C07 `research-log.md:29–30,96,118`; JSON `conventions` | The log treats a quantified lap as optional “resolver risk.” The registry already counts a quantified negative effect on a listed metric, and separately counts an explicit decline in net benefit. Neither requires unexpectedly high cancellations or a net-negative product. | Compared the registry with C07’s conventions and its “if a quantified lap counts” sensitivity. C05:30 explicitly recognizes a statement attributing a two-point reduction in current-quarter growth to the RNPL comparison. | Use a literal classification table: qualitative tough comparison alone = No; qualifying quantified RNPL effect on Q3/Q4 metric = Yes; explicit net-benefit decline = Yes even if still positive. Do not automatically promote old direction-only timing sentences to Yes. Reforecast after this repair. |
| A04-02 | C05, C06 | major | `datasets/metric_persistence_matrix_4Q20-2Q26.csv`; C05:40; C06:39 | The matrix confuses numeric disclosure with topical mentions and changes the measured object within rows. | The 1Q25 call’s cancellation-rate mention is an analyst question; 3Q25 discusses cancellations without a rate. Both are marked disclosed. The 2Q26 conflict discussion is qualitative but is marked as a points disclosure. “Guest Favorites share” mixes listing counts, cumulative nights and bookings share; 1Q24’s >100m cumulative nights is omitted while adjacent cumulative disclosures count. | Recode from management quotations with metric, denominator, period and venue fields. Removing only the three explicit cancellation/conflict false positives changes continuation to **88/109 = 80.73%**, gap return to **4/19 = 21.05%**. This is a partial repair, not a certified replacement. |
| A04-03 | C05, C06 | major | C05:40,104; C06:39,95; shared matrix/gap datasets | The pooled rate lacks window robustness and overstates the size and independence of its evidence. There are **16**, not 17, metrics. The five “stopped flattering” series are a retrospectively selected group. | Original matrix: all-period continuation **91/111 = 81.98%**, W1 **58/76 = 76.32%**, W2 **38/54 = 70.37%**. Gap returns: **5/19**, **5/17**, **5/16**. Windows use the outcome quarter. Multiple observations concern the same metric and print. | Publish both windows and metric-level counts; do not treat metric-quarters as independent management decisions. The 0/5 versus 5/14 split reproduces but needs a classification defined without using subsequent disclosure outcomes. |
| A04-04 | C05, C07 | major | C05:41,104; C07:39,102 | Historical denominators are not equivalent to trials of the current question. C05’s 2/23 includes quarters before RNPL existed. C07’s 0/4 retrospectively applies a baseline established at the last of those prints. | RNPL matrix: bundle points in **2/4** post-launch prints; continuation **1/2**; completed return-after-gap trials **n=0**. C07 labels reproduce **0/4**, generous **3/4**, Laplace **1/6**. There are no completed post-2Q26 trials of escalation beyond that baseline. | Keep these as descriptive analogues with explicit limitations. Do not present 0/4 as four independent failures to escalate beyond an already established 2Q26 baseline. C06’s directly comparable share-continuation history is only **1/1**. |
| A04-05 | C05 | major | C05:45–46; `datasets/bundle_3q26_mechanical_contribution.csv` | The bridge combines incompatible endpoints of two complementary ex-NA legs. | The source split is 40–50% of a **1.75-point** ex-NA bundle: fee/cancellation **0.70–0.88**, RNPL **1.05–0.87**. They sum to 1.75 at either endpoint, rather than independently ranging from 1.57 to 1.93. | Preserving the other inputs, gross contribution becomes **2.81–3.06**, and after the stated cancellation deductions **1.88–2.91**, versus reported **2.63–3.24** and **1.70–3.09**. These remain conditional scenario calculations. |
| A04-06 | C05 | major | C05:46,97,104; source `D1_bundle_crosscheck.csv` | The total-bundle bridge is used to support an RNPL-alone attribution. Its baseline is also a fitted allocation of management’s already-net contribution, not a measured gross uplift. | The source cross-check labels 1Q26 agreement “fitted…by construction”; D032 concerns three features. C05:97 invokes the total 2.3–2.5-point bridge when discussing RNPL alone. D033 explicitly describes net-of-cancellation benefits. | Build separate bundle and RNPL-only branches. Explain which cancellation effect is incremental to the fitted baseline before subtracting it. Replace “could truthfully state” with “scenario-implied under these assumptions.” |
| A04-07 | C06 | major | C06:41–42,87,117; share-model `seas` | The assertion that Q3 is the lowest-GBV quarter is false, and high take rate does not establish the shortest booking lead time or a −2 to 0-point RNPL-share penalty. | `data/processed/abnb_driver_history_quarterly.csv`, 2023–25 means: Q3 GBV **$20.433bn**, Q4 **$17.833bn**; Q4 is lower in each year. Q3 take rate **18.337%** reproduces, but mixes current bookings with peak-season recognized revenue. The cited mechanics note also says lead time is undisclosed. | Remove the penalty absent independent evidence. The supplied simulation with no seasonal penalty gives true rounded-share probabilities **40.0555/59.9445/0%**; applying its disclosure/wording model gives **25.23/18.88/25.88/30%**. |
| A04-08 | C06 | major | C06:36–37,42; share-model `s2`, `ramp`, `exp_` | “Over 20%” supplies no 23% upper bound. Roughly 70% adoption does not establish saturation, particularly across different denominators and geographies. These assumptions manufacture a narrow share distribution. | D005 measures people offered RNPL in the US; D022 uses eligible-booking adoption with a GBV basis. D043 provides only the lower-bound wording. D044 gives no size for July’s eligibility expansion. | Label **U(21,23)**, **U(0,2)** and the exponential expansion distribution as assumptions. Test broader starting-share support and joint expansion/adoption scenarios. Preserve the reproduced large-expansion sensitivity: **P(true rounded share ≥25) = 55.2555%**. |
| A04-09 | C06 | major | C06:38 | A conditional backlog-stock solve is used as evidence against a higher quarterly booking-flow share. It does not identify that flow share. | `data/processed/rnpl_short_audit/verify_bs_uf_only_solve.csv`, named baseline, 2Q26: unpaid backlog **15.377% at B=1.00**, **23.070% at B=1.10**. The source audit explicitly leaves unpaid share and book length inseparable. | Retain the balance-sheet consistency check, but remove its role as an upper constraint on Q3 flow share. Model the stock-to-flow bridge before using it quantitatively. |
| A04-10 | C05, C07 | major | C05:105; C07:103–104 | The logs blend the team nowcast with Kalshi without a reproducible mixing rule, although brief rule 6 requires print-dependent questions to use the team band and its error distribution. C05’s Kalshi claim is marked non-load-bearing despite entering the calculation. | Normal approximation with mean **9.5**, SD **1.48** gives states ≥10 / 9–10 / <9 of **36.774/26.451/36.774%**, not **42/30/28%**. With C05’s existing conditional probabilities, quantification is **28.37%**, versus **26.46%** under its supplied states. | Use the specified nowcast distribution for the headline. Keep Kalshi as a separately reported sensitivity; document any authorized blend, threshold interpolation and distributional assumptions. |
| A04-11 | all | major | C05:49–50; C06:44; C07:48–49; Kalshi JSON and derived CSV | Volume/open interest are reported as null because obsolete field names were read. The snapshots also contain freshness indicators omitted from the logs. | At the 146m strike, `volume_fp=998.66`, `open_interest_fp=689.51`; ladder totals **3,237.21** and **2,178.46**. All seven `volume_24h_fp` values are zero; `updated_time` is **2026-08-04T18:47:36.451419Z**. | Parse fixed-point fields and save them in the CSV. Distinguish retrieval time from quote freshness; the metadata alone does not prove when each quote last changed. The saved annual market is **FY2026**, not a Q4-only market. |
| A04-12 | C07 | major | C07:42–44,93,103 | The model centers an unexpectedly bad Q3 cancellation quarter, while the contract also includes declining net benefit, Q4 effects and cash/revenue/take-rate disclosures. Its quoted cancellation “bounds” are a central scenario slice. | The source note’s broader grid reaches **−1.37 points** in Q3. `rnpl_nights_module.csv` has Q3 propensity effects **−1.425 / −0.568 / −0.158** across bear/base/bull. Management’s positive Q3 unearned-fee timing prediction does not eliminate other metrics or Q4. | Build mutually exclusive scenarios covering the full contract. Keep the central −0.15 to −0.93 range as a labeled scenario slice, not an empirical bound or likelihood estimate. |
| A04-13 | all | major | Each log §5; C05:39,95; C06:95–100 | Three independent estimates were not obtained. C06’s “base rate” and decomposition share the same simulated share and wording model. C05’s deliberate-reframing explanation is an inference presented as fact. | Null anchors appear in all JSONs. C06 explicitly multiplies the same conditional split by two disclosure probabilities. C05’s raw facts reproduce—Q1/Q2 nights **9.154/10.342%**, Q2 day-one return **17.4%**—but do not establish why management omitted the figure. | Keep `NO_EXTERNAL_ANCHOR`; explicitly state that the three-estimate requirement remains unmet. Label shared models and management-intent assumptions. Do not force a market number or treat close internal estimates as corroboration. |
| A04-14 | C07 | minor | C07:103,119; JSON sensitivities | Two displayed calculations do not follow their stated inputs. | **0.28 × 0.6 = 0.168**, not 0.20; this gives **0.1924** under the stated conditional Yes probabilities. At strong-print **P(S)=0.05**, the same model gives **0.1275**, not 0.11. | Correct the arithmetic or explicitly identify the additional judgmental adjustment. This alone does not invalidate a rounded 20% headline. |
| A04-15 | C06 | minor | C06:100 | The stated approximately 3:1 ensemble weighting does not produce the final vector. | Three parts decomposition plus one part base rate gives **(0.145, 0.250, 0.335, 0.270)**. The final is **(0.15, 0.24, 0.31, 0.30)**. | State that the final essentially adopts the decomposition with a small discretionary transfer, or publish the actual weights and subsequent adjustments. |
| A04-16 | C05, C06 | minor | JSON `sensitivity`; C05:127; C06:119 | Some sensitivity vectors are not normalized. | C05’s rounding sensitivity, retaining unspecified c/d, totals **1.03**. C06’s strong-print sensitivity totals **1.01**. | Supply complete vectors with explicit transfers. Under C06’s own conditional split and 80% disclosure, the unrounded result is approximately **15.56/27.67/36.77/20%**. |
| A04-17 | C05 | minor | C05:119 | The stated log-score cost is incorrect and confuses realized with expected score. | If d resolves, moving its probability from .73 to .70 changes log score by **ln(.70/.73) = −0.041964**, not approximately −0.01. | Correct the conditional score change. An expected score comparison needs probabilities over all outcomes. |
| A04-18 | all | minor | Claims on September news/appearances; query logs; `sources/` | The source folders do not substantiate the exhaustive absence claims. No saved search responses, full 4,000-event enumeration or conference-page snapshot accompanies them. | Inventoried all three folders. They contain selected market responses and RNPL excerpts, but not those materials. The quoted final “this week” query is not evidence of an applied 72-hour filter. | Say “no relevant result found in the searches recorded,” not “no market/comment/change exists.” Save result timestamps, search constraints and snapshots; distinguish old historical evidence from claims about the current absence of news. |

## What the logs do well and should keep

**C05.** The core disclosure sequence is sourced correctly: D014 gives >200bp nights/~300bp GBV for 4Q25; D032 gives approximately 3/4 points for 1Q26; 2Q26 substitutes GBV-share wording. Keep the distinction between growth contribution and share, the explicit lower-bound mapping, and the possibility of call-only disclosure. The direct sizing refusal is present in `abnb_declined_to_quantify.csv`; the **37 total / four in 2Q26** counts reproduce.

**C06.** The forecast addresses disclosed wording rather than only latent share, respects the GBV denominator and quarter-specific gate, and includes non-disclosure. The base, large-expansion and no-season Monte Carlo results reproduce. Keep the separation between latent share, disclosure probability and wording—but label their assumptions individually.

**C07.** The 2Q26 10-Q baseline is correctly extracted. Keep the distinction between an aggregate cancellation-rate observation and a qualifying effect on a listed metric. The module’s base Q3 nights growth **9.49%**, propensity effect **−0.568 points**, and earlier-cohort share **45.75%** reproduce from the saved CSVs. Keep the failed calendar-reopening test as evidence against a simple cancellation narrative, without treating failure to detect a signature as proof of no effect.

## Independent audit numbers

These are audit judgments, not externally anchored probabilities or blinded second forecasts.

**C05: (a 0.10, b 0.14, c 0.08, d 0.68).**  
Use team-normal print states **(.3677, .2645, .3677)** and judgmental quantification probabilities **(.20, .30, .45)**, giving **P(quantification)=.3184**.  
Allocate quantified outcomes **31/44/25%** across a/b/c; this preserves the disclosure gate while allowing both renewed positive attribution and qualifying negative attribution.

**C06: (a 0.25, b 0.19, c 0.26, d 0.30).**  
Use the reproducible no-season benchmark: latent rounded-share probabilities **(.400555, .599445, 0)**, with the existing **70%** disclosure gate and wording mapping.  
This yields **(.25235, .18883, .25883, .30)**; it is a transparent sensitivity-based reassessment, not independent validation of the remaining share-model assumptions. The low-share tail still requires better modeling.

**C07: P(Yes) = 0.25; judgmental 80% interval 0.10–0.45.**  
Partition outcomes into unexpectedly adverse RNPL performance **15%**, ordinary performance with a lap/declining-benefit explanation **25%**, and routine performance/disclosure **60%**.  
Assign qualifying-disclosure probabilities **70/40/7.5%**, respectively: **.15×.70 + .25×.40 + .60×.075 = .25**; the middle branch explicitly restores qualifying effects that need no cancellation surprise.

## Reproduction script

The script is read-only, uses stdlib plus pandas, and was run successfully. Partial matrix repairs are deliberately labeled; they do not certify unreviewed cells.

```python
"""A04 read-only reproduction.
Run from repo root: python docs/pitch-forecasts/audits/A04-reproduce.py
Requires stdlib + pandas. No network or file writes.
"""
from pathlib import Path
import gzip
import html
import json
import math
import random
import re
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
SLUGS = [
    "bundle-attribution-quantified",
    "rnpl-gbv-share-disclosed",
    "rnpl-negative-effect-acknowledged",
]
A, B, C = [Q / s for s in SLUGS]


def plain(path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    s = raw.decode("utf-8", errors="replace")
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", s, flags=re.I | re.S)
    return re.sub(
        r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))
    )


def folded(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def rate_table(matrix):
    rows = []
    quarters = list(matrix.columns)
    windows = [
        ("All", 0),
        ("W1 target>=1Q23", quarters.index("1Q23")),
        ("W2 target>=1Q24", quarters.index("1Q24")),
    ]
    for label, start in windows:
        k = n = g = h = 0
        for values in matrix.ne("--").to_numpy().tolist():
            for t in range(max(1, start), len(values)):
                if values[t - 1]:
                    n += 1
                    k += int(values[t])
            for t in range(max(2, start), len(values)):
                if values[t - 2] and not values[t - 1]:
                    h += 1
                    g += int(values[t])
        rows.append([
            label, k, n, k / n if n else None,
            g, h, g / h if h else None,
        ])
    return pd.DataFrame(rows, columns=[
        "window", "continued", "eligible", "continuation",
        "returned", "gaps", "return_rate",
    ])


matrix = pd.read_csv(
    A / "datasets/metric_persistence_matrix_4Q20-2Q26.csv"
).set_index("metric")
print("MATRIX SHAPE", matrix.shape)
print(rate_table(matrix).to_string(index=False))

gaps = pd.read_csv(A / "datasets/metric_gap_events.csv")
returned = gaps.returned_next_quarter.astype(str).str.lower().eq("true")
print("SAVED GAP LEDGER", int(returned.sum()), "/", len(gaps))
unflattering = [
    "cross-border share %",
    "long-term stays share %",
    "urban/high-density share %",
    "active listings growth %",
    "1BR vs hotel price comparison",
]
mask = gaps.metric.isin(unflattering)
print("POST-HOC FIVE-METRIC GROUP",
      int(returned[mask].sum()), "/", int(mask.sum()))
print("OTHER GAP EVENTS",
      int(returned[~mask].sum()), "/", int((~mask).sum()))

# Partial audit repairs; all other cells remain uncertified.
partial = matrix.copy()
partial.loc["cancellation rate %", ["1Q25", "3Q25"]] = "--"
partial.loc["Middle East conflict (pts)", "2Q26"] = "--"
print("THREE VERIFIED CELL REMOVALS")
print(rate_table(partial).to_string(index=False))

print("EXCLUDE THREE MIXED/INCORRECT SERIES; SENSITIVITY ONLY")
print(rate_table(matrix.drop(index=[
    "Guest Favorites share",
    "cancellation rate %",
    "Middle East conflict (pts)",
])).to_string(index=False))

rnpl = matrix.loc[
    ["RNPL/bundle contribution (pts)", "RNPL GBV share"],
    ["3Q25", "4Q25", "1Q26", "2Q26"],
]
print("FOUR POST-LAUNCH PRINTS\n", rnpl.to_string())
for name in rnpl.index:
    print(name, "disclosed", int(rnpl.loc[name].ne("--").sum()), "/4")
print("BUNDLE RETURN-AFTER-GAP: completed n=0")
print("GBV SHARE CONTINUATION: 1/1, 1Q26 -> 2Q26")

ledger = pd.read_csv(
    ROOT / "data/processed/overnight2/D/rnpl_statement_ledger.csv"
)
cache, failed = {}, []
checked = 0
for _, row in ledger[ledger.source_file.notna()].iterrows():
    path = ROOT / row.source_file
    if path not in cache:
        cache[path] = folded(plain(path))
    checked += 1
    if folded(str(row.quote)) not in cache[path]:
        failed.append(row.statement_id)
print("RNPL LEDGER", len(ledger), "rows;",
      checked, "local quote checks; failed", failed)
print("BUNDLE NUMERIC DISCLOSURES\n",
      ledger[ledger.statement_id.isin(["D014", "D032"])][
          ["statement_id", "date", "period_referenced", "quantity"]
      ].to_string(index=False))

guide = pd.read_csv(
    ROOT / "data/processed/overnight/02_guidance_ledger.csv"
)
rnpl_rows = guide.fillna("").astype(str).apply(
    lambda s: s.str.contains(
        r"RNPL|Reserve Now|Pay Later", case=False
    ).any(),
    axis=1,
)
print("GUIDANCE LEDGER", guide.shape,
      "RNPL ROWS", int(rnpl_rows.sum()))

declines = pd.read_csv(
    ROOT / "data/processed/abnb_declined_to_quantify.csv"
)
print("DECLINES", len(declines), "2Q26",
      int(declines.quarter.eq("2026Q2").sum()))
print(declines[
    declines.asked.str.contains("Reserve Now", case=False, na=False)
].to_string(index=False))

# Reproduces author labels, not an endorsement of the resolution rule.
prior = pd.read_csv(
    C / "datasets/prior_prints_scored_under_c07_criteria.csv"
)
strict, generous, events = set(), set(), set()
for _, row in prior.iterrows():
    qs = set(re.findall(r"[1-4]Q\d{2}", str(row["print"])))
    events |= qs
    if str(row.strict_reading).startswith("Yes"):
        strict |= qs
    if str(row.generous_reading).startswith("Yes"):
        generous |= qs
print("C07 AUTHOR LABELS", len(strict), "/", len(events),
      "generous", len(generous), "/", len(events),
      "Laplace", (len(strict) + 1) / (len(events) + 2))

kpi = pd.read_csv(
    ROOT / "data/processed/abnb_driver_history_quarterly.csv"
)
print("CURRENT KPI VALUES\n",
      kpi[kpi.quarter.isin(["3Q25", "1Q26", "2Q26"])][
          ["quarter", "nights_m", "nights_m_yoy_pct"]
      ].to_string(index=False))
print("2023-25 GBV/TAKE-RATE MEANS\n",
      kpi[kpi.year.between(2023, 2025)].groupby("q")[
          ["gbv_b", "take_rate_calc_pct"]
      ].mean().to_string())

reaction = pd.read_csv(
    ROOT / "data/processed/abnb_guidance_reaction_panel.csv"
)
print("2Q26 REACTION\n",
      reaction[reaction.quarter.eq("2Q26")][
          ["print_date", "ret_1d", "exc_1d"]
      ].to_string(index=False))
reaction2 = pd.read_csv(
    ROOT / "data/processed/abnb_earnings_reactions.csv"
)
print(reaction2[reaction2.quarter.eq("2026Q2")][
    ["reaction_date", "abnb_1d_pct", "excess_1d_pct"]
].to_string(index=False))


def share_sim(exp_mean=1.4, season=True, n=200000):
    rng = random.Random(7)
    counts = [0, 0, 0]
    for _ in range(n):
        s = rng.uniform(21, 23) + rng.uniform(0, 2)
        s += min(6, rng.expovariate(1 / exp_mean))
        # Draw even when disabled, preserving RNG alignment.
        seasonal = rng.uniform(-2, 0)
        s += seasonal if season else 0
        counts[0 if s >= 24.5 else 1 if s >= 20.5 else 2] += 1
    return [x / n for x in counts]


def wording(probs, disclose=0.70):
    high, middle, low = probs
    return [
        disclose * 0.9 * high,
        disclose * 0.45 * middle,
        disclose * (0.1 * high + 0.55 * middle + low),
        1 - disclose,
    ]


for name, mean, seasonal in [
    ("base", 1.4, True),
    ("large", 4, True),
    ("no season", 1.4, False),
]:
    probs = share_sim(mean, seasonal)
    print("SHARE SIM", name, probs, "wording", wording(probs))

mechanical = pd.read_csv(
    A / "datasets/bundle_3q26_mechanical_contribution.csv"
)
legs = mechanical[
    mechanical.in_3Q26_yoy_window.fillna("").str.startswith("yes")
]
legs = legs[~legs.component.str.startswith("Cancellation-propensity")]
lo = legs.points_of_total_nights_low.sum()
hi = legs.points_of_total_nights_high.sum()
print("AUTHOR BUNDLE", lo, hi, "net", lo - 0.93, hi - 0.15)
print("PAIRED EX-NA TOTAL", 0.70 + 1.05, 0.88 + 0.87)
print("PAIRED GROSS",
      0.66 + 1.75 + 0.10 + 0.30,
      0.66 + 1.75 + 0.30 + 0.35)
print("PAIRED NET",
      0.66 + 1.75 + 0.10 + 0.30 - 0.93,
      0.66 + 1.75 + 0.30 + 0.35 - 0.15)

cohort = pd.read_csv(
    ROOT / "data/processed/overnight2/D/D1_cohort_matrix_cancellation.csv"
)
prior_q = cohort.booking_quarter.isin(
    ["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
)
print("EARLIER-COHORT Q3 CANCELLATION SHARE",
      cohort.loc[prior_q, "3Q26"].sum() / cohort["3Q26"].sum())

module = pd.read_csv(
    ROOT / "data/processed/rnpl_short_audit/rnpl_nights_module.csv"
)
print("Q3 MODULE\n", module[module.quarter.eq("3Q26")][
    ["scenario", "m4_propensity_drag_pts", "nights_yoy_pct"]
].to_string(index=False))

bs = pd.read_csv(
    ROOT / "data/processed/rnpl_short_audit/verify_bs_uf_only_solve.csv"
)
print("UF STOCK SOLVE\n", bs[
    bs.quarter.eq("2Q26")
    & bs.B.isin([1.0, 1.1])
    & bs.norm.eq("note baseline: next-Q rev, 2023+2024+1H25")
].to_string(index=False))

snap = json.loads((
    A / "sources/kalshi_KXABNB-26NOVNEB_20260917T025351Z.json"
).read_text())
markets = snap["markets"]
for row in sorted(markets, key=lambda x: x["floor_strike"]):
    mid = (
        float(row["yes_bid_dollars"]) + float(row["yes_ask_dollars"])
    ) / 2
    print("KALSHI", row["floor_strike"], mid,
          row["volume_fp"], row["open_interest_fp"],
          row["volume_24h_fp"], row["updated_time"])
print("KALSHI TOTAL VOLUME/OI", *[
    sum(float(row[key]) for row in markets)
    for key in ("volume_fp", "open_interest_fp")
])

tail = 0.5 * math.erfc((10 - 9.5) / (1.48 * math.sqrt(2)))
states = [tail, 1 - 2 * tail, tail]
print("TEAM NORMAL STATES >=10, 9-10, <9", states)
print("C05 AUTHOR DECOMPOSITION",
      0.42 * 0.15 + 0.30 * 0.28 + 0.28 * 0.42)
print("C05 TEAM-ONLY SAME CONDITIONALS",
      sum(x * y for x, y in zip(states, [0.15, 0.28, 0.42])))
print("C07 S FROM STATED INPUTS",
      0.28 * 0.6, "P", 0.10 + 0.55 * (0.28 * 0.6))
print("C07 STRONG-PRINT SENSITIVITY", 0.05 * 0.65 + 0.95 * 0.10)
print("C05 LOG-SCORE CHANGE IF d", math.log(0.70 / 0.73))
print("C06 STATED 3:1 BLEND", [
    (3 * x + y) / 4
    for x, y in zip(
        [0.14, 0.24, 0.32, 0.30],
        [0.16, 0.28, 0.38, 0.18],
    )
])
print("C06 80% DISCLOSURE SENSITIVITY", wording(share_sim(), 0.80))

saved = {}
related = [
    "risk-july-rnpl-expansion-offsets-lap",
    "risk-q3-nights-meets-guide",
]
for slug in SLUGS + related:
    path = Q / slug / "forecasts/2026-09-17-forecast.json"
    if not path.exists():
        continue
    obj = json.loads(path.read_text())
    saved[obj["question_id"]] = obj
    print("FINAL", obj["question_id"], obj["final"])
    if "vector" in obj["final"]:
        base = dict(zip("abcd", obj["final"]["vector"].values()))
        print("FINAL SUM", sum(base.values()))
        for sensitivity in obj["sensitivity"]:
            revised = dict(base)
            revised.update(sensitivity["moves_to"])
            if not math.isclose(sum(revised.values()), 1):
                print("INVALID SENSITIVITY SUM",
                      sensitivity["assumption"], sum(revised.values()))

if all(q in saved for q in ["R03", "R01", "C06"]):
    cap = min(
        saved["R01"]["final"]["p"],
        list(saved["C06"]["final"]["vector"].values())[0],
    )
    print("R03 CAP", saved["R03"]["final"]["p"], "<=", cap)

# Judgmental audit alternatives; not empirical frequencies or market anchors.
quantify = sum(
    x * y for x, y in zip(states, [0.20, 0.30, 0.45])
)
print("AUDIT C05", [
    quantify * 0.31, quantify * 0.44,
    quantify * 0.25, 1 - quantify,
])
print("AUDIT C06 NO-SEASON BENCHMARK", wording(share_sim(1.4, False)))
print("AUDIT C07", 0.15 * 0.70 + 0.25 * 0.40 + 0.60 * 0.075)
```