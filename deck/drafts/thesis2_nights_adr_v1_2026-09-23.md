# Thesis 2 (nights and ADR): memo text and sources, 23 Sep 2026

Krish with Claude (Opus 5.5). Replaces the team draft's "Thesis Point 2 Nights". Pairs with Thesis 1
(`thesis1_rnpl_v1_2026-09-23.md`), which carries the RNPL lap and cancellations, so this one does not repeat them.

## Memo text (~220 words; ADR from PR #67, adr_engine_v3)

**Both legs sit below the Street, and nights does most of the work.** Bloomberg's 28 estimates put 3Q26 nights at +11.5%
(148.9m): management's "low double digits" carried forward, and an acceleration for only the fourth time in 16 prints. Every
route we built that passes its backtest lands at 144.6–146.8m (+8.2% to +9.9%), below the lowest estimate. The centrepiece is
a stays index from 71 million Inside Airbnb guest reviews across 123 markets, corrected for the 15–16% of reviews that vanish each
year. It reads +9.2% to +9.5% and beats a naive forecast out of sample (0.68x the error). Twelve external series read +9.2%,
led by STR weekly hotel RevPAR (+8.2% in July, +4% by mid-August). The World Cup does not close the gap: host-city match nights priced
+9% and stays ran 7.9pts above controls, but that is ~0.1pt of global nights. For 4Q26 we have +8.1%, and even the top of our
range (132.9m) is below the Street's 134.0m (+9.9%). On price, the Street's 3Q26 ADR ($177.06) is exactly what a straight
currency translation gives ($177.07); our FX estimate with the better point-in-time record makes FX a −0.4pp drag, not
+0.4pp: $175.66. ADR then slows to +1.0% ex-FX by 1Q27: the bundle's ~1pt ADR lift laps, pricing reverts to its 2023–26
average, and North America's slowdown tilts mix to cheaper regions (−1.6pp).

(Final, 222 words. The new-listings sentence was cut to make room for the ADR trajectory; keep it for Q&A: new listings
added 18.9pts of stays growth in 1Q23 but 11.4pts in 2Q26.)

### ADR trajectory, term by term (PR #67 head 8e13628b, `exfx_forward_base.csv`, `exfx_history.csv`; pp of ADR y/y)

