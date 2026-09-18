# V1 — Street rows, vendor and date stamped

## 1. Header
- Line: V1 · Judge's question: "Which consensus, from whom, as of when?"
- Digger: sonnet · Date: 2026-09-18 · Commit: e39d9e4

## 2. The number

Scenario = "street" throughout (there is no base/short/breaker split for a consensus stamp). Every
row below carries its vendor and capture date in the **vendor / note** column, appended to the
template's columns because the brief requires it explicitly. "LSEG-family" = LSEG (Refinitiv
Workspace desktop pull), Yahoo Finance and Alpha Vantage, which the governing notes establish are one
panel surfaced through three interfaces and must not be double-counted (A1 §2, `03_consensus_pit.md`
§0). Where LSEG-family and Zacks differ, both rows are given per the brief; no row here decides which
vendor is "the" Street.

| scenario | period | object | point | low | high | unit | vintage | vendor / note |
|---|---|---|---|---|---|---|---|---|
| street | 3Q26 | revenue | 4744 | 4737 | 4745 | musd | 2026-09-10/13 | LSEG-family: LSEG desktop pull (as-of trading day 2026-09-11, pulled 13 Sep) $4,744.3M n=37; Yahoo 13 Sep 15:20 UTC $4,744.9M n=36; Alpha Vantage 11 Sep $4,737.5M n=36; S&P/StockAnalysis 10 Sep $4,740M n=35; Zacks 11 Sep $4,740M n=7. Spread only $2.5–8M — **not** a LSEG-vs-Zacks conflict at this period (A1 §2). Memo v3 quotes $4,744M. |
| street | 3Q26 | nights | 148.9 | 147.0 | 151.0 | m | 2026-09-12 (label) / 2026-09-04 (level) | **Conflicted — see §4/§7.** Memo v3 attributes 148.9m to "Bloomberg MODL, 12 Sep, 28 estimates" (screenshot, Krish); the underlying capture CSV for that same 12-Sep MODL screenshot records **mean 149.0m** (low 147.0/high 151.0, n=28). 148.9m instead matches a *different*, earlier Bloomberg capture ("Bloomberg FA", 4 Sep 2026, a single displayed level, not a 28-name mean) used throughout `research/notes/reverse_dcf/`. No free vendor page (Zacks, Yahoo, S&P/StockAnalysis) publishes a forward nights consensus at all (A1 §3, exhaustive). |
| street | 3Q26 | ADR | 177.06 | 173.71 | 179.12 | usd | 2026-09-12 | Bloomberg MODL, screenshot 12 Sep 2026 (Krish), n=26. Only source found anywhere (A1 §3: no vendor page carries ADR). |
| street | 3Q26 | adj. EBITDA | 2362 | 2323 | 2420 | musd | 2026-09-11 (as-of) / pulled 2026-09-13 | LSEG (Refinitiv Workspace desktop pull via `03_consensus_pit`), mean $2,361.5M, n=36, sd $20.0M, implied margin 49.78%. **Only source**: A1 (11 Sep, free web only) found no free adj-EBITDA consensus anywhere; `03_consensus_pit.md` line 263 explicitly supersedes that with the LSEG desktop pull (see §4). |
| street | 4Q26 | revenue (LSEG-family) | 3161 | 3158 | 3162 | musd | 2026-09-10/13 | LSEG desktop (as-of 2026-09-11) $3,161.8M n=37; Yahoo 13 Sep $3,161.0M n=36; Alpha Vantage 11 Sep $3,158.1M n=36; S&P/StockAnalysis 10 Sep $3,160M n=35. Corroborated by Bloomberg MODL 12-Sep (n=37, mean $3,157M, low 3,052/high 3,223). |
| street | 4Q26 | revenue (Zacks) | 3200 | 3050 | 3700 | musd | 2026-09-11 | Zacks, n=10 — the brief's named conflict. Register note: "HIGH OUTLIER: +40M above Yahoo/S&P 3160 and +42M above Alpha Vantage 3158 on the same day," thinnest panel of the three (n=10 vs 35–37), unchanged since the 4 Sep vintage. |
| street | FY26 | revenue (LSEG-family) | 14160 | 14155 | 14190 | musd | 2026-09-10/13 | LSEG desktop (as-of 2026-09-11) $14,189.6M n=44; Yahoo 13 Sep $14,164.6M n=43; Alpha Vantage 11 Sep $14,155.1M n=43; S&P/StockAnalysis 10 Sep $14,160M n=43. |
| street | FY26 | revenue (Zacks) | 14100 | 13960 | 14210 | musd | 2026-09-11 | Zacks, n=8. Register note: "LOW outlier on FY26 (−60M vs Yahoo/S&P 14160)," unchanged vs 4 Sep. |
| street | FY27 | revenue (LSEG-family) | 15798 | 15758 | 15819 | musd | 2026-09-10/13 | LSEG desktop (as-of 2026-09-11) $15,819.3M n=44; Yahoo 13 Sep $15,798.2M n=43; Alpha Vantage 11 Sep $15,757.8M n=44; S&P/StockAnalysis 10 Sep $15,770M (n unavailable, paywalled detail column). |
| street | FY27 | revenue (Zacks) | 15740 | 14990 | 16290 | musd | 2026-09-11 | Zacks, n=13, drifted +$10M from the 4 Sep vintage. |
| street | FY27 | adj. EBITDA | 5766 | 5493 | 6255 | musd | 2026-09-11 (as-of) / pulled 2026-09-13 | LSEG desktop pull, mean $5,766.1M, n=44, sd $154.2M. Implied margin (mean EBITDA ÷ mean revenue) 36.45%; LSEG's own separately-averaged margin field gives 35.06% — a different basis, both reported in `03_consensus_pit.md`, not reconciled here (see §8). **Only source**; no free vendor page carries this metric (A1 §3). |
| street | FY27 | EPS | 6.23 | 6.04 | 6.23 | usd | 2026-09-10/13 | LSEG desktop (as-of 2026-09-11) $6.2275 n=43; Yahoo 13 Sep $6.2251 n=40; Alpha Vantage 11 Sep $6.1858 n=41; S&P/StockAnalysis 10 Sep $6.17 (n unavailable); Zacks 11 Sep $6.04 n=13 (low outlier). |
| street | 4Q26 | nights bar | 134.0 | 130.0 | 136.0 | m | 2026-09-12 | Bloomberg MODL, screenshot 12 Sep 2026 (Krish), n=28. Clean: matches the brief's figure exactly, mean growth +9.93% on the 121.9m 4Q25 base. No free vendor page carries this metric. |
| street | 3Q26 | nights bar | 148.9 | 147.0 | 151.0 | m | 2026-09-12 (label) / 2026-09-04 (level) | Duplicate of the nights row above, listed again because the brief names it as its own object. Same conflict applies. |

