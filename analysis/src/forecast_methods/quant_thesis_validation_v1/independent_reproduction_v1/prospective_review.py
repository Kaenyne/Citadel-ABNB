"""Independent point/selection/loss/attribution reconstruction plus adversarial calls."""
import argparse
import copy
import csv
import hashlib
import importlib.util
import itertools
import json
import math
import statistics
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
PKG = ROOT / "data/processed/forecast_methods/quant_thesis_validation_v1"
CAN = PKG / "prospective_v1/results_v1"
AUTHOR = ROOT / "analysis/src/forecast_methods/quant_thesis_validation_v1/prospective_v1/run.py"
METHODS = ["candidate_k0_gbv", "B1_guide_growth", "B2_revenue_naive_cushion"]
TERMS = ["U", "C", "P", "UC", "UP", "CP", "UCP", "ROUND"]
TOL = 1e-6


def read(p):
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def qindex(q):
    return int(q[:4]) * 4 + int(q[-1]) - 1


def quarter(i):
    return f"{i // 4}Q{i % 4 + 1}"


def shift(q, n):
    return quarter(qindex(q) + n)


def canon(q):
    return "20" + q[2:] + "Q" + q[0] if len(q) == 4 else q


def estimate(rows, season, variant):
    f = sorted([r for r in rows if r["q"][-1] == season], key=lambda r: r["q"])
    if variant == "ex_covid":
        f = [r for r in f if math.isfinite(r["nights"]) and abs(r["nights"]) <= 25]
    elif variant == "last3":
        f = f[-3:]
    if not f:
        raise LookupError("no season observations")
    weights = [2 ** ((i - len(f) + 1) / 2) for i in range(len(f))] if variant == "ewm" else [1] * len(f)
    return sum(r["lambda"] * w for r, w in zip(f, weights)) / sum(weights), [r["q"] for r in f]


