"""Independent arithmetic audit of F; reads source files and writes only new receipts."""
from pathlib import Path
import hashlib
import json
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/forecast_methods/refute_f_vintage_v1"
F = ROOT / "data/processed/forecast_methods/rnpl_v2"


def shift(q, k):
    return str(pd.Period(q, freq="Q") + k)


def stock(p, fit):
    # Sum each old booking cohort's still-unrecognized seasonal fee contribution.
    gbv = p.set_index("quarter").gbv_musd.to_dict()
    rows = []
    for r in p.itertuples():
        if any(shift(r.quarter, -j) not in gbv for j in range(4)):
            continue
        value = 0.0
        for age in range(4):
            for lag in range(age + 1, 5):
                landing = (r.season + lag - age - 1) % 4 + 1
                value += gbv[shift(r.quarter, -age)] * fit[f"phi_{lag}"] * fit[f"c_Q{landing}"] / 100
        rows.append(dict(quarter=r.quarter, season=r.season, fee_stock_musd=value,
                         unearned_fees_musd=r.unearned_fees_musd,
                         unpaid_share=1-r.unearned_fees_musd/value))
    result = pd.DataFrame(rows)
    norms = result[result.quarter.between("2022Q1", "2025Q2")].groupby("season").unpaid_share.agg(["mean", "count"])
    result["norm"] = result.season.map(norms["mean"])
    result["norm_n"] = result.season.map(norms["count"])
    result["excess_unpaid_pp"] = 100*(result.unpaid_share-result.norm)
    return result


def estimate(rows, variant):
    sample = rows.sort_values("quarter")
    if variant == "ex_covid":
        sample = sample[sample.nights_yoy_pct.notna() & (sample.nights_yoy_pct.abs() <= 25)]
    elif variant == "last3":
        sample = sample.tail(3)
    if len(sample) == 0:
        raise ValueError("empty lambda sample")
    weights = np.exp2(-np.arange(len(sample)-1, -1, -1)/2) if variant == "ewm" else np.ones(len(sample))
    return float(np.average(sample.lam, weights=weights)), sample


