**S01 verdict: revise before using the forecast in the pitch.**  
**Object:** the headline forecasts the correct unconditional, raw close-to-close return; the stated base-case conditional omits a required gate in code.  
**Reproduction:** the −2.9% median, threshold probabilities, conditional table and sensitivity outputs reproduce exactly.  
**First required change:** construct one joint distribution over print sign, C01, C02 and return, then derive both unconditional and conditional outputs from it.  
**Assessment:** modest unconditional downside is defensible as judgment; the claimed 50% base-case probability and 87% conditional probability of a decline are not established as written.

Audit date: 2026-09-17. Repository unchanged; neither prohibited raw directory was opened. I replayed the supplied calculations in memory after removing their output-writing statements. `py -3.13` was inaccessible and the available `python` lacked SciPy; replacing the options calculation’s normal CDF and root solver with standard-library equivalents reproduced its saved term structure to numerical precision. Market evidence below is from the saved snapshots. The Federal Reserve calendar was separately fetched successfully.

References below use:

- **Q** = `docs/pitch-forecasts/questions/day1-move-5nov/`
- **log** = `Q/research-log.md`
- **code** = `Q/datasets/s01_mixture.py`
- **forecast** = `Q/forecasts/2026-09-17-forecast.json`
- **C panel** = `data/processed/reverse_dcf/C/C_print_panel.csv`

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A06-01 | S01 | critical | log:28,118; code:154–156; forecast `conditional_base_case` | The stated base case requires **deceleration AND guide below Street AND C02(c or d)**. The simulation conditions only on the first two. No C02 outcome is generated. Historical `guide_dir_code <= 0` is also not the same event as the specified C02 labels. | The mask is `(sign == -1) & (gap < 0)`. Its probability reproduces as 0.503. C02 is absent from the executable model. With revision-1 C02(c+d)=0.56, these marginals alone permit triple-intersection probability anywhere from approximately **0.063 to 0.503**. | Generate the C02 outcome jointly and apply all three gates. Do not label 0.503 as the triple-intersection probability without an explicit dependence assumption. |
| A06-02 | S01 | major | code:134,154–167; log:128,130,132,162 | The conditional tables are separate forecasts, not conditionals derived from the published final mixture. The final uses 50% decomposition/25% historical/25% options; the base case switches to 70% decomposition/30% selected historical cell, and the breaker uses decomposition alone. No joint model or posterior weight update explains these changes. | The six saved cell probabilities and conditional means recombine to approximately **−4.68%**, the decomposition mean, not the final **−2.69%**. If the historical/options components retain their prior weights and are independent of the cell, the two-gate conditional gives **P(return≤−8)=0.380, P(return<0)=0.711**, rather than 0.532/0.869. This is an illustrative coherent construction, not the uniquely correct repair. | Specify scenario likelihoods for every component or construct the complete joint distribution directly. Recompute all conditionals from that distribution. |
| A06-03 | S01 | major | code:104–110; log:95–98; forecast `estimates.anchor` | Only the options **width** is market-derived. The negative location is imposed by an uncalibrated split-normal construction, yet called risk-neutral and directionless. A −3.5-point risk reversal does not itself establish this day-1 distribution. | With downside scale 9.9, upside 8.1 and mode −0.3, the analytic mean is **−1.736%**; the replay produces median −1.47%, mean −1.76%, P(down)=0.565. No fitted mapping from the saved smile to the 1.10 multiplier is provided. Replacing only this anchor with N(0,9²) moves the final median to **−2.53%**, P(≤−8) to **0.280** and P(≥+5) to **0.213**. | Call the shape/location a judgmental transformation, or fit an event distribution with a stated carry constraint. Extend `NOT_INDEPENDENTLY_DERIVED` beyond width. Keep the neutral-anchor sensitivity. |
| A06-04 | S01 | major | log:42–44,132; forecast `print_state_probabilities` | The cross-question integration is now stale. S01 explicitly uses C01/C02 revision 1, whereas their current files are revision 2. This is a dependency-update requirement, not evidence that S01 misread the original versions. | Current C01 is **0.72**, guide SD **$97M**; S01 uses 0.75/$87M. Current C02 vector is **0.18/0.17/0.30/0.31/0.04**, with a different print-distribution convention. S01 still states 0.21/0.19/0.39/0.17/0.04 and common print-distribution coherence. | Pin dependency revisions, reconcile the print distribution explicitly, and rerun before X01 consumes S01. Preserve the mandated team-nowcast input unless the response explains the adopted change. |
| A06-05 | S01 | major | log:37; forecast `conditional_base_case.panel_cell` | The explanation of the brief’s **n=5, mean −8.0%** statistic silently mixes two nights-guide coding schemes. Under the cited C panel, adding the two accelerating prints to the strict n=3 cell is incomplete: 4Q24 also qualifies. | Legacy `abnb_guidance_reaction_panel.csv` gives n=5, mean **−8.00%**, median **−10.90%**. The C panel recodes 4Q24 as a decelerating guide, giving **n=6, mean −4.27%, median −7.10%** for below-Street guide plus lower nights direction. The strict decelerating-print intersection remains n=3, mean −7.77%. | Report both coding conventions and explain 4Q24’s inclusion. Use one convention throughout the conditional evidence. |
| A06-06 | S01 | major | log:35–36,94; code:61–63 | The reaction model omits the required W2 check. Its two fitted windows are n=16 ex-reopening and W1 n=14; they are not W1/W2. The missing check matters particularly for the guide coefficient. | Refit on W2, 1Q24–2Q26, n=10: S1 sign coefficient **7.285**, residual SD **6.699**, LOO R² **0.458**. S2 guide coefficient falls to **0.644**, residual SD rises to **6.986**, and LOO R² falls to **0.271**. W1 S2 guide coefficient is 1.322; the implemented blended coefficient is 1.69. | Publish W2 alongside W1. The sign association persists; incremental guide-term usefulness does not survive this comparison. Reconsider its 40% weight rather than claiming both-window support. |
| A06-07 | S01 | major | log:134,151 | The tail comparison materially understates the generated forecast’s extreme-move frequency. The claim that its ≥15% frequency lies between history and the implied normal is false. | Exact replay: **P(abs(return)≥15)=0.12552**, not approximately 0.06. History is **1/23=0.04348**; the cited 9.5%-SD normal is approximately 0.114. Also **P(return<−25)=0.00933** unconditional and **0.01660** in the reported base-case distribution, not the stated 0.006. | Replace the prose with computed tail probabilities. Explicitly describe the forecast as having a heavier ≥15% tail than both quoted comparators. |
| A06-08 | S01 | major | log:136 | The extreme-tail justification uses the full panel’s n=16 even though only four observations clear the claimed deceleration-plus-guide-below gates. Zero successes in that small cell is weak evidence for a 1.1% upper-tail probability. | Eligible observations are 1Q23, 1Q24, 2Q24 and 1Q25: **0/4** returned ≥10%. Requiring lower nights-guide direction leaves **0/3**. For context, the one-sided 95% binomial upper bound for 0/4 is **52.7%**; this is an uncertainty diagnostic, not a proposed forecast. | Correct the denominator and label 1.1% as a model-tail judgment. Include model/cell uncertainty rather than presenting absence of precedent as substantial validation. |
| A06-09 | S01 | minor | log:92–98; forecast `estimates.independence_note` | The historical estimate and decomposition reuse the same earnings observations. Their agreement is not independent empirical corroboration. The options component also acquires a discretionary directional shift. | Both historical components read `abnb_earnings_reactions.csv` directly or through the C panel; S1/S2 are fitted on overlapping subsets of those observations. | Describe these as dependent model specifications with judgmental weights. Keep the independent public-options width check separate. |
| A06-10 | S01 | minor | log:51 | “Volume and open interest fields None … zero liquidity” overlooks the API’s fixed-point fields. The saved market was thin and inactive over 24 hours, but not untraded or devoid of quoted size. | Saved KXABNB snapshot: summed `volume_fp` **3,237.21**, `open_interest_fp` **2,178.46**, `volume_24h_fp` zero; positive bid/ask sizes exist. `liquidity_dollars` is zero, a separate field. | Correct the field names and characterization. This does not require assigning the market substantial forecast weight. |
| A06-11 | S01 | minor | log:48,85 | “Six of eleven” negative large earnings moves on beats does not match the reaction file. The causal claim that every large move followed nights guidance/lead-time language is also stronger than the cited event descriptions. | The reaction CSV has **11** ≥7% absolute moves, **5 negative**. By reaction dates since 2023 there are **7**, **4 negative**. The C panel records EPS misses for 2Q24 and 3Q24; the event note identifies expense growth/EPS disappointment for 3Q24. | Replace the count and distinguish revenue beats from EPS beats. Treat retrospective catalyst labels as descriptions, not proof that other information cannot matter. |
| A06-12 | S01 | minor | log:47 | 4Q24 is incorrectly presented as a decelerating Street bar followed by an accelerating print. The cited note contains the same internal contradiction. | `data/processed/reverse_dcf/E/E_street_sign_history.csv` labels 4Q24 **Street acceleration / actual acceleration**. 2Q26 and 4Q25 are the cited decelerating-bar examples that do match. | Remove 4Q24 from that example set. Retain the separate, supported statement that no observed accelerating-bar/decelerating-print case exists in the scored history. |
| A06-13 | S01 | minor | log:42–43; code:60,84 | The stated guide sensitivity is twice the implemented sensitivity. | At Street $3,161M, 0.32 percentage points of guide gap per one point of nights means **$5.06M per +0.5 point**, not $10M. $10M requires approximately **0.633** as the slope. | Correct the prose or the coefficient. Current C01 revision 2 states approximately $5M, which is consistent with the existing coefficient. |
| A06-14 | S01 | minor | log:45,98,134 | The options reconciliation confuses calendar days with sessions and repeats a background-volatility argument already handled by the estimator. Its displayed variance arithmetic also fails. | 5–20 November is **15 calendar days**, **11 reaction-and-later weekdays**, or **10 sessions after 6 November**. The estimator already subtracts background variance through `E=Tpost(σpost²−σpre²)`. Also √(7.5²+2.4²+1.3²+3.5²)=**8.715**, not 9.4. | Correct the calendar count; explain residual event-identification uncertainty without deducting background variance twice. Recompute the variance decomposition, including within-cell guide-gap variation. |
| A06-15 | S01 | minor | log:111,115; code:116–124; forecast bound-mass fields | The 0.1% boundary floors and suggested sliders are not implemented by the reproduced model. Consequently the exported summaries do not describe one fully specified distribution. | Saved/replayed natural masses are approximately **0.0005 below −40** and **0.0002 above +40**; no floor-and-renormalize step exists. The proposed slider components are a different Gaussian mixture from the t-residual/historical/options construction. | Implement the added boundary mass with explicit normalization and regenerate summaries. Label sliders approximate, or supply an exact CDF representation. |
| A06-16 | S01 | minor | log:151,161; forecast `monitoring` | The calendar contains an unsupported FOMC date and calls 4 November’s close the pre-print denominator. | The [Federal Reserve calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm) schedules **27–28 October 2026**, not 4–5 November. For an after-close 5 November release, S01’s denominator is **5 November’s close**. | Correct the FOMC example. Preserve 4 November for C01’s prescribed consensus capture, but separately capture the 5 November stock close for S01 resolution. |

