"""Build review memo/card from explicitly selected, hashed L4 snapshots.

No price recommendation, investment probability, live research, registry or
scorer operation is performed. Each invocation writes a new version directory.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from render import render

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "data/processed/forecast_methods/lane4_review_v1"
DECK = ROOT / "deck/drafts/lane4_v1"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows):
    if not rows:
        raise ValueError("Refusing empty output table")
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fields)
        writer.writeheader()
        writer.writerows(rows)


def num(row, key):
    import math
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"Nonfinite {key}")
    return value


def one(rows, **conditions):
    selected = [r for r in rows if all(str(r.get(k)) == str(v) for k, v in conditions.items())]
    if len(selected) != 1:
        raise ValueError(f"Expected unique {conditions}, got {len(selected)}")
    return selected[0]


def validate_financial_row(row):
    fcf = (num(row, "adj_ebitda") + num(row, "interest_income") - num(row, "interest_expense")
           - num(row, "cash_taxes") + num(row, "d_unearned") + num(row, "wc_resid") - num(row, "capex"))
    if abs(fcf - num(row, "fcf")) > 0.001:
        raise ValueError("Annual cash-flow bridge does not reconcile")
    if abs(num(row, "fcf") - num(row, "sbc") - num(row, "sbc_adj_fcf")) > 0.001:
        raise ValueError("SBC-adjusted cash flow does not reconcile")


def validate_valuation_row(row):
    if num(row, "fy27_shares_m") <= 0:
        raise ValueError("Shares must be positive")
    ev = num(row, "exit_multiple") * num(row, "fy27_ebitda_musd")
    equity = ev + num(row, "fy27_net_cash_musd")
    value = equity / num(row, "fy27_shares_m")
    for field, expected in [("enterprise_value_musd", ev), ("equity_value_musd", equity), ("value_per_share", value)]:
        if abs(num(row, field) - expected) > 0.001:
            raise ValueError(f"Valuation bridge mismatch: {field}")


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"] +
                     ["| " + " | ".join(str(v).replace("|", "/") for v in r) + " |" for r in rows])


def snapshot(source_dir, target_dir, names, manifest):
    target_dir.mkdir(parents=True, exist_ok=False)
    for name in names:
        path = source_dir / name
        if not path.is_file():
            raise FileNotFoundError(path)
        before = digest(path)
        shutil.copyfile(path, target_dir / name)
        if digest(path) != before or digest(target_dir / name) != before:
            raise ValueError(f"Changing input during snapshot: {path}")
        manifest.append({"source": str(path), "snapshot": str(target_dir / name), "sha256": before,
                         "evidence_status": "upstream conditional calculation"})


def source_copies(target, manifest):
    sources = {
        "adr.csv": "data/processed/adrv3/P/adr_card_v3.csv",
        "lambda_rule.json": "data/processed/forecast_methods/rnpl_v2/lambda_card_rule.json",
        "legacy_valuation.csv": "data/processed/forecast_methods/valuation_v1/football_field_reconciliation.csv",
        "a2_b2_f_claims.md": "docs/revenue-forecast-strategy/05_backtests/LANE2_MEMO_READY_CLAIMS.md",
        "f_rnpl.md": "docs/revenue-forecast-strategy/05_backtests/ALPHA_F_RNPL.md",
        "adr_synthesis.md": "docs/adrv3/SYNTHESIS.md",
        "lane1_claims.md": "docs/revenue-forecast-strategy/05_backtests/LANE1_MEMO_READY_CLAIMS_v2.md",
        "d_card.md": "docs/revenue-forecast-strategy/05_backtests/D_CARD_ADDENDUM_LAMBDA.md",
        "convention.md": "docs/thesis-kernel-topdown/lane2/CONVENTION.md",
        "memo_v0_reference.md": "deck/drafts/memo_v0_2026-09-11.md",
    }
    target.mkdir(parents=True, exist_ok=False)
    for name, source in sources.items():
        path = ROOT / source
        raw = path.read_bytes()
        (target / name).write_bytes(raw)
        manifest.append({"source": source, "snapshot": str(target / name),
                         "sha256": hashlib.sha256(raw).hexdigest(),
                         "evidence_status": "committed evidence; not a new re-estimation"})


def build_card(forecast, adr, rule, destination):
    q3 = one(forecast, scenario="review_with_k", quarter="2026Q3")
    q4 = one(forecast, scenario="review_with_k", quarter="2026Q4")
    adr3 = one(adr, quarter="3Q26", variant="v3_with_K", fx_estimator="midpoint")
    base = num(rule, "base_musd")
    warning, escalation = num(rule, "warn_below_lambda_pct"), num(rule, "escalate_below_lambda_pct")
    rows = [
        {"id": "L4-C01", "metric": "2026Q3 consolidated revenue conversion", "unit": "%", "definition": f"100 * Q3 revenue USDm / {base:.12f}; fixed card denominator (2*27200+29200)/3", "reference": f"warning {warning}%; escalation {escalation}%", "score": "NO ALARM if lambda interval low>=17.09; WARN if low>=16.93 and high<17.09; ESCALATE if high<16.93; otherwise AMBIGUOUS; missing=ABSENT", "source": "Q3 2026 shareholder letter/10-Q revenue; frozen F lambda_card_rule.json", "rounding": "Integer USDm revenue +/-0.5; denominator fixed by definition", "status": "UNSIGNED diagnostic; cannot identify RNPL cancellations"},
        {"id": "L4-C02", "metric": "2026Q4 guide midpoint", "unit": "USD millions", "definition": "Arithmetic mean of management's Q4 revenue guide endpoints", "reference": f"review_with_k {num(q4, 'guide_musd'):.9f}", "score": "Report midpoint minus each frozen scenario; absolute and % error; endpoint-rounding interval versus forecast. No arbitrary hit tolerance. Score versus each vendor separately.", "source": "Q3 letter: Q4 revenue guidance; L4 forecast snapshot; dated consensus snapshot", "rounding": "Round each published endpoint by half its stated precision; midpoint extrema average endpoint extrema", "status": "UNSIGNED forecast comparison; no probability of beat/miss asserted"},
        {"id": "L4-C03", "metric": "2026Q3 revenue", "unit": "USD millions", "definition": "Reported consolidated revenue for quarter ended 30 September 2026", "reference": f"review_with_k {num(q3, 'revenue_musd'):.9f}", "score": "Report observed interval minus each scenario. No guide hit awarded by comparing revenue with Q4 guide.", "source": "Q3 letter/10-Q; L4 forecast snapshot", "rounding": "Whole USDm +/-0.5", "status": "UNSIGNED; current-quarter nights absent from two-lag revenue equation"},
        {"id": "L4-C04", "metric": "2026Q3 take rate jointly with GBV", "unit": "%; USD millions", "definition": "100 * Q3 consolidated revenue / Q3 GBV; show both denominator and revenue", "reference": "Inherited diagnostic 18.10% with GBV >=26300 USDm; adoption open", "score": "Apply ratio extrema using both rounding intervals; pair threshold only wholly met when TR low>=18.10 and GBV low>=26300. Crossing=AMBIGUOUS. Never a cover/reverse instruction.", "source": "Q3 letter revenue and GBV; AGENT_BRIEF proposed joint diagnostic", "rounding": "Use precision of original units: USD billions to USDm before half-unit bounds; do not assume GBV exact", "status": "UNSIGNED candidate; cutoff not newly calibrated"},
        {"id": "L4-C05", "metric": "2026Q3 reported ADR", "unit": "USD/night; percentage-point YoY", "definition": "Company reported blended ADR and its year-over-year comparison with prior-year reported blended ADR", "reference": f"ADR v3 midpoint with-K {num(adr3,'adr_usd_point'):.2f}; central scenario bounds [{num(adr3,'adr_usd_central_lo'):.2f},{num(adr3,'adr_usd_central_hi'):.2f}]", "score": "Report point error and whether printed interval overlaps scenario band; band is RSS sensitivity, not a coverage-calibrated prediction interval. Preserve separate reported-dollar and integer-fair ex-FX target scores.", "source": "Q3 letter ADR and FX/ex-FX disclosures; committed ADRv3 P card and S harness", "rounding": "ADR printed to cents +/-0.005 USD; whole-point ex-FX +/-0.5pp; respect explicit <1% intervals", "status": "UNSIGNED; ADR history n=10/9 differs from main W1/W2"},
        {"id": "L4-C06", "metric": "2026Q4 nights guidance", "unit": "Exact quoted words; % only if disclosed", "definition": "Management's prospective Q4 nights growth language, with full context", "reference": "Record whether explicitly low double digit or stronger; do not translate a model's 10% into management words", "score": "Human classify exact quote as at_least_low / below_low / ambiguous; omitted=ABSENT. Quantified statement preserved as interval with stated precision.", "source": "Q3 letter/earnings remarks; exact document/page/time", "rounding": "No invented numerical mapping for high single digit/low double digit", "status": "UNSIGNED input to proposed F conjunction"},
        {"id": "L4-C07", "metric": "Q3 UF growth less Q3 GBV growth", "unit": "percentage points YoY", "definition": "100*(UF26Q3/UF25Q3-1) - 100*(GBV26Q3/GBV25Q3-1)", "reference": "Proposed F gap strictly above -8pp", "score": "Form ratio extrema for each growth series then difference extrema. Criterion holds only if entire gap interval >-8pp; crossing or equality=inconclusive; missing=ABSENT.", "source": "Q3 2026/2025 comparative 10-Q UF balances and letter GBV", "rounding": "All four observations have their disclosed precision; use low current/high prior for growth minimum", "status": "Cleaner payment-timing diagnostic; not an identified RNPL exposure share"},
        {"id": "L4-C08", "metric": "Q3 funds payable growth", "unit": "% YoY", "definition": "100*(FP26Q3/FP25Q3-1); compare documented prior base 7209 USDm", "reference": "Neutral descriptive band [5,11]%", "score": "Wholly inside=INSIDE; wholly below/above=BELOW/ABOVE; boundary crossing=AMBIGUOUS. Require translation/noncash reconciliation before any interpretation.", "source": "Comparative 10-Q funds payable and cash-flow/accounting notes", "rounding": "Whole USDm balances +/-0.5 on numerator and denominator", "status": "UNSIGNED; inside band does not mean deferral on schedule"},
        {"id": "L4-C09", "metric": "Stated revenue FX and cohort FX", "unit": "pp YoY; USDm; dimensionless multiplier separately", "definition": "Management's stated after-hedge revenue FX contribution versus L3 currency-timing output when accepted", "reference": "L3 cohort recognition FX pending; no central value assigned", "score": "Record stated integer contribution as interval and hedge wording separately. No score against absent L3 estimate. Do not add full FX factor to USD-GBV revenue; do not equate contribution change with level multiplier.", "source": "Q3 letter/10-Q FX and hedging disclosures; future versioned L3 adapter", "rounding": "Whole percentage contribution +/-0.5pp; no fabricated precision", "status": "PENDING INTEGRATION; baseline pending is not zero"},
        {"id": "L4-C10", "metric": "Product-bundle contribution and cancellation language", "unit": "Exact words; pp if disclosed", "definition": "Record bundle scope (RNPL, cancellation redesign, price display/fees) and any quantified nights/GBV/ADR contribution", "reference": "No bundle component assumed to equal RNPL alone", "score": "Save exact statement with period/denominator. Omitted amount=ABSENT, not zero; a quantified bundle is not feature-specific causation.", "source": "Q3 letter/earnings remarks; exact quotation and publication stamp", "rounding": "Stated numerical precision; preserve more than/approximately language", "status": "UNSIGNED descriptive evidence"},
        {"id": "L4-C11", "metric": "F combined proposed refutation condition", "unit": "Three observable conditions", "definition": "ALL: lambda interval >=17.09%; UF-minus-GBV growth interval strictly >-8pp; explicit Q4 nights wording low double digit or stronger", "reference": "ALPHA_F_RNPL.md single D-10 option; not adopted", "score": "All true=PROPOSED REFUTATION CONDITION MET; any missing=ABSENT; otherwise INCONCLUSIVE. Does not validate the opposite thesis, identify a causal RNPL effect or authorize a trade.", "source": "C01/C06/C07 with primary publication fields", "rounding": "Inherit each input's conservative interval and exact quote review", "status": "UNSIGNED proposed thesis-condition only"},
    ]
    for row in rows:
        row.update({"observed_value": None, "outcome": "NOT YET SCORED", "publication_path": None,
                    "page_or_table": None, "retrieved_at_utc": None, "restatement_version": None,
                    "conversion_status": "Fixed 2/3 K0 benchmark provisional pending accepted L3 conversion validation"})
    write_csv(destination / "unsigned_card.csv", rows)
    (destination / "unsigned_card.json").write_text(json.dumps({"adoption": "UNSIGNED", "event": "2026-11-05 (project calendar; verify issuer schedule before use)", "score_date": "2026-11-06 after complete publications", "rules": rows}, indent=2), encoding="utf-8")
    content = "# ABNB | Unsigned November review card\n\nStatus: Review-ready, not signed. Direction, target, probabilities and formal adoption remain open. No score is a trading instruction. All conversion-dependent forecasts use the fixed 2/3 K0 BENCHMARK and are provisional pending L3 conversion validation. L3 FX/RNPL integration is a separate pending input. The fixed historical card denominator/thresholds do not silently change with a future conversion fit.\n\n"
    content += f"Fixed conversion denominator: {base:.12f} USDm. Warning {warning:.2f}% corresponds to {base*warning/100:.9f} USDm; escalation {escalation:.2f}% to {base*escalation/100:.9f} USDm. These exact percentage cutoffs control.\n\n"
    content += "Capture protocol: record each primary file/URL, page/table, published units, precision, information timestamp, extraction timestamp and restatement version. Never fill missing evidence with zero. November 5 is the inherited project event date; verify the issuer calendar before use. Score on November 6 once the letter and 10-Q are available. Freeze any pre-letter consensus benchmark separately before release; keep the September snapshot as a historical review comparator.\n\n"
    for row in rows:
        content += f"## {row['id']} - {row['metric']}\n\n"
        for label, key in [("Units", "unit"), ("Definition", "definition"), ("Reference", "reference"), ("Rule", "score"), ("Source", "source"), ("Precision", "rounding"), ("Standing", "status")]:
            content += f"**{label}:** {row[key]}\n\n"
    content += "## Additional diagnostic limits\n\nThe corrected excess-unpaid history is 1.969114 / 8.047784 / 9.705899pp (Q4 2025 / Q1 2026 / Q2 2026), rounded 2.0 / 8.0 / 9.7. These are retrospective frozen-stock estimates, not prospective scoreable release items or measured RNPL cohort shares. A future reconstruction requires a new version using frozen K1 coefficients and documented allocations; the press release and 10-Q alone cannot supply that model stock.\n\nScoring implementation: `analysis/src/forecast_methods/lane4_review_v1/scoring.py`; full source hashes are in the accompanying input manifest. There are zero newly fitted parameters.\n"
    (destination / "unsigned_november_card.md").write_text(content, encoding="utf-8")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revenue-dir", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--run-id", default=datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ"))
    parser.add_argument("--render-source", type=Path)
    args = parser.parse_args()
    if Path(args.run_id).name != args.run_id:
        raise ValueError("run-id must be a single directory name")
    run = OUT / args.run_id
    deck = DECK / args.run_id
    run.mkdir(parents=True, exist_ok=False)
    deck.mkdir(parents=True, exist_ok=False)
    manifest = []
    revenue_names = ["forecast.csv", "operating_inputs.csv", "cohort_weights.csv", "guide_reconciliation.csv", "issued_guide_comparison.csv",
                     "cushion_inputs.csv", "consensus_comparison.csv", "sensitivity.csv", "fee_mechanics_comparison.csv", "integration_status.json"]
    model_names = ["scenario_summary.csv", "annual.csv", "valuation.csv", "legacy_replication.json", "model_input.json", "input_manifest.json"]
    snapshot(args.revenue_dir.resolve(), run / "inputs/revenue", revenue_names, manifest)
    snapshot(args.model_dir.resolve(), run / "inputs/model", model_names, manifest)
    source_copies(run / "inputs/evidence", manifest)
    for path in sorted(Path(__file__).parent.glob("*.py")):
        manifest.append({"source": str(path.relative_to(ROOT)), "sha256": digest(path), "evidence_status": "review builder source"})
    (run / "input_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    forecast = read_csv(run / "inputs/revenue/forecast.csv")
    model = read_csv(run / "inputs/model/scenario_summary.csv")
    adr = read_csv(run / "inputs/evidence/adr.csv")
    rule = json.loads((run / "inputs/evidence/lambda_rule.json").read_text())
    build_card(forecast, adr, rule, deck)
    build_review(run, deck, forecast, model, adr, rule)
    if args.render_source:
        shutil.copyfile(args.render_source, deck / "review_memo.md")
    receipt = render(deck / "review_memo.md", deck / "review_memo.pdf")
    receipt.update({"run_id": args.run_id, "created_at_utc": datetime.now(timezone.utc).isoformat(),
                    "adoption": "UNSIGNED", "l3_integration": "PENDING - not estimated zero",
                    "conversion_status": "Fixed 2/3 K0 benchmark; provisional pending accepted L3 conversion validation",
                    "upstream_snapshot_hashes": {m["source"]: m["sha256"] for m in manifest},
                    "outputs": {p.name: digest(p) for p in deck.iterdir() if p.is_file()}})
    (run / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps({"run": str(run), "deck": str(deck), "pages": 2, "visual_inspection": "required"}, indent=2))


# build_review is defined below to keep the independent card logic readable.


def build_review(run, deck, forecast, model, adr, rule):
    revdir = run / "inputs/revenue"
    operating = read_csv(revdir / "operating_inputs.csv")
    cohorts = read_csv(revdir / "cohort_weights.csv")
    reconciliation = read_csv(revdir / "guide_reconciliation.csv")
    sensitivity = read_csv(revdir / "sensitivity.csv")
    issued = read_csv(revdir / "issued_guide_comparison.csv")
    comparisons = read_csv(revdir / "consensus_comparison.csv")
    annual = read_csv(run / "inputs/model/annual.csv")
    legacy = one(read_csv(run / "inputs/evidence/legacy_valuation.csv"), scenario="Base")
    integration = json.loads((revdir / "integration_status.json").read_text())
    if integration.get("accepted_l3_inputs") != 0 or integration.get("incremental_fx_musd") is not None:
        raise ValueError("This review template is for the pending-L3 baseline; version it before consuming L3")
    f = {(r["scenario"], r["quarter"]): r for r in forecast}
    m = {r["scenario"]: r for r in model}
    if len(f) != len(forecast) or len(m) != len(model):
        raise ValueError("Duplicate scenario/quarter keys")
    ref4, ref3, ref1 = (f[("review_with_k", q)] for q in ["2026Q4", "2026Q3", "2027Q1"])
    op3 = one(operating, scenario="review_with_k", quarter="2026Q3")
    op4 = one(operating, scenario="review_with_k", quarter="2026Q4")
    refmodel = m["review_with_k"]
    refannual = one(annual, scenario="review_with_k", year="2027")
    for row in annual:
        validate_financial_row(row)
    for row in model:
        validate_valuation_row(row)
    if any("benchmark" not in r.get("conversion_status", "").lower() or "pending" not in r.get("conversion_status", "").lower() for r in forecast):
        raise ValueError("Every forecast must preserve provisional conversion benchmark status")
    for scenario, mr in m.items():
        if scenario in {x["scenario"] for x in forecast}:
            expected = num(f[(scenario, "2026Q4")], "guide_musd")
            if abs(num(mr, "q4_guide_musd") - expected) > 0.001:
                raise ValueError(f"Model/revenue Q4 guide mismatch: {scenario}")

    # Current panel selection preserves vendor timestamp and avoids counting relays
    # as additional independent panels. No September row enters a historical test.
    panel_rows = [r for r in comparisons if r["scenario"] == "review_with_k" and r["quarter"] == "2026Q4"]
    def latest_panel(part):
        selected = [r for r in panel_rows if part.lower() in r["consensus_vendor"].lower()]
        if not selected:
            raise ValueError(f"Missing {part} consensus")
        def stamp(r):
            dt = datetime.fromisoformat(r["consensus_as_of_timestamp"].replace("Z", "+00:00"))
            return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt.astimezone(timezone.utc)
        return sorted(selected, key=stamp)[-1]
    lseg, sp, zacks = [latest_panel(s) for s in ["Yahoo", "S&P", "Zacks"]]
    panels = [lseg, sp, zacks]
    q4cush = {r["assumption"]: r for r in sensitivity if r["quarter"] == "2026Q4" and r["scenario"] == "review_with_k" and r["driver"] == "cushion"}
    labels = {"review_with_k": "ADR v3 with-K / review", "review_without_k": "ADR v3 without-K", "nights_case_a": "Q4 nights case A", "adr_mean_reversion": "ADR residual reversion", "k0_conditional": "K0 conditional ledger"}

    # An explicit ledger supplies all quantitative table cells and their units.
    ledger = []
    for r in forecast:
        for field, unit in [("revenue_musd", "USD millions"), ("guide_musd", "USD millions"), ("lambda_pct", "%"), ("cushion_decimal", "decimal")]:
            ledger.append({"id": f"R:{r['scenario']}:{r['quarter']}:{field}", "metric": field,
                           "scenario": r["scenario"], "period": r["quarter"], "value": num(r, field), "units": unit,
                           "as_of": r["information_date"], "status": "calculated", "evidence_status": "conditional benchmark review; conversion and FX/RNPL pending",
                           "source": str(revdir / "forecast.csv"), "definition": "Kernel/guide calculation; pending L3 adjustment is not zero"})
    for r in model:
        for field in ["fy26_revenue_musd", "fy27_revenue_musd", "fy27_ebitda_musd", "fy27_net_income_musd", "fy27_fcf_musd", "fy27_net_cash_musd", "fy27_shares_m", "exit_multiple", "enterprise_value_musd", "equity_value_musd", "value_per_share", "six_lens_mean"]:
            ledger.append({"id": f"M:{r['scenario']}:{field}", "metric": field, "scenario": r["scenario"], "period": "FY2027" if not field.startswith("fy26") else "FY2026", "value": num(r, field),
                           "units": "USD/share" if field in ["value_per_share", "six_lens_mean"] else ("million shares" if field.endswith("shares_m") else ("EV/adjusted EBITDA turns" if field == "exit_multiple" else "USD millions")),
                           "as_of": integration["as_of"], "status": "estimated", "evidence_status": "inherited model assumptions; fixed2/3 benchmark provisional", "source": str(run / "inputs/model/scenario_summary.csv"), "definition": "FY27-end cash/shares; no adopted target"})
    for row in operating:
        for field, unit in [("nights_m", "million nights"), ("adr_usd", "USD/night"), ("gbv_musd", "USD millions"), ("embedded_adr_fx_pp", "ADR YoY percentage points"), ("k_line_pp", "ADR YoY percentage points")]:
            if row.get(field) in ("", None):
                continue
            ledger.append({"id": f"O:{row['scenario']}:{row['quarter']}:{field}", "metric": field, "scenario": row["scenario"], "period": row["quarter"], "value": num(row, field), "units": unit,
                           "as_of": row["information_date"], "status": "observed" if row.get("kind") == "reported" else "estimated", "source": str(revdir / "operating_inputs.csv"), "definition": row.get("description", ""), "evidence_status": row.get("evidence_status", "")})
    for row in cohorts:
        ledger.append({"id": f"W:{row['scenario']}:{row['target_quarter']}:{row['booking_quarter']}", "metric": "USD baseline cohort contribution weight", "scenario": row["scenario"], "period": row["target_quarter"], "value": num(row,"usd_baseline_contribution_weight"), "units": "decimal share", "as_of": row["information_date"], "status": "calculated", "source": str(revdir / "cohort_weights.csv"), "definition": "booking quarter " + row["booking_quarter"] + "; weighted USD GBV / total weighted USD GBV", "evidence_status": "Not a measured recognition probability or constant-FX currency exposure"})
    for row in reconciliation:
        ledger.append({"id": "BRIDGE:"+row["step"], "metric": row["change"], "scenario": "H2-v3 to K0 reconciliation", "period": "2026Q4", "value": num(row,"delta_musd"), "units": "guide USD millions", "as_of": integration["as_of"], "status": "calculated", "source": str(revdir / "guide_reconciliation.csv"), "definition": "Deterministic sequential attribution; order preserved"})
    for row in issued:
        ledger.append({"id": "ISSUED:"+row["method"], "metric": "Already-issued guide to Q3 revenue", "scenario": row["method"], "period": row["quarter"], "value": num(row,"revenue_musd"), "units": "USD millions", "as_of": row["guide_information_date"], "status": "calculated", "source": str(revdir / "issued_guide_comparison.csv"), "definition": "Issued midpoint times (1 + named cushion); original D-01 comparator"})
    for row in annual:
        for field in ["adj_ebitda", "interest_income", "interest_expense", "cash_taxes", "d_unearned", "wc_resid", "capex", "fcf", "sbc", "sbc_adj_fcf"]:
            ledger.append({"id": f"CF:{row['scenario']}:{row['year']}:{field}", "metric": field, "scenario": row["scenario"], "period": "FY"+row["year"], "value": num(row,field), "units": "USD millions", "as_of": integration["as_of"], "status": "estimated", "source": str(run / "inputs/model/annual.csv"), "definition": "Inherited cost/cash-flow assumptions with linked benchmark revenue"})
    for i, r in enumerate(panels):
        ledger.append({"id": f"C{i+1}", "metric": "Q4 revenue consensus", "scenario": "vendor panel", "period": "2026Q4", "value": num(r, "consensus_musd"), "units": "USD millions", "as_of": r["consensus_as_of_timestamp"], "status": "consensus", "source": r["consensus_source_path"], "definition": r["consensus_vendor"], "url": r["consensus_url"], "register_id": r["consensus_register_id"]})
    write_csv(deck / "source_assumption_ledger.csv", ledger)

    # Quantified choices preserve comparisons without assigning team decisions.
    decisions = []
    def decision(ident, choice, value, units, effect, source, prerequisite):
        decisions.append({"id": "L4-" + ident, "choice": choice, "value": value, "units": units, "effect_vs_review_reference": effect,
                          "source": source, "adoption": "OPEN - unsigned", "required_before_adoption": prerequisite,
                          "conversion_status": "fixed2/3 K0 benchmark provisional pending L3 conversion", "original_decision_reference": "D-01" if ident == "D09" else "No original decision ID reassigned"})
    for sc in ["review_with_k", "k0_conditional", "review_without_k", "adr_mean_reversion", "nights_case_a"]:
        fr = f[(sc, "2026Q4")]
        mr = m[sc]
        decision("D01" if sc in ["review_with_k", "k0_conditional"] else "D02", labels[sc], num(fr, "guide_musd"), "Q4 guide USDm",
                 f"Q4 guide delta {num(fr,'guide_musd')-num(ref4,'guide_musd'):+.6f}; Q1 guide {num(f[(sc,'2027Q1')],'guide_musd'):.6f}; FY27 value/share {num(mr,'value_per_share'):.6f} ({num(mr,'value_per_share')-num(refmodel,'value_per_share'):+.6f})",
                 "L4 revenue forecast.csv / model scenario_summary.csv", "Choose operating baseline and recognize K mechanics and residual are assumptions")
    for key, row in q4cush.items():
        decision("D03", key, num(row, "value")*100, "cushion %", f"Q4 guide {num(row,'guide_musd'):.6f}; delta {num(row,'guide_musd')-num(ref4,'guide_musd'):+.6f} USDm; revenue/valuation unchanged", "L4 sensitivity.csv", "Choose estimator on evidence; zero is a mechanical boundary, not a forecast")
    for row in panels:
        decision("D04", row["consensus_vendor"], num(row, "consensus_musd"), "Q4 consensus USDm", f"Review guide gap {num(ref4,'guide_musd')-num(row,'consensus_musd'):+.6f} USDm ({100*(num(ref4,'guide_musd')/num(row,'consensus_musd')-1):+.6f}%)", row["consensus_register_id"]+" / "+row["consensus_as_of_timestamp"], "Keep independent panels separate; restamp pre-letter before November scoring")
    for sc in ["review_with_k_fx_down_sensitivity", "review_with_k_fx_up_sensitivity"]:
        row = m[sc]
        decision("D05", sc, num(row, "value_per_share"), "FY27-end USD/share", f"Q4 guide {num(row,'q4_guide_musd'):.6f}; FY27 revenue {num(row,'fy27_revenue_musd'):.6f}; value delta {num(row,'value_per_share')-num(refmodel,'value_per_share'):+.6f}", "L4 model scenario_summary.csv", "Generic +/-1% applied to Q3/Q4 2026 and Q1 2027; FY27 Q3/Q4 inherit growth on altered 2026 base, Q2 unchanged; not an FX estimate; accept explicit versioned L3 inputs before actual FX application")
    decision("D05", "L3 cohort FX/RNPL central integration", None, "USDm / level multiplier / YoY pp separately", "Unavailable: no central estimate; not represented as zero", "L4 integration_status.json", "Require bundle version/commit, checksums, reference basis, cohort share denominator, timing, treatment and hedge reconciliation")
    for field, name in [("price", "Legacy final-model EBITDA lens"), ("football_mean", "Legacy six-lens mean")]:
        decision("D06", name, num(legacy, field), "USD/share", f"Difference from new reference FY27-end value {num(legacy,field)-num(refmodel,'value_per_share'):+.6f}; distinct horizon/input/method objects", "valuation_v1/football_field_reconciliation.csv", "Choose explicit valuation lens and horizon; do not mechanically average; +0.48 relation excluded")
    price_values = [num(r, "value_per_share") for r in model]
    decision("D07", "Direction, target and scenario probabilities", None, "team adoption", f"Displayed model values span {min(price_values):.6f}-{max(price_values):.6f} USD/share; no expected value or expected return is computed", "L4 model scenario_summary.csv", "Team must choose direction/horizon/target and defensible probabilities; short return additionally needs borrow/dividend/cost inputs")
    decision("D08", "Formal November card adoption", None, "signature", "11 proposed diagnostics; lambda 17.09/16.93%, joint UF-GBV gap strictly >-8pp, exact nights wording; missing/ambiguous distinct", "unsigned_november_card.md", "Team review and signature; no trade authorization follows from diagnostic scores")
    decision("D09", "Original D-01: Q3 fixed2/3 benchmark revenue", num(ref3,"revenue_musd"), "Q3 revenue USDm", "Benchmark comparator; not a new Q3 management guide", "L4 forecast.csv", "Choose already-guided-quarter revenue approach separately from Q4 guide; L3 conversion results pending")
    for row in issued:
        decision("D09", "Original D-01: " + row["method"], num(row,"revenue_musd"), "Q3 revenue USDm", f"Delta vs Q3 benchmark {num(row,'delta_vs_kernel_musd'):+.9f} USDm; issued guide midpoint {num(row,'issued_guide_mid_musd'):.3f} from {row['guide_information_date']}; cushion {num(row,'cushion_decimal')*100:.9f}%", "L4 issued_guide_comparison.csv", "Revenue estimate from an already issued guide; do not treat as a new implied guide or stack on kernel revenue")
    decision("D10", "Conversion methodology: retain current benchmark pending L3", num(ref4,"lambda_pct"), "Q4 benchmark lambda %", f"Fixed first-lag coefficient 2/3; current provisional Q4 guide {num(ref4,'guide_musd'):.9f} USDm; alternative conversion effect unavailable", "L4 forecast.csv; imported K0 v2", "L3 owns estimation/validation. Require explicit accepted version/commit and checksums before changing conversion parameters; distinct from FX/RNPL integration")
    write_csv(deck / "decision_register.csv", decisions)
    decision_md = "# Quantified decision register | Unsigned\n\nAll choices remain open. Values are conditional arithmetic using the fixed 2/3 K0 BENCHMARK, provisional pending L3 conversion validation, separately from pending FX/RNPL integration. Comparisons use the same review reference unless a distinct legacy horizon is explicit. IDs L4-Dxx are new; L4-D09 preserves the original D-01 Q3 revenue decision, without redefining any existing team decision.\n\n"
    decision_md += table(["Decision", "Choice", "Value / unit", "Quantified effect", "Required before adoption"], [[r["id"], r["choice"], ("Unavailable" if r["value"] is None else f"{r['value']:.6f}") + " " + r["units"], r["effect_vs_review_reference"], r["required_before_adoption"]] for r in decisions])
    (deck / "decision_register.md").write_text(decision_md+"\n", encoding="utf-8")

    # Tables and paragraphs below share one editable Markdown source with the PDF.
    guide_rows = []
    for sc in ["review_with_k", "review_without_k", "adr_mean_reversion", "k0_conditional"]:
        fr = f[(sc, "2026Q4")]
        op = one(operating, scenario=sc, quarter="2026Q3")
        guide_rows.append([labels[sc], f"{num(op,'gbv_musd')/1000:.3f}", f"{num(fr,'revenue_musd'):,.1f}", f"{num(fr,'guide_musd'):,.1f}", f"{num(fr,'guide_musd')-num(lseg,'consensus_musd'):+.1f}"])
    for key, label in [("trailing8_mean", "Review / mean cushion"), ("legacy_q4_cushion", "Review / legacy cushion")]:
        row = q4cush[key]
        guide_rows.append([label, f"{num(op3,'gbv_musd')/1000:.3f}", f"{num(row,'revenue_musd'):,.1f}", f"{num(row,'guide_musd'):,.1f}", f"{num(row,'guide_musd')-num(lseg,'consensus_musd'):+.1f}"])
    guide_table = table(["Conditional case", "Q3 GBV $bn", "Q4 revenue $m", "Q4 guide $m", "Gap to LSEG $m"], guide_rows)
    value_rows = []
    for sc, label in [("review_with_k", "Operating review"), ("k0_conditional", "K0 conditional ledger"), ("review_with_k_fx_down_sensitivity", "-1% revenue sensitivity"), ("review_with_k_fx_up_sensitivity", "+1% revenue sensitivity")]:
        row = m[sc]
        value_rows.append([label, f"{num(row,'fy27_revenue_musd')/1000:.3f}", f"{num(row,'fy27_ebitda_musd')/1000:.3f}", f"{num(row,'fy27_fcf_musd')/1000:.3f}", f"{num(row,'value_per_share'):.2f}"])
    valuation_table = table(["Conditional case", "FY27 rev $bn", "Adj. EBITDA $bn", "FCF $bn", "Value $/share"], value_rows)
    q4weights = sorted([r for r in cohorts if r["scenario"] == "review_with_k" and r["target_quarter"] == "2026Q4"], key=lambda r:int(r["lag"]))
    if len(q4weights) != 2:
        raise ValueError("Q4 cohort contributions missing")
    if abs(sum(num(r, "usd_baseline_contribution_weight") for r in q4weights)-1) > 1e-8:
        raise ValueError("Q4 contribution weights do not conserve exposure")
    gap = num(ref4,'guide_musd') - num(lseg,'consensus_musd')
    legacy_start, legacy_end = reconciliation[0], reconciliation[-1]
    delta_parts = [num(one(reconciliation, step=str(i)), "delta_musd") for i in [1,2,3]]
    adr3 = one(adr, quarter="3Q26", variant="v3_with_K", fx_estimator="midpoint")
    source_lines = "Sources: [R] L4 revenue snapshot: forecast, operating_inputs, guide_reconciliation, sensitivity and consensus_comparison CSVs; [M] L4 model snapshot: scenario_summary, annual and valuation CSVs. Exact paths, information dates and SHA-256 hashes accompany this memo."
    memo = f"""# Airbnb | Forecast the guide, test the composition

