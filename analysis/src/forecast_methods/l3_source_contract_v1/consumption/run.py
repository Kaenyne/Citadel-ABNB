"""Lossless classification of frozen L3 evidence; never produces forecasts."""
from __future__ import annotations
import argparse
import ast
import collections
import csv
from datetime import date, datetime, timezone
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[5]
INPUTS = ROOT / "data/processed/forecast_methods/l3_source_contract_v1/consumption/inputs_v2"
BUNDLE = ROOT / "data/processed/forecast_methods/l3_bundle_v1"
PATH_INVENTORY = INPUTS.parent / "supplemental_path_inventory_v1.json"
EXPECTED = {
    "l4_inputs.csv": "d53e07ca35868aed0e1c71c04d8ef07565a00230628f1044a4c8659bf3742638",
    "bundle.json": "344f505596f66f66385e9a478a6cfa963c1359ac0a6f56016f3b78afc2eb9dc2",
    "inputs_manifest": "8dbb605edd033daab92a0fb5299b96156940bc1816843376df243dab289c13e1",
    "path_inventory": "973d03ab14924da7d557a3b2dd658e93e2ee07c90b3534f2f2dafed94cb91d23",
}
STATUSES = ("usable_as_observed_input", "usable_as_conditional_scenario", "descriptive_only",
            "comparator_only", "unavailable", "rejected")
PACKAGE_COUNTS = {"cohort_fx": 1080, "fee_panel": 2, "adr_hotel": 86, "nclh": 12, "conversion": 7}
FX_CONDITIONAL = {"rnpl_retimed_kernel_revenue", "rnpl_fx_incremental_replacement", "rnpl_fx_replacement_multiplier"}
FX_DESCRIPTIVE = {"reference_normalized_kernel_revenue", "ordinary_booking_kernel_revenue", "rnpl_fx_level_multiplier"}
FX_TREATMENTS = dict(zip(
    ["reference_normalized_kernel_revenue", "ordinary_booking_kernel_revenue", "rnpl_retimed_kernel_revenue", "rnpl_fx_incremental_replacement", "rnpl_fx_replacement_multiplier", "rnpl_fx_level_multiplier"],
    ["diagnostic_reference_only_not_new_forecast", "baseline_identity_do_not_add", "conditional_replacement_level", "incremental_replacement_only_after_compatibility_check", "multiply_only_matching_ordinary_booking_baseline", "reference_level_only_never_multiply_reported_kernel"]))
ADR_SCENARIOS = {"adr_exfx_yoy", "adr_reported_yoy", "adr_usd"}
ADR_COMPONENTS = {"adr_component_" + x for x in ["like_for_like_pricing_residual", "geographic_mix", "unit_size_party", "length_of_stay_mix", "new_business_seats", "interaction", "fee_migration_mechanics_K"]}
HOTEL = {"hotel_comparator_cpi_lodging_yoy_pct", "hotel_comparator_bea_hotels_price_yoy_pct"}
NCLH = {"NCLH_" + m + "_revenue_usd_m_" + kind for m in ("passenger_ticket", "total") for kind in ("kernel_rmse_ratio", "lambda_range")}
CONVERSION = {"shared_lag_w", "free_to_fixed_PIT_RMSE_ratio"} | {f"seasonal_conversion_Q{i}" for i in range(1, 5)}
METRIC_UNITS = {
    **{m: ("ratio" if "multiplier" in m else "USD") for m in FX_CONDITIONAL | FX_DESCRIPTIVE},
    **{m: "percentage_points" for m in ADR_COMPONENTS | HOTEL | {"adr_exfx_yoy", "adr_reported_yoy"}},
    "adr_usd": "USD_per_night", "gbv_identity_comparison": "USD_billions",
    "fee_theta_log": "fraction_log_neutral_reprice", "shared_lag_w": "fraction_of_lagged_GBV_driver_coefficient",
    "free_to_fixed_PIT_RMSE_ratio": "USD_level_RMSE_ratio",
    **{f"seasonal_conversion_Q{i}": "percent_of_weighted_lagged_GBV_coefficient_level" for i in range(1, 5)},
    **{m: ("ratio to seasonal naive; USD-level RMSE" if m.endswith("rmse_ratio") else "percentage points; realized seasonal range; no uncertainty interval") for m in NCLH},
}


