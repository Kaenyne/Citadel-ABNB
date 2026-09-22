# 41. The cost leg: is the Street too light on Airbnb's costs?

Krish with Claude (Opus 5.5), 22 Sep 2026. Script `analysis/src/margin_build/41_cost_leg/run.py` (`py -3.13`, exit 0), outputs
`data/processed/margin_build/41_cost_leg/`. Pre-registered in `41_42_prereg.md` (commit f6d01166, before the script existed). Prompted by
the 22 Sep Codex Astra audit of `40_line_build`, which found the build's FY27 cost excess over the Street is one assumption (the 3Q26
reconciliation carried forward) and that the earnings gap in every version of the model is mostly revenue. This package asks whether the
repo has independent evidence for a cost leg. Cost measure throughout: revenue minus adjusted EBITDA ("EBITDA costs"), the only cost
object the Street publishes implicitly. Street = LSEG means; dates are in the input files. Nothing in `40_line_build` or the official
model is changed.

## Bottom line (revised after the Codex check, `audit/CODEX_COST_LEG_CHECK.md`)

1. **The Street's FY27 cost growth is the slowest of any year since the IPO, but only because FY26 is fast.** Street FY27 EBITDA costs
   grow **+10.0%** (FY28 +8.7%) against +21.2% / +25.0% / +14.0% / +12.7% / +12.5% in FY21-25, after **+15.0% in FY26E**. Over two years
   the Street compounds at 12.5% a year from FY25, in line with FY24-25's 12.6%. So the Street is not assuming cheap costs; it assumes
   **the FY26 step-up is not repeated.** The cost claim therefore rests on persistence: management said the 2025 launch spend would
   "carry into next year as fixed headcount" (Mertz, 2Q25 call, `transcripts/web/2Q25.html`), and on 8 Sep 2026 Chesky said "We're
   going to have some major announcements next year" (Goldman Communacopia, `05_statements.csv` V023; the repo reads it as launch spend
   ahead of revenue in FY27, no budget given). Its FY27 incremental margin is 43.7% against 32.7% and 22.5% in FY24 and FY25.
2. **Costs have started to come in above consensus (descriptive).** At the pre-print consensus, costs were below the Street in 16 of the
   18 prints from 2021Q1 to 2025Q2 and above it in 3 of the 4 since (3Q25 +$4M, 4Q25 +$41M, 1Q26 +$28M, 2Q26 −$0.4M; mean +0.9%). The
   regime split was chosen after seeing the data (p 0.007 / 0.005 is descriptive). The registered persistence test passes (slope 0.53 W1,
   0.67 W2) but it is the same evidence: controlling for the regime, the slope falls to 0.09 / 0.07 (p 0.25 / 0.42). Its forecast for
   3Q26 is slightly *below* the Street (−0.2% to −0.7%).
3. **Cost of revenue has run above the Street's COGS estimate recently, but the test is fragile.** On point values, cost of revenue came
   in above LSEG's COGS consensus at 11 of 14 prints in W1 (p 0.029) and 8 of 10 in W2 (p 0.055), PASS as registered. Two of those are
   rounding (4Q23 +$0.25M, 2Q25 +$0.03M); counted as misses the test fails (9 of 14, p 0.21; 7 of 10, p 0.17). The last four: +$35M,
   +$17M, +$1M, +$11M. Cost of revenue is fees, amortisation and hosting together (the FY25 increase was fees +$188M, amortisation
   +$28M, hosting +$27M), so this residual cannot be pinned on AI hosting. Our FY27 excess over the Street sits in the same line (cost of
   revenue +$101M against the COGS consensus, opex +$30M), which is where the line build put its hosting assumption.
4. **What it is worth.** Each point of FY27 cost growth is 58bp of margin at the Street's revenue. If FY26's step persists and FY27 costs
   grow at the FY24-25 average (+12.6%) from the Street's FY26 base: FY27 EBITDA $5,531M, **−$235M / −149bp / −$0.34 EPS**. Applying the
   historical rate from FY25 instead (no FY26 step) gives only −$21M. Line-build growth rebased to the Street's FY26 costs: −$94M / −59bp;
   Street plus the recent surprise: −$91M / −57bp. On the official v2 revenue: −$395M (Street costs), −$488M, −$630M / −315bp.
5. **3Q26 is a coin flip on costs.** The registered call is costs above the Street's $2,382.8M; persistence says slightly below. Carrying
   the recent +0.9% gives 3Q26 EBITDA $2,340M at Street revenue (−$21M) and $2,287M at official v2 revenue (−$75M).

Framing for the pitch: **the Street's FY27 needs Airbnb to stop the FY26 spending step; management has said the step is partly fixed
(headcount, launches, hosting commitments); and for the first time costs have come in above consensus in three of four prints.** That
supports "the cost base will not flex down when revenue slows", which is what the official model's revenue-driven gap needs. It is not a
demonstrated cost-forecasting edge, and the note should never be quoted as one.

## Tables

**Annual EBITDA costs** (`41_annual_cost_growth.csv`)

