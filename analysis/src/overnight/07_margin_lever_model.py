"""Workstream 07 part 4: a lever-by-lever margin model for FY2026E, FY2027E and FY2028E.

What it does that abnb_margin_bridge.py does not
  - carries a third year (FY2028E);
  - splits sales and marketing into brand-and-performance marketing and field operations and policy (the
    new-business / go-to-market line), so "S&M" stops being one opaque lever;
  - runs below Adjusted EBITDA: SBC, D&A, interest income and expense, cash taxes, unearned fees and capex, so the
    same levers produce a GAAP operating margin, an FCF margin and an SBC-adjusted FCF margin;
  - attributes the margin change of each year to each lever in margin points, using the same decomposition as
    abnb_margin_bridge.py (unit-cost effect plus a revenue-per-night effect split log-linearly into ADR ex-FX, FX and
    take rate), so the numbers reconcile with data/processed/abnb_margin_bridge.csv;
  - puts a probability on the "path to 40%" with a Monte Carlo over the lever ranges instead of asserting one.

Method
  Cost lines are driven by their natural unit: cost of revenue by GBV dollars (payments and hosting), operations and
  support by nights, product development / brand-and-performance marketing / field operations / G&A by cash growth
  rates. Revenue = nights x ADR (ex-FX x FX) x take rate. Adjusted EBITDA = revenue - cash costs + add-backs.
  Below the line: GAAP operating income = Adjusted EBITDA - SBC - D&A - other add-backs. FCF = Adjusted EBITDA
  + interest income - interest expense + other income - cash taxes + change in unearned fees + working-capital
  residual - capex, with the residual calibrated to -1.1% of revenue, the FY2024 and FY2025 actual (both -$140M).

Reads
  data/processed/abnb_quarterly_cost_stack_exsbc.csv      cash cost stack, nights, GBV, SBC by line, D&A, Adj. EBITDA
  data/processed/abnb_fcf_bridge.csv                      interest, taxes, unearned fees, capex, FCF, SBC
  data/processed/overnight/07_cost_lines_per_night.csv    the quarterly S&M split (brand+performance vs field ops)
  data/processed/abnb_margin_scenarios.csv                the existing FY26/FY27 scenarios, for reconciliation

Writes
  data/processed/overnight/07_margin_levers_fy26_fy28.csv

Run: py -3.13 analysis/src/overnight/07_margin_lever_model.py
"""
import csv, math, os, random

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
P = lambda *a: os.path.join(ROOT, *a)
OUT = P("data", "processed", "overnight", "07_margin_levers_fy26_fy28.csv")
LINES = ["cor", "ops", "pd", "bpm", "fop", "ga"]
NAMES = {"cor": "Cost of revenue (payments, chargebacks, hosting) per $ GBV",
         "ops": "Operations & support per night",
         "pd": "Product development, cash (ex-SBC)",
         "bpm": "Brand and performance marketing",
         "fop": "Field operations and policy, cash (new-business investment)",
         "ga": "General and administrative, cash"}


