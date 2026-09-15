"""Independent local-source replay; imports no data-audit or quant functions."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / "data/processed/forecast_methods/gbv_joint_cohort_v1"


def run(output):
    output = Path(output).resolve()
    if not output.is_relative_to(BASE / "review_v1"):
        raise ValueError("review outputs must be new children of review_v1")
    output.mkdir(parents=True, exist_ok=False)
    audit = BASE / "data_audit_v1"
    summary = json.loads((audit / "summary.json").read_text())
    inventory = pd.read_csv(audit / "evidence_inventory.csv")
    checks = []

    def check(label, passed, detail=""):
        checks.append({"check": label, "pass": bool(passed), "detail": str(detail)})

    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", summary["pr60_commit"], "HEAD"],
                              cwd=ROOT, capture_output=True)
    check("PR60 is ancestor of reviewed checkout", ancestor.returncode == 0, summary["pr60_commit"])
    for name, expected in summary["input_sha256"].items():
        path = ROOT / name
        check("source hash: " + name, path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() == expected)
    for row in inventory.itertuples():
        path = ROOT / row.path
        check("actual locality: " + row.source_id, path.exists() == bool(row.local_exists))
        if path.exists() and pd.notna(row.sha256):
            check("inventory hash: " + row.source_id, hashlib.sha256(path.read_bytes()).hexdigest() == row.sha256)
    for name, exists in summary["missing_candidates"].items():
        check("raw-candidate locality: " + name, (ROOT / name).exists() == exists)
    check("no candidate labelled direct/current corporate cohort",
          not inventory.direct_current_corporate_cohort_eligible.any())

    k2 = pd.read_csv(ROOT / "data/processed/forecast_methods/kernel_leadtime_v2/K2_recommended_prior.csv")
    k2 = k2.loc[k2.weighting.eq("value")]
    check("K2 four value groups", len(k2) == 4)
    check("K2 denominator retains3+tail", np.allclose(k2[["phi0", "phi1", "phi2", "phi3"]].sum(axis=1), 1))
    check("K2 sample count", k2.n_reservations.sum() == 268110)
    check("K2 source month labels retained", set(k2.melbourne_months) == {"1-2-3", "4-5-6", "7-8-9", "10-11-12"})
    trunc = pd.read_csv(ROOT / "data/processed/forecast_methods/kernel_leadtime_v2/K2_truncation_validation.csv")
    check("K2 correction did not recover reference mean", (trunc.ipw_mean_lead < trunc.true_mean_lead).all(),
          "IPW range %.5f..%.5f vs reference %.5f" % (trunc.ipw_mean_lead.min(), trunc.ipw_mean_lead.max(), trunc.true_mean_lead.iloc[0]))

    samples = ROOT / "data/processed/github_altdata/samples"
    columns = pd.read_csv(samples / "hf-buenosaires-airbnb-reviews/buenos_aires_reviews_head_2023-03_dump.csv", nrows=0).columns
    check("review actual header lacks booking/fee/cancellation", set(columns) == {"listing_id", "id", "date", "reviewer_id", "reviewer_name", "comments"})
    wsdm = json.loads((samples / "bookingcom-multi-destination-trip-wsdm2021/manifest.json").read_text())
    check("WSDM advertised created_date absent in sampled schema", "created_date" not in wsdm["columns"] and "absent" in wsdm["issues"])
    check("WSDM sampled reservation CSV unavailable here", not (samples / "bookingcom-multi-destination-trip-wsdm2021/bkng_trip_train_head.csv").exists())
    sideye = (samples / "sideye-boston-occupancy-tax-imputed-nights/compute_reservations.py").read_text()
    check("Sideye labels availability transitions as bookings", "(merged.available_prev == 't') & (merged.available_post == 'f')" in sideye)
    check("Sideye discards repeated reservation-date state", "reservations.groupby(['id', 'date']).last()" in sideye)
    flights = pd.read_csv(ROOT / "data/processed/govdata_v2/qtd75_pit.csv")
    valid = flights.dropna(subset=["commit_date", "day75"])
    dates = pd.to_datetime(valid.commit_date)
    day75 = pd.to_datetime(valid.day75)
    check("flight snapshot occurs no earlier than observation cutoff", dates.ge(day75).all())
    check("flight vintage lag arithmetic", np.array_equal((dates - day75).dt.days.to_numpy(), valid.lag_days.to_numpy()))
    check("flight panel has no joint cohort identifiers", not {"booking_date", "reservation_id", "recognized_fee"}.intersection(flights.columns))

    pd.DataFrame(checks).to_csv(output / "checks.csv", index=False)
    receipt = {"checks": len(checks), "passed": sum(c["pass"] for c in checks),
               "review_scope": "independent local source and schema replay; no model fit", "direct_current_cohort_status": "UNAVAILABLE",
               "reason": "No qualifying observed corporate booking-date x recognition-fee ledger; this is not rejection of a tested physical survival hypothesis.",
               "sources_audited": len(inventory), "source_review_summary": str((audit / "summary.json").relative_to(ROOT)),
               "bound_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in [audit / "summary.json", audit / "evidence_inventory.csv", Path(__file__)]}}
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt))
    if receipt["passed"] != receipt["checks"]:
        raise AssertionError("independent source review contains failed checks; retained in output")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    run(parser.parse_args().out)
