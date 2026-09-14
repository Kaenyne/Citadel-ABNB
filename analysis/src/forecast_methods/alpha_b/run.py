"""B': reproducible FY term-structure feasibility and live scenarios; no source writes."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
from kernel_engine_v2 import engine as k0
from harness import REGISTRY_COLUMNS, load_calendar

OUT = ROOT / "data/processed/forecast_methods/alpha_b"
METHOD = "alpha-b"
OBJECT = "fy_gap_at_print"
INPUTS = [
    "data/processed/overnight/02_fy_guide_revisions.csv",
    "data/processed/overnight/02_guidance_ledger.csv",
    "data/processed/overnight/16_consensus_at_print_merged.csv",
    "data/processed/forecast_methods/L0/L0_vintage_register.csv",
    "data/processed/abnb_earnings_reactions.csv",
]


def stamped_consensus(register, period, as_of):
    """Latest admissible row per vendor. Date-only same-day observations excluded."""
    cutoff = pd.Timestamp(as_of).normalize()
    r = register.copy()
    r["stamp"] = pd.to_datetime(r.as_of_timestamp, errors="coerce", utc=True).dt.tz_localize(None).dt.normalize()
    r = r[(r.period == period) & (r.metric == "revenue") & (r.unit == "musd")
          & r.pit_usable.eq(True) & r.vendor_attributed.eq(True) & r.vendor.notna()
          & r.stamp.notna() & r.stamp.lt(cutoff) & pd.to_numeric(r.value, errors="coerce").gt(0)]
    r = r.sort_values(["stamp", "register_id"]).drop_duplicates("vendor", keep="last")
    r["age_days"] = (cutoff - r.stamp).dt.days
    r["stale_over_30_days"] = r.age_days.gt(30)
    return r


def annual_sum(values, year):
    keys = [f"{year}Q{s}" for s in range(1, 5)]
    if any(q not in values or not np.isfinite(values[q]) for q in keys):
        return np.nan
    return float(sum(values[q] for q in keys))


def historical_dates(calendar):
    # The calendar row names the quarter reporting at the event; windows name the successor guide target.
    return (calendar[calendar.next_quarter_guided.between("2023Q1", "2026Q2")]
            [["next_quarter_guided", "guide_date"]].rename(columns={"next_quarter_guided": "fiscal_quarter"}))


def revision_metrics(frame):
    """Missing target/denominator never becomes a correct no-revision prediction."""
    d = frame.replace([np.inf, -np.inf], np.nan).dropna(subset=["gap_pct", "revision_pct"])
    d = d[d.gap_pct.abs().gt(0.5)]
    n = len(d)
    hits = int((np.sign(d.gap_pct) == np.sign(d.revision_pct)).sum())
    rate = hits / n if n else None
    z = 1.959963984540054
    if n:
        c = (rate + z*z/(2*n)) / (1+z*z/n)
        h = z*np.sqrt(rate*(1-rate)/n + z*z/(4*n*n)) / (1+z*z/n)
        low, high = float(c-h), float(c+h)
    else:
        low = high = None
    corr = float(pearsonr(d.gap_pct, d.revision_pct).statistic) if n >= 3 and d.gap_pct.nunique() > 1 and d.revision_pct.nunique() > 1 else None
    return dict(n=n, hits=hits, hit_rate=rate, wilson_low=low, wilson_high=high,
                correlation=corr, pass_line_met=bool(n and corr is not None and rate >= .7 and corr > .4))


def historical_audit(register, fy, dates, panel_full):
    rows = []
    guides = fy[fy.metric.eq("revenue_yoy_pct")].copy()
    guides["date"] = pd.to_datetime(guides.print_date)
    for e in dates.itertuples(index=False):
        origin, target = str(e.guide_date)[:10], e.fiscal_quarter
        year = int(target[:4])
        p = k0._panel(origin)
        try:
            term = k0.term_structure(origin)
            values = dict(zip(p.quarter, p.revenue_musd))
            values.update({r.quarter: r.point for r in term.itertuples() if r.status != "unavailable"})
            # Only quarters beyond the requested two-quarter kernel may use a seasonal naive.
            second = str(pd.Period(p.quarter.max(), freq="Q") + 2)
            for q in [f"{year}Q{s}" for s in range(1, 5)]:
                if q > second and q not in values:
                    prior = str(pd.Period(q, freq="Q") - 4)
                    if prior in values:
                        values[q] = values[prior]
            prediction = annual_sum(values, year)
            missing = [f"{year}Q{s}" for s in range(1, 5) if not np.isfinite(values.get(f"{year}Q{s}", np.nan))]
        except (k0.DataUnavailable, k0.PointInTimeError) as exc:
            prediction, missing = np.nan, [str(exc)]
        cons = stamped_consensus(register, f"FY{year}", origin)
        g = guides[(guides.target_period == f"FY{year}") & guides.date.lt(pd.Timestamp(origin))]
        current = g.iloc[-1] if len(g) else None
        future = guides[(guides.target_period == f"FY{year}") & guides.date.gt(pd.Timestamp(origin))]
        nxt = future.iloc[0] if len(future) else None
        actual = annual_sum(dict(zip(panel_full.quarter, panel_full.revenue_musd)), year)
        # Growth-language bucket changes are descriptive only: no invented dollar midpoint.
        rows.append(dict(target_quarter=target, origin=origin, year=year,
                         kernel_fy_musd=prediction, missing_forecast_quarters="|".join(missing),
                         fy_consensus_vendors_n=len(cons), guide_bucket_available=current is not None,
                         guide_bucket_pct=float(current.value_mid) if current is not None else np.nan,
                         guide_bucket_date=current.print_date if current is not None else "",
                         next_bucket_revision_pct=float(nxt.value_mid-current.value_mid) if current is not None and nxt is not None else np.nan,
                         actual_fy_musd=actual, actual_fy_rounding_halfwidth_musd=2.0 if np.isfinite(actual) else np.nan,
                         gap_pct=np.nan, revision_pct=np.nan,
                         reason="No complete PIT FY kernel; no numeric FY revenue midpoint or stamped FY comparator",
                         no_revision_prediction_pct=0.0, last_revision_prediction_pct=np.nan,
                         seasonal_kernel_parameters=4, live_ledger_coefficients=2,
                         latest_kpi_date=str(p.print_date.max().date())))
    return pd.DataFrame(rows)


def run(as_of):
    started = time.perf_counter()
    OUT.mkdir(parents=True, exist_ok=True)
    reg = pd.read_csv(ROOT / INPUTS[3], comment="#")
    fy = pd.read_csv(ROOT / INPUTS[0])
    returns = pd.read_csv(ROOT / INPUTS[4])
    cal = load_calendar()
    dates = historical_dates(cal)
    panel = k0._panel(as_of)
    audit = historical_audit(reg, fy, dates, panel)
    audit.to_csv(OUT / "historical_origin_audit.csv", index=False)
    metrics = []
    for window, minimum in [("W1", "2023Q1"), ("W2", "2024Q1")]:
        d = audit[audit.target_quarter.ge(minimum)]
        m = revision_metrics(d)
        m.update(window=window, origins_n=len(d), full_fy_forecast_n=int(d.kernel_fy_musd.notna().sum()),
                 stamped_fy_comparator_dates_n=int(d.fy_consensus_vendors_n.gt(0).sum()),
                 return_20d_n=0, return_60d_n=0, baseline_no_revision_score_n=0,
                 baseline_last_revision_score_n=0, actual_fy_comparison_n=int((d.kernel_fy_musd.notna() & d.actual_fy_musd.notna()).sum()))
        metrics.append(m)
    pd.DataFrame(metrics).to_csv(OUT / "window_metrics.csv", index=False)

    live = k0.term_structure(as_of)
    live.to_csv(OUT / "live_term_structure.csv", index=False)
    # K0 owns coefficient fitting and ledger scenario assumptions; B only exposes a fixed-coefficient weight sensitivity.
    nowcasts = k0._ledger_nowcasts(panel, as_of)
    gbv = dict(zip(panel.quarter, panel.gbv_musd))
    gbv.update({q: v["point"] for q, v in nowcasts.items()})
    sensitivity = []
    for q in ["2026Q4", "2027Q1"]:
        lam = k0.pit_lambda(int(q[-1]), as_of)
        for weight in [.33, 2/3]:
            base = weight*gbv[str(pd.Period(q, freq="Q")-1)] + (1-weight)*gbv[str(pd.Period(q, freq="Q")-2)]
            sensitivity.append(dict(quarter=q, as_of=as_of, weight=weight, lambda_pct=lam["lambda_pct"],
                                    revenue_musd=base*lam["lambda_pct"]/100, n_train=lam["n_train"],
                                    sensitivity_type="fixed K0 lambda arithmetic; not refitted; not confidence bounds"))
    band = pd.DataFrame(sensitivity)
    band.to_csv(OUT / "weight_sensitivity.csv", index=False)
    live_values = dict(zip(panel.quarter, panel.revenue_musd))
    live_values.update(dict(zip(live.quarter, live.point)))
    fy26 = annual_sum(live_values, 2026)
    comparisons = []
    for period in ["2026Q4", "2027Q1", "FY2026"]:
        cs = stamped_consensus(reg, period, as_of)
        model = fy26 if period == "FY2026" else float(live.loc[live.quarter.eq(period), "point"].iloc[0])
        if cs.empty:
            comparisons.append(dict(period=period, kernel_musd=model, vendor="unavailable", as_of_timestamp="",
                                    consensus_musd=np.nan, gap_pct=np.nan, n_consensus=0, stale_over_30_days=None))
        for c in cs.itertuples():
            comparisons.append(dict(period=period, kernel_musd=model, vendor=c.vendor, as_of_timestamp=c.as_of_timestamp,
                                    register_id=c.register_id, consensus_musd=c.value, gap_pct=100*(model/c.value-1),
                                    n_consensus=1, age_days=c.age_days, stale_over_30_days=c.stale_over_30_days))
    pd.DataFrame(comparisons).to_csv(OUT / "stamped_live_comparisons.csv", index=False)

    # The frozen harness has no FY period or FY-gap target and no 12-Sep origin.
    # Keep a schema-correct empty candidate in our package; never mislabel the annual gap as quarterly revenue.
    candidate = pd.DataFrame(columns=REGISTRY_COLUMNS)
    candidate.to_csv(OUT / "alpha-b__fy_gap_at_print.registry_pending.csv", index=False)
    registry_status = dict(method=METHOD, object=OBJECT, submitted_rows=0, reason="No eligible historical cells; FY-gap target and 2026-09-12 origin absent from FORMAT 1.0",
                           required_change="Add annual revenue/FY-gap target and new allowable date without reinterpreting a quarterly target")
    (OUT / "registry_status.json").write_text(json.dumps(registry_status, indent=2)+"\n", encoding="utf-8")
    summary = dict(verdict="underpowered", as_of=as_of, windows=metrics, fy2026_kernel_musd=fy26,
                   open_return_columns=[c for c in returns if c.startswith("open_")],
                   current_q1_2027_consensus_n=int(len(stamped_consensus(reg, "2027Q1", as_of))),
                   conditional_not_validated=True, runtime_seconds=round(time.perf_counter()-started, 3))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    (OUT / "input_hashes.json").write_text(json.dumps({p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in INPUTS}, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, allow_nan=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", default="2026-09-12")
    run(parser.parse_args().as_of)
