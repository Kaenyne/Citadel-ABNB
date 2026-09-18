"""Independent metadata/nominal-range checks of worker A's source audit."""
import argparse
import csv
import hashlib
import json
import re
from decimal import Decimal as D
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "data/processed/forecast_methods/quant_thesis_validation_v1"
REF = PKG / "source_audit_v1/results_v3"
REBUILT = PKG / "independent_reproduction_v1/source_rebuild_v1"


def read(p):
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def canon(q):
    if re.fullmatch(r"[1-4]Q\d\d", q):
        return f"20{q[2:]}Q{q[0]}"
    return q


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out.resolve()
    if out.exists() or not out.is_relative_to((PKG / "independent_reproduction_v1").resolve()):
        raise ValueError("New destination in independent_reproduction_v1 required")
    files = sorted(REF.iterdir())
    assert len(files) == 8
    reproduction = [{"file": p.name, "canonical_sha256": sha(p), "rebuild_sha256": sha(REBUILT / p.name),
                     "pass": p.read_bytes() == (REBUILT / p.name).read_bytes()} for p in files]
    assert all(x["pass"] for x in reproduction)
    guides = [r for r in read(ROOT / "data/processed/overnight/02_guidance_ledger.csv") if r["metric"] == "revenue_usd_m" and r["guide_type"] == "range"]
    calendar = {r["print_quarter"]: r for r in read(ROOT / "data/processed/forecast_methods/harness/calendar.csv")}
    source_docs = {r["fiscal_period"]: r for r in read(ROOT / "theos-past-research/research/guidance/data/manifests/source_documents.csv") if r["document_type"] == "shareholder_letter"}
    audit = read(REF / "material_input_ledger.csv")
    intervals = []
    for g in guides:
        quote_dollars = re.findall(r"\$([0-9.]+)\s+billion", g["quote"])
        lo, hi = [D(x) * 1000 for x in quote_dollars]
        mid = (lo + hi) / 2
        assert lo == D(g["value_low"]) and hi == D(g["value_high"]) and mid == D(g["value_mid"])
        q = canon(g["target_period"])
        sourceq = canon(g["print_quarter"])
        assert g["print_date"] == calendar[sourceq]["print_date"] == source_docs[sourceq]["document_date"]
        a = [r for r in audit if r["period"] == q and r["metric"] == "guide_mid"]
        assert len(a) == 1 and D(a[0]["value"]) == mid
        quantum = max(D(10) ** D(x.as_tuple().exponent) * 1000 for x in [D(t) for t in quote_dollars])
        assert D(a[0]["precision_increment"]) == quantum
        intervals.append({"target": q, "source_quarter": sourceq, "guide_date": g["print_date"],
                          "low_musd": str(lo), "high_musd": str(hi), "mid_musd": str(mid),
                          "source_display_quantum_musd": str(quantum), "administrative_mid_interval_low_musd": str(mid - D(".5")),
                          "administrative_mid_interval_high_musd": str(mid + D(".5")),
                          "interval_meaning": "protocol_scoring_convention_not_management_range_or_source_rounding_uncertainty"})
    assert len(intervals) == 20
    assert sum(D(x["source_display_quantum_musd"]) == 10 for x in intervals) == 19
    assert sum(D(x["source_display_quantum_musd"]) == 100 for x in intervals) == 1
    available = read(REF / "observation_availability.csv")
    for a in available:
        q = a["quarter"]
        date = calendar["2021Q3" if q == "2020Q3" else q]["print_date"]
        assert a["conservative_available_date"] == date
        assert a["available_after"] == date + "T23:59:59 America/New_York"
    early = next(a for a in available if a["quarter"] == "2020Q3")
    assert early["conservative_available_date"] == "2021-11-04" and early["source_period"] == "2021Q3"
    builder = (ROOT / "analysis/src/overnight/02_kpi_panel.py").read_text(encoding="utf-8-sig")
    assert 'src_q = "3Q21" if q == "3Q20" else "4Q20"' in builder
    later_filing = calendar["2023Q4"]
    assert later_filing["print_date"] == "2024-02-13" and later_filing["filing_date"] == "2024-02-16"
    missing = read(REF / "unavailable_cells.csv")
    assert len(missing) == 10 and all(r["value"] == "" and r["status"] == "unavailable" for r in missing)
    source_files = [ROOT / "analysis/src/forecast_methods/quant_thesis_validation_v1/source_audit_v1/run.py",
                    ROOT / "docs/revenue-forecast-strategy/quant_thesis_validation_v1/source_audit_v1/WP_Q1_SOURCE_AUDIT_v1.md"]
    receipt = {"reviewer": "/root/uncertainty_auditor", "author": "/root/source_auditor", "status": "PASS_source_reproduction_with_retained_original_vintage_limits",
               "canonical_output": str(REF.relative_to(ROOT)), "files_byte_identical": len(reproduction),
               "guide_ranges_independently_verified": len(intervals), "availability_rows_independently_checked": len(available),
               "guide_midpoint_interval": "nominal midpoint +/-0.5 USDm administrative protocol convention",
               "raw_letter_vintages_newly_recovered": 0, "sample_extended": False,
               "bound_author_files_sha256": {str(p.relative_to(ROOT)): sha(p) for p in source_files + files},
               "limitations": ["Exact original shareholder-letter bytes/SEC acceptance clocks absent in committed store.",
                               "Frozen values may carry later precision; date-qualified reconstruction is not original unrevised vintage data.",
                               "2020Q3 comparative availability is conservative source-based date, not first-publication claim.",
                               "Early revenue precision beyond retained quote remains unresolved."]}
    out.mkdir(parents=True)
    for name, data in [("byte_reproduction.csv", reproduction), ("guide_nominal_intervals.csv", intervals)]:
        with (out / name).open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(data[0]))
            writer.writeheader()
            writer.writerows(data)
    (out / "source_independent_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "bound_author_files_sha256"}, indent=2))


if __name__ == "__main__":
    main()