def source_date(value):
    """The original bundle has a September 13 daily cutoff, not a refreshed vintage."""
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            result = date.fromisoformat(value)
        else:
            stamp = datetime.fromisoformat(value)
            if stamp.tzinfo is None:
                raise ValueError("Timestamp requires explicit timezone")
            result = stamp.astimezone(timezone.utc).date()
    except (TypeError, ValueError) as error:
        raise ValueError("Malformed source information date") from error
    if result > date(2026, 9, 13):
        raise ValueError("Future information relative to frozen original bundle")
    return result


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_csv(path):
    with Path(path).open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("Duplicate or absent columns")
        if any(None in r or any(v is None for v in r.values()) for r in rows):
            raise ValueError("Ragged CSV")
        return reader.fieldnames, rows


def write_csv(path, rows, fields=None):
    if fields is None:
        fields = list(rows[0]) if rows else []
    with Path(path).open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def gap(gap_id, applies_to, exact_inputs, prohibition, source):
    return dict(gap_id=gap_id, applies_to=applies_to, current_status="unresolved_for_direct_model_use",
                exact_additional_inputs=exact_inputs, prohibited_shortcut=prohibition, evidence_reference=source)


GAPS = [
    gap("L4_FORMAT", "all model-application candidates", "New immutable accepted integration version translating appropriate rows to L4 JSON revenue_adapter schema; actual source commit membership and payload hashes verified.", "Do not pass the research CSV/bundle.json directly to the existing L4 loader or rename metrics to force acceptance.", "committed L4 l3_contract.py:load_bundle/apply_row; frozen L3 bundle.json"),
    gap("FX_BASELINE", "cohort_fx", "Exact L4 quarter/scenario/revenue_musd, lag-1/lag-2 cohort_gbv_musd, matching lambda policy and reference exposures reconstructing each USD GBV; explicit USD to USDm division by 1000000 where relevant.", "Do not attach an inherited K0 baseline or its dollar delta to a different operating scenario.", "committed L4 l3_contract.py:apply_row; original baseline_being_replaced and baseline_value_usd"),
    gap("FX_HEDGE", "cohort_fx", "Verified baseline hedge contribution h in USDm for each target with hedge_source_ref and hedge_evidence_status=verified_baseline_reconciliation; reconstruct a compatible operating-only T/B after removing/reconciling hedge effects in the baseline, lambda and cohort construction, before (R-h)*T/B+h.", "Historical hedge disclosures do not identify a future scenario hedge contribution; missing h is not zero. The unresolved original aggregate T/B is not certified as an operating-only multiplier merely by supplying h.", "committed L4 l3_contract.py:apply_row; original embedded_hedges"),
    gap("FX_EXPOSURE", "cohort_fx", "Surviving recognized-revenue reference exposures by booking quarter/currency; u on that same cohort denominator; full p recognition allocation summing to one; observed/assumed status and all source/vintage fields.", "Do not use RNPL stock, funds receivable, total future bookings or USD contribution weights as measured recognition cohort shares.", "committed L4 l3_contract.py:timing_identity; L3_COHORT_FX_ACCOUNTING.md"),
    gap("FX_ROOT_QUOTES", "cohort_fx", "Per-currency booking, recognition and fixed-reference rate quote/source cutoffs; USD-per-currency direction; reference identifier; exact averaging windows/coverage; observed-versus-scenario flags, input checksums and transformation chain. Preserve quote<=source<=as-of for observed data.", "The current L4 contract validates row information_date and supplied ratios but does not require root quote metadata. Parent or new contract must validate it; do not silently relabel scenario future rates as observations.", "committed L4 l3_contract.py:timing_identity/apply_row; adapter.py:dated"),
    gap("FX_ROUTE", "cohort_fx", "Choose exactly one compatible representation: replacement level T, incremental T-B, or multiplier T/B. Reconcile baseline hedge and distinguish reported USD GBV booking FX from timing replacement.", "Do not sum equivalent routes, add baseline B, multiply by T/R0 or apply a second gross FX/fee/hedge overlay.", "original treatment and embedded_fx; L3_COHORT_FX_ACCOUNTING.md"),
    gap("ADR_ADOPTION", "adr_hotel ADR scenarios/components", "Explicit chosen ADR scenario for the same quarter and units, component/mix assumptions and mean-reversion rule, benchmark being replaced, and separate acknowledgement of retrospective evidence limitations.", "Implementation or descriptive acceptance does not make residual pricing or imposed K an identified causal estimate.", "original limitations; L3 ADR/hotel audit; committed L4 README"),
    gap("ADR_FX_FEE", "adr_hotel ADR scenarios/components", "State ex-FX versus reported ADR, prior-year ADR base for YoY conversion, selected booking FX translation and K inclusion; reconcile with the L4 operating ADR and later FX timing route.", "Do not add K or components already in total ADR, add a take-rate fee uplift, or translate reported ADR twice.", "original metric/treatment/embedded_fx; committed L4 fee_mechanics_comparison description"),
    gap("ADR_NIGHTS_LAGS", "adr_hotel ADR and GBV identities", "Matching nights in millions and quarter; explicit USD/night to USDm GBV bridge; next revenue target through the fixed lag kernel, and separately justified guide cushion.", "GBV identity is not same-quarter revenue. Q3 operating GBV enters Q4/Q1 lagged revenue; do not apply same-quarter take rate.", "original gbv_identity_comparison limitations; committed L4 adapter.py:forecast"),
    gap("FEE_CAPTURE", "fee_panel; each month estimated separately", "Eligible captured listing-stay panel for the named monthly triplet (September 14/16/18 or October 12/14/16), with valid capture timestamps, currency, nightly price, listing/stay identity, city and residence metadata; appropriate monthly treatment/control under prereg gates. Both triplets are needed only for both monthly outputs; no automatic pooling.", "September does not require October captures. No eligible wave CSV exists at inventory time; dryrun is not a wave. Missing theta is not zero. Do not launch or wait for a collector in this task.", "existing_data_inventory.json; fee_panel_v1/run.py"),
    gap("FEE_IDENTIFICATION", "fee_panel", "Pass prereg coverage and valid matched design; neutral-reprice normalization, residence/fee eligibility, outcome denominator and timing; explicit replacement of overlapping ADR K mechanics.", "Fee mechanics are not an empirical pass-through estimate; do not combine theta with already embedded repricing.", "fee panel prereg; SC-B accounting supplement when accepted"),
    gap("HOTEL_COMPLETENESS", "incomplete hotel comparator rows", "Complete quarter of official comparable price-index observations with original release dates and source vintages; historical reconstruction if making PIT claims.", "Do not extrapolate one month into a full quarter or fill blanks with zero.", "original hotel limitations; no new content in bounded local inventory"),
    gap("HOTEL_MAPPING", "hotel comparators", "Material new dated primary evidence and a separately preregistered ABNB mapping that passes required windows, before any production re-evaluation.", "US hotel/category price indices are comparators, not Airbnb pricing or proof of competitive pressure; existing production eligibility remains 0/13.", "original hotel research notes and frozen comparator outputs"),
    gap("NCLH_NO_TRANSFER", "nclh", "No current ABNB application route. Only materially new issuer-relevant PIT evidence and a new authorized preregistered study could revisit the failed transferability claim; matched GAAP guide and consensus needed for the unavailable guide comparison.", "Do not reuse failed NCLH coefficients as an ABNB adjustment or reinterpret missing guide scores as success.", "L3_NCLH_RESULTS_v1.md; NCLH results_v4"),
    gap("CONVERSION_POLICY", "conversion", "Preserve fixed 2/3-1/3 operational estimator. Any later adoption requires a new authorized specification/validation decision and joint weight plus four lambdas with exact GBV/revenue definition and information set.", "Full22 descriptive w and six-year-block sensitivity bounds cannot replace the fixed operational model; free/fixed PIT FAIL remains, W2 is nested in W1.", "conversion accepted_validation_spec.json and acceptance receipt; QVS context"),
    gap("GUIDE_EXPECTATIONS", "all guide-expectations claims", "Dated vendor/source observations specifically forecasting management's guide, or a separately justified explicit revenue-consensus-to-guide model with its own cushion assumptions.", "Captured revenue consensus is not expected management guidance; guide-minus-revenue-consensus arithmetic does not measure a guide surprise.", "committed L4 consensus_comparison.csv and run.py; QVS basis note"),
]
GAP_LOOKUP = {g["gap_id"]: g for g in GAPS}
FEE_TRIPLETS = {"sep": "September 14/16/18", "oct": "October 12/14/16"}


