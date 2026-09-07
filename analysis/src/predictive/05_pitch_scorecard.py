"""
05_pitch_scorecard.py -- score earlier ABNB pitches and research pieces against what happened.

Inputs (all in the repo):
  research/notes/2026-09-04_abnb-pitch-landscape.md and 2026-09-04_abnb-pitch-catalogue.md
      -> the pitch table below is hand-transcribed from those two notes (dates, stance, PT, KPIs, method).
  research/airbnb_earnings_call_study.md (sec. 3.1, 5, 8) and research/notes/2026-09-05_margin-drivers.md
      -> the outcome record used to judge whether each thesis's KPI direction happened.
  data/raw/prices/ABNB_daily.csv, data/raw/prices/QQQ_daily.csv (yfinance, adj_close; gitignored)
  data/processed/abnb_quarterly_cost_stack_exsbc.csv, abnb_fcf_bridge.csv, abnb_kpi_vs_category_quarterly.csv,
  data/external/abnb_revenue_guidance_vs_actual.csv, capital_return_scorecard_annual.csv
      -> numbers for the metrics nobody used.

Outputs:
  data/processed/predictive/05_pitch_scorecard.csv
  data/processed/predictive/05_metric_usage.csv
  (summary printed to stdout; the note research/notes/predictive/05_pitch-scorecard.md is written by hand from it)

Scoring rules (kept deliberately simple, stated in the note):
  * price_at_date = ABNB adj close on or before the pitch date; returns are close-to-close (ABNB pays no dividend).
  * Windows: 3m = +91 days, 6m = +182, 12m = +365, "to date" = last close (2026-09-04). A window that ends after
    the last close is left blank (unfinished).
  * Evaluation window for the direction call = the pitch's own horizon if it has finished (12m for sell-side,
    longer for DCF pieces), otherwise to date (flagged provisional). Rows under 60 days old are "too early" and
    excluded from win rates.
  * long right if ABNB return > 0; short right if < 0; hold right if |return| <= 10%.
  * target reached = ABNB traded through the PT in the right direction (max close >= PT for longs/holds above
    price, min close <= PT for shorts/holds below price) between the pitch date and the end of the stated horizon
    (or last close if the horizon is open).
  * call_quality: direction right and target reached = 2; direction right (or no target to reach) = 1; wrong = 0.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(r"C:\Users\krish\citadel-abnb-predict")
PRICES = ROOT / "data" / "raw" / "prices"
OUT = ROOT / "data" / "processed" / "predictive"
OUT.mkdir(parents=True, exist_ok=True)
AS_OF = pd.Timestamp("2026-09-04")  # last close before the 2026-09-05 write-up date

# ----------------------------------------------------------------------------------------------------------------
# 1. The pitches. One row per dated pitch or research piece. KPI tags use the controlled vocabulary in METRICS.
#    horizon_m = months the target is meant for (12 for sell-side by convention; DCF pieces as stated).
#    thesis_kpi_happened: did the KPI direction / catalyst the thesis leaned on actually occur, judged against the
#    earnings-call study KPI table (nights 7% 2Q25 -> 10% 2Q26; ADR +5-9%; take rate 13.2% flat, LTM -31 bps,
#    guided flat for 2026; EBITDA margin floor >=35.5%; buybacks ~$1.1B/qtr; SBC 13% of revenue).
# ----------------------------------------------------------------------------------------------------------------
P: list[dict] = []


def add(**kw):
    P.append(kw)


add(pitch_id="P01", date="2024-09-17", author="Disruptive Analytics (M. Ofstad)", kind="Substack", direction="long",
    lean="bull", price_target=120.0, horizon_m=12, valuation_method="Fair value (DCF-style)",
    primary_thesis="Unpriced optionality in Experiences and event hosting; fair value ~$120 vs $117.55",
    kpis="experiences_services;take_rate;revenue_growth", framing="optionality / new businesses",
    thesis_kpi_happened="partly",
    outcome_note="Take rate stayed flat as feared (13.6% FY24 -> 13.4% FY25); Experiences still immaterial; stock re-rated on nights instead.",
    source="catalogue #disruptive-2024-09-17", date_flag="")
add(pitch_id="P02", date="2024-11-17", author="Wolf of Harcourt Street (bull case)", kind="Substack", direction="long",
    lean="bull", price_target=np.nan, horizon_m=12, valuation_method="Forward P/E (29x)",
    primary_thesis="Core enhancements plus new ventures; buybacks shrinking share count",
    kpis="nights_growth;fcf_margin;buybacks_share_count;experiences_services", framing="optionality / new businesses",
    thesis_kpi_happened="partly",
    outcome_note="Buybacks continued (diluted shares -3.4% in 2025) and FCF held ~37%; author sold seven months later on the Q1'25 slowdown, so the thesis was abandoned before it paid.",
    source="catalogue #wolf-2024-11-17", date_flag="")
add(pitch_id="P03", date="2024-11-20", author="Henry Fund, U. Iowa (Opeloyeru)", kind="Student report", direction="hold",
    lean="neutral", price_target=140.0, horizon_m=12, valuation_method="50% DCF/EP + 50% relative P/E",
    primary_thesis="Fairly valued asset-light platform; 7.5% nights CAGR, 14% take rate fading to 13.5%",
    kpis="nights_growth;take_rate;ebitda_margin;pe_multiple", framing="valuation multiple / fair value",
    thesis_kpi_happened="partly",
    outcome_note="Nights ran 8-10% (above the 7.5% CAGR); take rate came in below 14% (13.2-13.5%). Hold missed a +34% move.",
    source="catalogue #henry-2024-11-20", date_flag="")
add(pitch_id="P04", date="2025-01-02", author="Speedwell Research (Deep Dive, 108 pp)", kind="Research (paid)", direction="long",
    lean="bull", price_target=np.nan, horizon_m=36, valuation_method="Not visible (paywalled)",
    primary_thesis="Highly profitable platform with 90% unpaid traffic; a new $1B business every year; regulation the Achilles heel",
    kpis="unpaid_traffic_share;fcf_margin;experiences_services;regulation", framing="optionality / new businesses",
    thesis_kpi_happened="partly",
    outcome_note="Unpaid traffic still ~90% but S&M grew 1.5x revenue; no new $1B business yet (management: 3-5 yrs); regulation contained (no city >2% of revenue).",
    source="catalogue #speedwell-2025-01-02", date_flag="paywalled: PT not visible")
add(pitch_id="P05", date="2025-01-21", author="Summit Stocks (Lucas), 'Airbnb Stock in 2025'", kind="Substack", direction="long",
    lean="bull", price_target=np.nan, horizon_m=60, valuation_method="20-yr DCF on FCF (2.5% terminal)",
    primary_thesis="Great company at a fair price; 9-13% expected annual return; core to 1B nights",
    kpis="nights_growth;fcf_margin;experiences_services", framing="optionality / new businesses",
    thesis_kpi_happened="partly",
    outcome_note="Nights growth accelerated (7% -> 10%) but TTM nights ~560M, far from 1B; no new $1B business.",
    source="catalogue #summit-2025-01-21", date_flag="")
add(pitch_id="P06", date="2025-02-19", author="Byte Alchemist", kind="Substack", direction="long",
    lean="bull", price_target=239.0, horizon_m=120, valuation_method="10-yr DCF (conservative $210-268; midpoint used)",
    primary_thesis="Fairly valued core with unpriced optionality in Experiences, loyalty, ads, hotels",
    kpis="nights_growth;take_rate;fcf_margin;buybacks_share_count;experiences_services", framing="optionality / new businesses",
    thesis_kpi_happened="partly",
    outcome_note="Hotels became real (3x growth); loyalty and ads not launched (sponsored listings 2027); FCF $4.8B TTM vs $4.5B cited. Bought at a local high; lagged QQQ.",
    source="catalogue #byte-2025-02-19", date_flag="")
add(pitch_id="P07", date="2025-02-26", author="Eremos Notes (J. Mayhew), 'Thesis Update'", kind="Substack", direction="long",
    lean="bull", price_target=350.0, horizon_m=60, valuation_method="DCF to 2029, 25x EBIT exit, 3 scenarios; ventures separately",
    primary_thesis="Market too conservative after NA slowdown; take rate to 14% by 2029, 44% terminal EBIT margin, new ventures $70/sh",
    kpis="take_rate;ebitda_margin;sm_intensity;buybacks_share_count;experiences_services;nights_growth", framing="take-rate expansion bull",
    thesis_kpi_happened="partly",
    outcome_note="Right that the market was too conservative (stock +26%); wrong so far on take rate (LTM -31 bps to 13.2%, guided flat, host-fee cut test) and on margin expansion (floor 35.5%, not rising).",
    source="catalogue #eremos-2025-02-26", date_flag="")
add(pitch_id="P08", date="2025-05-14", author="Emerging Moats / Chit Chat Stocks (B. Schafer)", kind="Substack", direction="long",
    lean="bull", price_target=np.nan, horizon_m=120, valuation_method="Qualitative",
    primary_thesis="Never sell; Services/Experiences convert luxury-hotel customers; supply is the constraint",
    kpis="experiences_services;supply_listings_occupancy", framing="optionality / new businesses",
    thesis_kpi_happened="no",
    outcome_note="Experiences/Services still 'not material' (management, 3-5 yrs); the conversion story that worked was hotels-to-homes, not Experiences. Stock +32% anyway.",
    source="catalogue #emergingmoats-2025-05-14", date_flag="")
add(pitch_id="P09", date="2025-06-09", author="Wolf of Harcourt Street (exit note)", kind="Substack", direction="short",
    lean="bear", price_target=np.nan, horizon_m=12, valuation_method="Trailing/forward P/E (35x/31.5x)",
    primary_thesis="Good business, no longer a good stock: nights +8% slowest since Covid, ADR -1%, op margin down, Services weak",
    kpis="nights_growth;adr;ebitda_margin;experiences_services;pe_multiple", framing="slowing-demand bear",
    thesis_kpi_happened="no",
    outcome_note="Nights went 8% -> 7% -> 9% -> 10% -> 9% -> 10%; ADR +3% to +9%; FY margin 35% then guided >=35.5%. Every KPI reversed within two quarters.",
    source="catalogue #wolf-2025-06-09", date_flag="")
add(pitch_id="P10", date="2025-08-16", author="Compounding Your Wealth (Sergey)", kind="Substack", direction="long",
    lean="bull", price_target=np.nan, horizon_m=12, valuation_method="Forward P/E (27.6x)",
    primary_thesis="Q2'25 beat, new verticals, $6B buyback; risks US/EMEA moderating and tough Q4 comps",
    kpis="nights_growth;ebitda_margin;buybacks_share_count;experiences_services", framing="buyback / capital return",
    thesis_kpi_happened="yes",
    outcome_note="Bought the post-Q2'25 -8% drop; buybacks $1.1B/qtr continued; the feared Q4 comp turned into a 10% nights print.",
    source="catalogue #cyw-2025-08-16", date_flag="")
add(pitch_id="P11", date="2025-08-25", author="Sanjiv, Long-term Investing", kind="Substack", direction="hold",
    lean="bear", price_target=116.5, horizon_m=12, valuation_method="DCF (FV $113-120); fwd P/E 27x; P/FCF 16x",
    primary_thesis="Slightly overvalued: growth (12.7%) below 5-yr CAGR; NA only +7.8%; Services incredibly early",
    kpis="revenue_growth;take_rate;fcf_margin;regional_mix;pe_multiple", framing="slowing-demand bear",
    thesis_kpi_happened="no",
    outcome_note="Revenue growth accelerated to 17-18% and NA moved to HSD nights; the 6-8% expected return became +42% in a year.",
    source="catalogue #sanjiv-2025-08-25", date_flag="")
add(pitch_id="P12", date="2025-11-11", author="Morningstar (D. Wasiolek), moat -> Wide", kind="Research", direction="long",
    lean="bull", price_target=154.0, horizon_m=12, valuation_method="DCF fair value",
    primary_thesis="Wide moat: network effect (5M hosts, 2B arrivals) strengthened by AI, hotels, RNPL",
    kpis="hotels;rnpl;ai_cost_lever;supply_listings_occupancy", framing="nights acceleration / product catalysts",
    thesis_kpi_happened="yes",
    outcome_note="RNPL >20% of GBV, hotels 3x homes, AI support -16%/booking; FV $154 reached within nine months.",
    source="catalogue #morningstar-2025-11", date_flag="direction inferred: FV 26% above price")
add(pitch_id="P13", date="2025-11-23", author="Rebound Capital, 'Deep Dive'", kind="Substack (paid)", direction="long",
    lean="bull", price_target=np.nan, horizon_m=36, valuation_method="Not visible (paywalled)",
    primary_thesis="Market assigns zero value to Experiences; ~50% of Experience bookers have no stay; leverage over hosts",
    kpis="experiences_services;take_rate;ebitda_margin", framing="optionality / new businesses",
    thesis_kpi_happened="partly",
    outcome_note="Stock +59% (best entry in the sample) but for reasons other than Experiences; 'leverage over hosts' cut the other way (6-10% host-fee test).",
    source="catalogue #rebound-2025-11-23", date_flag="paywalled: PT not visible")
add(pitch_id="P14", date="2025-12-14", author="The Finance Corner (K. Ristovski)", kind="Substack", direction="hold",
    lean="neutral", price_target=145.0, horizon_m=12, valuation_method="10-yr DCF",
    primary_thesis="Fair value $145 (13% upside), no position; take rate mature at 13.5%; questions product-dev ROI",
    kpis="revenue_growth;ebitda_margin;take_rate;product_dev_spend", framing="valuation multiple / fair value",
    thesis_kpi_happened="yes",
    outcome_note="Take rate did stay 'mature' (13.2%). But the 9.6% revenue CAGR assumption was too low for 2026 (+17-18%) and FV $145 was passed in May.",
    source="catalogue #financecorner-2025-12-14", date_flag="")
add(pitch_id="P15", date="2025-12-27", author="Motley Fool (N. Patel), 'What to watch in 2026'", kind="Web", direction="long",
    lean="bull", price_target=np.nan, horizon_m=12, valuation_method="Operating-income consensus",
    primary_thesis="Watch GBV, first-time bookers (Japan, India), operating income +15%, FCF $4.5B",
    kpis="gbv_growth;first_time_bookers;op_income;fcf_margin", framing="nights acceleration / product catalysts",
    thesis_kpi_happened="yes",
    outcome_note="GBV +19%/+16%, first-time bookers +10%/+11% (best in four years), FY26 guide raised twice.",
    source="catalogue #fool-2025-12-27", date_flag="")
add(pitch_id="P16", date="2026-01-09", author="Barclays (UW -> EW)", kind="Sell-side", direction="hold",
    lean="neutral", price_target=120.0, horizon_m=12, valuation_method="20x FY27 GAAP EPS",
    primary_thesis="2026 room nights +9% vs consensus 7.5% on RNPL, hotels, World Cup; still a single-product company at full valuation",
    kpis="nights_growth;rnpl;hotels;pe_multiple", framing="nights acceleration / product catalysts",
    thesis_kpi_happened="yes",
    outcome_note="The differentiated KPI call (nights ~9-10%) was right; the Equal Weight rating and $120 PT were wrong (+31%). KPI right, multiple discipline cost the call.",
    source="catalogue #barclays-2026-01-09", date_flag="")
add(pitch_id="P17", date="2026-02-14", author="Speedwell Memos, '4Q25 Business Update'", kind="Substack (paid)", direction="long",
    lean="bull", price_target=np.nan, horizon_m=12, valuation_method="Not visible (paywalled)",
    primary_thesis="Reacceleration is product-driven (Project Hawaii); AI is top-of-funnel; risk is agentic-web disintermediation",
    kpis="nights_growth;gbv_growth;ai_disintermediation;op_income", framing="nights acceleration / product catalysts",
    thesis_kpi_happened="yes",
    outcome_note="Q1/Q2'26 nights 9%/10%, GBV +19%/+16%; the AI-disintermediation scare (3 Feb 2026, -7%) faded with ABNB falling half as much as BKNG/EXPE.",
    source="catalogue #speedwell-2026-02-14", date_flag="paywalled: PT not visible")
add(pitch_id="P18", date="2026-02-25", author="LongYield, 'Illusion of Strength'", kind="Substack", direction="hold",
    lean="bear", price_target=132.0, horizon_m=12, valuation_method="EV/EBITDA (26x vs BKNG 14-18x); scenarios $88/$132/$175",
    primary_thesis="Record cash flow masks SBC (12.7% of rev), falling host occupancy, spreading regulation, Google chokepoint",
    kpis="sbc_adjusted_fcf;supply_listings_occupancy;regulation;ev_ebitda_multiple;fcf_margin", framing="quality of cash / SBC / margin",
    thesis_kpi_happened="partly",
    outcome_note="SBC did stay 13% of revenue and FCF/EBITDA kept converging (right), but demand reaccelerated and the stock passed the $175 bull case in August. Author turned constructive 8 Aug.",
    source="catalogue #longyield-2026-02-25", date_flag="")
add(pitch_id="P19", date="2026-03-09", author="Phaetrix, 'AI Is Working. I Want to See the Bill.'", kind="Substack", direction="hold",
    lean="bear", price_target=145.0, horizon_m=12, valuation_method="Fwd P/E mid-20s to 30x; EV/FCF 15-17x; tripwires",
    primary_thesis="Take rate 13.6% vs 14.1% YoY is the critical red flag; AI is cost leverage not monetisation",
    kpis="take_rate;gbv_growth;ai_cost_lever;fcf_margin", framing="take-rate skeptic",
    thesis_kpi_happened="yes",
    outcome_note="Take rate stayed flat/down and 2026 guide slipped from 'modest upside' to 'flat' (KPI right); GBV did not decelerate (the exit tripwire never fired) and the stock +36%.",
    source="catalogue #phaetrix-2026-03-09", date_flag="")
add(pitch_id="P20", date="2026-03-26", author="Truist (Scholes), Sell -> Hold", kind="Sell-side", direction="hold",
    lean="neutral", price_target=129.0, horizon_m=12, valuation_method="20x 2027E adj. EBITDA (blended)",
    primary_thesis="Travel demand resilient; 2026E EBITDA $4.79B / EPS $5.03",
    kpis="ebitda_margin;eps_growth;ev_ebitda_multiple", framing="valuation multiple / fair value",
    thesis_kpi_happened="partly",
    outcome_note="Demand resilient (right); 2026E EBITDA $4.79B looks ~5% low against the >=35.5% on >=mid-teens guide (~$5.0B). Hold at $131 missed +39%.",
    source="catalogue #truist-2026-03-26", date_flag="")
add(pitch_id="P21", date="2026-04-22", author="Wells Fargo (Gawrelski), EW -> OW", kind="Sell-side", direction="long",
    lean="bull", price_target=178.0, horizon_m=12, valuation_method="28x forward P/E",
    primary_thesis="Significant business inflection: hotels, sponsored listings 2027, RNPL 70%+ adoption, AI support",
    kpis="hotels;rnpl;ai_cost_lever;app_share;pe_multiple", framing="nights acceleration / product catalysts",
    thesis_kpi_happened="yes",
    outcome_note="Q2'26 delivered nights +10%, hotels 3x homes, RNPL >20% of GBV, support cost -16%; PT $178 hit on the print day (7 Aug).",
    source="catalogue #wells-2026-04-22", date_flag="")
add(pitch_id="P22", date="2026-05-07", author="Oppenheimer (Kelly), Perform -> OP", kind="Sell-side", direction="long",
    lean="bull", price_target=180.0, horizon_m=12, valuation_method="n/a (not public)",
    primary_thesis="Hotels + RNPL + AI search = durable revenue reacceleration",
    kpis="hotels;rnpl;nights_growth", framing="nights acceleration / product catalysts",
    thesis_kpi_happened="yes",
    outcome_note="Upgraded into the Q1 print that dipped -1.8% AH; Q2 print then delivered and PT $180 was reached in August.",
    source="catalogue #oppenheimer-2026-05-07", date_flag="")
add(pitch_id="P23", date="2026-05-07", author="TIKR (three posts, May-Jul 2026)", kind="Web", direction="long",
    lean="bull", price_target=314.0, horizon_m=55, valuation_method="NTM EV/EBITDA vs BKNG; DCF-style mid case to 2030 ($303-325)",
    primary_thesis="Sideways for years, EPS trajectory says otherwise; take rate in Q2 is the cleanest tell",
    kpis="ev_ebitda_multiple;eps_growth;take_rate;peer_multiple_relative", framing="valuation multiple / fair value",
    thesis_kpi_happened="partly",
    outcome_note="Stock broke out (+30%) but the 'cleanest tell' (Q2 take rate) came in flat at 13.2%, i.e. the tell said no while the stock said yes.",
    source="catalogue #tikr-2026 (first post dated; 15 Jun and 8 Jul posts folded in)", date_flag="three posts folded into one row")
add(pitch_id="P24", date="2026-05-21", author="Trefis, 'Set up for a re-rating?'", kind="Web", direction="long",
    lean="bull", price_target=220.0, horizon_m=36, valuation_method="Hold P/E flat at 33x, grow earnings",
    primary_thesis="Trades below MAR/HLT P/E despite faster growth; revenue $12.6B -> $17.5B",
    kpis="pe_multiple;peer_multiple_relative;revenue_growth", framing="valuation multiple / fair value",
    thesis_kpi_happened="partly",
    outcome_note="Re-rating started (stock +36% in 3.5 months, P/E to ~31x fwd) though the $220 three-year target is 21% away.",
    source="catalogue #trefis-2026-05-21", date_flag="")
add(pitch_id="P25", date="2026-05-27", author="Summit Stocks, 'Travel Ecosystem, Not a Booking App'", kind="Substack", direction="long",
    lean="bull", price_target=np.nan, horizon_m=60, valuation_method="EV/FCF 15x (24x SBC-adjusted)",
    primary_thesis="Ecosystem thesis: hotels 55% convert to homes, RNPL 20% of GBV, app 63% of nights",
    kpis="hotels;rnpl;app_share;gbv_growth;sbc_adjusted_fcf", framing="nights acceleration / product catalysts",
    thesis_kpi_happened="yes",
    outcome_note="Hotels-to-home conversion was restated 55% -> 35% in the Q2 letter, but hotels grew 3x, RNPL and app share rose as described.",
    source="catalogue #summit-2026-05-27", date_flag="")
add(pitch_id="P26", date="2026-06-24", author="High Tech Investing (S. Waldhauser), 'Travel Super App?'", kind="Substack", direction="long",
    lean="bull", price_target=np.nan, horizon_m=36, valuation_method="None",
    primary_thesis="Real growth acceleration; could challenge Uber as super app; FCF margin compressing on investment",
    kpis="revenue_growth;nights_growth;fcf_margin", framing="optionality / new businesses",
    thesis_kpi_happened="yes",
    outcome_note="Acceleration continued (Q2 revenue +17%); FCF margin 36.7% TTM as flagged.",
    source="catalogue #hightech-2026-06-24", date_flag="")
add(pitch_id="P27", date="2026-07-30", author="Morgan Stanley (Nowak), Underweight", kind="Sell-side", direction="short",
    lean="bear", price_target=125.0, horizon_m=12, valuation_method="n/a public (P/E ~37x vs BKNG cited)",
    primary_thesis="Listings growth slowing 12% -> ~7% creates occupancy headwinds and lower forward room-night demand",
    kpis="supply_listings_occupancy;nights_growth;peer_multiple_relative", framing="supply / regulation bear",
    thesis_kpi_happened="no",
    outcome_note="One week later nights +10%, first-time bookers +11%, guide raised; stock +17% on the day. Supply thesis has been wrong on demand for five quarters.",
    source="catalogue #morgan-stanley-2026-07-30", date_flag="")
add(pitch_id="P28", date="2026-08-07", author="Wedbush (Arounian), Neutral -> OP", kind="Sell-side", direction="long",
    lean="bull", price_target=200.0, horizon_m=12, valuation_method="n/a (not public)",
    primary_thesis="Broad strength and new-initiative positives: RNPL, single fee, hotels, car rental, luggage",
    kpis="rnpl;take_rate;hotels;gross_margin;experiences_services", framing="nights acceleration / product catalysts",
    thesis_kpi_happened="open",
    outcome_note="Post-print upgrade at $178; stock has traded $180-190 since. Single-fee take-rate lift is contradicted by the 'flat for 2026' guide and the 6-10% host-fee test.",
    source="catalogue #wedbush-2026-08-07", date_flag="")
add(pitch_id="P29", date="2026-08-07", author="MBI Deep Dives, '2Q26: Widening the Gap' (+ model update 19 Aug)", kind="Substack (paid)", direction="long",
    lean="bull", price_target=np.nan, horizon_m=36, valuation_method="Full model (paywalled)",
    primary_thesis="Acceleration sustained; take-rate recovery more sluggish than expected (LTM -31 bps) on RNPL timing and incentives",
    kpis="nights_growth;take_rate;adr;first_time_bookers;app_share", framing="take-rate skeptic",
    thesis_kpi_happened="open",
    outcome_note="Take-rate caution validated three weeks later by the host-fee pilot (Skift, 29 Aug); stock flat since.",
    source="catalogue #mbi-2026-08", date_flag="paywalled: PT not visible; two posts folded into one row")
add(pitch_id="P30", date="2026-08-07", author="Susquehanna (Positive, PT $200) and Evercore ISI (OP, PT $200)", kind="Sell-side", direction="long",
    lean="bull", price_target=200.0, horizon_m=12, valuation_method="n/a (not public)",
    primary_thesis="Guidance raise; post-Q2'26 target raises",
    kpis="nights_growth;ebitda_margin", framing="nights acceleration / product catalysts",
    thesis_kpi_happened="open",
    outcome_note="Post-print raises; no public detail.",
    source="landscape sec. 1b; catalogue sec. C 'other post-Q2 targets'", date_flag="date approximate (post-print, 'Aug 2026')")
add(pitch_id="P31", date="2026-08-07", author="BofA (Post) $160 / UBS (Ju) $163-172 / BMO (Pitz) $165 / JPMorgan $130 Neutral", kind="Sell-side", direction="hold",
    lean="neutral", price_target=160.0, horizon_m=12, valuation_method="n/a (not public)",
    primary_thesis="Post-Q2'26 target raises that stayed below the $178 print-day price",
    kpis="ebitda_margin;pe_multiple", framing="valuation multiple / fair value",
    thesis_kpi_happened="open",
    outcome_note="Ratings not public; direction inferred from PTs 10-27% below the price. Stock has held $180-190 since.",
    source="landscape sec. 1b", date_flag="date approximate; direction inferred from PT below price; four houses folded into one row")
add(pitch_id="P32", date="2026-08-08", author="LongYield, 'Reaccelerating, But...' (turned constructive)", kind="Substack", direction="long",
    lean="bull", price_target=np.nan, horizon_m=12, valuation_method="Multiples ('no longer obviously cheap')",
    primary_thesis="Core markets moved from LSD/MSD to HSD nights; hotels and services the next leg; deserves a quality multiple if margins hold",
    kpis="nights_growth;regional_mix;ebitda_margin;hotels", framing="nights acceleration / product catalysts",
    thesis_kpi_happened="open",
    outcome_note="Flipped from bear-leaning to constructive after a +50% move; too recent to judge.",
    source="catalogue #longyield-2026-08-08", date_flag="")
add(pitch_id="P33", date="2026-08-11", author="Phillip Securities (Chew), Neutral -> Reduce", kind="Sell-side", direction="short",
    lean="bear", price_target=158.0, horizon_m=12, valuation_method="P/E vs 2-yr history (30.9x > +1 sigma 29.6x)",
    primary_thesis="AI and reacceleration baked in; earnings keep growing but the price ran ahead",
    kpis="pe_multiple;peer_multiple_relative;ai_cost_lever", framing="valuation multiple / fair value",
    thesis_kpi_happened="open",
    outcome_note="Stock -1.6% since (roughly flat); too early.",
    source="catalogue #phillip-2026-08-11", date_flag="")
add(pitch_id="P34", date="2026-08-14", author="Finn 'Running Thesis' scorecard", kind="Tool", direction="hold",
    lean="neutral", price_target=np.nan, horizon_m=12, valuation_method="Scorecard (valuation 2/5)",
    primary_thesis="Bull: support cost -16%, hotels 3x; bear: RNPL cancellations and cash timing, S&M +33%, OCF flat",
    kpis="support_cost_per_booking;hotels;rnpl;sm_intensity;fcf_margin", framing="quality of cash / SBC / margin",
    thesis_kpi_happened="open",
    outcome_note="Undated (Aug 2026); mid-month used. Notable for being one of two pieces that named flat operating cash flow / RNPL cash timing.",
    source="catalogue #finn-2026-08", date_flag="date approximate ('Aug 2026')")
add(pitch_id="P35", date="2026-08-24", author="Bernstein (Clarke), 'Acceleration Is Here to Stay'", kind="Sell-side", direction="long",
    lean="bull", price_target=217.0, horizon_m=12, valuation_method="25.5x EBITDA on 12% revenue growth; reverse DCF (market implies 10.5-11%)",
    primary_thesis="Fifth straight quarter of ~10% nights makes acceleration structural; ~20% EPS CAGR; single fee lifts take rate toward 15.5%",
    kpis="nights_growth;take_rate;eps_growth;ev_ebitda_multiple;buybacks_share_count", framing="take-rate expansion bull",
    thesis_kpi_happened="open",
    outcome_note="Published at the local high ($190); take-rate leg already contradicted by the flat-2026 guide and the 6-10% host-fee test five days later.",
    source="catalogue #bernstein-2026-08-24", date_flag="")
add(pitch_id="P36", date="2026-09-01", author="Rosenblatt (initiation, Buy)", kind="Sell-side", direction="long",
    lean="bull", price_target=220.0, horizon_m=12, valuation_method="n/a (multiple expansion)",
    primary_thesis="Overhang lifting as new businesses show measurable results; GBV +16% on a two-year stack",
    kpis="gbv_growth;gross_margin;experiences_services", framing="nights acceleration / product catalysts",
    thesis_kpi_happened="open",
    outcome_note="Three trading days old.",
    source="catalogue #rosenblatt-2026-09-01", date_flag="")
add(pitch_id="P37", date="2026-09-03", author="Theo, ABNB macro-to-equity IC brief", kind="Internal research", direction="none",
    lean="neutral", price_target=np.nan, horizon_m=np.nan, valuation_method="None (process brief, 'do not trade yet')",
    primary_thesis="Guidance level/direction does not map to returns (r=0.08, n=16); activity composite tracks guidance level (r=0.78) but not acceleration (r=-0.63)",
    kpis="guidance_change;macro_travel_activity", framing="process / no call",
    thesis_kpi_happened="n/a",
    outcome_note="Not a stock call; excluded from win rates. Its finding that raw guidance changes carry no return information matches this scorecard (holds and valuation-only calls did worst).",
    source="theos-past-research/docs/forecasting/abnb_ic_brief/brief.tex; generated/metrics.tex", date_flag="not scored")

pitches = pd.DataFrame(P)
pitches["date"] = pd.to_datetime(pitches["date"])

# ----------------------------------------------------------------------------------------------------------------
# 2. Prices and returns
# ----------------------------------------------------------------------------------------------------------------


def load_px(ticker: str) -> pd.Series:
    df = pd.read_csv(PRICES / f"{ticker}_daily.csv", parse_dates=["date"])
    s = df.set_index("date")["adj_close"].sort_index()
    return s[s.index <= AS_OF]


abnb = load_px("ABNB")
qqq = load_px("QQQ")
LAST = abnb.index.max()


def px_on_or_before(s: pd.Series, d: pd.Timestamp) -> float:
    return float(s[:d].iloc[-1])


def ret(s: pd.Series, d0: pd.Timestamp, d1: pd.Timestamp):
    """Close-to-close return from d0 to d1 (both snapped to on-or-before trading day). NaN if d1 is after the last close."""
    if d1 > LAST:
        return np.nan
    return px_on_or_before(s, d1) / px_on_or_before(s, d0) - 1.0


rows = []
for _, r in pitches.iterrows():
    d0 = r["date"]
    p0 = px_on_or_before(abnb, d0)
    out = {"price_at_date": round(p0, 2), "pt_upside_at_date_pct": np.nan}
    for lab, days in [("3m", 91), ("6m", 182), ("12m", 365)]:
        d1 = d0 + pd.Timedelta(days=days)
        ra, rq = ret(abnb, d0, d1), ret(qqq, d0, d1)
        out[f"abnb_ret_{lab}_pct"] = round(ra * 100, 1) if pd.notna(ra) else np.nan
        out[f"qqq_ret_{lab}_pct"] = round(rq * 100, 1) if pd.notna(rq) else np.nan
        out[f"excess_{lab}_pct"] = round((ra - rq) * 100, 1) if pd.notna(ra) else np.nan
    ra, rq = ret(abnb, d0, LAST), ret(qqq, d0, LAST)
    out["abnb_ret_to_date_pct"] = round(ra * 100, 1)
    out["qqq_ret_to_date_pct"] = round(rq * 100, 1)
    out["excess_to_date_pct"] = round((ra - rq) * 100, 1)
    out["days_elapsed"] = int((LAST - d0).days)

    # evaluation window for the direction call: the pitch's own horizon if finished, else to date
    hz = r["horizon_m"]
    h_end_eval = d0 + pd.DateOffset(months=int(hz)) if pd.notna(hz) else pd.NaT
    horizon_done = pd.notna(h_end_eval) and h_end_eval <= LAST
    too_early = out["days_elapsed"] < 60 and not horizon_done
    if horizon_done:
        ra_h, rq_h = ret(abnb, d0, h_end_eval), ret(qqq, d0, h_end_eval)
        eval_ret, eval_excess = round(ra_h * 100, 1), round((ra_h - rq_h) * 100, 1)
        eval_win = f"{int(hz)}m (finished)"
    else:
        eval_ret, eval_excess = out["abnb_ret_to_date_pct"], out["excess_to_date_pct"]
        eval_win = "too early (<60 days)" if too_early else "to date (provisional)"
    out["eval_window"] = eval_win
    out["eval_abnb_ret_pct"] = eval_ret
    out["eval_excess_pct"] = eval_excess

    direction = r["direction"]
    if too_early or direction == "none":
        dir_right, excess_right = np.nan, np.nan
    elif direction == "long":
        dir_right, excess_right = eval_ret > 0, eval_excess > 0
    elif direction == "short":
        dir_right, excess_right = eval_ret < 0, eval_excess < 0
    elif direction == "hold":
        dir_right, excess_right = abs(eval_ret) <= 10, abs(eval_excess) <= 10
    else:
        dir_right, excess_right = np.nan, np.nan
    out["direction_right"] = dir_right
    out["excess_vs_qqq_right"] = excess_right

    # target reached within horizon
    pt = r["price_target"]
    if pd.isna(pt) or direction == "none":
        out["target_reached"] = "no target"
        out["horizon_end"] = np.nan
        if pd.isna(r["horizon_m"]):
            out["horizon_status"] = "n/a"
        else:
            out["horizon_status"] = "finished" if d0 + pd.DateOffset(months=int(r["horizon_m"])) <= LAST else "open"
    else:
        h_end = d0 + pd.DateOffset(months=int(r["horizon_m"]))
        out["horizon_end"] = h_end.date().isoformat()
        window = abnb[d0:min(h_end, LAST)]
        if direction == "long" and pt <= p0:
            hit = None  # a "target" already at or below the entry price is not a call
        elif direction == "long":
            hit = bool(window.max() >= pt)
        elif direction == "short":
            hit = bool(window.min() <= pt)
        else:  # hold: reached if the price touched the fair value from either side
            hit = bool(window.max() >= pt) if pt >= p0 else bool(window.min() <= pt)
        if hit is None:
            out["target_reached"] = "PT at/below price at date (no credit)"
        elif hit:
            out["target_reached"] = "yes"
        elif h_end <= LAST:
            out["target_reached"] = "no (horizon finished)"
        else:
            out["target_reached"] = "not yet (horizon open)"
        out["horizon_status"] = "finished" if h_end <= LAST else "open"
        out["pt_upside_at_date_pct"] = round((pt / p0 - 1) * 100, 1)

    # call quality
    if direction == "none" or too_early:
        cq = np.nan
    elif not dir_right:
        cq = 0
    elif out["target_reached"] == "yes":
        cq = 2
    else:
        cq = 1
    out["call_quality"] = cq
    rows.append(out)

score = pd.concat([pitches.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
score["date"] = score["date"].dt.date.astype(str)
col_order = ["pitch_id", "date", "author", "kind", "direction", "lean", "framing", "price_at_date", "price_target",
             "pt_upside_at_date_pct", "horizon_m", "horizon_end", "horizon_status", "primary_thesis", "kpis",
             "valuation_method",
             "abnb_ret_3m_pct", "qqq_ret_3m_pct", "excess_3m_pct", "abnb_ret_6m_pct", "qqq_ret_6m_pct", "excess_6m_pct",
             "abnb_ret_12m_pct", "qqq_ret_12m_pct", "excess_12m_pct", "abnb_ret_to_date_pct", "qqq_ret_to_date_pct",
             "excess_to_date_pct", "days_elapsed", "eval_window", "eval_abnb_ret_pct", "eval_excess_pct",
             "direction_right", "excess_vs_qqq_right", "target_reached", "thesis_kpi_happened", "call_quality",
             "outcome_note", "source", "date_flag"]
score = score[col_order]
score.to_csv(OUT / "05_pitch_scorecard.csv", index=False, encoding="utf-8")

# ----------------------------------------------------------------------------------------------------------------
# 3. Metric usage. Controlled vocabulary -> label, what users assumed, what actually happened (outcome record).
#    Metrics with zero usage are the framings our own data supports but no pitch used.
# ----------------------------------------------------------------------------------------------------------------
stack = pd.read_csv(ROOT / "data/processed/abnb_quarterly_cost_stack_exsbc.csv").set_index("quarter")
sm_pn_2q24, sm_pn_2q25, sm_pn_2q26 = (stack.loc[q, "sm_cash_per_night"] for q in ["2Q24", "2Q25", "2Q26"])
rev_pn_2q24, rev_pn_2q26 = stack.loc["2Q24", "rev_per_night"], stack.loc["2Q26", "rev_per_night"]
guide = pd.read_csv(ROOT / "data/external/abnb_revenue_guidance_vs_actual.csv").dropna(subset=["actual_musd"])
n_guides, n_beat, mean_beat = len(guide), int((guide["actual_vs_mid_pct"] > 0).sum()), guide["actual_vs_mid_pct"].mean()
fcfb = pd.read_csv(ROOT / "data/processed/abnb_fcf_bridge.csv").set_index("period")
fcf_ebitda_22 = fcfb.loc["FY2022", "fcf"] / fcfb.loc["FY2022", "adj_ebitda"] * 100
fcf_ebitda_25 = fcfb.loc["FY2025", "fcf"] / fcfb.loc["FY2025", "adj_ebitda"] * 100
cap = pd.read_csv(ROOT / "data/external/capital_return_scorecard_annual.csv")
ncr_abnb = float(cap[(cap.ticker == "ABNB") & (cap.fy == "2023-2025 cumulative")]["net_cash_return_pct_fcf"].iloc[0])
ncr_bkng = float(cap[(cap.ticker == "BKNG") & (cap.fy == "2023-2025 cumulative")]["net_cash_return_pct_fcf"].iloc[0])
kvc = pd.read_csv(ROOT / "data/processed/abnb_kpi_vs_category_quarterly.csv").set_index("quarter")
adr_2q26, hot_2q26 = kvc.loc["2026Q2", "adr_yoy_pct"], kvc.loc["2026Q2", "bea_hotels_price_yoy_pct"]
adr_1q26, hot_1q26 = kvc.loc["2026Q1", "adr_yoy_pct"], kvc.loc["2026Q1", "bea_hotels_price_yoy_pct"]

METRICS = {
    # tag: (label, direction the users assumed, what actually happened, moved as assumed?)
    "nights_growth": ("Nights & seats booked growth", "bulls: reacceleration; bears (P09, P27): deceleration",
                      "7% (2Q25) -> 9% -> 10% -> 9% -> 10% (2Q26); Q3'26 guide low double digits", "yes for bulls, no for bears"),
    "gbv_growth": ("GBV growth", "acceleration", "+11% (2Q25) -> +14% -> +16% -> +19% -> +16% (2Q26), ~3 pts FX in 2026", "yes"),
    "adr": ("ADR", "P09 assumed ADR falling; P29 tracks ex-FX", "-1% (1Q25) -> +3% -> +5% -> +6% -> +9% -> +5%; ex-FX +4% in 1H26", "no for the bear"),
    "take_rate": ("Take rate (revenue / GBV)", "bulls (P07, P35): expansion to 14-15.5%; skeptics (P14, P19, P29): flat or down",
                  "13.2% in 2Q26 flat YoY; LTM -31 bps; 2026 guided flat; 6-10% host-fee test Aug 2026", "no for bulls, yes for skeptics"),
    "ebitda_margin": ("Adj. EBITDA margin", "bulls: expansion; bears (P09): compression", "FY25 35%; FY26 floor raised 35% -> 35.5%; Q3'26 guided down slightly YoY", "neither: flat floor"),
    "fcf_margin": ("FCF / FCF margin", "bulls: ~38-40% sustained", "TTM FCF $4.8B, margin 36.7% (down from 44% peak); FCF/EBITDA 105%", "partly (level held, margin drifting down)"),
    "sbc_adjusted_fcf": ("SBC-adjusted FCF / FCF yield", "bears: SBC ~13% of revenue makes 'real' margin ~25%", "SBC $1.7B TTM, 13% of revenue, unchanged; stock ignored it", "yes on the KPI, no on the price"),
    "sm_intensity": ("Sales & marketing intensity", "bears: growth is bought",
                     "S&M +27%% (2Q26) vs revenue +17%%; field ops & policy +43%% in 2025; cash S&M/night $%.2f -> $%.2f" % (sm_pn_2q25, sm_pn_2q26), "yes"),
    "first_time_bookers": ("First-time booker growth", "acceleration = structural demand", "+10% (1Q26), +11% (2Q26), best in four years", "yes"),
    "app_share": ("App share of nights", "rising engagement", "59% -> 64%; app nights +23%", "yes"),
    "hotels": ("Hotels on Airbnb", "bulls: meaningful new supply and conversion", "single-digit % of nights growing ~3x homes; 20+ cities; conversion restated 55% -> 35%", "yes (growth), unproven (economics)"),
    "rnpl": ("Reserve Now, Pay Later", "bulls: conversion lift", ">20% of GBV, ~70% adoption; +1 pt cancellations; laps from Q3'26", "yes (level shift, lapping)"),
    "experiences_services": ("Experiences / Services optionality", "bulls: unpriced $1B businesses", "supply +80% but 'not material'; management says 3-5 years", "no (not yet)"),
    "support_cost_per_booking": ("Customer-support cost per booking (AI)", "falling", "-10% (1Q26), -16% (2Q26); ~45% of tickets self-resolved", "yes"),
    "regional_mix": ("Regional mix / expansion markets", "expansion 2x core; bears: NA weak", "expansion ~2x core; core markets moved to HSD nights in 2Q26", "yes for bulls, no for bears"),
    "buybacks_share_count": ("Buybacks / share count", "shrinking count supports EPS", "$1.1B per quarter; diluted shares -3.4% (2025), -9% since 2022", "yes"),
    "pe_multiple": ("Forward P/E (absolute or vs history)", "bears/holds: multiple full at 27-31x", "multiple expanded to ~31x forward; stock +30-40% from those calls", "no"),
    "ev_ebitda_multiple": ("EV/EBITDA (absolute or vs BKNG)", "mixed: cheap (TIKR 14x NTM) vs rich (LongYield 26x trailing)", "definitions differ by 10 turns (guest float in cash); stock re-rated regardless", "mixed"),
    "peer_multiple_relative": ("Relative multiple vs BKNG/EXPE or MAR/HLT", "framing decides conclusion", "vs hotels: re-rating happened (P24); vs OTAs: premium widened (P27, P33 wrong so far)", "mixed"),
    "eps_growth": ("EPS growth / EPS estimates", "~20% CAGR", "2026 EPS estimates raised twice; tax-comp distortions (CAMT)", "yes so far"),
    "revenue_growth": ("Revenue growth", "bears (P11): decelerating below 5-yr CAGR", "+13% (2Q25) -> +18% (1Q26) -> +17% (2Q26); FY26 guide >= mid-teens", "no for bears"),
    "op_income": ("Operating income", "+15% in 2026", "on track; 1H26 op income up with 35%+ EBITDA margin on +17% revenue", "yes"),
    "gross_margin": ("Gross margin (~83%)", "supports expansion", "82.5% derived in 2Q26, flat", "yes (flat)"),
    "product_dev_spend": ("Product-development spend / ROI", "questioned", "cash product dev flat at 10-11% of revenue since 2022; GAAP creep is SBC", "partly (the worry was SBC in disguise)"),
    "supply_listings_occupancy": ("Listings growth / host occupancy", "bears: supply slowdown caps nights", "Airbnb stopped disclosing supply in 2024; nights accelerated anyway", "no"),
    "regulation": ("Regulation (NYC LL18, Barcelona, Paris)", "bears: spreading", "spreading, but no city >2% of revenue; no visible KPI impact", "yes (event), no (impact)"),
    "ai_cost_lever": ("AI as cost lever", "real savings", "support cost -16%/booking; 60% of code AI-written", "yes"),
    "ai_disintermediation": ("AI / agentic-web disintermediation", "risk", "3 Feb 2026 scare -7% (BKNG -9%, EXPE -15%); faded; AI-native share ~3% (Third Bridge)", "not so far"),
    "unpaid_traffic_share": ("Direct / unpaid traffic share", "~90% sustained", "still ~90% per management; paid growth initiatives rising in emerging markets", "yes"),
    "guidance_change": ("Raw guidance change (Theo)", "tested as a signal", "r = 0.08 with excess return (n=16); direction aligned 7/19", "no signal"),
    "macro_travel_activity": ("Macro / travel-activity composite (Theo)", "tested as a signal", "r = 0.78 with guidance level, r = -0.63 with acceleration; 0 strict-PIT rows", "level yes, change no"),
    # ---- metrics nobody used ----
    "cash_sm_per_night": ("Cash S&M per night (ex-SBC)", "n/a",
                          "$%.2f (2Q24) -> $%.2f (2Q25) -> $%.2f (2Q26), +%.0f%% in two years vs revenue/night +%.0f%%"
                          % (sm_pn_2q24, sm_pn_2q25, sm_pn_2q26, (sm_pn_2q26 / sm_pn_2q24 - 1) * 100, (rev_pn_2q26 / rev_pn_2q24 - 1) * 100), "unused"),
    "ex_sbc_cost_stack": ("Ex-SBC cash cost stack by line", "n/a", "2022-25: revenue/night added 5.1 margin pts, S&M took back 4.2; product dev flat at 10-11% cash", "unused"),
    "guidance_cushion": ("Revenue guidance cushion (actual vs guided midpoint)", "n/a",
                         "%d of %d guided quarters beat the midpoint, mean +%.1f%%; range width narrowed 6%% -> 1.6%%" % (n_beat, n_guides, mean_beat), "unused"),
    "fcf_to_ebitda_gap": ("FCF-to-Adj. EBITDA conversion", "n/a",
                          "%.0f%% (FY22) -> %.0f%% (FY25); float switched off by RNPL, full tax provision, interest income falling" % (fcf_ebitda_22, fcf_ebitda_25), "unused"),
    "net_cash_return_after_sbc": ("Net cash return (buybacks - SBC) as % of FCF", "n/a",
                                  "ABNB %.0f%% cumulative 2023-25 vs BKNG %.0f%%; $1.4B of buybacks per 1%% share-count cut" % (ncr_abnb, ncr_bkng), "unused"),
    "peer_read_through": ("Peer read-through (BKNG/EXPE prints, hotel deals)", "n/a", "only one 7%+ ABNB day was peer-driven (3 Feb 2026); BKNG prints never moved ABNB 7%", "unused"),
    "hotel_price_vs_adr": ("US hotel price inflation relative to ABNB ADR", "n/a",
                           "ADR ran 5-6 pts above hotels through 1Q26 (%.1f vs %.1f); gap closed in 2Q26 (%.1f vs %.1f)" % (adr_1q26, hot_1q26, adr_2q26, hot_2q26), "unused"),
    "unearned_fees_rnpl_adj": ("Unearned fees adjusted for RNPL (forward booked business)", "n/a", "unearned fees flat YoY at $2.83B while GBV +16%; coverage of next-quarter revenue fell 88% -> 76%", "unused"),
    "nights_second_derivative": ("Second derivative of nights vs guide (the print reaction driver)", "n/a", "all 11 earnings moves >=7% keyed off forward nights, six on beats; 20-session mean excess after prints -4.7%", "unused (Barclays P16 closest)"),
    "post_print_fade_base_rate": ("Post-print fade base rate", "n/a", "every 7%+ up day before Q2'26 gave it back within 20 sessions; Q2'26 first exception (+22%)", "unused"),
    "field_ops_policy_split": ("S&M split: brand/performance vs field ops & policy", "n/a", "brand+perf +10% in 2025 vs field ops & policy +43% to $993M: the spend is supply acquisition, not ads", "unused"),
    "interest_income_share": ("Interest income inside FCF", "n/a", "5.2% of revenue TTM (7.4% peak in 2024), falling with rates; capitalised at an EBITDA multiple by every FCF-yield user", "unused (P25 mentioned in passing)"),
    "adr_ex_fx": ("ADR ex-FX as the margin driver", "n/a", "+1 pt ADR ex-FX ~ +0.5 pt margin; 2025-26 ADR tailwind Airbnb-specific, not category", "unused (P29 tracks NA ex-FX only)"),
}

usage_rows = []
scored = score[score["call_quality"].notna()]
for tag, (label, assumed, actual, moved) in METRICS.items():
    users = score[score["kpis"].str.split(";").apply(lambda ks: tag in ks)]
    users_scored = users[users["call_quality"].notna()]
    n_right = int((users_scored["call_quality"] >= 1).sum())
    usage_rows.append({
        "metric": tag, "label": label, "n_pitches_used": len(users),
        "used_by": ";".join(users["pitch_id"]),
        "n_calls_right": n_right,
        "n_calls_beat_qqq": int((users_scored["excess_vs_qqq_right"] == True).sum()),  # noqa: E712
        "hit_rate_pct": round(n_right / len(users_scored) * 100, 0) if len(users_scored) else np.nan,
        "n_scoreable": len(users_scored),
        "n_with_finished_horizon": int(users_scored["eval_window"].str.contains("finished").sum()),
        "mean_excess_to_date_pct": round(users_scored["excess_to_date_pct"].mean(), 1) if len(users_scored) else np.nan,
        "assumed_direction": assumed, "actual_move_2025_26": actual, "moved_as_assumed": moved,
    })
usage = pd.DataFrame(usage_rows).sort_values(["n_pitches_used", "metric"], ascending=[False, True])
usage.to_csv(OUT / "05_metric_usage.csv", index=False, encoding="utf-8")

# ----------------------------------------------------------------------------------------------------------------
# 4. Summary to stdout (numbers quoted in the note)
# ----------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    pd.set_option("display.width", 250, "display.max_columns", 30, "display.max_colwidth", 60)
    print(f"Last close used: {LAST.date()}  ABNB {abnb.iloc[-1]:.2f}  QQQ {qqq.iloc[-1]:.2f}")
    print(f"\nRows: {len(score)} ({len(scored)} scoreable; {(score.eval_window == 'too early (<60 days)').sum()} too early). "
          f"Finished horizons: {scored.eval_window.str.contains('finished').sum()}")
    print()
    print("12m-window view (all rows with a finished 12m window, regardless of stated horizon):")
    f12 = score[score.abnb_ret_12m_pct.notna() & (score.direction != "none")]
    print(f12.groupby("direction").agg(n=("pitch_id", "count"), mean_ret_12m=("abnb_ret_12m_pct", "mean"),
                                       mean_excess_12m=("excess_12m_pct", "mean")).round(1))
    print("\nBy direction:")
    print(scored.groupby("direction").agg(n=("pitch_id", "count"), right=("direction_right", "sum"),
                                          beat_qqq=("excess_vs_qqq_right", "sum"),
                                          mean_ret=("eval_abnb_ret_pct", "mean"), mean_excess=("eval_excess_pct", "mean"),
                                          mean_cq=("call_quality", "mean")).round(1))
    print("\nLongs by date bucket (before/after 2025-08-01):")
    lg = scored[scored.direction == "long"].copy()
    lg["bucket"] = np.where(lg["date"] < "2025-08-01", "pre-Aug-2025", "post-Aug-2025")
    print(lg.groupby("bucket").agg(n=("pitch_id", "count"), mean_ret=("eval_abnb_ret_pct", "mean"),
                                   mean_excess=("eval_excess_pct", "mean"), beat_qqq=("excess_vs_qqq_right", "sum")).round(1))
    print("\nBy framing:")
    print(scored.groupby("framing").agg(n=("pitch_id", "count"), right=("direction_right", "sum"),
                                        mean_excess=("eval_excess_pct", "mean"), mean_cq=("call_quality", "mean")).round(2))
    print("\nBy thesis_kpi_happened:")
    print(scored.groupby("thesis_kpi_happened").agg(n=("pitch_id", "count"), right=("direction_right", "sum"),
                                                    mean_excess=("eval_excess_pct", "mean")).round(1))
    print("\nTargets:", scored["target_reached"].value_counts().to_dict())
    print("\nTop metrics:")
    print(usage[usage.n_pitches_used > 0][["metric", "n_pitches_used", "n_scoreable", "n_calls_right", "n_calls_beat_qqq",
                                           "hit_rate_pct", "mean_excess_to_date_pct"]].to_string(index=False))
    print("\nUnused metrics:")
    print(usage[usage.n_pitches_used == 0][["metric", "actual_move_2025_26"]].to_string(index=False))
    print("\nScorecard (condensed):")
    print(score[["pitch_id", "date", "author", "direction", "price_at_date", "price_target", "eval_window",
                 "eval_abnb_ret_pct", "eval_excess_pct", "target_reached", "thesis_kpi_happened",
                 "call_quality"]].to_string(index=False))
