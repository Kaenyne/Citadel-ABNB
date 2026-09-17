# RESEARCH LOG

Revision 1 (2026-09-17, initial forecast, Fable). Batch A09 (with R01 and R02; this log carries the RNPL-specific claims in full and cites the R01 log for the nights-distribution claims it reuses, which are reproduced by the same script in this folder). Reproduction: `datasets/a09_nights_error_distribution.py` (seed 20260917; section 7 of the script is the joint model; output `datasets/a09_r03_joint.csv`).

## 0. Metadata
- question_name: risk-july-rnpl-expansion-offsets-lap
- question_url: n/a (internal; `docs/pitch-forecasts/QUESTIONS.md` § R03)
- type: binary
- run_mode: initial
- run_date: 2026-09-17
- open_date: 2026-09-17
- close_date: 2026-11-05
- resolution_date: 2026-11-05
- scoring: spot
- cp_visible: no
- cp_value: n/a
- revision: 1
- agent: fable

## 0b. Question (verbatim)
### Title
Will the 5 Nov print show both an RNPL GBV share ≥25% and 3Q26 nights growth ≥ +10.0%?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes only if both C06 resolves (a) and R01 resolves Yes. Resolution 5 Nov 2026.
### Fine Print
(None beyond the resolution rule. C06 (a) = "≥25%" under C06's conventions: a share stated on the call counts when the letter is silent; "a quarter of GBV" / "approximately 25%" / "25%" resolves (a); "nearly a quarter", "low-to-mid twenties", "23%" resolves (b); a share for a period other than 3Q26 does not count. R01 Yes = 3Q26 Nights and Seats Booked ≥ 147.0m.)

Conventions adopted: (1) both legs are read from the same 5 Nov release set (letter, press release, call, 10-Q); (2) if the share is given only as a nights-share or bookings-share, C06 resolves (d) and this question resolves No whatever nights print; (3) the true share is not the object; the disclosed share is.

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | C06 (revision 1): P(a ≥25% disclosed) 0.15, b 0.24, c 0.31, d 0.30; P(disclosed) 0.70; true-share Monte Carlo: 2Q26 share U(21,23), ex-US ramp U(0,2), July expansion Exp(mean 1.4) capped 6, Q3 lead-time seasonal U(−2,0) → P(true ≥25) 0.216; language mapping ≥25 → (a) 0.9; sensitivities: Exp(mean 4) expansion → (a) 0.35; P(disclosed) 0.90 → (a) 0.18; nights ≥10.6 → P(disclosed) 0.80, (a) 0.16; "R03 should sit near 0.08–0.11" | `docs/pitch-forecasts/questions/rnpl-gbv-share-disclosed/research-log.md` §5–7; `datasets/share_ramp_model_2026-09-17.py` | 2026-09-17 | 2026-09-17 | yes |
| 2 | R01 (this batch): P(3Q26 nights ≥ 10.0%) 0.42 (0.30–0.55); final-calibrated normal centre 9.67, sd 1.70; alt-data leg 0.33, outside view 0.55, Kalshi 0.59 | `../risk-q3-nights-meets-guide/research-log.md` §5–6; `datasets/a09_final.json` | 2026-09-17 | 2026-09-17 | yes |
| 3 | The July expansion: 2Q26 call (Mertz, 6 Aug 2026): "Given the strong results that it's delivered, in July, we expanded the types of bookings eligible for Reserve Now, Pay Later." (D044) Types unnamed, size unquantified; eligibility was previously "listings with a moderate or flexible cancellation policy" (D002, D026, D028), US domestic from Aug 2025 (D004), global from 17 Feb 2026 excluding BRL/INR/TRY payers (D025, D027) | `data/processed/overnight2/D/rnpl_statement_ledger.csv` rows D002, D004, D025–D028, D044; `data/raw/transcripts/web/2Q26.html` | 2026-08-06 | 2026-09-17 | yes |
| 4 | RNPL module (3Q26): the July expansion enters as +0.10 / +0.20 / +0.30 pts of nights (bear / base / bull) and is "the largest single offset to the 3Q26 lap", "entirely unquantified"; base 9.49, bull 10.25 (147.3m); "a 3Q26 print at or above 10.3% nights with an RNPL share at or above 25% says the July expansion is bigger than the US anniversary"; "if the July-2026 booking-type expansion is quantified at more than ~0.5 points of nights, M1 turns positive through 2Q27 and the 4Q26 and 1Q27 calls both weaken" | `docs/rnpl-short-audit/00_SYNTHESIS.md` §1 item 3, §5; `01_rnpl-nights-mechanics-audit.md` (scenario design; §"what would change the verdict"); `data/processed/rnpl_short_audit/rnpl_nights_module.csv` | 2026-09-11 | 2026-09-17 | yes |
| 5 | Adoption among the eligible is saturated (about 70% take-up, D005; over 70% by 4Q25, D022), so share growth needs eligibility growth; the first full global quarter moved the disclosed share only from "roughly 20%" (1Q26, D031) to "over 20%" (2Q26, D043); Q3 is the shortest-lead-time booking quarter, which limits deferral applicability | C06 log claims 4, 5, 9; `03_insider_mechanics.md` §1.3 | 2026-09-17 | 2026-09-17 | yes |
| 6 | Pre-registered card: "RNPL share ≥25% with nights ≥10 weakens" the drag hypothesis; "share flat or down versus 2Q26 while the nights line decelerates" supports; 21–24% inconclusive. The card's own note: the share "identifies nothing on its own" | `data/processed/overnight2/D/D1_prereg_thresholds.csv` row 6; `docs/rnpl-short-audit/00_SYNTHESIS.md` §2 | 2026-09-11 | 2026-09-17 | no |
| 7 | C05: the mechanical net bundle contribution management could truthfully state for 3Q26 is 1.7–3.1 pts of nights, of which the July expansion is +0.10 to +0.30 ("assumed; deliberately small"); P(any quantification) 0.27 | `docs/pitch-forecasts/questions/bundle-attribution-quantified/datasets/bundle_3q26_mechanical_contribution.csv`; its log §6 | 2026-09-17 | 2026-09-17 | no |
| 8 | Finimize (paywalled, undated, after 6 Aug): "Airbnb has broadened which stays qualify since launching the option in the US in August 2025 and taking it global in February"; B. Riley estimates RNPL added 150bp to nights growth in Q2 after 200bp in Q1; Mertz: it "nudges travelers to commit earlier and helps hosts fill their calendars further in advance". No named booking types, no share figure | https://finimize.com/content/airbnbs-reserve-now-pay-later-push-could-keep-bookings-growing (`sources/finimize_rnpl_expansion_2026.txt`) | 2026-08 (undated) | 2026-09-17 | no |
| 9 | No newsroom or help-centre post names the July expansion; the Feb 2026 global rollout post is the latest RNPL newsroom item found; no market on the disclosure exists (Polymarket search; Kalshi has the nights ladder only) | https://news.airbnb.com/reserve-now-pay-later-is-now-available-worldwide ; `sources/polymarket_search_airbnb_20260917T032158Z.json`; `sources/kalshi_markets_KXABNB_open_20260917T032158Z.json` | 2026-02-17 / 2026-09-17 | 2026-09-17 | no |
| 10 | Joint model (this log, `a09_r03_joint.csv`, base row): July expansion X ~ Exp(1.4) capped 6 (pts of share); share_true = U(21,23) + U(0,2) + X + U(−2,0); nights = c + 0.143·(X − E[X]) + N(0, 1.69), c solved so that P(nights ≥10) = 0.424; P(disclosed) = 0.70 + 0.10·1[nights ≥10.6] + 0.05·1[10.0 ≤ nights < 10.6]; (a) = share_true ≥ 24.5 and disclosed and language-(a) (0.9). Results: P(a) 0.144, P(R01) 0.424, P(R01 | a) 0.514, corr(a, R01) 0.075, joint 0.074, product of marginals 0.061, joint capped to C06's P(a) = 0.15: 0.074 | `datasets/a09_r03_joint.csv`, `a09_final.json` | 2026-09-17 | 2026-09-17 | yes |
| 11 | Joint variants: Exp(mean 4) expansion → P(a) 0.37, joint 0.185 uncapped, 0.075 capped to 0.15; nights-per-share k = 0.214 (module bull) → 0.077; k = 0 (disclosure dependence only) → 0.064; full independence → 0.057; P(disclosed) 0.90 → 0.092 uncapped / 0.076 capped; R01 at 0.38 → 0.066; R01 at 0.55 → 0.093 | `datasets/a09_r03_joint.csv` rows 2–8 | 2026-09-17 | 2026-09-17 | yes |
| 12 | Impact inputs: R01 impact row; RNPL module bull-vs-base FY27 6.88 vs 6.41 (+0.5pt) and the ex-NA lap offset if the expansion is ≥ 0.5pt (M1 positive through 2Q27); RNPL raises ADR through mix to larger homes (D016, D033); brief sensitivities as R01 claim 21 | `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `rnpl_statement_ledger.csv` D016; `docs/pitch-forecasts/00_BRIEF.md` | 2026-09-11 / 2026-09-16 | 2026-09-17 | yes (impact) |
| 13 | Final 72-hour check (batch query 18) and the RNPL-specific query (15): no terms change, no eligibility post, no management comment this week; nothing new | WebSearch (see §2) | 2026-09-17 | 2026-09-17 | no |

Newest load-bearing source: the C06 and R01 logs and the computed joint (17 Sep); the ledger rows are 6 Aug (the last management statement on RNPL), 42 days old, which is the age of the newest company statement and cannot be refreshed before the print.

## 2. Query Log
1. [repo] brief, `QUESTIONS.md`, skill and format references, example log; C01, S01, C06, C02, C05 logs, JSONs and datasets (`share_ramp_model_2026-09-17.py`, `bundle_3q26_mechanical_contribution.csv`)
2. [repo] `docs/q3nowcast/SYNTHESIS.md`; `research/notes/q3nowcast/E_*`, `G_*`
3. [repo, pandas] `data/processed/q3nowcast/E/`, `E_aug/` nowcast and walk-forward files
4. [repo] `data/processed/q3nowcast_v2/E/`, `E_attrition/`; `05_backtests/WPK_reviews-index-2023-vintage.md`
5. [repo] bridge and reconciliation notes (2026-09-10)
6. [repo] `docs/rnpl-short-audit/00_SYNTHESIS.md`, `01_*.md` (grep july|expansion|eligib); `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §2.4; `data/processed/overnight2/D/rnpl_statement_ledger.csv` (rows matching July|expand|eligib); `D1_prereg_thresholds.csv`
7. [repo] `research/notes/2026-09-13_market-implied-model.md` §10; `data/processed/reverse_dcf/E/` files
8. [repo, pandas] `data/processed/overnight/02_guidance_ledger.csv` nights rows
9. [repo] `03_insider_mechanics.md` §5.4
10. [repo] grep "WPK-A" / "0.757"
11. [Kalshi API] KXABNB — 2026-09-17T03:21:58Z
12. [Polymarket public-search] airbnb — 03:21:58Z (no RNPL or KPI market)
13. WebSearch: Airbnb news (charged to R01)
14. WebSearch: Airbnb third quarter 2026 nights and seats booked estimate analysts preview (charged to R01)
15. WebSearch: Airbnb Reserve Now Pay Later expanded eligible booking types July 2026 (charged to R03)
16. WebFetch: finimize.com RNPL article (paywalled fragment; B. Riley figures)
17. WebFetch: octagonai.co airbnb-bookings-in-q3
18. WebSearch: Airbnb bookings demand travel trends this week September 2026 (final 72-hour neutral recency check — nothing new; charged to R02)
19. [computed] `datasets/a09_nights_error_distribution.py` section 7

WebSearch calls charged to R03: 1 (query 15); batch total 4 of 15.

## 3. Leading Hypothesis Entities
Airbnb, Reserve Now Pay Later, Ellie Mertz, July 2026 eligibility expansion, RNPL share of GBV, Nights and Seats Booked, 3Q26 earnings call, 5 November 2026

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Product of marginals (0.15 × 0.42 = 0.063) | discarded as the method, kept as the floor | The July expansion raises both the share and nights, and management discloses more readily in a strong quarter; the computed joint is 0.074 with P(R01 \| a) 0.51 (claim 10) |
| Strong positive dependence (P(R01 \| a) ≈ 0.7) | discarded | The mechanical link is weak: the C06 mean expansion (1.4 pts of share) maps to +0.2pt of nights (module base), so even a 4-pt share expansion adds ≈ 0.6pt; the correlation of the two indicators is 0.075 (0.12 under Exp(4)) |
| The July expansion is large (Firm-policy listings, longer stays, Experiences eligible) | kept as the C06 Exp(4) sensitivity | Would raise the true-share ≥25 probability to 0.55, but C06's cap (a = 0.15) reflects the disclosure and language filters; uncapped the joint would be 0.19 |
| Management restates the share as "over 20%" even at a true 25% | kept inside C06's language mapping (0.9 for ≥25; 0.55 → (c) for 21–24) | Rounding habit (D022, D031, D043); a true 24.5–25.4 is the boundary where "nearly a quarter" (b) and "a quarter" (a) both plausible |
| Share given as nights-share or bookings-share only | inside C06's (d) ≈ 0.02 | Airbnb has always used the GBV basis for this metric |
| Nights ≥10 comes from non-RNPL sources (LatAm, Tokyo, hotels, seats) with the share flat | this is the R01-not-R03 path, 0.42 − 0.07 = 0.35 | The reviews index's regional texture (LatAm +27, APAC +10, NAM +7) is demand-mix, not RNPL |

## 5. Independent Estimates
- base_rate_estimate: 0.06 — product of the C06 base-rate vector's (a) (0.16) and R01's outside view (0.55) scaled by the observed conditional lift (0.51/0.42): 0.16 × 0.55 × 0.7 ≈ 0.06 (a crude outside-view joint; the persistence base rate says the share is disclosed 0.82 of the time, the language filter and the true-share model do the rest)
- decomposition_estimate: 0.074 — the computed joint (claim 10): common-cause July expansion, disclosure dependence on the print, C06's share model, R01's nights distribution; capped at C06's P(a) = 0.15 (not binding)
- anchor_estimate: none — no market prices either the share or the joint; the Kalshi nights ladder (P(≥147.0m) 0.59, stale) is R01's adjacent price, and multiplying it by C06's 0.15 gives 0.09 as an upper reference
- anchor_value: n/a (NO_EXTERNAL_ANCHOR; Kalshi × C06 reference 0.09)
- final_estimate: 0.07 (credible interval 0.04–0.12)
- final_minus_anchor: n/a. The base-rate and decomposition estimates agree within 1.5 points and share C06's share model, so the agreement is partly by construction; the number moves with P(disclosed) (0.70; a standing-KPI treatment at 0.90 gives 0.09) and with R01 (0.38 → 0.066; 0.55 → 0.093) more than with the mechanical link. Coherence: R03 ≤ min(C06 a, R01) = 0.15 holds with room; R03 / R01 = 0.17 is the share of R01-Yes worlds in which the RNPL narrative is also rebutted by a ≥25% share

## 6. Final Numbers
**Binary.** P(C06 = (a) and R01 = Yes) = **0.07**, credible interval **0.04–0.12** (variants in claim 11 span 0.057–0.093; the disclosure-probability and R01 sensitivities set the ends).

Decomposition of the 0.07: P(true share ≥ 24.5) 0.21 × P(disclosed as a 3Q26 GBV share | strong print) ≈ 0.73 × P(language (a) | true ≥25) 0.9 = P(a) 0.14; × P(nights ≥10 | a) 0.51 = 0.074. The dependence on disclosure is the binding filter: conditional on the true share being ≥25 and nights ≥10, the question still resolves No about a third of the time because the share is not stated, or is stated as "over 20%".

Extreme-probability gate: not triggered (0.07 > 0.05). Resolution audit anyway: (i) both legs read from the 5 Nov release set; (ii) a call-only share counts (C06 convention 1); (iii) a nights-share-only disclosure is No; (iv) a share stated for "the year to date" is No (C06 convention 3).

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| July expansion Exp(mean 1.4) in share points | Exp(mean 4): 0.19 uncapped, 0.075 at C06's cap (the cap is C06's own number; if C06 is revised to (a) 0.35 the joint becomes ≈ 0.19) |
| Nights per share point k = 0.143 (module base) | k = 0.214 (module bull): 0.077; k = 0 (no mechanical link): 0.064 |
| Disclosure lift on a strong print (+0.10 accel / +0.05 meet) | none (independence): 0.057 |
| P(disclosed) 0.70 | 0.90 (standing KPI): 0.092 uncapped, 0.076 capped; 0.50 (reframing removes RNPL numbers): ≈ 0.05 |
| R01 = 0.42 | 0.38 (C02/S01 conditioning value): 0.066; 0.55 (market view): 0.093 |
| Language mapping ≥25 → (a) 0.9 | 0.7 ("nearly a quarter" habit): 0.058 |

