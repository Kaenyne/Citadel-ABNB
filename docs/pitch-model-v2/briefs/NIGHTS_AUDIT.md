# Brief — adversarial audit of the nights line (line 1 of pitch model v2)

You are auditing one line of the ABNB pitch model: **Nights and Seats Booked**, and the engine built to forecast it
from public review data. This work will be judged by a hedge-fund travel-and-lodging analyst at the Citadel
Intercollegiate Stock Pitch Competition. The preliminary memo is due **2 October 2026**; finals are 22–24 October; the
3Q26 print lands 5 November, after finals.

**Your job is to break it, or to certify that you could not.** Confirming it is a valid and useful outcome, but only
after a genuine attempt to falsify it. Do not be agreeable. The authors would rather be corrected now than in front of
a judge. This line has already survived one external review (`NIGHTS_ENGINE_REVIEW_RESPONSE.md`) in which several
concerns were **conceded**; your job is to find what that review missed, not to repeat it.

Workspace: `~/Citadel-ABNB`. The engine is on `main`. Run every command from the repo root with `python3`.

---

## 1. Read first, in this order

1. `CLAUDE.md` — the repo rules. They bind you.
2. `docs/revenue-forecast-strategy/05_backtests/NIGHTS_PROCESS_COMPLETE.md` — **the governing document.** The whole
   process and, in Part 6, the authors' own statistical review register **R1–R22**. Start there; do not simply re-derive it.
3. `docs/revenue-forecast-strategy/05_backtests/REVIEWS_INDEX_v2.md` — §1 is the **frozen pre-registration**
   (`prereg.json`, sha256 `a531e9b0…`, frozen 18 Sep 15:57 before any stage ran); §2–5 are the results.
4. `docs/revenue-forecast-strategy/05_backtests/NIGHTS_ENGINE_REVIEW_RESPONSE.md` — the external review, answered A–I.
5. `REVIEWS_INDEX_v2_RATIONALE.md` (every number and every rejected alternative with its own number) and
   `NIGHTS_ENGINE.md` (how to run it).
6. `docs/pitch-model-v2/lines/final_nights.md` — the line as the pitch states it, and the mechanism base (DEC-0029).
7. `docs/pitch-model-v2/DECISIONS.md`, entries **DEC-0004, DEC-0016, DEC-0019, DEC-0020, DEC-0024 through DEC-0029, DEC-0033**.

Where a later note contradicts an earlier one, the later governs — but **say which superseded which**. Several documents
carry dated correction blocks at the top; a stale number surviving elsewhere is itself a finding.

## 2. Reproduce before you argue

```bash
cd ~/Citadel-ABNB/analysis/src/forecast_methods/reviews_index_v2
python3 -m pytest tests -q                 # 9 tests; the first pins the scorer to E5's 0.683209 on the v1 cell
python3 run.py --stage all                 # ~20 s; verdicts must print A True, B True, C False
python3 workbook.py                        # rebuilds model/ABNB_official_model.xlsx from the outputs
```

Outputs land in `data/processed/forecast_methods/reviews_index_v2/` (`audit/` holds diagnostics added in response to the
external review). **If a number in a document does not appear in an output file, that is a finding.** Report exit codes.

## 3. The claims, ranked by how much weight they carry

Attack in this order. The first three decide whether the line survives.

**C1 — The backtest is not point-in-time, and the authors know it.** Every historical predictor value is reconstructed
from the August 2025 and August 2026 file vintages; regional weights use the *same quarter's* 10-Q revenue, published
about five weeks after the forecast cutoff. `audit/availability_table.csv` classifies all 14 scored quarters as
**retrospective reconstruction**. The defence is that the expanding window still prevents outcome leakage into the
coefficients, that the lagged (real-time) weight policy reproduces the same 0.723 / 0.723, and that no claim of
real-time skill is made. **Test that defence.** Is there leakage the authors have not found — in the trim rule, in
`select_vintages`, in the partial-to-full gap, in the choice of `k`? Does any document still imply real-time skill?
Quantify: how much of the 0.723 survives a construction that uses only information available at each cutoff?

