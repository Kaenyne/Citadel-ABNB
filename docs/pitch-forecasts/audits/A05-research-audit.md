**C08 — 0.50 / 0.30 / 0.18 / 0.02: plausible judgment, insufficiently supported as written.**  
The main mixture reproduces; the headline vector sums to one.  
Its management guide record omits a material miss and assigns numbers to ambiguous language.  
First repair the reference class, model attribution, and invalid sensitivity vectors.  
Auditor comparison: **0.56 / 0.26 / 0.16 / 0.02**.

**C11 — 0.55: not defensible together with the published conditional forecasts.**  
The GBV-band table implies **0.7646**, independently reproduced as **0.7650** before rounding.  
The management-language evidence also contains a material transcription error.  
First construct one joint distribution whose conditional and unconditional probabilities agree.  
Auditor comparison: **0.68**, with judgmental uncertainty approximately **0.50–0.85**.

**C12 — 0.55: reproducible, but substantially assumption-driven.**  
The three-route mixture reproduces at approximately **0.558**.  
Unpaid-share growth, seasonal deepening, and treatment of management’s contrary statement drive the result.  
First correct the historical norm and explicitly price the alternative seasonal interpretation.  
Auditor comparison: **0.44**, with judgmental uncertainty approximately **0.25–0.65**.

## Scope and reproduction

Audit date: **2026-09-17**. Read-only audit of the supplied logs, JSON forecasts, datasets, saved market/FRED snapshots, relevant processed panels, backtest notes, letters, and available filings. No network fetch was attempted; external-source conclusions below concern the saved evidence, not independently refreshed information. Neither prohibited raw-data directory was opened.

All three forecast scripts were replayed **in memory**, intercepting their CSV writes. Their **14 generated tables** reproduced the saved numerical outputs within **3.7×10⁻¹²**. This establishes computational reproducibility, not validity of their assumptions. No repository files, workboard entries, or forecast registrations were changed.

In the table, `C08/`, `C11/`, and `C12/` denote:

- `docs/pitch-forecasts/questions/q3-revenue-fx-integer/`
- `docs/pitch-forecasts/questions/q3-take-rate-above-1810/`
- `docs/pitch-forecasts/questions/q3-unearned-fees-yoy/`

No R/B questions are included; impact tables and impact EV calculations are therefore inapplicable. There is no necessary probability ordering among these three events. Their shared FX, GBV, and RNPL assumptions require consistency, but the most direct mathematical contradiction is within C11.

## Findings

