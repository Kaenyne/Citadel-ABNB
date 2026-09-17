"""A15 read-only reproduction (B04, B05, B06, B07).
Run from the repository root: python -B docs/pitch-forecasts/audits/A15-reproduce.py
Requires stdlib + pandas only (no numpy/scipy). Writes nothing; no network.
"""
from pathlib import Path
from statistics import NormalDist
import glob
import html
import json
import math
import os
import re

import pandas as pd

ROOT = Path.cwd()
Q = ROOT / "docs/pitch-forecasts/questions"
N = NormalDist()


def head(t):
    print("\n" + "=" * 12 + " " + t + " " + "=" * 12)


def pct(a, b):
    return 100.0 * (a / b - 1.0)


# ------------------------------------------------------------------ B07
head("B07 NTTO overseas: the cache and the claims ledger")

raw = pd.read_csv(ROOT / "data/processed/q3nowcast/G/raw/ntto_arrivals_monthly.csv")
raw["p"] = pd.PeriodIndex(raw.month, freq="M")
S = raw[raw.region == "OVERSEAS"].set_index("p").arrivals.sort_index()


def P(s):
    return pd.Period(s, "M")


def qsum(series, year, q):
    m = {1: 1, 2: 4, 3: 7, 4: 10}[q]
    return series[P(f"{year}-{m:02d}"):P(f"{year}-{m + 2:02d}")].sum()


yoy = (S / S.shift(12) - 1) * 100
print("2026 monthly y/y:", {str(k): round(v, 2)
                            for k, v in yoy[yoy.index >= P("2026-01")].items()})
print("2025 monthly y/y:", {str(k): round(v, 2)
                            for k, v in yoy[(yoy.index >= P("2025-07")) &
                                            (yoy.index <= P("2025-12"))].items()})
print("  -> Sep 2025 is the WEAKEST month of 3Q25, i.e. the easiest 3Q26 comp")

for lab, y, q in [("3Q25", 2025, 3), ("4Q25", 2025, 4),
                  ("1Q26", 2026, 1), ("2Q26", 2026, 2)]:
    yy, qq = (y, q) if q else (y, q)
    print(lab, "y/y %:", round(pct(qsum(S, yy, qq), qsum(S, yy - 1, qq)), 3))

print("4Q25 two-year stack %:", round(pct(qsum(S, 2025, 4), qsum(S, 2023, 4)), 3),
      "| 4Q24 y/y %:", round(pct(qsum(S, 2024, 4), qsum(S, 2023, 4)), 3))
ytd = S[P("2026-01"):P("2026-07")].sum(), S[P("2025-01"):P("2025-07")].sum()
print("Jan-Jul 2026 vs 2025 (m):", round(ytd[0] / 1e6, 3), round(ytd[1] / 1e6, 3),
      "y/y %:", round(pct(*ytd), 3))
stack = (S / S.shift(24) - 1) * 100
print("2026 two-year stacks:", {str(k): round(v, 2)
                                for k, v in stack[stack.index >= P("2026-01")].items()})

# External cross-validation of the cache (figures quoted in the saved search notes)
print("cache vs published: Jan 2026", round(yoy[P("2026-01")], 2), "(pub -4.2)")
print("cache vs published: Jan-May 2026",
      round(pct(S[P("2026-01"):P("2026-05")].sum(),
                S[P("2025-01"):P("2025-05")].sum()), 2), "(pub -4.8)")
print("cache vs published: FY2025 overseas level (m)",
      round(S[P("2025-01"):P("2025-12")].sum() / 1e6, 2), "(pub 34.3)")
tot = raw[raw.region == "TOTAL ALL COUNTRIES"].set_index("p").arrivals.sort_index()
print("cache vs published: FY2025 total international y/y %",
      round(pct(tot[P("2025-01"):P("2025-12")].sum(),
                tot[P("2024-01"):P("2024-12")].sum()), 2), "(pub -5.5)")

