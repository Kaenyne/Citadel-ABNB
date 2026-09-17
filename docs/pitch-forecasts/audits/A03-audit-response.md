# Response to audit A03 (C04 fy26-margin-sentence, C09 q4-margin-direction-sentence)

Response date: 2026-09-17
Responds to: `A03-research-audit.md` (Astra, gpt-6-astra, read-only)
Revised research: `questions/fy26-margin-sentence/research-log.md` and `questions/q4-margin-direction-sentence/research-log.md` (both revision 2)
Revised forecasts: both `forecasts/2026-09-17-forecast.json` (revision 2; both vectors moved)
Revised model: `questions/fy26-margin-sentence/datasets/mc_sentence_model_v2.py` (mirrored in the C09 folder; the revision-1 `mc_sentence_model.py` and its outputs are left untouched as the audit trail); rebuilt ledgers `fy_margin_guide_ledger_v2.csv`, `quarterly_margin_sentence_ledger_v2.csv`
Reproduction script: `A03-reproduce.py` (the audit's script, saved verbatim; output in `A03-reproduce.stdout.txt` and at the end of this file)

## Summary

Twenty findings. Seventeen accepted, three accepted in part (A03-04, A03-08, A03-12), none rejected. Every number in the audit reproduced exactly (the script ran clean from the repo root with `py -3.13 -B`; no path fix was needed). Both independent comparison vectors also reproduce (C04 b 0.3877; C09 0.2933 / 0.2448 / 0.4119 / 0.05 before rounding).

Headline vectors, revision 1 → revision 2:
- **C04** (held / ≈36% / ≥36.5% / softer / none): 0.26 / 0.42 / 0.05 / 0.24 / 0.03 → **0.33 / 0.30 / 0.05 / 0.27 / 0.05**. The modal option moves from "approximately 36%" to "floor held", though the three live outcomes are within 6 points of each other.
- **C09** (down / flat / up / none): 0.28 / 0.27 / 0.40 / 0.05 → **0.22 / 0.26 / 0.47 / 0.05**.

What moved the numbers: (1) the required cushion over the stated level is now a separate object from rounding (A03-04): under a strict 50bp-grid rule with c_req ~ N(0.10, 0.15) the +50bp conversion is affordable in 25% of draws, and the revision-1 optimistic threshold (35.85) keeps only half the weight; (2) hold-and-cut is implemented as a Q4 cost cut before either sentence is generated (A03-09), which moves C04 mass from (d) to (a) and, because the cut lifts Q4 margin, moves C09 mass from (a) to (c); (3) C01's revision-2 guide histogram (mean $3,101M, sd 97; P(below Street) 0.73) replaces the provisional N(3,090, 80); (4) the Q4 internal centre is set at 29.0 (mean of the four team Q4 views) instead of 29.3. Every published number — both vectors, the C04×C09 joint, the conditionals on C01 — now comes from one Monte Carlo run (A03-05), and the coherence checks are shown in each log's §6.

What did not change: the structural reading that the FY sentence and the Q4 direction are one decision under the budget identity (now stated as a dependency constraint, not a rule), the exact distinction between a retained floor and an "approximately" point, and the absence of any external market.

## Finding-by-finding

### A03-01 (major, C09) — reference class denominator: accepted
Reproduced: filtering `02_guidance_ledger.csv` to the two exact margin metrics and requiring target − print = 1 quarter gives 20 sentences; the 2Q25 letter's 4Q25 row is two quarters ahead and drops; joining to the 21 print opportunities since 2Q21 leaves 4Q21 without a next-quarter margin sentence (its Q1 2022 outlook reads "we expect to achieve our first positive Q1 Adjusted EBITDA in Airbnb history" — dollars, not margin). Counts: 20/21 disclosed; down family 11, flat 1, up family 8; since the 2Q24 print 7/1/1 of 9; Novembers 5/5 (3 up-family, 2 down); W1 9/1/4 of 14, W2 7/1/2 of 10. `quarterly_margin_sentence_ledger_v2.csv` carries the horizon check, the print calendar and the 4Q21 "none" row. C09 claims 1–2 and §5 rewritten; the base-rate estimate is unchanged at c 0.35 because the corrected up share (8/20 = 0.40 vs rev 1's 8/21 = 0.38) and the corrected recent count (1/9 vs 1/10) offset.