def select(rows):
    variants = ["ex_covid", "last3", "ewm"]
    w = [r for r in rows if "2023Q1" <= r["q"] <= "2026Q2"]
    errors = {v: [] for v in variants}
    for target in w:
        try:
            values = [estimate([r for r in w if r["q"] != target["q"]], target["q"][-1], v)[0] for v in variants]
        except LookupError:
            continue
        for variant, coefficient in zip(variants, values):
            errors[variant].append((coefficient / target["lambda"] - 1) * 100)
    if len(errors[variants[0]]) < 8:
        return "ex_covid", len(errors[variants[0]])
    return min(variants, key=lambda v: sum(e * e for e in errors[v]) / len(errors[v])), len(errors[variants[0]])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    out = parser.parse_args().out.resolve()
    if out.exists() or not out.is_relative_to((PKG / "independent_reproduction_v1").resolve()):
        raise ValueError("New independent_reproduction_v1 output required")
    av = {r["quarter"]: r["conservative_available_date"] for r in read(PKG / "source_audit_v1/results_v2/observation_availability.csv")}
    panel = {}
    for r in read(ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv"):
        q = canon(r["quarter"])
        panel[q] = dict(q=q, available=av[q], gbv=float(r["gbv_musd"]), revenue=float(r["revenue_musd"]),
                        nights=float(r["nights_yoy_pct"]) if r["nights_yoy_pct"] else math.nan)
    guides = {}
    for r in sorted(read(ROOT / "data/processed/overnight/02_guidance_ledger.csv"), key=lambda r: r["print_date"]):
        if r["metric"] == "revenue_usd_m" and r["guide_type"] == "range":
            q = canon(r["target_period"])
            guides.setdefault(q, dict(mid=(float(r["value_low"]) + float(r["value_high"])) / 2, available=r["print_date"]))
    cushions = {canon(r["target_period"]): float(r["actual"]) / float(r["value_mid"])
                for r in read(ROOT / "data/processed/overnight/02_guidance_cushion_series.csv")}
    sessions = sorted({r["date"] for r in read(ROOT / "data/processed/forecast_methods/returns_v1/ohlc_daily.csv") if r["ticker"] == "QQQ"})
    reference = {(r["quarter"], r["method"]): r for r in read(CAN / "forecast/predictions.csv")}
    numerical, reconstructed, selection_trace = [], {}, []

    def check(area, key, value, expected):
        difference = abs(float(value) - float(expected))
        if not difference < TOL:
            raise AssertionError((area, key, value, expected, difference))
        numerical.append(dict(area=area, key=key, value=float(value), expected=float(expected), difference=difference))

    origins = {}
    for i in range(qindex("2021Q4"), qindex("2026Q4") + 1):
        q = quarter(i)
        start = date(int(q[:4]), (int(q[-1]) - 1) * 3 + 1, 1)
        anchor = start - timedelta(days=18)
        d = max(x for x in sessions if x <= str(anchor))
        assert (anchor - date.fromisoformat(d)).days <= 4
        origins[q] = d
        obs = {k: v for k, v in panel.items() if v["available"] < d}
        historical_c = sorted(k for k in cushions if av[k] < d)[-8:]
        divisor = statistics.median(cushions[k] for k in historical_c) if len(historical_c) >= 3 else None
        latest = max(obs)
        lam_rows = []
        for tq, r in obs.items():
            if all(shift(tq, -lag) in obs for lag in (1, 2)):
                b = (2 * obs[shift(tq, -1)]["gbv"] + obs[shift(tq, -2)]["gbv"]) / 3
                lam_rows.append(dict(**r, base=b, **{"lambda": r["revenue"] / b}))
        chosen, loo_n = select(lam_rows)
        selection_trace.append(dict(quarter=q, chosen=chosen, common_loo_cells=loo_n, origin=d))
        for method in METHODS:
            expected = reference[(q, method)]
            assert expected["origin_date"] == d and expected["anchor_date"] == str(anchor)
            close = datetime.fromisoformat(d + "T16:00:00").replace(tzinfo=ZoneInfo("America/New_York"))
            assert expected["origin_close"] == close.isoformat()
            if q in guides:
                assert guides[q]["available"] > d
            result = dict(quarter=q, method=method, origin=d)
            try:
                if method == METHODS[0]:
                    if divisor is None:
                        raise LookupError("cushion")
                    lam, trained = estimate(lam_rows, q[-1], chosen)
                    gv = []
                    for lag in (1, 2):
                        tq = shift(q, -lag)
                        gv.append(obs[tq]["gbv"] if tq in obs else obs[shift(tq, -4)]["gbv"] * obs[latest]["gbv"] / obs[shift(latest, -4)]["gbv"])
                    base = (2 * gv[0] + gv[1]) / 3
                    point = lam * base / divisor
                    result.update(lam=lam, base=base, divisor=divisor)
                    check("lambda", q, lam * 100, expected["lambda_pct"])
                    check("divisor", q, divisor, expected["cushion_divisor"])
                    check("GBV1", q, gv[0], expected["gbv1_hat_musd"])
                    check("GBV2", q, gv[1], expected["gbv2_hat_musd"])
                    assert expected["lambda_variant"] == chosen
                    assert expected["lambda_training_quarters"] == ";".join(trained)
                elif method == METHODS[1]:
                    known_guides = {k: v for k, v in guides.items() if v["available"] < d}
                    h = max(known_guides)
                    point = known_guides[shift(q, -4)]["mid"] * known_guides[h]["mid"] / known_guides[shift(h, -4)]["mid"]
                else:
                    if divisor is None:
                        raise LookupError("cushion")
                    point = obs[shift(q, -4)]["revenue"] * obs[latest]["revenue"] / obs[shift(latest, -4)]["revenue"] / divisor
                result.update(status="forecast", point=point)
                assert expected["status"] == "forecast"
                check("forecast", q + ":" + method, point, expected["point_musd"])
                if q in guides:
                    result["raw"] = point - guides[q]["mid"]
                    result["fair"] = math.copysign(max(abs(result["raw"]) - .5, 0), result["raw"])
            except (KeyError, LookupError, ValueError) as exc:
                if isinstance(exc, AssertionError):
                    raise
                result["status"] = "abstain"
                assert expected["status"] == "abstain", (q, method, exc)
            reconstructed[(q, method)] = result
    errors_ref = {(r["quarter"], r["method"]): r for r in read(CAN / "evaluation/errors.csv")}
    for key, row in reconstructed.items():
        if "fair" in row:
            check("raw_error", str(key), row["raw"], errors_ref[key]["error_raw_musd"])
            check("interval_error", str(key), row["fair"], errors_ref[key]["error_interval_musd"])
    matched, scores = {}, []
    for window, lo in [("W1", "2023Q1"), ("W2", "2024Q1")]:
        sets = {m: {q for (q, method), r in reconstructed.items() if method == m and "fair" in r and lo <= q <= "2026Q2"} for m in METHODS}
        matched[window] = set.intersection(*sets.values())
        for sr in read(CAN / "evaluation/scores.csv"):
            if sr["window"] != window:
                continue
            scope, method = sr["scope"], sr["method"]
            qs = sets[method] if scope == "own_available" else (matched[window] if scope == "all_three" else sets[METHODS[0]] & sets[scope[5:]])
            e = np.array([reconstructed[(q, method)]["fair" if sr["basis"] == "interval" else "raw"] for q in sorted(qs)])
            for field, value in {"n": len(e), "rmse": np.sqrt(np.mean(e * e)), "mae": np.mean(abs(e)), "bias": np.mean(e), "mse": np.mean(e * e)}.items():
                check("score", str((window, scope, method, sr["basis"], field)), value, sr[field])
            if scope == "all_three" and sr["basis"] == "interval":
                scores.append(dict(window=window, method=method, n=len(e), rmse=np.sqrt(np.mean(e * e)), mae=np.mean(abs(e)), bias=np.mean(e)))
    for yr in read(CAN / "evaluation/year_deletion.csv"):
        qs = [q for q in matched[yr["window"]] if q[:4] != yr["deleted_year"]]
        c, b = [np.mean([reconstructed[(q, m)]["fair"] ** 2 for q in qs]) for m in (METHODS[0], yr["baseline"])]
        check("year_deletion", str(yr), c - b, yr["mse_delta"])
    contribution_rows = {}
    for cr in read(CAN / "evaluation/contributions.csv"):
        q = cr["quarter"]; r = reconstructed[(q, METHODS[0])]
        base = (2 * panel[shift(q, -1)]["gbv"] + panel[shift(q, -2)]["gbv"]) / 3
        realized = panel[q]["revenue"]; mid = guides[q]["mid"]
        u, c, p = r["base"] / base - 1, r["lam"] / (realized / base) - 1, realized / (r["divisor"] * mid) - 1
        values = np.array([mid * u, mid * c, mid * p, mid * u * c, mid * u * p, mid * c * p, mid * u * c * p, r["fair"] - r["raw"]])
        for term, value in zip(TERMS, values):
            check("contribution", q + ":" + term, value, cr[term])
        check("term_sum", q, sum(values), r["fair"])
        contribution_rows[q] = values
    moments = read(CAN / "evaluation/contribution_cross_moments.csv")
    covariance_summaries = []
    for win, qs in matched.items():
        x = np.stack([contribution_rows[q] for q in sorted(qs)])
        cross = x.T @ x / len(x); means = x.mean(axis=0)
        covariance = (x - means).T @ (x - means) / len(x)
        total, diagonal = cross.sum(), cross.diagonal().sum()
        for mr in [r for r in moments if r["window"] == win]:
            i, j = TERMS.index(mr["term1"]), TERMS.index(mr["term2"])
            check("cross_moment", win + ":" + str((i, j)), cross[i, j], mr["raw_cross_moment"])
            check("covariance", win + ":" + str((i, j)), covariance[i, j], mr["population_covariance"])
        error_mse = np.mean([reconstructed[(q, METHODS[0])]["fair"] ** 2 for q in qs])
        check("MSE_identity", win, total, error_mse)
        covariance_summaries.append(dict(window=win, n=len(qs), true_mse=error_mse, diagonal_only_mse=diagonal, cross_terms=total - diagonal, exact_mse=total))
    for br in read(CAN / "evaluation/prediction_bands.csv"):
        q, m = br["quarter"], br["method"]
        r = reconstructed[(q, m)]
        history = sorted(k for (k, method), z in reconstructed.items() if method == m and "raw" in z and k < q and guides[k]["available"] < origins[q])[-8:]
        assert int(br["calibration_n"]) == len(history) and br["calibration_quarters"] == ";".join(history)
        if len(history) >= 6:
            order = math.ceil(.8 * (len(history) + 1))
            residuals = sorted(abs(reconstructed[(k, m)]["raw"]) / reconstructed[(k, m)]["point"] for k in history)
            a = residuals[order - 1]
            for field, value in {"relative_halfwidth": a, "lo_musd": max(0, r["point"] * (1 - a)), "hi_musd": r["point"] * (1 + a)}.items():
                check("band", q + ":" + m + ":" + field, value, br[field])
        else:
            assert br["status"] == "insufficient_chronological_errors" and br["lo_musd"] == ""
    # Author API is used only for independently specified adversarial perturbations.
    spec = importlib.util.spec_from_file_location("independent_adversarial_target", AUTHOR)
    api = importlib.util.module_from_spec(spec); sys.modules[spec.name] = api; spec.loader.exec_module(api)
    src = api.load_sources(); k0, naive = api.load_apis(); poison_checks = []
    for q, d in origins.items():
        poisoned = copy.deepcopy(src); cutoff = date.fromisoformat(d)
        mask = poisoned.panel.print_date >= cutoff
        poisoned.panel.loc[mask, ["gbv_musd", "revenue_musd", "nights_yoy_pct"]] = 1e11
        poisoned.cushions.loc[poisoned.cushions.print_date >= cutoff, ["actual", "value_mid"]] = [8e12, 2.0]
        mask = poisoned.guides.print_date >= cutoff
        poisoned.guides.loc[mask, ["value_low", "value_high", "value_mid"]] *= 1e8
        result = api.forecast_one(q, poisoned, k0, naive)
        for pr in result["predictions"]:
            own = reconstructed[(q, pr["method"])]
            assert pr["status"] == own["status"]
            if pr["status"] == "forecast":
                check("future_poisoning", q + ":" + pr["method"], pr["point_musd"], own["point"])
        poison_checks.append(dict(quarter=q, origin=d, future_KPI_guide_cushion_poisoned=True, forecast_status_and_points_unchanged=True))
    rebuilt = PKG / "independent_reproduction_v1/prospective_rebuild_v1"
    byte_rows = [{"file": str(p.relative_to(CAN)), "pass": p.read_bytes() == (rebuilt / p.relative_to(CAN)).read_bytes(), "sha256": sha(p)} for p in CAN.rglob("*") if p.is_file()]
    assert all(x["pass"] for x in byte_rows)
    receipt = dict(reviewer="/root/uncertainty_auditor", author="/root/source_auditor", status="PASS_independent_reproduction_research_hurdle_FAIL_preserved",
                   primary_n={k: len(v) for k, v in matched.items()}, numeric_checks=len(numerical), tolerance=TOL,
                   max_difference=max(r["difference"] for r in numerical), files_byte_identical=len(byte_rows), poisoned_origins=len(poison_checks),
                   independent_point_rule_and_dynamic_K0_reconstruction=True, author_point_functions_used_for_numerical_reconstruction=False,
                   author_API_used_only_for_adversarial_challenges=True, empirical_new_specifications=0,
                   bindings={str(p.relative_to(ROOT)): sha(p) for p in [AUTHOR, AUTHOR.with_name("test_prospective.py"), ROOT / "docs/revenue-forecast-strategy/quant_thesis_validation_v1/FINAL_PROTOCOL_v1.md", *[p for p in CAN.rglob("*") if p.is_file()]]})
    out.mkdir(parents=True)
    for name, values in [("numeric_checks.csv", numerical), ("reconstructed_scores.csv", scores), ("dynamic_selection_trace.csv", selection_trace),
                         ("covariance_summaries.csv", covariance_summaries), ("poisoning_checks.csv", poison_checks), ("byte_reproduction.csv", byte_rows)]:
        with (out / name).open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(values[0])); writer.writeheader(); writer.writerows(values)
    (out / "prospective_independent_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k != "bindings"}, indent=2))


if __name__ == "__main__":
    main()
