# REFUTE B — mechanism

Agent `ref_b_mechanism` · 2026-09-12 · parent-managed branch `codex/lane1-full` (as identified by the package; no git operations) · final computation 0.323 seconds tool wall time.

## Verdict: survived

The original exact sentence survives. Independently reconstructed origins total 14 in W1 and 10 in W2, and the supplied FY ledger contains **zero dollar revenue guides**. That necessary-target failure alone forces **zero eligible dollar FY-guide-revision tests**, irrespective of whether the forecast is a kernel, a seasonal rule, or a constant. All 12 usable, attributed FY revenue consensus rows also postdate the historical origins. The strongest mechanism attack works against any stronger interpretation of the live gap: a simple cushion calculation reproduces almost all of the Q4 kernel–consensus gap at the broad panels, with no booking-kernel inputs. B's exact sentence already withholds revision-alpha validation, so this attack reinforces rather than refutes it.

## Pre-registration (before independent numerical execution)

Original exact sentence: “At strict pre-guide dates, the supplied data yield zero eligible FY-guide-revision tests in W1 (0/14) and W2 (0/10), so the live kernel–consensus gap is a conditional scenario, not validated revision alpha.”

The refuter has no numerical pass threshold. The final verdict will be exactly survived, refuted, or partial on that sentence. I will independently enumerate guide origins from the guidance ledger; isolate dollar-denominated FY revenue guides and strictly earlier FY consensus in the named source inputs; try qualitative-growth conversions, altered information timing, a no-revision alternative, and a cushion-only explanation of the live gap. Missing targets remain missing. Any relaxation of the stated eligibility policy is labelled a counterfactual, not silently counted as an original eligible test. W1 and W2 are nested eligibility audits, not two independent statistical samples. All computations use inline Python; only this new note is written. No package code or derived results will be read, no external data fetched, and no registry or shared file changed.

This pre-registration was written to this new note before the independent numerical calculations. No numerical pass line was invented for the refuter.

## What ran

Read the assigned B note, the permitted numbers cheatsheet and frozen harness README, and the four source inputs below. The repository brief and workboard were read first as required by the user's top-level instructions. A filename search located the note's abbreviated input names. No B/K0 source code, package-derived audit, live output, or pending registry candidate was read. A filename-only search found **zero actual `alpha-b__*.csv` registry files** (n=0); B correctly describes itself as unregistered.

Source discovery used PowerShell `Get-Content -LiteralPath`, `rg --files data | rg "(fy|FY|guidance|guide|quarterly|earnings_reactions|vintage|alpha.b|rnpl)"`, and inline standard-library Python schema inspection. The final exact numerical command is reproduced below. It ran from the repository root using the relative project-venv interpreter, exited **0**, took **0.322670 seconds** of tool-reported wall time, and reported **0.003527300 seconds** inside Python. Earlier schema discovery initially treated L0's comment preamble as a header; this was corrected by excluding `#` lines before any register count. An initial Q4 display filter used the ledger spelling `4Q26`; the final run uses L0's canonical `2026Q4`. Neither discovery mismatch affected the final counts.

No files other than this note were written. No forecast registration, scorer, web retrieval, licensed-data access, branch operation, or fitted model was run. Token usage and total agent elapsed time are unavailable; no estimate is presented as measured usage.

| Source input | Rows read, n | SHA-256 |
|---|---:|---|
| `data/processed/overnight/02_guidance_ledger.csv` | 194 | `c1a2b34330dc6655c549cbe7cab66adabcaaffcffc4441c833c726714d8267f2` |
| `data/processed/overnight/02_fy_guide_revisions.csv` | 47 | `eabcd118fc428559cee78ad63090c2015f53cf29fd9e268e7754fbbc136776fd` |
| `data/processed/forecast_methods/L0/L0_vintage_register.csv` | 161 data rows, excluding comments | `c6402930b7e785a5c24829c6e124023525d3a4be64f33f41ad0ef394cb5af3de` |
| `data/processed/abnb_earnings_reactions.csv` | 23 | `45f368e6f10150a481929f199fc1d430a52d6f40e9dd6f5485b661ffa6448b87` |

