# Independent research audit — batch A18 (B14, B15, B16)

Auditor: Claude Opus 5 (1M), standing in for Codex `gpt-6-astra`, whose usage limit is exhausted. Read-only except for this
file and `A18.done`. Audit date **2026-09-17**.

**B14 — submitted probability: 0.08, interval 0.04–0.14.**
Defensible as written: yes on the number, no on the arithmetic that produced it — the log sits below three of its own routes.
First fix: the analog route the log calls its base rate is 0.077 for the landfall leg **alone**; add the log's own 0.02 citation leg and it is **0.095**, not 0.08, and §7's "analogs weighted fully → 0.04" implies a landfall leg of 0.02 that appears nowhere.
Next fix: the Kalshi anchor is not thin — `volume_fp` is **12,117.55** contracts with 266 traded in 24h and a 1,219-contract bid; the log read the wrong field and discounted a real market.
Independent comparison: **0.09** (0.05–0.15); immaterial either way, and the log's central claim — 0 of 23 letters and 0 of 23 calls — is **true**, which is rare in this run.

**B15 — submitted probability: 0.10, interval 0.05–0.18.**
Defensible as written: **no.** The distribution it is built on was withdrawn on disk before this audit began.
First fix: R11 on disk is **revision 2** (its A12 response), and its `r11_v2_joint_object.json` names B15 in `must_adopt`: **P(≤ +1.0) = 0.232**, not 0.10. B15's anchor ("R11 centre +3.5, sd 1.7, P(≤1) 0.07") and its coherence line ("P(≥4) unchanged at 0.38") are both withdrawn numbers.
Next fix: claim 4's "6 of 13 ≤ +1" is the hand-typed `r11_model.py:36` list that R11 revision 2 explicitly withdraws; and §9 mis-applies the margin coefficient as a dollar rate — the exact error A12-02 corrected in R11 a few hours earlier.
Independent comparison: **0.23** (0.15–0.34); stock −$2.0, **EV −$0.46/share** — still immaterial, but the EV doubles.

**B16 — submitted probability: 0.87, interval 0.75–0.95.**
Defensible as written: the number is right and the data work behind it is the best in the batch; the published derivation is not the one that gets there.
First fix: §6's "0.70 + 0.30 × 0.6 = 0.88" silently swaps **0.6** for the model's own P(leg A | not B) = **0.7163**; at the number the log actually holds, the same identity gives **0.915**. The haircut is defensible — it is just not written down as a judgement.
Next fix: claim 3's "no Q4 adoption in any year" is **false for Q4 2023** (Balogh, 29 Nov 2023, 525,688 shares, in the FY2023 10-K Item 9B — and in the log's own plan table), and the path it cites, `data/raw/filings/abnb_10k_FY2023-2025.htm`, does not exist.
Independent comparison: **0.89** (0.79–0.96); EV −$0.45 on the level, **−$0.06 on the surprise**, which is the number the memo should use.

## Scope and verification

Read-only review of revision 1 of all three logs, against R11 revision 2 and `audits/A12-audit-response.md` as they stood on disk
at 2026-09-17. `py -3.13` (pandas) recomputed every base rate below from repository files; no network was used, so every external
claim was checked against the saved `sources/` snapshots. No prohibited directory was opened. I wrote only this file and `A18.done`.

**B14's HURDAT2 work reproduces exactly and then some.** Re-parsing `sources/hurdat2-1851-2025.txt` independently gives every
figure in claim 3 to the digit: Cat 3+ (`L`, HU, ≥96 kt) landfalls in FL/TX/NC/SC on or after 17 Sep in **8 of 60** seasons
1966–2025 (0.133), **6 of 35** 1991–2025 (0.171), **5 of 26** 2000–2025 (0.192), **4/60** after 1 Oct, **1/60** after 15 Oct
(Wilma), **0/175** after 1 Nov, **15/60** any month; the eight window years are 1967 Beulah, 1989 Hugo, 1995 Opal, 2004 Jeanne,
2005 Wilma, 2018 Michael, 2022 Ian, 2024 Helene/Milton. Claim 4's El Niño analog count is **0 of 11** exactly (1965 Betsy 8 Sep
and 2023 Idalia 30 Aug both fall before the window; no other analog year has any qualifying landfall in any month). The state
boxes, which the log's own RESUME flags as untested, are **clean**: a wide sweep of every Cat 3+ `L` record in 23–40°N / 74–98°W
since 1950 returns, beyond the 14 records the script keeps, only Bahamas points (Jeanne 25 Sep 2004 at 26.7N 77.3W, Joaquin 2015,
Matthew's Grand Bahama landfall 7 Oct 2016 at 26.7N 79.0W), Louisiana (Zeta 2020), and **Rita 2005** at 29.7N 93.7W on the
Texas–Louisiana line — whose season already counts through Wilma, so no rate changes. Nothing is missing and nothing is
double-counted.

**Two conditioners the log does not use both point its way.** No season 1966–2025 reached 17 September with **zero** hurricanes
(the latest first hurricane on record is 11 Sep, in 2002 and 2013), so claim 5's "passed the satellite-era record" verifies from
HURDAT2 itself. And the **15 lowest ACE-through-16-September seasons** of the satellite era (1968, 1972, 1973, 1977, 1982, 1983,
1984, 1986, 1987, 1991, 1992, 1994, 2002, 2013, 2015) produced **0** qualifying window landfalls — a better-powered version of the
El Niño test (P(0 | the 11/76 unconditional rate) = 0.096, against 0.179 for the 11-year analog set). The union of the two
conditioners is 0 of 20, Laplace 0.045.

**B16's EDGAR pull reproduces to the dollar.** 563 Form 4/4A XMLs are on disk; the parse yields **1,122** code-S sales across 418
accessions worth **$4,487M** — Gebbia $3,060M (**68.2%** of the record), Chesky $754M, Blecharczyk $465M, Balogh $106M, Mertz $30M,
Jordan $24M, Stephenson $23M, Bernstein $15M. The 1,219 rolling 137-day windows give P(≥$150M) **0.9500** all-filer (median $334M)
and **0.3979** ex-Gebbia (median $120M); the three same-calendar windows are **$464.4M / $292.0M / $242.2M** and ex-Gebbia
**$310.0M / $112.1M / $61.5M**. Every plan figure in claims 4 and 5 verifies against `sales_by_owner_and_plan.csv`: Gebbia's
27 Feb 2026 plan sold **3,450,000 of 3,450,000** (exhausted), Chesky's 26 Feb 2026 plan **1,260,000 of 1,785,000**, Blecharczyk's
28 Aug 2025 plan **1,627,685 of 2,224,176**; Chesky's Feb-2025 plan 24,500 of 649,000 and Aug-2025 plan 60,000 of 690,000; the
Dec–Jan pairs are Gebbia **$144.8M / $38.1M** and Chesky **$21.1M / $7.9M**. The 2026 monthly tape (Jan $16.3M … Jul $399.1M,
Aug $222.6M, Sep $3.3M, YTD $995.4M) and the 16 Sep price $167.51 all check out. Claim 3's plan table matches the saved 10-Q
Item 5 extracts line for line, with one exception (A18-13).

**R11's revision-2 mixture reproduces.** 0.90 × N(2.795, 2.111) + 0.10 × N(0.8, 1.8) gives P(≤1) **0.2322**, P(≥4) **0.2594**,
P(1 < x < 4) **0.5083**, P(≤0) **0.1163**, mean **2.5955**, sd **2.1663**, E[x | ≤1] **−0.253**, E[x | ≥4] **+5.305** — the joint
object file to four decimals, and the three buckets sum to 1.0000. B15's own published mixture is internally consistent too
(P(≤1) 0.0956, P(≥4) 0.3868, matching its claim 9), and R11 revision 1's normal N(3.517, 1.676) gives P(≤1) **0.0666** — it is the
distribution, not the arithmetic, that has been withdrawn.

Arithmetic checks: B14's Polymarket scaling (0.055 × 1.8 × 0.65 = **0.0644**) and its EV (0.08 × −0.2 = **−0.016**) reproduce;
B14's own nights derivation gives **0.058pt**, booked conservatively at 0.1. B15's EV (0.10 × −2.5 = −0.25) reproduces given its
inputs; three of its five §9 rows do not (A18-03). B16's Monte Carlo summary reproduces from `b16_summary.json` (leg A 0.780205,
leg A | not B 0.7163, P(Yes) 0.91527) and §6's stated identity does not (A18-10). All three binaries clear the
extreme-probability gate (0.08 > 0.05; 0.87 < 0.95).

