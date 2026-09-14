# Market-implied case: shared brief for the 12-13 Sep 2026 overnight run

Owner: Krishang (asleep; do not wait for answers). Branch `krish/reverse-dcf`, worktree `C:\Users\krish\citadel-abnb-reversedcf`. Every agent works in this worktree, writes only to its own paths (below), and does not commit; Krish's session commits at the end.

## The question

The management half is done (`research/notes/2026-09-12_management-implied-model.md`, `model/ABNB_management_implied.xlsx`): if what management says is true the stock is worth $174 / $182 / $196 (literal / delivered / ambition) at mid multiples, and consensus FY27 ($15.75bn revenue, $6.08 EPS) is exactly the "delivered" case. The market half asks: **what does the share price, the options market and the sell-side tape imply for revenue, nights, ADR, GBV, margin and the 5 Nov print, and how does that compare with management's case and the team's own forecasts?** Krish's decisions on approach:

1. The current price is the market's fair value; the sell-side mean and the options distribution are separate checks (not "price plus a bit").
2. Try the joint solve first (WS12: the multiple moves +0.48 turns of EV/NTM EBITDA per point of forward revenue growth, so growth and multiple are solved together); if it does not produce a sensible answer, fall back to the simple hold (fixed multiple, solve for revenue; fixed revenue, solve for multiple). Report both.
3. Decompose revenue into nights / ADR / FX / take rate only where a real anchor exists (Bloomberg FA quarterly consensus for 3Q26 and 4Q26; the team's elasticities). **Krish's team has found that nights growth, and in particular accelerating vs decelerating nights guidance, does move the stock and the multiple**; treat nights as a priced variable, not just a residual of revenue.
4. Options: straddle and skew are enough; do not build a full risk-neutral surface unless it falls out cheaply.
5. Produce a **range**: the market-implied numbers at several price points, not one.

## Anchors (do not re-derive; cite this brief)

| Item | Value | Source |
|---|---|---|
| Price | $170.19, close 11 Sep 2026 (fell from $181.94 on 4 Sep to $167.65 on 10 Sep around the 8 Sep Communacopia fireside; no company news) | yfinance |
| Diluted shares | 597.0m (2Q26 diluted WA); basic 589.6m at 15 Jul 2026 (419.5m A + 170.1m B); 37.8m RSUs, 5.7m options | 10-Q |
| Net cash ex float | $9,593m ($12,069m cash + ST investments less $2,476m senior notes; funds held for clients excluded) | 10-Q 2Q26 |
| Market cap / EV at $170.19 | $101.6bn / $92.0bn | arithmetic |
| Management "delivered" case | FY26 rev $14,231m (+16.3%), margin 36.2%, EPS $5.37, FCF $5.3bn; FY27 rev $16,025m (+12.6%), EBITDA $5,801m, margin 36.2%, EPS $6.08, FCF $5.9bn, end-FY27 net cash $10.6bn, 4Q27 diluted shares 570.7m; 3Q26 nights +11.5%, rev $4,815m; 4Q26 nights +10.5%, rev $3,130m | `data/processed/reverse_dcf/mgmt_implied_summary.csv` |
| Management "literal" / "ambition" FY27 | rev $15,630m / $16,791m; EBITDA $5,549m / $6,213m; EPS $5.72 / $6.68 | same |
| Team base (WS29/30) | 3Q26 nights +9.9%, rev $4,771m; 4Q26 nights +8.9% (8.0-8.2% if the ex-NA lap is adopted), rev $3,111m; FY26 $14,168m, 36.2%; FY27 $15,804m (+11.6%), 36.4%, EPS $5.90 | `data/processed/overnight/29_*`, `30_*` |
| Street | 3Q26 rev $4,744m, nights 148.9m (+11.1%), GBV $26.35bn (+15.1%), ADR $177.0 (+3.3%), EBITDA $2,360m (49.7%), EPS $2.87-2.88; 4Q26 rev $3,154-3,200m, nights 134.2m (+10.1%), GBV $23.0bn (+12.7%), ADR $171.3 (+2.3%), EBITDA $915m (29.0%), EPS $0.82-0.85; FY26 rev $14,100-14,160m, EPS $5.23-5.28, FCF $5.35bn; FY27 rev $15,730-15,760m (range 14,990-16,290, 13 est.), EPS $6.02-6.14 (range 5.35-6.80) | Bloomberg FA PDF 4 Sep (`data/raw/theo_onedrive/AIRBNB DATA/instOf_bdd692f4-49c2-46a0-8d41-fd50f7ae5c5e.PDF`), Zacks 4 Sep, S&P 3 Sep (`04_current_consensus.csv`) |
| Sell-side targets | 31 live targets: mean $179.5, median $175, p25 $165, p75 $197.5, min $125 (Morgan Stanley), max $220 (Rosenblatt, DA Davidson); S&P 46-analyst mean $178.96; yfinance 11 Sep mean $182.1, median $185 (40 opinions); implied EV/FY27 EBITDA per target already in the file | `data/processed/overnight/12_analyst_targets.csv`, `12_analyst_target_summary.csv` |
| WS12 multiple regression | EV/NTM EBITDA on NTM revenue growth: +0.477 turns per point (t 2.3 on 45 monthly obs 2023-26, R2 0.24 with margin, Newey-West); +0.48 t 8.3 in levels, +0.49 t 5.6 in 12-month changes per the synthesis; margin coefficient insignificant (t 0.3-0.4). ABNB actual 18.5x on 4 Sep vs cross-section fits 12.0-15.6x | `12_abnb_multiple_regressions.csv`, `12_abnb_multiples_monthly.csv`, `research/notes/overnight/12_valuation-multiple-regime.md` |
| Exit multiples the team supports | EV/FY27E EBITDA 13.5 / 16.5 / 18.5x; P/E 22 / 27 / 30x; EV/FCF 14 / 17 / 20x | WS12 and the management note |
| Elasticities | 1pt of 3Q26 nights = ~$259m GBV = ~$46m revenue = ~1% of quarterly EBITDA; 1pp ADR = $1.71 = $259m GBV = $46m revenue (H note) | `research/notes/q3nowcast/H_3q26-adr-card.md` |
| Print reactions | 23 prints 4Q20-2Q26; executable next-open entry returns; 71% of the absolute print-day move is multiple (84% on moves of 7%+); 2Q26 +17.4% on an estimate change of -0.2%; 41 moves of 7%+ since IPO | `20_executable_returns.csv`, `20_prediction_ledger.csv`, `12_print_move_attribution.csv`, `abnb_earnings_reactions.csv`, `abnb_major_moves_events.csv`, `04_reaction_panel.csv`, `04_reaction_tests.csv` |
| Consensus at each print | revenue 23/23, next-Q revenue 18/23, EPS 17/23, nights 18/23, GBV 12/23 | `04_consensus_at_print.csv`, `16_consensus_at_print_merged.csv` |
| Guidance ledger | 194 statements, all 23 prints, with direction (accel/decel) and outcome | `02_guidance_ledger.csv`, `02_kpi_panel_quarterly.csv` (nights_yoy_accel_pts column) |
| Options | Bloomberg workbook built 4 Sep 2026: daily IV/realised/put-call since IPO, ATM term structure 30D-12M with 90/95/105/110 moneyness, 67 monthly ATM straddles Jan 2021-Sep 2026 (implied avg 10.4% vs realised 10.7%; Aug 2026 implied 10.0% vs realised 33.7%), full 4 Sep chain (1,255 contracts with IV): `data/raw/theo_onedrive/AIRBNB DATA/ABNB_Options_Bloomberg_Pull (1).xlsx` (licensed, never commit). Yahoo chains 5-6 Sep in `data/processed/abnb_options_ledger.csv`; live chains via `py -3.13` + yfinance. Prior implied-move work: `09_implied_move_live.json`, `09_implied_vs_realised.csv`, `analysis/src/abnb_options_ledger.py` (the A08 event-variance estimator was flagged as unidentified; check before reusing) |
| Daily prices | `data/processed/abnb_daily_close.csv` to 4 Sep; refresh with yfinance (`py -3.13`); `20_prices_ohlc.csv` |
| Next print | 5 Nov 2026 after close (Zacks expected date 11/5/26) |

## Conventions

- Python: `py -3.13` (has yfinance, pandas, numpy, openpyxl, scipy, matplotlib, pywin32). The venv has no pip. Excel is installed; `analysis/src/reverse_dcf/mgmt_implied_model.py` shows how to recalc a workbook through COM.
- Label every number as one of: ANCHOR (from this brief), MEASURED (computed from data, say which), JUDGEMENT (yours, say why). Report negatives as fully as positives.
- Walk-forward or leave-one-out for anything fitted; report n, t, R2; say what would change the conclusion.
- Every quote from a call or letter must be verbatim; every consensus number must carry vendor and date.
- Write notes in plain prose with tables, no em-dashes, numbers in tables not sentences. Lead with the answer.
- Do not touch `model/ABNB_management_implied.xlsx`, `model/ABNB_driver_model.xlsx` or anything outside your paths.
- Licensed data (Bloomberg workbook, PDF) may be read and summarised; never copied into a committed file.

## Workstreams and paths

| WS | Question | Scripts | Outputs | Note |
|---|---|---|---|---|
| A | Joint solve: what FY27 revenue growth, EBITDA and nights does each price point imply, with the multiple endogenous (WS12) and with the multiple held; decomposition into nights / ADR / FX / take rate at the anchored quarters | `analysis/src/reverse_dcf/A_*.py` | `data/processed/reverse_dcf/A/` | `research/notes/reverse_dcf/A_joint-solve.md` |
| B | Options: 5 Nov implied move (straddle, term-structure event variance), skew (up vs down), 12-month implied price distribution percentiles, historical print-move base rate vs implied | `analysis/src/reverse_dcf/B_*.py` | `data/processed/reverse_dcf/B/` | `research/notes/reverse_dcf/B_options-implied.md` |
| C | Reaction function: how the stock and the multiple respond to nights acceleration / deceleration, guide direction, revenue and EPS surprise; what 3Q26 print and 4Q26 guide is "priced" (zero expected move) given B's implied move | `analysis/src/reverse_dcf/C_*.py` | `data/processed/reverse_dcf/C/` | `research/notes/reverse_dcf/C_reaction-function.md` |
| D | Sell-side dispersion: what each live target implies (multiple, FY27 EBITDA/revenue, nights), the p25/mean/p75 range, what the bulls and bears each assume, rating and target revision history around prints | `analysis/src/reverse_dcf/D_*.py` | `data/processed/reverse_dcf/D/` | `research/notes/reverse_dcf/D_sell-side-dispersion.md` |
| Audit | one auditor per workstream, then one on the synthesis | | `data/processed/reverse_dcf/audit/` | `research/notes/reverse_dcf/audit_*.md` |
| Synthesis | `model/ABNB_market_implied.xlsx` (formula-driven, same conventions as the management workbook), `research/notes/2026-09-13_market-implied-model.md`, `docs/reverse_dcf/SYNTHESIS.md` | `analysis/src/reverse_dcf/market_implied_model.py` | `data/processed/reverse_dcf/market/` | |

Price points every workstream must report against (the "range"): **$150 (bear tape), $165 (p25 target), $170.19 (price), $179.5 (mean target), $185 (median yfinance target), $197.5 (p75 target), $220 (top target)**, plus B's options-implied 1-year p25 / p50 / p75 once B has them (synthesis adds those).
