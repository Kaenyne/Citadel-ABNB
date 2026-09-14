# G1b: DoltHub consensus history into the L0 vintage register (stand-in for WP-G1)

Agent/session: Claude Code (Fable 5.1) subagent, orchestrated run. Date: 14 September 2026. Branch: `krish/github-altdata-catalog` (worktree `C:/Users/krish/citadel-abnb-ghcat`). Packages touched, all new: `analysis/src/forecast_methods/L0_dolthub_v2/` (run.py, t0_provenance.py, post_append_checks.py, t1_vendor_equivalence.py, register_street_dolthub.py, nclh_pull.py, README.md), `data/processed/forecast_methods/L0_dolthub_v2/`, the registry file `data/processed/forecast_methods/registry/l0-dolthub-v2__street_dolthub.csv`, this note, two rows in `WORKBOARD.md`. Pre-existing files touched: `data/processed/forecast_methods/L0/L0_vintage_register.csv`, append-only, after a dated byte copy to `L0_vintage_register.backup_2026-09-14.csv`; `harness/scoreboard.csv` and `scoreboard.md`, rewritten by `score.py` as the harness intends. Time spent: about 1.5 hours wall, most of it the 10 s / 60 s API spacing.

## Verdict

Pass. The DoltHub `post-no-preference/earnings` history is now in the L0 vintage register as a second, vintage-stamped vendor: 1,159 ABNB revenue rows (290 weekly snapshots, 2021-02-07 to 2026-09-13, four period slots each, one row dropped for a missing consensus), vendor string `DoltHub post-no-preference/earnings`, `role=pit_history`. The register went from 161 to 1,320 data rows; its first 43,035 bytes are byte-identical to the backup; no duplicate ids; the frozen `test_l0.py` suite is 20 passed before and 20 passed after; the LSEG $4,610M hard-rule row is untouched and `pre_guide_street('2026Q3')` still returns it. T0 (is the history immutable?) passed on the second attempt: at the commit that wrote each of three historical snapshots (2022-08-07, 2024-02-11, 2025-08-03), every one of the 12 AS OF rows equals today's table to the dollar and to the analyst. T1 (is DoltHub the same Street as the register's press quotes?) passed both pre-registered lines: on the 18 pre-guide cells the median |diff| is 0.48 % (line: at most 1.0 %) and the sign of guide minus Street agrees on 18 of 18 (line: at least 16); on the 23 at-print cells the median |diff| is 0.0 % (line: at most 0.5 %), 12 of 23 exact. The two register holes now have a DoltHub value: 2021Q4 pre-guide $1,430M (n=10, 2021-10-31 snapshot, guide mid $1,435M) and 2024Q3 pre-guide $3,860M (n=11, 2024-07-28 snapshot, guide mid $3,700M, so the guide came in below the Street). The first T0 attempt is written up below as inconclusive (my query picked the wrong commit of the day; zero rows came back), not deleted. A registry baseline `l0-dolthub-v2 / street_dolthub` is scored (W1 ratio 1.146, W2 0.881, not a survivor, same shape as `baselines/street` at 1.073 / 0.871). One behaviour change matters for every consumer of `l0.pit_consensus(..., vendor=None)`: all 23 guide-date lookups and all 23 print-date lookups now return a DoltHub snapshot where they returned None or an older-vintage press quote; pass `vendor=` or `role=` to reach the register's original values. Quoting a historical DoltHub value externally as Zacks needs a human decision (WP-O line added).

## Pre-registration (written before computing anything)

Source: `data/processed/github_altdata/samples/dolthub-post-no-preference-earnings-consensus-vintages/sales_estimate_ABNB_BKNG_EXPE.csv`, pulled 14 Sep 2026 from the DoltHub SQL API (`post-no-preference/earnings`, branch `master`). The ABNB slice is the complete `sales_estimate` table for the ticker: 1,160 rows, 290 snapshot dates from 2021-02-07 to 2026-09-13, four period slots per snapshot (Current Quarter, Next Quarter, Current Year, Next Year), consensus in whole US dollars, with count, high, low and year_ago. Descriptive facts noted before the tests, not results: 282 of 290 snapshot dates are Sundays; 2023-02-28 (Tuesday) and 2025-10-13 (Monday) are the two exceptions. One row (2023-08-06, Current Quarter, period end 2023-09-30) has no consensus, count, high or low; it is dropped and logged. Every Current Year / Next Year row has a December period end.

Vendor string for every appended row: `DoltHub post-no-preference/earnings`. It must not contain the substring `zacks` in any case, because `l0.pit_consensus()` filters vendor with `str.contains(case=False)` and the frozen test `test_zacks_4740_is_not_usable_as_the_six_august_street` asserts that `pit_consensus('revenue','2026Q3','2026-08-06', vendor='Zacks')` is None; a vendor string carrying "zacks" would leak the 2 Aug 2026 DoltHub snapshot into that lookup.

