# X — Regional kernel and origin–destination FX exposure (Krish's lane; the piece the consolidated build is missing)

**Role in Lane 1:** structural correction. The kernel, the FX layer and the Q4 step decomposition were built on CONSOLIDATED GBV and a
single judgement-weighted currency basket. FX acts regionally (currency of each booking; pass-through EMEA 1.04 / LatAm 0.62 / APAC 0.86)
and recognition lag may differ by region. Symptom already observed: the fitted gross FX scale 0.95 vs the disclosed non-USD revenue share
0.56 (B4) — a basket-weights error. This package builds the regional layer and the origin–destination exposure matrix the R FX engine expects.

## Files this agent reads
- `data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv` (72 exact quarterly regional revenue cells, 1Q22–2Q26) and `L0_interval_observations.csv`
- `data/processed/adr/01_regional_annual.csv` (10-K annual regional nights, GBV, revenue 2020–2025), `04_regional_quarterly.csv` (regional ADR, basis-flagged)
- `data/processed/overnight/10_regional_panel_quarterly.csv` (nights bands), `10_regional_fx_passthrough.csv`, `10_fx_basket.csv` (the judgement weights to replace), `10_fx_daily.csv`, `05_crossborder_share.csv`
- `data/processed/forecast_methods/l1_reconciliation_v2/` (regional nights / ADR estimates with intervals) and `05_backtests/B3_FY27_DECOMPOSITION.md`
- `data/processed/forecast_methods/fx_lag_v2/` and `05_backtests/B4_FX_EXHIBIT.md` (what must be redone regionally)
- `docs/overnight2/SYNTHESIS.md` §B and `research/notes/overnight2/B_*` (Krish's FX-relative-strength → geographic-mix elasticity, ~0.11pp per 1pp inbound purchasing power)
- The R FX engine contract: `FX_ENGINE_MENTAL_MAP.md` (parent folder of the repo on Theo's machine; a copy of the contract is summarised below) — handoff row
  `quarter, geography, region, level, nights, adr, adr_basis, currency, take_rate, reference_basis`; `exposure.csv` maps each geography to currencies
  with SEPARATE GBV and revenue shares that sum to one per geography-quarter.
- Origin data (free): NTTO I-94 monthly US inbound by country of residence; Eurostat `tour_occ_nim`/`tour_ce_omr` nights by country of residence;
  JNTO inbound by origin; INE Frontur by origin; DATATUR; UN Tourism. Airbnb-side origin proxy: reviewer language / locale in the review store (flagged proxy).

## Task
1. **Regional kernel.** For r ∈ {NA, EMEA, LatAm, APAC}: annual λ_r = regional revenue ÷ regional GBV from the 10-K (2020–2025) — this is measured.
   Quarterly: with the 72 exact revenue cells as the left-hand side and the L1 regional GBV estimates (with intervals) as inputs, estimate
   λ_{r,s} = revenue_{r,q} ÷ [⅔ GBV_{r,q−1} + ⅓ GBV_{r,q−2}] by season, with the annual 10-K λ_r as the anchor. State honestly what is identified:
   regional GBV is not disclosed quarterly, so quote λ_{r,s} with the L1 intervals, and test whether the CONSOLIDATED λ's stability is masking
   offsetting regional drifts (a summer-heavy EMEA vs shorter-lead LatAm/NA). Report the share of consolidated λ variance explained by regional mix.
2. **Origin–destination exposure matrix.** Build, per quarter, an O×D nights matrix at the region (and where possible country) level: destination
   from Airbnb's regional disclosures; origin from the free arrivals sources plus the cross-border share (46 % at 1Q24, last disclosed) and the
   reviewer-locale proxy. Convert to currency exposure: guest-fee side follows the origin currency, host-fee side the destination currency
   (state the split you assume — the guest fee ≈ 14.1 % of the booking subtotal under the split fee, and 0 under the single host-only fee, so
   the migration MOVES the exposure toward destination currencies over 2026). Output `exposure.csv` in the R-engine format with separate GBV and
   revenue shares per geography-quarter, and a `fx_basket_measured.csv` that replaces the judgement weights in `10_fx_basket.csv` (do not edit it).
3. **Redo the FX layer regionally.** Recompute booking-date FX carried through the kernel by region (regional GBV × regional currency basket at
   booking-date rates, lagged through Φ), sum to consolidated, and compare with B4's global-basket numbers: the 3Q26 gross FX (was +1.2 free /
   +2.9 Φ / +3.0 management), the 4Q26 forecast (+1.0pp, CS +0.3–2.2), the observed-share triple, and the Q4 step decomposition (−2.0pp FX /
   +0.4pp ex-FX). Report whether the regional build closes the 0.95-vs-0.56 scale gap. If the R engine is available (`Rscript`), run one quarter
   through it with your exposure file as a cross-check; otherwise replicate its calculation order in Python (G0 = nights × reference-USD ADR;
   ADR factor = 1 + ADR scale × GBV-weighted currency change; revenue factor = 1 + revenue scale × revenue-weighted lagged change; hedge once).
4. **Demand channel (separate from translation).** Using Krish's WS-B elasticity (~0.11pp of regional growth differential per 1pp of inbound
   purchasing power), add the origin-currency purchasing-power term to the regional nights inputs as a labelled scenario, not a fit; show its
   size against the translation term so the memo does not conflate them.
