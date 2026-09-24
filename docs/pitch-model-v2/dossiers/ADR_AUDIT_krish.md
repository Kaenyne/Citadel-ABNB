# ADR line — adversarial audit

**22 September 2026.** Auditor: Claude (Opus 5.5), run on Krish's machine against `theo/pitch-model-v2` at
`84c430b7` (detached worktree `citadel-abnb-adraudit`), per `docs/pitch-model-v2/briefs/ADR_AUDIT.md`. Nothing
committed, nothing pushed, nothing under `analysis/src/forecast_methods/`, `data/processed/forecast_methods/`,
`docs/revenue-forecast-strategy/` or `model/` touched. Receipts (every script, log and CSV behind every number
below): `data/processed/pitch_model_v2/receipts/ADR_AUDIT/`. Three parts were delegated to sub-agents and are
receipted separately: C4 (`C4_pooled_reconciliation.md`), C5 (`C5_filing_search.md`) and the document sweep
(`DOC_CONSISTENCY.md`).

---

## 1. Verdict

**No, not as filed.** The binding negative survives a hostile read: no defensible composition route puts 4Q26 ADR
below the Street's $171.33, even after corrections that lower the base by up to $0.50. But four supports do not
survive:

- **The FX point.** The identity is conditionally biased high by about 0.4pp in the configuration 3Q26 is in.
- **The pooled reconciliation's significance.** Its p-value is invalid with four clusters.
- **The pre-registered 3Q26 FX falsifier.** It would withdraw a correct identity 88% of the time.
- **Three document claims:** the core is "40% of ex-FX", the lap-only row "crosses" the Street, and "RNPL was not named in a filing until 2Q26".

Together these take 3Q26's P(print ≥ Street) from 0.645 to between 0.36 and 0.61.

---

## 2. Reproduction

| # | command (from the worktree root) | exit | result |
|---|---|---|---|
| 1 | `PYTHONPATH=analysis/src py -3.13 -m pitch_model_v2.adr_engine.run --no-posterior --no-workbook` | **1** | Fails in `refresh_prices.py:168`: `no listings.csv.gz found under ~/abnb_ia_capture`. The 2026 Inside Airbnb dumps live only on the build machine. The FX stages ran before the failure and reproduced (row 2). |
| 2 | same + `--no-refresh-prices` | **0** | 16.9 s. Every output file reproduces the committed one: max \|diff\| 1.03e-6 on `fx_pit_walkforward.csv` (MAP optimiser), ≤ 1.1e-7 on `fx_scores.csv`, ≤ 2.3e-13 on everything else. The geomix stage's own checks all print "reproduced (<1e-6)". Log: `run_fast_norefresh.log`. |
| 3 | `PYTHONPATH=analysis/src py -3.13 -m pytest analysis/src/pitch_model_v2/adr_engine/tests -q` | **0** | 27 passed in 5.1 s (`pytest.log`). |
| 4 | full run with the PyMC posterior | not run | No Python on this machine has PyMC (`py -3.13` lacks it; the repo venv lacks matplotlib). The posterior (EMEA 1.199, LatAm 0.460 …) is **not reproduced**. As a cross-check I fitted V1 by MAP on all 17 quarters: β = 0.999 / 1.203 / 0.405 / 1.294, consistent with the posterior means. |
| 5 | workbook build | not run | It writes under `model/`, which brief rule 7 forbids. |

Tracked outputs overwritten by runs 1–2 were restored with `git checkout`, so the tree differs from HEAD only by
this file and the receipts. `python3` on this machine is the Windows Store stub, so every command used `py -3.13`
(Python 3.13.14, pandas 2.3.3).

**The brief's table, recomputed** (sweep in `DOC_CONSISTENCY.md`). Every number reproduces: identity max
\|gap\| 0.0422 on 14 quarters; ratios 0.3437 / 0.3027 / 0.3831 / 0.3173; bootstrap uppers 0.4384 / 0.3688 /
0.5091 / 0.4181; FX +0.4153 / +0.5137; ADR 177.681 / 173.034; half-bands 0.9775 / 1.9319; P 0.6447 / 0.7008;
annual mix −1.102 / −1.325 / −1.672 vs −1.083 / −1.244 / −1.584; sub-regional −0.4534 / −0.1517 / −0.1372 /
−0.1468; origin +81.04% vs +39.96%, 13.4% cheaper, −0.354%/yr; size-mix 2025 +0.7395 in [0.4166, 1.2879]; the
whole §6.2 ladder to the cent. Three mismatches:

| claim | document says | output says |
|---|---|---|
| geo-mix method vs H term | "within 0.13pp" (`final_adr.md:307, 551`) | mean \|diff\| **0.134**, max **0.218** (3Q24) |
| V0 bias range | "+0.11 to −0.07" (`final_adr.md:157`) | **+0.15** to −0.07 (the +0.15 is W1 O3) |
| sub-regional 4Q26 in dollars | "−$0.24" (`final_adr.md:346`) | −$0.246; DEC-0038 says "−0.25" |

Both data traps are real, and the shipped code avoids both. A naive `groupby().sum()` on
`origin_lang_rotation_ltm.csv` gives +66.2%. A positional `iloc[-4:]` on `geomix_subregional_term.csv` gives
−0.074. `workbook.py` filters by label first.

---

## 3. Findings, ranked by how far they move 3Q26 or 4Q26 ADR