head("B07 persistence table (claim 5) and the saved dataset")
rows = []
for y in list(range(2004, 2020)) + [2024, 2025]:
    q2 = pct(qsum(S, y, 2), qsum(S, y - 1, 2))
    q3 = pct(qsum(S, y, 3), qsum(S, y - 1, 3))
    q4 = pct(qsum(S, y, 4), qsum(S, y - 1, 4))
    jul = pct(S[P(f"{y}-07")], S[P(f"{y - 1}-07")])
    rows.append(dict(year=y, q2=q2, jul=jul, q3=q3, q4=q4,
                     d_q4_jul=q4 - jul, d_q4_q2=q4 - q2, d_q4_q3=q4 - q3))
mine = pd.DataFrame(rows).round(2).set_index("year")
saved = pd.read_csv(Q / "bonus-us-inbound-falls/datasets/ntto_q4_persistence.csv"
                    ).set_index("year")
print("max abs diff vs saved dataset:",
      (mine - saved[mine.columns]).abs().max().max())
for c in ["d_q4_q3", "d_q4_jul", "d_q4_q2"]:
    s = mine[c]
    print(c, "n", len(s), "mean", round(s.mean(), 2), "sd", round(s.std(ddof=1), 2),
          "MAD", round((s - s.median()).abs().median(), 2))

head("B07 recomputed centres and probabilities")
st26 = S[P("2026-07")] / S[P("2024-07")] - 1
q3_hold = (S[P("2026-07")] + S[P("2024-08")] * (1 + st26) +
           S[P("2024-09")] * (1 + st26))
q3_hold = pct(q3_hold, qsum(S, 2025, 3))
q4_hold = pct(qsum(S, 2024, 4) * (1 + st26), qsum(S, 2025, 4))
print("July 2026 stack %:", round(100 * st26, 2))
print("3Q26 at a held stack %:", round(q3_hold, 2),
      "(log uses -6.5, which needs a stack of about -11.0)")
print("4Q26 at a held stack %:", round(q4_hold, 2), "(log's persist scenario: -5.6)")

REG = ["WESTERN EUROPE", "ASIA", "SOUTH AMERICA", "CENTRAL AMERICA", "CARIBBEAN",
       "OCEANIA", "EASTERN EUROPE", "MIDDLE EAST", "AFRICA"]
piv = raw.pivot_table(index="p", columns="region", values="arrivals")
w4 = piv.loc[P("2025-10"):P("2025-12"), REG].sum()
print("4Q25 regional shares %:",
      {k: round(v, 2) for k, v in (100 * w4 / w4.sum()).items()})
jul_yoy = (piv.loc[P("2026-07"), REG] / piv.loc[P("2025-07"), REG] - 1) * 100
print("Jul 2026 regional y/y %:", {k: round(v, 2) for k, v in jul_yoy.items()})
print("4Q25-share-weighted Jul y/y %:",
      round(((w4 / w4.sum()) * jul_yoy).sum(), 2))
rs = piv.loc[P("2026-07"), REG] / piv.loc[P("2024-07"), REG]
q4r = (piv.loc[P("2024-10"):P("2024-12"), REG].sum() * rs).sum()
print("regional constant-stack 4Q26 y/y %:",
      round(pct(q4r, piv.loc[P("2025-10"):P("2025-12"), REG].sum().sum()), 2))

print("log base-rate branches:",
      [round(N.cdf((-5 + 7.0) / s), 4) for s in (4.0, 3.6)],
      round(N.cdf((-5 + 8.0) / 5.0), 4), round(N.cdf((-5 + 5.0) / 4.0), 4))
mix = sum(w * N.cdf((-5 - mu) / 2.0)
          for w, mu in [(0.55, -5.6), (0.30, -3.5), (0.15, -8.2)])
print("log decomposition mixture:", round(mix, 4))
for mu, sd in [(-6.24, 4.04), (-6.8, 4.2), (-7.08, 4.2), (-7.53, 4.2)]:
    print(f"  auditor centre {mu} sd {sd} -> P(<=-5) {N.cdf((-5 - mu) / sd):.3f}")

# ------------------------------------------------------------------ B06
head("B06 geopolitical base rate: dataset, letters, reaction")
g = pd.read_csv(Q / "bonus-geopolitical-headwind-cited/datasets/"
                    "letter_geopolitical_base_rate_4Q20-2Q26.csv")
