# Response to the September 11 research audit

Response date: 2026-09-11 (19:30–20:00 UTC)
Responds to: [2026-09-11-research-audit.md](2026-09-11-research-audit.md)
Revised research: [research-log.md](../research-log.md) (revision 2)
Prepared forecast: [forecasts/2026-09-11-prepared-cdf.json](../forecasts/2026-09-11-prepared-cdf.json) — **not submitted**

## Summary

All seven findings were checked against fresh computations and new fetches. Six are accepted in full, one (independence of the three estimates) is accepted with the claim withdrawn rather than repaired. The headline forecast moves only at the margin: median 257k (was 258k), 55% above 250k (unchanged to rounding), 2.5% below 150k (was 1.5%, now including an explicit 1% resolution-source risk). The supporting argument changed materially: the market anchor is now 63% above 250k, not 57%, and the forecast is stated as an 8-point divergence from it with a named reason, rather than as agreement.

## Finding-by-finding

### 1. Market anchor — accepted

Fresh books were saved at 2026-09-11T19:32Z to [sources/polymarket_rials_books_20260911T193202Z.json](../sources/polymarket_rials_books_20260911T193202Z.json). Midpoints for the December event: <2.0M 0.155, 2.0–2.5M 0.215, 2.5–3.0M 0.095, 3.0–3.5M 0.305, 3.5–4.0M 0.123, ≥4.0M 0.0405; sum 0.934. The lower two brackets carry the only real depth (933 shares bid at 0.15; 76 at 0.21), while the ≥4.0M bracket shows 0.011 bid / 0.07 ask. The coherent repair is therefore the lower-bracket complement: **P(≥250k) = 0.63**, spread interval 0.62–0.64. The raw upper-bracket sum (0.57) and proportional normalization (0.61) are recorded as alternatives, not used.

The log now states the forecast's 55% as a **−8 point divergence** from the anchor with the reason given in section 5 of the revised log: the market's 21.5% on 200–250k under-weights the historical frequency of post-peak stabilization (one-third of crisis windows end with the rial stronger), and the period-restricted base rates (51–55%) sit below the anchor. Thin liquidity (total volume ≈ $9.4k) is the reason for not compressing further, not the reason for the divergence.

### 2. Crisis threshold and base-rate probability — accepted

Definitions are now explicit: window = 111 calendar days forward from each observation date, terminal value = last quote on or before the target date, 90 days of history required, log returns, sample SD, nearest-rank quantiles. The original "trailing 90-day return >25%" was the log return >0.25 (simple >28.4%). Results with the corrected labels, P(>250k) computed directly from a 235k start (needed log move +0.0619):

| Sample | n | median log | P(>250k) | P(<0) |
|---|---:|---:|---:|---:|
| All windows | 3,805 | +0.064 | 0.505 | 0.273 |
| Crisis, log90 > 0.25 | 490 | +0.099 | 0.576 | 0.333 |
| Crisis, simple90 > 25% | 599 | +0.100 | 0.569 | 0.327 |
| Crisis simple > 25%, start ≥ 2018 | 487 | +0.096 | 0.542 | 0.359 |
| Crisis simple > 25%, start ≥ 2020 | 318 | +0.094 | 0.547 | 0.340 |
| Crisis simple > 25%, start ≥ 2023 | 202 | +0.070 | 0.510 | 0.356 |

The crisis windows collapse into about eight distinct episodes (2012, 2018, 2020, 2022–23, 2024–25 winter, 2025 autumn, 2025–26 winter). The base-rate estimate is now stated as P(>250k) = 0.57 with a 0.51–0.58 range across definitions and periods, effective n ≈ 8 episodes.

### 3. Rally comparison — accepted

The five "post-event" figures were 20-day minima, not 111-day extremes, and are relabeled as an event study. Fixed-horizon extremes are now reported separately: the largest 111-day decline in the quote is **−39.7%** (2018-09-25 → 2019-01-14, log −0.506), which exceeds the −36.2% needed to reach 150k from 235k. Unconditional frequencies: 111-day decline ≥15% in 2.5% of windows, ≥20% in 1.2%, ≥25% in 0.4%, ≥36% in 0.03% (all from the 2018 episode). The sentence claiming no rally beyond −20% is deleted. The 2018 episode also matters for the causal argument: that rally followed a central-bank leadership change and market-liberalization measures, not sanctions relief, so scenario B is relabeled "policy or sentiment reversal, or talks" and no longer asserts that only blockade relief or regime change can produce >20% appreciation. Percentage conventions are now stated: all moves are changes in the toman-per-dollar quote.

