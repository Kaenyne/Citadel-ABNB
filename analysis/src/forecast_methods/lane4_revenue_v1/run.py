"""Rebuild L4 reconciliation to a NEW output directory; never register forecasts."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import pandas as pd

from adapter import dated, forecast, quarter, shift
from kernel_engine_v2 import engine as k0
from l3_contract import apply_row, load_bundle

ROOT = Path(__file__).resolve().parents[4]
DEFAULT_OUTPUT = ROOT / "data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1"
CARD = "data/processed/adrv3/P/adr_card_v3.csv"
TERMS = "data/processed/adrv3/P/P1_card_v3_terms.csv"
KPI = "data/processed/overnight/02_kpi_panel_quarterly.csv"
CALENDAR = "data/processed/forecast_methods/harness/calendar.csv"
H2 = "data/processed/h2_bridge_v3/h2_bridge_revenue_dollars.csv"
K0_SNAPSHOT = "data/processed/forecast_methods/kernel_engine_v2/term_structure_2026-09-12.csv"
REGISTRY = "data/processed/forecast_methods/L0/L0_vintage_register.csv"
CONVERSION_STATUS = "fixed_K0_2over3_benchmark_provisional_pending_L3_conversion_validation"


def canon(q):
    return q if len(q) == 6 else f"20{q[-2:]}Q{q[0]}"


def load_inputs(as_of):
    calendar = pd.read_csv(ROOT / CALENDAR).set_index("fiscal_quarter")
    panel = pd.read_csv(ROOT / KPI, usecols=["quarter", "gbv_musd", "revenue_musd", "nights_m", "adr_usd"])
    panel["quarter"] = panel.quarter.map(canon)
    panel["information_date"] = panel.quarter.map(calendar.print_date)
    panel = panel[panel.information_date < as_of]
    # Printed USD GBV intentionally remains the published figure; disclosed rounded
    # ADR/nights cannot be forced to reproduce it without changing reported data.
    reported = [dict(quarter=r.quarter, gbv_musd=float(r.gbv_musd), kind="reported",
                     information_date=r.information_date, source_ref=KPI)
                for r in panel.itertuples()]
    card = pd.read_csv(ROOT / CARD)
    card = card[card.fx_estimator == "midpoint"].copy()
    card["quarter"] = card.quarter.map(canon)
    return panel, reported, card


def build_operating(card):
    rows = []
    definitions = {
        "review_with_k": ("v3_with_K", "case_B", "Team Q3 nights; ADRv3 Q4 case B; published dollar ADR with imposed K mechanics"),
        "review_without_k": ("v3_without_K", "case_B", "Same nights; ADRv3 without-K replaces with-K ADR once"),
        "nights_case_a": ("v3_with_K", "case_A", "Q4 case A team 132.7m replaces case B 131.8m; Q3 unchanged"),
        "adr_mean_reversion": ("v3_with_K", "case_B", "Residual 2.398pp replaces last_q 4.849326pp; K and other components retained"),
    }
    term = pd.read_csv(ROOT / TERMS)
    residual = term[(term.quarter == "3Q26") & (term.variant == "v3_with_K") & (term.term == "like_for_like_pricing_residual")].iloc[0]
    for scenario, (variant, case, description) in definitions.items():
        for q in ["2026Q3", "2026Q4"]:
            subset = card[(card.quarter == q) & (card.variant == variant)]
            if q == "2026Q4":
                subset = subset[subset.nights_case.str.contains(case)]
            if len(subset) != 1:
                raise ValueError(f"Ambiguous operating input: {scenario}/{q}")
            c = subset.iloc[0]
            adr = float(c.adr_usd_point)
            if scenario == "adr_mean_reversion":
                adr += float(c.base_adr_usd) * (float(residual.lo_pp) - float(residual.point_pp)) / 100
            rows.append(dict(scenario=scenario, quarter=q, nights_m=float(c.nights_m), adr_usd=adr,
                             gbv_musd=float(c.nights_m) * adr, kind="forecast", information_date="2026-09-11",
                             source_ref=CARD + ";" + TERMS, description=description,
                             adr_variant=variant, adr_fx_estimator="midpoint already embedded",
                             embedded_adr_fx_pp=float(c.fx_effect_pp), k_line_pp=float(c.k_line_pp),
                             nights_basis=c.nights_case, evidence_status="conditional_review_not_adopted",
                             precision_basis="published card USD ADR to cents and nights to 0.1m; multiplication not rounded"))
    return rows, definitions


def reconcile(h2, old_k0, latest_k0, reported):
    h = h2[h2.quarter == "4Q26"].iloc[0]
    k = old_k0[old_k0.quarter == "2026Q4"].iloc[0]
    latest = latest_k0[latest_k0.quarter == "2026Q4"].iloc[0]
    prior_gbv = next(r["gbv_musd"] for r in reported if r["quarter"] == "2026Q2")
    k_gbv = (k.base_musd - prior_gbv / 3) * 1.5
    state = dict(gbv_musd=h.gbv_3q26_assumed_busd * 1000,
                 lambda_pct=h.conversion_mean * 100, cushion_decimal=h.hist_actual_vs_guide_mid_pct / 100)
    def value():
        return (2 / 3 * state["gbv_musd"] + prior_gbv / 3) * state["lambda_pct"] / 100 / (1 + state["cushion_decimal"])
    rows = []
    previous = value()
    rows.append(dict(step=0, change="H2 v3 original", guide_musd=previous, delta_musd=0, **state))
    changes = [("Q3 GBV: rate-compounded operating bridge to K0 ledger scenario", "gbv_musd", k_gbv),
               ("Lambda: 2023-25 same-season mean to K0 EWM selection", "lambda_pct", k.lambda_pct),
               ("Cushion: historical Q4 3.88% to trailing-8 median", "cushion_decimal", k.point / k.guide_mid_musd - 1)]
    for i, (label, field, val) in enumerate(changes, 1):
        state[field] = float(val)
        v = value()
        rows.append(dict(step=i, change=label, guide_musd=v, delta_musd=v-previous, **state))
        previous = v
    rows.append(dict(step=4, change="Explicit additional fee/FX/cancellation overlays: absent on both dollar paths", guide_musd=previous, delta_musd=0, **state))
    rows.append(dict(step=5, change="Information date roll 2026-09-12 to 2026-09-13: no new KPI print", guide_musd=float(latest.guide_mid_musd), delta_musd=float(latest.guide_mid_musd)-previous, **state))
    residual = value() - float(k.guide_mid_musd)
    if abs(residual) >= .001 or abs(rows[0]["guide_musd"] - h.implied_guide_mid_if_cushion_holds) >= .001:
        raise AssertionError("Reconciliation fails $0.001M acceptance")
    return rows, residual


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", default="2026-09-13")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--l3-manifest", type=Path)
    args = parser.parse_args()
    started = time.perf_counter()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit(f"Refusing existing output directory: {output}; choose new --output")
    dated("2026-09-13", args.as_of)
    output.mkdir(parents=True)
    try:
        panel, reported, card = load_inputs(args.as_of)
        operating, definitions = build_operating(card)
        lambdas = {s: k0.pit_lambda(s, args.as_of) for s in [1, 3, 4]}
        guide_info = {stat: k0.kernel_guide("2026Q3", args.as_of, cushion=stat) for stat in ["median", "mean"]}
        cushion = guide_info["median"]["cushion"]
        term = k0.term_structure(args.as_of)
        k0_gbv = {}
        printed_gbv = {r["quarter"]: r["gbv_musd"] for r in reported}
        for target in ["2026Q4", "2027Q1"]:
            row = term[term.quarter == target].iloc[0]
            lag1, lag2 = shift(target, -1), shift(target, -2)
            second = k0_gbv.get(lag2, printed_gbv.get(lag2))
            k0_gbv[lag1] = (float(row.base_musd) - second / 3) * 1.5
        for q, gbv in k0_gbv.items():
            operating.append(dict(scenario="k0_conditional", quarter=q, nights_m=None, adr_usd=None,
                                  gbv_musd=gbv, kind="forecast", information_date="2026-09-12",
                                  source_ref="analysis/src/forecast_methods/kernel_engine_v2/engine.py::term_structure",
                                  description="Existing K0 ledger GBV with undisclosed RNPL ramp; second missing quarter persists GBV growth; not a measured RNPL input",
                                  adr_variant="not decomposed", adr_fx_estimator="USD GBV embeds booking FX",
                                  embedded_adr_fx_pp=None, k_line_pp=None, nights_basis="not separately identified",
                                  evidence_status="conditional_comparison_not_headline", precision_basis="K0 public term structure full precision"))
        forecasts, weights = [], []
        scenario_labels = dict((k, v[2]) for k, v in definitions.items())
        scenario_labels["k0_conditional"] = "Inherited K0 ledger scenario and growth persistence; no validated conditional forecast coverage"
        for scenario, description in scenario_labels.items():
            explicit = [r for r in operating if r["scenario"] == scenario]
            for q in ["2026Q3", "2026Q4", "2027Q1"]:
                row, parts = forecast(q, args.as_of, reported + explicit, cushion, lambdas[int(q[-1])])
                row.update(scenario=scenario, scenario_description=description,
                           conversion_status=CONVERSION_STATUS, method_available_date="2026-09-13",
                           cushion_n_train=guide_info["median"]["cushion_n"], cushion_information_date=guide_info["median"]["knowable_from"],
                           n_new_fitted_parameters=0, parameter_definition="K0 inherited seasonal EWM lambda; fixed 2/3 lag; trailing8 median cushion; explicit operating assumptions",
                           evidence_status="conditional_review_not_adopted", source_ref="K0 v2 public lambda + explicit GBV; see source ledger",
                           fx_integration_status="pending_explicit_L3_bundle", incremental_fx_musd=None,
                           scope="consolidated reported revenue; historical lambda embeds FX/fees/cancellations and hedges",
                           hedge_treatment="baseline includes historical reported accounting; incremental hedge dollars unavailable",
                           n_replay_W1=0, n_replay_W2=0)
                row["guide_status"] = "diagnostic_already_issued_guide" if q == "2026Q3" else "future_guide_conditional_scenario"
                forecasts.append(row)
                weights.extend(dict(p, scenario=scenario, conversion_status=CONVERSION_STATUS) for p in parts)
        if args.l3_manifest:
            manifest, adapter_rows = load_bundle(args.l3_manifest, args.as_of)
            seen = set()
            for l3 in adapter_rows:
                key = (l3["scenario"], l3["quarter"])
                if key in seen or any((r["scenario"], r["quarter"]) == key for r in forecasts):
                    raise ValueError("Duplicate L3 scenario/quarter")
                seen.add(key)
                matches = [r for r in forecasts if r["scenario"] == l3["baseline_scenario"] and r["quarter"] == l3["quarter"]]
                if len(matches) != 1:
                    raise ValueError("Missing/ambiguous L3 baseline")
                baseline = dict(matches[0], cohort_gbv_musd={p["booking_quarter"]: p["gbv_musd"] for p in weights if p["scenario"] == l3["baseline_scenario"] and p["target_quarter"] == l3["quarter"]})
                applied = apply_row(baseline, l3, args.as_of)
                applied.pop("cohort_gbv_musd")
                applied.update(l3_bundle_version=manifest["bundle_version"], l3_commit=manifest["commit"])
                forecasts.append(applied)
        else:
            manifest = None
        h2, old_k0 = pd.read_csv(ROOT / H2), pd.read_csv(ROOT / K0_SNAPSHOT)
        reconciliation, residual = reconcile(h2, old_k0, term, reported)
        # The latest unprinted target is not in the realized-cushion history;
        # retrieve its issued range from the frozen calendar instead.
        calendar = pd.read_csv(ROOT / CALENDAR)
        issued = calendar[calendar.next_quarter_guided == "2026Q3"]
        if len(issued) != 1:
            raise ValueError("Missing/ambiguous issued Q3 guide")
        issued = issued.iloc[0]
        dated(issued.guide_date, args.as_of)
        q3_ref = next(r for r in forecasts if r["scenario"] == "review_with_k" and r["quarter"] == "2026Q3")
        issued_comparison = [dict(quarter="2026Q3", method="issued_guide_times_"+stat,
                                  issued_guide_low_musd=issued.guide_lo, issued_guide_high_musd=issued.guide_hi,
                                  issued_guide_mid_musd=issued.guide_mid, guide_information_date=issued.guide_date,
                                  cushion_decimal=g["cushion"], cushion_n=g["cushion_n"],
                                  revenue_musd=issued.guide_mid*(1+g["cushion"]),
                                  delta_vs_kernel_musd=issued.guide_mid*(1+g["cushion"])-q3_ref["revenue_musd"],
                                  source_ref=CALENDAR+";K0 public kernel_guide cushion",
                                  evidence_status="once_guided_baseline_comparison; decision_not_adopted") for stat,g in guide_info.items()]
        pd.DataFrame(issued_comparison).to_csv(output / "issued_guide_comparison.csv", index=False)
        sensitivity = []
        for r in forecasts:
            if r["scenario"] != "review_with_k":
                continue
            for label, c in [("trailing8_median", cushion), ("trailing8_mean", guide_info["mean"]["cushion"]), ("legacy_q4_cushion", .0388), ("zero_cushion_mechanical_boundary", 0.0)]:
                if label == "legacy_q4_cushion" and r["quarter"] != "2026Q4":
                    continue
                sensitivity.append(dict(quarter=r["quarter"], scenario="review_with_k", driver="cushion", assumption=label, value=c,
                                        units="decimal", revenue_musd=r["revenue_musd"], guide_musd=r["revenue_musd"]/(1+c),
                                        delta_guide_musd=r["revenue_musd"]/(1+c)-r["guide_musd"], evidence_status="deterministic_sensitivity_no_probabilities"))
            for cohort in ["2026Q3", "2026Q4"]:
                for driver in ["nights", "adr"]:
                    for direction in [-1, 1]:
                        explicit = [dict(p) for p in operating if p["scenario"] == "review_with_k"]
                        for p in explicit:
                            if p["quarter"] == cohort:
                                p["nights_m" if driver == "nights" else "adr_usd"] *= 1 + direction / 100
                                p["gbv_musd"] = p["nights_m"] * p["adr_usd"]
                        f, _ = forecast(r["quarter"], args.as_of, reported + explicit, cushion, lambdas[int(r["quarter"][-1])])
                        sensitivity.append(dict(quarter=r["quarter"], scenario="review_with_k", driver=f"{cohort}_{driver}", assumption="relative level change", value=direction, units="percent",
                                                revenue_musd=f["revenue_musd"], guide_musd=f["guide_musd"], delta_guide_musd=f["guide_musd"]-r["guide_musd"],
                                                evidence_status="deterministic_sensitivity_no_probabilities"))
        registry = pd.read_csv(ROOT / REGISTRY, comment="#")
        consensus = registry[(registry.period == "2026Q4") & (registry.metric == "revenue") & registry.value.notna() & (registry.role == "current") & registry.pit_usable & registry.vendor_attributed].copy()
        for c in consensus.to_dict("records"):
            dated(c["as_of_timestamp"], args.as_of)
            if c["unit"] != "musd":
                raise ValueError("Consensus unit is not USD millions")
        consensus.to_csv(output / "consensus_source_rows.csv", index=False)
        consensus["panel_family"] = consensus.vendor.map(lambda x: "LSEG family" if ("Yahoo" in x or "Alpha Vantage" in x) else "S&P Global" if "S&P" in x else x)
        consensus["observed_timestamp"] = pd.to_datetime(consensus.as_of_timestamp, format="mixed", utc=True)
        consensus = consensus.sort_values("observed_timestamp").groupby("panel_family", sort=False).tail(1).copy()
        consensus["observation_status"] = consensus.as_of_timestamp.map(lambda x: "captured_today_not_necessarily_new_vendor_publication" if str(x).startswith(args.as_of) else "older_dated_anchor_not_refreshed_today")
        consensus.to_csv(output / "consensus_selection.csv", index=False)
        comparisons = []
        for r in forecasts:
            if r["quarter"] != "2026Q4":
                continue
            for c in consensus.to_dict("records"):
                # L0 raw values in musd; include actual vintage fields, never restamp.
                comparisons.append(dict(scenario=r["scenario"], quarter=r["quarter"], guide_musd=r["guide_musd"],
                                        consensus_musd=c["value"], gap_musd=r["guide_musd"]-c["value"], gap_pct=100*(r["guide_musd"]/c["value"]-1),
                                        **{f"consensus_{k}": v for k,v in c.items() if k != "value"}))
        for name, rows in [("forecast", forecasts), ("operating_inputs", operating), ("cohort_weights", weights),
                           ("guide_reconciliation", reconciliation), ("sensitivity", sensitivity), ("consensus_comparison", comparisons)]:
            pd.DataFrame(rows).to_csv(output / f"{name}.csv", index=False, float_format="%.15g")
        term.to_csv(output / "k0_public_api_snapshot.csv", index=False, float_format="%.15g")
        pd.DataFrame([dict(statistic=s, cushion_decimal=g["cushion"], n=g["cushion_n"], information_date=g["knowable_from"], source_ref="K0 kernel_guide public API; trailing eight realized ratios") for s,g in guide_info.items()]).to_csv(output / "cushion_inputs.csv", index=False)
        fee = []
        for q in ["2026Q3", "2026Q4", "2027Q1"]:
            with_k = next(r for r in forecasts if r["quarter"] == q and r["scenario"] == "review_with_k")
            without = next(r for r in forecasts if r["quarter"] == q and r["scenario"] == "review_without_k")
            fee.append(dict(quarter=q, baseline="review_without_k", replacement="review_with_k", revenue_delta_musd=with_k["revenue_musd"]-without["revenue_musd"], guide_delta_musd=with_k["guide_musd"]-without["guide_musd"], treatment="Published ADR with-K replaces without-K; no fee take-rate uplift added", evidence_status="imposed_mechanics_not_causal_estimate"))
        pd.DataFrame(fee).to_csv(output / "fee_mechanics_comparison.csv", index=False)
        source_paths = [CARD, TERMS, KPI, CALENDAR, H2, K0_SNAPSHOT, REGISTRY,
                        "data/processed/overnight/02_guidance_cushion_series.csv", "analysis/src/forecast_methods/kernel_engine_v2/engine.py",
                        "analysis/src/forecast_methods/kernel_phi_v2/stage_d.py", "docs/adrv3/SYNTHESIS.md",
                        "docs/revenue-forecast-strategy/05_backtests/ALPHA_F_RNPL.md", "docs/revenue-forecast-strategy/05_backtests/LANE2_MEMO_READY_CLAIMS.md"]
        ledger = [dict(path=p, sha256=hashlib.sha256((ROOT / p).read_bytes()).hexdigest(), scope="committed L1/L2 input; never mutated", imported_at=args.as_of) for p in source_paths]
        for path in Path(__file__).parent.rglob("*.py"):
            ledger.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), scope="L4 reproducible code", imported_at=args.as_of))
        pd.DataFrame(ledger).to_csv(output / "source_ledger.csv", index=False)
        status = dict(as_of=args.as_of, l3_bundle_status="accepted" if manifest else "pending_not_supplied", accepted_l3_inputs=0 if not manifest else len(adapter_rows),
                      conversion_status=CONVERSION_STATUS, conversion_integration_owner="L3 estimation and validation; no new weight fitted in L4",
                      l3_commit_content_verification="not performed by loader; parent must verify supplied hashed files against claimed Git commit before promotion" if manifest else "not_applicable_no_bundle",
                      incremental_fx_musd=None, hedge_dollars=None, fx_neutral_revenue=None,
                      reason="Existing USD GBV and reported-revenue lambda retain embedded FX; L3 must supply verified cohort denominator/rates/timing before incremental replacement",
                      timing_hypothesis="RNPL recognition-period FX is an unverified working hypothesis; payment/FX fixing/recognition dates remain distinct",
                      research_adoption="No new empirical test; no direction, target, probability or card adoption")
        (output / "integration_status.json").write_text(json.dumps(status, indent=2)+"\n", encoding="utf-8")
        receipt = dict(as_of=args.as_of, completed_utc=datetime.now(timezone.utc).isoformat(), n_forecast_rows=len(forecasts), n_operating_rows=len(operating),
                       conversion_status=CONVERSION_STATUS,
                       n_cohort_rows=len(weights), reconciliation_residual_musd=residual, k0_q4_guide_musd=float(term[term.quarter=="2026Q4"].iloc[0].guide_mid_musd),
                       n_new_fitted_parameters=0, elapsed_seconds=time.perf_counter()-started,
                       missing_l3_inputs="cohort currency/reference weights; surviving RNPL revenue share; timing allocations; compatible rates; hedge bridge",
                       claimed_historical_validation="none; conditional review scenario only; W1=0 W2=0")
        (output / "run_receipt.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
        print(pd.DataFrame(forecasts)[["scenario", "quarter", "revenue_musd", "guide_musd"]].to_string(index=False))
        print(json.dumps(receipt, indent=2))
    except Exception as exc:
        (output / "FAILED_RUN.json").write_text(json.dumps(dict(error=type(exc).__name__, message=str(exc)), indent=2)+"\n", encoding="utf-8")
        raise


if __name__ == "__main__":
    main()
