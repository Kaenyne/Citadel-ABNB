C01 verdict: **Revise before memo use; 75% reproduces, but is not defensible as documented.**  
Arithmetic: the saved model gives **74.6094%**, with all seven reported percentiles reproduced.  
First correction: distinguish **no revenue guidance** from growth-only guidance, which remains resolvable.  
Next corrections: exclude the unusable consensus vintage, repair the mixture description, and justify the probability adjustments.  
Independent comparison: **62% Yes**, with a conditional guide median near **$3,125M**.

Audit scope: read-only review of revision 1 and its saved evidence. Yahoo’s live fetch returned HTTP 429; the Kalshi fetch was blocked. Market verification therefore uses the timestamped snapshots, not independently refreshed quotes. No prohibited directories were opened. The model was imported with bytecode writing disabled; its file-writing main routine was not executed.

Below, `log`, `model`, and `forecast` mean `research-log.md`, `datasets/c01_model.py`, and `forecasts/2026-09-17-forecast.json` under `docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/`.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A01-01 | C01 | critical | `log:97,112,126`; `forecast.continuous.p_no_dollar_guide` | Growth-only guidance is grouped with “No,” and the output defines the excluded event as **no dollar guide**. C01 excludes only **no revenue guidance**; growth-only guidance must be converted using $2,778M. The pre-mortem later treats growth-only guidance differently. | Compared these fields with `QUESTIONS.md` C01 and `log:22,147`; inspected the model’s single `given` gate and universal $5M rounding. | Separate dollar guidance, growth-only guidance, and no revenue guidance. Convert growth-only endpoints before comparison. If the 1% was intended solely for no revenue guidance, correct the labels and explicitly allocate growth-only probability; a numerical change is not automatically required. |
| A01-02 | C01 | major | `log:33,103`; `model:131–146` | Historical base rates knowingly include `PG-2024Q3-revenue`, which the register excludes from **every PIT use**. Disclosure of the flag does not make inclusion valid. “LSEG era” also differs from a vendor-filtered LSEG-family sample. | Joined the reaction panel’s next-quarter target to the L0 register and recomputed gaps from midpoint/value. Excluding the unusable row gives **7/18**, not 8/19; LSEG-era **5/11**, not 6/12; nights-lower **4/8**, not 5/9. LSEG-era mean/SD become **+0.492% / 1.847pp**. | Apply the register gate before counting. Report LSEG/Refinitiv-only **7/15** separately. W1 eligible targets give **6/13**; W2 **4/9**. November remains **3/4**. Label morning-of-print observations as historical proxies for C01’s previous-close convention. |
| A01-03 | C01 | major | `log:90,104,108`; `model:32–36` | The explanation attributes the move from B2 almost entirely to GBV and cushion. Material additional choices are a **−0.5% residual mean**, narrower residual SD, and different fees. Thus “0.80 on the nowcast alone” is false. | Sequential reruns at the same Street threshold: B2-like no-fee inputs **0.4973** → team GBV only **0.6864** → cushion 2.4% **0.7396** → fee mixture **0.7000** → residual mean −0.5% **0.7480** → residual SD 2.0% **0.8003**. Attribution is order-dependent, but the omitted choices clearly matter. | Publish the full bridge. Treat the residual adjustment, SD reduction, seasonal cushion blend, and their dependence as explicit judgments requiring validation. The cited leakage scenarios do not estimate a −0.5% residual mean. |
| A01-04 | C01 | major | `log:46,105–108`; `datasets/kalshi_q3_nights_implied.csv` | “Volume not returned” results from reading the wrong API field. The anchor also lacks a meaningful liquidity assessment. Retrieval time alone does not establish when the information in quotes changed. | The saved API includes `volume_fp`, `volume_24h_fp`, and quote sizes. Across seven strikes: total volume **3,237.21 contracts**, 24-hour volume **0**. At 148M, bid/ask sizes are **3 / 200** contracts; all `updated_time` fields show **2026-08-04**. That metadata alone does not prove quote staleness. | Correct the parser and ledger. Distinguish capture time, metadata update time, trading activity, and executable size. Justify the market route’s 25% weight in light of these limitations. |
| A01-05 | C01 | major | `log:105`; `model:92,116` | The “Kalshi-implied” GBV normal matches approximately the median but does not preserve the market’s distribution. Its $600M SD is not derived from the ladder or an ADR uncertainty model. | Linear interpolation reproduces median **148.270M** and P(>147M) **0.585**. The ladder assigns **4.5%** below/equal 138M and **34%** above 150M. Holding the stated ADR fixed, `N(26260,600)` implies only **0.122%** below 138M. | Construct a ladder-consistent nights distribution, retain explicit tail masses, and convolve with documented ADR uncertainty. Alternatively rename this a judgmental median-matched scenario. Keep `NOT_INDEPENDENTLY_DERIVED`: the kernel and cushion remain shared. |
| A01-06 | C01 | major | `log:112,130`; `forecast.model.final_mixture` | The structural component is described as 0.722, but the implemented component is different. The displayed weighted arithmetic is wrong. | Replayed `model:116–123`: component probabilities are **0.8011275 / 0.6826175 / 0.6317550**, yielding **0.746094125**. The displayed `0.60×0.800 + 0.25×0.683 + 0.15×0.722` equals **0.75905**. Structural-component mean/SD are **$3,121.48M / $109.48M**, not approximately $3,105M/$105M. | Correct the component probability and suggested distribution settings. The saved headline and percentile table already match the implemented mixture; this finding alone does not require changing them. |
| A01-07 | C01 | major | `log:135–159`; `forecast.sensitivity`, `forecast.monitoring` | Sensitivities describe the 80% component, while machine-readable fields and monitoring instructions present them as changes to the 75% final forecast. “Moves proportionally” does not specify a valid update rule. | Applying shared changes to all three components gives: Street +1% **0.83968**, −1% **0.62573**; full primitive fee **0.66388**, no fee **0.78813**; trailing-eight cushion throughout **0.69333**. These differ materially from the displayed component values. | Store both component and final-mixture sensitivities. Specify which branches each update changes and rerun accordingly. For full-fee certainty, the final change is approximately **−8.2 points**, not the monitoring table’s −4 points. |
| A01-08 | C01 | major | `log:41,90,108` | The load-bearing reviews-index skill claim omits the later vintage audit. The mandated nowcast can remain an input, but its old backtest cannot be presented without the correction. | Read `05_backtests/WPK_reviews-index-2023-vintage.md:105–110,158` and `data/processed/q3nowcast_v2/E/t1_fail_e5_rerun.csv`: original ratio **0.683209**; fresh-vintage alternatives **0.756595** and **0.841012**, each W2-scored n=10. | Attach the revintaging caveat and reconsider how strongly the performance claim supports model weighting/error width. The later note explicitly leaves the current vintage-matched nowcast band unchanged. |
| A01-09 | C01 | major | `log:153`; `forecast.monitoring` weekly event | The monitoring instruction calls DoltHub/yfinance a capture of the **LSEG-family** mean. DoltHub is the Zacks-mirror proxy identified elsewhere in this same log; it cannot replace the resolution series. | Read the named DoltHub sample, L0 vendor fields, and claims 14–15. Current values differ: DoltHub/Zacks **$3,200M** versus saved Yahoo/LSEG **$3,161.02149M**. | Separate vendor-specific monitors. Use DoltHub only for the explicitly labeled proxy/sensitivity; use LSEG-family evidence for the resolution threshold. |
| A01-10 | C01 | minor | `log:45,96` | Drift arithmetic reproduces, but “last Sunday before each print” is not always the endpoint. The series measures weekly, rounded Zacks-mirror changes, not changes through the last trading-day LSEG close. | Rebuilt all 20 observations from the named source: mean **−0.154910%**, SD **0.610397pp**; 2023+ n=15 mean **+0.013020%**, SD **0.461509pp**. For the 2024-08-06 print, the last available observation is **2024-07-28**, nine days earlier. | Describe the rule as “last available observation before the print,” report endpoint ages, and retain vendor/rounding caveats when using 0.6% as forward LSEG drift uncertainty. |
| A01-11 | C01 | minor | `log:50,128` | The FY revenue floor is a **realized revenue** requirement, not a hard floor on the Q4 guide. “Not binding on any plausible guide” and “below every FY26 arithmetic” overstate the constraint. | `12,241×1.15−2,678−3,608−4,800 = $2,991.15M` required Q4 revenue. At a 2.4% cushion, the corresponding guide is **$2,921.04M**. | Distinguish guide and realized revenue. Test the FY sentence jointly with the Q3 print and expected Q4 cushion; do not use $2,991M as a guide boundary. |
| A01-12 | C01 | minor | `log:126–132` | The floor check covers only $2,950–3,275M inside a declared $2,900–3,400M range. The claimed necessary conditions for the upper tail are not necessary under the model. | Reproduced conditional tail masses **0.80625% below $2,900M** and **0.113% above $3,400M**. A $26.3bn GBV input, +7% residual, full primitive fee, and 1% cushion already produce approximately **$3,427M**—without $27.5bn GBV or zero cushion. | Audit the entire stated range and give scenario-based justification for thin tails. Label the continuous distribution as conditional on resolvable revenue guidance. Reproduction verifies these tail probabilities under the assumptions, not their calibration. |
| A01-13 | C01 | minor | `log:51` | The cited Bloomberg-derived CSV does not contain the stated 148.9M Q3 nights mean. | `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv`, `quarter=3Q26`, `metric=nights_m`: `street_mean=149.00`, `n_estimates=28`. Its Q4 revenue row does contain **$3,157M**, n=37. | Quote **149.0M** from this file, or identify a separate timestamped source for 148.9M. |

