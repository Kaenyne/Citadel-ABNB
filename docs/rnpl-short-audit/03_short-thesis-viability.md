# Can we short Airbnb on Reserve Now, Pay Later? A devil's-advocate audit

- **Date:** 2026-09-11. **Author:** Opus audit agent for Theo.
- **Brief:** build the strongest RNPL-centred short a Citadel PM would state, then attack it with everything in this repository, then price the trade.
- **Read-only pass.** Nothing in the tree was edited; this is the only file written.
- **Evidence labels used throughout:** *measured* (disclosed or computed from a primary source), *derived* (computed from measured inputs under stated assumptions), *assumed* (a scenario input), *withdrawn* (a repo claim that has been retracted and must not be quoted as live).
- **Withdrawn numbers deliberately absent from this note,** per `docs/revenue-forecast-strategy/08_THESIS_MAP.html` §05 and `research/notes/overnight/14_master-synthesis.md` §11: the −3.4pp 4Q26 FX step, "82% determined", the +4.05% fee uplift as measured, the 9/9 drift rule as a mechanical rule, "half of ADR is unit size", and PR #32's "+10.2% consensus" (which is the team's own frozen card, not a Street number — `research/notes/2026-09-10_nights-baseline-reconciliation.md` §5).

---

## Bottom line

**(b) A supporting leg of a composition / "shape" thesis. Not a standalone short, and not a red herring.**