### 2a. Model inputs (machine-readable)

Per DEC-0005 (coordinator decision): the 3Q26 Street nights bar is **149.0m**, the value in the
12-Sep MODL capture cited above, not the 148.9m the memo currently prints (§4/§7 unresolved-conflict
note above is left as written — it is the investigative record; this table reflects the decision).

| item | scenario | period | point | unit | note |
|---|---|---|---|---|---|
| street_revenue_musd | street | 3Q26 | 4744 | musd | LSEG-family: LSEG desktop pull as-of 2026-09-11 (pulled 13 Sep) $4744.3M n=37; Yahoo 13 Sep 2026 15:20 UTC $4744.9M n=36; Alpha Vantage 11 Sep 2026 $4737.5M n=36 |
| street_revenue_musd | street | 4Q26 | 3161 | musd | LSEG-family: LSEG desktop pull as-of 2026-09-11 (pulled 13 Sep) $3161.8M n=37; Yahoo 13 Sep 2026 15:20 UTC $3161.0M n=36 |
| street_revenue_musd | street | FY26 | 14160 | musd | LSEG-family: LSEG desktop pull as-of 2026-09-11 (pulled 13 Sep) $14189.6M n=44; Yahoo 13 Sep 2026 15:20 UTC $14164.6M n=43 |
| street_revenue_musd | street | FY27 | 15798 | musd | LSEG-family: Yahoo 13 Sep 2026 15:20 UTC $15798.2M n=43; LSEG desktop pull as-of 2026-09-11 (pulled 13 Sep) $15819.3M n=44 |
| street_nights_m | street | 3Q26 | 149.0 | m | Bloomberg MODL, screenshot 12 Sep 2026 (Krish), n=28, per DEC-0005 |
| street_nights_m | street | 4Q26 | 134.0 | m | Bloomberg MODL, screenshot 12 Sep 2026 (Krish), n=28 |
| street_adr_usd | street | 3Q26 | 177.06 | usd | Bloomberg MODL, screenshot 12 Sep 2026 (Krish), n=26 |
| street_adr_usd | street | 4Q26 | 171.33 | usd | Bloomberg MODL, screenshot 12 Sep 2026 (Krish), n=25 |
| street_take_rate_pct | street | 3Q26 | 17.98 | pct | DEC-0018: street_revenue_musd 4744 ÷ (street_nights_m 149.0 × street_adr_usd 177.06 = 26381.94) × 100 = 17.98%. Cross-check: Bloomberg MODL's own directly-published 3Q26 take_rate_pct mean is 18.0% (n=28, screenshot 12 Sep 2026, Krish) — same capture, 0.02pt apart. |
| street_take_rate_pct | street | 4Q26 | 13.77 | pct | DEC-0018: street_revenue_musd 3161 ÷ (street_nights_m 134.0 × street_adr_usd 171.33 = 22958.22) × 100 = 13.77%. Cross-check: Bloomberg MODL's own directly-published 4Q26 take_rate_pct mean is 13.76% (n=28, screenshot 12 Sep 2026, Krish) — same capture, 0.01pt apart. |
| street_ebitda_musd | street | 3Q26 | 2362 | musd | LSEG desktop pull, as-of trading day 2026-09-11 (pulled 13 Sep 2026), mean $2361.5M, n=36 |
| street_ebitda_musd | street | FY27 | 5766 | musd | LSEG desktop pull, as-of trading day 2026-09-11 (pulled 13 Sep 2026), mean $5766.1M, n=44 |
| street_eps_usd | street | 3Q26 | 2.85 | usd | LSEG desktop pull, as-of trading day 2026-09-11 (pulled 13 Sep 2026), mean $2.8454, n=34 |
| street_eps_usd | street | FY27 | 6.23 | usd | LSEG desktop pull, as-of trading day 2026-09-11 (pulled 13 Sep 2026), mean $6.2275, n=43 |
| street_margin_pct | street | FY27 | 36.45 | pct | Implied basis (mean adj. EBITDA ÷ mean revenue), LSEG desktop pull as-of 2026-09-11, pulled 13 Sep 2026 |
| street_margin_field_pct | street | FY27 | 35.06 | pct | LSEG's own separately-averaged EBITDA-margin-mean field, a different basis from street_margin_pct; LSEG desktop pull as-of 2026-09-11, pulled 13 Sep 2026 |
| street_revenue_musd | street_zacks | 4Q26 | 3200 | musd | Zacks, 11 Sep 2026 15:44 ET, n=10, unchanged since the 4 Sep 2026 vintage |
| street_revenue_musd | street_zacks | FY26 | 14100 | musd | Zacks, 11 Sep 2026 15:44 ET, n=8, unchanged since the 4 Sep 2026 vintage |
| street_revenue_musd | street_zacks | FY27 | 15740 | musd | Zacks, 11 Sep 2026 15:44 ET, n=13, drifted +$10M from the 4 Sep 2026 vintage |