## C01 — what the log does well and should keep

The raw-consensus headline and cushion-subtracted companion are clearly distinguished. The Yahoo snapshot supports **$3,161.02149M, 36 analysts**, captured at the stated time. Preserve the separate vendor sensitivities and the explicit admission that the Kalshi-derived anchor shares the model’s assumptions.

The following source checks passed:

- `02_guidance_ledger.csv`: **20** dollar ranges, **19/19** realized midpoint beats, **15/19** above the upper endpoint. Trailing-eight cushion mean/median/SD: **1.856743% / 1.790491% / 1.004800pp**. Recent Q4 cushions: **3.162791%, 2.691511%, 3.271375%**, mean **3.041893%**, n=3. Cushion trend: **−0.123352pp/print**, p≈**0.05485**.
- `kernel_lambda/01_lambda_table.csv`: recomputed Q4 conversion mean **12.029793%**, range **0.171124pp**, n=3. `h2_bridge_v3/h2_bridge_revenue_dollars.csv` contains Q4 revenue **$3,178.10785M** and implied guide **$3,059.40301M**, using its stated 3.88% cushion.
- Individual `guidance_policy/07b_backtest_guide_mid_rows.csv` rows reproduce the published G4 comparisons: **7/14 W1** and **4/10 W2** model wins. W1 model/Street MAE is **1.9861% / 1.9661%**. These are checks of the published backtest, separate from the corrected C01 reference-class counts.
- Saved shareholder letters support the quoted historical guidance and 2Q26 outlook. The saved 2Q26 10-Q supports the higher-cancellation and timing-correlation statements. Preserve their distinction from estimated RNPL leakage.
- The implemented mixture weights sum to one; the percentile table is monotone. The headline binary does not trigger the extreme-probability gate. C01 has no R/B impact requirement or separate cross-question inequality in this batch.

