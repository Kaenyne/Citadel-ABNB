# REFUTE A — mechanism

Agent `ref_a_mechanism` · 2026-09-12 · parent-managed branch · token usage unavailable.

## Verdict

**survived** on the original exact sentence. Independent reconstruction finds **0 eligible signals across 14 W1 and 10 W2 guide dates** because no admissible consensus record precedes the guide date. The strongest attack works against a mechanism interpretation: a consensus-availability mask, with no kernel at all, reproduces the result. This is a failed opportunity to test the economic mechanism, not an empirical finding about its strength. The package's sentence already confines itself to the supplied strict test, so that criticism does not contradict it.

## Preregistered adjudication

The original exact sentence is: **“The supplied Lane-1 data do not establish a pre-guide expectations edge: the strict point-in-time test has 0 eligible signals across 14 W1 and 10 W2 guide dates.”**

This is a refutation audit, not a new economic backtest. Before computing counts, the verdict rule is: `survived` only if independently reconstructed input eligibility confirms zero in both stated windows and none of the attacks contradicts the exact sentence; `refuted` if an admissible signal or a denominator error contradicts it; `partial` if only a weaker replacement sentence is supportable. No hit rate, power, or minimum detectable effect will be invented at n=0.

The mechanism test will replace the kernel by an arbitrary forecast and ask whether the same consensus-availability mask forces the same zero. Additional attacks will address same-day timing, seasonal/cushion alternatives, vendor dependence, executable-return fields, and the registry inventory. Same-day sensitivity is explicitly outside the supplied strict-before-date rule.

Only this new note will be written. Parent owns board, scorer, and git actions. No package code or derived output will be imported or inspected.

## Results — independent reconstruction

Dates are target-quarter windows: W1 is 2023Q1–2026Q2 and W2 is 2024Q1–2026Q2. For each target, the previous quarter's `AP-...-revenue` record in L0 supplies the print-day date. Every reconstructed event is cross-checked against the next calendar day's reaction date in the named earnings-reactions file. This verifies internal consistency of the two supplied inputs; it is not an independent corporate-calendar audit.

| Input or statistic | Extended sample, n=19 dates | W1, n=14 dates | W2, n=10 dates |
|---|---:|---:|---:|
| Admissible revenue consensus dated strictly before event | 0 | 0 | 0 |
| Maximum eligible signals for **any** forecast model | 0 | 0 | 0 |
| Pre-guide candidate has same-day date-only stamp | 17 | 13 | 9 |
| Pre-guide candidate has no date stamp | 2 | 1 | 1 |
| Attributed, usable consensus under same-day-inclusive sensitivity | 15 | 13 | 9 |

The last row is a cutoff sensitivity, not a replacement PIT test. The extended sample additionally excludes two vendor-unattributed same-day records. W2 is contained in W1, so the historical claim concerns 14 distinct events, not 24 independent events. Hit rates, effect sizes, Wilson intervals, numerical power and a minimum detectable effect are **inestimable at n=0**.

The complete W1 audit below has n=1 event per row; W2 starts at 2024Q1. Values are historical candidate records excluded under the strict rule, not current Street estimates. Each register ID is `PG-<target>-revenue`.

| Target (n=1 each) | Reconstructed guide date | L0 vendor | L0 as-of | Candidate revenue, USD m | Strict eligible |
|---|---|---|---|---:|---:|
| 2023Q1 | 2023-02-14 | Refinitiv | 2023-02-14 | 1,690 | 0 |
| 2023Q2 | 2023-05-09 | Refinitiv | 2023-05-09 | 2,420 | 0 |
| 2023Q3 | 2023-08-03 | Refinitiv | 2023-08-03 | 3,220 | 0 |
| 2023Q4 | 2023-11-01 | LSEG | 2023-11-01 | 2,180 | 0 |
| 2024Q1 | 2024-02-13 | LSEG | 2024-02-13 | 2,030 | 0 |
| 2024Q2 | 2024-05-08 | LSEG | 2024-05-08 | 2,740 | 0 |
| 2024Q3 | 2024-08-06 | LSEG | missing | 3,840 | 0 |
| 2024Q4 | 2024-11-07 | LSEG | 2024-11-07 | 2,420 | 0 |
| 2025Q1 | 2025-02-13 | LSEG | 2025-02-13 | 2,300 | 0 |
| 2025Q2 | 2025-05-01 | LSEG | 2025-05-01 | 3,040 | 0 |
| 2025Q3 | 2025-08-06 | LSEG | 2025-08-06 | 4,050 | 0 |
| 2025Q4 | 2025-11-06 | LSEG | 2025-11-06 | 2,670 | 0 |
| 2026Q1 | 2026-02-12 | LSEG | 2026-02-12 | 2,530 | 0 |
| 2026Q2 | 2026-05-07 | LSEG | 2026-05-07 | 3,460 | 0 |

