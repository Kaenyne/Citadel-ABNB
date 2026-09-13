"""Read-only integration audit of Lane 2 append provenance and LIVE rows."""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
from harness_v1_1 import RUN_DATE, registry as registry_api

OUT = ROOT / "data/processed/forecast_methods/lane2_validation_v1"
BASE = "051b03a864593f35c75236c8e1bcf4e0cc40c67e"


def parse_l0(raw):
    return list(csv.DictReader(line for line in raw.decode("utf-8-sig").splitlines()
                               if not line.startswith("#")))


def audit_append(backup):
    path = ROOT / "data/processed/forecast_methods/L0/L0_vintage_register.csv"
    before, after = backup.read_bytes(), path.read_bytes()
    committed = subprocess.check_output(["git", "show", f"{BASE}:{path.relative_to(ROOT).as_posix()}"], cwd=ROOT)
    assert before.replace(b"\r\n", b"\n") == committed.replace(b"\r\n", b"\n"), "backup content differs from the pre-lane committed register"
    assert after.startswith(before), "L0 original byte prefix changed"
    old, new = parse_l0(before), parse_l0(after)
    assert new[:len(old)] == old
    assert len({r["register_id"] for r in new}) == len(new), "duplicate L0 ID"
    admitted = new[len(old):]
    now = pd.Timestamp.now(tz="UTC")
    for row in admitted:
        assert row["role"] == "current", row
        assert row["pit_usable"].lower() == row["vendor_attributed"].lower() == "true", row
        assert row["vendor"] and row["vendor"] != "vendor_not_recorded", row
        assert float(row["n_estimates"]) > 0, row
        assert row["url"].startswith("https://"), row
        stamp = pd.Timestamp(row["as_of_timestamp"])
        assert stamp.tzinfo is not None and stamp <= now, row
        assert stamp.date() == RUN_DATE, row
    protected = [line for line in before.splitlines() if line.startswith(b"PG-2026Q3-revenue,")]
    assert len(protected) == 1 and after.splitlines().count(protected[0]) == 1
    assert admitted, "consensus package did not append any usable observation"
    return {"backup": backup.relative_to(ROOT).as_posix(),
            "backup_sha256": hashlib.sha256(before).hexdigest(),
            "before_rows": len(old), "after_rows": len(new), "admitted_rows": len(admitted),
            "original_byte_prefix_unchanged": True, "protected_aug6_line_byte_identical": True,
            "new_rows": admitted}


def audit_live(destination):
    all_live, format_live = [], []
    for path in sorted((ROOT / "data/processed/forecast_methods/registry").glob("*.csv")):
        frame = pd.read_csv(path)
        if "window" not in frame:
            continue
        if "format_version" in frame:
            modern_all = frame[frame.format_version.astype(str).eq("1.1")]
            for row in modern_all.itertuples():
                expected = pd.Period(row.quarter, freq="Q").ordinal - pd.Period(row.vintage_date, freq="Q").ordinal
                assert row.horizon_q == expected, f"FORMAT horizon unit mismatch: {path.name} {row.quarter} {row.vintage_date}"
        live = frame[frame.window == "LIVE"].copy()
        if live.empty:
            continue
        live["registry_file"] = path.relative_to(ROOT).as_posix()
        all_live.append(live)
        if "format_version" not in live:
            continue
        modern = live[live.format_version.astype(str) == "1.1"].copy()
        if modern.empty:
            continue
        registry_api.validate_registry_frame(modern.drop(columns=["registry_file", "format_version"]))
        assert (pd.to_datetime(modern.vintage_date).dt.date == RUN_DATE).all()
        format_live.append(modern)
    assert format_live, "no FORMAT 1.1 LIVE rows"
    rows = pd.concat(format_live, ignore_index=True)
    assert not rows.duplicated(["method", "object", "quarter", "vintage_date", "prior_basis", "spec_id"]).any()
    rows.to_csv(destination / "live_format_1_1_rows.csv", index=False)
    pd.concat(all_live, ignore_index=True).to_csv(destination / "all_live_rows.csv", index=False)
    return {"format_1_1_live_rows": len(rows),
            "by_method": rows.groupby("method").size().to_dict(),
            "run_date": str(RUN_DATE), "validated_with_existing_api": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backup", required=True)
    parser.add_argument("--stage", required=True)
    args = parser.parse_args()
    assert args.stage.replace("_", "").isalnum()
    destination = OUT / args.stage
    destination.mkdir(parents=True, exist_ok=True)
    report = {"audited_at_utc": dt.datetime.now(dt.timezone.utc).isoformat()}
    report["consensus_append"] = audit_append(ROOT / args.backup)
    report["live"] = audit_live(destination)
    report["verdict"] = "PASS"
    (destination / "integration_review.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "consensus_append"}, indent=2))
    print(f"L0: {report['consensus_append']['before_rows']} -> {report['consensus_append']['after_rows']}; byte prefix unchanged")


if __name__ == "__main__":
    main()
