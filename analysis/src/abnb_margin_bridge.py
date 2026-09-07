"""Margin bridge (FY2022 -> FY2025) and FY2026 / FY2027 margin scenarios for Airbnb.

Input: data/processed/abnb_quarterly_cost_stack_exsbc.csv (from abnb_exsbc_stack.py).

Bridge method. Adjusted EBITDA margin = 1 - sum(cash cost line / revenue) + (D&A + other add-backs) / revenue.
Each cash line ratio is written as (cost per night) / (revenue per night), and revenue per night = ADR x take rate.
The change in a line's ratio between two years is split into
  unit-cost effect     = (c1 - c0) / r0            (cost per night moved, revenue per night held at year 0)
  revenue-per-night    = c1 * (1/r1 - 1/r0)        (denominator moved, cost per night held at year 1)
The revenue-per-night term is then split log-linearly into take rate, FX, and ADR ex-FX using the FX impact on
revenue growth disclosed in the shareholder letters (reported vs ex-FX growth).

Scenario method. Bottom-up from nights, ADR (ex-FX and FX), take rate, cash cost per night by line and the
add-back ratio. Base case is calibrated to management's Q3 2026 and FY2026 outlook (Aug 6 2026 letter).

Outputs: data/processed/abnb_margin_bridge.csv, data/processed/abnb_margin_scenarios.csv
Run: python analysis/src/abnb_margin_bridge.py
"""
import csv, math, os, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
STACK = os.path.join(ROOT, "data", "processed", "abnb_quarterly_cost_stack_exsbc.csv")
LINES = ["cor", "ops", "pd", "sm", "ga"]
NAMES = {"cor": "Cost of revenue", "ops": "Operations & support", "pd": "Product development", "sm": "Sales & marketing", "ga": "G&A"}

# FX impact on reported revenue growth, percentage points, from the letters (reported minus ex-FX growth).
FX_PTS = {2022: -6.0, 2023: 1.0, 2024: 0.0, 2025: 0.0}


def load():
    rows = list(csv.DictReader(open(STACK)))
    for r in rows:
        for k, v in r.items():
            if k != "quarter":
                r[k] = float(v) if v not in ("", None) else None
        r["year"] = 2000 + int(r["quarter"][2:])
    return rows


def annual(rows, year):
    qs = [r for r in rows if r["year"] == year]
    if len(qs) != 4:
        return None
    a = {"year": year, "rev": sum(r["revenue_musd"] for r in qs), "nights": sum(r["nights_m"] for r in qs),
         "gbv": sum(r["gbv_busd"] for r in qs) * 1000, "adj": sum(r["adj_ebitda"] for r in qs),
         "addbacks": sum(r["da"] + r["other_addbacks"] - r["restr"] for r in qs)}  # restructuring is in costs and added back; net it here
    for k in LINES:
        a[k] = sum(r[f"{k}_cash"] for r in qs)
    a["adr"] = a["gbv"] / a["nights"]
    a["take"] = a["rev"] / a["gbv"]
    a["rpn"] = a["rev"] / a["nights"]
    a["margin"] = a["adj"] / a["rev"]
    a["margin_from_stack"] = 1 - sum(a[k] for k in LINES) / a["rev"] + a["addbacks"] / a["rev"]
    return a


