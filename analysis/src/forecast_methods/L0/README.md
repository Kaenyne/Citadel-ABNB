# L0 — the constraint spine (Card 0)

Three files, and **no model reads a disclosure except through them**. Import `l0.py`; do not
re-parse `10_xbrl_revenue_geography.csv`, `10_regional_panel_quarterly.csv`,
`02_guidance_ledger.csv`, `04_current_consensus.csv` or `04/16_consensus_at_print*.csv`.

## Run

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
python analysis/src/forecast_methods/L0/run.py
```

Exit code 0 means all three files rebuilt, every hard assertion held and all 20 tests passed.
Outputs land in `data/processed/forecast_methods/L0/`. The build writes progressively: file 1
is on disk and asserted before file 2 starts.

Tests only:

```bash
python -m pytest "analysis/src/forecast_methods/L0/test_l0.py" -q
```

(`pytest` was not in the venv; it was installed. `run.py` falls back to calling the test
functions directly if it is ever missing again, so the package still self-verifies.)

## Outputs

| File | Rows | What |
|---|---|---|
| `L0_exact_regional_revenue.csv` | 72 | 56 filed three-month regional cells 1Q22-2Q26 + 16 Q4 back-outs 2022-2025 |
| `L0_interval_observations.csv` | 186 (172 in the default view) | every censored/rounded disclosure as an interval |
| `L0_vintage_register.csv` | 127 | every consensus value with vendor, period, metric, value, n_estimates, as-of, url |
| `L0_build_diagnostics.json` | — | every count, every assertion result, the soft-check tables |
| `L0_exact_regional_revenue_reconciliation.csv` | 18 | regions vs consolidated revenue, per quarter |
| `L0_exact_regional_revenue_seasonality_check.csv` | 16 | the Q4/Q3 seasonality checks S1 and S2 |
| `L0_interval_observations_midpoint_bias.csv` | 7 | the band-midpoint bias, measured |

## Loader

```python
import sys; sys.path.insert(0, ".../analysis/src/forecast_methods/L0")
import l0

l0.load_exact_regional_revenue()             # 72 rows; pass "filed" or "back_out" to filter
l0.regional_revenue_wide()                   # quarter x region + total
l0.load_interval_observations()              # 172 rows; derived rows DROPPED by default
l0.load_interval_observations(include_derived=True)   # 186 rows, audit only
l0.interval_likelihood_rows(as_of="2025-08-06")       # derived + LIVE dropped, PIT-filtered
l0.load_vintage_register()                   # 127 consensus values
l0.pit_consensus("revenue", "2026Q3", "2026-08-07")   # latest vintage STRICTLY before as_of
l0.pre_guide_street("2026Q3")                # LSEG $4,610M @ 2026-08-06 -- the Street baseline
```

## Rules this package enforces, not merely documents

1. **Two geography axes, never mixed.** The four-region axis is
   `srt:NorthAmericaMember`, `us-gaap:EMEAMember`, `srt:LatinAmericaMember`,
   `srt:AsiaPacificMember` (45 raw rows each). `country:US`, `us-gaap:NonUsMember` and
   `country:FR` are a *different* axis and are never summed with it. A test asserts 1Q22
   totals $1,509M, not $2,281M, which is what you get if the US axis leaks in.
2. **De-duplicate before you count.** 88 three-month regional rows collapse to 56 unique
   `(start, end, geo)` cells; the file restates cells across filings. The earliest filing date
   is kept as `vintage` and the accession number is carried.
3. **There is never a filed Q4 regional cell.** Regional revenue is filed only in the three
   10-Qs each year. The 16 Q4 cells are `basis = back_out` = annual 10-K minus the three filed
   quarters, and the four company totals reproduce to $0.0M.
4. **`basis == 'derived'` rows are excluded from every likelihood** — dropped by the loader's
   default, kept in the file with `included = False` for audit.
5. **Never a midpoint.** Every interval row carries `lo`/`hi`. Letter integers are
   `[x-0.5, x+0.5]`; the 22 stated-integer regional nights cells are rounding intervals.
6. **The 6 Aug 2026 pre-guide Street is LSEG $4,610M.** Zacks $4,740M is a 4 Sep vintage;
   `pit_consensus(..., as_of="2026-08-06")` returns `None` for it, by test.
7. **`pit_usable == False` rows are never returned** by `pit_consensus` — vintage_unknown,
   missing value, or provenance that contradicts itself.

See `docs/revenue-forecast-strategy/05_backtests/L0-spine.md` for results, failures and the
two counts that do not match the architect's.