Status: UNSIGNED | ABNB, Nasdaq Class A | USD | As of {integration['as_of']}; operating inputs {ref4['information_date']}, consensus dates below. Fixed 2/3 K0 BENCHMARK; conversion-dependent claims are provisional pending L3 validation. FX/RNPL integration is separately pending. Direction, target and probabilities remain open.

**The benchmark operating review implies a Q4 guide of ${num(ref4,'guide_musd'):,.0f}M**, ${abs(gap):.1f}M ({100*abs(gap)/num(lseg,'consensus_musd'):.2f}%) below captured LSEG-family revenue consensus. The same revenue at the inherited Q4 cushion implies ${num(q4cush['legacy_q4_cushion'],'guide_musd'):,.0f}M. This is conditional arithmetic; it does not establish a trading edge. [R]

## Operating inputs reach revenue with a lag

The review uses {num(op3,'nights_m'):.1f}M Q3 nights x ${num(op3,'adr_usd'):.2f} ADR = ${num(op3,'gbv_musd')/1000:.4f}bn GBV. Revenue = lambda x [(2/3) prior-quarter GBV + (1/3) second-prior GBV]; guide = revenue / (1 + cushion). Imported Q4 lambda is {num(ref4,'lambda_pct'):.5f}% and the trailing-eight median cushion is {num(ref4,'cushion_decimal')*100:.5f}%. Dollar contribution shares are {num(q4weights[0],'usd_baseline_contribution_weight')*100:.2f}% / {num(q4weights[1],'usd_baseline_contribution_weight')*100:.2f}%, not literal 2/3 and 1/3 revenue shares. Q3 nights affect Q4 revenue; Q4 nights first affect Q1 2027. [R]

