# REFUTE_X_vintage — independent source-vintage audit

Agent `/root/ref_x_vintage` · 12 September 2026 · parent owns branch/board/scorer/git · token usage unavailable.

## Verdict

**survived** on the complete original sentence. Independent source arithmetic and date matching reproduce **0/14 W1 and 0/10 W2 eligible historical guide observations**. The published tourism data measure visitors or platform nights; the conversion to Airbnb origin–destination and payment-currency weights remains assumed. Rebuilding the note's example exposure weights does not turn them into measured exposures. This verdict supports the stated evidence limit, not a claim that B4 is the optimal model.

## Pre-registered audit (written before independent calculations)

Original sentence: “The regional FX reconstruction does not yet justify replacing B4: no measured Airbnb origin–destination currency matrix is identified, and the current reconstruction has 0/14 W1 and 0/10 W2 point-in-time guide observations.”

The assignment has no statistical pass line: the output must be exactly one of survived / refuted / partial on the complete original sentence. I will independently count the guide dates from the named guidance ledger; compare every date to the public-input release stamps and the stated reconstruction date; rebuild tourism coverage and exposure-weight arithmetic from permitted source inputs; search actual registry filenames for X objects; distinguish Airbnb data from public tourism proxies and future interface examples. At least five explicit attacks will be reported. No X code or X derived output tables will be read. Neither a current reconstruction nor an accounting identity will count as a historical forecast. No external benchmark forecast comparison will be invented.

## Results: seven explicit refutation attempts

