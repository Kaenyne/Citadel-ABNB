# WS23 — Fixing the options event-implied-move estimator (audit finding A08)

- **Date:** 2026-09-06. **Author:** Krishang Surapaneni (compiled with Claude Code), overnight workstream 23.
- **Closes:** A08 in `docs/2026-09-06_audit_findings_ai_handoff.md` §10 (P2, "Options event-variance estimator and expiry selection are inadequate for the stated interpretation").
- **Code:** `analysis/src/abnb_options_ledger.py` (rewritten), `analysis/src/overnight/23_options_estimator_test.py` (acceptance tests), `analysis/src/overnight/23_update_ws09_options.py` (regenerates the WS09 artefacts).
- **Data:** `data/processed/abnb_options_ledger.csv` (schema v2), `data/processed/overnight/23_options_event_estimates.csv`, `data/processed/overnight/09_implied_move_live.json`, `data/processed/overnight/09_implied_vs_realised.csv`.
- **Live snapshot used:** yfinance chains pulled 2026-09-06 19:20 UTC; ABNB spot $181.94.

**Provenance of the copy.** `analysis/src/abnb_options_ledger.py` and `data/processed/abnb_options_ledger.csv` did not exist in the overnight worktree. Both were untracked files in the MAIN tree (`C:\Users\krish\citadel-abnb`, commit `e9c840d` era, written 5 Sep 2026). The MAIN copies were **not modified**. The script was rewritten at the same relative path in the overnight tree; the MAIN CSV's twelve 5 Sep rows are carried into the new overnight CSV as `schema_version = 1` legacy rows with the defective `event_implied_move_pct` column dropped and `qq_flags = legacy_schema_v1;event_estimate_withdrawn_A08` (see `merge_legacy()`).

---

## 1. Bottom line

The old estimator did not estimate what it claimed, and the headline that came out of it — *"the option market prices no 5 Nov event premium; implied event premium = 0.002 pts"* — is **withdrawn, not corrected**. It was never a measurement of the event premium.

The rewritten estimator is correctly identified and passes 25/25 synthetic acceptance checks. Run on the live chain today it produces three mutually irreconcilable answers (non-positive, 2.31%, 6.73% event standard deviation), so the honest output for the 6 Sep snapshot is **"event estimate not identified in practice; raw term structure only."** That is a better answer than a confident wrong one, and it becomes a real number when the 6 Nov weekly lists in late October.

---

## 2. The identification algebra

Write total variance to expiry *i* as a background (diffusive) part plus a discrete event:

```
sigma_i^2 * T_i  =  b * T_i  +  E * d_i          d_i = 1 if expiry i settles after the event
```

`b` is the annualised background variance rate; `E` is the variance of the event's log-return (so `sqrt(E)` is the event standard deviation, and `sqrt(E) * sqrt(2/pi)` is the expected absolute move under a normal jump).

**What the old code did.** `analysis/src/abnb_options_ledger.py:69–75` (MAIN copy) computed

```
var_event = sigma_near^2 * T_near  -  sigma_far^2 * T_near
```

then floored it at zero and reported `sqrt(max(var_event, 0)) * 0.8`. If **both** expiries contain the event — which they did, because near and far were the 20 Nov and 18 Dec monthlies and the print is 5 Nov — then `sigma_near^2 = b + E/T_near` and `sigma_far^2 = b + E/T_far`, so

```
var_event = (b + E/T_near) * T_near - (b + E/T_far) * T_near
          = E * (1 - T_near/T_far)
```

At the actual ABNB maturities (T_near = 75/365, T_far = 103/365) that recovers **27% of E**, and the extra ×0.8 pushes it to ~22%. So a genuine 7% event sigma would have printed as ~3.3%, and any error in the two IVs of more than about a vol point flips the sign and gets floored to a spurious exact zero — which is exactly what the 5 Sep ledger shows for ABNB (`event_implied_move_pct = 0.0`). Test **T7** in the acceptance suite reproduces this bias to machine precision on synthetic data with a known E.

**Two further defects on top of the algebra.**

- **Expiry selection.** The far expiry was chosen by proximity to a hard-coded target date, not by any relation to the print. For EXPE and HLT the "near" expiry (23 Oct) fell **before** the intended print, so the ledger's `event_implied_move_pct` for those two rows was neither the old estimand nor E.
- **"Straddle".** The nearest-strike call and the nearest-strike put were selected independently and summed. On a thin chain those are frequently different strikes, so the "straddle" was not a straddle and `straddle_pct_spot` was not an implied move.

