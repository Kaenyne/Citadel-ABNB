"""Preregistered preannouncement guide reconstruction; immutable staged outputs."""
from __future__ import annotations

import argparse
import hashlib
import importlib
import io
import itertools
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
COMMIT = "8821961853e4068febbfe2712f9a4e1036c9e629"
PROTOCOL = "docs/revenue-forecast-strategy/quant_thesis_validation_v1/FINAL_PROTOCOL_v1.md"
PROTOCOL_HASH = "dd010ed6d158f1003b9ec55147e16a3f9464010c571b20fe25dad254202cb8ec"
PROPOSAL = "docs/revenue-forecast-strategy/quant_thesis_validation_v1/protocol_design_v1/PROTOCOL_PROPOSAL_v1.md"
PROPOSAL_HASH = "93cb753261d549512d82e11115aa53ca77ecda97f578605fe7a90197db30f4ed"
AVAILABILITY = "data/processed/forecast_methods/quant_thesis_validation_v1/source_audit_v1/results_v2/observation_availability.csv"
FILES = {
    "panel": "data/processed/overnight/02_kpi_panel_quarterly.csv",
    "guides": "data/processed/overnight/02_guidance_ledger.csv",
    "cushion": "data/processed/overnight/02_guidance_cushion_series.csv",
    "calendar": "data/processed/forecast_methods/harness/calendar.csv",
    "sessions": "data/processed/forecast_methods/returns_v1/ohlc_daily.csv",
    "engine": "analysis/src/forecast_methods/kernel_engine_v2/engine.py",
    "baseline": "analysis/src/forecast_methods/harness/baselines.py",
    "loaders": "analysis/src/forecast_methods/harness/loaders.py",
    "quarters": "analysis/src/forecast_methods/harness/quarters.py",
    "targets": "data/processed/forecast_methods/harness/targets.csv",
}
METHODS = ("candidate_k0_gbv", "B1_guide_growth", "B2_revenue_naive_cushion")
EASTERN = ZoneInfo("America/New_York")
TERMS = ("U", "C", "P", "UC", "UP", "CP", "UCP", "ROUND")


class MissingInput(ValueError):
    pass


def sha(data):
    return hashlib.sha256(data).hexdigest()


def blob(path):
    return subprocess.check_output(["git", "show", f"{COMMIT}:{path}"], cwd=ROOT)


def read_git(path):
    return pd.read_csv(io.BytesIO(blob(path)))


def canon(q):
    q = str(q)
    return "20" + q[2:] + "Q" + q[0] if len(q) == 4 and q[1] == "Q" else q


def shift(q, n):
    return str(pd.Period(q, freq="Q") + n)


def jsonable(x):
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [jsonable(v) for v in x]
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        return float(x) if math.isfinite(x) else None
    if isinstance(x, (date, datetime, pd.Timestamp)):
        return x.isoformat()
    if pd.isna(x):
        return None
    return x