| id | question | severity | file:line or field | what is wrong | how you verified | proposed fix (with the recomputed number where available) |
|---|---|---|---|---|---|---|
| A05-01 | C11 | critical | `C11/forecasts/2026-09-17-forecast.json`: `final.p`, `conditional_on_gbv`; log §6 | The required conditionals and unconditional are different forecasts. Calling the GBV table the “final mixture” is incorrect after separately pooling its probability with language and Street estimates. | The CSV’s six masses sum to **1.000**; Σ mass × conditional P = **0.764632**. In-memory replay gives **0.765010**. The headline is **0.55**. The stated final pool separately gives **0.5265**, followed by an upward judgment adjustment. | Build a joint distribution for every final component and regenerate both outputs. Alternatively label the existing table explicitly as decomposition-only, but still supply the required final conditionals. The existing table supports approximately **0.765**, not **0.55**. |
| A05-02 | C08 | major | `C08/research-log.md`: claims 3, 14; §5; `datasets/c08_guide_track_record.csv` | The “9 of 10 / never more than 0.5 below guidance” record is a selected, partly subjective reference class. It omits a clear W1 numeric miss. The 3Q23 letter’s comparison with the preceding quarter does not uniquely specify a +2 FX guide; the 1Q24 letter’s combined sequential headwind does not specify −0.5 FX. | Re-read the relevant Outlook paragraphs. `02_guidance_ledger.csv` gives 1Q23 reported-growth midpoint **18.5%**, ex-FX **20.5%**: FX guide **−2**, versus printed **−4**. Numeric-only pairs checked are **−2→−4, −3→−2, +3→+3, +3→+4**. | Publish a complete guide-availability ledger and separate explicit numeric guidance from analyst coding. Numeric-only “printed ≥ guide” is **3/4 in W1, 3/3 in W2**; the +3 subgroup remains **2/2**, too small to establish a 0.6-point predictive SD. |
| A05-03 | C11 | major | `C11/research-log.md`: claim 4; §5 `base_rate_estimate` | The 2Q25 take-rate increase is **+21.2 bp**, not +9 bp. Moreover, realized changes are labeled “errors versus guided direction” without defining a numerical forecast for “higher.” The assertion that prints exceeded guidance by at most 9 bp is unsupported. | From `data/processed/abnb_driver_history_quarterly.csv`: **3096/23500 − 2748/21200 = 0.00212204**, or **21.2204 bp**. The six actual changes are **+0.43, +21.22, −68.51, −47.33, −10.22, +9.02 bp**, mean **−15.90 bp**. | Correct the history; preregister numerical language intervals before scoring them. Treat **0.18** as an elicited language-based judgment, not a reproduced empirical probability. Include earlier available language observations or explain their exclusion. |
| A05-04 | C08 | major | `C08/datasets/c08_model.py`: sensitivity `add(...)` calls; `c08_sensitivity.csv`; JSON `sensitivity` | Two supposed single-assumption sensitivities change mixture weights without normalization. The dollar-weakening scenario also moves the USD-per-currency basket in the wrong direction. | “Management centre 3.5” uses weights totaling **0.92**; its saved vector sums to **0.921**. “Dollar −5%” uses weights totaling **1.05**; its saved vector sums to **1.048**. Code subtracts **0.8** from a basket defined positive for dollar weakness. | Hold weights fixed. Analytic repaired centre-3.5 vector: **0.5683/0.2437/0.1680/0.0200**. For a **+0.8-point basket** scenario, repaired vector: **0.5171/0.3152/0.1477/0.0200**. Separately justify how a 5% dollar move maps to that basket change. |
| A05-05 | C08 | major | `C08/research-log.md`: claims 4–6; §4 first hypothesis; §5 | Evidence for the ADR-FX H2 model is transferred to the basket construction that produces approximately +3. These are different specifications. | Recomputed from `fx_lag_v2/09b_pit_expanding_window_forecasts.csv`: H2 ADR-FX RMSE **0.9936**, **n=10 in both windows**, live point **1.8527**. H2b basket RMSE **1.7975/1.3155**, **n=14/10**, live point **2.9960**. `B4_FX_EXHIBIT.md` explicitly calls Φ×0.851 a construction, not a fitted object. | Attribute each score to its exact model. Do not describe the +2.9/+3 basket component as the winner with 0.99 RMSE. Calibrate its uncertainty using its own errors or label the narrower SD as judgment. |
| A05-06 | C08, C11, C12 | major | All logs §5; JSON `estimates`, `not_independently_derived_flag` | Three independent estimates are not established. C08’s “anchor” is a cluster already inside its decomposition; C11’s anchor is a judgmental blend partly using the same Kalshi route already inside its decomposition. C12 correctly flags dependence, but its anchor’s **0.45** is not derived from a probability distribution. | Traced model components and anchor descriptions. C11’s actual external inputs are LSEG-family revenue **$4,744.88187M**, stamped **2026-09-13T15:20Z**, and MODL GBV **$26,375M**, dated **12 Sep**. Neither directly supplies P=0.45. No direct event market is present in the saved searches. | Set C08/C11 dependence flags true; preserve C12’s flag. Distinguish external observed levels from internally transformed probabilities. Specify transformations and pooling weights. Label absent external probability anchors as absent instead of manufacturing apparent agreement. |
| A05-07 | C12 | major | `C12/research-log.md`: §0b convention 4; §4 first hypothesis; §7 pre-mortem | The strongest contrary evidence is interpreted away without an explicit alternative-model weight. “RNPL cannot raise the stock” is valid only holding the booking book fixed; the forecast itself allows RNPL to change demand and lead times. | The saved 1Q26 letter explicitly says lower unearned fees in Q1/Q2 and higher in Q3. D038/D055 in `rnpl_statement_ledger.csv` interpret this as a forward test. The log instead predicts a **more negative** sequential change, and acknowledges a contrary seasonal mechanism as “not modelled.” | Retain both readings as uncertain interpretations. Give a separately specified branch to payment catch-up/lower September unpaid share. Show how much that branch changes P, rather than letting an accounting argument eliminate an economic scenario. |
| A05-08 | C12 | major | `C12/research-log.md`: claim 5; claims 14–15; `c12_model.py` unpaid-share inputs | The quoted historical unpaid-share range is too narrow, and extrapolation to **u=18±3%** suppresses the backlog-scale ambiguity emphasized by its source. Flow adoption is not a measurement of unpaid quarter-end stock. | `docs/rnpl-short-audit/04_balance-sheet-verification.md` C3 gives, at B=1, **1Q26 10.7–13.9%** and **2Q26 14.0–16.8%**; at B=1.10, **18.8–21.8%** and **21.8–24.4%**. It explicitly says public evidence does not separate **u from B**. Replayed Route A: u=15 gives **0.1961**, u=18 **0.4551**. | Correct the quoted ranges. Model backlog scale and unpaid share coherently, or call u an effective shortfall parameter conditional on B=1. Expose uncertainty in its seasonal mean and avoid treating “over 20%” flow adoption as convergence evidence. |
| A05-09 | C12 | major | `C12/research-log.md`: §5 Route C; `c12_model.py`: `norm_mu=0.661` | The “pre-RNPL” normal ratio effectively includes the RNPL launch quarter, then applies another full unpaid-share deduction. | From `02_kpi_panel_quarterly.csv`: Q3 UF/next-quarter revenue is **0.661407, 0.668145, 0.655148** for 2023–25. The genuine 2023–24 mean is **0.664776**; the three-year mean is **0.661566**, matching the selected 0.661. The log itself calls 3Q25 RNPL-contaminated. | Use **0.664776** for a two-year pre-RNPL norm, or justify a different dated window. If using 3Q25, adjust its treatment explicitly. The two-year sample is small: retain norm uncertainty rather than presenting it as an established constant. |
| A05-10 | C12 | major | `C12/research-log.md`: §8, 2026-10-13; JSON `monitoring` | The October migration deadline is treated as a direct probability-moving event for a balance measured on **30 September**. | Compared the resolution date-of-balance with the monitoring rule “migration term to the top of its range … final −0.03.” October completion alone does not change September transactions. | Update only if October information reveals migration already effective by **30 September**. Otherwise assign no direct change to this forecast; use the completion information for Q4. |
| A05-11 | C11 | major | `C11/datasets/c11_model.py`: point-GBV loop; log §6 | “Point-GBV” runs are not conditional probabilities from the joint model. They recenter GBV at each queried value, so the standardized GBV shock returns to zero instead of conditioning revenue on the original shock. | Code calls `run(gbv_override=g, gbv_override_sd=1.0)` and recomputes `z=(gbv−mean)/sd`. Thus the point table changes the prior. It is distinct from correctly filtering the existing band draws. | Label these as alternative-GBV-prior sensitivities. For P(YES \| G=g), condition within each original component and update component weights by their GBV densities. Regenerate them after repairing A05-01. |
| A05-12 | C11 | major | `C11/research-log.md`: §5 final adjustment; JSON `reason_for_rounding_up` | The upward adjustment for the FX wedge risks counting information twice. The numerator begins with a revenue guide already inclusive of approximately +3 points FX; the denominator uses reported ADR. | Verified the 2Q26 letter’s guide and `c11_model.py` inputs. The linear pool is **0.5265**, raised to **0.55** for the same FX story. C08 meanwhile assigns only **0.50** to ≥+3 stated points. | Show which component receives genuinely additional information. Integrate revenue-FX alternatives into revenue draws, or make an explicit language-component adjustment. Do not apply an unexplained extra uplift to the pooled probability. |
| A05-13 | C12 | major | `C12/research-log.md`: §5 `base_rate_estimate` | Route A is a structural scenario model, not an empirical base rate. The event’s historical frequency is absent. | Recomputed UF growth from `02_kpi_panel_quarterly.csv`: **0/14** outcomes ≤−3% in W1 and **0/10** in W2; Q3-only **0/3**. The post-launch observations 3Q25–2Q26 also contain **0/4** threshold breaches. | Publish these counts with the explicit regime-break caveat. Rename 0.46 “gap-model estimate.” Historical zero frequency does not imply zero probability, but the departure needs to be attributed to quantified new assumptions. |
| A05-14 | C11 | major | `C11/research-log.md`: §6 extreme gate; JSON `conditional_on_gbv` | “Extreme-probability gate: not triggered” overlooks published conditional forecasts of **1.00**, **0.99**, **0.97**, and **0.00**. | The underlying final GBV band has P=**0.004**, rounded to **0.00**; low bands are displayed as certainty. No resolution-edge audit accompanies them. The model also does not explicitly round simulated GBV to the release’s reporting grid. | Preserve nonzero probabilities and perform the conditional extreme gate. Test release rounding and numerator/denominator conventions explicitly before publishing probabilities near certainty. |
| A05-15 | C08 | minor | `C08/research-log.md`: §6; JSON `within_option` | Two subsidiary tail probabilities do not follow from the stated model. | Analytically integrated the same normal components through the triangular integer kernel: **P(integer≤0)=0.04441**, **P(integer<0)=0.00729**, versus published approximately **0.10/0.02**. P(≥4)=**0.12805** does reproduce. | Replace the two tail values or identify a separately specified tail adjustment and regenerate the entire distribution. |
| A05-16 | C11 | minor | `C11/research-log.md`: claim 9; saved Kalshi JSON | “Volume field None” misses available activity fields, obscuring the weakness of the adjacent-market anchor. | Each of seven saved contracts has `volume_fp`; examples: **590.96** at 150M and **428.14** at 148M. All seven show `volume_24h_fp="0.00"` and `liquidity_dollars="0.0000"`. Quoted bids/asks reproduce. | Report the available fields and treat midpoint interpolation as a thin-market indication. Do not infer executable depth from the quoted spread. The interpolated median is approximately **148.27M nights**. |
| A05-17 | C08, C11, C12 | minor | All logs §2; `sources/web_queries_2026-09-17.md` | The claimed final 72-hour recency check reuses the earlier broad query; the saved record does not demonstrate a separate final, date-filtered search. The two fetched web pages are represented by excerpts, without saved full responses. | Compared ordered query logs and all three source inventories. FRED/API snapshots exist; the Smoobu/help-page claims have only the shared query note and excerpts. | Describe this limitation accurately. Preserve full fetched responses and search time/filter metadata on the next authorized refresh. Keep the neutral initial query; no evidence here warrants alleging a predominantly confirmation-shaped search. |
| A05-18 | C11 | minor | `C11/research-log.md`: §4 “in-line” hypothesis | The claimed inconsistency between “in-line” and guide-midpoint arithmetic is not demonstrated under the log’s own ±10 bp interpretation. | **4730/26317 = 17.97317%**, versus prior **4095/22900 = 17.88210%**: **+9.11 bp**, within ±10 bp. | Remove “inconsistent.” Explain instead why revenue beats, GBV forecast differences, and uncertainty might move the realized ratio outside the language interval. |

