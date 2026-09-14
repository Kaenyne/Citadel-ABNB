"""Read-only reproduction of accepted evidence; no fit, search, or registration."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
BUNDLE = ROOT / "data/processed/forecast_methods/l3_bundle_v1"
CONV = BUNDLE / "payload/conversion"
BASELINE = "8821961853e4068febbfe2712f9a4e1036c9e629"
MANIFEST_SHA = "9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixed_revenue(g1: float, g2: float, lam: float, w: float = 2 / 3,
                  multiplier: float = 1) -> float:
    if not all(np.isfinite(v) for v in (g1, g2, lam, w, multiplier)):
        raise ValueError("Nonfinite input")
    if min(g1, g2, lam, multiplier) <= 0 or not 0 <= w <= 1:
        raise ValueError("Positive levels and bounded w required")
    return lam * (w * g1 + (1 - w) * g2) * multiplier


def guide(revenue: float, cushion: float) -> float:
    if not np.isfinite(revenue + cushion) or revenue <= 0 or cushion <= -1:
        raise ValueError("Positive revenue and cushion greater than -1 required")
    return revenue / (1 + cushion)


def pooled_within(frame: pd.DataFrame, col: str) -> tuple[float, float]:
    ss = float(((frame[col] - frame.groupby("season")[col].transform("mean")) ** 2).sum())
    df = len(frame) - frame.season.nunique()
    return np.sqrt(ss / df), 1 - ss / float(((frame[col] - frame[col].mean()) ** 2).sum())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    allowed = ROOT / "data/processed/forecast_methods/quant_thesis_validation_v1/uncertainty_audit_v1"
    if not out.is_relative_to(allowed.resolve()):
        raise ValueError("Output must stay in the exclusive uncertainty_audit_v1 package")
    if out.exists():
        raise FileExistsError(f"Choose a new output version: {out}")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if head != BASELINE:
        raise ValueError(f"Expected immutable baseline {BASELINE}; got {head}")
    if sha(BUNDLE / "SHA256SUMS.json") != MANIFEST_SHA:
        raise ValueError("Unexpected bundle manifest identity")
    bound = json.loads((BUNDLE / "SHA256SUMS.json").read_text())
    bad = [p for p, h in bound.items() if sha(BUNDLE / p) != h]
    if bad:
        raise ValueError(f"Bundle hash mismatch: {bad}")
    receipt = json.loads((CONV / "final_review_acceptance.json").read_text())
    accepted_mismatch = [p for p, h in receipt["reviewed_output_sha256"].items() if sha(CONV / p) != h]
    if accepted_mismatch:
        raise ValueError(f"Accepted output mismatch: {accepted_mismatch}")

    inputs = [ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv",
              ROOT / "docs/revenue-forecast-strategy/05_backtests/K1_KERNEL_WEIGHTS_AND_BACKLOG.md",
              ROOT / "docs/revenue-forecast-strategy/05_backtests/K2_KERNEL_FROM_LEAD_TIMES.md"]
    inputs += sorted(CONV.glob("*"))
    for name in ("QVS_VARIANCE_AND_PRESENTATION_ARGUMENTS_v1.md", "QVS_GUIDE_BASIS_AND_DECISION_LOGIC_v1.md"):
        inputs.append(ROOT.parent.parent / "docs/revenue-forecast-strategy/05_backtests" / name)
    manifest = [{"path": str(p), "sha256": sha(p), "role": "read_only_accepted_or_legacy_evidence"} for p in inputs if p.is_file()]

    panel = pd.read_csv(inputs[0])
    panel["quarter"] = panel.quarter.map(lambda q: "20" + q[2:] + "Q" + q[0])
    panel = panel.sort_values("quarter").reset_index(drop=True)
    panel["year"] = panel.quarter.str[:4].astype(int)
    panel["season"] = panel.quarter.str[-1].astype(int)
    panel["g1"], panel["g2"] = panel.gbv_musd.shift(1), panel.gbv_musd.shift(2)
    panel["base_musd"] = (2 * panel.g1 + panel.g2) / 3
    panel["a_pp"] = 100 * 2 * panel.g1 / (2 * panel.g1 + panel.g2)
    panel["lambda_pct"] = 100 * panel.revenue_musd / panel.base_musd
    z = panel.dropna(subset=["g1", "g2", "lambda_pct"]).copy()
    assert len(panel) == 24 and len(z) == 22
    accepted_data = pd.read_csv(CONV / "dataset_22.csv")
    joined = z.merge(accepted_data, on="quarter", suffixes=("", "_accepted"), validate="one_to_one")
    for left, right in [("g1", "gbv_l1"), ("g2", "gbv_l2"), ("revenue_musd", "revenue_musd_accepted")]:
        np.testing.assert_allclose(joined[left], joined[right], rtol=0, atol=1e-9)

    rows, seasons, deletions = [], [], []
    for window, start in [("ALL", 2021), ("EX2021", 2022), ("W1", 2023), ("W2", 2024)]:
        d = z[z.year >= start]
        for col in ["a_pp", "lambda_pct"]:
            within, ss_share = pooled_within(d, col)
            rows.append(dict(window=window, variable=col, n=len(d), mean=d[col].mean(), variance=d[col].var(),
                             sd=d[col].std(), minimum=d[col].min(), maximum=d[col].max(),
                             pooled_within_season_sd=within, season_explained_ss_fraction=ss_share,
                             interpretation="retrospective_arithmetic_not_predictive_uncertainty"))
            for season, ds in d.groupby("season"):
                seasons.append(dict(window=window, season=season, variable=col, n=len(ds), mean=ds[col].mean(),
                                    sd=ds[col].std(), minimum=ds[col].min(), maximum=ds[col].max()))
            if window in ("W1", "W2"):
                for year in sorted(d.year.unique()):
                    dy = d[d.year != year]
                    deletions.append(dict(window=window, omitted_year=int(year), variable=col, n=len(dy),
                                          pooled_within_season_sd=pooled_within(dy, col)[0]))

    paths = pd.read_csv(CONV / "chronological_paths.csv")
    score_ref = pd.read_csv(CONV / "chronological_scores.csv")
    delta_ref = pd.read_csv(CONV / "paired_error_deltas.csv")
    scores, delta_rows, coverage = [], [], []
    max_score_error = 0.0
    for window, start in [("W1", "2023Q1"), ("W2", "2024Q1")]:
        primary = paths[(paths.quarter >= start) & paths.model.isin(["free_w_usd", "fixed_2_3_usd"])].copy()
        primary["calculated_error"] = primary.point - primary.actual
        wide = primary.pivot(index=["quarter", "year", "vintage_date"], columns="model", values="calculated_error").reset_index()
        free, fixed = wide.free_w_usd.to_numpy(), wide.fixed_2_3_usd.to_numpy()
        for model, errors in [("free_w_usd", free), ("fixed_2_3_usd", fixed)]:
            result = dict(window=window, model=model, n=len(errors), rmse_musd=np.sqrt(np.mean(errors ** 2)),
                          mae_musd=np.mean(abs(errors)), bias_musd=np.mean(errors))
            ref = score_ref[(score_ref.window == window) & (score_ref.model == model)].iloc[0]
            for metric in ["rmse_musd", "mae_musd", "bias_musd"]:
                error = abs(result[metric] - ref[metric])
                max_score_error = max(max_score_error, error)
                assert error < 2e-7, (window, model, metric, error)
            result["free_over_fixed_rmse"] = np.sqrt(np.mean(free ** 2) / np.mean(fixed ** 2))
            scores.append(result)
            d = primary[(primary.model == model) & primary.q10.notna() & primary.q90.notna()]
            coverage.append(dict(window=window, model=model, n_eligible=len(d), n_covered=int(((d.actual >= d.q10) & (d.actual <= d.q90)).sum()),
                                 quarters="|".join(d.quarter), mean_full_width_pct=np.mean(100 * (d.q90 - d.q10) / d.point)))
        wide["window"] = window
        wide["sq_error_delta_musd2"] = free ** 2 - fixed ** 2
        wide["absolute_error_delta_musd"] = abs(free) - abs(fixed)
        reference = delta_ref[delta_ref.window == window].set_index("quarter").loc[wide.quarter]
        np.testing.assert_allclose(wide.sq_error_delta_musd2, reference.sq_error_delta_musd2, atol=3e-6, rtol=0)
        delta_rows.append(wide)

    draws = pd.read_csv(CONV / "parameter_bootstrap.csv")
    pct_ref = pd.read_csv(CONV / "parameter_uncertainty.csv")
    quantiles = []
    for col in ["w"] + [f"lambda_Q{s}_pct" for s in range(1, 5)]:
        q = draws[col].quantile([.025, .5, .975]).to_numpy()
        ref = pct_ref[pct_ref.parameter == col].iloc[0]
        np.testing.assert_allclose(q, ref[["lower", "median", "upper"]].to_numpy(float), atol=2e-9, rtol=0)
        quantiles.append(dict(parameter=col, draws=len(draws), n_year_blocks=6, lower=q[0], median=q[1], upper=q[2]))
    # No new resampling: summarize the accepted draw rows only.
    paired_draws = pd.read_csv(CONV / "paired_year_bootstrap.csv")
    paired_pct_ref = pd.read_csv(CONV / "paired_uncertainty.csv")
    paired_summaries = []
    for window, ds in paired_draws.groupby("window"):
        ref = paired_pct_ref[paired_pct_ref.window == window].iloc[0]
        for col, prefix in [("rmse_ratio", "rmse_ratio"), ("mean_sq_error_delta_musd2", "mse_delta")]:
            q = ds[col].quantile([.025, .5, .975]).to_numpy()
            np.testing.assert_allclose(q, ref[[prefix + "_lower", prefix + "_median", prefix + "_upper"]].to_numpy(float), atol=2e-7, rtol=0)
            paired_summaries.append(dict(window=window, metric=col, draws=len(ds), n_year_blocks=int(ref.n_year_blocks), lower=q[0], median=q[1], upper=q[2]))

    compensation = []
    wbar, dw = draws.w.mean(), draws.w - draws.w.mean()
    for season, ds in z.groupby("season"):
        r = float((ds.g1 / ds.g2).mean())  # Fixed descriptive all22 seasonal mean ratio.
        lam = draws[f"lambda_Q{season}_pct"] / 100
        lbar = lam.mean()
        effective = lam * (1 + draws.w * (r - 1))
        term_lam = (1 + wbar * (r - 1)) * (lam - lbar)
        term_w = lbar * (r - 1) * dw
        cross = (r - 1) * dw * (lam - lbar)
        np.testing.assert_allclose(effective, lbar * (1 + wbar * (r - 1)) + term_lam + term_w + cross, atol=1e-14, rtol=0)
        covariance = float(np.cov(term_lam, term_w, ddof=1)[0, 1])
        compensation.append(dict(season=int(season), n_historical_ratio=len(ds), r_season_mean=r,
                                 n_year_blocks=6, draws=len(draws), corr_w_lambda=draws.w.corr(lam),
                                 lambda_sd_pct=float(lam.std() * 100), effective_slope_sd_pct=float(effective.std() * 100),
                                 marginal_linear_variance=float(term_lam.var() + term_w.var()),
                                 twice_covariance=2 * covariance, joint_linear_variance=float((term_lam + term_w).var()),
                                 exact_joint_variance=float(effective.var()), interaction_sd=float(cross.std()),
                                 interpretation="accepted_free_weight_draws_research_diagnostic_only_not_operational"))

    # Deterministic source precision illustration; holds existing descriptive mean lambda fixed.
    lam_q3 = float(z[(z.year >= 2023) & (z.season == 3)].lambda_pct.mean() / 100)
    old_base, precise_base = (2 * 27200 + 29200) / 3, (2 * 27247 + 29187) / 3
    precision = {"n": 1, "target": "2026Q3", "frozen_g1_musd": 27200, "frozen_g2_musd": 29200,
                 "filing_g1_musd": 27247, "filing_g2_musd": 29187, "base_delta_musd": precise_base - old_base,
                 "held_fixed_lambda": lam_q3, "revenue_delta_musd": lam_q3 * (precise_base - old_base),
                 "label": "QVS_recorded_filing_precision_sensitivity_not_historical_replacement_or_new_forecast"}
    # Minimal algebra checks are embedded; no forecast or probability is emitted.
    assert abs(fixed_revenue(26000, 28000, .12) - 3200) < 1e-10
    assert abs(guide(3200, .0179) * 1.0179 - 3200) < 1e-10
    out.mkdir(parents=True, exist_ok=False)
    tables = {"arithmetic_window_summary": pd.DataFrame(rows), "arithmetic_season_summary": pd.DataFrame(seasons),
              "arithmetic_year_deletion": pd.DataFrame(deletions), "historical_arithmetic": z,
              "accepted_score_reproduction": pd.DataFrame(scores), "accepted_paired_delta_reproduction": pd.concat(delta_rows),
              "accepted_interval_reproduction": pd.DataFrame(coverage), "accepted_parameter_percentiles": pd.DataFrame(quantiles),
              "accepted_paired_percentiles": pd.DataFrame(paired_summaries), "joint_parameter_compensation": pd.DataFrame(compensation),
              "input_manifest": pd.DataFrame(manifest)}
    for name, data in tables.items():
        data.to_csv(out / (name + ".csv"), index=False, float_format="%.12g")
    (out / "precision_sensitivity.json").write_text(json.dumps(precision, indent=2) + "\n", encoding="utf-8")
    summary = dict(status="PASS_bounded_arithmetic_reproduction", baseline_commit=head,
                   bundle_manifest_sha256=MANIFEST_SHA, bundle_files_verified=len(bound),
                   acceptance_output_bindings_verified=len(receipt["reviewed_output_sha256"]),
                   max_score_difference_musd=max_score_error, n_full=22, n_W1=14, n_W2=10,
                   new_models_fitted=0, new_weight_searches=0, new_resamples=0, registrations=0,
                   operational_parameters_changed=False, probability_calibration_claimed=False)
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