1. **Claim → no measured Airbnb O-D currency matrix is identified. Attack → use the official tourism counts to identify the purported missing matrix. Result: survived.** The [NTTO report](https://www.trade.gov/sites/default/files/2026-05/NTTO-Spring-Forecast-2026.pdf), actual-2025 column on page 3, independently confirms 68,288,000 visitors, 52,713,000 in the named origins, and 51,151,000 mapped to the supplied currencies: **77.1922% origin coverage / 74.9048% currency-proxy coverage** (n=11 extract records, combining three European origins). The [JAPAN NATIONAL TOURISM ORGANIZATION release](https://www.jnto.go.jp/en/news/20260819.pdf) confirms 3,442,100 July-2026 arrivals, 3,274,000 classified by region, and 1,505,300 assigned a supplied currency: **95.1164% / 43.7320%** (n=5 regional records; n=8 currency records including Mexico). These national arrivals are not Airbnb stays or booking-payment currencies. The Eurostat extract gives **62.1792% foreign** from 591,704,241 / 951,611,862 nights (n=2 records), but foreign does not identify a regional origin or a currency. No row in these inputs directly observes an Airbnb origin–destination–settlement-currency cell. The metric mismatch survives even if every tourism count is correct.

2. **Claim → currency weights are scenarios. Attack → independently reproduce the selected weights and see whether they encode disclosed exposure rather than assumptions. Result: survived.** The supplied `10_fx_basket.csv` explicitly labels its weights judgment. Aggregating its named proxy currencies yields the note's destination weights: EMEA EUR 0.62+0.08=0.70, LatAm BRL 0.45+0.10=0.55, APAC AUD 0.40+0.15=0.55. I reconstructed all four destination and revenue distributions for each of the 14 W1 target quarters, using only source nights margins and public extracts. At guest share 0.5 and country-cross-border share 0.46, revenue weight equals **0.77 × destination basket + 0.23 × foreign-origin currency proxy**. The latest source-quarter examples below match the note's three-decimal figures. A sum-to-one check therefore verifies a normalized assumed allocation; it supplies no direct currency observation. Varying guest share to 0 or 14.1/17.1=0.8245614 preserves the same public visitor counts while changing revenue exposure, a concrete identification counterexample.

| Independent reconstruction, 2026Q2 source margins | n currency cell | Destination weight | Rebuilt midpoint revenue weight | Note rounded weight |
|---|---:|---:|---:|---:|
| NA / USD | 1 | 0.900000 | 0.744947 | 0.745 |
| EMEA / EUR | 1 | 0.700000 | 0.605896 | 0.606 |
| LatAm / BRL | 1 | 0.550000 | 0.446096 | 0.446 |
| APAC / AUD | 1 | 0.550000 | 0.498007 | 0.498 |

3. **Claim → the four-by-four O-D matrix is assumed, despite its Airbnb destination margins. Attack → treat the 46% cross-border disclosure as the missing matrix constraint. Result: survived.** The named regional panel's last nonempty cross-border share is **1Q24, 46%**; its accompanying quote describes total **gross** nights booked. It is neither a 2026 measurement nor a regional-border share. In the independent construction, domestic country travel and within-region international travel both lie on the diagonal. With each quarter's source nights margins, the implied interregional share is only **27.9016%–28.6755%** (n=14 retrospective scenario quarters), not 46%. At 2026Q2 it is 28.2666%. Destination margins sum to one and every reconstructed currency distribution sums to one, but these identities leave the origin allocation and settlement currency unidentified. US arrivals cannot measure origins for all NA destinations, Japan cannot measure all APAC destinations, and EMEA/LatAm foreign origins are imputed from regional nights weights.

4. **Claim → 0/14 W1 and 0/10 W2 PIT observations. Attack → the zero might merely reflect a September reconstruction timestamp, which is not sufficient evidence of look-ahead. Result: survived, with that rationale explicitly rejected.** A historical replay may legitimately be built today from historically available inputs. I therefore removed reconstruction date from the eligibility calculation altogether and matched the source releases to the guidance ledger. It still returns **0/14 and 0/10**. The latest scored guide is 7 May 2026, while the JNTO release used in every APAC reconstruction is explicitly dated 19 August 2026. No scored date has the complete current input set. NTTO's 1 June date is only a conservative stored cutoff: the PDF says April and its URL says May, so an earlier exact publication date might admit NTTO at the final guide. Even granting that most favorable case changes the complete-input counts by **zero**. All source providers and all stored publication-date values were checked; no consensus vendor is present in these source extracts.

5. **Claim → the accounting evidence cannot furnish missing historical forecasts. Attack → use the 24 annual ratios or 72 exact regional revenue cells to turn the reconstruction into a forecast replay. Result: survived.** Independently computing 100×revenue/GBV reproduces **24/24 annual source ratios**, maximum difference **0.0pp** at Python float precision. But the annual source has `source_10k` fiscal-year labels and no filing-publication-date field. The note's fixed FY2025 annual anchor contains a future fiscal year at **12/14 W1 and 8/10 W2** guide dates. The exact regional revenue source contains **72 cells across 18 quarters** with explicit `knowable_from`; for each of the 14 scored target quarters all four target revenue cells become knowable after its guide. Their actual dates appear below. Such target cells can score a forecast after the event; they cannot define a same-cell lambda in its forecasting information set. Quarterly ADR/nights-share inputs also have modeled or derived labels and no vintage columns. Replacing their quarter labels with guide dates would produce a prohibited splice, not rescue eligibility.

6. **Claim → no valid X historical registry objects alter the zero. Attack → locate actual registered forecasts or a vendor-stamped alternative hidden by the note's abstention language. Result: survived within the assigned evidence set.** The actual registry directory contains **69 CSV filenames** at audit time, with **zero X/regional-kernel/O-D/exposure matches**; the full filename inventory likewise contains no X object. The package note states no object was registered and consumes no consensus value. Consequently there is no X `vintage_date`, `street_as_of`, `street_vendor`, or `knowable_from` row to rehabilitate, and no consensus-splice route in the examined inputs. I did not read unrelated registry contents or infer program behavior from code. The stronger evidence for zero admissible observations is the independently checked future source release, not registry absence alone.

7. **Claim → future-labelled interface checks do not create historical or current forecasts. Attack → count the 13 September K0 handoff or the 5 November availability ceiling as additional validation. Result: survived.** The note explicitly describes one K0 interface test at **as_of=2026-09-13** with reconstruction data dated **2026-09-12**. Both follow every historical guide; the as-of date is also after this assignment's 12 September research date. The frozen harness README accepts research-date rows only at 2026-09-11, and treats the 2026-08-06 guide as LIVE, outside both scored windows. Merely extending the allowed current date would not repair historical input availability. The note's 5 November calendar/publication-lag arithmetic is prospective and supplies no observed future FX or measured volume. These examples verify an interface or conditional availability arithmetic; neither is a new historical economic test.

## Every historical guide date: O-D and exposure audit

Each row is **one guide observation**; W2 is a subset of W1. The NTTO / Eurostat / JNTO columns indicate whether the **stored source cutoff** is strictly before that guide, not whether the statistical period is historical. Stored cutoffs are 2026-06-01 / 2026-07-02 / 2026-08-19. The O-D share is an independent retrospective scenario using target-quarter source margins, displayed to expose the look-ahead rather than to claim a forecast. Every date has 16 constructed O-D cells and four normalized currency distributions. Measured Airbnb currency cells remain zero throughout.

| Target | Guide date | Window | n | NTTO / Eurostat / JNTO admissible | Target revenue `knowable_from` | Rebuilt interregional O-D share | Eligible complete X observation |
|---|---|---|---:|---|---|---:|---:|
| 2023Q1 | 2023-02-14 | W1 | 1 | 0 / 0 / 0 | 2023-05-09 | 27.9016% | 0 |
| 2023Q2 | 2023-05-09 | W1 | 1 | 0 / 0 / 0 | 2023-08-03 | 28.0669% | 0 |
| 2023Q3 | 2023-08-03 | W1 | 1 | 0 / 0 / 0 | 2023-11-01 | 28.6450% | 0 |
| 2023Q4 | 2023-11-01 | W1 | 1 | 0 / 0 / 0 | 2024-02-16 | 28.6520% | 0 |
| 2024Q1 | 2024-02-13 | W1/W2 | 1 | 0 / 0 / 0 | 2024-05-08 | 27.9960% | 0 |
| 2024Q2 | 2024-05-08 | W1/W2 | 1 | 0 / 0 / 0 | 2024-08-06 | 28.1626% | 0 |
| 2024Q3 | 2024-08-06 | W1/W2 | 1 | 0 / 0 / 0 | 2024-11-07 | 28.6218% | 0 |
| 2024Q4 | 2024-11-07 | W1/W2 | 1 | 0 / 0 / 0 | 2025-02-13 | 28.6188% | 0 |
| 2025Q1 | 2025-02-13 | W1/W2 | 1 | 0 / 0 / 0 | 2025-05-01 | 28.0169% | 0 |
| 2025Q2 | 2025-05-01 | W1/W2 | 1 | 0 / 0 / 0 | 2025-08-06 | 28.1268% | 0 |
| 2025Q3 | 2025-08-06 | W1/W2 | 1 | 0 / 0 / 0 | 2025-11-06 | 28.6755% | 0 |
| 2025Q4 | 2025-11-06 | W1/W2 | 1 | 0 / 0 / 0 | 2026-02-12 | 28.5404% | 0 |
| 2026Q1 | 2026-02-12 | W1/W2 | 1 | 0 / 0 / 0 | 2026-05-07 | 28.1984% | 0 |
| 2026Q2 | 2026-05-07 | W1/W2 | 1 | 0 / 0 / 0 | 2026-08-06 | 28.2666% | 0 |
| W1 total | — | W1 | 14 | — | — | retrospective | 0/14 |
| W2 total | — | W2 | 10 | — | — | retrospective | 0/10 |

For reconstruction, let s[d] be a destination's normalized source nights share, f[o,d] its imputed foreign-origin share, b[c,d] its judgment destination basket, and c[c,d] its foreign-origin currency proxy. Then O-D[o,d] = s[d]×(0.54×1[o=d]+0.46×f[o,d]). Unresolved NTTO/JNTO regional origins are allocated by s; unresolved currencies are allocated by b. EMEA/LatAm foreign regional origins use s, with currency proxy sum_o(s[o]×b[c,o]). Midpoint revenue exposure is 0.77b+0.23c. The source's rounded nights shares are normalized before use. None of these rules measures migration penetration or payment currency.

## What ran, failures, and scope

All reads and calculations ran from the repository root. Only this new note was written. X code, tests and derived output tables were not read or executed. No forecast was registered; no scorer, board or git mutation was performed. This audit estimates no statistical parameters. Its reproduction uses the note's fixed 0.46 cross-border and 0.5 guest-share scenarios; X's stated 16 kernel coefficients are not independently fitted here.

Permitted evidence read: the assignment, cheatsheet, harness README, X note; `public_inputs.csv`; `adr/01_regional_annual.csv`, `adr/04_regional_quarterly.csv`, `adr/04_regional_quarterly_wide.csv`; `overnight/02_guidance_ledger.csv`, `overnight/10_fx_basket.csv`, `overnight/10_regional_panel_quarterly.csv`, `overnight/10_regional_quotes.csv`; `L0/L0_exact_regional_revenue.csv`; registry **filenames only**. An exploratory read of `overnight/10_fx_daily.csv` found its end date 2026-08-28; it is not the note's described 4 September cache and was not used to infer the note's FX cutoff. The mandatory parent instructions required initial reads of AGENT_BRIEF and WORKBOARD before the narrower assignment was opened.

Commands `rg --files "data/processed/forecast_methods/registry"` and path-filtered `rg --files "data" "analysis/src/forecast_methods"` returned exit 0. The named evidence was read with `Get-Content -LiteralPath`. Initial plain `python -` failed because Python was not on PATH (exit 1, 1.52s); prepending the project `.venv/Scripts` resolved this without changing any file. One exploratory quarter parser omitted the `20` century prefix and returned empty windows; those results were discarded. The corrected and final calculation asserts exactly 14/10 dates. The source-date/cell-date calculation exited 0 (0.59s shell wall time); cross-border source inspection exited 0 (0.54s). Final reproduction below exited **0**, **0.89s shell wall time / 0.0111s computation**. Token use and total elapsed session time are not available and are not estimated.

The two official PDFs were opened and their table pages requested through the web tool. NTTO's report month and JNTO's dated release were directly checked. Opening the [Eurostat API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/tour_ce_omr?geo=EU27_2020&time=2025&indic_to=NGT_SP&unit=NR) failed in the web fetcher; an exact-URL `urllib.request.urlopen(..., timeout=25)` fallback hit a restricted socket (caught error; 0.10s computation). Its numeric ratio is reproduced from the supplied input, but its current API update timestamp is **not independently reverified**. JNTO alone suffices to establish zero complete historical observations, so this limitation does not weaken the verdict. No claim is made about X's full FX fit, test-suite execution or unseen derived output contents.

Exact final PowerShell reproduction command (read-only; no X imports):

```powershell
$env:PATH = (Join-Path (Get-Location) '.venv\Scripts') + [IO.Path]::PathSeparator + $env:PATH
@'
import csv, collections, pathlib, time
started = time.perf_counter()
def read(path):
    with open(path, encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))
def canon(q): return '20' + q[2:] + 'Q' + q[0] if len(q)==4 and q[1]=='Q' else q
p = read('analysis/src/forecast_methods/regional_kernel_v1/public_inputs.csv')
l = read('data/processed/overnight/02_guidance_ledger.csv')
g = sorted({(canon(r['target_period']), r['print_date']) for r in l if r['metric']=='revenue_usd_m' and '2023Q1'<=canon(r['target_period'])<='2026Q2'})
assert len(g)==14 and sum(q>='2024Q1' for q,d in g)==10
for w, rows in [('W1',g), ('W2',[(q,d) for q,d in g if q>='2024Q1'])]:
    print(w, len(rows), sum(all(x['publication_date']<d for x in p) for q,d in rows))
regions = ['na','emea','latam','apac']
b = {r:collections.defaultdict(float) for r in regions}
for x in read('data/processed/overnight/10_fx_basket.csv'):
    if x['currency']!='BASKET': b[x['region']][x['proxy_series'] or x['currency']]+=float(x['weight'])
ccy = sorted(set(c for r in b.values() for c in r))
nt = [x for x in p if x['provider']=='NTTO']
ja = [x for x in p if x['provider']=='JNTO']
jc = [x for x in p if x['provider']=='JNTO_CCY']+[x for x in ja if x['currency']!='UNRESOLVED']
for name, source, total in [('NTTO',nt,68288000),('JNTO currency',jc,3442100)]:
    print(name,'mapped currency pct',100*sum(float(x['visitors_or_nights']) for x in source if x['currency']!='UNRESOLVED')/total)
wide = {canon(x['quarter']):x for x in read('data/processed/adr/04_regional_quarterly_wide.csv')}
for q,d in g:
    row=wide[q]; s={r:float(row['nights_share_'+r+'_pct']) for r in regions}; s={r:v/sum(s.values()) for r,v in s.items()}
    od={}; e={}
    for dest in regions:
        if dest in ['na','apac']:
            src=nt if dest=='na' else ja; total=sum(float(x['visitors_or_nights']) for x in src)
            f={r:sum(float(x['visitors_or_nights']) for x in src if x['origin_region']==r)/total for r in regions}
            missing=1-sum(f.values()); f={r:f[r]+missing*s[r] for r in regions}
            cs=nt if dest=='na' else jc
            c={k:sum(float(x['visitors_or_nights']) for x in cs if x['currency']==k)/total for k in ccy}
            missing=1-sum(c.values()); c={k:c[k]+missing*b[dest][k] for k in ccy}
        else:
            f=s; c={k:sum(s[r]*b[r][k] for r in regions) for k in ccy}
        od[dest]={r:s[dest]*(0.54*(r==dest)+0.46*f[r]) for r in regions}
        e[dest]={k:0.77*b[dest][k]+0.23*c[k] for k in ccy}
    assert abs(sum(sum(v.values()) for v in od.values())-1)<1e-12
    assert max(abs(sum(v.values())-1) for v in e.values())<1e-12
    print(q,d,'O-D interregional pct',round(100*sum(od[x][y] for x in regions for y in regions if x!=y),4),'PIT complete',all(x['publication_date']<d for x in p))
    if q=='2026Q2': print('exposure example',e['na']['USD'],e['emea']['EUR'],e['latam']['BRL'],e['apac']['AUD'])
a=[x for x in read('data/processed/adr/01_regional_annual.csv') if x['region']!='total']
print('annual ratios',len(a),max(abs(100*float(x['revenue_musd'])/float(x['gbv_musd'])-float(x['take_rate_pct'])) for x in a))
r=list(pathlib.Path('data/processed/forecast_methods/registry').glob('*.csv'))
print('registry files',len(r),'X matches',[x.name for x in r if any(t in x.name.lower() for t in ['regional-kernel','regional_kernel','od-fx','od_fx','exposure'])])
print('compute seconds',round(time.perf_counter()-started,4))
'@ | python -
```

## Interpretation

The strongest attempted rescue was that modern reconstruction dates need not invalidate historical work. That objection is correct in general and does not rescue this package: future tourism releases and undated current regional assumptions remain in its historical scenario construction. A normalized O-D table is achievable; an independently observed Airbnb currency matrix is not identified by these inputs. No corrected headline number is required. The original **0/14 and 0/10** is reproduced without relying on the reconstruction-date field or a missing-registry shortcut.

## RESUME

Parent should use the verdict **survived** for this vintage lens, preserve the original evidence-limit sentence, and retain the caveat that current creation dates alone are not proof of look-ahead. A successor needs archived public releases, dated annual/quarterly reconstruction inputs, and a defensible Airbnb/settlement-currency mapping before attempting PIT exposure forecasts; Eurostat's live timestamp still needs a successful public fetch. Refit each eligible historical specification with its own information set, distinguish scenario exposure from measurement, and register only under a new method. Parent owns workboard, scorer, branch and git; this agent wrote only this note.
