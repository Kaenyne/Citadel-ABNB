"""Reconstruct frozen earnings-event price legs and explicitly labelled guide proxies."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[5]
SEED = 20260915
PERMUTATIONS = 19999
PATHS = {
    "calendar": "data/processed/forecast_methods/harness/calendar.csv",
    "ohlc": "data/processed/forecast_methods/returns_v1/ohlc_daily.csv",
    "published_returns": "data/processed/forecast_methods/returns_v1/earnings_reactions_open_v1.csv",
    "register": "data/processed/forecast_methods/L0/L0_vintage_register.csv",
    "kpi": "data/processed/overnight/02_kpi_panel_quarterly.csv",
    "guides": "data/processed/overnight/02_guidance_ledger.csv",
    "forecasts": "data/processed/forecast_methods/gbv_event_v1/forecast_v1/results_v1/pre_event_forecasts.csv",
}
PRIMARY_SIGNALS = ["published_guide_vs_revenue_consensus_pct", "published_guide_vs_implied_guide_pct"]
PRIMARY_OUTCOMES = ["gap_excess_pct", "session_excess_pct"]
SECONDARY_OUTCOMES = ["cc_excess_pct", "open_5d_excess_pct", "open_20d_excess_pct"]


def canonical_quarter(value):
    if pd.isna(value) or not str(value).strip():
        return None
    value = str(value)
    return value if value[:4].isdigit() else "20" + value[-2:] + "Q" + value[0]


def truth(value):
    return str(value).lower() == "true"


def named_vendor(value):
    if pd.isna(value):
        return False
    v = str(value).strip().lower()
    return bool(v) and not any(x in v for x in ("unattributed", "unknown", "not_recorded", "not recorded"))


def observation_before_close(raw, event_date):
    """Date-only legacy stamps use the certified convention; timed stamps retain their instant."""
    if pd.isna(raw):
        return False, "missing_timestamp"
    stamp=str(raw).strip()
    event_day=pd.Timestamp(event_date).normalize()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}",stamp):
        day=pd.Timestamp(stamp)
        return day<=event_day, "date_only_morning_convention" if day==event_day else "prior_date_only"
    try:
        instant=pd.Timestamp(stamp)
    except ValueError:
        return False,"invalid_timestamp"
    if instant.tzinfo is None:
        return False,"ambiguous_naive_timestamp"
    close=pd.Timestamp(event_day.date().isoformat()+" 16:00",tz="America/New_York")
    return instant<close,"explicit_before_preclose" if instant<close else "explicit_at_or_after_preclose"


def select_primary(register, quarter, role, cutoff):
    """Original identified PG/AP row only; no vendor=None or mirror fallback."""
    prefix = "PG" if role == "pre_guide" else "AP"
    q = register.loc[register.register_id.eq(f"{prefix}-{quarter}-revenue") & register.role.eq(role)]
    if len(q) != 1:
        return None, "missing_original_row" if q.empty else "duplicate_original_row"
    r = q.iloc[0]
    if not truth(r.pit_usable) or not truth(r.vendor_attributed) or not named_vendor(r.vendor):
        return None, "quarantined_or_unattributed"
    if not np.isfinite(r.value) or r.value <= 0 or pd.isna(r.as_of):
        return None, "missing_value_or_timestamp"
    admitted,basis=observation_before_close(r.as_of_timestamp,cutoff)
    if not admitted:
        return None, "future_or_ambiguous_consensus:"+basis
    return r, "eligible_original:"+basis


def select_dolthub(register, quarter, cutoff):
    q = register.loc[register.period.eq(quarter) & register.metric.eq("revenue")
                     & register.vendor.eq("DoltHub post-no-preference/earnings")
                     & register.role.eq("pit_history")
                     & register.pit_usable.map(truth) & (register.as_of < pd.Timestamp(cutoff))
                     & register.value.gt(0)].sort_values(["as_of", "register_id"])
    return None if q.empty else q.iloc[-1]


def price_legs(prices, event_date):
    d = pd.Timestamp(event_date)
    out = {}
    for ticker in ("ABNB", "QQQ"):
        px = prices.loc[prices.ticker.eq(ticker)].sort_values("date").set_index("date")
        i = int(px.index.searchsorted(d, side="right"))
        if i == 0 or i >= len(px):
            raise ValueError(f"missing preclose/entry: {ticker} {event_date}")
        entry, predate = px.index[i], px.index[i - 1]
        if ticker == "QQQ" and (entry != out["entry_date"] or predate != out["preclose_date"]):
            raise ValueError("benchmark trading dates do not match")
        pre, op, cl = [float(v) for v in (px.close.iloc[i-1], px.open.iloc[i], px.close.iloc[i])]
        if min(pre, op, cl) <= 0:
            raise ValueError("nonpositive price")
        t = ticker.lower()
        out.update(entry_date=entry, preclose_date=predate)
        out.update({f"{t}_preclose": pre, f"{t}_open": op, f"{t}_close": cl,
                    f"{t}_high": float(px.high.iloc[i]), f"{t}_low": float(px.low.iloc[i]),
                    f"{t}_gap_pct": 100*(op/pre-1), f"{t}_session_pct": 100*(cl/op-1),
                    f"{t}_cc_pct": 100*(cl/pre-1)})
        for h in (5, 20):
            out[f"{t}_open_{h}d_pct"] = 100*(float(px.close.iloc[i+h-1])/op-1) if i+h-1 < len(px) else np.nan
    for leg in ("gap", "session", "cc", "open_5d", "open_20d"):
        out[f"{leg}_excess_pct"] = out[f"abnb_{leg}_pct"]-out[f"qqq_{leg}_pct"]
    out["cross_term_excess_pp"] = (out["abnb_gap_pct"]*out["abnb_session_pct"]
                                    -out["qqq_gap_pct"]*out["qqq_session_pct"])/100
    out["compounding_identity_error_pp"] = out["cc_excess_pct"]-(out["gap_excess_pct"]
        +out["session_excess_pct"]+out["cross_term_excess_pp"])
    return out


def guide_surprises(guide, revenue_consensus, cushion):
    if not np.isfinite(guide) or not np.isfinite(revenue_consensus) or revenue_consensus <= 0:
        return np.nan, np.nan, np.nan
    raw = 100*(guide/revenue_consensus-1)
    if not np.isfinite(cushion) or cushion <= -1:
        return raw, np.nan, np.nan
    implied = revenue_consensus/(1+cushion)
    return raw, 100*(guide/implied-1), implied


def preevent_cushion(history, cutoff):
    eligible = history.loc[(history.actual_publication < pd.Timestamp(cutoff)) & history.actual.gt(0)
                           & history.guide_mid.gt(0)].sort_values("actual_publication").tail(8)
    value = float(np.median(eligible.actual/eligible.guide_mid-1)) if len(eligible) >= 3 else np.nan
    return value, eligible


def fit_slope(x, y, control=None):
    x, y = np.asarray(x, float), np.asarray(y, float)
    X = np.column_stack([np.ones(len(x)), x] + ([] if control is None else [np.asarray(control, float)]))
    n, k = X.shape
    if n <= k+1 or np.linalg.matrix_rank(X) < k or np.std(x) == 0 or np.std(y) == 0:
        return {"n": n, "slope": np.nan, "status": "insufficient_or_degenerate"}
    bread = np.linalg.inv(X.T@X)
    beta = bread@X.T@y
    residual = y-X@beta
    cov = (n/(n-k))*bread@(X.T@(X*residual[:, None]**2))@bread
    se = math.sqrt(max(float(cov[1, 1]), 0))
    critical = stats.t.ppf(.975, n-k)
    return {"n": n, "intercept": float(beta[0]), "slope": float(beta[1]), "slope_hc1_se": se,
            "slope_95_lo": float(beta[1]-critical*se), "slope_95_hi": float(beta[1]+critical*se),
            "slope_hc1_t": float(beta[1]/se) if se else np.nan,
            "slope_hc1_p": float(2*stats.t.sf(abs(beta[1]/se), n-k)) if se else np.nan,
            "r2": float(1-np.sum(residual**2)/np.sum((y-y.mean())**2)), "n_parameters": k,
            "status": "descriptive_approximate_HC1_interval"}


def association(frame, signal, outcome, permutation=False):
    d = frame.dropna(subset=[signal, outcome])
    x, y = d[signal].to_numpy(float), d[outcome].to_numpy(float)
    result = fit_slope(x, y)
    if len(x) < 4 or np.std(x) == 0 or np.std(y) == 0:
        return result
    pearson = float(stats.pearsonr(x, y).statistic)
    spearman = stats.spearmanr(x, y)
    z = np.arctanh(np.clip(pearson, -.999999999, .999999999))
    width = stats.norm.ppf(.975)/math.sqrt(len(x)-3)
    result.update(pearson=pearson, pearson_95_lo=float(np.tanh(z-width)), pearson_95_hi=float(np.tanh(z+width)),
                  spearman=float(spearman.statistic), spearman_asymptotic_p=float(spearman.pvalue))
    if permutation:
        rng = np.random.default_rng(SEED)
        xc, yc = x-x.mean(), y-y.mean()
        denom = np.linalg.norm(xc)*np.linalg.norm(yc)
        greater = sum(abs(float(np.dot(xc, rng.permutation(yc))/denom)) >= abs(pearson)-1e-14
                      for _ in range(PERMUTATIONS))
        result["pearson_permutation_p"] = (greater+1)/(PERMUTATIONS+1)
    return result


def holm(pvalues):
    p = np.asarray(pvalues, float)
    order = np.argsort(p)
    adjusted = np.empty(len(p))
    running = 0.
    for i, j in enumerate(order):
        running = max(running, (len(p)-i)*p[j])
        adjusted[j] = min(1., running)
    return adjusted


def window_slice(frame, window):
    if window == "all":
        return frame
    return frame.loc[frame.print_quarter.ge("2023Q1" if window == "W1_print_2023plus" else "2024Q1")]


def build_tables(root):
    src = {k: pd.read_csv(root/v, comment="#") for k, v in PATHS.items()}
    cal, prices, reg, kpi, guides = [src[k] for k in ("calendar", "ohlc", "register", "kpi", "guides")]
    prices["date"] = pd.to_datetime(prices.date)
    reg["as_of"] = pd.to_datetime(reg.as_of_timestamp, format="mixed", errors="coerce", utc=True).dt.tz_convert(None).dt.normalize()
    reg["value"] = pd.to_numeric(reg.value, errors="coerce")
    kpi = kpi[["quarter", "revenue_musd"]].copy()
    kpi["q"] = kpi.quarter.map(canonical_quarter)
    kpi = kpi.set_index("q")
    cal["print_date"] = pd.to_datetime(cal.print_date)
    history = []
    for r in cal.itertuples():
        q = r.next_quarter_guided
        actual_cal = cal.loc[cal.print_quarter.eq(q) & ~cal.is_forecast_row.map(truth)]
        if pd.notna(q) and pd.notna(r.guide_mid) and q in kpi.index and len(actual_cal) == 1:
            history.append({"quarter": q, "guide_mid": float(r.guide_mid), "actual": float(kpi.loc[q, "revenue_musd"]),
                            "actual_publication": actual_cal.print_date.iloc[0]})
    hist = pd.DataFrame(history)
    events, cushion_rows, guide_checks = [], [], []
    for r in cal.loc[cal.print_date_basis.eq("ledger") & ~cal.is_forecast_row.map(truth)].itertuples():
        d, q = r.print_date, r.next_quarter_guided
        row = {"event_date": d, "event_year": d.year, "print_quarter": r.print_quarter, "guided_quarter": q,
               "first_guide_mid_musd": r.guide_mid, "guide_low_musd": r.guide_lo, "guide_high_musd": r.guide_hi,
               "signal_known_before_release": False, "intraday_call_leg_available": False,
               "candle_order_available": False, "expectations_type": "realized_revenue_consensus_not_observed_guide_expectations"}
        row.update(price_legs(prices, d))
        cushion, training = preevent_cushion(hist, d)
        row.update(preevent_cushion=cushion, cushion_n=len(training),
                   cushion_quarters=";".join(training.quarter), cushion_latest_actual_publication=training.actual_publication.max())
        for t in training.itertuples():
            cushion_rows.append({"event_date": d, "print_quarter": r.print_quarter, **t._asdict()})
        if pd.notna(r.guide_mid):
            gg = guides.loc[guides.print_quarter.map(canonical_quarter).eq(r.print_quarter)
                            & guides.target_period.map(canonical_quarter).eq(q) & guides.horizon_quarters.eq(1)
                            & guides.metric.eq("revenue_usd_m") & guides.guide_type.eq("range")]
            if len(gg) != 1 or not np.isclose(float(gg.value_mid.iloc[0]), r.guide_mid):
                raise ValueError(f"guide ledger mismatch {r.print_quarter}: {len(gg)}")
            guide_checks.append({"print_quarter":r.print_quarter,"guided_quarter":q,"guide_mid_musd":r.guide_mid,
                                 "guide_id":gg.guide_id.iloc[0],"guide_source":gg.source_file.iloc[0],"matches":True})
            row.update(guide_id=gg.guide_id.iloc[0], guide_source=gg.source_file.iloc[0])
        cs, status = select_primary(reg, q, "pre_guide", d)
        row["primary_eligibility"] = status if pd.notna(r.guide_mid) else "no_numeric_forward_guide"
        row.update(consensus_revenue_musd=float(cs.value) if cs is not None else np.nan,
                   consensus_vendor=cs.vendor if cs is not None else None,
                   consensus_as_of=cs.as_of if cs is not None else pd.NaT,
                   consensus_as_of_raw=cs.as_of_timestamp if cs is not None else None,
                   consensus_register_id=cs.register_id if cs is not None else None)
        a,b,c = guide_surprises(r.guide_mid, row["consensus_revenue_musd"], cushion)
        row.update(published_guide_vs_revenue_consensus_pct=a, published_guide_vs_implied_guide_pct=b,
                   preevent_implied_guide_musd=c)
        dh = select_dolthub(reg, q, d)
        da,db,dc = guide_surprises(r.guide_mid, float(dh.value) if dh is not None else np.nan, cushion)
        row.update(dolthub_consensus_musd=float(dh.value) if dh is not None else np.nan,
                   dolthub_as_of=dh.as_of if dh is not None else pd.NaT,
                   dolthub_register_id=dh.register_id if dh is not None else None,
                   dolthub_guide_vs_revenue_pct=da, dolthub_guide_vs_implied_pct=db,
                   dolthub_implied_guide_musd=dc)
        ap, apstatus = select_primary(reg, r.print_quarter, "at_print", d)
        actual = float(kpi.loc[r.print_quarter,"revenue_musd"])
        row.update(current_revenue_actual_musd=actual, current_consensus_status=apstatus,
                   current_revenue_consensus_musd=float(ap.value) if ap is not None else np.nan,
                   current_consensus_vendor=ap.vendor if ap is not None else None,
                   current_consensus_as_of=ap.as_of if ap is not None else pd.NaT,
                   current_consensus_as_of_raw=ap.as_of_timestamp if ap is not None else None,
                   current_revenue_surprise_pct=100*(actual/float(ap.value)-1) if ap is not None else np.nan)
        events.append(row)
    return pd.DataFrame(events), pd.DataFrame(cushion_rows), pd.DataFrame(guide_checks), src


def analyze(events):
    rows, influence, groups, controls, sensitivity = [], [], [], [], []
    for window in ("all", "W1_print_2023plus", "W2_print_2024plus"):
        f = window_slice(events, window)
        for signal in PRIMARY_SIGNALS:
            for outcome in PRIMARY_OUTCOMES+SECONDARY_OUTCOMES:
                primary = outcome in PRIMARY_OUTCOMES
                d = f.dropna(subset=[signal, outcome])
                meta = {"window":window,"signal":signal,"outcome":outcome,"primary_family":primary,
                        "eligible_event_ids":";".join(d.print_quarter)}
                result = association(d, signal, outcome, permutation=primary)
                rows.append({**meta, **result})
                for sign, condition in (("negative", d[signal]<0), ("zero", d[signal].eq(0)), ("positive",d[signal]>0)):
                    g = d.loc[condition]
                    groups.append({**meta,"signal_sign":sign,"n":len(g),"mean_return_pct":g[outcome].mean(),
                                   "median_return_pct":g[outcome].median(),"n_positive_returns":int(g[outcome].gt(0).sum()),
                                   "min_return_pct":g[outcome].min(),"max_return_pct":g[outcome].max()})
                if primary:
                    for omission, values in (("event", list(d.print_quarter.unique())),("year",list(d.event_year.unique()))):
                        for value in values:
                            remain = d.loc[d["print_quarter" if omission=="event" else "event_year"].ne(value)]
                            influence.append({**meta,"omission_type":omission,"omitted":str(value),
                                              **association(remain,signal,outcome)})
                    ctl = d.dropna(subset=["current_revenue_surprise_pct"])
                    if len(ctl)>=8:
                        controls.append({**meta,"model":"same_rows_uncontrolled",**fit_slope(ctl[signal],ctl[outcome])})
                        controls.append({**meta,"model":"plus_current_revenue_surprise",**fit_slope(ctl[signal],ctl[outcome],ctl.current_revenue_surprise_pct)})
            # Uniform DoltHub sensitivity, never fill missing primary observations.
        for signal in ("dolthub_guide_vs_revenue_pct","dolthub_guide_vs_implied_pct"):
            for outcome in PRIMARY_OUTCOMES:
                sensitivity.append({"window":window,"signal":signal,"outcome":outcome,"basis":"separate_DoltHub_mirror_panel",
                                    **association(f,signal,outcome)})
    result = pd.DataFrame(rows)
    mask = result.primary_family & result.pearson_permutation_p.notna()
    result.loc[mask,"holm_12_primary_p"] = holm(result.loc[mask,"pearson_permutation_p"])
    result.loc[mask,"holm_family_n"] = int(mask.sum())
    return {"associations":result,"influence":pd.DataFrame(influence),"sign_groups":pd.DataFrame(groups),
            "current_print_control":pd.DataFrame(controls),"vendor_sensitivity":pd.DataFrame(sensitivity)}


def forecast_join(events, forecasts, register, prices):
    """Preserve abstentions and unmatched/live rows; never use event consensus at early origin."""
    forecasts=forecasts.loc[forecasts.method.eq("candidate_k0_gbv")].copy()
    by_target={r.guided_quarter:r for r in events.itertuples() if pd.notna(r.guided_quarter)}
    records=[]
    for f in forecasts.itertuples():
        origin=pd.Timestamp(f.origin_date)
        consensus=select_dolthub(register,f.quarter,origin)
        e=by_target.get(f.quarter)
        row={"target_quarter":f.quarter,"origin_date":origin,"origin_close_utc":f.origin_close_utc,
             "candidate_status":f.status,"candidate_reason":f.reason,"candidate_guide_musd":f.point_musd,
             "candidate_revenue_musd":f.revenue_point_musd,"origin_cushion_divisor":f.cushion_divisor,
             "origin_consensus_musd":float(consensus.value) if consensus is not None else np.nan,
             "origin_consensus_as_of":consensus.as_of if consensus is not None else pd.NaT,
             "origin_consensus_register_id":consensus.register_id if consensus is not None else None,
             "origin_consensus_vendor":"DoltHub post-no-preference/earnings" if consensus is not None else None,
             "information_status":"reconstructed_pre_event_signal_not_archived_forecast",
             "event_available":e is not None}
        row["origin_implied_guide_musd"]=row["origin_consensus_musd"]/f.cushion_divisor
        row["predicted_proxy_vs_origin_implied_guide_pct"]=100*(f.point_musd/row["origin_implied_guide_musd"]-1)
        row["predicted_proxy_vs_origin_revenue_pct"]=100*(f.point_musd/row["origin_consensus_musd"]-1)
        if e is not None:
            if origin>=e.event_date:
                raise ValueError("forecast origin not before the event")
            row.update(event_date=e.event_date,print_quarter=e.print_quarter,actual_guide_musd=e.first_guide_mid_musd,
                       lead_days=int((e.event_date-origin).days),
                       realized_proxy_at_origin_convention_pct=100*(e.first_guide_mid_musd/row["origin_implied_guide_musd"]-1))
            for outcome in PRIMARY_OUTCOMES+SECONDARY_OUTCOMES:
                row[outcome]=getattr(e,outcome)
            # A position formed at the reconstructed early close also bears the intervening return.
            for ticker in ("ABNB","QQQ"):
                px=prices.loc[prices.ticker.eq(ticker)].set_index("date")
                if origin not in px.index:
                    raise ValueError("early forecast origin is not a held trading session")
                close=float(px.loc[origin,"close"])
                row[f"{ticker.lower()}_origin_close"]=close
                row[f"{ticker.lower()}_origin_to_nextopen_pct"]=100*(getattr(e,f"{ticker.lower()}_open")/close-1)
                row[f"{ticker.lower()}_origin_to_nextclose_pct"]=100*(getattr(e,f"{ticker.lower()}_close")/close-1)
            for endpoint in ("nextopen","nextclose"):
                row[f"origin_to_{endpoint}_excess_pct"]=(row[f"abnb_origin_to_{endpoint}_pct"]-row[f"qqq_origin_to_{endpoint}_pct"])
        records.append(row)
    panel=pd.DataFrame(records)
    summaries=[]
    forecast_influence=[]
    for window,lower,upper in (("all",None,None),("W1_guide_target_2023plus","2023Q1",None),
                              ("W2_guide_target_2024plus","2024Q1",None),
                              ("W1_frozen_target_through2026Q2","2023Q1","2026Q2"),
                              ("W2_frozen_target_through2026Q2","2024Q1","2026Q2")):
        sample=panel if lower is None else panel.loc[panel.target_quarter.ge(lower)]
        if upper is not None:
            sample=sample.loc[sample.target_quarter.le(upper)]
        for signal in ("predicted_proxy_vs_origin_implied_guide_pct","predicted_proxy_vs_origin_revenue_pct"):
            for outcome in PRIMARY_OUTCOMES+["origin_to_nextopen_excess_pct","origin_to_nextclose_excess_pct"]:
                summaries.append({"window":window,"signal":signal,"outcome":outcome,
                                  "interpretation":"secondary_reconstructed_signal; no_strategy_promotion",**association(sample,signal,outcome)})
                available=sample.dropna(subset=[signal,outcome]).copy()
                available["event_year"]=pd.to_datetime(available.event_date).dt.year
                for omission,column in (("event","target_quarter"),("year","event_year")):
                    for value in available[column].unique():
                        remain=available.loc[available[column].ne(value)]
                        forecast_influence.append({"window":window,"signal":signal,"outcome":outcome,
                                                   "omission_type":omission,"omitted":str(value),
                                                   **association(remain,signal,outcome)})
    return {"pre_event_forecast_join":panel,"pre_event_signal_associations":pd.DataFrame(summaries),
            "pre_event_signal_influence":pd.DataFrame(forecast_influence)}


def serializable(value):
    if isinstance(value, dict): return {k:serializable(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)): return [serializable(v) for v in value]
    if isinstance(value, (np.integer,)): return int(value)
    if isinstance(value, (np.floating,float)): return float(value) if np.isfinite(value) else None
    if isinstance(value, (pd.Timestamp,)): return value.isoformat() if pd.notna(value) else None
    if value is pd.NaT: return None
    if isinstance(value,(np.bool_,)): return bool(value)
    return value


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    output=Path(args.out).resolve()
    allowed=(ROOT/"data/processed/forecast_methods/gbv_event_v1").resolve()
    if not output.is_relative_to(allowed) or output==allowed:
        raise ValueError("output must be a new child of gbv_event_v1")
    output.mkdir(parents=True,exist_ok=False)
    events,cushions,guide_checks,src=build_tables(ROOT)
    tables={"event_panel":events,"cushion_training":cushions,"guide_tieout":guide_checks,**analyze(events),
            **forecast_join(events,src["forecasts"],src["register"],src["ohlc"])}
    published=src["published_returns"].set_index("print_quarter")
    checks=[]
    for r in events.itertuples():
        for new,old in (("gap_excess_pct",None),("session_excess_pct","excess_open_1d_pct"),
                        ("cc_excess_pct","excess_cc_1d_pct"),("open_5d_excess_pct","excess_open_5d_pct"),
                        ("open_20d_excess_pct","excess_open_20d_pct")):
            expected=(published.loc[r.print_quarter,"gap_pct"]-published.loc[r.print_quarter,"qqq_gap_pct"] if old is None
                      else published.loc[r.print_quarter,old])
            delta=float(getattr(r,new)-expected)
            checks.append({"event":r.print_quarter,"metric":new,"difference_pp":delta,"pass":abs(delta)<1e-9})
    tables["return_tieout"]=pd.DataFrame(checks)
    if not all(x["pass"] for x in checks) or events.compounding_identity_error_pp.abs().max()>1e-9:
        raise ValueError("return arithmetic or frozen return tieout failed")
    for name,table in tables.items():
        table.to_csv(output/f"{name}.csv",index=False,float_format="%.15g")
    (output/"chart_data.json").write_text(json.dumps(serializable({k:v.to_dict("records") for k,v in tables.items()
        if k in ("event_panel","associations","sign_groups","vendor_sensitivity")}),indent=2,allow_nan=False),encoding="utf-8")
    receipt={"status":"completed_descriptive_audit_no_strategy_promotion","event_n":len(events),
        "numeric_guide_n":int(events.first_guide_mid_musd.notna().sum()),
        "primary_proxy_n":int(events[PRIMARY_SIGNALS[0]].notna().sum()),
        "adjusted_proxy_n":int(events[PRIMARY_SIGNALS[1]].notna().sum()),
        "primary_family_n":int(tables["associations"].primary_family.sum()),"permutations":PERMUTATIONS,"seed":SEED,
        "return_tieout_n":len(checks),"max_compounding_error_pp":float(events.compounding_identity_error_pp.abs().max()),
        "known_before_release":False,"actual_guide_expectations_available":False,
        "source_hashes":{v:hashlib.sha256((ROOT/v).read_bytes()).hexdigest() for v in PATHS.values()},
        "outputs":{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file()},
        "limits":["Historical events previously examined; not fresh confirmation", "Same-day consensus follows recorded morning convention",
                  "Cushion prior actual publications strictly before event", "Different-object and hypothetical expectation proxies",
                  "No timestamped intraday prices or causal call-leg attribution", "Small nested samples; approximate intervals and exchangeability assumption",
                  "No pre-event strategy or cost-adjusted performance inferred from published guide"]}
    (output/"receipt.json").write_text(json.dumps(serializable(receipt),indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps({k:receipt[k] for k in ("status","event_n","numeric_guide_n","primary_proxy_n","adjusted_proxy_n","return_tieout_n")}))
    print(tables["associations"].loc[tables["associations"].primary_family,
        ["window","signal","outcome","n","pearson","slope","slope_95_lo","slope_95_hi","pearson_permutation_p","holm_12_primary_p"]].to_string(index=False))


if __name__=="__main__":
    main()