## Independent results

Eligibility here uses B's strict pre-guide information set and its **dollar FY-revenue-guide** target. The first W1 origin is 2023-02-14 (guide target 1Q23), the first W2 origin is 2024-02-13 (1Q24), and both end on 2026-05-07 (2Q26). The 2026-08-06 event is excluded as LIVE.

| Audit, PIT origin selection | W1 result / n audited | W2 result / n audited |
|---|---:|---:|
| Quarterly revenue-guide origins | 14 / 14 | 10 / 10 |
| Prior same-FY dollar revenue guides | 0 / 14 | 0 / 10 |
| Prior same-FY growth-language guidance exists | 1 / 14 | 1 / 10 |
| Strictly earlier, usable, attributed same-FY revenue consensus exists | 0 / 14 | 0 / 10 |
| Allow same-day consensus instead: comparator exists | 0 / 14 | 0 / 10 |
| Eligible dollar FY-guide-revision tests, upper bound and actual | **0 / 14** | **0 / 10** |
| No-revision alternative: same eligible outcome sample | 0 / 14 | 0 / 10 |

The single prior growth-language row becomes available before the 2026-05-07 origin; it is the 2026-02-12 FY2026 statement. There are **3** FY revenue rows across the **47** FY-ledger rows, all growth buckets: encoded centres 11%, 14%, and 15%, dated 2026-02-12, 2026-05-07, and 2026-08-06. These produce **2 coded consecutive differences**, +3pp and +1pp, but **0 dollar-guide differences**. The first and last statements use open-ended language. The narrow integer measurement rule of ±0.5 does not turn those qualitative growth buckets into precise observations.

The L0 source contains **12** FY revenue consensus rows passing its usable/attributed flags; their earliest date is **2026-09-03**. These cover FY2026/FY2027 and therefore cannot supply any strictly earlier historical FY comparator. This is an independent blocker for B's secondary FY-consensus-revision test, but is not required to prove that its primary dollar FY-guide-revision test is empty.

## Numbered refutation attempts

1. **Claim:** The zero counts reflect a property of the kernel. **Attack:** Remove the entire kernel and apply only the necessary-target gate: a dollar FY-guide revision needs two comparable dollar FY-guide observations. **Result: survived on the exact sentence; kernel-specific attribution refuted.** **Evidence:** The FY ledger has 0 dollar revenue guides among 47 rows, so every possible forecast rule has an empty paired sample: 0/14 W1 and 0/10 W2. The simple alternative explaining the counts is source/target incompatibility, not seasonality, model precision, or a failed economic signal. B's exact sentence accurately attributes the result to the supplied data.

2. **Claim:** There are zero eligible FY-guide-revision tests. **Attack:** Treat the three numerical bucket centres as actual FY guidance and count their changes. **Result: survived under the declared target; partial only under a deliberately changed qualitative target.** **Evidence:** The source does contain two coded transitions (+3pp, +1pp; n=2), and before 2026-05-07 it contains one older FY growth statement. But a centre chosen to encode a broad phrase is not a management-issued dollar midpoint. Multiplying an analyst-chosen centre by prior-year revenue supplies the analyst's assumptions, not a missing guide. The source also explicitly says guidance was raised in May, so a future qualitative direction study is possible; it would need its own signal, target and origin convention. It cannot silently replace B's dollar-gap test or validate its |gap| threshold.

3. **Claim:** Strict pre-guide timing explains the absence of an eligible historical test. **Attack:** Relax same-day exclusion and even grant an oracle complete FY kernel prediction at every origin. **Result: survived; the empty test is overdetermined by target availability.** **Evidence:** With either `< date` or `<= date`, attributed same-FY consensus exists at 0/14 and 0/10 origins because the earliest FY revenue vintage is 2026-09-03. More decisively, the count of dollar FY guides remains 0 even with unlimited future access to the supplied ledger. Improving GBV forecasting or shifting to a post-letter information set cannot alone create the absent dollar revision target. This does not establish that historical GBV nowcasts are intrinsically impossible.