**C2 — The mapping is two parameters on ten quarters, and the intercept does most of the work.**
`nights y/y = 6.825 + 0.350 × index`, frozen on 1Q23–2Q25. For the 3Q26 read of 8.92, the intercept supplies **6.83 of
8.92 (77%)** and the index contributes 2.10. A one-point move in the index moves the answer 0.35pp. The authors argue
the intercept is not the forecast — an intercept-only walk-forward scores **1.4–3.9× naive** (see the audit in the
review response, §F) so the slope is doing real work. **Test that.** Is the 0.35 slope stable, or an artefact of the
2023 quarters? Leave-one-quarter-out gives 0.258–0.350 and **0.258 without 1Q23**. What does the read become under each?
Is there an economic account of a 6.8pp intercept that survives a judge asking "what is that number?"

**C3 — The W1 pass depends on two quarters.** W1 is 0.723 over 14 scored quarters but **0.838 scored from 3Q23**
(dropping 1Q23–2Q23), which fails the 0.75 line. W2 (0.723, n 10) shares **10 of its quarters with W1** — the two
windows are nested, not independent. The largest naive miss in the sample is 2Q23 (−7.62pp), the post-COVID
deceleration. **Decide whether "clears on both windows" is a defensible sentence**, and if not, write the sentence that is.

**C4 — Stage C is a bound presented in a document that once called it a test.** The post-launch residual is
+0.86 / +0.34 / −0.80 / +1.55, mean **+0.486** against a band of **±1.850**; the pre-registered line (mean > 1 band and
≥ 3 of 4 > ½ band) was not met. `audit/f_h_checks.json` gives its power: **6% / 16% / 32% / 53%** against true effects of
0.5 / 1.0 / 1.5 / 2.0pp. Confirm the failure is reported with its pre-written reading everywhere and that no document
converts a bound into evidence. **Then extend:** is there a sharper test of the same hypothesis on this data — pooling,
a one-sided test with the sign pre-committed, a longer pre-window?

**C5 — The residual is not identified as RNPL, and management has disclosed a rival explanation.** A positive residual
is produced by anything that lengthens the gap between booking and stay. Airbnb's own 1Q26 call (ledger D033, mirror
transcript) says RNPL is *"driving longer booking lead times"* — a lead-time extension raises printed nights above
review-implied nights **with no cancellation at all**. Length-of-stay drift, review-propensity drift and sample-to-platform
composition do the same. **Quantify the lead-time channel** from `kernel_leadtime_v2` (refit the kernel by year if the
data allow) and tell us how much of the +0.486 it can absorb. This is the single most valuable finding you can return:
if lead time explains the residual, the RNPL reading of it is dead and the line's evidence rests on the balance sheet alone.

**C6 — The balance-sheet result is the only significant RNPL evidence, and it may prove the wrong thing.** Unearned fees
minus GBV y/y: **+2.696 ± 2.947pp** over ten pre-RNPL quarters, then **−4.09 / −8.05 / −18.81 / −16.65**; Welch
t −4.04, **p 0.021** (ex-FX p 0.028); the block-position permutation reaches only **p 0.091** (its floor, 1/11).
This establishes **payment deferral and RNPL exposure**. It does **not** establish that conversion has deteriorated —
every RNPL booking could still complete. Check: is the Welch test appropriate on n 4 vs 10 with possible seasonality
(the pre-period lag-1 autocorrelation is −0.14)? Does a quarter-fixed-effects version survive? Does extending the
pre-window to 2019–22 change it? **And check the accounting claim itself** against the FY25 10-K Note 2 — the authors
quote it second-hand from `final_nights.md` §6.1 and did not re-extract it.

**C7 — The geographic weights are estimated proxies with a look-ahead, and five markets carry LatAm.**
`w = regional revenue ÷ ADR index`, renormalised. Revenue ÷ ADR is nights × **take rate**, not nights. The ADR index
(1.42 / 0.97 / 0.68 / 0.59) is a 2026 calibration. LatAm is **5 markets** and contributes 4.93 of the 3Q26 composite's
5.90 points; EMEA is 51.5% of the Q3 weight while our EMEA sample reads +0.86%. `audit/weights_sensitivity.csv` shows
four schemes (0.682–0.770 on W1). **Test the take-rate objection numerically** and run a jackknife of the index by
region and by market. If the answer moves more than the band, that is a finding.