def classify(row):
    """Evidence use is separate from direct-model approval; all original cells stay intact."""
    p, m, status = row["package"], row["metric"], row["evidence_status"]
    if m not in METRIC_UNITS or row["units"] != METRIC_UNITS[m]:
        raise ValueError("Unknown metric or incompatible source units")
    information_day = source_date(row["information_date"])
    if source_date(row["source_information_date"]) > information_day:
        raise ValueError("Source publication cannot follow analysis information date")
    out = dict(row)
    ids = []
    definition, bounds, dependency, permission, reason = "", "No bounds supplied; absence is not zero or a probability interval.", "", "", ""
    parent = row["baseline_being_replaced"] or row["baseline_replaced"] or "No production baseline identified in original row."
    if p == "cohort_fx" and m in FX_CONDITIONAL | FX_DESCRIPTIVE:
        if status != "scenario_only_unidentified_exposure_and_timing" or row["treatment"] != FX_TREATMENTS[m]:
            raise ValueError("Unexpected FX evidence status")
        category = "usable_as_conditional_scenario" if m in FX_CONDITIONAL else "descriptive_only"
        definition = {
            "reference_normalized_kernel_revenue": "R0: inherited lambda times fixed-reference-currency weighted exposure; diagnostic denominator, not new revenue.",
            "ordinary_booking_kernel_revenue": "B: ordinary booking-FX kernel identity tied to the named inherited reported-USD baseline.",
            "rnpl_retimed_kernel_revenue": "T: cohort retiming scenario level; conditional alternative to the same B baseline.",
            "rnpl_fx_incremental_replacement": "T-B: incremental difference representing replacement of embedded booking FX; not an independent revenue driver.",
            "rnpl_fx_replacement_multiplier": "T/B: ratio of retimed to ordinary-booking kernel; one alternative representation of the same replacement.",
            "rnpl_fx_level_multiplier": "T/R0: reference-level factor; never a multiplier on the reported-USD kernel.",
        }[m]
        ids = ["L4_FORMAT", "FX_BASELINE", "FX_HEDGE", "FX_EXPOSURE", "FX_ROOT_QUOTES", "FX_ROUTE"]
        dependency = "Same quarter/scenario R0,B,T cohort construction and selected FX/u/p assumptions; T, T-B and T/B are mutually exclusive representations."
        permission = "Display the existing conditional arithmetic with its exact baseline and all assumed exposures/timing labels." if m in FX_CONDITIONAL else "Display the reference/baseline identity and accounting checks only."
        reason = "No empirical cohort identification, matched L4 baseline or reconciled forward hedge; existing JSON interface does not accept this metric/manifest."
    elif p == "fee_panel" and m == "fee_theta_log":
        if status != "blocked_future_or_missing_captures" or row["value"] != "" or row["treatment"] != "unavailable_do_not_apply":
            raise ValueError("Unavailable fee theta must remain blank")
        if row["scenario"] not in FEE_TRIPLETS:
            raise ValueError("Unknown fee month; do not pool monthly estimates")
        category = "unavailable"
        definition = "Unestimated log fraction of neutral fee repricing for the named fee-panel month."
        ids = ["FEE_CAPTURE", "FEE_IDENTIFICATION", "L4_FORMAT"]
        dependency = "Named monthly triplet " + FEE_TRIPLETS[row["scenario"]] + " only, matching monthly treatment/control, residence-specific fee schedule and non-overlapping ADR mechanics; no automatic pooling."
        permission = "Show unavailability and missing wave requirements only."
        reason = "Zero eligible observed wave CSVs at the frozen inventory time; missing coefficient is not a zero effect."
    elif p == "adr_hotel" and m in ADR_SCENARIOS:
        if status != "scenario_assumption_research_only" or row["treatment"] != "replacement":
            raise ValueError("Unexpected ADR scenario status/treatment")
        category = "usable_as_conditional_scenario"
        definition = {"adr_exfx_yoy": "Conditional ex-FX ADR year-over-year growth in percent; original percentage_points units lexeme is preserved, but this is a total growth rate rather than a component contribution.", "adr_reported_yoy": "Conditional reported-USD ADR year-over-year growth in percent; includes the selected booking FX path.", "adr_usd": "Conditional ADR in USD per night; already incorporates its named component, FX and K choices."}[m]
        bounds = "RSS component sensitivity range from the named scenario; not confidence, predictive, or independently additive endpoint probabilities."
        ids = ["ADR_ADOPTION", "ADR_FX_FEE", "ADR_NIGHTS_LAGS", "L4_FORMAT"]
        dependency = "One ADR route per quarter, matching nights and prior-year base; totals already contain component terms."
        permission = "Display a labelled ADR sensitivity as a candidate replacement for the same quarter operating ADR."
        reason = "Not a direct revenue adapter; L4 must explicitly select and reconcile operating inputs before any new calculation."
    elif p == "adr_hotel" and m in ADR_COMPONENTS:
        if not status.startswith("assumed_or_proxy_component:") or row["treatment"] != "descriptive":
            raise ValueError("Unexpected component provenance")
        category = "descriptive_only"
        definition = "Component contribution within the named ADR decomposition: " + m.removeprefix("adr_component_") + "; source measured/proxy/assumed qualifier retained verbatim."
        bounds = "Authored component assumption/sensitivity endpoints; not confidence intervals. Components can overlap economically and are already in total ADR."
        ids = ["ADR_ADOPTION", "ADR_FX_FEE"]
        dependency = "Parent named ADR total contains this component; residual pricing absorbs omitted mix; K is imposed mechanics."
        permission = "Explain the existing ADR scenario composition and which terms are measured proxies or assumptions."
        reason = "No independent incremental application; components already included and pricing residual/K are not causal estimates."
    elif p == "adr_hotel" and m == "gbv_identity_comparison":
        if status != "descriptive_identity_on_unadopted_nights_scenario" or row["treatment"] != "descriptive":
            raise ValueError("Unexpected GBV identity status")
        category = "descriptive_only"
        definition = "Same-quarter conditional ADR times nights identity in USD billions; unadopted operating scenario, not revenue."
        ids = ["ADR_ADOPTION", "ADR_NIGHTS_LAGS", "ADR_FX_FEE"]
        dependency = "Exact ADR/nights case; conversion to USDm requires multiplying USD billions by 1000, then correctly lagging GBV."
        permission = "Display the operating identity and its scenario inputs only."
        reason = "Existing conditional identity supplies neither actual GBV nor same-quarter revenue; no independent scenario adoption."
    elif p == "adr_hotel" and m in HOTEL:
        if row["treatment"] != "descriptive":
            raise ValueError("Hotel comparator cannot become a replacement")
        definition = "Year-over-year percent change of the named US lodging/hotel category price index; not Airbnb ADR."
        ids = ["HOTEL_MAPPING"]
        dependency = "Official index definition and dated quarter completeness; US category coverage differs from Airbnb global geography/property mix."
        if status == "missing_incomplete_quarter" and row["value"] == "":
            category, ids = "unavailable", ["HOTEL_COMPLETENESS", "HOTEL_MAPPING"]
            permission = "Show the quarter as incomplete and value unavailable."
            reason = "Only one of three months available in frozen evidence; no new source content located in bounded inventory."
        elif status == "descriptive_complete_quarter" and row["value"]:
            category = "comparator_only"
            permission = "Display the complete-quarter public index comparator with geography, vintage and mapping caveats."
            reason = "Observed comparator is not an observed ABNB input; no release-vintage reconstruction or validated production mapping."
        else:
            raise ValueError("Unexpected hotel evidence/value combination")
    elif p == "nclh" and m in NCLH:
        if not status.startswith("research_fail_") or row["treatment"] != "No ABNB forecast or valuation adjustment":
            raise ValueError("NCLH negative result must remain negative")
        category = "descriptive_only"
        definition = "Failed cross-issuer seasonal-naive USD-level RMSE comparison." if m.endswith("rmse_ratio") else "Realized 2023-2025 seasonal conversion coefficient range in percentage points, n=3 per season."
        ids = ["NCLH_NO_TRANSFER"]
        dependency = "NCLH issuer-specific current advance-ticket-sales balance and lagged issuer revenue; ex-COVID rules; W2 nested in W1."
        permission = "Cite the failed transferability/stability test with its actual window and n."
        reason = "Evidence of research failure remains useful, but no NCLH-to-ABNB numerical application is permitted."
    elif p == "conversion" and m in CONVERSION:
        expected_treatment = "descriptive" if m == "free_to_fixed_PIT_RMSE_ratio" else "descriptive_do_not_apply_as_production_replacement"
        if row["treatment"] != expected_treatment:
            raise ValueError("Conversion treatment changed")
        category = "descriptive_only"
        ids = ["CONVERSION_POLICY"]
        dependency = "Joint five-parameter full22 calibration; matched free/fixed USD OLS comparison distinct from the inherited operational seasonal estimator. W2 is nested in W1."
        permission = "Describe calibration uncertainty and the chronological promotion FAIL while retaining the fixed operational specification."
        reason = "Free/fixed RMSE ratios 1.165407390/1.015512948 fail promotion in W1 n14/W2 n10; descriptive fit is not production adoption."
        if m == "free_to_fixed_PIT_RMSE_ratio":
            if status not in {"chronological_PIT_n14_post_letter_no_guide_input", "chronological_PIT_n10_post_letter_no_guide_input"}:
                raise ValueError("Unexpected validation status")
            definition = "Paired-window free-weight divided by matched fixed-weight USD-level revenue RMSE, available post-letter; ratio above one is worse."
        else:
            if status != "fullsample_descriptive_calibration_n22_five_parameters":
                raise ValueError("Unexpected calibration status")
            definition = "Lagged-GBV driver coefficient w; not booking probability or dollar contribution share." if m == "shared_lag_w" else "Seasonal coefficient level in percent of weighted lagged GBV; divide by 100 for the dimensionless coefficient, not a growth-pp impact."
            bounds = "Joint year-block bootstrap sensitivity endpoints from only six year blocks; marginal bounds are not an independently combinable parameter box or calibrated forecast interval."
    else:
        raise ValueError(f"Unknown package/metric: {p}/{m}")
    if row["value"] == "" and category != "unavailable":
        raise ValueError("Missing numeric evidence cannot be promoted")
    for key in ("value", "lower", "upper", "lower_bound", "upper_bound", "baseline_value_usd"):
        if row[key] and not Decimal(row[key]).is_finite():
            raise ValueError("Nonfinite source cell")
    if not row["source_reference"].strip() or not row["information_date"].strip() or not row["source_information_date"].strip():
        raise ValueError("Missing source/vintage")
    additional = [GAP_LOOKUP[i]["exact_additional_inputs"] for i in ids]
    if p == "fee_panel":
        additional[ids.index("FEE_CAPTURE")] = "Eligible captured listing-stay panel for " + FEE_TRIPLETS[row["scenario"]] + "; valid capture timestamps, currency, nightly price, listing/stay identity, city and residence metadata, plus this month's treatment/control and prereg coverage gates. The other month's triplet is not required for this coefficient; no automatic pooling."
    out.update(consumption_status=category, l4_may_consume_now=permission,
               direct_l4_model_application="blocked", not_consume_reason=reason,
               exact_additional_inputs=" | ".join(additional),
               gap_ids=";".join(ids), metric_definition=definition, bounds_meaning=bounds,
               parent_baseline_contract=parent, dependency_contract=dependency,
               same_basis_expectations_rule="Revenue consensus is not expected management guide; see GUIDE_EXPECTATIONS.",
               classification_information_date="2026-09-14",
               model_adoption="none; unchanged fixed operational policy",
               original_row_sha256=sha(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()))
    return out