**What identifies E.** With the model above, the design matrix over maturities is `[T_i, d_i]`. E is identified iff that matrix has rank 2, which needs either

- **one pre-event and one post-event maturity:** `b = sigma_pre^2`, then `E = T_post * (sigma_post^2 - b)`; or
- **two post-event maturities:** `b = (sigma_3^2 T_3 - sigma_2^2 T_2) / (T_3 - T_2)`, then `E = T_2 T_3 (sigma_2^2 - sigma_3^2) / (T_3 - T_2)`.

A single post-event maturity alone is **not** identified — b and E trade off exactly — and the old code's implicit claim otherwise is the root of A08. With more than two maturities the same system is solved by least squares, which is what the new code does, plus a leave-one-maturity-out spread to expose how fragile the fit is.

**Declared assumptions** (carried in every output row, column `assumptions`):

- **A1** a single background variance rate `b` applies across every maturity used;
- **A2** exactly one discrete event sits inside every post-event expiry and none inside the pre-event expiries (no other differentiating catalyst);
- **A3** each expiry's ATM IV proxies that expiry's total variance — no skew or variance-swap replication correction;
- **A4** the quotes across maturities are contemporaneous.

A1 is the assumption that fails today (§5). A2 is weak while the nearest post-event expiry is 15 days past the print. A3 is a known small bias. A4 is approximately satisfied by a single yfinance snapshot on a trading day, less so on stale strikes.

---

## 3. What changed, before and after

| | Before (5 Sep, MAIN) | After (6 Sep, overnight) |
|---|---|---|
| Event timestamp | implicit; a hard-coded target expiry date with a "verify when announced" comment | explicit `EventSpec` per ticker: earliest date, latest date, release time, **confidence tier**, and the source string |
| Expiry eligibility | nearest listed expiry to the target date | `post_event` iff settlement (16:00 ET on the expiry date) is **strictly after** the latest plausible release; `pre_event` iff strictly before the earliest; otherwise `ambiguous` and never used |
| No post-event expiry | silently produced a number | reports `unavailable_no_post_event_expiry`; raw measures only |
| Estimand | `sigma_near^2 T_near - sigma_far^2 T_near`, i.e. `E*(1 - T_near/T_far)` | `E` from the least-squares fit of `sigma_i^2 T_i = b T_i + E d_i` |
| Maturities | exactly 2, chosen by date proximity | every listed expiry inside 160 days that passes quote-quality and eligibility screens (10 for ABNB) |
| Negative estimate | floored to 0, reported as an implied move | returned as-is, `event_var_sign = non_positive`, with an explicit note that this is **not** evidence of no earnings premium |
| Fudge factor | `sqrt(var) * 0.8` "straddle-equivalent", undocumented | none; `sqrt(E)` is the event sigma and `sqrt(E)*sqrt(2/pi)` the expected absolute move, both labelled |
| Straddle | nearest-strike call + nearest-strike put, strikes not checked | shared-strike requirement enforced; `straddle_verified` boolean and `straddle_reject_reason` on every row |
| Quote record | `bid > 0 & ask > 0` filter, nothing stored | bid, ask, mid and strike stored per leg; straddle bid / mid / ask; relative spreads; open interest; volume; last-trade timestamps; quote age; `quote_quality` in {good, fair, poor, unusable} and a `qq_flags` string |
| Observation time | run date only | `run_datetime_utc` to the second, plus `expiry_settle_et` |
| Raw vs event | `straddle_pct_spot` sat next to `event_implied_move_pct` with no distinction | raw columns renamed `raw_atm_iv_pct`, `raw_straddle_mid_pct_spot`, `raw_straddle_bid/ask_pct_spot` and documented as **total** implied move to expiry; event estimates live in a separate file |
| Peers | 8 tickers, all treated as if the print date were known | 5 tickers with third-party-estimated dates; TRIP, H and JETS get `unknown` confidence and therefore raw measures only |
| Tests | none | 25 synthetic acceptance checks, `--dry-run`, non-zero exit on failure |

---

## 4. Acceptance tests

`py -3.13 analysis/src/overnight/23_options_estimator_test.py --dry-run` → **25/25 pass**, no network. Synthetic truth: background vol 30.00%, event sigma 7.00%.