Paths below are relative to `docs/pitch-forecasts/questions/`; **B14**, **B15**, **B16** and **R11** name their folders, and
`log`, `forecast` mean `research-log.md` and `forecasts/2026-09-17-forecast.json`.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix |
|---|---|---|---|---|---|---|
| A18-01 | B15 | critical | `log:3,32`(claim 1), `log:27`(conventions), `log:74,78,79`; `forecast.final.p`, `.estimates.anchor_source`, `.estimates.joint_distribution_with_R11` | B15's entire distribution is one R11 withdrew. The log's anchor is "R11 (17 Sep, **rev 1**): centre +3.5, sd 1.7, P(≥4) 0.38, P(≤1) 0.07", and its stated convention is that B15 and R11 are "one object". R11 on disk is **revision 2**, whose own §6 says "B15's revision-1 mixture 0.90 N(3.7,1.6)+0.10 N(0.8,1.8) with P(≤1) = 0.10 … **withdrawn**". The two published numbers are not one object: 0.10 + 0.52 + 0.38 = 1.00 only against a distribution that no longer exists. | Read `R11/forecasts/2026-09-17-forecast.json` (`"revision": 2`, p 0.26) and `R11/datasets/r11_v2_joint_object.json`, whose `must_adopt` list names B15 by slug and batch: **"P(≤ +1.0) = 0.232 (revision 1: 0.10)"**. `audits/A12-audit-response.md` is on disk (33 KB, 12:05). Recomputed the adopted mixture from its parameters: P(≤1) **0.2322**, P(≥4) **0.2594**, middle **0.5083**, sum 1.0000. | Republish B15 at **0.232** (rounded **0.23**), interval 0.15–0.34, reading the joint object rather than restating R11's parameters. Delete the parallel mixture in `forecast.estimates.joint_distribution_with_R11` and point at the file, so the next revision of one question cannot silently orphan the other. |
| A18-02 | B15 | critical | claim 4; `forecast.estimates.inputs.base_rate_le1_2023Q2_2026Q2`, `.base_rate_le1_2024_2025` | The base-rate route quotes a **withdrawn** series as measured fact: "post-recovery quarterly US RevPAR y/y (2023Q2–2026Q2, 13 quarters …): 3, 1.5, 2, 1, 1, 2, 3, 0, −0.5, −1, 0, 3.8, 5.2; share ≤ +1: 6/13 = 0.46; within 2024–2025 alone 6/8 = 0.75". R11 revision 2 claim 6 records that this list is the hand-entered `r11_model.py:36` array, "not a series, not sourced", and withdraws it. Brief rule 1's discipline on withdrawn numbers applies inside the run, not only to the kill list. | Read `R11/datasets/r11_v2_quarterly_base_rate.csv`, whose last row is literally `rev-1 hand list (r11_model.py:36) | 1 of 13 >=4; 6 of 13 <=1 | WITHDRAWN (A12-03)`. The replacement is measured from 28 monthly observations parsed out of 58 saved Lodging Magazine reprints: **≤ +1.0 in 4 of 9** quarters 2023Q3–2026Q2 (Laplace 0.455), **3 of 6** on fully-snapshotted quarters (0.50). | Replace claim 4 with the measured rows and cite `r11_v2_quarterly_base_rate.csv`. The route barely moves (0.46 → 0.455) — which is the point: the number survives, the provenance does not, and a judge who pulls the thread finds a withdrawn array. |
| A18-03 | B15 | major | `log:121,122,123`; `forecast.impact.margin_fy26_pp`, `.margin_fy27_pp`, `.eps_fy27_usd` | Three of the five computed §9 rows are wrong, all in the same direction, and one repeats the error A12-02 had just corrected in R11. (i) FY26 margin "−0.05 (0.59 × $36M / $12.9bn × the Q4 weight)" applies a Q4 weight to a figure that is **already** Q4-only. (ii) FY27 margin "−0.10 (0.66 × 0.4pt / **about 2.7**)" divides by an undefined 2.7. (iii) FY27 EPS "−0.04 ($60M × **0.66** × $0.0014)" applies the pp-per-point margin coefficient **and** the dollar EPS rate — two coefficients where the brief gives one. | Recomputed on the line build (`docs/margin-build/SYNTHESIS.md`, FY26 14,268 / 5,098; FY27 15,829 / 5,483) at the held convention, on the corrected revenue deltas of A18-04: FY26 margin **−0.134pp**, FY27 margin **−0.224pp**, FY27 EPS **−$0.076** held / **−$0.048** flex. R11's own §9, written the same day, states the rule: "0.66 is pp-of-margin per point of revenue and must not be applied a second time as a dollar rate". | Rebuild §9 as R11's mirror, with the flow-through convention named in the JSON as R11 does. The corrected rows are 2–3× the published ones and the immaterial verdict still survives, which is the useful result. |
| A18-04 | B15 | major | `log:112,117,118,119,120,124`; `forecast.impact` | The conditional delta and every row below it are computed off the withdrawn distribution, and the stock row double-books narrative. The log conditions on "E[RevPAR given ≤1] about −0.2% vs the base-case +3.4% = **−3.6pp**"; on the adopted distribution it is **−0.253 vs +2.595 = −2.85pp**. The stock line is "−$1.0 fixed-multiple nights plus about **−$1.5** for the corroboration", where R11's mirror books **−$1.0** of narrative, and where the fixed-multiple arithmetic does not give $1.0 either. | Recomputed the whole mirror on R11's own stated rules (slope 0.4, halved; ADR 0.4pt per 2.71pp; 60% persistence into FY27; $158M per FY27 point): nights **−0.57pt**, ADR **−0.42pt**, 4Q26 revenue **−$30M**, FY27 revenue **−$54M**; FY27-nights stock line **−$0.51** fixed-multiple / **−$1.67** joint-solve. | Publish nights −0.6, ADR −0.4, 4Q26 −$30M, FY27 −$54M, stock **−$2.0** (the symmetric mirror of R11's +$2.0), and state the narrative dollar separately from the fundamental one. **EV = 0.232 × −$2.0 = −$0.46/share** — still under the $1 bar, but nearly double what is published. |
| A18-05 | B14 | major | claim 8; `log:81,82`; `forecast.estimates.anchor_source` ("thin") | The only market on the question is dismissed on a parser error, and the error pushes the number the wrong way. Claim 8 reports "volume field null (thin)" for KXHURCTOTMAJ-26DEC01-T0 and the anchor is then discounted as "itself a computation on a thin Kalshi market". This is the same wrong-field read as A01-04. | Read the saved record: `volume_fp` **12,117.55**, `volume_24h_fp` **266.48**, `open_interest_fp` **6,528.36**, `yes_bid_size_fp` **1,219.00** against `yes_ask_size_fp` 26.10, spread 0.32/0.36. The sister strikes are deeper still (T1 volume 21,268, T2 volume 40,740). The quoted prices (bid 0.32, ask 0.36, last 0.33) all verify. | Correct the volume statement and say what the market is: a ladder with ~$34k of notional traded in 24 hours and a four-cent spread, whose rules (`rules_primary`) resolve on **NHC records of >0 Cat 3+ Atlantic hurricanes between 1 Jan and 1 Dec 2026** — which, with zero majors to date, is exactly P(≥1 major forms in the remaining window). That is a cleaner anchor than the log claims, and it is a reason to keep 0.34 rather than shade it. |
| A18-06 | B14 | major | claim 10; `log:80` (decomposition); `log:95` (§7 row 2) | The conditional that carries the whole landfall leg is a rough count the log itself asks to be redone: "about three quarters of seasons had one, giving P(qualifying landfall given ≥1 late-season MH) of about **0.23**". It is then haircut by an unquantified "hostile-regime" adjustment from 0.078 to 0.065, so neither the input nor the output is the measured quantity. | Rebuilt it directly from HURDAT2 first-96-kt dates, as the RESUME asks: seasons with a major first reaching 96 kt on or after 17 Sep number 35/60 (1966–2025), 45/76 (1950–2025), 26/35 (1991–2025); of those, the share with a qualifying Cat 3+ FL/TX/NC/SC window landfall is **6/35 = 0.171**, **9/45 = 0.200**, **6/26 = 0.231**. On a per-storm basis it is **7/65 = 0.108**, 10/83 = 0.120, 7/53 = 0.132, and such seasons average **1.84–2.04** late majors each. | Publish **0.20** as the season-conditional and **0.12** as the per-late-major rate, and drop the undocumented haircut. The two corrections nearly cancel: 0.34 × 0.20 = **0.068**, and integrating the per-major rate over Kalshi's own count ladder (P(N=1) 0.195, P(N=2) 0.115, P(N≥3) 0.03) gives **0.059**. Leg L is **0.06**, essentially where the log has it — but measured rather than asserted. |
| A18-07 | B14 | major | `log:79` (base_rate_estimate 0.08); `log:96` (§7 "El Niño analogs weighted fully → 0.04") | The published number sits **below** the log's own analog route, and the sensitivity row that is supposed to show the analog case sits below it again. §5 builds 0.08 as "regime-conditioned by the El Niño analogs (0/11, Laplace 1/13 = 0.077) … plus about 0.015 for the citation leg" — but 0.077 is the **landfall leg alone**, so the analog-conditioned total is 0.077 + 0.02 = **0.095**. §7 then says weighting the analogs fully moves the number to **0.04**, which requires a landfall leg of ~0.02, a quarter of the analog rate. | Arithmetic against the log's own stated inputs, and the analog count re-derived from HURDAT2 (0 of 11, Laplace 0.0769). | State the analog route as **0.095** and either justify the haircut to 0.065 or drop it. §7's row should read "analogs weighted fully: **0.10**" (the direction is up, not down), or be deleted. This is the single largest reason my number is 0.09 rather than 0.08. |
| A18-08 | B14 | major | `log:80` (citation leg 0.02); `log:73` (§4 row 3); claim 1 | The citation leg is priced off the 0/23 record and never prices the one route the record actually contains. The 4Q25 call carries an analyst asking "how Reserve Now, Pay Later cancellations have been pacing … **in the face of weather disruptions in the 1Q**"; Mertz answered on RNPL only. That is the exact question form that, asked again after a Q4 disaster on a decelerating print, produces the Mertz template ("yes, cancellations were elevated, but …") — which under the log's own convention 3 ("'reducing' includes 'elevated cancellations'") resolves **Yes**. | Verbatim from `data/raw/transcripts/web/4Q25.html`. The A15 audit established the same template as load-bearing on B04 (`overnight2/D/rnpl_statement_ledger.csv` D006). The log's own pre-mortem names the incentive ("management, guiding a deceleration on 5 Nov or in Feb, named a disaster") and then leaves the leg at 0.02. | Raise leg C to **0.03**: P(a disaster with plausible Airbnb salience in a 105-day window, given no qualifying landfall) ~0.55 × P(management attributes a nights or GBV reduction to it by the Feb print) ~0.06. The conditional stays low precisely because the one time the question was asked, management declined to attribute — that negative observation belongs in the log, on the record, not as an unexplained 0.02. |
| A18-09 | B14 | major | `log:128`; `forecast.impact.stock_usd_per_share` | The stock row uses the wrong coefficient for the event it prices. "−0.1pt × $1.50" is the brief's **FY27-nights** fixed-multiple rate, applied to a one-quarter nights delta whose own table books **FY27 revenue 0** and **FY27 EPS 0.00** two rows above. A $3M one-off revenue event is a rounding error in a multiple-based valuation, not $0.20/share. | Read `00_BRIEF.md` §Sensitivities ("1pt of FY27 nights ≈ $4.90/share (joint solve) or $1.50 (fixed multiple)") against `log:124,126,127`. | Book **−$0.02 to −$0.05/share** and say it is the present value of one quarter's $3M, or book $0.00 and keep the narrative point. EV falls from −$0.02 to about **−$0.005**. The verdict does not change; the row is the kind a judge reads aloud. |
| A18-10 | B16 | major | `log:84` (§6); `forecast.estimates.legs` | The published derivation is arithmetic on a number the log does not hold. §6: "P(Yes) = P(B) + P(not B) × P(A given not B) = **0.70 + 0.30 × 0.6** = 0.88, rounded to 0.87". Claim 8 and the model give P(A | not B) = **0.7163**; substituting it into the same identity gives **0.9149**, which is the Monte Carlo's 0.915. The 0.6 appears nowhere else in the log. | `b16_summary.json`: `p_legA_given_no_new_ceo_plan` 0.7162757, `p_yes` 0.91527. Recomputed both identities. | Either write the haircut as the judgement §5 describes — "not-B is informative: the two founders adopt on one cadence, so P(A | not B) is nearer 0.55–0.60 than the model's 0.716, because the model treats the two adoptions as independent" — or publish 0.91. Do not present a judgement as arithmetic. My own number uses the first route and lands at 0.89. |
| A18-11 | B16 | major | `log:75,76,79,84`; claim 8; `forecast.estimates.legs.sales_ge_150m` | Leg A is published at three different values in one document — Monte Carlo **0.78** (claim 8 and `b16_summary.json`), §6 "about **0.75**", JSON `legs` **0.75** — and leg B at two: §5's base-rate line uses "a CEO plan in 5 of the last 6 half-year slots, **Laplace 0.75**" while the model and §6 use **0.70**. | Read the four fields against `b16_summary.json` (`p_legA_sales_ge150` 0.780205, `p_legB_new_ceo_plan` 0.70). | Pick one number per leg and carry it into the JSON. If the intent is that 0.78 is the model and 0.75 the judgement, label them. |
| A18-12 | B16 | major | claim 2; `forecast.estimates.anchor_source` ("n 1,219") | The anchor's sample size is overstated by two orders of magnitude. 1,219 daily-start windows of 137 days overlap almost entirely; the effective independent sample is **~9**. The anchor 0.95 and the ex-Gebbia 0.40 are then quoted to two decimals, and the gap between the anchor and the final is explained as a story about Gebbia rather than as sampling noise on a handful of observations. | Reproduced the windows (n 1,219, P(all) 0.9500, P(ex-Gebbia) 0.3979) and computed n_eff = 1,219 / 137 ≈ 8.9. The honest non-overlapping sample is the three same-calendar windows the log already gives: all-filer **3 of 3** (Laplace 0.80), ex-Gebbia **1 of 3** (Laplace 0.40). | Report the overlapping rate with n_eff beside it, and promote the three-window sample to the anchor. A second fact belongs with it, and it is the strongest single number in the log: **Gebbia alone** sold $154.5M, $179.8M and $180.7M in the three prior 17 Sep–31 Jan windows — i.e. in every prior window the dominant seller cleared the threshold by himself, which is exactly why his exhausted plan is the question. |
| A18-13 | B16 | major | claim 3; its source path | Two defects in one load-bearing row. (i) "no Q4 adoption in any year (10-K Item 9B: none in Q4 2023, 2024, 2025)" is **false for Q4 2023**: the FY2023 10-K Item 9B discloses Ari Balogh adopting on **11/29/2023** (525,688 shares). The log's own `sales_by_owner_and_plan.csv` carries that plan ("November 29, 2023", 443,978 shares, $71.1M). (ii) The cited path `data/raw/filings/abnb_10k_FY2023-2025.htm` **does not exist**; the repo holds `abnb_10k_FY2023.htm`, `…FY2024.htm`, `…FY2025.htm`. | Parsed Item 9B out of all three 10-Ks: FY2023 carries an adoption table; FY2024 and FY2025 both read "none of our officers or directors adopted, modified or terminated". `Path.exists()` on the cited file returns False. | Rewrite as "no **CEO** Q4 adoption in 2023–2025; one officer (Balogh) adopted in Q4 2023", cite the three files, and keep convention 2's conclusion — it rests on the CEO-specific record, which survives. |
| A18-14 | B16 | minor | `log:75,91`; §7 row 1 | Leg B's reference class is the wrong one. What leg B needs is a **Q3** adoption (only a Q3 plan reaches a 10-Q inside the window); the log reasons from "half-year slots". On the Q3 slot the record is Chesky **2 of 3** — adopted 22 Aug 2024 and 25 Aug 2025, not in 3Q23 — i.e. Laplace 0.60, or **2 of 2** since the Feb/Aug rhythm began (Laplace 0.75). | Parsed the ten saved 10-Q Item 5 tables: 2Q23 Chesky adopt, 3Q23 none (Stephenson only), 1Q24, 3Q24, 1Q25, 3Q25, 1Q26 Chesky adopt; 2Q25 and 2Q26 none. | Say which class 0.70 comes from. One fact belongs in it and is absent: in August 2025 Chesky adopted a new plan while **96%** of his Feb-2025 plan (624,500 of 649,000 shares) was still unsold — the same configuration he faces now with 525,000 unsold. That is the strongest evidence for leg B and it argues for the top of the 0.60–0.75 bracket. |
| A18-15 | B16 | minor | `log:80` (decomposition); `b16_model.py` | The model has no new-**Blecharczyk**-plan route. He adopts roughly annually (30 May 2023, 31 May 2024, 28 Aug 2025), his current plan expires 20 Nov 2026, and his last plan sold **$265M**. A Q3-2026 adoption selling after a ~90-day cooling-off is a live December–January route worth a few points of leg A; it appears in neither the Monte Carlo nor §7. | Read `b16_model.py`'s branch list against `sales_by_owner_and_plan.csv`. The model prices only "others lognormal median $10M" beyond the two founders. | Add the branch at P ≈ 0.45 with a Dec–Jan median near $40M, or say in §4 why it is excluded. It is the only omission I found that pushes the number up. |
| A18-16 | B16 | minor | convention 1 (`log:28`) | Convention 1 excludes codes F, G, C, M/A and J. Excluding them is right — F is a disposition to the issuer for tax withholding, not a sale — but the convention is load-bearing and its size is never stated, so a reader cannot see how much the resolution rule decides. | Summed the excluded codes: code **F** is $193.0M across 78 transactions, and **$67.1M / $77.4M / $1.9M** in the three same-calendar windows; code G covers 12.1m shares including Gebbia's 24 Aug 2026 gift of 960,000. | One sentence: "on a looser reading that counted tax-withholding dispositions, the 2024–25 ex-Gebbia window would rise from $112M to $190M". Then the convention is visibly doing work, which is what a pre-registered convention is for. |
| A18-17 | B16 | minor | `log:124`; `forecast.impact.eps_fy27_usd` note | "buybacks absorb about 6m shares a quarter against about **1.5m** of insider sales" understates the insider side by a third. | `data/processed/abnb_capital_return_quarterly.csv` 2Q26 buybacks **$1,051M** ≈ 6.3m shares at $167 ✓. Code-S sales are **33.56m shares** over 16 quarters = **2.10m per quarter**, and 6.62m in 2026 to 16 Sep (≈2.2m per quarter). | Use 2.1m. The point — buybacks absorb about three times the insider supply — is unchanged and is the right point. |
| A18-18 | B16 | minor | `log:126,127`; `forecast.impact.ev_stock_usd_per_share` | The EV is a level EV on an event the log itself calls the base case. A 0.87-probability routine 10-Q disclosure is already in the price; the memo trades the surprise. The same objection A15-14 raised on B05 applies here with more force, because the operating content is exactly zero. | Surprise EV = (1 − 0.87) × −$0.5 = **−$0.065**. Level EV 0.87 × −0.5 = −0.435 ✓ as booked. | Report both, and lead with the surprise. Then the §9 conclusion — "one sentence of colour at most" — is supported by a number rather than asserted. |
| A18-19 | B14 | minor | claim 3 / `log:75` (§4 row 5) | "after 17 Sep the record is Florida-dominated (**10 of 14 events** since 1950)" counts HURDAT2 landfall **records**, not storms. | Ian alone contributes three `L` records (24.6N 82.9W, 26.8N 82.0W, 26.7N 82.2W). On distinct storms the window record since 1950 is **12** storms — 8 Florida (King, Opal, Jeanne, Wilma, Michael, Ian, Helene, Milton), 3 South Carolina (Hazel, Gracie, Hugo), 1 Texas (Beulah) — i.e. **8 of 12**. | Say "records" or use 8 of 12. The Florida-dominance conclusion is unaffected. |
| A18-20 | B14 | minor | convention 1 vs claim 3 | The base rate is computed on HURDAT2 **best track** (post-season re-analysis) while the question is pre-registered to resolve on the **operational advisory at landfall**. These differ at exactly the margin the question turns on: Ian was carried operationally as Cat 4 at Cayo Costa and re-analysed to Cat 5; the convention's own examples (Ian, Michael count; Florence, Matthew do not) are best-track judgements. | Compared convention 1 (`log:28`) with the data source named in claim 3. | One line naming the basis mismatch and its sign (operational estimates at landfall are, if anything, less likely to be called Cat 3 than the re-analysis, so the best-track base rate is a mild upper bound on the operational one). It is worth under a point; it is the sort of thing an auditor asks first. |
| A18-21 | B15 | minor | conventions 1 (`log:27`), shared with R11 | The resolution object and the modelling object are not the same function of the three months. Convention 1 resolves on "the **mean** of the October, November and December y/y figures", while the FY-implied leg is built on a RevPAR-**weighted** quarterly identity. December carries the lowest RevPAR of the three, so a simple mean over-weights it relative to the quarter. | Read convention 1 against R11 claim 12's FY identity and its quarter shares. Recomputed the FY-implied leg at several weightings: equal weights give **+2.97**, an approximate RevPAR weighting **+2.61**, against the published +2.69. | The convention is pre-registered and the fallback ("STR's own Q4 figure governs where both exist") is right; name the basis and note the ~0.3pp wedge between the two readings. |
| A18-22 | B15 | minor | claim 9 (trend centre); inherited from R11 claim 12 | The leg that sets the centre swings more on an unobserved assumption than on everything the log argues about. The FY-implied 4Q26 is computed from CoStar/TE's FY26 +4.4% net of measured Q1/Q2 and an **assumed** Q3 of +5.0–6.0. | Recomputed on an approximate RevPAR weighting: Q3 +5.0 → 4Q26 **+3.18**; +5.5 → **+2.61**; +6.0 → **+2.04**; +6.5 → **+1.46**. That 1.7pp range dwarfs the election-week (−0.4), CR (−0.2) and comp (+0.2) adjustments the two logs spend their §7 on. | Put the Q3 grid at the top of §7 in both questions, and carry R11's own correct caveat — that a strong September is evidence the stale FY figure will be **raised**, not that Q4 must be weak. |
| A18-23 | B15 | minor | claim 1 ("P(≤1) 0.07") | Even before the withdrawal, the quoted anchor was the rounded one: R11 revision 1's exact normal **N(3.517, 1.676)** gives P(≤1) **0.0666**; 0.07 comes from reading (3.5, 1.7) off the prose. | Recomputed both. | Moot after A18-01; noted because 0.07 is the number §5 calls `anchor_estimate` and `final_minus_anchor` is computed from it. |
| A18-24 | B14, B15 | minor | both §9 / cross-question | The two questions are positively correlated and neither says so: the modal B14 Yes is a Cat 3+ Florida landfall in October, which is a US-hotel-RevPAR event — R11's own claim 8 cites "hurricane-market comps" in the October 2025 base, and CoStar's monthly releases in the saved set include one titled "holidays and **natural disasters** impact U.S. hotel performance". | Read B14 §9 against R11 claim 8 and the `lodging_monthly/` filenames. | One line in each, and a note for X01 not to treat them as independent. The correlation is small (a single-state landfall is worth perhaps 0.3pp of a quarterly US RevPAR figure, and it cuts both ways through displacement demand) but it is free to state. |
| A18-25 | B14, B15, B16 | minor | each `sources/web_search_log_2026-09-17.md` | The final-recency claims (B14 claim 13, B15 claim 12, B16 claim 11) are stated as facts about the world but rest on WebSearch notes with no saved result payloads — the gap flagged as A11-24 and A15-25, now in its third batch. | Inventoried all three `sources/` directories. B14 is a partial exception (the NHC outlook, TCR and GTWO pages and the CSU PDF are saved and load-bearing; the NOAA August outlook 403'd and is recorded as such). B15's three saved trade-press pages support "nothing newer than 11 Sep". **B16 is the model and should be the standard**: its primary source is saved in full — 563 Form 4 XMLs and the EDGAR submissions JSON — so every number in the log is re-derivable offline without trusting a snippet. | Write "no relevant result in the searches recorded" rather than "nothing new", and keep doing what B16 did. |

## B14 — what the log does well and should keep

**The central empirical claim is true, and it is checkable in ten seconds.** Across all 23 shareholder letters and all 23 call
mirrors — and, it turns out, the five conference mirrors too — management has never attributed a reduction in nights or GBV to a
hurricane or any natural disaster. A regex sweep for hurricane / wildfire / natural disaster / earthquake / typhoon / storm /
weather / flood / fire returns hits in four letters and six transcripts, and every one of them is something else: Airbnb.org
relief (4Q20 founding; 3Q24 "Since the start of Hurricanes Helene and Milton, approximately 800 hosts in Florida, North Carolina,
South Carolina and Georgia have generously offered … more than 6,000 people"; the 4Q24 letter and call on the LA fires, "housed
more than 19,000 people … along with over 2,300 pets"), an analyst's phrase (4Q25), or an idiom ("planning for a storm", "throw
fuel on the fire", "quick-fire round"). Two facts strengthen it further and are not in the log: the **1Q25** letter and call —
the quarter of the Los Angeles fires — contain no instance of "fire", "Los Angeles" or "disaster" at all; and
`data/processed/abnb_big_moves_7pct.csv` records **0** weather-driven moves in 41 rows ≥7%. After A15 found the analogous
"management has never" claim on B04 to be false, this one being right matters.

**The HURDAT2 pipeline is the cleanest dataset in the batch.** It is 44 lines of stdlib, it runs in under two seconds, it writes
both its intermediate and its summary table, and every figure in claim 3 reproduces from an independent re-parse. The state boxes,
which the log flags as unverified, survive a wide-box audit: the only Cat 3+ landfall record in the window they exclude that a
reader might argue about is **Rita 2005** at the Texas–Louisiana line, and 2005 already counts through Wilma. The El Niño analog
count is exact. The RESUME asks precisely the three questions an auditor would ask, in the right order.

**The resolution conventions are doing real work and were written before the modelling.** Ruling that a Cat 3 storm weakening to
Cat 2 before landfall resolves No, that Louisiana/Mississippi/Alabama/Georgia do not count, that the operational advisory governs
because the best track will not exist by 31 December, and that an **Airbnb.org relief paragraph is not a citation of a reduction**
are four decisions the question genuinely needs. The last one is the load-bearing one, and it is right.

**The materiality conclusion is correct and should go into the memo as written**: even the modal Yes carries almost no operating
content, and — as with B06 — a named external cause is *worse for the short than for the long*, because it converts "deceleration"
into "one-off". Listing B14 as a monitoring line rather than a bonus item is the right call.

## B15 — what the log does well and should keep

**The decision to make B15 and R11 one object is the right architecture**, and it is stated in the conventions before any
modelling: "identical to R11's so the two questions are one object … Coherence: P(≤1) + P(1 < x < 4) + P(≥4) = 1". The failure
here is not the design, it is that the design was not re-read after R11 moved. A15 found the same pattern on B04 (a stale C07
analogue); this is that pattern with a 13-point consequence.

**The left-tail mechanisms are dated, specific and actionable**, and they are what a symmetric normal cannot carry: the CR expiry
on **11 December 2026** with the 2025 shutdown's measured cost (~1.5m room-nights, ~0.4% of a month's demand) as the yardstick;
the 16 September hike with three more priced; TSA throughput −3.7% y/y as fares ration air travel; the midterm week of 3 November
against a 2025 comp that printed **+6.2%** off the 2024 election week. Each has a date on the monitoring calendar and a stated
move. That is the best-built §8 in the batch.

**Claim 8 is the right way to ask the question** and should survive into the memo verbatim: a ≤ +1% quarter requires the Q4 level
back at 2024 in nominal terms while ADR runs +2–3%, i.e. occupancy −1 to −2 against a base whose October occupancy was already
−2.4% — "a demand contraction of the 2025 kind, not a mere fade of the summer premium". Setting out what the tail *requires*,
rather than only how far it is in standard deviations, is the discipline the rest of §5 lacks.

**Claim 10 is honest about the readthrough and should be kept**, including the part that cuts against the log's own §9: hotel
RevPAR and Airbnb nights correlate at r 0.88 post-2022 but have decoupled since 2024, so "the hotel line is corroboration for the
memo, not an input to the KPI". The §9 nights row then books a −0.7pt delta from it anyway; the sentence is right and the row
should be built to match it, not the other way round.

## B16 — what the log does well and should keep

**The EDGAR work is the best primary-source effort in the run so far.** 563 Form 4/4A XMLs pulled, saved, and parsed into three
intermediate tables, with the puller kept in `datasets/` so the whole thing re-derives offline. Every headline reproduces to the
dollar: 1,122 code-S sales worth $4,487M; Gebbia 68.2% of the record; the three same-calendar windows $464M / $292M / $242M and
$310M / $112M / $61.5M ex-Gebbia; the 2026 monthly tape; the per-plan execution table. Nothing in this run should be audited
without a source set this good behind it.

**The question's real structure is identified correctly, and it is not the obvious one.** The unconditional window rate is 0.95
and would be an easy number to publish; §4 discards it for the right reason — the seller who produced two thirds of the record
has an **exhausted** plan (3,450,000 of 3,450,000 sold by 28 July 2026), and ex-Gebbia the same window has run $310M → $112M →
$61.5M, monotonically down. Finding that the anchor is 0.95 and then explaining in one line why the question is really about two
partially-executed plans and two unobserved adoptions is exactly the work the flow is for.

**The plan-level forensics are precise where precision matters.** Chesky's remaining 525,000 shares to 25 November and
Blecharczyk's 596,491 to 20 November are computed from plan authorisations net of footnote-matched executions, not estimated; the
execution-fraction priors are argued against the record (Chesky's Feb-2025 plan sold 24,500 of 649,000 at $115–135, his Feb-2026
plan 1,260,000 at $133–178, so the branch is price-state-dependent rather than a fixed rate); and the cooling-off timing is taken
from observed first-sale dates (28 November – 12 December 2025 under the August 2025 plans), not from the rule book.

**§4 disposes of the two traps cleanly**: Gebbia's 24 August 2026 gift of 960,000 shares is code G to an indirect holding and is
not a sale, and a Q4-2026 adoption would surface only in the 10-K on ~12 February, outside the window. Both are the kind of thing
a careless resolver gets wrong.

## Independent numbers

These are audit judgements built from the same repository inputs, not blinded second forecasts. No tradable market exists on B15
or B16; B14's Kalshi ladder is the only market in the batch and I used the saved snapshot rather than refreshing it.

**B14: P(Yes) = 0.09.** Judgmental 80% interval **0.05–0.15**.
*Leg L = 0.06.* Two routes agree. Integrating the measured per-late-major qualifying-landfall rate (0.12, from 7 of 65 late majors
1966–2025) over Kalshi's own count ladder (P(N=0) 0.66, N=1 0.195, N=2 0.115, N≥3 0.03) gives **0.059**; the season-conditional
route, Kalshi mid 0.34 × the measured conditional 0.200, gives **0.068**. Both are consistent with the regime evidence — 0 of 11
El Niño analogs, 0 of 15 lowest-ACE seasons, and a 2026 that has no satellite-era precedent (no season 1966–2025 reached 17
September with zero hurricanes) — and with climatology as the ceiling (8 of 60 = 0.133).
*Leg C = 0.03.* P(a disaster with plausible Airbnb salience in the window, given no qualifying landfall) ~0.55 × P(a nights or GBV
reduction attributed to it by the Feb print) ~0.06. The conditional is low because the record is 0 of 23 letters and 0 of 23 calls
across Ian, Helene, Milton and the LA fires, and because the one time an analyst asked the question directly (4Q25) management
declined to attribute; it is not lower because the 1Q26 "approximately 100bps" conflict citation shows this management will size
an external shock when a decelerating guide needs one.
Union = 0.06 + 0.94 × 0.03 = **0.091**.
*Impact and EV.* 4Q26 nights **−0.06pt** (the log's own derivation; −0.1 as published is a conservative round-up), ADR 0, 4Q26
revenue **−$3M**, FY27 revenue **$0M**, FY26 margin **−0.01pp** held, FY27 margin 0, FY27 EPS **$0.00**, stock **−$0.03/share**
(the present value of one quarter's $3M; the published −$0.20 misapplies the FY27-nights coefficient). **EV = 0.09 × −$0.03 ≈
−$0.003/share**, or **−$0.018** on the published coefficient. Immaterial by two orders of magnitude; drop it from the memo and
keep the 1 November line on the monitoring calendar, when leg L dies mechanically (0 of 175 seasons since 1851).

**B15: P(Yes) = 0.23.** Judgmental 80% interval **0.15–0.34**.
Adopt R11 revision 2's joint object exactly — **P(≤ +1.0) = 0.2323** on 0.90 × N(2.795, 2.111) + 0.10 × N(0.8, 1.8) — so that the
two questions remain one distribution, which is B15's own stated convention and R11's `must_adopt` instruction. My independent
centre differs by 0.1pp (I would take the election-week drag at −0.5 rather than −0.4: the midterm week of 3 November 2026 faces
both its own depression and a 2025 comp that printed +6.2% off the 2024 election week), which moves the tail to **0.238** — inside
the rounding, and not worth breaking coherence for. The route: FY-implied 4Q26 **+2.69** (CoStar/TE FY26 +4.4% net of measured Q1
+3.53 and Q2 +5.60 and an assumed Q3 +5.0–6.0; I reproduce +2.61 on my own RevPAR weighting), the two-start AR leg **+3.87**,
averaged to +3.28, +0.2 measured comp credit, −0.5 election, −0.2 CR → centre **+2.78**; against the measured base rate of
**4 of 9** quarters ≤ +1 (Laplace 0.455) at 0.2 weight.
*Impact and EV, rebuilt on the adopted distribution.* Conditional delta **−2.85pp** (E[x | ≤1] −0.25 vs mean +2.60). 4Q26 nights
**−0.6pt**, ADR **−0.4pt**, 4Q26 revenue **−$30M**, FY27 revenue **−$54M**, FY26 margin **−0.13pp** held (−0.09 flex), FY27 margin
**−0.22pp** held (−0.14 flex), FY27 EPS **−$0.08** held (−$0.05 flex; the coefficient applied **once**, as $0.0014 per $M of
EBITDA), stock **−$2.0** (−$0.51 fixed-multiple or −$1.67 joint-solve on 0.34pt of FY27 nights, plus ~−$1.0 for the corroboration
a rolling-over hotel tape gives the deceleration narrative, mirroring R11's +$1.0). **EV = 0.232 × −$2.0 = −$0.46/share** —
immaterial, but 1.8× what is published, and the pair (R11 +$0.5, B15 −$0.46) is now symmetric.

**B16: P(Yes) = 0.89.** Judgmental 80% interval **0.79–0.96**.
*Leg B = 0.73.* Leg B needs a **Q3-2026** adoption, because only a Q3 plan reaches a 10-Q (≈5–6 November) inside the window; a Q4
adoption surfaces in the 10-K on ~12 February, outside it. Chesky's Q3-slot record is 2 of 3 (none in 3Q23, adopt 22 Aug 2024 and
25 Aug 2025) — Laplace 0.60 — or 2 of 2 since the February/August rhythm began, Laplace 0.75. The tie-breaker is mechanical: both
August adoptions came about three months before a February plan expired, with the old plan still running and, in 2025, **96%
unsold** — which is precisely the configuration today (525,000 of 1,785,000 unsold, expiry 25 November 2026).
*Leg A | not B = 0.58.* Not-B is informative: the two founders adopt on one cadence, so a missing Chesky plan makes a missing
Gebbia plan more likely, and the model's 0.716 treats them as independent. On that branch leg A leans on Blecharczyk's remaining
596,491 shares (~$100M) and Chesky's 525,000 (~$88M) — expected execution ~$126M against a $150M bar — plus a residual Gebbia
probability. Offsetting, the model omits a **new Blecharczyk plan** (annual cadence, current plan expiring 20 November, last plan
sold $265M), worth a few points.
P(Yes) = 0.73 + 0.27 × 0.58 = **0.887**. The two published anchors bracket it: the unconditional window rate 0.95 (on an effective
n of ~9, and driven by a seller whose plan is exhausted) and the Monte Carlo's 0.915 (which the log is right to shade, for a
reason it should state rather than bury in a substituted digit).
*Impact and EV.* Every operating row is **0** and should stay 0 — insider sales touch no line of the model, and $4.5bn of them
since 2022 produced 0 of the 41 moves ≥7%. Stock **−$0.5/share** is a judgement overlay, not a repo sensitivity, and should be
labelled as one. **EV = 0.89 × −$0.5 = −$0.45/share on the level, and (1 − 0.89) × −$0.5 = −$0.06 on the surprise** — the surprise
number is the honest one for a routine disclosure that is already the base case. Immaterial on either reading; the memo's one
sentence of colour is the right treatment, and the genuine signal the log names — a founder plan adopted **after** 5 November with
an unusual size or a price floor — belongs on the monitoring calendar, not in the number.

## Reproduction script

Read-only, stdlib plus pandas, no numpy or scipy, no network, no file writes. Run from the repository root with
`python -B docs/pitch-forecasts/audits/A18-reproduce.py`. It re-parses HURDAT2 from scratch, recomputes every base rate, conditional
and window rate asserted above, re-reads the Kalshi and Polymarket snapshots, re-greps the 23 letters and 28 transcript mirrors,
rebuilds both impact tables, and prints the saved-versus-recomputed comparison for each.

```python
"""A18 read-only reproduction (B14 bonus-weather-event, B15 bonus-q4-us-revpar-soft, B16 bonus-insider-selling).
Run from the repository root: python -B docs/pitch-forecasts/audits/A18-reproduce.py
Requires stdlib + pandas only (no numpy/scipy). Writes nothing; no network.
"""
from pathlib import Path
from statistics import NormalDist
import collections
import json
import math
import re

import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
N = NormalDist()


def head(t):
    print("\n" + "=" * 12 + " " + t + " " + "=" * 12)


# ------------------------------------------------------------------ B14
head("B14 HURDAT2: parse, state boxes, window base rates")

TXT = Q / "bonus-weather-event/sources/hurdat2-1851-2025.txt"
storms, cur = [], None
for ln in TXT.read_text().splitlines():
    p = [x.strip() for x in ln.split(",")]
    if p[0].startswith("AL"):
        cur = {"id": p[0], "name": p[1], "rows": []}
        storms.append(cur)
    else:
        cur["rows"].append(p)


def ll(r):
    lat = float(r[4][:-1]) * (1 if r[4][-1] == "N" else -1)
    lon = float(r[5][:-1]) * (-1 if r[5][-1] == "W" else 1)
    return lat, lon


def region(lat, lon):
    if -97.9 <= lon <= -93.8 and 25.8 <= lat <= 30.2:
        return "TX"
    if -87.6 <= lon <= -79.8 and 24.4 <= lat <= 31.0:
        return "FL"
    if -81.1 <= lon <= -78.4 and 32.0 <= lat <= 33.95:
        return "SC"
    if -78.6 <= lon <= -75.3 and 33.8 <= lat <= 36.6:
        return "NC"
    return None


hits = collections.defaultdict(list)
wide = []
firsthu, late96 = {}, collections.defaultdict(list)
for s in storms:
    y = int(s["id"][4:])
    first96 = None
    for r in s["rows"]:
        if r[3] == "HU":
            if y not in firsthu or r[0] < firsthu[y]:
                firsthu[y] = r[0]
        if r[3] == "HU" and int(r[6]) >= 96 and first96 is None:
            first96 = r[0]
        if r[2] == "L" and r[3] == "HU" and int(r[6]) >= 96:
            lat, lon = ll(r)
            if -98 <= lon <= -74 and 23 <= lat <= 40:
                wide.append((y, r[0], s["name"], int(r[6]), lat, lon))
            reg = region(lat, lon)
            if reg:
                hits[y].append((r[0], s["name"], reg, int(r[6])))
    if first96 and first96[4:] >= "0917":
        late96[y].append(s["name"])

win = {y for y in hits if any(d[4:] >= "0917" for d, _, _, _ in hits[y])}
for start in (1851, 1950, 1966, 1991, 2000):
    n = 2025 - start + 1
    row = {}
    for cut, lab in (("0917", ">=17Sep"), ("1001", ">=1Oct"), ("1015", ">=15Oct"), ("1101", ">=1Nov")):
        row[lab] = sum(1 for y in range(start, 2026)
                       if any(d[4:] >= cut for d, _, _, _ in hits.get(y, [])))
    row["any"] = sum(1 for y in range(start, 2026) if hits.get(y))
    print("  %d-2025 (n %d):" % (start, n), {k: "%d/%d = %.3f" % (v, n, v / n) for k, v in row.items()})
print("  claim 3 asserts 8/60, 6/35, 5/26 in-window; 4/60 after 1 Oct; 1/60 after 15 Oct; 0/175 after 1 Nov; 15/60 any month")

w = [(y, d, nm, rg) for y in hits for d, nm, rg, _ in hits[y] if y >= 1950 and d[4:] >= "0917"]
storms_w = sorted({(nm, rg) for _, _, nm, rg in w})
print("  in-window since 1950: records", len(w), "| distinct storms", len(storms_w))
print("   FL records", sum(1 for x in w if x[3] == "FL"), "| FL storms", sum(1 for x in storms_w if x[1] == "FL"),
      "<- the log's '10 of 14 events' counts RECORDS; on storms it is 8 of 12 (A18-19)")
print("  wide-box in-window Cat3+ records the tight state boxes drop:")
for e in sorted(wide):
    if e[0] >= 1950 and e[1][4:] >= "0917" and not any(x[0] == e[0] and x[1] == e[1] for x in w):
        print("    ", e)
print("  RITA 2005 (29.7N 93.7W, TX/LA line) is excluded by the TX box; 2005 already counts via WILMA, so no count changes")

head("B14 regime conditioners")
print("  latest first-hurricane dates 1966-2025:",
      sorted(((v[4:], k) for k, v in firsthu.items() if k >= 1966), reverse=True)[:4])
print("  seasons 1966-2025 with NO hurricane by 17 Sep:",
      [y for y in range(1966, 2026) if firsthu.get(y, "99991231")[4:] > "0917"], "<- 2026 is unprecedented")


def ace(y, cut="0916"):
    tot = 0.0
    for s in storms:
        if int(s["id"][4:]) != y:
            continue
        for r in s["rows"]:
            if r[1] in ("0000", "0600", "1200", "1800") and r[3] in ("HU", "TS") and r[0][4:] <= cut:
                if int(r[6]) >= 34:
                    tot += int(r[6]) ** 2 / 1e4
    return tot


rows = sorted((ace(y), y) for y in range(1966, 2026))
low15 = [y for _, y in rows[:15]]
print("  lowest-15 ACE-through-16-Sep seasons:", sorted(low15))
print("   qualifying window landfalls among them:", [y for y in low15 if y in win],
      "-> 0/15, Laplace 1/17 = %.3f" % (1 / 17))
en = [1957, 1963, 1965, 1972, 1982, 1987, 1994, 1997, 2002, 2015, 2023]
print("  El Nino analogs (claim 4):", [y for y in en if y in win], "-> 0/11, Laplace 1/13 = %.3f" % (1 / 13),
      "| any-month hits:", [y for y in en if y in hits])
print("  union of the two conditioners: 0/%d, Laplace %.3f"
      % (len(set(en) | set(low15)), 1 / (len(set(en) | set(low15)) + 2)))
print("  power check: P(0 hits in 11 yrs | 11/76) = %.3f ; in 15 yrs = %.3f"
      % ((1 - 11 / 76) ** 11, (1 - 11 / 76) ** 15))

head("B14 conditional landfall rate (claim 10 asserts 0.23; the log's RESUME asks for this)")
for a, b in ((1950, 2025), (1966, 2025), (1991, 2025)):
    L = [y for y in range(a, b + 1) if late96.get(y)]
    h = [y for y in L if y in win]
    nmaj = sum(len(late96[y]) for y in L)
    nhit = 0
    for s in storms:
        y = int(s["id"][4:])
        if not (a <= y <= b):
            continue
        f96, qual = None, False
        for r in s["rows"]:
            if r[3] == "HU" and int(r[6]) >= 96 and f96 is None:
                f96 = r[0]
            if (r[2] == "L" and r[3] == "HU" and int(r[6]) >= 96
                    and r[0][4:] >= "0917" and region(*ll(r))):
                qual = True
        if f96 and f96[4:] >= "0917" and qual:
            nhit += 1
    print("  %d-%d: seasons with a major first reaching 96kt >=17 Sep %d/%d; qualifying %d/%d = %.3f; "
          "per-late-major %d/%d = %.3f; mean late majors per such season %.2f"
          % (a, b, len(L), b - a + 1, len(h), len(L), len(h) / len(L), nhit, nmaj, nhit / nmaj, nmaj / len(L)))
pk = {0: 0.66, 1: 0.195, 2: 0.115, 3: 0.03}
print("  auditor leg L, per-major 0.12 integrated over the Kalshi count ladder: %.4f"
      % sum(p * (1 - 0.88 ** n) for n, p in pk.items()))
print("  auditor leg L, season-conditional 0.34 x 0.200: %.4f ; total with leg C 0.03: %.4f"
      % (0.34 * 0.20, 0.06 + 0.94 * 0.03))

head("B14 Kalshi and Polymarket snapshots")
k = json.loads((Q / "bonus-weather-event/sources/kalshi_markets_KXHURCTOTMAJ.json").read_text())
for m in k["markets"]:
    if m["ticker"].endswith(("-T0", "-T1", "-T2")):
        print("  ", m["ticker"], "bid", m["yes_bid_dollars"], "ask", m["yes_ask_dollars"],
              "last", m["last_price_dollars"], "| volume_fp", m["volume_fp"],
              "volume_24h_fp", m["volume_24h_fp"], "OI", m["open_interest_fp"],
              "bid_size", m["yes_bid_size_fp"])
print("  -> claim 8's prices verify; its 'volume field null (thin)' does not: volume lives in volume_fp/volume_24h_fp (A18-05)")
pm = json.loads((Q / "bonus-weather-event/sources/polymarket_hurricane_landfall_20260917.json")
                .read_text(encoding="utf-8", errors="replace"))


def walk(o):
    if isinstance(o, dict):
        if "question" in o and not o.get("closed"):
            print("  ", str(o["question"])[:70], o.get("outcomePrices"), "vol24", o.get("volume24hr"))
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(pm)
print("  Polymarket scaling check: 0.055 x 1.8 x 0.65 = %.4f" % (0.055 * 1.8 * 0.65))

head("B14 management-citation record (claim 1)")
pat = re.compile(r"hurricane|wildfire|natural disaster|earthquake|typhoon|\bstorm|\bweather\b|\bflood|\bfires?\b", re.I)


def txt(p):
    s = re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="ignore"))
    return re.sub(r"\s+", " ", s)


for lab, g in (("letters", "data/raw/letters/*.htm"), ("transcripts+confs", "data/raw/transcripts/web/*.html")):
    n = tot = 0
    for p in sorted(ROOT.glob(g)):
        h = pat.findall(txt(p))
        tot += 1
        if h:
            n += 1
            print("   %s %s: %d hits" % (lab, p.stem[:6], len(h)))
    print("  %s: %d of %d files contain any weather/disaster word" % (lab, n, tot))
print("  every hit is Airbnb.org relief (4Q20; 3Q24 Helene/Milton, ~800 hosts / 6,000 people;")
print("  4Q24 letter+call LA fires, '19,000 residents'), an analyst's phrase (4Q25 'weather disruptions in the 1Q',")
print("  answered on RNPL only), or an idiom (3Q22 'planning for a storm', 3Q24 'fuel on the fire', BERN24 'quick-fire round').")
print("  1Q25 - the quarter of the LA fires - contains NO 'fire'/'Los Angeles'/'disaster' string in the letter or the call.")
print("  -> claim 1 (0 of 23 letters, 0 of 23 calls) VERIFIED, and it holds over the 5 conference mirrors too")

head("B14 impact arithmetic")
print("  4Q26 nights: 0.03 x 0.25 x (2/13) x 0.5 = %.3f pt (log books -0.1)"
      % (0.03 * 0.25 * (2 / 13) * 0.5 * 100))
print("  4Q26 revenue: 0.1 x $30M = -$3M; FY26 margin on held costs %.3f pp (log books 0.00)"
      % (((5098 - 3) / (14268 - 3) - 5098 / 14268) * 100))
print("  stock: 0.1pt x $1.50 = $0.15 (booked -0.2); EV 0.08 x -0.2 = %.3f" % (0.08 * -0.2))
print("  NOTE: $1.50/pt is the FY27-NIGHTS coefficient; a one-quarter 0.06pt event has no FY27 content (A18-09)")

# ------------------------------------------------------------------ B15 / R11
head("B15 vs R11: which revision is on disk, and the joint object")
r11 = json.loads((Q / "risk-q4-us-revpar-strong/forecasts/2026-09-17-forecast.json").read_text())
b15 = json.loads((Q / "bonus-q4-us-revpar-soft/forecasts/2026-09-17-forecast.json").read_text())
jo = json.loads((Q / "risk-q4-us-revpar-strong/datasets/r11_v2_joint_object.json").read_text())
print("  R11 on disk: revision", r11["revision"], "p", r11["final"]["p"])
print("  B15 on disk: revision", b15["revision"], "p", b15["final"]["p"])
print("  R11 rev2 joint object must_adopt:")
for x in jo["must_adopt"]:
    print("    -", x)
print("  R11 rev2 superseded:", jo["superseded"])


def mix(x, w=0.9, mu=2.795, sd=2.111, sw=0.1, smu=0.8, ssd=1.8):
    return w * N.cdf((x - mu) / sd) + sw * N.cdf((x - smu) / ssd)


print("  adopted mixture 0.90 N(2.795,2.111) + 0.10 N(0.8,1.8):")
print("    P(<=1) %.4f  P(>=4) %.4f  P(1..4) %.4f  P(<=0) %.4f"
      % (mix(1), 1 - mix(4), mix(4) - mix(1), mix(0)))
print("    mean %.4f  sd %.4f" % (0.9 * 2.795 + 0.1 * 0.8,
      math.sqrt(0.9 * (2.111 ** 2 + 2.795 ** 2) + 0.1 * (1.8 ** 2 + 0.8 ** 2) - (0.9 * 2.795 + 0.1 * 0.8) ** 2)))
print("  B15's published (withdrawn) mixture 0.90 N(3.7,1.6)+0.10 N(0.8,1.8): P(<=1) %.4f  P(>=4) %.4f"
      % (mix(1, mu=3.7, sd=1.6), 1 - mix(4, mu=3.7, sd=1.6)))
print("  R11 rev1 normal N(3.517,1.676): P(<=1) %.4f  P(>=4) %.4f  <- withdrawn on disk (A18-01, A18-23)"
      % (N.cdf((1 - 3.517) / 1.676), 1 - N.cdf((4 - 3.517) / 1.676)))
print("  auditor centre +2.78 (election -0.5): P(<=1) %.4f" % mix(1, mu=2.745))

head("B15 measured quarterly base rate (R11 rev2 claim 6 replaces B15 claim 4)")
br = pd.read_csv(Q / "risk-q4-us-revpar-strong/datasets/r11_v2_quarterly_base_rate.csv")
print(br.to_string(index=False))
print("  measured months parsed:",
      len(pd.read_csv(Q / "risk-q4-us-revpar-strong/datasets/us_revpar_monthly_yoy_measured.csv")))
print("  B15 claim 4's hand list '6 of 13 <= +1' is the withdrawn r11_model.py:36 series (A18-02)")
q1, q2 = 3.533, 5.600
for q3 in (5.0, 5.5, 6.0, 6.5):
    w = (0.22, 0.265, 0.275, 0.24)
    print("  FY-implied 4Q26 at Q3 %.1f (RevPAR-weighted): %.2f" % (q3, (4.4 - w[0] * q1 - w[1] * q2 - w[2] * q3) / w[3]))
print("  -> a 1.7pp swing on an unobserved assumption, larger than every adjustment the logs debate (A18-22)")

head("B15 impact table on the ADOPTED distribution (mirror of R11's own rules)")
d = jo["conditional_means_pct"]["given_le_1"] - jo["parametric"]["mean"]
nights = 0.4 * abs(d) / 2
adr = 0.4 * abs(d) / 2.71
rev4 = -(nights * 30 + adr * 30)
fy27 = -(0.6 * nights * 158)
print("  conditional delta %.2f pp (B15 log uses -3.6 off the withdrawn distribution)" % d)
print("  nights -%.2f pt | ADR -%.2f pt | 4Q26 rev %.0f | FY27 rev %.0f" % (nights, adr, rev4, fy27))
print("  FY26 margin held %.3f pp (log books -0.05) | FY27 margin held %.3f pp (log books -0.10)"
      % (((5098 + rev4) / (14268 + rev4) - 5098 / 14268) * 100,
         ((5483 + fy27) / (15829 + fy27) - 5483 / 15829) * 100))
print("  FY27 EPS held %.3f (log books -0.04 via 0.66 x 0.0014: two coefficients) | flex %.3f"
      % (fy27 * 0.0014, fy27 * 0.0014 * 0.42 / 0.66))
print("  stock: fixed-multiple %.2f, joint-solve %.2f, plus ~-1.0 narrative (R11 mirror)"
      % (-0.6 * nights * 1.50, -0.6 * nights * 4.90))
for p in (0.10, 0.2323):
    print("  EV at P=%.4f on -$2.0/share: %.2f" % (p, p * -2.0))

# ------------------------------------------------------------------ B16
head("B16 Form 4 pull: totals, owners, window base rates")
s = pd.read_csv(Q / "bonus-insider-selling/datasets/form4_sales_codeS.csv")
s["txn_date"] = pd.to_datetime(s.txn_date)
t = pd.read_csv(Q / "bonus-insider-selling/datasets/form4_transactions.csv")
t["txn_date"] = pd.to_datetime(t.txn_date)
print("  code-S rows", len(s), "| accessions", s.accession.nunique(), "| XML files",
      len(list((Q / "bonus-insider-selling/sources/form4_xml").glob("*.xml"))))
print("  total $%.0fM | by owner $M:" % (s.value.sum() / 1e6),
      {k: round(v / 1e6) for k, v in s.groupby("owner").value.sum().sort_values(ascending=False).head(8).items()})
print("  Gebbia share of the record: %.1f%%" % (100 * s[s.owner.str.contains("Gebbia")].value.sum() / s.value.sum()))
print("  all transaction codes:", t.code.value_counts().to_dict())
print("  EXCLUDED code F (tax withholding) totals $%.0fM overall; in the three same-calendar windows:"
      % (t[t.code == "F"].value.sum() / 1e6),
      [round(t[(t.code == "F") & (t.txn_date >= pd.Timestamp("%d-09-17" % y))
              & (t.txn_date <= pd.Timestamp("%d-01-31" % (y + 1)))].value.sum() / 1e6, 1)
       for y in (2023, 2024, 2025)], "<- convention 1 is load-bearing and unsized (A18-16)")

starts = pd.date_range("2023-01-01", "2026-05-03", freq="D")
vals, valsx = [], []
for st in starts:
    en = st + pd.Timedelta(days=136)
    sub = s[(s.txn_date >= st) & (s.txn_date <= en)]
    vals.append(sub.value.sum() / 1e6)
    valsx.append(sub[~sub.owner.str.contains("Gebbia", case=False)].value.sum() / 1e6)
vals, valsx = pd.Series(vals), pd.Series(valsx)
print("  137-day windows n %d (OVERLAPPING; effective independent n ~ %d) (A18-12)"
      % (len(starts), len(starts) // 137))
print("  P(all >= 150) %.4f median %.1f | P(ex-Gebbia >= 150) %.4f median %.1f"
      % ((vals >= 150).mean(), vals.median(), (valsx >= 150).mean(), valsx.median()))
for y in (2023, 2024, 2025):
    m = (s.txn_date >= pd.Timestamp("%d-09-17" % y)) & (s.txn_date <= pd.Timestamp("%d-01-31" % (y + 1)))
    sub = s[m]
    print("   %d-09-17..%d-01-31 all $%.1fM ex-Gebbia $%.1fM | Gebbia alone $%.1fM"
          % (y, y + 1, sub.value.sum() / 1e6,
             sub[~sub.owner.str.contains("Gebbia", case=False)].value.sum() / 1e6,
             sub[sub.owner.str.contains("Gebbia", case=False)].value.sum() / 1e6))
print("  -> non-overlapping sample = 3 windows: all-filer 3/3, ex-Gebbia 1/3; Gebbia ALONE cleared $150M in all three")

head("B16 plans: execution and cadence")
pl = pd.read_csv(Q / "bonus-insider-selling/datasets/sales_by_owner_and_plan.csv")
print(pl[pl.owner.str.contains("Chesky|Gebbia|Blecharczyk")].to_string(index=False))
print("  Gebbia Feb-2026 plan sold %d of the 3,450,000 authorised -> EXHAUSTED"
      % pl[(pl.owner.str.contains("Gebbia")) & (pl.plan == "February 27, 2026")].shares.iloc[0])
print("  Chesky Feb-2026: 1,260,000 of 1,785,000 -> 525,000 remain (expiry 25 Nov 2026)")
print("  Blecharczyk Aug-2025: 1,627,685 of 2,224,176 -> 596,491 remain (expiry 20 Nov 2026)")
print("  monthly 2026 code-S $M:",
      {str(k): round(v / 1e6, 1) for k, v in
       s[s.txn_date >= "2026-01-01"].groupby(s.txn_date.dt.to_period("M")).value.sum().items()})
for y in (2024, 2025):
    m = (s.txn_date >= pd.Timestamp("%d-12-01" % y)) & (s.txn_date <= pd.Timestamp("%d-01-31" % (y + 1)))
    print("  Dec-Jan %d/%d: Gebbia $%.1fM Chesky $%.1fM (claim 5 says $145M/$21M then $38M/$8M)"
          % (y, y + 1, s[m & s.owner.str.contains("Gebbia")].value.sum() / 1e6,
             s[m & s.owner.str.contains("Chesky")].value.sum() / 1e6))

item5 = re.sub(r"[^\x20-\x7e\n]", " ",
               (Q / "bonus-insider-selling/sources/tenq_item5_10b51_tables.txt")
               .read_text(encoding="utf-8", errors="replace"))
print("  10-Q Item 5 snapshots on disk:", re.findall(r"=== (\S+)", item5))
print("  Chesky adoptions by calendar quarter: 2Q23 yes, 3Q23 NO, 1Q24 yes, 3Q24 yes, 1Q25 yes, 3Q25 yes, 1Q26 yes, 2Q26 no")
print("  -> leg B needs a Q3-2026 adoption: Q3-slot record 2 of 3 (Laplace %.2f), 2 of 2 since the Feb/Aug rhythm (Laplace %.2f) (A18-14)"
      % (3 / 5, 3 / 4))
for y in (2023, 2024, 2025):
    p = ROOT / ("data/raw/filings/abnb_10k_FY%d.htm" % y)
    tt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="ignore")))
    i = [m.start() for m in re.finditer(r"Item\s*9B", tt, re.I)][-1]
    ok = "none of our officers" in tt[i:i + 300]
    print("  FY%d Item 9B:" % y, "no Q4 adoption" if ok else "HAS a Q4 adoption (Balogh, 11/29/2023, 525,688 shares)")
print("  -> claim 3's 'no Q4 adoption in any year' is WRONG for Q4 2023 (A18-13); and its cited path exists:",
      (ROOT / "data/raw/filings/abnb_10k_FY2023-2025.htm").exists())

head("B16 leg arithmetic")
sm = json.loads((Q / "bonus-insider-selling/datasets/b16_summary.json").read_text())
print("  model: P(legA) %.4f  P(legB) %.2f  P(legA|not B) %.4f  P(Yes) %.5f"
      % (sm["p_legA_sales_ge150"], sm["p_legB_new_ceo_plan"],
         sm["p_legA_given_no_new_ceo_plan"], sm["p_yes"]))
print("  log section 6 writes 0.70 + 0.30 x 0.6 = %.3f, but the model's P(A|not B) is %.3f, which gives %.4f (A18-10)"
      % (0.70 + 0.30 * 0.6, sm["p_legA_given_no_new_ceo_plan"],
         0.70 + 0.30 * sm["p_legA_given_no_new_ceo_plan"]))
for pB, pA in ((0.70, 0.716), (0.73, 0.58), (0.75, 0.55)):
    print("  P(B)=%.2f P(A|notB)=%.3f -> P(Yes)=%.4f" % (pB, pA, pB + (1 - pB) * pA))
print("  EV: 0.87 x -$0.5 = %.3f ; on the surprise (1-P) x -$0.5 = %.3f (A18-18)" % (0.87 * -0.5, (1 - 0.87) * -0.5))
print("  buyback vs insider supply: 2Q26 buybacks $1,051M ~ 6.3m shares; code-S sales %.2fm shares / 16 quarters = %.2fm per quarter (A18-17)"
      % (s.shares.sum() / 1e6, s.shares.sum() / 1e6 / 16))

head("Cross-question coherence")
print("  R11 rev2 0.2594 + B15 corrected 0.2323 + middle 0.5083 = %.4f" % (0.2594 + 0.2323 + 0.5083))
print("  B15 as published (0.10) with R11 rev2 (0.259): the two tails sum to 0.359 and the middle is left at 0.52 -> not one object")
for slug in ("bonus-weather-event", "bonus-q4-us-revpar-soft", "bonus-insider-selling", "risk-q4-us-revpar-strong"):
    dd = json.loads((Q / slug / "forecasts/2026-09-17-forecast.json").read_text())
    im = dd.get("impact", {})
    print("  %-4s rev %d p %.3f ci %s | stock %.2f EV %.3f material %s"
          % (dd["question_id"], dd["revision"], dd["final"]["p"], dd["final"]["ci"],
             im.get("stock_usd_per_share", 0), im.get("ev_stock_usd_per_share", 0), im.get("material")))
```