def classify_all(fields, rows):
    if len(rows) != 1187 or collections.Counter(r["package"] for r in rows) != PACKAGE_COUNTS:
        raise ValueError("Frozen package count conservation failed")
    keys = [(r["package"], r["quarter"], r["metric"], r["scenario"]) for r in rows]
    if len(set(keys)) != len(rows):
        raise ValueError("Duplicate semantic row key")
    result = []
    for i, row in enumerate(rows, 1):
        transformed = classify(row)
        if set(fields) != set(row) or any(transformed[k] != row[k] for k in fields):
            raise ValueError("Original metadata changed")
        transformed["original_row_number"] = str(i)
        result.append(transformed)
    return result


def load_inputs():
    if sha(PATH_INVENTORY.read_bytes()) != EXPECTED["path_inventory"]:
        raise ValueError("Supplemental path inventory hash mismatch")
    for name in ("l4_inputs.csv", "bundle.json"):
        if sha((BUNDLE / name).read_bytes()) != EXPECTED[name]:
            raise ValueError(f"Frozen bundle hash mismatch: {name}")
    manifest = INPUTS / "manifest.json"
    if sha(manifest.read_bytes()) != EXPECTED["inputs_manifest"]:
        raise ValueError("Frozen evidence manifest hash mismatch")
    frozen = json.loads(manifest.read_text(encoding="utf-8"))
    for name, checksum in frozen["files"].items():
        if Path(name).name != name or sha((INPUTS / name).read_bytes()) != checksum:
            raise ValueError("Frozen interface/inventory hash mismatch")
    interface = json.loads((INPUTS / "l4_interface_snapshot.json").read_text(encoding="utf-8"))
    contract_record = interface["source_manifest"][0]
    if sha(interface["contract_source"].encode()) != contract_record["sha256"]:
        raise ValueError("Committed L4 contract source hash mismatch")
    inventory = json.loads((INPUTS / "existing_data_inventory.json").read_text(encoding="utf-8"))
    return interface, inventory


