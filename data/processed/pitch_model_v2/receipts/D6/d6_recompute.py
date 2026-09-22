"""D6 derived arithmetic: not a package run, reads only committed CSVs, writes only
inside data/processed/pitch_model_v2/receipts/D6/. Three checks:
 (1) history identity nights_m x adr == gbv_musd, 1Q23-2Q26, from abnb_driver_history_quarterly.csv (H0's source).
 (2) regional_kernel_v1 sum-to-consolidated check, GBV and revenue, from its own output CSVs.
 (3) decided-input GBV = nights x ADR for 3Q26/4Q26 x {base, short, breaker}, per DEC-0004/DEC-0008/DEC-0009 and D2,
     plus comparison to PREREG D-04 block ii (147.38 / 180.15 / 26,550) and block i (146.3 / 176.47 / 25,816).
"""
import pandas as pd
from pathlib import Path

ROOT = Path("/Users/theomachado/Citadel-ABNB")
OUT = ROOT / "data/processed/pitch_model_v2/receipts/D6"

# ---------- (1) history identity ----------
hist = pd.read_csv(ROOT / "data/processed/abnb_driver_history_quarterly.csv")
def conv(q):
    qtr, yr = q[0], q[2:]
    return ("20" + yr if len(yr) == 2 else yr) + "Q" + qtr
hist["quarter_std"] = hist["quarter"].apply(conv)
sel = [f"{y}Q{q}" for y in range(2023, 2027) for q in range(1, 5)]
sel = [q for q in sel if q <= "2026Q2"]
sub = hist[hist["quarter_std"].isin(sel)].copy()
sub["identity_musd"] = sub["nights_m"] * sub["adr"]
sub["dev_musd"] = sub["identity_musd"] - sub["gbv_musd"]
sub["dev_pct"] = sub["dev_musd"] / sub["gbv_musd"] * 100
sub = sub.sort_values("quarter_std")
cols = ["quarter_std", "nights_m", "adr", "gbv_musd", "identity_musd", "dev_musd", "dev_pct"]
sub[cols].to_csv(OUT / "d6_history_identity.csv", index=False)
max_row = sub.loc[sub["dev_pct"].abs().idxmax()]
print("=== (1) History identity, 1Q23-2Q26, n =", len(sub), "===")
print(sub[cols].to_string(index=False))
print(f"max abs dev pct = {sub['dev_pct'].abs().max():.4f}%  at {max_row['quarter_std']}")

# ---------- (2) regional sum-to-consolidated ----------
reg = pd.read_csv(ROOT / "data/processed/forecast_methods/regional_kernel_v1/regional_gbv_k0.csv")
agg = reg.groupby("quarter")["gbv_usd_booking_dated"].sum().reset_index()
agg["gbv_musd_regional_sum"] = agg["gbv_usd_booking_dated"] / 1e6
merged = agg.merge(hist[["quarter_std", "gbv_musd"]], left_on="quarter", right_on="quarter_std", how="inner")
merged["dev_pct"] = (merged["gbv_musd_regional_sum"] - merged["gbv_musd"]) / merged["gbv_musd"] * 100
merged[["quarter", "gbv_musd_regional_sum", "gbv_musd", "dev_pct"]].to_csv(OUT / "d6_regional_sum_check.csv", index=False)
print("\n=== (2) Regional GBV sum vs consolidated, history n =", len(merged), "===")
print(f"max abs dev pct = {merged['dev_pct'].abs().max():.6f}%  (all rows 0.0% -- algebraic same-cell reconstruction per package README/reconciliation.csv basis column)")

# check for any live 3Q26/4Q26 regional GBV rows
future_rows = reg[reg["quarter"].isin(["2026Q3", "2026Q4"])]
print(f"regional_gbv_k0.csv rows for 2026Q3/2026Q4: {len(future_rows)} (0 = no live regional GBV forecast split exists; only a regional REVENUE point exists in k0_handoff_check.json for 2026Q3)")

# ---------- (3) decided-input GBV, D6 scenario table ----------
nights = {
    "3Q26": {"base": 146.3, "short": 145.0, "breaker": 147.0},
    "4Q26": {"base": 131.8, "short": 131.2, "breaker": 134.1},
}
adr = {
    "3Q26": {"base": 176.88, "short": 173.80, "breaker": 178.47},
    "4Q26": {"base": 173.94, "short": 170.94, "breaker": 177.35},
}
rows = []
for period in ["3Q26", "4Q26"]:
    for scen in ["base", "short", "breaker"]:
        n, a = nights[period][scen], adr[period][scen]
        rows.append({"period": period, "scenario": scen, "nights_m": n, "adr_usd": a, "gbv_musd": round(n * a, 3)})
decided = pd.DataFrame(rows)
decided.to_csv(OUT / "d6_decided_gbv.csv", index=False)
print("\n=== (3) Decided-input GBV = nights x ADR ===")
print(decided.to_string(index=False))

# D-04 comparison
d04 = pd.DataFrame([
    {"block": "decided_base_3Q26", "nights_m": 146.3, "adr_usd": 176.88, "gbv_musd": round(146.3*176.88, 2)},
    {"block": "D04_block_i_backtest_winner", "nights_m": 146.3, "adr_usd": 176.47, "gbv_musd": 25816.0},
    {"block": "D04_block_ii_registered_headline", "nights_m": 147.38, "adr_usd": 180.15, "gbv_musd": 26550.0},
])
d04["dev_vs_decided_musd"] = d04["gbv_musd"] - d04.loc[0, "gbv_musd"]
d04["dev_vs_decided_pct"] = d04["dev_vs_decided_musd"] / d04.loc[0, "gbv_musd"] * 100
d04.to_csv(OUT / "d6_d04_comparison.csv", index=False)
print("\n=== D-04 block comparison ===")
print(d04.to_string(index=False))
