**S02 — $162 median: plausible, but not defensible as documented.**  
The Monte Carlo and published percentile table reproduce.  
First remove the unauthorized corporate-action resolution rule.  
Then correct the options-distribution description, drift calculations, and tail evidence.  
Independent comparison: median **$163**, P(≤$150) **0.32**, P(≤$143) **0.23**, P(≥$180) **0.29**.

**S03 — $165 median: plausible, but its supporting construction needs revision.**  
The forecast correctly follows the actual February release date.  
First separate pre-release seasonality from the February earnings reaction.  
Then repair the options interpolation and inherited S02 findings.  
Independent comparison: median **$167**, P(≤$150) **0.32**, P(≤$143) **0.25**, P(≥$180) **0.38**.

**S04 — 29%: reproducible, but insufficiently supported as written.**  
First restore the question’s inclusive threshold: exactly $176.80 resolves **Yes**.  
Correct the down-print reference class and quantify the target model’s residual uncertainty.  
The 50% “anchor” is an interpretation of another repo judgment, not independent consensus.  
Independent comparison: **33%**, with a judgmental uncertainty interval of **20–45%**.

## Scope and verification

Audit date: **2026-09-17**. Reviewed the three revision-1 logs, forecast JSONs, calculation scripts, saved distributions, source snapshots, and cited processed data. No files were changed; neither prohibited raw-data directory was opened.

The 400,000-draw Monte Carlo reproduced **exactly**, including S04’s **0.2953025**. Both final CDFs are monotone, and their reported percentiles and threshold probabilities reproduce to rounding. The four print weights sum to one. No R/B impact table is required for these questions.