4. **Claim:** The live positive kernel–consensus gap supplies distinct kernel information. **Attack:** Independently calculate the trailing-eight median actual/guide cushion from the raw quarterly guidance ledger, then strip it out of the quoted Q4 kernel revenue. **Result: the stronger mechanism claim is refuted; the exact cautious sentence survived.** **Evidence:** The eight quarters 3Q24–2Q26 give **c = 1.790491%** (n=8 historical ratios, available at the live date). `3214.78 / (1+c) = 3158.23214`. Thus the reported revenue gaps of +1.798% against Alpha Vantage and +1.734% against the S&P/Yahoo rows become conditional guide gaps of **+0.00735%** and **−0.05595%**, respectively. These are single-date arithmetic comparisons, not estimated revision effects. The transformation reproduces B's own $3,158.23 guide to rounding. A revenue forecast versus a revenue consensus remains a valid descriptive level comparison; the attack shows why it cannot, by itself, identify an expectations edge in the guide.

5. **Claim:** The annual live result requires a booking kernel. **Attack:** Construct a simple alternative using only printed H1 revenue, the already-issued Q3 guide, the raw-ledger cushion, and each stamped Q4 consensus: `H1_actual + (Q3_guide + Q4_consensus) × (1+c)`. **Result: mechanism identification fails; the exact sentence survived.** **Evidence:** H1 is $6,286M (n=2 printed quarters), Q3 guide midpoint is $4,730M (n=1 guide), and the eight-ratio cushion is 1.790491%. The alternative is **$14,315.23M** with Alpha Vantage's Q4 $3,158M and **$14,317.27M** with S&P/Yahoo's $3,160M. Those are only **$6.09M/$8.13M above** B's quoted $14,309.14M FY result (n=1 live scenario per row). This is a deliberately simple numerical counterexample, not a recommended revenue forecast: multiplying Q4 revenue consensus by a cushion assumes that it approximates a future guide and may double count a beat already included by analysts. Its close fit shows observational non-identification at one date; it does not prove that the cushion causes the kernel result.

6. **Claim:** Multiple positive vendor gaps give corroborating revision-alpha evidence. **Attack:** Retain exact vendor/date labels, apply the same arithmetic across panels, and inspect whether the conclusion survives changing only the comparison anchor. **Result: a stronger corroboration claim fails; the exact sentence survived.** **Evidence:** With Zacks' Q4 $3,200M (2026-09-11), the revenue gap is +0.46188%, but the conditional guide gap is **−1.30525%**; the annual cushion-only counterexample differs from B by −$48.85M. S&P/Yahoo's lower Q4 anchors give almost zero guide gap. Each is n=1; identical or shared upstream panels cannot increase the event count. No panel has a historical eligible FY revision pair here.

7. **Claim:** The empty historical result can still be rescued by a no-revision baseline, returns, or the live weight band. **Attack:** Check the target gate for the baseline, inspect the source return schema, and separate arithmetic sensitivities from estimated performance. **Result: survived.** **Evidence:** No-revision has 0 paired dollar targets in both windows, not a perfect zero error. The 23-row return file has 0 `open_*` columns and 0 60-day columns. B's fixed-lambda weight band is an arithmetic exercise; there are 0 eligible revision outcomes against which to estimate its directional success, calibration or incremental value. A different weight or larger-looking live gap does not manufacture observations. This audit does not refit that band or claim a statistical test of it.

## Live arithmetic table

All amounts are USD millions. The Q4 kernel value **$3,214.78M** is taken explicitly from the permitted B note; the cushion and alternative values below are independently recalculated from the named raw inputs. The estimated historical cushion uses n=8 ratios, but each live comparison has n=1 and no revision outcome.