The sign convention throughout is **help** (the correction lowers ADR, which helps the short) or **hurt** (it
raises ADR or removes a bearish route).

| # | finding | 3Q26 $ | 4Q26 $ | short |
|---|---|---:|---:|---|
| F1 | FX identity conditionally biased high in LatAm-strong quarters (C3) | **−0.66** (−0.74 by error regression) | **−0.39** (−0.58) | help |
| F2 | The ex-FX base mixes three term constructions | −0.09 to **−0.51** | −0.09 to **−0.50** | help |
| F3 | The "AR(1) on core" row uses the residual's constant | (row) | row −0.51 to **−1.23** → $171.15 | help |
| F4 | Bundle band 0.8–1.2 is narrower than its source's rounding | ±0.84 on core | **±0.84** | band |
| F5 | The World Cup is absent from the ADR line | unsized | unsized; break-even below | help (sign) |
| F6 | The "+ sub-regional" row double counts 2Q26's term | +0.17 on the row | **+0.17** on the row | hurt |
| F7 | Mean reversion uses the residual's mean (brief's flag) | −0.22 on the row | **−0.21** on the row | help |
| F8 | The core's own record does not support carrying beyond h = 2 | 0 | 0 | help (FY27 −$2.50) |
| F9 | The seats step inside the 1Q26 core is an assumption | 0 (base) | MR row +0.52 if the step is not real | hurt |
| F10 | EMEA's one validated proxy argues for persistence | 0 | 0 | hurt |
| F11 | The 3Q26 FX falsifier is mis-specified | 0 | 0 | — |
| F12 | Pooled reconciliation: p invalid; slope is mostly Brazil's CPI (C4) | 0 | 0 | — |
| F13 | The 4Q27 FX artefact reaches FY27 unlabelled | 0 | 0 | FY27 ±$1.7–2.0 |

### F1. The identity is biased high in exactly the configuration 3Q26 and 4Q26 are in (C3)

**Claim** (`final_adr.md` §2.6, lines 152–162). The euro-only OLS scores best but is not the leg for three
reasons:

1. It was excluded before the scores existed.
2. It is biased −0.27 to −0.34pp.
3. It is blind to MXN / BRL / AUD, "3Q26 is their quarter". MXN, BRL and AUD contribute +1.08pp of the +0.415pp.

**Evidence against.** Leg 3 cuts harder against the identity than against V2. The identity's own point-in-time
error rises with its own LatAm component in every promotion cell, on both windows (`audit_fx2.log`):

| cell | n | error on X_latam | p | r |
|---|---:|---:|---:|---:|
| W1 O2 | 14 | +0.69 | 0.002 | +0.76 |
| W1 O3 | 14 | +0.59 | 0.002 | +0.74 |
| W2 O2 | 10 | +0.66 | 0.011 | +0.76 |
| W2 O3 | 10 | +0.55 | 0.012 | +0.76 |

In the six quarters where X_latam exceeds 0.5pp (3Q23, 4Q23, 1Q24, 4Q25, 1Q26, 2Q26), the identity
over-predicted **6 of 6 times, mean +0.51pp**. The last three misses at O3, with every rate already observed, are
+0.54, +0.50 and +0.82.

3Q26's largest component is X_latam = **+0.606pp** (EMEA −0.404, APAC +0.194, NA +0.019). That is the quarter
where the identity is least reliable, not most.

Three independent reads of the same weakness agree:

| method | 3Q26 FX | 4Q26 FX | source |
|---|---:|---:|---|
| V1 MAP, fitted on all 17 quarters | +0.03 | +0.28 | `C3_forecast_quarters_by_variant.csv` |
| posterior means (EMEA 1.199, LatAm 0.460, APAC 1.266) | +0.06 | +0.30 | same |
| the W1 O3 error regression | −0.02 | +0.17 | `audit_fx2.log` |

Thesis sentence 3 (`adr_v2_thesis.md:21`) says the posterior explains the misses "without improving it out of
sample". That is false for W2: V1 beats V0 in both W2 promotion cells (0.347 / 0.290 against 0.383 / 0.317).

**The defence, leg by leg.**

- **Leg 1** is procedurally valid for *promotion*: the registered tie-break keeps V0. But it is not "blind", and
  its timing cannot be proven from git:
  - `data/processed/overnight/05_fx_fits.csv` (committed 6 Sep) already ranked the euro fit the best ADR-FX
    object (LOO RMSE 0.507 on n 17).
  - The N1 card (11 Sep) already carried its 3Q26 value of −1.12.
  - The pre-registration first appears in the same commit as its results (`15a1bf02`, author = committer =
    21 Sep 23:39 EDT). That commit already contains §10's line "Filed 2026-09-22 02:10 EDT".
  - Blob `0495e5f3` is not in the object store.
  - What *is* verified: the first 183 lines of the file (§0–§9 plus the §10 heading) hash to
    `0495e5f32a904274cd0cce0c5ffa73f41aa70918`, so the registered text is unedited since that hash was taken.
  - The defensible form of leg 1 is: *the exclusion runs against the short*. V2 is the bearish variant, so no
    pro-short selection happened.
- **Leg 2** holds against promoting V2, for a better reason than the one filed:
  - V2's intercept (−0.567) is 45–46% of its 3Q26 / 4Q26 forecast. The intercept has no translation content: at
    zero currency moves the true effect is zero.
  - A through-origin V2 scores worse (0.274–0.388, bias +0.37 to +0.62).
  - V2's bias is not stable. At O3 it is −0.28 in 2023, −0.20 in 2024, −0.09 in 2025 and **−0.76 in 1H26**
    (`C3_bias_by_episode.csv`).