## What the S01 log does well and should keep

The headline object, thresholds and units are correct. Raw versus QQQ-excess returns are distinguished, the nowcast enters probabilistically, and the log discloses the reaction coefficients’ fragility and multiple-testing problem. Its search log starts neutrally and includes a recency pass; it is not predominantly confirmation-shaped. The options snapshot has a precise retrieval timestamp, saved quotes and reproducible calculations.

The following numerical foundations survive rereading and recalculation:

| Source and definition | Recomputed result |
|---|---|
| `abnb_earnings_reactions.csv`, all 23 raw reactions | Mean **+1.1565%**, RMS **8.9156%**, 13 positive; ≥7% absolute **11/23**, ≥10% **8/23** |
| C panel, ex-reopening n=16 | Mean **−0.9375%**, median **−1.10%**, sample SD **9.5834%** |
| C panel, W1 decelerating prints | **n=8**, raw mean **−4.9625%**, 2 positive raw / 0 positive excess |
| C panel, W2 decelerating prints | **n=5**, raw mean **−5.32%**, 2 positive raw / 0 positive excess |
| `overnight/02_guidance_ledger.csv`, completed one-quarter dollar revenue ranges | **19/19** above midpoint; **15/19** above top; trailing-eight midpoint cushion **1.8567%** |
| Saved options chain, Black-76/smile reconstruction | 16 Oct/20 Nov event SD **9.12%**; 30 Oct/20 Nov **7.97%**; one-print LS **8.23%**, LOO **7.85–8.51%** |
| Saved 20 Nov $170 call-plus-put quotes | Straddle midpoint **13.029% of spot**, bid **11.969%**, ask **14.089%** |
| `B_bbg_print_implied_vs_realised.csv`, processed data only | Mean implied crush SD **10.4661%**; correlation with absolute realized raw return **0.0518**, n=23 |

