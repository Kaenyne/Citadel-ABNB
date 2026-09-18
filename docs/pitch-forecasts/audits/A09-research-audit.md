**R01 — 42%: not defensible under the question’s required derivation.**  
The calculation reproduces, but 40% of its weight comes from outside the specified nowcast distribution.  
First remove the market contribution and separate management-delivery assumptions from the requested forecast.  
Keep the denominator fixed at 133.6m; rebuild impacts from the same distribution used for the probability.  
My independent benchmark is **38%**; the log’s own alt-data-only construction gives **33.2%**.

**R02 — 32%: plausible numerically, but not defensible as written.**  
It inherits R01’s derivation violation and uses a different distribution for its impact calculation.  
First produce R01 and R02 from one nowcast distribution, with an explicit printed-number rounding convention.  
The sequential and headline empirical-error counts reproduce; the claimed persistence evidence does not.  
My independent benchmark is **25%**; the log’s own alt-data-only construction gives approximately **22%**.

**R03 — 7%: obsolete relative to its current upstream forecast.**  
C06 is now revision 2, with P(disclosed share ≥25%) = **25%**, versus the **15%** used here.  
First replace C06’s withdrawn share model and reconcile the joint’s marginals with the current forecasts.  
The conjunction does not establish that RNPL caused the nights outcome or that the lap thesis is disproved.  
My independent benchmark is **11%**; retaining the old conditional probability with current C06 gives **12.85%**.

## Scope and verification

Audit date: 2026-09-17. Reviewed all three revision-1 logs, forecast JSONs, saved sources, and datasets, together with their cited repo inputs.

The original calculation was replayed with directory creation disabled and every save redirected to memory. All ten output artifacts reproduced exactly or within floating-point CSV precision; the three dataset folders are byte-identical. Unrounded outputs are **0.4236515384 / 0.3159324240 / 0.074105**. Reproducibility therefore passes; several modeling and interpretation choices do not.

A direct Kalshi fetch failed with `WinError 10013`—socket access forbidden. External-source conclusions below use saved snapshots, not a fresh market verification. Neither excluded raw-data directory was opened. No files were written.

