# Pitch-forecasts run — synthesis

Written 17 Sep 2026 by the synthesis agent (Fable 5.1) after all 19 batches reached `done`
(`py -3.13 analysis/src/pitch_forecasts/state.py`). Inputs: `forecast_table.csv` (53 rows, regenerated 13:29),
every `audits/<batch>-audit-response.md` final table, the A14/A18 audits (audit-only batches), the four adopted objects,
the RUN_STATE ledger notes, and the v2 memo. Memo v3 files and the change log are described at the end.

## Bottom line

The flow moved the pitch's *event* numbers a lot and its *fundamental* numbers not at all. The 3Q26 nights view (+9.5%,
band 8.5–10.0), the 4Q26 guide arithmetic, the estimates table, the FY27 margin views and the 12-month fundamental targets
($143 base, $125 short case, $180–190 breaker) came out of the run untouched, because no question re-forecast them; the
memo's 25/45/30 survives as what it always was, a partition of the 3Q26 nights print (0.26 / 0.45 / 0.29 under the adopted
N(9.5, 1.70)), and the 12-month probability-weighted target moves from $146 to **$148 (−12%)**. What changed is everything the
memo said about the day and the weeks after it. The base-case 5 Nov day is a median of about **−5% with P(≤ −8%) 0.37**, not
"−8 to −13%"; the unconditional day-1 median is **−2.1%** (P(≤ −8%) 0.27; −2.5% / 0.28 rebased on the adopted print states) against
an options market pricing zero; the 15 Dec close has a median of **$166** and a probability-weighted mean of **$167.3**, i.e. the
reaction function on its own delivers −1% to −3%, not −13%, by December — the rest of the memo's return is the estimate cuts and
multiple compression that follow a FY27 growth reset, which the run prices only through the S02 drift terms. The 5 Nov
disclosure-gate scenario object (X01) puts **0.55** on the memo's short case under the literal reading (0.48 material), 0.14 on
the thesis breaker, 0.17 on the base and 0.14 on "none", and says plainly that 0.55 is a wording bet on two language events
with no precedent. Of the 33 risk and bonus items, **5 of 16 risks and 5 of 17 bonus items** clear the $1/share expected-value
bar; the memo's risk and bonus sections are cut to those. Every number in the v3 memo now traces to a research log, an
independent audit and an audit response; the two-window rule and the extreme-probability gate were applied throughout.

## Table 1 — every question (revision-2 numbers; audit-only batches carry the auditor's number)

Anchor = the log's external or repo anchor as published; blank where the log declared `NO_EXTERNAL_ANCHOR`. For MC questions
|final − anchor| is on the leading option. "Astra" = Codex gpt-6-astra (A01–A09); "Opus" = the Opus fallback auditor (A10–A19).