### A03-02 (major, C04) — "two mid-year raises" false: accepted
Reproduced from the panel: 1Q26 `fy_margin_action = first`, `fy_margin_raised = 0`, delta 0 (the May letter replaced "stable year-over-year" = 35.1 with a numeric floor of 35%, which is not a raise); 2Q26 `raised`, 1, +0.5. Pre-2026 coded raises 0/8 reproduces, but the letters show qualitative mid-year upgrades in FY22 (Feb "directionally in-line" → May "modest ... expansion") and FY23 (May "broadly in-line" → Aug "modestly higher"), so 2026 is not the first year with mid-year strengthening; in 2023 the mid-year upgrade was followed by a further November raise, in 2022 by no FY sentence. The "spent cushion" conditioning of the base rate is replaced by conditioning on the floor's cushion (team card +0.23pp vs FY24 +1.4 / FY25 +0.6 realised at the August floor). Claim 15 rewritten.

### A03-03 (major, C04) — outcome-selected disclosure class: accepted
Reproduced: the 3Q22 letter's Outlook gives only the Q4 sentence ("in-line to modestly higher than last year's margin of 22%") although a FY2022 margin-expansion guide had been in force since May. Reference classes now separated: 2/2 numeric-floor conversions; 3/4 November disclosures with a pre-existing FY margin outlook. (e) raised 0.03 → 0.05.

### A03-04 (major, C04) — positive cushions used to justify a negative required cushion: accepted in part
Reproduced the code (`fy >= 36 - tol`) and the diagnostics: tolerance −0.10 gives raw b 21.7%, zero 26.8%, +0.15 35.3%. Accepted that "36% with any cushion" was rounding optimism and that "zero tolerance requires a 0.9 cushion" was wrong (withdrawn). The revision-2 rule separates the two objects: the strict branch rounds (internal − c_req) down to the 50bp grid with c_req ~ N(0.10, 0.15), labelled judgment (realised November cushions are the only observable and do not identify the internal forecast); a thin-cushion branch keeps the 35.85 threshold at weight 0.50. In part: the thin branch is retained rather than removed, because one of the two precedents (2025, realised cushion +0.10) is consistent with management accepting a near-zero cushion, and the sensitivity table now shows the strict-only case (b 0.22) beside it.

### A03-05 (major, both) — conditionals did not belong to the final marginals: accepted
Reproduced: with P(C01) = 0.80 the published C04 conditionals give 0.376, not 0.42; C09's give (0.296, 0.254, 0.400, 0.050); the raw joint reweighted to the final C04 gives C09 (0.260, 0.218, 0.472, 0.050). Revision 2 publishes one joint (`mc_joint_and_conditionals_v2.json`) and derives every marginal and conditional from it; both logs' §6 show the arithmetic (C04: 0.731 × 0.2245 + 0.269 × 0.4874 = 0.295; C09: Σ P(C04) P(c | C04) = 0.469). The conditioning event is now "guide midpoint < $3,161.02M" on the C01 rev-2 histogram (P 0.731), not the rev-1 0.80.

### A03-06 (major, both) — three estimates not independent: accepted
Both anchors are marked `NOT_INDEPENDENTLY_DERIVED` in the logs and JSONs, described as internal-prior comparisons, and their shared inputs (November history, budget identity, LSEG consensus) are listed. C09's "un-priced remainder" phrase is withdrawn (the 0.6/0.4 prior already summed to one; it is now scaled to 0.95 with (d) 0.05). The dated LSEG margin level is recorded as the one genuinely external input, with the wording conversion labelled as a further judgment.

### A03-07 (major, both) — asymmetry versus the 14 Sep priors overstated: accepted
Reproduced from `05_mgmt_statements_v2.md`: the 35% branch reads "the two mid-year raises already spent the cushion; 9M y/y only +0.3"; the note carries the 28.3% Q4 base and the ≈36% → Q4 ≈30.9% arithmetic; M3 discusses the Street and the Q3/Q4 trade-off. The logs now name the new input as the C01 distribution and its transmission to management's internal margin through Q4 revenue (and, in revision 2, the required-cushion reading of the two precedents), and drop the claim that the previously considered items justify the departure.

