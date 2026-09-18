# Response to audit A10 (R04, R05, R07; B02 revised for coherence)

Response date: 2026-09-17
Responds to: `A10-research-audit.md` (independent Opus auditor standing in for Codex, read-only)
Revised research: `questions/risk-single-fee-take-rate-accretion-stated/research-log.md`, `questions/risk-q3-margin-sandbagged/research-log.md`, `questions/risk-adr-residual-persists/research-log.md` (all revision 2); `questions/bonus-adr-residual-reverts/research-log.md` (revision 2, coherence revision under A10-03 only)
Revised forecasts: each question's `forecasts/2026-09-17-forecast.json` (revision 2)
Revised models: `risk-q3-margin-sandbagged/datasets/r05_model_v2.py` → `r05_results_v2.csv`; `risk-adr-residual-persists/datasets/adr_joint_model_v2.py` → `adr_joint_results_v2.csv` (written into both the R07 and B02 folders); `risk-single-fee-take-rate-accretion-stated/datasets/r04_extract_v2.py` → `r04_statement_hits_v2.csv`, `r04_statement_record_v2.csv`, `r04_decomposition_v2.csv`. Revision-1 scripts and CSVs are left untouched as the audit trail.
Reproduction script: `A10-reproduce.py` (the audit's script, saved verbatim from the audit file; ran clean from the repo root with `py -3.13 -B`, exit 0, no path fix needed; output in `A10-reproduce.stdout.txt` and at the end of this file).

## Summary

Twenty-five findings. Twenty-four accepted, one accepted in part (A10-19), none rejected. Every number in the audit reproduced: the R05 identity (4,804.04 − 2,405.03 + 20.63 = 2,419.64 = the line build's adj_ebitda), the corrected Monte Carlo (0.2806 at the published cost sd), the R07 mixture (0.1076 / 0.1728), the Normal carrying the rev-1 pair (N(3.18, 1.28)), the R04 route arithmetic (0.392063 / 0.574444), the FY27 margin on the new denominator (+0.793pp), the MODL anchor (0.0958, 94.6% of range), the 2Q26 call readings and the unparseable statement record. The three critical findings each changed the object being forecast, not just its number.

Headline numbers, revision 1 → revision 2:

- **R04** 0.58 (0.42–0.72) → **0.52 (0.38–0.66)**. The 2Q26 print is rescored No under the log's own conventions (A10-04), the two-print base rate becomes a dependence range 0.25–0.44 (A10-05), and convention (3) is loosened (A10-07). The impact is re-priced as a statement (A10-01): expected stock +$2.2 (0.90 direction-only at +$1.5, 0.10 quantified at +$8), **EV $4.1 → $1.1/share, borderline material**.
- **R05** 0.17 (0.10–0.27) → **0.22 (0.13–0.32)**. The cost-stack identity now carries the D&A add-back (A10-02): the Monte Carlo is 0.28–0.31, not 0.19, and it is a line-build object (centre 50.37/50.67), not the card. The final is a stated four-route blend (card bias-corrected 0.35 / corrected cost stack 0.25 / M5 0.20 / ceiling base rate 0.20 = 0.219). The 5 Nov threshold is S&M ≤ $724M = +23.7% y/y (A10-21), not $706M / +20.7%. EV $0.5 → $0.8, still immaterial.
- **R07** 0.17 (0.10–0.28) → **0.17 (0.11–0.27)** — the same number, now the model's own headline rather than a ×1.5 lift on 0.11: the K line is restored and half the walk-forward bias is applied to the centre (A10-03, A10-12, A10-13). Impact priced at E[ADR | Yes] = +4.95 for coherence with B02: stock +$10, EV $1.2 → $1.7, material.
- **B02** 0.18 (0.10–0.30) → **0.12 (0.07–0.20)**, read from the same draws as R07 (A10-03). Impact −$12, EV −$2.2 → −$1.4, material.

What actually moved the numbers: for R05 the identity fix (+0.09 on the decomposition, +0.05 on the headline); for R04 the 2Q26 rescoring (base rate 0.61 → 0.34) and, on the impact, the recognition that a statement changes the market's mark and not the fee's arithmetic (EV −$3.0); for the ADR pair, one distribution centred +3.4 replaces two mixtures each quoted in the direction that made its own risk look bigger (R07 unchanged, B02 −0.06).

## Finding-by-finding

### A10-01 (critical, R04) — impact prices a statement as a delivered take-rate step: accepted
Reproduced: `fee-takerate.md` §3 (n 20, slope −105.7bp per unit share, t −0.24, permutation p 0.730; "the printed take rate must be treated as an OUTPUT"), §1 (migrated-cohort GBV −1.6 to −2.3% in every θ row below 1), §5 (FY27 migration line +23.7bp central, i.e. the team's own mechanism build already carries what a "+20bp" statement would say). A statement changes what the sell-side marks, not what the fee does; the memo's path already carries the migration. Fix: §9 split by the form of the Yes — direction-only/gross (0.90 of the Yes mass; revenue delta 0; sell-side mark of a few bp ≈ +$1.5/share) and quantified (0.10; +$230M FY27 revenue marked in full, +$207M EBITDA, level +$5.6 on 591.7m shares plus multiple +$6.1, haircut to +$8). Expected conditional on Yes: FY27 revenue +$23M, margin +0.09pp, EPS +$0.03, stock +$2.2; **EV 0.52 × 2.2 = $1.1/share, borderline material** (auditor: +$2, EV $1.0 at P 0.52). Claim 16 added; §4 row added; the memo's reply is pre-written in the EV line.

### A10-02 (critical, R05) — cost-stack identity drops the D&A add-back: accepted
Reproduced on `40_lines_quarterly.csv` 3Q26 base: cash lines sum to 2,405.027 = `total_cash_costs`; revenue − cash = 2,399.009 (the rev-1 MC centre, 49.937%); revenue − cash + da (20.634) = 2,419.642 = `adj_ebitda` (50.367%); revenue − cash − sbc = 1,947.429 = `op_income`. The line build's own parameter sheet says "D&A $21M/q" (`40_line_build.md` line 40). So the rev-1 MC was the line build mislabelled as the card. Fix: `r05_model_v2.py` computes margin = (revenue − cash costs + D&A) / revenue: P(≥51.5) 0.280 at the published cost sd 60 (auditor 0.2806), 0.309 at sd 72 (A10-19); median 50.67; P(above the ceiling) 0.64–0.66. The object is now called what it is — management's budget with a slip skew — and the card enters the headline as its own route. The 3Q25 identity's implied $27M includes other adjusted-EBITDA add-backs, so $20.6–27M brackets the add-back (0.43–0.56pp); a $27M add-back moves the cost stack to 0.31 and the headline by less than a point (sensitivity row).

### A10-03 (critical, R07 / B02) — two distributions for one printed number: accepted
Reproduced: the rev-1 mixture gives 0.1076 / 0.1728 (median 3.120, sd 1.121); the Normal carrying the published pair 0.17 / 0.18 is N(3.18, 1.28) — centre below both cards, sd 38% above the walk-forward RMSE. Fix: one model, `adr_joint_model_v2.py`, with the card's mix −1.16, the K line +0.17 as a separate term, B02's four-branch residual mixture (it is the more complete one and includes the fitted AR(1)), the FX mixture, and a +0.15 centre adjustment (half of −0.308). **P(≥4.4) 0.172, P(≤2.0) 0.119**, median 3.40, mean 3.35, sd 1.12; the Normal carrying both revision-2 tails is N(3.33, 1.13) — centre between the without-K and with-K cards, sd 21% above RMSE, which the FX-estimator choice and the geographic-mapping error justify. B02's log is revised to revision 2 on the same draws; every conditional and sensitivity in both logs comes from one run and integrates to its headline. **C11 implication**: C11 revision 2 adopted the rev-1 B02 mixture (mean +3.04) as its ADR input; the joint model's mean is +3.35, which lifts C11's print-state GBV centre by ≈ $80M and, by C11's own sensitivity (≈ −0.11 per ADR point), takes C11 from 0.76 to ≈ 0.73. Recorded in both ADR logs and flagged for X01; C11 is not edited here.

### A10-04 (major, R04) — 2Q26 scored a half-Yes against the log's own convention: accepted
Re-read the 2Q26 call mirror in full and re-extracted every sentence containing the fee keywords (`r04_extract_v2.py`, 61 hits across the four prints). The fee is named three times on the 2Q26 call: "helped our host price more competitively and provided greater price transparency" (prepared remarks, as one of two changes that "contributed to our strong growth"), "in aggregate, has a kind of downward pressure on pricing" (Q&A), and Chesky's "prices have become more competitive". The accretion sentence ("driven by our monetization initiatives and execution across our product roadmap") enumerates nothing. Under conventions (1) and (5) that is a No. Per-print base 1/4 = 0.25 (Laplace 0.33). Convention (1) now says explicitly that a naming in a host-pricing, guest-value or growth framing does not count.

### A10-05 (major, R04) — two-print base rate assumes independence: accepted
Reproduced 1 − 0.625² = 0.6094. The base rate is now a range: 0.25 (perfectly correlated) to 0.4375 (independent), midpoint 0.34, in `r04_decomposition_v2.csv`. The "two estimates agree within 4 points" sentence is withdrawn; §5 now says the base rate and the decomposition disagree by 23 points because of the dependence structure, and states the blend weights (0.50 decomposition / 0.25 base / 0.25 prior → 0.49, rounded to 0.52 for A10-07).

### A10-06 (major, R04) — FY27 margin on the old denominator; share count: accepted
Reproduced: FY27 revenue 15,828.6, EBITDA 5,483.3 (34.642%); +$230M at 90% flow-through → 35.435% = +0.793pp; the brief's rule gives +0.959pp. Rev 1's +1.3pp withdrawn. Shares: the line build's 591.7m replaces 620m in all three impact tables and in B02 ($207M × 16 / 591.7 = $5.6 vs $5.3).

### A10-07 (major, R04) — convention (3) narrowed the Yes space asymmetrically: accepted
The qualifier "only if it explicitly covers Q4" is dropped: with one quarter left, an FY26 take-rate statement at 5 Nov is a statement about 4Q26, and the base rate already counts the 1Q26 FY26 statement in full. Effect: a small addition to the letter route (an FY26 reiteration of the 1Q26 sentence is the cheapest Yes path, made less likely by the 2Q26 walk-back), carried as +0.02–0.03 on the final (0.49 → 0.52) and as a sensitivity row (rev-1 convention: 0.50).

### A10-08 (major, R05) — ceiling / Street threshold conflation: accepted
Reproduced: 1 − Φ((49.776 − 49.940)/1.6232) = 0.5403 (the card's P(beat Street)); 1 − Φ((50.085 − 49.940)/1.6232) = 0.4644. The companion is now quoted per route: card raw 0.46, card bias-corrected 0.53, M5 0.53, corrected cost stack 0.64–0.66, blend ≈ 0.55; the JSON carries all five and the note that the card's 0.54 is P(> Street).

### A10-09 (major, R05) — ad-hoc haircut double-counts the 2025 "down" prints: accepted
Both prints are rows in `r05_ceiling_record.csv` (excess −2.4, −2.5) and two of the nine non-qualifiers behind the Laplace 0.167. The haircut is removed; claim 10 says so.

### A10-10 (major, R05 ↔ C04) — C04's N(49.95, 1.0) implies P(≥51.5) 0.06: accepted (recorded, not edited)
Reproduced 0.0606. The card's conformal sd is 1.62 (W2) / 1.72 (W1), at which P(≥51.5) is 0.168–0.182; C04's own sensitivity row (sd 1.6 → (c) 0.08) shows the tail is live at the card's real spread. C04 is not edited (its response is closed); the R05 log's claim 11, its JSON `cross_question` field and this file record the joint value for X01: use the card at sd 1.62 across C04, C09 and R05 (P(≥51.5) 0.17–0.21), and treat C04's sd 1.0 as the outlier.

### A10-11 (major, R05) — C04 channel valued off a superseded vector: accepted
C04 rev 2: (a) 0.33, (b) 0.30, (c) 0.05, (d) 0.27, (e) 0.05; its rows for a 3Q26 print of 50.4 ((b) 0.36) and 52.4 ((b) 0.46, (c) 0.34) interpolate at 51.5 to (b) ≈ 0.43, (c) ≈ 0.20: +13pt and +15pt, not +6pt. Stock +3 → +3.5 (level +$1.7 on 591.7m shares plus ~$1.5–2 through the sentence-reaction correlation); EV 0.22 × 3.5 = $0.8, still immaterial.

### A10-12 (major, R07) — two centres, and the decomposition estimate was a sensitivity row: accepted
Reproduced from `adr_card_v3.csv`: mix = `adr_exfx_yoy_pp − residual_pp` = −1.160 in all six 3Q26 rows; with-K residual 5.02. The rev-1 MC's "−1.15 (J3 fills)" was the card's mix and its "−0.98 (H fills)" was the same mix plus the K line; the persistence branch reproduced the without-K card. The joint model carries mix −1.16 and K +0.17 separately, so its persistence/midpoint branch is the with-K card (+3.43); the decomposition estimate is the model's headline (0.17); the "mix −0.98 = the card's own" label is withdrawn from both logs.

### A10-13 (major, R07) — final above all three estimates via a non-uniform lift: accepted
Reproduced the Gaussian routes (0.1478 / 0.2376 midpoint; 0.3677 / 0.4803 baskets; 0.0644 / 0.1201 euro). The bias is now applied to the centre — half of it, because n is 10, the bias is concentrated in 1Q24 and 3Q25, and B02's direction split shows it is −0.69 in accelerations and +0.07 in decelerations — and the conditionals fall out of the model (FX ≥ +0.2 → 0.49; midpoint → 0.13; euro → 0.01; ex-FX "5%" → 0.56, "4%" → 0.11; they integrate to 0.172). Sensitivity: no adjustment 0.14, full adjustment 0.22.

### A10-14 (minor, R04) — "overlap ρ 0.5" undefined: accepted
Reproduced (independence intersection 0.070875, blended 0.147937, union 0.392063, total 0.574444). The rule — intersection = L·C + ρ·(min(L, C) − L·C); union = L + C − intersection — is stated in claim 15 and as a row of `r04_decomposition_v2.csv`.

### A10-15 (minor, R04) — statement record does not parse; extraction script missing: accepted
Reproduced the `ParserError` on line 4. `r04_extract_v2.py` is shipped: it re-extracts every keyword sentence from the four letters and call mirrors (61 hits, all fields quoted, `r04_statement_hits_v2.csv`), writes the hand-classified four-row record with `csv.QUOTE_ALL` (`r04_statement_record_v2.csv`, asserted to parse), and writes the decomposition. The rev-1 file is left in place.

### A10-16 (minor, R04) — 4Q26 revenue line mixes a print step with a market re-rating, and misstates C01: accepted
C01 rev 2 carries the fee at 45/40/15 over 0 / +0.55% / +1.11%: expected step $12.3M, full step $35.3M, delta +$23.0M (reproduced). The $12M re-rating is moved to the stock line. The 4Q26 revenue line is now +$15M and labelled a market mark (the 5 Nov-route share ≈ 0.65 of the Yes mass × +$23M; a February statement comes after the 4Q26 print), with the print itself unchanged by a statement.

### A10-17 (minor, R04) — "+51–58bp" and the omitted GBV offset: accepted
The θ table gives 14.99 → 15.50 (+51bp) in every row; 58bp mixed in the payout-neutral listed reprice. Claim 5 now reads +51bp and carries the migrated-cohort GBV −1.6 to −2.3% and the FY27 GBV growth contribution −0.62pp; §9 says the mechanism is a ratio effect, not a clean add.

### A10-18 (minor, R05) — MAE-Gaussian 1.30 used as an sd: accepted
`23_bands.csv` `gaussian_from_mae_80` = 1.2971 is an 80% half-width; sd 1.012 → P(≥51.5) 0.0616 (reproduced). The row is relabelled in claim 5 and `r05_model_v2.py`; the "0.12" low bracket is withdrawn; the sd-1.01 route is not used because it is narrower than the card's own conformal band.

### A10-19 (minor, R05) — MC total sd 1.42 vs conformal 1.62: accepted in part
Reproduced sd 1.421. Accepted: the cost sd is widened 60 → 72 so the MC's total sd (1.65) matches the card's conformal 1.62, and that version (0.309) is the decomposition estimate; the rev-1 sd is kept as a sensitivity (0.280). In part: the MC's centre is management's budget, which has no walk-forward record at all, so matching the *spread* of the calibrated object does not make the route calibrated; that is why the cost stack carries a quarter of the headline weight and the card (the only walk-forward-calibrated object) carries the most. The widening moves the headline by less than a point.

### A10-20 (minor, R05) — de-duplication mis-described; W2 MAE 0.79 vs 0.808: accepted
`r05_model_v2.py` runs both choices (keep the 2Q25 h=2 row, or the 3Q25 h=1 row, for the 4Q25 target): both give n 10, 1 at ≥1.4pp, 2 above, Laplace 0.167. Claim 3 describes the operation correctly and says the h=1 sentence is the true analogue; claim 5 reads 0.81.

### A10-21 (minor, R05) — 5 Nov audit-read rule calibrated on the wrong identity: accepted
Reproduced: with the add-back, 51.5% at $4,804M allows cash costs ≤ $2,350.6M, S&M ≤ $724M = +23.7% y/y (at $4,744M: $695M, +18.8%; at $4,850M: $746M, +27.6%). The thresholds are restated in claim 7, §8 and the JSON; the memo line becomes "Yes needs S&M growth to decelerate by about three points from 2Q26's +26.6%", not "to halve"; the audit-read rule is S&M ≤ $724M with revenue ≥ $4,800M → pre-print P should have been ~0.40. The corrected threshold is a weaker reply than revision 1 believed, and the log says so.

### A10-22 (minor, R07) — "0 of 7" and "96th percentile": accepted
Reproduced: six FX ≤ 0 quarters (1Q23, 2Q23, 2Q24, 3Q24, 4Q24, 1Q25); 178.83 at 94.6% of the MODL range; range-as-±2sd anchor 0.0958 (0.133 at the card's RMSE). Corrected in claim 3, claim 8 and the JSON anchor field; the B02 anchor field now also states 174.72 at 18.7% of the range (its rev-1 "4th–8th percentile" was a count-of-estimates guess).

### A10-23 (minor, R07) — stale C11 quote; reverse dependency: accepted
Claim 12 now quotes C11 rev 2 (0.76 → 0.62 under ADR N(4.4, 1.0)) and states the reverse dependency with the number (joint mean +3.35 vs the +3.04 C11 adopted → C11 ≈ 0.73), flagged for X01 in both ADR logs and JSONs.

### A10-24 (minor, R07) — kernel-lag double count in FY26 margin: accepted
The recognition convention is stated once (claim 11): implied take rate in both quarters; the kernel-lag term on the 3Q26 GBV surprise is the same revenue on another convention and is not added. Applied symmetrically to B02 (4Q26 −$100M → −$57M). Because the R07 impact is now priced at E[ADR | Yes] = +4.95 (+1.65pt, see below) rather than the threshold, the FY26 line is +0.5pp; at the threshold it is +0.35pp (bracketed in the log), i.e. the double count is removed and the delta scale changed.

### A10-25 (minor, R07) — three qualifications on `last_q` omitted: accepted
`docs/adrv3/SYNTHESIS.md` lines 10 and 34, verbatim: post-hoc promotion on 11 September after J3's table; binding case passes by 0.011 (eur, W2, jackknife max 0.989); the card's ex-FX is 0.30pp below the harness convention because of J3's H fills. Carried in R07 claim 5 and B02 claim 2 wherever the rule is used as the centre.

## Response-agent choices not in the audit

1. **R07 impact priced at E[ADR | ≥ 4.4] = +4.95 (+1.65pt)**, the convention B02 already used (E[ADR | ≤ 2.0]), so both tails are priced off one distribution on one convention (the spirit of A10-03). The threshold-based figures (+1.1pt, stock +$7, EV $1.2) are kept in brackets in §9 and in the JSON's `at_threshold_4.4` block. The stock haircut (~70%) is the same in both tails.
2. **R05 route weights** (0.35 / 0.25 / 0.20 / 0.20) are stated as a judgment in §5 with the single-route bounds (0.17–0.31); Astra's weights with the unwidened sd give 0.214.
3. **R04 blend weights** (0.50 / 0.25 / 0.25) are stated in §5 with the bounds (equal thirds 0.47; decomposition only 0.57).

## What the audit missed

1. **The corrected cost stack contradicts the card on the ceiling question, and the audit did not say so.** Once the D&A is restored, management's own budget (line build 50.37%) sits 0.28pp *above* the 3Q25 ceiling, and the cost stack gives P(above the ceiling) 0.64–0.66 against the card's 0.46. The audit's weights (0.40 card / 0.25 stack) implicitly adjudicate this, but the log's leading hypothesis ("the sentence is the cost budget; the print is 49.9–50.4") had to be rewritten: on the corrected identity the budget object already implies a small upside miss of the sentence. `40_line_build.md` line 189 leaves this open for Krish ("whether to adopt the reconciled base or the evidence build"); X01 should carry it as a named choice.
2. **The 3Q25 identity's "implied D&A $27M" is not pure D&A.** The audit used it to confirm the identity (correctly) but the line build's own D&A is $20.6M ("D&A $21M/q"); the $27M includes other adjusted-EBITDA add-backs (restructuring, lodging-tax items). The add-back for 3Q26 is therefore $20.6–27M (0.43–0.56pp); the R05 sensitivity row carries the $27M case (cost stack 0.31, headline unchanged to a point).
3. **The corrected S&M threshold is cleared by the evidence build's own S&M line.** At $724M the threshold sits above the evidence-only build's S&M ($710M, +21.4%) — so the memo's "sandbag" reply is not "S&M would have to halve" but "S&M would have to land where the 10-Q evidence already puts it". The audit called the argument "weaker than the log believes"; it is weaker than that, and the R05 log now says so in the §4 table and the EV line.
4. **The auditor's coherent Normal has no skew; the structural mixture does.** N(3.50, 1.05) gives 0.196 / 0.077; the joint mixture at almost the same centre and sd (N(3.33, 1.13) equivalent) gives 0.172 / 0.119 because the AR(1) and lap-and-proxy branches are fitted reversion paths that put more mass below the centre. The audit's own random-walk cross-check (0.175 / 0.107) sits closer to the mixture than to its headline pair; the decision to keep the mixture is recorded in both logs' §5.
5. **The R04 route inputs are more robust than the base rate.** The audit moved the letter-route inputs (0.45 → 0.52, 0.70 → 0.80) and got a decomposition of 0.615 against this log's 0.565; both land the final at 0.52 once the base rate is repaired. The number's sensitivity is in the base-rate dependence (0.25–0.44) and the call-answer probability (0.30–0.55 → 0.47–0.59), not in the letter route, which the sensitivity table now shows.
6. **R01 is now revision 2 at 0.39**, not the 0.42 C11 rev 2 and C04 rev 2 quote; not in this batch's scope, but X01 should re-plug it alongside the ADR distribution when it re-runs C11.
7. **B02's MODL anchor position.** The audit corrected R07's "96th percentile" but not B02's mirror claim ("4th–8th percentile"); 174.72 sits at 18.7% of the low-to-high range. Corrected in B02 claim 9 (the anchor value, 0.07, does not change).

## Reconciliation with the auditor's numbers

| question | auditor | revision 2 | gap | decision |
|---|---|---|---|---|
| R04 | 0.52 (0.37–0.67) | 0.52 (0.38–0.66) | 0 | Same number by a slightly different route (decomposition 0.615 vs 0.565; base 0.35 vs 0.34; same prior). No asymmetry to name. |
| R05 | 0.21 (0.13–0.32) | 0.22 (0.13–0.32) | +1 | Same four routes; the difference is the widened cost sd (A10-19 accepted in full rather than in part by the auditor's own weights). Hold 0.22. |
| R07 | 0.19 (0.12–0.30) | 0.17 (0.11–0.27) | −2 | The mixture's fitted reversion branches vs a symmetric Normal; the auditor's own random-walk cross-check (0.175) is at this number. Hold 0.17. |
| B02 | ≈ 0.08 | 0.12 (0.07–0.20) | +4 | Same asymmetry as R07 in the other direction; the reversion branches are fitted (AR(1) ρ 0.747, innovation sd 0.94), not assumed. Hold 0.12. |

No gap exceeds 10 points.

## Implications for the synthesis (X01)

- **C04's 3Q26 margin draw N(49.95, 1.0) is the outlier** (A10-10): it implies P(≥51.5) 0.06 against the card's conformal sd 1.62 (0.17) and this log's 0.22. X01 should draw one 3Q26 margin distribution for C04, C09 and R05 — the card at sd 1.62, or the four-route blend here — and not reconcile the three separately. C04 is not edited by this response.
- **C11 rev 2 adopted the rev-1 B02/R07 mixture (mean +3.04)**; the joint model's mean is +3.35 (median +3.40). Re-running `c11_model_v2.py` on the joint distribution should move C11 from 0.76 to ≈ 0.73 (its own sensitivity: ADR N(4.4, 1.0) → 0.62, N(2.0, 1.0) → 0.85). C11 is not edited by this response; the implication is recorded in the R07 and B02 logs and JSONs.

## Reproduction output

`py -3.13 -B docs/pitch-forecasts/audits/A10-reproduce.py` from the repo root, 2026-09-17 (script saved verbatim from the audit; no edits; exit 0). Full text in `A10-reproduce.stdout.txt`; reproduced here in full:

```
======== R05  ceiling base rate ========
ceilings n: 10  exceeded by >=1.4pp: 1  exceeded at all: 2  Laplace: 0.16666666666666666
rows in the source with target 4Q25 (2Q25 and 3Q25 prints): 2 - drop_duplicates keeps the h=2 sentence, not the h=1 analogue
print_quarter target_period  value_high  actual  excess
         2Q22          3Q22       -0.22     1.3    1.52
         4Q22          1Q23        0.00    -0.8   -0.80
         1Q23          2Q23        0.00    -0.8   -0.80
         1Q24          2Q24        0.00    -0.5   -0.50
         2Q24          3Q24        0.00    -1.5   -1.50
         3Q24          4Q24        0.00    -2.5   -2.50
         4Q24          1Q25        0.00    -1.4   -1.40
         1Q25          2Q25        0.00     1.2    1.20
         2Q25          3Q25        0.00    -2.4   -2.40
         2Q25          4Q25        0.00    -2.5   -2.50

======== R05  line build: is D&A inside total_cash_costs? ========
sum of cash lines: 2405.027  total_cash_costs: 2405.027
revenue - cash costs       : 2399.009
revenue - cash costs + D&A : 2419.642  == 40_lines adj_ebitda 2419.642
op_income check rev-cash-SBC: 1947.429  == op_income 1947.429
line-build 3Q26 margin: 50.3669  vs R05 MC centre (rev-cost, no add-back): 49.9374  -> D&A is worth 0.4295 pp
3Q25 identity: cash costs ex-SBC 2071.0  revenue-cash 2024.0  printed adj EBITDA 2051  implied D&A 27.0
3Q25 printed S&M: 639.0  line-build S&M base implied by 40_lines: 585.0

======== R05  cost-stack Monte Carlo, as published and with the D&A add-back ========
as published                     P(>=51.5)=0.1914  median=50.234  sd=1.421  P(>=50.085)=0.5421
with line-build D&A add-back     P(>=51.5)=0.2806  median=50.663  sd=1.420  P(>=50.085)=0.6609

======== R05  Gaussian routes on the card, and what the card's own band says ========
      calibration  n   qhat80  gaussian_from_mae_80  gaussian_sd_from_qhat80      mae      bias  bias_last5
       W1_all_n14 14 2.203943              1.809296                 1.719681 1.126425 -0.669316   -0.271274
recent_2024Q1plus 10 2.080265              1.297069                 1.623178 0.807524 -0.484542   -0.271274
card raw, W1 sd                mu=49.940 sd=1.720 P(>=51.5)=0.1822 P(>=50.085)=0.4664 P(>Street 49.776)=0.5380
card raw, W2 sd                mu=49.940 sd=1.623 P(>=51.5)=0.1682 P(>=50.085)=0.4644 P(>Street 49.776)=0.5403
bias-corrected (last5), W2 sd  mu=50.211 sd=1.623 P(>=51.5)=0.2136 P(>=50.085)=0.5310 P(>Street 49.776)=0.6058
gaussian_from_mae_80 (1.297) is an 80% HALF-WIDTH; r05_model uses 1.30 as an sd.  as sd: 0.1145  as half-width: 0.0616
C04 rev-2 draws 3Q26 margin ~ N(49.95, 1.0) -> P(>=51.5) = 0.0606 (R05 publishes 0.17)

======== R05  revenue leg: cash costs and S&M implied by a 51.5% print ========
rev   4744.3 published: costs<= 2301.0 S&M<=   674 (+15.3% y/y) | with D&A: costs<= 2321.6 S&M<=   695 (+18.8% y/y)
rev   4770.0 published: costs<= 2313.4 S&M<=   687 (+17.4% y/y) | with D&A: costs<= 2334.1 S&M<=   707 (+20.9% y/y)
rev   4804.0 published: costs<= 2330.0 S&M<=   703 (+20.2% y/y) | with D&A: costs<= 2350.6 S&M<=   724 (+23.7% y/y)
rev   4850.0 published: costs<= 2352.2 S&M<=   726 (+24.0% y/y) | with D&A: costs<= 2372.9 S&M<=   746 (+27.6% y/y)
1H26 printed S&M growth: 1Q26 33.4 %  2Q26 26.6 %

======== R05  Street and the M5 anchor ========
LSEG 3Q26 EBITDA 2361.52 margin 49.7757 n 36.0 EBITDA sd 20.0425
sd implied by M5 composite 50.19 and P(margin beat) 0.62: 1.356 -> P(>=51.5) = 0.167
raw Street at its own EBITDA sd: P(EBITDA >= 0.515 x 4804) = 0.0

======== R07  ADR history and base rates ========
quarter  adr_yoy_reported_pp  fx_effect_pp  adr_exfx_yoy_pp  residual_pricing_pp
   1Q23             0.214196          -2.8              3.0             3.476560
   2Q23             1.386344          -0.6              2.0             2.472040
   3Q23             3.157760           2.7              0.5             1.005194
   4Q23             2.565277           2.1              0.5             0.833963
   1Q24             2.642047           0.6              2.0             2.255775
   2Q24             2.120354          -0.9              3.0             3.234376
   3Q24             1.400421          -0.6              2.0             2.083189
   4Q24             0.893256          -1.1              2.0             2.760245
   1Q25            -0.890791          -1.9              1.0             2.231374
   2Q25             2.919837           1.9              1.0             1.905623
   3Q25             4.674896           2.7              2.0             2.822291
   4Q25             5.931828           2.9              3.0             3.698813
   1Q26             9.034668           5.0              4.0             4.380589
   2Q26             5.301467           1.3              4.0             4.849326
n: 14  reported >= 4.4: 4  quarters with FX <= 0: 6 (the log says 7)  reported>=4.4 with FX<=0: 0  ex-FX-0.43 >= 4.4: 0
residual quarterly changes: [-1.0, -1.47, -0.17, 1.42, 0.98, -1.15, 0.68, -0.53, -0.33, 0.92, 0.88, 0.68, 0.47]
  mean 0.106  sd 0.898  |change| >= 1.26 in 2 of 13

======== R07  card v3: what the mix term actually is ========
v3_without_K   eur_fit   fx=-1.12 resid=4.85 exfx=3.69 reported=2.57 usd=175.69 mix(exfx-resid)=-1.160
v3_without_K   baskets   fx=+0.26 resid=4.85 exfx=3.69 reported=3.95 usd=178.06 mix(exfx-resid)=-1.160
v3_without_K   midpoint  fx=-0.43 resid=4.85 exfx=3.69 reported=3.26 usd=176.88 mix(exfx-resid)=-1.160
v3_with_K      eur_fit   fx=-1.12 resid=5.02 exfx=3.86 reported=2.74 usd=175.99 mix(exfx-resid)=-1.160
v3_with_K      baskets   fx=+0.26 resid=5.02 exfx=3.86 reported=4.12 usd=178.35 mix(exfx-resid)=-1.160
v3_with_K      midpoint  fx=-0.43 resid=5.02 exfx=3.86 reported=3.43 usd=177.17 mix(exfx-resid)=-1.160
=> the card's mix term is -1.16, so r07_model's -1.15 IS the card's mix and its
   'mix -0.98 (H fills)' row is the same thing with the K line moved out of the
   residual. The MC's persistence branch reproduces the WITHOUT-K card (+3.26).

======== R07  walk-forward errors and Gaussian routes ========
midpoint  n=10 RMSE=0.927 bias=-0.308 P(>=4.4) raw=0.1478 bias-corrected=0.2376
eur       n=10 RMSE=1.093 bias=-0.377 P(>=4.4) raw=0.0644 bias-corrected=0.1201
baskets   n=10 RMSE=0.829 bias=-0.239 P(>=4.4) raw=0.3677 bias-corrected=0.4803

======== R07 / B02  one distribution or two? ========
r07_model mixture: P(>=4.4)=0.1076 P(<=2.0)=0.1728 median=3.120 sd=1.121
published pair: R07 0.17 (model 0.11, lifted ~1.5x); B02 0.18 (model 0.176, no lift)
the Normal that would carry BOTH published tails: N(3.18, 1.28)
  its centre is below the card without K (3.26) and with K (3.43); its sd is 38%
  above the card's own walk-forward RMSE (0.93)
  coherent alternative N(3.43, 0.93): R07 0.148  B02 0.062
  coherent alternative N(3.5, 1.05): R07 0.196  B02 0.077
  coherent alternative N(3.74, 0.93): R07 0.239  B02 0.031

======== R07  MODL anchor ========
MODL n 26 low/mean/high growth 1.413 3.369 4.571  range/4 = 0.789  P(>=4.4) = 0.0958
threshold 178.83 sits at 94.6 % of the analyst range (the log says the 96th percentile)

======== R04  driver-attribution table and route arithmetic ========
letters/calls n: 13  driver named: 9  positive monetization driver: 5  conditional: 1
letter 0.225 call 0.315  independence-intersection 0.070875  rho-blended intersection 0.147937  union 0.392063 (file: 0.3921)
total with the Feb conditional: 0.574444 (file: 0.5744 )
  per-print base 0.375 -> two prints, independent: 0.6094
  per-print base 0.25 -> two prints, independent: 0.4375
  per-print base 0.5 -> two prints, independent: 0.7500
the two-print base rate assumes the prints are independent; management's framing
is persistent, so 0.61 is an upper bound on that class.
r04_statement_record.csv DOES NOT PARSE: ParserError Error tokenizing data. C error: Expected 8 fields in line 4, saw 9

======== R04  impact arithmetic ========
FY27 model revenue 15828.6 EBITDA 5483.3 margin 34.642%
  log's arithmetic  d_EBITDA / OLD revenue = 1.308 pp (the published +1.3pp)
  correct           new margin 35.435% -> +0.793 pp
  brief's rule      1.453% of revenue x 0.66 = +0.959 pp
share count: the card uses 591.7m; the R04/R05/R07 impact tables use 620m (205M of EBITDA at 16x: $5.54 vs $5.29 per share)
```

Separately run (revision-2 models, outputs in the question folders): `r05_model_v2.py` — corrected MC 0.2800 (sd 60) / 0.3086 (sd 72), median 50.67, blend 0.2186; `adr_joint_model_v2.py` — P(≥4.4) 0.1723, P(≤2.0) 0.1187, median 3.396, mean 3.349, sd 1.122, rev-1 forms reproduced at 0.1079 / 0.1722 and 0.1063 / 0.1759; `r04_extract_v2.py` — decomposition 0.565125, base range 0.25 / 0.3438 / 0.4375, statement record parses (4 rows), 61 sentence hits.

## Final table

| question | revision-1 | auditor | revision-2 | anchor | \|final − anchor\| | EV $/share | material |
|---|---|---|---|---|---|---|---|
| R04 P(fee accretion stated at 5 Nov or Feb) | 0.58 (0.42–0.72) | 0.52 (0.37–0.67) | **0.52 (0.38–0.66)** | 0.50 (flat prior; no market) | 0.02 | +$1.1 (stock +$2.2 expected: 0.90 × $1.5 direction-only, 0.10 × $8 quantified; rev 1 +$4.1) | borderline yes (one-line risk with the reply) |
| R05 P(3Q26 margin ≥ 51.5%) | 0.17 (0.10–0.27) | 0.21 (0.13–0.32) | **0.22 (0.13–0.32)** | 0.17 (M5 composite on LSEG 11 Sep) | 0.05 | +$0.8 (stock +$3.5; rev 1 +$0.5) | no |
| R07 P(3Q26 ADR ≥ +4.4%) | 0.17 (0.10–0.28) | 0.19 (0.12–0.30) | **0.17 (0.11–0.27)** | 0.12 (MODL n 26) | 0.05 | +$1.7 (stock +$10 at E[ADR \| Yes] +4.95; +$1.2 at the threshold; rev 1 +$1.2) | yes |
| B02 P(3Q26 ADR ≤ +2.0%) | 0.18 (0.10–0.30) | ≈ 0.08 | **0.12 (0.07–0.20)** | 0.07 (MODL n 26) | 0.05 | −$1.4 (stock −$12; rev 1 −$2.2) | yes |

Synthesis lines: **C04-sd** — C04 rev 2's 3Q26 draw N(49.95, 1.0) gives P(≥51.5) 0.06 against the card's conformal 1.62 (0.17) and R05's 0.22; X01 should use one 3Q26 margin distribution (the card at sd 1.62) for C04, C09 and R05 and treat C04's sd as the outlier. **C11** — C11 rev 2 adopted the rev-1 B02 mixture (ADR mean +3.04); the joint distribution's mean is +3.35, so re-running `c11_model_v2.py` on it should take C11 from 0.76 to ≈ 0.73; C11 is not edited here.