def rd(path):
    return list(csv.DictReader(open(path, newline="", encoding="utf-8")))


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------------------------------- actuals
def actuals():
    S = rd(P("data", "processed", "abnb_quarterly_cost_stack_exsbc.csv"))
    C = {r["quarter"]: r for r in rd(P("data", "processed", "overnight", "07_cost_lines_per_night.csv"))}
    B = {r["period"]: r for r in rd(P("data", "processed", "abnb_fcf_bridge.csv"))}
    out = {}
    for y in (2024, 2025):
        qs = [r for r in S if r["quarter"].endswith(str(y)[2:])]
        assert len(qs) == 4, y
        g = lambda c: sum(f(r[c]) for r in qs)
        bpm = sum(f(C[r["quarter"]]["sm_brand_perf_musd"]) for r in qs)          # GAAP; media spend, no SBC in it
        sm_cash = g("sm_cash")
        a = {"year": y, "rev": g("revenue_musd"), "nights": g("nights_m"), "gbv": 1000 * g("gbv_busd"),
             "cor": g("cor_cash"), "ops": g("ops_cash"), "pd": g("pd_cash"), "bpm": bpm, "fop": sm_cash - bpm,
             "ga": g("ga_cash"), "addbacks": g("da") + g("other_addbacks") - g("restr"), "adj": g("adj_ebitda"),
             "sbc": g("sbc_total"), "da": g("da"), "other_addbacks": g("other_addbacks")}
        b = B[f"FY{y}"]
        a.update({"interest_income": f(b["interest_income"]), "interest_expense": f(b["interest_expense"]),
                  "other_income": f(b["other_income_expense"]), "cash_taxes": f(b["cash_taxes_paid_10k"]),
                  "d_unearned": f(b["change_unearned_fees"]), "capex": -f(b["capex"]), "fcf_actual": f(b["fcf"])})
        a["adr"] = a["gbv"] / a["nights"]; a["take"] = a["rev"] / a["gbv"]; a["rpn"] = a["rev"] / a["nights"]
        a["margin"] = a["adj"] / a["rev"]
        # working-capital residual implied by the actual FCF, the piece the bridge cannot name (mostly deferred tax)
        a["wc_resid"] = a["fcf_actual"] - (a["adj"] + a["interest_income"] - a["interest_expense"] + a["other_income"]
                                           - a["cash_taxes"] + a["d_unearned"] - a["capex"])
        out[y] = a
    h1 = [r for r in S if r["quarter"] in ("1Q26", "2Q26")]
    out["1H26"] = {"rev": sum(f(r["revenue_musd"]) for r in h1), "adj": sum(f(r["adj_ebitda"]) for r in h1),
                   "nights": sum(f(r["nights_m"]) for r in h1), "sbc": sum(f(r["sbc_total"]) for r in h1)}
    return out