The strongest countercase should remain prominent: decelerating prints were positive **3/9** times on raw returns in the wider sample, including +13.4%. The strictly relevant historical cells contain only three or four observations. The evidence supports a bearish directional hypothesis much more comfortably than a precisely estimated 87% probability of a decline.

The replay verifies saved-data arithmetic, not the authenticity of every upstream vendor observation. Snippet-only current-news claims remain unverified and should retain zero quantitative weight. S01 has no R/B impact-table requirement.

## Independent S01 forecast

This is an independently constructed comparison, not a claim of independent underlying evidence.

| Percentile | Raw day-1 return |
|---|---:|
| 5 | −16.6% |
| 10 | −13.3% |
| 25 | −8.0% |
| 50 | **−2.2%** |
| 75 | +3.6% |
| 90 | +8.9% |
| 95 | +12.3% |

**P(≤−8%)=0.250; P(≤−5%)=0.373; P(≥+5%)=0.202; P(≥+10%)=0.081.** Mean −2.19%; SD 9.08%. Model mass below −40 is **0.000932**; above +40 is **0.000504**.

**Derivation, line 1:** Retain the prescribed N(9.55,1.48²) nights input; use six print-sign/guide cells and shrink each observed raw-return mean toward the n=16 overall mean using four prior-equivalent observations. Assign below-Street probabilities 0.77/0.72/0.58679 to decelerating/flat/accelerating states, matching current C01=0.72.  
**Derivation, line 2:** Within each cell use 95% N(cell mean,8²)+5% N(cell mean,18²); this judgmental tail allowance yields total SD 9.08%, near the reproduced options width, without an added positioning penalty or imposed bearish options mean.

