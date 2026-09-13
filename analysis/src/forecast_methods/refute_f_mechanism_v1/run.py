"""Audit F's mechanism without importing rnpl_v2 or refitting coefficients."""
from pathlib import Path
import hashlib
import json
import sys
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
from kernel_engine_v2 import engine

OUT = ROOT / "data/processed/forecast_methods/refute_f_mechanism_v1"
KPI = ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv"
FIT = ROOT / "data/processed/forecast_methods/kernel_phi_v2/A1_phi_estimates.csv"
D1 = ROOT / "data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv"
OLD = ROOT / "data/processed/forecast_methods/rnpl_v2"
REG = ROOT / "data/processed/forecast_methods/registry/rnpl-v2__revenue_next_q.csv"


def main():
    started = time.perf_counter()
    p = pd.read_csv(KPI)
    p["q"] = p.quarter.map(lambda q: pd.Period("20" + q[2:] + "Q" + q[0], freq="Q"))
    p = p.set_index("q").sort_index()
    fits = pd.read_csv(FIT)
    chosen = fits[fits["sample"].str.startswith("ex") & fits.spec.eq("pooled")]
    assert len(chosen) == 1
    fit = chosen.iloc[0]
    weights = [float(fit[f"phi_{k}"]) for k in range(5)]
    assert min(weights) >= 0 and np.isclose(sum(weights), 1)
    rows = []
    for q, r in p.iterrows():
        if any(q-lag not in p.index for lag in range(4)):
            continue
        # Each booking vintage contributes its remaining recognition-weight tail.
        fee_stock = 0.0
        for lag in range(4):
            gbv = p.loc[q-lag, "gbv_musd"]
            for arrival in range(1, 5-lag):
                season = (q+arrival).quarter
                fee_stock += gbv * weights[lag+arrival] * fit[f"c_Q{season}"] / 100
        rows.append({"quarter": str(q), "season": q.quarter,
                     "fee_stock_musd": fee_stock,
                     "uf_musd": r.unearned_fees_musd,
                     "paid_fraction": r.unearned_fees_musd / fee_stock})
    d = pd.DataFrame(rows)
    reference = d[d.quarter.between("2022Q1", "2025Q2")].groupby("season").paid_fraction.agg(["mean", "count"])
    d["norm_paid_fraction"] = d.season.map(reference["mean"])
    d["norm_n"] = d.season.map(reference["count"])
    d["excess_unpaid_pp"] = 100*(d.norm_paid_fraction-d.paid_fraction)
    # If settlement timing and booked exposure are unchanged, a lower total fee
    # yield can produce exactly the same modeled excess. This is a falsification
    # counterfactual, not an estimate that such fee changes actually occurred.
    d["fee_only_yield_ratio_to_norm"] = d.paid_fraction/d.norm_paid_fraction
    d["fee_only_yield_decline_pct"] = 100*(1-d.fee_only_yield_ratio_to_norm)
    d["uf_shortfall_to_norm_musd"] = d.fee_stock_musd*d.norm_paid_fraction-d.uf_musd
    recent = d[d.quarter.isin(["2025Q4", "2026Q1", "2026Q2"])].copy()
    prior = pd.read_csv(OLD / "paid_backlog.csv")
    comparison = recent.merge(prior[["quarter", "excess_unpaid_pp"]], on="quarter", suffixes=("_audit", "_package"))
    err = float(abs(comparison.excess_unpaid_pp_audit-comparison.excess_unpaid_pp_package).max())
    assert err < 1e-8, err
    claimed = {"2025Q4": 2.0, "2026Q2": 9.7}
    for q, x in claimed.items():
        assert abs(recent.set_index("quarter").loc[q, "excess_unpaid_pp"]-x) < .05

    paths = pd.read_csv(OLD / "live_scenarios.csv")
    team = paths[(paths.nights_variant == "team") & (paths.quarter == "2026Q4")].iloc[0]
    lam = engine.pit_lambda(4, "2026-09-13")
    # Independent path multiplication; the fixed ADR is a disclosed model input.
    q3_nights = p.loc[pd.Period("2025Q3"), "nights_m"] * 1.099
    q3_gbv = q3_nights * team.fixed_q3_adr_usd
    pure = ((2/3)*q3_gbv+(1/3)*p.loc[pd.Period("2026Q2"), "gbv_musd"])*lam["lambda_pct"]/100
    assert abs(pure-team.pure_kernel_revenue_musd) < 1e-8
    grid = pd.read_csv(D1)
    central = grid[(grid.share_path == "share_central") & (grid.adr_ratio == "adr_plus25") &
                   (grid.delta_scenario == "delta_4pp") & (grid.lead_time == "lead_2.2") &
                   (grid.lead_uplift == "uplift_7") & (grid.rebook_offset == .25)]
    assert len(central) == 1
    night_share = float(central.iloc[0].rnpl_nights_share_4q26_pct)/100
    dollar_share = night_share*1.25/(1-night_share+night_share*1.25)
    loss_fraction = dollar_share*.04
    stress = pure*(1-loss_fraction)
    assert abs(stress-team.registered_revenue_musd) < 1e-8
    assert abs(stress-3185) < .5
    registry = pd.read_csv(REG)
    registered = registry[(registry.spec_id == "team") & (registry.quarter == "2026Q4")]
    assert len(registered) == 2 and np.allclose(registered.point, stress)
    assert set(registry.window) == {"LIVE"}
    sensitivities = pd.DataFrame([
        {"case": "Published gross assumed loss", "n": 1, "revenue_musd": stress},
        {"case": "If 25 percent rebook elsewhere on Airbnb", "n": 1, "revenue_musd": pure*(1-loss_fraction*.75)},
        {"case": "If half the loss is already embedded", "n": 1, "revenue_musd": pure*(1-loss_fraction*.5)},
        {"case": "If all loss is already embedded", "n": 1, "revenue_musd": pure},
        {"case": "Exact 23 percent flow share, 4pp", "n": 1, "revenue_musd": pure*(1-.23*.04)},
    ])
    routing = {"constant_total_fee_payer_change_uf_delta": 0.0,
               "equation": "UF = host_fee + guest_fee; d(host_fee) = -d(guest_fee) implies d(UF) = 0",
               "interpretation": "Pure payer migration cannot create unpaid share. Total fee yield and exposure may change."}
    result = {"as_of": "2026-09-13", "verdict": "SURVIVED",
              "stock_max_abs_difference_pp": err,
              "q4_lambda_pct": lam["lambda_pct"], "q4_lambda_n": lam["n_train"],
              "q4_pure_revenue_musd": pure, "q4_implied_gbv_share": dollar_share,
              "q4_leakage_fraction": loss_fraction, "q4_stress_revenue_musd": stress,
              "q4_gross_loss_musd": pure-stress,
              "w1_historical_scenario_n": 0, "w2_historical_scenario_n": 0,
              "routing": routing, "runtime_seconds": time.perf_counter()-started}
    OUT.mkdir(parents=True, exist_ok=True)
    recent.to_csv(OUT / "fee_only_counterfactual.csv", index=False)
    comparison.to_csv(OUT / "endpoint_reproduction.csv", index=False)
    sensitivities.to_csv(OUT / "incrementality_sensitivity.csv", index=False)
    (OUT / "audit_receipt.json").write_text(json.dumps(result, indent=2), encoding="utf8")
    source_paths = [KPI, FIT, D1, OLD/"paid_backlog.csv", OLD/"live_scenarios.csv", REG,
                    ROOT/"data/raw/regulatory/quantification/abnb_2025_10k.json",
                    ROOT/"data/raw/regulatory/quantification/abnb_2026q2_10q.html", Path(__file__)]
    pd.DataFrame([{"path": str(f.relative_to(ROOT)), "sha256": hashlib.sha256(f.read_bytes()).hexdigest()} for f in source_paths]).to_csv(OUT/"input_manifest.csv",index=False)
    print(json.dumps(result, indent=2))
    print(recent.to_string(index=False))
    print(sensitivities.to_string(index=False))


if __name__ == "__main__":
    main()