References below use `R01/log`, `R02/log`, and `R03/log` for the respective `research-log.md` files under `docs/pitch-forecasts/questions/<slug>/`. `A09/script` denotes their identical `datasets/a09_nights_error_distribution.py`.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A09-01 | R01, R02 | critical | `QUESTIONS.md`, R01 fine print; both JSONs `estimates.blend_weights`; `A09/script` §6 | The requested probability must derive from the team nowcast and its error distribution, explicitly excluding web-derived forecasting. The final instead assigns 30% to management/sequential assumptions and 10% to Kalshi. The log itself labels alt-data-only as the strict reading. | Replayed `0.60×alt + 0.30×outside + 0.10×market`, obtaining 0.423652/0.315932. The specified alt-data leg gives **0.332140/0.217920**. | Make the nowcast-derived probabilities the answers. Present other views as diagnostics. Removing only Kalshi and renormalizing gives **0.405457/0.291113**, which still retains the outside-view modification. |
| A09-02 | R01; inherited by R03 | critical | `R01/log:28`, convention 2 | The log changes the resolution rule if Airbnb restates the prior-year base: it substitutes the letter’s stated y/y. The registry specifies division by **133.6m**. These can resolve differently. | Compared the registry’s explicit formula with convention 2. | Retain the fixed denominator. Discuss restated growth separately; do not change the event through a forecasting convention. |
| A09-03 | R03 | major | `R03/log`, claims 1, 5, 10–11; JSON `joint_model`, `cap_c06_p_a` | The dependency is stale at audit handoff. C06 revision 2 raises (a) from 0.15 to **0.25** and explicitly withdraws the directional `U(-2,0)` seasonal penalty still embedded in R03. | Read current C06 JSON and rebuilt its v2 share simulation: true high-share probability **0.38910**; disclosed-(a) construction **0.248051**. The final vector sums to 1. | Rebuild from C06 v2 and the revised nights distribution. Holding only the old `P(R01 given a)=0.514074` fixed gives **0.128518**. This is a dependency update, not evidence the original agent could have known a later revision. |
| A09-04 | R01, R02 | major | R01 claim 14; R02 claim 14; saved Kalshi JSON; Octagon snapshot | The logs miss populated fixed-point volume/OI fields and confuse last trades with bid/ask midpoints. “Unchanged since July 29” is not demonstrated. They also give an explicitly stale anchor nonzero weight, contrary to the forecasting standard. | At 146m/148m/150m, `volume_fp` is **998.66/428.14/590.96**, OI **689.51/423.14/413.21**, and 24-hour volume zero. `updated_time` is August 4. Octagon’s 60/53/30 are last prices; current saved mids are **64.5/52.5/34**, not all within two points. | Correct the field extraction and distinguish metadata update, last trade, and quote freshness. Preserve the timestamped ladder as an adjacent comparison; give it zero forecast weight under the question’s fine print and the skill’s stale-source rule. |
| A09-05 | R01, R02 | major | `A09/script` §§1–2; both logs claim 4 and §5 | The probability construction uses only W2 errors despite loading both windows. Multiplying every model’s errors by one model’s RMSE ratio is described as “revintaged” although those seven error paths were not refitted. | From `E_aug/backtest_wf_paths.csv`, the scaled-kernel probabilities at the original 10/10.6 thresholds are **0.268391/0.167173** on W2, versus **0.176605/0.123499** on the six available W1 models. W1 has no median-weighted model. `t1_fail_e5_rerun.csv` supplies a headline-model aggregate RMSE, not seven replacement error vectors. | Show both-window sensitivity; label uniform scaling a judgmental stress test. Do not imply these are measured revintaged residuals or a validated probability ensemble. |
| A09-06 | R01, R02 | major | Both logs claim 3; R01 §5 asymmetry; R02 §4 | “Only two quarters where every row under-predicted” is false. The narrative then overstates the exclusivity of the product-acceleration explanation. | Pivoted the seven W2 error paths. All seven underpredicted **4Q24, 3Q25, and 2Q26**. For 3Q25, errors range **−0.0626 to −0.9825pp**; headline error is **−0.2481pp**. | Correct to **3/10** common underprediction quarters. Keep the narrower R02 headline-tail count **2/10**, which does reproduce. Establish causal/pre-announcement claims separately from error signs. |
| A09-07 | R01, R02 | major | Guidance claims; `A09/script` management-delivery construction; pre-mortems | The management record is heterogeneous, and “a 16-print record of guides met” overstates even its own coding. The supposed stable-guide errors are not all changes against the prior quarter. Neither the 0.6 cushion nor 1.3 error SD is estimated from a comparable low-double-digit-floor sample. | `02_guidance_ledger.csv` contains **13 met, 2 above-range, 1 not-met, 1 pending**. The 1Q25 comparator is **1Q24 excluding Leap Day, 8.5%**, not preceding-quarter growth of 12.35%; 1Q23 says “nearly as strong,” not stable. | Report **15/16 meeting or exceeding the coded guide**, including the definition caveats. Treat `N(0.6,0.5)` and management SD 1.3 as assumptions, not a calibrated base rate. The sequential rates themselves pass: **7/16, 6/16**; W1 **6/14, 5/14**; W2 **5/10, 4/10**. |
| A09-08 | R03 | major | `R03/log:86–91`, Independent Estimates | The claimed base-rate derivation is internally inconsistent. It says it scales by a conditional lift of `0.51/0.42` but actually multiplies by **0.7**. Its agreement with the decomposition is not independent evidence. | `0.16×0.55×(0.51/0.42)=0.106857`; `0.16×0.55×0.7=0.0616`. Both constructions reuse C06’s share assumptions. | Remove the unexplained multiplier. State **NOT_INDEPENDENTLY_DERIVED** and **NO_EXTERNAL_ANCHOR**. Do not invent a third independent estimate when none exists. |
| A09-09 | R03 | major | Claim 5, “adoption … saturated” | About 70% adoption does not establish saturation or that only eligibility growth can increase share. The two cited 70% figures also have different denominators. | RNPL ledger D005 is people offered the product; D022 and the 4Q25 letter footnote use global GBV-weighted adoption among eligible bookings. D022’s note explicitly warns against chaining the two statistics. | Label saturation an assumption; allow adoption and booking-mix changes within existing eligibility. Preserve the denominator distinction when arguing about share growth. |
| A09-10 | R01, R02 | major | R01 §5 “every outside series … decelerates”; R02 §4; external-stack claims | The synthesis overstates the uniformity of outside evidence and selectively uses the final August hotel week without its calendar counterpart. | `G_external-sources-q3-read.md` §1 reports NTTO improving **−14.1% to −7.0%**, Expedia July consistent with Q2, and STR **+1.7% followed by +16.1%**, explicitly identifying a Labor Day timing artifact. | Keep the cleaner mid-August slowdown and the broad +9.2% consistency check. Remove “every series” and show contrary/neutral signals. The query log itself starts neutrally; this is an interpretation problem, not demonstrated query-selection misconduct. |
| A09-11 | All | major | R01 §6; R02 claim 19; `A09/script` §§7–8 | The “final-calibrated normal” is not the distribution that generated both final probabilities. R03 additionally copies the R01 conditional mean despite modeling positive dependence with RNPL share. | `N(9.672647,1.70)` gives **P(≥10.6)=0.292704**, versus the final blend **0.315932**. R03 impact code passes exactly R01’s conditional mean rather than conditioning on both legs. | Use one joint distribution for R01, R02, R03 and conditional impacts. The simple subset inequalities pass, but those inequalities do not validate the impact distribution. |
| A09-12 | R01, R03 | major | `A09/script` §8 `d1_r01`; impact stock rows | The stock calculation calls all flat/accelerating S01 cells “given nights ≥10,” omitting the **10.00–10.09%** interval that S01 classifies as decelerating. It also retains old S01 state weights after changing the nights probabilities. | S01’s stated cutoffs are 10.09 and 10.59. Under its `N(9.55,1.48)`, the omitted interval has **2.294% unconditional probability**. The selected rounded cells total 0.37; their weighted return is **1.3027%**. | Condition S01 draws directly on the R01 event and the updated nights distribution. For R03, condition on both nights and disclosure; do not reuse R01’s cell mix. |
| A09-13 | All | major | Impact stock and EV rows | The reported “EV” mixes conditional return expectations with baseline medians, then adds a forward-growth multiple effect to an earnings-reaction estimate without identifying a separate horizon or avoiding overlapping repricing. | S01 identifies **−8.6% as a base-case median**, with mean **−8.3%**; unconditional median is −2.9%, mean approximately −2.7%. The A09 code adds `FY27 growth × 0.44 × $9.5` to the reaction-cell result. | Choose a valuation horizon and compute expected dollar outcomes consistently. Show event-reaction and fundamental-valuation impacts separately unless their incremental relationship is modeled. Current materiality labels are arithmetic results of this construction, not validated expected payoffs. |
| A09-14 | All | major | Impact FY26 margin and FY27 EPS; `A09/script` `impact()` | **0.66pp margin change per 1% revenue change is not 66% EBITDA flow-through.** FY26 margin is also approximated by half the H2 margin change instead of recomputing the annual ratio. | `23_macro_sensitivity.csv` identifies 0.66 as a margin sensitivity under held costs. Under held costs, incremental revenue equals incremental EBITDA. Using `23_forecast_annual.csv` and the logs’ existing dollar shocks gives FY27 EPS **$0.119/$0.196/$0.295**, versus $0.078/$0.129/$0.195; FY26 margin changes **0.514/0.669/0.567pp**, versus 0.42/0.56/0.47. | Recompute revenue, EBITDA, and margin identities under one cost assumption. These corrections isolate accounting errors; they do not endorse the underlying revenue shocks. |
| A09-15 | R02 | major | §9, 4Q26 nights persistence | The claim that accelerating Q3 prints were followed by Q4 at or above Q3 in “2 of 2 bucket-era cases” is unsupported and contradicts the examples beside it. The 60%/50% persistence factors remain judgmental. | Original growth series: **3Q22 25.09 → 4Q22 20.16; 3Q23 13.54 → 4Q23 12.02; 3Q25 8.79 → 4Q25 9.82**. Thus **1/3 since 2022**, or **1/2 since 2023**. Only the 2025 transition enters the stated numerical-bucket era. | Delete 2/2. Retain persistence only as a clearly labeled scenario with sensitivity; those observations do not estimate 60% persistence. |
| A09-16 | R03 | major | §9 opening and materiality sentence; FY27 impact | The event is elevated from a joint observation to causal proof: “the lap thesis is wrong, not just early.” Its resolution does not require that the July expansion generated the nights growth or removed future drag. | `D1_prereg_thresholds.csv` says the combination **weakens** the hypothesis and that share identifies nothing alone. R03 itself retains a non-RNPL nights-growth pathway. The module’s base/bull FY27 growth is **6.41/6.88**, a 0.47pt scenario difference, not an identified conditional effect. | Replace “wrong” with “weakens.” Treat the added FY27 +0.8pt as a separate upside assumption, not an implication of resolution. |
| A09-17 | R03 | major | JSON `impact.adr_pts`; `A09/script` `impact()` | ADR +0.3pt appears in the impact table but affects none of its revenue, EBITDA, or EPS computations. | `adr` is returned as metadata only. Revenue calculations use nights alone. The brief’s Q3 sensitivity would make +0.3 ADR approximately **+$13.8M Q3 revenue** before any explicitly modeled lag effects. | Either propagate a specified ADR path through GBV/revenue or remove the quantified ADR shock. Do not present mutually inconsistent driver and financial rows. |
| A09-18 | R01, R02 | minor | Resolution conventions versus `T_R01,T_R02` and market interpolation | The logs say printed millions govern, but calculations use exact growth cutoffs 10.0/10.6, equivalent to **146.96m/147.7616m**. No latent-to-reported rounding model is specified. | Exact growth at 147.0m/147.8m is **10.029940%/10.628743%**. Saved-ladder interpolation at printed thresholds is **0.585/0.537**, versus 0.5874/0.539304. | Specify whether the random variable is reported millions or latent nights rounded to one decimal. Implement that convention consistently. The numerical effect is small. |
| A09-19 | All | minor | JSON `final.p` versus `impact.ev_stock_usd_per_share`; impact display equations | EV uses hidden unrounded probabilities and unrounded stock impacts, while the displayed equations use rounded inputs. | Using published probabilities and stock impacts gives **$7.896/$7.296/$1.554**, versus stored **$7.98/$7.21/$1.64**. The latter reproduce from internal calculations. | Use one canonical precision or label EV as computed before rounding. In particular, `0.32×22.8` rounds to **$7.3**, not $7.2. |
| A09-20 | R01, R02 | minor | Claim 5 | “September is 40% of the quarter’s days” is false. | Calendar arithmetic: **30/(31+31+30)=32.61%**. Additional unobserved August days are a different coverage concept. | Correct the calendar fraction and separately quantify the observation cutoff. |
| A09-21 | R01, R02 | minor | §7 versus §8 monitoring rules | Identical center assumptions lead to conflicting update instructions. | R01 §7 gives center 9.2 → final **0.41**, while §8 gives **0.35**. R02 gives **0.31** versus **0.26**. The script does not implement these monitoring overrides. | Generate updates from a defined distribution transformation and weight rule. Distinguish replacing a center from shifting all mixture components. |

