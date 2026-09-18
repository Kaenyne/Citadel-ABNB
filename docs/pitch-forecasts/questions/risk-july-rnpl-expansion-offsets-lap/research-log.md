# RESEARCH LOG

Revision 2 (2026-09-17, audit response to A09, Fable). Revision 1 (2026-09-17, initial forecast, Fable) is superseded where §10 says so. Batch A09 (with R01 and R02; this log carries the RNPL-specific claims in full and cites the R01 log for the nights-distribution claims it reuses). Reproduction: revision 2 `../risk-q3-nights-meets-guide/datasets/a09_v2_print_distribution.py` section 5 (the joint; seed 20260917; writes `datasets/a09_v2_r03_joint.csv`, `a09_v2_impact.csv`, `a09_v2_final.json` into this folder); revision 1 `datasets/a09_nights_error_distribution.py` and its `a09_*.csv` left untouched. Upstream inputs: C06 revision 2 (`../rnpl-gbv-share-disclosed/`), R01 revision 2 (`../risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json`). Audit: `docs/pitch-forecasts/audits/A09-research-audit.md`; response `audits/A09-audit-response.md`.

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
- revision: 2
- revised: 2026-09-17
- agent: fable

## 0b. Question (verbatim)
### Title
Will the 5 Nov print show both an RNPL GBV share ≥25% and 3Q26 nights growth ≥ +10.0%?
### Resolution Criteria
**Type.** Binary. **Resolution.** Yes only if both C06 resolves (a) and R01 resolves Yes. Resolution 5 Nov 2026.
### Fine Print
(None beyond the resolution rule. C06 (a) = "≥25%" under C06's conventions: a share stated on the call counts when the letter is silent; "a quarter of GBV" / "approximately 25%" / "25%" resolves (a); "nearly a quarter", "low-to-mid twenties", "23%" resolves (b); a share for a period other than 3Q26 does not count. R01 Yes = 3Q26 Nights and Seats Booked ≥ 147.0m.)

Conventions adopted: (1) both legs are read from the same 5 Nov release set (letter, press release, call, 10-Q); (2) if the share is given only as a nights-share or bookings-share, C06 resolves (d) and this question resolves No whatever nights print; (3) the true share is not the object; the disclosed share is; (4) R01's revision-2 conventions apply to the nights leg (fixed 133.6m base; printed ≥ 147.0m = latent ≥ 146.95m); (5) resolution says nothing about causation: a Yes is the joint observation the pre-registered card says "weakens" the RNPL-drag hypothesis, not proof that the July expansion produced the nights outcome (A09-16).

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | **C06 revision 2** (replaces rev 1): P(a ≥25% disclosed) **0.25**, b 0.20, c 0.26, d 0.29; P(disclosed) 0.71 with a level-dependent gate (true ≥25: 0.75; 21–24: 0.68; ≤20: 0.55); language map for true ≥24.5: (a) 0.85, (b) 0.05, (c) 0.10; true-share model v2: 1Q26 share U(19,21), Q1→Q2 increment U(0.5,3.5) with 2Q26 in [20.5,23.5], Q3 ramp U(0,0.5)×increment, July expansion 0.75·Exp(1.4) + 0.25·Exp(3.5) capped 8, symmetric mix noise U(−1,1), no directional seasonal penalty → P(true ≥25) 0.389; every input labelled an assumption; sensitivities: standing-KPI gate 0.90 → (a) 0.30; reframing gate 0.50 → 0.16; large expansion only → 0.38; small only → 0.21; nights ≥10.6 (gate +0.10) → 0.28. Rev 1's (a) 0.15 and its U(−2,0) penalty are withdrawn by C06 itself | `../rnpl-gbv-share-disclosed/research-log.md` §5–7, §10; `forecasts/2026-09-17-forecast.json` (revision 2); `datasets/share_ramp_model_v2_2026-09-17.py` | 2026-09-17 | 2026-09-17 | yes |
| 2 | **R01 revision 2**: P(3Q26 nights printed ≥ 147.0m) **0.39** (0.386) from N(9.5, 1.70) on latent growth (the nowcast object; the rev-1 blend 0.42 and its N(9.67, 1.70) withdrawn); R02 0.26; S01 states decel 0.636 / flat 0.104 / accel 0.261 | `../risk-q3-nights-meets-guide/research-log.md` §5–6; `datasets/adopted_print_states_v2.json` | 2026-09-17 | 2026-09-17 | yes |
| 3 | The July expansion: 2Q26 call (Mertz, 6 Aug 2026): "Given the strong results that it's delivered, in July, we expanded the types of bookings eligible for Reserve Now, Pay Later." (D044) Types unnamed, size unquantified; eligibility was previously "listings with a moderate or flexible cancellation policy" (D002, D026, D028), US domestic from Aug 2025 (D004), global from 17 Feb 2026 excluding BRL/INR/TRY payers (D025, D027) | `data/processed/overnight2/D/rnpl_statement_ledger.csv` rows D002, D004, D025–D028, D044; `data/raw/transcripts/web/2Q26.html` | 2026-08-06 | 2026-09-17 | yes |
| 4 | RNPL module (3Q26): the July expansion enters as +0.10 / +0.20 / +0.30 pts of nights (bear / base / bull) and is "the largest single offset to the 3Q26 lap", "entirely unquantified"; base 9.49, bull 10.25 (147.3m); FY27 base 6.41 / bull 6.88 (a 0.47pt **scenario difference**, not an identified conditional effect, A09-16); "if the July-2026 booking-type expansion is quantified at more than ~0.5 points of nights, M1 turns positive through 2Q27 and the 4Q26 and 1Q27 calls both weaken" | `docs/rnpl-short-audit/00_SYNTHESIS.md` §1 item 3, §5; `01_rnpl-nights-mechanics-audit.md`; `data/processed/rnpl_short_audit/rnpl_nights_module.csv` | 2026-09-11 | 2026-09-17 | yes |
| 5 | Adoption figures, **relabelled (A09-09)**: "about 70%" (D005) is the share of people offered the product in the US who take it; "over 70%" by 4Q25 (D022, 4Q25 letter footnote) is global GBV-weighted adoption among eligible bookings; D022's own note warns against chaining the two. Neither establishes saturation; share can also rise through adoption within existing eligibility and booking-mix shifts. "Share growth needs eligibility growth" is an **assumption** used only to motivate the common-cause structure; the first full global quarter moved the disclosed share from "roughly 20%" (1Q26, D031) to "over 20%" (2Q26, D043) | C06 rev 2 log claims 4, 5, 9 (rewritten there for A04-08); `rnpl_statement_ledger.csv` D005, D022, D031, D043; `03_insider_mechanics.md` §1.3 | 2026-09-17 | 2026-09-17 | no |
| 6 | Pre-registered card: "RNPL share ≥25% with nights ≥10 **weakens**" the drag hypothesis; "share flat or down versus 2Q26 while the nights line decelerates" supports; 21–24% inconclusive. The card's own note: the share "identifies nothing on its own" | `data/processed/overnight2/D/D1_prereg_thresholds.csv` row 6; `docs/rnpl-short-audit/00_SYNTHESIS.md` §2 | 2026-09-11 | 2026-09-17 | yes (§9 wording) |
| 7 | C05: the mechanical net bundle contribution management could truthfully state for 3Q26 is 1.7–3.1 pts of nights, of which the July expansion is +0.10 to +0.30 ("assumed; deliberately small"); P(any quantification) 0.27 | `../bundle-attribution-quantified/datasets/bundle_3q26_mechanical_contribution.csv`; its log §6 | 2026-09-17 | 2026-09-17 | no |
| 8 | Finimize (paywalled, undated, after 6 Aug): "Airbnb has broadened which stays qualify since launching the option in the US in August 2025 and taking it global in February"; **B. Riley estimates RNPL added 150bp to nights growth in Q2 after 200bp in Q1** at a disclosed share of "over 20%" / "roughly 20%"; Mertz: it "nudges travelers to commit earlier and helps hosts fill their calendars further in advance". No named booking types, no share figure. **Used in revision 2 as the only outside-estimated nights-per-share ratio: 1.5–2.0 pts of nights per ~20 pts of share ≈ 0.075–0.10 per share point (k)** | https://finimize.com/content/airbnbs-reserve-now-pay-later-push-could-keep-bookings-growing (`sources/finimize_rnpl_expansion_2026.txt`) | 2026-08 (undated) | 2026-09-17 | yes (k) |
| 9 | No newsroom or help-centre post names the July expansion; the Feb 2026 global rollout post is the latest RNPL newsroom item found; no market on the disclosure exists (Polymarket search; Kalshi has the nights ladder only, untraded since 29 Jul) | https://news.airbnb.com/reserve-now-pay-later-is-now-available-worldwide ; `sources/polymarket_search_airbnb_20260917T032158Z.json`; `sources/kalshi_markets_KXABNB_open_20260917T032158Z.json` | 2026-02-17 / 2026-09-17 | 2026-09-17 | no |
| 10 | **Joint model, revision 2** (`a09_v2_r03_joint.csv`, adopted row): share drawn with C06 rev 2's exact structure (claim 1); X = the July expansion in share points (mean 1.83, sd 1.90); nights = 9.5 + k·(X − E[X]) + ε with k = 0.10 and ε ~ N(0, √(1.70² − (k·sd X)²)) so the nights marginal is R01's N(9.5, 1.70); disclosure gate = C06's level gate + 0.10·1[accel ≥10.59] + 0.05·1[147.0m ≤ nights < 10.59] − E[lift], centred so C06's unconditional P(a) is preserved; language (a) 0.85 for true ≥ 24.5. Results: P(true ≥25) 0.389, **P(a) 0.249**, P(R01) 0.385, **P(R01 \| a) 0.445**, P(a \| R01) 0.288, corr 0.071, **joint 0.111**, product of marginals 0.096; E[nights \| both] 11.25; within the joint, accelerating 0.70 / flat 0.25 / sliver 0.05; E[X \| both] 3.6 vs 1.8 unconditional | `datasets/a09_v2_r03_joint.csv`, `a09_v2_final.json` | 2026-09-17 | 2026-09-17 | yes |
| 11 | Joint variants (`a09_v2_r03_joint.csv`): independence 0.095; disclosure dependence only (k 0) 0.103; mechanical link only (k 0.10) 0.104; k 0.143 (module base +0.20 / rev-1 mean 1.4) 0.115; k 0.214 (module bull) 0.122; k 0.075 0.109; disclosure lift doubled 0.118; standing-KPI gate 0.90 (C06 a 0.30) 0.133; reframing gate 0.50 (C06 a 0.16) 0.076; July expansion large only (C06 a 0.38) 0.170; small only (a 0.21) 0.090; language (a) 0.70 0.092; nights centre 9.9 0.135; 9.2 0.094; nights sd 1.475 0.108; 2.159 0.116 | `datasets/a09_v2_r03_joint.csv` | 2026-09-17 | 2026-09-17 | yes |
| 12 | Impact inputs: R01 rev-2 impact row; the module's FY27 bull-vs-base 6.88 vs 6.41 (+0.47pt) as a **labelled scenario**; RNPL raises ADR through mix to larger homes (D016, D033) — direction only, magnitude unquantified, **not carried as a number (A09-17)**; brief sensitivities and the held-cost identity as R01 claim 21; S01 rev-2 state means +2.02 / −0.89 / −4.30 | `data/processed/rnpl_short_audit/rnpl_nights_module.csv`; `rnpl_statement_ledger.csv` D016, D033; `00_BRIEF.md`; `23_forecast_annual.csv`; `../day1-move-5nov/datasets/s01_v2_cells.csv` | 2026-09-11 / 2026-09-17 | 2026-09-17 | yes (impact) |
| 13 | Final 72-hour check (batch query 18) and the RNPL-specific query (15): no terms change, no eligibility post, no management comment this week; nothing new | WebSearch (see §2) | 2026-09-17 | 2026-09-17 | no |
| 14 | Audit A09: benchmark R03 0.11 (6–18) from C06 rev 2's (a) 0.25, its rebuilt v2 share draws (true ≥25 0.389, disclosed-(a) 0.248) and a weak common-cause link (k 0.143 → P(R01 \| a) 0.427, joint 0.107; independence 0.094; k 0.214 → 0.113); rev-1 base-rate arithmetic inconsistent (0.16 × 0.55 × 0.7 vs the stated lift 0.51/0.42); retaining the rev-1 conditional with current C06 gives 0.129 | `docs/pitch-forecasts/audits/A09-research-audit.md`; `A09-reproduce.stdout.txt` | 2026-09-17 | 2026-09-17 | yes (audit trail) |

Newest load-bearing source: the C06 rev-2 and R01 rev-2 objects and the computed joint (17 Sep); the ledger rows are 6 Aug (the last management statement on RNPL), 42 days old, which is the age of the newest company statement and cannot be refreshed before the print.

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
19. [computed] `datasets/a09_nights_error_distribution.py` section 7 (revision 1)
20. [rev 2, repo] `audits/A09-research-audit.md`; `../rnpl-gbv-share-disclosed/` revision 2 (log §10, JSON, `share_ramp_model_v2_2026-09-17.py`, `.csv`); `../risk-q3-nights-meets-guide/` revision 2; S01 rev 2 cells
21. [rev 2, computed] `audits/A09-reproduce.py` (exit 0; C06-v2 share rebuild 0.389 / 0.248 and the k sensitivities reproduce) → `A09-reproduce.stdout.txt`
22. [rev 2, computed] `../risk-q3-nights-meets-guide/datasets/a09_v2_print_distribution.py` section 5 → `datasets/a09_v2_r03_joint.csv`, `a09_v2_impact.csv`, `a09_v2_final.json`

WebSearch calls charged to R03: 1 (query 15); batch total 4 of 15; none added in revision 2.

## 3. Leading Hypothesis Entities
Airbnb, Reserve Now Pay Later, Ellie Mertz, July 2026 eligibility expansion, RNPL share of GBV, Nights and Seats Booked, 3Q26 earnings call, 5 November 2026

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| Product of marginals (0.25 × 0.39 = 0.096) | discarded as the method, kept as the floor | The July expansion raises both the share and nights, and management discloses more readily in a strong quarter; the computed joint is 0.111 with P(R01 \| a) 0.445 (claim 10); the two dependences add 0.008 each |
| Retain revision 1's P(R01 \| a) = 0.514 and multiply by the new C06 (a) → 0.129 | discarded | The 0.514 was computed on the withdrawn share model (U(−2,0) penalty, Exp(1.4) only), the withdrawn nights blend (0.424) and k 0.143; every input has moved |
| Strong positive dependence (P(R01 \| a) ≈ 0.7) | discarded | The mechanical link is weak: the only outside-estimated ratio (B. Riley, claim 8) is 0.075–0.10 nights-pt per share-pt, so even the large-expansion draws (E[X \| both] 3.6) add ≈ 0.4pt; corr(a, R01) 0.07 |
| k = 0.143 (revision 1: module +0.20 ÷ C06 rev-1 mean 1.4) | discarded as the central value; kept as a sensitivity (0.115) | A ratio of two team assumptions with no measured analogue (rev-1 RESUME); B. Riley's Q1/Q2 estimates give a measured-analogue ratio at the low end; k = 0.10 adopted, 0.075–0.214 spanned |
| The July expansion is large (Firm-policy listings, longer stays, Experiences eligible) | inside C06 rev 2's mixture (25% weight on Exp(3.5)); C06's large-only sensitivity gives (a) 0.38 → R03 0.17 | C06 rev 2 no longer caps the share; the joint follows it |
| Management restates the share as "over 20%" even at a true 25% | inside C06's language map (0.85 → (a); 0.10 → (c)) | Rounding habit (D022, D031, D043) |
| Share given as nights-share or bookings-share only | inside C06's (d) | Airbnb has always used the GBV basis for this metric |
| Nights ≥10 comes from non-RNPL sources with the share flat | this is the R01-not-R03 path, 0.39 − 0.11 = 0.28 | The reviews index's regional texture (LatAm +27, APAC +10) is demand-mix, not RNPL |
| A Yes proves the lap thesis wrong | discarded (A09-16) | The card says "weakens"; resolution is a joint observation, and R03 itself keeps a non-RNPL nights path; the FY27 offset is a labelled scenario in §9, not an implication |

## 5. Independent Estimates
- base_rate_estimate: NOT_INDEPENDENTLY_DERIVED — there is no reference class for the conjunction; the independence product 0.25 × 0.39 = 0.096 is the floor and reuses C06's share model and R01's object (revision 1's "0.16 × 0.55 × 0.7 ≈ 0.06" is withdrawn: the multiplier was unexplained and the arithmetic with the stated lift gave 0.107, A09-08)
- decomposition_estimate: 0.11 — the computed joint (claim 10): C06 rev 2's share model and level gate, R01 rev 2's N(9.5, 1.70), a common-cause link k = 0.10 nights-pt per share-pt of expansion (claim 8), and a disclosure lift of +0.10 on an accelerating print / +0.05 on a meet, centred so C06's marginal is preserved
- anchor_estimate: NO_EXTERNAL_ANCHOR — no market prices the share or the joint; the Kalshi nights ladder is untraded since 29 July (R01 claim 14) and is not used even as a reference
- anchor_value: n/a
- final_estimate: 0.11 (credible interval 0.07–0.15)
- final_minus_anchor: n/a. One estimate, not three: the number is the decomposition, and its uncertainty is C06's (a) (0.16–0.30 across C06's own sensitivities → 0.08–0.13) and R01's centre (9.2–9.9 → 0.09–0.13) more than the link (0.10–0.12 across k). Coherence: R03 ≤ min(C06 a = 0.25, R01 = 0.39) holds; R03 / R01 = 0.29 is the share of R01-Yes worlds in which a ≥25% share is also disclosed; P(a \| R01) 0.29 vs C06's 0.25 unconditional. Against Astra's 0.11: same number; Astra used k 0.143 without the disclosure lift (0.107), this log k 0.10 with it (0.111)

## 6. Final Numbers
**Binary.** P(C06 = (a) and R01 = Yes) = **0.11** (0.111), credible interval **0.07–0.15** (the variants in claim 11 span 0.076–0.170; the ends are C06's disclosure-gate and expansion-size sensitivities, which belong to C06).

Decomposition of the 0.11: P(true share ≥ 24.5) 0.39 × P(disclosed as a 3Q26 GBV share | true ≥25) 0.75 × P(language (a) | true ≥25) 0.85 = P(a) 0.25; × P(nights printed ≥ 147.0m | a) 0.445 = 0.111. The lift from 0.386 to 0.445 is half the mechanical link (k 0.10 on an expansion averaging 3.6 share points in the (a) worlds) and half the disclosure dependence. The disclosure gate is the binding filter: conditional on the true share being ≥25 and nights ≥10, the question still resolves No about 36% of the time because the share is not stated, or is stated as "over 20%" / "nearly a quarter".

Extreme-probability gate: not triggered (0.11 > 0.05). Resolution audit anyway: (i) both legs read from the 5 Nov release set; (ii) a call-only share counts (C06 convention 1); (iii) a nights-share-only disclosure is No; (iv) a share stated for "the year to date" is No (C06 convention 3); (v) the nights leg uses R01's fixed-denominator and rounding conventions.

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|
| C06 (a) = 0.25 (rev 2) | Standing-KPI gate 0.90 ((a) 0.30): 0.13; reframing gate 0.50 ((a) 0.16): 0.08; July expansion large only ((a) 0.38): 0.17; small only ((a) 0.21): 0.09; language (a) 0.70: 0.09 |
| R01 = 0.39 (centre 9.5, sd 1.70) | Centre 9.9: 0.135; 9.2: 0.09; sd 1.475: 0.11; 2.159: 0.12 |
| Nights per share point k = 0.10 | k = 0 (disclosure dependence only): 0.10; 0.075: 0.11; 0.143 (module base ratio): 0.115; 0.214 (module bull): 0.12 |
| Disclosure lift +0.10 accel / +0.05 meet | none: 0.104 (k only); doubled: 0.12; full independence: 0.096 |
| Joint structure | Product of marginals 0.096 (floor); revision-1 conditional 0.514 × C06 rev 2: 0.129 (rejected, §4) |

Pre-mortem ("it is 5 Nov and both legs resolved Yes"): (1) **the July expansion was big** (Firm-policy listings or long stays made eligible) and management, proud of it, gave "a quarter of GBV" alongside a 10%+ print; this is C06's large-expansion world (R03 0.17) and it is where the memo's RNPL leg is weakened most; the impact row carries the lap-offset scenario as a labelled line. (2) **The share rose on the ex-US ramp alone** (Q3 is the first full quarter with UK/AU/APAC/CA at maturity) and nights cleared 10 for unrelated reasons; priced as the independence path (0.096). (3) **Disclosure habit**: the share becomes a standing KPI like app share (gate 0.90), priced at 0.13. ("It resolved No although the true share was ≥25 and nights ≥10"): (4) management said "over 20%" again or moved to a year-to-date figure; this is the disclosure filter and the reason the number is 0.11 rather than 0.17. Asymmetry: R03's role in the memo is the "both risks at once" line; at $0.7/share of EV it is worth one sentence inside R01's line, not a row of its own.

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
| 2026-09-17 to 2026-10-31 | Airbnb newsroom / help-centre changes naming the July-expanded booking types (policy types, stay lengths, hotels, Experiences) | A named expansion to Firm-policy listings or long stays: C06 moves to its large-expansion row ((a) 0.38) and R03 → 0.17; a restriction: C06 (a) ≤ 0.15, R03 ≤ 0.07 |
| 2026-09-18 to 2026-09-30 | September Inside Airbnb dumps; R01 re-centred by its §8 rule | R03 ≈ 0.29 × P(R01) at the new centre (`a09_v2_final.json`, `monitoring_rule`): centre 9.2 → 0.09; 9.9 → 0.14; re-run the v2 script for the exact joint |
| 2026-10-02 | Prelim memo | Quote 0.11 (0.07–0.15) as the "both at once" line; state that it is inside R01's EV and immaterial on its own |
| 2026-10-26 to 2026-11-04 | Sell-side previews modelling an RNPL share | Any preview at ≥25%: C06 +3 pts on (a) → R03 +0.013 |
| 2026-11-05 (after close) | 3Q26 letter (governs), call, 10-Q | Resolve both legs; if the letter gives the share, ignore the call; record the pair (share, nights) on the pre-registered card (claim 6) as "weakens" / "supports" / "inconclusive", not as proof either way |

## 9. Impact
If both legs happen (nights printed ≥ 147.0m with a disclosed RNPL share ≥25%), the memo loses its print sign and the pre-registered card reads "weakens" on its RNPL-drag leg. Deltas versus the memo's base case (`datasets/a09_v2_impact.csv`, R03 row; conditional on both legs from the joint draw):

| Item | Delta if R03 happens | Source / computation |
|---|---|---|
| 3Q26 nights (pts) | **+1.7** (E[nights \| R01 and a] 11.25 − 9.5; 0.06 above R01's conditional mean because the (a) worlds carry a larger expansion) | joint draw, claim 10 |
| 4Q26 nights (pts) | **+1.0** (60% persistence; **judgement**) | as R01 |
| FY27 nights (pts) | **+0.7** (40% persistence; **judgement**) | as R01 |
| ADR (pts) | 0.0 (the larger-home mix effect, D016/D033, is a direction with no measured magnitude; revision 1's +0.3 withdrawn, A09-17) | — |
| 3Q26 revenue ($M) | +84 (1.75 × $48M); GBV +$414M | brief sensitivity (context) |
| 4Q26 revenue ($M) | **+65** = ⅔ × $414M × 12.03% + 1.05pt × $30M | kernel carry + brief sensitivity |
| FY27 revenue ($M) | **+110** (0.70pt × $158M) | brief sensitivity |
| FY26 adj. EBITDA margin (pp) | **+0.66 held** ((5,098 + 148) / (14,268 + 148) − 35.73%); +0.42 flex | A09-14 |
| FY27 adj. EBITDA margin (pp) | **+0.45 held**; +0.29 flex | A09-14 |
| FY27 EPS ($) | **+0.15 held** ($110M × $0.0014); +0.12 flex | A09-14 |
| Stock ($/share), 5 Nov reaction session | **+6.2 vs the R03-No world** (E[day-1 \| both] +1.0% from S01 rev-2 state means at the joint's within-event mix accel 0.70 / flat 0.25 / sliver 0.05, against −2.7% in the complement, which contains the R01-Yes-but-not-(a) worlds: +3.7pt × $167.51); +5.5 vs the unconditional (−2.3%); +9.4 vs the memo's base-case cell (−4.6%). S01 has no RNPL-share dimension, so the disclosure adds nothing to the reaction beyond the nights mix | S01 rev-2 `s01_v2_cells.csv`; A09-12 |
| Fundamental re-rating line (separate horizon, **not added**) | +$2.9 (0.70pt × 0.44 × $9.5) | A09-13 |
| **Lap-offset scenario (labelled, not in EV; A09-16)** | If the expansion is also what removes the FY27 lap drag (module bull vs base): FY27 nights +0.47pt more → revenue +$74M, EPS +$0.10 held, re-rating line +$2.0; this is what a Yes "weakens" toward, not what it establishes | `rnpl_nights_module.csv` FY27 6.88 vs 6.41 |
| **EV = P × impact** | **0.11 × $6.2 = $0.7/share** (vs the R03-No world); 0.11 × $9.4 = $1.0 vs the base-case cell | published rounded inputs (A09-19) |
| Materiality | **Immaterial on its own** (< $1/share vs the complement; $1.0 vs the base-case cell is the margin). It is a subset of R01 (0.11 of 0.39) and must not be added to R01's or R02's EV. The memo can carry it as one sentence inside the R01 line: "if the share is a quarter of GBV and nights hold 10%, the pre-registered card reads 'weakens' on the lap thesis" — not "the lap thesis is wrong" | |

## 10. Revision notes
| Change | Finding |
|---|---|
| Metadata: revision 2, revised 2026-09-17; reproduction and upstream paths in the header | — |
| Rebuilt on C06 revision 2 ((a) 0.25; v2 share model with the level gate and the expansion mixture; the U(−2,0) penalty gone) and R01 revision 2 (N(9.5, 1.70), 0.39); final 0.07 → **0.11** | A09-03, A09-01 |
| Convention 5 added: resolution is a joint observation, not causal proof; §4 row and §9 wording changed from "wrong" to "weakens" | A09-16 |
| §5 base-rate estimate withdrawn (unexplained 0.7 multiplier); NOT_INDEPENDENTLY_DERIVED and NO_EXTERNAL_ANCHOR stated; no third estimate invented | A09-08 |
| Claim 5 rewritten: the two 70% figures have different denominators; saturation is an assumption; adoption and mix paths allowed | A09-09 |
| One joint draw for the probability and the impact (nights marginal = R01's object; E[nights \| both] from the same draw; S01 mix conditioned on both legs) | A09-11, A09-12 |
| k = 0.143 (ratio of two team assumptions) replaced by k = 0.10 from the only outside-estimated analogue (B. Riley, claim 8); 0.075–0.214 spanned; the disclosure lift centred so C06's marginal is preserved | rev-1 RESUME item (1), A09-03 |
| ADR +0.3 withdrawn (unquantified; not propagated); driver and financial rows now consistent | A09-17 |
| FY27 lap-offset (+0.47pt module scenario) moved out of the deltas into a labelled scenario line, excluded from EV | A09-16 |
| Margins as annual ratios under held costs; EPS $M × $0.0014; flex beside them | A09-14 |
| Stock line from S01 rev 2 conditioned on both legs vs the complement; reaction and re-rating separated; EV $1.6 → **$0.7**; materiality Material (marginal) → **Immaterial** | A09-12, A09-13, A09-19 |
| Claims 1, 2, 8, 10–12, 14 rewritten; queries 20–22 added | — |

## RESUME
Revision 2 is C06 rev 2 × R01 rev 2 with a weak, centred dependence. The next agent should re-run section 5 of `../risk-q3-nights-meets-guide/datasets/a09_v2_print_distribution.py` whenever C06 or R01 moves (the joint is ≈ 0.29 × P(R01) at C06 (a) = 0.25, and ≈ 0.445 × P(a) at R01 = 0.39). The remaining soft spots are C06's disclosure gate (0.50–0.90 spans 0.08–0.13 here) and C06's expansion prior (0.09–0.17); the link k matters less (0.10–0.12). Nothing on the web can refresh the 6 Aug statements before the print.
