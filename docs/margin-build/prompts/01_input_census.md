# WS01: Census of every input in the repo that could bear on a cost line, an add-back, or a below-EBITDA item

Read `docs/margin-build/00_BRIEF.md` first. Slug: `01_input_census`.

## Goal

The revenue work uses a large set of alternative and disclosed inputs (GBV, nights, ADR, FX, regional mix, seats, Experiences/Services,
length of stay, party size, fee panels, RNPL ledger, supply/churn panels, reviews index, calendar pace, regulatory profile, Lane 1 kernel).
Margins have so far been modelled from the P&L alone (WS31). Your job is to go through the WHOLE repo and worktree (docs, research notes,
analysis scripts, data/processed, data/manifests, model workbooks, the Lane 1 package from PR #53, Theo's package under `theos-past-research/`,
`ABNB-Crossover/`) and build the definitive census of inputs that could move any of these targets:

cost of revenue (payment processing, hosting, insurance/AirCover claims, chargebacks), operations & support (customer service, trust & safety),
product development, sales & marketing (brand vs performance, host acquisition, referral), general & administrative (legal, lodging taxes,
bad debt, corporate), SBC by line, D&A, restructuring/other add-backs, interest income (funds held on behalf of guests x rates), other income,
tax, share count, unearned fees and funds payable (FCF timing), capex.

## Deliverables

1. `data/processed/margin_build/01_input_census/01_input_census.csv`: one row per series/file with columns:
   `series_id, description, file_path, script_path, frequency, first_period, last_period, n_obs, pit_lag_days (when it becomes knowable
   relative to the quarter it describes), target_lines (semicolon list of the cost/other lines it could explain), mechanism (one sentence: why it
   would move that line), prior_evidence (what the repo already found about it, with note path), status (available | needs_refresh | licensed_local |
   candidate_pull), suggested_method (M1 driver | M4 alt | M6 cycle | M7 below-EBITDA | M3 guide | M5 street)`.
   Expect 80-200 rows. Include the revenue-side driver series themselves (nights, GBV, ADR, take rate, FX pts, regional nights share,
   seats/experiences volumes, LOS, party size) because cost lines are modelled per unit.
2. `01_gaps.csv`: inputs that do NOT exist in the repo but plausibly bear on a line (e.g. job-posting counts, ad-spend trackers, support
   ticket proxies, payment processing rate changes, hosting price indices, wage indices, funds-held yield), with a suggested source and whether it is
   reachable under the brief's rules (archives / third-party public / LSEG / EDGAR / not reachable). WS04 will pull from this list, so make
   the source suggestions concrete (URL patterns, LSEG field names where you know them, EDGAR form types).
3. `01_line_mechanisms.md` section inside your note: for each of the six cash cost lines and each below-EBITDA item, a paragraph on what
   drives it economically (cite the 10-K cost-line definitions from `data/raw/xbrl` / filings and the 31a management statements),
   which repo series proxy each driver, and what the WS31 model currently assumes.
4. Note `docs/margin-build/notes/01_input_census.md`: bottom line (the ten most promising inputs not yet used for margins, ranked, with why),
   the census summary table by target line (count of available series, count of candidate pulls), corrections to existing work if any,
   "For the model", and a RESUME paragraph.

## Method

- Use Glob/Grep/Read widely; read `docs/2026-09-06_research-inventory.md`, `docs/2026-09-07_revenue-forecasting-inventory.md`,
  `data/README.md`, `docs/revenue-forecast-strategy/AGENT_BRIEF.md`, `docs/revenue-forecast-strategy/05_backtests/SCOREBOARD_v2.md`,
  `research/notes/overnight/14_master-synthesis.md`, and every `README.md` under `analysis/src/`.
- For each candidate, actually open the file and record real first/last periods and n; do not guess.
- Where a series was already tested against margins (predictive/04, WS07, WS31), quote the result and n.
- Script `analysis/src/margin_build/01_input_census/run.py` that at least validates the CSV (paths exist, columns present) and exits 0.

## Pass line (pre-registered)

Census covers every `data/processed` folder and every research note; every row's `file_path` exists; at least 10 candidate pulls with concrete
sources for WS04. If you cannot cover everything in ~90 minutes of work, prioritise breadth over depth and say what you skipped.