### A03-08 (major, both) — realised margins do not identify internal forecasts, bias or band: accepted in part
Reproduced: W2 realised y/y mean −0.19, median −0.94, 4/10 positive, W1 mean +0.47; the rev-1 Q3 normal put 44.5% above the 50.085 ceiling. Accepted: the statistics are restated as actual outcomes against a directional bound; the 0.3 tilt, the flat band (now 0.7 ± 0.25) and the Q3 distribution are labelled judgments with sensitivities (tilt 0 → c 0.53, 0.7 → 0.39; band 0.4 → b 0.15, 1.0 → 0.36; Q3 49.4 / 50.4 / 52.4 / sd 1.6 rows). In part: the Q3 centre stays at the team card's 49.95 (brief rule 6: the repo's calculated number is the input) rather than being truncated at the ceiling; the ceiling-respecting case (49.4) is the first Q3 sensitivity row and is what a "13/14 met" reading would use (C04 b 0.22, a 0.39).

### A03-09 (major, both) — "hold and cut" relabelled without changing costs: accepted
Reproduced: `40_short_case_summary.csv` gives the $176.709M cut lifting 4Q26 from 23.589% to 29.547% (5.96pp); replaying the rev-1 split gives C04 ≈ (0.303, 0.353, 0.054, 0.269, 0.020) while the code left Q4 draws untouched. Revision 2 implements the intervention: when the internal FY is below 35.5, with p 0.50 a Q4 cut restoring floor + 0.1 (capped at 5.9pp) is applied to the Q4 margin draw before either sentence is written; 17.9% of draws are cut by 2.17pp on average. The line build's Q4 treatment is now described as a floor-preserving assumption, not evidence. Effect: C04 (a) 0.19 → 0.34 and (d) 0.42 → 0.27 relative to a never-cut run; C09 (c) 0.40 → 0.47.

### A03-10 (major, C09) — budget identity used as a language implication: accepted
Reproduced: `23_card_budget_identity.csv` Q4 30.125% at FY 36 / Q3 49.94 but 29.002% at FY 35.75; FY 36 and Q4 28.3 coexist at Q3 51.147% on the bridge path; the rev-1 MC itself gave P(c | raw b) 0.694. The logs now state the Q3, revenue and sentence-type conditions, call the identity a dependency constraint, and read the Q4 sentence independently; P(c | C04 = b) is 0.71 from the joint, and the 3Q25 precedent (dollar clause vs margin clause) is the reason the margin clause alone resolves.

### A03-11 (major, both) — LSEG fields mixed and undated: accepted
Reproduced: EBITDA mean $913.68388M (n 36, sd $26.52396M) / revenue $3,161.81627M (n 37) = 28.897437%, both observed 2026-09-07 and captured into the 11 Sep row; `lseg_margin_mean_pct` 28.05833%; sd / revenue = 0.8389pp. Claims now carry vendor, field, observation date and capture date; the ratio is preferred because it is consistent with the dollar consensus the print is measured against and with `23_vs_consensus.csv`, but the logs note that the Street's Q4 sign is +0.6 on the ratio and −0.2 on the margin field, so the Street does not call a direction this year (C09 claim 5); the 0.8389pp figure is labelled as the dispersion conversion it is.

### A03-12 (major, C04) — option set not exhaustive for unusual numerics: accepted in part
Accepted that 36.25–36.49 and a nudged floor in 35.51–35.74 are undefined by the registry. Conventions adopted and stated in §0b (36.25–36.49 → (c); floor in 35.51–35.74 → (a); point in 35.51–35.74 → (d)), flagged for the registry owner, with the ~1–2% ambiguity mass identified (management has never guided margin off the 50bp grid in 20 FY guides). In part: the question is not changed and the mass is carried inside the named options rather than as a separate bucket, because the registry has no residual option.

### A03-13 (minor, C04) — FY ledger included FCF spread rows: accepted
Reproduced: 22 copied rows including two `fcf_margin_minus_ebitda_margin_pts` rows; exact filtering gives 20. Rebuilt as `fy_margin_guide_ledger_v2.csv` with `guide_id`, `metric` and units retained. The 2/2 November result is unaffected.