| | Revenue | Adj. EBITDA | Margin | Revenue growth | Cost growth | Incremental margin |
|---|---|---|---|---|---|---|
| FY23 actual | 9,917 | 3,653 | 36.8% | +18.1% | +14.0% | 49.4% |
| FY24 actual | 11,102 | 4,041 | 36.4% | +12.0% | +12.7% | 32.7% |
| FY25 actual | 12,241 | 4,297 | 35.1% | +10.3% | +12.5% | 22.5% |
| FY26 Street (n 44) | 14,190 | 5,054 | 35.6% | +15.9% | +15.0% | 38.8% |
| FY27 Street (n 44) | 15,819 | 5,766 | 36.4% | +11.5% | **+10.0%** | **43.7%** |
| FY28 Street (n 26) | 17,535 | 6,603 | 37.7% | +10.9% | +8.7% | 48.8% |
| FY27 line build base | 15,829 | 5,644 | 35.7% | +10.9% | +11.1% | 35.0% |
| FY27 official v2 | 15,425 | 5,240 | 34.0% | +9.3% | +11.1% | 22.4% |

**Cost surprise at print** (`41_cost_surprise_history.csv`, `41_tests.csv`; + = costs above consensus)

| Window | n | Costs above Street | Mean cost surprise | Recent 4 vs earlier | Persistence slope (p) | COR above COGS consensus |
|---|---|---|---|---|---|---|
| W1 (1Q23+) | 14 | 4 | −1.1% | +0.90% vs −1.87% (p 0.007*) | 0.53 (0.003) | 11 of 14 (p 0.029) |
| W2 (1Q24+) | 10 | 3 | −0.9% | +0.90% vs −2.06% (p 0.005*) | 0.67 (0.0004) | 8 of 10 (p 0.055) |
| 2021Q1+ | 22 | 5 | −2.7% | | 0.38 (0.038) | 12 of 22 (p 0.42) |

\* the 3Q25 split was chosen after seeing the data; descriptive. The ex-variable version (the revenue beat's own cost-of-revenue share
removed) gives the same verdicts. In 2021-22 the Street over-forecast cost of revenue; the under-forecast is a 2023+ feature.

**Our costs against LSEG's COGS consensus** (`41_cogs_attribution.csv`)

| | Street costs | Ours | Gap | of which cost of revenue | of which opex |
|---|---|---|---|---|---|
| 3Q26 | 2,383 | 2,384 | +2 | +9 | −7 |
| 4Q26 | 2,248 | 2,279 | +31 | +27 | +4 |
| FY26 | 9,136 | 9,170 | +34 | +39 | −5 |
| FY27 | 10,053 | 10,184 | +131 | +101 | +30 |

Street FY27 COGS grows 11.0%; our cost of revenue grows 13.4% (hosting $447M vs $330M of pre-plug run-rate).

**FY27 cost paths on the Street's FY26 cost base** (`41_fy27_scenarios.csv`)

| Cost growth | At Street revenue | At official v2 revenue |
|---|---|---|
| Street +10.0% | 36.45% (bar) | 34.82%, −$395M |
| Street + recent surprise +11.0% | 35.88%, −$91M, −$0.13 EPS | 34.24%, −$485M |
| Line-build growth +11.1% (rebased) | 35.86%, −$94M | 34.22%, −$488M |
| FY24-25 average +12.6% | **34.96%, −$235M, −$0.34 EPS** | 33.30%, −$630M, −$0.91 |
| (FY24-25 average from FY25, two years) | 36.3%, −$21M | |
| FY26E Street +15.0% | 33.58%, −$453M | 31.89%, −$848M |

## What failed or is weak

- T1 is post hoc and is reported as descriptive only. With n = 4 recent prints the regime could be noise. T2 is not independent of it
  (Codex F3) and T3 depends on two rounding-level prints (Codex F1): the cost-surprise evidence is descriptive, not a passed test.
- T2's own forecast for 3Q26 is slightly *below* the Street, so persistence supports the claim that costs stopped beating, not that they
  will overrun next quarter. The registered live call (costs above the Street) is scored on 5 Nov.
- The COGS consensus has no contributor count in the file and some observation dates are 3-4 weeks before the print. The basis matches
  reported cost of revenue closely (mean W1 gap +1.0%), so it is usable, but it is one field from one vendor.
- "EBITDA costs" include whatever add-backs the Street and the company make; lodging-tax reserves are added back on both sides.
- Parameter count: zero fitted parameters in the tables; T2 fits two per window.

## RESUME

Done. Next: (1) on 5 Nov score the live call in `41_live_3q26.csv` and append 3Q26 to the surprise record (the at-print consensus comes
from the L0 register or an LSEG pull that morning); (2) if the memo adopts the cost leg, quote bottom lines 1-3 with the caveats above,
never T1 as a test; (3) the hosting line (DEC-0023) is where the COR evidence points; a hosting schedule that separates committed cloud
spend from the AI ramp is the next build (see the 22 Sep audit, B-02).