# --------------------------------------------------------------------------------------------------- levers
# Each entry: (bear, base, bull, unit, evidence). Signs are as entered into the projection.
LEVERS = {
    2026: {
        "nights":     (0.095, 0.100, 0.103, "y/y growth", "1H26 actual +9.7% (304.5M vs 277.5M); 2Q26 +10%. Guide implies mid-teens revenue growth on a flat take rate"),
        "adr_exfx":   (0.030, 0.035, 0.040, "y/y growth", "Letters: ADR ex-FX +3% (4Q25), +4% (1Q26), +4% (2Q26). US hotel prices turned positive in 2Q26 (+4.9%), closing the gap"),
        "fx":         (0.018, 0.020, 0.023, "y/y effect on revenue", "2Q26 letter: about a 3-point FX tailwind to revenue growth after hedging, expected to fade into Q4"),
        "take_bps":   (-5, 0, 5, "bps change vs 13.41%", "Management guides the 2026 take rate flat; new-business incentives are the offset to the 15.5% single-fee rollout"),
        "cor_per_gbv": (0.005, 0.000, -0.005, "y/y change in cost per $ GBV", "2Q26 10-Q: cost of revenue +16% on GBV +16%; merchant fees +$131M and chargebacks +$25M in 1H26 with 'a slight increase in our chargeback rate', server costs +$15M"),
        "ops_cpn":    (-0.040, -0.050, -0.060, "y/y change in cash cost per night", "Support cost per booking -10% (1Q26) and -16% (2Q26); third-party service providers -$17M in 2Q26. Offset by payroll +$41M, customer relations +$14M, insurance +$9M in 1H26"),
        "pd_cash":    (0.115, 0.110, 0.105, "y/y cash growth", "1H26 product development +11%, entirely payroll on higher average headcount (10-Q)"),
        "bpm_cash":   (0.28, 0.25, 0.23, "y/y growth", "1H26 brand and performance marketing +32% ($1,091M vs $824M). The base case needs H2 at about +17% y/y (H2 2025 was $771M); the 35.5% FY floor is only breached above about +29% H2 growth, so the floor has cushion the base case does not"),
        "fop_cash":   (0.20, 0.18, 0.16, "y/y cash growth", "Field operations and policy +24% in 1H26, decelerating from +43% in FY2025 as the Services and Experiences launch spend laps"),
        "ga_cash":    (0.03, 0.02, 0.00, "y/y cash growth", "1H26 G&A +1%: payroll +$38M offset by non-income taxes -$38M"),
        "addback_pct": (0.9, 0.9, 0.9, "% of revenue", "D&A plus acquisition-related add-backs; 0.9% of revenue in FY2025"),
        "sbc_growth": (0.16, 0.13, 0.10, "y/y growth", "1H26 SBC $897M vs $782M, +14.7%. Management guides SBC growth below 2025 (+10%)"),
        "int_income": (620, 660, 700, "$M", "1H26 interest income $338M vs $363M, -7%; $12.1B of cash and short-term investments at 30 Jun 2026 against falling rates"),
        "int_expense": (125, 120, 115, "$M", "$2.5B senior notes issued 16 Mar 2026 at 4.40-5.25%; interest expense $37M in 2Q26, $58M in 1H26"),
        "cash_tax_pct_rev": (0.035, 0.026, 0.020, "% of revenue", "FY2025 cash taxes $232M (1.9% of revenue) against a $626M provision; 1H26 provision $202M on a 17.1% effective rate. The released deferred tax assets are being consumed"),
        "d_unearned_pct_rev": (-0.005, 0.000, 0.005, "% of revenue", "Unearned fees fell y/y in 2Q26 ($2,831M vs $2,857M) as Reserve Now, Pay Later moves collection to check-in"),
    },
    2027: {
        "nights":     (0.060, 0.085, 0.100, "y/y growth", "Nights have grown 8-10% every quarter since 2Q24. Bear is a 2020-style demand stall plus regulatory losses; bull is hotels and expansion markets contributing"),
        "adr_exfx":   (0.010, 0.025, 0.035, "y/y growth", "ADR ex-FX has run +3-4%. Once US hotel pricing is positive the Airbnb-specific premium is gone and ADR reverts to mix plus inflation"),
        "fx":         (-0.020, 0.000, 0.010, "y/y effect on revenue", "61% of revenue is from international hosts. A 1% dollar move is worth ~0.55% of revenue; hedges lag it by a few quarters"),
        "take_bps":   (-15, 0, 15, "bps change", "Bull: the 15.5% single fee, loyalty and sponsored listings ('on the horizon', Feb 2026). Bear: incentives for hotels, Services and Experiences"),
        "cor_per_gbv": (0.015, 0.000, -0.010, "y/y change per $ GBV", "Payments has been flat at 1.82-1.89% of GBV since 2022. The risk is committed compute: purchase obligations $1,749M at end-2025 vs $719M at end-2024"),
        "ops_cpn":    (-0.020, -0.050, -0.070, "y/y change per night", "AI resolution went from a third to ~45% of contacts in three quarters; voice and more languages are the stated next step. Bear assumes the easy contacts are done"),
        "pd_cash":    (0.090, 0.100, 0.100, "y/y cash growth", "Cash product development has been 10-11% of revenue since 2022 and grew 11% in 1H26. NOTE the bear is LOWER than the base: in a demand bear management slows hiring, it just does not slow it enough to hold the margin"),
        "bpm_cash":   (0.120, 0.160, 0.145, "y/y growth", "Mertz: core-market brand spend is 'effectively a fixed amount per market'. The 2026 ramp is emerging markets and partnerships. Bear cuts spend (2020 precedent: brand and performance marketing fell 58% in a demand shock) but revenue falls faster; bull spends into a strong year and still gets leverage"),
        "fop_cash":   (0.100, 0.140, 0.120, "y/y cash growth", "Hotels and enterprise org built out through 2026 (Rijvers, D'Amico, Fuldner). Bear slows the build; bull grows it into a bigger revenue base. Field ops grew 43% in 2025 and 24% in 1H26"),
        "ga_cash":    (0.050, 0.055, 0.045, "y/y cash growth", "G&A cash has grown 4-6% a year ex the 2023-2024 tax reserves; it is the most predictable line in the P&L"),
        "addback_pct": (0.9, 0.9, 0.9, "% of revenue", "held flat"),
        "sbc_growth": (0.14, 0.10, 0.06, "y/y growth", "SBC grew 10-13% a year 2023-2025. It is the whole GAAP margin gap to Booking (13.0% of revenue vs 2.3%)"),
        "int_income": (540, 620, 690, "$M", "Falling rates against a cash pile held roughly flat by buybacks at 80%+ of FCF"),
        "int_expense": (128, 125, 122, "$M", "Full year of the $2.5B notes"),
        "cash_tax_pct_rev": (0.045, 0.034, 0.026, "% of revenue", "Cash taxes converge on the provision (~5% of revenue) as the 2023 valuation-allowance release is consumed; $376M of it was used in 2025"),
        "d_unearned_pct_rev": (-0.005, 0.000, 0.003, "% of revenue", "RNPL has switched the float off; no reason for it to restart"),
    },
    2028: {
        "nights":     (0.050, 0.080, 0.095, "y/y growth", "Extrapolation, no guide. Bear is the mature-market saturation case; bull needs hotels and Experiences to be material"),
        "adr_exfx":   (0.010, 0.025, 0.035, "y/y growth", "Long-run: lodging price inflation plus mix"),
        "fx":         (0.000, 0.000, 0.000, "y/y effect", "No view three years out; set to zero in every case so FX does not flatter the path"),
        "take_bps":   (-10, 5, 20, "bps change", "Bull is the advertising / sponsored-listings case Wells Fargo models for 2027 onward, plus loyalty"),
        "cor_per_gbv": (0.010, -0.005, -0.015, "y/y change per $ GBV", "Payments scale and hosting amortisation rolling off the 2025-2031 commitment"),
        "ops_cpn":    (-0.020, -0.050, -0.070, "y/y change per night", "Third year of AI support compounding"),
        "pd_cash":    (0.085, 0.095, 0.095, "y/y cash growth", "Below revenue growth in the base and bull: this is the line AI engineering productivity is supposed to bend. In the bear it is above revenue growth even at 8.5%"),
        "bpm_cash":   (0.110, 0.135, 0.125, "y/y growth", "Expansion-market brand spend annualising. In every case marketing grows slower than in 2026 (+25%), which is the single biggest assumption in the model"),
        "fop_cash":   (0.090, 0.120, 0.105, "y/y cash growth", "New-business go-to-market normalising toward revenue growth. No disclosure exists to anchor this: field ops is the least forecastable line"),
        "ga_cash":    (0.050, 0.050, 0.040, "y/y cash growth", "trend; G&A cash grew 15.7% in 2025 and about 1% in 1H26"),
        "addback_pct": (0.9, 0.9, 0.9, "% of revenue", "held flat"),
        "sbc_growth": (0.12, 0.08, 0.04, "y/y growth", "Bull is the only case in which SBC as a share of revenue falls meaningfully"),
        "int_income": (500, 590, 680, "$M", "Cash pile roughly flat; rate path unknown"),
        "int_expense": (128, 125, 122, "$M", "fixed-rate notes"),
        "cash_tax_pct_rev": (0.052, 0.040, 0.032, "% of revenue", "Bear is full convergence on the ~5% provision; bull assumes credits and foreign-derived income keep the cash rate below it"),
        "d_unearned_pct_rev": (-0.005, 0.000, 0.003, "% of revenue", "no float growth assumed"),
    },
}
SCEN_IDX = {"Bear": 0, "Base": 1, "Bull": 2}