def bridge(a0, a1):
    out = []
    r0, r1 = a0["rpn"], a1["rpn"]
    total_rpn_effect = 0.0
    for k in LINES:
        c0, c1 = a0[k] / a0["nights"], a1[k] / a1["nights"]
        unit = -(c1 - c0) / r0            # higher cost per night lowers margin
        rpn = -c1 * (1 / r1 - 1 / r0)     # higher revenue per night raises margin
        total_rpn_effect += rpn
        out.append({"component": f"{NAMES[k]}: cash cost per night ({c0:.2f} -> {c1:.2f} $/night)", "margin_pts": 100 * unit})
    # split the revenue-per-night effect: ln(rpn1/rpn0) = ln(take1/take0) + ln(adr1/adr0); ADR split into FX and ex-FX
    ln_take = math.log(a1["take"] / a0["take"])
    ln_adr = math.log(a1["adr"] / a0["adr"])
    fx_factor = 1.0
    for y in range(a0["year"] + 1, a1["year"] + 1):
        fx_factor *= 1 + FX_PTS.get(y, 0.0) / 100
    ln_fx = math.log(fx_factor)
    ln_adr_exfx = ln_adr - ln_fx
    tot_ln = ln_take + ln_adr
    for label, part in [("Revenue per night: take rate", ln_take), ("Revenue per night: FX", ln_fx), ("Revenue per night: ADR ex-FX", ln_adr_exfx)]:
        out.append({"component": f"{label}", "margin_pts": 100 * total_rpn_effect * (part / tot_ln if tot_ln else 0)})
    addb = a1["addbacks"] / a1["rev"] - a0["addbacks"] / a0["rev"]
    out.append({"component": "D&A and other add-backs / revenue", "margin_pts": 100 * addb})
    stack_delta = 100 * (a1["margin_from_stack"] - a0["margin_from_stack"])
    reported_delta = 100 * (a1["margin"] - a0["margin"])
    out.append({"component": "Residual (identity gaps in the stack)", "margin_pts": reported_delta - stack_delta})
    return out, reported_delta


# ----------------------------------------------------------------------------------------------------------
# Scenarios. Growth rates are year over year unless stated. "cpn" = cash cost per night (or per GBV dollar for CoR).
SCEN = {
    "Base": {
        "note": "FY26 calibrated to the Aug 2026 outlook plus the usual 50 to 100 bps beat of the floor: nights +10%, ADR ex-FX +3.5%, FX +2% (3 pts in Q1-Q3 fading in Q4), "
                "take rate flat, cost of revenue scales with GBV, support cost per night -5% (AI), product dev cash +11%, S&M cash +25% (1H ran +30%), G&A flat. "
                "FY27: nights +9%, ADR ex-FX +3%, no FX, take rate flat, support -5% per night, product dev +9%, S&M +17% (management keeps reinvesting), G&A +5%.",
        2026: {"nights": 0.10, "adr_exfx": 0.035, "fx": 0.02, "take_bps": 0, "cor_per_gbv": 0.0, "ops_cpn": -0.05, "pd_cash": 0.11, "sm_cash": 0.25, "ga_cash": 0.00, "addback_pct": 0.9},
        2027: {"nights": 0.09, "adr_exfx": 0.03, "fx": 0.0, "take_bps": 0, "cor_per_gbv": 0.0, "ops_cpn": -0.05, "pd_cash": 0.09, "sm_cash": 0.17, "ga_cash": 0.05, "addback_pct": 0.9},
    },
    "Bear": {
        "note": "FY26 misses the 35.5% floor slightly: take rate -5 bps from incentives, S&M +24%, support savings slower. "
                "FY27 is a 2024-style slowdown: nights +6%, ADR ex-FX +1%, FX -1.5%, take rate -15 bps to new-business incentives; management flexes S&M growth down to +9% but keeps product headcount (+8%).",
        2026: {"nights": 0.095, "adr_exfx": 0.03, "fx": 0.02, "take_bps": -5, "cor_per_gbv": 0.0, "ops_cpn": -0.04, "pd_cash": 0.11, "sm_cash": 0.24, "ga_cash": 0.01, "addback_pct": 0.9},
        2027: {"nights": 0.06, "adr_exfx": 0.01, "fx": -0.015, "take_bps": -15, "cor_per_gbv": 0.0, "ops_cpn": -0.02, "pd_cash": 0.08, "sm_cash": 0.09, "ga_cash": 0.04, "addback_pct": 0.9},
    },
    "Bull": {
        "note": "FY26: nights +10.5%, ADR ex-FX +4%, monetization +5 bps, support cost per night -7%, S&M +22%. "
                "FY27 shows what happens if the reinvestment cycle eases: nights +10%, ADR ex-FX +3.5%, take rate +10 bps (single fee, insurance), support -7% per night, product dev +8%, S&M +18%, G&A +3%.",
        2026: {"nights": 0.105, "adr_exfx": 0.04, "fx": 0.025, "take_bps": 5, "cor_per_gbv": -0.01, "ops_cpn": -0.07, "pd_cash": 0.10, "sm_cash": 0.22, "ga_cash": 0.00, "addback_pct": 0.9},
        2027: {"nights": 0.10, "adr_exfx": 0.035, "fx": 0.005, "take_bps": 10, "cor_per_gbv": 0.0, "ops_cpn": -0.07, "pd_cash": 0.08, "sm_cash": 0.18, "ga_cash": 0.03, "addback_pct": 0.9},
    },
}


