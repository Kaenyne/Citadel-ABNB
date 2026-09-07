# Street consensus at every ABNB print, and the reaction function re-run against it

Workstream 04, overnight run 6 Sep 2026. Author: Claude (agent 04).
Scripts: `analysis/src/overnight/04_consensus_at_print.py`, `analysis/src/overnight/04_reaction_vs_consensus.py`
Data: `data/processed/overnight/04_consensus_at_print.csv`, `04_consensus_sources.csv`,
`04_current_consensus.csv`, `04_reaction_panel.csv`, `04_reaction_tests.csv`, `04_q3_2026_breakeven.csv`

---

## Bottom line

1. **The consensus is now reconstructed for all 23 prints.** Revenue consensus 23/23, next-quarter
   revenue consensus 18/23, EPS 17 usable, nights 18, GBV 12, adjusted EBITDA 8. Theo's
   `consensus_snapshots.csv` (23 rows, all "missing") can be filled from
   `04_consensus_at_print.csv`. 145 verbatim source quotes with URLs sit in `04_consensus_sources.csv`.

2. **Beat-vs-consensus on revenue is almost as empty as beat-vs-guide.** ABNB beat the revenue
   consensus at **22 of 23 prints** (the sole miss: 2Q22, -0.28%). So the *event* carries no
   information; only the *magnitude* does, and it is heavily right-skewed by the 2021 reopening
   (max +24.2% in 1Q21, median +2.21%, post-2022 median +1.70%).

3. **Day-1 still has no usable signal, but consensus roughly doubles the in-sample fit.**
   Best single day-1 regressor is **guide midpoint vs next-quarter Street** (n=18, R² 0.116,
   HC1 t = 1.59, p = 0.11) against **beat-vs-guide-midpoint** R² 0.055 — which reproduces the
   driver-model note's 0.04-0.07. Revenue surprise vs consensus gets R² 0.097 (t = 1.51).
   **Every day-1 spec has a negative leave-one-out R²**, i.e. all of them lose to predicting the
   sample mean out of sample. Conclusion is unchanged: do not build a print-day trade.

4. **The one thing that survives LOO is at 20 days, not day 1: nights vs the StreetAccount
   nights consensus.** n = 18, R² 0.220, slope **+1.54 pts of 20-day excess return per 1% nights
   beat**, HC1 t = 2.46 (p = 0.014), permutation p = 0.053, and **LOO R² = +0.13** — the only
   positive out-of-sample R² among 97 tests. Post-2022 (n = 11) it strengthens: R² 0.373,
   slope +2.83, t = 2.83, LOO R² = +0.18. Jackknife-stable (r ranges 0.35-0.57 across
   leave-one-out). The nights *beat* has essentially zero correlation with the **day-1** move
   (r = -0.03) — this is a drift, not a reaction.

5. **"Guide below Street" is the cleanest qualitative rule, but weaker than it first looks.**
   All 8 prints where the guide midpoint sat below the next-quarter consensus produced a negative
   20-day excess return (mean -7.95% vs -2.90% when above). Against a coin flip that is p = 0.004;
   **against ABNB's actual base rate of a negative 20-day excess return (72.7% of all prints) it is
   p = 0.078.** Report the base-rate version. Day-1: 6 of 8 negative, p = 0.12 vs base rate.

6. **For 5 Nov: the Street now sits on the guide midpoint, which is unusual.** Q3-26 consensus
   revenue is **$4.74bn** (Zacks, 7 estimates) versus a guide midpoint of **$4.73bn** — the Street
   is 0.2% *above* the midpoint. On 6 Aug the guide was 2.6% *above* consensus. The revenue bar is
   therefore effectively "any print above $4.74bn", which base rates clear comfortably
   (post-2022 median beat vs guide midpoint +2.15% implies **~$4.83bn**).

---

## Coverage