def pick(year, name, scen):
    return LEVERS[year][name][SCEN_IDX[scen]]


def project(a0, year, params):
    nights = a0["nights"] * (1 + params["nights"])
    adr = a0["adr"] * (1 + params["adr_exfx"]) * (1 + params["fx"])
    gbv = nights * adr
    take = a0["take"] + params["take_bps"] / 10000
    rev = gbv * take
    cost = {"cor": (a0["cor"] / a0["gbv"]) * (1 + params["cor_per_gbv"]) * gbv,
            "ops": (a0["ops"] / a0["nights"]) * (1 + params["ops_cpn"]) * nights,
            "pd": a0["pd"] * (1 + params["pd_cash"]),
            "bpm": a0["bpm"] * (1 + params["bpm_cash"]),
            "fop": a0["fop"] * (1 + params["fop_cash"]),
            "ga": a0["ga"] * (1 + params["ga_cash"])}
    addb = rev * params["addback_pct"] / 100
    adj = rev - sum(cost.values()) + addb
    sbc = a0["sbc"] * (1 + params["sbc_growth"])
    da = rev * 0.007                       # D&A has been 0.6-0.8% of revenue since 2023
    other_addbacks = addb - da
    op_income = adj - sbc - da - other_addbacks
    cash_tax = rev * params["cash_tax_pct_rev"]
    d_unearned = rev * params["d_unearned_pct_rev"]
    capex = rev * 0.003
    wc_resid = -0.011 * rev                # FY2024 and FY2025 both -$140M, about -1.1% of revenue
    fcf = adj + params["int_income"] - params["int_expense"] - cash_tax + d_unearned + wc_resid - capex
    a = {"year": year, "rev": rev, "nights": nights, "gbv": gbv, "adr": adr, "take": take, "rpn": rev / nights,
         "addbacks": addb, "adj": adj, "margin": adj / rev, "sbc": sbc, "da": da, "other_addbacks": other_addbacks,
         "op_income": op_income, "op_margin": op_income / rev, "interest_income": params["int_income"],
         "interest_expense": params["int_expense"], "cash_taxes": cash_tax, "d_unearned": d_unearned,
         "capex": capex, "wc_resid": wc_resid, "fcf": fcf, "fcf_margin": fcf / rev,
         "sbc_adj_fcf": fcf - sbc, "sbc_adj_fcf_margin": (fcf - sbc) / rev, "other_income": 0.0, **cost}
    return a