## 4. Issues the authors already flagged — verify and extend

- **The lagged-weight policy should be primary and is not.** The real-time policy gives the same 0.723 / 0.723 and a
  3Q26 read of **8.85** against the filed **8.92**. Flagged in Part 5, not yet promoted. **Decide whether it should be,
  and say so.**
- **`final_model_landing.csv` is marked NOT FOR QUOTATION** (this PR): it feeds the *net* observed gaps into the kernel
  as if they were *gross* cohorts, double counting cancellations already landed. The timing logic is sound. **Rebuild it
  on gross cohorts** — disclosed x = 16–17% times the RNPL booking flow implied by the ">20% of GBV" disclosure — or
  confirm it should be deleted.
- **1Q27's option term is +0.80pp — a tailwind**, because it laps 1Q26's negative residual. Any narrative calling 1Q27
  "flat" or "neutral" is stale. Check every document and the workbook for survivors of the old wording.
- **The band is an error scale, not an interval.** 1.850 is the RMSE of six expanding-refit errors; its own bootstrap
  90% range is **[1.11, 2.46]**; parameter uncertainty and the partial-quarter term are excluded. Confirm no document
  treats ±1.85 as a prediction interval, and **propose the interval that should be used** for the 3Q26 read.

## 5. Specific numbers to verify

Recompute, do not accept:

| object | claimed |
|---|---|
| review corpus, latest vintage | 75.1 M reviews, 123 markets (49.1 M since 2023); 697,888 daily count rows |
| vintage-matched markets | 119 of 123; 16,963 market-months |
| Paris June, same-age vs single-file | −11.7% vs +11.7%; 21% of June-2025 listings gone from the later file |
| 2Q26 regional stays y/y | NAM +6.90 · EMEA +1.48 · LatAm +20.40 · APAC +2.30 |
| 2Q26 index | 5.62% |
| frozen mapping | a 6.825, b 0.350, n 10 (1Q23–2Q25) |
| walk-forward vs naive | W1 0.723 (n 14), W2 0.723 (n 10); pre-RNPL W2 0.700 (n 6) |
| bootstrap 90% | [0.614, 1.081] W1; [0.577, 0.966] W2 |
| Diebold–Mariano | −1.293 (p 0.218) W1; −1.199 (p 0.261) W2 |
| vs prior-year / AR(1) | 0.169 / 0.521 (W1); 0.425 / 0.741 (W2) |
| acceleration target | W1 **1.560** (fails), W2 0.680 |
| other constructions | `yoy_vmatch` 0.682/0.720 · `yoy_all` 0.749/0.684 · `yoy_all_mix` 0.823/0.749 · `yoy_mature` 0.972/0.908 |
| post-launch gaps | +0.858 / +0.337 / −0.802 / +1.552; mean +0.486; band 1.850 |
| 3Q26 partial composite → read | 5.899 + 0.087 = 5.987 → **8.918%** → 145.5m [143.0, 148.0] |
| 3Q26 regional partials | NAM 6.85 · EMEA 0.86 · LatAm 27.53 · APAC 7.35; weights .265 / .515 / .100 / .120 |
| Eurostat panel | β 0.4936 (se 0.0696, t 7.09, wild-cluster p 0.001, n 702, 18 clusters); **with month FE 0.3127** (t 4.52) |
| first differences | β 0.7034 (se 0.1030, p 0.001, n 684) |
| per-country out of sample | median 0.590; 17 of 18 ≤ 0.75 (CZ 0.42 … MT 0.76) |
| DiD power | US pre-trend −3.950pp; MDE 7.174 (permutation) / 3.978 (placebo dates) vs a sought ≤ 3pp |
| P(3Q26 print ≥ Street 149.0) | 0.079 on the stays read |