| Metric | Prints with consensus | Vendor(s) | Gaps |
|---|---|---|---|
| Revenue | **23 / 23** | LSEG (12) / Refinitiv (10), Yahoo unattributed (4Q20); Zacks cross-checks on 4 | none |
| Next-quarter revenue | **18 / 23** | LSEG (11) / Refinitiv (4), StreetAccount (1), CNBC unattributed (2); Zacks post-guide cross-checks on 2 | 4Q20, 1Q21, 2Q21 (no numeric guide existed); **2Q24 (guide quoted, Street number not found)**; 3Q21 direction only |
| EPS (comparable) | 17 / 23 | LSEG (10) / Refinitiv (6), Zacks-derived (1); Zacks and CapIQ cross-checks on 6 | 4Q20, 1Q21, 2Q21 (none quoted); 3Q21, 3Q23, 4Q23 (GAAP one-offs, flagged "not comparable" by CNBC) |
| Nights & experiences/seats | 18 / 23 | StreetAccount (16), FactSet (1), LSEG (1); 1Q23 quoted as "in line" with no number | 3Q22, 2Q24, 2Q26 |
| Gross booking value | 12 / 23 | StreetAccount (9), FactSet (2), unattributed (1) | — |
| Adjusted EBITDA | 8 / 23 | StreetAccount (5), LSEG (1), Yahoo (1), TIKR-derived (1) | — |
| ADR | **0 / 23** | — | No publisher quotes an ADR consensus for ABNB, at any print. |

Every row carries a `confidence` field: 19 `high`, 4 `medium`. The four `medium` rows and why:

- **4Q20** — first post-IPO print. CNBC explicitly refused to compare EPS ("uncertain share counts
  can skew expectations"); Zacks' -$9.18 loss estimate is a pre-IPO share-count artefact. Revenue
  consensus is Yahoo's $739.7m, corroborated by Zacks $735.1m (0.6% apart).
- **4Q21** — the next-quarter (1Q22) consensus of $1.24bn is unattributed in CNBC and implies a
  guide **16.5% above Street**, which is 3x any other observation in the sample. Kept, flagged,
  and it is the single largest `guide_vs_street_pct` outlier; dropping it does not change any
  conclusion.
- **3Q22** — CNBC/Refinitiv say revenue consensus $2.80bn, Zacks implies $2.853bn. The beat is
  either +3.0% or +1.1% depending on vendor. EPS consensus ($1.4229) is derived from the Zacks
  +25.8% surprise, not from LSEG.
- **2Q24** — revenue and EPS consensus are clean LSEG numbers, but the next-quarter (3Q24)
  consensus could not be found in any retrievable source (see "What I could not get").

### Vendor disagreements kept in the file (do not average them away)

| Print | LSEG/Refinitiv | Zacks / other | Effect |
|---|---|---|---|
| 1Q25 EPS | $0.24 (in line) | $0.25 (-4% miss) | flips in-line to a miss |
| 3Q25 EPS | $2.34 (-5.6%) | $2.29 (-3.5%) | halves the miss |
| 2Q26 EPS | $1.25 (+9.6%) | Zacks $1.20 (+14.2%); TIKR/CapIQ $1.25 (+10.0%) | |
| 2Q26 revenue | $3.58bn | TIKR $3.576bn; StockStory $3.579bn | agree to 0.1% |
| 3Q22 revenue | $2.80bn | Zacks $2.853bn | +3.0% vs +1.1% beat |
| 4Q22 next-Q rev | $1.69bn | Zacks $1.90bn | guide above vs below Street — **opposite signs** |
| 4Q24 next-Q rev | $2.30bn (LSEG) | $2.301bn (S&P Global/Visible Alpha via StockStory) | agree to 0.04% |

The last row is the reason the primary series is LSEG/Refinitiv throughout: it is the only vendor
quoted at all 23 prints, and where a second high-quality vendor exists it agrees to within 0.1%.

---

## Results

97 tests were run and are all in `04_reaction_tests.csv` (75 regressions across three horizons
-- 30 univariate, 24 multivariate, 21 post-2022 -- plus 19 sign tests and 3 jackknives). Bonferroni at 0.05 would require p < 0.00053; nothing is close.
Read the LOO column, not the p-values.

### Day-1 excess return (vs QQQ)

| Spec | n | R² | adj R² | HC1 t | perm p | **LOO R²** |
|---|---|---|---|---|---|---|
| guide mid vs next-Q Street (%) | 18 | 0.116 | 0.061 | +1.59 | 0.17 | -0.18 |
| revenue surprise vs consensus (%) | 23 | 0.097 | 0.054 | +1.51 | 0.15 | -0.17 |
| **beat vs guide midpoint (%) — benchmark** | 19 | **0.055** | -0.000 | +1.32 | 0.33 | -0.01 |
| rev surprise + guide-vs-Street | 18 | 0.125 | 0.008 | -0.39 / +1.26 | 0.37 | -0.29 |
| nights surprise vs consensus (%) | 18 | 0.001 | -0.061 | — | 0.89 | -0.08 |
| EPS surprise (bps of pre-print price) | 17 | 0.003 | -0.064 | — | 0.85 | -0.20 |
| adj EBITDA surprise (%) | 8 | 0.063 | -0.093 | — | 0.73 | -0.64 |
| nights acceleration (predictive-study rule) | 21 | 0.032 | -0.019 | -0.92 | 0.45 | -0.18 |
| 20-day run-up into the print | 22 | 0.016 | -0.034 | — | 0.57 | -0.07 |

Consensus surprises beat the guide-based spec in-sample (0.10-0.12 vs 0.055) and lose to it out of
sample. **No day-1 alpha.** That is the third independent confirmation (driver model, predictive
study, this).

Post-2022 subsample (14 prints) is worse still: revenue surprise R² 0.008, beat-vs-guide R² 0.0002,
guide-vs-Street R² 0.063 — all LOO-negative.

### 20-day excess return — where the signal is

| Spec | n | R² | HC1 t | perm p | **LOO R²** |
|---|---|---|---|---|---|
| **nights surprise vs consensus (%)** | **18** | **0.220** | **+2.46** | **0.053** | **+0.133** |
| nights surprise, post-2022 | 11 | 0.373 | +2.83 | 0.048 | +0.178 |
| GBV surprise vs consensus (%) | 12 | 0.205 | +2.52 | 0.14 | -0.125 |
| EPS surprise (%) | 16 | 0.159 | -1.60 | 0.13 | -0.008 |
| EPS surprise (%), post-2022 | 11 | 0.316 | -2.62 | 0.078 | +0.222 |
| revenue surprise + nights surprise | 18 | 0.220 | +2.20 (nights) | 0.17 | +0.034 |
| guide mid vs Street (%) | 17 | 0.006 | — | 0.79 | -0.08 |
| beat vs guide midpoint (%) | 18 | 0.009 | — | 0.71 | -0.06 |

Fitted line (all 18): `excess_20d% = -3.84 + 1.544 x nights_surprise%`.
Post-2022 (11): `excess_20d% = -5.19 + 2.834 x nights_surprise%`, which crosses zero at a
**+1.83% nights beat**. Median nights beat in the sample is only +0.58% — so the *typical*
ABNB print is followed by a negative 20-day excess return, and it takes a large nights beat to
flip it. Worked examples: 4Q25 nights +3.66% -> +10.1% excess; 1Q26 nights +0.28% -> -6.4%;
1Q22 nights +1.22% -> -15.5% (the worst residual, a rate-shock quarter).

**The EPS result has the wrong sign** (post-2022 EPS *beats* precede 20-day *under*performance,
LOO +0.22 on n=11). I do not believe it and I am not carrying it forward; it is reported because
it is one of only two positive-LOO results and a reader who re-runs the file will find it. The
most likely explanation is that ABNB's large EPS beats cluster in quarters with tax/one-off noise
and with high 20-day-forward market beta, not that EPS beats are bad news.

### Sign tests

| Condition | Horizon | n | negative | mean | p vs 0.5 | **p vs ABNB base rate** |
|---|---|---|---|---|---|---|
| guide midpoint **below** Street | 20d | 8 | **8** | -7.95% | 0.004 | **0.078** |
| guide midpoint **below** Street | 1d | 8 | 6 | -2.08% | 0.14 | 0.12 |
| guide midpoint **above** Street | 20d | 10 | 6 | -2.90% | — | — |
| nights **miss** vs consensus | 20d | 6 | 5 | -4.30% | 0.11 | 0.55 |
| revenue **beat** vs consensus | 1d | 22 | 10 | +0.71% | 0.42 | 0.34 |
| nights acceleration positive (predictive study) | 1d | 9 | 2 | +3.21% | 0.090 | 0.070 |

Mann-Whitney, guide-above vs guide-below Street: day-1 p = 0.076, 20-day p = 0.119.
The eight guide-below-Street prints: 3Q21, 3Q22, 1Q23, 3Q23, 1Q24, 3Q24, 4Q24, 1Q25.

The predictive study's nights-acceleration day-1 sign rule survives contact with the consensus
data (7 of 9 positive-acceleration prints had a positive day-1 excess, mean +3.2%, p = 0.07 vs
base rate) but adds nothing in a regression (R² 0.032, t = -0.92 — the linear slope even has the
wrong sign, so treat it strictly as a sign rule, not a magnitude rule).

---

## Reaction-function implications

- **Replace "did they beat the guide" with two variables:** (i) *nights vs StreetAccount* for the
  20-day drift, (ii) *guide midpoint vs next-quarter Street* as a binary risk flag. Revenue
  surprise vs consensus adds nothing once nights is in (its coefficient turns negative and
  insignificant in `rev+nights`).
- **Do not size a day-1 trade off any of this.** Nine day-1 specs, best LOO R² -0.01, all negative.
- The market appears to price ABNB's revenue print immediately (revenue beats are universal and
  therefore already discounted) and to price the *nights* number slowly. That is consistent with
  the driver-model view that nights is the volume variable investors actually re-forecast off,
  while revenue is mostly a guided, take-rate-mechanical number.