## What the logs do well and should keep

### R01

Keep the seven nowcast rows, full historical error vectors, empirical-versus-normal comparison, and explicit WPK downgrade. The headline W2 error statistics reproduce: **n=10, mean +0.528315pp, sample SD 1.446836pp, RMSE 1.470755pp, seven overpredictions**. The counterargument that stay-date reviews can miss booking-date acceleration is directly relevant.

The ledger’s sequential counts reproduce without manually typed history. The Bloomberg processed snapshot also supports **28 estimates, 147–151m range**, with a **12 September** source date. This is evidence about analyst positioning, not a probability distribution of outcomes.

### R02

Keep the stricter-threshold calculation, SD sensitivity, and separation of the event from descriptive “acceleration” language. The headline plug-in count is **2/10**, and the sequential acceleration reference class is **6/16**, with **3/4** Q2-to-Q3 transitions clearing the required increase.

The cited reaction contrast reproduces on fiscal-quarter windows: W1 decelerating prints **−5.5889% excess, n=8, zero positive**, accelerating **+6.0379%, n=5**; W2 gives **−5.9675%, n=5** and **+8.8319%, n=4**. Keep the small-sample qualification and the prohibition on adding R01 and R02 EVs.

### R03

Keep the distinction between true share and disclosed GBV share, the language/disclosure gates, and the explicit common-cause model. D043/D044 are supported by the saved 2Q26 transcript: management reported over-20% GBV share and a July eligibility expansion without quantifying its size.

