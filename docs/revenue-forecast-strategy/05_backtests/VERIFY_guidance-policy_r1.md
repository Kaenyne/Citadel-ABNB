# VERIFY guidance-policy — round 1

Verifier run 2026-09-11. Independent re-run + manual recomputation from source CSVs,
not a re-read of the implementer's own printed numbers.

## Verdict: **PARTIAL** — safe to score, with two named fixes before it is treated as final

Every headline number I could check reproduces exactly, twice: once from a full fresh
run of `run.py`, and once from independent from-scratch recomputation against the raw
overnight CSVs (bypassing the package's own code). The point-in-time discipline is
sound and the failure disclosures (Gate G4, the 9/9 rule) are the most honest thing in
the programme so far. But there are two concrete defects that must be fixed, not just
noted, because one of them is in a field the harness itself scores.

---

## 1. Re-run

```
cd ".../Citadel-ABNB"
/Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/guidance_policy/run.py
```

Exit code **0**. Wall time **2.4s** (`time` output: 2.01s user, 0.15s sys, 2.379s total).
Existing outputs were copied to `data/processed/forecast_methods/guidance_policy_prev/`
and existing registry files to `data/processed/forecast_methods/registry_prev_guidance_policy/`
before the re-run; a diff of the CSVs shows byte-for-byte reproduction (deterministic:
fixed bootstrap seed, no randomness in the point forecasts).

Console output: 18 of 21 acceptance tests pass. Same three failures as the note claims
in aggregate: A1, E1 (Gate G4), H1 (the 9/9 rule) — see §5 on A1, which is the one that
is NOT individually named anywhere in the note despite the "three failures" framing.

`harness/score.py` was also re-run (not required by the task, but cheap and it is the
real consumer of these registry files): exit 0, and it independently recomputes
`print_from_guide` W2 PIT `rmse_ratio_to_naive = 0.330772` — matching the note's quoted
0.331 to three decimals, computed by a completely different code path (the harness
scorer, not the package's local scoring table). That is a strong independent check.

## 2. Registry format

All five files validated on write (register() raises on any format violation and none
were raised on this re-run). Spot-checked columns, vintage dates, and window/prior_basis
coverage directly:

| object | rows | windows | prior_basis | vintage_date range | n_params |
|---|---|---|---|---|---|
| guide_mid_next_q | 50 | W1, W2, LIVE | PIT, full_sample | 2023-02-14 .. 2026-08-06 | 7 |
| print_from_guide | 50 | W1, W2, LIVE | PIT, full_sample | 2023-02-14 .. 2026-08-06 | 1 |
| print_kernel_policy | 50 | W1, W2, LIVE | PIT, full_sample | 2023-02-14 .. 2026-08-06 | 5 |
| q4_2026_guide_mid | 15 | LIVE | PIT | 2026-09-11 | 7 |
| q4_2026_print | 15 | LIVE | PIT | 2026-09-11 | 7 |

No forecast has a vintage_date on/after its target quarter's print date (the harness's
own PIT validator enforces this and did not reject anything). The two LIVE objects
correctly use `strict_windows=False`, which is a real and correctly-diagnosed harness
gap (`window_of_target("2026Q4")` returns `[]` because `GUIDE_EVENTS_ALL` stops at the
2026-08-06/2026Q3 guide — confirmed by reading `harness/windows.py` directly). The three
harness change requests in the note (no naive baseline for `guide_mid`, no 2026Q4 row in
`targets.csv`, the strict_windows/LIVE interaction) are all real and correctly diagnosed
against the actual harness source, not invented.

**Defect found in the registry (see §5 for detail): `n_params` is wrong for 3 of 5
objects.** `guide_mid_next_q`, `q4_2026_guide_mid` and `q4_2026_print` are all registered
with `n_params=7` ("5 kernel + c + kappa"), but reading `_pit_forecast()` and the section-F
live-grid code line by line shows kappa is used **only** to compute the informational
`cons_at_print_musd` column — never the `guide_mid`/`revenue_musd` point or q50 that is
actually registered and scored. The correct count for all three is **6** (4 seasonal
lambda + 1 lag weight w + 1 cushion c). This is not a leakage or fabrication issue —
it overstates the parameter count, which is the conservative direction — but `n_params`
feeds `param_obs_ratio` in the harness scoreboard, so it is a scored field and must be
corrected, not just caveated.

## 3. Leakage audit

Went through every input source used at every guide date:

* **Pre-guide Street for the historical W1/W2 backtest** comes from
  `16_consensus_at_print_merged.csv` via `street_pre_guide_musd`/`_as_of`, vintage-stamped
  to the *issuing* print date — confirmed by reading `harness/spine.py::build_targets`.
  No 4-Sep-2026 or 11-Sep-2026 vendor value is used as a historical pre-guide Street
  anywhere in the W1/W2 backtest rows. Those two 2026 vintages are used **only** for the
  live 4Q26 object, correctly labeled `street_as_of = 2026-09-04` / consumed at
  `vintage_date = 2026-09-11`, which is the live forecast date, not a historical one.
* **`history_as_of(gdate)`** includes the same-day letter (documented, harness-wide
  convention in `loaders.py`, not a package-specific choice) — this is deliberate and
  is why the trailing-8 cushion at 2026-08-06 reproduces; verified it is the harness's
  own rule, not something this package invented to get a better number.
* **Full-sample priors**: the `full_sample` replay in `_pit_forecast()` deliberately uses
  `lam_full` (the whole-sample lambda table, unfiltered by quarter) and a whole-sample
  cushion — this *is* leakage, but it is labeled `prior_basis == "full_sample"` on every
  row, never presented as PIT, and the note spends an entire subsection (§ "Reading")
  explaining that the PIT-vs-full-sample MAE gap (1.99% → 1.17%) is "almost all...
  parameter leakage." This is the correct, disclosed use of a full-sample replay as a
  contrast, not a hidden shortcut.
* **Just-printed quarter's GBV used before its print date**: checked directly — for
  every `(gdate, tq)` pair, the kernel base uses `GBV_{tq-1}` and `GBV_{tq-2}}`, and
  `tq-1` is exactly the quarter whose results are being announced *in the same letter*
  as `gdate` (by construction of `GUIDE_EVENTS_ALL`). Nothing later is touched.
* **Letter-rounded integers scored as points**: the revenue guide ranges are genuine
  low/high ranges from the ledger, not rounded single points. The nights/GBV bucket
  words are handled as intervals (`BUCKET_WORDS` bounds, and the 4Q26 bucket-probability
  calculation integrates a Normal over interval boundaries at 6.5/9.5/12.5) — correct
  treatment, not point-scored.
* **`basis == 'derived'` rows**: this package never reads `10_regional_panel_quarterly.csv`
  or any regional file (`grep` confirms zero references) — not applicable, and correctly
  so; this package doesn't touch regional data at all.

**No leakage findings.** The one construct that looks like leakage at first glance
(`lam = lam_full[lam_full["quarter"] < tq]` immediately overwritten by `lam = lam_full`
on the line right below it, in `_pit_forecast`) is the `full_sample` branch, which is
*supposed* to use the whole table — the PIT branch (`lam = lambda_table(hist, SEASON_W)`,
computed from the point-in-time `hist` slice) is the one that matters for the PIT claims,
and it is correctly scoped. Flagging this only so a future reader doesn't mistake dead
code for a bug: the redundant `lam = lam_full[lam_full["quarter"] < tq]` line before the
overwrite is inert and should be deleted for clarity, not because it does anything wrong.

## 4. Number check — 9 numbers recomputed independently from the source CSVs

All done with a fresh Python session reading `02_guidance_ledger.csv`,
`16_consensus_at_print_merged.csv`, and `02_kpi_panel_quarterly.csv` directly — not by
re-reading the package's own printed output.

| # | claim | note says | independently recomputed | match |
|---|---|---|---|---|
| 1 | prints beating guide midpoint | 19/19, 0 below low | 19/19, 0 below low (n=19 scoreable) | exact |
| 2 | prints beating range top | 15/19 | 15/19 | exact |
| 3 | trailing-8 cushion at 2026-08-06 (raw ratios) | mean 1.8567%, median 1.7905%, sd 1.0048pp | mean 1.8567%, median 1.7905%, sd 1.0048pp | exact |
| 4 | kappa, LSEG-only pairs | n=12, mean +0.604%, median +0.517%, sd 0.300pp | n=12, mean +0.604%, median +0.5166%, sd 0.3001pp | exact |
| 5 | guide-vs-Street / surprise sd, LSEG era (2023Q3+) | 2.13pp vs 1.16pp, n=12 each | 2.1277pp vs 1.1566pp, n=12 each | exact |
| 6 | Q4 seasonal lambda | mean 12.0298%, range 0.1711pp, n=3 (4Q23/24/25) | mean 12.0298%, range 0.1711pp (11.9461/12.1173/12.026) | exact |
| 7 | GBV_2Q26 input to the live grid | 27,200M | 27,200M (`02_kpi_panel_quarterly.csv`) | exact |
| 8 | live grid, central GBV 26,300, no fee | print 3,200 / guide 3,142 | print 3,199.9 / guide 3,141.6 | exact (rounds identically) |
| 9 | live grid, central GBV 26,300, half fee | print 3,240 / guide 3,181 | print 3,239.9 / guide 3,180.9 | exact (rounds identically) |

No mismatches. This is a genuinely well-checked package — the numbers are not merely
internally consistent, they survive a rebuild from raw sources using independently
written arithmetic.

## 5. Acceptance tests — did they actually run, and was anything marked passed without evidence?

All 21 ran (`00_acceptance_tests.csv`, 21 rows). 18 passed, 3 failed on this re-run,
matching the note's own "18 of 21" claim exactly. Nothing was marked passed without
supporting evidence in the printed detail strings — every PASS line carries the actual
computed numbers, not just a boolean.

**But: the implementer's structured report to this verifier listed only 12 acceptance
tests (A2, A3, B1, B2, B3, C1, C2, D1, D2, E1, F2, H1) and named only E1 and H1 as
failures.** The actual run has 21 tests and 3 failures. The third failure, **A1**
("guide ranges in ledger == 22 (19 scoreable + 3 with no actual yet)"), was silently
dropped from that list. Checked independently against the raw ledger:

```
total revenue-range rows in 02_guidance_ledger.csv: 20   (not 22)
  scoreable (has actual): 19
  pending (no actual yet, i.e. 2026Q3 LIVE): 1            (not 3)
```

The note's own prose in section (a) still reads "22 quarterly revenue ranges in the
ledger, 19 with a realised actual... 2026Q3 is LIVE" — internally inconsistent with its
own rebuilt `01_guide_history.csv` (20 rows) and with the raw ledger (20 rows). This
looks like a stale number carried over from an earlier draft of the spec/tell-file that
was never reconciled after the ledger data was pulled. It does not affect any scored
number (19/19 and 15/19 are both independently verified correct above, and n=19 is used
correctly everywhere downstream), but it is a factual error still sitting in the note,
and the failing test that would have caught it (A1) was not disclosed to this verifier
even though the note's own console output flags it as a FAIL every time the script runs.

## 6. Honesty of the interpretation

This is the strongest part of the package. Specific things done right:

* Leads with the failure, not the win: Gate G4 (a pre-registered architect falsification
  test — confirmed by reading `04_synthesis/00_INTEGRATED_SYSTEM.md` line 421 and
  `01_METHOD_CARDS.md` line 143, both of which specify "target ≥8/14" exactly as coded)
  is reported as **failing on both windows**, with the correct fallback already invoked
  ("lead the memo with the FX/mix decomposition, not the gap forecast" — verbatim from
  the architect's own contingency plan for this exact failure mode).
* Publishes the PIT-vs-full-sample gap as the headline of §(c) rather than only in an
  appendix, and states outright that "almost all of the apparent skill in a full-sample
  replay is parameter leakage."
* Corrects two tell-file claims that turn out to be wrong on inspection of the primary
  data: the "FY guide is only raised, never cut" claim (one real cut found, FY2025
  new-business investment 225M→200M at 2Q25), and the addendum's stated predictive sd
  (2.6pp vs the measured 3.03pp) — both flagged as the single largest disagreements in
  the package rather than quietly reconciled.
* Kills the 9/9 drift rule as a tradeable signal on its own initiative, with the correct
  methodological move (strip the un-tradeable overnight gap by re-entering at the
  reaction-day close) and a calendar-artefact check that independently explains away the
  apparent pattern.
* Every full-sample number is labeled as such; nothing PIT-scored is silently swapped
  for a full-sample number to make a headline look better.

Two things pull this down from "pass" to "partial": the n_params overcount on 3 objects
(§2) is a real scored-field defect, not just a disclosure gap, and needs a one-line code
fix (`n_params: 7 -> 6` at three call sites) plus a re-register before this package's
`param_obs_ratio` can be trusted in the cross-package scoreboard. The A1 omission (§5) is
lower stakes — no scored number is affected — but the note should name it explicitly and
fix the stale "22" figure rather than leaving an unexplained FAIL in the console output
that contradicts the note's own prose.

## Issues to fix, in priority order

1. **Fix `n_params` for `guide_mid_next_q`, `q4_2026_guide_mid`, `q4_2026_print`: 7 → 6.**
   Kappa is not used in any of these objects' `point`/`q50` (verified: it feeds only the
   informational `cons_at_print_musd` grid column). Re-register after the fix; this
   changes the harness's `param_obs_ratio` for these three files.
2. **Reconcile the A1 test.** The ledger has 20 revenue-range rows (19 scoreable + 1
   pending: 2026Q3), not 22 (19+3). Fix the hard-coded expectation in `section_a`'s
   acceptance test, and correct the "22 quarterly revenue ranges" sentence at the top of
   note section (a) to "20." State explicitly in the note's "What failed" list that A1
   was a stale-expectation bug in the test itself, not a data problem.
3. (Cosmetic) Delete the dead `lam = lam_full[lam_full["quarter"] < tq]` line in
   `_pit_forecast` (immediately overwritten) so it doesn't read as leakage on a future
   pass.
4. (Cosmetic) The section-(d) headline prose says "guide 3,141"; the table two lines
   below says "3,142" for the same cell (3,141.6 rounds to 3,142). Make them agree.

None of these four issues change any of the substantive conclusions (print_from_guide's
edge, Gate G4's failure, the 9/9 rule's death, the live 4Q26 grid) — all of which are
independently verified correct above.
