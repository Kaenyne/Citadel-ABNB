"""Join the manually reviewed source ledger to the frozen pilot's Airbnb dates.

Verifies sample identity and cited raw capture hashes. Preserves evidence strength
and unknown operating states; does not turn catalog observations into migration.
"""
import csv
import hashlib
import json

from probe_listing_archives import ROOT, capture_timing
from summarize_listing_destinations import validate_sample_identity


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    with (ROOT / "data/raw/listing_churn_execution/destination_sample.csv").open(encoding="utf-8-sig", newline="") as handle:
        sample_rows = list(csv.DictReader(handle))
    ledger = json.loads((ROOT / "research/sources/listing_platform_history.json").read_text(encoding="utf-8"))
    validate_sample_identity(sample_rows, ledger["sample_identity_sha256"])
    sample = {row["case_id"]: row for row in sample_rows}
    rows, summaries, seen = [], [], set()
    for case in ledger["cases"]:
        case_id = case["case_id"]
        if case_id in seen or case_id not in sample:
            raise ValueError("Duplicate or unknown case: " + case_id)
        seen.add(case_id)
        source = sample[case_id]
        dates = dict(last_airbnb_present=source["last_present"], first_airbnb_absent=source["first_terminal_absence"])
        summaries.append(dict(case_id=case_id, **dates, identity=case["identity"], before_state=case["before_state"],
                              after_state=case["after_state"], conclusion=case["conclusion"]))
        for observation in case["observations"]:
            if "raw_path" in observation:
                digest = hashlib.sha256((ROOT / observation["raw_path"]).read_bytes()).hexdigest()
                if digest != observation["raw_sha256"]:
                    raise ValueError("Capture checksum changed: " + observation["raw_path"])
            timing = capture_timing(observation["date"].replace("-", "") + "000000",
                                    source["last_present"], source["first_terminal_absence"])
            rows.append(dict(case_id=case_id, **dates, evidence_date=observation["date"],
                             date_basis=observation["date_basis"], relative_timing=timing,
                             observed_on=ledger["investigated_on"], channel=observation["channel"],
                             state=observation["state"], finding=observation["finding"],
                             source_url=observation["source_url"], raw_sha256=observation.get("raw_sha256", "")))
    out = ROOT / "data/processed/listing_platform_history"
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "case_summary.csv", summaries)
    write_csv(out / "timeline.csv", sorted(rows, key=lambda row: (row["case_id"], row["evidence_date"], row["channel"])))
    print(f"Verified frozen sample and cited capture hashes; wrote {len(rows)} observations for {len(summaries)} targeted cases.")


if __name__ == "__main__":
    main()
