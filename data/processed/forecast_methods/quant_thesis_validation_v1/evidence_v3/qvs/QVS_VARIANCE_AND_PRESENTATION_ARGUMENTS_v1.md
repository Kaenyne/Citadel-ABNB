# Quant support — variance and presentation arguments

13 September 2026 · WP-QVS · independent agent `/root/quant_variance_support`, reviewed and saved by parent task `01a09cd6-dbfc-7fe0-b673-430fd3e309e8`. Latest agent calculation: 2026-09-13 23:57:23 UTC. Workspace branch `codex/lane2-full`; no commits or branch changes. This is new explanatory research only.

## Verdict

**The evidence supports retaining the simple kernel as a forecasting benchmark with explicit uncertainty. It does not establish exact booking-cohort conversion shares.** L3's completed test reinforces this distinction: estimating an additional lag weight failed its preregistered forecasting hurdle in both windows. The strongest presentation argument is disciplined model selection and transparent sensitivity, rather than statistical certainty about two thirds.

This support audit independently reproduced descriptive statistics, inspected accepted L3 outputs, checked accounting definitions and derived sensitivities. It ran no new inferential test, fitted no competing model, registered no forecast and changed no existing file. L3 retains model-estimation ownership; L4 retains forecast and presentation integration.

## Evidence references

- **P:** [Frozen KPI panel](<C:/Users/wille/Desktop/Citadel - ABNB/data/processed/overnight/02_kpi_panel_quarterly.csv>).
- **K1:** [Kernel weights and backlog](<C:/Users/wille/Desktop/Citadel - ABNB/docs/revenue-forecast-strategy/05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md>).
- **K2:** [Lead-time analysis](<C:/Users/wille/Desktop/Citadel - ABNB/docs/revenue-forecast-strategy/05_backtests/K2_KERNEL_FROM_LEAD_TIMES.md>).
- **C:** [Accepted L3 results](<C:/Users/wille/Desktop/Citadel - ABNB/.worktrees/lane3-full/docs/revenue-forecast-strategy/05_backtests/L3_CONVERSION_RESULTS_v1.md>) and [final closure](<C:/Users/wille/Desktop/Citadel - ABNB/.worktrees/lane3-full/docs/revenue-forecast-strategy/05_backtests/L3_CONVERSION_FINAL_CLOSURE_v1.md>). Canonical tables are in `C:/Users/wille/Desktop/Citadel - ABNB/.worktrees/lane3-full/data/processed/forecast_methods/conversion_validation_v1/results_v2/`.
- **L2:** [Current memo-ready claims](<C:/Users/wille/Desktop/Citadel - ABNB/docs/revenue-forecast-strategy/05_backtests/LANE2_MEMO_READY_CLAIMS.md>).
- **L4:** [Baseline integration closure](<C:/Users/wille/Desktop/Citadel - ABNB/.worktrees/lane4-full/docs/revenue-forecast-strategy/05_backtests/L4_CLOSE_HANDOFF_v1.md>).
- **Q:** [Parent guide-basis and decision-logic audit](<C:/Users/wille/Desktop/Citadel - ABNB/docs/revenue-forecast-strategy/05_backtests/QVS_GUIDE_BASIS_AND_DECISION_LOGIC_v1.md>).

## Five different uncertainties

Let `B = w*G1 + (1-w)*G2`, `R = lambda_s*B`, and modeled guide `Q = R/(1+c)`. G1/G2 are the previous two quarters' GBV and c is the assumed actual-to-guide cushion.

| Object | Meaning | Interpretation limit |
|---|---|---|
| Arithmetic contribution `a = w*G1/B` | Fraction of modeled revenue attributed to the first lag | Changes with GBV proportions conditional on the chosen kernel; not uncertainty about w |
| Estimated w | Shared fitted lag coefficient | Reduced-form calibration sensitivity; not a measured booking probability |
| Realized `lambda_t = R_t/B_t` | Revenue divided by weighted lagged GBV | Combines timing, fees, FX, cancellations, specification error and input precision; not commission take rate |
| Predictive error | Outcome minus an admissibly formed forecast | Includes more than coefficient dispersion; unprinted GBV introduces upstream forecast error |
| Guide/economic sensitivity | Revenue mapped through cushion and expectations | Determines whether uncertainty changes the decision; small parameter dispersion alone does not establish an edge |

## Descriptive variance reproduction

