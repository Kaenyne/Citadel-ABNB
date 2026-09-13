"""Independently recompute RNPL stock and LIVE scenario identities from inputs."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
from kernel_engine_v2 import engine as K
from harness_v1_1 import RUN_DATE

OUT = ROOT / "data/processed/forecast_methods"
source = pd.read_csv(ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv")
source["quarter"] = source.quarter.map(lambda s: "20" + s[2:] + "Q" + s[0])
source = source.set_index("quarter")
phi = pd.read_csv(OUT / "kernel_phi_v2/A1_phi_estimates.csv")
fit = phi[phi["sample"].str.startswith("ex") & phi.spec.eq("pooled")].iloc[0]
backlog = pd.read_csv(OUT / "rnpl_v2/paid_backlog.csv").set_index("quarter")
recomputed = []
for q in backlog.index:
    if q < "2022Q1":
        continue
    quarter = pd.Period(q, freq="Q")
    stock = 0.0
    for ahead in range(1, 5):
        season = (quarter + ahead).quarter
        for lag in range(5 - ahead):
            stock += float(source.loc[str(quarter - lag), "gbv_musd"]) * fit[f"phi_{ahead+lag}"] * fit[f"c_Q{season}"] / 100
    np.testing.assert_allclose(stock, backlog.loc[q, "kernel_fee_stock_musd"], rtol=0, atol=1e-8)
    recomputed.append({"quarter": q, "season": quarter.quarter,
                       "unpaid": 1 - float(source.loc[q, "unearned_fees_musd"]) / stock})
recomputed = pd.DataFrame(recomputed)
norm = recomputed[recomputed.quarter.le("2025Q2")].groupby("season").unpaid.mean()
excess = []
for q in ("2025Q4", "2026Q1", "2026Q2"):
    row = recomputed[recomputed.quarter.eq(q)].iloc[0]
    value = 100 * (row.unpaid - norm.loc[row.season])
    np.testing.assert_allclose(value, backlog.loc[q, "excess_unpaid_pp"], rtol=0, atol=1e-9)
    excess.append({"quarter": q, "excess_unpaid_pp": value})

scenarios = pd.read_csv(OUT / "rnpl_v2/live_scenarios.csv")
q3 = K.kernel_forecast("2026Q3", str(RUN_DATE))["point"]
lam4 = K.pit_lambda(4, str(RUN_DATE))["lambda_pct"]
b2 = float(source.loc["2026Q2", "gbv_musd"])
for row in scenarios.itertuples():
    nights = float(source.loc["2025Q3", "nights_m"]) * (1 + row.q3_nights_yoy_pct/100)
    gbv3 = nights * row.fixed_q3_adr_usd
    pure = q3 if row.quarter == "2026Q3" else (K.WEIGHT*gbv3 + (1-K.WEIGHT)*b2)*lam4/100
    np.testing.assert_allclose(pure, row.pure_kernel_revenue_musd, rtol=0, atol=1e-8)
    np.testing.assert_allclose(pure*(1-row.applied_L), row.registered_revenue_musd, rtol=0, atol=1e-8)
    if row.nights_variant == "theo" and row.quarter == "2026Q4":
        assert row.applied_L == 0, "overlapping cancellation tail compounded"
assert scenarios[scenarios.quarter.eq("2026Q3")].registered_revenue_musd.nunique() == 1
report = {"verdict": "PASS", "stock_cells_from_raw_GBV_and_frozen_phi": len(recomputed),
          "excess_cells": excess, "scenario_cells": len(scenarios),
          "q3_lag_invariance": True, "theo_q4_no_extra_overlapping_leakage": True,
          "limitation": "Checks arithmetic and scenario plumbing; does not identify RNPL causality or validate D1 assumptions."}
(OUT / "lane2_validation_v1/f_independent_review.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report, indent=2))