def main():
    t0 = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    paths = {
        "kpi": ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv",
        "coefficients": ROOT / "data/processed/forecast_methods/kernel_phi_v2/A1_phi_estimates.csv",
        "D1": ROOT / "data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv",
        "registry": ROOT / "data/processed/forecast_methods/registry/rnpl-v2__revenue_next_q.csv",
        "published_stock": F / "paid_backlog.csv", "live": F / "live_scenarios.csv",
    }
    frames = {k: pd.read_csv(v) for k,v in paths.items()}
    p = frames["kpi"].copy()
    p["quarter"] = p.quarter.map(lambda q: "20"+q[2:]+"Q"+q[0])
    p["season"] = p.quarter.str[-1].astype(int)
    p = p.sort_values("quarter")
    assert p.quarter.is_unique and p.quarter.max() == "2026Q2"
    fits = frames["coefficients"]
    f = fits[(fits["sample"] == "ex_covid_nightsyoy_25") & (fits.spec == "pooled")]
    assert len(f) == 1
    rebuilt = stock(p, f.iloc[0])
    joined = rebuilt.merge(frames["published_stock"][["quarter", "kernel_fee_stock_musd", "excess_unpaid_pp"]], on="quarter", suffixes=("_audit", "_published"), validate="one_to_one")
    max_stock_error = float((joined.fee_stock_musd-joined.kernel_fee_stock_musd).abs().max())
    max_excess_error = float((joined.excess_unpaid_pp_audit-joined.excess_unpaid_pp_published).abs().max())
    assert max_stock_error < 1e-8 and max_excess_error < 1e-10
    rebuilt.to_csv(OUT / "independent_stock.csv", index=False)
    # Remove all future/actual revenue inputs: the independent stock code never reads them.
    stripped = p[["quarter", "season", "gbv_musd", "unearned_fees_musd"]]
    pd.testing.assert_frame_equal(stock(stripped, f.iloc[0]), rebuilt)
    endpoint = rebuilt[rebuilt.quarter.isin(["2025Q4", "2026Q1", "2026Q2"])].copy()
    assert endpoint.excess_unpaid_pp.round(1).tolist() == [2.0, 8.0, 9.7]
    # Equivalent paid/booked ratio: future revenue denominators must cancel exactly.
    denominator_errors = []
    published = frames["published_stock"].set_index("quarter")
    for row in endpoint.itertuples():
        alloc = published.loc[row.quarter, "alloc_factor"]
        carried = published.loc[row.quarter, "carried_next_revenue_musd"]
        for denominator in [3000.0, 4730.0, 6000.0]:
            share = 1-(row.unearned_fees_musd/denominator*alloc)/(carried/denominator)
            denominator_errors.append(abs(share-row.unpaid_share))
    assert max(denominator_errors) < 1e-14
    # Three existing pooled fits show the sensitivity of the model-dependent stock.
    sensitivity = []
    for fit in fits[fits.spec == "pooled"].to_dict("records"):
        alternative = stock(stripped, fit)
        for r in alternative[alternative.quarter.isin(endpoint.quarter)].itertuples():
            sensitivity.append(dict(fit_sample=fit["sample"], fit_n=fit["n"], fit_n_params=fit["n_params"],
                                    quarter=r.quarter, n_norm=r.norm_n, excess_unpaid_pp=r.excess_unpaid_pp,
                                    basis="retrospective structural sensitivity; not independent evidence"))
    pd.DataFrame(sensitivity).to_csv(OUT / "frozen_fit_sensitivity.csv", index=False)
    # Independently calculate K0's lambda selection from the same primitive panel.
    lookup = p.set_index("quarter").gbv_musd.to_dict()
    p["base"] = p.quarter.map(lambda q: 2/3*lookup.get(shift(q,-1), np.nan)+1/3*lookup.get(shift(q,-2), np.nan))
    p["lam"] = 100*p.revenue_musd/p.base
    history = p.dropna(subset=["lam"])
    w = history[history.quarter.between("2023Q1", "2026Q2")]
    candidates = []
    for variant in ["ex_covid", "last3", "ewm"]:
        errors = []
        for row in w.itertuples():
            train = w[(w.season == row.season) & (w.quarter != row.quarter)]
            lam, _ = estimate(train, variant)
            errors.append(100*((lam/100*row.base)/row.revenue_musd-1))
        candidates.append(dict(variant=variant, n=len(errors), W1_loo_rmse_pct=np.sqrt(np.mean(np.square(errors)))))
    selection = pd.DataFrame(candidates).sort_values("W1_loo_rmse_pct", kind="stable")
    chosen = selection.iloc[0].variant
    lam4, train4 = estimate(history[history.season == 4], chosen)
    selection.to_csv(OUT / "lambda_selection.csv", index=False)
    train4[["quarter", "lam"]].to_csv(OUT / "q4_lambda_training.csv", index=False)
    live = frames["live"]
    target = live[(live.nights_variant == "team") & (live.quarter == "2026Q4")]
    assert len(target) == 1
    target = target.iloc[0]
    # This ADR is an explicitly declared conditional input, not a forecast measured by this audit.
    adr = float(target.fixed_q3_adr_usd)
    q3_nights = float(p.set_index("quarter").loc["2025Q3", "nights_m"])*(1+9.9/100)
    q3_gbv = q3_nights*adr
    q4_base = 2/3*q3_gbv+1/3*lookup["2026Q2"]
    pure = q4_base*lam4/100
    grid = frames["D1"]
    cell = grid[(grid.share_path == "share_central") & (grid.adr_ratio == "adr_plus25") &
                (grid.delta_scenario == "delta_4pp") & (grid.lead_time == "lead_2.2") &
                (grid.lead_uplift == "uplift_7") & (grid.rebook_offset == .25)]
    assert len(cell) == 1
    cell = cell.iloc[0]
    ns = cell.rnpl_nights_share_4q26_pct/100
    gbv_share = ns*1.25/(1-ns+ns*1.25)
    leakage = gbv_share*cell.delta_pp_applied/100
    stressed = pure*(1-leakage)
    assert abs(stressed-target.registered_revenue_musd) < 1e-8
    registry = frames["registry"]
    assert len(registry) == 12
    assert (registry.window == "LIVE").all()
    assert (registry.vintage_date == "2026-09-13").all()
    assert (registry.knowable_from == "2026-09-13").all()
    assert (pd.to_datetime(registry.vintage_date) >= pd.Timestamp("2026-09-11")).all()
    assert registry.notes.str.contains("D1 assumptions dated 2026-09-11", regex=False).all()
    assert registry.notes.str.contains("no causal inference", regex=False).all()
    assert set(registry.prior_basis) == {"PIT", "full_sample"}
    pairs = registry.pivot(index=["spec_id", "quarter"], columns="prior_basis", values="point")
    assert (pairs.PIT == pairs.full_sample).all()
    hashes = []
    for name,path in paths.items():
        hashes.append(dict(input=name, path=str(path.relative_to(ROOT)).replace("\\", "/"), sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    pd.DataFrame(hashes).to_csv(OUT / "input_hashes.csv", index=False)
    receipt = dict(
        audit_date="2026-09-13", audit_basis="independent arithmetic; no package run functions imported",
        max_stock_error_musd=max_stock_error, max_excess_error_pp=max_excess_error,
        endpoints=endpoint[["quarter", "norm_n", "excess_unpaid_pp"]].to_dict("records"),
        future_denominator_max_share_error=max(denominator_errors),
        lambda_variant=chosen, lambda_q4_pct=lam4, lambda_q4_training_n=len(train4),
        q3_declared_conditional_adr_usd=adr, q3_nights_m=q3_nights, q3_gbv_musd=q3_gbv,
        q4_base_musd=q4_base, q4_pure_revenue_musd=pure, q4_gbv_share=gbv_share,
        q4_gross_leakage=leakage, q4_stress_revenue_musd=stressed,
        live_registry_n=len(registry), historical_W1_n=0, historical_W2_n=0,
        stress_difference_musd=pure-stressed, elapsed_seconds=time.perf_counter()-t0,
        result="ARITHMETIC_AND_LIVE_VINTAGES_PASS",
    )
    (OUT / "audit_receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
