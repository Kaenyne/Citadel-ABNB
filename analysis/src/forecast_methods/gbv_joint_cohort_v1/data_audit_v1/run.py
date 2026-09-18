"""Read-only schema/admissibility audit; no downloads, estimation or personal rows."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import subprocess

import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
PR60 = "dd3aa1440b152b46fdee8c094875d178b802d74a"
SAMPLES = "data/processed/github_altdata/samples/"


def source(key, path, unit, timing, use, reason, booking="absent", stay="absent", value="absent", cancel="absent", fees="absent", vintage="absent", date_cols="", manifest=""):
    return dict(source_id=key, path=path, unit=unit, timing=timing, allowed_use=use,
                decision_reason=reason, original_booking_date=booking, stay_date=stay,
                monetary_value=value, cancellation_history=cancel, platform_fees=fees,
                historical_vintage=vintage, date_columns=date_cols, manifest=manifest,
                direct_current_corporate_cohort_eligible=False)


SOURCES = [
    source("K2_recommended", "data/processed/forecast_methods/kernel_leadtime_v2/K2_recommended_prior.csv", "season x weighting; accommodation shares", "Mar2016-Feb2017; Jan-Mar pools years", "old_proxy_sensitivity_only", "Saved reconstructed Melbourne accommodation shares; not corporate fees; raw absent; reverse shares cannot identify forward conversion.", booking="reconstructed in upstream raw, not rows", stay="pooled month groups", value="relative accommodation proxy", vintage="single old sample"),
    source("K2_leadtime_month", "data/processed/forecast_methods/kernel_leadtime_v2/K2_leadtime_by_stay_month.csv", "stay month", "2014-2017 old study", "old_proxy_sensitivity_only", "Processed means/CDFs only; no booking-cohort denominator or cancellation ledger.", date_cols="stay_ym"),
    source("K2_raw_coverage", "data/processed/forecast_methods/kernel_leadtime_v2/K2_booked_date_coverage_by_month.csv", "stay month", "2014-2017 old study", "source_diagnostic", "Shows severe booking-date coverage truncation, not quarterly fee conversion.", date_cols="stay_ym"),
    source("K2_truncation", "data/processed/forecast_methods/kernel_leadtime_v2/K2_truncation_validation.csv", "simulation specification", "old Melbourne sample", "source_diagnostic", "Upstream truncation correction failed reference-mean recovery; preserve as uncertainty evidence."),
    source("financial_kpi", "data/processed/overnight/02_kpi_panel_quarterly.csv", "corporate fiscal quarter; USD millions", "printed quarterly series", "aggregate_model_input", "Provides reported net GBV and total revenue margins only; cannot uniquely allocate joint cohort cells.", value="corporate revenue / net reported GBV", vintage="separate publication calendar required", date_cols="quarter"),
    source("calendar_reopen", "data/processed/overnight2/A/A2_market_interval_table.csv", "market x capture interval", "2025-09 to2026-08; multiple capture intervals", "descriptive_corrob_only", "Reopening can be cancellation, blocks or delisting; rates lack prices/actual completion and original booking dates; no W1/W2.", booking="availability interval only", stay="future-horizon bands", cancel="reopening proxy only", vintage="snapshot0/snapshot1", date_cols="snapshot0|snapshot1"),
    source("rnpl_scenario_matrix", "data/processed/overnight2/D/D1_cohort_matrix_stay.csv", "booking quarter x assumed stay quarter; million nights", "2025-2026 scenario", "scenario_only", "Already a constructed allocation; not observed cohorts and cannot validate another fitted matrix.", booking="scenario index", stay="scenario columns", cancel="scenario elsewhere", date_cols="booking_quarter"),
    source("rnpl_scenario_parameters", "data/processed/overnight2/D/D1_rnpl_parameters.csv", "parameter", "mixed sourced/assumed", "assumption_audit", "Separates sourced disclosures from assumed quarterly RNPL shares and timing parameters."),
    source("PR60_daio_PIT", "data/processed/govdata_v2/qtd75_pit.csv", "quarter; 75-day flights YoY percent", "day75 and actual git commit_date", "dated_demand_feature_candidate", "Use only commit_date <= origin; target-quarter day75 unavailable at preceding-quarter guide. Demand proxy cannot identify booking-to-fee cells.", vintage="commit+commit_date", date_cols="q_start|day75|commit_date|last_entry_in_file"),
    source("PR60_daio_features", "data/processed/govdata_v2/C_feature_panel.csv", "quarter; flights YoY and nights targets", "2019-2026", "conditional_feature_candidate", "Use dedicated PIT table to gate release; full-quarter targets/features cannot be used before available. Flight quantity is neither booking date nor fee.", vintage="PIT variant linked externally", date_cols="quarter"),
    source("PR60_review_vintages", "data/processed/q3nowcast_v2/E/market_vintage_monthly.csv", "market x vintage x review month", "2023 captures with historical review dates", "source_diagnostic", "Review posting dates omit original booking, paid value, cancelled/no-review stays; second-vintage study rejects fixed survivor wedge.", stay="review month proxy", vintage="dump_date", date_cols="dump_date|ym"),
    source("PR60_review_raw_manifest", "data/processed/q3nowcast_v2/E/raw_manifest_vintage2023.csv", "raw file manifest", "March-May2023 captures pulled Sep2026", "source_diagnostic", "External raw-store paths and hashes are evidence of prior pull, not currently local raw files.", vintage="dump_date+pulled_at", date_cols="dump_date|pulled_at"),
    source("PR60_review_BA_sample", SAMPLES+"hf-buenosaires-airbnb-reviews/buenos_aires_reviews_head_2023-03_dump.csv", "individual review; sample", "2023 capture, historical posting dates", "schema_only", "Actual schema has date+listing id, not booking date/value/cancellation; no personal rows exported.", stay="review posting date only", vintage="single March2023 capture", date_cols="date", manifest="hf-buenosaires-airbnb-reviews"),
    source("PR60_WSDM_sample", SAMPLES+"bookingcom-multi-destination-trip-wsdm2021/bkng_trip_train_head.csv", "competitor reservation within trip", "2016-Feb2017 per manifest", "excluded", "CSV absent locally; README advertises created_date but manifest reports it absent. No prices/cancellations; multi-city selected competitor sample.", stay="checkin/checkout per manifest", manifest="bookingcom-multi-destination-trip-wsdm2021"),
    source("PR60_RecTour_sample", SAMPLES+"bookingcom-rectour24-accommodation-reviews/rectour24_train_users_head.csv", "competitor reviewed stay", "2023 stay-month integer", "excluded", "CSV absent locally; manifest schema has month, room_nights, no booking date, monetary values or cancellations; filtered reviewed stays.", stay="month integer per manifest", manifest="bookingcom-rectour24-accommodation-reviews"),
    source("PR60_BrightData_quotes", SAMPLES+"brightdata-booking-listings-sample-1001/brightdata_booking_1001.csv", "property x fixed search quotation", "Jan1-10 2025 requested stay dates", "excluded", "CSV absent locally; quotes with free-cancellation policy are not reservations or realized cancellations.", stay="queried stay dates", value="offered quote only", cancel="policy flag only", manifest="brightdata-booking-listings-sample-1001"),
    source("PR60_Boston_booked", SAMPLES+"sideye-boston-occupancy-tax-imputed-nights/long_date_booked.csv", "city x scrape interval; imputed nights", "Jul2018-May2019", "method_example_only", "Separate aggregate booking/stay margins cannot be joined as a joint matrix; calendar blocks ambiguous; raw never committed.", booking="scrape interval inference", value="mean nightly quote", vintage="scrape period labels", date_cols="dates", manifest="sideye-boston-occupancy-tax-imputed-nights"),
    source("PR60_Boston_stay", SAMPLES+"sideye-boston-occupancy-tax-imputed-nights/long_reservation_date_by_month.csv", "city x month; imputed nights", "month without year,2018-19 per manifest", "method_example_only", "No original booking key shared with booked-date panel; upstream code uses last availability transition and removes cancellation history.", stay="month only", value="mean nightly quote", date_cols="month", manifest="sideye-boston-occupancy-tax-imputed-nights"),
    source("PR60_iCal_demo", SAMPLES+"pixelcrash-sync-rentals-ical-merger/allservices_events.csv", "calendar event", "2019 single generation", "excluded", "All DTSTAMP values are same generation timestamp, not booking times; no prices/cancellation history; demo overlaps and inconsistent channels.", stay="dtstart/dtend", vintage="single file DTSTAMP only", date_cols="dtstart|dtend|dtstamp", manifest="pixelcrash-sync-rentals-ical-merger"),
    source("PR60_card_spend", SAMPLES+"opportunity-insights-tracker/Affinity - National - Daily.csv", "national day/week; spending change", "2018-12-31 to2024-06-16", "excluded_from_joint_model", "Truncated before late W2; no Airbnb merchant, reservation, stay or original booking fields; insufficient vintage path for forecast admission.", value="aggregate card-spend index", date_cols="year|month|day", manifest="opportunity-insights-tracker"),
    source("PR60_BNPL_adoption", SAMPLES+"augustliu-bnpl-merchant-dataset/BNPL_Merchant_Adoption_Date.csv", "merchant x provider", "2026 snapshot; inferred earlier captures", "excluded", "Directory presence/first web capture is not adoption event, RNPL participation, transaction volume or booking survival.", date_cols="first_confirmed_bnpl_date|adoption_date_best", manifest="augustliu-bnpl-merchant-dataset"),
    source("PR60_BNPL_financial", SAMPLES+"augustliu-bnpl-merchant-dataset/public_company_panel_data_2015-2026.csv", "company x quarter", "2015-2026 retrieved2026-08-09", "duplicate_aggregate_only", "SEC-derived aggregate revenue repeats accounting margins, not new joint cohort constraints; one extracted vintage does not prove original-vintage values.", value="corporate income statement", vintage="filing_date/accession retrieved_at", date_cols="period_end|filing_date|retrieved_at", manifest="augustliu-bnpl-merchant-dataset"),
    source("PR60_Texas_lodging", SAMPLES+"texas-comptroller-hotel-occupancy-tax/hotel_history_long.csv", "property x annual/quarter period", "2023 annual+2024Q3-2026Q2 partial", "excluded_from_joint_model", "Lodging receipts lack booking dates/cancellations; annual/quarter rows mixed, latest partial, narrow geography and no W1.", value="lodging receipts/revpar", date_cols="period", manifest="texas-comptroller-hotel-occupancy-tax"),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT/"data/processed/forecast_methods/gbv_joint_cohort_v1/data_audit_v1")
    args = parser.parse_args()
    out = args.out.resolve()
    if out.exists():
        raise FileExistsError(f"Choose a NEW output directory: {out}")
    ancestry = subprocess.run(["git", "merge-base", "--is-ancestor", PR60, "HEAD"], cwd=ROOT, capture_output=True)
    if ancestry.returncode:
        raise RuntimeError("PR60 is not a verified ancestor of HEAD")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    rows, fields, inputs = [], [], {}
    for spec in SOURCES:
        row = dict(spec)
        path = ROOT/spec["path"]
        row.update(local_exists=path.exists(), n_rows=None, n_columns=None, actual_columns="", sha256="")
        if path.exists():
            inputs[spec["path"]] = sha(path)
            frame = pd.read_csv(path, low_memory=False)
            row.update(n_rows=len(frame), n_columns=len(frame.columns), actual_columns="|".join(frame.columns), sha256=inputs[spec["path"]])
            for col in frame.columns:
                series = frame[col]
                date_field = col in spec["date_columns"].split("|")
                fields.append(dict(source_id=spec["source_id"], field=col, n_rows=len(frame), nonnull=int(series.notna().sum()), n_unique=int(series.nunique()), dtype=str(series.dtype), minimum=str(series.dropna().astype(str).min()) if date_field and series.notna().any() else "", maximum=str(series.dropna().astype(str).max()) if date_field and series.notna().any() else "", range_basis="lexical field range, not date inference" if date_field else ""))
            if spec["source_id"] == "PR60_BNPL_adoption":
                row["adoption_date_best_nonnull"] = int(frame.adoption_date_best.notna().sum())
            if spec["source_id"] == "PR60_iCal_demo":
                row["distinct_dtstamp"] = int(frame.dtstamp.nunique())
            if spec["source_id"] == "PR60_review_raw_manifest":
                row["manifest_raw_paths_local"] = sum(Path(p).exists() for p in frame.path)
            if spec["source_id"] == "PR60_daio_PIT":
                row["max_commit_lag_days"] = int(frame.lag_days.max())
        if spec["manifest"]:
            mp = ROOT/SAMPLES/spec["manifest"]/"manifest.json"
            if mp.exists():
                inputs[str(mp.relative_to(ROOT)).replace("\\", "/")] = sha(mp)
                info = json.loads(mp.read_text(encoding="utf-8-sig"))
                row.update(manifest_claimed_rows=info.get("rows", ""), manifest_claimed_columns=info.get("columns", ""), manifest_claimed_dates=info.get("date_range", ""), captured_or_pulled_at=info.get("pulled_at", ""))
        rows.append(row)
    # A manifest is an index, not evidence that every advertised sample is local.
    coverage = []
    for mp in sorted((ROOT/SAMPLES).glob("*/manifest.json")):
        info = json.loads(mp.read_text(encoding="utf-8-sig"))
        files = info.get("files", [])
        strings = [f for f in files if isinstance(f, str)]
        coverage.append(dict(slug=mp.parent.name, manifest_sha256=sha(mp), advertised_file_entries=len(files), string_file_entries=len(strings), advertised_files_present=sum((mp.parent/f).is_file() for f in strings), advertised_csv_files=sum(f.lower().endswith(".csv") for f in strings), advertised_csv_files_present=sum(f.lower().endswith(".csv") and (mp.parent/f).is_file() for f in strings), pulled_at=info.get("pulled_at", "")))
        inputs[str(mp.relative_to(ROOT)).replace("\\", "/")] = sha(mp)
    catalog_path = ROOT/"research/notes/github_altdata/catalog.csv"
    catalog = pd.read_csv(catalog_path)
    inputs[str(catalog_path.relative_to(ROOT)).replace("\\", "/")] = sha(catalog_path)
    selected = catalog[catalog.sample_slug.fillna("").isin([s["manifest"] for s in SOURCES if s["manifest"]])]
    out.mkdir(parents=True)
    pd.DataFrame(rows).to_csv(out/"evidence_inventory.csv", index=False)
    pd.DataFrame(fields).to_csv(out/"field_profile.csv", index=False)
    pd.DataFrame(coverage).to_csv(out/"sample_manifest_locality.csv", index=False)
    selected[[c for c in ["name", "sample_slug", "url", "source_family", "review_tier", "verdict", "time_coverage", "sample_issues"] if c in selected]].to_csv(out/"catalog_crosswalk.csv", index=False)
    additional = ["data/processed/github_altdata/samples/sideye-boston-occupancy-tax-imputed-nights/compute_reservations.py", "data/processed/github_altdata/samples/bookingcom-multi-destination-trip-wsdm2021/bkng_trip_README.md", "docs/github-altdata/INTEGRATION_PLAN.md"]
    for rel in additional:
        inputs[rel] = sha(ROOT/rel)
    missing_candidate_paths = ["data/raw/booking/rectour24_train_users.csv", "data/raw/booking/bkng_trip_train_head.csv"]
    summary = dict(pr60_commit=PR60, head=commit, pr60_ancestor=True,
                   catalog_rows=len(catalog), sample_manifests=len(coverage),
                   sources_audited=len(rows), local_table_sources=sum(r["local_exists"] for r in rows),
                   current_direct_joint_cohort_sources=0,
                   direct_cohort_gate="FAIL: no observed, current booking-date x fee-recognition-dollar ledger with compatible original-booking denominator and cancellation history",
                   admissible_computation="Aggregate margin model and sensitivity/identification analysis; dated flights may be a preregistered predictive auxiliary, never a cohort observation.",
                   input_sha256=inputs, missing_candidates={p:(ROOT/p).exists() for p in missing_candidate_paths})
    for rel, digest in inputs.items():
        if sha(ROOT/rel) != digest:
            raise RuntimeError(f"Input changed during audit: {rel}")
    (out/"summary.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k != "input_sha256"}, indent=2))


if __name__ == "__main__":
    main()