def bridge(a0, a1):
    """Margin-point attribution, same decomposition as analysis/src/abnb_margin_bridge.py."""
    out, rpn_total = [], 0.0
    r0, r1 = a0["rpn"], a1["rpn"]
    for k in LINES:
        c0, c1 = a0[k] / a0["nights"], a1[k] / a1["nights"]
        out.append((NAMES[k], 100 * (-(c1 - c0) / r0), f"{c0:.2f} -> {c1:.2f} $/night"))
        rpn_total += -c1 * (1 / r1 - 1 / r0)
    ln_take, ln_adr = math.log(a1["take"] / a0["take"]), math.log(a1["adr"] / a0["adr"])
    ln_fx = math.log(1 + a1["_fx"])
    tot = ln_take + ln_adr
    for label, part, det in [("Revenue per night: take rate", ln_take, f"{100*a0['take']:.2f}% -> {100*a1['take']:.2f}%"),
                             ("Revenue per night: FX", ln_fx, f"{100*a1['_fx']:+.1f}% on revenue"),
                             ("Revenue per night: ADR ex-FX", ln_adr - ln_fx, f"{100*a1['_adr_exfx']:+.1f}% ADR ex-FX")]:
        out.append((label, 100 * rpn_total * (part / tot if tot else 0), det))
    out.append(("D&A and other add-backs / revenue", 100 * (a1["addbacks"] / a1["rev"] - a0["addbacks"] / a0["rev"]), "0.9% of revenue"))
    return out