| | 2Q26 (printed) | 3Q26 | 4Q26 | 1Q27 | 2Q27 | evidence |
|---|---:|---:|---:|---:|---:|---|
| core (like-for-like price) | 3.85 | 3.80 | 3.80 | 2.46 | 2.46 | unobserved; carried in 2026, expanding mean in 2027 (fix m) |
| bundle (RNPL + fee + cancellation) | 1.00 | 0.49 | 0 | 0 | 0 | management's GBV pts − nights pts (4 − 3 in 1Q26), lapped on filed dates |
| geographic mix | −1.27 | −1.29 | −1.34 | −1.62 | −1.08 | computed from the nights line's NA vs ex-NA growth |
| unit size (bigger homes) | 0.70 | 0.80 | 0.80 | 0.80 | 0.80 | measured (alt data) |
| length of stay | 0.30 | 0.05 | 0.05 | 0.28 | 0.28 | 3Q26/4Q26 measured on 34-market calendars (fix k); 2027 carried |
| seats / new business | −0.48 | −0.48 | −0.48 | −0.56 | −0.56 | assumed |
| construction basis + interaction + World Cup | −0.10 | −0.45 | −0.45 | −0.40 | −0.45 | fix (c) basis −0.30; World Cup −0.05 (fix l, PR #68) |
| **ex-FX y/y** | **4.00** | **2.96** | **2.43** | **0.95** | **1.44** | |
| FX (pp) | 1.3 | −0.41 | −0.37 | −0.37 | −0.43 | midpoint leg 2026 (fix j); identity at held spot 2027 |

Bridge 2Q26 → 1Q27 (−3.05pp ex-FX): core reversion −1.39 (an assumed rule, the biggest piece), bundle lap −1.00, geographic
mix −0.35, construction basis −0.30, everything else ≈ 0. Bridge 2Q26 → 3Q26 (−1.04pp): bundle −0.51, LOS −0.25, basis −0.30,
core and World Cup −0.10, geo −0.03, unit size +0.10.

**Does the Street mismodel FX, LOS and geographic mix?** FX: the numbers support it. The Street's 3Q26 ADR equals our build
under the identity FX leg to the cent ($177.07 vs $177.06), and the midpoint leg has the better point-in-time record (RMSE 0.20–0.25x
naive vs 0.30–0.38x in all four promotion cells). LOS and geographic mix: real drivers of our path, but the record cannot show
the Street has them wrong. Under the identity FX leg, the Street's implied 3Q26 ex-FX (+2.95%) equals ours (+2.96%), so the
whole 3Q26 gap is FX. In 4Q26 the Street is *more* bearish on ex-FX than we are. Geographic mix bites in 1Q27, a quarter for
which no Street ADR exists. Say "we measure", not "the Street misses", for LOS and mix.

**To reach ~180 words:** drop the new-listings sentence (−19), then "(0.68x the error)" (−4), then shorten the FX
parenthetical to "(Airbnb converts at spot)" (−12).

ADR source (PR #67, branch `krish/adr-audit-fixes`, `data/processed/pitch_model_v2/adr_engine_v3/adr_path.csv`):
3Q26 $175.66, reported +2.55%, ex-FX +2.96%, FX −0.41pp (midpoint leg, fix j), P(print ≥ Street) 0.21; 4Q26 $170.96,
+2.06%, P 0.45, against the Street's $171.33 (+2.28%). Geographic mix −1.29pp (3Q26), `exfx_forward_base.csv`. FX at spot:
`docs/cc-search-price/I6b_cross_domain_fx_full.md` (same listing, one USD and one non-USD domain, same crawl; conversion
margin inside ±25bp, no rate lag). 4Q26 ADR is $0.37 below the Street, so the text does not claim a 4Q26 price miss.

## Where each number comes from

| Claim | Number | Source |
|---|---|---|
| Street 3Q26 nights | 148.9m, +11.5%; 28 estimates, low 147.0m | Bloomberg MODL, 12 Sep 2026 (memo v3; `final_nights.md` rounds to 149.0) |
| Street = the guide carried forward; acceleration for the 4th time in 16 prints | | memo v3 §"How we know the view is variant"; guide "low double-digit" (2Q26 letter, ledger D052) |
| Every tested route | 144.6–146.8m | `docs/pitch-model-v2/lines/final_nights.md` §3.13: mechanism 146.8 (the base, DEC-0029), W2-corrected reviews index 146.3, RNPL cohort module 146.3, H1–H2 bridge 146.3, stays-only 145.8–146.0, external stack 145.9, joint fit 144.6–145.5 |
| Reviews stays index | 71m unique reviews dated Jan 2018–Sep 2026 in each market's latest dump (75m from 2015; 211m review rows read across all 365 dumps, the repeat vintages being what measures survivorship), 123 markets, computed from `data/processed/q3nowcast/E_aug/market_vintage_monthly.csv`; 15–16% of reviews vanish per year of dump age; walk-forward RMSE 0.68x naive; 3Q26 +9.2% (stays-only, vintage-matched) to +9.5% (W2-corrected) | `docs/q3nowcast/SYNTHESIS.md`; `final_nights.md` §3.1–3.13 |
| External stack | 12 survivors from 40 ranked sources, +9.2% (band 6.8–12.0); STR RevPAR +8.2% July → +4% mid-Aug; NTTO I-94 0.72x naive; EUROCONTROL daily flights (EMEA) | `research/notes/q3nowcast/G_external-sources-q3-read.md` |
| New-listing contribution | +18.9pp (1Q23) → +11.4pp (2Q26); same-listing stays −7.1% in 2Q26 | N1 dossier via `final_nights.md` §3.13. Only the *movement* is informative; the level is listing-ageing arithmetic |
| World Cup | quotes on stays wholly in the tournament +11.1% (LA + Mexico City, 362k quotes); match nights +8.9% across 17 host markets; host-city stays +7.9pp vs controls (19 v 19); ≈0.1pt of global 2Q26 nights; 0.05–0.30pp of 2Q26 ADR | `docs/worldcup-premium/RESULTS.md` on `krish/worldcup-premium` (worktree `../citadel-abnb-worldcup`, **uncommitted**) |
| 4Q26 | base 131.8m +8.12%; envelope high 132.94m; Street 134.0m +9.93% | `final_nights.md` §1 and §2a |
| ADR builds | $177.68 (engine v2, main), $176.90 (card v3.1, `krish/cc-search-price`), $175.66 (engine v3, PR #67, open); Street $177.06 (MODL, n 26) | `final_adr.md` §5; `docs/adr-card-v3_1/CARD_V3_1.md`; `adr_v3_corrections.md` on PR #67 |
| ADR terms | geographic mix −1.293pp, unit size +0.797pp (3Q26) | `final_adr.md` §3.2 |

## What changed from the team draft, and why

1. **146.3m / +9.5% → 146.8m / +9.9%.** The official base moved to the mechanism on 18 Sep (DEC-0029). 146.3m is now one of
   the cross-checks. The memo should use one number across all sections.
2. **"This data comes from a consumer relative strength index… and 1,159 vintage-stamped consensus rows"** is wrong. The
   consumer index is background, not an input, and the consensus rows are what make the backtests point-in-time. Neither is
   a source of the nights number. Dropped.
3. **Calendar booking pace** failed its backtest (sign inverted, n 5). Dropped rather than quoted as a direction check.
4. **The revenue decomposition and "backing out the World Cup and FX leaves 6–7%"** are replaced. Our own measurement puts
   the World Cup at ~0.1pt of nights and ≤0.3pp of ADR, so the World Cup cannot be what takes growth to 6–7%. The bundle
   does that (Thesis 1: ~7% underlying). Saying otherwise invites a judge to ask for the World Cup number.
5. **ADR added.** It is on consensus across all three builds, so the thesis says so and puts the gap on volume. The price
   argument (FX turning, the unobserved like-for-like core) is a 4Q26–2027 risk, not a 3Q26 variance.

## Open before 2 Oct

- **ADR line: PR #67 chosen (23 Sep).** It is still open, so merge it before the memo quotes $175.66. The workbook and the
  margin build still read engine v2 / card v3.1, so the revenue and margin sections need the same ADR.
- **The World Cup result is uncommitted** on `krish/worldcup-premium`. Commit it before the memo cites it.
- **The nights line still books +0.5pt of World Cup in 2Q26 and a −0.5pt lap in 2Q27.** The measurement says ~0.1pt. That
  is a correction to the nights line, and it cuts slightly against the short in 2Q27.
- Re-pull MODL before submission ("below the lowest estimate" depends on the 147.0m low).