## 3. Derivation chain
1. Vendor pages / terminal screens — Zacks detailed-estimates page, Yahoo Finance analysis tab,
   Alpha Vantage `EARNINGS_ESTIMATES` (MCP), StockAnalysis/S&P Global MI forecast page, LSEG/Refinitiv
   Workspace desktop app (`lseg-data` 2.1.1), Bloomberg MODL and Bloomberg FA terminal screens (no API;
   read off a screenshot) →
2. Raw captures: `data/raw/consensus/2026-09-11/*.csv` (A1, 11 Sep); `analysis/src/forecast_methods/consensus_stamp_v2/capture_20260913T152058Z/*.csv` and `stockanalysis_web_capture.json` (M, 13 Sep); `data/processed/margin_build/03_consensus_pit/03_current_consensus.csv` (LSEG desktop pull, 13 Sep session, as-of row date 2026-09-11); `data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv` (Bloomberg MODL screenshot transcription, 12 Sep) →
3. Register: `data/processed/forecast_methods/L0/L0_vintage_register.csv`, `role=current` rows
   `CU-2026Q3-revenue-*`, `CU-2026Q4-revenue-*`, `CU-FY2026-revenue-*`, `CU-FY2027-revenue-*` and their
   EPS siblings (append scripts: `consensus_stamp_v2/run.py --append`, already run by WP-M; not re-run
   here) →
