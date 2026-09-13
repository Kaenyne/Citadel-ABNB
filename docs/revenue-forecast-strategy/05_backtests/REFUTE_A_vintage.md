# REFUTE A — vintage

Agent `ref_a_vintage` · 2026-09-12 · parent-owned branch `codex/lane1-full` · read-only independent audit.

## Verdict

**survived.** The original exact sentence survives independent enumeration: there are **0 eligible consensus observations and therefore 0 eligible joint signals across 14 W1 and 10 W2 guide dates** under the package's explicit strictly-before-calendar-date cutoff. The strongest attack identifies a substantive distinction: 13 W1 / 9 W2 attributed consensus records have same-day stamps and describe morning publication, which the harness permits. They fail this package's stricter rule. Thus the zero is a result of the specified information set; it does not establish that historical pre-event consensus never existed or that the economic edge is zero. The claim already confines itself to the strict test, so this caveat does not require weakening its sentence.

## Pre-registered audit design

Original exact claim: “The supplied Lane-1 data do not establish a pre-guide expectations edge: the strict point-in-time test has 0 eligible signals across 14 W1 and 10 W2 guide dates.”

Before calculation, attempt to defeat the zero count by searching every L0 revenue record for the correct target period, an identified vendor, a usable value, and an `as_of_timestamp` strictly before the guide date. Derive dates independently from L0's prior-quarter at-print revenue records, cross-check against the supplied reaction dates, and enumerate both W1 (2023Q1–2026Q2) and W2 (2024Q1–2026Q2). Separately relax same-day eligibility, attribution, and missing-time exclusions as deliberately invalid attacks. Do not import package code or read its derived outputs. Inventory only package-A registry filenames. A sufficient proof of zero eligible consensus observations also proves zero joint signals, without reproducing the kernel coefficient. No forecasts will be registered.

The refuter has no statistical pass line. Final verdict on the original exact sentence must be `survived`, `refuted`, or `partial`. At zero valid observations, empirical power, effect size, confidence intervals, and return performance are inestimable.

## Results

These are independent PIT-eligibility counts, not full-sample model performance. The input register contains 161 rows, including 66 revenue rows. For every audited target there are exactly two same-period revenue candidates: its pre-guide record and its later at-print record. Searching all roles, rather than only `pre_guide`, finds no strictly earlier candidate.

| Window | n guide dates | Strictly earlier attributed consensus dates | Attributed usable same-day dates | Pre-guide records missing timestamps | Later same-period attributed candidates |
|---|---:|---:|---:|---:|---:|
| W1: 2023Q1–2026Q2 | 14 | 0 | 13 | 1 | 14 |
| W2: 2024Q1–2026Q2 | 10 | 0 | 9 | 1 | 10 |
| Extended: 2021Q4–2026Q2 | 19 | 0 | 15 | 2 | 19 |

There are 17 same-day pre-guide stamps in the extended sample, including two unattributed CNBC values; three extended pre-guide rows are unattributed in total, including the missing 2021Q4 record. W2 is nested within W1, not an independent ten-event replication.

Guide dates below were rebuilt from the prior-quarter `at_print` revenue record, without importing the package or reading its outputs. Every date is exactly one calendar day before the prior quarter's corresponding reaction date: 14/14 W1 and 10/10 W2. Register IDs follow `PG-<target>-revenue`. Values are audit-only USD millions, never replacement eligible observations.