## What C08 should keep

Keep the distinction between **stated after-hedge FX**, gross FX, and contemporaneous currency movement. The saved FRED reconstruction reproduces **Q1 +5.675**, **Q2 +2.266**, and **Q3 QTD +0.483 / spot-held +0.600** approximately. The management +3 quotation and the competing registered model points are traceable.

The triangular rounding model is useful for the **difference between two printed integer growth rates**. Keep that branch, while distinguishing it from direct prose quantification and making any dollar-only resolution convention explicit. The final vector is normalized, and the 2% nondisclosure allocation has a documented format-change rationale.

## What C11 should keep

Keep the actual resolution object: **reported revenue divided by same-quarter reported GBV**. The distinction from the lagged kernel ratio is essential. The B1 replication succeeds: approximately **0.536** against the source’s **0.5345** under its inputs.

Keep the dated Street inputs, GBV sensitivity, and seasonal revenue-cushion calculation. The ledger confirms **19/19 midpoint beats**, **14/14 W1**, and **10/10 W2**. Q3 cushions are **1.9081%, 1.4030%, 0.8649%, 0.8621%** for 2022–25; the 2023–25 mean is **1.0433%**, and trailing-eight all-quarter mean **1.8567%**.

## What C12 should keep

Keep the correction to the superseded migration story. The available FY2025 10-K confirms that both host and guest fees enter unearned fees; the 2Q26 filing confirms RNPL payments do not enter that balance until received. The underlying audit’s small UF cash-flow reconciliation residuals support separating this line from funds-payable translation effects.