## Main exhibit | Q4 guide and cushion sensitivity

{guide_table}

Notes: LSEG-family ${num(lseg,'consensus_musd'):,.3f}M, {lseg['consensus_as_of_timestamp']}; S&P ${num(sp,'consensus_musd'):,.0f}M, {sp['consensus_as_of_timestamp']}; Zacks ${num(zacks,'consensus_musd'):,.0f}M, {zacks['consensus_as_of_timestamp']}. Yahoo/Alpha Vantage relays count as one LSEG-family panel. These are revenue consensus comparators, not explicit management-guide consensus. All rows are scenarios, not probability intervals. [R]

The older ${num(legacy_start,'guide_musd'):,.1f}M H2-v3 guide reconciles to K0's ${num(legacy_end,'guide_musd'):,.1f}M: changing Q3 GBV adds ${delta_parts[0]:.2f}M, lambda ${delta_parts[1]:.2f}M, and the cushion ${delta_parts[2]:.2f}M in that order. The review uses its own ADRv3 operating block; numbers were not selected for their sign versus Street. [R]

**FX integration remains unresolved.** USD GBV already contains booking-period FX. L3 must supply verified cohort/currency weights and recognition timing before replacing the relevant FX component once. RNPL remains in total exposure; payment, FX fixing and recognition are distinct dates. No full FX factor or assumed zero hedge line is added. ADRv3's Q3 {num(op3,'embedded_adr_fx_pp'):+.2f}pp / Q4 {num(op4,'embedded_adr_fx_pp'):+.2f}pp ADR FX is already embedded and is not the revenue-FX contribution. [R, F]