def write_json(path, obj):
    path.write_text(json.dumps(jsonable(obj), indent=2, allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path, rows, columns=None):
    f = rows if isinstance(rows, pd.DataFrame) else pd.DataFrame(rows, columns=columns)
    f.to_csv(path, index=False, float_format="%.15g", lineterminator="\n")


def require_unique_dates(frame, key, column, label):
    if frame[key].isna().any() or frame.duplicated(key).any():
        raise ValueError(label + " missing or duplicate key")
    dates = pd.to_datetime(frame[column], errors="coerce")
    if dates.isna().any():
        raise ValueError(label + " missing or invalid publication date")
    return dates.dt.date


def positive(value, label):
    x = float(value)
    if not math.isfinite(x) or x <= 0:
        raise MissingInput("missing_or_nonpositive:" + label)
    return x


def first_guides(raw):
    g = raw[(raw.metric == "revenue_usd_m") & (raw.guide_type == "range")].copy()
    g["quarter"] = g.target_period.map(canon)
    g["print_date"] = pd.to_datetime(g.print_date, errors="coerce").dt.date
    if g.print_date.isna().any():
        raise ValueError("Guide publication date missing")
    # First-issued target only. Later revisions may exist but cannot overwrite it.
    g = g.sort_values(["quarter", "print_date", "guide_id"])
    first_date = g.groupby("quarter").print_date.transform("min")
    first = g[g.print_date == first_date].copy()
    if first.duplicated("quarter").any():
        raise ValueError("Ambiguous same-date first guidance")
    if not np.allclose(first.value_mid, (first.value_low + first.value_high) / 2, rtol=0, atol=1e-9):
        raise ValueError("Guide midpoint does not reconcile to original endpoints")
    return first.reset_index(drop=True)


@dataclass
class Sources:
    panel: pd.DataFrame
    guides: pd.DataFrame
    cushions: pd.DataFrame
    sessions: list
    calendar: pd.DataFrame
    manifest: list


def load_sources():
    manifest = []
    for path, expected in ((PROTOCOL, PROTOCOL_HASH), (PROPOSAL, PROPOSAL_HASH)):
        actual = sha((ROOT / path).read_bytes())
        if actual != expected:
            raise ValueError("Frozen protocol hash changed: " + path)
        manifest.append(dict(path=path, source="protocol_freeze", sha256=actual))
    for label, path in FILES.items():
        data = blob(path)
        disk = (ROOT / path).read_bytes()
        if disk.replace(b"\r\n", b"\n") != data.replace(b"\r\n", b"\n"):
            raise ValueError("Immutable input differs on disk: " + path)
        manifest.append(dict(path=path, source=COMMIT, sha256=sha(data)))
    av = pd.read_csv(ROOT / AVAILABILITY)
    require_unique_dates(av, "quarter", "conservative_available_date", "availability")
    manifest.append(dict(path=AVAILABILITY, source="source_audit_v1/results_v2", sha256=sha((ROOT / AVAILABILITY).read_bytes())))
    panel = read_git(FILES["panel"])[["quarter", "gbv_musd", "revenue_musd", "nights_yoy_pct"]].copy()
    panel["quarter"] = panel.quarter.map(canon)
    panel["print_date"] = panel.quarter.map(av.set_index("quarter").conservative_available_date)
    panel["print_date"] = require_unique_dates(panel, "quarter", "print_date", "KPI")
    panel = panel.sort_values("quarter").reset_index(drop=True)
    guides = first_guides(read_git(FILES["guides"]))
    cushions = read_git(FILES["cushion"])
    cushions["quarter"] = cushions.target_period.map(canon)
    cushions["print_date"] = cushions.quarter.map(panel.set_index("quarter").print_date)
    cushions["print_date"] = require_unique_dates(cushions, "quarter", "print_date", "cushions")
    ohlc = read_git(FILES["sessions"])
    sessions = sorted(pd.to_datetime(ohlc.loc[ohlc.ticker == "QQQ", "date"]).dt.date.tolist())
    if len(set(sessions)) != len(sessions):
        raise ValueError("Duplicate QQQ session")
    calendar = read_git(FILES["calendar"])
    calendar["print_date"] = pd.to_datetime(calendar.print_date).dt.date
    return Sources(panel, guides, cushions, sessions, calendar, manifest)


def load_apis():
    # load_sources verifies exact inherited code before public API imports.
    k0 = importlib.import_module("analysis.src.forecast_methods.kernel_engine_v2.engine")
    baseline = importlib.import_module("analysis.src.forecast_methods.harness.baselines")
    return k0, baseline


def origin(q, sessions):
    anchor = pd.Period(q, freq="Q").start_time.date() - timedelta(days=18)
    dates = [d for d in sessions if d <= anchor]
    if not dates or (anchor - dates[-1]).days > 4:
        raise MissingInput("session_missing_within_four_days")
    d = dates[-1]
    # All protocol anchors are mid-month, not scheduled holiday-eve half-days.
    if d.month not in (3, 6, 9, 12) or not 9 <= d.day <= 16 or d.weekday() > 4:
        raise ValueError("Origin outside verified regular-session anchor domain")
    close = datetime.combine(d, time(16), EASTERN)
    return dict(anchor_date=anchor, origin_date=d, origin_close=close.isoformat(),
                origin_close_utc=close.astimezone(ZoneInfo("UTC")).isoformat(),
                close_basis="regular_session_midmonth; no scheduled early close at these anchors")


def forecast_one(q, src, k0, baseline):
    meta = dict(quarter=q, **origin(q, src.sessions))
    d = meta["origin_date"]
    guide_meta = src.guides[src.guides.quarter == q]
    scheduled = src.calendar[src.calendar.next_quarter_guided == q]
    target_date = guide_meta.iloc[0].print_date if len(guide_meta) else (scheduled.iloc[0].print_date if len(scheduled) else None)
    if target_date is None or target_date <= d:
        raise ValueError("Target guide already available or issuance metadata missing")
    meta.update(guide_issuance_date=target_date, lead_days=(target_date-d).days,
                target_date_basis="observed_first_issuance" if len(guide_meta) else "scheduled_assumption_not_verified_current",
                reconstruction_status="frozen_panel_reconstruction_not_archived_forecast")
    # Validate dates before filtering; validate numbers only after the cutoff.
    p = src.panel.copy()
    p["print_date"] = require_unique_dates(p, "quarter", "print_date", "KPI")
    p = p[p.print_date < d].copy().sort_values("quarter")
    for col in ("gbv_musd", "revenue_musd"):
        if not all(np.isfinite(p[col]) & (p[col] > 0)):
            raise MissingInput("invalid_admissible_" + col)
    if q in set(p.quarter):
        raise ValueError("Target actual is already in forecasting panel")
    public_guides = src.guides[src.guides.print_date < d].copy()
    if q in set(public_guides.quarter):
        raise ValueError("Target guide leaked to predictor information set")
    inputs = [dict(quarter=q, role="admissible_KPI", input_quarter=r.quarter,
                   available_date=r.print_date, gbv_musd=r.gbv_musd, revenue_musd=r.revenue_musd,
                   nights_yoy_pct=r.nights_yoy_pct) for r in p.itertuples()]
    guide_inputs = []
    cushion_inputs = []
    train = []
    gbv_predictions = []
    predictions = []
    c_all = src.cushions.copy()
    c_all["print_date"] = require_unique_dates(c_all, "quarter", "print_date", "cushions")
    c = c_all[c_all.print_date < d].copy().sort_values("quarter").tail(8)
    divisor = None
    if len(c) >= 3:
        ratios = [positive(r.actual, "cushion_actual") / positive(r.value_mid, "cushion_mid") for r in c.itertuples()]
        divisor = float(np.median(ratios))
        for row, ratio in zip(c.itertuples(), ratios):
            panel_match = p[p.quarter == row.quarter]
            panel_actual = float(panel_match.iloc[0].revenue_musd) if len(panel_match) else np.nan
            cushion_inputs.append(dict(quarter=q, input_quarter=row.quarter, actual_musd=row.actual,
                first_guide_mid_musd=row.value_mid, ratio=ratio, actual_available_date=row.print_date,
                panel_revenue_musd=panel_actual, cushion_minus_panel_actual_musd=float(row.actual)-panel_actual))
    common = dict(cushion_divisor=divisor, cushion_n=len(c),
                  cushion_quarters=";".join(c.quarter.tolist()), panel_n=len(p),
                  panel_quarters=";".join(p.quarter.tolist()))
    # Candidate only needs public financial observations, never the unknown target guide.
    try:
        if divisor is None:
            raise MissingInput("fewer_than_three_cushion_observations")
        lam = k0.pit_lambda(int(q[-1]), d.isoformat(), variant=None, panel=p)
        lookup = p.set_index("quarter")
        if p.empty:
            raise MissingInput("no_GBV_observed")
        latest = p.iloc[-1].quarter
        missing = [k for k in (shift(q, -1), shift(q, -2)) if k not in lookup.index]
        growth = None
        if missing:
            if shift(latest,-4) not in lookup.index:
                raise MissingInput("GBV_latest_yoy_anchor:" + shift(latest,-4))
            growth = positive(lookup.loc[latest,"gbv_musd"], "latest_GBV") / positive(lookup.loc[shift(latest,-4),"gbv_musd"], "latest_GBV_lag4")
        gbv = {}
        for lag in (1, 2):
            k = shift(q, -lag)
            if k in lookup.index:
                gbv[k] = positive(lookup.loc[k,"gbv_musd"], "observed_"+k)
                kind, anchor, anchor_value = "observed_at_origin", k, gbv[k]
            else:
                anchor = shift(k,-4)
                if anchor not in lookup.index:
                    raise MissingInput("GBV_seasonal_anchor:" + anchor)
                anchor_value = positive(lookup.loc[anchor,"gbv_musd"], "GBV_anchor_"+anchor)
                gbv[k] = anchor_value * growth
                kind = "reconstructed_latest_observed_yoy_persistence"
            gbv_predictions.append(dict(quarter=q, lag=lag, input_quarter=k, value_musd=gbv[k], kind=kind,
                source_anchor_quarter=anchor, source_anchor_musd=anchor_value,
                source_anchor_available_date=lookup.loc[anchor,"print_date"],
                latest_actual_quarter=latest, latest_actual_yoy_ratio=growth,
                latest_actual_available_date=lookup.loc[latest,"print_date"],
                yoy_denominator_quarter=shift(latest,-4) if growth is not None else "",
                current_lag_actual_used=kind == "observed_at_origin"))
        base = (2*gbv[shift(q,-1)]+gbv[shift(q,-2)])/3
        revenue = lam["lambda_pct"] / 100 * base
        point = positive(revenue/divisor, "candidate_point")
        predictions.append(dict(**meta, **common, method=METHODS[0], status="forecast", reason="",
            point_musd=point, revenue_point_musd=revenue, gbv1_hat_musd=gbv[shift(q,-1)],
            gbv2_hat_musd=gbv[shift(q,-2)], base_hat_musd=base, lambda_pct=lam["lambda_pct"],
            lambda_variant=lam["variant"], lambda_n_train=lam["n_train"],
            lambda_training_quarters=";".join(lam["training_quarters"]),
            lambda_knowable_from=lam["knowable_from"], n_unprinted_gbv=len(missing), n_params=5))
        for tq in lam["training_quarters"]:
            row = lookup.loc[tq]
            g1, g2 = lookup.loc[shift(tq,-1)], lookup.loc[shift(tq,-2)]
            train.append(dict(quarter=q, training_quarter=tq, revenue_musd=row.revenue_musd,
                revenue_available_date=row.print_date, gbv1_musd=g1.gbv_musd, gbv2_musd=g2.gbv_musd,
                gbv1_available_date=g1.print_date, gbv2_available_date=g2.print_date,
                lambda_observation_pct=100*row.revenue_musd/((2*g1.gbv_musd+g2.gbv_musd)/3),
                nights_yoy_pct=row.nights_yoy_pct, selection=lam["variant"]))
    except (MissingInput, k0.DataUnavailable) as exc:
        predictions.append(dict(**meta, **common, method=METHODS[0], status="abstain", reason=str(exc), point_musd=np.nan, n_params=5))
    try:
        g = public_guides.set_index("quarter").sort_index()
        if g.empty:
            raise MissingInput("no_prior_guides")
        h = g.index[-1]
        required = (shift(q,-4), h, shift(h,-4))
        absent = [x for x in required if x not in g.index]
        if absent:
            raise MissingInput("B1_missing_guides:" + ";".join(absent))
        vals = [positive(g.loc[x,"value_mid"], "guide_"+x) for x in required]
        point = vals[0]*vals[1]/vals[2]
        predictions.append(dict(**meta, method=METHODS[1], status="forecast", reason="", point_musd=point,
            source_quarters=";".join(required), n_params=0))
        for role, tq in zip(("seasonal_anchor", "latest_guide", "latest_guide_year_ago"), required):
            guide_inputs.append(dict(quarter=q, role="B1_"+role, input_quarter=tq,
                guide_mid_musd=g.loc[tq,"value_mid"], available_date=g.loc[tq,"print_date"]))
    except MissingInput as exc:
        predictions.append(dict(**meta, method=METHODS[1], status="abstain", reason=str(exc), point_musd=np.nan, n_params=0))
    try:
        if divisor is None:
            raise MissingInput("fewer_than_three_cushion_observations")
        t = p[["quarter", "print_date", "revenue_musd"]].copy()
        required = [shift(q,-4)]
        latest = t.iloc[-1].quarter if len(t) else None
        required += [latest, shift(latest,-4)] if latest else ["no_latest"]
        absent = [x for x in required if x not in set(t.quarter)]
        if absent:
            raise MissingInput("B2_missing_revenue_yoy_or_anchor:" + ";".join(absent))
        result = baseline.baseline_naive(d, q, metric="revenue_musd", prior_basis="PIT", targets=t)
        if result is None:
            raise MissingInput("B2_public_API_unavailable")
        point = positive(result["point"], "B2_revenue") / divisor
        predictions.append(dict(**meta, **common, method=METHODS[2], status="forecast", reason="",
            point_musd=point, revenue_point_musd=result["point"], source_quarters=";".join(required),
            n_params=1, api_interval_discarded=True))
    except MissingInput as exc:
        predictions.append(dict(**meta, **common, method=METHODS[2], status="abstain", reason=str(exc), point_musd=np.nan, n_params=1))
    return dict(predictions=predictions, panel_inputs=inputs, guide_inputs=guide_inputs,
                cushion_inputs=cushion_inputs, lambda_training=train, gbv_inputs=gbv_predictions)


def forecast_stage(out, src):
    k0, baseline = load_apis()
    all_rows = {k: [] for k in ("predictions", "panel_inputs", "guide_inputs", "cushion_inputs", "lambda_training", "gbv_inputs")}
    quarters = [str(q) for q in pd.period_range("2021Q4", "2026Q4", freq="Q")]
    for q in quarters:
        result = forecast_one(q, src, k0, baseline)
        for key, values in result.items():
            all_rows[key].extend(values)
    out.mkdir(parents=True)
    for key, values in all_rows.items():
        write_csv(out / (key+".csv"), values)
    predictions = pd.DataFrame(all_rows["predictions"])
    write_csv(out/"exclusions.csv", predictions[predictions.status == "abstain"])
    write_json(out/"input_manifest.json", src.manifest)
    write_json(out/"forecast_freeze.json", dict(protocol_sha256=PROTOCOL_HASH, proposal_sha256=PROPOSAL_HASH,
        source_commit=COMMIT, code_sha256=sha(Path(__file__).read_bytes()),
        stage="all point forecasts and used inputs fixed before outcome evaluation",
        n_target_origins=len(quarters), n_method_rows=len(predictions),
        files={p.name: sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()}))
    return predictions


def window(frame, win):
    return frame[frame.quarter.between("2023Q1" if win=="W1" else "2024Q1", "2026Q2")].copy()


def metrics(errors):
    e = np.asarray(errors, dtype=float)
    return dict(n=len(e), rmse=float(np.sqrt(np.mean(e*e))) if len(e) else np.nan,
                mae=float(np.mean(abs(e))) if len(e) else np.nan,
                bias=float(np.mean(e)) if len(e) else np.nan,
                mse=float(np.mean(e*e)) if len(e) else np.nan)


def errors_frame(predictions, src):
    # Outcome-only join: this function is never called by forecast_stage.
    g = src.guides[["quarter", "value_low", "value_high", "value_mid", "print_date"]].rename(columns={"print_date":"target_available_date"})
    f = predictions[predictions.status == "forecast"].merge(g, on="quarter", how="left", validate="many_to_one")
    f["target_mid_lo"] = f.value_mid - .5
    f["target_mid_hi"] = f.value_mid + .5
    f["rounding_basis"] = "project midpoint +/-0.5 USDm convention; nominal guide endpoints"
    f["error_raw_musd"] = f.point_musd-f.value_mid
    f["error_interval_musd"] = f.point_musd-f.point_musd.clip(f.target_mid_lo, f.target_mid_hi)
    f.loc[f.value_mid.isna(), "error_interval_musd"] = np.nan
    f["rounding_adjustment_musd"] = f.error_interval_musd-f.error_raw_musd
    f["error_raw_pct"] = 100*f.error_raw_musd/f.value_mid
    f["error_interval_pct"] = 100*f.error_interval_musd/f.value_mid
    f["year"] = f.quarter.str[:4].astype(int)
    f["season"] = f.quarter.str[-1].astype(int)
    return f


def score_tables(errors):
    scores, paired, deletions, slices, coverage = [], [], [], [], []
    matched_sets = {}
    for win in ("W1", "W2"):
        w = window(errors,win).dropna(subset=["error_interval_musd"])
        availability = {method: set(w[w.method == method].quarter) for method in METHODS}
        common = set.intersection(*availability.values())
        matched_sets[win] = common
        max_slots = [str(q) for q in pd.period_range("2023Q1" if win=="W1" else "2024Q1","2026Q2",freq="Q")]
        for method in METHODS:
            coverage.append(dict(window=win, method=method, n=len(availability[method]),
                maximum_slots=len(max_slots), quarters=";".join(sorted(availability[method])),
                unavailable_quarters=";".join(q for q in max_slots if q not in availability[method]),
                all_three_n=len(common), all_three_quarters=";".join(sorted(common))))
        scopes = [("own_available", None), ("all_three", common)]
        scopes += [("pair_"+m, availability[METHODS[0]] & availability[m]) for m in METHODS[1:]]
        for scope, keep in scopes:
            for method in METHODS:
                if scope.startswith("pair_") and method not in (METHODS[0],scope[len("pair_"):]):
                    continue
                rows = w[w.method == method]
                if keep is not None:
                    rows = rows[rows.quarter.isin(keep)]
                for basis,col in (("interval", "error_interval_musd"),("raw", "error_raw_musd")):
                    scores.append(dict(window=win,scope=scope,method=method,basis=basis,**metrics(rows[col])))
        common_rows = w[w.quarter.isin(common)]
        for method in METHODS[1:]:
            for scope,keep in (("all_three",common),("pair",availability[METHODS[0]] & availability[method])):
                a = w[(w.method==METHODS[0]) & w.quarter.isin(keep)].set_index("quarter")
                b = w[(w.method==method) & w.quarter.isin(keep)].set_index("quarter")
                for q in sorted(keep):
                    x,y = a.loc[q],b.loc[q]
                    paired.append(dict(window=win,scope=scope,baseline=method,quarter=q,n=1,
                        candidate_error_musd=x.error_interval_musd, baseline_error_musd=y.error_interval_musd,
                        signed_error_delta_musd=x.error_interval_musd-y.error_interval_musd,
                        absolute_loss_delta_musd=abs(x.error_interval_musd)-abs(y.error_interval_musd),
                        squared_loss_delta_musd2=x.error_interval_musd**2-y.error_interval_musd**2,
                        raw_squared_loss_delta_musd2=x.error_raw_musd**2-y.error_raw_musd**2))
            for year in sorted(common_rows.year.unique()):
                left = common_rows[common_rows.year != year]
                a,b = [left[left.method==m] for m in (METHODS[0],method)]
                ma,mb = metrics(a.error_interval_musd), metrics(b.error_interval_musd)
                deletions.append(dict(window=win,baseline=method,deleted_year=int(year),n=ma["n"],
                    remaining_years=int(left.year.nunique()),candidate_mse=ma["mse"],baseline_mse=mb["mse"],
                    mse_delta=ma["mse"]-mb["mse"],
                    lower_mse=bool(ma["mse"] < mb["mse"]-1e-9), refit=False))
        for dimension in ("year","season"):
            for value in sorted(common_rows[dimension].unique()):
                for method in METHODS:
                    r = common_rows[(common_rows[dimension]==value)&(common_rows.method==method)]
                    slices.append(dict(window=win,dimension=dimension,value=int(value),method=method,**metrics(r.error_interval_musd)))
    return scores,paired,deletions,slices,coverage,matched_sets


def contributions(errors, src, matched):
    rows, moment_rows, identities = [], [], []
    panel = src.panel.set_index("quarter")
    for r in errors[(errors.method==METHODS[0]) & errors.quarter.between("2023Q1","2026Q2")].itertuples():
        q = r.quarter
        rev = float(panel.loc[q,"revenue_musd"])
        base = (2*float(panel.loc[shift(q,-1),"gbv_musd"])+float(panel.loc[shift(q,-2),"gbv_musd"]))/3
        lam_star, h_star = rev/base, r.value_mid/rev
        bhat, lhat, hhat = r.base_hat_musd,r.lambda_pct/100,1/r.cushion_divisor
        b,l,a = bhat-base,lhat-lam_star,hhat-h_star
        parts = dict(U=lam_star*h_star*b,C=base*h_star*l,P=lam_star*base*a,
                     UC=h_star*b*l,UP=lam_star*b*a,CP=base*l*a,UCP=b*l*a,
                     ROUND=r.error_interval_musd-r.error_raw_musd)
        raw_sum = sum(parts[x] for x in TERMS if x!="ROUND")
        fair_sum = sum(parts.values())
        if abs(raw_sum-r.error_raw_musd)>1e-8 or abs(fair_sum-r.error_interval_musd)>1e-8:
            raise ValueError("Exact attribution does not reconcile")
        ordered = [lhat*(bhat-base)*hhat,(lhat*base-rev)*hhat,rev*hhat-r.value_mid]
        rows.append(dict(quarter=q,n=1,actual_revenue_musd=rev,actual_base_musd=base,
            lambda_star=lam_star,divisor_star=rev/r.value_mid,b=b,l=l,a=a,**parts,
            raw_error=r.error_raw_musd,interval_error=r.error_interval_musd,
            raw_reconciliation_residual=raw_sum-r.error_raw_musd,
            interval_reconciliation_residual=fair_sum-r.error_interval_musd,
            ordered_upstream=ordered[0],ordered_conversion=ordered[1],ordered_policy=ordered[2],
            interpretation="expost accounting identity; interactions not unique causal shocks"))
    f = pd.DataFrame(rows)
    for win,quarters in matched.items():
        z = f[f.quarter.isin(quarters)]
        mse_sum=0.
        for x in TERMS:
            diag=float(np.mean(z[x]**2)); mean=float(np.mean(z[x])); mse_sum+=diag
            moment_rows.append(dict(window=win,n=len(z),term1=x,term2=x,
                mean_term1=mean,mean_term2=mean,raw_cross_moment=diag,
                contribution_to_mse=diag,population_covariance=diag-mean**2))
        for x,y in itertools.combinations(TERMS,2):
            cross=float(np.mean(z[x]*z[y]));mx=float(np.mean(z[x]));my=float(np.mean(z[y]));mse_sum+=2*cross
            moment_rows.append(dict(window=win,n=len(z),term1=x,term2=y,
                mean_term1=mx,mean_term2=my,raw_cross_moment=cross,
                contribution_to_mse=2*cross,population_covariance=cross-mx*my))
        actual=float(np.mean(z.interval_error**2))
        if abs(mse_sum-actual)>1e-7:
            raise ValueError("Covariance-aware MSE identity fails")
        identities.append(dict(window=win,n=len(z),interval_mse=actual,sum_second_moments_and_cross_terms=mse_sum,
            residual=mse_sum-actual,independence_assumed=False))
    return f,moment_rows,identities


def intervals(errors, predictions, src):
    bands, calibration = [], []
    guide_dates = src.guides.set_index("quarter").print_date.to_dict()
    for r in predictions[predictions.status=="forecast"].itertuples():
        origin_d = pd.Timestamp(r.origin_date).date()
        hist = errors[(errors.method==r.method) & (errors.quarter < r.quarter)].dropna(subset=["value_mid"]).copy()
        hist = hist.loc[hist.quarter.map(lambda q: guide_dates[q] < origin_d).astype(bool)].sort_values("quarter").tail(8)
        residuals = abs(hist.value_mid/hist.point_musd-1).to_numpy()
        m = len(hist);rank=math.ceil((m+1)*.8)
        halfwidth = float(np.sort(residuals)[rank-1]) if m>=6 and rank<=m else np.nan
        lo=max(0,r.point_musd*(1-halfwidth)) if np.isfinite(halfwidth) else np.nan
        hi=r.point_musd*(1+halfwidth) if np.isfinite(halfwidth) else np.nan
        current=errors[(errors.method==r.method)&(errors.quarter==r.quarter)]
        target=float(current.iloc[0].value_mid) if len(current) else np.nan
        valid = bool(np.isfinite(lo) and np.isfinite(target))
        bands.append(dict(quarter=r.quarter,method=r.method,n=1,origin_date=r.origin_date,
            point_musd=r.point_musd,calibration_n=m,rank=rank,
            calibration_quarters=";".join(hist.quarter),relative_halfwidth=halfwidth,
            lo_musd=lo,hi_musd=hi,width_musd=hi-lo,width_pct=100*(hi-lo)/r.point_musd,
            actual_mid_musd=target,raw_midpoint_covered=(lo<=target<=hi) if valid else None,
            target_interval_overlaps=(lo<=target+.5 and hi>=target-.5) if valid else None,
            target_interval_contained=(lo<=target-.5 and hi>=target+.5) if valid else None,
            status="band" if np.isfinite(lo) else "insufficient_chronological_errors",
            interpretation="descriptive historical band; no exchangeability/80pct guarantee"))
        for x,err in zip(hist.itertuples(),residuals):
            calibration.append(dict(quarter=r.quarter,method=r.method,input_quarter=x.quarter,
                target_guide_available_date=guide_dates[x.quarter],origin_date=origin_d,
                source_forecast_musd=x.point_musd,source_actual_guide_musd=x.value_mid,abs_raw_relative_error=err))
    b=pd.DataFrame(bands);coverage=[]
    for win in ("W1","W2"):
        for method in METHODS:
            w=window(b,win);r=w[(w.method==method)&(w.status=="band")].dropna(subset=["actual_mid_musd"])
            coverage.append(dict(window=win,method=method,n=len(r),maximum_point_n=len(w[w.method==method]),
                raw_midpoint_coverage=float(r.raw_midpoint_covered.astype(float).mean()) if len(r) else np.nan,
                interval_overlap_coverage=float(r.target_interval_overlaps.astype(float).mean()) if len(r) else np.nan,
                interval_containment_coverage=float(r.target_interval_contained.astype(float).mean()) if len(r) else np.nan,
                mean_width_musd=float(r.width_musd.mean()) if len(r) else np.nan,
                interpretation="descriptive only; no advertised calibrated probability"))
    return b,calibration,coverage


def evaluate_stage(out, forecast_dir, src):
    freeze=json.loads((forecast_dir/"forecast_freeze.json").read_text())
    for name, expected in freeze["files"].items():
        if sha((forecast_dir/name).read_bytes())!=expected:
            raise ValueError("Forecast freeze changed: "+name)
    if freeze["protocol_sha256"] != PROTOCOL_HASH:
        raise ValueError("Protocol mismatch in forecast freeze")
    p=pd.read_csv(forecast_dir/"predictions.csv")
    errors=errors_frame(p,src)
    scores,paired,deletions,slices,coverage,matched=score_tables(errors)
    contrib,moments,identities=contributions(errors,src,matched)
    bands,calibration,band_coverage=intervals(errors,p,src)
    score=pd.DataFrame(scores);delete=pd.DataFrame(deletions)
    checks=[]
    for win,minn in (("W1",8),("W2",6)):
        qset=matched[win]
        n=len(qset);seasons=len({q[-1] for q in qset});years=len({q[:4] for q in qset})
        coverage_ok=n>=minn and seasons==4 and years>=3
        rows=score[(score.window==win)&(score.scope=="all_three")&(score.basis=="interval")].set_index("method")
        for method in METHODS[1:]:
            a,b=rows.loc[METHODS[0]],rows.loc[method]
            dd=delete[(delete.window==win)&(delete.baseline==method)]
            checks.append(dict(window=win,baseline=method,n=n,seasons=seasons,years=years,coverage_ok=coverage_ok,
                rmse_candidate=a.rmse,rmse_baseline=b.rmse,rmse_ratio=a.rmse/b.rmse,
                mae_candidate=a.mae,mae_baseline=b.mae,
                rmse_lower=bool(a.rmse < b.rmse-1e-9),mae_no_worse=bool(a.mae <= b.mae+1e-9),
                all_year_deletions_lower=bool(len(dd) and dd.lower_mse.all() and (dd.remaining_years>=2).all())))
    if not all(x["coverage_ok"] for x in checks):
        verdict="INSUFFICIENT COVERAGE"
    elif not all(x["rmse_lower"] for x in checks):
        verdict="FAIL"
    elif not all(x["mae_no_worse"] and x["all_year_deletions_lower"] for x in checks):
        verdict="NUMERICAL IMPROVEMENT / STABILITY HURDLE FAIL"
    else:
        verdict="LOWER HISTORICAL MATCHED LOSS UNDER RECONSTRUCTED PROTOCOL"
    out.mkdir(parents=True)
    tables=dict(errors=errors,scores=scores,paired_errors=paired,year_deletion=deletions,
        year_season_slices=slices,coverage=coverage,contributions=contrib,
        contribution_cross_moments=moments,mse_reconciliation=identities,
        prediction_bands=bands,calibration_inputs=calibration,band_coverage=band_coverage,hurdle_checks=checks)
    for name, table in tables.items():
        write_csv(out/(name+".csv"),table)
    summary=dict(verdict=verdict,protocol_sha256=PROTOCOL_HASH,forecast_freeze_sha256=sha((forecast_dir/"forecast_freeze.json").read_bytes()),
        method_identity="quant-thesis-validation-v1__preannouncement_guide_diagnostic",
        W1_n=len(matched["W1"]),W2_n=len(matched["W2"]),candidate_system_n_params=5,
        B1_n_params=0,B2_common_statistic_n_params=1,upstream_gbv_fitted_parameters=0,
        promotion="none; separate production decision",trading_edge="not tested",registration="none; incompatible historical origin semantics",
        source_limitation="historical frozen-panel reconstruction; no unrevised original-vintage archive",
        uncertainty="descriptive chronology only; overlapping windows and few calendar-year blocks",
        minimum_coverage_floors="8 W1 / 6 W2; all seasons; at least3 years",checks=checks)
    write_json(out/"verdict.json",summary)
    write_json(out/"evaluation_receipt.json",dict(stage="outcomes loaded after forecast freeze",protocol_sha256=PROTOCOL_HASH,
        forecast_freeze_sha256=sha((forecast_dir/"forecast_freeze.json").read_bytes()),
        files={p.name:sha(p.read_bytes()) for p in sorted(out.iterdir()) if p.is_file()}))
    return summary


def run(out, stage="all", forecast_dir=None):
    if out.exists():
        raise FileExistsError("New immutable output directory required: "+str(out))
    src=load_sources()
    if stage=="forecast":
        forecast_stage(out,src)
        return dict(stage=stage,output=str(out))
    if stage=="evaluate":
        if forecast_dir is None:
            raise ValueError("--forecast-dir required for evaluation")
        return evaluate_stage(out,forecast_dir,src)
    out.mkdir(parents=True)
    forecast_stage(out/"forecast",src)
    result=evaluate_stage(out/"evaluation",out/"forecast",src)
    write_json(out/"attempt_ledger.json",dict(attempt="first preregistered empirical specification",specification_changes=0,
        protocol_sha256=PROTOCOL_HASH,stages=["write immutable forecast ledger", "hash and freeze", "join outcome targets", "evaluate locked tests"],
        verdict=result["verdict"]))
    return result


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out",required=True,type=Path)
    ap.add_argument("--stage",choices=("forecast","evaluate","all"),default="all")
    ap.add_argument("--forecast-dir",type=Path)
    args=ap.parse_args()
    print(json.dumps(jsonable(run(args.out.resolve(),args.stage,args.forecast_dir.resolve() if args.forecast_dir else None)),indent=2))