Keep the exact threshold **$1,765.4M**, the distinction between payment timing and cancellation, and the three routes as **dependent sensitivity lenses**. The panel verifies the $1,820M comparative and $2,831M starting balance; the available 2Q26 filing independently confirms $2,831M. A separate 3Q25 10-Q was not located in the permitted filing directories, so the comparative was checked against processed records rather than independently against that filing.

## Independent comparison forecasts

These are separately specified auditor judgments using the audited evidence. They are not market probabilities or fitted confidence guarantees.

### C08

| ≥+3 | +2 | ≤+1 | Not stated |
|---:|---:|---:|---:|
| **0.56** | **0.26** | **0.16** | **0.02** |

Derivation: assign 50% to management-centered N(3,1²), 25% to H2 ADR-FX N(1.8527,0.9936²), and 25% to H2b basket N(2.9960,1.3155²); apply the integer kernel and 2% nondisclosure.  
This yields **0.5582/0.2626/0.1592/0.0200**; the management weight and its SD are explicit judgments, with wider error than the selected ten-row record.

### C11

**P(YES)=0.68; judgmental uncertainty approximately 0.50–0.85.**

Derivation: use the mandated nights center 9.5%, SD 1.6 points, ADR 3.3%, SD 1.3 points; guide revenue × the verified 1.0433% Q3 cushion, cushion SD 0.5 points, correlation 0.5, and a 5% guide-miss branch gives approximately **0.857**.  
Pool that joint model at 70% with a 30% language regime having take rate N(17.90%,0.35²), P≈**0.284**, retaining the same GBV marginal; the resulting coherent joint forecast gives approximately **0.684**.

