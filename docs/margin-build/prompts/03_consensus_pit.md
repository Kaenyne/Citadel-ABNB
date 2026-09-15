# WS03: Point-in-time consensus for EBITDA, margin, EPS, FCF and cost lines; surprise history

Read `docs/margin-build/00_BRIEF.md` first. Slug: `03_consensus_pit`.

## Goal

Every margin forecast in this run will be compared with what the Street expected at the same date. Build the point-in-time consensus panel
for ABNB from the LSEG desktop session (primary) and the local Bloomberg long file (secondary), stamp it at every guide date and print date
in the frozen harness calendar, and characterise how the Street has been wrong on margins.

## Pull (LSEG via `py -3.13` and lseg-data; see the brief for the session snippet; raw to `data/raw/margin_build/03_consensus_pit/`, manifest to `data/manifests/margin_build/03_consensus_pit.csv`)

For ABNB.O, daily history 2021-01-01 to 2026-09-13, periods FQ1..FQ4 and FY1..FY3 where the field supports `Period`:
- EBITDA: `TR.EBITDAMean`, `TR.EBITDAMedian`, `TR.EBITDAHigh`, `TR.EBITDALow`, `TR.EBITDANumberOfEstimates`, `TR.EBITDAStdDev`, and the
  actual/report date fields (`TR.EBITDAActValue`, `TR.EBITDAActReportDate` or the equivalents you find; use `ld.get_data` with the
  `.date` and `.periodenddate` sub-fields so every row carries its observation date and the fiscal period end).
- Revenue (`TR.RevenueMean` etc.), EPS (`TR.EPSMean`, `TR.EPSActValue`), operating income (`TR.OperatingIncomeMean` / `TR.OPRMean`),
  net income, free cash flow (`TR.FCFMean` or `TR.FreeCashFlowMean`), EBITDA margin if a field exists, and any cost-line estimates that exist
  (SG&A, R&D, cost of goods: try `TR.SGAExpMean`, `TR.RDExpMean`, `TR.COGSMean`; record which return data and which do not).
- Also pull the same EBITDA/revenue fields for BKNG.O and EXPE.O (peers, for the cyclicality comparison in M6), FY1/FY2 only, monthly.
- Field names above are best guesses; use `ld.discovery` / the search tools or try variants, and record the exact field that worked. Do not
  spend more than ~30 minutes on field discovery; whatever returns data is enough.

Bloomberg (read-only from `data/raw/theo_onedrive/.../bloomberg/bbg_extracted_long.csv`, sheet `1_Consensus_TS`): BEST_EBITDA, BEST_SALES,
BEST_EPS for 1FQ/2FQ/1FY/2FY by obs_date. Establish whether obs_date is a true history (values change over time for the same fiscal period)
or a pull-date artefact; the repo memory says pull-date anchored, so test it and report.

## Deliverables (all derived, no raw licensed rows)

1. `data/processed/margin_build/03_consensus_pit/03_consensus_at_dates.csv`: for each date in the union of the frozen harness calendar
   (guide dates W1/W2/LIVE, print dates; `analysis/src/forecast_methods/harness/` `calendar.csv`) plus 2026-09-12: for each target period
   (the quarter being guided, the next quarter, FY current, FY next): consensus EBITDA mean/median/n/std, revenue mean, implied EBITDA margin
   (mean EBITDA / mean revenue), EPS, FCF, with `vendor`, `field`, `obs_date` (the last observation on or before the date; state the staleness in days).
   Schema-compatible with `data/processed/forecast_methods/L0/L0_vintage_register.csv` where possible (do NOT edit L0; write a proposed
   append file `03_L0_append_candidates.csv` in L0's exact schema for a human to merge).
2. `03_surprise_history.csv`: for every print 1Q21-2Q26: reported adjusted EBITDA (from the letters; cross-check WS02 if its panel is on disk),
   consensus EBITDA at the print date and at the prior guide date, surprise in $ and in margin points, revenue surprise, implied incremental
   margin on the revenue surprise ((EBITDA surprise) / (revenue surprise)), Street margin vs actual margin, and the guide-implied margin where a
   guide existed (`overnight/02_guidance_ledger.csv`).
3. `03_revision_paths.csv`: how consensus EBITDA for a quarter moved from its guide date to its print date (daily), summarised per quarter
   (drift %, days), and the same for FY EBITDA across the year.
4. `03_surprise_stats.md` section in the note: mean and sd of the margin surprise, by quarter of year (seasonality of surprises), by window
   (W1, W2), equal- and recency-weighted; the flow-through of revenue beats to EBITDA beats (regression with n); Street's implied incremental
   margin vs actual; whether Street margin errors are autocorrelated; whether the Street anchors on the FY floor.
5. `03_current_consensus.csv`: as of 2026-09-12: 3Q26, 4Q26, FY26, FY27, FY28 consensus EBITDA, margin, EPS, FCF with n and dispersion,
   LSEG and Bloomberg side by side, and the management guide (FY26 margin >= 35.5%).
6. Script `analysis/src/margin_build/03_consensus_pit/run.py` that rebuilds from the raw pulls (skips the pull if raw exists), exit 0; README.
7. Note `docs/margin-build/notes/03_consensus_pit.md` with bottom line, tables, the field-discovery log, caveats (licence, staleness, vendor
   differences vs the 16_consensus_at_print values already in the repo, with a comparison table), "For the model", "For the 5 Nov card", RESUME.

## Pass line (pre-registered)

Consensus EBITDA at print for at least 18 of 22 prints 1Q21-2Q26 with an observation no older than 7 days; the LSEG values agree with the
repo's 8 existing at-print EBITDA consensus rows within 3% (report every disagreement).