P has 24 quarters, 2020Q3–2026Q2; 22 have both lagged GBVs, 2021Q1–2026Q2. These are retrospective descriptions using frozen inputs. Sample variances use n−1. Percentage levels and percentage-point changes are distinguished.

At w=2/3, `a_t = 2*G1/(2*G1+G2)`. Its complement has the same variance.

| Window | n | Mean first-lag contribution | Variance, pp² | SD, pp | Min–max |
|---|---:|---:|---:|---:|---:|
| All lag-complete | 22 | 67.7277% | 26.4420 | 5.1422 | 59.5312–77.7191% |
| W1: 2023Q1 onward | 14 | 67.4733% | 21.5669 | 4.6440 | 62.8803–75.1381% |
| W2: 2024Q1 onward | 10 | 67.5210% | 21.8343 | 4.6727 | 62.8803–74.7145% |

| Target season | W1 n | Mean contribution | Contribution SD, pp | Mean realized lambda | Lambda SD, pp | Lambda range, pp |
|---|---:|---:|---:|---:|---:|---:|
| Q1 | 4 | 63.4909% | 0.4913 | 12.6938% | 0.3001 | 0.7090 |
| Q2 | 4 | 74.3845% | 0.6853 | 13.7136% | 0.2040 | 0.4973 |
| Q3 | 3 | 65.2844% | 0.4102 | 17.2394% | 0.1324 | 0.2453 |
| Q4 | 3 | 65.7570% | 0.3113 | 12.0298% | 0.0856 | 0.1711 |

Realized lambda means above are descriptive ratios, not L3's fitted OLS coefficients or replacements for K0's operational estimates.

| Target season | All-history n | All contribution SD / lambda SD, pp | W2 n | W2 contribution SD / lambda SD, pp |
|---|---:|---:|---:|---:|
| Q1 | 6 | 1.9920 / 0.3873 | 3 | 0.5949 / 0.3566 |
| Q2 | 6 | 1.4385 / 0.5851 | 3 | 0.5708 / 0.2497 |
| Q3 | 5 | 3.0371 / 0.4531 | 2 | 0.5679 / 0.0257 |
| Q4 | 5 | 0.8422 / 0.1959 | 2 | 0.4364 / 0.0646 |

Season means account for 99.05% of W1 contribution sum-of-squares and 99.11% of W1 lambda sum-of-squares. This is an arithmetic decomposition, not a causal result, significance test or statement that 99% of future revenue is predictable.

| Sample | n | Pooled within-season contribution SD, pp | Pooled within-season lambda SD, pp |
|---|---:|---:|---:|
| All history | 22 | 1.9709 | 0.4370 |
| Excluding 2021 | 18 | 0.7692 | 0.2258 |
| W1 | 14 | 0.5161 | 0.2109 |
| W2 | 10 | 0.5586 | 0.2529 |

The pooled calculation uses residual sum-of-squares around the four season means divided by n−4. Deleting each year from W1 yields contribution SD 0.4623–0.5586pp and lambda SD 0.1692–0.2529pp, with remaining n=10 or 12. For W2 the ranges are 0.3345–0.6580pp and 0.1777–0.3082pp, remaining n=6 or 8. Deletion changes season composition and sometimes leaves one observation in a season. These are sensitivity descriptions, not confidence intervals.

Recent stability is visible in this dataset, but W1/W2 have only two to four observations per season. Including 2021 materially changes the dispersion.

## What the completed L3 test establishes

L3 accepts the five-parameter descriptive fit and rejects its promotion.

| Matched chronological comparison | W1, n=14 | W2, n=10 |
|---|---:|---:|
| Free-weight revenue RMSE, USDm | 63.1971 | 57.3924 |
| Fixed 2/3 with identically estimated lambda, USDm | 54.2275 | 56.5157 |
| Free/fixed RMSE | 1.1654 | 1.0155 |
| Preregistered promotion hurdle | FAIL | FAIL |

The free model's RMSE is 16.54% and 1.55% higher, respectively. This does not establish universal inferiority: paired year-block ratio sensitivity ranges span 0.8483–1.5251 and 0.8069–1.1359, including equality. W1 has four target-year blocks; W2 has three and is nested in W1.

The all22 fit gives w=0.78648, versus 0.53873 excluding 2021 and 0.35696 for 2023 onward. The six-year-block sensitivity range is 0.30791–0.85733. These are neither physical booking shares nor precise structural confidence bounds.

