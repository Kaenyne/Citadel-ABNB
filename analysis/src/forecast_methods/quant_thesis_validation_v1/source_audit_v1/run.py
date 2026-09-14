"""Immutable Q1 audit. No fitting, registry writes, network or protected edits."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
COMMIT = "8821961853e4068febbfe2712f9a4e1036c9e629"
RESEARCH_COMMIT = "7fb6fe0f248d5492b899672b9b70545da62d63ee"
L4_COMMIT = "29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70"
BUNDLE = "data/processed/forecast_methods/l3_bundle_v1"
EXPECTED = "9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970"
L4_FORECAST = "data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1/forecast.csv"
INPUTS = [
    "data/processed/overnight/02_kpi_panel_quarterly.csv",
    "data/processed/overnight/02_kpi_panel_long.csv",
    "data/processed/overnight/02_guidance_ledger.csv",
    "data/processed/forecast_methods/harness/calendar.csv",
    "data/processed/forecast_methods/harness/targets.csv",
    "data/manifests/edgar_filings_log.csv",
    "theos-past-research/research/guidance/data/manifests/source_documents.csv",
    "theos-past-research/research/guidance/data/normalized/guidance_events.csv",
    "theos-past-research/research/guidance/data/normalized/quarterly_actuals.csv",
    "theos-past-research/research/guidance/data/normalized/source_excerpts.csv",
    "data/processed/abnb_driver_history_quarterly.csv",
    "analysis/src/overnight/02_kpi_panel.py",
    "analysis/src/forecast_methods/kernel_engine_v2/engine.py",
    "data/raw/regulatory/quantification/abnb_2026q2_10q.html",
    BUNDLE + "/SHA256SUMS.json",
    BUNDLE + "/payload/conversion/source_manifest.csv",
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(path, commit=COMMIT):
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)


def rows(path):
    return list(csv.DictReader(io.StringIO(blob(path).decode("utf-8-sig"))))


def canon(q):
    return "20" + q[2:] + "Q" + q[0] if re.fullmatch(r"[1-4]Q\d{2}", q) else q


def csv_write(path, data):
    if not data:
        raise ValueError("Refuse schema-less empty output")
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, list(data[0]))
        writer.writeheader()
        writer.writerows(data)


def run(out):
    if out.exists():
        raise FileExistsError("New output path required: " + str(out))
    for commit in (COMMIT, RESEARCH_COMMIT, L4_COMMIT):
        subprocess.run(["git", "cat-file", "-e", commit + "^{commit}"], cwd=ROOT, check=True)
    manifests = []
    for path in INPUTS:
        data = blob(path)
        local = ROOT / path
        disk = local.read_bytes() if local.exists() else b""
        manifests.append(dict(path=path, commit=COMMIT, git_blob_sha256=sha(data),
                              disk_sha256=sha(disk), git_disk_exact=data == disk,
                              git_disk_text_equivalent=data.replace(b"\r\n", b"\n") == disk.replace(b"\r\n", b"\n")))
    bundle_manifest = blob(BUNDLE + "/SHA256SUMS.json")
    if sha(bundle_manifest) != EXPECTED:
        raise ValueError("Bundle manifest hash mismatch")
    payloads = json.loads(bundle_manifest)
    if len(payloads) != 108:
        raise ValueError("Unexpected bundle file count")
    bundle_check = []
    for path, expected in payloads.items():
        obj = blob(BUNDLE + "/" + path)
        actual = sha(obj)
        if actual != expected:
            raise ValueError("Git bundle mismatch: " + path)
        disk = (ROOT / BUNDLE / path).read_bytes()
        bundle_check.append(dict(path=path, expected_sha256=expected, git_sha256=actual,
                                 disk_sha256=sha(disk), git_pass=True, disk_pass=sha(disk) == expected))
    panel = rows(INPUTS[0])
    if len(panel) != 24 or len({r["quarter"] for r in panel}) != 24:
        raise ValueError("Frozen panel dimensions or uniqueness changed")
    cal = {r["print_quarter"]: r for r in rows(INPUTS[3])}
    docs = {r["fiscal_period"]: r for r in rows(INPUTS[6]) if r["document_type"] == "shareholder_letter"}
    events = {r["reported_period"]: r for r in rows(INPUTS[7])}
    long = {(r["quarter"], r["metric"]): r for r in rows(INPUTS[1])}
    # Provenance assertions are not upgraded to independent primary verification.
    availability = []
    material = []
    metrics = {"revenue_musd": "USD millions", "gbv_musd": "USD millions", "nights_m": "millions of nights and experiences/seats", "fx_pts_revenue": "percentage points of revenue YoY", "fx_pts_adr": "percentage points of ADR YoY"}
    for r in panel:
        q = canon(r["quarter"])
        c = cal[q]
        source_q = "2021Q3" if q == "2020Q3" else q
        d = docs.get(source_q, {})
        e = events.get(source_q, {})
        # Explicitly fix only the diagnostic availability map, never frozen calendar.
        date = cal[source_q]["print_date"]
        availability.append(dict(quarter=q, frozen_print_date=c["print_date"], source_period=source_q,
            conservative_available_date=date, available_after=date + "T23:59:59 America/New_York",
            source_url=d.get("source_url", ""), certainly_public_by_proxy=e.get("published_at_utc", ""),
            proxy_basis=e.get("event_notes", ""), filing_date=c["filing_date"],
            source_status="retained_source_metadata_not_independent_raw_validation",
            limit="2020Q3 sourced in 2021Q3 comparative; frozen date too early" if q == "2020Q3" else "clock is webcast proxy; original HTML not in committed letter store"))
        for metric, unit in metrics.items():
            lm = "gbv_busd" if metric == "gbv_musd" else metric
            provenance = long.get((r["quarter"], lm), {})
            value = r[metric]
            step = 100 if metric == "gbv_musd" and q >= "2021Q1" else (0.1 if metric in ("gbv_musd", "revenue_musd") and q < "2021Q1" else (1 if metric == "revenue_musd" else (0.1 if metric == "nights_m" else "")))
            state = "unavailable" if value == "" else ("calculated_from_reported_growth" if metric.startswith("fx") else "observed_source_transcription")
            material.append(dict(period=q, metric=metric, value=value, unit=unit,
                status=state, source_file=provenance.get("source_file", INPUTS[0]),
                source_url=d.get("source_url", ""), publication_date=date,
                admissible_origin="after " + date + " end-of-day; metadata-qualified",
                precision_increment=step, precision_meaning="source display increment; interval sensitivity only, not probabilistic error",
                primary_raw_in_baseline=False,
                verification="2026Q2 GBV and nights checked against SEC letter 2026-09-14" if q == "2026Q2" and metric in ("gbv_musd", "nights_m") else "retained metadata and source build independently traced",
                limitation="missing historical measurement" if value == "" else ("2020 revenue precision beyond letter integer needs original source vintage; does not affect W1 lead-time membership" if q < "2021Q1" and metric == "revenue_musd" else "No earliest-publication clock or raw-letter hash")))
    guides = [r for r in rows(INPUTS[2]) if r["metric"] == "revenue_usd_m" and r["guide_type"] == "range"]
    if len(guides) != 20:
        raise ValueError("Guide history changed")
    for r in guides:
        q = canon(r["print_quarter"])
        dollars = re.findall(r"\$(\d+\.\d+)\s+billion", r["quote"])
        if len(dollars) != 2 or any(abs(float(dollars[i]) * 1000 - float(r[col])) > 1e-6 for i, col in enumerate(("value_low", "value_high"))):
            raise ValueError("Guide numeric source quote mismatch: " + r["guide_id"])
        guide_quantum = max(1000 * 10 ** -len(value.split(".")[1]) for value in dollars)
        if r["print_date"] != docs[q]["document_date"]:
            raise ValueError("Guide/source document date mismatch: " + q)
        for metric, col in (("guide_low", "value_low"), ("guide_high", "value_high"), ("guide_mid", "value_mid")):
            material.append(dict(period=canon(r["target_period"]), metric=metric, value=r[col], unit="USD millions",
                status="calculated_endpoint_mean" if metric == "guide_mid" else "observed_management_range_endpoint",
                source_file=r["source_file"], source_url=docs[q]["source_url"], publication_date=r["print_date"],
                admissible_origin="target available for scoring after release, never as predictor of its own guide",
                precision_increment=guide_quantum, precision_meaning="issued range endpoint display quantum; nominal management choices, not probabilistic rounding error",
                primary_raw_in_baseline=False, verification="retained verified source quote metadata",
                limitation="original letter bytes unavailable in baseline; numeric range begins 2021Q4"))
    # Exact local filing HTML numerical check using text tokenization; no source refresh.
    from html import unescape
    text = unescape(re.sub(r"<[^>]+>", " ", blob(INPUTS[13]).decode("utf-8")))
    text = " ".join(text.split())
    if not all(v in text for v in ("27,247", "56,434", "23,447", "47,962")):
        raise ValueError("Precision example filing values missing")
    # Hold exact committed L4 retained operational coefficient fixed; no refit.
    l4_bytes = blob(L4_FORECAST, L4_COMMIT)
    l4_rows = list(csv.DictReader(io.StringIO(l4_bytes.decode("utf-8-sig"))))
    q3_lambda_values = {float(r["lambda_pct"]) / 100 for r in l4_rows if r["quarter"] == "2026Q3"}
    if len(q3_lambda_values) != 1:
        raise ValueError("Exact operational Q3 coefficient unavailable or ambiguous")
    lam = q3_lambda_values.pop()
    manifests.append(dict(path=L4_FORECAST, commit=L4_COMMIT, git_blob_sha256=sha(l4_bytes),
                          disk_sha256="external_git_object_only", git_disk_exact="not_applicable", git_disk_text_equivalent="not_applicable"))
    delta_q2 = 27247 - 27200
    delta_q1 = (56434 - 27247) - 29200
    delta_basis = (2 * delta_q2 + delta_q1) / 3
    precision = [
        dict(case="Q2 2026 GBV", n=1, frozen_musd=27200, precise_musd=27247, delta_musd=delta_q2, available_date="2026-08-06", status="observed_filing", note="Same date as letter; clock unavailable, use end-of-day"),
        dict(case="Q1 2026 GBV via H1 minus Q2", n=2, frozen_musd=29200, precise_musd=29187, delta_musd=delta_q1, available_date="2026-08-06", status="calculated_later_vintage", note="Not admissible at Q1 release on May 7 from this cited source"),
        dict(case="Q3 2026 weighted GBV base", n=2, frozen_musd=(2*27200+29200)/3, precise_musd=(2*27247+29187)/3, delta_musd=delta_basis, available_date="2026-08-06", status="calculated_sensitivity", note="Retained w=2/3; no model re-estimation"),
        dict(case="Q3 2026 revenue at exact operational lambda", n=2, frozen_musd=(2*27200+29200)/3*lam, precise_musd=(2*27247+29187)/3*lam, delta_musd=delta_basis*lam, available_date="2026-09-13", status="conditional_sensitivity", note=f"lambda={100*lam:.13f}% from immutable L4 September13 output; source precision available August6; no refit"),
        dict(case="Q3 two-lag GBV rounding envelope", n=2, frozen_musd=0, precise_musd=0, delta_musd=50*lam, available_date="2026-09-13", status="worst_case_half_width", note="Both source GBVs +/-50m at fixed exact lambda; dependent/unknown errors, not SD"),
    ]
    summary = dict(l3_commit=COMMIT, research_commit=RESEARCH_COMMIT, external_l4_commit=L4_COMMIT,
        manifest_sha256=EXPECTED, bundle_files=len(bundle_check), bundle_git_pass=sum(r["git_pass"] for r in bundle_check),
        bundle_disk_pass=sum(r["disk_pass"] for r in bundle_check), panel_quarters=len(panel), lag_complete_quarters=len(panel)-2,
        material_cells=len(material), unavailable_material_cells=sum(r["status"] == "unavailable" for r in material),
        historical_guide_ranges=len(guides), W1_max_n=14, W2_max_n=10,
        source_contract_in_baseline=False, archived_source_letter_files_in_baseline=0,
        result="identity PASS; availability and precision PARTIAL with explicit limits",
        estimated_parameters=0, source_precision_delta_Q3_revenue_musd=delta_basis*lam,
        operational_Q3_lambda_pct=100*lam,
        source_dates_corrected_in_new_map_only=["2020Q3"], network_required_for_rebuild=False)
    accepted_reconciliation = []
    for source in rows(BUNDLE + "/payload/conversion/source_manifest.csv"):
        p = source["path"]
        obj = blob(p)
        disk = (ROOT / p).read_bytes()
        accepted_reconciliation.append(dict(path=p, accepted_sha256=source["sha256"],
            git_sha256=sha(obj), disk_sha256=sha(disk),
            accepted_exact_match=source["sha256"] in (sha(obj), sha(disk)),
            accepted_crlf_render_match=sha(obj.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")) == source["sha256"]))
    if not all(r["accepted_exact_match"] or r["accepted_crlf_render_match"] for r in accepted_reconciliation):
        raise ValueError("Accepted conversion source identity failed")
    out.mkdir(parents=True)
    csv_write(out / "input_manifest.csv", manifests)
    csv_write(out / "bundle_checks.csv", bundle_check)
    csv_write(out / "observation_availability.csv", availability)
    csv_write(out / "material_input_ledger.csv", material)
    csv_write(out / "unavailable_cells.csv", [r for r in material if r["status"] == "unavailable"])
    csv_write(out / "source_precision_sensitivity.csv", precision)
    csv_write(out / "accepted_source_reconciliation.csv", accepted_reconciliation)
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, type=Path)
    run(ap.parse_args().out.resolve())