- **Caveat that matters:** the nights-drift result rests on 18 observations, uses a StreetAccount
  consensus that is quoted only when CNBC chose to quote it (a selection channel I cannot rule
  out), and comes from a file with 97 tests. Treat it as a hypothesis to carry into the 5 Nov and
  Feb prints, not as an established effect. Two consecutive out-of-sample confirmations would
  make it pitchable.

---

## Current Street numbers (as of 3-4 Sep 2026)

Full detail with quotes and URLs in `04_current_consensus.csv`.

| Period | Metric | Consensus | # est. | Low - High | Source (date) |
|---|---|---|---|---|---|
| Q3 2026 | Revenue | **$4.74bn** (+15.8% y/y) | 7 | 4.72 - 4.77 | Zacks Detailed Estimates (4 Sep 26) |
| Q3 2026 | Adj. EPS | **$2.87** (+29.9% y/y) | 11 | 2.52 - 3.28 | Zacks (4 Sep 26) |
| Q3 2026 | Adj. EBITDA | **not published** | — | — | — |
| Q3 2026 | Nights | **not published** | — | — | — |
| Q4 2026 | Revenue | $3.20bn | 10 | 3.05 - 3.70 | Zacks (4 Sep 26) |
| Q4 2026 | Adj. EPS | $0.82 | 10 | 0.67 - 0.96 | Zacks (4 Sep 26) |
| FY2026 | Revenue | $14.10bn / **$14.16bn** | 8 / 43 | 13.96-14.21 / 13.8-14.3 | Zacks / S&P Global via stockanalysis (3 Sep 26) |
| FY2026 | Adj. EPS | $5.23 / **$5.28** | 13 / 43 | 4.85-5.74 / 5.00-5.91 | Zacks / S&P Global |
| FY2026 | FCF | $5.35bn | — | — | S&P Global (3 Sep 26) |
| FY2026 | Operating income | $3.16bn | — | — | S&P Global (3 Sep 26) |
| FY2027 | Revenue | $15.73bn / **$15.76bn** | 13 | 14.99-16.29 | Zacks / S&P Global |
| FY2027 | Adj. EPS | $6.02 / **$6.14** | 13 | 5.35-6.80 | Zacks / S&P Global |
| NTM | Price target | **$178.96** (-1.6% vs $181.94) | 46 | 125 - 220 | S&P Global/TipRanks (3 Sep 26) |

Positioning colour: consensus rating "Buy"; ratings mix 21 Strong Buy / 4 Buy / 18 Hold /
1 Sell / 2 Strong Sell (46 total, Aug-26), i.e. **46% of the tape (21 of 46) is Hold-or-worse and the average
price target is below the last close.** Zacks Rank 3 (Hold), Earnings ESP +0.45% (Most Accurate
$2.88 vs consensus $2.87). Q3-26 EPS estimate momentum is strongly positive: $2.62 ninety days ago
-> $2.64 at 30 days -> $2.87 now, 9 revisions up / 0 down in 30 days. Expected report date 5 Nov 26.

