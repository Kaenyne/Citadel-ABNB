"""Offline accounting contract. No forecasts, refits, registrations or raw-source writes."""
from __future__ import annotations
import argparse
import csv
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
AS_OF = "2026-09-14"
BUNDLE = ROOT / "data/processed/forecast_methods/l3_bundle_v1"
BASELINE = "inherited_K0_Q3_2026_reported_USD_kernel"
SOURCE = BUNDLE / "payload/cohort_fx/l4_adapter.csv"
ROUTES = {
    "reference_normalized_kernel_revenue": ("diagnostic_reference_level", "R0", "1", "USD"),
    "ordinary_booking_kernel_revenue": ("diagnostic_baseline_identity", "B", "1", "USD"),
    "rnpl_retimed_kernel_revenue": ("conditional_replace_B_with_T", "T", "1", "USD"),
    "rnpl_fx_incremental_replacement": ("conditional_add_delta_to_B", "T-B", "1", "USD"),
    "rnpl_fx_replacement_multiplier": ("conditional_multiply_B_by_T_over_B", "T", "B", "ratio"),
    "rnpl_fx_level_multiplier": ("diagnostic_reference_multiplier", "T", "R0", "ratio"),
}
REQUIRED = ["id", "numerator", "denominator", "units", "cohort_period", "recognition_period",
            "source_ids", "source_date", "admissible_origin", "evidence_status", "embedded_fx",
            "hedge_basis", "baseline_overlap", "treatment"]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("date must be an explicit YYYY-MM-DD")
    return date.fromisoformat(value)


def load_spec():
    spec = json.loads((HERE / "source_contract.json").read_text(encoding="utf-8"))
    validate_spec(spec)
    return spec


def validate_spec(spec):
    cutoff = parse_date(spec["audit_as_of"])
    if cutoff != parse_date(AS_OF):
        raise ValueError("wrong audit cutoff")
    sources = {s["id"]: s for s in spec["sources"]}
    if len(sources) != len(spec["sources"]):
        raise ValueError("duplicate source")
    for source in sources.values():
        if not re.fullmatch("[0-9a-f]{64}", source["sha256"]):
            raise ValueError("source hash invalid")
        if parse_date(source["first_known_date"]) > cutoff:
            raise ValueError("future source")
        if not parse_date(source["first_known_date"]) <= parse_date(source["reviewed_on"]) <= cutoff:
            raise ValueError("incoherent retrieval date")
        for key in ["url_or_path", "local_hash_path", "hash_basis", "section_scope"]:
            if not source[key].strip():
                raise ValueError("missing source provenance")
    seen = set()
    for row in spec["definitions"]:
        if row["id"] in seen:
            raise ValueError("duplicate definition")
        seen.add(row["id"])
        for key in REQUIRED:
            if not row.get(key) or isinstance(row[key], str) and not row[key].strip():
                raise ValueError("missing definition metadata: " + key)
        refs = row["source_ids"]
        if any(s not in sources for s in refs):
            raise ValueError("unknown source")
        known = max(parse_date(sources[s]["first_known_date"]) for s in refs)
        if not known <= parse_date(row["source_date"]) <= parse_date(row["admissible_origin"]) <= cutoff:
            raise ValueError("incoherent information dates")
        if bool(row.get("allowed_route", "").strip()) == bool(row.get("unusable_reason", "").strip()):
            raise ValueError("exactly one route or unusability reason required")
        if row["evidence_status"] == "unavailable" and row.get("allowed_route"):
            raise ValueError("unavailable definition cannot be admitted")
        if row["id"] in ROUTES:
            expected = ROUTES[row["id"]]
            actual = tuple(row[k] for k in ["allowed_route", "numerator", "denominator", "units"])
            if actual != expected:
                raise ValueError("metric denominator/unit/route mismatch")
    fact_ids = set()
    for fact in spec["facts"]:
        if fact["id"] in fact_ids:
            raise ValueError("duplicate fact")
        fact_ids.add(fact["id"])
        if fact["source_id"] not in sources or not fact["section"].strip() or not fact["paraphrase"].strip():
            raise ValueError("fact provenance invalid")
        if fact["source_date"] != sources[fact["source_id"]]["first_known_date"]:
            raise ValueError("fact source date mismatch")
    event_ids = set()
    for event in spec["events"]:
        if event["event"] in event_ids or not all(event[k].strip() for k in event):
            raise ValueError("duplicate or missing event metadata")
        event_ids.add(event["event"])
        if set(event["fact_ids"].split(";")) - fact_ids or parse_date(event["review_date"]) > cutoff:
            raise ValueError("event provenance/date invalid")
    if set(ROUTES) - seen:
        raise ValueError("missing exported metric definition")


def read_rows(path=None):
    path = SOURCE if path is None else path
    with Path(path).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_bound_rows():
    """Every admission path must prove source identity before rebuilding rows."""
    expected = load_spec()["bundle_fx_sha256"]
    if sha(SOURCE) != expected:
        raise ValueError("frozen bundle FX input changed")
    return read_rows(SOURCE)


