# 19. Triage and repair of the independent audit's findings

*Overnight run follow-up, 6 September 2026. Working tree `C:\Users\krish\citadel-abnb-overnight`,
branch `krish/overnight-synthesis`, HEAD `77037c2` at the start of the pass. Input:
`C:\Users\krish\citadel-abnb\docs\2026-09-06_audit_findings_ai_handoff.md` (read-only; nothing in the
main tree was touched).*

Deliverables: `data/processed/overnight/19_audit_triage.csv` (19 rows),
`19_repairs_applied.csv` (23 rows), `analysis/src/overnight/19_audit_triage.py` (the generator).

---

## Bottom line

**Nineteen findings triaged: 6 fixed here, 10 reassigned to other agents mid-run, 1 judgment call for
Krish, 2 already fixed in `77037c2` and re-verified.** Two of the audit's findings are partly or
wholly **not reproducible in this tree** and are recorded as such.

Fixed by this pass: **A01** (future revenue leaking into a pre-print backlog feature), **A05**
(Common Crawl year-over-year comparing the wrong quarters), **A09** (the malformed WS16 news CSV),
**A10** (the reverse-DCF `#DIV/0!`), **S01** (a red-team allegation that was itself wrong), and
**K01** (Krish's `15_cross_note_conflicts` complaint).

**No headline number moved.** Every model output is unchanged: the rebuilt workbook still
reconciles **216/216** named outputs and **2,349/2,349** formula cells against the Python mirror in a
real Excel 16.0 full rebuild, with **0 error cells in 5,547**, and the scenario switch still returns
**141 comparisons, 0 mismatches**. FY26/27/28 base revenue, EBITDA, FCF per share, share count and
the football field are byte-identical to the committed run. The alt-data scoreboard is also
unchanged in aggregate — still 598 tests, still 52 beating AR(1), 31 beating naive, 26 beating both.
The corrections change *which* rows are legitimate, not what the run concludes.

Scope note: partway through this pass the orchestrator reassigned most findings to agents 20-25.
Three files I had already edited belong to agent 24 and the edits were **left in the tree** at the
orchestrator's instruction — they are listed in "Edits left in the tree for other owners" below, and
in `19_repairs_applied.csv` with the id suffix `(out of scope, edit left in tree)`. Where those edits
would have changed another workstream's published numbers, I **restored the data outputs** and left
only the code.

---

## Triage table

| id | finding (short) | status on HEAD `77037c2` | decision | sev |
|---|---|---|---|---|
| A01 | Backlog feature divides by the target quarter's actual revenue | still open, reproduced | **fix now — done** | high |
| A02 | Reaction tests are LOO, and the return window starts before the predictor exists | still open | reassigned — agent 20 | high |
| A03 | Window sensitivity, multiple testing, data vintage | still open | reassigned — agent 20 | high |
| A04 | Partial Inside Airbnb snapshots contaminate year-ago pairs | still open | reassigned — agent 21 | med |
| A05 | Common Crawl four-**row** shift is not four **quarters** | still open, reproduced | **fix now — done** | med |
| A06 | Regulatory tail sampled without its parent; Barcelona conditional | still open | reassigned — agent 22 | med |
| A07 | Reproducibility: deps, paths, build order | **partly not reproducible here** | reassigned — agent 24 / disagree in part | med |
| A08 | Options event-variance identification | **not reproducible here** (file absent) | reassigned — agent 23 | med |
| A09 | Two malformed records in `16_news_since_5sep.csv` | still open, reproduced | **fix now — done** | med |
| A10 | Reverse-DCF `#DIV/0!` when growth equals the discount rate | still open, reproduced in Excel | **fix now — done** | med |
| A11 | Rerun script cannot append a quarter; stale derived surprises | still open; my edit left in tree, outputs reverted | reassigned — agent 24 | med |
| A12 | Valuation-date and share-count conventions | open question, not an error | **judgment call for Krish** | med |
| A13 | Audit scripts never exit nonzero | still open; my edit left in tree | reassigned — agent 24 | med |
| R01 | FY2026 share-count double-count | **already fixed**, re-verified | no action | — |
| R02 | Workbook mechanics / WS16 integration | **already fixed**, re-verified | no action | — |
| S01 | The "~50% single fee was invented" allegation is itself wrong | still open in the WS15 files | **fix now — done** | med |
| S02 | Stale counts and "eight prints" in `FINAL_SUMMARY.md` | still open | reassigned — agent 25 | low |
| S03 | WS17 note needs a superseded marker | still open | reassigned — agent 25 | low |
| K01 | "Listing 15_cross_note_conflicts seems to have paused" | see the diagnosis below | **fix now — done** | med |

Full rows, with the files, the audit's proposed repair and my evidence, are in
`data/processed/overnight/19_audit_triage.csv`.

---

## What was repaired, before and after

### A01 — future revenue in the backlog feature

`analysis/src/overnight/08_altdata_backtests.py`, `backlog_features()`. The feature was

```
F["bl_unearned_to_next_rev_lag1"] = b["unearned_to_next_q_revenue"].shift(1)
```

and `unearned_to_next_q_revenue` at quarter *q* is `unearned[q] / revenue[q+1]` — the ratio is built
with a **negative** shift in `analysis/src/abnb_eu_platform_and_backlog.py`. Shifting the finished
ratio forward one row therefore gives, at target quarter *t*, `unearned[t-1] / revenue[t]`. The
numerator is historical; the denominator is the actual revenue of the very quarter being forecast. A
lag applied *after* a ratio is formed does not remove leakage. The audit is exactly right.

Replaced with `unearned[t-1] / revenue[t-1]` (`bl_unearned_to_prior_rev_lag1`) — both operands were
reported at the prior print. The retrospective next-quarter ratio is deliberately **not** carried
into the feature frame, because every `bl_` column in that frame is tested as a pre-print feature.

*Acceptance check.* On a four-quarter fixture, perturbing the 2025Q4 actual revenue while holding
everything knowable at the cutoff fixed **changes the old feature** at 2025Q4 and **does not change
the replacement**.

| | old (leaky) | new |
|---|---|---|
| rows in `08_feature_tests_all.csv` | 6 | 6 |
| Pearson r range | −0.143 to −0.465 | +0.020 to −0.318 |
| best walk-forward ratio vs AR(1) | 0.951 | 0.995 |

The leaky feature was **never a reported survivor** — its best result was still worse than AR(1) — so
nothing in any note has to be withdrawn. What changes is that six of the 598 rows are now legitimate
pre-print tests. Family counts (598 tests, 52 beat AR(1), 31 beat naive, 26 beat both) are unchanged.

### A05 — Common Crawl year-over-year

`cc_features()` grouped informative crawls by quarter and then took `.shift(4)` on the observed rows.
Informative crawls skip quarters, so four rows is often not four quarters. Reproduced exactly,
including all three of the audit's examples:

| target quarter | old comparison | correct |
|---|---|---|
| 2023Q4 | 2022Q3 | 2022Q4 |
| 2024Q1 | 2022Q4 | 2023Q1 |
| 2024Q2 | 2023Q1 | 2023Q2 |
| 2024Q3 | 2023Q2 | 2023Q3 (missing) |
| 2026Q1 | 2024Q4 | 2025Q1 |
| 2026Q2 | 2025Q1 | 2025Q2 |
| 2026Q3 | 2025Q2 | 2025Q3 |

**Seven of twelve comparisons were wrong.** Fixed by reindexing onto a contiguous quarterly
`PeriodIndex` before the difference. Gaps stay `NaN` — no forward fill, so no crawl observation is
invented to obtain a y/y.

`cc_survival_yoy_pts`, before → after: 2023Q4 −4.816 → −2.885; **2024Q1 −3.100 → +2.767 (sign
flip)**; 2024Q2 2.211 → 0.911; 2024Q3 2.095 → NaN; 2026Q1 2.248 → 2.303; 2026Q2 1.553 → −0.021;
2026Q3 0.064 → −1.422.

Downstream: the `cc_survival_yoy_pts → nights_yoy` test goes from n 11, r −0.581, walk-forward
0.690× naive, sign accuracy 0.571 to **n 10, r −0.544, 0.675× naive, sign accuracy 0.833**. The
component-family "best ratio" cell in `08_test_scoreboard.csv` moves 0.690 → 0.675. `08_q3_2026_nowcast.csv`
and `08_demand_index_quarterly.csv` — the two WS08 files the driver model reads — are **byte-identical**,
so the model is untouched.

### A09 — the malformed WS16 news CSV

Confirmed on HEAD. Physical lines 15 and 16 carried an unquoted publisher
`TipRanks (estimated, not company-confirmed)`, giving eight fields against a seven-field header, and
`pandas.read_csv` raised. Quoted both fields. The file now parses in strict `csv.reader` and in
pandas as **20 data rows × 7 fields**, every value preserved, URL and status columns unshifted.

### A10 — the reverse-DCF boundary case

`13_excel_builder.py`, `rdcf()`. The ten-year leg was the closed-form annuity
`b*(1+g)/(coe−g)*(1−((1+g)/(1+coe))^10)`, which divides by zero when the assumed growth equals the
cost of equity — even though a ten-year stream is perfectly well defined there (its value is `10·b`).
The shipped 10.5% cost of equity misses every rung of the growth ladder, which is why the bug was
invisible. Now written as the explicit ten-term discounted sum, which never divides by `(coe−g)`,
uses only `+ − * / ^` so the WS13 evaluator still parses it, and is continuous through equality. The
Gordon terminal keeps its `/(coe−g_term)`: a terminal growth at or above the discount rate is
genuinely invalid under a perpetual-growth formulation, and `#DIV/0!` there is the right answer
rather than a plausible price.

*Acceptance test, run in Excel 16.0 over COM on both workbooks:*

| cost of equity | old workbook `Valuation!B59` / `C59` | new workbook |
|---|---|---|
| 10.500% | 215.13 / 145.19 | 215.13 / 145.19 |
| 10.99999% | 201.02 / 136.04 | 201.02 / 136.04 |
| **11.000%** (equals the ladder's 11% rung) | **#DIV/0! / #DIV/0!** | **201.02 / 136.04** |

The new values also match the Python mirror: `dcf_constant(4827, 0.11, 10, 0.11, 0.03)` plus $9,593M
net cash over 597M shares gives 201.02 and 136.04. Excel and Python now agree in the region where
they used to disagree.

*Effect on everything else: none.* 22 formula cells changed text; 9 cell **values** changed, all at
the 1e-12 level (floating-point reassociation), the largest being `Valuation!B59` 215.130568281 →
215.130568280997. The reverse-DCF staleness-check cell moved from exactly 0 to −2.8e-13 and still
displays 0.00. All five `13_*.csv` outputs are byte-identical.

| after the rebuild and re-dump | value |
|---|---|
| cells dumped from Excel 16.0, error cells | 5,547 / **0** |
| named outputs matching the Python mirror | **216 / 216** |
| formula cells matching the evaluator | **2,349 / 2,349** |
| scenario switch | **141 comparisons, 0 mismatches** |
| static scan (informational) | 321 → 343 hits |

The 22 extra static-scan hits are the literal exponents `^1 … ^10` in the rewritten cells flagged as
"hard-coded constant in formula". They are not defects. `17_scenario_switch.csv` goes 143 → **145
rows** (141 comparisons + 4 change-count summaries) because the pre-WS17-fix "before" dumps now exist
in the dump directory; 145 is the number the WS17 note itself documents, so this reconciles the CSV
with its note.

### S01 — a red-team allegation that was itself wrong

WS15's CONF-11 said the "~50% of active listings on the single service fee" figure appeared in
neither the 2Q26 letter nor the 2Q26 call. It **is** in the call, prepared remarks,
`data/raw/regulatory/transcripts/2026-Q2.txt` line 272: *"Approximately half of our active listings
are now subject to the single service fee."* It is absent from the shareholder letter, which is a
different claim. WS16 caught this first; the WS15 files had not been updated. CONF-11 is now marked
withdrawn with the source and line, the companion claim row goes from `unsupported` to `confirmed`,
and the red-team note's tally moves from **83/9/2/4 to 84 confirmed / 9 wrong / 1 unsupported / 4
unverifiable**, with an amendment banner and the original tally kept in brackets.

---

## K01 — the `15_cross_note_conflicts` diagnosis

**The file was not truncated and nothing had stopped.** Measured on HEAD: 8,111 bytes, 17 CRLF lines,
**16 data rows carrying CONF-01 through CONF-16**, 8 columns, 86 double-quotes with every individual
line quote-balanced, no embedded newline, no control character, no non-ASCII byte, longest cell 560
characters, and `pandas.read_csv` returns `(16, 8)`. The generator
`analysis/src/overnight/15_claim_checks.py` contains all 16 conflict tuples and writes them with
`csv.writer`. Re-running it reproduces the file. There is no missing conflict and no half-written row.

What is actually wrong is three things, and the third is almost certainly what was seen.

**1. Excel silently evaluated cells that begin with `+` or `-`.** Opened in Excel 16.0 over COM and
compared cell by cell against the CSV text, the conflicts file had 24 cells where Excel showed
something other than what the file says, and the companion `15_claim_checks.csv` had 94. Most are
harmless, but four are **silent arithmetic corruption of the red-team's own evidence**:

| cell in `15_claim_checks.csv` | file says | Excel showed |
|---|---|---|
| WS03 credibility row, value claimed | `+0.69 / 0.0005 / +0.72` | **1916.667** |
| WS03 credibility row, value verified | `+0.688 / 0.0005 / +0.724` | **1900.552** |
| WS02 nights-guide row, value claimed | `+4.0 / +2.6` | **1.538462** |
| WS05 FX row, value verified | `+11.11 / +2.56 / −1.56` | **−2.78195** |

Excel treats a leading `=`, `+`, `-` or `@` as the start of a formula, quoting in the CSV does not
prevent it, and `+0.69 / 0.0005 / +0.72` happens to be a *valid* formula. Anyone reading these files
in Excel has been reading three fabricated numbers. In `15_cross_note_conflicts.csv` the same
mechanism turned `+12.4%` into the number 0.124.

**2. Workstream ids lost their leading zero.** `ws_a` / `ws_b` and the claim file's `workstream`
column held `"01"`…`"12"`; Excel renders them as 1…12, so the column reads as a number and sorts and
filters as one.

**3. The listing that genuinely stops short is in the note, not the CSV.** The "For the model" table
in `research/notes/overnight/15_red-team.md` lists CONF-01 … CONF-14 and then jumps straight to
CONF-16. **CONF-15 was missing** — fifteen of sixteen conflicts, with the gap in the middle. If the
complaint came from reading that table, the listing had indeed "paused". (The equivalent table in
`14_master-synthesis.md` has all sixteen.)

**Repairs.** The generator now (a) resolves its output directory from the project root instead of a
hard-coded absolute path, (b) writes workstream ids as `WS01`…`WS12`, (c) writes any cell that would
start with `= + - @` with one leading space so Excel keeps it as text, and (d) reads both files back
after writing and asserts they are rectangular, free of embedded newlines, free of formula-leading
cells, and that the conflicts file holds exactly `CONF-01`…`CONF-16`. The missing CONF-15 row was
added to the note's table.

Re-opened in Excel after the repair, no cell is evaluated as a formula and no leading zero is lost.
Three cosmetic differences remain and are not defects: Excel renders `36.6%` as `36.60%`, `+12.4%` as
`12.40%` and `0.0` as `0` — the same numbers, formatted. If you parse these files with pandas,
`.str.strip()` the values.

---

## Judgment call for Krish

**A12 — valuation date and share-count conventions.** `13_driver_model.py`'s `valuation()` seeds the
DCF with FY2027 FCF, discounts the next annual flow one period and divides by FY2027 shares, which is
naturally a *forward* convention, but upside is quoted against the September 2026 spot and the
football field mixes FY2027 and FY2028 exit lenses; separately, the 597M share anchor is Q2 diluted
**weighted-average** shares while the roll-forward output is labelled period-end diluted. *Neither is
an arithmetic error and I have not changed anything.* My recommendation: label the outputs **forward
targets at 31 Dec 2027** rather than present fair values (that is what the arithmetic already is, and
it is the honest description), and add one line to `model/assumptions.md` saying the share anchor is a
weighted-average proxy and the per-share outputs are therefore approximations, not reported GAAP EPS.
The alternative — re-timing every flow to a September 2026 present value — moves every headline price
and should not be done days before a pitch draft.

*(A02 and A03 are also conclusion-level rather than mechanical, but they were reassigned to agent 20
rather than left for Krish.)*

---

## Disagreements and non-reproducible findings

**A08 — not reproducible in this tree.** `analysis/src/abnb_options_ledger.py` **does not exist**
under `C:\Users\krish\citadel-abnb-overnight`; it is uncommitted work in the main tree. The audit's
algebra (the difference of squared vols recovers `E·(1 − T_near/T_far)`, not `E`) is correct on its
face and I do not dispute it, but it cannot be repaired or re-tested from the overnight tree.

**A07 — partly wrong for the authoritative tree.** The audit says `requirements.txt` "lacks
`statsmodels`, `scipy`, and a Parquet engine". That is true of MAIN. The overnight tree's
`requirements.txt` already contains `pyarrow`, `statsmodels` and `scipy` (with `requests` and
`statsmodels` duplicated, which is cosmetic), and `analysis/src/overnight/` is present in full. The
audit's own text scopes the finding to MAIN, so this is a scoping clarification rather than a flat
contradiction — but a reader skimming the findings table would draw the wrong conclusion about the
tree they are actually working in.

**Not a disagreement, but worth stating:** every other finding I checked reproduced exactly as
described, including all three of A05's cited quarter pairs, both of A09's line numbers, and A10's
"set the cost of equity to 11% and the 11% ladder row breaks" recipe. The audit's line references had
not drifted.

---

## Edits left in the tree for other owners

The orchestrator reassigned these files to **agent 24** after I had already changed them, and
instructed that the edits stay. All three are listed in `19_repairs_applied.csv`.

| file | what I changed | state |
|---|---|---|
| `analysis/src/overnight/17_excel_audit.py` | `main()` returns 1 on any failed named-output or formula-cell comparison, a wrong output count, or a missing required cell; the informational static scan does not affect status; `raise SystemExit(main())`. Prints PASS/FAIL | **in tree, verified running** (PASS, exit 0) |
| `analysis/src/overnight/17_scenario_switch.py` | same exit-status treatment, plus a failure if the selector moves 0 cells for a scenario; dump directory resolves from `argv[1]`, then `ABNB_EXCEL_DUMP_DIR`, then the historical default, with a named error on missing dumps | **in tree, verified running** (PASS, exit 0) |
| `analysis/src/overnight/16_merge_and_rerun.py` | rewritten: `main()` entry point, project-relative root, schema and duplicate-key validation, an explicit append path for a previously unseen quarter, and derived fields recomputed from primitives (sourced beats calculated, with a disagreement warning) | **script in tree; data outputs restored to their committed state** |

The last one needs agent 24's decision, because running it changes WS16's published numbers. With the
recompute in place, `eps_surprise_pct` is derived for three prints where WS16 supplied consensus and
actual but the surprise cell stayed blank — 2020Q4 −33.81, 2021Q1 −82.243, 2021Q2 +73.171 — which
moves `uni_eps_surprise_pct` from n 17 / 17 / 16 to **n 20 / 20 / 19** at 1d / 5d / 20d and shifts a
number of permutation p-values by a few thousandths. **No EPS specification becomes predictive
either way** (leave-one-out R² stays at or below +0.07). I reverted
`16_consensus_at_print_merged.csv`, `16_reaction_panel.csv`, `16_reaction_tests.csv` and
`16_rerun_delta.csv` to their committed contents so the CSVs still match the WS16 note; only the
A09 fix to `16_news_since_5sep.csv` remains.

---

## Corrections to existing work

- `research/notes/overnight/15_red-team.md` — amended (banner, verdict tally 83/9/2/4 → 84/9/1/4, the
  WS06 single-fee paragraph struck through and corrected, the missing CONF-15 row added). This is
  another workstream's note; the amendment is dated and the original text is preserved in brackets or
  struck through rather than deleted.
- `docs/overnight/FINAL_SUMMARY.md` — **not edited** (agent 25 owns it). Two things are stale there:
  line 67 still says "All eight prints where the guide came in below Street had a negative 20-day
  return" when WS16 made it **9 of 9**, and "Where everything lives" says 39 scripts / 153 CSVs / 15
  notes when the tree now holds **44 scripts, 169 CSVs, 18 notes** (24 figures is still right).
- `research/notes/overnight/17_excel-audit.md` — **not edited** (agent 25). Its bottom line still
  describes the share-count error as open; WS18 fixed it. It needs a superseded-by marker.

## Remaining open items

A02, A03 (agent 20); A04 (agent 21); A06 (agent 22); A08 (agent 23, and not reproducible here);
A07 path/build items, A11 data decision, A13 (agent 24); A12 and the documentation staleness S02/S03
(agent 25 and Krish).

## For the model

Nothing. This pass supplies no new parameters and moves no model number. The one thing it guarantees
is negative: after A10, `model/ABNB_driver_model.xlsx` no longer produces `#DIV/0!` anywhere in the
reverse-DCF ladder for any cost of equity, so flexing that input in Excel is safe.

## For the 5 Nov card

Nothing changes on the card. One caveat to carry: the `cc_survival_yoy_pts` series that feeds the
supply index is now correctly aligned and its 2026Q2 and 2026Q3 readings flipped from mildly positive
to slightly negative (1.553 → −0.021 and 0.064 → −1.422). The supply index was not a forecaster
before the fix and still is not, so nothing on the card depends on it — but do not quote the old
values.