def main():
    A = actuals()
    rows = []
    results = {}
    for scen in ("Bear", "Base", "Bull"):
        prev = A[2025]
        chain = {2025: A[2025]}
        for year in (2026, 2027, 2028):
            params = {k: pick(year, k, scen) for k in LEVERS[year]}
            a = project(prev, year, params)
            a["_fx"], a["_adr_exfx"] = params["fx"], params["adr_exfx"]
            chain[year] = a
            # lever rows
            for k in LEVERS[year]:
                lo, base, hi = LEVERS[year][k][:3]
                rows.append({"row_type": "lever", "scenario": scen, "year": f"FY{year}E", "item": k,
                             "unit": LEVERS[year][k][3], "value": params[k],
                             "bear": lo, "base": base, "bull": hi, "margin_pts": "", "evidence": LEVERS[year][k][4]})
            # attribution rows
            for label, pts, detail in bridge(prev, a):
                rows.append({"row_type": "attribution", "scenario": scen, "year": f"FY{year}E", "item": label,
                             "unit": "margin points vs prior year", "value": "", "bear": "", "base": "", "bull": "",
                             "margin_pts": round(pts, 2), "evidence": detail})
            rows.append({"row_type": "attribution", "scenario": scen, "year": f"FY{year}E", "item": "TOTAL change in Adj. EBITDA margin",
                         "unit": "margin points vs prior year", "value": "", "bear": "", "base": "", "bull": "",
                         "margin_pts": round(100 * (a["margin"] - prev["margin"]), 2), "evidence": ""})
            # results
            for label, val, unit in [
                    ("Revenue", a["rev"], "$M"), ("Revenue growth", 100 * (a["rev"] / prev["rev"] - 1), "%"),
                    ("Nights", a["nights"], "M"), ("ADR", a["adr"], "$"), ("Take rate", 100 * a["take"], "%"),
                    ("Adjusted EBITDA", a["adj"], "$M"), ("Adjusted EBITDA margin", 100 * a["margin"], "%"),
                    ("SBC", a["sbc"], "$M"), ("SBC % revenue", 100 * a["sbc"] / a["rev"], "%"),
                    ("GAAP operating income", a["op_income"], "$M"), ("GAAP operating margin", 100 * a["op_margin"], "%"),
                    ("Interest income", a["interest_income"], "$M"), ("Interest expense", a["interest_expense"], "$M"),
                    ("Cash taxes", a["cash_taxes"], "$M"),
                    ("Free cash flow", a["fcf"], "$M"), ("FCF margin", 100 * a["fcf_margin"], "%"),
                    ("FCF / Adjusted EBITDA", 100 * a["fcf"] / a["adj"], "%"),
                    ("SBC-adjusted FCF", a["sbc_adj_fcf"], "$M"), ("SBC-adjusted FCF margin", 100 * a["sbc_adj_fcf_margin"], "%")]:
                rows.append({"row_type": "result", "scenario": scen, "year": f"FY{year}E", "item": label,
                             "unit": unit, "value": round(val, 2), "bear": "", "base": "", "bull": "", "margin_pts": "", "evidence": ""})
            prev = a
        results[scen] = chain

    # ------------------------------------------------------------------ reconciliation to the existing scenarios
    old = {(r["scenario"], r["period"]): r for r in rd(P("data", "processed", "abnb_margin_scenarios.csv"))}
    for scen in ("Bear", "Base", "Bull"):
        for year in (2026, 2027):
            o = old.get((scen, f"FY{year}E"))
            if not o:
                continue
            new = results[scen][year]
            rows.append({"row_type": "reconciliation", "scenario": scen, "year": f"FY{year}E", "item": "Adj. EBITDA margin vs abnb_margin_scenarios.csv",
                         "unit": "margin points", "value": round(100 * new["margin"] - f(o["adj_ebitda_margin_pct"]), 2),
                         "bear": "", "base": "", "bull": "", "margin_pts": "",
                         "evidence": f"this model {100*new['margin']:.1f}% vs existing {f(o['adj_ebitda_margin_pct']):.1f}%; revenue ${new['rev']:,.0f}M vs ${f(o['revenue_musd']):,.0f}M"})

    # implied H2 2026 and Q4 2026 against the guide, base case
    h1 = A["1H26"]
    for scen in ("Bear", "Base", "Bull"):
        a26 = results[scen][2026]
        q3_rev, q3_margin = {"Bear": (4700.0, 0.483), "Base": (4730.0, 0.490), "Bull": (4800.0, 0.502)}[scen]
        q4_rev = a26["rev"] - h1["rev"] - q3_rev
        q4_adj = a26["adj"] - h1["adj"] - q3_rev * q3_margin
        rows.append({"row_type": "result", "scenario": scen, "year": "Q4 2026E (implied)", "item": "Adjusted EBITDA margin",
                     "unit": "%", "value": round(100 * q4_adj / q4_rev, 1), "bear": "", "base": "", "bull": "", "margin_pts": "",
                     "evidence": f"FY26E less 1H26 actual (${h1['rev']:,.0f}M rev, ${h1['adj']:,.0f}M Adj. EBITDA) less Q3 at the guide midpoint "
                                 f"(${q3_rev:,.0f}M at {100*q3_margin:.1f}%); Q4 2025 printed 28.3% on revenue of ${q4_rev:,.0f}M implied"})

    # ------------------------------------------------------------------ path to 40%: Monte Carlo over the ranges
    random.seed(20260906)
    N = 40000
    Z = 1.2816                      # bear and bull are read as the 10th and 90th percentile of the common factor
    RHO = 0.75                      # how much of each lever is the common demand / dollar / spending-discipline state
    PERSIST = 0.6                   # year-to-year persistence of that state (a bad year is usually followed by a bad year)

    def draw_year(year, z):
        p = {}
        for k, three in {k: v[:3] for k, v in LEVERS[year].items()}.items():
            lo, base, hi = three
            t = RHO * z + math.sqrt(1 - RHO ** 2) * random.gauss(0, 1)
            p[k] = base + (max(t, 0) / Z) * (hi - base) + (max(-t, 0) / Z) * (lo - base)
        return p

    for label, correlated in (("Monte Carlo (correlated)", True), ("Monte Carlo (independent)", False)):
        draws = {2026: [], 2027: [], 2028: []}
        hits = {y: {40: 0, 38: 0, 36: 0, 34: 0} for y in (2026, 2027, 2028)}
        for _ in range(N):
            prev, z = A[2025], 0.0
            for year in (2026, 2027, 2028):
                if correlated:
                    z = PERSIST * z + math.sqrt(1 - PERSIST ** 2) * random.gauss(0, 1)
                    params = draw_year(year, z)
                else:
                    params = {}
                    for k, three in {k: v[:3] for k, v in LEVERS[year].items()}.items():
                        a_, b_ = min(three), max(three)
                        mode = min(max(three[1], a_), b_)
                        params[k] = a_ if a_ == b_ else random.triangular(a_, b_, mode)
                a = project(prev, year, params)
                draws[year].append(100 * a["margin"])
                prev = a
            for year in (2026, 2027, 2028):
                m = draws[year][-1]
                for thr in (40, 38, 36):
                    hits[year][thr] += m >= thr
                hits[year][34] += m < 34
        for year in (2026, 2027, 2028):
            d = sorted(draws[year])
            note = ("levers share a common state with correlation 0.75 and 0.6 year-to-year persistence, so a bad demand year "
                    "drags ADR, FX, take rate and spending discipline together; bear and bull are read as the 10th and 90th percentile"
                    if correlated else
                    "levers drawn independently (triangular on bear/base/bull). This is the wrong model - it cancels the tails - and is "
                    "shown only to bound how much the correlation assumption matters")
            rows.append({"row_type": "path_to_40", "scenario": label, "year": f"FY{year}E", "item": "Adj. EBITDA margin distribution",
                         "unit": "%", "value": round(sum(d) / len(d), 2), "bear": round(d[int(0.10 * len(d))], 2),
                         "base": round(d[len(d) // 2], 2), "bull": round(d[int(0.90 * len(d))], 2), "margin_pts": "",
                         "evidence": f"{N:,} draws; P(>=40%) {100*hits[year][40]/N:.1f}%, P(>=38%) {100*hits[year][38]/N:.1f}%, "
                                     f"P(>=36%) {100*hits[year][36]/N:.1f}%, P(<34%) {100*hits[year][34]/N:.1f}%. {note}"})

    # what it takes: hold the base revenue path and solve the cost side for 40% in FY2028
    prev = A[2025]
    chain = {}
    for year in (2026, 2027, 2028):
        params = {k: pick(year, k, "Base") for k in LEVERS[year]}
        chain[year] = params
        prev = project(prev, year, params)
    SOLVES = [  # label, lever keys, search bounds, +1 if margin rises with the lever, unit, display scale
        ("S&M cash growth (brand+performance and field operations together)", ("bpm_cash", "fop_cash"), (-0.40, 0.60), -1, "y/y growth %", 100),
        ("Operations & support cash cost per night", ("ops_cpn",), (-0.45, 0.30), -1, "y/y change %", 100),
        ("Product development cash growth", ("pd_cash",), (-0.45, 0.50), -1, "y/y growth %", 100),
        ("Take rate change per year", ("take_bps",), (-60.0, 200.0), +1, "bps per year", 1),
        ("Nights growth", ("nights",), (0.0, 0.45), +1, "y/y growth %", 100),
    ]
    for label, keys, (lo, hi), sign, unit, scale in SOLVES:
        def margin_at(v):
            p = A[2025]
            for year in (2026, 2027, 2028):
                q = dict(chain[year])
                for k in keys:
                    q[k] = v
                p = project(p, year, q)
            return 100 * p["margin"]
        best_end = hi if sign > 0 else lo                # the end of the range that maximises the margin
        feasible = margin_at(best_end) >= 40
        if not feasible:
            rows.append({"row_type": "path_to_40", "scenario": "Solve", "year": "FY2028E",
                         "item": f"{label} required every year for a 40% FY2028 margin", "unit": unit, "value": "not reachable",
                         "bear": "", "base": round(scale * chain[2028][keys[0]], 1), "bull": "", "margin_pts": "",
                         "evidence": f"even at the edge of the search range ({scale*best_end:.1f}) the FY2028 margin only reaches "
                                     f"{margin_at(best_end):.1f}% with every other lever at base"})
            continue
        for _ in range(60):
            mid = (lo + hi) / 2
            hits = margin_at(mid) >= 40
            if sign > 0:                                  # margin rises with the lever: shrink toward the smallest value that works
                lo, hi = (lo, mid) if hits else (mid, hi)
            else:                                         # margin falls with the lever: find the largest value that still works
                lo, hi = (mid, hi) if hits else (lo, mid)
        v = hi if sign > 0 else lo
        rows.append({"row_type": "path_to_40", "scenario": "Solve", "year": "FY2028E", "item": f"{label} required every year for a 40% FY2028 margin",
                     "unit": unit, "value": round(scale * v, 1), "bear": "", "base": round(scale * chain[2028][keys[0]], 1), "bull": "", "margin_pts": "",
                     "evidence": "every other lever held at its base value in all three years; solved by bisection. 'base' column is the base-case setting for FY2028"})

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    keys = ["row_type", "scenario", "year", "item", "unit", "value", "bear", "base", "bull", "margin_pts", "evidence"]
    with open(OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys); w.writeheader(); w.writerows(rows)

    # ------------------------------------------------------------------ console
    print(f"FY2025 actual: revenue ${A[2025]['rev']:,.0f}M, Adj. EBITDA margin {100*A[2025]['margin']:.1f}%, "
          f"S&M cash split brand+perf ${A[2025]['bpm']:,.0f}M / field ops ${A[2025]['fop']:,.0f}M, FCF ${A[2025]['fcf_actual']:,.0f}M, wc residual ${A[2025]['wc_resid']:,.0f}M")
    print(f"\n{'scen':5s} {'year':7s} {'rev':>8s} {'gr%':>6s} {'adjEB%':>7s} {'GAAPop%':>8s} {'SBC%':>6s} {'FCF%':>6s} {'FCF/EB':>7s} {'exSBCFCF%':>9s}")
    for scen in ("Bear", "Base", "Bull"):
        for year in (2026, 2027, 2028):
            a = results[scen][year]
            print(f"{scen:5s} FY{year:4d} {a['rev']:8,.0f} {100*(a['rev']/results[scen][year-1]['rev']-1):6.1f} {100*a['margin']:7.1f} "
                  f"{100*a['op_margin']:8.1f} {100*a['sbc']/a['rev']:6.1f} {100*a['fcf_margin']:6.1f} {100*a['fcf']/a['adj']:7.0f} {100*a['sbc_adj_fcf_margin']:9.1f}")
    print("\nBase-case attribution, FY2025 -> FY2026 (margin points):")
    for label, pts, det in bridge(A[2025], results["Base"][2026]):
        print(f"  {pts:+6.2f}  {label}  [{det}]")
    print("\nBase-case attribution, FY2027 -> FY2028 (margin points):")
    for label, pts, det in bridge(results["Base"][2027], results["Base"][2028]):
        print(f"  {pts:+6.2f}  {label}  [{det}]")
    print("\nPath to 40% and reconciliation rows:")
    for r in rows:
        if r["row_type"] in ("path_to_40", "reconciliation") or (r["row_type"] == "result" and r["year"].startswith("Q4")):
            print(f"  [{r['row_type']}] {r['scenario']:11s} {r['year']:20s} {r['item'][:64]:64s} {r['value']} {r['unit']}")
            if r["row_type"] == "path_to_40" and r["scenario"] == "Monte Carlo":
                print(f"       {r['evidence']}")
    print("\n->", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