For an explicit C02 joint structure, assign P(c or d | decelerating/flat/accelerating)=**0.80/0.50/0.15694**, matching current C02(c+d)=0.61. Assume C01 and C02 are conditionally independent given print sign, and no additional return effect from C02 after those cells. These are declared assumptions, not estimated correlations.

Under that construction the three-gate base case has probability **0.396**, conditional median **−4.24%**, P(down)=**0.697**, and P(≤−8%)=**0.324**. Its much weaker downside confidence shows what changes when small-cell evidence is shrunk and the missing gate is made explicit. The extreme boundary masses arise from the stated wide component; they are judgmental allowances, not frequencies established by 23 observations.

## Reproduction script

Run from the repository root:

```powershell
python docs/pitch-forecasts/audits/A06-reproduce.py
```

The script uses only the standard library and pandas. It reads files, prints results, and performs no network requests or writes. It recomputes the historical rates, window regressions, source discrepancies, exact historical-kernel estimate, options pair arithmetic and independent comparison distribution. The full supplied Monte Carlo and smile-fit replays were performed separately as described above.

```python
from pathlib import Path
from statistics import NormalDist
import json
import math
import pandas as pd

ROOT = Path.cwd()
D = ROOT / "data/processed"
Q = ROOT / "docs/pitch-forecasts/questions/day1-move-5nov"
Phi = NormalDist().cdf

rx = pd.read_csv(D / "abnb_earnings_reactions.csv")
panel = pd.read_csv(D / "reverse_dcf/C/C_print_panel.csv")
ex = panel.loc[panel.sample_ex_reopening].copy()


def describe(name, frame):
    x = frame.ret_1d_cc_raw_pct
    e = frame.ret_1d_cc_excess_pct
    result = {
        "n": len(frame),
        "mean_raw": x.mean(),
        "median_raw": x.median(),
        "sd_raw_sample": x.std(ddof=1),
        "rms_raw": math.sqrt(x.pow(2).mean()),
        "positive_raw": int((x > 0).sum()),
        "positive_excess": int((e > 0).sum()),
        "abs_ge_7": int((x.abs() >= 7).sum()),
        "abs_ge_10": int((x.abs() >= 10).sum()),
        "abs_gt_15": int((x.abs() > 15).sum()),
    }
    print(name, result)


def solve(a, b):
    """Small dense linear system: pivoted Gauss-Jordan elimination."""
    m = [list(map(float, row)) + [float(v)]
         for row, v in zip(a, b)]
    n = len(b)
    for j in range(n):
        k = max(range(j, n), key=lambda i: abs(m[i][j]))
        m[j], m[k] = m[k], m[j]
        if abs(m[j][j]) < 1e-12:
            raise ValueError("Singular regression")
        scale = m[j][j]
        m[j] = [v / scale for v in m[j]]
        for i in range(n):
            if i != j:
                scale = m[i][j]
                m[i] = [v - scale * w for v, w in zip(m[i], m[j])]
    return [row[-1] for row in m]


def fit(x, y):
    k = len(x[0])
    a = [[sum(row[i] * row[j] for row in x)
          for j in range(k)] for i in range(k)]
    b = [sum(row[i] * v for row, v in zip(x, y))
         for i in range(k)]
    return solve(a, b)


def regression(frame, columns):
    x = [[1.0] + list(row)
         for row in frame[columns].itertuples(index=False, name=None)]
    y = frame.ret_1d_cc_excess_pct.tolist()
    beta = fit(x, y)
    sse = sum(
        (v - sum(a * b for a, b in zip(row, beta))) ** 2
        for row, v in zip(x, y)
    )
    loo_error = baseline_error = 0.0
    for i, v in enumerate(y):
        xx, yy = x[:i] + x[i + 1:], y[:i] + y[i + 1:]
        bb = fit(xx, yy)
        pred = sum(a * b for a, b in zip(x[i], bb))
        loo_error += (v - pred) ** 2
        baseline_error += (v - sum(yy) / len(yy)) ** 2
    return {
        "coefficients": beta,
        "residual_sd": math.sqrt(sse / (len(y) - len(beta))),
        "loo_r2": 1 - loo_error / baseline_error,
    }


def fisher_sign(frame):
    a = frame.loc[frame.nights_accel_sign == 1]
    b = frame.loc[frame.nights_accel_sign == -1]
    n1, n2 = len(a), len(b)
    observed = int((a.ret_1d_cc_excess_pct > 0).sum())
    successes = observed + int((b.ret_1d_cc_excess_pct > 0).sum())

    def mass(k):
        return (math.comb(n1, k) * math.comb(n2, successes - k)
                / math.comb(n1 + n2, successes))

    p0 = mass(observed)
    return sum(
        mass(k)
        for k in range(max(0, successes - n2), min(n1, successes) + 1)
        if mass(k) <= p0 + 1e-12
    )


describe("All prints", panel)
windows = {
    "ex_reopening": ex,
    "W1": panel.loc[panel.print_quarter >= "2023Q1"],
    "W2": panel.loc[panel.print_quarter >= "2024Q1"],
}
for name, frame in windows.items():
    describe(name, frame)
    for sign in (-1, 0, 1):
        describe(f"{name}: sign={sign}",
                 frame.loc[frame.nights_accel_sign == sign])
    below = frame.guide_vs_street_pct < 0
    decel = frame.nights_accel_sign == -1
    strict = frame.loc[below & decel & (frame.guide_dir_code < 0)]
    broad = frame.loc[below & decel & (frame.guide_dir_code <= 0)]
    describe(f"{name}: strict historical proxy", strict)
    describe(f"{name}: broad historical proxy", broad)
    for cols in (
        ["nights_accel_sign"],
        ["nights_accel_sign", "guide_vs_street_pct"],
        ["guide_vs_street_pct"],
    ):
        print(name, cols, regression(frame, cols))
    print(name, "Fisher two-sided excess positivity", fisher_sign(frame))

for sign in (-1, 0, 1):
    for below in (True, False):
        cell = ex.loc[
            (ex.nights_accel_sign == sign)
            & ((ex.guide_vs_street_pct < 0) == below)
        ]
        print("Historical cross-cell", sign, below,
              "n", len(cell),
              "mean", cell.ret_1d_cc_raw_pct.mean(),
              "labels", cell.label.tolist())

old = pd.read_csv(D / "abnb_guidance_reaction_panel.csv")
old_cell = old.loc[
    (old.guide_vs_street_pct < 0) & (old.nq_nights_dir < 0)
]
new_cell = ex.loc[
    (ex.guide_vs_street_pct < 0) & (ex.guide_dir_code < 0)
]
print("Legacy below+lower", len(old_cell),
      old_cell.ret_1d.mean(), old_cell.ret_1d.median())
print("C-panel below+lower", len(new_cell),
      new_cell.ret_1d_cc_raw_pct.mean(),
      new_cell.ret_1d_cc_raw_pct.median())

eligible = ex.loc[
    (ex.nights_accel_sign == -1) & (ex.guide_vs_street_pct < 0)
]
print("Eligible >=10% successes",
      int((eligible.ret_1d_cc_raw_pct >= 10).sum()), "/", len(eligible))
print("0/n one-sided 95% upper bound",
      1 - 0.05 ** (1 / len(eligible)))

g = pd.read_csv(D / "overnight/02_guidance_ledger.csv")
g = g.loc[
    (g.metric == "revenue_usd_m")
    & (g.horizon_quarters == 1)
    & g.actual.notna() & g.value_mid.notna()
].sort_values("print_date")
print("Revenue guides", len(g),
      "above midpoint", int((g.actual > g.value_mid).sum()),
      "above top", int((g.actual > g.value_high).sum()),
      "last8 cushion", (g.tail(8).actual / g.tail(8).value_mid - 1).mean())

big = rx.loc[rx.abnb_1d_pct.abs() >= 7]
recent = big.loc[big.reaction_date >= "2023-01-01"]
print("Large moves: all/negative", len(big),
      int((big.abnb_1d_pct < 0).sum()))
print("Large moves since 2023: all/negative", len(recent),
      int((recent.abnb_1d_pct < 0).sum()))

street = pd.read_csv(D / "reverse_dcf/E/E_street_sign_history.csv")
print("4Q24 Street classification",
      street.loc[street["print"] == "4Q24",
                 ["street_positioned_for", "printed"]].to_dict("records"))
crush = pd.read_csv(D / "reverse_dcf/B/B_bbg_print_implied_vs_realised.csv")
print("IV-crush mean/correlation",
      crush.implied_event_sd_crush_pct.mean(),
      crush.implied_event_sd_crush_pct.corr(
          crush.realised_raw_cc_1d_pct.abs()))

kalshi = json.loads(
    (Q / "sources/kalshi_markets_KXABNB_open_20260917T030925Z.json")
    .read_text(encoding="utf-8")
)
for key in ("volume_fp", "open_interest_fp", "volume_24h_fp"):
    print("Kalshi", key,
          sum(float(m.get(key) or 0) for m in kalshi["markets"]))

# Exact historical Gaussian-kernel estimate, without Monte Carlo.
weights = [2.0 if q >= "2023Q1" else 1.0 for q in rx.quarter]
weight_sum = sum(weights)


def historical_cdf(x):
    return sum(
        w * Phi((x - v) / 3)
        for w, v in zip(weights, rx.abnb_1d_pct)
    ) / weight_sum


def quantile(cdf, probability):
    lo, hi = -200.0, 200.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if cdf(mid) < probability:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


percentiles = (.05, .10, .25, .50, .75, .90, .95)
print("Historical KDE percentiles",
      [quantile(historical_cdf, p) for p in percentiles])
print("Historical KDE P<=-8 / P>=5",
      historical_cdf(-8), 1 - historical_cdf(5))

# Pair arithmetic from the independently replayed saved term structure.
ts = pd.read_csv(Q / "datasets/options_term_structure.csv").set_index("expiry")
for pre in ("2026-10-16", "2026-10-30"):
    for post in ("2026-11-20", "2026-12-18"):
        a, b = ts.loc[pre], ts.loc[post]
        variance = b["T"] * (
            (b.atm_iv_pct / 100) ** 2 - (a.atm_iv_pct / 100) ** 2
        )
        print("Options pair", pre, post, 100 * math.sqrt(max(0, variance)))

meta = json.loads(
    (Q / "sources/yfinance_abnb_chain_meta_20260917T030919Z.json")
    .read_text(encoding="utf-8")
)
chain = pd.read_csv(Q / "sources/yfinance_abnb_chain_20260917T030919Z.csv")
straddle = chain.loc[
    (chain.expiry == "2026-11-20") & (chain.strike == 170)
]
assert len(straddle) == 2
print("20Nov $170 straddle bid/mid/ask %spot",
      100 * straddle.bid.sum() / meta["spot"],
      50 * (straddle.bid.sum() + straddle.ask.sum()) / meta["spot"],
      100 * straddle.ask.sum() / meta["spot"])
print("Split-normal imposed mean",
      -.3 + math.sqrt(2 / math.pi) * (8.1 - 9.9))
print("Implemented dollars per +0.5pt nights", .0032 * .5 * 3161)
print("Log's displayed SD formula",
      math.sqrt(7.5**2 + 2.4**2 + 1.3**2 + 3.5**2))

saved = json.loads(
    (Q / "datasets/s01_components.json").read_text(encoding="utf-8")
)
print("Saved cell-weighted mean",
      sum(c["prob"] * c["mean"] for c in saved["cells_model"]))
print("Saved final mean", saved["estimates"]["FINAL_mixture"]["mean"])

# Auditor's explicit joint distribution: judgmental parameters, not a fit.
states = {
    -1: Phi((10.09 - 9.55) / 1.48),
    1: 1 - Phi((10.59 - 9.55) / 1.48),
}
states[0] = 1 - sum(states.values())
below = {-1: .77, 0: .72}
below[1] = (.72 - sum(states[s] * below[s] for s in (-1, 0))) / states[1]
cd = {-1: .80, 0: .50}
cd[1] = (.61 - sum(states[s] * cd[s] for s in (-1, 0))) / states[1]

prior = float(ex.ret_1d_cc_raw_pct.mean())
cells = []
for sign in (-1, 0, 1):
    for is_below in (True, False):
        sample = ex.loc[
            (ex.nights_accel_sign == sign)
            & ((ex.guide_vs_street_pct < 0) == is_below)
        ]
        mean = (sample.ret_1d_cc_raw_pct.sum() + 4 * prior) / (len(sample) + 4)
        weight = states[sign] * (
            below[sign] if is_below else 1 - below[sign]
        )
        cells.append((float(weight), float(mean)))


def mixture_cdf(x, components=cells):
    return sum(
        w * (.95 * Phi((x - mu) / 8) + .05 * Phi((x - mu) / 18))
        for w, mu in components
    )


assert abs(sum(w for w, _ in cells) - 1) < 1e-12
print("Auditor states/below/C02cd", states, below, cd)
print("Auditor percentiles", [quantile(mixture_cdf, p) for p in percentiles])
print("Auditor thresholds",
      mixture_cdf(-8), mixture_cdf(-5),
      1 - mixture_cdf(5), 1 - mixture_cdf(10))
mean = sum(w * mu for w, mu in cells)
variance = sum(w * (77 + mu * mu) for w, mu in cells) - mean * mean
print("Auditor mean/sd", mean, math.sqrt(variance))
print("Auditor boundary masses", mixture_cdf(-40), 1 - mixture_cdf(40))
base_components = [(1.0, cells[0][1])]
base_cdf = lambda x: mixture_cdf(x, base_components)
print("Auditor three-gate base probability",
      states[-1] * below[-1] * cd[-1])
print("Auditor base median/Pdown/P<=-8",
      quantile(base_cdf, .5), base_cdf(0), base_cdf(-8))
```