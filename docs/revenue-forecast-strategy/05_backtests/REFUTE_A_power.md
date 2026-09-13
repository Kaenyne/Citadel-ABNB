# REFUTE A — power lens

Agent: Codex ref_a_power · 2026-09-12 · branch `codex/lane1-full`.

## Preregistered refutation protocol

Recorded before the independent eligibility calculation. The assignment has no statistical pass line: its required outcome is a refutation verdict. Judge the original exact sentence, **“The supplied Lane-1 data do not establish a pre-guide expectations edge: the strict point-in-time test has 0 eligible signals across 14 W1 and 10 W2 guide dates.”** Find an admissible nonempty sample or a different denominator to refute the count; distinguish absent observations from evidence of a zero effect. Recompute eligibility from the named L0 raw input, not package code or package-derived outputs. Count declared specifications, thresholds, windows, and response horizons from the note. Report Wilson/bootstrap intervals and detectable effect as unavailable if the actual performance sample is empty; never substitute the number of inspected dates for the number of evaluated signals. Inspect only allowed inputs and registry filenames. At least five numbered attacks and one final verdict exactly `survived`, `refuted`, or `partial` follow.

## Verdict

**survived.** The original exact sentence withstands the power audit. Independently scanning the supplied L0 register produces zero strictly earlier, attributed, usable revenue-consensus observations at all 14 W1 and 10 W2 origins. An eligible consensus-relative signal requires one of those observations, so its count is necessarily zero without inspecting or re-running the kernel. The strongest attack establishes that the empty sample is substantially a consequence of the specified date cutoff: changing `< guide date` to `<= guide date` admits 13 W1 and nine W2 consensus candidates. Those are not validated complete signals, and that change is not the strict test named in the original sentence. The result cannot reject an economic edge or estimate its size.

## Independent results

This is a deterministic eligibility audit of PIT inputs, not a fitted full-sample performance backtest. Target-quarter ranges were independently enumerated. For target quarter q, the guide-day date was taken from the L0 `at_print` record for q−1 and checked against the q−1 event's reaction date in the separately supplied reactions file. Every reaction date was exactly one day later. No date was inferred by subtracting an arbitrary trading-day offset, and no package-derived calendar was read. All usable attributed revenue rows for q were considered, regardless of role, so a differently named eligible vintage could have refuted the zero count.

| Window | Inspected dates n | Same-day pre-guide stamps n | Missing stamps n | Strict consensus dates n | Eligible signal n, forced by missing consensus | Date-inclusive consensus candidates n |
|---|---:|---:|---:|---:|---:|---:|
| W1, 2023Q1–2026Q2 | 14 | 13 | 1 | 0 | 0 | 13 |
| W2, 2024Q1–2026Q2 | 10 | 9 | 1 | 0 | 0 | 9 |
| Older extension plus W1, 2021Q4–2026Q2 | 19 | 17 | 2 | 0 | 0 | 15 |

The extended date-inclusive count is 15 rather than 17 because the 2022Q1 and 2022Q2 records are not vendor-attributed. W2 is contained in W1: there are 14 unique dates across the two primary windows, not 24 independent observations. The extension contains the primary windows and adds five dates.

| Target quarter | Guide date checked | L0 pre-guide vendor | L0 pre-guide timestamp | Date n | Strict eligible consensus n |
|---|---|---|---|---:|---:|
| 2021Q4 | 2021-11-04 | missing | missing | 1 | 0 |
| 2022Q1 | 2022-02-15 | CNBC unattributed | 2022-02-15 | 1 | 0 |
| 2022Q2 | 2022-05-03 | CNBC unattributed | 2022-05-03 | 1 | 0 |
| 2022Q3 | 2022-08-02 | StreetAccount | 2022-08-02 | 1 | 0 |
| 2022Q4 | 2022-11-01 | Refinitiv | 2022-11-01 | 1 | 0 |
| 2023Q1 | 2023-02-14 | Refinitiv | 2023-02-14 | 1 | 0 |
| 2023Q2 | 2023-05-09 | Refinitiv | 2023-05-09 | 1 | 0 |
| 2023Q3 | 2023-08-03 | Refinitiv | 2023-08-03 | 1 | 0 |
| 2023Q4 | 2023-11-01 | LSEG | 2023-11-01 | 1 | 0 |
| 2024Q1 | 2024-02-13 | LSEG | 2024-02-13 | 1 | 0 |
| 2024Q2 | 2024-05-08 | LSEG | 2024-05-08 | 1 | 0 |
| 2024Q3 | 2024-08-06 | LSEG | missing | 1 | 0 |
| 2024Q4 | 2024-11-07 | LSEG | 2024-11-07 | 1 | 0 |
| 2025Q1 | 2025-02-13 | LSEG | 2025-02-13 | 1 | 0 |
| 2025Q2 | 2025-05-01 | LSEG | 2025-05-01 | 1 | 0 |
| 2025Q3 | 2025-08-06 | LSEG | 2025-08-06 | 1 | 0 |
| 2025Q4 | 2025-11-06 | LSEG | 2025-11-06 | 1 | 0 |
| 2026Q1 | 2026-02-12 | LSEG | 2026-02-12 | 1 | 0 |
| 2026Q2 | 2026-05-07 | LSEG | 2026-05-07 | 1 | 0 |

