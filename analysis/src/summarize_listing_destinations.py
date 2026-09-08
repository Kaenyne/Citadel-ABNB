"""Join the fixed manual evidence ledger to the random sample and reconcile counts.

This does not infer destinations from web-search non-results or impute unknown cases.
Manual evidence is separate from generated outputs, so rerunning does not erase review.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import date
import hashlib
import json
from pathlib import Path

from execute_listing_churn import ROOT, write_csv

FINDINGS = {"sale_reported", "residential_rental_reported", "unresolved"}


def sample_identity_hash(sample):
    keys = ["case_id", "listing_id", "license_id", "first_terminal_absence"]
    identity = [{k:r[k] for k in keys} for r in sorted(sample, key=lambda r:r["case_id"])]
    return hashlib.sha256(json.dumps(identity, sort_keys=True).encode("utf-8")).hexdigest()


def validate_sample_identity(sample, expected_hash):
    if not expected_hash or sample_identity_hash(sample) != expected_hash:
        raise ValueError("The sample or exit dates changed. Do not attach old manual case labels to new properties; create a new evidence ledger.")


def reconcile(sample, evidence):
    sample_ids = [r["case_id"] for r in sample]
    evidence_ids = [r["case_id"] for r in evidence]
    if (not sample or len(set(sample_ids)) != len(sample_ids)
            or len(set(evidence_ids)) != len(evidence_ids) or set(sample_ids) != set(evidence_ids)):
        raise ValueError("Evidence must cover the fixed sample exactly once")
    sample_map = {r["case_id"]:r for r in sample}
    for r in evidence:
        for key in ('listing_id', 'license_id', 'first_terminal_absence', 'last_present'):
            if key in r and r[key] != sample_map[r['case_id']].get(key):
                raise ValueError(f'Manual evidence cannot change sample identity/timing: {key}')
        if r["finding"] not in FINDINGS:
            raise ValueError("Unsupported finding; update the documented evidence rules first")
        if r["finding"] != "unresolved":
            if not r.get("sources") or not r.get("event_date"):
                raise ValueError("A reported event requires a date and evidence source")
            if date.fromisoformat(r["event_date"]) < date.fromisoformat(sample_map[r["case_id"]]["first_terminal_absence"]):
                raise ValueError("Event predates observed absence; review its interpretation")
    return [{**sample_map[r["case_id"]], **r} for r in evidence]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=ROOT/"data/raw/listing_churn_execution")
    parser.add_argument("--output-dir", type=Path, default=ROOT/"data/processed/listing_churn_execution")
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    path = args.evidence or args.output_dir/"destination_evidence.json"
    ledger = json.loads(path.read_text(encoding="utf-8"))
    with (args.raw_dir/"destination_sample.csv").open(newline="", encoding="utf-8") as handle:
        sample = list(csv.DictReader(handle))
    validate_sample_identity(sample, ledger.get("sample_identity_sha256"))
    reviewed = reconcile(sample, ledger["cases"])
    fields = ["case_id", "finding", "event_date", "sale_event", "use_evidence", "identity",
              "match_basis", "other_platform_evidence", "timing", "caveat"]
    public = [{**{k:r.get(k, "") for k in fields}, "investigated_on":ledger["investigated_on"],
               "current_registry_match":int(r["registry_match_count"]) == 1,
               "sources":" | ".join(r["sources"])} for r in reviewed]
    write_csv(args.output_dir/"destination_review.csv", public)
    for r in reviewed:
        r["sources"] = " | ".join(r["sources"])
    all_fields = list(dict.fromkeys(k for r in reviewed for k in r))
    write_csv(args.raw_dir/"destination_sample_reviewed.csv",
              [{k:r.get(k, "") for k in all_fields} for r in reviewed])
    counts = Counter(r["finding"] for r in reviewed)
    metrics = [(name, counts[name], "Evidence found in pilot; not an estimated population destination share")
               for name in ("sale_reported", "residential_rental_reported", "unresolved")]
    metrics += [
        ("matched_other_platform_catalog", sum(r["other_platform_evidence"] == "matched_catalog_record" for r in reviewed),
         "Subset of unresolved; matching catalog record, no verified current bookings or migration"),
        ("candidate_other_platform_leads", sum(r["other_platform_evidence"].startswith("candidate_") for r in reviewed),
         "Subset of unresolved; primary verification or identity incomplete"),
        ("confirmed_new_platform_migration", 0, "No new migration established; does not mean no migration occurred"),
        ("current_registry_match", sum(int(r["registry_match_count"]) == 1 for r in reviewed),
         "Overlapping licensing flag, not property use; includes both reported event cases")]
    result = [{"metric":name, "count":n, "sample_denominator":len(reviewed), "interpretation":note}
              for name, n, note in metrics]
    write_csv(args.output_dir/"destination_summary.csv", result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
