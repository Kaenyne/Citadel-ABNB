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