| Test | What it demonstrates | Result |
|---|---|---|
| T1 | one pre-event + one post-event maturity recovers E and b exactly (and the sd and expected-abs-move conversions) | E = 0.0049000000 vs true 0.0049; b = 0.09 |
| T2 | two post-event maturities recover E and b exactly | E = 0.0049000000 |
| T3 | four maturities via least squares recover E; LOO spread is degenerate on clean data | residual RMSE 9.3e-18 |
| T4 | **expiries before the event fail eligibility**: a chain of only pre-event expiries returns `unavailable_no_post_event_expiry`, never a number | pass |
| T4b–e | with the real ABNB spec, 11 Sep / 16 Oct / 23 Oct classify `pre_event`; 20 Nov / 18 Dec / 15 Jan classify `post_event`; an expiry **on** the release date is `ambiguous`, not `post_event` | pass |
| T5 | one post-event maturity with no pre-event maturity is `unavailable_insufficient_maturities` | pass |
| T6 | `ambiguous` maturities are dropped from identification | pass |
| T7 | the **old** estimator returns `E*(1 - T_near/T_far)` on the same quotes: 0.00131923 vs true 0.0049, i.e. 26.9% of E — 3.63% reported sigma against a true 7.00% | pass |
| T8 | a negative fitted E is returned, not floored, and is labelled `non_positive_event_variance` with the explicit "NOT evidence" wording | pass |
| T9 | same-strike straddle construction; bid/ask/mid/strike/observation time all stored; disjoint call/put strikes are rejected (`straddle_verified = False`, `quote_quality = unusable`) and excluded from identification | pass |
| T10 | confidence gating: `unknown` and `pattern_estimate` yield `unavailable_no_event_timestamp`; every shipped `EventSpec` carries a confidence label and sources | pass |

The suite exits non-zero on any failure, so it can be wired into the WS15/A13 machine-detectable checks.

---

## 5. Live result, 6 September 2026

**Event specification.** ABNB Q3 2026, window **4–12 Nov 2026**, release after close, confidence **`third_party_estimate`** — Yahoo Finance's earnings calendar returns a single date of 5 Nov 2026, the repo-wide working assumption is 5 Nov, and the Q3 pattern is 6 Nov 2025 / 7 Nov 2024 / 1 Nov 2023. **Airbnb IR had not published the date as of 6 Sep 2026** (`16_news_since_5sep.csv`). The window matters less than it looks: every date in it sits strictly between the 23 Oct and 20 Nov expiries, so expiry eligibility is robust to the date uncertainty even though the date itself is not confirmed. The code checks this rather than assuming it.

**Listed expiries.** `2026-09-11, 09-18, 09-25, 10-02, 10-09, 10-16, 10-23, 11-20, 12-18, 2027-01-15, 03-19, …` — **the 6 Nov 2026 weekly is not listed**. The chain jumps from 23 Oct to 20 Nov, so the nearest post-event expiry is 15 calendar days past the print.

**Raw measures** (verified same-strike straddles; **total** implied move to expiry, not event moves):

| Expiry | Class | dte | Strike | ATM IV | Straddle mid % spot | Straddle bid–ask % spot | Quality |
|---|---|---|---|---|---|---|---|
| 11 Sep | pre | 5 | 182.5 | 32.22% | 2.97% | 2.63–3.31 | good |
| 18 Sep | pre | 12 | 182.5 | 31.12% | 4.27% | 3.85–4.70 | fair |
| 25 Sep | pre | 19 | 182.5 | 35.39% | 5.39% | 4.15–6.62 | poor |
| 2 Oct | pre | 26 | 182.5 | 34.39% | 6.32% | 5.17–7.48 | poor |
| 9 Oct | pre | 33 | 182.5 | 36.74% | 7.54% | 6.13–8.96 | poor |
| 16 Oct | pre | 40 | 180 | 32.72% | 8.20% | 7.67–8.74 | fair |
| 23 Oct | pre | 47 | 185 | 37.81% | 9.11% | 7.12–11.10 | poor |
| **20 Nov** | **post** | 75 | 180 | 38.15% | **13.38%** | 12.94–13.82 | fair |
| **18 Dec** | **post** | 103 | 180 | 38.68% | **15.65%** | 14.92–16.38 | fair |
| **15 Jan 27** | **post** | 131 | 180 | 38.22% | **17.01%** | 15.80–18.22 | fair |

**Fitted event estimates** (`23_options_event_estimates.csv`):

| Specification | Maturities | b (vol) | E | Event sigma | E abs move | LOO range |
|---|---|---|---|---|---|---|
| 23 Oct + 20 Nov | 1 pre, 1 post | 37.81% | 0.000534 | **2.31%** | 1.84% | — |
| All eligible | 7 pre, 3 post | 36.21% | 0.004524 | **6.73%** | 5.37% | 5.23–8.05% |
| 20 Nov + 18 Dec | 0 pre, 2 post | 40.08% | −0.003106 | **non-positive** | — | — |