| Target | n | Guide date | Vendor | Pre-guide as_of | Consensus USD m | Strict eligible |
|---|---:|---|---|---|---:|---:|
| 2023Q1 | 1 | 2023-02-14 | Refinitiv | 2023-02-14 | 1,690 | 0 |
| 2023Q2 | 1 | 2023-05-09 | Refinitiv | 2023-05-09 | 2,420 | 0 |
| 2023Q3 | 1 | 2023-08-03 | Refinitiv | 2023-08-03 | 3,220 | 0 |
| 2023Q4 | 1 | 2023-11-01 | LSEG | 2023-11-01 | 2,180 | 0 |
| 2024Q1 | 1 | 2024-02-13 | LSEG | 2024-02-13 | 2,030 | 0 |
| 2024Q2 | 1 | 2024-05-08 | LSEG | 2024-05-08 | 2,740 | 0 |
| 2024Q3 | 1 | 2024-08-06 | LSEG | missing; PIT false | 3,840 | 0 |
| 2024Q4 | 1 | 2024-11-07 | LSEG | 2024-11-07 | 2,420 | 0 |
| 2025Q1 | 1 | 2025-02-13 | LSEG | 2025-02-13 | 2,300 | 0 |
| 2025Q2 | 1 | 2025-05-01 | LSEG | 2025-05-01 | 3,040 | 0 |
| 2025Q3 | 1 | 2025-08-06 | LSEG | 2025-08-06 | 4,050 | 0 |
| 2025Q4 | 1 | 2025-11-06 | LSEG | 2025-11-06 | 2,670 | 0 |
| 2026Q1 | 1 | 2026-02-12 | LSEG | 2026-02-12 | 2,530 | 0 |
| 2026Q2 | 1 | 2026-05-07 | LSEG | 2026-05-07 | 3,460 | 0 |

## Numbered refutation attempts

1. **Claim → no eligible earlier consensus. Attack → remove any package-specific role filter and search all 66 L0 revenue rows for each correct target period. Result → survived.** All 14 W1 and 10 W2 target periods lack any usable, attributed, strictly earlier revenue observation. This is a sufficient independent proof of zero joint signals regardless of lambda or the signal threshold.

2. **Claim → strict zero can be called a pre-guide data limitation. Attack → use the register's morning-publication notes and the harness's same-day allowance. Result → survived on the exact sentence; the broader suggestion that no historical pre-event consensus exists is refuted.** Relaxing `< date` to `<= date` supplies 13/14 W1 and 9/10 W2 consensus dates. The harness README explicitly describes its Street baseline as morning-of-print and allows `street_as_of <= vintage_date`. However, A's written preregistration expressly rejects date-only same-day stamps. The corrected sensitivity count is 13/14 and 9/10 **consensus dates**, not eligible complete kernel signals or successful forecasts. Calling these 13/9 complete signals would require another unverified change to the GBV information set.

3. **Claim → no consensus splice generates a valid signal. Attack → substitute the same target's at-print consensus for its pre-guide consensus. Result → survived.** This provides an attributed value in all 14 W1 / 10 W2 periods, but every such timestamp is later than the reconstructed guide date. Renaming a later observation or joining it solely by target period does not change its availability. Using the prior quarter's earlier consensus would instead change the target period and fail the period match.

4. **Claim → one missing timestamp cannot be repaired from a vendor label. Attack → reinstate the LSEG 2024Q3 record or infer its date from its `PG` ID. Result → survived.** This single row is explicitly `pit_usable=False`, lacks `as_of_timestamp`, and its own note says that contemporaneous next-quarter consensus was not found. Attribution is present; timing is not. Imputation could raise relaxed same-day coverage from 13/14 to 14/14 and 9/10 to 10/10, but supplies no evidence for the imputed date and still does not make it strictly earlier.

5. **Claim → 14/10 are the correct denominators. Attack → find an off-by-one target/origin shift, omit a failing period, or count the extended history as W1. Result → survived.** Inclusive target ranges independently yield 14 and 10. All reconstructed origins agree with the reaction-date cross-check. The five older candidates increase the extended denominator to 19 and add no strict consensus observation. No date is omitted because it has a missing vendor or timestamp.

6. **Claim → current vendor snapshots cannot rescue the historical sample. Attack → splice one of the September 2026 Q4 anchors into a historical period or multiply evidence by counting duplicated vendor vintages. Result → survived.** The exact Q4 live entries include Alpha Vantage, 2026-09-11, USD 3,158m (n=1 register row); S&P Global Market Intelligence via StockAnalysis, 2026-09-10, USD 3,160m (n=1); Zacks, 2026-09-11, USD 3,200m (n=1), plus its 2026-09-04 predecessor (n=1); and Yahoo Finance, 2026-09-11, USD 3,160m (n=1). All have target 2026Q4 outside W1/W2 and timestamps later than every audited origin. The package's three stated live anchors match their L0 vendors and dates. This audit does not validate the live kernel output or treat vendors as independent trials.