## Numbered refutation attempts

1. **Count or window error.** Claim → zero across exactly 14/10 dates. Attack → enumerate quarterly targets independently, search **all** same-period revenue records in L0 rather than only `pre_guide` rows, and require usable value, attributed vendor and timestamp before the reconstructed event. Result → **survived**: 14/10 denominators and 0/0 eligible consensus dates reproduce. A missing denominator prevents a consensus-relative signal regardless of model internals. No claim of zero numerical signal is made.

2. **Timing convention creates the failure.** Claim → the strict test establishes no pre-guide expectations edge. Attack → the L0 record notes explicitly describe many same-day observations as morning-of-print consensus; the frozen harness README also accepts same-day Street timestamps and describes morning information preceding the after-close guide. Recompute with `as_of <= event_date`. Result → **partially** effective criticism: usable attributed consensus becomes 13/14 W1 and 9/10 W2. Calling this a universal absence of pre-release Street data would overstate the evidence. However, the original exact sentence expressly says the **strict** test, and this assignment demands strictly-before-date timestamps. It survives. Accepting date-only same-day records would change that rule; it also would not itself make the simultaneously released GBV input a pre-release observation.

3. **The kernel explains none of the observed count.** Claim → perhaps the result conveys something about the kernel's mechanism. Attack → construct the minimum alternative `M_d = 1` for all dates and define eligibility `E_d = I(admissible current consensus) × I(available forecast)`. The independently computed first factor is zero on every date. Therefore the constant model, a seasonal model, a cushion model and even a hypothetical perfect forecast have exactly the same 0/14 and 0/10 eligible counts. No model needs to be fitted. Result → **survived** on the exact no-established-edge sentence; **refuted** as an inference that this result tests or rejects the kernel mechanism. Missingness alone explains every central number. The package appropriately states that the economic effect need not be zero.

4. **A cushion-only rule can manufacture a directional signal.** Claim → a consensus-base comparison might isolate value added by the kernel. Attack → for consensus `C` and a positive trailing cushion `c`, the note's comparison rule `G = C/(1+c)` produces `100 × (G/C−1) = −100c/(1+c)`. Its sign is negative by construction; a negative signal does not establish information from booked GBV. Seasonality can likewise explain guide levels without identifying a consensus-relative edge. Result → **survived** on the exact sentence because no comparative performance is claimed or estimable at n=0. The proposed design still cannot attribute predictive value to the kernel without evaluable comparisons. This is a symbolic mechanism check, with no fitted coefficient or historical cushion estimate.

5. **Vendor choice manufactures the live threshold crossing.** Claim → a live scenario might rescue evidence for a kernel edge. Attack → hold the note's conditional guide fixed at USD 3,158.228m and independently recompute the percentage gaps from the three designated L0 records. Result → **survived** on the historical no-established-edge sentence; the live threshold is plainly vendor-dependent. One live event and three alternative denominators cannot replace the absent historical test. The signal changes from +0.0072% to −1.3054% solely through vendor selection. These are arithmetic checks of a supplied conditional forecast, not independent validation of that forecast.

   | Live Q4 scenario (n=1 event each) | Vendor timestamp | Consensus, USD m | Recomputed gap | Absolute gap >1pp |
   |---|---|---:|---:|---|
   | Alpha Vantage aggregated sell-side | 2026-09-11 | 3,158 | +0.007220% | no |
   | S&P Global Market Intelligence via StockAnalysis | 2026-09-10 | 3,160 | −0.056076% | no |
   | Zacks | 2026-09-11 | 3,200 | −1.305375% | yes |