Keep the no-external-anchor admission and the warning that R03 is inside R01. The original 7% joint satisfies the marginal bounds, including the current C06 bound; its problem is the obsolete construction, not a violated probability inequality.

## Independent forecasts

These are independently recomputed audit benchmarks, not claims of independent underlying evidence. Intervals below are judgmental model-uncertainty ranges.

### R01: **38%**, range **27–50%**

Use the repo nowcast center **9.5%** and an assumed **1.70pp** predictive SD, between the fresh-read W2 RMSEs **1.634–1.816pp**; assign no market weight.  
Modeling reported nights continuously gives `P(growth ≥10.029940%) = 0.377623`; using the registry’s unrounded 10% formula gives 0.384334, also 38% rounded.

### R02: **25%**, range **14–38%**

Use the same distribution and the printed **147.8m** threshold: `P(growth ≥10.628743%) = 0.253356`.  
At center 9.5, SD 1.48 gives **22.3%**, SD 1.816 gives **26.7%**, and naive-scale SD 2.159 gives **30.1%**.

### R03: **11%**, range **6–18%**

Use current C06(a) **25%**, rebuild its v2 share draws, and allow a weak positive link between the shared expansion variable and nights; this gives `P(R01 given a) ≈0.427`.  
Thus the joint is **0.1066**; independence gives **0.0944**, and a stronger assumed link gives **0.1127**. The link is a scenario assumption, not an estimated causal coefficient.