7. **Claim → there is no registered or executable evidence that contradicts the empty test. Attack → inventory A registry objects and inspect return-field names. Result → survived within the permitted read scope.** There are no `alpha-a` / `alpha_a` package objects among 69 registry CSV filenames. There are zero `open_*` columns among the 11 fields in `abnb_earnings_reactions.csv`. The date cross-check uses that file only as a chronology check; no close-based field is relabelled executable. The filename inventory verifies absence of A's designated registrations; other packages' file contents were not searched for mislabelled A rows because that would exceed the assignment.

## What ran

The preregistered design was saved before the independent count. Commands ran from the repository root. The numerical audit below exited **0**, with **0.620581 seconds** shell-tool wall time and **0.012027 seconds** measured Python audit time. Python resolved to the repository `.venv`. Token usage and total session elapsed time are unavailable and are not estimated. Parameter count: **0 fitted parameters**; the audit uses fixed eligibility rules and counts.

Exact independent calculation command:

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + ';' + $env:PATH
@'
import csv, datetime as dt, hashlib, json, pathlib, sys, time
start = time.perf_counter()
root = pathlib.Path.cwd()
p = root / 'data/processed/forecast_methods/L0/L0_vintage_register.csv'
with p.open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(line for line in f if not line.startswith('#')))
rp = root / 'data/processed/abnb_earnings_reactions.csv'
with rp.open(encoding='utf-8-sig', newline='') as f:
    reaction_reader = csv.DictReader(f)
    fields = reaction_reader.fieldnames
    reactions = {r['quarter']: r['reaction_date'] for r in reaction_reader}
def previous(q):
    y, k = int(q[:4]), int(q[-1])
    return f'{y}Q{k-1}' if k > 1 else f'{y-1}Q4'
def timestamp(value):
    if not value:
        return None
    return dt.datetime.fromisoformat(value.replace('Z','+00:00'))
def usable(r):
    return r['pit_usable'].lower() == 'true' and r['vendor_attributed'].lower() == 'true' and bool(r['vendor'].strip()) and bool(r['value'])
periods = [f'{y}Q{k}' for y in range(2021,2027) for k in range(1,5) if '2021Q4' <= f'{y}Q{k}' <= '2026Q2']
audit = []
for q in periods:
    ap = [r for r in rows if r['period'] == previous(q) and r['metric']=='revenue' and r['role']=='at_print']
    assert len(ap)==1, (q,ap)
    date = timestamp(ap[0]['as_of_timestamp'])
    assert date is not None
    candidates = [r for r in rows if r['period']==q and r['metric']=='revenue']
    pg = [r for r in candidates if r['role']=='pre_guide']
    assert len(pg)==1, (q,pg)
    pg = pg[0]
    strict = [r for r in candidates if usable(r) and timestamp(r['as_of_timestamp']) is not None and timestamp(r['as_of_timestamp']) < date]
    same = [r for r in candidates if usable(r) and timestamp(r['as_of_timestamp']) is not None and timestamp(r['as_of_timestamp']) == date]
    future = [r for r in candidates if usable(r) and timestamp(r['as_of_timestamp']) is not None and timestamp(r['as_of_timestamp']) > date]
    next_reaction = dt.date.fromisoformat(reactions[previous(q)])
    audit.append(dict(target=q, guide_date=date.date().isoformat(), n=1, candidates=len(candidates), pg_vendor=pg['vendor'] or None, pg_value=pg['value'] or None, pg_as_of=pg['as_of_timestamp'] or None, pg_usable=pg['pit_usable'], pg_attributed=pg['vendor_attributed'], pg_intraday_wording='morning' in pg['note'].lower(), strict_ids=[r['register_id'] for r in strict], same_day_ids=[r['register_id'] for r in same], future_ids=[r['register_id'] for r in future], reaction_day_lag=(next_reaction-date.date()).days))