4. Package script: `analysis/src/forecast_methods/L0/l0.py` (`pit_consensus`, `pre_guide_street`) reads
   the register; `analysis/src/forecast_methods/consensus_stamp_v2/run.py` (no flag) re-verifies the
   13-Sep append's byte-preserving property against the register on disk →
5. Output consumed by the memo: `deck/drafts/memo_v3_short_2026-09-17.md`, the "Street (LSEG 11 Sep /
   BBG)" table (lines 44–56) and the "How we know the view is variant" paragraph (line 33), which is
   where the 148.9m / 134.0m nights bars are asserted as a single Bloomberg MODL capture.

## 4. Governing sources

| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|
| 2026-09-11 | `A1_consensus_vintages.md` | First same-day multi-vendor capture (Alpha Vantage, Zacks, Yahoo, S&P/StockAnalysis, MarketBeat quarantined); "no adjusted-EBITDA consensus anywhere free"; "no forward nights/ADR/GBV consensus was found on any source reached." | **Governs** vendor identity and the LSEG-family-is-one-panel finding. Its adj-EBITDA absence claim is **superseded** by `03_consensus_pit.md` (below) for anyone with LSEG Workspace access — the two are not in conflict, they differ in which sources were reachable. |
| 2026-09-13 | `M_CONSENSUS_2026-09-13.md` | Re-stamp: 10 new current rows (8 Yahoo/LSEG-family, 2 S&P), Zacks and quarterly S&P unobtainable through the sanctioned fetch route that day; explicitly flags that higher API precision (e.g. $3,161.02M vs the page-rounded $3,160M) is not itself evidence of a revision. | **Governs** the 13-Sep LSEG-family revenue/EPS values used above. Supersedes nothing in A1; extends it. |
| 2026-09-13 (Sat night) | `docs/margin-build/notes/03_consensus_pit.md` (LSEG Workspace desktop pull, `py -3.13`, `lseg-data` 2.1.1) | Full daily PIT panel for adjusted EBITDA, revenue, EPS, EBIT, net income, FCF etc., 4Q20–2Q27 / FY2020–FY2028, one row per trading day; explicit line: **"'published 3Q26 adjusted-EBITDA consensus retrievable' is now superseded: LSEG has $2,361.5M (n=36)."** | **GOVERNS** every adj-EBITDA and EPS row above; this is the only source for those metrics and it explicitly names what it supersedes (A1's free-web absence finding). Not in the reproducible-packages list for this brief (read-only source, `data/processed/margin_build/03_consensus_pit/`), so it is cited but not re-run. |
| 2026-09-14 | `G1b_dolthub_consensus_history.md` | Appends DoltHub `post-no-preference/earnings` as a second vintage-stamped vendor, 1,159 ABNB rows; T1 vendor-equivalence PASS on both pre-registered lines (median \|diff\| 0.48% pre-guide, 0.0% at-print). Interpretation section: "the 13 Sep 2026 [DoltHub] rows equal the 11 Sep Zacks capture to the dollar and to the analyst" — DoltHub's current snapshot is a Zacks mirror, not an independent panel. | Governs register mechanics and the "don't double-count DoltHub against Zacks" rule; does not add a fourth independent revenue panel to §2 above. |
| 2026-09-13 | `LANE2_DATA_CONVENTION_AUDIT.md` / `docs/thesis-kernel-topdown/lane2/CONVENTION.md` | The PIT convention: a guide-date vintage may use everything dated on or before it; `role=pre_guide`/`role=at_print` rows are the historical-backtest Street, `role=current` rows (this dossier's whole table) are September-2026 vintages and are **never** admissible at a historical date. | **Governs** how every row in §2 must and must not be used downstream — none of them may be substituted into a historical W1/W2 test. |
| 2026-09-17 | `deck/drafts/memo_v3_short_2026-09-17.md` | Latest note chronologically; asserts "Bloomberg MODL, 12 Sep: 28 estimates for 3Q26 nights, low 147.0m, mean 148.9m, high 151m." | **Does not govern the 148.9m level** — it is internally inconsistent with its own cited source (`E_street_distribution_vs_team.csv`, same 12-Sep MODL screenshot, mean 149.0m) and with `research/notes/reverse_dcf/` files that attribute 148.9m to a separate 4-Sep "Bloomberg FA" capture. Being the latest note is not sufficient to govern when the note itself misattributes its number; flagged unresolved, not adjudicated (§7). |

## 5. Reproduction receipt
- Receipts: `data/processed/pitch_model_v2/receipts/V1/receipt.json` (primary) and
  `data/processed/pitch_model_v2/receipts/V1/receipt_l0_pytest.json` (secondary, saved by hand because
  the wrapper's fixed per-id path would otherwise have overwritten the first run — both are legitimate
  runs against this line's own commit).
- **Primary — the package that actually produced most of the rows above.**
  Command: `python3 analysis/src/forecast_methods/consensus_stamp_v2/run.py` (run via
  `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id V1 --watch data/processed/forecast_methods/consensus_stamp_v2 --cmd "python3 analysis/src/forecast_methods/consensus_stamp_v2/run.py"`)
  · Exit: **1** · Wall: 0.0s · Interpreter: `python3` (plain; no pandas-3 failure, `.venv-pd2` not needed).
  Output: none written (script raised before writing) · Committed value: n/a · Tolerance: n/a ·
  **Match: no.**
  Why: `run.py`'s offline `verify()` step asserts the current register's logical SHA-256 equals the
  `after_lf_sha256` recorded in `append_receipt.json` at the moment of WP-M's 13-Sep append (register
  then: 171 data rows). The register has since grown to **1,320 data rows** (WP `G1b`'s DoltHub append,
  14 Sep, per its own note, and further nine-digger parallel activity in this clone per the operational
  notes) — an authorized, append-only change, not corruption. `run.py`'s verify mode checks one specific
  append event's byte-preservation, not "does the register still exist and hold these values"; it has no
  way to succeed once the register has legitimately moved on. `git status --porcelain` on the watched
  path was clean before and after the run (no contention with the other diggers); the wrapper's own
  `restored: true` confirms nothing was left dirty.
- **Secondary — the frozen invariant this line's PIT hard rule rests on.**
  Command: `python3 -m pytest analysis/src/forecast_methods/L0/test_l0.py -q` (via the same wrapper,
  `--watch data/processed/forecast_methods/L0 --watch analysis/src/forecast_methods/L0`) · Exit: **0** ·
  Wall: 0.4s · Interpreter: `python3`.
  Output: `test_l0.py::test_six_august_pre_guide_street_is_lseg_4610` — `l0.pre_guide_street("2026Q3")` ·
  Committed value: vendor `LSEG`, value `4610.0` · Reproduced value: vendor `LSEG`, value `4610.0` ·
  Tolerance: exact · **Match: yes.** 20/20 frozen L0 tests pass; only three new `.pyc` cache files
  appeared, restored/cleaned, no tracked file changed.
  This confirms the register's PIT scaffolding (the frozen 6-Aug pre-guide hard rule that every
  `role=current` row in §2 sits downstream of) is intact — but it reproduces a *different* object (the
  historical pre-guide Street) from the ones §2 actually asks for (September-vintage current Street). It
  is evidence the infrastructure works, not a reproduction of any §2 cell.

## 6. Test record

| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
| n/a | n/a | — | — | — | — | — | This line is a data-stamping deliverable (vendor-attributed consensus levels), not a fitted forecast; it has no W1/W2 predictive claim of its own to score. | n/a |
| for context only | W1=14, W2=10 | RMSE ratio to naive, `l0-dolthub-v2 / street_dolthub` (the one Street object G1b did register and score) | W1 1.146, W2 0.881 | 1.0 by construction | `baselines/street` W1 1.073 / W2 0.871 (near-identical shape) | — | survive both W1 and W2 (beat naive) | **fail** — beats naive on W2 only, same as the press-quote Street baseline |

Strongest known failure: **the memo's own headline nights bar (148.9m, "Bloomberg MODL, 12 Sep, 28
estimates") does not reproduce from the capture file it cites for that exact screenshot — that file's
28-estimate mean is 149.0m — and 148.9m instead matches an unrelated, earlier 4-Sep Bloomberg capture, so
the short thesis's stated "fourth accelerating bar" evidence carries an unresolved 0.1m vendor/date
mix-up at its own citation.**

## 7. Kill list and consistency
- Kill-list check: none of AGENT_BRIEF.md §6's items are used or quoted as ours in this dossier. No
  restated-unearned-fees number, no "82%"/FX-step figure, no drift-rule p-value appears here.
- Conflicts:
  1. **3Q26 nights bar, 148.9m vs 149.0m** (§2/§4 above) — unresolved. This is the strongest inconsistency
     found in this line and is the one the memo's own "variant view" argument leans on hardest.
  2. **LSEG-family vs Zacks, named by the brief** — 4Q26 revenue ($3,158–3,162M vs $3,200M, ~$40M/1.3%),
     FY26 revenue ($14,155–14,190M vs $14,100M, ~$60–90M), FY27 revenue ($15,758–15,819M vs $15,740M,
     ~$20–80M). Not a data error; Zacks is consistently the thinnest panel (n=7–13 vs n=35–44) and has been
     stable at each level since its 4-Sep vintage while the LSEG-family panel has drifted slightly upward
     with recapture. Neither side is favored here (rule 6).
  3. **FY27 adj-EBITDA margin, two bases from the same LSEG pull**: implied (mean EBITDA ÷ mean revenue)
     36.45% vs LSEG's own separately-averaged margin field 35.06% — a 1.4pt gap from computing the ratio
     two different ways on the same day's data (`03_consensus_pit.md` lines 209/248). Memo v3 quotes
     36.5%, i.e. the implied basis, without naming the alternative.
  4. Per the LANE2 convention, every row in §2 is `role=current` (September 2026 vintage) and must never
     be substituted into a historical guide-date or print-date test; none of the packages this dossier
     touched attempted that substitution.
  5. **DEC-0018 gap: no FY26 or FY27 Street take rate.** `street_take_rate_pct` is added to §2a for 3Q26
     (17.98%) and 4Q26 (13.77%) only, because the Bloomberg MODL screenshot (12 Sep 2026, Krish) — the
     one source anywhere with a vendor-stamped forward nights and ADR — is quarterly-only: it has no FY26
     or FY27 nights or ADR row (A1 §3, exhaustive free-web check, confirms the same absence; `D_sell-side-
     dispersion.md` states directly: "nobody publishes an FY27 nights estimate"). No row is derived for
     either annual period; deriving one would require a nights or ADR number this dossier's sources do
     not contain. Nearest available substitutes, for the humans to choose from (not adopted here): (a)
     the two quarterly MODL take rates already in §2a (17.98% / 13.77%) as a floor/ceiling band for
     FY26/FY27, since 2H26 dominates the FY sequence; (b) `D_sell-side-dispersion.md`'s FY27 *derived*
     nights range (+8.0% to +9.0% on the delivered/Zacks FY26 base — explicitly labelled JUDGEMENT, not a
     consensus, and out of scope for a `street_*` row per this brief's vendor-attribution rule); (c) hold
     the FY26/FY27 take rate flat at the FY26-to-date printed level and let the revenue/EBITDA rows in
     §2a carry the disagreement instead.

## 8. Open choices
1. **Which 3Q26 nights bar number goes in the memo: 148.9m or 149.0m, and from which Bloomberg
   screen.** Options: (a) correct the memo to 149.0m (MODL, 12 Sep, n=28, the file actually cited);
   (b) keep 148.9m but re-attribute it correctly to "Bloomberg FA, 4 Sep" and drop the "28 estimates"
   framing (FA displays a single figure, not a panel mean); (c) re-pull the MODL screenshot to confirm
   149.0m is still current and treat 148.9m as a stale draft artifact. **Recommendation: (a)** — the
   dossier's own §2 table and the CSV it is built from agree at 149.0m; re-attributing an old FA figure
   (b) keeps two live numbers in play for no benefit, and the growth-rate rounding (both read "+11.5%")
   is exactly the kind of near-miss that lets a wrong number survive a spot check.
2. **Whether to quote a single "the Street" 4Q26/FY26/FY27 revenue number in the memo, or keep both
   LSEG-family and Zacks rows visible.** Options: (a) keep both, as this dossier does, and let the reader
   see the ~1.3% (4Q26) to ~0.6% (FY27) spread; (b) pick LSEG-family as "the Street" because it is the
   thicker panel (n=35–44 vs n=7–13) and is the basis memo v3 already uses for its EBITDA/EPS/margin
   rows; (c) pick the DoltHub/Zacks reading because two independent capture routes (Zacks page, DoltHub
   API) agree to the dollar. **Recommendation: (b)**, with the Zacks row kept as a labelled footnote —
   consistent with how the rest of memo v3's table already treats LSEG as the headline "Street" column.
3. **Whether FY27 adj-EBITDA margin should be quoted on the implied basis (36.45%) or LSEG's own margin
   field (35.06%).** Options: (a) implied, as memo v3 already does (36.5%); (b) LSEG's own field
   (35.06%), which is a distinct, separately-modeled series, not a derived ratio; (c) show both with the
   1.4pt gap stated every time. **Recommendation: (c)** — the two bases disagree by more than the
   Street's own historical FY-floor-anchoring gap (`03_consensus_pit.md` §5, ~0.5pt), so picking one
   silently understates how uncertain "the Street's FY27 margin" really is.
4. **Whether `consensus_stamp_v2/run.py`'s offline verify mode should be re-scoped** so it can still be
   run as a smoke test after other packages have legitimately extended the register (currently it can
   only ever pass once, immediately after its own append). Options: (a) leave it as a point-in-time
   append-integrity check only, and rely on `L0/test_l0.py` for ongoing register health (what this
   dossier did); (b) add a mode that re-derives "is my 10-row append still present and byte-correct as a
   subsequence" rather than "is the whole file still byte-identical to my snapshot." **Recommendation:
   (b)** for the next agent who needs to re-verify WP-M's specific contribution after further appends —
   not something this digger's lane is authorized to build (out of scope: only `consensus_stamp_v2`,
   `L0_dolthub_v2` read-only, and their own output paths).

## 9. Judge Q&A
1. Q: Which consensus, from whom, as of when, for 3Q26 and 4Q26 revenue? A: 3Q26 revenue $4,744M,
   LSEG-family (LSEG Refinitiv Workspace as-of 2026-09-11, cross-checked by Yahoo/Alpha Vantage/S&P/
   Zacks the same week, spread only $2.5–8M — near-unanimous). 4Q26 revenue is genuinely two numbers:
   $3,158–3,162M from the LSEG-family panel (n=35–37, as-of 2026-09-10/13) versus $3,200M from Zacks
   (n=10, unchanged since 4 Sep) — a real ~$40M/1.3% split the memo should carry as two rows, not one.
2. Q: Is the "Street expects an accelerating 3Q26 nights print" claim, the pivot of the short thesis,
   actually reproducible? A: The direction (Street above the team's own +9.5% nowcast) reproduces
   cleanly — every reading, 147–151m or 148.9–149.0m, sits well above any team estimate. The exact level
   quoted in the memo (148.9m, attributed to a 12-Sep, 28-estimate Bloomberg MODL screenshot) does not
   reproduce from that screenshot's own transcription (149.0m); it matches a different, earlier
   4-Sep Bloomberg capture instead. The thesis's direction survives; its headline number needs a one-line
   correction.
3. Q: Can any of these numbers be used in the historical W1/W2 backtests the rest of the model runs? A:
   No. Every row here is `role=current` (September 2026 vintage) under the register's own convention
   (`docs/thesis-kernel-topdown/lane2/CONVENTION.md`); using one at a historical guide or print date would
   repeat the exact mistake that note was written to prevent. This dossier's numbers feed the memo's
   forward comparison table only.

## 10. Grade
Grade: C — the receipt for the package that actually produced most of §2's rows
(`consensus_stamp_v2/run.py`) exits 1 today, because its offline verify step checks one specific 13-Sep
append event against the register's current bytes, and the register has since grown legitimately (WP
`G1b`'s 14-Sep DoltHub append plus nine parallel diggers in this clone) — an expected, not a data,
failure, but a failure of the only reproduction path this brief authorizes for the object in question.
The one clean, exit-0 reproduction obtained (`L0/test_l0.py`, the frozen 6-Aug pre-guide $4,610M hard
rule) confirms the register's PIT scaffolding is sound but reproduces an adjacent historical object, not
any of the September-vintage "street" cells §2 asks for. No W1/W2 survival claim applies (this is a data
line, not a fitted forecast), and the line's own headline number (the 148.9m nights bar) carries an
unresolved vendor/date mix-up at its citation (§4, §7). B was considered and rejected because "reproduced"
should mean the reproduction of this line's actual required objects succeeded, not an adjacent one.
