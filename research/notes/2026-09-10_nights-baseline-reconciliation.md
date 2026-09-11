# Nights baseline reconciliation: WS10, the frozen card, PR #32, the H1-H2 bridge and Jessie's simplified model

- **Date:** 2026-09-10. **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Output:** `data/processed/nights_baseline_reconciliation.csv` (every model's 3Q26, 4Q26, implied FY26 and implied H2 on the same disclosed 2025 denominators).
- **Sources compared:** `data/processed/overnight/10_regional_forecast.csv` (WS10), `20_frozen_q3_2026.csv` and `research/notes/overnight/14_master-synthesis.md` (frozen card), PR #32 `origin/krish/nights-quarterly` (`nights_quarterly_total.csv`, `nights_quarterly_na.csv`, `research/notes/nights_quarterly.md`), `data/processed/h2_bridge/` (bridge), `origin/jessie/backlog-conversion` (`nights_simple.py`, `nights_simple.csv`, `abnb_backlog_conversion_annual.csv`, additions to `choice_nights_driver.md` and the EU/backlog note).
- **Fixed inputs:** disclosed nights 1Q25 143.1, 2Q25 134.4, 3Q25 133.6, 4Q25 121.9, 1Q26 156.2, 2Q26 148.3 (millions). H1 2026 is +9.73% y/y on H1 2025. FY25 is 533.0.

## 1. Bottom line

1. **Every quarterly model lands 3Q26 between 9.5% and 10.3% before any lap haircut, and between 8.5% and 9.9% with one.** The models disagree about the size and timing of the product-bundle lap, not about underlying demand. The management guide of "low double digits" sits at the top of the cluster, and only WS10's bull case clears it by more than a rounding.
2. **The "+10.2% consensus" in PR #32 is not consensus.** It is the team's own frozen 5 November card (WS13/WS14, 147.2 million). The WS14 master synthesis states that no public nights consensus was found as of 6 September, and Zacks carries none. PR #32's "essentially in line with consensus" conclusion is the model agreeing with our own earlier number. That line needs relabelling before the PR merges.
3. **Jessie's simplified annual model is inconsistent with the H1 print.** FY26 at +7.9% (575.1 million) with H1 already at +9.7% requires H2 at +5.9%, below every quarterly model, WS10's bear case and the guide. The model's feature-level term (2.0% in 2025 to 3.0% in 2026, so +1.0 point of growth) is too small against management's ~3 points of y/y contribution in 1Q26. It needs re-anchoring on the two 2026 quarters before it is used for 2026. Its FY27 mechanics (bundle plateaus, cancellation drag compounds) survive and are the one thing no other model carries.
4. **Reconciled team baseline:** 3Q26 nights **+9.9%** (146.8 million), band 8.5% to 10.3%; 4Q26 **+8.9%** (132.7 million), band 8.1% to 9.9%; FY26 **+9.6%** (584 million), band 9.0% to 10.0%. Point estimates are PR #32's base, which is built on real quarters with fitted product terms and coincides with the bridge's no-lap case. The band's low end is the bridge half-lap, the high end WS10.
5. **What the guide embeds:** for "low double digits" to hold, the H1 to Q3 transition has to sit at the top of its historical range and the US RNPL anniversary has to cost nothing in Q3, or be offset by international adoption. Management issued the guide on 6 August with July in hand, so that is management's view. The pre-registered card threshold stands: **at or above 10.5% is the surprise; 10.0% or below is the pattern.** A deceleration against 2Q26's 10.3% remains the base case in every model except the naive carry-forward.

## 2. The table

| Model | 3Q26 y/y | 4Q26 y/y | FY26 y/y | Implied H2 y/y | What it assumes about the lap |
|---|---|---|---|---|---|
| WS10 regional build, base | 10.29 | 9.94 | 9.9 | 10.1 | None explicit. NA held at 7 both quarters, although its own rationale says 3Q25 was the RNPL acceleration quarter |
| WS10 bear / bull | 7.97 / 12.44 | 7.02 / 9.94 | 8.7 / 10.5 | 7.5 / 11.3 | |
| Frozen 5 Nov card (WS13/14) | 10.2 | n/a | n/a | n/a | Driver-model base; band 7.9 to 12.6. Mislabelled "consensus" in PR #32 |
| PR #32 NA-lap, base | 9.89 | 8.90 | 9.6 | 9.4 | RNPL fitted +2.4 pts, fee and cancellation redesign +2.3 pts, NA only; RNPL laps 3Q26, rest 4Q26 |
| PR #32 bear / bull | 9.89 / 10.23 | 8.62 / 8.90 | 9.5 / 9.7 | 9.3 / 9.6 | |
| Bridge, pattern only | 9.49 | 10.62 | 9.9 | 10.0 | 2023 to 2025 seasonal transition, no lap |
| Bridge, no lap plus World Cup 0.5 | 9.99 | 10.62 | 10.0 | 10.3 | |
| Bridge, half lap | 8.49 | 8.12 | 9.0 | 8.3 | -1.5 / -2.5 total-level overlay, unfitted |
| Bridge, full lap | 6.99 | 7.62 | 8.6 | 7.3 | -3 / -3, unfitted |
| Naive carry-forward of 2Q26 | 10.34 | 10.34 | 10.0 | 10.3 | |
| Jessie nights_simple (annual) | n/a | n/a | 7.9 | **5.9** | Bundle +1.0 pt for the year, cancellation -0.6 pt; not calibrated to H1 |
| Management guide | ≥10 ("low double digits") | none yet | "at least mid-teens" revenue | | |

## 3. Where the models actually disagree

**The lap.** Three treatments of the same disclosure ("~3 points" of 1Q26 nights growth from RNPL, the cancellation redesign and the single fee, per the RNPL handoff's correction):

- WS10 ignores it in the numbers and mentions it in the rationale.
- PR #32 fits it on four NA observations: RNPL +2.4, the rest +2.3, and laps RNPL from 3Q26 and everything by 4Q26 in North America only. Its ex-NA rows are WS10's, so the international lap is deferred to 1Q27 as a scenario switch that moves FY27 by 1.8 points.
- The bridge overlays -1.5 / -2.5 at the total level as a scenario, with no fit.
- Jessie treats it as a level that plateaus, worth +1.0 point of FY26 growth and zero after, which understates 2026 and is the reason the model misses H1.

The reconciled treatment for 2026 is PR #32's: the lap is real, it is NA-first, and its Q3 cost is about 0.4 points of total nights (NA 7 to 5.6 at a 28.8% share), rising to about 1.0 point in Q4. The bridge's half-lap scenario is a bear case, not a base. The full-lap scenario double counts, because the 3-point figure was the whole bundle and the bundle laps on three dates, not one.

**The World Cup.** WS10 argues that World Cup stay nights were booked in 4Q25 to 2Q26, so 3Q26 *booked* nights get no event lift. The bridge assumed +0.5 for July bookings. The call study records management saying the Q3 guide was "helped by World Cup stays," which is a revenue and check-in statement, not a booked-nights one. WS10 is right for the KPI. The bridge's no-lap case without the World Cup term is 9.5, which is where the reconciled band's centre sits once the small NA lap is applied.

**Underlying demand.** No disagreement. WS10's regional cells (NA 7, EMEA 8, LatAm 18, APAC 17 in 3Q26), PR #32's NA underlying of 3.3 plus product, and the bridge's H1 mean of 9.7 all describe the same H1 2026 run rate. Jessie's 7.5% "pre-RNPL" underlying is the 1H25 print and is a year stale.

**Cancellations.** Only Jessie's model carries the mechanical drag of a rising platform cancellation rate on reported net nights (-0.6 points in 2026, -0.9 in 2027). The RNPL handoff's materiality arithmetic says one point of Q3 growth is 1.34 million net nights, and no RNPL-specific cancellation rate has been measured. Keep the term as a stated risk in the 2027 view, not as a 2026 haircut.

## 4. Two things the Jessie branch adds that should be merged

1. **The backlog-conversion table.** Revenue divided by revenue plus closing unearned fees was a seasonal constant from 2022 to 2025 (about 46% in Q1, 51 to 52% in Q2, 69 to 70% in Q3, 61 to 62% in Q4). 2026 breaks it: Q1 49.5% against 45.5%, Q2 56.0% against 52.0%. That is RNPL removing fees from the unearned pool until closer to check-in, so the reported backlog understates booked business. It is the cleanest public evidence that the payment-timing shift is large, and it is why the bridge's unearned-fees rows are flagged as distorted. It says nothing about demand.
2. **The plateau-plus-drag structure for FY27.** A one-off level gain that stops contributing to growth on dated anniversaries, against a cancellation rate that keeps rising with adoption, is the right skeleton for the February FY27 framing. Re-anchor its 2026 level on the H1 actuals and it becomes the FY27 model; as committed it is not a 2026 forecast.

## 5. Actions

- Relabel the "consensus +10.2%" line in PR #32 as "team frozen card (WS14)"; there is still no public nights consensus. The point-in-time Bloomberg pull remains the open item.
- Adopt 9.9 / 8.9 (3Q26 / 4Q26) as the team nights baseline with the bands above; retire WS10's 10.29 / 9.94 as the base and keep it as the top of the band.
- Drop the World Cup +0.5 from the bridge's no-lap case when the bridge is next re-run; the RNPL handoff's status notice already marks the overlays as scenarios.
- Ask Jessie to re-anchor the simplified model's feature level so that FY26 reproduces H1 at +9.7% with H2 in the 8.5 to 10 band, then use it for FY27 only.
- Pin the international RNPL rollout dates (17 February 2026 announcement, currency exceptions) before deciding whether the 1Q27 lap is NA-only or global. PR #32 is right that this is the highest-value open question for FY27.

## 6. Caveats

- All quarterly NA figures are WS10 estimates with bands; Airbnb discloses regional nights annually and qualitatively by quarter.
- PR #32's two product parameters are identified by launch timing on four observations. The bridge's transitions are three years. Neither can be error-bounded conventionally.
- "Low double digits" mapped to 10 to 12 is a researcher reading, per the RNPL handoff.
- The Jessie branch was inspected, not audited. Its EU and backlog-indicator edits were not reviewed here.
