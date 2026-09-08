# templates/ — SIG CSV schemas worth cloning for ABNB

Copied files are SIG data, kept only for their column layout and the discipline they encode. Build the ABNB versions with the same columns and the same sourcing rule: **every hard number carries a `file:line` or filing reference in a `source` column.**

## `kpi_panel_quarterly.csv` (from `forward_exhibits.py`)

SIG columns: quarter, call_date, sss_pct, revenue, AUR splits, units text, merch margin bps, gross margin bps, LGD penetration, attach bps, inventory, qualitative texts, buyback text, source, then derived (implied_units_pct) and merged alt-data columns (gold, promo depth, Tenoris).

ABNB mapping (one row per quarter since Q4-2020):

| SIG column | ABNB column | Source |
|---|---|---|
| sss_pct | nights_and_experiences_booked, nights_yoy_pct | shareholder letter |
| revenue_musd | gbv_musd, revenue_musd, revenue_fx_neutral_yoy | letter |
| merch_aur_pct | adr_usd, adr_yoy_pct, adr_fx_neutral_yoy | letter |
| implied_units_pct (derived) | implied_adr = gbv/nights; take_rate = revenue/gbv; nights_ex_experiences (when disclosed) | derived |
| merch_margin_bps_yoy | adj_ebitda_musd, adj_ebitda_margin_pct, fcf_musd, fcf_margin_pct | letter |
| inventory / services text | active_listings_text, supply_growth_text, region_growth_text (NA / EMEA / LatAm / APAC) | letter + call |
| buyback_text | buyback_musd, sbc_musd, diluted_shares_m, net_share_change_pct | letter, 10-Q cover page |
| gold / promo / Tenoris merges | bea_accommodations_yoy, str_revpar_yoy (if obtained), trends_share_of_search, similarweb_visits, card_panel_yoy | your alt-data pulls |

The SIG deck's single best unbuilt-then-built exhibit was a *derived* series nobody had computed (implied unit comps). The ABNB analog: **take rate by quarter with FX and mix stripped out**, and **implied ADR vs BEA hotel price index** (is Airbnb pricing above or below hotels?).

## `bear_scoreboard.csv` (from `deck_charts_v2.py`)

Columns: KPI, bear's dated prediction (with their fiscal year fixed), our number, latest actual, next print / tracker. Built from the VIC short's transcribed model. For ABNB, populate from the best-articulated published bear (VIC / a short report) and keep it live every print. The SIG correction C17 (mislabeling the bear's fiscal years) is the error to avoid: pin every bear number to a calendar quarter.

## `print_day_moves.csv`

Columns: date, fiscal quarter, quarter number, close-to-close move %. Feed for the print-day distribution chart and the "40% of prints exceed the implied move" line. ABNB: ~22 prints since IPO; note ABNB reports after market close, so the reaction day is T+1 (SIG was pre-market, same day). Adjust the convention and state it.

## `sig_notable_moves.csv`

Columns: Date, type (1-day / 5-day / curated), pct_move, Close, Volume, category, explanation, confidence (H/M/L). Method: top-30 |1-day| and top-25 non-overlapping 5-day moves computed first, then attributed from 2+ independent sources or the 8-K calendar; unexplained stays unexplained. This fed the annotated decade chart artifact. Same process for ABNB from Dec-2020.

## Consensus-at-call (`../data/bb_consensus_at_call.csv`)

Columns: page, company, date, event, mktcap, price, ytd change, consensus EPS Q/FY, consensus sales Q/FY. Comes free from the Bloomberg transcript export page headers.

## Document templates worth cloning (in `SIG/`, no CSV)

- **Corrections ledger** (`research/00_MASTER_SYNTHESIS.md` §1; `DATA_INVENTORY` §2): numbered table of old claim → corrected finding → source. SIG accumulated 33 corrections across two weeks; several would have been judge kill-shots. Start the ABNB ledger on day one.
- **Expectations map** (`research/sept9_expectations.md`): guidance detail → street consensus by aggregator → whisper proxies → revision direction → analyst actions log → alt-data scoreboard → positioning (price action, options, SI, 13F, insiders, buyback) → peer read-throughs → scenario map with reaction function. Build for the early-November ABNB print.
- **Pre-registered prediction card** (deck S12): numeric predictions dated before the print, with the falsifier for each pillar and the tracker that resolves it.
- **Data digest** (`DATA_DIGEST_2026-09-02.md`): decision-organized readable layer over the big inventory, with ✅/◐/✗ build status. Pair every large reference doc with one of these (Obsidian convention in memory).