**The central mathematical explanation:** within season s, if `G1/G2 ≈ r_s`, then

`R ≈ lambda_s * [1 + w*(r_s−1)] * G2`.

Changing w can be offset by changing lambda_s. Stable seasonal GBV proportions can therefore produce similar revenue predictions while leaving the lag coefficient weakly identified. Stability of the arithmetic contribution does not solve identification; it can help explain the ambiguity.

In L3's existing 1,000 parameter draws, correlations between w and Q1/Q2/Q3/Q4 lambda are +0.906/−0.991/+0.813/+0.846. These describe six-block resampling, not precise population correlations. Preserve joint parameter draws when propagating uncertainty. Combining independent marginal extremes can create incoherent scenarios.

Retaining fixed 2/3 establishes that this tested flexibility failed the agreed hurdle, not that 2/3 is uniquely optimal. Neither the free calibration nor the newly fitted all22 fixed-OLS coefficients should replace the operational policy automatically.

## Identification and source cautions

K1's five-lag fit uses eight free parameters on 14–20 quarters; season-specific weights require 20 parameters on 16–20 observations. Ex-COVID bootstrap ranges are approximately 0–0.724 for phi1, 0–0.640 for phi2 and 0.152–0.871 for their sum. Calling the sum an identified 58–64% overstates precision. Nine rolling-12 fits have phi1/phi2 SD 17.952/21.588pp but adjacent fits share eleven observations. They are not nine independent experiments. The older 0.65–0.70 sweep searched 21 weights across three estimation rules retrospectively; its W1 covers only 12 of 14 targets. The new matched L3 test is the relevant selection evidence.

K2's 268,110 reservations come from one city and one clean March-2016–February-2017 period. That count does not produce hundreds of thousands of independent current/global observations. Limitations include truncated capture windows, imported tails, unverified price units, price-times-nights rather than complete GBV, surviving stays rather than all bookings, and a six-month seasonal mapping that misaligns Christmas. Its ranges bracket tail assumptions and validation discrepancies; its later suggestion to use them as ±1 SD is inconsistent with their construction.

If C[b,t] is fee revenue from booking cohort b recognized in period t, backward revenue-origin shares are `C[b,t]/sum_b C[b,t]`; forward cohort-recognition shares are `C[b,t]/sum_t C[b,t]`. Their denominators differ. A backward value-weighted stay-origin proxy cannot simply become a forward GBV allocation.

Airbnb states that full GBV is recorded at booking regardless of payment, revenue is recognized at check-in, and cancellations reduce the period when they occur. RNPL may weaken the association between bookings, revenue and cash. Reported net GBV is therefore not a clean gross cohort, and unpaid-balance stocks are not revenue-flow weights. [2026 Q2 10-Q, Key Business Metrics](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm).

The same filing reports Q2 GBV $27,247m and H1 $56,434m, implying Q1 $29,187m; P uses $27,200m/$29,200m. Holding existing lambda fixed, this adds $27m to the weighted Q3 denominator, approximately $4.659m revenue. This is a source-precision sensitivity, not a new forecast or an edit to frozen inputs. Parent independently checked the filing table. Avoid presentation precision finer than the source basis justifies.

## Dollar sensitivities

At fixed parameters:

`dR = B*d(lambda) + lambda*(G1−G2)*dw + lambda*w*dG1 + lambda*(1−w)*dG2`

`dQ = dR/(1+c) − R*dc/(1+c)^2`.

Revenue elasticities to G1/G2 are a and 1−a. Refitting lambda when w changes adds `B*d(lambda)/dw`; it is not captured by a held-fixed partial derivative. Joint dependence and residual errors matter.

**Illustration only, n=1 assumed reference:** G1=$26bn, G2=$28bn, lambda=12%, w=2/3, c=1.79%. Revenue=$3,200m, guide=$3,143.73m, a=65%. These are not adopted ABNB inputs or probability bounds.

| Isolated change | Revenue change, USDm | Guide change, USDm |
|---|---:|---:|
| w +10pp, lambda held fixed | −24.00 | −23.58 |
| lambda +0.10pp | +26.67 | +26.20 |
| G1 +1% | +20.80 | +20.43 |
| G2 +1% | +11.20 | +11.00 |
| Both GBVs +1% | +32.00 | +31.44 |
| Cushion +1pp | 0 | −30.58, exact finite change |