Every row's pre-guide register ID is `PG-<target quarter>-revenue`. No consensus value is used as an economic estimate in this note. The date-inclusive column above is a deliberately inadmissible sensitivity check on the consensus filter only.

## Declared specification count and inferential limits

The note declares one fixed kernel rule and three comparison rules: zero, previous-surprise sign, and consensus-base. That is four named rules and eight rule-by-primary-window evaluations. It declares two signal-selection thresholds (all nonzero signals and |S| > 1pp), three directional groups (positive, negative, direction-adjusted pooled), three executable horizons (1, 5, 20 days), and two primary windows. Those dimensions imply **36 kernel conditional-return summaries**, with all 36 empty on this audit. They are overlapping reporting cells, not 36 independent experiments. The extension is a third sample definition; the post-letter diagnostic is a second timing design. Three live vendor scenarios are prospective comparisons and add no historical observations.

The note also declares one ridge specification with two fitted coefficients, a fixed penalty of one, a fixed slope prior of one, and a minimum of six training pairs. It declares 9,999 permutations, 2,000 bootstrap draws, block length two, and one random seed. Resampling counts do not increase sample size. It reports two kernel/cushion quantities per target season and fixed kernel weights. The empty admissible sample permits **zero fitted pre-guide ridge models**, regardless of the declared parameter count. Internal attempted specifications or searches cannot be independently enumerated from a note alone; package code and derived outputs were prohibited reads, so the counts here are explicitly the disclosed specification family rather than a claim about hidden execution history.

| Inference | W1 actual signal n | W2 actual signal n | Honest result |
|---|---:|---:|---|
| Hit rate at the 1pp threshold | 0 | 0 | Undefined, not 0% |
| 95% Wilson hit-rate interval | 0 | 0 | Unavailable; independent function returns `None` at n=0 |
| Mean signed executable return | 0 | 0 | Undefined at every declared horizon |
| Return or slope bootstrap interval | 0 | 0 | Unavailable: no empirical observations to resample |
| Permutation p-value | 0 | 0 | Unavailable: no eligible sign labels |
| Numerically detectable effect / minimum detectable effect | 0 | 0 | Inestimable at the actual n=0; no numerical effect size is reported |

The six-signal requirement is an operational floor, not a demonstrated power calculation. Even passing that count would not by itself justify precise sign or return inference. At the actual n=0, any numerical minimum detectable effect would require a substituted hypothetical sample or externally imposed distribution, neither of which answers this assignment.

## Numbered refutation attempts

1. **Claim → the zero could be a denominator error or selection of the worse window. Attack →** Independently enumerate 2023Q1–2026Q2 and 2024Q1–2026Q2, join the L0 prior-quarter at-print dates, verify all event dates against reactions, and scan every usable revenue vintage for each target. **Result → survived:** 14 and 10 inspected dates, zero eligible consensus dates on both; W2 adds no independent observations to W1. No preferred-window statistic can be selected from an empty sample.

2. **Claim → “strict point-in-time” might simply discard known pre-release data and overstate missing evidence. Attack →** L0 calls its pre-guide records morning-of-print observations, and the frozen harness README allows same-date consensus (`<=`). Relax the filter to that date-inclusive convention. **Result → partially:** this attack succeeds against any broad interpretation that the data contain no pre-guide consensus information; it recovers 13 and nine attributed consensus candidates. It fails against the exact original sentence because the package's preregistered rule explicitly rejects date-only same-day stamps. Complete signals remain untested under the alternate cutoff; the note separately identifies the contemporaneously released GBV requirement. A same-day clock time would need a revised information-set design rather than silently treating these candidates as validated signals.