### A03-14 (minor, both) — 3Q25 "flat-to-down slightly" describes dollars: accepted
Reproduced from the letter: "Adjusted EBITDA in Q4 2025 to be flat-to-down slightly ... and for Adjusted EBITDA Margin to decline". The rebuilt quarterly ledger classifies the margin clause; "slightly" now rests on n 2 (mean absolute 0.960pp) with the three-case 1.491pp recorded as a rejected extraction; C09 §0b adds the convention that the margin clause resolves.

### A03-15 (minor, both) — "no market exists" and "volume null": accepted
Reproduced: `hasMore = true`, `totalResults = 190` with five saved events; Kalshi `volume` is a null key while `volume_fp` is 428.14 at >148m and 998.66 at >146m; `updated_time` is a 2026-08-04 batch stamp. Polymarket pagination completed in this response (4 pages, 190 results, 187 unique titles, saved as `sources/polymarket_search_airbnb_page{1..4}_20260917T0757*.json` in both folders): the open Airbnb events are the weekly and monthly price ladders and "Up or Down on September 17"; the one earnings-language market ("What will Airbnb say during their next earnings call?") is closed and concerned a past call. Both logs now say "none found in the saved searches" and report `volume_fp` in contracts with `volume_24h_fp` 0.

### A03-16 (minor, both) — 72-hour check undocumented and off-subject: accepted
Reproduced from `web_search_log.md`: "Airbnb ABNB this week", no date filter, stock-news subject, one stale result acknowledged. One further query was run with a date term on the decisive variable ("Airbnb fourth quarter 2026 marketing spend margin guidance news September 2026", the 5th and last WebSearch of the shared budget): results were the 8-K letters, the 1Q26 results page, Fool transcripts from February and May, Quartr and a May TIKR piece — nothing published in September on Q4 spend. Both logs record it as a limited search that found nothing, not as confirmation.

### A03-17 (minor, both) — monitoring updates not probability vectors: accepted
Reproduced: C04's "b +4, d −3" adds one point; C09's "c +5, a −3" two; "a +3 per launch" had no funding rule. Both calendars are rewritten as full re-runs of the script with the named input moved (each row gives the complete vector), and launch announcements move the Q4 centre once, capped at −1.0, so correlated announcements do not accumulate.

### A03-18 (minor, C04) — threshold/probability pair: accepted
Reproduced: rev-1 P(FY ≥ 36.5) 7.68%, ≥ 36.7 3.64%, ≥ 36.9 1.54%. Revision 2 reports the full threshold table from the new run (≥ 36.5 0.091, ≥ 36.7 0.048, ≥ 36.9 0.024) and distinguishes the convention branch's 36.9 condition from the strict branch's 36.5 + c_req.

### A03-19 (minor, C04) — log-score claim unsupported: accepted
Reproduced: 0.002745 nats for one point each into (c) and (e); 0.005167 for both into (e); the split leaves (e) at 4%. The "~0.05" claim is replaced in §6 by the computed figure under the revision-2 vector (0.0025 nats), with the alternative vector stated.

### A03-20 (minor, C09) — 3Q21 realised figure: accepted
Reproduced from the ledger: `actual = 24.10`, `comparator_value = 11.9`, `distance_from_mid = 12.20`. Claim 1 now reads +24.1pts realised y/y, +12.2 above the guided comparison; the up-family classification stands.

## What the audit missed

