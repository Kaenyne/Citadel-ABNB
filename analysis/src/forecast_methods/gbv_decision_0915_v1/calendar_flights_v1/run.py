"""One preregistered flight-timing repair; research dates are never backdated."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
CORE_DIR = ROOT / "analysis/src/forecast_methods/gbv_joint_cohort_v1/quant_v1"
sys.path.insert(0, str(CORE_DIR))
import run as core
import diagnostics as prior

HORIZON = ROOT / "data/processed/forecast_methods/gbv_decision_0915_v1/horizon_v1"
PREREG = ROOT / "docs/revenue-forecast-strategy/05_backtests/GD_CALENDAR_FLIGHT_PREREG_v1.md"
MODELS = ["joint_flight", "joint_noflight", "fixed_flight", "fixed_noflight", "guide_growth", "revenue_growth"]


def calendar_origin(target):
    return pd.Period(target, freq="Q").start_time - pd.Timedelta(days=16)


def training_pairs(panel, flights, asof):
    # A training outcome must be public BEFORE evaluation; each feature is itself
    # reconstructed at the same calendar offset that would precede that outcome.
    records = []
    known = panel[panel.print_date < pd.Timestamp(asof)]
    for row in known.itertuples():
        feature_date = calendar_origin(core.qshift(row.quarter, 1))
        observed = panel[panel.print_date <= feature_date].sort_values("quarter")
        if observed.empty:
            continue
        latest = observed.quarter.iloc[-1]
        if latest != core.qshift(row.quarter, -1):
            continue
        lookup = observed.set_index("quarter").gbv_musd.to_dict()
        if any(q not in lookup for q in [core.qshift(latest, -4), core.qshift(row.quarter, -4)]):
            continue
        try:
            flight = prior.eligible_flight(flights, feature_date, latest)
        except ValueError:
            continue
        growth = lookup[latest] / lookup[core.qshift(latest, -4)] - 1
        actual = row.gbv_musd / lookup[core.qshift(row.quarter, -4)] - 1
        records.append(dict(target=row.quarter, feature_origin=str(feature_date.date()),
                            latest_company_quarter=latest, outcome_publication=str(row.print_date.date()),
                            flight_quarter=flight.quarter, flight_commit_utc=flight.committed_utc.isoformat(),
                            flight_commit_full=flight.commit_full,
                            x=float(flight.eu40_flt_da_yoy / 100 - growth), y=float(actual - growth)))
    return pd.DataFrame(records)


def predict_pair(known, target, phi, joint_lambda, fixed_lambda, growth):
    lookup = known.set_index("quarter").gbv_musd.to_dict()
    latest = max(lookup)
    for p in pd.period_range(core.qshift(latest, 1), target, freq="Q"):
        q = str(p)
        lookup[q] = lookup[core.qshift(q, -4)] * (1 + growth)
    x = np.array([lookup[target], lookup[core.qshift(target, -1)], lookup[core.qshift(target, -2)],
                  np.mean([lookup[core.qshift(target, -3)], lookup[core.qshift(target, -4)]])])
    joint = float(x @ phi * joint_lambda)
    fixed = float((2 / 3 * lookup[core.qshift(target, -1)] + 1 / 3 * lookup[core.qshift(target, -2)]) * fixed_lambda)
    if not np.isfinite([joint, fixed]).all() or min(joint, fixed) <= 0:
        raise ValueError("Invalid forecast dollars")
    return joint, fixed


def metrics(predictions):
    scores, pairs, deletions, gates = [], [], [], []
    rng = np.random.default_rng(core.SEED)
    for window, lower in core.WINDOWS.items():
        d = predictions[predictions.target >= lower]
        wide = d.pivot(index="target", columns="model", values="guide_mid_musd")
        actual = d.drop_duplicates("target").set_index("target").actual_guide_mid_musd.reindex(wide.index)
        errors = wide.sub(actual, axis=0)
        years = np.array([int(q[:4]) for q in errors.index])
        unique_years = np.unique(years)
        for model in MODELS:
            e = errors[model].to_numpy()
            scores.append(dict(window=window, model=model, n=len(e), n_year_clusters=len(unique_years),
                               rmse_musd=float(np.sqrt(np.mean(e ** 2))), mae_musd=float(np.mean(np.abs(e))),
                               bias_musd=float(np.mean(e)), error_sd_musd=float(np.std(e, ddof=1)),
                               worst_abs_miss_musd=float(np.max(np.abs(e)))))
        for candidate in ["joint_flight", "fixed_flight"]:
            own = candidate.replace("flight", "noflight")
            all_pairs = {}
            for baseline in [own, "guide_growth", "revenue_growth"]:
                ec, eb = errors[candidate].to_numpy(), errors[baseline].to_numpy()
                ratio = float(np.sqrt(np.mean(ec ** 2) / np.mean(eb ** 2)))
                csum = np.array([np.sum(ec[years == y] ** 2) for y in unique_years])
                bsum = np.array([np.sum(eb[years == y] ** 2) for y in unique_years])
                chosen = rng.integers(0, len(unique_years), (2000, len(unique_years)))
                ratios = np.sqrt(csum[chosen].sum(axis=1) / bsum[chosen].sum(axis=1))
                deletion_ratios = []
                for kind, groups in [("year", unique_years), ("quarter", errors.index)]:
                    for group in groups:
                        keep = years != group if kind == "year" else errors.index != group
                        dr = float(np.sqrt(np.mean(ec[keep] ** 2) / np.mean(eb[keep] ** 2)))
                        deletion_ratios.append(dr)
                        deletions.append(dict(window=window, candidate=candidate, baseline=baseline,
                                              deletion_kind=kind, excluded=str(group), n=int(sum(keep)), rmse_ratio=dr))
                row = dict(window=window, candidate=candidate, baseline=baseline, n=len(ec),
                           n_year_clusters=len(unique_years), rmse_ratio=ratio, paired_draws=2000,
                           ratio_p05=float(np.quantile(ratios, .05)), ratio_p95=float(np.quantile(ratios, .95)),
                           worst_deletion_ratio=max(deletion_ratios), any_deletion_reversal=max(deletion_ratios) >= 1)
                pairs.append(row)
                all_pairs[baseline] = row
            a, b = all_pairs[own], all_pairs["guide_growth"]
            gates.append(dict(window=window, candidate=candidate, n=len(errors),
                              own_rmse_ratio=a["rmse_ratio"], guide_growth_ratio=b["rmse_ratio"],
                              minimum_n_pass=len(errors) >= 8, own_10pct_pass=a["rmse_ratio"] <= .9,
                              own_deletion_pass=not a["any_deletion_reversal"], guide_growth_pass=b["rmse_ratio"] < 1,
                              pass_window=bool(len(errors) >= 8 and a["rmse_ratio"] <= .9 and not a["any_deletion_reversal"] and b["rmse_ratio"] < 1)))
    return {"scores": pd.DataFrame(scores), "paired_comparisons": pd.DataFrame(pairs),
            "deletions": pd.DataFrame(deletions), "remedy_gates": pd.DataFrame(gates)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError("Copy-only: choose a new output directory")
    sources = {"prereg": PREREG, "core": Path(core.__file__), "prior_diagnostics": Path(prior.__file__),
               "calendar_points": HORIZON / "calendar_arm_v1/predictions.csv", "fits": HORIZON / "results_v2/origin_fits.csv",
               "flights": core.SOURCES["pr60_flights"], "flight_lineage": prior.LINEAGE,
               "panel": core.SOURCES["kpi"], "company_calendar": core.SOURCES["calendar"]}
    hashes = {key: core.sha(path) for key, path in sources.items()}
    panel, _ = core.load_inputs()
    flights = prior.flight_source()
    points = pd.read_csv(sources["calendar_points"])
    points = points[(points.horizon_quarters == 2) & (~points.is_live)].copy()
    fits = pd.read_csv(sources["fits"]).set_index("origin_date")
    records, skips, training, features, checks = [], [], [], [], []
    for joint in points[points.model == "joint"].itertuples():
        origin = pd.Timestamp(joint.origin_date)
        assert origin == calendar_origin(joint.target)
        known = panel[panel.print_date <= origin].copy()
        latest = known.quarter.max()
        assert latest == joint.last_reported_quarter
        assert joint.point_reused_after_information_equality_check
        tr = training_pairs(panel, flights, origin)
        try:
            flight = prior.eligible_flight(flights, origin, latest)
            if len(tr) < 6:
                raise ValueError("fewer than six completed calendar-dated training pairs")
            denominator = float(np.sum(tr.x ** 2))
            if denominator <= 1e-12:
                raise ValueError("degenerate predictor variation")
            beta = float(np.clip(np.sum(tr.x * tr.y) / denominator, -2, 2))
            lookup = known.set_index("quarter").gbv_musd.to_dict()
            growth = lookup[latest] / lookup[core.qshift(latest, -4)] - 1
            adjusted = growth + beta * (flight.eu40_flt_da_yoy / 100 - growth)
            if not np.isfinite(adjusted) or adjusted <= -1:
                raise ValueError("invalid adjusted GBV growth")
        except ValueError as exc:
            skips.append(dict(target=joint.target, origin_date=joint.origin_date, n_training_pairs=len(tr), reason=str(exc)))
            continue
        match = points[(points.target == joint.target) & (points.origin_date == joint.origin_date)].set_index("model")
        assert all(name in match.index for name in ["fixed", "guide_growth", "revenue_growth"])
        fit = fits.loc[joint.source_origin_date]
        phi = fit[[f"weight_group_{k}" for k in range(4)]].to_numpy(dtype=float)
        jl, fl = joint.seasonal_lambda_pct / 100, float(match.loc["fixed", "seasonal_lambda_pct"]) / 100
        jo, fi = predict_pair(known, joint.target, phi, jl, fl, adjusted)
        jo0, fi0 = predict_pair(known, joint.target, phi, jl, fl, growth)
        assert np.isclose(jo0, joint.revenue_musd, rtol=0, atol=1e-7)
        assert np.isclose(fi0, match.loc["fixed", "revenue_musd"], rtol=0, atol=1e-7)
        mutated = panel.copy()
        mutated.loc[mutated.print_date >= origin, "gbv_musd"] *= 10
        assert training_pairs(mutated, flights, origin).equals(tr), "Future outcomes leaked into training"
        hidden = flights[flights.committed_utc > origin.tz_localize("UTC")].copy()
        hidden["eu40_flt_da_yoy"] = 99999
        perturbed = pd.concat([flights[flights.committed_utc <= origin.tz_localize("UTC")], hidden])
        assert prior.eligible_flight(perturbed, origin, latest).commit_full == flight.commit_full
        for row in tr.to_dict("records"):
            assert pd.Timestamp(row["outcome_publication"]) < origin
            assert pd.Timestamp(row["flight_commit_utc"]) <= pd.Timestamp(row["feature_origin"], tz="UTC")
            training.append(dict(evaluation_target=joint.target, evaluation_origin=joint.origin_date, **row))
        base = dict(target=joint.target, year=joint.year, origin_date=joint.origin_date, source_origin_date=joint.source_origin_date,
                    last_reported_quarter=latest, actual_guide_mid_musd=joint.actual_guide_mid_musd,
                    actual_revenue_musd=joint.actual_revenue_musd, cushion_pct=joint.cushion_pct,
                    point_in_time_status="reconstructed_asof_with_inherited_input_lineage",
                    registry_status="UNREGISTERED_non_earnings_historical_origin_HCR_required")
        predictions = {"joint_flight": jo, "fixed_flight": fi,
                       "joint_noflight": joint.revenue_musd, "fixed_noflight": float(match.loc["fixed", "revenue_musd"])}
        for model, revenue in predictions.items():
            records.append(dict(**base, model=model, revenue_musd=revenue, guide_mid_musd=revenue / joint.cushion_divisor))
        for model in ["guide_growth", "revenue_growth"]:
            records.append(dict(**base, model=model, revenue_musd=float(match.loc[model, "revenue_musd"]),
                                guide_mid_musd=float(match.loc[model, "guide_mid_musd"])))
        age = pd.Period(latest, freq="Q").ordinal - pd.Period(flight.quarter, freq="Q").ordinal
        features.append(dict(**{k: base[k] for k in ["target", "origin_date", "last_reported_quarter"]},
                             flight_quarter=flight.quarter, flight_commit_utc=flight.committed_utc.isoformat(),
                             flight_commit_full=flight.commit_full, flight_days=int(flight.days_cur_present),
                             flight_growth_pct=float(flight.eu40_flt_da_yoy), age_quarters_vs_last_company=age,
                             current_unprinted_quarter=flight.quarter == core.qshift(latest, 1),
                             beta=beta, n_training_pairs=len(tr), extra_parameter_count=1,
                             company_growth_pct=100 * growth, adjusted_growth_pct=100 * adjusted))
        checks.append(dict(target=joint.target, noflight_reconstruction_pass=True,
                           future_outcome_mutation_pass=True, future_feature_mutation_pass=True, training_date_pass=True))
    predictions = pd.DataFrame(records)
    if predictions.empty:
        raise ValueError("No evaluable forecasts; write a coverage report instead")
    assert not predictions.duplicated(["target", "model"]).any()
    assert predictions.groupby("target").size().eq(6).all()
    outputs = {"predictions": predictions, "features": pd.DataFrame(features), "skipped": pd.DataFrame(skips),
               "training_pairs": pd.DataFrame(training), "checks": pd.DataFrame(checks), **metrics(predictions)}
    current_origin = pd.Timestamp("2026-09-15")
    current = prior.eligible_flight(flights, current_origin, panel.quarter.max())
    outputs["current_feature_only"] = pd.DataFrame([dict(origin_date="2026-09-15", flight_quarter=current.quarter,
                    flight_commit_utc=current.committed_utc.isoformat(), flight_commit_full=current.commit_full,
                    flight_growth_pct=float(current.eu40_flt_da_yoy), days_present=int(current.days_cur_present),
                    live_forecast_emitted=False, interpretation="availability only; no causal or booking-cohort measurement")])
    assert hashes == {key: core.sha(path) for key, path in sources.items()}, "Source changed during run"
    out.mkdir(parents=True)
    for name, frame in outputs.items():
        frame.to_csv(out / f"{name}.csv", index=False)
    gates = outputs["remedy_gates"]
    summary = dict(n_unique_targets=int(predictions.target.nunique()), skipped=len(skips),
                   current_quarter_feature_count=int(outputs["features"].current_unprinted_quarter.sum()),
                   slope_min=float(outputs["features"].beta.min()), slope_max=float(outputs["features"].beta.max()),
                   promoted={m: bool(d.pass_window.all()) for m, d in gates.groupby("candidate")},
                   limitations=["few independent years and overlapping windows", "inherited flight commit lineage; raw mirror not recertified",
                                "reused historical validation sample", "historical calendar origins unsupported by frozen harness", "no live guide forecast"])
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    manifest = dict(code_sha256=core.sha(__file__), inputs={k: dict(path=str(p.relative_to(ROOT)), sha256=hashes[k]) for k, p in sources.items()},
                    outputs={p.name: core.sha(p) for p in out.iterdir()})
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