def project(a_prev, p, year):
    nights = a_prev["nights"] * (1 + p["nights"])
    adr = a_prev["adr"] * (1 + p["adr_exfx"]) * (1 + p["fx"])
    gbv = nights * adr
    take = a_prev["take"] + p["take_bps"] / 10000
    rev = gbv * take
    cost = {"cor": (a_prev["cor"] / a_prev["gbv"]) * (1 + p["cor_per_gbv"]) * gbv,
            "ops": (a_prev["ops"] / a_prev["nights"]) * (1 + p["ops_cpn"]) * nights,
            "pd": a_prev["pd"] * (1 + p["pd_cash"]), "sm": a_prev["sm"] * (1 + p["sm_cash"]), "ga": a_prev["ga"] * (1 + p["ga_cash"])}
    addb = rev * p["addback_pct"] / 100
    adj = rev - sum(cost.values()) + addb
    a = {"year": year, "rev": rev, "nights": nights, "gbv": gbv, "adr": adr, "take": take, "rpn": rev / nights, "addbacks": addb, "adj": adj,
         "margin": adj / rev, "margin_from_stack": adj / rev, **cost}
    return a


def main():
    rows = load()
    years = {y: annual(rows, y) for y in (2022, 2023, 2024, 2025)}
    h1_26 = [r for r in rows if r["quarter"] in ("1Q26", "2Q26")]

    # ---- bridge
    br_rows = []
    for y0, y1 in [(2022, 2025), (2023, 2025), (2024, 2025)]:
        comps, delta = bridge(years[y0], years[y1])
        for c in comps:
            br_rows.append({"bridge": f"FY{y0}->FY{y1}", **c, "margin_pts": round(c["margin_pts"], 2)})
        br_rows.append({"bridge": f"FY{y0}->FY{y1}", "component": "TOTAL change in Adj. EBITDA margin", "margin_pts": round(delta, 2)})
    with open(os.path.join(ROOT, "data", "processed", "abnb_margin_bridge.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["bridge", "component", "margin_pts"]); w.writeheader(); w.writerows(br_rows)
    print("\n=== Annual cash stack (% of revenue) ===")
    print("FY | rev | nights | ADR | take | " + " ".join(LINES) + " | addbacks | adj margin | stack margin")
    for y, a in years.items():
        print(y, "|", round(a["rev"]), "|", round(a["nights"], 1), "|", round(a["adr"], 1), "|", f"{100*a['take']:.2f}%", "|",
              " ".join(f"{100*a[k]/a['rev']:.1f}" for k in LINES), "|", f"{100*a['addbacks']/a['rev']:.1f}", "|", f"{100*a['margin']:.1f}%", "|", f"{100*a['margin_from_stack']:.1f}%")
    print("\n=== Bridge FY2022 -> FY2025 (margin points) ===")
    for r in br_rows:
        if r["bridge"] == "FY2022->FY2025":
            print(f"{r['margin_pts']:+7.2f}  {r['component']}")

    # ---- scenarios
    sc_rows = []
    print("\n=== Scenarios ===")
    for name, s in SCEN.items():
        a25 = years[2025]
        a26 = project(a25, s[2026], 2026)
        a27 = project(a26, s[2027], 2027)
        # H2 2026 implied by FY26 less reported H1
        h1 = {"rev": sum(r["revenue_musd"] for r in h1_26), "adj": sum(r["adj_ebitda"] for r in h1_26)}
        h2_rev, h2_adj = a26["rev"] - h1["rev"], a26["adj"] - h1["adj"]
        # Q3 at the guide midpoint with the scenario's margin assumption; Q4 is the remainder
        q3_rev = {"Base": 4730.0, "Bear": 4700.0, "Bull": 4800.0}[name]
        q3_margin = {"Base": 0.490, "Bear": 0.483, "Bull": 0.502}[name]
        q3_adj = q3_rev * q3_margin
        q4_rev, q4_adj = h2_rev - q3_rev, h2_adj - q3_adj
        for lab, a in (("FY2026E", a26), ("FY2027E", a27)):
            sc_rows.append({"scenario": name, "period": lab, "revenue_musd": round(a["rev"]), "rev_growth_pct": round(100 * (a["rev"] / (a25["rev"] if lab == "FY2026E" else a26["rev"]) - 1), 1),
                            "nights_m": round(a["nights"], 1), "adr": round(a["adr"], 1), "take_rate_pct": round(100 * a["take"], 2),
                            **{f"{k}_pct_rev": round(100 * a[k] / a["rev"], 1) for k in LINES},
                            "adj_ebitda_musd": round(a["adj"]), "adj_ebitda_margin_pct": round(100 * a["margin"], 1)})
        for lab, rv, aj in (("Q3 2026E", q3_rev, q3_adj), ("Q4 2026E (implied)", q4_rev, q4_adj)):
            sc_rows.append({"scenario": name, "period": lab, "revenue_musd": round(rv), "adj_ebitda_musd": round(aj), "adj_ebitda_margin_pct": round(100 * aj / rv, 1)})
        print(f"\n{name}: {s['note']}")
        print(f"  FY26E rev {a26['rev']:,.0f} (+{100*(a26['rev']/a25['rev']-1):.1f}%)  margin {100*a26['margin']:.1f}%  | Q3E {100*q3_margin:.1f}% on {q3_rev:,.0f} | Q4E implied {100*q4_adj/q4_rev:.1f}% on {q4_rev:,.0f}")
        print(f"  FY27E rev {a27['rev']:,.0f} (+{100*(a27['rev']/a26['rev']-1):.1f}%)  margin {100*a27['margin']:.1f}%  lines % rev: " + " ".join(f"{k}={100*a27[k]/a27['rev']:.1f}" for k in LINES))
    keys = ["scenario", "period", "revenue_musd", "rev_growth_pct", "nights_m", "adr", "take_rate_pct"] + [f"{k}_pct_rev" for k in LINES] + ["adj_ebitda_musd", "adj_ebitda_margin_pct"]
    with open(os.path.join(ROOT, "data", "processed", "abnb_margin_scenarios.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(sc_rows)

    h1 = {"rev": sum(r["revenue_musd"] for r in h1_26), "adj": sum(r["adj_ebitda"] for r in h1_26)}
    for g in (0.15, 0.16):
        fy_rev = years[2025]["rev"] * (1 + g); fy_adj = 0.355 * fy_rev
        q4_rev = fy_rev - h1["rev"] - 4730.0; q4_adj = fy_adj - h1["adj"] - 4730.0 * 0.49
        print(f"Floor case: FY26 rev +{100*g:.0f}% at exactly 35.5% with Q3 at 49% -> Q4 margin {100*q4_adj/q4_rev:.1f}% on {q4_rev:,.0f} (Q4 2025 was 28.3%)")

    # ---- sensitivities on the FY2026 base
    print("\n=== FY2026E base-case sensitivities (margin points) ===")
    base = SCEN["Base"][2026]
    a25 = years[2025]
    b = project(a25, base, 2026)
    for label, key, dv in [("+1 pt ADR ex-FX", "adr_exfx", 0.01), ("+1 pt FX", "fx", 0.01), ("+10 bps take rate", "take_bps", 10),
                           ("+1 pt nights growth", "nights", 0.01), ("-10% support cost per night", "ops_cpn", -0.10), ("+5 pts S&M cash growth", "sm_cash", 0.05)]:
        p = dict(base); p[key] = p[key] + dv
        a = project(a25, p, 2026)
        print(f"{label:32s} {100*(a['margin']-b['margin']):+.2f} pts margin, {a['adj']-b['adj']:+,.0f} $M EBITDA")


if __name__ == "__main__":
    sys.exit(main())