{source_lines}

<!-- PAGEBREAK -->

# Valuation is conditional; adoption is open

**The review financial path produces ${num(refmodel,'value_per_share'):.2f}/share at {num(refmodel,'exit_multiple'):.1f}x FY27 adjusted EBITDA.** This uses FY27-end cash and diluted shares, a 31 December 2027 convention; it is not an adopted target. FY27 beyond the kernel-covered quarters inherits the model's growth, cost, cash and share assumptions. The +/-1% rows below test incremental revenue sensitivity; they are not L3 FX estimates or probability bounds. [M]

{valuation_table}

Notes: Illustrative +/-1% net after-hedge consolidated revenue changes apply to Q3/Q4 2026 and Q1 2027. FY27 Q3/Q4 inherit growth on the changed 2026 base; Q2 is unchanged. This is not a measured RNPL/timing coefficient. FCF = adjusted EBITDA + net interest - cash taxes + change in unearned fees + working-capital residual - capex. Review FY27 cash taxes are ${num(refannual,'cash_taxes'):,.1f}M, capex ${num(refannual,'capex'):,.1f}M; FCF after deducting SBC is ${num(refannual,'sbc_adj_fcf'):,.1f}M. Cash-flow assumptions are inherited. [M]

Reference per-share value = ({num(refmodel,'exit_multiple'):.1f} x ${num(refmodel,'fy27_ebitda_musd'):,.1f}M EBITDA + ${num(refmodel,'fy27_net_cash_musd'):,.1f}M net cash) / {num(refmodel,'fy27_shares_m'):.3f}M shares: EV ${num(refmodel,'enterprise_value_musd'):,.1f}M; equity ${num(refmodel,'equity_value_musd'):,.1f}M. Legacy arithmetic reproduces ${num(legacy,'price'):.2f} for its EBITDA lens versus ${num(legacy,'football_mean'):.2f} for its six-lens mean, with an approximate September-2027 label using year-end balances. These are distinct objects. The unvalidated +0.48 growth/multiple relation is excluded. [M, V]