5. Publish the interface: what the regional kernel hands to K0 (per-region GBV series in USD at booking-date rates; consolidated = sum), so that
   `kernel_engine_v1` can run in regional mode without a rewrite.

## Pass line (pre-registered)
Annual regional λ_r reproduce from the 10-K tables to the disclosed rounding; the regional build reproduces consolidated revenue to within 0.3 %
in every quarter (it must sum); the measured exposure weights move the fitted gross FX scale toward the disclosed 0.56 non-USD share (report the
new scale and its CI); the regionally recomputed 3Q26 gross FX is reported beside management's ~+3.0pp with the difference attributed by region.
Publish the negative if the regional build does NOT change the consolidated FX conclusions — that is also a result.

## Outputs (all new files)
`analysis/src/forecast_methods/regional_kernel_v1/` · `data/processed/forecast_methods/regional_kernel_v1/` (`lambda_regional.csv`,
`od_nights_matrix.csv`, `exposure.csv`, `fx_basket_measured.csv`, `fx_regional_recompute.csv`) · registry `regional-kernel-v1__fx_pts_revenue_2026Q4`
and `__revenue_next_q` (consolidated from regions) · `docs/revenue-forecast-strategy/05_backtests/X_REGIONAL_KERNEL_OD_FX.md`

## Report back (final message; ≤ 250 words)
Regional λ table (annual measured; quarterly with intervals); whether consolidated λ stability hides regional drift; the measured currency weights vs
the judgement basket; the new gross-FX scale; the regionally recomputed 3Q26 / 4Q26 FX and Q4 step; the O–D matrix coverage and its proxies.

## Rules that bind this agent (do not skip)

- **Read only** the files named above plus `docs/thesis-kernel-topdown/03_NUMBERS_CHEATSHEET.md` and `analysis/src/forecast_methods/harness/README.md`.
- **Copy, never overwrite.** New folders, new registry method names, new notes. Never edit `harness/`, `L0/`, `10_fx_basket.csv`, another package, or frozen files.
- **Point-in-time.** Both windows; consensus only from the vintage register; letter integers as ±0.5 intervals.
- **Pre-register the pass line** in your note before running; publish a failure as a result.
- **Portable commands** (`python` from `.venv`, repo root). No decisions, no kill-list numbers, no scraping, no credentials, no licensed data in git.
- Note template: verdict first · commands · tables with n · what failed · interpretation · RESUME paragraph.