print('PYTHON', sys.executable)
print('L0_rows',len(rows),'revenue_rows',sum(r['metric']=='revenue' for r in rows))
print('AUDIT',json.dumps(audit,indent=2))
for window, lower in [('W1','2023Q1'),('W2','2024Q1'),('extension','2021Q4')]:
    a = [r for r in audit if r['target']>=lower]
    print('SUMMARY',json.dumps(dict(window=window,n_dates=len(a),n_strict_consensus_dates=sum(bool(r['strict_ids']) for r in a),n_same_day_attributed_dates=sum(bool(r['same_day_ids']) for r in a),n_missing_pg_timestamp=sum(r['pg_as_of'] is None for r in a),n_unattributed_pg=sum(r['pg_attributed'].lower()!='true' for r in a),n_pg_morning_notes=sum(r['pg_intraday_wording'] for r in a),n_later_attributed_dates=sum(bool(r['future_ids']) for r in a),n_reaction_day_lag_1=sum(r['reaction_day_lag']==1 for r in a))))
registry = sorted((root/'data/processed/forecast_methods/registry').glob('*.csv'))
a_registry = [p.name for p in registry if p.name.lower().startswith(('alpha-a__','alpha_a__','alpha-a-','alpha_a_'))]
print('REGISTRY',json.dumps(dict(total_csv_files=len(registry),a_files=a_registry)))
print('REACTION_FIELDS',json.dumps(fields),'OPEN_FIELDS',json.dumps([x for x in fields if x.startswith('open_')]))
print('LIVE_Q4_REVENUE',json.dumps([{k:r[k] for k in ['register_id','vendor','value','as_of_timestamp','pit_usable','vendor_attributed']} for r in rows if r['metric']=='revenue' and r['period']=='2026Q4'],indent=2))
for fp in [p,rp]:
    print('SHA256',fp.relative_to(root).as_posix(),hashlib.sha256(fp.read_bytes()).hexdigest())
print('AUDIT_SECONDS',round(time.perf_counter()-start,6))
'@ | python -
```

Registry inventory command: `rg --files 'data/processed/forecast_methods/registry'` (exit 0). Preliminary reads used `Get-Content -LiteralPath` for the assignment, package note, harness README, allowed cheatsheet, L0 register and reactions file. No package code or derived outputs were read. The repository-required AGENT_BRIEF and WORKBOARD startup reads preceded the more restrictive assignment. Parent retains all board, scorer and git actions; this audit created only this note.

Input SHA-256 receipts:

```text
data/processed/forecast_methods/L0/L0_vintage_register.csv
c6402930b7e785a5c24829c6e124023525d3a4be64f33f41ad0ef394cb5af3de
data/processed/abnb_earnings_reactions.csv
45f368e6f10150a481929f199fc1d430a52d6f40e9dd6f5485b661ffa6448b87
```

## What failed or could not be done

No attempted splice passed the stated target/date/vendor checks. Kernel coefficients, the claimed 11 post-letter diagnostic points, and same-letter GBV release timing were not independently recomputed: the permitted inputs do not include the underlying GBV panel or package code, and none is needed to prove the joint sample is empty once its necessary consensus component is empty. This is not validation of every ancillary sentence in A's note. No source URLs were opened, no prices fetched, no harness modification requested, and no forecast registered. Numerical power is inestimable at n=0.

## Interpretation

Retain the original exact sentence. Its count is reproducible, and it correctly refrains from treating missing evidence as evidence of no economic effect. Keep the explicit word **strict** and preserve the package's definition as a prior-calendar-date information set. The harness's morning-of-event convention answers a different timing question and would support more consensus observations, but this audit supplies no complete signal-performance result under that alternative design.

## RESUME

Parent should count this as `survived` on A's original exact sentence, retain the 13/9 same-day-consensus sensitivity caveat beside the 0/0 strict result, and perform the assigned board, scorer and git actions. A future package can preregister an event-time cutoff, verify public source timing, and supply a genuinely pre-guide GBV estimate plus executable returns. Do not turn the relaxed consensus count into eligible kernel signals, alter historical timestamps, or infer empirical power from this empty sample.