Pre-mortem ("it is 5 Nov and both legs resolved Yes"): (1) **the July expansion was big** (Firm-policy listings or long stays made eligible) and management, proud of it, gave "a quarter of GBV" alongside a 10%+ print; this is the Exp(4) world and it is where the whole memo's RNPL leg fails, which is why the impact row carries the drag rebuttal. (2) **The share rose on the ex-US ramp alone** (Q3 is the first full quarter with UK/AU/APAC/CA at maturity) and nights cleared 10 for unrelated reasons; priced as the independence path (0.057). (3) **Disclosure habit**: the share becomes a standing KPI like app share (0.90 disclosure), priced at 0.09. ("It resolved No although the true share was ≥25 and nights ≥10"): (4) management said "over 20%" again or moved to a year-to-date figure; this is the disclosure filter and the reason the number is 0.07 rather than 0.09–0.11. Asymmetry: R03's role in the memo is the "both risks at once" line; at $1.6/share of EV it is worth one sentence, and it is entirely inside R01's EV.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-10-31 | Airbnb newsroom / help-centre changes naming the July-expanded booking types (policy types, stay lengths, hotels, Experiences) | A named expansion to Firm-policy listings or long stays: move the expansion prior toward Exp(4), R03 → 0.10–0.12 (with C06 (a) revised); a restriction: R03 ≤ 0.04 |
| 2026-09-18 to 2026-09-30 | September Inside Airbnb dumps; R01 re-centred | R01 ± 0.08 per ±0.5pt on the centre → R03 ± 0.015 |
| 2026-10-02 | Prelim memo | Quote 0.07 (0.04–0.12) as the "both at once" line; state that it is inside R01's EV |
| 2026-10-26 to 2026-11-04 | Sell-side previews modelling an RNPL share | Any preview at ≥25%: +0.01 (via C06 +3 pts on (a)) |
| 2026-11-05 (after close) | 3Q26 letter (governs), call, 10-Q | Resolve both legs; if the letter gives the share, ignore the call; record the pair (share, nights) on the pre-registered card (claim 6) |