- **Leg 3** is right that V2 under-predicts in these quarters (mean −0.62 in the same six LatAm-strong
  quarters). V2 adjusted for that still says 3Q26 −0.82 and 4Q26 −0.88.

**Would a two- or three-currency fit beat both?** No (`C3_posthoc_scores.csv`, same PIT protocol, labelled not
promotable). EUR plus the identity's LatAm+APAC component, by OLS, scores 0.300 / 0.313 / 0.330 / 0.345. It beats
V0 only in the two O2 cells, never beats V2, and is biased −0.43 to −0.53. Freezing the posterior weights scores
0.231–0.295, but those weights come from all 17 quarters in hindsight, so that is a ceiling, not a test.

**Size.**

| FX variant | 3Q26 ADR | 4Q26 ADR |
|---|---:|---:|
| V0 identity (filed) | $177.68 | $173.03 |
| V1 MAP | **$177.02** | **$172.65** |
| error regression | $176.94 | $172.46 |
| V2 euro-only (all 17) | $174.87 | **$170.08** |

The Street is $177.06 and $171.33. V1 alone moves P(print ≥ Street) to about 0.49 (3Q26) and 0.66 (4Q26).

**Verdict on C3.** The defence stands against *promoting* V2. V2's route below the Street rests 45% on an
intercept artefact, which **hurts the short**. But the identity's point for 3Q26 carries a documented,
significant conditional error of about +0.4pp, which **helps the short**. The honest 3Q26 FX range is −0.8 to
+0.42, with the pre-registered V1 at +0.03 in the middle. The committed card's −0.43 is inside that range.

### F2. The ex-FX base is built on three different term constructions

**Claim.** The forward ex-FX = the 2Q26 core carried flat plus forward terms "carried exactly as the card carries
them" (`adr_fx_prereg.md` §6).

**Evidence.** The core is 2Q26 ex-FX minus the **H decomposition's** terms (`exfx.py` `history()`). The forward
adds terms from **other constructions** (`audit_basis.log`):

| term | 2Q26 inside the core | same construction as the forward, 2Q26 | offset | forward 3Q26 |
|---|---:|---:|---:|---:|
| geo mix | H −1.267 | bucket arithmetic −1.135 | **+0.132**; positive in all 7 quarters 4Q24–2Q26, mean +0.134 (`geo_mix_method_check.csv`) | bucket −1.293 |
| unit size | H 0.700 | I, identical construction, **0.867** | **+0.166** | I 0.797 |
| LOS | H **0.30, an assumed fill** (`adr_history_components.csv` `term_fill_2026`) | none exists | — | I 0.056 (blocked-run measure) |

Measured on one construction, geo falls 0.158 and unit falls 0.070 from 2Q26 to 3Q26. The filed build implicitly
moves geo by only −0.026 and unit by +0.097, each 0.13–0.17 above its same-construction change, while LOS falls
0.244 through the construction switch.

Two cases bound the LOS switch:

- **Case A:** the switch is a basis offset, and LOS truly held. The base is overstated by **0.054pp**.
- **Case B:** LOS genuinely fell. The base is overstated by **0.298pp**.

**Size.** 3Q26 −$0.09 to −$0.51 ($177.59 to $177.17); 4Q26 −$0.09 to −$0.50 ($172.94 to $172.54). The direction
is robust in both cases. Helps the short.

**Associated finding.** The 2Q26 core "acceleration" of +0.469 is **entirely** the H terms moving: geo contributes
+0.224 and unit +0.245, while ex-FX printed "4" in both 1Q26 and 2Q26 (`audit_core.log`). On I's construction the
2Q26 unit term barely moved.

### F3. The ladder's "AR(1) on core" is not an AR(1) on the core

**Claim.** `final_adr.md:510` shows "AR(1) on core, ρ 0.747, $172.38".

**Evidence.** `exfx.py:144` sets `rho, const = 0.747, 0.750` and labels them "K4's AR(1) on the residual". That
constant implies a long-run mean of 0.750 / 0.253 = **2.96**, against the core's own 2023–25 mean of **2.27**. It
is the same defect the brief flags for mean reversion, only larger: a 0.69pp error in the mean against 0.13.
Like-for-like
(`C2_ladder_corrections.csv`):

| version | 4Q26 ADR | 3Q26 ADR |
|---|---:|---:|
| filed row | $172.38 | $177.30 |
| K4's ρ with the core's own mean | **$171.87** | $177.00 |
| AR(1) fitted on the 14-quarter core (ρ 0.465, μ 2.41) | **$171.15**, below the Street | $176.36 |

Caveat stated against the finding: the refit AR(1) has a poor point-in-time record. It loses to the carry at h = 1
and h = 2 (`C1_core_pit_scores.csv`). Helps the short, as a scenario row.

### F4. The bundle's sizing band is narrower than its source's rounding (C5)

**Claim.** Bundle = 1.0pp, band 0.8–1.2 (`exfx.py:15`, envelope ±0.20).

**Evidence** (C5, verbatim, CFO prepared remarks). Both are three-feature, global, y/y contributions in the
quarter, with no ex-FX qualifier.