6. **The return filter might be the only reason the backtest is empty.** Claim → zero eligible signals could conceal a valid predictive sample excluded merely for execution details. Attack → compute consensus eligibility before reading return values, then audit the reaction header. Result → **survived**: the signal set is already empty before returns; the 23-row reaction file independently contains zero `open_*` fields. Restoring executable prices alone cannot repair missing current consensus or make the kernel input pre-release. I do not infer the precise construction of the existing percentage-return columns from their names alone; their lack of an explicitly documented open entry is sufficient for refusing them under the stated rule.

7. **Unreported registrations could contradict the note.** Claim → no A forecasts were registered. Attack → inspect shared-registry filenames for all `alpha-a` objects, also normalizing an underscore method spelling, without inspecting another package's contents. Result → **survived**: zero matching registry files. The separate broad `rg` filename search also returned no matches. This verifies the current on-disk inventory, not any prior registration history. The unregistered package template and derived output tables were deliberately not read.

## What ran

The preregistration section was written before the computational audit. The following exact PowerShell command ran from the repository root. It uses the project `.venv` interpreter through `python` and writes nothing. Exit code **0**; measured Python calculation time **0.003923 seconds**; tool-reported wall time **0.5497061 seconds**. No package tests, package code, scorer or registration were run. New fitted parameters: **0**. Token usage is unavailable and is not estimated.

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv/Scripts') + [IO.Path]::PathSeparator + $env:PATH
@'
import csv, datetime as dt, hashlib, io, json, pathlib, sys, time
start = time.perf_counter()
root = pathlib.Path.cwd()
reg = root / 'data/processed/forecast_methods/L0/L0_vintage_register.csv'
raw = reg.read_bytes()
rows = list(csv.DictReader(line for line in raw.decode('utf-8-sig').splitlines() if not line.startswith('#')))
reactions_path = root / 'data/processed/abnb_earnings_reactions.csv'
rr = list(csv.DictReader(io.StringIO(reactions_path.read_text(encoding='utf-8-sig'))))
reactions = {r['quarter']: r for r in rr}
by_id = {r['register_id']: r for r in rows}
def prev(q):
    y, n = int(q[:4]), int(q[-1])
    return f'{y}Q{n-1}' if n > 1 else f'{y-1}Q4'
def truth(x):
    return x.strip().lower() == 'true'
def acceptable(r):
    return truth(r['pit_usable']) and truth(r['vendor_attributed']) and bool(r['vendor'].strip()) and bool(r['value'])
cells = []
for q in [f'{y}Q{k}' for y in range(2021, 2027) for k in range(1, 5) if '2021Q4' <= f'{y}Q{k}' <= '2026Q2']:
    origin = by_id[f'AP-{prev(q)}-revenue']['as_of_timestamp']
    d = dt.date.fromisoformat(origin)
    assert (dt.date.fromisoformat(reactions[prev(q)]['reaction_date']) - d).days == 1
    all_q = [r for r in rows if r['metric'] == 'revenue' and r['period'] == q]
    strict = [r for r in all_q if acceptable(r) and r['as_of_timestamp'] and dt.date.fromisoformat(r['as_of_timestamp'][:10]) < d]
    relaxed = [r for r in all_q if acceptable(r) and r['as_of_timestamp'] and dt.date.fromisoformat(r['as_of_timestamp'][:10]) <= d]
    pg = by_id[f'PG-{q}-revenue']
    cells.append({'quarter':q,'guide_date':origin,'vendor':pg['vendor'],'as_of':pg['as_of_timestamp'],'pre_guide_value_musd':pg['value'],'strict_n':len(strict),'same_day_inclusive_n':len(relaxed),'pg_id':pg['register_id']})
