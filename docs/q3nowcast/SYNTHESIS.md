# Q3 2026 nowcast: what the team's data can and cannot say about the 5 Nov print

- **Date:** 2026-09-11 (day 73 of 92 in 3Q26). **Author:** Krishang Surapaneni (compiled with Claude Code).
- **Branch:** `krish/q3-nowcast`, commits 86d4e0a (H), e9f8eb6 (G), 8a7483d (E), 4072c06 (F). Not pushed. Nothing on main or in the live model changed.
- **Read next:** the four notes under `research/notes/q3nowcast/`.

## 1. The answer

**3Q26 Nights and Seats Booked: +9.5 to +10.0% y/y, band 8.5 to 11.0.** This is the review-date stays index (E), the first team-built alternative series that beats a naive forecast of nights out of sample, corroborated in direction by hotel RevPAR, NTTO inbound arrivals and the calendar flow (F, G). It does not support an acceleration from 2Q26's +10.3%, and it does not resolve the guide question: "low double digits" needs 10.0 or more, and the index's central reading sits at or just under it. The team baseline of +9.9% (bridge and PR #32) is unchanged by this run; the new evidence narrows nothing below about a 2.5-point band, which is the honest resolution of stay-date alternative data on a booking-date KPI.

**3Q26 ADR: about +3.2% y/y, $176.8, central band +1.6 to +4.6 (H).** Ex-FX about +3.5%, FX between -1.1 and +0.3 pp depending on estimator. No free source measures realised ADR; this is a structural build, and the component build fails the walk-forward test (RMSE 1.29 pp vs naive 0.82), so the naive "same as 1H26" route (+4.0 ex-FX) is carried alongside it. Management said "a moderate increase in ADR due to mix shift and price appreciation."

**Implied 3Q26 GBV about $25.9bn and revenue about $4.80bn** at 146.8mm nights, $176.8 ADR and the WS-B FX schedule; the guide is $4.69 to 4.77bn. The beat is not the trade (19 of 19); the acceleration sign and the Q4 guide are.

## 2. What each workstream found

| WS | Data | Beats naive? | 3Q26 read | Status |
|---|---|---|---|---|
| E reviews stays index | 123 markets, 363 reviews dumps incl. 2025 vintages refreshed today, review dates 2018 to 17 Aug 2026 | **Yes, coincident level**: WF RMSE 1.48 pp vs naive 2.16 (ratio 0.68; family 0.65 to 0.75 across 2,560 cells; jackknife 0.63 to 0.86). Lag-1 marginal (0.87 to 0.91). First differences never. Eurostat monthly check 0.59 | Vintage-matched stays: July +3.8%, Aug-to-date +8.2%, 3Q26-to-date +5.2% vs 2Q26 +4.3%. Mapped through the fitted slope: **+9.5% nights, band 8.5 to 11.0** (headline row +10.0, 8.6 to 11.5) | Survivorship measured: 15 to 16% of a month's reviews vanish per year of dump age; within-vintage y/y runs ~20 pp high but the wedge is stable (20.7 vs 20.4 pp), which is why the backtest works. 111 markets, 88% of the base, have both July and August. Same-listing volume is -3 to -7%; all growth is from listings under a year old. NYC, LA, SF, Tokyo absent from the August row |
| F calendar booking pace | 34 markets; 164 new 2024-25 vintages downloaded today (now 328 files); Theo's Jun 2026 curve reproduced exactly | **No**: the flow y/y correlates -0.43 with disclosed nights and -0.53 with its acceleration on n = 5 with rising coverage; sign inverted, reported as a failure | Net blocking Jul to late Aug 2026 ran +0.18 pp per 30 days faster than 2025 across 11 markets (no NA market qualifies; Inside Airbnb never dumped NA in Jun 2025). Gross new blocks +4.0% y/y. Blocked-share levels are down y/y everywhere but contaminated by new supply | Direction-only cross-check. No Sep 2026 dump exists yet (374 probes, all 403); re-run F0b when they land mid-to-late Sep |
| G external sources | 40 sources ranked, 96 commentary rows from 27 companies, 288 backtests | Hotel RevPAR family now beats naive on nights (0.665x, n 10) with 2026 added; **NTTO I-94 inbound arrivals is a new survivor** (0.72 to 0.74x, knowable before print); TSA still fails | STR weekly US RevPAR: July +8.2%, mid-August fading +7% to +4%, ADR +5.7% to +0.6%, Labor Day noise after. NTTO overseas July -7.0% vs 2Q26 -14.1% (shrinking drag). Stack of 12 knowable survivors: **+9.2% median, 6.8 to 12.0** (in-sample, not independent) | Airbnb gave no quarter-to-date number at any venue 1 Aug to 11 Sep. Marriott 9 Sep: July RevPAR +7%, US and Canada +8%, +5% ex World Cup. Expedia: July consistent with Q2. No source, free or paid, delivers September before 2 Oct |
| H ADR card | Decomposition components on main + WS-B FX + WS-C mix | Component build **fails** WF (1.29 vs 0.82 naive, biased 1.5 pp low into accelerations); kept for attribution | 3Q26 +3.2% ($176.8, 174.0 to 179.1); 4Q26 +3.9% ($174.1, 171.1 to 177.8). 1 pp of ADR = $1.71, $259mm GBV, $46mm revenue | Largest uncertainties: like-for-like pricing residual (31% of band variance in 3Q26), fee-migration reprice in 4Q26 (35%), FX estimator choice (26%). The pricing residual stepped from 2 to 3.5 pp in 2023-25 to 4.4 and 4.9 pp in 1H26; that carried 1H26, not mix or size |

## 3. Reading the evidence together

1. **Every independent read lands at or slightly below the 2Q26 rate.** Reviews +9.5 to 10.0, external stack +9.2, hotel RevPAR fading through August, calendar flow flat-to-slightly-up. Nothing points to the +10.5% or more that the pre-registered card calls the surprise. The deceleration base case from the reconciliation note stands and now has alternative-data support rather than only a seasonal pattern.
2. **Regional texture is consistent across sources:** LatAm very strong (reviews +20 to +44% vintage-matched, though from a 7-market panel), NAM mid-to-high single digits and improving into August, EMEA weakest (+0.3 to +1.1% stays; Rome the only negative calendar market), APAC mid-single to high-single. That matches WS10's cells and WS-C's split, and it says the EMEA summer was soft on a stay basis.
3. **The stay-date to booking-date gap is the residual risk.** Reviews and RevPAR measure stays in July and August; the KPI counts bookings made in July to September, including bookings for 4Q26 and 1Q27 stays. The E slope (0.32 nights-points per stays-point, r 0.86) absorbs that mapping historically; a late-quarter booking shift, which is where RNPL and hurricanes act, is outside what any stay-date series can see.
4. **ADR is the softer line.** Hotel ADR growth collapsed to +0.6% by mid-August, CPI lodging fell from +4.9 to +3.1%, and the component build says the 1H26 pricing residual has to persist for +3.5% ex-FX. If ADR ex-FX prints closer to +2%, revenue still clears the guide on FX, but the Q4 revenue guide arithmetic gets tighter.

## 4. Data added to the main-tree store today (gitignored, manifests committed)

- 240 reviews dumps (Aug-Sep 2025 vintages and Aug 2026 refresh) under `data/raw/inside_airbnb_reviews/` (E `download_manifest.csv`). G reports Inside Airbnb is shipping an unlisted Aug 2026 batch for 86 markets; the disk holds about 49; LA, SF, Chicago, London, Paris, Barcelona, Sydney are missing from that batch and should be pulled.
- 164 calendar vintages from 2024-25 under `data/raw/inside_airbnb_calendar/` (F `F0b_new_vintages_manifest.csv`, sha256 recorded). Austin, Nashville, Paris and Rome now go back to spring 2024 monthly.
- Cached TSA, BLS, INE, Eurostat, NTTO series under `data/processed/q3nowcast/G/raw/`.

## 5. Decisions and next steps for Krish

1. **Use the reviews index as the pitch's alternative-data exhibit.** It is the one series that beats naive out of sample, it is reproducible from public data, and it says "no acceleration" for 3Q26. Show the survivorship wedge and the coverage table so the judges see the correction.
2. **Keep 3Q26 nights at +9.9% with the 8.5 to 11.0 band; do not move it on this run.** The three reads (bridge 9.9, reviews 9.5 to 10.0, external stack 9.2) agree within their bands.
3. **Adopt one ADR-FX estimator** (EUR fit has the better backtest, 0.458 vs 0.535 pp; the basket build is unfitted and says +1.7 pp more for 4Q26). Naming it changes the Q4 ADR line by more than anything else measured.
4. **Re-run E and F when the September Inside Airbnb dumps land (mid-to-late Sep)**, which closes the 3Q26 stay window before the 2 Oct pitch. Pull the missing Aug 2026 batch now.
5. **Retire the calendar-flow metric as a nights input** (sign-inverted backtest); keep the pace tables as a supply-adjusted descriptive only.
6. **Fix two repo priors:** YipitData has no travel footprint; Bloomberg Second Measure is not in a standard terminal seat, so the Hough Hall access-map assumption needs one email.
7. **The 5 Nov score sheet** should add: reviews-index 3Q26 read vs printed nights (was the slope right), ADR ex-FX vs +3.5%, and whether management restates the product-bundle contribution figure.