| Vendor (verbatim L0) | Timestamp | Q4 consensus | Revenue gap % | Conditional guide gap % | Kernel minus consensus × (1+c), $M | FY arithmetic alternative, $M | n live comparisons |
|---|---|---:|---:|---:|---:|---:|---:|
| Alpha Vantage (aggregated sell-side panel) | 2026-09-11 | 3,158 | +1.79797 | +0.00735 | +0.23629 | 14,315.23 | 1 |
| S&P Global Market Intelligence via StockAnalysis | 2026-09-10 | 3,160 | +1.73354 | −0.05595 | −1.79952 | 14,317.27 | 1 |
| Yahoo Finance | 2026-09-11 | 3,160 | +1.73354 | −0.05595 | −1.79952 | 14,317.27 | 1 |
| Zacks | 2026-09-11 | 3,200 | +0.46188 | −1.30525 | −42.51571 | 14,357.99 | 1 |

The exact arithmetic identity is `revenue_gap = (1 + cushion) × (1 + guide_gap) − 1`, using ratios rather than percentage points. It does not provide statistical support. W1/W2 apply to the historical eligibility question, not to this single-date identity. With zero eligible revision trials there is no hit rate, Wilson interval, correlation, fitted effect, or detectable-effect calculation to report. W2 is contained in W1; it does not double the evidence. The live median cushion is a historical descriptive estimate, but its successful reconstruction of a quoted calculation is not a test of forecast skill.

## What failed or could not be done, and why

The attempts to manufacture an eligible dollar revision observation failed. A qualitative target would admit different information, but B explicitly excludes turning its bucket centres into precise dollar guidance. The no-kernel eligibility gate therefore suffices to establish the central count without rerunning K0. I did **not** independently reproduce the separate claim of zero complete pre-guide kernel FY forecasts: doing so would require K0 code, its derived outputs or additional explicitly identified vintage inputs beyond this assignment's allowed reads. That unverified subsidiary claim is unnecessary for the proven zero upper bound on eligible dollar revisions.

I also did not claim to rebuild the live kernel's fitted coefficients or RNPL scenario. Its two quoted live points are labelled quoted inputs when constructing counterexamples. No confidence bands were estimated from those points. This preserves the boundary between independently verified target sufficiency, quoted model output, and conditional arithmetic.

## Interpretation

Keep the original sentence exactly as written. Its operative conclusion is absence of validation, not evidence that a future properly designed kernel revision signal must fail. The mechanism refutation is that the same zero-test counts arise with no kernel, and nearly the same live numbers can arise from a simple cushion convention. Neither the zero sample nor the live arithmetic supports ranking the kernel against seasonality, last revision, or a guide policy. No regression or kernel coefficients are newly fitted in this audit; the live alternative uses one descriptive median re-estimated from eight already-public ratios.

## Exact final command

Executed in PowerShell from the repository root. The relative interpreter is the project `.venv` Python, not a machine-specific absolute path.