3. **Claim → zero eligible observations might be presented as zero hits, zero return, or a bound on alpha. Attack →** Feed the independently recovered actual n=0 to a Wilson implementation and examine the data required for bootstrap and permutation inference. **Result → survived:** the Wilson calculation returns unavailable, bootstrap/permutation have no empirical sample, and no numerical power or detectable effect can be estimated. The original sentence says the evidence is not established; it does not claim a zero effect. Reading it as economic rejection would be invalid.

4. **Claim → the six-signal floor and 70% success threshold might manufacture adequate statistical power. Attack →** Separate the arbitrary admissibility floor from a power calculation, and require an actual denominator and, for returns, variance and dependence assumptions. **Result → partially:** the design has no demonstrated power justification for the six-cell floor. That weakness matters for a future nonempty test but does not change this sample's count or the exact no-established-edge verdict. Neither six nor the 14/10 inspected dates may replace the actual n=0 in a power formula.

5. **Claim → the result could survive only after trying many specifications or understating uncertainty. Attack →** Count the four rules, two primary windows, two thresholds, three directional groups, three horizons, the extension, timing diagnostic and fixed ridge/resampling choices. **Result → survived for the original sentence:** at least the 36 declared kernel return summaries share an empty strict sample. Multiplicity cannot turn empty cells into negative evidence or confidence. The audit does not certify an exhaustive internal search count, and any future claimed positive result across this family needs a prespecified primary statistic and a treatment of selection.

6. **Claim → the 23 earnings-return rows or the post-letter diagnostic could supply sufficient observations despite consensus rejection. Attack →** Inspect the named reactions file's schema and count explicitly executable `open_*` fields. **Result → survived:** 23 supplied return rows contain zero such fields; close-based columns cannot satisfy the requested executable-return object. The note's post-letter count was not independently recomputed because its derived output is out of scope, and those observations cannot enter the strict sample even if the reported count is correct. A published guide changes the prediction task.

7. **Claim → expanding to older dates could rescue power and contradict zero coverage. Attack →** Independently include all five older candidate quarters and apply the same attribution/timestamp conditions. **Result → survived:** the full 19-date extension has 17 same-day stamps, two missing stamps, and zero strictly earlier consensus observations. Two of the same-day rows are additionally unattributed. Extension alone supplies no admissible performance observations.

8. **Claim → the unregistered rationale could conceal actual successful A forecasts. Attack →** Inventory every shared registry CSV filename and look for the exact A method spellings or requested guide-gap object. **Result → survived within the permitted inventory:** 69 registry CSVs and no `alpha-a__*`, `alpha_a__*`, or `guide_gap_next_q` file. The frozen README also explicitly lists its supported-date and target restrictions. No other package's registry contents were inspected, no score was generated, and no guide-level object was silently substituted for a consensus-relative gap.

## What ran and reproducibility

All commands ran from the repository root. Required contextual reads were the agent brief, workboard, assignment, cheatsheet, frozen harness README, and package note. Analytical inputs were only the note's L0 register and reactions CSV. Registry inspection was filenames only. Parent owns workboard, scorer and git actions; this agent wrote only this new note and registered nothing.

The exact independent calculation below exited **0**, Python-measured runtime **0.003464 seconds**, tool wall time **0.672432 seconds**. Overall agent runtime and token usage are unavailable and are not estimated. `.venv` was placed first on PATH, so the portable `python` command used the project interpreter.

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + [IO.Path]::PathSeparator + $env:PATH
@'
import csv, hashlib, json, math, time
from datetime import date, timedelta
from pathlib import Path
started = time.perf_counter()
inputs = [Path('data/processed/forecast_methods/L0/L0_vintage_register.csv'), Path('data/processed/abnb_earnings_reactions.csv')]
with inputs[0].open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(line for line in f if not line.startswith('#')))
with inputs[1].open(encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f)
    returns = list(reader)
    return_fields = reader.fieldnames
revenue = [r for r in rows if r['metric'] == 'revenue']
pg = {r['period']: r for r in revenue if r['role'] == 'pre_guide'}
ap = {r['period']: r for r in revenue if r['role'] == 'at_print'}
rx = {r['quarter']: date.fromisoformat(r['reaction_date']) for r in returns}
def periods(first, last):
    return [f'{i//4}Q{i%4+1}' for i in range(first, last+1)]
def previous(q):
    i = 4 * int(q[:4]) + int(q[-1]) - 2
    return f'{i//4}Q{i%4+1}'
def valid(r):
    try:
        return (r['pit_usable'].lower() == 'true' and r['vendor_attributed'].lower() == 'true'
                and bool(r['vendor'].strip()) and math.isfinite(float(r['value']))
                and bool(r['as_of_timestamp']))
    except (ValueError, TypeError):
        return False
