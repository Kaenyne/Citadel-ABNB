# Memo v5 (29 Sep 2026)

The team's own-words memo (29 Sep), with the fixes from Bill's feedback and the two later reviews, and a promotional pass
that keeps the team's voice. Built in Microsoft Word with Aptos: **2 pages**, page 2 ending at 750pt of 756pt, so there is
**no slack**. Charts are the same two as v4.3 (nights 1Q23–4Q27; margin bridge), floated at 3.6in.

## Rebuild, from the repo root

```
Rscript analysis/src/pitch_charts_pm/graph1_history.R
python analysis/src/pitch_charts_pm/compose_v4_3.py
NODE_PATH=<dir with node_modules/docx> node deck/drafts/memo_v5_2026-09-29/build_memo.js
```

## What changed from the team's text

| Area | Change | Evidence |
|---|---|---|
| Title / thesis | "Reserved Now, Paying Later"; "re-acceleration is not a turnaround; it was bought"; the 6-month horizon is tied to the two prints; February = FY27 outlook | Feb letters carry a full-year margin outlook every year since 2023 (`02_guidance_ledger.csv`) |
| Overview | Required by Citadel, so kept. The "fallen 9 of 19 times" sentence is cut: it is the day-1 framing Bill questioned. | |
| Street section | Adds management's 3Q26 guide ("low double digits", 10–12%). Adds that nights have beaten guidance in every 2026 quarter and that the call is the first print below management's nights guide. | Ledger: 16 of 16 nights guides met or beaten; 4Q25 guide 4–6% vs 9.8%; 1Q26 7–9% vs 9.2%; 2Q26 "slightly decelerate" vs 10.3%; 3Q26 guide 10–12% |
| Bundle | Level vs growth ("lifts the level for good, growth only once"); laps named as laps; "if non-RNPL bookings still cancel at 16%"; payment is due before the free-cancellation window closes, not just before check-in; the timing comes from the cohort model; FX removed from this nights paragraph | Reviewer points; `overnight2/D` cohort engine |
| Stays index | ~6% (not 5.99%); ±1.9pp is defined as out-of-sample error; the naive benchmark is named; the post-RNPL gap (+0.7pp average) is added, giving 9.6%; "point estimate"; "agree", not "confirm" | `REVIEWS_INDEX_v2.md` §2.4 (Stage C: gaps +0.66, +0.71, −0.07, +1.59); band = pre-RNPL W2 walk-forward RMSE 1.88 |
| ADR | Fixed as agreed: $175.66 includes the FX drag; ex-FX growth matches the Street; "because we model FX differently" | `adr_v3_corrections.md` §3 (midpoint comparison run post hoc, 23 Sep) |
| Growth section | Retitled "Growth now depends on new supply". Adds that the new-listing contribution is also slowing (18.9 → 11.4pts), which answers the cannibalization point. The North America share sentence is cut (the ADR paragraph carries the mix shift). Spain alone = 65k. The CoStar line is cut. | thesis 2 draft (N1 dossier); `factor_register.md` |
| Margins | The team's rewrite, plus: "incremental revenue per incremental S&M dollar"; AI savings ~$40M vs hosting +$90M (FY26, like for like); "our estimates"; management's "reinvest" quote; **FY26 34.9%** against the FY26 floor | Model v2 `Income_Statement` rows 57–59, 124, 132, 137; 10-Q $17M |
| Catalysts | Management's guide named; February = FY27 margin outlook + the 1Q27 guide lapping +17.9%; "+6.4% nights, +7.5% revenue" | |
| Valuation | Rebuilt on FY27: 13.7x consensus FY27 multiple on our $4.89B = **$130 (−14%)**; 12.5x = **$120 (−21%)**; net cash $9.6B (cash $12,069M − debt $2,476M); 589.6M shares. The "historical trough" claim is dropped. | Arithmetic below |
| Risks | AI: in-house agent bounded by the bundle's peak lift. Buyback: the confounded event study is replaced with EBITDA/multiple plus "bought less after the Aug 2025 drop". Loyalty: the team's two sentences. (4) Main risk + $178 marker. | research log claims 5, 7 |

## Valuation arithmetic

- EV today = $151.39 × 589.6M − $9,593M = $79,666M; consensus FY27 EBITDA $5,826.4M → **13.67x**.
- 13.67 × $4,894.7M + $9,593M = $76,519M ÷ 589.6M = **$129.8**.
- (120 × 589.6 − 9,593) ÷ 4,894.7 = **12.50x**, 1.17 turns below 13.67x.
- The ~0.5 turns per point of growth is descriptive: 12-month changes in EV/LTM, `valuation_v1/regression_reproduction.csv`, 0.486. The NTM-level version fails W2. FY27 revenue growth gap: 11.65 − 7.51 = 4.1pts.
- **The model Cover uses a different method** (the average of NTM, FY27 and 4Q26 multiples − $0.70 = $120.19). The memo's bridge lands on the same $120, but update the Cover to show the FY27 bridge, or a judge who opens the model will see two methods.

## Verify before sending (not checked against primary sources here)

1. "The Fed resumed hiking on 16 Sep": the source is a team note (`bonus-interest-income-falls/README.md`). Check the FOMC statement.
2. "Meta's Muse" and the Expedia integration: press only (TravelPulse, 22 Sep).
3. Airfares +25.5% YoY (July CPI): `05_macro-outlook-and-transmission.md`.
4. Spain 65,122 listings removed: `factor_register.md` (2Q26 10-Q).
5. The Bloomberg FY27 nights +8.9%: pull date.
6. SI 3.59% (Bloomberg) and the price: re-stamp on submission day.
7. Export the PDF with no comments or markup; Citadel's limit is 2 pages including any appendix.