active = g[g.active_conflict.str.lower() != "none"]
active = active[~active.active_conflict.str.contains("none named|tariffs", case=False)]
yes = g[g.resolves_yes_under_B06.str.startswith(("named", "quantified"))]
print("prints:", len(g), "| active-conflict prints:", len(active),
      "| coded Yes:", list(yes["print"]))
print("log coding 3/8 -> Laplace", round(4 / 10, 3),
      "| strict 1/8 (1Q26 only) ->", round(2 / 10, 3),
      "| convention-2 coding 2/8 (3Q23,1Q26) ->", round(3 / 10, 3),
      "| unconditional 3/23 ->", round(3 / 23, 3))

pat = re.compile(r"Ukraine|Middle East|geopolit|conflict", re.I)
found = {}
for f in sorted(glob.glob(str(ROOT / "data/raw/letters/*.htm"))):
    q = os.path.basename(f)[:4]
    t = re.sub(r"\s+", " ", html.unescape(
        re.sub(r"<[^>]+>", " ", open(f, encoding="utf-8", errors="ignore").read())))
    found[q] = len(pat.findall(t))
    for key in ["Risks to nights booked in Q2 2022",
                "closely monitoring macroeconomic trends and geopolitical conflicts",
                "roughly 100bps headwind related to the conflict"]:
        if key in t:
            i = t.index(key)
            print(f"  {q}: ...{t[i:i + 150]}...")
print("letters with any geopolitical hit:",
      {k: v for k, v in found.items() if v})

r = pd.read_csv(ROOT / "data/processed/abnb_earnings_reactions.csv")
r1 = r[r.quarter == "2026Q1"].iloc[0]
print("1Q26 print: raw 1d", r1.abnb_1d_pct, "| QQQ 1d", r1.qqq_1d_pct,
      "| EXCESS 1d", r1.excess_1d_pct, "<- sign flips on the excess convention")

print("B06 decomposition replay:", round(0.30 * 0.75 + 0.70 * 0.15, 4))
print("B06 FY26 margin row: 0.7*0.59*0.25 =", round(0.7 * 0.59 * 0.25, 3),
      "| two-quarter weight =", round(0.7 * 0.59 * 0.5, 3), "| log prints -0.15")
print("B06 EV:", round(0.35 * -1.5, 3))

# ------------------------------------------------------------------ B05
head("B05 regulation: gate, event count, decomposition")
ev = pd.read_csv(Q / "bonus-eu-regulation-hit/datasets/qualifying_events_trailing_24m.csv")
ev["year"] = ev.date.str.extract(r"(\d{4})").astype(int)
qual = ev[ev.qualifies_under_B05_convention.str.startswith(("yes", "marginal"))]
print("rows:", len(ev), "| qualifying (clear+marginal):", len(qual))
print(qual[["measure", "date", "qualifies_under_B05_convention"]].to_string(index=False))
print("events by calendar year:", ev.groupby("year").size().to_dict())
print("qualifying by year:", qual.groupby("year").size().to_dict(),
      "<- none dated 2026")

win = 147 / (365.25 / 12)
print("window months:", round(win, 4))
for lab, n, months in [("24m, 6 events (log)", 6, 24), ("24m, strict 4", 4, 24),
                       ("24m, lenient 13", 13, 24),
                       ("trailing 18m, 3 events", 3, 18),
                       ("trailing 12m, 1 event", 1, 12)]:
    lam = n * win / months
    print(f"  {lab}: lambda {lam:.3f} -> P(>=1) {1 - math.exp(-lam):.3f}")

routes = [0.18, 0.15, 0.30, 0.12, 0.12, 0.10, 0.05, 0.10, 0.01]
comp = 1.0
for p in routes:
    comp *= (1 - p)
print("decomposition complement:", round(comp, 5), "-> P", round(1 - comp, 5),
      "| log states complement 0.273 -> 0.73")