**No adjusted-EBITDA or nights consensus for Q3 2026 is published anywhere retrievable.** That is a
real gap for the 5 Nov card and the reason the derived bars below are labelled derived.

---

## For the 5 Nov card

`data/processed/overnight/04_q3_2026_breakeven.csv` holds these with their arithmetic.

| Line | Number | How it was derived |
|---|---|---|
| Revenue bar (beat) | **> $4,740m** | Zacks consensus, 7 estimates |
| ... vs guide midpoint $4,730m | consensus is **+0.21% above the midpoint** | first time in the sample the Street sits above the midpoint by this little after an above-Street guide |
| ... vs guide high $4,770m | consensus is 0.63% **below** the high | a print at the guide high is a +0.6% beat only |
| Base-rate revenue print | **~$4.83bn** | post-2022 median beat vs guide midpoint +2.15% |
| Base-rate revenue print (consensus basis) | **~$4.82bn** | post-2022 median beat vs consensus +1.70% |
| Adj. EBITDA bar (**derived, not sourced**) | **$2.3-2.4bn** | Q3-25 margin 50.1% held flat on $4.74bn -> $2,374m; the FY ">=35.5%" guide is an annual figure and is not the Q3 bar |
| Nights bar (**derived, not sourced**) | **~144-146m** | Q3-25 actual 133.6m; StreetAccount has sat a median 0.58% below the actual, and +9-10% y/y is the run-rate |
| Adj. EPS bar | **> $2.87** | 11 estimates, 2.52-3.28; Most Accurate $2.88 |
| Q4-26 guide bar | **$3.20bn** | but the range is 3.05-3.70, a 21% high-low spread — by far the widest in the table. The Street has not converged on the post-hotel-mix Q4 seasonal, so a Q4 guide anywhere in $3.1-3.3bn can be spun either way |

**How to read the print on the day:**

1. Revenue above $4.74bn is the base case and carries no information. Ignore it.
2. **The tradeable number is nights.** If nights beat the (unpublished) StreetAccount figure by
   more than ~1.8%, the 20-day drift has historically been positive; below that it has been
   negative. Get the buy-side whisper on nights before the print — it is worth more than the
   revenue consensus.
3. **Watch the Q4-26 guide midpoint against $3.20bn.** All eight prints where the guide came in
   below Street produced a negative 20-day excess return (base-rate-adjusted p = 0.078).
4. ABNB has missed adjusted EPS in three of the last four quarters (3Q25 -3.5%, 4Q25 -15.2%,
   1Q26 -16.1%, then 2Q26 +14.2% on the Zacks panel). The Street has since marked Q3 EPS up 8.7%
   in 30 days ($2.64 -> $2.87) on the back of that one beat. That is an asymmetric setup on the EPS line even
   though EPS misses have not moved the stock much (5 misses, mean day-1 excess -3.5%, p = 0.46).
5. Positioning into the print: last close $181.94 vs an average target of $178.96, with 46% of
   ratings at Hold or worse. The stock is 20% above its pre-print level ($151.64 close on 6 Aug -> $178.07 on
   the reaction day -> $181.94 on 4 Sep), so the run-up variable is at the high end of its range
   (though run-up has no measurable predictive value: R² 0.016).

---

## For the model

Parameters and series this workstream supplies:

| Name | Value / series | Unit | Source |
|---|---|---|---|
| `cons_revenue_musd` | 23-print series | $m | `04_consensus_at_print.csv` (LSEG/Refinitiv primary) |
| `revenue_surprise_pct` | 23-print series, median +2.21 (post-2022 +1.70) | % | derived |
| `nights_surprise_pct` | 18-print series, median +0.58 | % | derived, StreetAccount primary |
| `guide_vs_street_pct` | 18-print series, 11 above / 7 below | % | derived |
| Drift coefficient (all) | `excess_20d% = -3.84 + 1.544 x nights_surprise%` | pts | `04_reaction_tests.csv` |
| Drift coefficient (post-2022) | `excess_20d% = -5.19 + 2.834 x nights_surprise%`, zero at +1.83% | pts | `04_reaction_tests.csv` |
| Q3-26 Street revenue | 4,740 | $m | Zacks, 4 Sep 26 |
| Q3-26 Street adj EPS | 2.87 | $ | Zacks, 4 Sep 26 |
| Q4-26 Street revenue | 3,200 (range 3,050-3,700) | $m | Zacks, 4 Sep 26 |
| FY26 Street revenue | 14,100 (Zacks) / 14,160 (S&P Global) | $m | 3-4 Sep 26 |
| FY26 Street adj EPS | 5.23 / 5.28 | $ | 3-4 Sep 26 |
| FY26 Street FCF | 5,350 | $m | S&P Global, 3 Sep 26 |
| FY27 Street revenue | 15,730 / 15,760 | $m | 3-4 Sep 26 |
| FY27 Street adj EPS | 6.02 / 6.14 | $ | 3-4 Sep 26 |
| Street NTM price target | 178.96 (46 analysts, 125-220) | $ | S&P Global/TipRanks, 3 Sep 26 |

Use the FY26/FY27 lines as the "what is already in the price" anchor for the football field: a
bull case has to differ from $14.16bn / $15.76bn revenue and $5.28 / $6.14 EPS, not from
last-twelve-months actuals.

---

## Corrections to existing work

- `theos-past-research/research/guidance/data/normalized/consensus_snapshots.csv` has 23 rows all
  marked `missing`. 23 revenue, 18 next-quarter revenue, 17 EPS, 18 nights, 12 GBV and 8 adjusted
  EBITDA values are now available in `04_consensus_at_print.csv` and can be merged in on
  `reported_period`. I did not edit his file.
- `data/processed/abnb_reaction_inputs.csv` and the driver-model day-1 regression use
  `beat_vs_mid_pct` only. That is not wrong, but the note should say the R² 0.04-0.07 is against
  a regressor that is positive at 19/19 prints; the consensus version (positive at 22/23) is
  barely better, which strengthens rather than weakens the driver-model conclusion.
- CNBC's 6 Nov 2025 recap contains a typo, "$2.21 vs. $2.34 cents expected"; the estimate is
  $2.34 per share. Recorded as-is in the sources file with the correction noted.

## What I could not get, and why

- **2Q24 next-quarter (Q3-24) revenue consensus.** CNBC quotes the $3.67-3.73bn guide but no Street
  number. The session's WebSearch budget (200 calls) was exhausted by earlier workstreams;
  DuckDuckGo returned bot challenges and Reuters is not fetchable from this environment. This is
  the single next-quarter gap and it removes one observation (2Q24, day-1 excess -12.3%) from the
  guide-vs-Street tests. Left blank rather than guessed.
- **EPS consensus for 4Q20, 1Q21, 2Q21.** Not published in comparable form; CNBC declined for 4Q20.
- **ADR consensus at any print.** No publisher quotes one. If the team wants an ADR surprise
  variable it will have to come from a licensed estimate feed (Visible Alpha, Consensus Metrix),
  not from the press.
- **Q3-2026 adjusted EBITDA and nights consensus.** Not published in any free source. The bars in
  the 5 Nov table are derived from margin and y/y arithmetic and are labelled as such.
- **Options-implied move at each print.** Only one preview (Benzinga/Options AI, May 2021) was
  retrievable and it does not state ABNB's own implied move. `data/processed/abnb_options_ledger.csv`
  from an earlier branch is the better place to look for this.

## What to build next

1. Merge these 23 rows into Theo's `consensus_snapshots.csv` so the guidance dataset stops
   reporting "missing".
2. Get a **nights** whisper for Q3-26 before 5 Nov. It is the only variable in this study with
   out-of-sample power and there is currently no published consensus for it.
3. Re-run `04_reaction_vs_consensus.py` after the 5 Nov print. One clean out-of-sample
   confirmation of the nights-drift coefficient would move it from hypothesis to pitchable;
   one clean failure kills it.
4. If anyone gets a licensed estimate feed, back-fill the 2Q24 next-quarter consensus, the six
   missing EPS rows, and a full adjusted-EBITDA consensus series — the EBITDA test currently
   runs on n = 8 and is worthless.