These point estimates satisfy **R02 ≤ R01** and **R03 ≤ min(C06a,R01)**. None triggers the binary extreme-probability gate.

## Reproduction script

Save as `docs/pitch-forecasts/audits/A09-reproduce.py` and run from the repository root. It uses only the standard library and pandas, reads existing files, and makes no network requests or writes.

```python
"""A09 audit reproduction. Run from repo root; stdlib + pandas; no writes/network."""
from pathlib import Path
from statistics import NormalDist, mean, pstdev
import json
import math
import random
import pandas as pd

ROOT = Path.cwd()
assert (ROOT / "docs/pitch-forecasts/QUESTIONS.md").exists(), "Run from repo root"
Q = ROOT / "docs/pitch-forecasts/questions"
A = Q / "risk-q3-nights-meets-guide"
C = Q / "rnpl-gbv-share-disclosed"
N = NormalDist()


def read(path):
    return pd.read_csv(ROOT / path)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def qi(q):
    return (2000 + int(q[-2:])) * 4 + int(q[0]) - 1


def tail(mu, sd, threshold):
    return N.cdf((mu - threshold) / sd)


def report_rate(name, values, thresholds):
    values = list(values)
    print(name, "n =", len(values),
          [(t, sum(x >= t for x in values),
            round(sum(x >= t for x in values) / len(values), 6))
           for t in thresholds])


# Guidance and sequential-change reference classes: originals, no typed history.
g = read("data/processed/overnight/02_guidance_ledger.csv")
g = g[g.metric.eq("nights_yoy_pct")].sort_values("print_date")
resolved = g[g.actual.notna()]
print("Guidance outcomes:", g.outcome.value_counts().to_dict())
print("Resolved guides meeting/exceeding coded guidance:",
      resolved.outcome.isin(["met", "above_range"]).sum(), "/", len(resolved))
levels = dict(zip(resolved.target_period, resolved.actual))
levels["2Q22"] = float(
    g.loc[g.print_quarter.eq("2Q22"), "comparator_value"].iloc[0]
)
keys = sorted(levels, key=qi)
changes = [(q, levels[q] - levels[keys[i-1]])
           for i, q in enumerate(keys) if i]
for label, rows in [
    ("All 3Q22-2Q26", changes),
    ("W1 target 1Q23+", [(q, x) for q, x in changes if qi(q) >= qi("1Q23")]),
    ("W2 target 1Q24+", [(q, x) for q, x in changes if qi(q) >= qi("1Q24")]),
    ("Q2-to-Q3", [(q, x) for q, x in changes if q.startswith("3Q")]),
]:
    report_rate(label, [x for _, x in rows], [-0.34, 0.26])
    print("  members:", rows)
print("Stable/approximate comparators:")
print(g[g.direction.isin(["stable", "approx"])][
    ["target_period", "comparator_value", "actual", "distance_from_mid", "quote"]
].to_string(index=False))

# Original nowcast rows and full-precision errors; W2 has 7 models, W1 only 6.
nc = read("data/processed/q3nowcast/E_aug/q3_2026_nowcast.csv")
wf = read("data/processed/q3nowcast/E_aug/backtest_wf_paths.csv")
wf = wf[wf.target.eq("nights_yoy") & wf.lag.eq(0)]
rev = read("data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv")
v1 = rev.loc[rev.variant.str.startswith("v1"), "wf_ratio_vs_naive"].iloc[0]
factor = (
    rev.loc[rev.variant.str.startswith("b:"), "wf_ratio_vs_naive"].iloc[0] / v1
)
print("Revintage inputs:", rev[
    ["variant", "wf_n", "wf_rmse", "wf_ratio_vs_naive"]
].to_string(index=False))
thresholds = [10.0, 10.6, (147.8 / 133.6 - 1) * 100]
features = [f"{r.region}|{r.measure}|{r.weighting}" for r in nc.itertuples()]
kernel_w2 = None
for window in ["2023Q1+", "2022Q1+"]:
    probs = []
    print("ERROR WINDOW", window)
    for r, feature in zip(nc.itertuples(), features):
        e = wf[wf.feature.eq(feature) & wf.window.eq(window)].sort_values("qi")
        if e.empty:
            print("  MISSING:", feature)
            continue
        errors = e.err_feature.tolist()
        actual = [r.implied_nights_yoy - x for x in errors]
        plug = [sum(x >= t for x in actual) / len(actual) for t in thresholds]
        kernel = [
            mean(tail(r.implied_nights_yoy - factor*x, 0.5, t) for x in errors)
            for t in thresholds
        ]
        probs.append(kernel)
        print(feature, "n", len(e), "bias", mean(errors),
              "sample_sd", e.err_feature.std(),
              "rmse", math.sqrt(mean(x*x for x in errors)),
              "overpredictions", sum(x > 0 for x in errors),
              "plugin", plug, "scaled_kernel", kernel)
    mix = [mean(p[i] for p in probs) for i in range(len(thresholds))]
    print("Equal-model kernel mixture:", mix, "models", len(probs))
    if window == "2023Q1+":
        kernel_w2 = mix
        panel = wf[
            wf.feature.isin(features) & wf.window.eq(window)
        ].pivot(index="qi", columns="feature", values="err_feature")
        print("All models underpredicted:", [
            f"{int(q)//4}Q{int(q)%4+1}"
            for q in panel.index[(panel < 0).all(axis=1)]
        ])
        print("Minimum pairwise error correlation:", panel.corr().min().min())
print("Analytic alt-only blend at original thresholds:",
      [(kernel_w2[i] + tail(9.55, 1.7, thresholds[i])) / 2 for i in [0, 1]])

# Saved market fields: fixed-point strings are real volume/OI fields.
market = load(A / "sources/kalshi_markets_KXABNB_open_20260917T032158Z.json")
mids = {}
for m in market["markets"]:
    strike = m["floor_strike"] / 1e6
    mids[strike] = (
        float(m["yes_bid_dollars"]) + float(m["yes_ask_dollars"])
    ) / 2
    print("Kalshi", strike, "mid", mids[strike], "last", m["last_price_dollars"],
          "volume", m["volume_fp"], "OI", m["open_interest_fp"],
          "24h", m["volume_24h_fp"], "updated", m["updated_time"])


def interp(x):
    return mids[146] + (mids[148] - mids[146]) * (x - 146) / 2


print("Market interpolation, printed thresholds:", interp(147), interp(147.8))
print("Market interpolation, original script:",
      interp(133.6*1.10), interp(133.6*1.106))

# Original JSON algebra and cross-question consistency.
f = load(A / "datasets/a09_final.json")
for q in ["r01", "r02"]:
    calc = (
        0.6*f["alt_data"]["used"][q]
        + 0.3*f["base_rate"]["used"][q]
        + 0.1*f["market"]["kalshi_mid_interp"][q]
    )
    print("Original blend", q, calc, "saved", f["final"][q],
          "remove market and renormalize",
          (calc - 0.1*f["market"]["kalshi_mid_interp"][q]) / 0.9)
print("Impact normal P(R02):",
      tail(f["final_calibrated_normal"]["centre"], 1.7, 10.6))
c06 = load(C / "forecasts/2026-09-17-forecast.json")
pa = c06["final"]["vector"]["a_ge_25pct"]
print("Current C06 revision/vector:", c06["revision"], c06["final"]["vector"])
print("Current C06 times old conditional:", pa*f["r03"]["p_r01_given_a"])
print("R03 base-rate formula with stated lift:", .16*.55*(.51/.42),
      "with unexplained .7:", .16*.55*.7)

# RNPL disclosure continuation from both saved matrices.
for name in [
    "metric_persistence_matrix_4Q20-2Q26.csv",
    "metric_persistence_matrix_v2_4Q20-2Q26.csv",
]:
    d = pd.read_csv(C / "datasets" / name, keep_default_na=False)
    cols = list(d.columns)[1:]
    for start in ["4Q20", "1Q23", "1Q24"]:
        hit = den = 0
        for row in d.itertuples(index=False, name=None):
            cells = row[1:]
            for i in range(max(1, cols.index(start)), len(cols)):
                if "L" in cells[i-1] or "C" in cells[i-1]:
                    den += 1
                    hit += int("L" in cells[i] or "C" in cells[i])
        print("Disclosure continuation", name, start, hit, den, hit/den)

# Reaction reference classes use fiscal-quarter windows, not announcement years.
p = read("data/processed/reverse_dcf/C/C_print_panel.csv")
for label, s in [
    ("W1", p[p.print_quarter >= "2023Q1"]),
    ("W2", p[p.print_quarter >= "2024Q1"]),
]:
    for sign, group in s.groupby("nights_accel_sign"):
        v = group.ret_1d_cc_excess_pct
        print("Reaction", label, sign, "n", len(v), "mean", v.mean(),
              "positive", int((v > 0).sum()))
s = read("data/processed/reverse_dcf/E/E_street_sign_history.csv")
s = s[s.day1_excess_pct.notna() & s.street_positioned_for.eq("acceleration")]
print("Accelerating Street bars:",
      s[["print", "day1_excess_pct"]].to_dict("records"),
      "mean", s.day1_excess_pct.mean())
hist = p.set_index("label").nights_yoy_pct
for year in [22, 23, 25]:
    print("Accelerating Q3 to Q4:", year,
          hist[f"3Q{year}"], hist[f"4Q{year}"])

# Keep original dollar shocks to isolate the impact accounting errors.
annual = read("data/processed/margin_build/23_final_model/23_forecast_annual.csv")
annual = annual[annual.scenario.eq("base")].set_index("period")
impact = pd.read_csv(A / "datasets/a09_impact.csv")
for r in impact.itertuples():
    fixed = {}
    for year, dr in [
        ("FY26", r.rev_3q26_musd+r.rev_4q26_musd),
        ("FY27", r.rev_fy27_musd),
    ]:
        revenue = annual.loc[year, "revenue_musd"]
        ebitda = annual.loc[year, "adj_ebitda_musd"]
        fixed[year] = 100*((ebitda+dr)/(revenue+dr)-ebitda/revenue)
    published_p = {"R01": .42, "R02": .32, "R03": .07}[r.question]
    print("Impact", r.question, "held-cost margin changes", fixed,
          "held-cost EPS27", r.rev_fy27_musd*.0014,
          "EV from displayed p/stock",
          published_p*r.stock_usd_per_share_vs_base_case)
print("S01 mean of chosen cells:",
      (.08*5+.17*1.8+.08*(-2.9)+.04*.2)/.37)
print("S01 omitted 10.00-10.09 mass:",
      N.cdf((10.09-9.55)/1.48)-N.cdf((10-9.55)/1.48))

# Auditor benchmarks: one repo-nowcast location/scale, no market weight.
t1, t2 = [(m/133.6-1)*100 for m in [147, 147.8]]
print("Auditor normal probabilities:",
      tail(9.5, 1.7, t1), tail(9.5, 1.7, t2))
for sd in [1.0, 1.48, 1.633596, 1.7, 1.815866, 2.159143, 2.5]:
    print("Auditor sd sensitivity:", sd,
          tail(9.5, sd, t1), tail(9.5, sd, t2))

# Rebuild C06-v2 share draws, then a weak common-cause sensitivity.
# Share priors and k are assumptions, not measured causal coefficients.
rng = random.Random(7)
xs, high = [], []
while len(xs) < 200000:
    s1, step = rng.uniform(19, 21), rng.uniform(.5, 3.5)
    s2 = s1 + step
    if not 20.5 <= s2 <= 23.5:
        continue
    ramp = rng.uniform(0, .5)*step
    exp_mean = 1.4 if rng.random() < .75 else 3.5
    x = min(8, rng.expovariate(1/exp_mean))
    share = s2 + ramp + x + rng.uniform(-1, 1)
    xs.append(x)
    high.append(share >= 24.5)
print("C06-v2 true high share / disclosed-a:",
      mean(high), mean(high)*.75*.85)
for k in [0, .1, .2/1.4, .3/1.4]:
    sigma = math.sqrt(1.7**2-k*k*pstdev(xs)**2)
    ex = mean(xs)
    conditional = [tail(9.5+k*(x-ex), sigma, t1) for x in xs]
    p_given_a = sum(v for v, h in zip(conditional, high) if h)/sum(high)
    print("Auditor joint sensitivity k", k,
          "nights marginal", mean(conditional),
          "P(R01|a)", p_given_a,
          "joint at current C06", pa*p_given_a)
```