**Why they disagree, quantified.** The seven pre-event weekly ATM IVs run 31.12, 32.22, 32.72, 34.39, 35.39, 36.74, 37.81 — a **6.68 vol-point spread with no scheduled event between them**. That dispersion is measurement noise (wide spreads, stale last trades, thin open interest: five of the seven are flagged `poor`), and it violates assumption A1 directly. Holding the 20 Nov quote fixed and sweeping the assumed background across exactly that observed range:

| Assumed background vol | E | Event sigma |
|---|---|---|
| 31.12% | 0.01001 | 10.01% |
| 32.72% | 0.00791 | 8.89% |
| 34.39% | 0.00561 | 7.49% |
| 35.39% | 0.00417 | 6.46% |
| 36.74% | 0.00217 | 4.66% |
| 37.81% | 0.00053 | 2.30% |
| ≥ 38.15% | ≤ 0 | non-positive |

**The event variance is entirely inside the noise in the background baseline.** A one-vol-point error in b moves the implied event sigma by roughly 1.5–2 points at this maturity, and the data supply nearly seven points of ambiguity.

**Peers.** None of BKNG, EXPE, MAR or HLT had a company-confirmed Q3 2026 date on 6 Sep, and the vendors disagree (BKNG: Yahoo 27 Oct vs TipRanks 4 Nov; MAR: Yahoo 3 Nov vs TipRanks 29 Oct). All four are run at `third_party_estimate` confidence with windows wide enough to cover the disagreement; all four windows still sit between the 23 Oct and 20 Nov expiries, so eligibility holds. Their fits show the same instability, and one of them shows the same sign flip the old estimator would have hidden:

| Ticker | Window | pre + first post | all eligible | two post |
|---|---|---|---|---|
| BKNG | 26 Oct – 5 Nov | 8.20% | 10.57% (LOO 8.90–12.42) | **non-positive** |
| EXPE | 2 – 12 Nov | 11.09% | 10.31% (LOO 9.59–10.52) | 13.00% |
| MAR | 27 Oct – 4 Nov | 3.99% | 3.81% (LOO 2.77–4.18) | 3.94% |
| HLT | 26 Oct – 4 Nov | 5.49% | 4.81% (LOO 4.08–5.12) | 6.83% |

MAR and HLT are reasonably stable across specifications (spread ≤ 2 points) and their chains are less noisy; EXPE is stable at ~10–13%. ABNB and BKNG are the two names where the estimate is not usable. Note also what the old code would have reported for EXPE and HLT: it selected the 23 Oct expiry as the "near, event-containing" leg, but 23 Oct settles **before** every plausible release date for both names, so those two ledger rows were meaningless. The new code classifies 23 Oct as `pre_event` for both and uses it as the baseline instead.

TRIP, H and JETS carry `confidence = unknown`; they get raw measures and an explicit `unavailable_no_event_timestamp`.

---

## 6. What can and cannot be claimed today

**Can be claimed.**

- The raw straddle prices are real, quoted, verified same-strike, two-sided mids with their bid–ask range recorded: **20 Nov 13.38% of spot** (K 180, bid–ask 12.94–13.82), **18 Dec 15.65%**, **15 Jan 17.01%**. These are total implied moves to expiry.
- The 6 Nov 2026 weekly is **not listed** as of 6 Sep 2026, so the market has not yet created the instrument that isolates the print.
- The estimator is now correctly identified and demonstrably recovers a known E on synthetic data.
- MAR (≈3.8–4.0%) and HLT (≈4.8–6.8%) have event estimates stable enough to quote with a range attached; EXPE ≈10–13%.

**Cannot be claimed.**

- **Any single ABNB event-implied move.** The specifications span non-positive to 6.73% and the sensitivity analysis spans non-positive to 10%.
- **"The market prices no event premium."** This was the old headline and it is withdrawn. A non-positive fit on two post-event expiries says nothing about the event; a non-positive fit on a pre/post pair says the pre-event baseline is noisy. Neither is a market view.
- **A cheap/rich verdict on the 20 Nov straddle versus the 7.1% base rate.** The 20 Nov straddle contains 75 days of background vol plus the print; you cannot net the print out of it today.
- Anything conditioned on a confirmed print date. No issuer in the set has published one.

---

## 7. Corrections to existing work