1. **The LSEG margin-field choice changes the sign of the Street's Q4 view.** The audit treated the ratio-vs-field question as a reporting issue. On the margin field (28.06) the Street implies −0.2pp against 4Q25, on the ratio (28.90) +0.6pp; the C09 base-rate argument "management's stated sign matched the Street's 3/3" therefore does not call a direction this year on either reading, which is why the base-rate estimate now sits at c 0.35 rather than higher. Recorded in C09 claims 4–5.
2. **The Q3 revenue and Q4 guide draws were independent in revision 1.** C01's model derives the guide from the same 3Q26 GBV that drives 3Q26 revenue, so the two co-move; revision 2 draws them with ρ 0.5 through a common shock. The effect on the vectors is under a point (the `rho_0` sensitivity row), but the FY-internal tails are wider than revision 1's.
3. **C01's revision-2 sd is 97, not 80, and its P(below Street) is 0.73, not 0.80.** The audit used the provisional inputs it was given. The wider guide distribution is worth about +0.01 on C04 (c) and the lower P(below) about +0.02 on (b); both are inside the revision-2 run.
4. **Astra's own C09 comparison commits the A03-08 conflation.** Its Normal(28.6, 1.8) is a predictive distribution of the realised Q4 margin read as if the sentence described the realised outcome, with no management-expectation layer, no tilt and no cut lever; it also averages the line build's 28.3 with the Street ratio while noting that the ratio is not the margin field. It is recorded as the audit's number (C09 claim 18) with that caveat.
5. **Astra's C04 blend gives the 2/2 convention 25% weight unconditionally.** That is itself the "convention regardless of the arithmetic" branch the audit criticises in revision 1; revision 2 keeps such a branch (weight 0.50) but only above the 35.85 threshold, and shows the strict-only case beside it. This is the one named choice behind the 9-point gap on (b).
6. **The FY revenue sentence is decided jointly with the margin sentence.** At a guide midpoint of ~$3,100M and a 3Q26 print near $4,800M, FY26 revenue is ~$14,190M (+15.9%), so the "at least mid teens" floor is being converted at the same time; neither the audit nor revision 1 modelled the joint wording decision (C03 is a separate question). Recorded as an unmodelled dependency, not priced.
7. **The audit did not test the cut cap.** The line build's $177M cut (5.9pp of Q4 margin) bounds the hold-and-cut branch; in revision 2 the cap binds on 1.6% of draws (internal FY below ~34.2). Without the cap the C04 (a) share would be the same; with a lower cap (say 3pp, a "visible but partial" cut) about a third of the cut draws would still leave the floor short — a case the short memo should keep as its "floor at risk" sentence.

## Reconciliation with Astra's vectors

| | Astra | Revision 2 | Gap on the leading option | Decision |
|---|---|---|---|---|
| C04 | 30 / 39 / 6 / 22 / 3 | 33 / 30 / 5 / 27 / 5 | b: −9; a: +3 | Hold. Under 10 points on every option. The b gap is the unconditional 25% convention weight in Astra's blend versus the conditional 50% here; the thin-cushion weight 0.65 (rev 1) gives 0.32 and Astra's structure 0.39, both recorded in C04 §7/§9. |
| C09 | 29 / 25 / 41 / 5 | 22 / 26 / 47 / 5 | c: +6; a: −7 | Hold. Under 10 points on every option. Astra's object is the realised Q4 margin; this log's is management's expectation with the cut lever (p_cut 0 → c 0.40, the Astra-like case). Recorded in C09 §9. |

Against the repo priors (the designated anchors, both NOT_INDEPENDENTLY_DERIVED): C04 (b) 0.55 → 0.30 is a 25-point divergence whose asymmetry is the C01 distribution transmitted to management's internal FY margin plus the required-cushion reading of the two precedents; C09 (a) 0.50 → 0.22 is a 28-point divergence whose asymmetry is the low 4Q25 base, the Street inside the flat band on either field, and the joint with C04 (a raise or a held-and-cut floor both put Q4 at or above 28.3). Both are written in the logs' §5.

## Reproduction output

`py -3.13 -B docs/pitch-forecasts/audits/A03-reproduce.py` from the repo root, 2026-09-17 (no edits to the script; saved to `A03-reproduce.stdout.txt`):