for name, lo in [('EXTENSION','2021Q4'),('W1','2023Q1'),('W2','2024Q1')]:
    w = [x for x in cells if x['quarter'] >= lo]
    print(json.dumps({'window':name,'dates':len(w),'strict_consensus_dates':sum(x['strict_n']>0 for x in w),'same_day_inclusive_consensus_dates':sum(x['same_day_inclusive_n']>0 for x in w),'same_day_pg_stamps':sum(x['as_of']==x['guide_date'] for x in w),'missing_pg_stamps':sum(not x['as_of'] for x in w),'max_eligible_any_model':sum(x['strict_n']>0 for x in w)}))
print('PER_DATE_AUDIT')
print(json.dumps(cells, indent=2))
print('REGISTRY', json.dumps([str(p.relative_to(root)) for p in (root/'data/processed/forecast_methods/registry').glob('*.csv') if p.name.split('__',1)[0].replace('_','-') == 'alpha-a']))
print('REACTIONS', json.dumps({'rows':len(rr),'columns':list(rr[0]),'open_fields':[x for x in rr[0] if x.startswith('open_')]}))
print('LIVE_VENDOR_SENSITIVITY')
for key in ['CU-2026Q4-revenue-AlphaVantage','CU-2026Q4-revenue-SPGlobal-20260910','CU-2026Q4-revenue-Zacks-20260911']:
    r = by_id[key]
    signal = (3158.228 / float(r['value']) - 1) * 100
    print(json.dumps({'id':key,'vendor':r['vendor'],'as_of':r['as_of_timestamp'],'value_musd':float(r['value']),'conditional_signal_pct':signal,'threshold_abs_gt_1':abs(signal)>1}))
print('SHA256', hashlib.sha256(raw).hexdigest(), hashlib.sha256(reactions_path.read_bytes()).hexdigest())
print('PYTHON_PREFIX', sys.prefix)
print('RUNTIME_SECONDS', round(time.perf_counter()-start,6))
'@ | python -
```

The registry filename search was `rg --files "data/processed/forecast_methods/registry" -g "*alpha*a*"`; exit **1** means no matching filenames, with no error output; wall time **0.5296404 seconds**.

Input SHA-256 receipts:

- `L0_vintage_register.csv`: `c6402930b7e785a5c24829c6e124023525d3a4be64f33f41ad0ef394cb5af3de`.
- `abnb_earnings_reactions.csv`: `45f368e6f10150a481929f199fc1d430a52d6f40e9dd6f5485b661ffa6448b87`.

## What could not be established

The named raw inputs do not allow this lens to independently rebuild the kernel's lambda, its claimed first-lag release timing, a guide-level seasonal alternative, or the post-letter diagnostic. Those would require reading other package code or inputs beyond this assignment. None is needed for the strict zero upper bound: admissible current consensus alone is absent. I have not silently treated the package's 11 post-letter diagnostic observations as independently verified. Numerical power at n=0 and causal mechanism attribution are unavailable. The source metadata supports a meaningful same-day timing objection; exact intraday provenance was not fetched because the task restricts the source scope.

## Interpretation

Keep the original sentence unchanged if used. It survives as a statement about the supplied strict test. It must not be promoted into “the kernel has no expectations edge,” “the kernel fails against seasonality,” or “no historical pre-release consensus exists.” The minimum explanation of the reported zero is an empty information-eligibility mask, and vendor selection alone explains the live threshold difference. These are material limits on what the package can contribute to the pitch's mechanism argument.

Final verdict on the original exact sentence: **survived**.

## RESUME

Parent should retain this refutation note and its zero-count finding, and use the exact verdict in the majority tally. To investigate the economic mechanism later, preregister a new version with a clearly timed pre-release forecast origin, verifiable pre-release consensus, an independently available GBV forecast and executable entry prices; then compare the kernel with seasonality and cushion-only rules on the same eligible dates. Do not reinterpret the present zero as evidence for or against the economic mechanism, and do not relax its cutoff retrospectively. Parent owns all board, scorer and git actions; this agent changed only this new note.