1. **`research/notes/overnight/09_stock-behaviour-and-alpha.md`** — bottom-line item 8, §7's live-term-structure paragraph, correction 10.4 and the options bullet in §11 were rewritten in place on 6 Sep 2026, each carrying a dated correction marker, plus a correction line in the header block. The withdrawn claims are the "implied event premium of zero / 0.002 pts" statements and "the correct answer at 76 dte does happen to be approximately zero".
2. **`analysis/src/overnight/15_claim_checks.py:99`** hard-codes the WS09 claim *"no implied event premium 60 days out (0.002 pts)"* with status `confirmed` and evidence `"straddle ledger 13.38 near / 15.65 far, event premium 0.0016 pts"`. That row is now **stale and should be marked withdrawn**. I did not edit it — 15_* files are outside this workstream's scope. The claim-check row should become: claim withdrawn (A08); the ledger comparison it cites used two post-event expiries and cannot detect an event premium.
3. **`analysis/src/overnight/09_stock_behaviour.py:507–553`** still contains the old inline `implied_vs_realised()` live block (the `jv_flat` / `jv_upper` "bracketing" estimators and the ledger √time cross-check). Its `jv_flat` is in fact the correct pre/post identity, but `jv_upper` is a bound on total incremental variance rather than on event variance, and the ledger cross-check is the defective one. Re-running that script would overwrite the corrected `09_implied_move_live.json`. **Before the next full rebuild, replace that block with a call to `abnb_options_ledger.run()` / `23_update_ws09_options.py`.** I did not edit 09_stock_behaviour.py to avoid colliding with WS09's own outputs; this is a one-function change.
4. **`analysis/src/overnight/19_audit_triage.py:98`** lists the A08 location as `analysis/src/abnb_options_ledger.py (MAIN only)`. The file now also exists in the overnight tree at the same relative path.
5. **`data/README.md`** does not yet list `data/processed/abnb_options_ledger.csv` or `23_options_event_estimates.csv` for the overnight tree.

---

## 8. For the model

Nothing in this workstream feeds the driver model. It supplies one trade-structure input and one deleted number.

| Name | Value | Unit | Source |
|---|---|---|---|
| ABNB 20 Nov 2026 ATM straddle, mid | 13.38 (bid–ask 12.94–13.82) | % of spot | `abnb_options_ledger.csv`, run 2026-09-06 |
| ABNB 18 Dec 2026 ATM straddle, mid | 15.65 | % of spot | same |
| ABNB background vol, 10-maturity fit | 36.21 | % annualised | `23_options_event_estimates.csv`, spec `all_eligible` |
| ABNB event-implied move, 5 Nov print | **not identified** | — | see §5; do not substitute a number |
| MAR / HLT / EXPE Q3-26 event sigma | 3.8–4.0 / 4.8–6.8 / 10.3–13.0 | % | `23_options_event_estimates.csv` |
| Historical base rate, mean absolute day-1 move | 7.07 (median 6.87) | % | `09_implied_vs_realised.csv`, n = 23 |

---

## 9. For the 5 Nov card

- **Use the 7.1% historical base rate for the day, not an implied move.** There is no options-implied number available today, and the ones a naive term-structure read produces range from zero to 10%.
- **The 20 Nov straddle at 13.38% of spot is the only quotable option price.** It covers 75 days including the print; it is not an earnings straddle.
- **Re-run date: the week of 26–30 Oct 2026.** Once the 6 Nov 2026 weekly lists (weeklies typically appear four to six weeks out; the 23 Oct weekly is already listed, so the 6 Nov one should appear from about 25 Sep and certainly by mid-October), the estimator has a post-event expiry one day after the print and a pre-event expiry (30 Oct) one week before it. That pair collapses the background-baseline sensitivity from ±7 vol points to a fraction of a point, and E becomes quotable. Commands:
  ```
  py -3.13 analysis/src/overnight/23_options_estimator_test.py --dry-run
  py -3.13 analysis/src/abnb_options_ledger.py
  py -3.13 analysis/src/overnight/23_update_ws09_options.py
  ```
  The ledger appends by run date, so the weekly captures build the term-structure history the pitch wants. Check `event_confidence` at that point — Airbnb should have confirmed the date by then, which upgrades the spec to `company_confirmed` (edit `EVENTS["ABNB"]` and narrow the window to the single date).
- **Decision rule when it becomes measurable:** event-implied move below ~7% ⇒ the straddle is cheap against the base rate; above ~9% ⇒ rich. Apply it to the fitted E, not to the raw straddle, and only if the three specifications agree within ~1.5 points.