```powershell
@'
import csv,hashlib,re,statistics,time
from pathlib import Path
start=time.perf_counter()
paths=['data/processed/overnight/02_guidance_ledger.csv','data/processed/overnight/02_fy_guide_revisions.csv','data/processed/forecast_methods/L0/L0_vintage_register.csv','data/processed/abnb_earnings_reactions.csv']
def read(p):
    with Path(p).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(x for x in f if not x.startswith('#')))
def qkey(q):
    m=re.fullmatch(r'([1-4])Q(\d{2})',q)
    return int('20'+m[2])*4+int(m[1])-1 if m else None
g,fy,reg,ret=map(read,paths)
rev=[r for r in fy if r['metric'].startswith('revenue')]
usd=[r for r in rev if r['metric']=='revenue_usd_m' and r['value_mid'] and r['guide_type'] in ('point','range')]
cons=[r for r in reg if r['metric']=='revenue' and r['period'].startswith('FY') and r['pit_usable'].lower()=='true' and r['vendor_attributed'].lower()=='true' and r['vendor'] and r['as_of_timestamp']]
origins=sorted([r for r in g if r['metric']=='revenue_usd_m' and r['guide_type']=='range' and qkey(r['target_period']) is not None and qkey('1Q23')<=qkey(r['target_period'])<=qkey('2Q26')],key=lambda r:r['print_date'])
print('source_rows',list(map(len,[g,fy,reg,ret])),'FY_revenue',len(rev),'FY_dollar',len(usd),'FY_consensus',len(cons),'earliest',min(r['as_of_timestamp'] for r in cons))
for r in origins:
    p='FY20'+r['target_period'][-2:]; d=r['print_date']
    print('origin',r['target_period'],d,'prior_dollar',sum(x['target_period']==p and x['print_date']<d for x in usd),'prior_growth',sum(x['target_period']==p and x['print_date']<d for x in rev),'earlier_consensus',sum(x['period']==p and x['as_of_timestamp'][:10]<d for x in cons),'same_day_consensus',sum(x['period']==p and x['as_of_timestamp'][:10]<=d for x in cons))
for w,first in [('W1','1Q23'),('W2','1Q24')]:
    n=sum(qkey(r['target_period'])>=qkey(first) for r in origins)
    print('window',w,'n',n,'eligible_upper_bound',0 if not usd else 'inspect')
print('coded_transitions',[(a['print_date'],b['print_date'],float(b['value_mid'])-float(a['value_mid'])) for a,b in zip(rev,rev[1:])])
print('return_fields',list(ret[0]),'B_registry_files',list(Path('data/processed/forecast_methods/registry').glob('alpha-b__*.csv')))
dates={r['print_quarter']:r['print_date'] for r in g}
ranges=sorted([r for r in g if r['metric']=='revenue_usd_m' and r['guide_type']=='range' and r['actual'] and dates.get(r['target_period'],'9999')<'2026-09-12'],key=lambda r:dates[r['target_period']])
c=statistics.median(float(r['actual'])/float(r['value_mid'])-1 for r in ranges[-8:])
h1=sum(float(r['actual']) for r in ranges if r['target_period'] in ['1Q26','2Q26'])
g3=float(next(r['value_mid'] for r in g if r['metric']=='revenue_usd_m' and r['target_period']=='3Q26'))
q4=3214.78; fy_point=14309.14; g4=q4/(1+c)
print('cushion',c,'trailing8',[(r['target_period'],r['actual'],r['value_mid']) for r in ranges[-8:]],'H1',h1,'Q3_guide',g3,'Q4_guide',g4)
for r in reg:
    if r['metric']=='revenue' and r['period']=='2026Q4' and r['as_of_timestamp'][:10]>='2026-09-10' and r['pit_usable'].lower()=='true' and r['vendor_attributed'].lower()=='true':
        x=float(r['value']); alt=h1+g3*(1+c)+x*(1+c)
        print('Q4',r['vendor'],r['as_of_timestamp'],x,'revenue_gap_pct',100*(q4/x-1),'guide_gap_pct',100*(g4/x-1),'kernel_minus_cushioned_street',q4-x*(1+c),'FY_alternative',alt,'B_minus_alternative',fy_point-alt)
for p in paths: print('sha256',p,hashlib.sha256(Path(p).read_bytes()).hexdigest())
print('runtime_seconds',time.perf_counter()-start)
'@ | .\.venv\Scripts\python.exe -
```

## RESUME

Retain B's exact cautious sentence and the independent 0/14 and 0/10 dollar-target sufficiency result. Before any new B test, define whether the target is a dollar FY guide, a qualitative guide change, or an FY consensus revision, then obtain the relevant targets and strictly dated signals for that specific object. Score a no-revision rule and a guide/cushion alternative on the identical nonempty outcome sample. Keep the live revenue gap, conditional guide gap, and vendor stamp distinct; the cushion counterexample here establishes numerical non-identification at one date, not an investment forecast or an estimate of incremental kernel alpha. Parent owns board, scorer and git operations.
