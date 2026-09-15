# Airbnb | Revenue, guide and value

Status: UNSIGNED local review. Information frozen 13 September 2026; execution date 14 September. No adopted direction, target or probabilities.

**Our conditional Q4 revenue is $3,179.3m, $18.3m (+0.58%) above the captured Street revenue estimate.** The $3,123.4m implied guide uses a separate cushion assumption. Comparing that guide directly with revenue consensus does not establish a negative guide surprise. Explicit expectations for management's guide remain unavailable. [R,Q]

## Compare the same forecast object

| Q4 2026 object | USDm | Interpretation |
| --- | --- | --- |
| Own revenue R / Street revenue S | 3,179.344 / 3,161.021 | Yahoo / LSEG-family revenue; 13 Sep 15:20 UTC |
| Revenue gap R - S | +18.322 | +0.5796% of Street revenue; same basis |
| Own implied guide G | 3,123.419 | R / (1+c); c=1.7905%, trailing-eight median |
| G - S | -37.602 | Different objects; diagnostic, not guide surprise |
| Hypothetical Street guide S / (1+c) | 3,105.419 | Assumes our cushion; not observed consensus |

## Retain the tested fixed rule

Revenue = seasonal lambda x [2/3 prior-quarter GBV + 1/3 two-quarters-prior GBV]. L3 accepted implementation and completed validation; estimating a shared lag weight failed its preregistered promotion hurdle. Existing K0 seasonal estimation stays in production. The all22 weight 0.786478 and newly fitted fixed-OLS coefficients are descriptive only. [C]

| Chronological window | Free RMSE, USDm | Matched fixed OLS | Free/fixed; result |
| --- | --- | --- | --- |
| W1 (n=14) | 63.20 | 54.23 | 1.1654 / FAIL |
| W2 (n=10) | 57.39 | 56.52 | 1.0155 / FAIL |

Notes: W1 is 2023Q1-2026Q2; W2 is 2024Q1-2026Q2 and nested. Origins are letter-close with newly printed GBV. Errors do not measure pre-release guide skill or include today's forecast-Q3-GBV and cushion risk. The shared weight is not a measured booking-cohort probability. Three full accepted charts and their limitations accompany this memo. [C,Q]

<!-- PAGEBREAK -->

# The financial consequence is conditional

## Operating assumptions flow into cash and value

| Conditional case | FY27 revenue, $m | EBITDA, $m | FCF, $m | 13 Sep 2027 / share |
| --- | --- | --- | --- | --- |
| Soft envelope | 15,741 | 5,625 | 5,364 | $177.33 |
| Reference | 15,952 | 5,808 | 5,537 | $182.87 |
| Firm envelope | 16,050 | 5,900 | 5,624 | $185.68 |

Soft uses ADR mean reversion, lambda -0.10pp and 3.88% Q4 cushion; firm uses alternative nights A, lambda +0.10pp and the median cushion. Weight stays 2/3. These are assumed envelopes, not CIs or probability cases. Separate +/-1% net after-hedge revenue sensitivities affect Q3/Q4 2026 and Q1 2027, then propagate changed annual bases; they are not measured FX and are not combined with lambda stresses. [R,M]

**The reference is $182.87 per share at 13 September 2027**, twelve months from the frozen information date: 16.5x full FY27 EBITDA plus $10,029.1m net cash, divided by 578.85m diluted-share proxy. Cash and shares use FY26 end plus 256/365 of FY27 net flows, assumed uniform within year. The later 31 December value is $184.66; the $1.80 difference changes only balance timing. The multiple is inherited and conditional. [M,V]

Notes: FY27 net income $3,355m. FCF = adjusted EBITDA + net interest - cash taxes + change in unearned fees + working-capital residual - capex. Cash taxes $542m; capex $48m; unearned change 0. Total EBITDA addbacks include D&A; GAAP operating proxy subtracts SBC and total addbacks once. Customer funds are excluded. Share mechanics inherit the $181.94 price anchor dated 4 Sep 2026; it is not a return denominator. Later-quarter growth and costs remain inherited assumptions. [M,V]

## Evidence that can and cannot change the decision

L3's 108-file bundle and 1,187 row dispositions are verified. FX scenario arithmetic reconciles, but matching pre-hedge baseline, signed H/H_new, and RNPL recognition exposures remain unidentified. Current cohort inputs cover Q3 only, not Q4/Q1. Incremental FX stays null, not measured zero. Fee theta is unavailable (0/6 scheduled captures); NCLH transfer fails and supplies no ABNB adjustment; hotels remain comparators. [S]

A2 remains PARTIAL with no executable edge; its historical sign test compares guide with revenue expectations, not explicit guide expectations. B2 fails (5/9 and 4/7 versus 70%). The unsigned November card preserves rounding-aware lambda, payment-balance, ADR and exact management-wording tests. Missing evidence is ABSENT; no rule automatically trades or validates the opposite thesis. [E,F]

Sources: [R] L4 revenue v2 frozen bridge and dated expectations; [M] linked L4 model v2 and independent tieout; [C,S] accepted L3 bundle 8821961853e4, research 7fb6fe0f248d, source audit v2; [Q] 13 Sep QVS basis/variance notes; [E,F] committed L2 A2/B2 and corrected RNPL notes; [V] inherited driver model, 7 Sep 2026. Full paths, hashes, units, statuses and decision alternatives are in the source ledger and unsigned register.