Its illustrative GBV conditionals are:

| GBV, $M | Mass | P(YES given band) |
|---|---:|---:|
| <25,600 | 0.28501 | 0.78684 |
| 25,600–25,900 | 0.22830 | 0.77170 |
| 25,900–26,200 | 0.22469 | 0.75234 |
| 26,200–26,500 | 0.15265 | 0.63537 |
| 26,500–26,800 | 0.07544 | 0.20104 |
| ≥26,800 | 0.03391 | 0.08158 |

Unlike the original table, these probabilities integrate to the associated headline. The alternative language regime and its 30% weight remain judgments, not measured frequencies.

### C12

**P(YES)=0.44; judgmental uncertainty approximately 0.25–0.65.**

Derivation: use the uncontaminated norm **0.664776±0.008**, Q4 revenue **$3,178.108±60M**, effective unpaid share **16.5±4%**, migration **+1±1%**, and FX **0±0.5%**, multiplying the level terms before comparing with **$1,765.4M**.  
This gives approximately **0.438**, median **$1,781M**; unpaid-share means of 15% and 18% give approximately **0.313/0.569**, demonstrating the dominant unresolved assumption.

## Reproduction script

Run from the repository root:

```powershell
python docs/pitch-forecasts/audits/A05-reproduce.py
```

The script uses **stdlib plus pandas only**, reads permitted files, and makes no writes or network requests. It reproduces the historical counts, key arithmetic, analytic C08 probabilities, and auditor comparison forecasts. It does not execute the original write-producing scripts.