reg = pd.read_csv(ROOT / "data/processed/abnb_regulatory_events.csv").set_index("id")
claim5 = {"EU-AHA": 0.12, "ES-REMOVE": 0.35, "ES-REGIONS": 0.45, "PARIS-PRO": 0.30,
          "IT-NAT": 0.30, "GR-FREEZE": 0.70, "UK-ENG": 0.20, "IE-REG": 0.35,
          "PT-RETIGHT": 0.20, "NL-AMS": 0.30, "BCN-2028": 0.00}
print("claim 5 p27 check:",
      all(abs(reg.loc[k, "p27"] - v) < 1e-9 for k, v in claim5.items()))
print("register event bars (B05 needs mere enactment):")
for k in ["ES-REMOVE", "IE-REG", "UK-ENG", "IT-NAT"]:
    print("   ", k, "->", reg.loc[k, "event"][:95])
print("IT-NAT gates mention the 2026 budget law:",
      "budget law" in str(reg.loc["IT-NAT", "gates"]).lower(),
      "| present in the trailing-24m table:",
      ev.measure.str.contains("budget", case=False).any())

sc = pd.read_csv(Q / "bonus-eu-regulation-hit/datasets/"
                     "eurostat_country_shares_scaled_to_emea.csv").set_index("geo")
print("EMEA shares (scaled): FR ES IT DE EL PT PL HR AT NL IE =",
      [round(float(sc.loc[c, "emea_share_est_pct"]), 2)
       for c in ["FR", "ES", "IT", "DE", "EL", "PT", "PL", "HR", "AT", "NL", "IE"]])
inv = pd.read_csv(Q / "bonus-eu-regulation-hit/datasets/"
                      "regulatory_market_inventory.csv").set_index("market")
for m in ["Paris", "London", "Madrid", "Athens", "Barcelona",
          "Lisbon municipality", "Florence", "Amsterdam"]:
    print("  listings", m, int(inv.loc[m, "total"]))
print("Canaries / Spain INE:",
      round(100 * inv.loc["Canary Islands (INE)", "total"] /
            inv.loc["Spain (INE)", "total"], 2), "%")

panel = pd.read_csv(ROOT / "data/processed/overnight/10_regional_panel_quarterly.csv")
p2 = panel[panel.quarter == "2Q26"].iloc[0]
print("2Q26 EMEA nights share %:", p2.emea_nights_share_est_pct,
      "| EMEA revenue share %:", round(p2.emea_revenue_share_pct, 2))
print("gate is GBV-based: Paris 1.0/0.40 =", round(1.0 / 0.40, 2),
      "% of EMEA GBV; at a 1.4-1.5x city ADR premium that is",
      round(2.5 / 1.45, 2), "% of EMEA NIGHTS; Rome 1.5/1.45 =",
      round(1.5 / 1.45, 2), "% -> borderline")

big = pd.read_csv(ROOT / "data/processed/abnb_big_moves_7pct.csv")
print("moves >=7%:", len(big), big.driver.value_counts().to_dict())
prof = pd.read_csv(ROOT / "data/processed/abnb_regulatory_profile.csv")
med = prof[prof.percentile.astype(str) == "50"].iloc[0]
print("2027 median regulatory drag % of revenue:", round(med.revenue_loss_pct, 4),
      "| $/share:", round(med.value_per_share_usd, 4))
print("B05 EV level:", round(0.68 * -2.5, 3),
      "| EV on the surprise (1-P):", round((1 - 0.68) * -2.5, 3))

# ------------------------------------------------------------------ B04
head("B04 host churn: listings disclosure, RNPL precedent, churn panel")
apat = re.compile(r"active listings[^.]{0,200}", re.I)
for f in sorted(glob.glob(str(ROOT / "data/raw/letters/*.htm")),
                key=lambda f: (os.path.basename(f)[2:4], os.path.basename(f)[:2])):
    q = os.path.basename(f)[:4]
    if q[2:] < "23":
        continue
    t = re.sub(r"\s+", " ", html.unescape(
        re.sub(r"<[^>]+>", " ", open(f, encoding="utf-8", errors="ignore").read())))
    hits = [m.group(0) for m in apat.finditer(t)
            if re.search(r"\bgrew\b|\bgrowth\b|\bin-?line\b|million", m.group(0), re.I)
            and "expectations regarding" not in m.group(0)]
    print(q, "->", (hits[0][:110] if hits else "NO growth/level sentence"))