def wilson(hits, n):
    if n == 0:
        return None
    z = 1.959963984540054
    p = hits / n
    d = 1 + z*z/n
    c = (p + z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return [c-h, c+h]
audit = []
for q in periods(4*2021+3, 4*2026+1):
    prior = previous(q)
    cutoff = date.fromisoformat(ap[prior]['as_of_timestamp'])
    assert rx[prior] == cutoff + timedelta(days=1), (q, 'event-date mismatch')
    r = pg[q]
    stamp = r['as_of_timestamp']
    same = bool(stamp) and date.fromisoformat(stamp) == cutoff
    candidates = [s for s in revenue if s['period'] == q and valid(s)]
    strict = [s for s in candidates if date.fromisoformat(s['as_of_timestamp']) < cutoff]
    inclusive = [s for s in candidates if date.fromisoformat(s['as_of_timestamp']) <= cutoff]
    audit.append({'quarter':q,'guide_date':cutoff.isoformat(),'register_id':r['register_id'],
                  'vendor':r['vendor'],'as_of':stamp or None,'same_day':same,
                  'strict_consensus_n':len(strict),'inclusive_consensus_n':len(inclusive)})
summary = []
for label, first in [('W1','2023Q1'),('W2','2024Q1'),('extension','2021Q4')]:
    a = [r for r in audit if r['quarter'] >= first]
    n = sum(r['strict_consensus_n'] > 0 for r in a)
    summary.append({'window':label,'n_dates':len(a),'same_day':sum(r['same_day'] for r in a),
                    'missing_stamp':sum(r['as_of'] is None for r in a),
                    'strict_consensus_dates':n,
                    'inclusive_consensus_dates':sum(r['inclusive_consensus_n']>0 for r in a),
                    'eligible_signals_upper_bound':n,'wilson_at_actual_n':wilson(0,n)})
files = sorted(p.name for p in Path('data/processed/forecast_methods/registry').glob('*.csv'))
alpha_files = [p for p in files if p.startswith(('alpha-a__','alpha_a__')) or 'guide_gap_next_q' in p]
print(json.dumps({'l0_data_rows':len(rows),'summary':summary,'date_audit':audit,
    'registry_csv_count':len(files),'a_registry_files':alpha_files,'return_rows':len(returns),
    'open_fields':[c for c in return_fields if c.startswith('open_')],
    'sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
    'runtime_seconds':round(time.perf_counter()-started,6)}, indent=2))
'@ | python -
```

Input fingerprints:

| Input | Rows n | SHA-256 |
|---|---:|---|
| `data/processed/forecast_methods/L0/L0_vintage_register.csv` | 161 data rows, comment preamble excluded | `c6402930b7e785a5c24829c6e124023525d3a4be64f33f41ad0ef394cb5af3de` |
| `data/processed/abnb_earnings_reactions.csv` | 23 | `45f368e6f10150a481929f199fc1d430a52d6f40e9dd6f5485b661ffa6448b87` |

## What failed or could not be done

An initial `csv.DictReader` schema inspection did not skip the L0 comment preamble and produced an invalid schema; that read was discarded before the independent calculation. The corrected parser explicitly skips comment lines and reads 161 actual data rows. No reported statistic uses the malformed read. The assignment forbade package code and derived outputs, so this audit does not certify every internal attempted specification, the kernel's independent GBV rejection, or the post-letter diagnostic count. None is needed for the decisive necessary-condition proof: without a permissible dated consensus denominator, there is no permissible consensus-relative signal. Return confidence intervals, regression inference and numerical power could not be computed because actual signal n=0. This is not a tool or numerical failure.

## Interpretation

Retain the exact sentence with its “supplied data” and “strict” qualifiers. It is an auditable non-establishment statement, not evidence that the kernel is economically useless, that a pre-release trade cannot exist, or that the true expected return is zero. The most decision-useful correction is to preserve the distinction between 14/10 inspected events and zero scored signals. A future redesign needs its own preregistered information cutoff and a usable signal/target pair before any power or performance claim can be made.

## RESUME

Parent should retain this `survived` vote on the original exact sentence, record the independently verified 14/0 and 10/0 counts, and carry forward the date-cutoff caveat rather than changing the sentence's meaning. If the team revisits the test, obtain sufficiently timestamped contemporaneous inputs, define how GBV is available at the chosen origin, and supply executable returns in a new package; keep the primary hypothesis distinct from the declared overlapping return summaries and justify the needed sample size before testing. Parent owns board, scorer and git actions. No follow-up computation is needed to finalize this refutation.