```
FY EBITDA-margin rows: 20
Copied rows / FCF rows: 22 2
Exact next-quarter sentences: 20 {'down': 9, 'up': 7, 'flat_to_down': 2, 'flat_to_up': 1, 'flat': 1}
All print opportunities: 21 {'down': 11, 'flat': 1, 'up': 8, 'none': 1}
No quarterly sentence: ['4Q21']
Since 2Q24: 9 {'down': 7, 'flat': 1, 'up': 1, 'none': 0}
Novembers: 5 {'down': 2, 'flat': 0, 'up': 3, 'none': 0}
Target window 1Q23 through 2Q26: 14 {'down': 9, 'flat': 1, 'up': 4, 'none': 0}
Target window 1Q24 through 2Q26: 10 {'down': 7, 'flat': 1, 'up': 2, 'none': 0}
Midyear actions: [{'quarter': '1Q22', 'fy_margin_action': 'reiterated', 'fy_margin_raised': 0.0}, {'quarter': '2Q22', 'fy_margin_action': 'reiterated', 'fy_margin_raised': 0.0}, {'quarter': '1Q23', 'fy_margin_action': 'reiterated', 'fy_margin_raised': 0.0}, {'quarter': '2Q23', 'fy_margin_action': 'reiterated', 'fy_margin_raised': 0.0}, {'quarter': '1Q24', 'fy_margin_action': 'reiterated', 'fy_margin_raised': 0.0}, {'quarter': '2Q24', 'fy_margin_action': 'reiterated', 'fy_margin_raised': 0.0}, {'quarter': '1Q25', 'fy_margin_action': 'reiterated', 'fy_margin_raised': 0.0}, {'quarter': '2Q25', 'fy_margin_action': 'reiterated', 'fy_margin_raised': 0.0}, {'quarter': '1Q26', 'fy_margin_action': 'first', 'fy_margin_raised': 0.0}, {'quarter': '2Q26', 'fy_margin_action': 'raised', 'fy_margin_raised': 1.0}]
Pre-2026 coded raises: 0 / 8
Numeric-floor November rule: [{'print': '3Q24', 'predicted': np.float64(35.5), 'stated': 35.5, 'exact': np.True_}, {'print': '3Q25', 'predicted': np.float64(35.0), 'stated': 35.0, 'exact': np.True_}]
Exact matches: 2 / 2
Ledger November cushions: [0.77, 0.8999999999999986, 0.10000000000000142]
Mean ledger November cushion: 0.59
FY2022 pre-November guide: ['We continue to forecast delivering Adjusted EBITDA margin expansion for the full-year 2022 relative to 2021']
November type hits: 4 / 5
Cushions by bucket: {'AUG': {'count': 4, 'mean': 3.0614505170827844}, 'FEB': {'count': 4, 'mean': 3.0614505170827844}, 'MAY': {'count': 4, 'mean': 3.0614505170827844}, 'NOV': {'count': 3, 'mean': 0.5920515247256048}}
Realised window 2023Q1 n 14 guide met 13 yoy mean/median/positive 0.47264285714285703 -0.601 6
Realised window 2024Q1 n 10 guide met 9 yoy mean/median/positive -0.19360000000000002 -0.9395 4
Stored slightly: 3 1.4912408456978614
Margin-only slightly: 2 0.9603424223125563
Historical identity maximum error: 0.0
Q4 actual minus November-implied: 3 2.86838034238736
Pre-November Street: [{'quarter': '2023Q4', 'street_q4_margin_pct': 29.518654021988883, 'seasonal_naive_q4_margin_pct': 26.603575184016822}, {'quarter': '2024Q4', 'street_q4_margin_pct': 29.934987030644805, 'seasonal_naive_q4_margin_pct': 33.27321911632101}, {'quarter': '2025Q4', 'street_q4_margin_pct': 27.98961055592747, 'seasonal_naive_q4_margin_pct': 30.846774193548388}]
Street direction matches: 3 / 3
2022-25 Q4 mean/sample SD: 29.754326248741535 2.9232746597182495
Current LSEG fields: {'as_of_row_date': '2026-09-11', 'ebitda_obs_date': '2026-09-07', 'revenue_obs_date': '2026-09-07', 'ebitda_mean': 913.68388, 'revenue_mean': 3161.81627, 'ebitda_n': 36.0, 'revenue_n': 37.0, 'implied_margin_pct': 28.897437484563262, 'lseg_margin_mean_pct': 28.05833}
Ratio margin: 28.897437484563266
EBITDA dispersion / fixed revenue: 0.8388836584739314
Live identity multipliers: 4.489508862512732 -1.5116024162512356
FY36/Q4 28.3 requires Q3 margin: 51.147146683883115
Bridge implied Q4 guide: 3059.4030114230018
Final sums: 1.0 1.0
C04 b implied by published conditionals: 0.376
C09 implied by published conditionals: {'a': 0.296, 'b': 0.254, 'c': 0.39999999999999997, 'd': 0.05}
Raw joint reweighted to final C04: {'a': 0.2600464532978016, 'b': 0.21767360477611017, 'c': 0.4719277190720954, 'd': 0.05035222285399289}
Polymarket pagination: {'hasMore': True, 'totalResults': 190}
Kalshi saved liquidity: {'ticker': 'KXABNB-26NOVNEB-148000000', 'volume': None, 'volume_fp': '428.14', 'yes_bid_dollars': '0.5000', 'yes_ask_dollars': '0.5500'}
Kalshi saved liquidity: {'ticker': 'KXABNB-26NOVNEB-146000000', 'volume': None, 'volume_fp': '998.66', 'yes_bid_dollars': '0.6300', 'yes_ask_dollars': '0.6600'}
Expected log cost, nats: 0.0027453289379102113
Expected log cost, nats: 0.005167100238181647
Independent C04 affordability blend: 0.3876505701970903
Independent C09 before rounding: [0.2933487775272504, 0.2447918991993794, 0.41185932327337016, 0.05]
No files written.
```