| id | question (short) | final (rev 2) | CI / vector | auditor's independent | anchor | \|final − anchor\| | audit verdict | notes |
|---|---|---|---|---|---|---|---|---|
| C01 | 4Q26 revenue guide mid < Street mean (4 Nov) | **0.72** | 0.60–0.82; guide mid p5/50/95 $2,945 / 3,100 / 3,265M; guide-surprise object 0.51 | Astra 0.62 | 0.67 (Kalshi ladder through the kernel, thin, not independent) | 0.05 | 13 findings, 11 accepted, 2 in part; 0.75 → 0.72 | Street mean used $3,161M (LSEG family, n 36, 17 Sep). P(below) 0.795 given nights < 10.0, 0.567 given ≥ 10.6 |
| C02 | 4Q26 nights bucket language | **(a) 0.18 / (b) 0.17 / (c) 0.30 / (d) 0.31 / (e) 0.04** | (c)+(d) = 0.61 deceleration block | Astra 0.17 / 0.18 / 0.30 / 0.30 / 0.05 | (c) 0.32 (MODL 134.0m mapped to language) | 0.08 on (d) | 16 accepted; leader moved (c) → (d) | 8 of 17 historical descriptors resolve (d); 7 of those 8 are the directional "moderate" word, 1 an explicit bucket |
| C03 | FY26 revenue guide language | **(a) raised 0.36 / (b) 0.16 / (c) ≈15% 0.28 / (d) 0.08 / (e) 0.12** | | Astra 0.35 / 0.19 / 0.21 / 0.10 / 0.15 | (a) 0.38 (Street-implied FY26 $14,173M) | 0.02 | 16 accepted | 3 of 3 Novembers with an FY sentence raised it |
| C04 | FY26 margin sentence | **(a) held 0.33 / (b) ≈36% 0.30 / (c) ≥36.5% 0.05 / (d) softer 0.27 / (e) 0.05** | | Astra 0.30 / 0.39 / 0.06 / 0.22 / 0.03 | (b) 0.55 (M3/WS05 repo prior) | 0.15 on (a) | 20 findings, 17 accepted, 3 in part; leader moved (b) → (a) | P(d \| C01 below) 0.32, P(d \| not below) 0.15. 0 of 16 prints ever softened an FY floor. 3Q26 margin draw sd 1.0 is an outlier (see defects) |
| C09 | 4Q26 margin direction sentence | **(a) down 0.22 / (b) flat 0.26 / (c) up 0.47 / (d) 0.05** | | Astra 0.29 / 0.25 / 0.41 / 0.05 | (a) 0.50 / (c) 0.35 (WS05/M3) | 0.12 on (c) | same MC as C04 | P(c \| C01 below) 0.35, P(c \| not below) 0.78 |
| C05 | bundle contribution quantified | **(a) ≥2.5pt 0.07 / (b) 0.11 / (c) <1.5 0.10 / (d) not 0.72** | P(any figure) 0.28 | Astra 0.10 / 0.14 / 0.08 / 0.68 | — | — | 18 findings, 14 accepted, 4 in part | (c) now carries the quantified-lap route C07 also counts |
| C06 | RNPL share of 3Q26 GBV disclosed | **(a) ≥25% 0.25 / (b) 21–24 0.20 / (c) "over 20%" 0.26 / (d) 0.29** | | Astra 0.25 / 0.19 / 0.26 / 0.30 | — | — | largest move in A04 (a 0.15 → 0.25) | v2 share model: P(true share ≥ 24.5) 0.39 |
| C07 | RNPL negative effect acknowledged | **0.27** | 0.15–0.40 | Astra 0.25 | — | — | 0.20 → 0.27 (contract read wider) | partition adverse / ordinary-decel / routine on the print states |
| C08 | stated 3Q26 revenue-FX integer | **(a) ≥+3 0.49 / (b) +2 0.28 / (c) ≤+1 0.21 / (d) 0.02** | P(≥+4) 0.20 | Astra 0.56 / 0.26 / 0.16 / 0.02 | (a) 0.22 (fx-lag-v2 H2 through the kernel) | 0.27 | 18 findings, 15 accepted, 3 in part | the memo's "0/+1 short-lag vs +3 kernel" paired tell stands |
| C11 | 3Q26 take rate ≥ 18.10% | **0.76** | 0.60–0.88 | Astra 0.68 | 0.40 (Street-implied 17.99%) | 0.36 | 0.55 → 0.76: rev-1 headline was incoherent with its own band table | ≈ 0.73 on the joint ADR model (A10 note); by GBV band ≥0.995 / 0.99 / 0.97 / 0.76 / 0.18 / ≤0.005 |
| C12 | unearned fees ≤ −3% y/y at 30 Sep | **0.43** | 0.28–0.60 | Astra 0.44 | 0.45 (note-04 deferral table) | 0.02 | 0.55 → 0.43 | median −2.2% ($1,780M); the 13 Oct rule withdrawn |
| S01 | day-1 move after 5 Nov | **median −2.1%** | p5/25/75/95 −17.1 / −8.6 / +4.2 / +14.5; P(≤−8) 0.27, P(≤−5) 0.38, P(≥+5) 0.22 | Astra −2.2, P(≤−8) 0.25 | 0.0 (options, sd 9.0%) | 2.1pt | 16 accepted; one joint draw replaces the rev-1 mixture | base-case cell (decel & guide below & bucket down, p 0.36): median −5.1, P(≤−8) 0.37, P(<0) 0.71 [rev 1 −8.6 / 0.53 withdrawn]; breaker cell (p 0.11) +2.9. Published on the pre-A09 states (accel 0.32); rebased on the adopted states (X01): median −2.5, P(≤−8) 0.28 |
| S02 | 15 Dec 2026 close | **median $166** | p5/25/75/95 121 / 146 / 186 / 221; P(≤150) 0.30, P(≤143) 0.22, P(≥180) 0.32 | Astra $163 | $170.6 (real-world mixture RND; $169.3 risk-neutral) | $5.0 | 17 findings, 15 accepted, 2 in part | by branch: accel $172 / flat $165 / decel-guide-ok $163 / decel-guide-below $156; still carries accel 0.32 (adopted 0.26; worth ≈ −$1 on the median) |
| S03 | 12 Feb 2027 close (first session after 4Q26 print) | **median $166** | 110 / 141 / 195 / 244; P(≤150) 0.34, P(≤143) 0.27, P(≥180) 0.37 | Astra $167 | $169.9 | $3.5 | same batch | Feb day-1 history 13.3 / 3.6 / 13.4 / −1.7 / 14.4 / 4.6: **5 of 6 positive, 3 of 6 ≥ +5%** |
| S04 | mean sell-side target ≤ $176.8 on 15 Dec | **0.30** | 0.20–0.42 | Astra 0.33 | 0.50 (repo prior) | 0.20 | same batch | tape follows price with a 1–2 month lag |
| F01 | 1Q27 nights descriptor ≥ +8.2% | **0.28** | 0.16–0.42 | Astra 0.26 | 0.43 (MODL 4Q26 bar through the tree) | 0.15 | 21 findings, 19 accepted | conditioned on a pre-final cut of the Q4 object (mean 8.7, P(≥134m) 0.29 vs adopted 8.61 / 0.307): immaterial, not re-run |
| F02 | 1Q27 revenue-guide growth | **median +10.5%** | p5/25/75/95 5.1 / 8.3 / 12.8 / 16.1; P(<10) 0.45, P(<9.4) 0.36, P(≥12) 0.34 | Astra +10.3 | +12.4 raw (LSEG 1Q27, 13 Aug) | 1.9pt | same | comp 1Q26 +17.9%; same pre-final Q4 object as F01 |
| F03 | FY27 margin guide (Feb) | **(a) ≥36.5 0.02 / (b) 0.04 / (c) 0.10 / (d) <35.5 or down 0.36 / (e) none 0.48** | literal convention | Astra 0.03 / 0.05 / 0.10 / 0.32 / 0.50 | (d) 0.55 / (e) 0.33 (WS05/H12) | 0.19 on (d) | convention decided: literal ((e) is the modal option) | B12-literal = P(d) + P(numeric floor below the FY26 print) = 0.36 + 0.15 |
| F04 | FY27 S&M ex-SBC ≥ 21.9% of revenue | **0.55** | 0.40–0.68; by F03 bucket a 0.37 / b 0.43 / c 0.53 / d 0.64 / e 0.50 | Astra 0.55 | 0.33 (Street residual 21.04%) | 0.22 | unchanged centre | resolves Feb 2028 |
| R01 | 3Q26 nights print ≥ +10.0% | **0.39** | 0.30–0.47 | Astra 0.38 | 0.585 (Kalshi mids, untraded since 29 Jul; zero weight) | 0.20 | 21 findings; headline re-scoped to the nowcast object (fine print) | management-delivery constructions 0.57–0.82 and the sequential class 0.44–0.50 published beside it at zero weight; adopted print states P(<10.0) 0.614 / 10.0–10.6 0.126 / ≥10.6 0.260 |
| R02 | 3Q26 nights print ≥ +10.6% (accelerates) | **0.26** | 0.18–0.34 | Astra 0.25 | 0.537 (Kalshi) | 0.28 | same object | subset of R01 |
| R03 | RNPL share ≥25% and nights ≥10% | **0.11** | 0.07–0.15 | Astra 0.11 | — | — | 0.07 → 0.11 on C06 rev 2 | subset of R01; one sentence |
| R04 | fee accretion to take rate stated (5 Nov or Feb) | **0.52** | 0.38–0.66 | Opus 0.52 | 0.50 (flat prior) | 0.02 | 25 findings, 24 accepted; impact re-priced as a statement | 2Q26 print rescored No |
| R05 | 3Q26 margin ≥ 51.5% (sentence sandbagged) | **0.22** | 0.13–0.32 | Opus 0.21 | 0.17 (M5 composite) | 0.05 | D&A add-back identity fixed | 5 Nov threshold: S&M ≤ $724M (+23.7% y/y) |
| R07 | 3Q26 ADR ≥ +4.4% | **0.17** | 0.11–0.27 | Opus 0.19 (A14 auditor also 0.19) | 0.12 (MODL n 26) | 0.05 | one ADR distribution with B02 | E[ADR \| Yes] +4.95 |
| R06 | buyback ≥$5bn authorization or ≥$1.5bn Q4 pace | **0.46** | 0.30–0.60 | Opus 0.42 | — | — | 25 findings, 19 accepted, 6 in part | renewal at the existing pace is modal and already in the share count |
| R08 | new quantified 2027 growth lever ≥1pt | **0.13** | 0.06–0.24 | Opus 0.13 | — | — | same | no 3Q letter or call has ever previewed the next year numerically |
| R09 | hotels/Experiences/Services ≥3% or ≥$500M disclosed | **0.25** | 0.13–0.38 | Opus 0.25 | — | — | same | |
| R10 | dollar (DTWEXBGS) ≥4% weaker by 11 Feb | **0.10** | 0.06–0.17 | Opus 0.11 | 0.11 (implied-vol construction) | 0.01 | 25 findings, 22 accepted, 3 in part | bridge arithmetic, not a risk line |
| R11 | 4Q26 US RevPAR ≥ +4% | **0.26** | 0.17–0.40 | Opus 0.29 | 0.25 (CoStar/TE FY26 +4.4% implied) | 0.01 | adopted object `r11_v2_joint_object.json` (mean +2.60, sd 2.17) | base rate rebuilt from 28 parsed CoStar monthly releases |
| R15 | World Cup quantified as ≤1pt / immaterial | **0.18** | 0.10–0.30 | Opus 0.18 | — | — | same batch | a disclosure, not a booking: no model line moves |
| R16 | 4Q26 nights print ≥ 134.0m (Street bar) | **0.31** | 0.19–0.44 | Opus 0.30 | 0.50 (Bloomberg MODL 134.0m, n 28) | 0.19 | adopted object `adopted_q4_states_v2.json` (mean 8.61, sd 2.28; tails 0.307 / 0.309) | paired with B13 as the two tails of one distribution |
| R12 | ≥3 upgrades or mean target ≥$190 by 15 Dec | **0.47** any-day (0.43 on the 15 Dec reading) | 0.34–0.60 | Opus 0.47 | 0.32 (S04 rev 2, not independent) | 0.15 | 25 findings, 21 accepted, 4 in part; rebuilt on S02/S04 rev 2 | marker of the breaker branch, not additive |
| R13 | short interest ≥ 5.0% of shares by 15 Jan | **0.02** | 0.005–0.06 | Opus 0.02 | ≈0.01 | 0.01 | jump double-count removed | float basis ≈ 0.22 (different object) |
| R14 | 12 Feb day-1 ≥ +5% | **0.26** | 0.17–0.37 | Opus 0.26 | 0.27 (options Feb event sd 9.0) | 0.01 | one-sided $5.3 EV line withdrawn | exit-timing statement: 0.26 up ≥5% vs 0.30 down ≥5%, P(<0) 0.55 |
| B01 | "moderation"-class demand language at 5 Nov | **0.33** (auditor's; log rev 2 0.33) | 0.23–0.45 | Opus 0.33 | 0.31 | 0.02 | **audit-only** (A14); adopted the auditor's number | base-case language marker, not a memo line; ~0 incremental EV vs the base case |
| B02 | 3Q26 ADR ≤ +2.0% | **0.12** rev 2 (A10 response); **auditor 0.09** | 0.07–0.20 | Opus 0.09 (Astra-family A14: ≈0.08) | 0.07 (MODL n 26) | 0.05 | **audit-only** (A14) for the third pass; the number was reconciled to R07's distribution inside A10 | carry 0.12 as the run-coherent number and 0.09 as the auditor's beside it |
| B03 | marketing cut / slower S&M signalled at 5 Nov | **0.21** (auditor's; log rev 1 0.18) | 0.12–0.33 | Opus 0.21 | 0.24 | 0.03 | **audit-only** (A14); log stays revision 1 + audit | stock-line sign disputed (log −$3, auditor's components +$3.5 to +$5.6); immaterial either way |
| B04 | host churn / listings ≤ +3% attributed to the fee | **0.21** | 0.12–0.33 | Opus 0.24 | — | — | 25 findings, 19 accepted, 6 in part | |
| B05 | EU/UK STR restriction enacted (market ≥1% of EMEA) | **0.62** | 0.42–0.78 | Opus 0.62 | — | — | same | modal event is mid-sized and mostly after Jun 2027 |
| B06 | geopolitical headwind ≥0.5pt cited | **0.32** | 0.20–0.45 | Opus 0.33 | — | — | same | 1Q26 "≈100bps" is the template |
| B07 | NTTO overseas arrivals 4Q26 ≤ −5% | **0.63** | 0.47–0.77 | Opus 0.63 | — | — | same | inbound is 2.5% of nights |
| B08 | ≥$50M FY27 AI/hosting step or 4Q26 CoR ≥ +18% | **0.44** | 0.31–0.57 | Opus 0.45 | — (internal: line build 0.63) | — | 25 findings, 22 accepted; 0.38 → 0.44 | line build's own 4Q26 CoR is $578M vs the $575M threshold |
| B09 | 4Q26 SBC ≥ $500M | **0.08** | 0.04–0.14 | Opus 0.08 | — (internal: M7 0.16) | — | same | SBC series defect found here (see below) |
| B10 | 4Q26 interest income ≤ 90% of 4Q25 | **0.04** | 0.015–0.08 | Opus 0.04 | — (internal: M7 0.11) | — | same | rates are a tailwind to the line now |
| B17 | take rate guided lower at 5 Nov | **0.41** | 0.28–0.55 | Opus 0.38 | — | — | same | modal Yes = the CFO repeating her 6 Aug sentence |
| B11 | ≥3 downgrades by 15 Dec | **0.11** | 0.05–0.21 | Opus 0.13 | 0.09 (own base-rate family) | 0.02 | 25 findings, 17 accepted, 6 in part; rebuilt on S02 rev 2 | marker of the decel-guide-below branch, not additive |
| B12 | FY27 margin guided down / investment year (Feb) | **0.49 literal / 0.36 material** | 0.37–0.61 / 0.26–0.48 | Opus 0.47 / 0.36 | 0.65 (WS05 prior, not independent) | 0.16 | same | one object with F03 |
| B13 | 4Q26 nights print ≤ 131.0m | **0.31** | 0.19–0.43 | Opus 0.30 | 0.02 (V3, not independent) | 0.29 | adopted the Q4 object (0.309) | mirror of R16 |
| B14 | hurricane landfall / disaster cited | **0.09** (auditor's; log rev 1 0.08) | 0.05–0.15 | Opus 0.09 | 0.08 (Kalshi count ladder) | 0.01 | **audit-only** (A18) | EV ≈ −$0.003; drop |
| B15 | 4Q26 US RevPAR ≤ +1% | **0.23** (auditor's = R11 joint object; log rev 1 0.10 withdrawn) | 0.15–0.34 | Opus 0.23 | 0.07 | 0.16 | **audit-only** (A18) | base-rate row must read "4 of 9", not "6 of 13" |
| B16 | insider sales ≥ $150M or new CEO 10b5-1 by 31 Jan | **0.89** (auditor's; log rev 1 0.87) | 0.79–0.96 | Opus 0.89 | 0.95 | 0.06 | **audit-only** (A18) | routine disclosure; surprise EV −$0.06 |
| X01 | 5 Nov scenario probabilities (disclosure gates) | **breaker 0.14 / base 0.17 / short case 0.55 / none 0.14** (literal) | material reading 0.14 / 0.20 / 0.48 / 0.18; short-first precedence 0.11 / 0.17 / 0.59 / 0.13 | Opus 0.14 / 0.17 / 0.55 / 0.14 (stdlib quadrature within 0.0007 of every cell) | none by construction (the memo's 25/45/30 is the object under audit; no \|final − anchor\| row) | — | 18 findings, 18 accepted; base gate corrected from "<10.6" to "decelerating" | print partition 0.26 / 0.45 / 0.29 is the memo's 12-month object; memo-conjunctive short scenario 0.046, breaker 0.050 |

## Table 2 — risks and bonus items ranked by |EV|

**Stock convention (one for every row):** the stock impact is the *joint-solve repricing* of the item's fundamental delta
(1pt of FY27 nights = $4.90/share; EBITDA level changes at ~16x on the run's share counts; statements priced as the change in the
market's mark), with **no print reaction added**. R16's revision-2 line (+$8.8 joint solve + ~$4 February reaction = +$11, EV
+$3.4) is therefore restated on the joint-solve-only convention as the exact mirror of B13: **R16 +$2.3 / B13 −$2.3** (the
February reaction belongs to S03 and is not additive). The four questions whose content *is* the 5 Nov reaction (R01, R02, R03,
B01) are priced by their logs as the day-1 differential against their complement at $167.51; those rows are labelled
"reaction-horizon" and carry their joint-solve equivalent in the mechanism column. EVs are P × impact; R02 and R03 are subsets of
R01 and are not added. Materiality bar: |EV| ≥ $1.00/share.

| rank | id | item | P | stock $/share | EV $/share | material | mechanism (one line) |
|---|---|---|---|---|---|---|---|
| 1 | R01 | 3Q26 nights print ≥ +10.0% | 0.39 | +8.7 (reaction-horizon; joint-solve 0.67pt FY27 = +3.3) | **+3.4** | yes | day-1 +0.9% given Yes vs −4.3% given No; E[nights \| Yes] 11.2 vs 9.5; 4Q26 revenue +$62M, FY27 +$106M |
| 2 | R02 | 3Q26 nights print ≥ +10.6% (accelerates) | 0.26 | +9.8 (reaction-horizon; joint-solve +4.2) | +2.5 | yes, subset of R01 | day-1 +2.0% given accelerating vs −3.8% otherwise |
| 3 | B13 | 4Q26 nights print ≤ 131.0m | 0.31 | −7.5 | **−2.3** | yes | E[Q4 \| Yes] 5.9 vs 8.1 (−2.2pt, −$65M), 70% persistence = −1.5pt FY27 nights |
| 3 | R16 | 4Q26 nights print ≥ 134.0m (Street bar) | 0.31 | +7.5 (log: +8.8 joint solve at 60% persistence, +$11 with the Feb reaction) | **+2.3** (+2.7 on the log's persistence) | yes | E[Q4 \| Yes] 11.2 vs 8.1 (+3.1pt, +$92M), FY27 +$290M; symmetric tail of B13 |
| 5 | B12 | FY27 margin guided down / investment year (Feb) | 0.49 lit. / 0.36 mat. | −3.9 / −5.5 | **−1.9 / −2.0** | yes | E[floor \| Yes] 34.8 → realised ≈35.6, −0.85pp vs the Street at a constant multiple; Feb reaction handed to S03 |
| 6 | R07 | 3Q26 ADR ≥ +4.4% | 0.17 | +10 | **+1.7** | yes | E[ADR \| Yes] +4.95 vs card +3.3: 3Q26 GBV +$427M, FY27 revenue +$260M, FY27 margin +1.1pp; haircut 70% (no ADR term in the reaction function) |
| 7 | B02 | 3Q26 ADR ≤ +2.0% | 0.12 (auditor 0.09) | −12 (auditor −8.6) | **−1.4** (−0.8 at the auditor's P and impact) | yes at the run number; borderline at the auditor's | E[ADR \| Yes] +1.4: 3Q26 GBV −$496M vs "mid-teens" guide, FY27 −$302M, FY26 margin −0.6pp (most of the floor's cushion) |
| 7 | B08 | AI/hosting step ≥$50M FY27 or 4Q26 CoR ≥ +18% | 0.44 | −3.2 (expectation across the three Yes forms; full mark −4.5) | **−1.4** | yes | +$100M FY27 cost = −0.63pp FY27 margin, −$0.14 EPS; widens the team-vs-Street FY27 margin gap 1.8 → 2.4pp |
| 9 | B05 | EU/UK STR restriction enacted | 0.62 | −2.1 | −1.3 level / −0.8 surprise | no (surprise basis) | modal enactment costs 0.1–0.2% of revenue, mostly after Jun 2027; tail (Spanish mass removal, Paris) −$5 at P ≈ 0.20 |
| 10 | R04 | fee accretion to take rate stated | 0.52 | +2.2 (0.90 × +1.5 direction-only, 0.10 × +8 quantified) | **+1.1** | yes, borderline | a statement changes the market's mark, not the fee's arithmetic (no detectable fee effect through 2Q26, n 20, p 0.73) |
| 11 | B17 | take rate guided lower at 5 Nov | 0.41 | −2.5 (0.60 of the Yes mass is a repeat of the 6 Aug sentence at −$0.5; 0.05 tail −$9) | **−1.0** | yes, borderline (mirror of R04) | modal form already inside the LSEG 4Q26 mean and FY27 estimates |
| 12 | B01 | demand-softening language at 5 Nov | 0.33 | −3.0 vs the unconditional; +1.9 vs the base-case cell | −1.0 vs unconditional; ≈0 incremental | no (base-case marker) | 3Q26 nights −0.34pt by selection; the word is the base case's language, not a separate event |
| 13 | R05 | 3Q26 margin ≥ 51.5% | 0.22 | +3.5 | +0.8 | no | +$75M 3Q26 EBITDA, FY26 +0.5pp; level +$1.7 plus the C04 channel |
| 14 | R10 | dollar ≥4% weaker by 11 Feb | 0.10 | +5 (FX growth discounted) to +10 (joint solve) | +0.5 to +1.0 | no (bridge arithmetic) | FY27 revenue FX +2.5pp = +$362M ceiling, FY27 margin +1.5pp held |
| 15 | B04 | host churn / listings ≤ +3% attributed to the fee | 0.21 | −3.3 | −0.7 | no | churn route (0.69 of Yes): 0.87pt FY27 nights |
| 15 | R12 | ≥3 upgrades or mean target ≥$190 | 0.47 | +1.5 direct (+14.5 as a branch marker, not additive) | +0.7 | no | analyst actions outside prints move the stock by nothing detectable |
| 15 | R03 | RNPL share ≥25% and nights ≥10% | 0.11 | +6.2 (reaction-horizon; joint-solve +3.4) | +0.7 | no (inside R01) | E[nights \| both] 11.25; day-1 +1.0% vs −2.7% |
| 18 | B06 | geopolitical headwind ≥0.5pt cited | 0.32 | −2.0 | −0.6 | no | 0.7pt off 4Q26 nights on the 1Q26 template, less a +$0.4 reaction credit |
| 18 | R06 | buyback ≥$5bn or ≥$1.5bn Q4 pace | 0.46 | +1.2 | +0.6 | no | renewal at pace is modal and in the share count; day-0 CARs confounded with the print |
| 20 | R08 | new quantified 2027 lever ≥1pt | 0.13 | +3.5 (growth +4.9 less margin debit −1.4) | +0.5 | no | +$158M FY27 revenue less $100–125M launch opex |
| 20 | R09 | new businesses ≥3% / ≥$500M disclosed | 0.25 | +2.0 | +0.5 | no | narrative re-rating only; volumes already inside nights and the ADR mix drag |
| 20 | R11 | 4Q26 US RevPAR ≥ +4% | 0.26 | +2.0 | +0.5 | no | +0.5pt 4Q26 nights, +0.4pt ADR; loses the "hotels are decelerating" corroboration |
| 20 | B03 | marketing cut signalled at 5 Nov | 0.21 | −3 (log) / +3.5 to +5.6 (auditor's components) | −0.5 / +0.8 | no | FY26 margin +1.2pp on the cost side; read as growth capitulation on the stock |
| 24 | B15 | 4Q26 US RevPAR ≤ +1% | 0.23 | −2.0 | −0.5 | no | mirror of R11 on the same joint object |
| 24 | B16 | insider sales ≥$150M or new CEO plan | 0.89 | −0.5 | −0.45 level / −0.06 surprise | no | $4.5bn of sales since 2022, 0 of 41 big moves |
| 26 | R14 | 12 Feb day-1 ≥ +5% | 0.26 | +1.5 (operating carry only; the ±$17 tail is S03's) | +0.4 | no as an EV line; yes as exit timing | P(1Q27 guide ≥ Street \| up day) 0.63 vs 0.45 |
| 27 | B09 | 4Q26 SBC ≥ $500M | 0.08 | −3 | −0.24 | no | below adjusted EBITDA; half-weighted P/E mark |
| 28 | B11 | ≥3 downgrades by 15 Dec | 0.11 | −1.5 direct (−15.8 as a branch marker) | −0.2 | no | measured effect of analyst actions is zero; overlay for the MS 7 Dec 2022 exception |
| 29 | B07 | NTTO overseas arrivals ≤ −5% | 0.63 | −0.3 | −0.2 | no | 3pp × 2.5% inbound share = −0.08pt of 4Q26 nights |
| 30 | R15 | World Cup quantified as small | 0.18 | +1.0 | +0.2 | no | removes one bear talking point about 2Q27 comps; no model line moves |
| 31 | B10 | 4Q26 interest income ≤ 90% of 4Q25 | 0.04 | −2 | −0.08 | no | −$90M FY27 run-rate at a cash-yield multiple |
| 32 | R13 | short interest ≥ 5% | 0.02 | +1.0 | +0.02 | no | right-tail widening on an accelerating print only |
| 33 | B14 | hurricane / disaster cited | 0.09 | −0.03 (log −0.2 misapplied the FY27 coefficient) | −0.003 | no | 0 of 23 letters and calls ever attributed a nights effect to a disaster |

**How many are material.** Risks: **5 of 16** (R01, R02, R16, R07, R04), of which R02 is a subset of R01, so four independent
risk lines; R10 reaches the bar only on the joint-solve reading of an FX move that the bridge already carries. Bonus: **5 of 17**
(B13, B12, B02, B08, B17), with B02 borderline at the auditor's 0.09 and B17 borderline at the line; B05 clears the bar on the
level basis but not on the surprise basis the memo trades, and B01 is the base case's own language. Net of the material lines
the risk side sums to about +$8.5/share (R01 + R16 + R07 + R04, R02 excluded) and the bonus side to about −$8.0/share
(B13 + B12 + B02 + B08 + B17): the distribution of what the memo does not already price is close to symmetric, which is the
honest thing to say about a quarter that has not started.

## The 5 Nov scorecard

Pre-registered tells with the run's probabilities (all resolve on the 3Q26 letter, call or 10-Q unless stated).

| tell | supports the short | weakens the short | run probability | source |
|---|---|---|---|---|
| 3Q26 nights print | < 10.0% (0.61); ≤ 8.5% (0.29) | ≥ 10.0% (R01 **0.39**); ≥ 10.6% accelerating (R02 **0.26**) | adopted N(9.5, 1.70): P(<10.0) 0.614 / 10.0–10.6 0.126 / ≥10.6 0.260 | A09 rev 2 |
| 4Q26 revenue guide midpoint vs LSEG mean ($3,161M) | below (C01 **0.72**; guide-surprise object 0.51) | at/above 0.28 | guide mid p50 $3,100M (p5 $2,945M, p95 $3,265M) | A01 rev 2 |
| 4Q26 nights descriptor | "high single digits" (c) 0.30 or "moderate"/mid-single (d) 0.31 → block **0.61** | "low double digits" (a) 0.18; "around 10" (b) 0.17 | (e) none 0.04 | A02 rev 2 |
| FY26 revenue guide language | narrowed to ≈15% (c) 0.28 or lowered (d) 0.08 | raised (a) **0.36**; reiterated (b) 0.16 | (e) 0.12 | A02 rev 2 |
| FY26 margin sentence | floor held at 35.5% (a) 0.33; softened (d) **0.27** | ≈36% (b) 0.30; ≥36.5% (c) 0.05 | P(d \| guide below) 0.32; 0 of 16 prints ever softened a floor | A03 rev 2 |
| 4Q26 margin direction vs 28.3% | down (a) 0.22; flat (b) 0.26 | up (c) **0.47** | P(c \| guide below) 0.35 | A03 rev 2 |
| bundle contribution figure | none or <1.5pt: (d) **0.72** + (c) 0.10 | ≥2.5pt restated (a) 0.07; 1.5–2.5 (b) 0.11 | | A04 rev 2 |
| RNPL share of GBV | "over 20%" repeated / ≤20 (c) 0.26; not disclosed (d) 0.29 | ≥25% (a) **0.25** (R03 = (a) and nights ≥10%: 0.11) | 21–24% (b) 0.20 | A04 rev 2 |
| RNPL negative effect acknowledged | yes **0.27** | | beyond the 2Q26 10-Q boilerplate | A04 rev 2 |
| stated 3Q26 revenue FX | ≤ +1 (c) 0.21 (short-lag view) | ≥ +3 (a) **0.49** (kernel view); +2 (b) 0.28 | P(≥+4) 0.20 | A05 rev 2 |
| printed take rate ≥ 18.10% | yes **0.76** (≈0.73 on the joint ADR model) paired with GBV vs $26.6bn | | P(yes \| GBV < $25.9bn) ≥ 0.97; P(yes \| GBV ≥ $26.8bn) ≈ 0 | A05 rev 2 |
| unearned fees y/y ≤ −3% (10-Q) | yes **0.43** | | median −2.2% | A05 rev 2 |
| 3Q26 ADR | ≤ +2.0% (B02 0.12) | ≥ +4.4% (R07 0.17) | one distribution centred +3.35 | A10 rev 2 |
| 3Q26 margin ≥ 51.5% | | yes (R05 0.22); tell S&M ≤ $724M | | A10 rev 2 |
| demand-softening word ("moderation" etc.) | yes (B01 0.33) | | base-case marker | A14 audit |
| take rate guided lower | yes (B17 0.41; modal form is a repeat of 6 Aug) | fee accretion stated (R04 0.52) | | A16 / A10 rev 2 |

Conditional day-1 and 15 Dec distributions (X01 rev 2, joint of S01 rev 2 and S02 rev 2 on the adopted print states):

| scenario object | P | day-1 median | day-1 P(≤ −8%) | day-1 P(≥ +5%) | 15 Dec median | 15 Dec p25–p75 | P(≤ $150) | P(≥ $180) | E[nights] | P(C01 below) |
|---|---|---|---|---|---|---|---|---|---|---|
| **Print partition (12-month table)** | | | | | | | | | | |
| thesis breaker: print ≥ 10.6% | 0.26 | +2.1% | 0.12 | 0.37 | $175.0 | 155.9–196.5 | 0.18 | 0.43 | 11.6 | 0.57 |
| base: 8.5–10.6% | 0.45 | −3.8% | 0.32 | 0.17 | $162.2 | 144.3–182.3 | 0.33 | 0.27 | 9.6 | 0.73 |
| short case: ≤ 8.5% | 0.29 | −4.8% | 0.36 | 0.15 | $159.6 | 142.1–179.3 | 0.36 | 0.24 | 7.5 | 0.85 |
| **Disclosure gates (X01, literal reading, breaker-first)** | | | | | | | | | | |
| thesis breaker: ≥10.6% and C02 (a) | 0.14 | +2.2% | 0.12 | 0.37 | $175.1 | 156.0–196.6 | 0.18 | 0.44 | 12.0 | 0.50 |
| base: decelerating and (C02 b/c or C01 yes), not short | 0.17 | −4.7% | 0.36 | 0.15 | $160.6 | 143.0–180.4 | 0.35 | 0.25 | 9.4 | 0.72 |
| short case: ≤8.5% or C02 (d) or C04 (d) | 0.55 | −3.8% | 0.33 | 0.18 | $161.9 | 143.9–182.1 | 0.33 | 0.27 | 8.6 | 0.82 |
| none of the above | 0.14 | +0.3% | 0.17 | 0.29 | $171.2 | 152.4–192.4 | 0.22 | 0.39 | 10.7 | 0.54 |
| **Unconditional** | 1.00 | −2.1% (S01 published) / −2.5% (rebased) | 0.27 / 0.28 | 0.22 / 0.21 | $166 (S02) / $164.7 (X01) | 146–186 | 0.30 | 0.32 | 9.5 | 0.72 |

Probability-weighted 15 Dec close: **$167.3 on the mean convention** (Σ P × conditional mean = the joint's unconditional mean);
$164.8 as the median of branches. The memo uses the mean convention because its own 12-month figure is built from scenario range
midpoints. The memo's own three-gate base case (decelerating print, guide below Street, bucket downgraded; S01 cell p 0.36) has
a day-1 median of −5.1% with P(≤ −8%) 0.37 and P(<0) 0.71. Under the disclosure gates the short-case option is *not* the
worst 5 Nov outcome: a third of it is a directional "moderate" word and a fifth of its draws sit on a print ≥ 10.0%.

## Coherence and data-defect notes (nothing tracked was edited)

Objects adopted late, and which logs still quote superseded values:

1. **3Q26 print states** (`questions/risk-q3-nights-meets-guide/datasets/adopted_print_states_v2.json`, A09 rev 2: N(9.5, 1.70),
   accelerating 0.26). S01, S02, S03 and S04 rev 2 were built on the pre-A09 states (accelerating 0.32; R01 0.42): S01's
   published median −2.1 / P(≤−8) 0.27 becomes −2.5 / 0.28 rebased (X01); S02's median would move about −$1; R12 prices the
   difference at −0.017. C04 and C11 quote R01 at 0.42 (now 0.39). None was re-run; the memo footnotes the rebased values.
2. **4Q26 nights object** (`questions/risk-q4-nights-print-meets-street/datasets/adopted_q4_states_v2.json`, A12 rev 2: mean 8.61,
   sd 2.28, tails 0.307 / 0.309). F01 and F02 rev 2 conditioned on a pre-final cut (mean 8.7, P(≥134m) 0.29); B13 rev 2 adopted the
   final object; R16 rev 1's parameters are withdrawn. Effect on F01/F02 is inside rounding.
3. **4Q26 US RevPAR object** (`questions/risk-q4-us-revpar-strong/datasets/r11_v2_joint_object.json`: mean +2.60, tails 0.259 /
   0.232). B15's log (revision 1) still prints 0.10 and a "6 of 13" base-rate row; SYNTHESIS carries 0.23 and "4 of 9".
4. **ADR joint distribution** (A10 rev 2: one distribution centred +3.35 for R07 and B02). C11 rev 2 adopted the rev-1 B02 mixture
   (mean +3.04); re-running `c11_model_v2.py` on the joint would take C11 from 0.76 to ≈ 0.73. The A14 auditor's independent
   B02 0.09 / R07 0.19 sits beside the run's 0.12 / 0.17.
5. **C04's 3Q26 margin draw** N(49.95, 1.0) is an outlier against the margin card's conformal sd 1.62 (P(≥51.5) 0.06 vs 0.17 vs
   R05's 0.22). One 3Q26 margin distribution (the card at sd 1.62) should serve C04, C09 and R05; not re-run.
6. **S02's day-1 mixture** carries the team base-case cell at mean −6.0 (two gates) where S01's three-gate cell is −5.1 (median);
   both are published, the memo quotes S01's.
7. **X01 unconditional day-1** is S01 rebased (−2.5 / 0.28); the memo quotes S01's published −2.1 / 0.27 with the rebased value in
   a footnote. Revision 1 of X01 printed −2.4 and 167.3 where the model file says −2.50 and 167.2; corrected in rev 2.
8. **R16/B13 stock convention**: R16 rev 2 books joint solve + February reaction (+$11); B13 books joint solve only (−$7.5).
   Table 2 uses joint-solve only for both (+$2.3 / −$2.3 EV).
9. **R12 vs B11 feed-capture convention** (0.85 vs 1.0) is unified at 0.85 in both rev-2 logs.

Data defects found by the run (list only; CLAUDE.md rule 1 forbids editing tracked data from this branch):

- `data/processed/abnb_driver_history_quarterly.csv` **SBC series** is wrong for 4Q23 ($270M; printed $290M), 4Q24 ($400M; printed
  $368M) and 4Q25 ($400M; printed $411M). FY25 SBC $1,592M reconciles only with $411M. (A16 / B09.)
- `data/processed/overnight/02_guidance_ledger.csv` **`sbc_yoy_pct` actuals** derive from that series (FY23 18.28 / FY24 30.82); on the
  printed basis they are FY23 20.43 / FY24 25.63 / FY25 13.15, which turns the outcome column from beat / miss / miss into
  met / miss-by-5.6 / met. Any base rate that used `sbc_yoy_pct` inherits the error (B08 claim 8 cites the same metric). (A16.)
- **Kalshi `updated_time` misreading** in the early logs (A01, A09, A12 rev 1): the field was read as a last-trade timestamp; the
  ladder's cumulative volumes are identical to the 29 Jul Octagon snapshot, so the KXABNB nights market has not traded since
  29 Jul and is carried at zero weight everywhere in rev 2. (A12-14, A09.)
- `data/processed/abnb_capital_return_quarterly.csv` mixes a **cash basis** (cash-flow statement repurchases) with a **trade
  basis** (letter repurchase figures) across quarters; R06 rev 2 rebuilt its own letter-vs-cash table. (A11.)
- **C04's 3Q26 margin sd** 1.0 (see item 5 above).
- **C11** 0.76 should read ≈ 0.73 on the joint ADR model (item 4).
- **R04's impact** uses the 591.7m 3Q26-dated share count on an FY27 effect (the run's FY27 convention is 573m); the difference is
  inside the rounding of a $2.2 line.
- `data/raw/regulatory/quantification/workbook_build/node_modules/` shows untracked on every status; unrelated to this run.

## Open decisions for Krish before 2 Oct

1. **X01 reading.** The memo v3 carries the literal reading (short case 0.55; C02 (d)'s directional "moderate" sentence trips the
   gate) with the material reading (0.48) in the caption. Both are defensible from the registered text; the literal one is what
   the question says, the material one is what a judge will assume "mid single digits" means. Also: if the memo keeps its own
   breaker column (which requires an FY sentence at ≈36%), the short-first precedence split 0.11 / 0.59 is the coherent one.
2. **Which price object leads.** The 12-month fundamental targets give PW $148 (−12%); the run's reaction-function objects give a
   15 Dec median of $166 and PW mean $167.3 (−0.1%), with P(≤ $150) 0.30. The memo v3 carries both, labelled; the recommendation
   line still quotes the fundamental target. Decide whether the pitch is the 5 Nov event (then the honest headline is a −5%
   base-case day and a coin-flip-and-a-half on ≤ $150 by December) or the FY27 reset (then the 12-month table leads and the
   S02 numbers are the risk that the reset takes longer than the horizon).
3. **R01 headline.** 0.39 is the nowcast-only object the fine print demands; the management-delivery construction (0.57–0.82) and
   the sequential class (0.44–0.50) are published at zero weight. If the memo wants a blended "management delivers" probability
   for risk 1, that is a memo decision to write down there; v3 quotes 0.39 with the alternative range in parentheses.
4. **B08's 10-K purchase-obligation convention** (does the $1,749M hosting commitment schedule count as a "quantified FY27 spend"?)
   and **the 4Q26 hosting line** ($100M line build vs $85M in B08): the line build's own 4Q26 cost of revenue ($578M) sits above
   B08's $575M threshold, which the memo should not show next to a 0.44.
5. **F03's convention** (literal adopted: a "stable year-over-year" sentence is (e), not a bucket; (e) 0.48 is modal). B12 is the same
   object; quote one of them.
6. **S02/S04 state vector.** S02 rev 2 carries accelerating 0.32; the adopted A09 states say 0.26. Re-running `abnb_path_mixture_v2.py`
   on the adopted states moves the 15 Dec median by about −$1 and S04 by < 0.02; not done, footnoted.
7. **FY27 margin build** (carried from v2): the run's top-down 34.6% vs the line build's 35.7%; pick one before 2 Oct. B08 and B12
   are priced off the line build.
8. **B02 0.12 vs 0.09** and **C11 0.76 vs ≈0.73**: adopt the run-coherent numbers or the auditors'; v3 quotes the run numbers
   with the alternatives noted here.
9. **R12's reading** (any-day 0.47 vs 15 Dec 0.43) — only matters if R12 is quoted; v3 does not quote it.
10. **Re-run trigger.** When the September Inside Airbnb dumps land (18–30 Sep), re-run E (reviews index), then
    `questions/risk-q3-nights-meets-guide/datasets/a09_v2_print_distribution.py`, then
    `questions/scenario-probabilities/datasets/x01_joint.py` and `x01_reclassify_v2.py`, then `analysis/src/pitch_forecasts/aggregate.py`.
    A +0.5pt move in the print centre is ≈ +0.02 breaker / −0.04 short / +0.03 none on X01 and takes P(≤ 8.5%) from 0.29 to 0.22
    on the partition (PW 12-month target $148 → about $154 at a 10.0 centre; $142 at 9.0).

## Method note

The flow as run: 54 questions in 19 batches; per batch a Fable forecast agent (INITIAL mode of Krish's forecast skill, research log
in the skill's schema plus a FORMAT-1.0-style JSON), an independent read-only audit, and a Fable audit-response agent producing
revision 2. Audits A01–A09 ran on Codex `gpt-6-astra` (one at a time, then two concurrently from 04:42 when the audit queue became
the bottleneck). Codex's usage limit was exhausted at 05:24 (reset 19 Sep 19:05), so audits A10–A19 ran as independent Opus agents
on the same `prompts/audit_<batch>.md`; every Opus audit shipped a stdlib reproduction script that ran clean from the repo root.
Two session-limit outages interrupted the run (00:05–03:50 and 05:24–08:50); agents killed mid-work were relaunched from disk
truth (`state.py`), which is why A02, A08, A09, A12, A14 and A15 show two launches. At 11:39 the first Fable account hit its weekly
limit; by Krish's decision (11:45) the remaining risk/bonus responses (A12, A15 finisher, A16, A17) ran on Opus, A14 and A18
became audit-only (the auditor's numbers are adopted here; their logs stay revision 1 + audit), and Fable was reserved for A19
(X01) and this synthesis. Totals: about 21 forecast-agent launches, 21 response-agent launches, 9 Codex audits and 10 Opus audits;
WebSearch stayed inside the 5-per-question cap; Kalshi and Polymarket were queried directly. Every batch's response reproduced
every number in its audit; no audit finding was rejected outright, and the largest single corrections were A19-01 (X01's base
gate), A06-01 (S01's base-case cell), A05-01 (C11's incoherent headline), A13-02 (R14's one-sided $5.3 EV) and A10-01/A16-03
(statements priced as delivered take-rate steps).

## What was written after this file

- `deck/drafts/memo_v3_short_2026-09-17.md`, `.html`, and `deck/drafts/ABNB_short_memo_draft_2026-09-17.pdf` (3 pages, Chrome
  headless, page count checked with pypdf and all three pages rasterised with pypdfium2 and inspected; HTML typography tightened
  from 9.4pt to 8.4pt base to hold three pages with the two added scenario tables).
- `docs/pitch-forecasts/MEMO_CHANGES.md`: every change v2 → v3 with its source, and what was deliberately left alone.
