"""R2 — recompute the 3Q26 revenue objects from committed repo files.

Reads only. Writes r2_objects.csv + r2_objects.json into this receipt folder.

Objects:
  1. kernel        lambda_Q3 x (2/3 GBV_2Q26 + 1/3 GBV_1Q26), from the PRINTED GBV
  2. guide+cushion guide midpoint x (1 + trailing-8 mean cushion)
  3. bridge v3     data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv, 3Q26
  4. street        L0 vintage register, LSEG-family as-of 2026-09-11 (V1 / DEC-0013)
  5. card          the recommended carried value, by scenario

Run:
  PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id R2 \
    --watch data/processed/forecast_methods/live_block_v2 \
    --cmd "python3 data/processed/pitch_model_v2/receipts/R2/r2_recompute.py"
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
rows: list[dict] = []


def add(item, scenario, period, point, unit, note):
    rows.append({"item": item, "scenario": scenario, "period": period,
                 "point": point, "unit": unit, "note": note})


# ---------------------------------------------------------------- 1. kernel
kpi = pd.read_csv(ROOT / "data/processed/airbnb_quarterly_kpis.csv")
g1 = float(kpi.loc[kpi.quarter == "2026Q1", "gbv_usd_b"].iloc[0])
g2 = float(kpi.loc[kpi.quarter == "2026Q2", "gbv_usd_b"].iloc[0])
base_musd = (2 / 3) * g2 * 1000 + (1 / 3) * g1 * 1000
LAM_DEC = 0.1724                     # DEC-0006, rounded to 2dp
LAM_PKG = 0.17239361851242432        # kernel_lambda 3-cell mean, full precision
kern_dec = LAM_DEC * base_musd
kern_pkg = LAM_PKG * base_musd

# the three Q3 cells the 3-cell mean is built from
wedge = pd.read_csv(ROOT / "data/processed/forecast_methods/live_block_v2/"
                    "06_seasonal_history_and_kernel_wedge.csv")
cells = wedge[wedge.quarter.isin(["2023Q3", "2024Q3", "2025Q3"])]
lam_cells = cells.lambda_pct.tolist()
lam_mean = sum(lam_cells) / 3

# ------------------------------------------------------- 2. guide + cushion
led = pd.read_csv(ROOT / "data/processed/overnight/02_guidance_ledger.csv")
grow = led[(led.target_period == "3Q26") & (led.metric == "revenue_usd_m")].iloc[0]
guide_lo, guide_hi, guide_mid = float(grow.value_low), float(grow.value_high), float(grow.value_mid)
cush = pd.read_csv(ROOT / "data/processed/forecast_methods/guidance_policy/02_cushion_pit.csv")
crow = cush[cush.guide_date == "2026-08-06"].iloc[0]
c_mean_full = float(crow.c_mean_pct) / 100        # 1.856743%
C_DEC = 0.01857                                   # DEC-0001, rounded
gc_full = guide_mid * (1 + c_mean_full)
gc_dec = guide_mid * (1 + C_DEC)
gc_median = guide_mid * (1 + float(crow.c_median_pct) / 100)

# ------------------------------------------------------------- 3. bridge v3
br = pd.read_csv(ROOT / "data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv")
b3 = br[br.quarter == "3Q26"].iloc[0]
bridge_rev = float(b3.revenue_musd)
bridge_lagged = float(b3.lagged_gbv_busd) * 1000
bridge_lam = float(b3.conversion_mean)
bridge_lo, bridge_hi = float(b3.revenue_low), float(b3.revenue_high)
bridge_gbv_3q26 = float(b3.gbv_3q26_assumed_busd) if pd.notna(b3.gbv_3q26_assumed_busd) else None
card = pd.read_csv(ROOT / "data/processed/h2_bridge_v3/h2_bridge_v3_card_check.csv")
c3 = card[card.quarter == "3Q26"].set_index("object")["bridge"]
bridge_nights, bridge_adr = float(c3["nights, mm"]), float(c3["ADR $"])
bridge_gbv = float(c3["GBV, $bn"]) * 1000

# ---------------------------------------------------------------- 4. street
STREET = 4744.0   # V1 dossier / DEC-0013, LSEG-family as-of 2026-09-11

# --------------------------------------- 5. scenario card on decided inputs
NIGHTS = {"base": 146.3, "short": 145.0, "breaker": 147.0}          # DEC-0004
ADR = {"base": 176.88, "short": 173.80, "breaker": 178.47}          # DEC-0008/0009
gbv_sc = {s: NIGHTS[s] * ADR[s] for s in NIGHTS}
tr_tie = kern_pkg / gbv_sc["base"]        # take rate that ties base to the kernel
card_sc = {s: gbv_sc[s] * tr_tie for s in NIGHTS}

LIVE_TR = 0.1814                          # live-block-v2 reconciled printed take rate
rev_at_live_tr = {s: gbv_sc[s] * LIVE_TR for s in NIGHTS}

# -------------------------------------------------------------- emit rows
for s in ("base", "short", "breaker"):
    add("revenue_kernel_musd", s, "3Q26", round(kern_pkg, 1), "musd",
        f"lambda_Q3 x (2/3 GBV_2Q26 + 1/3 GBV_1Q26); SCENARIO-INVARIANT (both GBV are printed)")
    add("revenue_guide_cushion_musd", s, "3Q26", round(gc_dec, 1), "musd",
        "guide mid 4730 x (1 + 1.857%); SCENARIO-INVARIANT")
    add("revenue_bridge_musd", s, "3Q26", round(bridge_rev, 1), "musd",
        "h2_bridge_v3 3Q26; IDENTICAL to the kernel by construction; SCENARIO-INVARIANT")
    add("revenue_street_musd", s, "3Q26", STREET, "musd",
        "LSEG-family as-of 2026-09-11 (V1, DEC-0013); SCENARIO-INVARIANT")
    add("revenue_card_musd", s, "3Q26", round(card_sc[s], 1), "musd",
        f"nights x ADR x implied take rate {tr_tie*100:.4f}% (held fixed so base ties to the kernel)")

obj = {
    "printed_gbv_used_musd": {"1Q26": g1 * 1000, "2Q26": g2 * 1000},
    "kernel_base_musd": base_musd,
    "lambda_q3_cells_pct": {"2023Q3": lam_cells[0], "2024Q3": lam_cells[1], "2025Q3": lam_cells[2]},
    "lambda_q3_mean_pct": lam_mean,
    "kernel_at_DEC0006_lambda_1724": kern_dec,
    "kernel_at_package_lambda": kern_pkg,
    "guide": {"low": guide_lo, "high": guide_hi, "mid": guide_mid},
    "cushion_pct": {"mean_full": crow.c_mean_pct, "mean_DEC0001": 1.857, "median": crow.c_median_pct},
    "guide_cushion_at_DEC0001": gc_dec,
    "guide_cushion_at_full_precision": gc_full,
    "guide_cushion_at_median": gc_median,
    "bridge": {"revenue_musd": bridge_rev, "lagged_gbv_musd": bridge_lagged,
               "conversion_mean": bridge_lam, "low": bridge_lo, "high": bridge_hi,
               "nights_m": bridge_nights, "adr_usd": bridge_adr, "gbv_musd": bridge_gbv,
               "implied_take_rate_pct": 100 * bridge_rev / bridge_gbv},
    "bridge_equals_kernel": {
        "lagged_gbv_diff_musd": bridge_lagged - base_musd,
        "lambda_diff_pp": 100 * (bridge_lam - LAM_PKG),
        "revenue_diff_musd": bridge_rev - kern_pkg},
    "street_musd": STREET,
    "live_block_v2_revenue_musd": 4816.1,
    "scenario_gbv_musd": gbv_sc,
    "implied_take_rate_pct_tying_base_to_kernel": 100 * tr_tie,
    "card_musd": card_sc,
    "revenue_if_take_rate_held_at_live_block_1814": rev_at_live_tr,
}

pd.DataFrame(rows).to_csv(OUT / "r2_objects.csv", index=False)
(OUT / "r2_objects.json").write_text(json.dumps(obj, indent=2, default=float))

print(f"printed GBV used  1Q26 = ${g1*1000:,.0f}M   2Q26 = ${g2*1000:,.0f}M")
print(f"kernel base       2/3 x {g2*1000:,.1f} + 1/3 x {g1*1000:,.1f} = {base_musd:,.4f} musd")
print(f"lambda_Q3 cells   {lam_cells[0]:.6f} / {lam_cells[1]:.6f} / {lam_cells[2]:.6f}  mean {lam_mean:.6f}%")
print(f"KERNEL            {LAM_DEC:.4f} x {base_musd:,.4f} = {kern_dec:,.2f} musd   (DEC-0006 lambda 17.24%)")
print(f"KERNEL            {LAM_PKG:.10f} x {base_musd:,.4f} = {kern_pkg:,.2f} musd   (package lambda)")
print(f"GUIDE+CUSHION     {guide_mid:,.0f} x (1 + {C_DEC:.5f}) = {gc_dec:,.2f} musd   (DEC-0001 1.857%)")
print(f"GUIDE+CUSHION     {guide_mid:,.0f} x (1 + {c_mean_full:.10f}) = {gc_full:,.2f} musd (full precision)")
print(f"GUIDE+CUSHION med {guide_mid:,.0f} x (1 + median) = {gc_median:,.2f} musd")
print(f"BRIDGE v3         {bridge_rev:,.4f} musd = {bridge_lam:.10f} x {bridge_lagged:,.4f}")
print(f"  bridge - kernel: lagged GBV {bridge_lagged-base_musd:+.6f} musd, "
      f"lambda {100*(bridge_lam-LAM_PKG):+.10f} pp, revenue {bridge_rev-kern_pkg:+.6f} musd")
print(f"  bridge own card: nights {bridge_nights:.3f}m x ADR ${bridge_adr:.3f} = GBV ${bridge_gbv:,.1f}M"
      f"  -> implied take rate {100*bridge_rev/bridge_gbv:.4f}%")
print(f"STREET            {STREET:,.0f} musd (LSEG-family 2026-09-11)")
print(f"LIVE BLOCK v2     4816.1 musd (optimal-mix bma_logscore combination, NOT guide x cushion)")
print()
print(f"decided GBV (D1 nights x D4 ADR): "
      + "  ".join(f"{s} {gbv_sc[s]:,.1f}" for s in ("base", "short", "breaker")))
print(f"take rate tying base to the kernel: {100*tr_tie:.4f}%  "
      f"(bridge card {100*bridge_rev/bridge_gbv:.4f}%, live-block-v2 18.1399%, 3Q25 printed 17.882%)")
print(f"CARD              "
      + "  ".join(f"{s} {card_sc[s]:,.1f}" for s in ("base", "short", "breaker")))
print(f"same GBV at the live-block take rate 18.14%: "
      + "  ".join(f"{s} {rev_at_live_tr[s]:,.1f}" for s in ("base", "short", "breaker")))
print(f"wrote {OUT/'r2_objects.csv'} and {OUT/'r2_objects.json'}")
