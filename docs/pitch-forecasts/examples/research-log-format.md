# Research log Schema (machine-parsed — follow exactly)

File name: `research-log-<question-name>.md`. Section headers and table columns are parsed by harness scripts; keep them verbatim. Dates are ISO `YYYY-MM-DD`; use `unknown` only when genuinely undeterminable (each `unknown` on a load-bearing claim counts against the freshness check).

```markdown
# RESEARCH LOG

## 0. Metadata
- question_name: <question-name>
- question_url: <url or n/a>
- type: <binary|multiple_choice|continuous|group>
- run_mode: <initial|update>
- run_date: YYYY-MM-DD
- open_date: YYYY-MM-DD
- close_date: YYYY-MM-DD
- resolution_date: YYYY-MM-DD
- scoring: <time_averaged|spot|unknown>
- cp_visible: <yes|no>
- cp_value: <value or n/a>

## 0b. Question (verbatim)
### Title
<verbatim>
### Resolution Criteria
<verbatim>
### Fine Print
<verbatim>

## 1. Claims Ledger
| # | Claim | Source URL | Published | Retrieved | Load-bearing |
|---|-------|-----------|-----------|-----------|--------------|
| 1 | <one-sentence factual claim> | <url> | YYYY-MM-DD | YYYY-MM-DD | yes/no |

Rules: every factual claim the forecast relies on gets a row. "Load-bearing: yes" = removing this claim would change the final number by ≥2 points or reshape the distribution. Market prices are claims (Published = the live-fetch timestamp date). Claims sourced from training knowledge rather than a fetched source: Source URL = `training`, Published = `unknown`.

## 2. Query Log
1. <verbatim query 1>
2. <verbatim query 2>
(ordered, complete, including failed/empty searches and the final 72-hour recency check)

## 3. Leading Hypothesis Entities
<comma-separated proper nouns of the leading hypothesis/outcome — used by the search-bias check>

## 4. Hypotheses Considered and Discarded
| Hypothesis / scenario / pathway | Status | Reason |
|---------------------------------|--------|--------|
| <e.g., NY S9144 pathway> | discarded | <specific reason with source #> |

## 5. Independent Estimates
- base_rate_estimate: <number> — <one-line derivation>
- decomposition_estimate: <number> — <one-line derivation>
- anchor_estimate: <number> — <anchor source + timestamp>
- anchor_value: <the designated external anchor number>
- final_estimate: <number or percentile summary>
- final_minus_anchor: <difference; if |diff| < 10 points, add flag NOT_INDEPENDENTLY_DERIVED or justify independence in one line>

## 6. Final Numbers
<binary: point + interval | MC: full vector | continuous: percentile table + bounds mass>

## 7. Sensitivity
| Assumption | If reversed, number moves to |
|------------|------------------------------|

## 8. Monitoring Calendar
| Date | Event / checkpoint | Expected action |
|------|--------------------|-----------------|
```
