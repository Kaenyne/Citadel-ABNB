"""Accepted-source integration and deterministic propagation; never estimate models."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pandas as pd

from adapter import dated, number, shift

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "data/processed/forecast_methods/lane4_sources_v2/snapshot_v1"
BUNDLE = SOURCE / "bundle"
MANIFEST_SHA = "9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970"
CONVERSION_STATUS = "accepted_L3_free_weight_promotion_failed_W1_W2_retained_operational_K0_2over3"
JOINT_STATUS = "conditional_fixed_K0_assumed_stress_no_probability_no_predictive_band"
DRAW_STATUS = "rejected_free_weight_model_descriptive_joint_resampling_not_production_not_predictive_band"
QUARTERS = ["2026Q3", "2026Q4", "2027Q1"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_csv(output, name, rows):
    pd.DataFrame(rows).to_csv(output / (name + ".csv"), index=False, float_format="%.15g")


def verify_accepted_source(as_of):
    dated("2026-09-13", as_of)
    manifest_path = BUNDLE / "SHA256SUMS.json"
    if sha(manifest_path) != MANIFEST_SHA:
        raise ValueError("Accepted L3 manifest identity mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if len(manifest) != 108:
        raise ValueError("Expected108 accepted payload bindings")
    for rel, expected in manifest.items():
        p = (BUNDLE / rel).resolve()
        if not p.is_relative_to(BUNDLE.resolve()) or sha(p) != expected:
            raise ValueError("L3 accepted payload hash/path mismatch: " + rel)
    receipt = json.loads((SOURCE / "integrity_receipt.json").read_text(encoding="utf-8"))
    if receipt["integrity_status"] != "PASS" or receipt["manifest_sha256"] != MANIFEST_SHA:
        raise ValueError("Source worker verification unavailable")
    # This receipt is attribution to the source worker's actual Git-object audit;
    # checking commit syntax alone would not prove content membership.
    return receipt


def expectation_row(revenue, guide, cushion, consensus, street_cushion=None):
    r, g, s = (number(x, n, True) for x, n in [(revenue, "revenue"), (guide, "guide"), (consensus, "consensus")])
    c = number(cushion, "cushion")
    sc = c if street_cushion is None else number(street_cushion, "street cushion")
    if min(c, sc) <= -1 or not math.isclose(g, r / (1+c), abs_tol=1e-6, rel_tol=0):
        raise ValueError("Own revenue/guide/cushion identity inconsistent")
    hypothetical = s / (1 + sc)
    return dict(own_revenue_musd=r, own_guide_mid_musd=g, cushion_decimal=c,
                revenue_consensus_musd=s, revenue_gap_musd=r-s, revenue_gap_pct=100*(r/s-1),
                guide_minus_revenue_diagnostic_musd=g-s,
                hypothetical_street_cushion_decimal=sc, hypothetical_street_guide_musd=hypothetical,
                hypothetical_like_basis_guide_gap_musd=g-hypothetical,
                guide_expectations_status="explicit_dated_guide_expectations_unavailable",
                revenue_comparison_status="same_basis_reported_revenue_comparison",
                cross_object_status="different_objects_not_guide_surprise",
                hypothetical_status="assumed_Street_cushion_transformation_not_observed_guide_consensus")


def tuple_revenue(parameters, target, lag1, lag2):
    """Apply an intact accepted parameter row, with no fit or marginal splicing."""
    w = number(parameters["w"], "w")
    if not 0 <= w <= 1:
        raise ValueError("Joint weight outside [0,1]")
    # Requiring all four seasonal values prevents acceptance of partial tuples.
    for s in range(1, 5):
        number(parameters[f"lambda_Q{s}_pct"], "joint seasonal lambda", True)
    lam = float(parameters[f"lambda_Q{target[-1]}_pct"])
    b = w * number(lag1, "lag1", True) + (1-w) * number(lag2, "lag2", True)
    return b * lam / 100


def main_joint_rows(forecasts, weights, cushion_info):
    lookup = {(r["scenario"], r["quarter"]): r for r in forecasts}
    parts = {(r["scenario"], r["target_quarter"], r["lag"]): r for r in weights}
    contexts = [
        ("joint_reference", "review_with_k", 0.0, "trailing8_median"),
        ("joint_soft", "adr_mean_reversion", -0.10, "legacy_Q4_else_trailing8_mean"),
        ("joint_firm", "nights_case_a", 0.10, "trailing8_median"),
    ]
    rows, bridge = [], []
    for scenario, operating, lambda_shift, c_policy in contexts:
        for q in QUARTERS:
            ref, op = lookup["review_with_k", q], lookup[operating, q]
            g1, g2 = [parts[operating, q, lag]["gbv_musd"] for lag in [1, 2]]
            lam = op["lambda_pct"] + lambda_shift
            c = (.0388 if q == "2026Q4" else cushion_info["mean"]["cushion"]) if scenario == "joint_soft" else ref["cushion_decimal"]
            r = lam / 100 * (2/3*g1 + 1/3*g2)
            guide = r / (1+c)
            rows.append(dict(scenario=scenario, context=scenario, quarter=q, operating_scenario=operating,
                             conversion_basis="operational_K0_seasonal_lambda_plus_explicit_level_stress",
                             source_draw=None, selected_years=None, kernel_weight=2/3,
                             lambda_pct=lam, lambda_stress_pp=lambda_shift, lambda_n_train=op["lambda_n_train"],
                             lag1_gbv_musd=g1, lag2_gbv_musd=g2, cushion_decimal=c, cushion_policy=c_policy,
                             net_revenue_factor=1.0, pre_net_revenue_musd=r, revenue_musd=r, guide_musd=guide,
                             delta_revenue_vs_reference_musd=r-ref["revenue_musd"],
                             delta_guide_vs_reference_musd=guide-ref["guide_musd"],
                             guide_status=ref["guide_status"], information_date="2026-09-13",
                             n_new_fitted_parameters=0, parameter_definition="inherited seasonal K0 estimates and fixed2/3; named0.10pp assumed stress is not fitted",
                             evidence_status=JOINT_STATUS, conversion_status=CONVERSION_STATUS,
                             stress_basis="lambda shift is assumed 0.10 percentage point; no fitted parameter bound; absorbs unspecified conversion risks",
                             overlap_treatment="full operating ADR replacement once; no additive FX fee cancellation RNPL or generic net overlay"))
            # Exact order attribution: operating replacement; lambda level; cushion.
            states = [("reference", ref["revenue_musd"], ref["guide_musd"]),
                      ("operating_GBV_replacement", op["revenue_musd"], op["guide_musd"]),
                      ("fixed_weight_seasonal_lambda_stress", r, r/(1+ref["cushion_decimal"])),
                      ("cushion_replacement", r, guide)]
            previous = states[0]
            for step, (label, rev, gui) in enumerate(states):
                bridge.append(dict(scenario=scenario, quarter=q, step=step, change=label, revenue_musd=rev,
                                   guide_musd=gui, delta_revenue_musd=rev-previous[1], delta_guide_musd=gui-previous[2],
                                   evidence_status=JOINT_STATUS))
                previous = (label, rev, gui)
    return rows, bridge


def descriptive_draws(forecasts, weights):
    source = BUNDLE / "payload/conversion/parameter_bootstrap.csv"
    draws = pd.read_csv(source)
    if len(draws) != 1000 or draws.draw.duplicated().any() or not (draws.model == "free_w").all() or not (draws.loss == "usd").all():
        raise ValueError("Unexpected accepted joint draw inventory")
    ref = {r["quarter"]: r for r in forecasts if r["scenario"] == "review_with_k"}
    cohorts = {(r["target_quarter"], r["lag"]): r["gbv_musd"] for r in weights if r["scenario"] == "review_with_k"}
    def project(p, kind):
        rows = []
        for q in QUARTERS:
            r = tuple_revenue(p, q, cohorts[q, 1], cohorts[q, 2])
            rows.append(dict(source_draw=p.get("draw"), selected_years=p.get("selected_years"),
                             source_draw_n=p["n"], source_n_parameters=p["n_parameters"],
                             quarter=q, operating_scenario="review_with_k", kernel_weight=p["w"],
                             **{f"lambda_Q{s}_pct":p[f"lambda_Q{s}_pct"] for s in range(1,5)},
                             lambda_pct=p[f"lambda_Q{q[-1]}_pct"], lag1_gbv_musd=cohorts[q,1], lag2_gbv_musd=cohorts[q,2],
                             cushion_decimal=ref[q]["cushion_decimal"], net_revenue_factor=1,
                             revenue_musd=r, guide_musd=r/(1+ref[q]["cushion_decimal"]),
                             delta_revenue_vs_K0_musd=r-ref[q]["revenue_musd"],
                             delta_guide_vs_K0_musd=r/(1+ref[q]["cushion_decimal"])-ref[q]["guide_musd"],
                             evidence_status=DRAW_STATUS, exhibit=kind,
                             parameter_source=(source if kind!="all22_fullsample_point_not_adopted" else BUNDLE/"payload/conversion/parameters.csv").relative_to(ROOT).as_posix(), n_source_year_blocks=6,
                             interpretation="fitted-model resampling sensitivity; ignores future residual forecast GBV and cushion uncertainty"))
        return rows
    all_rows = [r for p in draws.to_dict("records") for r in project(p, "all_existing_1000_joint_draws")]
    q4 = [r for r in all_rows if r["quarter"] == "2026Q4"]
    extremes = []
    for label, selected in [("minimum_Q4_result_intact_tuple", min(q4,key=lambda r:r["revenue_musd"])),
                            ("maximum_Q4_result_intact_tuple", max(q4,key=lambda r:r["revenue_musd"]))]:
        p = draws[draws.draw == selected["source_draw"]].iloc[0].to_dict()
        extremes.extend(project(p, label))
    parameters = pd.read_csv(BUNDLE / "payload/conversion/parameters.csv")
    p = parameters[(parameters["sample"] == "all22") & (parameters.model == "free_w") & (parameters.loss == "usd")]
    if len(p) != 1:
        raise ValueError("Missing full22 descriptive tuple")
    extremes.extend(project(p.iloc[0].to_dict(), "all22_fullsample_point_not_adopted"))
    return all_rows, extremes


def integrate(output, forecasts, operating, weights, consensus, guide_info, accepted, as_of):
    accounting=json.loads((SOURCE/"accounting_eligibility.json").read_text(encoding="utf-8"))
    if accounting["central_fx_financial_eligibility"] or accounting["estimated_incremental_fx_musd"] is not None:
        raise ValueError("Source eligibility changed; explicit new review and contract required")
    for name in ["accounting_eligibility.json","cohort_baseline_compatibility.csv","fx_isolated_diagnostics.csv"]:
        (output/name).write_bytes((SOURCE/name).read_bytes())
    expectations = []
    for r in forecasts:
        if r["quarter"] == "2026Q4":
            for c in consensus.to_dict("records"):
                expectations.append(dict(scenario=r["scenario"], quarter=r["quarter"],
                                         vendor_family=c["panel_family"], vendor=c["vendor"],
                                         consensus_as_of_timestamp=c["as_of_timestamp"], consensus_n_estimates=c["n_estimates"],
                                         consensus_source_ref=c["source_path"], consensus_url=c["url"],
                                         **expectation_row(r["revenue_musd"], r["guide_musd"], r["cushion_decimal"], c["value"])))
    write_csv(output, "expectations_comparison", expectations)
    q4ref = next(r for r in forecasts if r["quarter"] == "2026Q4" and r["scenario"] == "review_with_k")
    lseg = consensus[consensus.panel_family == "LSEG family"].iloc[0]
    street_grid = []
    for label, c in [("zero_cushion_boundary",0), ("trailing8_median_assumed_Street",q4ref["cushion_decimal"]),
                     ("trailing8_mean_assumed_Street",guide_info["mean"]["cushion"]), ("legacy3.88pct_assumed_Street",.0388)]:
        street_grid.append(dict(assumed_street_policy=label, consensus_vendor=lseg.vendor,
                               consensus_as_of_timestamp=lseg.as_of_timestamp,
                               **expectation_row(q4ref["revenue_musd"], q4ref["guide_musd"], q4ref["cushion_decimal"], lseg.value, c)))
    write_csv(output,"hypothetical_street_cushion",street_grid)
    joint, bridge = main_joint_rows(forecasts, weights, guide_info)
    write_csv(output,"joint_scenarios",joint)
    write_csv(output,"joint_scenario_bridge",bridge)
    joint_expectations=[]
    for r in joint:
        if r["quarter"] == "2026Q4":
            joint_expectations.append(dict(scenario=r["scenario"],vendor=lseg.vendor,consensus_as_of_timestamp=lseg.as_of_timestamp,
                                           **expectation_row(r["revenue_musd"],r["guide_musd"],r["cushion_decimal"],lseg.value)))
    write_csv(output,"joint_expectations",joint_expectations)
    draw_rows, extremes = descriptive_draws(forecasts,weights)
    write_csv(output,"descriptive_joint_draws",draw_rows)
    write_csv(output,"descriptive_joint_extremes",extremes)
    envelope=[]
    for q in QUARTERS:
        rows=[r for r in joint if r["quarter"]==q]
        envelope.append(dict(quarter=q,scope="three_named_fixed_K0_conditional_cases_only", n_cases=len(rows),
                             minimum_revenue_musd=min(r["revenue_musd"] for r in rows), maximum_revenue_musd=max(r["revenue_musd"] for r in rows),
                             minimum_guide_musd=min(r["guide_musd"] for r in rows),maximum_guide_musd=max(r["guide_musd"] for r in rows),
                             evidence_status=JOINT_STATUS, excludes="isolated generic net sensitivity; rejected free-weight draws; unidentified empirical FX/RNPL"))
    write_csv(output,"conditional_envelope",envelope)
    net=[]
    precision=[]
    for r in forecasts:
        if r["scenario"] != "review_with_k":
            continue
        q=r["quarter"]
        for factor in [.99,1.01]:
            net.append(dict(scenario="illustrative_net_minus1" if factor<1 else "illustrative_net_plus1",quarter=q,
                            net_revenue_factor=factor, baseline_revenue_musd=r["revenue_musd"],revenue_musd=r["revenue_musd"]*factor,
                            guide_musd=r["guide_musd"]*factor,delta_revenue_musd=r["revenue_musd"]*(factor-1),
                            delta_guide_musd=r["guide_musd"]*(factor-1), guide_status=r["guide_status"],
                            evidence_status="illustrative_net_after_hedge_consolidated_revenue_change_not_estimated_FX",
                            overlap_treatment="isolated from seasonal conversion fee cancellation RNPL stresses"))
        # Read-only QVS reports parent-verified SEC filing table; exact filing
        # sensitivity leaves historical K0 calibration and source card unchanged.
        delta_base=27.0 if q=="2026Q3" else 47/3 if q=="2026Q4" else 0.0
        delta_r=delta_base*r["lambda_pct"]/100
        precision.append(dict(quarter=q,frozen_Q1_GBV_musd=29200,frozen_Q2_GBV_musd=27200,
                              filing_Q1_GBV_musd=29187,filing_Q2_GBV_musd=27247,filing_H1_GBV_musd=56434,
                              weighted_GBV_delta_musd=delta_base,revenue_musd=r["revenue_musd"]+delta_r,
                              guide_musd=r["guide_musd"]+delta_r/(1+r["cushion_decimal"]),delta_revenue_musd=delta_r,
                              delta_guide_musd=delta_r/(1+r["cushion_decimal"]),
                              information_date="2026-08-06",verification_information_date="2026-09-13",
                              source_url="https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm",
                              source_ref=(SOURCE/"qvs/QVS_VARIANCE_AND_PRESENTATION_ARGUMENTS_v1.md").relative_to(ROOT).as_posix(),
                              evidence_status="source_precision_sensitivity_parent_verified_filing_not_new_forecast",
                              calibration="K0 lambda still fitted on frozen rounded panel; partial input precision change only"))
    write_csv(output,"net_revenue_sensitivity",net)
    write_csv(output,"filing_precision_sensitivity",precision)
    # An evidence update changes no operational dollar. Every row independently
    # matches the immutable prior snapshot below the preregistered $0.001M line.
    prior=pd.read_csv(ROOT/"data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1/forecast.csv")
    changes=[]
    for r in forecasts:
        p=prior[(prior.scenario==r["scenario"]) & (prior.quarter==r["quarter"])].iloc[0]
        changes.append(dict(scenario=r["scenario"],quarter=r["quarter"],old_revenue_musd=p.revenue_musd,
                            new_revenue_musd=r["revenue_musd"],revenue_delta_musd=r["revenue_musd"]-p.revenue_musd,
                            old_guide_musd=p.guide_musd,new_guide_musd=r["guide_musd"],guide_delta_musd=r["guide_musd"]-p.guide_musd,
                            changed_component="research disposition and expectations basis only; no operating overlay"))
    max_change=max(abs(r[k]) for r in changes for k in ["revenue_delta_musd","guide_delta_musd"])
    if max_change>=.001:
        raise ValueError("Operational v1 baseline changed without allowed reconciliation")
    write_csv(output,"v1_v2_baseline_reconciliation",changes)
    validation=pd.read_csv(BUNDLE/"payload/conversion/chronological_scores.csv")
    accepted_rows=validation[validation.model.isin(["free_w_usd","fixed_2_3_usd","K0_fixed_operational"])].copy()
    accepted_rows["adoption_interpretation"]="free-weight fails matched promotion both windows; fixed matched OLS is distinct from retained K0 seasonal policy"
    accepted_rows["evaluation_origin"]="letter-close includes just-printed prior-quarter GBV; not today's before-release forecast horizon"
    accepted_rows["new_estimation_in_L4"]=False
    accepted_rows.to_csv(output/"accepted_conversion_validation.csv",index=False,float_format="%.15g")
    ledger=pd.read_csv(output/"source_ledger.csv").to_dict("records")
    for p in [SOURCE/"integrity_receipt.json",BUNDLE/"SHA256SUMS.json",BUNDLE/"payload/conversion/parameter_bootstrap.csv",
              BUNDLE/"payload/conversion/parameters.csv",BUNDLE/"payload/conversion/chronological_scores.csv",
              SOURCE/"qvs/QVS_VARIANCE_AND_PRESENTATION_ARGUMENTS_v1.md", SOURCE/"qvs/QVS_GUIDE_BASIS_AND_DECISION_LOGIC_v1.md",
              SOURCE/"accounting_eligibility.json",SOURCE/"cohort_baseline_compatibility.csv",SOURCE/"fx_isolated_diagnostics.csv",
              SOURCE/"row_dispositions.csv"]:
        ledger.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p),scope="accepted immutable source copy; no new fit",imported_at=as_of))
    write_csv(output,"source_ledger",ledger)
    return dict(accepted_bundle_commit=accepted["bundle_commit"],accepted_research_commit=accepted["research_commit"],
                accepted_manifest_sha256=MANIFEST_SHA,verified_payload_hashes=108,source_integrity_receipt_sha256=sha(SOURCE/"integrity_receipt.json"),
                n_existing_joint_draws=1000,n_descriptive_draw_output_rows=len(draw_rows),n_main_joint_cases=3,
                main_joint_status=JOINT_STATUS,descriptive_draw_status=DRAW_STATUS,
                operational_baseline_max_abs_change_musd=max_change,consensus_information_snapshot="2026-09-13; per-vendor original timestamps preserved",
                new_fits=0,guide_expectations_status="unavailable; hypothetical common-cushion bridge separately labelled")