RNPL is the *mechanism* that explains why Airbnb's 2026 nights acceleration does not repeat. It is not, on this repository's own arithmetic, a *magnitude* large enough to carry a short by itself. The cancellation drag the hypothesis rests on is worth −0.10 to −1.37 growth points in 3Q26 across 2,025 parameter cells, while the level anniversary it sits next to is two to fifteen times bigger (`research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md` §1.6, *derived*). The one independent test the team ran for an RNPL cancellation signature — 34 markets, pre-registered — found none (`research/notes/overnight2/A_calendar-reopening-34-markets.md`, *measured*). The cleanest catalyst, P(4Q26 guide below Street), is 0.49 to 0.50 against the broad panels (`docs/revenue-forecast-strategy/05_backtests/B2_Q4_GUIDE_EXHIBIT.md`, *derived*), and the reaction rule that was supposed to monetise it is dead (`docs/revenue-forecast-strategy/05_backtests/RED_TEAM.md` must-fix #10: "Quote no p-value for the drift rule").

The thesis that survives is bigger than RNPL and smaller in its claims: **the composition of Airbnb's growth changes on dated schedules that the Street has not phased, and the equity is priced off forward growth at +0.48 turns per point.** RNPL is one of three product legs inside that, and the only one with a compounding term attached. Pitch it as a paragraph, not as the thesis.

---

## 1. The strongest RNPL-centred short, stated (247 words)

Airbnb's 2026 re-acceleration is a product bundle lapping, not demand. Management attributed "over 200 basis points of growth in nights booked and roughly 300 basis points of growth in GBV" (4Q25 call, ledger D014) and "approximately 3 points of nights / 4 points of GBV" (1Q26 call, D032) to RNPL **plus** the October-2025 cancellation redesign **plus** the single-fee migration [*measured*, `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md` §2.1]. Those legs anniversary on dated schedules: US RNPL from 3Q26, the global cancellation and fee legs from 4Q26, ex-NA RNPL from 1Q27 [*derived*, D §2.2].

The level gain stops contributing to y/y; the cancellation term does not. RNPL is over 20% of GBV (2Q26 call, D043); the platform cancellation rate went ~16% to ~17% (D017/D018); and the 2Q26 10-Q states in MD&A that RNPL bookings "have experienced higher cancellation rates than historic bookings" and that the timing among GBV, revenue and cash receipts "may become less correlated" [*measured*, `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §1.1]. Forty-six percent of 3Q26 and 49% of 4Q26 excess cancellations arrive from earlier booking cohorts [*derived*, D §2.4].

Re-based, 3Q26 nights are **+9.3%** (band 8.8–9.8) against a "low double digits" floor of 10.0, and 4Q26 **+7.6%** (7.2–8.1) against the team's 8.9% [*derived*, `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §2.4]. FY27 nights are +8.2% on an NA-only lap or +6.4% on a global lap against Street FY27 revenue +11.3% to +11.5% [*derived* / *measured*].

The multiple pays **+0.48 turns of EV/EBITDA per point of forward revenue growth and zero per point of margin** [*measured*, `research/notes/overnight/12_valuation-multiple-regime.md`]. Two to three points off FY27 growth is ~1.0–1.4 turns, ~$9–13 a share, 5–7% on a $181.94 spot. Short ABNB against QQQ into the composition, not the level.

---

## 2. The attack, ranked by damage

### Rank 1 — The arithmetic kills the size, and the team's own engine is what kills it

Across 2,025 parameter cells the incremental reported-nights effect of an RNPL cancellation-propensity assumption is **−0.10 to −1.37 growth points in 3Q26** and **−0.08 to −1.36 in 4Q26**; in the central cell, −0.15 at +1pt propensity, −0.62 at +4pts, −0.93 at the management-implied +6.0pts. The level lap is 1.35 points from the North American bundle alone plus 0.70–0.88 ex-NA. "**The anniversary is two to fifteen times the cancellation drag**" (`research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md` §1.6, §2.3, *derived*).

Worse for the short: **the drag laps too.** The 2025 denominator already contains US RNPL from 3Q25, so what remains is the y/y *increase* in excess cancellations, which was large into 1H26 (share ~0 to 20%) and much smaller into 2H26 (D §1.7, *derived*). This is the single most damaging fact in the file and it was produced by the team member trying to prove the thesis.

**Damage:** fatal to (a). The tradeable content of RNPL is an anniversary every competent sell-side model can also compute.

### Rank 2 — Management's net-benefit test, and the fact that the realised curves matched it

Four statements, all on the record (D §4, *measured*): cohorts were tested "to ensure that by the time the cohorts opting into the product had reached their check-in date, that it was net beneficial to the business, meaning that the growth lift in bookings was larger than the net increase in cancellations before check-in" (D019); realised cancellation curves are "very close to what we saw from a tested perspective" (D020); the elevated cancellations are "already absorbing" into results (D021); RNPL drives "a meaningful lift to all booking metrics, net of cancellation" (D033).

The honest rebuttal is narrow and the repo states it: the test is a **stay-date** test on a booking cohort, while Nights and Seats Booked is a **transaction-period** metric in which a cancellation reduces the quarter it occurs in (D054), so a product can pass management's test and still move nights between reported quarters (D §1.9). That is a timing argument worth at most ~1 growth point. It is not an economics argument, and a judge will hear the difference.

**Damage:** severe. It reduces the thesis from "the product is bad" to "the product moves nights between quarters", which is a one-point claim.

### Rank 3 — 19 of 19 beats and the cushion mechanism remove the revenue leg entirely

`docs/revenue-forecast-strategy/05_backtests/guidance-policy.md` (*measured*): **19 of 19** prints beat the guide midpoint, **0** below the low end, **15 of 19** above the top of the range. `guide midpoint × (1 + trailing-8 mean cushion)` — one free parameter, cushion **1.8562%** at the 6 Aug 2026 guide date — forecasts the revenue level at **RMSE/naive 0.379 (W1, n 14) and 0.331 (W2, n 10)**, MAPE ~1.0%, surviving both windows.

So there is no revenue short once Airbnb has guided. Anything the memo says about revenue is an argument about the *next* guide, not this print. That removes the loudest line item from the short and forces it onto nights and composition, where no public consensus exists to be missed (`docs/revenue-forecast-strategy/05_backtests/A1_consensus_vintages.md`: no nights, ADR or GBV forward consensus exists anywhere, *measured*).

**Damage:** severe, and structural. It also means the short cannot be scored against a visible bar.

### Rank 4 — The one hard catalyst is a coin toss, and the panel it is measured against is contested

`docs/revenue-forecast-strategy/05_backtests/B2_Q4_GUIDE_EXHIBIT.md` (*derived*): the unconditional 4Q26 guide midpoint is **$3,161.3M**, 80% band **$3,011.9–3,311.8**, sd $117.0M (3.70%). P(below LSEG-family $3,158) = **0.492**; P(below S&P $3,160) = **0.499**; P(below Zacks $3,200, n 10) = **0.632**. If the half fee step lands, those become **0.433 / 0.440 / 0.575**.

Two further cuts. First, B2's own caveat 4: Zacks' $3,200 mean carries a probably-bad $3,700 high; **its median is nearer $3,150, "which would remove the trade."** Second, `A1_consensus_vintages.md` shows the panel spread is only **$41.9M (1.33%)** across four vendors, of which Yahoo and Alpha Vantage are one LSEG/Refinitiv panel — so there are **three** panels, not four, and the two broad ones sit at 3,158/3,160, i.e. exactly on the modelled midpoint.

**Damage:** severe. The short's single dated catalyst inside the horizon is 49/51.

### Rank 5 — The drift rule is dead, so there is no reaction function to monetise the catalyst

Three p-values circulate for "guide below Street → negative 20-day drift" (`docs/revenue-forecast-strategy/05_backtests/RED_TEAM.md`, *withdrawn as a mechanical rule*):

| Convention | Result | p |
|---|---|---|
| Next-session **open** entry, binomial vs ABNB's own 69.6% negative base rate (n 23) | 9/9 negative, mean −4.21%, median −4.42% | **0.038** |
| Next-session open entry, Fisher in-window | mean −4.21% | **0.27** |
| **Reaction-day close** entry | **8 of 9** negative; below −4.84% vs above −3.34%, spread −1.50pp | **0.141** |
| 5-day executable | −2.18% vs −3.00%, spread +0.82pp | 0.650 |

And the killer: **2022Q3–2025Q1 had 9 of 11 prints negative regardless of guide sign, and 8 of the 9 guide-below observations fall in that window.** Outside it, only 4 of 8 are negative and 1 of 8 is guide-below. RED_TEAM's verdict is "**NOT A SIGNAL**" and its must-fix #10 is "**Quote no p-value for the drift rule.**" `08_THESIS_MAP.html` lists it under **dead**: "9/9 drift rule (8/9 executable, p 0.14–0.27)".

Separately, **Gate G4 FAILS**: the sign test against vintage-stamped pre-guide Street is 7/14 on W1 (p 0.605) and 4/10 on W2 (p 0.828). The programme cannot forecast the *direction* of guide-vs-Street out of sample; it only passes on full-sample leakage.

**Damage:** severe. Even if the guide comes in low, the repo no longer claims to know what the stock does.

### Rank 6 — The 34-market calendar test is a clean pre-registered null

`research/notes/overnight2/A_calendar-reopening-34-markets.md` (*measured*, pre-registration written into the file before the script ran):

- Rome is idiosyncratic: late-minus-early short-run reopening **+1.46 pts** against **London −2.34, Paris −2.18, Barcelona −0.85**; pooled European night-weighted ex-Rome **−1.97 pts**.
- Non-US minus US market-mean change **+2.12 pts**, label-permutation **p 0.259** on 32 markets.
- The largest increase sits in **Australia (+3.21 pts, bootstrap 1.45–4.90)** — the pre-registered **opposite-season control**, which is not what a common February treatment predicts.
- Pre-rollout (Sep–Dec) the **US level was already higher** than the rest of the world (12.59% vs 8.72%), so the cross-sectional ordering is the opposite of treatment status.
- **San Diego**, treated since 3Q25, is one of only five markets whose increase excludes zero.
- The tilt is fragile: dropping Barossa Valley moves the non-US market-mean from +0.23 to **−0.47**.
- "**No haircut is applied to any nights, revenue or EPS forecast from this workstream.**"

The note states exactly what would have supported the hypothesis and reports that the opposite set is what the data show. This is the only independent attempt at the causal question in the repo, and it is negative.

**Damage:** high. It is the evidence a judge will ask for, and it says no.

### Rank 7 — July 2026 is fresh treatment inside the very quarter being printed

RNPL eligible booking types expanded in **July 2026** (2Q26 call, D044), types unnamed. D §5 calls it "**the largest unquantified offset to the 3Q26 lap and… the only thing in the ledger that is fresh treatment inside the quarter being printed**" (*measured* date, *unquantified* size). Theo's bridge puts only +0.30 / +0.20 / +0.10 points on it by scenario and says so deliberately (`research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §2.4, *assumed*). If it is worth a full point, 3Q26 nights clear the 10.0 floor and the thesis loses its first test.

**Damage:** high, and asymmetric — it is an unbounded offset against a bounded drag.

### Rank 8 — The CEO has already told you RNPL is not the variable

"The pricing roadmap is many multiples bigger than RNPL" (CEO, ledger D053, *measured*). Management's own named offsets to the lap are global RNPL ramp, the July eligibility expansion, hotels growing ~3x homes, first-time bookers +11% ("highest in four years"), Experiences supply +80% (`docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` §5.4, *measured*).

**Damage:** high in a Q&A. A short whose engine is the small term invites "why are you arguing about this?"

### Rank 9 — The FX lap steals the short's own evidence

Revenue FX runs **+3.0pp (3Q26) → −0.4pp (4Q26) → −0.6pp (FY27)**, and **84% of the 4Q26 driver has already happened** (`research/notes/overnight/14_master-synthesis.md` §8.1–8.2, *derived*; do not quote the withdrawn "82% determined" or the withdrawn −3.4pp step). `docs/2026-09-07_research-state-of-play.md` states it plainly: about 3 points of the Q4 step-down is arithmetic, "so nobody reads the step-down as a demand break on 5 November."

A soft Q4 guide is therefore **over-determined**. The RNPL short cannot claim it as evidence, because FX explains it first and management will say so on the call.

**Damage:** high. It removes the most visible confirming datapoint from the bear's hands.

### Rank 10 — The Q3 print lands after the finals, and nothing else does

Prelim memo + model due **2 Oct 2026**; finalists notified **12 Oct**; NYC finals **22–24 Oct**; ABNB prints **Thu 5 Nov 2026 AMC** (`docs/competition/citadel_2026_format.md`, *measured*; `docs/revenue-forecast-strategy/05_backtests/A1_consensus_vintages.md` confirms the date). `research/notes/catalyst_calendar.md` is explicit: "**no ABNB print falls between 2 Oct and 24 Oct.** The stock will trade on the EU act, AI-distribution headlines, macro and peer prints. The thesis has to be a view on the ~5 Nov Q4 nights guide."

Two consequences. The thesis is judged on a **forecast of a guide**, never on a realised print; and the options structure that would make the trade defined-risk cannot be priced until the 6 Nov weekly lists in the week of **26–30 Oct** — i.e. after the finals (`research/notes/overnight/14_master-synthesis.md` §6.3, *measured*).

**Damage:** high, and specific to this competition.

### Rank 11 — The loss case is documented and it is recent

- **7 Aug 2026: +17.4%**, and `research/notes/2026-09-05_abnb-major-moves.md` records it as **the first 7%+ up move in the dataset that did not fade within 20 sessions** (+22.2% raw after 20 sessions). Its §4.2 names "the 17% squeeze" as the risk for a short.
- Mean absolute day-1 move **7.07%**, median 6.87%; **10 of 23 prints moved ≥8%** and 5 of 23 moved ≤1.1% — bimodal, big or nothing (`research/notes/overnight/14_master-synthesis.md` §6.3, *measured*).
- Short interest **2.17% of shares** (14 Aug 2026, near the lowest since 2023; `research/notes/overnight/09_stock-behaviour-and-alpha.md`) or **3.39% of float** (`research/notes/2026-09-04_abnb-pitch-landscape.md`). Either way, **no squeeze fuel and no crowded-short cushion**, and short interest is uncorrelated with forward 1- and 3-month returns (|r| ≤ 0.15).
- **Buybacks are a floor, not a catalyst:** $2.1bn repurchased in 1H26, **$3.4bn authorisation remaining**, diluted shares 649M (2Q24) → 597M (2Q26), −8% in two years; and buyback authorisations produce abnormal returns indistinguishable from zero and are never announced off-cycle (`09_stock-behaviour-and-alpha.md` §6, *measured*). The catalyst calendar's own analogue: "**Floor on selloffs, not a spike.**"

**Damage:** high for sizing, moderate for the thesis.

### Rank 12 — Theo's own exposure solve shrinks the tail, and the balance-sheet test is confounded

`research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` (*derived*): the joint solve of unearned fees and funds payable gives **7 to 19 million live unpaid nights at 30 June**, against the **40 million illustrative** exposure in `outputs/rnpl-audit-20260910/materiality.md`. At 7–19M, a one-point 3Q26 haircut **from the opening backlog alone** needs a **7 to 17 point** upward revision in conditional cancellation probability — "**which is implausible**". Materiality: one point of Q3 growth is **1.336M** net lost nights, one point of Q4 is **1.219M**.

And the pre-registered unearned-fees test is contaminated: unearned fees and funds payable diverge from 4Q25 because of the **single-fee migration**, not RNPL, and deferral-only scenarios give 3Q26 unearned fees **anywhere from −2% to −17% y/y with no cancellation effect at all** (§1.2). Neither line can see a cancelled RNPL booking, "because a cancelled RNPL booking was never recorded" (§2.3).

**Damage:** moderate-to-high. It bounds the tail and disarms the cleanest pre-registered test.

### Rank 13 — Everything else, in one block

- **The alt data says "no acceleration", not "RNPL drag".** Reviews stays index **+9.5%** (band 8.5–11.0, the first team series to beat a naive forecast out of sample, WF RMSE ratio 0.68); external stack **+9.2%** median (6.8–12.0); hotel RevPAR fading through August (`docs/q3nowcast/SYNTHESIS.md`, *measured*). All three sit inside D §5's **inconclusive** band (8.6–10.2). The stays index cannot see a booking-date tail by construction (SYNTHESIS §3.3).
- **The lap is already a known bear point.** `research/notes/2026-09-04_abnb-pitch-landscape.md` records live debate #1 as "~2–4 pts came from RNPL + cancellation-policy changes + fee migration… RNPL laps from Q3'26," and the Finn bear scorecard already lists "RNPL cancellations and cash timing." Not virgin territory.
- **The guide already contains the lap.** The 3Q26 "low double digits" nights guide "was set on 6 August with July bookings in hand, so it already contains management's own view of the lap and of the World Cup residual" (`03_insider_mechanics.md` §5.4, *measured*).
- **The repo has already corrected this exact misattribution once.** `research/notes/overnight/15_red-team.md` CONF-12 and its do-not-say list: "**'Reserve Now Pay Later added 3 points of nights growth.' It was three features, not one.**"
- **The valuation argument does the work, not RNPL.** Base football-field mean **$156.79**, 25/50/25 across all lenses **$154**, base EV/EBITDA FY2027E lens **$180.88** against a **$181.94** spot; "the base case carries a 12-month target of about $181" (`14_master-synthesis.md` §0, §8.1, §11.5). A short on ABNB is a multiple short with an RNPL skin unless the growth number moves.
- **One turn of EV/NTM EBITDA is $9.11 = 5.0%** (`14_master-synthesis.md` §7.1; WS12's per-lens range is $8.6 / $10.3 / $11.8). A typical print moves the forward multiple ~1.5 turns — i.e. the print noise is larger than two points of FY27 growth.
- **ADR risk is one-sided against the short.** The like-for-like pricing residual stepped from 1.9–3.5pp (2023–25) to **4.4pp in 1Q26 and 4.9pp in 2Q26** and is 31% of the 3Q26 band variance; the component build **fails** its walk-forward (RMSE 1.29 vs 0.82 naive) and is biased ~1.5pp low into accelerations (`research/notes/q3nowcast/H_3q26-adr-card.md`, *measured*). A mean-reverting residual gives reported ADR nearer +0.8% against management's "moderate increase" and the team's +3.0–3.2% — which is a *revenue* bear point, not an RNPL one, and it is the leg with the better evidence.
- **Take rate cuts both ways.** The single 15.5% fee is worth **+40 to +50bps only if the replaced blended guest fee was 14.1%**, −15bps at 15.0% and −124bps at 16.5%; the 6–10% direct-link pilot is the first explicit cut but is worth **0–15bp of FY27 take rate**, with −0.8pt reserved for a "pilot becomes policy" tail (`14_master-synthesis.md` §8.3, *measured* mechanics / *derived* sizing).
- **Airbnb is taking share.** Booking.com's alternative-accommodation premium over its own total room nights went from **+6 pts (3Q24) to −1 pt (2Q26)**: alt-accom +4% against Airbnb's +10.3%, verified against the SEC-filed BKNG Q2'26 release (`14_master-synthesis.md` §8.2, *measured*). This is the fact that most directly contradicts a demand-side short.
- **Two documented pieces of internal fragility on the short's side.** Gate **G1 FAILS** (the backlog construction does not beat naive on revenue growth on both windows: 1.171 W1 / 1.168 W2); Gate **G3 FAILS** (the 120-market bottom-up panel is not usable as a nights measurement). The RNPL-corrected backlog ratio of 0.680/0.593 is "corroboration, not a cleared G1" (`RED_TEAM.md`, *measured*).
- **One sourcing flag to respect.** `RED_TEAM.md` §7 notes the **15 Sep / 13 Oct 2026 fee-migration deadlines have no primary source in the repository**, although `research/notes/2026-09-07_fee-churn-catalyst.md` and `03_insider_mechanics.md` §4 both carry them (from a PMS supplier notice and Airbnb's host resource page). Do not present them as company disclosure in the memo.

---

## 3. Trade construction

### 3.1 Catalysts, in order

| Date | Event | What it can move | Status |
|---|---|---|---|
| **13 Oct 2026** (15 Sep for ex-EEA) | Single-fee migration deadline, EEA + Switzerland, by **host residence** | Not RNPL. Listed prices may rise **~14.8%** for the migrating cohort if hosts reprice to hold payout — **unmodelled anywhere** (`03_insider_mechanics.md` §4). The transition window recreates the 2020 relative-price effect in reverse: early switchers look ~15% more expensive on dateless searches (`research/notes/host_only_fee_history_and_elasticity.md` §3) | *measured* mechanics, *unverified* dates (RED_TEAM §7). The **only** catalyst between the prelim deadline and the finals |
| **5 Nov 2026 AMC** | 3Q26 print, 4Q26 guide, and **whether the quantified bundle contribution returns** (over 200bp in 4Q25, ~3pts in 1Q26, **silence in 2Q26**) | The whole thesis. D §1.1: "Whether the figure returns on 5 November, and at what level, is the most direct read available on whether the lap is biting" | *measured* schedule. **After the finals** |
| **~11 Feb 2027** | 4Q26 print, **1Q27 guide**, FY27 framing | The shape trade. Note: "**the Feb-2027 'FY27 guide' does not exist as a point**" — ABNB guides a 1Q27 range plus qualitative colour (`docs/revenue-forecast-strategy/05_backtests/OPTIMAL_MIX.md`; `07_MORNING_REPORT.md` §"Do not let the memo imply…") | *measured*. Inside the 3–12 month horizon from 2 Oct |

Also dated and worth one line each: 9 Sep 2026 EU Affordable Housing Act draft (0 of 41 ≥7% moves have ever been regulatory); FOMC 15–16 Sep, 27–28 Oct, 8–9 Dec; BKNG/EXPE Q3 prints late Oct (peer read-across is null: 2 nominal hits in 24 tests with contradictory signs).

### 3.2 The reaction function as it stands after the red team

**Executable:**
- `guide × (1 + trailing-8 mean cushion)` forecasts the revenue **level** at RMSE/naive **0.379 / 0.331**. A forecasting tool, not a trade (`guidance-policy.md`).
- Base rates only, on the executable next-session-open convention (`data/processed/overnight/20_executable_returns.csv`, recomputed for this note):

| Group | n | Mean 20d excess | Median | sd | Negative |
|---|---|---|---|---|---|
| All prints | 23 | **−2.18%** | −3.76% | 7.83 | 16 (69.6%) |
| Guide **below** Street | 9 | **−4.21%** | −4.42% | 3.83 | 9 |
| Guide **at/above** Street | 14 | **−0.88%** | −1.39% | 9.50 | 7 |
| Guide below Street, **day 1** | 9 | **+0.91%** | — | — | **3** |

Note the last row: **the day-1 half of the rule collapses entirely** under an executable entry.

**Withdrawn / not executable:**
- The **nights-surprise → 20-day drift**: legacy LOO R² +0.156 becomes **−0.016** on an open entry, walk-forward **1.076×** the zero baseline; **zero of WS20's 18 primary executable drift specs beat their baselines** (`research/notes/overnight/20_temporal-validation.md` §4, §9).
- **All day-1 alpha**: the overnight gap is **73%** of the variance of the legacy day-1 number; mean absolute day-1 move capturable at the open is **3.22%** against a **7.07%** headline base rate (20_temporal-validation §1, §11).
- The **guide-below-Street rule as a mechanical rule** — see Rank 5. Quote it as a base rate with its n, or not at all.
- Gate **G4 fails**, so the sign of guide-vs-Street is itself not forecastable out of sample.

Legacy-convention numbers that still appear in the deck and must be labelled as non-executable: `05_reaction_by_accel.csv` post-2022 decelerating prints day-1 excess **−5.9%** (n 9) and 20-day **−8.0%**; accelerating **+6.0%** day-1, **+1.3%** 20-day (n 5/4). These start at the pre-release close and cannot be transacted.

### 3.3 Expected-value sketch

**Assumptions, stated in full.**
1. Trade: short ABNB, long QQQ at equal notional (every return in this repository is ABNB minus QQQ). Entry at the **open of the reaction session** (6 Nov); exit at the close of the 20th session (~4 Dec). This is the only convention the repo treats as executable.
2. Payoff distribution: the repo's own conditional executable 20-day excess returns, treated as the sampling distribution. n = 9 (guide below) and n = 14 (guide at/above). **This over-states the edge**, because RED_TEAM calls the conditioning a calendar artefact.
3. P(guide below the panel) from B2: **0.49** against the LSEG-family/S&P broad panels (n 35–36). The Zacks-based 0.632 is not used because B2's caveat 4 says the Zacks median is nearer $3,150.
4. No RNPL-specific term is added, because nothing in this repository measures one.
5. Frictions, borrow and carry ignored; the sketch is gross.

**Arithmetic.**
- E[20-day excess] = 0.49 × (−4.21%) + 0.51 × (−0.88%) = **−2.51%** → **EV(short) ≈ +2.5%**.
- Mixture sd ≈ **7.5%**. Ratio of edge to dispersion ≈ **0.34** for the single event.
- P(the short loses money) ≈ 0.49 × 0/9 + 0.51 × 7/14 = **~0.26** on these samples.
- **Strip the conditioning** (RED_TEAM's position) and the answer is the unconditional base rate: EV(short) **+2.18%**, sd **7.83%**, P(loss) **7/23 = 0.30**.

**The finding that matters: conditioning on the Q4 guide is worth about +0.33 percentage points of expected 20-day excess return.** The whole "RNPL → weak guide → short" channel adds a third of a point to a base rate that already exists for every ABNB print, because P is a coin toss and the unconditional drift is already negative. That is not a thesis; it is a base rate with a story attached.

**If you hold the overnight gap** (short from the pre-release close): historical mean 20-day excess is **−3.51%**, sd **9.19%** — i.e. +1.33pp more EV for +1.4pp more sd. But the gap itself has mean **−0.99%** with sd **7.40%** (t ≈ −0.64): **no evidence the gap has a negative mean. Do not size for it.**

**Sanity check against the multiple.** Two to three points off FY27 revenue growth at +0.48 turns/point is 0.96–1.44 turns; at $9.11 a turn that is **$8.7–13.1 a share, 4.8–7.2%** on $181.94. That is the *fundamental* prize, and it is roughly 2–3x the event EV — which is the argument for the shape trade over the print trade.

### 3.4 Pre-registered flip rules

**From `research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md` §5, scored on the 3Q26 print:**

| Metric | Supports the drag | Weakens it | Inconclusive |
|---|---|---|---|
| 3Q26 nights y/y | ≤ 8.5% (≤ 144.9mm) | ≥ 10.3% (≥ 147.3mm) | 8.6–10.2% |
| 3Q26 GBV minus nights growth | widens > 7 pts with nights ≤ 9% | narrows < 4.5 pts with nights ≥ 10% | 4.5–7 pts |
| 3Q26 quarter-end unearned fees y/y | ≤ −3% (< ~$1,765mm) | ≥ +6% (~$1,930mm+) | −3% to +6% |
| Backlog conversion, rev / (rev + closing UF) | ≥ 74% | 70–71% (pre-RNPL constant) | 71–74% |
| **4Q26 nights guide** | implies ≤ 7.5% | implies ≥ 9.5% | 7.6–9.4% |
| RNPL GBV share disclosed for 3Q26 | flat or down vs 2Q26 **while nights decelerate** | ≥ 25% with nights ≥ 10% | 21–24% |
| **Quantified bundle contribution for 3Q26** | none given, or ≤ 1.5 pts | ≥ 2.5 pts | qualitative only |

**Theo's replacement for row 3** (`research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §2.3, and §5 item 3 asks for it to be swapped before the card is frozen): **score funds payable, not unearned fees.** Funds payable y/y **+5% to +11%** is deferral on schedule; **below +3%** means the unpaid book is larger than modelled — **more adoption, not more cancellation**; and the unearned-fees-minus-funds-payable growth gap is the **migration** term and should widen. Deferral-only scenarios put 3Q26 unearned fees anywhere from **−2% to −17% y/y with no cancellation effect at all**, so the original row can be tripped by migration alone.

Read the direction of the unearned-fee row carefully (D §5): **management predicted unearned fees would be *higher* in Q3** (1Q26 letter, D038), so a weak print contradicts management and a strong print says the deferred fees are arriving on schedule.

### 3.5 Options

`data/processed/overnight/23_options_event_estimates.csv`, run 6 Sep 2026, model `sigma_i^2*T_i = b*T_i + E*d_i` (*measured*, and the answer is "not identified"):

| Spec | Maturities | Event sd | Implied abs move | Note |
|---|---|---|---|---|
| `all_eligible` | 10 (7 pre, 3 post) | **6.726%** | 5.367% | LOO range 5.227–8.051%; background vol 36.209% ann. |
| `pre_plus_first_post` | 23 Oct / 20 Nov | **2.311%** | 1.844% | |
| `first_two_post` | 20 Nov / 18 Dec | **non-positive** | — | "the fitted term structure shows no event kink"; explicitly **not** evidence that no premium is priced |

Three mutually irreconcilable answers, because the 6 Nov weekly was **not listed on 6 Sep** — the chain jumps 23 Oct → 20 Nov. The prior "implied event premium ≈ 0" claim is **withdrawn**, not corrected. The usable number today is the historical base rate: mean absolute day-1 move **7.07%**, median 6.87%, 10 of 23 ≥8%, 5 of 23 ≤1.1%.

**Action, and its timing problem:** re-run `analysis/src/abnb_options_ledger.py` and `23_update_ws09_options.py` in the week of **26–30 Oct**, once a 30 Oct pre-event and 6 Nov post-event pair exists; then, and only if the three specifications agree within ~1.5 points, **below ~7% implied E the structure is cheap against the 7.1% base rate and above ~9% it is rich** (`14_master-synthesis.md` §6.3). **That week falls after the finals (22–24 Oct).** The defined-risk expression therefore cannot be priced inside the competition; it can only be described.

### 3.6 Print trade vs shape trade vs relative

**(A) The print trade — short into 5 Nov.**
EV **+2.2% to +2.5%** of 20-day beta-hedged excess, sd **7.5–7.8%**, P(loss) **0.26–0.30**, on a conditioning variable the red team calls "not a signal" and a probability of 0.49. The payoff is bimodal and 73% of the day-1 move is an ungettable gap. It resolves **after** the competition. **Verdict: not the pitch.** If run at all, run it as a put spread priced in the week of 26–30 Oct, not as stock.

**(B) The shape trade — short into the February 1Q27 guide and FY27 framing.**
This is where the repository's own disagreement with the Street lives: "**The disagreement with the Street is not the annual number, it is the shape:** base-case 1Q27 **+9.9%** against 1Q26's **+17.9%**, and 2Q27 **+10.7%** against **+16.5%**. If the Street phases FY27 like FY26, its first half is too high" (`03_insider_mechanics.md` §5.5, *derived*). The kernel puts the **1Q27 guide midpoint at $2,930–2,990m, +9.4% to +11.6% y/y — the first sub-teens quarterly guide since 2023** (`M3_guidance_function_and_revision_game.md`, *derived*). It is also where RNPL carries real weight: ex-NA RNPL laps in 1Q27 (partial, 5–6 of 13 weeks) and fully from 2Q27, and the NA-vs-global lap switch is worth **1.8 points of FY27** (`2026-09-10_nights-baseline-reconciliation.md` §3, *derived*). Jessie's plateau-plus-drag skeleton is the right FY27 structure (same note §4.2), and her annual build already carries the cancellation term at **−0.6 pts in 2026 and −0.9 in 2027**.

Two honest costs. First, **February is ABNB's best month**: +7.7% excess vs QQQ, **6 of 6**, p 0.005 — and it is mechanically the Q4 print, which has produced a positive day-1 move in **all six** observations (+13.3, +3.6, +13.4, −1.7, +14.4, +4.6) (`09_stock-behaviour-and-alpha.md` §5, `14_master-synthesis.md` §7.1). A February short is short the one print in the year that has never gone against a long. Second, the FY27 annual number is not in dispute — three team constructions land within a point of the Street (+11.3% to +11.6% vs $15.73–15.76bn).

**Verdict: this is the trade the evidence supports**, entered before the November print and held through to the February guide (a 3–12 month horizon the format explicitly allows), sized down into the Feb print itself.

**(C) Relative / pairs.**
The repo does **not** support a pair. Peer read-across into ABNB is null (2 nominal hits in 24 tests, contradictory signs); ABNB's univariate beta to the OTAs fell to **0.54** and to hotels **0.45** in 2026; **64% of 2026 daily variance is idiosyncratic** and the entire 2026 +34% move is model alpha (+32.7 pts) (`09_stock-behaviour-and-alpha.md` §1, §3). A BKNG pair is worse than neutral: it fights the one measured fundamental fact in Airbnb's favour — **BKNG alternative-accommodation room nights +4% against Airbnb's +10.3%**, with the premium gone from +6 pts (3Q24) to −1 pt (2Q26).

**The construction the evidence does support is the one every statistic in the repo already uses: short ABNB, hedged against QQQ** (2026 multivariate β 0.91; rolling 126-day β 0.86). Note the one style caveat: ABNB carries a **−0.77 momentum loading in 2026** (t −6.6), so a short in this name is implicitly long momentum.

### 3.7 Sizing discipline the judges would expect

`docs/competition/README.md` is an empty placeholder and `citadel_2026_format.md` records that "judging criteria are not published", so there is **no repo-sourced rubric**. What follows is inference from the format (2-page PDF including appendix, model attached, 3–12 month horizon) and from the repo's own discipline.

1. **Size on the loss tail, not the EV.** ABNB's 2026 annualised vol is **39.1%**, idiosyncratic vol **31.2%**; a typical print moves the forward multiple ~1.5 turns ≈ **7.5%**; the worst recent single day for a short was **+17.4%** and it did not fade. Underwrite the position to a +17% day, not to a 7% one.
2. **Use the guide flag for sizing, never as the trade.** WS20's own instruction: "Use it for sizing, not as a short" — and after RED_TEAM, without a p-value attached.
3. **Name the invalidation before the entry.** The seven D §5 cells plus Theo's funds-payable rule are already pre-registered; put the "weakens" column on the page and state the cut.
4. **Defined risk where possible.** The day-1 distribution is bimodal (10 of 23 ≥8%, 5 of 23 ≤1.1%), which argues for a put spread over stock — but the event premium is not identifiable until the week of 26–30 Oct, so the memo should say "we would express this as a Nov put spread if the fitted event sd prints below ~7%; otherwise stock", and state the fallback size.
5. **A number, not an adjective.** On a 39% vol name with a ~2.5% event edge and a 7.5% event sd, a 1–2% notional core with the option to add on the D §5 confirmations is the defensible answer. Say it, and say what takes it to zero.
6. **Do not lean on borrow or a squeeze.** Short interest is at a three-year low and uncorrelated with forward returns; buybacks are a documented floor with $3.4bn of authorisation remaining.

---

## 4. The eight hardest judge questions, and the honest one-line answers

**1. "Management tested this. The cohorts were net beneficial by check-in and the realised cancellation curves matched the tests. Why are they wrong?"**
They are not wrong — their test is a stay-date test on a booking cohort while Nights and Seats Booked is a transaction-period metric, so the product can be net beneficial and still move nights between reported quarters, which is a timing claim worth at most about one growth point, not an economics claim (`research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md` §1.9, ledger D019/D020/D021/D054).

**2. "Size it. How many points of nights growth is the cancellation tail, and what is the live exposure?"**
−0.10 to −1.37 points in 3Q26 across 2,025 cells and −0.15 to −0.93 in the central cell, against a level anniversary two to fifteen times larger; the live unpaid book solves to 7–19 million nights at 30 June against a 40 million illustrative, at which a one-point haircut from the opening backlog needs an implausible 7–17 point revision in conditional cancellation probability (D §1.6/§2.3; `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §1.3; `outputs/rnpl-audit-20260910/materiality.md`: one point = 1.336M Q3 nights).

**3. "You tested 34 markets for a cancellation signature. What did you find?"**
Nothing: Rome is idiosyncratic (+1.46 pts against London −2.34, Paris −2.18, Barcelona −0.85), non-US minus US is +2.12 pts at permutation p 0.259, the largest rise sits in Australia — the pre-registered opposite-season control — and the US level was already higher pre-rollout (12.59% vs 8.72%), so no haircut was applied (`research/notes/overnight2/A_calendar-reopening-34-markets.md`).

**4. "About three points of the Q4 revenue step-down is a dollar lap. How do I know a weak guide is RNPL and not FX?"**
You cannot tell from revenue — revenue FX goes +3.0pp in 3Q26 to −0.4pp in 4Q26 to −0.6pp in FY27 with 84% of the 4Q26 driver already realised — which is exactly why the thesis has to be argued on the nights line and the bundle anniversary and never on the revenue guide (`research/notes/overnight/14_master-synthesis.md` §8.1–8.2; `docs/2026-09-07_research-state-of-play.md`).

**5. "Airbnb has beaten its own guide 19 times out of 19. What exactly are you short?"**
Not the revenue level — guide × (1 + trailing-8 cushion of 1.8562%) forecasts it at RMSE/naive 0.379 and 0.331 across both windows — we are short the **next** guide and the composition of growth, on a nights line for which no public consensus exists in any vendor we can reach (`docs/revenue-forecast-strategy/05_backtests/guidance-policy.md`; `A1_consensus_vintages.md`).

**6. "Your CEO says the pricing roadmap is 'many multiples bigger than RNPL.' Aren't you arguing about the small term?"**
Yes, if RNPL is the thesis — which is why it is not: RNPL is the mechanism that explains why a one-off level gain does not repeat, and the position is on the whole three-leg bundle anniversary plus the FX lap, with RNPL the smallest measured leg (ledger D053; D §2.2).

**7. "Your catalyst is 5 November, which is after the finals, and your own reaction rule is dead. What do I own for the next six weeks?"**
A base rate and a forecast, honestly labelled: no ABNB print falls between 2 Oct and 24 Oct, P(4Q26 guide below the broad panels) is 0.49–0.50, the guide-below drift rule is "not a signal" with three incompatible p-values (0.27 / 0.038 / 0.141) and 8 of its 9 observations inside a window where 9 of 11 prints fell regardless, and no event-implied move is identifiable until the 6 Nov weekly lists in the week of 26–30 Oct (`catalyst_calendar.md`; `B2_Q4_GUIDE_EXHIBIT.md`; `RED_TEAM.md`; `23_options_event_estimates.csv`).

**8. "The last print was +17.4% and it did not fade, short interest is 2.17%, and they have $3.4bn of buyback left. What is your stop and your size?"**
1–2% of notional, QQQ-hedged, underwritten to a +17% day rather than the 7.07% mean absolute move, cut on the pre-registered "weakens" column — 3Q26 nights ≥10.3%, a 4Q26 nights guide implying ≥9.5%, a bundle contribution ≥2.5 points, or funds payable below +3% (which reads as more adoption, not more cancellation) — and we do not rely on borrow, positioning or a buyback pause, because buyback authorisations produce abnormal returns indistinguishable from zero (`2026-09-05_abnb-major-moves.md` §4.2; `09_stock-behaviour-and-alpha.md` §6, §9; D §5; `2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` §2.3).

---

## 5. Verdict

**(b) A supporting leg of a composition / "shape" thesis.**

**Why not (a), a standalone short.** Four independent constraints, each sufficient on its own. The drag is bounded at −0.10 to −1.37 points of 3Q26 nights and is two to fifteen times smaller than the anniversary it sits beside, and it laps too. The only causal test in the repository — 34 markets, pre-registered, with the falsifying patterns written down in advance — is a clean null. The live exposure solves to 7–19 million nights, not 40. And the trade that would express it is a 0.49 coin toss monetised by a rule the red team has ruled "not a signal", resolving three weeks after the finals. A standalone RNPL short is a one-point claim dressed as a thesis, and the first judge question dismantles it.

**Why not (c), a red herring.** RNPL is the only *dated, mechanical, disclosed* reason why Airbnb's 2026 growth rate does not repeat, and it is the only one with a compounding term. Three facts survive every attack in section 2: management quantified the bundle twice and then stopped (over 200bp → ~3 points → silence); the 2Q26 10-Q says in audited MD&A that RNPL bookings cancel more and that GBV-to-revenue-to-cash timing "may become less correlated"; and the anniversary schedule is pinned to sourced dates (US 3Q26, global cancellation/fee legs 4Q26, ex-NA RNPL 1Q27). That is the spine of the FY27 shape argument — 1Q27 +9.9% against 1Q26's +17.9%, 2Q27 +10.7% against +16.5% — and the shape is where the multiple pays, at +0.48 turns per point of forward growth and zero per point of margin. Two to three points is $9–13 a share on $181.94.

**What the memo should therefore say.** The variant perception is *composition*: reported FY27 growth will look worse than FY27 demand, and both reasons are already knowable — a dollar lap that is 84% realised, and a three-leg product bundle that anniversaries on three dates. RNPL is one paragraph inside that: the reason the level gain does not repeat and the reason the cancellation line keeps drifting. It is not the headline and it is not the number.

**What would move me to (a):**
1. A reservation-event panel (PMS or channel manager) with an RNPL flag, booking date, cancellation date and policy, giving a **measured** cancellation propensity above about +6 points **and** a measured live exposure above ~40 million nights. That combination is the only route to a ≥1.5-point drag, and D §4 states plainly that the engine cannot measure either.
2. IR disclosing the unbilled confirmed-bookings balance Airbnb already hedges (ledger D056) at a level implying more than ~40 million live unpaid nights.
3. On 5 Nov, three of the seven pre-registered "supports" cells firing together — nights ≤8.5%, the 4Q26 nights guide implying ≤7.5%, and no bundle contribution given (or ≤1.5 points).

**What would move me to (c):**
1. On 5 Nov, nights ≥10.3% with a restated bundle contribution ≥2.5 points and an RNPL GBV share ≥25% — the level is still compounding and there is no tail.
2. Funds payable +5% to +11% with the unearned-fees-minus-funds-payable gap widening: deferral on schedule, migration doing the work, no cancellation signal.
3. Any quantification of the July 2026 eligibility expansion large enough to offset the US lap — the one unbounded term on the other side.

**What would move me off the *composition* thesis altogether** (i.e. kill the short, not just the RNPL leg): a 4Q26 guide midpoint at or above ~$3.17bn with nights guided "low double digits" again and the FY26 revenue guide raised to a point estimate — the repository's own definition of "what a good Q4 guide looks like" (`03_insider_mechanics.md` §5.5).

---

## Files cited

`research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-scenarios.md` · `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` · `research/notes/overnight2/A_calendar-reopening-34-markets.md` · `docs/RNPL_HANDOFF.md` · `outputs/rnpl-audit-20260910/materiality.md` · `docs/q3nowcast/SYNTHESIS.md` · `research/notes/q3nowcast/H_3q26-adr-card.md` · `research/notes/overnight/04_consensus-and-reaction.md` · `research/notes/overnight/09_stock-behaviour-and-alpha.md` · `research/notes/overnight/12_valuation-multiple-regime.md` · `research/notes/overnight/15_red-team.md` · `research/notes/overnight/20_temporal-validation.md` · `research/notes/overnight/14_master-synthesis.md` (§11 binding) · `research/notes/overnight/03_management-language-and-stock.md` · `research/notes/2026-09-10_nights-baseline-reconciliation.md` · `research/notes/2026-09-05_margin-drivers.md` · `research/notes/host_only_fee_history_and_elasticity.md` · `research/notes/2026-09-07_fee-churn-catalyst.md` · `research/notes/catalyst_calendar.md` · `research/notes/2026-09-04_abnb-pitch-catalogue.md` · `research/notes/2026-09-04_abnb-pitch-landscape.md` · `research/notes/2026-09-05_abnb-major-moves.md` · `docs/2026-09-07_research-state-of-play.md` · `docs/competition/citadel_2026_format.md` · `docs/revenue-forecast-strategy/05_backtests/guidance-policy.md` · `docs/revenue-forecast-strategy/05_backtests/B2_Q4_GUIDE_EXHIBIT.md` · `docs/revenue-forecast-strategy/05_backtests/A1_consensus_vintages.md` · `docs/revenue-forecast-strategy/05_backtests/RED_TEAM.md` · `docs/revenue-forecast-strategy/08_THESIS_MAP.html` · `docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` · `docs/revenue-forecast-strategy/02_proposals/M3_guidance_function_and_revision_game.md` · `data/processed/overnight/20_executable_returns.csv` · `20_postrelease_drift.csv` · `23_options_event_estimates.csv` · `04_current_consensus.csv` · `03_reaction_summary.csv` · `05_reaction_by_accel.csv` · `09_earnings_drift_stats.csv` · `02_guidance_ledger.csv`