The strongest opposing case is already partly present: the model has no established historical guide-sign advantage, management can observe October activity, and a modest positive recognition residual or smaller cushion can absorb the roughly $60M gap between the final guide mean and current Street. Keep this argument prominent.

The query sequence begins broadly and includes a recency pass; I do not find a demonstrated confirmation-shaped search problem. Snippet-only recent news is explicitly marked non-load-bearing and should remain so. The more consequential confirmation risk is the selection of favorable model adjustments.

## C01 — independent comparison forecast

**P(Yes): 0.62.** Subjective 80% uncertainty interval: **0.50–0.80**; this interval is judgmental, not a fitted posterior.  
**Cushion-subtracted companion: approximately 0.41.**

| Percentile | Guide midpoint, USD M |
|---|---:|
| 5 | 2,955 |
| 10 | 2,995 |
| 25 | 3,055 |
| 50 | 3,125 |
| 75 | 3,195 |
| 90 | 3,260 |
| 95 | 3,295 |

Derivation: retain the mandated team inputs, giving GBV **$25,885.28M**; apply the published Q4 kernel, B2’s half-fee step and trailing-eight cushion, giving guide mean **$3,126.17M**.  
Use the published **3.030509%** conditional guide-error scale plus $500M GBV uncertainty: guide SD **$102.68M**; combine with 0.6% Street drift and a judgmental 1% chance of **no revenue guidance**, yielding **0.62441**.