```python
from pathlib import Path
import json
import math
import random
from statistics import NormalDist

import pandas as pd

ROOT = Path.cwd()
if not (ROOT / "docs/pitch-forecasts/QUESTIONS.md").exists():
    ROOT = Path(__file__).resolve().parents[3]

QUESTIONS = ROOT / "docs/pitch-forecasts/questions"
SLUGS = {
    "C08": "q3-revenue-fx-integer",
    "C11": "q3-take-rate-above-1810",
    "C12": "q3-unearned-fees-yoy",
}


def read_csv(path):
    return pd.read_csv(ROOT / path, comment="#")


def dataset(question, filename):
    return pd.read_csv(
        QUESTIONS / SLUGS[question] / "datasets" / filename
    )


def quarter_order(series):
    return (
        series.str[-2:].astype(int) * 4
        + series.str[0].astype(int)
    )


def show(label, value):
    print("\n" + label)
    if isinstance(value, pd.DataFrame):
        print(value.to_string(index=False))
    else:
        print(value)


# Revenue guide base rates and seasonal cushions.
ledger = read_csv("data/processed/overnight/02_guidance_ledger.csv")
guides = ledger[
    ledger.metric.eq("revenue_usd_m")
    & ledger.guide_type.eq("range")
    & ledger.actual.notna()
].copy()
guides = guides.sort_values("target_period", key=quarter_order)
guides["beat_pct"] = 100 * (guides.actual / guides.value_mid - 1)

show("Revenue midpoint beats: successes, n",
     (int((guides.beat_pct > 0).sum()), len(guides)))

for year in (23, 24):
    sub = guides[
        guides.target_period.str[-2:].astype(int) >= year
    ]
    show(f"Revenue beats, targets 20{year}+",
         (int((sub.beat_pct > 0).sum()), len(sub)))

q3_guides = guides[guides.target_period.str.startswith("3Q")]
show("Q3 revenue cushions",
     q3_guides[["target_period", "beat_pct"]])

q3_recent = q3_guides[
    q3_guides.target_period.str[-2:].astype(int) >= 23
]
cushion_mean = q3_recent.beat_pct.mean() / 100
print("Q3 mean including 2022:", q3_guides.beat_pct.mean())
print("Q3 mean 2023-25:", 100 * cushion_mean)
print("Trailing-eight mean:", guides.tail(8).beat_pct.mean())


# Printed take rates and the six selected language-pair outcomes.
driver = read_csv(
    "data/processed/abnb_driver_history_quarterly.csv"
).sort_values("quarter", key=quarter_order)
driver["take"] = 100 * driver.revenue_musd / driver.gbv_musd
driver["change_bp"] = 100 * driver["take"].diff(4)

show("Historical Q3 printed take rates",
     driver[driver.quarter.str.startswith("3Q")][
         ["quarter", "revenue_musd", "gbv_musd", "take"]
     ])

selected = ["3Q24", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
show("Six language-pair actual changes; not guidance residuals",
     driver[driver.quarter.isin(selected)][
         ["quarter", "take", "change_bp"]
     ])

for year in (23, 24):
    sub = driver[
        driver.quarter.str.startswith("3Q")
        & (driver.quarter.str[-2:].astype(int) >= year)
    ]
    print("Q3 take >=18.10, starting year", year,
          int((sub["take"] >= 18.10).sum()), "/", len(sub))

print("Guide-midpoint take rate:", 100 * 4730 / 26317)
print("Prior Q3 take rate:", 100 * 4095 / 22900)
print("Difference, bp:",
      10000 * (4730 / 26317 - 4095 / 22900))


# FX guide record: reproduce supplied coding, then numeric-only cases.
track = dataset("C08", "c08_guide_track_record.csv")
track = track.dropna(subset=["printed"])
errors = track.printed - track.guided_num
print("\nSupplied FX track: n, >=guide, mean error, sample SD:",
      len(track), int((errors >= 0).sum()),
      errors.mean(), errors.std(ddof=1))

numeric_pairs = []
indexed = driver.set_index("quarter")
for target in ("1Q23", "1Q25"):
    rows = ledger[ledger.target_period.eq(target)]
    reported = rows[
        rows.metric.eq("revenue_yoy_pct")
        & rows.guide_type.eq("range")
        & rows.value_mid.notna()
    ].value_mid.iloc[0]
    exfx = rows[
        rows.metric.eq("revenue_yoy_exfx_pct")
        & rows.guide_type.eq("range")
        & rows.value_mid.notna()
    ].value_mid.iloc[0]
    numeric_pairs.append(
        (target, reported - exfx, indexed.loc[target, "fx_pts"])
    )

# Explicit +3 guidance transcribed from the 4Q25 and 1Q26 letters.
# Kept separate from qualitative phrases assigned numerical values.
for target in ("1Q26", "2Q26"):
    numeric_pairs.append(
        (target, 3.0, indexed.loc[target, "fx_pts"])
    )

numeric = pd.DataFrame(
    numeric_pairs, columns=["target", "guided_fx", "printed_fx"]
)
numeric["error"] = numeric.printed_fx - numeric.guided_fx
show("Explicit numeric FX guide/print pairs", numeric)

for year in (23, 24):
    sub = numeric[numeric.target.str[-2:].astype(int) >= year]
    print("Numeric FX printed >= guide, starting year", year,
          int((sub.error >= 0).sum()), "/", len(sub))


# PIT model attribution, including half-point interval scoring.
pit = read_csv(
    "data/processed/forecast_methods/fx_lag_v2/"
    "09b_pit_expanding_window_forecasts.csv"
)
for spec in ("H2_phi_adrfx", "H2b_phi_basket"):
    for window in ("in_W1", "in_W2"):
        mask = pit[window].astype(str).str.lower().eq("true")
        sub = pit[
            pit.spec.eq(spec) & mask & pit.actual.notna()
        ]
        err = sub.point - sub.actual
        interval_err = (err.abs() - 0.5).clip(lower=0)
        print("PIT", spec, window, "n", len(sub),
              "RMSE", math.sqrt((err ** 2).mean()),
              "interval RMSE",
              math.sqrt((interval_err ** 2).mean()))

show("Live H2/H2b points",
     pit[
         pit.spec.isin(["H2_phi_adrfx", "H2b_phi_basket"])
         & pit.target_quarter.eq("3Q26")
     ][["spec", "guide_date", "point", "sigma"]])


# Analytic triangular rounding kernel for two printed integer rates.
# E[(F-a)+] for F ~ Normal(mu, sd).
NORMAL = NormalDist()


def positive_part(mu, sd, boundary):
    z = (mu - boundary) / sd
    density = math.exp(-z * z / 2) / math.sqrt(2 * math.pi)
    return (mu - boundary) * NORMAL.cdf(z) + sd * density


def prob_integer_ge(mu, sd, integer):
    return (
        positive_part(mu, sd, integer - 1)
        - positive_part(mu, sd, integer)
    )


def fx_vector(mu, sd):
    a = prob_integer_ge(mu, sd, 3)
    b = prob_integer_ge(mu, sd, 2) - a
    return [a, b, 1 - a - b]


spec_points = dataset("C08", "c08_spec_points.csv")
means = [
    3.0, spec_points.point.iloc[1], 2.05,
    spec_points.point.iloc[7], spec_points.point.iloc[8],
]
sds = [0.6, 0.6, 0.7, 0.7, 0.7]
weights = [0.38, 0.20, 0.27, 0.12, 0.03]


def original_fx_mix(component_means):
    return [
        0.98 * sum(
            w * fx_vector(mu, sd)[i]
            for mu, sd, w in zip(component_means, sds, weights)
        )
        for i in range(3)
    ] + [0.02]


print("\nC08 analytic original mixture:", original_fx_mix(means))
changed = means.copy()
changed[0] = 3.5
print("Corrected centre-only sensitivity:",
      original_fx_mix(changed))

changed = means.copy()
changed[3] += 0.45 * 0.8
changed[4] += 0.56 * 0.8
print("Corrected +0.8-point basket sensitivity:",
      original_fx_mix(changed))

for cutoff in (0, -1):
    p = 0.98 * sum(
        w * (1 - prob_integer_ge(mu, sd, cutoff + 1))
        for mu, sd, w in zip(means, sds, weights)
    )
    print(f"C08 P(integer <= {cutoff}):", p)

sensitivity = dataset("C08", "c08_sensitivity.csv")
sensitivity["vector_sum"] = sensitivity[
    ["a_ge3", "b_eq2", "c_le1", "d_not_stated"]
].sum(axis=1)
show("Invalid saved C08 sensitivity vectors",
     sensitivity[
         (sensitivity.vector_sum - 1).abs() > 0.002
     ])


# C11 total-probability check and saved external anchors.
bands = dataset("C11", "c11_by_gbv_band.csv")
bands = bands.dropna(subset=["mass"])
print("\nC11 band mass:", bands.mass.sum())
print("C11 integrated probability:",
      (bands.mass * bands.p_yes_given_band).sum())
print("C11 stated final linear pool:",
      0.45 * 0.77 + 0.25 * 0.18 + 0.30 * 0.45)

register = read_csv(
    "data/processed/forecast_methods/L0/L0_vintage_register.csv"
)
show("C11 L0 revenue anchor",
     register[
         register.register_id.eq(
             "CU-2026Q3-revenue-Yahoo-20260913T1520Z"
         )
     ][["value", "vendor", "as_of_timestamp", "n_estimates"]])

street = read_csv(
    "data/processed/reverse_dcf/E/E_street_distribution_vs_team.csv"
)
show("C11 MODL GBV anchor",
     street[
         street.quarter.eq("3Q26") & street.metric.eq("gbv_musd")
     ][["street_mean", "n_estimates", "source"]])

market_file = (
    QUESTIONS / SLUGS["C11"] / "sources"
    / "kalshi_markets_KXABNB_open_20260917T031010Z.json"
)
markets = json.loads(
    market_file.read_text(encoding="utf-8")
)["markets"]
fields = [
    "floor_strike", "yes_bid_dollars", "yes_ask_dollars",
    "volume_fp", "volume_24h_fp", "liquidity_dollars",
]
show("Saved Kalshi activity fields",
     pd.DataFrame([{k: m.get(k) for k in fields} for m in markets]))

midpoints = {
    m["floor_strike"]: (
        float(m["yes_bid_dollars"]) + float(m["yes_ask_dollars"])
    ) / 2
    for m in markets
}
median_nights = 148 + 2 * (
    midpoints[148000000] - 0.5
) / (
    midpoints[148000000] - midpoints[150000000]
)
print("Interpolated Kalshi median, million nights:", median_nights)


# C12 historical frequency, seasonal norms, threshold and route pool.
panel = read_csv("data/processed/overnight/02_kpi_panel_quarterly.csv")
panel = panel.sort_values("quarter", key=quarter_order).reset_index(drop=True)
uf = panel[
    ["quarter", "unearned_fees_musd", "revenue_musd", "gbv_musd"]
].copy()
uf["yoy"] = 100 * uf.unearned_fees_musd.pct_change(4)
uf["sequential"] = 100 * uf.unearned_fees_musd.pct_change()
uf["norm"] = uf.unearned_fees_musd / uf.revenue_musd.shift(-1)

for year in (23, 24):
    sub = uf[
        (uf.quarter.str[-2:].astype(int) >= year)
        & uf.yoy.notna()
    ]
    print("UF <=-3%, starting year", year,
          int((sub.yoy <= -3).sum()), "/", len(sub))

q3 = uf[uf.quarter.isin(["3Q23", "3Q24", "3Q25"])]
show("C12 Q3 historical observations",
     q3[["quarter", "unearned_fees_musd", "yoy", "sequential", "norm"]])
print("Q3 sequential mean / sample SD:",
      q3.sequential.mean(), q3.sequential.std(ddof=1))
norm = q3[q3.quarter.isin(["3Q23", "3Q24"])].norm.mean()
print("Pre-RNPL norm:", norm)
print("Norm including RNPL launch quarter:", q3.norm.mean())

base = float(
    uf.set_index("quarter").loc["3Q25", "unearned_fees_musd"]
)
threshold = 0.97 * base
print("Dollar threshold:", threshold)
print("Route A central unpaid-share threshold:",
      3.5 + (13.2 + 1 + 3) / 1.16)
print("Route C central unpaid-share threshold:",
      100 * (1 - threshold / (0.661 * 3178 * 1.015)))

routes = dataset("C12", "c12_routes.csv")
print("C12 weighted probability from rounded components:",
      sum(w * p for w, p in zip(
          [0.45, 0.30, 0.25], routes.p_yes.iloc[:3]
      )))


# Auditor comparison forecasts: explicit judgments, not fitted priors.
own_fx = [
    0.98 * (
        0.50 * fx_vector(3.0, 1.0)[i]
        + 0.25 * fx_vector(1.8527, 0.9936)[i]
        + 0.25 * fx_vector(2.9960, 1.3155)[i]
    )
    for i in range(3)
] + [0.02]
print("\nAuditor C08:", own_fx)

draws = 150000
rng = random.Random(20260917)
gbv_base = 133.6 * 171.29
gbv_mean = gbv_base * 1.095 * 1.033
gbv_sd = gbv_base * math.sqrt(
    1.095 ** 2 * 0.013 ** 2
    + 1.033 ** 2 * 0.016 ** 2
    + 0.016 ** 2 * 0.013 ** 2
)
cuts = [25600, 25900, 26200, 26500, 26800]
counts, successes = [0] * 6, [0] * 6
total_yes = direct_yes = 0

for _ in range(draws):
    gbv = gbv_base * (1 + rng.gauss(0.095, 0.016))
    gbv *= 1 + rng.gauss(0.033, 0.013)
    cushion = cushion_mean + 0.005 * (
        0.5 * (gbv - gbv_mean) / gbv_sd
        + math.sqrt(0.75) * rng.gauss(0, 1)
    )
    revenue = 4730 * (1 + cushion)
    if rng.random() < 0.05:
        revenue = 4690 * (1 + rng.gauss(-0.003, 0.004))
    direct = revenue / gbv >= 0.181
    language = rng.gauss(17.9, 0.35) >= 18.1
    outcome = direct if rng.random() < 0.70 else language
    band = sum(gbv >= cut for cut in cuts)
    counts[band] += 1
    successes[band] += outcome
    total_yes += outcome
    direct_yes += direct

print("Auditor C11 direct route / final:",
      direct_yes / draws, total_yes / draws)
print("Auditor C11 bands: mass, conditional probability")
for count, success in zip(counts, successes):
    print(count / draws, success / count)

bridge = read_csv(
    "data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv"
)
revenue_q4 = float(
    bridge.loc[bridge.quarter.eq("4Q26"), "revenue_musd"].iloc[0]
)

for unpaid_mean in (0.15, 0.165, 0.18):
    rng = random.Random(12)
    balances = []
    for _ in range(draws):
        balance = rng.gauss(norm, 0.008)
        balance *= rng.gauss(revenue_q4, 60)
        balance *= 1 - rng.gauss(unpaid_mean, 0.04)
        balance *= 1 + rng.gauss(0.01, 0.01)
        balance *= 1 + rng.gauss(0, 0.005)
        balances.append(balance)
    probability = sum(v <= threshold for v in balances) / draws
    median = sorted(balances)[draws // 2]
    print("Auditor C12: unpaid mean, P, median UF:",
          unpaid_mean, probability, median)
```