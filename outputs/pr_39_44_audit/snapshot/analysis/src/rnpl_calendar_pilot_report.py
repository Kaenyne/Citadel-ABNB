"""Render the completed three-market pilot JSONs as a research note; no data fitting."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs/rnpl-calendar-pilot-20260910"


def pct(x):
    return "—" if x is None else f"{x:.1f}%"


def main():
    data = [json.loads((OUT / f"{m}.json").read_text(encoding="utf-8")) for m in ["austin", "rome", "sydney"]]
    with (ROOT / "data/processed/adr/14c_calendar_manifest.csv").open(encoding="utf-8-sig", newline="") as f:
        manifest = {(r["market"], r["date"]): r for r in csv.DictReader(f)}
    for d in data:
        for p in d["provenance"]:
            record = manifest[(d["market"], p["snapshot"])]
            assert record["url"] == p["source_url"]
            assert int(record["size"]) == p["compressed_bytes"]
    lines = ["# RNPL calendar pilot: Austin, Rome, Sydney", "",
             "Completed September 10, 2026. Local-data pilot only; no forecast adjustment or causal RNPL estimate.", "",
             "## Decision", "",
             "The calendar files support reproducible reopening and reclosure diagnostics for retained listing/stay-date keys. They do not identify canceled reservations, RNPL use, or platform net lost nights. Use this pilot to assess the proxy and prioritize reservation-event data, not to apply a Q3/Q4 cancellation haircut.", "",
             "The empirical finding is mixed rather than a common deterioration across markets. Rome's short-run reopening rises in the final interval, while Austin is roughly flat and Sydney declines. Rome's increase also appears in each of the first three fixed days-to-arrival bands, so it is not solely the change in the broad horizon mix. However, interval duration, calendar season, initial booking age, and traveler/policy mix remain uncontrolled. Treat Rome as a hypothesis for independent verification, not an identified RNPL effect.", "",
             "Broad reopening levels fall materially under the short-run screen in every market, and a substantial fraction of observed reopenings later become unavailable again. These results show why the raw calendar proxy cannot be mapped directly to permanent lost nights. Neither the stricter screen nor reclosure establishes true booking status.", "",
             "## Sample and provenance", "",
             "Austin, Rome, and Sydney were selected before inspecting outcomes: all have five vintages, with Europe and Asia-Pacific represented alongside the US. The code applies a fixed SplitMix64 hash to listing IDs and retains one hash bucket out of ten. The same ID is selected in every vintage. This is a deterministic approximately 10% listing sample, not a demonstrated population-representative sample. Results are night-weighted within it; no listing-night independence or statistical significance is assumed.", "",
             "All 15 source files fully parsed; sampled keys were checked for duplicates and sampled availability values validated. File URLs and byte sizes match the existing `data/processed/adr/14c_calendar_manifest.csv`. Fresh SHA-256 hashes are saved in the per-market JSONs; they fingerprint the files used, not an independently archived server hash. Source: Inside Airbnb, CC BY 4.0. The acquisition code streamed downloads without synthesizing rows.", "",
             "| Market | Raw rows read across vintages | Sampled listing-nights across vintages | Sample listings per vintage | Listings in all five |",
             "|---|---:|---:|---|---:|"]
    for d in data:
        ps = d["provenance"]
        lines.append(f"| {d['market']} | {sum(p['raw_rows'] for p in ps):,} | {sum(p['sample_rows'] for p in ps):,} | " + " / ".join(str(p["sample_listings"]) for p in ps) + f" | {d['coverage'][0]['stable_all_five_listings']:,} |")
    lines += ["", "These are repeated listing-night observations, not distinct reservations or distinct stayed nights.", "",
              "## Matching and attrition", "",
              "Join exact listing ID and stay date. Retain only stay dates strictly after the later snapshot; elapsed dates are never treated as conversions. Reopening = unavailable at first capture, available at second. The denominator is initially unavailable nights that remain observable in both captures. Missing listings are not treated as cancellations, bookings, or survival.", "",
              "| Market | Observation interval | Days apart | Future rows retained | Initially unavailable rows retained |",
              "|---|---|---:|---:|---:|"]
    for d in data:
        for c in d["coverage"]:
            lines.append(f"| {d['market']} | {c['snapshot0']} → {c['snapshot1']} | {c['interval_days']} | {pct(c['matched_future_row_retention_pct'])} | {pct(c['unavailable_row_retention_pct'])} |")
    lines += ["", "Retention refers to baseline dates still in the future at capture 2. Stable-all-five screens additionally condition on surviving future snapshots; they are descriptive sensitivity checks with look-ahead, not point-in-time backtests.", "",
              "## Reopening: broad versus screened", "",
              "Four regimes are saved. **Broad** is all matched keys. **Stable** requires the listing in all five vintages. **Screened** also requires less than 95% unavailable in each full calendar, unchanged minimum nights, and a minimum of at most seven nights. **Short-run** further requires an interior initial unavailable run of 1–14 consecutive days (runs touching a calendar boundary are excluded). These thresholds were selected before outcomes; they do not establish which dates are real bookings. Short-run selection intentionally changes the cohort and may select more transient states.", "",
              "| Market | Interval ending | Broad rate | Stable rate | Screened rate | Short-run rate | Short-run reopened / initially unavailable |",
              "|---|---|---:|---:|---:|---:|---:|"]
    for d in data:
        for c in d["coverage"]:
            rs = {r["regime"]: r for r in d["pairs"] if r["window"] == "all_future" and r["snapshot1"] == c["snapshot1"]}
            r = rs["screened_short_run"]
            lines.append(f"| {d['market']} | {c['snapshot1']} | " + " | ".join(pct(rs[k]["reopening_rate_pct"]) for k in ["all_matched", "stable_all_five", "screened", "screened_short_run"]) + f" | {r['reopened_nights']:,} / {r['initial_unavailable_nights']:,} |")
    lines += ["", "### Fixed-horizon cross-check: short-run reopening", "",
              "| Market | Days after second snapshot | March→June rate | June→August rate |",
              "|---|---|---:|---:|"]
    for d in data:
        ends = [c["snapshot1"] for c in d["coverage"]][-2:]
        for horizon in ["d001_030", "d031_060", "d061_090"]:
            rs = [next(r for r in d["pairs"] if r["snapshot1"] == end and r["regime"] == "screened_short_run" and r["window"] == horizon) for end in ends]
            lines.append(f"| {d['market']} | {horizon} | {pct(rs[0]['reopening_rate_pct'])} | {pct(rs[1]['reopening_rate_pct'])} |")
    lines += ["", "Different intervals are 60–100 days apart and cover different seasons/horizons. Their raw percentages cannot establish acceleration or deceleration in cancellation risk. Fixed 1–30, 31–60, 61–90, and 91–180 day-to-arrival slices are also in the JSONs; they still have different interval lengths and seasonal stay dates. No annualization or causal before/after estimate is made.", "",
              "The short-run regime also filters initially available spells in the underlying transition table. Its newly-unavailable and net-unavailable-change fields are not a full inventory-flow estimate and are not used here to infer demand or cancellation offsets. All regimes are selected subpopulations; the strictest one is not proven to be the most accurate.", "",
              "## Latest June-to-August interval: dates still ahead", "",
              "Q3 below covers only the remainder of Q3 after each market's August snapshot, not all Q3 stays and not cancellations recorded throughout Q3. Q4 covers the matched October–December stay dates. These are stay-date windows; reported Nights and Seats Booked uses booking/cancellation transaction dates.", "",
              "| Market | Stay-date window | Broad reopening | Short-run reopening | Short-run reopened / initial unavailable | Top 10 listings' share of short-run reopenings |",
              "|---|---|---:|---:|---:|---:|"]
    for d in data:
        last = d["coverage"][-1]["snapshot1"]
        for window in ["Q3_2026", "Q4_2026"]:
            rs = {r["regime"]: r for r in d["pairs"] if r["snapshot1"] == last and r["window"] == window}
            r = rs["screened_short_run"]
            lines.append(f"| {d['market']} | {window} | {pct(rs['all_matched']['reopening_rate_pct'])} | {pct(r['reopening_rate_pct'])} | {r['reopened_nights']:,} / {r['initial_unavailable_nights']:,} | {pct(r['top10_listings_share_of_reopenings_pct'])} |")
    lines += ["", "## Reopened then unavailable again", "",
              "The latest triple is March → June → August. Restrict to identical stay dates after the August capture, observable in all three. Among dates unavailable in March and available in June, count those unavailable again in August. Reclosure can represent a booking, a host block, or other calendar changes. It is not confirmed replacement booking and cannot be used as the rebooking offset in the RNPL materiality table.", "",
              "| Market | Regime | Reopened nights followed | Reclosed by August | Reclosed share |",
              "|---|---|---:|---:|---:|"]
    for d in data:
        last = d["coverage"][-1]["snapshot1"]
        for regime in ["all_matched", "screened_short_run"]:
            r = next(r for r in d["triples"] if r["snapshot2"] == last and r["window"] == "all_future" and r["regime"] == regime)
            lines.append(f"| {d['market']} | {regime} | {r['reopened_followed_nights']:,} | {r['reclosed_nights']:,} | {pct(r['reclosed_pct'])} |")
    lines += ["", "The denominator excludes reopened dates that elapsed before August or lost listing/date coverage. The JSON records pre-third-join reopened counts for the broad all-future cohort. There is no September/December observation after the final August capture, so June→August reopenings cannot yet be followed to a later reclosure or completed stay.", "",
              "## What this changes for the forecast", "",
              "Do not multiply these reopening rates by Airbnb nights or RNPL GBV share. The missing links are booking-versus-block classification, RNPL eligibility/use, guest origin, exact cancellation timestamps, treatment/control assignment, representative platform weights, and the cancellation risk already in the forecast. The directory starts after US RNPL launch and has no 2024 baseline. International snapshots cross global rollout, but also seasons and other policy changes; those comparisons are not a natural experiment without additional fields.", "",
              "The pilot establishes technical feasibility for matched calendar diagnostics and measures how much those diagnostics change under screening. It does not establish excess RNPL cancellations or rule them out. Keep the RNPL cancellation adjustment uncalibrated; prioritize a small reservation-event sample with booking/cancellation dates and RNPL or eligibility fields before expanding this analysis to all 34 markets.", "",
              "## Reproduction and checks", "",
              "Run `.venv/Scripts/python.exe analysis/src/rnpl_calendar_pilot.py`, then `.venv/Scripts/python.exe analysis/src/rnpl_calendar_pilot_report.py`. `--market austin` runs one market; `--self-test` runs a synthetic check covering elapsed/unmatched exclusion and known transition counts. The main run checks sampled key uniqueness, availability states, one-to-one joins and transition-count identities. Source manifest URL/size reconciliation checks run during report generation.", "",
              "Artifacts: [Austin](austin.json), [Rome](rome.json), [Sydney](sydney.json). Each holds provenance, raw/sample coverage, every horizon/regime pair, and three-capture reclosure results. No raw guest or reservation information was acquired; no existing forecast was changed."]
    (OUT / "pilot-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT / 'pilot-report.md'}; 15 source URL/size checks passed.")


if __name__ == "__main__":
    main()