led = pd.read_csv(ROOT / "data/processed/overnight2/D/rnpl_statement_ledger.csv")
for sid in ["D006", "D009", "D017", "D018"]:
    row = led[led.statement_id == sid].iloc[0]
    print(sid, row.date, row.speaker, "|", str(row.quote)[:150])
print("-> 'management has never attributed a negative to its own product (0/23)' "
      "is false; at least 2 prints (3Q25, 4Q25) do, and 4Q25 quantifies it")

pool = pd.read_csv(ROOT / "data/processed/fee_churn_recent/pooled_rates.csv")
rev = pool[pool.cohort == "reviewed_str_homes"]
print("13-market reviewed-home disappearance:",
      [round(100 * x, 2) for x in rev.disappearance_rate],
      "(the >=6% trigger is set against the 4.20 reading)")
note = (ROOT / "research/notes/2026-09-07_fee-churn-recent-followup.md"
        ).read_text(encoding="utf-8", errors="ignore")
i = note.find("reviewed-home rates are")
snip = note[max(0, i - 190):i + 60].replace("\n", " ")
print("London (migrated 22 Jun):",
      snip.encode("ascii", "replace").decode("ascii"))

mig = pd.read_csv(ROOT / "data/processed/forecast_methods/fee_takerate/"
                         "03_migrated_share_path.csv").set_index("quarter")
print("migrated listing share: 3Q26", mig.loc["2026Q3", "listing_share_central"],
      "| 4Q26", mig.loc["2026Q4", "listing_share_central"])
sc4 = pd.read_csv(ROOT / "data/processed/fee_churn_history/catalyst_scenarios.csv")
m = sc4[(sc4.affected_booking_share == 0.5) & (sc4.demand_recapture == 0.5) &
        (sc4.relative_take_rate_change == 0)]
print("scenario grid (50% exposure, 50% recapture, no take-rate offset):",
      [(r.incremental_churn, round(100 * r.revenue_change, 2),
        round(r.revenue_change_usd_m, 1)) for r in m.itertuples()])

print("B04 base rate as written:", round(1 - 0.96 ** 2, 4),
      "| with 3 opportunities:", round(1 - 0.96 ** 3, 4),
      "| at 2/23 (Laplace 3/25) over 2 prints:", round(1 - (1 - 3 / 25) ** 2, 4))
print("B04 decomposition replay:", round(0.25 * 0.35 + 0.04 + 0.02 + 0.03, 4),
      "| without the convention-1 branch:", round(0.25 * 0.35 + 0.04 + 0.02, 4),
      "| with P(churn)=0.35:", round(0.35 * 0.35 + 0.04 + 0.02, 4))
print("B04 EV as booked:", round(0.15 * -6.4, 3),
      "| conditioned on the churn-bearing half:", round(0.15 * -3.2, 3))

# ------------------------------------------------------------------ coherence
head("Cross-question coherence and JSON checks")
for slug in ["bonus-host-churn-cited", "bonus-eu-regulation-hit",
             "bonus-geopolitical-headwind-cited", "bonus-us-inbound-falls",
             "q4-nights-bucket", "rnpl-negative-effect-acknowledged",
             "bonus-moderation-language",
             "risk-single-fee-take-rate-accretion-stated"]:
    d = json.loads((Q / slug / "forecasts/2026-09-17-forecast.json"
                    ).read_text(encoding="utf-8"))
    f = d["final"]
    if "p" in f:
        print(d["question_id"], slug, "rev", d["revision"], "p", f["p"], f["ci"])
    else:
        v = f["vector"]
        print(d["question_id"], slug, "rev", d["revision"],
              "sum", round(sum(v.values()), 6),
              "| P(bucket <= high single digits) =",
              round(sum(x for k, x in v.items()
                        if k.startswith(("(c)", "(d)"))), 4))
print("B04 quotes C07 at 0.20; C07 revision 2 is 0.27 -> stale analogue")
