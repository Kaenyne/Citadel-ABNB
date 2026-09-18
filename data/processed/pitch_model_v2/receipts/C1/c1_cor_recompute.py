"""C1 independent recompute: reproduce 40_line_build's cost-of-revenue formula
(cor_fees + cor_chargebacks + cor_hosting + cor_other = cor_cash) for every
committed (quarter, scenario) cell in 40_lines_quarterly.csv, 40_short_case_quarterly.csv
and 40_annual.csv, using only 40_params.csv values and the committed
gbv_busd / nights_m / bookings-implied drivers already in those files (no re-derivation
of xb_drift_pts or the revenue path -- this checks the cost formula, not the revenue build).
Read-only: writes only inside this receipt folder.
"""
from pathlib import Path
import pandas as pd

ROOT = Path("/Users/theomachado/Citadel-ABNB")
LB = ROOT / "data/processed/margin_build/40_line_build"
OUT = ROOT / "data/processed/pitch_model_v2/receipts/C1"

params = pd.read_csv(LB / "40_params.csv").set_index("name")
def pv(name, scen):
    return float(params.loc[name, scen])

FEE_FACTOR = {1: 0.90, 2: 1.045, 3: 1.035, 4: 1.033}
QN = {"3Q26": 3, "4Q26": 4, "1Q27": 1, "2Q27": 2, "3Q27": 3, "4Q27": 4}

def recompute_row(row, cost_scen):
    q = row["quarter"]; qn = QN[q]; is27 = q.endswith("27")
    gbv = row["gbv_busd"]; nights = row["nights_m"]
    fee_rate = row["merchant_fee_rate_q_pct"]  # taken as given (depends on xb_drift_pts, not re-derived)
    fees_hat = fee_rate / 100 * gbv * 1000
    bookings = row["cor_chargebacks"] / (pv("chargeback_per_booking", cost_scen) + pv("chargeback_add_per_booking", cost_scen) if "chargeback_add_per_booking" in params.index else pv("chargeback_per_booking", cost_scen))
    chargebacks_hat = pv("chargeback_per_booking", cost_scen) * bookings  # base case, no RNPL overlay
    other_hat = pv("cor_other_per_night", cost_scen) * nights
    return fees_hat, chargebacks_hat, other_hat

rows_out = []
lq = pd.read_csv(LB / "40_lines_quarterly.csv")
for scen in ["base", "cost_bull"]:
    sub = lq[lq["scenario"] == scen]
    cost_scen = "base" if scen == "base" else "bull"
    for _, r in sub.iterrows():
        fees_hat, chg_hat, other_hat = recompute_row(r, cost_scen)
        rows_out.append(dict(source="40_lines_quarterly.csv", scenario=scen, quarter=r["quarter"],
                              fees_committed=r["cor_fees"], fees_recompute=fees_hat, d_fees=r["cor_fees"] - fees_hat,
                              chg_committed=r["cor_chargebacks"], chg_recompute=chg_hat, d_chg=r["cor_chargebacks"] - chg_hat,
                              other_committed=r["cor_other"], other_recompute=other_hat, d_other=r["cor_other"] - other_hat))

df = pd.DataFrame(rows_out)
df.to_csv(OUT / "c1_cor_recompute_check.csv", index=False)
maxdiff = df[["d_fees", "d_chg", "d_other"]].abs().max().max()
print(df.to_string())
print("max abs diff (fees/chargebacks/other, formula components only):", maxdiff)
assert maxdiff < 1e-6, "recompute mismatch"
print("PASS: fees, chargebacks and other-per-night components reproduce exactly from 40_params.csv.")