## 9. Impact
If both legs happen (nights ≥10 with a disclosed RNPL share ≥25%), the memo loses its print sign and its RNPL-drag leg at once. Deltas versus the memo's base case (`datasets/a09_impact.csv`, R03 row):

| Item | Delta if R03 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | **+1.3** (as R01: E[nights \| ≥10] 11.24 − 9.9) | R01 impact row |
| 4Q26 nights (pts) | **+1.2** (R01's +0.8 plus +0.4 for the ex-NA lap being offset by the expansion, the module's 4Q26 bull-vs-base gap) | `rnpl_nights_module.csv` 4Q26 bull 8.35 vs base 7.61 (+0.74; half taken) |
| FY27 nights (pts) | **+1.3** (R01's +0.5 plus +0.8: module bull-vs-base +0.5 and the M1-turns-positive case from a ≥0.5pt expansion) | claim 4, claim 12 |
| ADR (pts) | **+0.3** (larger-home mix under a bigger RNPL share; D016, D033) | judgement, half of the 2025 mix step |
| 4Q26 revenue ($M) | **+62** = ⅔ × $317M GBV × 12.03% + 1.21 × $30M | kernel carry + brief sensitivity |
| FY27 revenue ($M) | **+211** (1.34pt × $158M) | brief sensitivity |
| FY26 adj. EBITDA margin (pp) | **+0.5** (0.59 × (65 + 62)/7,980 × ½) | brief sensitivity, held costs |
| FY27 adj. EBITDA margin (pp) | **+0.9** (0.66 × 1.34) | brief sensitivity |
| FY27 EPS ($) | **+0.20** ($211M × 0.66 × $0.0014) | brief sensitivity |
| Stock ($/share) | **+22.2 vs the base-case day-1** ($16.6 from the R01 day-1 cell mix plus 1.34 × 0.44 × $9.5 = $5.6 on the multiple line as the FY27 lap narrative is dropped); **+12.6 vs the unconditional** | S01 cells; brief multiple slope |
| **EV = P × impact** | **0.07 × $22.2 = $1.6/share** (vs base case); $0.9 vs unconditional | |
| Materiality | **Material, marginally** (≥ $1/share vs the base case; below it vs the unconditional). It is a subset of R01 (0.07 of 0.42) and must not be added to R01's or R02's EV. The memo can carry it as one sentence: "if the share is a quarter of GBV and nights hold 10%, the lap thesis is wrong, not just early" | |

## RESUME
The next agent (audit response) should re-run the script (section 7 is the joint; deterministic) and attack: (1) the nights-per-share-point link k = 0.143, which is a ratio of two team assumptions (module +0.20pt of nights; C06 Exp(1.4) share expansion) with no measured analogue; (2) the disclosure lift (+0.10 on an accelerating print), taken from C06's own sensitivity; (3) whether the cap at C06's (a) = 0.15 should bind in the Exp(4) variant or whether C06 itself should move first. If C06 is revised in its audit response, recompute R03 with the revised P(a) and P(disclosed) before anything else; the joint is 0.51 × P(a) to within ±0.01 for any R01 between 0.38 and 0.45.