- 4Q25: "over 200 basis points of growth in nights booked and roughly 300 basis points of growth in GBV".
- 1Q26: "approximately three points of nights booked growth and approximately four points of GBV growth".

The GBV-minus-nights gap the rounding permits:

| call | nights | GBV | gap permitted |
|---|---|---|---|
| 4Q25 | 2.0–2.5 | 2.5–3.5 | 0.0–1.5pp |
| 1Q26 | 2.5–3.5 | 3.5–4.5 | 0.0–2.0pp |

An honest band is about 0.5–1.5pp.

The 1Q26 figure is preceded by "we expanded Reserve Now, Pay Later to more markets", so it **includes about six
weeks of the ex-NA leg**. The base sets that leg to 0 because "the 1Q26 '~1' did not rise above 4Q25's '~1'"
(`adr_v1_design.md:218`). At this rounding the statement cannot identify that.

**Size.** 4Q26 ex-FX moves one-for-one against the bundle size, because core = residual − bundle and the bundle
is zero from 4Q26. ±0.5pp is **±$0.84** on 4Q26, against the ±$0.34 filed. Symmetric, so it is a band finding.
Widening it moves the 4Q26 ex-FX half-band from 1.42 to about 1.50.

### F5. The World Cup is absent from the ADR line (C1 and C2)

**Evidence.** `final_adr.md`, `adr_v1_design.md`, the v2 notes and D4 never mention it. The nights line of the
same model says the bulk of World Cup nights were **booked in 2Q26** (`nights_v2_design.md:444`) and books a
−0.5pt 2Q27 lap of that pull-forward (`final_nights.md:931`). ADR is booking-dated. Any event-price composition in
2Q26 bookings therefore sits inside the 2Q26 core, which the ADR line carries flat through 2Q27, including the
quarter the nights line laps it. The two lines of one model disagree.