def interface_namespace(snapshot):
    """Execute exact pinned contract and its four original helpers; no L4 I/O/model code."""
    namespace = dict(date=date, math=math, re=re, Path=Path, hashlib=hashlib, json=json)
    for body in snapshot["adapter_functions"].values():
        exec(compile(body, "committed_adapter_function", "exec"), namespace)
    tree = ast.parse(snapshot["contract_source"])
    # Remove only the import whose four helpers were supplied from the same commit.
    tree.body = [node for node in tree.body if not (isinstance(node, ast.ImportFrom) and node.module == "adapter")]
    exec(compile(tree, "committed_l4_contract", "exec"), namespace)
    return namespace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    output = Path(args.out).resolve()
    if output.exists():
        raise FileExistsError("Immutable output already exists")
    interface, inventory = load_inputs()
    fields, rows = read_csv(BUNDLE / "l4_inputs.csv")
    mapped = classify_all(fields, rows)
    output.mkdir(parents=True, exist_ok=False)
    write_csv(output / "consumption_matrix.csv", mapped, fields + [k for k in mapped[0] if k not in fields])
    write_csv(output / "information_gaps.csv", GAPS)
    ledger = []
    for r in interface["source_manifest"]:
        ledger.append(dict(source_type="committed_L4_blob", source_reference=r["path"], commit=r["commit"], git_blob=r["git_blob"], sha256=r["sha256"], role="read_only_interface_or_baseline_evidence"))
    for name in ("l4_inputs.csv", "bundle.json"):
        ledger.append(dict(source_type="frozen_L3_bundle", source_reference=(BUNDLE / name).relative_to(ROOT).as_posix(), commit="8821961853e4068febbfe2712f9a4e1036c9e629", git_blob="", sha256=EXPECTED[name], role="unchanged_classification_input"))
    for p in sorted(INPUTS.iterdir()):
        if p.is_file():
            ledger.append(dict(source_type="frozen_local_audit", source_reference=p.relative_to(ROOT).as_posix(), commit="", git_blob="", sha256=sha(p.read_bytes()), role="offline_evidence_snapshot_not_market_refresh"))
    ledger.append(dict(source_type="frozen_local_audit", source_reference=PATH_INVENTORY.relative_to(ROOT).as_posix(), commit="", git_blob="", sha256=EXPECTED["path_inventory"], role="filename_only_supplemental_inventory"))
    write_csv(output / "source_manifest.csv", ledger)
    write_csv(output / "existing_data_inventory.csv", inventory["files"])
    interface_rows = [
        ("committed_bytes", "verified", "All nine inspected L4 sources read from pinned Git blobs; working copies equal their committed bytes. No moving L4 input was consumed.", "source_manifest.csv"),
        ("manifest_compatibility", "blocked", "L3 bundle.json has research_source_commit and CSV payload; L4 requires commit plus files entries and JSON revenue_adapter rows. Existing contract rejects supplied research bundle.", "l3_contract.py:load_bundle"),
        ("row_compatibility", "blocked", "All 1187 source rows rejected by existing apply_row as incomplete; it requires revenue_timing_multiplier and exact baseline/cohort/hedge metadata.", "l3_contract.py:apply_row; focused test"),
        ("baseline_identity", "enforced", "Quarter/scenario/revenue must match; both lag reference exposures reconstruct exact booking-USD GBV and recognition allocation conserves exposure.", "l3_contract.py:timing_identity/apply_row; synthetic attack"),
        ("hedge_treatment", "enforced_when_provenance_supplied", "Application is (R-h)*multiplier+h; positive pre-hedge base, verified hedge status/source required; no second application allowed. Status text is supplied evidence, not independent verification.", "l3_contract.py:apply_row; synthetic attack"),
        ("root_quote_metadata", "upstream_validation_required", "No underlying quote period/cutoff/source fields are required. The pinned interface accepts a synthetic correct row without quote metadata and ignores contradictory extra quote fields. Assumed future FX is permitted only as explicitly labelled scenario.", "l3_contract.py:timing_identity; adapter.py:dated; synthetic attack"),
        ("commit_membership", "parent_verification_required", "Loader checks 40 lowercase hex commit syntax and local payload SHA256, but accepts a syntactically valid invented commit without Git membership verification. README explicitly documents parent responsibility.", "l3_contract.py:load_bundle; README.md; synthetic fixture"),
        ("same_basis_expectations", "unavailable", "Captured source metric is revenue. Existing guide-minus-revenue-consensus table remains arithmetically valid but does not establish a surprise to management-guide expectations.", "committed consensus_comparison.csv; run.py; guide_basis_audit.csv"),
        ("conversion_policy", "fixed_operational_retained", "Existing L4 fixed 2/3 policy remains the benchmark. L3 free-w descriptive fit failed chronological promotion; no automatic code route accepts its five fitted coefficients.", "committed L4 README; original conversion rows"),
    ]
    write_csv(output / "interface_audit.csv", [dict(check_id=a, audit_status=b, finding=c, committed_evidence=d, l4_commit=interface["l4_commit"]) for a,b,c,d in interface_rows])
    selected = [r for r in interface["consensus_comparison_rows"] if r["scenario"] == "review_with_k" and r["consensus_panel_family"] == "LSEG family"]
    # Preserve all original comparator fields and label the different forecast objects.
    comparison_rows = []
    for r in selected:
        own = next(f for f in interface["forecast_rows"] if f["scenario"] == r["scenario"] and f["quarter"] == r["quarter"])
        comparison_rows.append(dict(**r, own_revenue_musd=own["revenue_musd"], own_cushion_decimal=own["cushion_decimal"],
                                    revenue_minus_revenue_consensus_musd=str(Decimal(own["revenue_musd"])-Decimal(r["consensus_musd"])),
                                    guide_expectation_consensus="unavailable", same_basis_status="guide_minus_revenue_consensus_is_not_guide_surprise"))
    if not comparison_rows:
        raise ValueError("Pinned Yahoo/LSEG comparator not found; do not substitute vendor")
    write_csv(output / "guide_basis_audit.csv", comparison_rows)
    summary = dict(as_of="2026-09-14", original_bundle_information_date="2026-09-13",
                   inventory_timestamp_utc=inventory["audit_timestamp_utc"], l4_commit=interface["l4_commit"],
                   original_rows=len(rows), original_columns=len(fields), original_cells_preserved=len(rows)*len(fields),
                   package_counts=dict(collections.Counter(r["package"] for r in rows)),
                   status_counts={s: sum(r["consumption_status"] == s for r in mapped) for s in STATUSES},
                   direct_l4_applicable_rows=0, new_eligible_fee_wave_files=len(inventory["actual_capture_wave_files"]),
                   material_new_local_content_files=len(inventory["material_new_content_files"]),
                   newline_only_inventory_differences=sum(r["new_or_changed_bytes"] and r["content_equal_after_CRLF_to_LF"] for r in inventory["files"]),
                   conditional_status_means="Existing labelled scenario exhibit only; exact additional inputs and separate adoption still required before model application.",
                   prior_conclusions="Free-weight promotion FAIL in W1 n14 and nested W2 n10; fixed operational policy retained. NCLH FAIL; hotel production eligibility unchanged; fee theta unavailable.",
                   l4_interface_gaps="Research CSV manifest is incompatible with existing JSON loader; exact scenario/cohort/hedge bridge absent. Loader does not prove Git membership or require root rate quote metadata.",
                   intervals="No output is promoted to a probability or independently combinable bound.",
                   original_fields=fields)
    (output / "summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    manifest = {p.name: sha(p.read_bytes()) for p in sorted(output.iterdir()) if p.is_file()}
    (output / "manifest.json").write_text(json.dumps(dict(files=manifest, source_hashes=EXPECTED), indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