Traps that exist in this lane:

- **Vintage age is not uniform.** Dumps span 2026-06 to 2026-08 across markets; "same age" holds per market, not
  globally. Check whether markets whose pair ages differ by more than ~30 days move the index.
- **The partial-to-full gap (+0.087) was estimated on the single-file construction** (`gap_source` in
  `q3_2026_nowcast.csv` says `assumed_from_yoy_all`) and applied to the vintage-matched one.
- **`index_quarterly_v2.csv` carries every construction**, `_mix` and non-`_mix`. `config.PRIMARY` decides which is
  quoted; a positional read of the wrong column silently changes the answer.
- **Quarters require all three months present**; a market missing one month drops out of that quarter entirely, so the
  sample composition moves between quarters.

## 6. Hard rules

1. **Do not scrape.** The review files are Inside Airbnb's published dumps; the download manifest with URLs and sha256
   is `data/processed/q3nowcast/E/download_manifest.csv`. Airbnb's robots.txt disallows `/rooms/*/reviews`. Anything
   touching `airbnb.com` is a terms-of-service decision for a human — **stop and ask**. Public SEC filings and press
   releases are fine; at most five web fetches, each logged.
2. **Never type credentials.** SSO button clicks are fine; passwords and two-factor codes are not.
3. **Do not commit, and do not push.** Write your audit to
   `docs/pitch-model-v2/dossiers/NIGHTS_AUDIT_<yourname>.md` and nothing else. Receipts may go under
   `data/processed/pitch_model_v2/receipts/NIGHTS_AUDIT/`.
4. **Do not change the frozen pre-registration** (`prereg.json`) or any file under
   `data/processed/forecast_methods/reviews_index_v2/` other than your own receipts folder. If a pass line looks wrong,
   that is a finding, not an edit.
5. **DEC-0016 binds you too.** Do not propose an input chosen to reach a price or a target. If you find a construction
   that moves the read, it must be the mechanical consequence of a stated assumption, and you must state the assumption first.
6. **Keep the three layers apart** — *measured* (the engine's outputs), *disclosed* (Airbnb's filings and calls), and
   *assumed* (the team's sizing of the RNPL conversion effect, the 1Q27 adoption ceiling, the exercise schedule). Part 4
   of the governing document defines them. Collapsing them is the error the authors most want caught.
7. **You do not decide.** List choices for the humans with options and a recommendation.
8. Do not modify anything under `analysis/src/pitch_model_v2/adr_engine/`, `data/processed/pitch_model_v2/adr_engine/`
   or `docs/pitch-model-v2/lines/adr*` — a separate audit owns the ADR line.

## 7. What to return

A dossier with, in this order:

1. **Verdict in one sentence.** Does the nights line survive a hostile read, yes or no — stated separately for
   **(a) the predictive engine** and **(b) the RNPL interpretation**. A useful predictor can survive a rejected RNPL story.
2. **Reproduction**: what you ran, exit codes, which claimed numbers reproduced and which did not, with both values
   side by side for every mismatch.
3. **Findings, ranked by how much they move the 3Q26 read (in millions of nights) or the credibility of the backtest.**
   For each: the claim, the evidence against it, the size of the error, and whether it helps or hurts the short. A
   finding that helps the short is not more valuable than one that hurts it — report both the same way.
4. **The C5 question answered explicitly**: how much of the +0.486pp residual can lead-time extension absorb?
5. **The C1 question answered explicitly**: what is the strongest defensible statement about forecast skill, given that
   no evaluation period is untouched and the predictor is retrospective?
6. **Anything the documents assert that the output files do not support.**
7. **Open choices for the humans**, numbered, each with options and your recommendation — including whether the lagged
   weight policy becomes primary and what interval should replace ±1.85.

Be specific. "The sample is small" is not a finding; "dropping the four markets whose vintage pair ages differ by more
than 60 days moves the 3Q26 index by X points and the read by Y, which is Z% of the band" is. Quote file paths and line
numbers. If you cannot break something, say that clearly — a clean bill of health from a real attempt is worth more
than a list of quibbles.
