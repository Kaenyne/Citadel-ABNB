# 43c — pre-registration: does cutting marketing cost Airbnb nights, and how does the cost thesis play through 5 Nov / 11 Feb

Written 22 Sep 2026 (Krish with Claude, Fable 5.1), on branch `krish/cost-leg`, worktree `citadel-abnb-marginaudit`, **before** any
nights-growth numbers for 3Q23–2Q24 or any peer room-night series were read for this package. Read so far: `42_event_reasons.md`,
`42_margin_reaction.md`, `41_cost_leg.md`, `40_line_build.md` (short-case table), `M6_cycle_flex.md` (asymmetry table, E3 dummies,
cut caps), the C-02 audit finding, `final_income_statement.md` §8, the B03 / B12 / C04 / C09 / F03 / R05 research-log summaries and the
C04×C09 joint. Disclosure: I hold general knowledge of Airbnb's reported nights growth series from memory; the pre-registration is
therefore about what *counts*, not about ignorance of the series. The S&M growth path (+28.6% 2Q23 → +3.8% 3Q23) is already known
from M6/B03.

## Question 1. Does a marketing cut cost nights? ("tails we win")

The claim under test: if management trims 4Q26 marketing to hold the FY26 "at least 35.5%" floor ($64M–$177M of Q4 marketing,
12.6%–35% of the quarter's line, `40_line_build.md` / C-02), nights growth slows further, so the short wins on revenue instead of margin.

**Episodes and the object measured.** Reported nights y/y growth (company total; regional where disclosed) in the 1–3 quarters after a
visible S&M deceleration, against (i) the prior two-quarter trend and (ii) peers' room-night growth over the same quarters (BKNG and
EXPE room nights, from the peer-readthrough package if present in the repo; otherwise from the letters/press, cited).

- **E-2023.** S&M y/y growth +28.6% in 2Q23 → +3.8% in 3Q23 (M6). Post-window: 3Q23, 4Q23, 1Q24 (h = 0, 1, 2 from the cut).
- **E-2020.** 2Q20 S&M −54% y/y (brand marketing paused). Confounded by the pandemic; scored qualitatively only (S-1 / letters on
  traffic mix), never as a pass/fail.
- **E-4Q24.** Q4 2024 S&M +27.5% y/y with nights +12% (accelerating from +8.5%); the *reverse* direction (spend up → nights up).
  Scored as association only.
- **E-2025/26.** "Paid growth initiatives in emerging markets" (10-Q 1Q26/2Q26; S&M +24% to +33% y/y from 3Q25). Test whether the
  regions named (Latin America, Asia Pacific) show nights-growth acceleration ≥ 3pts versus their 2024 average in the quarters of the
  step-up, while North America/EMEA do not. This is the symmetric test (spend buys nights ⇒ cutting spend costs nights).

**Pass line for "marketing cuts cost nights" (E-2023), registered now:**

- PASS if company nights y/y growth in the average of h = 1, 2 (4Q23, 1Q24) is **≥ 2.0pts below** the average of h = −2, −1 (1Q23,
  2Q23) **and** that deceleration **exceeds the peer deceleration by ≥ 1.0pt** over the same quarters (BKNG room nights as the primary
  peer; EXPE as a check), **and** the two-year stacked growth (to remove the 2022 reopening base) also decelerates by ≥ 1.0pt.
- FAIL if any of the three conditions is not met. A FAIL means "no evidence in the one clean episode that a marketing deceleration
  cost nights within three quarters", not proof that spend is inert.
- Confounders acknowledged in advance: 2023 was the ADR-normalisation year with an easy 1H22 base; the S&M drop was mostly a
  brand-campaign *phasing* (front-loaded 1H23), not a performance-marketing cut; the 2026 spend is paid/performance in emerging
  markets, which is a different elasticity. Any PASS/FAIL is therefore quoted with these caveats and n = 1 episode.

**Pass line for E-2025/26 (symmetric):** SUPPORTED if LatAm and APAC nights growth (as disclosed in the letters) rose ≥ 3pts versus
their 2024 average in ≥ 3 of the 4 quarters 3Q25–2Q26, while NA/EMEA did not rise by that much. Otherwise NOT SUPPORTED.

**Verdict rule for "tails we win":** HOLDS only if E-2023 PASSES or E-2025/26 is SUPPORTED with the mechanism explicit (paid nights in
emerging markets are the marginal nights a Q4 cut removes). Otherwise the verdict is "tails is a mechanism claim, not an evidenced one",
and the memo may carry it only as a stated assumption with the dollar arithmetic beside it. I will also record management's own words
on brand vs performance and on the direct/organic traffic share (05_statements.csv, letters, S-1 via web if needed) regardless of the
outcome.

## Question 2. Decision tree (no test; construction rules fixed now)

Branches on 5 Nov are defined by the C04 × C09 joint (`mc_joint_and_conditionals_v2.json`), with B03 and R05 as overlays:

| Branch | Definition in audited objects | Probability source |
|---|---|---|
| T1 "spend held, costs flagged" | C09 = (a) down y/y, or C09 = (b) flat with C04 = (d) softened | joint cells `*a` + `db` |
| T2 "spend trimmed to hold the floor" | C04 = (a) held **and** C09 ∈ {b, c}, plus the B03 tell inside it | joint cells `ab` + `ac`; B03 0.18 |
| T3 "costs fall on their own (AI support / G&A), sentence up y/y" | C04 ∈ {b, c} and C09 = (c) | joint cells `bc` + `cc` |
| T4 "sandbag beat" | R05 = Yes (3Q26 ≥ 51.5%) — overlay, not a joint cell | R05 0.22 |
| Residual | everything else (e-rows, `bb`, `bd`, `dc`, `dd`, ...) | remainder |

Street FY27 EBITDA response per branch uses the 41 scenario rows (−100/−150/−200bp × 0/−2/−4% revenue) and 42's slope range
(2.1–2.7 per 1% NTM cut, plus the constant-multiple ~1x row). Where a branch maps to a *positive* revision I use the same slope with the
sign reversed (the regression is symmetric by construction) and say so. February branches use B12 (0.49 literal / 0.36 material) and
F03 (d 0.36 / e 0.48). I will not add a February price reaction on top of S03 (B12 §9 rule).

## Question 3. Watch list / kill criteria (thresholds fixed now)

Thresholds for 5 Nov, set before the print:
- 3Q26 S&M print vs the line-build budget ($778–781M): ≤ $724M means the Q3 step never came (R05 arithmetic); ≥ $800M means spend
  is running ahead of budget.
- 3Q26 cost of revenue vs the $575M 4Q26 threshold (DEC-0023) and the 41 T3 record (above LSEG COGS in 11 of 14).
- 10-Q S&M split: brand vs performance vs field (the 10-K gives the annual split; the 10-Q gives the y/y driver sentence).
- Letter Q4 margin sentence: names a cost line (3Q24 form) = T1 confirmed; "up y/y" = T3 (cost leg hurts).
- "2027 investment plans" phrase or a 2027 launch budget = B12 T5 regime (0.60 literal).
- FY26 sentence: held / approx 36% / softened per C04.
Kill criteria for thesis 3 (cost leg) are written into 43c_catalyst_path.md from these, before the print.

## Question 4. Host-only fee migration (13 Oct 2026)

A sourced paragraph; the pre-registered answer space is {touches payment processing / chargebacks / support; take-rate only; no cost
effect found}. No test.