## Opposing evidence limits the conviction

A2 is PARTIAL: at letter-close vintages it matched guide-gap signs in 7/8 W1 and 6/7 W2 strong cases, but executable aligned 20-day excess returns averaged -0.308/-0.983pp; intervals cross zero. B2 FAILS its 70% revision hurdle (5/9 and 4/7); its unseasonal compounded-GBV LIVE values are excluded here. W2 is nested in W1. These findings cannot establish an actionable expectations edge. [E]

ADRv3's residual-carry rule passes its dollar target on n=10/9 windows, distinct from the main n=14/10 harness; its integer-fair ex-FX target does not pass both windows. Selection was post-hoc; the binding without-K jackknife margin is 0.011. Its {num(adr3,'residual_pp')-num(adr3,'k_line_pp'):.2f}pp residual remains unobserved. Reversion gives a ${num(f[('adr_mean_reversion','2026Q4')],'guide_musd'):,.0f}M Q4 guide versus ${num(f[('k0_conditional','2026Q4')],'guide_musd'):,.0f}M for stronger K0 GBV, without assigned probabilities. [A, R]

## What would change the conclusion

At the November print, score conversion using 100 x Q3 revenue / {num(rule,'base_musd'):,.6f}: warn below {num(rule,'warn_below_lambda_pct'):.2f}% and escalate below {num(rule,'escalate_below_lambda_pct'):.2f}%, with whole-million rounding intervals. F's proposed refutation requires all three: lambda wholly at least 17.09%; UF growth less GBV growth wholly above -8pp; and explicit Q4 nights guidance of low double digit or stronger. Missing or crossing evidence remains absent/inconclusive. This is an unsigned condition, not a trade instruction or RNPL causal test. [F]