Note: the "Final sums" and "implied by published conditionals" lines above were computed against the revision-1 JSONs. Re-run after the revision-2 JSONs were written (same script, same keys): `Final sums: 1.0 1.0`; `C04 b implied by published conditionals: 0.274` and `C09 implied by published conditionals: {'a': 0.246, 'b': 0.266, 'c': 0.436, 'd': 0.05}` — these use the script's hard-coded P(C01) = 0.80, whereas the revision-2 conditionals are defined on the C01 rev-2 histogram's P(below) = 0.731, at which they return the marginals exactly (0.731 × 0.2245 + 0.269 × 0.4874 = 0.295; 0.731 × 0.3526 + 0.269 × 0.7849 = 0.469; each log §6). The "raw joint reweighted" line still reads the revision-1 joint file by design.

Revision-2 Monte Carlo (`py -3.13 -B questions/fy26-margin-sentence/datasets/mc_sentence_model_v2.py`, seed 20260917, 400,000 draws; full log in `datasets/mc_run_log_v2.txt`): internal FY26 mean 35.717, sd 0.582; P(≥ 36.10) 0.2513; internal 4Q26 (pre-cut) mean 28.88, sd 2.13, P(> LY) 0.603; cut branch 17.9% of draws, mean +2.17pp; C04 0.3366 / 0.2953 / 0.0458 / 0.2727 / 0.0496; C09 0.2243 / 0.2566 / 0.4691 / 0.0500; P(guide < $3,161M) 0.731.

## Final table

| question | revision-1 vector | Astra's vector | revision-2 vector | anchor | \|final − anchor\| on the leading option |
|---|---|---|---|---|---|
| C04 — held / ≈36% / ≥36.5% / softer / none | 0.26 / 0.42 / 0.05 / 0.24 / 0.03 | 0.30 / 0.39 / 0.06 / 0.22 / 0.03 | **0.33 / 0.30 / 0.05 / 0.27 / 0.05** | repo prior (M3/WS05, 2026-09-14): b 0.55, a 0.18; NOT_INDEPENDENTLY_DERIVED | 0.15 on (a), the final's leading option (0.25 on (b), the anchor's); vs Astra 0.03 on (a), 0.09 on (b) |
| C09 — down / flat / up / none | 0.28 / 0.27 / 0.40 / 0.05 | 0.29 / 0.25 / 0.41 / 0.05 | **0.22 / 0.26 / 0.47 / 0.05** | repo prior (WS05/M3, 2026-09-14): a 0.50, c 0.35; NOT_INDEPENDENTLY_DERIVED | 0.12 on (c), the final's leading option (0.28 on (a), the anchor's); vs Astra 0.06 on (c) |
| C04 × C09 joint (for X01) | raw MC joint, pre-override | — | `datasets/mc_joint_and_conditionals_v2.json`: P(c \| b) 0.71, P(c \| a) 0.40, P(c \| d) 0.21; P(b \| C01 below) 0.22, P(b \| not below) 0.49; P(C09 c \| C01 below) 0.35, P(c \| not below) 0.78 | — | — |