For a reconciled constant-reference FX layer, `F = a*F1 + (1−a)*F2`, so `dF/da = F1−F2`. At $3.2bn reference revenue, a hypothetical 10pp FX-factor gap combined with Q4 W1 contribution SD 0.3113pp produces about $1.00m revenue/$0.98m guide sensitivity. It measures only arithmetic-weight sensitivity under that assumed construction. Currency exposure, fixing dates, RNPL flows, hedges and structural weights remain separate uncertainties.

Reported USD GBV already embeds FX; applying the illustrative gross factor again would double count it. Moving a recognized RNPL revenue-flow share p between fixing dates gives an incremental effect proportional to `p*(F_new−F_old)`. An unpaid-balance stock proxy cannot supply p.

## Inference and claims for the presentation

L3 already uses chronological refitting, a predeclared loss, matched information sets, explicit abstentions, paired errors, profile sensitivities and year deletion. Future revisions should retain those disciplines and match the intended forecast horizon. [Hyndman and Athanasopoulos, rolling-origin evaluation](https://otexts.com/fpp3/tscv.html).

A variance test requires a specified null and valid assumptions, rather than a generic significance p-value. See [NIST's variance-test framework](https://www.itl.nist.gov/div898/handbook/eda/section3/eda358.htm). In this application, normal-theory tests, asymptotic HAC precision, cluster inference with three or four year blocks and precise bootstrap probabilities would be fragile. More resamples do not create more years. L3's nominal 80% bands cover 7/8 eligible outcomes; the same eight appear in both windows. This is descriptive coverage, not independent replication or a coverage guarantee.

| Status / evidence | Honest presentation sentence | Skeptical question and answer | Weakener or required falsification evidence |
|---|---|---|---|
| Supported, P/C | Seasonal lagged GBV supplies an auditable revenue benchmark. | Is the mechanism structurally identified? Predictive and structural interpretations differ. | Matched-origin errors stop improving on simple baselines. |
| Supported, C | Estimating another lag parameter failed our predefined forecast hurdle, so we retained the fixed rule. | Did fixed weights prove optimal? No; the tested candidate failed promotion. | A preregistered successor reliably improves matched chronological performance. |
| Conditional, P | Recent within-season conversion is more stable than pooled quarter-to-quarter figures suggest. | How much history? Only 2–4 observations per season in W1/W2. | Persistent bias or repeated misses of defensible predictive ranges. |
| Unsupported, K1/K2/C | Do not claim two thirds of revenue physically comes from last quarter's bookings. | Where is the current cohort ledger? It is unavailable. | Current global fee-weighted booking-to-recognition data would directly test it. |
| Conditional, filings/K2/L2 | RNPL can change payment and cancellation timing; the revenue magnitude remains scenario-based. | Does unpaid balance measure lost revenue? No; it is a stock proxy. | Reconciled flows show no incremental effect, or the baseline already includes it. |
| Unsupported, L2/L4 | Do not claim an established tradeable guide-surprise edge. | Was the guide unknown in the test? Letter-close uses the same release's GBV, and returns did not establish an edge. | Before-release validation using historical GBV forecasts and dated guide expectations is needed. |

Today's Q4 forecast requires forecast Q3 GBV, so L3's conversion errors do not represent the complete uncertainty of today's Q4 guide forecast. L4's $3,123.419m guide versus $3,161.021m revenue consensus also mixes objects: its own revenue is $3,179.344m, about $18.322m above that revenue consensus. A common-cushion conversion is illustrative, not observed guide expectations. Q documents the exact basis check.

### Suggested spoken argument

“We use historical bookings as a transparent leading input to revenue. We tested whether estimating an additional lag weight improved forecasts formed using only information available at each historical origin. It did not clear our predefined hurdle, so we retained the simpler fixed rule. Our confidence comes from reproducibility, observed forecast errors and sensitivity to plausible changes. Exact current recognition shares remain uncertain, and we carry booking, conversion and management-guide uncertainty into the investment comparison.”

This sentence supports a forecasting method; it does not by itself establish a long or short thesis. The relevant forward risk is a change in seasonal booking relationships, fees, cancellations or FX behavior that makes the historical calibration less useful.

## Reproduction, checks and limitations

The following complete read-only command reproduces the core window/season statistics, sums-of-squares decomposition and year-deletion ranges. It creates no output files. The agent used these formulas; parent independently reran the main window/season statistics with exit 0 and obtained matching values. Pandas emitted performance warnings about DataFrame fragmentation; no numerical failure occurred.

```powershell
@'
import pandas as pd
f = pd.read_csv('data/processed/overnight/02_kpi_panel_quarterly.csv')
f['q'] = pd.PeriodIndex(f.quarter.map(lambda q: '20'+q[2:]+'Q'+q[0]), freq='Q')
f = f.sort_values('q').reset_index(drop=True).copy()
f['season'], f['year'] = f.q.dt.quarter, f.q.dt.year
f['g1'], f['g2'] = f.gbv_musd.shift(1), f.gbv_musd.shift(2)
f['base'] = (2*f.g1+f.g2)/3
f['a_pp'] = 100*2*f.g1/(2*f.g1+f.g2)
f['lambda_pct'] = 100*f.revenue_musd/f.base
z = f.dropna(subset=['g1','g2','lambda_pct'])
def within(d, col):
    v = d[col]-d.groupby('season')[col].transform('mean')
    return (v.pow(2).sum()/(len(d)-d.season.nunique()))**0.5
for name, start in [('ALL','2021Q1'),('EX2021','2022Q1'),('W1','2023Q1'),('W2','2024Q1')]:
    d = z[z.q >= pd.Period(start, freq='Q')]
    print(name, 'n=', len(d))
    for col in ['a_pp','lambda_pct']:
        print(col, d[col].agg(['count','mean','var','std','min','max']).to_dict())
        print(d.groupby('season')[col].agg(['count','mean','std','min','max']))
        sse = (d[col]-d.groupby('season')[col].transform('mean')).pow(2).sum()
        sst = (d[col]-d[col].mean()).pow(2).sum()
        print('pooled within-season SD=', within(d,col), 'season SS share=', 1-sse/sst)
        if name in ['W1','W2']:
            deleted = [(int(y),len(d[d.year!=y]),within(d[d.year!=y],col)) for y in sorted(d.year.unique())]
            print('year-deletion sensitivities=', deleted)
'@ | & '.venv/Scripts/python.exe' -B -
```

L3 parameter-draw correlations are reproducible by reading `parameter_bootstrap.csv` in C's canonical directory and computing ordinary sample correlations between `w` and `lambda_Q1_pct`, `lambda_Q2_pct`, `lambda_Q3_pct`, `lambda_Q4_pct`, preserving the source's units. They are descriptive of existing draws; no new fitting was conducted. Source tables for identification claims are K1's `A1_phi_estimates.csv`, `A4_rolling_windows.csv`, `A6_identification.csv` and `D3_carried_weight_pit_sweep.csv` under `data/processed/forecast_methods/kernel_phi_v2/`; L3's published parameter, score, profile, leave-year-out and uncertainty tables supersede old model-selection claims.

Independently read SHA-256 identities:

| Source | SHA-256 |
|---|---|
| P | `c8a42085fb1bda12e979308257413ae877efd36c14b79152ecee558ccb8c16ac` |
| C accepted specification | `f7cec04de2cdacfaad0fd7bb774992d933130e76918cca788bce151d482ddb40` |
| C acceptance receipt | `bf91d81a78e79368b8815ac33f626f0c12509158f4fe24161f34fd97d09bd973` |
| C chronological scores | `3ac919a1c3f88bc5a9653c8776b015c8d3690acb186cb73676d3e4ce4d0f87a7` |
| C parameter draws | `5f89aeeb8c14c3304728554c4e57794c3e565c7c805636c2a9d2372eb8ca6b3e` |
| L4 closure | `f7e6e6e3d83e222f11981e7f3e4b7546a6b661257a4a6858b43095e41b9bf891` |

Parent independently verified 32/32 acceptance bindings, including 24 output bindings, five source files, two reviews and the repeated accepted-specification binding. This confirms the consumed artifact identities, not independent statistical replication of every L3 procedure. No scorer run was required because no forecasts were registered.

## RESUME

Use this report and Q to review the investment argument. Consume L3's accepted immutable bundle in L4 through the existing handoff process, retaining the operational benchmark unless a separately reviewed decision changes it. Align forecast and consensus definitions, include unprinted GBV and cushion uncertainty, preserve joint parameter dependence and assess whether the economic conclusion survives. Keep exact cohort shares and RNPL causal magnitudes unresolved. This report completes the supportive audit without extending L3 or L4's implementation scope.