This is an independently constructed analytic comparison using shared repository inputs, not independent empirical corroboration. The conditional normal approximation assigns **1.38% below $2,900M** and **0.383% above $3,400M**; no-guidance probability is separate. Percentiles above are rounded to $5M. Growth-only guidance remains eligible after conversion. The normal approximation’s negative-revenue mass is negligible because zero is over 30 SD below its center.

## Reproduction script

Run from the repository root with `python -B docs/pitch-forecasts/audits/A01-reproduce.py`. The script uses only stdlib and pandas, writes nothing, and recomputes the checked base rates from source files. The original NumPy simulation was separately replayed during the audit; this script identifies its saved outputs without claiming to rerun that simulation.

```python
from pathlib import Path
from statistics import NormalDist
import json
import math
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions/q4-revenue-guide-vs-street"


def read(path):
    return pd.read_csv(ROOT / path, comment="#")


def true(series):
    return series.astype(str).str.lower().eq("true")


def rate(label, frame, col="gap"):
    s = frame[col].dropna()
    k, n = int((s < 0).sum()), len(s)
    print(label, dict(
        n=n, below=k, rate=k/n if n else None,
        laplace=(k+1)/(n+2), mean=s.mean(), sd=s.std()
    ))


def target(s):
    return "20" + s[2:] + "Q" + s[0]


ledger = read("data/processed/overnight/02_guidance_ledger.csv")
g = ledger[
    (ledger.metric == "revenue_usd_m") &
    (ledger.guide_type == "range")
].copy().sort_values("print_date")
g["period"] = g.target_period.map(target)
g["cushion_pct"] = 100 * (g.actual / g.value_mid - 1)
done = g.dropna(subset=["actual"])

print("Dollar ranges:", len(g), "realized:", len(done),
      "midpoint beats:", int((done.actual > done.value_mid).sum()),
      "top beats:", int((done.actual > done.value_high).sum()))
print("Trailing eight:",
      done.tail(8).cushion_pct.agg(["mean", "median", "std"]).to_dict())
print("All Q4:",
      done[done.period.str.endswith("Q4")].cushion_pct
      .agg(["count", "mean", "std"]).to_dict())
recent = done[done.period >= "2023Q1"].copy()
recent["season"] = recent.period.str[-2:]
print(recent.groupby("season").cushion_pct
      .agg(["count", "mean", "std"]).to_string())

# Cushion trend; numerical Student-t integration for a two-sided p-value.
y = done.cushion_pct.tolist()
n = len(y)
xm, ym = (n-1)/2, sum(y)/n
sxx = sum((x-xm)**2 for x in range(n))
slope = sum((x-xm)*(v-ym) for x, v in enumerate(y))/sxx
sse = sum((v-ym-slope*(x-xm))**2 for x, v in enumerate(y))
df = n-2
t = abs(slope / math.sqrt(sse/df/sxx))
h = t/10000


def tpdf(x):
    return (
        math.gamma((df+1)/2) /
        (math.sqrt(df*math.pi)*math.gamma(df/2)) *
        (1+x*x/df)**(-(df+1)/2)
    )


area = h/3 * (
    tpdf(0) + tpdf(t) +
    sum((4 if i % 2 else 2)*tpdf(i*h) for i in range(1, 10000))
)
print("Cushion trend:", slope, "pp/print; p =", 1-2*area)

# Match each print to the quarter being guided.
panel = read("data/processed/abnb_guidance_reaction_panel.csv")
panel["period"] = (
    pd.PeriodIndex(panel.print_quarter, freq="Q").shift(1).astype(str)
)
reg = read("data/processed/forecast_methods/L0/L0_vintage_register.csv")
pg = reg[(reg.role == "pre_guide") & (reg.metric == "revenue")]
p = panel.merge(pg, on="period", validate="one_to_one")
p["gap"] = 100*(p.nq_rev_guide_mid/p.value-1)
ok = p[true(p.pit_usable)].copy()

rate("Panel as used", panel, "guide_vs_street_pct")
rate("PIT-eligible all vendors", ok)
rate("PIT LSEG-era", ok[ok.print_date >= "2023-11-01"])
rate("PIT LSEG/Refinitiv only",
     ok[ok.vendor.isin(["LSEG", "Refinitiv"])])
rate("PIT November", ok[ok.print_date.str[5:7] == "11"])
rate("PIT nights lower",
     ok[(ok.nq_nights_dir == -1) | (ok.nq_nights_guide_pts < -1)])
rate("PIT nights higher",
     ok[(ok.nq_nights_dir == 1) | (ok.nq_nights_guide_pts > .5)])
rate("PIT last four", ok.sort_values("print_date").tail(4))
rate("PIT five-print run",
     ok[(ok.print_date >= "2024-05-01") &
        (ok.print_date <= "2025-08-01")])
for label, start in [("W1", "2023Q1"), ("W2", "2024Q1")]:
    rate(label, ok[(ok.period >= start) & (ok.period <= "2026Q2")])
print("Excluded:", p[~true(p.pit_usable)][
    ["register_id", "period", "value", "as_of_timestamp"]
].to_string(index=False))

# Select early/late observations independently from the source history.
d = read(
    "data/processed/github_altdata/samples/"
    "dolthub-post-no-preference-earnings-consensus-vintages/"
    "sales_estimate_ABNB_BKNG_EXPE.csv"
)
d = d[(d.act_symbol == "ABNB") & (d.period == "Next Quarter")].copy()
d["date"] = pd.to_datetime(d.date)
rows = []
for row in g.itertuples():
    dt = pd.Timestamp(row.print_date)
    end = pd.Period(row.period, freq="Q").end_time.strftime("%Y-%m-%d")
    v = d[d.period_end_date == end].sort_values("date")
    early = v[v.date <= dt-pd.Timedelta(days=50)]
    late = v[v.date < dt]
    if early.empty or late.empty:
        continue
    a, b = early.iloc[-1], late.iloc[-1]
    rows.append(dict(
        print_date=row.print_date,
        early_date=a.date.strftime("%Y-%m-%d"),
        late_date=b.date.strftime("%Y-%m-%d"),
        drift_pct=100*(b.consensus/a.consensus-1),
        late_age_days=(dt-b.date).days
    ))

drift = pd.DataFrame(rows)
for label, sub in [
    ("All", drift),
    ("2023+", drift[drift.print_date >= "2023-01-01"])
]:
    print("DoltHub", label,
          sub.drift_pct.agg(["count", "mean", "median", "std"]).to_dict())
print("November drift:",
      drift[drift.print_date.str[5:7] == "11"].to_string(index=False))
print("Stale endpoint:",
      drift[drift.print_date == "2024-08-06"].to_string(index=False))
saved = pd.read_csv(Q / "datasets/street_drift_dolthub.csv")
check = drift.merge(saved, on="print_date", suffixes=("_new", "_saved"))
assert len(check) == 20
assert (check.drift_pct_new-check.drift_pct_saved).abs().max() < 1e-10

# Published G4 comparison: recompute from individual forecast rows.
bt = read(
    "data/processed/forecast_methods/guidance_policy/"
    "07b_backtest_guide_mid_rows.csv"
)
bt = bt.merge(
    g[["period", "value_mid"]], left_on="quarter", right_on="period"
)
for w in ["W1", "W2"]:
    v = bt[(bt.prior_basis == "PIT") & (bt.window == w)]
    me = 100*(v.point/v.value_mid-1)
    se = 100*(v.base_street/v.value_mid-1)
    print("Published G4", w, "n", len(v),
          "wins", int((me.abs() < se.abs()).sum()),
          "MAE", me.abs().mean(), se.abs().mean(),
          "bias", me.mean(), se.mean())

k = read("data/processed/forecast_methods/kernel_lambda/01_lambda_table.csv")
k = k[(k.season == 4) & (k.q >= "2023Q1")]
lam = k.revenue_musd/(k.gbv_l1*2/3+k.gbv_l2/3)
print("Q4 lambdas %:", list(100*lam),
      "mean", 100*lam.mean(),
      "range pp", 100*(lam.max()-lam.min()))

# Parse actual API field names.
market = json.loads((
    Q / "sources/kalshi_markets_KXABNB_open_20260917T025304Z.json"
).read_text(encoding="utf-8"))
km = pd.DataFrame(market["markets"])
for c in [
    "floor_strike", "yes_bid_dollars", "yes_ask_dollars",
    "volume_fp", "volume_24h_fp"
]:
    km[c] = pd.to_numeric(km[c])
km = km.sort_values("floor_strike")
km["mid"] = (km.yes_bid_dollars+km.yes_ask_dollars)/2
print(km[[
    "floor_strike", "mid", "volume_fp", "volume_24h_fp", "updated_time"
]].to_string(index=False))
print("Volumes:", km.volume_fp.sum(), km.volume_24h_fp.sum())
prices = dict(zip(km.floor_strike/1e6, km.mid))
median = 148+2*(prices[148]-.5)/(prices[148]-prices[150])
print("Interpolated median nights:", median,
      "P(>147):", (prices[146]+prices[148])/2)

print("Stated mixture arithmetic:", .60*.800+.25*.683+.15*.722)
print("Saved mixture:", pd.read_csv(
    Q / "datasets/c01_final_mixture.csv", index_col=0
).value.to_dict())

# Auditor comparison: normal approximation, not fitted calibration.
inputs = read(
    "data/processed/forecast_methods/guidance_policy_v2/01_inputs.csv"
).set_index("input").value
snap = pd.read_csv(
    Q / "sources/yfinance_revenue_estimate_20260917T025239Z.csv"
).set_index("period")
street = float(snap.loc["+1q", "avg"])/1e6
gbv = 133.6*1.095*171.29*1.033
c = inputs["cushion_mean_pct"]/100
a = inputs["lambda_Q4_pct"]/100
fee = .005543
mu = a*(2*gbv/3+27200/3)*(1+fee)/(1+c)
sd = math.hypot(
    mu*inputs["sd_guide_mid_pp_CHOSEN"]/100,
    a*(2/3)*500*(1+fee)/(1+c)
)
dist = NormalDist(mu, sd)
p_yes = .99*NormalDist().cdf(
    (street-mu)/math.hypot(sd, .006*street)
)
print("Auditor GBV, guide mean, SD, P(Yes):", gbv, mu, sd, p_yes)
print("Percentiles:", {
    q: dist.inv_cdf(q/100) for q in [5, 10, 25, 50, 75, 90, 95]
})
print("Bounds mass:", dist.cdf(2900), 1-dist.cdf(3400))
p_surprise = .99*NormalDist().cdf(
    (street*(1-c)-mu)/math.hypot(sd, .006*street*(1-c))
)
print("Auditor cushion-subtracted comparison:", p_surprise)
```