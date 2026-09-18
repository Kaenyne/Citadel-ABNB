"""Independent Q5/Q6 bridge reproduction: no import of author calculation code."""
import argparse
import csv
import hashlib
import json
import subprocess
from decimal import Decimal as D, getcontext
from pathlib import Path

getcontext().prec = 40
ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "data/processed/forecast_methods/quant_thesis_validation_v1"
L4 = PKG / "evidence_v3/l4"
SRC_REL = "data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1"
SRC = L4 / SRC_REL
AUTHOR = PKG / "expectations_v1"
COMMIT = "29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70"
TOL = D("0.000001")


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(rows, **criteria):
    matched = [r for r in rows if all(r[k] == v for k, v in criteria.items())]
    if len(matched) != 1:
        raise ValueError((criteria, len(matched)))
    return matched[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out.resolve()
    if out.exists() or not out.is_relative_to((PKG / "accounting_review_v1").resolve()):
        raise ValueError("Use a new output within the exclusive accounting review package")
    source_names = ["forecast.csv", "cohort_weights.csv", "consensus_selection.csv", "cushion_inputs.csv"]
    for name in source_names:
        git_bytes = subprocess.check_output(["git", "show", COMMIT + ":" + SRC_REL + "/" + name], cwd=ROOT)
        if hashlib.sha256(git_bytes).hexdigest() != digest(SRC / name):
            raise ValueError("Extract differs from explicit L4 Git object: " + name)

    f = one(read(SRC / "forecast.csv"), quarter="2026Q4", scenario="review_with_k")
    cohorts = read(SRC / "cohort_weights.csv")
    g1 = D(one(cohorts, target_quarter="2026Q4", scenario="review_with_k", lag="1")["gbv_musd"])
    g2 = D(one(cohorts, target_quarter="2026Q4", scenario="review_with_k", lag="2")["gbv_musd"])
    lam, c = D(f["lambda_pct"]) / 100, D(f["cushion_decimal"])
    # Independent affine representation of fixed-kernel revenue versus unprinted G1.
    slope, intercept = D(2) * lam / 3, lam * g2 / 3
    r, q = slope * g1 + intercept, (slope * g1 + intercept) / (1 + c)
    checks = []

    def check(artifact, key, field, actual, expected):
        delta = abs(D(actual) - expected)
        checks.append({"artifact": artifact, "row_key": key, "field": field, "author_value": str(actual),
                       "independent_value": str(expected), "absolute_difference": str(delta), "pass": delta <= TOL})
        if delta > TOL:
            raise AssertionError((artifact, key, field, delta))

    check("L4_forecast", "2026Q4", "revenue_musd", f["revenue_musd"], r)
    check("L4_forecast", "2026Q4", "guide_musd", f["guide_musd"], q)
    panels = read(SRC / "consensus_selection.csv")
    author_same = read(AUTHOR / "same_basis.csv")
    author_be = read(AUTHOR / "break_even.csv")
    author_policy = read(AUTHOR / "cushion_policy.csv")
    assert len(panels) == len(author_same) == len(author_be) == 3
    cushions = {x["statistic"]: D(x["cushion_decimal"]) for x in read(SRC / "cushion_inputs.csv")}
    independent = []
    for p in panels:
        assert p["period"] == "2026Q4" and p["metric"] == "revenue" and p["unit"] == "musd"
        family, s = p["panel_family"], D(p["value"])
        same = one(author_same, panel_family=family)
        threshold = one(author_be, panel_family=family)
        for col in ["vendor", "observed_timestamp"]:
            assert same[col] == p[col] and threshold[col] == p[col]
        assert same["observed_guide_consensus_musd"] == "" and same["empirical_validation_n"] == "0"
        expected = {"own_revenue_musd": r, "street_revenue_musd": s, "revenue_gap_musd": r - s,
                    "revenue_gap_pct": (r - s) / s * 100, "own_cushion_pct": 100 * c, "own_guide_musd": q,
                    "different_object_guide_minus_revenue_musd": q - s, "hypothetical_street_guide_musd": s / (1 + c),
                    "hypothetical_common_cushion_guide_gap_musd": (r - s) / (1 + c)}
        for name, value in expected.items():
            check("same_basis.csv", family, name, same[name], value)
        gstar = g1 + (s - r) / slope
        lstar = lam * s / r
        own_cstar = (1 + c) * r / s - 1
        expected_be = {"g1_reference_musd": g1, "g1_break_even_musd": gstar, "g1_break_even_change_pct": 100 * (gstar - g1) / g1,
                       "lambda_reference_pct": 100 * lam, "lambda_break_even_pct": 100 * lstar,
                       "lambda_break_even_change_pp": 100 * (lstar - lam), "residual_revenue_factor_break_even": s / r,
                       "residual_revenue_change_pct": 100 * (s - r) / r, "own_cushion_break_even_pct": 100 * own_cstar,
                       "own_cushion_change_from_reference_pp": 100 * (own_cstar - c)}
        for name, value in expected_be.items():
            check("break_even.csv", family, name, threshold[name], value)
        check("inversion", family, "revenue_at_g1_boundary", slope * gstar + intercept, s)
        check("inversion", family, "guide_at_cushion_boundary", r / (1 + own_cstar), s / (1 + c))
        for label, cs in [("zero", D(0)), ("median", cushions["median"]), ("mean", cushions["mean"]), ("legacy_q4", D(".0388"))]:
            pr = one(author_policy, panel_family=family, imposed_street_cushion=label)
            for name, value in {"street_cushion_pct": 100 * cs, "hypothetical_street_guide_musd": s / (1 + cs),
                                "own_guide_musd": q, "hypothetical_gap_musd": q - s / (1 + cs),
                                "own_cushion_at_equality_pct": 100 * ((1 + cs) * r / s - 1)}.items():
                check("cushion_policy.csv", family + ":" + label, name, pr[name], value)
        independent.append({"panel_family": family, "n": 1, "empirical_validation_n": 0,
                            "revenue_gap_musd": str(r - s), "common_cushion_guide_gap_musd": str((r - s) / (1 + c)),
                            "g1_boundary_musd": str(gstar), "lambda_boundary_pct": str(100 * lstar),
                            "own_cushion_boundary_pct": str(100 * own_cstar),
                            "timestamp_precision": "date_only" if family != "LSEG family" else "minute_display_capture_at_15:20:58Z"})
    stress = read(AUTHOR / "stress_surface.csv")
    assert len(stress) == 35
    grid = {(str(g), str(D(l))) for g in [-5, -3, -1, 0, 1, 3, 5] for l in ["-.30", "-.10", "0", ".10", ".30"]}
    assert {(str(int(D(s["g1_change_pct"]))), str(D(s["lambda_change_pp"]))) for s in stress} == grid
    street = D(one(panels, panel_family="LSEG family")["value"])
    for sr in stress:
        gpct, lpp = D(sr["g1_change_pct"]), D(sr["lambda_change_pp"])
        gs, ls = g1 * (1 + gpct / 100), lam + lpp / 100
        # Exact factor product relative to baseline preserves all interactions.
        rs = r * (ls / lam) * ((D(2) * gs + g2) / (D(2) * g1 + g2))
        expected = {"g1_musd": gs, "lambda_pct": 100 * ls, "revenue_musd": rs, "guide_musd": rs / (1 + c),
                    "revenue_gap_to_lseg_musd": rs - street, "hypothetical_guide_gap_to_lseg_musd": (rs - street) / (1 + c)}
        for name, value in expected.items():
            check("stress_surface.csv", str(gpct) + ":" + str(lpp), name, sr[name], value)
        assert sr["probability"] == ""
    # A guide-policy perturbation alone leaves r and modeled earnings/cash inputs untouched.
    guide_only = {"revenue_musd": str(r), "median_guide_musd": str(q),
                  "mean_guide_musd": str(r / (1 + cushions["mean"])), "legacy_guide_musd": str(r / D("1.0388")),
                  "revenue_change_musd": "0", "direct_actual_earnings_change_musd": "0", "direct_cash_change_musd": "0"}
    bindings = {str(p.relative_to(ROOT)): digest(p) for p in [
        ROOT / "analysis/src/forecast_methods/quant_thesis_validation_v1/expectations_bridge.py",
        ROOT / "docs/revenue-forecast-strategy/quant_thesis_validation_v1/CHAIN_PROTOCOL_v1.md",
        *sorted(AUTHOR.glob("*")), *[SRC / n for n in source_names]] if p.is_file()}
    receipt = {"reviewer": "/root/uncertainty_auditor", "author": "/root", "status": "PASS_numerical_and_basis_review_with_timestamp_presentation_qualification",
               "independent_of_author_implementation": True, "author_functions_imported": False,
               "source_commit": COMMIT, "git_source_files_verified": 4, "numeric_checks": len(checks),
               "tolerance_musd": str(TOL), "max_abs_difference": str(max(D(x["absolute_difference"]) for x in checks)),
               "bound_inputs_code_and_outputs_sha256": bindings, "forecast_or_investment_adoption": False,
               "qualification": "S&P and Zacks timestamps are date-only; midnight values are normalized placeholders, not verified observation times."}
    out.mkdir(parents=True)
    for name, values in [("numeric_checks.csv", checks), ("critical_values.csv", independent)]:
        with (out / name).open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(values[0]))
            writer.writeheader()
            writer.writerows(values)
    (out / "guide_policy_only.json").write_text(json.dumps(guide_only, indent=2) + "\n")
    (out / "independent_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "bound_inputs_code_and_outputs_sha256"}, indent=2))


if __name__ == "__main__":
    main()