def enrich_rows(rows):
    spec = load_spec()
    defs = {r["id"]: r for r in spec["definitions"]}
    output = []
    seen = set()
    for i, row in enumerate(rows, 1):
        key = row["quarter"], row["scenario"], row["metric"]
        if key in seen:
            raise ValueError("duplicate source row")
        seen.add(key)
        route, numerator, denominator, units = ROUTES[row["metric"]]
        if row["units"] != units or row["baseline_being_replaced"] != BASELINE:
            raise ValueError("source units/baseline mismatch")
        if row["quarter"] != "2026Q3" or parse_date(row["information_date"]) > parse_date(AS_OF):
            raise ValueError("source period/date mismatch")
        for field in ["value", "lower", "upper", "baseline_value_usd"]:
            if row[field] and not math.isfinite(float(row[field])):
                raise ValueError("nonfinite source financial value")
        d = defs[row["metric"]]
        new = dict(row)
        new.update({"contract_row_id": f"cohort_fx:{i:04d}",
                    "contract_source_row_sha256": hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                    "contract_audit_date": AS_OF, "contract_numerator": numerator,
                    "contract_denominator": denominator, "contract_units": units,
                    "contract_cohort_period": "2026Q1;2026Q2", "contract_recognition_period": "2026Q3",
                    "contract_source_ids": ";".join(d["source_ids"]),
                    "contract_source_date": row["information_date"],
                    "contract_admissible_origin": AS_OF,
                    "contract_evidence_status": "conditional_scenario" if route.startswith("conditional") else "descriptive_diagnostic",
                    "contract_hedge_basis": "inherited_reported_lambda_unreconciled_no_certified_hedge_preservation",
                    "contract_embedded_fx": row["embedded_fx"],
                    "contract_baseline_overlap": "same_B_already_contains_booking_FX_and_baseline_net_cancellations",
                    "contract_treatment": d["treatment"], "contract_allowed_route": route,
                    "contract_unusable_reason": "", "contract_direct_L4_use": "unavailable",
                    "contract_direct_L4_unusable_reason": "no_compatible_L4_baseline_manifest_or_prehedge_bridge;unidentified_u_and_fixing;p_scenario_only",
                    "contract_exclusivity_group": row["quarter"] + ":" + row["scenario"] + ":one_of_T_delta_ratio",
                    "contract_long_stay_qualification": "recognition_period_includes_monthly_anniversaries_for_stays_at_least_28_nights"})
        output.append(new)
    return output


def validate_conditional_use(rows, request):
    """Admit one arithmetic exhibit route, never production or a new hedge assumption."""
    if len(rows) != 1:
        raise ValueError("choose exactly one mutually exclusive financial route")
    row = rows[0]
    route = row["contract_allowed_route"]
    if not route.startswith("conditional_"):
        raise ValueError("diagnostic cannot adjust a reported baseline")
    canonical = {r["contract_row_id"]: r for r in enrich_rows(load_bound_rows())}
    if row != canonical.get(row["contract_row_id"]):
        raise ValueError("row is not the immutable bound accounting contract")
    expected = {"use": "conditional_exhibit_only", "baseline_id": BASELINE,
                "baseline_currency_basis": "reported_USD", "u_denominator": "reference_basis_recognized_revenue_flow",
                "u_evidence": "scenario", "fixing_evidence": "scenario_hypothesis",
                "hedge_policy": "inherited_hedges_unresolved_no_new_hedge_or_afterhedge_claim", "cash_recognition_equivalence": False,
                "rnpl_incremental_demand": 0, "extra_cancellation_haircut": 0,
                "new_hedge_amount": None, "extra_fx_layer": False}
    for key, value in expected.items():
        if key not in request or request[key] != value:
            raise ValueError("incompatible conditional contract: " + key)
    if request.get("baseline_value_usd") != row["baseline_value_usd"]:
        raise ValueError("baseline amount must exactly match the bound source representation")
    if not parse_date(row["contract_admissible_origin"]) <= parse_date(request["origin"]) <= parse_date(AS_OF):
        raise ValueError("origin outside this contract's evidence cutoff")
    if request.get("target_period") != row["quarter"] or request.get("scenario") != row["scenario"]:
        raise ValueError("cohort/scenario/target mismatch")
    return {"route": route, "status": "conditional_exhibit_only", "production_adoption": False}


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False, separators=(",", ":")) if isinstance(v, (list, dict)) else v for k, v in row.items()})


def run(out):
    spec = load_spec()
    original = load_bound_rows()
    enriched = enrich_rows(original)
    if len(enriched) != 1080:
        raise ValueError("expected all 1080 original cohort-FX rows")
    out = Path(out).resolve()
    allowed = ROOT / "data/processed/forecast_methods/l3_source_contract_v1"
    if not out.is_relative_to(allowed) or out == allowed:
        raise ValueError("output must stay inside new source-contract data package")
    if out.exists():
        raise FileExistsError("output directory already exists; choose a new version")
    out.mkdir(parents=True)
    for name, rows in [("source_manifest.csv", spec["sources"]), ("primary_facts.csv", spec["facts"]),
                       ("timing_contract.csv", spec["events"]), ("definition_contract.csv", spec["definitions"]),
                       ("accounting_contract.csv", enriched)]:
        write_csv(out / name, rows)
    summary = {"audit_as_of": AS_OF, "original_fx_rows": len(enriched), "definitions": len(spec["definitions"]),
               "events": len(spec["events"]), "primary_facts": len(spec["facts"]), "new_fitted_parameters": 0,
               "conditional_arithmetic_rows": sum(r["contract_allowed_route"].startswith("conditional_") for r in enriched),
               "direct_L4_admitted_rows": 0, "production_adoption": "pending_no_change",
               "review_status": "implementation_ready_for_independent_review"}
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    manifest = [{"path": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": sha(p)} for p in [SOURCE, HERE / "source_contract.json", HERE / "run.py"]]
    write_csv(out / "run_inputs.csv", manifest)
    sums = {p.name: sha(p) for p in sorted(out.iterdir())}
    (out / "SHA256SUMS.json").write_text(json.dumps(sums, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    run(parser.parse_args().out)