**Size: unmeasured; sign unambiguous.** The team's World Cup work (`docs/pitch-forecasts/questions/
risk-world-cup-quantified-small/`) sizes no price. A carried event premium equals s × (k − 1), where s is the
share of 2Q26 nights priced at event rates and k is their price relative to average ADR. Break-even premium
(k − 1) needed to reach the Street at 4Q26:

| starting point | gap to Street | s = 0.45% (the nights line's own 0.5pt pull-forward) | s = 2% (illustration only*) |
|---|---:|---:|---:|
| filed base | 1.02pp | +225% | +51% |
| F6 netting + F2 case A | 0.92pp | +202% | +46% |
| F6 netting + F2 case B | 0.67pp | +148% | +34% |
| F6 netting + F2 case B + V1 FX (F1) | 0.44pp | +97% | +22% |

\* The 2Q26 letter says "Airbnb hosted millions of guest arrivals during the tournament". Two million arrivals, at
2.5 guests and 4.1 nights per booking, is about 3.3m nights, roughly 2% of 2Q26 nights, *if* booked in 2Q26. That
is an order-of-magnitude illustration, not a measurement.

A second channel runs the same way: any post-draw (5 Dec 2025) World Cup bookings at event prices in 4Q25 make
the 4Q26 comparison base tougher. Helps the short in sign. It is not quotable until s and k are measured
(open choice 7).

### F6. The "+ sub-regional" row double counts (hurts the short)

**Claim.** "base + sub-regional mix $172.79, −$0.25" (`final_adr.md:508`).

**Evidence.** `exfx.alternatives()` (`exfx.py:181`) adds the full forward term (−0.147) on top of a core that
already contains 2Q26's sub-regional term (−0.100). The residual is ex-FX minus the four-region terms only. The
authors' own H2 code does it correctly (`run.py` `h2_scores`: core2 = residual − bundle − subgeo). The netted
increment is **−0.047** (4Q26) and −0.037 (3Q26).

**Size.** The row is really **$172.96** (+$0.17). The OD-tilt and tilt-B rows are built on it and inherit the
double count.

### F7. Mean reversion uses the wrong mean (brief §4, confirmed)

`exfx.py:22` sets `CORE_MEAN_2023_25 = 2.398`, the residual's mean. The core's own mean is **2.272**.

| row | filed | like-for-like |
|---|---:|---:|
| 4Q26 | $170.60 | **$170.39** |
| 3Q26 | $175.20 | **$174.98** |

**Decision recommended: correct it.** It is a definitional fix, not a chosen input. The brief's "runs against the
short" describes the *error*; correcting it lowers the row by $0.21. Correct F3's AR(1) at the same time, because
it is the same defect.

### F8. The core's own record does not support carrying beyond two quarters (C1)

**Claim.** "Carried flat for six quarters … its own 0.88pp one-quarter error in the band" (`final_adr.md:258–262`).

**Evidence.**

- *The band's h-step sd shrinks at long horizons* (1.35 / 1.38 at h = 2–3, then 1.15 / 0.98 / 0.97 at h = 4–6,
  `C1_core_hstep_errors.csv`). That is the signature of a mean-reverting core, the process under which a flat
  carry from the series' historical high (3.849 is the maximum of 14) is biased. From starts more than 0.5pp
  above the mean, the mean h = 2 change was −1.47 (n 2 only, so descriptive).
- *Point-in-time, the carry loses to the core's expanding mean at longer horizons* (`C1_core_pit_scores.csv`):

  | h | ratio of mean to carry, targets 1Q24+ | targets 1Q25+ | n |
  |---:|---:|---:|---:|
  | 2 | 0.787 | 1.039 | 9 / 6 |
  | 3 | 0.784 | 0.839 | 8 / 6 |
  | 4 | 0.679 | 0.782 | 7 / 6 |

  At h = 3 and h = 4 the mean wins in **both** windows, which clears the repo's two-window rule, but on n 6–8. At
  h = 2 (4Q26) the windows split.
- *Rounding.* Ex-FX prints to whole points, so the carried 2Q26 level carries ±0.5 (sd 0.29). Rounding contributes
  0.41 in quadrature to the 0.88 quarterly-change sd; the true-change sd is about 0.78. Carrying the 1H26 average core (3.615) instead of the single rounded
  2Q26 value moves both quarters by −$0.39.

**Size.** Nothing on 3Q26 or 4Q26. With an expanding-mean core (2.464) for 1Q27–4Q27 and the carry for h ≤ 2, FY27
ADR is **$182.71 against $185.21 (−1.35%)** and FY27 GBV −$1.56bn (`C1_fy27_expanding_mean_core.csv`). Helps the
short on FY27.

**Also checked.** Nothing else in the repo identifies the core. The repo's own tests find no US lodging
comparator that works: US CPI lodging-away-from-home swung from about −4% (2H25) to +7% (Apr–May 2026) and back to
+1.8% (Jun–Aug), but the ADR line reports it at r 0.00. The World Cup (F5) and the H fills (F2, F9) are the only
in-repo mechanisms that bear on the 2026 step.

### F9. Part of the core's 2026 step is an assumption (hurts the short via the mean-reversion row)

**Evidence.** Of the 4Q25→1Q26 residual step of +0.682, **+0.306 is the assumed seats term** stepping from −0.177
to −0.483 (no volumes disclosed). LOS and interaction in 2026 are also fills. The carry forecast is unaffected,
because the same fills are carried forward. The "1.58pp above its mean" gap and the mean-reversion row are not.

**Size.** If the seats step were not real, the mean-reversion row is too low by up to 0.31pp (**+$0.52**).

### F10. EMEA's one validated proxy argues for persistence (hurts the short)

The constellation's only surviving proxy is EMEA ex-FX ADR against euro-area HICP accommodation (r 0.74,
`adr_v1_design.md:433`). Euro-area CP112 y/y (`govdata/P/raw/eurostat_hicp_cp112_family_monthly.csv`) averaged
**3.1% in 2H25, 4.1% in 1H26, and 4.6% in July 2026**. EMEA like-for-like pricing firmed in 2026 and had not faded
by July. EMEA is 37% of GBV. This is evidence for the carry on that share, not against it.

### F11. The 3Q26 FX falsifier is mis-specified

**Claim.** "(a) on 5 Nov the printed 3Q26 ADR-FX pp … must fall inside the 21 Sep as-of 80% band, else … the leg
is withdrawn" (`adr_fx_prereg.md:155`; `adr_v1_design.md:469–470`, band [0.36, 0.48]).

**Evidence.** The printed FX pp is reported y/y minus a *whole-point* ex-FX, so it carries ±0.5 of rounding. The
band is 0.125pp wide and holds only rate uncertainty. Simulated with the identity exactly right, P(print inside
the band) = **0.124** (`audit_fx2.log`). The rounding-aware reading (interval overlaps band) passes 0.995. Either
way the test cannot discriminate.

A single rounded print also cannot separate the identity (+0.42) from V1 (+0.03) or the basket fit (+0.44). It can
separate it from the euro fit (−1.12). "This adjudicates §2.6 directly" (`final_adr.md:527`) overstates.

DEC-0039's S1–S8 do not include this line and do handle rounding (S6 scores a whole number). But the §7(a)
wording has not been withdrawn. **Re-specify it before 5 Nov** (open choice 2).

### F12. The pooled reconciliation's significance is invalid, and its slope is mostly Brazil's CPI (C4)

Reproduced exactly (b 1.127, CRV1 p 0.042, 90% CI 0.349–1.905; LORO 1.127 / 1.235 / −0.302 / 1.247).

**Evidence** (`C4_pooled_reconciliation.md`).

- **With four clusters there is no valid cluster p-value.** The fully enumerated Webb wild-cluster bootstrap
  (1,296 draws) gives **p 0.889 for b = 0 and 0.898 for b = 1**. The observed sign vector is the least extreme of
  the 16 Rademacher draws.
- **LatAm's slope of 1.375 decomposes into:**
  - Brazil IPCA hospedagem moving inversely with the mix term: **+1.042, 76%** (r −0.81).
  - Airbnb's disclosed ex-FX: **+0.358, 26%**.
- **Neutral LatAm comparator.** Zero inflation gives pooled b **0.239**; the other regions' median gives
  **−0.353**. All four LORO slopes then agree. The CRV1 p-values that "reject 1" here inherit the same four-cluster
  problem, so the honest statement is the point estimates, not a rejection.
- **What the −0.81 is.** Over the 18 quarters the comparator exists, Brazil's hotel CPI has r **0.00** with the
  LatAm mix term. The −0.81 exists only in the seven disclosed quarters, when a Brazilian stays boom (+51% / +58%
  y/y in 1Q25 / 2Q25) moved both sides of the regression.
- **Mexico and Chile: not obtained** in three fetches (log below). INE Chile's IPC is behind an interactive
  selector; INE.Stat serves no price dataset; the INEGI page is JS-rendered and its API needs a token. Bound: with
  the pre-stated blend (Brazil 0.368 / Mexico 0.440 / Chile 0.192), the slope is 0.57 if the new series are
  neutral. It returns to 1.0 only if their hotel CPI co-moved at −0.81pp per pp, nearly Brazil's own −1.04.

**Consequence.** "Cannot reject it … That is the good news, and it is real" (`final_adr.md:389–390`) and
"compatible with the identity" (`final_adr.md:572`, thesis:35) should read **"not established"**. The annual
10-K reconciliation (−1.10 / −1.33 / −1.67 vs −1.08 / −1.24 / −1.58) is untouched and remains the evidence for the
between-region term. No ADR dollar changes.

### F13. The 4Q27 FX artefact reaches FY27 unlabelled (brief §4)

It is labelled where the FX point is shown (`final_adr.md` §2.8, :495, :666; `adr_v1_design.md:149, 506`;
prereg:209). It is **not** labelled in:

- `final_adr.md:487` (FX 0.000 in the §6.1 row), :489 and :668 (FY27 $185.21)
- thesis:54
- `adr_v1_design.md:36, 331, 393, 543–544`
- DEC-0035 ($178.10)
- the workbook, `ADR_Engine!AD51/AD94`, a live formula with no artefact text
- `Income_Statement!V10`
- FY27 revenue `=SUM(S12:V12)`
- `final_income_statement.md`'s FY27 revenue and margin (33.97% vs 36.45%)

4Q27 is 22.5% of FY27 nights, so each 1pp of 4Q27 FX is about $0.40 of FY27 ADR. Against the P10–P90 of
−4.3 / +5.1pp, that is ±$1.7–2.0 of FY27 ADR hidden inside one "exactly zero" cell.

### What I tried to break and could not

- **The FX identity's arithmetic, point-in-time protocol and promotion.** Correct as registered. V0 legitimately
  wins the pre-registered tie-break, and V2 cannot legitimately be promoted.
- **The ladder.** Every §6.2 number reproduces to the cent.
- **C6.** The sub-regional term is quarantined. `exfx.forward()` reads no sub-regional file; it enters only
  `alternatives()` and workbook block G1, which is labelled "NOT the base". The blind spots are stated: no Indian,
  Emirati, Malaysian, Indonesian or Vietnamese market. "Australia 57%" is its base-quarter share in the 2Q26 pair
  (57.1%); the pooled 1Q23–2Q26 figure is 52.9%, and neither document dates it.
- **C7.** The utilisation panel is reported as a failure everywhere (b 0.0829, p 0.794, n 94 / 92) and is read
  only by `market_panel.py` and the workbook's evidence block. It is never in the base or the band.
- **C5.** No filed magnitude exists. Ten filed documents were searched, including the 3Q25 10-Q and the 2026
  DEF 14A fetched from EDGAR. "Transcript-only" survives a wider search than the authors ran; see §5 for the
  wording that does not.
- **The pre-registration text.** §0–§9 are byte-identical to blob 0495e5f3.

---

## 4. The C2 question: is there a defensible composition route below the Street?

**No.** Stated assumptions first; every number is mechanical (`C2_basis_bounded.csv`,
`C2_ladder_corrections.csv`).

| construction (4Q26) | ADR | vs $171.33 |
|---|---:|---:|
| filed base | $173.03 | +$1.70 |
| + sub-regional, netted against 2Q26 (F6) | $172.96 | +$1.63 |
| + terms on one construction (F2), case A / case B | $172.87 / $172.46 | +$1.54 / +$1.13 |
| same, with the pre-registered V1 FX weights (F1) | $172.48 / **$172.07** | +$1.15 / **+$0.74** |
| filed "lap-only" (a core assumption, shown for reference) | $171.71 | **+$0.38** |
| lap-only on one construction, case A / B | $171.61 / $171.21 | +$0.28 / −$0.12 |

- **Composition, consistently measured, lands at $172.46–$172.87.** Adding the pre-registered V1 FX weights
  gives **$172.07–$172.48**. The audit narrows the gap to the Street from $1.70 to $0.74 at best. It does not
  close it.
- **The document's own ladder overstates the route.** "Only core assumptions cross ($171.71 lap-only, $170.60
  mean reversion)" is wrong for lap-only, which sits **$0.38 above** the Street as filed. As filed, only mean
  reversion crosses. After this audit, three core rows cross: mean reversion at the core's own mean ($170.39), an
  AR(1) fitted on the core ($171.15), and case-B lap-only ($171.21).
- **The one candidate that could make a composition route is the World Cup (F5).** It is unmeasured, and under
  DEC-0016 a premium cannot be picked to close the gap. Break-even: an event premium of +97% on the nights line's
  0.45% share, or +22% on a 2% share, starting from the most bearish consistent row. A defensible route requires:
  - measuring s and k from a sanctioned source (Inside Airbnb June 2026 listings for the 16 host cities against
    the same markets' June 2025 vintage);
  - writing the measurement rule down before looking;
  - resolving F2's LOS case.

  Until then the binding negative stands: **a below-Street 4Q26 ADR is a core call, not a mix call.**

---

## 5. What the documents assert that the outputs or filings do not support

| where | assertion | what the evidence says |
|---|---|---|
| `final_adr.md:565`; brief C1 | "The core is 40% of your ex-FX number" | Core 3.849 is **116%** of 3Q26 ex-FX (3.316) and **138%** of 4Q26 (2.784). The 41% is the unexplained step ÷ core. The core is larger than the whole ex-FX number. |
| `final_adr.md:516–517`; thesis:57; brief C2 | lap-only $171.71 "crosses" | It is $0.38 above $171.33. `adr_v1_design.md:339` says "on the Street", which is closer. |
| `final_adr.md:282, 575`; thesis:85–86; DEC-0041 | "Airbnb did not name RNPL in a filing at all until 2Q26" | **False.** The 3Q25 letter (8-K Ex 99.1, acc. 0001193125-25-269432) names "Reserve Now, Pay Later" five times, and the 4Q25 letter, FY25 10-K and 1Q26 letter name it too. It is true only of the acronym within the 10-K/10-Q series. The ledger's own row D008 cites the 3Q25 letter as filed. |
| `final_adr.md:280`; DEC-0041 | "read … both shareholder letters end to end"; search "exhaustive" | The letters were 4Q25 and 1Q26 only, and X3 read them through a keyword extraction, not end to end. C5 added the 2Q25, 3Q25 and 2Q26 letters, the 3Q25 10-Q, the DEF 14A and the 8-K list. The conclusion survives; the wording does not. |
| `final_adr.md:389–390, 572`; thesis:33–35 | "cannot reject it … real"; "compatible with the identity" | No valid inference at G = 4 (F12). Should read "not established". |
| thesis:21 | posterior "without improving it out of sample" | V1 beats V0 in both W2 cells. |
| `final_adr.md:154` | "excluded before the scores existed" | True of the walk-forward scores. The euro fit's LOO lead (6 Sep) and its 3Q26 value (11 Sep) predate the registration, and the ordering cannot be shown from git (F1). |
| `final_adr.md:413–414`; mitigation D:204 | "EMEA printed its first sub-50% English quarter in 2Q26" | The first was **4Q25** (49.54%); 1Q26 was 46.17%. |
| `final_adr.md:552`; thesis:49 | "Sub-regional construction reproduces the disclosed-share four-region term within 0.13pp" | That is the four-region bucket check, mislabelled; max 0.218. |
| `final_adr.md:14`, :15 | "reproduces from raw stores in about twenty seconds (27 tests)" | Only on a machine holding `~/abnb_ia_capture` 2026 dumps (exit 1 here); the posterior needs PyMC. |
| `final_adr.md:161, 527` | "3Q26 is their quarter"; the print "adjudicates §2.6 directly" | 3Q26 is the quarter where the identity's documented LatAm error is largest (F1). One rounded print cannot separate +0.42 from +0.03 (F11). |
| band labels, everywhere | "band 176.01–179.36" | The half-band is used as **one sd** (`assemble.py:21`), so it is a ~68% band built by RSS of half-ranges and sds. S7 (`upgrade6:132`) therefore fails about 32% of the time when the model is right. Unlabelled. |

**Stale numbers still live** (details and line numbers in `DOC_CONSISTENCY.md` Task 2):

| stale text | where | superseded by / correct value |
|---|---|---|
| "10 tests" | `adr_v1_design.md:8` | 27 |
| "1.45pp above its 2023–25 mean" | `adr_v1_design.md:197`, geomix_prereg:73, upgrade3:249, mitigation A:363, mitigation B:7 | final_adr's 1.58 against the core's mean |
| "1.1pp, not 1.45" | `adr_v1_design.md:268` | three step sizes live on three bases |
| tilt B $172.19 / −$0.84 | `adr_v1_design.md:272` | $172.18 / −$0.86 |
| like-for-like 2025 = 3.93 | `adr_v2_upgrade3_reconciliation.md:25, 35, 241` and `adr_v1_design.md:298` | withdrawn by DEC-0040; no supersession banner |
| V2 bias "−0.27 to −0.46" / "−0.3 to −0.5" / "−0.27 to −0.34" | across documents | each on a different, unnamed set of cells |
| card-v3 2027 path (4Q27 $177.47) | `dossiers/D4_d4_adr.md:131–145` | carried with no banner |

---

## 6. Open choices for the humans

Each has options and a recommendation. None is decided here.

1. **How to present 3Q26 / 4Q26 FX (F1).**
   - (a) V0 point only, as filed.
   - (b) V0 stays the registered leg, but show V1 (+0.03 / +0.28, a pre-registered variant) beside it with one
     sentence on the identity's LatAm-conditional error, and use the −0.8 to +0.42 range in the judge Q&A.
   - (c) Switch the leg to V1. This breaks the registered tie-break.

   **Recommend (b).** It keeps the registration and stops the pitch from quoting 65% for 3Q26 on a known
   conditional bias.
2. **Re-specify the 3Q26 FX falsifier before 5 Nov (F11).**
   - (a) Leave it: 88% false withdrawal.
   - (b) Replace it now, by dated correction, with a comparative interval-likelihood score of identity / V1 / card
     midpoint / euro fit against the ±0.5 printed interval, with withdrawal only if the identity is the worst of
     the four.
   - (c) Drop it and rely on S1–S8.

   **Recommend (b).** Filing before the print keeps it honest.
3. **Put the ex-FX terms on one construction (F2).**
   - (a) Rebuild each forward term as a change on one construction, and carry LOS at its in-core value until a
     same-construction 2Q26 LOS exists.
   - (b) Recompute the core on the forward terms' constructions.
   - (c) Leave it and label it.

   **Recommend (a),** which is case A: −$0.09. Report case B (−$0.50) as the bound until the LOS question is
   settled. Either way it is a consistency rule, not an input chosen for price.
4. **Correct the mean-reversion and AR(1) rows (F3, F7).**
   - (a) Correct both to the core's own mean and an AR(1) fitted on the core.
   - (b) Correct mean reversion only.
   - (c) Leave both, flagged.

   **Recommend (a),** and fix the ladder's "lap-only crosses" sentence at the same time.
5. **Fix the "+ sub-regional" row (F6).** Net the forward term against 2Q26's (−0.047, giving $172.96) or leave it.
   **Recommend netting.** The authors' own H2 code already does it.
6. **Rule for the core beyond two quarters (F8).**
   - (a) Carry for all six quarters, as filed.
   - (b) Pre-register now a horizon rule: carry for h ≤ 2, expanding mean for h ≥ 3. It wins at h = 3–4 on both
     windows (n 6–8) and gives FY27 $182.71.
   - (c) Show (b) as a labelled FY27 alternative only.

   **Recommend (c) now and (b) for Theo's decision,** stated with its n. The rule is chosen by its record, not
   its price.
7. **The World Cup term (F5).**
   - (a) Leave it out, as now.
   - (b) Add a labelled sensitivity row with the break-even table.
   - (c) Measure s and k from the sanctioned Inside Airbnb June 2026 host-city listings against the June 2025
     vintage, under a rule written before looking.

   **Recommend (b) now and (c) this week.** It is the only item that could turn C2 into a yes, and the capture
   window is seasonal. It also resolves the ADR / nights inconsistency.
8. **Widen the bundle band to the rounding-supported 0.5–1.5pp (F4)** and state that the 1Q26 figure includes
   about six weeks of ex-NA RNPL. **Recommend yes.**
9. **Downgrade the pooled reconciliation's wording to "not established" (F12),** and keep the annual 10-K
   reconciliation as the evidence. **Recommend yes.** Mexico and Chile need a human to register a free INEGI or
   Banxico token, or to use INEGI's browser export and INE Chile's interactive file selector
   (`C4_pooled_reconciliation.md` §6.2). The bound says even a perfect result restores the slope only if their
   hotel CPI surged exactly as Brazil's did. **Recommend deprioritising.**
10. **Amend DEC-0041's wording (C5).** Keep "transcript-only" (it survives a wider search), fix the RNPL-naming
    sentence, list the ten documents actually searched, and drop "both letters end to end". **Recommend yes.**
11. **Label the 4Q27 artefact wherever FY27 ADR, FY27 GBV or FY27 revenue appears (F13)**, including the workbook
    and `final_income_statement.md`, or carry FY27 with the 4Q27 FX shown as a band. **Recommend labelling now.**
12. **Housekeeping.**
    - Fix the six §5 statements.
    - Put supersession banners on `adr_v1_design.md`, `adr_v2_upgrade3_reconciliation.md` and D4.
    - Label the band as ±1σ.
    - Make `run.py` fall back to `--no-refresh-prices`, with a clear message, when the capture store is absent.

    **Recommend all.**

---

## Budget and rules log

**Web fetches: 5 of 5, all by sub-agents, all logged in their receipts.**

| # | agent | URL | result |
|---|---|---|---|
| 1 | C5 | `sec.gov/.../abnb-20250930.htm` | 200, 1,478,397 B |
| 2 | C5 | `sec.gov/.../d936646ddef14a.htm` | 200, 1,008,113 B |
| 3 | C4 | INE Chile IPC page | no file URL obtainable |
| 4 | C4 | `stat.ine.cl` SDMX structure | 200, 32,456 B; no price dataset |
| 5 | C4 | INEGI INPC page | JS-rendered, no data |

C5 reused the repo's existing EDGAR User-Agent string. C4 also ran five web *search* queries that fetched no data.
They are listed in its receipt so the humans can judge whether they count against the budget.

Nothing touched airbnb.com. No credentials were entered. Nothing was committed or pushed. Nothing on a kill list is
quoted as ours; the unit-size term is not described as "half of ADR growth".

---

## RESUME

The next agent should start with open choices 2 and 7, because both are time-bound.

**Choice 2.** The 3Q26 FX falsifier must be re-specified by dated correction before 5 Nov.

**Choice 7.** The World Cup measurement is the only route that could produce a defensible below-Street
composition case, and the June 2026 capture is seasonal. Before looking, pre-register:

- the host-city market list;
- the event-window definition;
- s as the share of 2Q26 booked nights in host cities on match-adjacent dates;
- k as their listed price against the same listings' June 2025 vintage.

**If Theo accepts choices 3–5.** Re-run the ladder: `exfx.alternatives()` needs the netting, the core's own mean,
a fitted AR(1) and one-construction terms. Then re-run `run.py --no-refresh-prices` and pytest, and update
`final_adr.md` §6.2 and the thesis.

**Receipts.** Every number in this dossier reproduces from `receipts/ADR_AUDIT/` with
`PYTHONPATH=analysis/src py -3.13 data/processed/pitch_model_v2/receipts/ADR_AUDIT/<script>.py`. Run them in this
order: `audit_fx.py`, `audit_fx2.py`, `audit_core.py`, `audit_extra.py`, `audit_basis.py`, then
`C4_audit.py` / `C4_bounds.py`. The last two are in `C4_pooled_reconciliation.md`.