F's corrected stock history is 2.0/8.0/9.7pp; migration and RNPL revenue-cohort shares remain unidentified. The October 2 submission precedes the project-calendar November 5 catalyst and October 22-24 finals. Accepted L3 conversion and FX/RNPL inputs may change these provisional values. [F, R]

Sources: [A] docs/adrv3/SYNTHESIS.md (11 Sep 2026); [E] LANE2_MEMO_READY_CLAIMS.md (13 Sep); [F] ALPHA_F_RNPL.md and D_CARD_ADDENDUM_LAMBDA.md (13/12 Sep); [V] LANE1_MEMO_READY_CLAIMS_v2.md (13 Sep). [R/M] exact snapshot paths and SHA-256 ledger accompany the editable source. Evidence base: commit 1c87628cedbc94ab8a0e8552743c94485ef353b8. Scenario values carry no expected-return or probability claim.
"""
    (deck / "review_memo.md").write_text(memo, encoding="utf-8")
    (run / "consistency_checks.json").write_text(json.dumps({"model_guide_tieout": "PASS", "valuation_rows_tied": len(model), "cash_flow_rows_tied": len(annual), "cohort_weight_sum": sum(num(r, "usd_baseline_contribution_weight") for r in q4weights), "l3_pending_preserved": True,
                     "reference_q4_guide_musd": num(ref4,"guide_musd"), "reference_value_per_share": num(refmodel,"value_per_share"), "decision_rows": len(decisions), "card_rows": 11}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
