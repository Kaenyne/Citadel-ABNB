# Government travel and price data survey, 12 Sep 2026: shared brief

Branch `krish/gov-data-survey`, worktree `C:\Users\krish\citadel-abnb-govdata`, based on main 5bd2d08. Owner Krishang Surapaneni, compiled with Claude Code. Scoping run, not a model change. Three workstreams: **V** (volume series against nights and regional nights), **P** (price series against ADR, ex-FX ADR, the pricing residual and regional ex-FX ADR), then **R** (a reviewer that audits V and P and challenges every elimination).

## The question
Is there official (government or statistical-agency) travel volume or travel price data, not yet in the repo, that either (a) beats naive out of sample on an Airbnb KPI and is knowable before 5 November, or (b) does not beat naive but corroborates the current 3Q26 and 4Q26 numbers with a read we do not already have? The output is a ranked list with a verdict per source and a reason, and a recommendation on whether a full workstream is worth running before the 2 October freeze.

## What is already tested (do not re-pull, do not re-test on the same construction)
- `data/processed/q3nowcast/G/source_inventory.csv` (40 ranked sources, URLs, access dates) and `research/notes/q3nowcast/G_external-sources-q3-read.md`. Machine-pulled and backtested: TSA daily throughput (fails, 0.92 best, 0.98 to 1.00 on the long window); NTTO I-94 arrivals by world region (survivor, 0.72 to 0.74 on nights, correlate not mechanism); BLS CPI lodging away from home SA and NSA and airfares (0.716 on ADR short window, 1.318 long window); Eurostat `tour_ce_omr` platform nights (150-day lag, no lead value); Spain INE Frontur arrivals and EOH hotel nights (0.839 short window, 1.003 long); Marriott and Hilton RevPAR (0.665 and 0.691 on nights). Raw caches under `data/processed/q3nowcast/G/raw/`.
- `data/processed/adrq3/J/proxy_tests.csv` (164 tests): CPI lodging three variants, BEA hotels PCE price index, euro-area HICP accommodation services, INE Spain hotel price index, MAR and HLT RevPAR, management wording, against the blended residual, blended ex-FX ADR and regional ex-FX. None beats naive against the residual (best 1.03). Euro-area HICP against EMEA ex-FX is the one marginal survivor (0.91) and the regional route built on it failed (adrv3 workstream L, read-only at `C:\Users\krish\citadel-abnb-adrv3\research\notes\adrv3\L_regional-residual-and-proxies.md`).
- `research/notes/overnight/10_regional-and-segment-decomposition.md` (3,446 correlations of external benchmarks against regional nights, three negatives; Eurostat as an EMEA share gauge only) and `research/notes/overnight/08_altdata-index-and-backtests.md` (the protocol). `research/notes/overnight2/C_consumer-relative-strength-regional-split.md` (OECD SDMX consumer panel, 29 countries; fails with the wrong sign as a split forecast).
- FRED keyless set already held under `data/raw/fred/` and `data/raw/macro/`; BEA PCE travel detail under `data/raw/bea/`; Hawaii DBEDT under `data/raw/hawaii_dbedt/` (annual and monthly highlights; only public party-size series).
- Identified but never pulled (G section 5): Spain INE EOAT table 429 tourist-apartment nights plus the IPAP apartment price index; Eurostat `tour_occ_nim` NACE I552 (reaches June 2026); StatCan Canada travellers; Census QSS NAICS 721 (3Q26 advance 19 Nov, too late for the print but history is testable); JNTO. These are the first things to pull.

## Selection criteria, in this order
1. **Asset class.** Short-term rental or tourist-apartment series first, then platform or "other accommodation" series, then hotel series, then arrivals. Say which.
2. **Coverage.** Reaches July or August 2026 today, or reaches September before 5 November. Record the release calendar.
3. **History.** At least ten quarters from 1Q23, so a walk-forward with six or more scored quarters exists. Series that start later can still be corroboration.
4. **Access.** Free, keyless, machine-pullable. A registration wall is acceptable if it is free; record it. Paid is out of scope but list it in one line.
5. **Test.** The note-08 protocol via `analysis/src/adrq3/I0_protocol.py`: expanding walk-forward from 1Q24, RMSE ratio vs naive last quarter, prior year and AR(1), 1,000-shuffle permutation p, jackknife, knowable-before-print flag. Both windows, 2023Q1+ and 2022Q1+; a series that only survives the short window is reported as such. Regional targets from `data/processed/adr/04_regional_quarterly_wide.csv` and the regional nights buckets in `data/processed/overnight/10_regional_panel_quarterly.csv`.

## Verdict vocabulary (one per source, with the reason)
- **survivor**: beats naive on both windows with six or more scored quarters.
- **short-window survivor**: beats naive on 2023Q1+ only.
- **corroboration**: has a 3Q26 reading we do not already hold, does not beat naive or cannot be tested.
- **duplicate**: measures the same thing as a series already held; name it.
- **no coverage**, **no history**, **no access**, **wrong asset class**: eliminated on a stated fact, with the fact.
Never eliminate on more than one reason at once; state the first failing criterion so the reviewer can check it.

## Rules
- Label every number sourced / descriptive / assumed. Write only inside this worktree: scripts `analysis/src/govdata/<WS>_*.py`, raw caches `data/processed/govdata/<WS>/raw/` (small CSVs, committed) with a manifest carrying URL, access date, bytes, sha256, outputs `data/processed/govdata/<WS>/`, note `research/notes/govdata/<WS>_<slug>.md`. Never modify the main tree.
- Python `py -3.13`. Network pulls allowed; respect robots and rate limits; never use a paid key. Bash calls time out at 10 minutes.
- Note format: date, author "Krishang Surapaneni (compiled with Claude Code)", sections Bottom line, Ranked table, Method, What this can and cannot identify, Next steps, Files. Plain prose, no em-dashes.
- Commit only your own files at the end (`git add <your paths>`; on `index.lock` wait 30 s, retry up to five times). Never push.