Rows appended: ABNB revenue only, one row per (snapshot date, period slot), `role=pit_history`, `pit_usable=True`, `vendor_attributed=True`, `as_of_timestamp` = the snapshot date, `register_id = PIT-{period}-revenue-DHPNP-{YYYYMMDD}`. No EPS rows (the DoltHub EPS basis is not the register's press-quote adjusted EPS). No NCLH rows (the register is ABNB-only).

### T0, provenance: is the DoltHub history immutable?

Method: keyless GET to `https://www.dolthub.com/api/v1alpha1/post-no-preference/earnings/master?q=<sql>`, at most 12 requests, 10 s apart. Queries, in order:

1. `select commit_hash, committer, date, message from dolt_log order by date desc limit 5`
2. `select commit_hash, committer, date, message from dolt_log order by date asc limit 3`
3. For each of three historical ABNB snapshot dates, 2022-08-07, 2024-02-11 and 2025-08-03: `select commit_hash, date from dolt_log where date between '<snapshot>' and '<snapshot + 14 days>' order by date limit 1`, then `select * from sales_estimate as of '<commit_hash>' where act_symbol = 'ABNB' and date = '<snapshot>'`.

Pass line: for all three snapshots, every (period, period_end_date) row returned by the AS OF query has consensus, count, high and low equal to the row in the current table (the sample CSV) to the dollar and to the unit. PASS means the history is immutable and every snapshot may be appended. FAIL (any AS OF row differs from the current row) means only the latest snapshot (2026-09-13) may be appended, and the rest are written to `dolthub_weekly_panel.csv` only. If the API is unreachable or returns 403 before the three checks complete, T0 is recorded as "not run", the append still proceeds with every snapshot, the verdict is written as "provenance unverified", and every appended row's note says so.

### T1, vendor equivalence against the register

Pre-guide cells: the register's `PG-*` rows with `pit_usable == True` and a value. There are 18 (2022Q1 to 2026Q3 minus 2024Q3; 2021Q4 has no value). For each, `guide_date` and `guide_mid` come from `data/processed/forecast_methods/harness/calendar.csv`, the row whose `next_quarter_guided` equals the period. DoltHub value: the latest snapshot with `date < guide_date` (strict) whose row's `period_end_date` maps to the period. `diff% = (DoltHub - register) / register * 100`. Sign agreement: `sign(guide_mid - Street)` under the register value versus under the DoltHub value, with numpy sign (zero counts as its own sign) and agreement meaning the two signs are equal.

Pass line, pre-guide: median |diff%| <= 1.0% AND sign agreement on at least 16 of the 18 cells.

At-print cells: the register's `role == at_print`, `metric == revenue` rows (23, 2020Q4 to 2026Q2). DoltHub value: the latest snapshot with `date < print_date` (strict, `print_date` from `calendar.csv`) whose `period_end_date` maps to the printed quarter. Cells where no DoltHub snapshot exists before the print date are reported as missing and excluded from the median, with n stated.

Pass line, at-print: median |diff%| <= 0.5%.

Both lines must hold for T1 to PASS. Either failing is a FAIL, written up, and the rows stay in the register (they are a second vendor with its own stamp, not a replacement for the register's values).

Also reported, not tested: the DoltHub next-quarter value strictly before the guide date at the two register holes, `PG-2021Q4-revenue` (no vintage) and `PG-2024Q3-revenue` (no vintage, `pit_usable=False`). Those rows are not edited.

### Hard-rule invariants after the append (step 6)

1. `py -3.13 -m pytest analysis/src/forecast_methods/L0/test_l0.py -q` gives exactly the same pass/fail counts as before the append (before: 20 passed, 0 failed).
2. The backup file is byte-identical to the prefix of the new register (the whole backup compared to the first `len(backup)` bytes of the new file).
3. Zero duplicate `register_id` values.
4. `l0.pre_guide_street('2026Q3')` is vendor LSEG, value 4610.0, as_of 2026-08-06.
5. `l0.pit_consensus('revenue','2026Q3','2026-08-06', vendor='Zacks')` is None.
6. `l0.pit_consensus('revenue','2026Q3','2026-08-06', vendor='DoltHub')` returns the 2026-08-02 snapshot (value reported).
7. `l0.pit_consensus('revenue','2026Q3','2026-09-11', vendor='Zacks')` is still 4740.0.
8. No appended vendor string contains `zacks` (case-insensitive).

Behaviour change measured, not tested: for every guide date and every print date in `calendar.csv` (non-forecast rows with a date), `pit_consensus('revenue', <next quarter after the print quarter> / <printed quarter>, as_of=<date>, vendor=None)` computed with the same selection logic against the backup and against the new register; the count of lookups whose value changes, and the largest relative change. Expectation stated in advance: most will change from None (the register holds no vintage strictly before a guide date for the next quarter) or from a stale earlier value to a DoltHub Sunday snapshot, because DoltHub is the only vendor in the register with weekly vintages. That is the point of the append, and it is why any consumer that wants the register's original press-quote values must pass a vendor or a role.

### Registry baseline (step 8)

If FORMAT 1.0 can be matched exactly: a new registry file `baselines-street-dolthub__street_dolthub.csv` (method `baselines-street-dolthub`, object `street_dolthub`), one row per guide date in the harness `GUIDE_EVENTS_ALL` per window per prior_basis, `target=revenue_musd`, `point = q50 =` the DoltHub next-quarter snapshot strictly before the guide date, `street_vendor='DoltHub post-no-preference/earnings'`, `street_as_of = knowable_from =` the snapshot date, `n_params=0`, sigma from trailing actual/DoltHub-street ratios exactly as `baseline_street` does (PIT: last 8 ratios whose print date is on or before the vintage; full_sample: all). Then `python analysis/src/forecast_methods/harness/score.py`, exit code recorded, and every pre-existing scoreboard row must be unchanged (diff of `scoreboard.csv` before and after, restricted to rows not belonging to the new method).

(Deviation recorded after the fact, before scoring: the method name became `l0-dolthub-v2`, the package name, because the harness README rule is "method = your package name" and the README wins. File: `registry/l0-dolthub-v2__street_dolthub.csv`. The object name, columns and construction are as pre-registered.)

## What ran

All from the worktree root `C:/Users/krish/citadel-abnb-ghcat`. `python` is the repo venv (3.11, pandas 3, no pytest, no scipy); `py -3.13` (pandas 2.3.3, pytest 9.1.1, scipy 1.17.1) is used where pytest or scipy is needed.

| step | command | exit | wall |
|---|---|---|---|
| tests before | `py -3.13 -m pytest analysis/src/forecast_methods/L0/test_l0.py -q` | 0 | 0.6 s, 20 passed |
| T0 attempt 1 | `python analysis/src/forecast_methods/L0_dolthub_v2/t0_provenance.py` | 0 | 8 requests, all HTTP 200, first two dolt_log reads 50 s each (cold), verdict FAIL-by-zero-rows, written up below |
| T0 attempt 2 | `python analysis/src/forecast_methods/L0_dolthub_v2/t0_provenance.py --by-message` | 0 | 4 requests, all HTTP 200, under 1 s each, verdict PASS |
| backup | `cp -p L0_vintage_register.csv L0_vintage_register.backup_2026-09-14.csv` then `cmp`, `sha256sum` | 0 | 43,035 bytes, sha256 c6402930...5af3de on both |
| dry run | `python analysis/src/forecast_methods/L0_dolthub_v2/run.py` | 0 | 1,159 rows built, register untouched (168 lines before and after) |
| append | `python analysis/src/forecast_methods/L0_dolthub_v2/run.py --append` | 0 | "appended 1159 rows (0 already present, skipped)"; 161 -> 1,320 data rows |
| tests after | `py -3.13 -m pytest analysis/src/forecast_methods/L0/test_l0.py -q` | 0 | 0.7 s, 20 passed |
| hard rules + behaviour change | `python analysis/src/forecast_methods/L0_dolthub_v2/post_append_checks.py` | 0 | `all_hard_rules_hold: true` |
| T1 | `python analysis/src/forecast_methods/L0_dolthub_v2/t1_vendor_equivalence.py` | 0 | `T1_PASS: true` |
| scoreboard backup | `cp -p harness/scoreboard.csv L0_dolthub_v2/scoreboard_before.csv` | 0 | 277 lines |
| registry | `python analysis/src/forecast_methods/L0_dolthub_v2/register_street_dolthub.py` | 0 | "registered 50 rows -> l0-dolthub-v2__street_dolthub.csv", no validator warnings |
| scorer (venv) | `python analysis/src/forecast_methods/harness/score.py` | 0 | 280 scoreboard rows, but `pit_ks_p` NaN everywhere (no scipy in the venv) |
| scorer (final) | `py -3.13 analysis/src/forecast_methods/harness/score.py` | 0 | 280 rows, `pit_ks_p` populated; this is the scoreboard left on disk |
| NCLH | `python analysis/src/forecast_methods/L0_dolthub_v2/nclh_pull.py` (background, 60 s between pages) | see below | see below |

Rebuild order and the same commands: `analysis/src/forecast_methods/L0_dolthub_v2/README.md`.

## Results

### T0 provenance

`dolt_log` head (attempt 1, query 1): the five latest commits are all by `post-no-preference`, 2026-09-12 22:07 (earnings_calendar) and 2026-09-14 03:04:28 to 03:04:44 (rank_score, eps_estimate, sales_estimate, eps_history, each "<table> 2026-09-13 update"). Tail (query 2): "Initialize data repository" 2021-04-21 01:19:15, then "rank_score 2017-12-31 update" and "eps_estimate 2017-12-31 update" seconds later. So the repository was created on 21 Apr 2021 and the ABNB rows dated 2021-02-07 to 2021-04-18 were loaded in that initial backfill; their vintage is the Zacks page date the publisher stamped, which the git history cannot independently verify. Every row from late April 2021 onward is committed within about a day of its snapshot date.

Attempt 1 (8 requests, 10 s apart): for each snapshot the first commit in the 14 days after it was 2022-08-08 05:12:19 (`94kead12h59c6cef9i41kumjt94dkbp3`), 2024-02-12 03:31:55 (`p40c5m0fcke76i9r48aljbc1tb6r8l7h`), 2025-08-04 02:52:36 (`vekif410brrdr2veuqrl2u4dauh5b550`). All three AS OF queries returned zero rows. Under the pre-registered line that is not a PASS, and it is not evidence of back-editing either: those hashes are the day's first commit (the `rank_score` update), which predates that day's `sales_estimate` commit by about 15 s. Recorded as inconclusive; raw responses in `t0_provenance.json`.

Attempt 2 (4 requests): one `dolt_log` query filtered on `message like 'sales_estimate <snapshot> update%'` returned `j2s47ospjd1vbouii690hkifso0up7h3` (2022-08-08 05:12:37), `id6rhl4mfi8lmp791pp2uidgigcd5lb7` (2024-02-12 03:32:08), `54csabpuanoeoq9ng4k35dub2g8k8f0q` (2025-08-04 02:52:49). AS OF each hash, `where act_symbol = 'ABNB' and date = '<snapshot>'`:

| snapshot | commit | slot | period end | AS OF consensus / n / high / low / year_ago | current table | match |
|---|---|---|---|---|---|---|
| 2022-08-07 | j2s47osp | Current Quarter | 2022-09-30 | 2,840,000,000 / 11 / 2.90B / 2.80B / 2.24B | same | yes |
| 2022-08-07 | j2s47osp | Current Year | 2022-12-31 | 8,340,000,000 / 12 / 8.44B / 8.18B / 5.99B | same | yes |
| 2022-08-07 | j2s47osp | Next Quarter | 2022-12-31 | 1,900,000,000 / 11 / 1.95B / 1.77B / 1.53B | same | yes |
| 2022-08-07 | j2s47osp | Next Year | 2023-12-31 | 9,680,000,000 / 12 / 10.32B / 8.98B / 8.34B | same | yes |
| 2024-02-11 | id6rhl4m | Current Quarter | 2023-12-31 | 2,160,000,000 / 11 / 2.20B / 2.15B / 1.90B | same | yes |
| 2024-02-11 | id6rhl4m | Current Year | 2023-12-31 | 9,860,000,000 / 12 / 9.90B / 9.85B / 8.40B | same | yes |
| 2024-02-11 | id6rhl4m | Next Quarter | 2024-03-31 | 2,040,000,000 / 10 / 2.09B / 1.97B / 1.82B | same | yes |
| 2024-02-11 | id6rhl4m | Next Year | 2024-12-31 | 11,100,000,000 / 12 / 11.46B / 10.64B / 9.86B | same | yes |
| 2025-08-03 | 54csabpu | Current Quarter | 2025-06-30 | 3,040,000,000 / 12 / 3.09B / 3.01B / 2.75B | same | yes |
| 2025-08-03 | 54csabpu | Current Year | 2025-12-31 | 12,060,000,000 / 13 / 12.24B / 11.91B / 11.10B | same | yes |
| 2025-08-03 | 54csabpu | Next Quarter | 2025-09-30 | 4,040,000,000 / 12 / 4.13B / 3.95B / 3.73B | same | yes |
| 2025-08-03 | 54csabpu | Next Year | 2026-12-31 | 13,190,000,000 / 13 / 13.63B / 12.79B / 12.06B | same | yes |

12 of 12 cells equal, n = 3 snapshots. T0 PASS: rows written in 2022, 2024 and 2025 read back today unchanged. Total requests 12, all HTTP 200, no 403.

### Register

| | data rows |
|---|---|
| Before (backup, sha256 c6402930...) | 161 |
| Appended (1,160 ABNB rows minus 1 with no consensus) | 1,159 |
| After | 1,320 |

Periods covered by the new rows: 2020Q4 to 2026Q4 (25 quarters) and FY2020 to FY2027 (8 years). Each new row carries vendor + snapshot timestamp + the exact API query URL (offset 0 for the first 1,000 pulled rows, offset 1000 for the rest) + the sample path + a note with slot, high, low, year_ago and "provenance verified". Hard-rule invariants after the append (all from `post_append_checks.json`): prefix byte-identical true (43,035 of 870,641 bytes); duplicate ids 0; DoltHub vendor strings = {`DoltHub post-no-preference/earnings`}, none containing "zacks"; `pre_guide_street('2026Q3')` = LSEG 4610.0 @ 2026-08-06; `pit_consensus(revenue, 2026Q3, 2026-08-06, vendor=Zacks)` = None; `pit_consensus(revenue, 2026Q3, 2026-08-06, vendor=DoltHub)` = 4540.0, n=10, as_of 2026-08-02; `pit_consensus(revenue, 2026Q3, 2026-09-11, vendor=Zacks)` = 4740.0 (2026-09-04 vintage). Frozen tests 20 passed before, 20 passed after.

### T1 vendor equivalence (register value vs DoltHub snapshot strictly before the event date)

Pre-guide cells, n = 18 of 18 with a DoltHub value. DoltHub slot is always Next Quarter.

| register_id | guide date | guide mid | register vendor | register | DoltHub date | DoltHub (n) | diff % | sign reg / DH | agree |
|---|---|---|---|---|---|---|---|---|---|
| PG-2022Q1 | 2022-02-15 | 1,445 | CNBC unattributed | 1,240 | 2022-02-13 | 1,270 (7) | +2.42 | + / + | yes |
| PG-2022Q2 | 2022-05-03 | 2,080 | CNBC unattributed | 1,960 | 2022-05-01 | 1,980 (11) | +1.02 | + / + | yes |
| PG-2022Q3 | 2022-08-02 | 2,830 | StreetAccount | 2,770 | 2022-07-31 | 2,760 (11) | -0.36 | + / + | yes |
| PG-2022Q4 | 2022-11-01 | 1,840 | Refinitiv | 1,850 | 2022-10-30 | 1,900 (10) | +2.70 | - / - | yes |
| PG-2023Q1 | 2023-02-14 | 1,785 | Refinitiv | 1,690 | 2023-02-12 | 1,680 (8) | -0.59 | + / + | yes |
| PG-2023Q2 | 2023-05-09 | 2,400 | Refinitiv | 2,420 | 2023-05-07 | 2,430 (10) | +0.41 | - / - | yes |
| PG-2023Q3 | 2023-08-03 | 3,350 | Refinitiv | 3,220 | 2023-07-30 | 3,180 (10) | -1.24 | + / + | yes |
| PG-2023Q4 | 2023-11-01 | 2,150 | LSEG | 2,180 | 2023-10-29 | 2,170 (11) | -0.46 | - / - | yes |
| PG-2024Q1 | 2024-02-13 | 2,050 | LSEG | 2,030 | 2024-02-11 | 2,040 (10) | +0.49 | + / + | yes |
| PG-2024Q2 | 2024-05-08 | 2,710 | LSEG | 2,740 | 2024-05-05 | 2,760 (11) | +0.73 | - / - | yes |
| PG-2024Q4 | 2024-11-07 | 2,415 | LSEG | 2,420 | 2024-11-03 | 2,420 (12) | 0.00 | - / - | yes |
| PG-2025Q1 | 2025-02-13 | 2,250 | LSEG | 2,300 | 2025-02-09 | 2,290 (11) | -0.43 | - / - | yes |
| PG-2025Q2 | 2025-05-01 | 3,020 | LSEG | 3,040 | 2025-04-27 | 3,030 (12) | -0.33 | - / - | yes |
| PG-2025Q3 | 2025-08-06 | 4,060 | LSEG | 4,050 | 2025-08-03 | 4,040 (12) | -0.25 | + / + | yes |
| PG-2025Q4 | 2025-11-06 | 2,690 | LSEG | 2,670 | 2025-11-02 | 2,670 (11) | 0.00 | + / + | yes |
| PG-2026Q1 | 2026-02-12 | 2,610 | LSEG | 2,530 | 2026-02-08 | 2,520 (9) | -0.40 | + / + | yes |
| PG-2026Q2 | 2026-05-07 | 3,570 | LSEG | 3,460 | 2026-05-03 | 3,480 (10) | +0.58 | + / + | yes |
| PG-2026Q3 | 2026-08-06 | 4,730 | LSEG | 4,610 | 2026-08-02 | 4,540 (10) | -1.52 | + / + | yes |

Median |diff| 0.48 %, mean diff +0.15 %, max |diff| 2.70 % (2022Q4). Sign agreement 18 / 18. Pre-guide line PASS.

At-print cells, n = 23 of 23 with a DoltHub value (slot always Current Quarter):

| register_id | print date | register vendor | register | DoltHub date | DoltHub (n) | diff % |
|---|---|---|---|---|---|---|
| AP-2020Q4 | 2021-02-25 | Yahoo/unattributed | 739.7 | 2021-02-21 | 735.05 (11) | -0.63 |
| AP-2021Q1 | 2021-05-13 | Refinitiv | 714.4 | 2021-05-09 | 714.58 (12) | +0.03 |
| AP-2021Q2 | 2021-08-12 | Refinitiv | 1,260 | 2021-08-08 | 1,280 (10) | +1.59 |
| AP-2021Q3 | 2021-11-04 | Refinitiv | 2,050 | 2021-10-31 | 2,060 (11) | +0.49 |
| AP-2021Q4 | 2022-02-15 | Refinitiv | 1,460 | 2022-02-13 | 1,460 (11) | 0.00 |
| AP-2022Q1 | 2022-05-03 | Refinitiv | 1,450 | 2022-05-01 | 1,450 (12) | 0.00 |
| AP-2022Q2 | 2022-08-02 | Refinitiv | 2,110 | 2022-07-31 | 2,100 (12) | -0.47 |
| AP-2022Q3 | 2022-11-01 | Refinitiv | 2,800 | 2022-10-30 | 2,850 (11) | +1.79 |
| AP-2022Q4 | 2023-02-14 | Refinitiv | 1,860 | 2023-02-12 | 1,870 (11) | +0.54 |
| AP-2023Q1 | 2023-05-09 | Refinitiv | 1,790 | 2023-05-07 | 1,790 (11) | 0.00 |
| AP-2023Q2 | 2023-08-03 | Refinitiv | 2,420 | 2023-07-30 | 2,410 (11) | -0.41 |
| AP-2023Q3 | 2023-11-01 | LSEG | 3,370 | 2023-10-29 | 3,370 (12) | 0.00 |
| AP-2023Q4 | 2024-02-13 | LSEG | 2,170 | 2024-02-11 | 2,160 (11) | -0.46 |
| AP-2024Q1 | 2024-05-08 | LSEG | 2,060 | 2024-05-05 | 2,070 (11) | +0.49 |
| AP-2024Q2 | 2024-08-06 | LSEG | 2,740 | 2024-07-28 | 2,750 (11) | +0.36 |
| AP-2024Q3 | 2024-11-07 | LSEG | 3,720 | 2024-11-03 | 3,720 (12) | 0.00 |
| AP-2024Q4 | 2025-02-13 | LSEG | 2,420 | 2025-02-09 | 2,420 (12) | 0.00 |
| AP-2025Q1 | 2025-05-01 | LSEG | 2,260 | 2025-04-27 | 2,260 (12) | 0.00 |
| AP-2025Q2 | 2025-08-06 | LSEG | 3,040 | 2025-08-03 | 3,040 (12) | 0.00 |
| AP-2025Q3 | 2025-11-06 | LSEG | 4,080 | 2025-11-02 | 4,080 (11) | 0.00 |
| AP-2025Q4 | 2026-02-12 | LSEG | 2,720 | 2026-02-08 | 2,720 (9) | 0.00 |
| AP-2026Q1 | 2026-05-07 | LSEG | 2,620 | 2026-05-03 | 2,620 (9) | 0.00 |
| AP-2026Q2 | 2026-08-06 | LSEG | 3,580 | 2026-08-02 | 3,580 (10) | 0.00 |

Median |diff| 0.00 % (12 exact matches), mean +0.14 %, max |diff| 1.79 % (2022Q3). At-print line PASS. Note that the 2024Q2 cell uses the 2024-07-28 snapshot because the 2024-08-04 Sunday is absent from the table (a gap week; the panel is not present for every Sunday).

T1 PASS on both pre-registered lines. Full table: `data/processed/forecast_methods/L0_dolthub_v2/t1_vendor_equivalence.csv`.

Second-vendor fallback for the two holes (reported only; WP-A may use them as vintage-stamped Street values; the PG rows themselves are not edited):

| hole | guide date | guide mid | DoltHub snapshot | DoltHub value (n) | sign(guide mid - Street) |
|---|---|---|---|---|---|
| PG-2021Q4-revenue (no vintage) | 2021-11-04 | 1,435 | 2021-10-31 | 1,430 (10) | + (guide above Street by $5M) |
| PG-2024Q3-revenue (no vintage, pit_usable False, audit value 3,840) | 2024-08-06 | 3,700 | 2024-07-28 | 3,860 (11) | - (guide below Street by $160M) |

Lookup: `l0.pit_consensus("revenue", "2024Q3", "2024-08-06", vendor="DoltHub")`.

### Behaviour change of `pit_consensus(..., vendor=None)` (measured, not tested)

Selection logic re-implemented on both files exactly as in `l0.pit_consensus` (pit_usable, metric, period, vintage strictly before as_of, ties to larger n then vendor). Guide dates: 23 (every non-forecast calendar row with a `guide_date`, 2021-02-25 to 2026-08-06; the harness's own list has 20 guide events because the first three calls carried no next-quarter range). Print dates: 23 (rows with `print_date_basis == ledger`, 2021-02-25 to 2026-08-06).

| lookup | n | changed | None before, value after | both values, value changed | both values, unchanged | largest relative change |
|---|---|---|---|---|---|---|
| next quarter as of guide date | 23 | 23 | 23 | 0 | 0 | not defined (every old value was None) |
| printed quarter as of print date | 23 | 23 | 6 | 15 | 2 (vendor changed, value not) | +16.9 % (2022Q1 as of 2022-05-03: CNBC $1,240M stamped 2022-02-15 -> DoltHub $1,450M stamped 2022-05-01) |

Why every lookup changes: a guide-date lookup with a strict inequality can never see the register's own pre-guide row (its stamp equals the guide date), so before the append it returned None; a print-date lookup used to fall back to the previous quarter's print-morning quote (the PG row, three months old), and now gets the Sunday before the print. The +16.9 % is therefore a vintage-recency effect, not a vendor disagreement (on the same vintage the two vendors agree to 0.0 % median, see T1). Concretely for the hard-rule date: `pit_consensus("revenue","2026Q3","2026-08-06")` with no vendor now returns DoltHub 4540.0 @ 2026-08-02 where it returned None; with `role="pre_guide"` it still returns None on 2026-08-06 and LSEG 4610.0 on 2026-08-07 (frozen test `test_pit_consensus_is_strictly_before`). `pre_guide_street()` reads role, not vendor, and is unaffected. Full table: `pit_consensus_vendor_none_delta.csv`.

Also checked: the harness spine's `_forward_consensus()` looks for a column named `as_of` in the register, which does not exist (the register has `as_of_timestamp`), so it falls through to `04_current_consensus.csv`; `targets.csv` cannot change because of this append. `harness/run.py` was not run.

### Registry baseline `l0-dolthub-v2 / street_dolthub`

50 rows written (20 guide events x windows x two replays; 2026Q3 is LIVE). Validator raised nothing; both replays present; W1 covers 14 quarters, W2 10. `street_as_of` is the Sunday (or the 2024-07-28 gap-week) before each guide date, always 2 to 9 days before the vintage date, so the PIT rule holds by construction.

Scoreboard after `py -3.13 harness/score.py` (n on every row; LIVE excluded):

| object | window | replay | n | MAE | RMSE | bias | RMSE ratio to naive | cov (q10-q90) | survives both |
|---|---|---|---|---|---|---|---|---|---|
| street_dolthub | W1 | PIT | 14 | 92.3 | 107.8 | -69.7 | 1.146 | 0.857 | no |
| street_dolthub | W1 | full_sample | 14 | 92.3 | 107.8 | -69.7 | 1.146 | 0.786 | no |
| street_dolthub | W2 | PIT | 10 | 83.5 | 95.5 | -51.9 | 0.881 | 0.800 | no |
| street_dolthub | W2 | full_sample | 10 | 83.5 | 95.5 | -51.9 | 0.881 | 0.900 | no |
| baselines/street (for comparison) | W1 | PIT | 14 | 87.7 | 100.9 | -68.3 | 1.073 | 0.786 | no |
| baselines/street | W2 | PIT | 10 | 82.1 | 94.5 | -54.9 | 0.871 | 0.700 | no |

The DoltHub Street behaves like the press-quote Street: below the print by about $52M to $70M on average (the Street sits below the eventual print, as the guide does), beats naive on W2 only, so not a survivor under the two-window rule, same as `baselines/street`.

Scoreboard diff, pre-existing rows (276 before, 280 after, 4 new): with a numeric tolerance of 1e-9, every `n`, `mae`, `rmse`, `bias`, `mape_pct`, `rmse_naive`, `rmse_ratio_to_naive`, `beats_naive`, `crps`, `pinball_mean`, `pit_mean`, `pit_ks_p`, `cov_empirical`, `survives_both_windows` and `replays_present` value is unchanged. Two columns differ on exactly 8 rows, all `tracker-backlog` (`nights_yoy_next_q` and `revenue_yoy_next_q`, W1 and W2, both replays): `conformal_cov_empirical` (max change 0.081) and `conformal_mean_width` (max 1.06). An in-memory rescore of the registry with the new method excluded reproduces those 8 differences exactly, so they are not caused by this registration: the checked-in `scoreboard.csv` (commit a35b0a6, 11 Sep) was built from a tracker-backlog registry state that differs from the files now on disk. Flagged for WP-J below, not fixed here. (A first scorer run with the venv `python` wrote `pit_ks_p` as NaN on every row because the venv has no scipy; the scorer was re-run with `py -3.13`, which has scipy, and that scoreboard is the one on disk.)

### NCLH pull for WP-E1

Partial. `nclh_pull.py` paged `select * from sales_estimate where act_symbol='NCLH' order by date, period limit 500 offset <k>` with 60 s between calls. Offsets 0, 500 and 1000 returned 500 rows each (HTTP 200, `Success`); offset 1500 at 13:59:39 returned HTTP 200 wrapping `query error: http status: 403`, the rate limit the manifest warned about (this session had made 12 T0 requests plus 3 pages in the preceding 25 minutes, on top of the catalogue lane's ~40 earlier in the day). The script stopped there as pre-specified.

File: `data/processed/forecast_methods/L0_dolthub_v2/dolthub_sales_estimate_NCLH.csv`, 1,500 rows, 375 weekly snapshots, 2017-10-27 to 2025-02-02, four slots per snapshot, no duplicate (date, period) keys, no missing consensus, 16 gaps longer than a week (max 14 days). Missing: every snapshot after 2025-02-02 (about 85 Sundays, roughly 340 rows) which covers the 2025 and 2026 NCLH guides WP-E1 will want most. Pull log: `dolthub_sales_estimate_NCLH.pull_log.json`. Not appended to the register (ABNB-only). To finish: re-run the same query at offsets 1500 and 2000 after the rate limit clears (an hour was enough for the catalogue lane), or run `nclh_pull.py` with its start offset changed to 1500; the file is safe to overwrite since it is a plain pull, not a register.

## What failed or could not be done, and why

1. T0 attempt 1 returned zero AS OF rows for all three snapshots: the query took the first commit of the day, which is the `rank_score` commit that precedes the `sales_estimate` commit by seconds. Written up as inconclusive above; attempt 2 located commits by message and passed. Both JSON logs are kept.
2. The first three ABNB snapshots' vintages (2021-02-07 to 2021-04-18) predate the repository's creation on 2021-04-21 and were loaded in the initial backfill; their vintage stamp is the publisher's, not a git timestamp. They are appended (T0 tests immutability since commit, which they pass by construction), and the earliest T1 cell that touches them (AP-2020Q4, 2021-02-21 snapshot, diff -0.63 %) agrees with the press quote. The next agent should treat vintages before 2021-04-21 as vendor-stamped, not git-stamped.
3. The venv `python` has no pytest and no scipy; `py -3.13` was used for the frozen tests and the final scorer run. The repo instructions say `python`; the numbers do not depend on the interpreter (the venv scorer produced identical values except `pit_ks_p`).
4. The 8 tracker-backlog conformal cells in `scoreboard.csv` had already drifted from the registry before this run (see above). Not touched.
5. The registry method name deviates from the pre-registered filename (`l0-dolthub-v2` instead of `baselines-street-dolthub`) to follow the README's naming rule; nothing about the object changed.
6. My first scoreboard comparison reported 83 changed `mae` cells; that was a string comparison of floats in my own check, corrected to a numeric tolerance before any conclusion was drawn. Recorded so nobody re-derives the false alarm.

## Interpretation

The register now has a weekly point-in-time Street series for ABNB revenue back to February 2021, covering every guide date in both windows with no holes, from a source whose history was shown not to have been rewritten (three snapshots read back at their own commits). It is the same Street the register already held in press quotes: on the same vintage the two agree to a 0.0 % median at prints and 0.48 % at guides, and the direction of every guide surprise (guide mid above or below Street) is identical under both. That is what WP-A needs for its consensus(q+1) column at n = 14 / 10 with no holes, and what WP-B needs for FY revisions. Two things it is not. It is not an independent second panel: the 13 Sep 2026 rows equal the 11 Sep Zacks capture to the dollar and to the analyst (3Q26 4,740 n=7; 4Q26 3,200 n=10; FY26 14,100 n=8; FY27 15,740 n=13), so DoltHub and Zacks must not be counted twice in any dispersion measure, exactly as Yahoo and Alpha Vantage are not. And it is a thin panel (7 to 14 analysts against 35 to 44 for the LSEG family), which is why its 4Q26 mark sits $40M above the wide-panel vendors. The historical rows are usable internally on the same footing as the Zacks page captures WP-M already appends; quoting a historical number externally as Zacks is the WP-O decision. Nothing here touches a number on the kill list; the DoltHub 2 Aug 2026 value of $4,540M is a pre-guide vintage and is not the September Zacks $4,740M.

## Harness change requests

1. `spine._forward_consensus()` reads the L0 register expecting a column `as_of`; the register's column is `as_of_timestamp`, so the branch never fires and the fallback to `04_current_consensus.csv` is silent. Either rename the expectation or document that the register is not consumed by the spine. No behaviour changes today.
2. `pit_ks_p` silently becomes NaN when scipy is missing; the scorer could print a one-line warning so the next agent does not diff a NaN column against a populated one.
3. For WP-J: the checked-in scoreboard's tracker-backlog conformal cells do not reproduce from the registry on disk (8 cells); a rescore from a clean registry state, or a note from the tracker-backlog owner, would settle which is stale.

## RESUME

The next agent should (a) point WP-A's consensus(q+1) column at `l0.pit_consensus("revenue", q, guide_date, vendor="DoltHub")` for all 20 harness guide events (including the two former holes, 2021Q4 $1,430M and 2024Q3 $3,860M) and run the pre-registered T2 vendor swap from `INTEGRATION_PLAN.md` (same verdict under the press-quote Street and the DoltHub Street = survivor); (b) run WP-B's FY-revision leg off the `FY*` rows (period FY2021 to FY2027, weekly, `n_estimates` carried; an exactly-zero weekly revision is common and counts as a miss under B's pre-registration); (c) pull the rest of the DoltHub tables only if needed (EPS is not appended and should stay out unless its basis is reconciled to the register's adjusted EPS); (d) re-run `run.py --append` after a fresh sample pull to add new Sundays (idempotent, existing ids are skipped), and re-run `post_append_checks.py` and the frozen tests each time; (e) log the WP-O decision on external quotation before any historical DoltHub number reaches the memo; (f) NCLH: the file stops at 2025-02-02 because the API rate-limited the fourth page; re-pull offsets 1500 and 2000 (60 s apart, after the limit clears) so WP-E1 has the 2025 and 2026 guides, and only then build the NCLH guide hit-rate leg. Do not edit `L0/` or the register by hand; every path in `README.md` rebuilds this package with exit 0.
