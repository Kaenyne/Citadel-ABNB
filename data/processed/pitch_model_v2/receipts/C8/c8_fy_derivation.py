"""C8 FY26/FY27 FCF and SBC-adjusted FCF by scenario (base/short/breaker).

DERIVED, not reproduced: no committed package in the repo builds a below-EBITDA
(capex/SBC/tax/interest -> FCF) forecast under the pitch-model-v2 short/breaker
scenario definitions. The only fully-built below-EBITDA object is
data/processed/margin_build/M7_below_ebitda/M7_below_ebitda_annual_forecasts.csv,
scenario "base", ebitda_source "driver-lines" (spec a_unit_rw, vintage 2026-09-11) --
which predates and differs from C6's post-audit adopted line-build (LB) EBITDA
(docs/pitch-model-v2/dossiers/C6_c6_ebitda.md sec 2a) by $75-82M.

Method: re-anchor M7's own base FCF to C6's LB EBITDA by adding the EBITDA delta
after tax (marginal EBITDA -> FCF at (1 - ETR), holding capex/SBC/interest/WC at
M7's base-case parameter values, which per M7_parameter_sheet.csv do not vary by
revenue/cost scenario). Then apply the short/breaker EBITDA deltas (also from C6,
same LB source) the same way. This is a linear approximation labelled DERIVED
throughout the dossier; it has NOT been tested (no W1/W2 backtest exists for a
scenario-conditional FCF object) and is not a substitute for C7's own build.
"""
import csv, json

M7 = {
    "FY2026": {"revenue": 14268.1433, "ebitda": 5173.983195779814, "capex": 38.858641991563914,
               "sbc": 1813.7397002142038, "fcf": 4906.643783563227, "shares": 595.7568600364291,
               "etr": 0.177426269597819},
    "FY2027": {"revenue": 15828.6066, "ebitda": 5562.175487684005, "capex": 35.717283983127835,
               "sbc": 2052.749616099962, "fcf": 5361.753334393954, "shares": 573.0411602185749,
               "etr": 0.175},
}
# C6 dossier sec 2a, adopted line-build (LB) adj_ebitda_musd, scenarios base/short/breaker
C6_LB_EBITDA = {
    "FY2026": {"base": 5098.5, "short": 4769.4, "breaker": 5194.2},
    "FY2027": {"base": 5644.2, "short": 4761.4, "breaker": 6023.5},
}
SPOT = 167.51  # DEC-0015 provisional, memo v3's 16 Sep 2026 close

rows = []
for fy in ("FY2026", "FY2027"):
    m = M7[fy]
    mktcap = SPOT * m["shares"]
    base_lb = C6_LB_EBITDA[fy]["base"]
    fcf_base = m["fcf"] + (base_lb - m["ebitda"]) * (1 - m["etr"])
    for scen in ("base", "short", "breaker"):
        ebitda_lb = C6_LB_EBITDA[fy][scen]
        fcf = fcf_base if scen == "base" else fcf_base + (ebitda_lb - base_lb) * (1 - m["etr"])
        fcf_ex_sbc = fcf - m["sbc"]
        rows.append({
            "period": fy, "scenario": scen, "ebitda_lb_musd": ebitda_lb,
            "capex_musd": round(m["capex"], 1), "sbc_musd": round(m["sbc"], 1),
            "fcf_musd": round(fcf, 1), "fcf_ex_sbc_musd": round(fcf_ex_sbc, 1),
            "diluted_shares_m": round(m["shares"], 1), "mktcap_musd": round(mktcap, 1),
            "fcf_yield_pct": round(100 * fcf / mktcap, 3),
            "fcf_exsbc_yield_pct": round(100 * fcf_ex_sbc / mktcap, 3),
        })
    # M7's own unadjusted base object, for comparison
    rows.append({
        "period": fy, "scenario": "base_M7_own_ebitda_source", "ebitda_lb_musd": round(m["ebitda"], 1),
        "capex_musd": round(m["capex"], 1), "sbc_musd": round(m["sbc"], 1),
        "fcf_musd": round(m["fcf"], 1), "fcf_ex_sbc_musd": round(m["fcf"] - m["sbc"], 1),
        "diluted_shares_m": round(m["shares"], 1), "mktcap_musd": round(mktcap, 1),
        "fcf_yield_pct": round(100 * m["fcf"] / mktcap, 3),
        "fcf_exsbc_yield_pct": round(100 * (m["fcf"] - m["sbc"]) / mktcap, 3),
    })

with open("data/processed/pitch_model_v2/receipts/C8/c8_fy_fcf_by_scenario.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)

print(json.dumps(rows, indent=2))