The saved 513-contract option chain independently reproduces the quoted ATM IVs and smile calculations. The [24/7 Wall St. September 16 article](https://247wallst.com/investing/2026/09/16/here-are-wednesdays-top-wall-street-analyst-research-calls-airbnb-booking-holdings-credicorp-dutch-bros-expedia-hartford-financial-services-group-meritage-homes-patchex-yum-brands/) was accessible and corroborates Morgan Stanley’s Equal Weight/$170 action. The Cerbat Gem fetch failed; that source was audited from the saved summary, which is explicitly not archived HTML.

`py -3.13` was unavailable. Repo `python` worked, although its advertised `statsmodels` package was absent. Regressions were independently reconstructed with linear algebra; the reproduction script below requires only Python’s standard library and pandas.

References below use:

- **S02**, **S03**, **S04** for their respective question folders under `docs/pitch-forecasts/questions/`.
- **D**, **C** for `data/processed/reverse_dcf/D/` and `C/`.
- **path model** for `S02/datasets/abnb_path_mixture.py`.
- **blend** for `S02/datasets/final_blend.py`.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A07-01 | S04 | critical | `research-log.md:27`, convention 5 | “Ties resolve No” reverses the registry’s **≤$176.80** rule. A discrete analyst-target mean is not generally continuous or incapable of equality. | Compared `QUESTIONS.md:162` with the convention. The simulation itself correctly uses `<=`. | Delete the exception. Exactly **$176.80 resolves Yes**; preserve the inclusive comparison in resolution code. |
| A07-02 | S02 | critical | `research-log.md:27`, convention 6 | Corporate actions are assigned a new resolution object: “last comparable close.” The question asks for the December 15 close and authorizes no such substitution. The claimed 0.5% corporate-action probability also has no explicit component in the distribution. | Compared the registry with the convention and inspected every path-model component. | Remove the fallback. Separate unresolved corporate-action treatment from the ordinary price forecast; do not assert that the registry authorizes a last-comparable-price resolution. |
| A07-03 | S02, S03 | major | S02 `research-log.md:90–94`; S03 `:58–62`; blend `:21–29` | The final distributions are described as blends with a shifted **smile RND**, but the code substitutes a **lognormal centered on the smile median**. The cited anchor threshold probabilities therefore do not describe the actual blended anchor. | Actual shifted-lognormal anchor probabilities, ordered ≤143 / ≤150 / ≥180: **S02 0.1870 / 0.2641 / 0.3615; S03 0.2400 / 0.3059 / 0.4012**. Rebuilding the genuine shifted-smile blend gives S02 P(<100) **0.00803**, versus published **0.00317**; S03 **0.02012**, versus **0.01545**. | Either label and justify the lognormal approximation throughout, or rebuild from a valid smile distribution. Recompute final-minus-anchor using the anchor actually used. Similar quartiles do not establish similar tails. |
| A07-04 | S02, S03 | major | `S02/datasets/implied_dist.py:77–81` | The fitted smile produces negative risk-neutral density; clipping it to zero and renormalizing conceals violations of call-price convexity. This is not an unqualified market-implied probability distribution. | Independent Black-76 reconstruction from saved quotes reproduces integrated negative density of **1.5382% for December** and **0.4750% for February** before clipping. | Fit a convex call-price curve or another constrained surface. Report removed negative mass, extrapolation, and truncation explicitly. Until repaired, treat the RND as a model-dependent approximation; the measured ATM IVs remain usable. |
| A07-05 | S02, S03 | major | S02 `research-log.md:37,82,90`; `analysis/src/overnight/09_stock_behaviour.py:241–250` | The −3.75% “post-print drift” is a difference of cumulative returns normalized to the **close 21 sessions before the reaction**, not the return earned from the reaction close. It is then used as a multiplicative post-print return. | Rebuilt from `data/processed/overnight/09_prices_daily.csv`. Legacy all-print mean: **−3.7500%, n=23**; correctly rebased reaction-close-to-+20 excess: **−3.1201%**. W1: **−0.8592%, n=14**; W2: **−1.9177%, n=10**. At +27, W1 is **+0.9748%, n=13**, W2 **−1.2502%, n=9**. | Rebase each asset at the reaction close, match the forecast horizon, and report both windows. Treat persistent negative drift as an uncertain assumption, not a demonstrated both-window effect. |
| A07-06 | S02, S03 | major | S02 `research-log.md:37`, accelerating-print drift | The stated **−4.7%** accelerating-print drift subtracts a five-print day-1 mean from a four-print day-20 mean. The missing observation is the large positive 2Q26 reaction. | `overnight/05_reaction_by_accel.csv` reports day-1 **n=5**, day-20 **n=4**. Pairing the four observations in `abnb_earnings_reactions.csv` gives **−2.125%**, not −4.7%. The updated C panel has all five and gives **−0.6130%** under its cumulative-excess-difference convention. | Use identical observations and a stated return convention. Reconsider the accelerating branch’s −2% drift, whose claimed “half-strength” basis changes materially. |
| A07-07 | S04 | major | `research-log.md:35,92` | The examples contaminate the ≤−5% print class with **2Q22, −1.13%**, and the monitoring rule changes “any net cut” into “cut ≥3.8%.” | Recomputed from `D_print_revisions.csv`. The qualifying six are 3Q22, 1Q23, 1Q24, 2Q24, 3Q24, 2Q25. Their target changes at +20 are **−7.6198, −6.4484, +1.6556, −14.0677, +3.5055, −0.0238%**. Any net cut: **4/6**; cut ≥3.8%: **3/6**. | Remove 2Q22 from the gated examples; include 1Q24. Correct the monitoring rationale to **3/6**, and distinguish effectively unchanged 2Q25 from a material target cut. |
| A07-08 | S04 | major | `research-log.md:36,40,79`; path model `:31–33,67–68` | The 3.5% three-month residual SD is not established by the fitted model. The log reports a **6.68%** print-window regression residual and a **3.4–3.8% one-month total-change SD**, then chooses 3.5% for a different three-month hybrid without residual validation. | Independently refitted the 22-window regression: intercept **−0.08485**, price coefficient **0.09676**, day-1 coefficient **0.40481**, residual SD **6.67679 percentage points**. W1/W2 residual SDs: **5.9224 / 6.8642**, n=13/9. Merely increasing the existing simulation’s log-noise SD to 6.68% moves P from **0.2953 to 0.3495**. | Estimate residuals for the exact hybrid equation and horizon, ideally walk-forward. Until then, show the wider-noise sensitivity prominently and label 3.5% as judgment. The sensitivity is not proof that simple-return and log-return residuals are interchangeable. |
| A07-09 | S04 | major | `research-log.md:61–64`; JSON `estimates.anchor` | A repo sentence saying “base case” is converted into **50%**, creating an apparent external anchor and a **21-point** disagreement. The original note supplies neither that probability nor an independent forecast method. | Read `research/notes/reverse_dcf/D_sell-side-dispersion.md:147`; it gives a qualitative 3–4% target-cut judgment. Both it and S04 use the same tape-lag history. | Label this a **non-independent repo prior**; do not present the 21-point gap as disagreement with market consensus. State that no direct probability anchor was verified. The timestamped $182.975 target mean is a level, not P(target ≤176.8). |
| A07-10 | S02, S03; inherited by S04 | major | S02 `research-log.md:42,79,94`; JSON `named_asymmetry` | The principal claimed informational advantage cites the old reviews-index RMSE **1.48 versus 2.16** without the September 14 revintaging failure. | `data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv`: original **1.475147 / 2.159143 = 0.683209**; literal substitution **1.815866 / 2.159143 = 0.841012**; 103-market variant **1.633596 / 2.159143 = 0.756595**; each scores n=10. The later WPK note explicitly withdraws the survivor interpretation. | Keep the user-specified nowcast band as an input, but correct its performance provenance and uncertainty. Do not claim an established forecasting edge using the superseded statistic. |
| A07-11 | S03 | major | `research-log.md:34,53`; `implied_dist.py:69–71` | Interpolating total variance between January and March prices only **44.44% of the February event**, even though S03 resolves after that event. Acknowledging this without repairing it leaves the anchor systematically short of event variance. | Calendar interpolation weight is **28/63=0.444444**. Assuming a 9.5% February event SD, restoring the missing 55.56% increases horizon log SD from **24.0576% to 25.0780%**, equivalent annual IV **37.6535% to 39.2506%**. | Separate background variance and event jumps before interpolation. Report February-event uncertainty as a sensitivity rather than calling 1.44 events “close to” two. |
| A07-12 | S03 | major | `research-log.md:37–38,52`; path model `:30,58–59` | Full January/February seasonality is used to motivate a **pre-February-release** drift, then a positive February earnings reaction is added separately. The calendar-February observation already contains that reaction and post-release sessions. Also, +2% is not a quarter of +14.6%. | Monthly excess means reproduce as **January +6.8610%, February +7.6674%, n=6 each**. Their sum is **14.5284%**; +2% retains **13.77%**, not 25%. The path applies +2% before the release and separately adds a mean February reaction of +2.60%. | Measure the actual December-15-to-pre-release window and separate the earnings day. State shrinkage consistently. Without that work, remove the seasonal increment; this alone lowers the decomposition median **$162.83→$159.64**. |
| A07-13 | S02, S03 | major | S02 `research-log.md:108`; S03 `:76` | Historical crash evidence understates the saved series’ left tail and misidentifies the relevant episode. | From the merged close CSV: worst 63-session return starting in 2023+ is **−29.2848%**, not −18%; all-history 63-session p1 is **−40.8183%**, not approximately −33%. There are **19 overlapping** 63-session windows ≤−40%. For 103 sessions, **11 overlapping windows** fall ≤−40%, with worst **−47.6693%**, starting February 16, 2022. | Replace the incorrect examples and distinguish overlapping windows from independent crash episodes. Reassess tail mass using correct evidence; these observations alone do not mechanically determine today’s tail probability. |
| A07-14 | S02, S03 | major | S02 `research-log.md:44,90`; S03 `:51`; path model `PARAMS` | S03 says its branch medians come from the repricing ladder, but the executable model contains no growth-to-multiple calculation or mapping from ladder prices. Branch drifts are assigned directly. | Inspected the complete model. `E_repricing_ladder.csv` contains team pivot **$167.018** and ex-NA cases **$166.212/$164.394**; no displayed computation transforms these into February branch medians **$181/$168/$166/$153**. | Label the ladder a qualitative cross-check, or show an explicit horizon/adoption mapping. Disclose the model’s judgmental flexibility: three free branch weights, 24 branch settings, and additional diffusion/seasonal/tape settings. |
| A07-15 | S02, S03, S04 | minor | S02 `research-log.md:33`; S03 `:27`; path model `:20,62–64` | Session accounting contains compensating errors. The February horizon is described as one session short, but the prose arithmetic omits the November event day. | Exclusive-start/inclusive-end counts: September 16→November 5 **36**; November 6→December 15 **26**; December 15→February 11 **39**. Model totals are **35+1+27=63** and **35+1+27+39+1=103**, both correct totals. | Use 36 pre-event and 26 post-event diffusion sessions. Correct the prose and recompute S04’s block timing; this is chiefly an allocation error, not a missing day of total variance. |
| A07-16 | S04 | minor | `datasets/target_base_rates.py:14–35`; `research-log.md:36,59` | Daily target windows use a **−3.5% log threshold**, print windows use **−3.5% simple**, and neither is the exact required decline from the assumed $183.21875 base. The print-window alignment also inherits the session mismatch. | Exact MS-adjusted log threshold is **−0.03566164**. Daily hit rates become **346/1,366=25.3294%**, **150/863=17.3812%**, **104/613=16.9657%**. The reported −0.035 cutoff gives 351/1,366, 153/863, 107/613. | Use one exact threshold and date convention; show the unadjusted-feed alternative separately. Disclose overlapping observations. The correction is small but reproducible. |
| A07-17 | S02, S03 | minor | S02 `research-log.md:27,91–94`; path model `:22,45–46`; blend `:27` | Drift and S01 reconciliation are described inconsistently. The decomposition uses 3% as total arithmetic drift; the anchor adds 3% above a forward already carrying 3.97%. Also, setting within-branch event SD to 9% does not reproduce S01’s 9.5% unconditional SD. | The four branch means contribute variance **0.00170475**. Thus unconditional event SD at 9% within branch is **9.902%**; matching 9.5% requires **8.556%** within branch. | Distinguish total expected return from excess return over cash in both components. Use the variance identity to reconcile S01, and describe any retained mismatch as deliberate. |

The current neighboring C01/C02 JSONs are already revision 2; A07 explicitly cites revision 1. Preserve the original-vintage attribution, then refresh those dependencies in the response. Do not silently claim that revision-1 probabilities are current.

## What the logs do well and should keep

**S02.** Keep the unconditional event mixture, separate base-case conditional reaction, archived option quotes, exact simulation seed, exported CDF, and sensitivity runs. The broad historical return calculations reproduce: 63-session all-history **n=1,384**, mean **+1.1479%**, SD **17.1364%**, median **+0.6587%**. The raw earnings reaction RMS is **8.9156%, n=23**. Rejecting the memo’s 12-month $143 target as a December median is justified.

**S03.** Keep the actual-release-date rule and the correction from “six of six February prints positive” to **five of six**. The six saved raw reactions have mean **+7.9333%** and median **+8.95%**. Keep the wider February distribution and the explicit `NOT_INDEPENDENTLY_DERIVED` flag; repair the cancellation-of-effects explanation rather than implying precision from it.

**S04.** Keep the fixed $176.80 threshold, distinction between feed universes, and Morgan Stanley scenario. The saved feed reproduces **32 firms, mean $181.8125, median $182.50**; replacing MS $125 with $170 gives **$183.21875**. The lag regression also reproduces: full-sample coefficients **0.073962 / 0.128091 / 0.095346**, n=1,366. Its three-month carry from known prior price moves is a useful correction to the older qualitative note.

## Independent comparison forecasts

These are independent constructions from shared evidence, not blind forecasts made before seeing A07.

| Percentile | S02: December 15 close | S03: first session after Q4 release |
|---|---:|---:|
| 5 | $122 | $114 |
| 10 | $130 | $124 |
| 25 | $145 | $143 |
| 50 | **$163** | **$167** |
| 75 | $184 | $196 |
| 90 | $205 | $225 |
| 95 | $219 | $245 |
| P(≤$150) | **31.76%** | **31.88%** |
| P(≤$143) | **22.87%** | **24.93%** |
| P(≥$180) | **29.09%** | **37.73%** |
| P(<$100) | 0.294% | 1.340% |
| P(>$260) | 0.442% | 2.913% |

**S02 derivation:** Moment-match a positive-return distribution using $167.51 spot, 62 non-event sessions at 30% annual background volatility, and a November event with mean −2.7%, SD 9.5%; use 3.97% cash plus a judgmental 3% equity premium.  
Apply no separately estimated post-print drift: median **$163.205**, log SD **17.785%**. This avoids treating a weak historical drift as persistent alpha.

**S03 derivation:** Extend the same construction to 101 non-event sessions and add a February event with mean +2.6%, SD 9.5%; the mean retains about one-third of the six-print historical +7.93%.  
Apply no separate January/February seasonal increment: median **$167.373**, log SD **23.259%**. Reschedule the diffusion horizon when the actual release date is announced.

The $100/$260 cutoffs are reporting thresholds, not registry-imposed bounds. The lognormal tails are modeling assumptions; the historical crash evidence does not justify treating these tails as measured probabilities.

**S04: P(Yes) = 0.33; judgmental uncertainty interval 0.20–0.45.**  
Independently refitting the 22 print-window observations and propagating the price/event uncertainty gives a target-change mean **−1.276%**, SD **8.337%**, and **39.47%** probability of the required −3.5033% simple decline from $183.21875.  
Blend two-thirds of that estimate with one-third of a **20.23%** outside view—the mean of the exact-threshold 2023+ daily rate and 3/13 print-window rate—to obtain **33.06%**. The blend weights are judgmental.

## Reproduction script

Save as `docs/pitch-forecasts/audits/A07-reproduce.py` and run from the repository root:

```powershell
python docs/pitch-forecasts/audits/A07-reproduce.py
```

The script performs no writes or network requests. Historical windows are overlapping unless identified as print observations. It reconstructs the principal base rates from the underlying panels rather than importing forecast scripts.

```python
"""A07 audit reproduction. Dependencies: Python stdlib + pandas only."""
from pathlib import Path
from statistics import NormalDist
import json
import math
import sys

import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
S02 = Q / "close-15dec-2026"
S04 = Q / "sellside-mean-target-cut-by-15dec"
PROC = ROOT / "data/processed"
N = NormalDist()


def read(path, **kwargs):
    return pd.read_csv(path, **kwargs)


def report(label, values):
    x = pd.Series(list(values), dtype=float).dropna()
    print(label, {
        "n": len(x),
        "mean": x.mean(),
        "sd_sample": x.std(),
        "median": x.median(),
        "positive": int((x > 0).sum()),
    })


def ols(frame, dependent, predictors):
    """OLS by pivoted elimination, avoiding numpy/statsmodels imports."""
    rows = [
        [1.0] + [float(r[x]) for x in predictors]
        for _, r in frame.iterrows()
    ]
    ys = frame[dependent].astype(float).tolist()
    k = len(predictors) + 1
    a = [
        [sum(r[i] * r[j] for r in rows) for j in range(k)]
        + [sum(r[i] * y for r, y in zip(rows, ys))]
        for i in range(k)
    ]
    for i in range(k):
        pivot = max(range(i, k), key=lambda j: abs(a[j][i]))
        a[i], a[pivot] = a[pivot], a[i]
        divisor = a[i][i]
        if abs(divisor) < 1e-12:
            raise ValueError("Singular regression")
        a[i] = [v / divisor for v in a[i]]
        for j in range(k):
            if j != i:
                factor = a[j][i]
                a[j] = [v - factor * u for v, u in zip(a[j], a[i])]
    beta = [a[i][-1] for i in range(k)]
    residual = [
        y - sum(b * z for b, z in zip(beta, row))
        for row, y in zip(rows, ys)
    ]
    sse = sum(e * e for e in residual)
    mean = sum(ys) / len(ys)
    r2 = 1 - sse / sum((y - mean) ** 2 for y in ys)
    return beta, math.sqrt(sse / (len(ys) - k)), r2


# 1. Price-window base rates, tails, and realized volatility.
prices = read(
    S02 / "datasets/abnb_close_merged_to_20260916.csv",
    parse_dates=["Date"],
).set_index("Date").Close.sort_index()
assert not prices.index.duplicated().any()
rx = read(PROC / "abnb_earnings_reactions.csv",
          parse_dates=["reaction_date"])

for horizon in (63, 103):
    returns = 100 * (prices.shift(-horizon) / prices - 1)
    for label, x in (
        ("all", returns.dropna()),
        ("starts_2023plus", returns.loc["2023":].dropna()),
        ("starts_2024plus", returns.loc["2024":].dropna()),
    ):
        report(f"price_return_{horizon}_{label}", x)
        print("quantiles", x.quantile(
            [.01, .05, .10, .25, .50, .75, .90, .95]
        ).to_dict())
        print("thresholds", {
            "le150": (x <= 100 * (150 / 167.51 - 1)).mean(),
            "le143": (x <= 100 * (143 / 167.51 - 1)).mean(),
            "ge180": (x >= 100 * (180 / 167.51 - 1)).mean(),
            "minimum": x.min(),
            "minimum_start": str(x.idxmin().date()),
            "overlapping_windows_le_minus40": int((x <= -40).sum()),
        })

logret = (prices / prices.shift(1)).apply(math.log)
for label, x in (
    ("2023plus", logret.loc["2023":]),
    ("2024plus", logret.loc["2024":]),
):
    no_event = x[~x.index.isin(rx.reaction_date)]
    print("annualized_vol", label, {
        "all_pct": x.std() * math.sqrt(252) * 100,
        "excluding_prints_pct": no_event.std() * math.sqrt(252) * 100,
    })

# 2. Earnings reactions, February history, guide gates, W1/W2.
for column in ("abnb_1d_pct", "excess_1d_pct"):
    x = rx[column]
    report(column, x)
    print("rms_and_absolute", {
        "rms": math.sqrt(x.pow(2).mean()),
        "mean_abs": x.abs().mean(),
        "abs_ge7": int((x.abs() >= 7).sum()),
        "abs_ge10": int((x.abs() >= 10).sum()),
    })

feb = rx[rx.quarter.str.endswith("Q4")]
print("February_rows",
      feb[["quarter", "abnb_1d_pct", "excess_1d_pct"]].to_dict("records"))
report("February_raw", feb.abnb_1d_pct)

guide = read(PROC / "abnb_guidance_reaction_panel.csv")
gated = guide[
    (guide.guide_vs_street_pct < 0) & (guide.nq_nights_dir == -1)
]
print("guide_below_and_nights_lower",
      gated[["print_quarter", "ret_1d", "exc_1d"]].to_dict("records"))
report("guide_below_lower_raw", gated.ret_1d)

cp = read(PROC / "reverse_dcf/C/C_print_panel.csv")
for start in ("2022Q3", "2023Q1", "2024Q1"):
    for sign in (-1, 0, 1):
        g = cp[
            (cp.print_quarter >= start) & (cp.nights_accel_sign == sign)
        ]
        report(f"sign_{start}_{sign}_excess", g.ret_1d_cc_excess_pct)
        report(f"sign_{start}_{sign}_raw", g.ret_1d_cc_raw_pct)
        report(
            f"sign_{start}_{sign}_paired_cumulative_difference",
            g.ret_20d_cc_excess_pct - g.ret_1d_cc_excess_pct,
        )

old = rx.merge(
    cp[["print_quarter", "nights_yoy_accel_pts"]],
    left_on="quarter", right_on="print_quarter",
)
old = old[
    (old.quarter >= "2023Q1") & (old.nights_yoy_accel_pts >= 0)
].dropna(subset=["excess_20d_pct"])
report("old_accelerating_paired_difference",
       old.excess_20d_pct - old.excess_1d_pct)

ledger = read(PROC / "overnight/02_guidance_ledger.csv")
nights = ledger[ledger.metric.str.contains("nights", na=False)]
print("nights_guide_outcomes",
      nights[["print_quarter", "target_period", "direction",
              "value_mid", "actual", "outcome"]].to_dict("records"))

# 3. Reconstruct legacy drift and correctly rebased excess returns.
px = read(PROC / "overnight/09_prices_daily.csv",
          parse_dates=["Date"]).set_index("Date")
px = px.dropna(subset=["ABNB"])
drift_rows = []
for _, event in rx.iterrows():
    i = px.index.get_loc(event.reaction_date)
    anchor, before, day = px.iloc[i - 21], px.iloc[i - 1], px.iloc[i]
    row = {
        "q": event.quarter,
        "date": event.reaction_date,
        "legacy_day1": 100 * (
            (day.ABNB - before.ABNB) / anchor.ABNB
            - (day.QQQ - before.QQQ) / anchor.QQQ
        ),
    }
    for h in (20, 27, 60):
        if i + h >= len(px):
            continue
        end = px.iloc[i + h]
        row[f"legacy{h}"] = 100 * (
            (end.ABNB - day.ABNB) / anchor.ABNB
            - (end.QQQ - day.QQQ) / anchor.QQQ
        )
        row[f"proper{h}"] = 100 * (
            end.ABNB / day.ABNB - end.QQQ / day.QQQ
        )
    drift_rows.append(row)
drift = pd.DataFrame(drift_rows)
for label, g in (
    ("all", drift),
    ("reaction_dates_2023plus", drift[drift.date >= "2023-01-01"]),
    ("W1", drift[drift.q >= "2023Q1"]),
    ("W2", drift[drift.q >= "2024Q1"]),
    ("day1_up", drift[drift.legacy_day1 >= 0]),
    ("day1_down", drift[drift.legacy_day1 < 0]),
):
    for column in ("legacy20", "proper20", "proper27",
                   "legacy60", "proper60"):
        report(f"drift_{label}_{column}", g[column])

monthly = px[["ABNB", "QQQ"]].resample("ME").last().pct_change() * 100
monthly = monthly.loc["2021":]
monthly["excess"] = monthly.ABNB - monthly.QQQ
for month in (1, 2, 9, 10, 11, 12):
    report(f"calendar_month_{month}",
           monthly.loc[monthly.index.month == month, "excess"])

# 4. Target tape and exact threshold.
ud = read(
    S04 / "sources/yfinance_upgrades_downgrades_20260917T031221Z.csv",
    parse_dates=["GradeDate"],
)
live = ud[
    (ud.GradeDate >= "2025-09-16")
    & (ud.GradeDate < "2026-09-17")
    & (ud.currentPriceTarget > 0)
].sort_values("GradeDate").groupby("Firm").tail(1)
base = live.currentPriceTarget.mean()
ms_base = live.currentPriceTarget.where(
    live.Firm != "Morgan Stanley", 170.0
).mean()
print("live_tape", {
    "n": len(live), "mean": base,
    "median": live.currentPriceTarget.median(),
    "MS_adjusted_mean": ms_base,
    "oldest": str(live.GradeDate.min()),
})
exact_log_threshold = math.log(176.8 / ms_base)

panel = read(PROC / "reverse_dcf/D/D_target_panel_daily.csv",
             parse_dates=["date"])
panel = panel[panel.n_targets >= 10].set_index("date").sort_index()
forward = (panel.mean_target.shift(-63) / panel.mean_target).apply(
    math.log
).dropna()
for threshold in (-.035, exact_log_threshold, math.log(176.8 / base)):
    for label, x in (
        ("all", forward),
        ("2023plus", forward.loc["2023":]),
        ("2024plus", forward.loc["2024":]),
    ):
        print("target_daily_rate", label, {
            "threshold_log": threshold, "n": len(x),
            "hits": int((x <= threshold).sum()),
            "p": (x <= threshold).mean(),
        })

# Rebuild the original -36/+27 print windows.
rows = []
for _, event in rx.iterrows():
    if event.reaction_date not in panel.index:
        continue
    i = panel.index.get_loc(event.reaction_date)
    if i < 36 or i + 27 >= len(panel):
        continue
    a, b = panel.iloc[i - 36], panel.iloc[i + 27]
    rows.append({
        "q": event.quarter,
        "target": 100 * (b.mean_target / a.mean_target - 1),
        "price": 100 * (b.close / a.close - 1),
        "day1": event.abnb_1d_pct,
    })
windows = pd.DataFrame(rows)
for label, g in (
    ("all", windows),
    ("W1", windows[windows.q >= "2023Q1"]),
    ("W2", windows[windows.q >= "2024Q1"]),
):
    print("target_print_windows", label, {
        "n": len(g), "hits_simple_le_minus3_5": int((g.target <= -3.5).sum()),
        "ols_beta_residual_sd_r2": ols(g, "target", ["price", "day1"]),
    })

lp = panel.close.apply(math.log)
lt = panel.mean_target.apply(math.log)
reg = pd.DataFrame({
    "y": lt.diff(21), "x0": lp.diff(21),
    "x1": lp.diff(21).shift(21), "x2": lp.diff(21).shift(42),
}).dropna()
for label, g in (
    ("all", reg), ("2023plus", reg.loc["2023":]),
    ("2024plus", reg.loc["2024":]),
):
    print("target_chase", label, len(g),
          ols(g, "y", ["x0", "x1", "x2"]))

revisions = read(PROC / "reverse_dcf/D/D_print_revisions.csv")
for label, g in revisions.groupby("print_class"):
    print("print_target_changes", label, {
        "n": len(g), "mean20": g.d_mean_target_plus20_pct.mean(),
        "mean40": g.d_mean_target_plus40_pct.mean(),
        "any_cut": int((g.d_mean_target_plus20_pct < 0).sum()),
        "cut_ge3_8": int((g.d_mean_target_plus20_pct <= -3.8).sum()),
    })
    print(g[["quarter", "price_move_day1_pct",
             "d_mean_target_plus20_pct"]].to_dict("records"))

# 5. Reviews-index correction and calendar arithmetic.
print("reviews_revintaging",
      read(PROC / "q3nowcast_v2/E/t1_fail_e5_rerun.csv").to_dict("records"))
holidays = pd.to_datetime([
    "2026-11-26", "2026-12-25", "2027-01-01", "2027-01-18",
])
for a, b in (
    ("2026-09-16", "2026-11-05"),
    ("2026-11-06", "2026-12-15"),
    ("2026-12-15", "2027-02-11"),
    ("2026-09-16", "2026-12-15"),
    ("2026-09-16", "2027-02-12"),
):
    print("sessions", a, b,
          len(pd.bdate_range(a, b, inclusive="right").difference(holidays)))

# 6. Actual saved blend anchor and event-variance correction.
imp = json.loads(
    (S02 / "datasets/implied_dist_20260917T031221Z.json").read_text()
)
for question, key in (("S02", "dec15"), ("S03", "feb12")):
    d = imp[key]
    median = d["smile_rnd"]["50"] * math.exp(.03 * d["T_years"])
    sd = d["sigma_pct"] / 100 * math.sqrt(d["T_years"])
    probabilities = {
        str(k): N.cdf(math.log(k / median) / sd)
        for k in (100, 143, 150, 180, 260)
    }
    print("actual_lognormal_anchor", question, median, probabilities)
    cdf = read(S02 / f"datasets/{question}_final_cdf.csv")
    assert cdf.cdf_final.diff().dropna().ge(0).all()
    assert cdf.cdf_final.between(0, 1).all()
    print("saved_final_CDF_at_thresholds", question,
          cdf[cdf.price.isin([100, 143, 150, 180, 260])].to_dict("records"))

w = 28 / 63
d = imp["feb12"]
variance = (d["sigma_pct"] / 100) ** 2 * d["T_years"]
print("February_event_corrected_log_sd",
      math.sqrt(variance + (1 - w) * .095 ** 2))

# Negative-density diagnostic from the saved fitted smile coefficients.
term = read(
    S02 / "datasets/implied_term_structure_20260917T031221Z.csv"
).set_index("expiry")


def gradient(y, dx):
    return (
        [(y[1] - y[0]) / dx]
        + [(y[i + 1] - y[i - 1]) / (2 * dx)
           for i in range(1, len(y) - 1)]
        + [(y[-1] - y[-2]) / dx]
    )


def area(y, dx):
    return dx * (sum(y) - .5 * (y[0] + y[-1]))


for target, first, second in (
    ("2026-12-15", "2026-12-18", None),
    ("2027-02-12", "2027-01-15", "2027-03-19"),
):
    T = (pd.Timestamp(target) - pd.Timestamp("2026-09-16")).days / 365
    z = term.loc[first]
    coeff = [z.atm_iv / 100, z.smile_b, z.smile_c]
    if second:
        z2 = term.loc[second]
        weight = (T - z["T"]) / (z2["T"] - z["T"])
        coeff = [
            (1 - weight) * a + weight * b
            for a, b in zip(coeff, [z2.atm_iv / 100,
                                    z2.smile_b, z2.smile_c])
        ]
    F = imp["spot"] * math.exp(.0397 * T)
    calls = []
    for i in range(2601):
        K = 60 + .1 * i
        x = max(-.45, min(.45, math.log(K / F)))
        vol = max(.05, min(2, coeff[0] + coeff[1] * x + coeff[2] * x*x))
        d1 = (math.log(F / K) + .5 * vol*vol*T) / (vol * math.sqrt(T))
        calls.append(F * N.cdf(d1) - K * N.cdf(d1 - vol * math.sqrt(T)))
    density = gradient(gradient(calls, .1), .1)
    print("negative_RND_mass", target,
          area([max(-v, 0) for v in density], .1))

# 7. Independent comparison distributions.
spot, bg, total_drift = 167.51, .30, .0697
nov_mean, nov_sd, feb_mean, feb_sd = -.027, .095, .026, .095
nov_var = math.log1p((nov_sd / (1 + nov_mean)) ** 2)
feb_var = math.log1p((feb_sd / (1 + feb_mean)) ** 2)

for question, sessions, include_feb in (
    ("S02", 62, False), ("S03", 101, True),
):
    mu = (
        math.log(spot) + (total_drift - bg*bg/2) * sessions / 252
        + math.log1p(nov_mean) - nov_var/2
    )
    variance = bg*bg * sessions / 252 + nov_var
    if include_feb:
        mu += math.log1p(feb_mean) - feb_var/2
        variance += feb_var
    sd = math.sqrt(variance)
    print("independent_price", question, {
        "percentiles": {
            q: math.exp(mu + sd * N.inv_cdf(q / 100))
            for q in (5, 10, 25, 50, 75, 90, 95)
        },
        "CDF": {
            k: N.cdf((math.log(k) - mu) / sd)
            for k in (100, 143, 150, 180, 260)
        },
    })

beta, residual_sd, _ = ols(windows, "target", ["price", "day1"])
expected_gross = math.exp(total_drift * 62 / 252) * (1 + nov_mean)
v = bg*bg * 62 / 252 + nov_var
return_mean = 100 * (expected_gross - 1)
return_variance = expected_gross**2 * math.expm1(v) * 10000
covariance = expected_gross / (1 + nov_mean) * nov_sd**2 * 10000
mu = beta[0] + beta[1] * return_mean + beta[2] * nov_mean * 100
sd = math.sqrt(
    residual_sd**2 + beta[1]**2 * return_variance
    + beta[2]**2 * (nov_sd * 100)**2
    + 2 * beta[1] * beta[2] * covariance
)
gate = 100 * (176.8 / ms_base - 1)
model_p = N.cdf((gate - mu) / sd)
recent = windows[windows.q >= "2023Q1"]
outside = (
    (forward.loc["2023":] <= exact_log_threshold).mean()
    + (recent.target <= gate).mean()
) / 2
print("independent_S04", {
    "target_change_mean_pct": mu, "target_change_sd_pct": sd,
    "required_simple_change_pct": gate, "model_p": model_p,
    "outside_p": outside, "final_p": (2 * model_p + outside) / 3,
})
```