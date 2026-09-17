"""A04 read-only reproduction.
Run from repo root: python docs/pitch-forecasts/audits/A04-reproduce.py
Requires stdlib + pandas. No network or file writes.
"""
from pathlib import Path
import gzip
import html
import json
import math
import random
import re
import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
SLUGS = [
    "bundle-attribution-quantified",
    "rnpl-gbv-share-disclosed",
    "rnpl-negative-effect-acknowledged",
]
A, B, C = [Q / s for s in SLUGS]


def plain(path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    s = raw.decode("utf-8", errors="replace")
    s = re.sub(r"<(script|style)\b.*?</\1>", " ", s, flags=re.I | re.S)
    return re.sub(
        r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))
    )


def folded(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def rate_table(matrix):
    rows = []
    quarters = list(matrix.columns)
    windows = [
        ("All", 0),
        ("W1 target>=1Q23", quarters.index("1Q23")),
        ("W2 target>=1Q24", quarters.index("1Q24")),
    ]
    for label, start in windows:
        k = n = g = h = 0
        for values in matrix.ne("--").to_numpy().tolist():
            for t in range(max(1, start), len(values)):
                if values[t - 1]:
                    n += 1
                    k += int(values[t])
            for t in range(max(2, start), len(values)):
                if values[t - 2] and not values[t - 1]:
                    h += 1
                    g += int(values[t])
        rows.append([
            label, k, n, k / n if n else None,
            g, h, g / h if h else None,
        ])
    return pd.DataFrame(rows, columns=[
        "window", "continued", "eligible", "continuation",
        "returned", "gaps", "return_rate",
    ])


matrix = pd.read_csv(
    A / "datasets/metric_persistence_matrix_4Q20-2Q26.csv"
).set_index("metric")
print("MATRIX SHAPE", matrix.shape)
print(rate_table(matrix).to_string(index=False))

gaps = pd.read_csv(A / "datasets/metric_gap_events.csv")
returned = gaps.returned_next_quarter.astype(str).str.lower().eq("true")
print("SAVED GAP LEDGER", int(returned.sum()), "/", len(gaps))
unflattering = [
    "cross-border share %",
    "long-term stays share %",
    "urban/high-density share %",
    "active listings growth %",
    "1BR vs hotel price comparison",
]
mask = gaps.metric.isin(unflattering)
print("POST-HOC FIVE-METRIC GROUP",
      int(returned[mask].sum()), "/", int(mask.sum()))
print("OTHER GAP EVENTS",
      int(returned[~mask].sum()), "/", int((~mask).sum()))

# Partial audit repairs; all other cells remain uncertified.
partial = matrix.copy()
partial.loc["cancellation rate %", ["1Q25", "3Q25"]] = "--"
partial.loc["Middle East conflict (pts)", "2Q26"] = "--"
print("THREE VERIFIED CELL REMOVALS")
print(rate_table(partial).to_string(index=False))

print("EXCLUDE THREE MIXED/INCORRECT SERIES; SENSITIVITY ONLY")
print(rate_table(matrix.drop(index=[
    "Guest Favorites share",
    "cancellation rate %",
    "Middle East conflict (pts)",
])).to_string(index=False))

rnpl = matrix.loc[
    ["RNPL/bundle contribution (pts)", "RNPL GBV share"],
    ["3Q25", "4Q25", "1Q26", "2Q26"],
]
print("FOUR POST-LAUNCH PRINTS\n", rnpl.to_string())
for name in rnpl.index:
    print(name, "disclosed", int(rnpl.loc[name].ne("--").sum()), "/4")
print("BUNDLE RETURN-AFTER-GAP: completed n=0")
print("GBV SHARE CONTINUATION: 1/1, 1Q26 -> 2Q26")

ledger = pd.read_csv(
    ROOT / "data/processed/overnight2/D/rnpl_statement_ledger.csv"
)
cache, failed = {}, []
checked = 0
for _, row in ledger[ledger.source_file.notna()].iterrows():
    path = ROOT / row.source_file
    if path not in cache:
        cache[path] = folded(plain(path))
    checked += 1
    if folded(str(row.quote)) not in cache[path]:
        failed.append(row.statement_id)
print("RNPL LEDGER", len(ledger), "rows;",
      checked, "local quote checks; failed", failed)
print("BUNDLE NUMERIC DISCLOSURES\n",
      ledger[ledger.statement_id.isin(["D014", "D032"])][
          ["statement_id", "date", "period_referenced", "quantity"]
      ].to_string(index=False))

guide = pd.read_csv(
    ROOT / "data/processed/overnight/02_guidance_ledger.csv"
)
rnpl_rows = guide.fillna("").astype(str).apply(
    lambda s: s.str.contains(
        r"RNPL|Reserve Now|Pay Later", case=False
    ).any(),
    axis=1,
)
print("GUIDANCE LEDGER", guide.shape,
      "RNPL ROWS", int(rnpl_rows.sum()))

declines = pd.read_csv(
    ROOT / "data/processed/abnb_declined_to_quantify.csv"
)
print("DECLINES", len(declines), "2Q26",
      int(declines.quarter.eq("2026Q2").sum()))
print(declines[
    declines.asked.str.contains("Reserve Now", case=False, na=False)
].to_string(index=False))

# Reproduces author labels, not an endorsement of the resolution rule.
prior = pd.read_csv(
    C / "datasets/prior_prints_scored_under_c07_criteria.csv"
)
strict, generous, events = set(), set(), set()
for _, row in prior.iterrows():
    qs = set(re.findall(r"[1-4]Q\d{2}", str(row["print"])))
    events |= qs
    if str(row.strict_reading).startswith("Yes"):
        strict |= qs
    if str(row.generous_reading).startswith("Yes"):
        generous |= qs
print("C07 AUTHOR LABELS", len(strict), "/", len(events),
      "generous", len(generous), "/", len(events),
      "Laplace", (len(strict) + 1) / (len(events) + 2))

kpi = pd.read_csv(
    ROOT / "data/processed/abnb_driver_history_quarterly.csv"
)
print("CURRENT KPI VALUES\n",
      kpi[kpi.quarter.isin(["3Q25", "1Q26", "2Q26"])][
          ["quarter", "nights_m", "nights_m_yoy_pct"]
      ].to_string(index=False))
print("2023-25 GBV/TAKE-RATE MEANS\n",
      kpi[kpi.year.between(2023, 2025)].groupby("q")[
          ["gbv_b", "take_rate_calc_pct"]
      ].mean().to_string())

reaction = pd.read_csv(
    ROOT / "data/processed/abnb_guidance_reaction_panel.csv"
)
print("2Q26 REACTION\n",
      reaction[reaction.quarter.eq("2Q26")][
          ["print_date", "ret_1d", "exc_1d"]
      ].to_string(index=False))
reaction2 = pd.read_csv(
    ROOT / "data/processed/abnb_earnings_reactions.csv"
)
print(reaction2[reaction2.quarter.eq("2026Q2")][
    ["reaction_date", "abnb_1d_pct", "excess_1d_pct"]
].to_string(index=False))


def share_sim(exp_mean=1.4, season=True, n=200000):
    rng = random.Random(7)
    counts = [0, 0, 0]
    for _ in range(n):
        s = rng.uniform(21, 23) + rng.uniform(0, 2)
        s += min(6, rng.expovariate(1 / exp_mean))
        # Draw even when disabled, preserving RNG alignment.
        seasonal = rng.uniform(-2, 0)
        s += seasonal if season else 0
        counts[0 if s >= 24.5 else 1 if s >= 20.5 else 2] += 1
    return [x / n for x in counts]


def wording(probs, disclose=0.70):
    high, middle, low = probs
    return [
        disclose * 0.9 * high,
        disclose * 0.45 * middle,
        disclose * (0.1 * high + 0.55 * middle + low),
        1 - disclose,
    ]


for name, mean, seasonal in [
    ("base", 1.4, True),
    ("large", 4, True),
    ("no season", 1.4, False),
]:
    probs = share_sim(mean, seasonal)
    print("SHARE SIM", name, probs, "wording", wording(probs))

mechanical = pd.read_csv(
    A / "datasets/bundle_3q26_mechanical_contribution.csv"
)
legs = mechanical[
    mechanical.in_3Q26_yoy_window.fillna("").str.startswith("yes")
]
legs = legs[~legs.component.str.startswith("Cancellation-propensity")]
lo = legs.points_of_total_nights_low.sum()
hi = legs.points_of_total_nights_high.sum()
print("AUTHOR BUNDLE", lo, hi, "net", lo - 0.93, hi - 0.15)
print("PAIRED EX-NA TOTAL", 0.70 + 1.05, 0.88 + 0.87)
print("PAIRED GROSS",
      0.66 + 1.75 + 0.10 + 0.30,
      0.66 + 1.75 + 0.30 + 0.35)
print("PAIRED NET",
      0.66 + 1.75 + 0.10 + 0.30 - 0.93,
      0.66 + 1.75 + 0.30 + 0.35 - 0.15)

cohort = pd.read_csv(
    ROOT / "data/processed/overnight2/D/D1_cohort_matrix_cancellation.csv"
)
prior_q = cohort.booking_quarter.isin(
    ["1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
)
print("EARLIER-COHORT Q3 CANCELLATION SHARE",
      cohort.loc[prior_q, "3Q26"].sum() / cohort["3Q26"].sum())

module = pd.read_csv(
    ROOT / "data/processed/rnpl_short_audit/rnpl_nights_module.csv"
)
print("Q3 MODULE\n", module[module.quarter.eq("3Q26")][
    ["scenario", "m4_propensity_drag_pts", "nights_yoy_pct"]
].to_string(index=False))

bs = pd.read_csv(
    ROOT / "data/processed/rnpl_short_audit/verify_bs_uf_only_solve.csv"
)
print("UF STOCK SOLVE\n", bs[
    bs.quarter.eq("2Q26")
    & bs.B.isin([1.0, 1.1])
    & bs.norm.eq("note baseline: next-Q rev, 2023+2024+1H25")
].to_string(index=False))

snap = json.loads((
    A / "sources/kalshi_KXABNB-26NOVNEB_20260917T025351Z.json"
).read_text())
markets = snap["markets"]
for row in sorted(markets, key=lambda x: x["floor_strike"]):
    mid = (
        float(row["yes_bid_dollars"]) + float(row["yes_ask_dollars"])
    ) / 2
    print("KALSHI", row["floor_strike"], mid,
          row["volume_fp"], row["open_interest_fp"],
          row["volume_24h_fp"], row["updated_time"])
print("KALSHI TOTAL VOLUME/OI", *[
    sum(float(row[key]) for row in markets)
    for key in ("volume_fp", "open_interest_fp")
])

tail = 0.5 * math.erfc((10 - 9.5) / (1.48 * math.sqrt(2)))
states = [tail, 1 - 2 * tail, tail]
print("TEAM NORMAL STATES >=10, 9-10, <9", states)
print("C05 AUTHOR DECOMPOSITION",
      0.42 * 0.15 + 0.30 * 0.28 + 0.28 * 0.42)
print("C05 TEAM-ONLY SAME CONDITIONALS",
      sum(x * y for x, y in zip(states, [0.15, 0.28, 0.42])))
print("C07 S FROM STATED INPUTS",
      0.28 * 0.6, "P", 0.10 + 0.55 * (0.28 * 0.6))
print("C07 STRONG-PRINT SENSITIVITY", 0.05 * 0.65 + 0.95 * 0.10)
print("C05 LOG-SCORE CHANGE IF d", math.log(0.70 / 0.73))
print("C06 STATED 3:1 BLEND", [
    (3 * x + y) / 4
    for x, y in zip(
        [0.14, 0.24, 0.32, 0.30],
        [0.16, 0.28, 0.38, 0.18],
    )
])
print("C06 80% DISCLOSURE SENSITIVITY", wording(share_sim(), 0.80))

saved = {}
related = [
    "risk-july-rnpl-expansion-offsets-lap",
    "risk-q3-nights-meets-guide",
]
for slug in SLUGS + related:
    path = Q / slug / "forecasts/2026-09-17-forecast.json"
    if not path.exists():
        continue
    obj = json.loads(path.read_text())
    saved[obj["question_id"]] = obj
    print("FINAL", obj["question_id"], obj["final"])
    if "vector" in obj["final"]:
        base = dict(zip("abcd", obj["final"]["vector"].values()))
        print("FINAL SUM", sum(base.values()))
        for sensitivity in obj["sensitivity"]:
            revised = dict(base)
            revised.update(sensitivity["moves_to"])
            if not math.isclose(sum(revised.values()), 1):
                print("INVALID SENSITIVITY SUM",
                      sensitivity["assumption"], sum(revised.values()))

if all(q in saved for q in ["R03", "R01", "C06"]):
    cap = min(
        saved["R01"]["final"]["p"],
        list(saved["C06"]["final"]["vector"].values())[0],
    )
    print("R03 CAP", saved["R03"]["final"]["p"], "<=", cap)

# Judgmental audit alternatives; not empirical frequencies or market anchors.
quantify = sum(
    x * y for x, y in zip(states, [0.20, 0.30, 0.45])
)
print("AUDIT C05", [
    quantify * 0.31, quantify * 0.44,
    quantify * 0.25, 1 - quantify,
])
print("AUDIT C06 NO-SEASON BENCHMARK", wording(share_sim(1.4, False)))
print("AUDIT C07", 0.15 * 0.70 + 0.25 * 0.40 + 0.60 * 0.075)