### 4. Update rules — accepted

One procedure is now defined and every sensitivity row is recomputed from it: (a) re-center the spot to the latest Bonbast close; (b) scale each component's drift by T/111 and its SD by √(T/111) for the remaining horizon T; (c) event triggers move weight between named components. Corrected rows:

| Case | Old log | Recomputed |
|---|---|---|
| Spot +5% at open (T=108) | +4 pts | P(>250k) 0.55 → **0.635** |
| Sep 30 Bonbast = 250k (T=92, weights unchanged) | ≥70%, median 285k | **0.65, median 269k** |
| Sep 30 Bonbast = 225k | ~40%, median 240k | **0.44, median 242k** |
| Talks announced: A1 48→38, A2 17→12, B 20→35 | −10 pts | **0.47 (−8 pts), median 246k** |
| Blockade lifted: A1 12, A2 8, B 35, C 5, D 40 | ~20%, median 205k | **0.22, median 209k** |
| September pace persists in A1 only (drift +0.90) | ~90%, median 500k | **0.665, median 418k**; 235k × 1.06^16 = 597k |
| Nov 29 with spot 260k / 300k / 230k (T=32) | fixed tail floors | P(>250k) **0.75 / 0.97 / 0.29** |

The "keep ≥8% below 200k" floor is withdrawn; late-November tails come from the procedure.

### 5. Economic-source claims — accepted

Claim 4 now states the Euronews "60%" as a 55.6% rise in the quote (35.7% loss in the rial's dollar value). Claim 5 says the struck complexes "account for" ~50%/70% of capacity and that damage extent is unreported. Claim 6 records $500M as one week's intervention and $2B as announced capacity, not a burn rate or reserve figure. The snippet-only Bloomberg export claim is replaced by a fetched Reuters/Al-Monitor piece (Sep 1): August loadings 220–255k bpd per Vortexa and Kpler, down from ~740k bpd in July and ~2M bpd in March; Kpler's analyst links the collapse to FX income and money-financed deficits. It is now load-bearing and cited for that purpose.

### 6. Resolution uncertainty — accepted

The resolution criteria were re-fetched at 19:31Z and remain null. The forecast is now stated as conditional on a Bonbast-type open-market source, with a separate 1% probability of a source that resolves below the lower bound. Below-bound mass is therefore 0.01 + 0.99 × 0.015 = 2.5%. The Polymarket contracts are described as "same subject", not "identical".

### 7. Reproducibility — accepted

Mixture summaries corrected: in-range mode ≈ 237,700; mass 150–200k 9.9%, 200–250k 32.7%; P(>400k) 8.1%. Volatility is recomputed with a documented method (zero-mean log returns divided by calendar-day gaps, annualized by 365): 30d 0.30, 60d 0.27, 90d 0.31, 180d 0.33, 365d 0.33. The Bonbast dataset note now says observations end 2026-09-10. The independence claim is withdrawn: the base-rate and decomposition estimates share the tgju series, and the market was read before the mixture was finalized. The 201-point CDF is exported with every step ≥ 5×10⁻⁵ and the in-range scoring density ≥ 0.054 everywhere.

## Forecast decision

| Quantity | Before audit | After response |
|---|---:|---:|
| Median | 258k | 257k |
| 5th / 95th | 180k / 440k | 175k / 438k |
| P(<150k) | 1.5% | 2.5% |
| P(>250k) | 55.5% | 54.9% |
| Anchor (Polymarket, coherent) | 57% | 63% |

The above-bound mass is held at 55% rather than moved toward 63% because the market's shape (bimodal, little mass in 200–250k) is an illiquid book's view of a knife-edge, and the historical crisis sample, especially the post-2018 restrictions, supports 51–58%. If the Sep 30 Bonbast print is at or above 250k, the procedure lifts the number to 65% without any further judgment.

## Remaining uncertainties

- Resolution criteria unpublished until Sep 14. Source, quote side (sell vs buy), and finalization rules are unknown.
- Whether the September pace (6.5%/week) is a blow-off top or a new trend. The procedure handles this through weekly re-centering, not through a drift change.
- Effective sample size for the base rate is about eight episodes.
