"""20_temporal_validation.py -- honest temporal validation of the ABNB reaction and alt-data results.

Implements audit finding A02 (repair) end to end:
  Task A  PRE-EARNINGS FORECAST. Forecast the nights surprise and the revenue surprise vs Street
          using only information available at the pre-release cutoff (the close of the print date;
          ABNB releases after that close). Expanding-window OLS, initial training 8, frozen
          candidate set of 8 features declared in 20_experiment_spec.json. Baselines are scored on
          exactly the same events.
  Task B  POST-RELEASE DRIFT. Use the ACTUAL released surprise, but start the return at the OPEN of
          the first session after the release (see 20_executable_returns.py). Expanding-window OLS,
          initial training 8, +5 and +20 sessions.
  LOO is computed but reported only as a supplementary descriptive column.
  Every prediction is written to 20_prediction_ledger.csv with decision time, last training label,
  forecast, consensus vintage, entry time/price and return endpoint.
  A perturbation check re-runs both tasks with every post-cutoff label and feature corrupted and
  asserts the earlier stored predictions are bit-identical.
  Finally the 9-of-9 guide-below-Street rule and the nights -> 20-day drift result are restated
  under each of the three entry conventions.

READS
  data/processed/overnight/16_reaction_panel.csv     surprises vs consensus, guide vs Street
                                                     (falls back to 04_reaction_panel.csv)
  data/processed/overnight/04_consensus_sources.csv  consensus vintage (publisher, date, vendor)
  data/processed/overnight/20_executable_returns.csv executable-entry event returns
  data/processed/overnight/08_panel_quarterly.csv    WS08 alt-data features (post A01/A05 fixes)
  data/processed/abnb_revenue_guidance_vs_actual.csv guide midpoints and realised cushion

WRITES  data/processed/overnight/
  20_pre_earnings_forecasts.csv  per-event Task A predictions and every baseline
  20_postrelease_drift.csv       per-event Task B predictions and baselines
  20_task_summary.csv            one row per (task, target, model): n, RMSE, baseline RMSEs, ratios,
                                 hit rate, supplementary full-sample LOO R2
  20_prediction_ledger.csv       the audit ledger (A02 acceptance check 3)
  20_perturbation_check.csv      A02 acceptance check 4
  20_convention_restatement.csv  guide-below-Street and nights-drift under each entry convention
  20_frozen_q3_2026.csv          the frozen 5 Nov 2026 prediction rows
Run: py -3.13 analysis/src/overnight/20_temporal_validation.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
PROC = ROOT / "data/processed"
OUT = PROC / "overnight"
OUT.mkdir(parents=True, exist_ok=True)

MIN_TRAIN = 8                      # A02: "expanding-window fits with initial training 8"
CUTOFF_CONVENTION = "close of the print date; ABNB releases after the US close"
NEXT_PRINT_Q = pd.Period("2026Q3")
NEXT_PRINT_DATE = "2026-11-05"

# ---------------------------------------------------------------- frozen candidate set (<=8)
# Declared here and mirrored in 20_experiment_spec.json. Nothing outside this list is fitted in
# Task A; everything else stays in the exploratory ledger (08_feature_tests_all.csv).
PRIMARY_FEATURES = {
    "f_prior_surprise":           "same surprise at the prior print (t-1)",
    "f_surprise_trail4":          "mean of the same surprise over t-4..t-1",
    "f_guide_vs_street_lag1":     "guide midpoint vs Street for THIS quarter, set at the prior print",
    "f_guide_cushion_trail4":     "mean revenue actual-vs-guide-midpoint over t-4..t-1",
    # NOT the WS08 pr_hotel_revpar_yoy: that averages MAR and HLT unconditionally, and MAR reported
    # AFTER ABNB in 2023Q3 (-1d) and 2025Q1 (-5d), HLT in 2024Q2 (-1d). The _pit version averages
    # only the hotels whose lead_days > 0 at each ABNB print. See "Corrections to existing work".
    "pr_hotel_revpar_yoy_pit":    "MAR/HLT RevPAR y/y, same quarter, ONLY peers that reported first",
    "bl_funds_yoy_lag1":          "funds held for clients y/y at end of t-1 (10-Q at the prior print)",
    "eu_platform_yoy_lag1":       "Eurostat EU27 platform nights y/y for t-1 (published before print t)",
    "ia_reviews_ltm_matched_yoy": "Inside Airbnb matched LTM reviews y/y (dumps 1-8 weeks pre-print)",
}
# evaluated alongside the primary set but flagged primary_spec=False: the un-corrected WS08 hotel
# feature, so the cost of the point-in-time correction is visible
COMPARISON_FEATURES = {"pr_hotel_revpar_yoy": "WS08 version, includes peers that reported AFTER ABNB"}
PRE_TARGETS = ["nights_surprise_pct", "revenue_surprise_pct"]
POST_TARGETS = ["open_5d_pct", "open_20d_pct"]
# comparison only: the same drift test under the two non-primary entry conventions, so the
# restatement can quote walk-forward numbers for each convention on identical events
POST_TARGETS_COMPARE = ["legacy_5d_pct", "legacy_20d_pct", "postclose_5d_pct", "postclose_20d_pct"]
POST_FEATURES = ["nights_surprise_pct", "revenue_surprise_pct", "guide_vs_street_pct"]

# A03 item 3: report every result in both evaluation windows, never n from one with a ratio
# from the other.
EVAL_WINDOWS = {"2023Q1+": pd.Period("2023Q1"), "2024Q1+": pd.Period("2024Q1")}

# trailing4/trailing8 matter: the full expanding mean of a surprise series that starts in 2021 is
# dominated by the COVID-rebound surprises (+16%, +24%), so beating it is trivial. Any model that is
# effectively an intercept shift will beat "zero" and "expanding_mean" and lose to "trailing4_mean".
BASELINES_PRE = ["zero", "last_quarter", "prior_year", "ar1", "expanding_mean",
                 "trailing4_mean", "trailing8_mean", "guide", "guide_plus_cushion"]
BASELINES_POST = ["zero", "last_quarter", "expanding_mean", "trailing4_mean"]


# ---------------------------------------------------------------- helpers
def rmse(pred, actual):
    p, a = np.asarray(pred, float), np.asarray(actual, float)
    m = ~(np.isnan(p) | np.isnan(a))
    return float(np.sqrt(np.mean((p[m] - a[m]) ** 2))) if m.sum() else np.nan


def ols(x, y):
    X = np.column_stack([np.ones(len(x)), np.asarray(x, float)])
    b, *_ = np.linalg.lstsq(X, np.asarray(y, float), rcond=None)
    return b


def loo_r2(x, y):
    """SUPPLEMENTARY ONLY. Full-sample leave-one-out R2 vs the LOO mean. This is not a historical
    trading simulation: every fold uses future quarters."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    n = len(y)
    if n < 6:
        return np.nan
    pr, ba = np.empty(n), np.empty(n)
    for i in range(n):
        m = np.arange(n) != i
        b = ols(x[m], y[m])
        pr[i] = b[0] + b[1] * x[i]
        ba[i] = y[m].mean()
    sse = ((y - pr) ** 2).sum()
    ssb = ((y - ba) ** 2).sum()
    return float(1 - sse / ssb) if ssb else np.nan


def add_baselines(ev, target, kind):
    """Point-in-time baseline forecasts for `target`, all computed from strictly earlier events."""
    s = ev[target]
    ev["BL_zero"] = 0.0
    ev["BL_last_quarter"] = s.shift(1)
    ev["BL_prior_year"] = s.shift(4)
    exp_mean, ar1 = [], []
    for i in range(len(ev.index)):
        h = s.iloc[:i].dropna()
        exp_mean.append(h.mean() if len(h) >= 2 else np.nan)
        if len(h) >= 6:
            b = ols(h.values[:-1], h.values[1:])
            ar1.append(b[0] + b[1] * h.values[-1])
        else:
            ar1.append(np.nan)
    ev["BL_expanding_mean"] = exp_mean
    ev["BL_ar1"] = ar1
    ev["BL_trailing4_mean"] = s.shift(1).rolling(4, min_periods=2).mean()
    ev["BL_trailing8_mean"] = s.shift(1).rolling(8, min_periods=4).mean()
    if kind == "revenue_surprise":
        # if the company prints exactly its guide midpoint, the surprise vs Street equals the
        # guide-vs-Street gap that was published at the prior print
        ev["BL_guide"] = ev["f_guide_vs_street_lag1"]
        g = ev["f_guide_vs_street_lag1"] / 100.0
        c = ev["f_guide_cushion_trail4"] / 100.0
        ev["BL_guide_plus_cushion"] = ((1 + g) * (1 + c) - 1) * 100.0
    else:
        ev["BL_guide"] = np.nan
        ev["BL_guide_plus_cushion"] = np.nan
    return ev


def expanding_eval(ev, feature, target, min_train=MIN_TRAIN):
    """One row per evaluated event. The fit uses ONLY events strictly earlier in calendar order.
    Every training label is a surprise or a return already realised at an earlier print, so it was
    known by the decision time of the event being predicted."""
    rows = []
    for t in ev.index:
        if pd.isna(ev.at[t, target]) or pd.isna(ev.at[t, feature]):
            continue
        tr = ev.loc[ev.index < t, [feature, target]].dropna()
        if len(tr) < min_train:
            continue
        b = ols(tr[feature].values, tr[target].values)
        pred = float(b[0] + b[1] * ev.at[t, feature])
        rows.append(dict(
            print_quarter=str(t), feature=feature, target=target,
            decision_time="%s 16:00 ET (%s)" % (ev.at[t, "print_date"].date(), CUTOFF_CONVENTION),
            last_training_label_quarter=str(tr.index.max()),
            last_training_label_known_at=str(ev.at[tr.index.max(), "print_date"].date()),
            n_train=len(tr), x=float(ev.at[t, feature]), pred=pred,
            actual=float(ev.at[t, target]), err=pred - float(ev.at[t, target]),
            slope=float(b[1]), intercept=float(b[0])))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- build the event frame
def build_events():
    src = OUT / "16_reaction_panel.csv"
    panel_src = "16_reaction_panel.csv"
    if not src.exists():
        src = OUT / "04_reaction_panel.csv"
        panel_src = "04_reaction_panel.csv"
    p = pd.read_csv(src, parse_dates=["print_date", "reaction_date"])
    p["q"] = pd.PeriodIndex(p["print_quarter"], freq="Q")
    ev = p.set_index("q").sort_index()

    er = pd.read_csv(OUT / "20_executable_returns.csv")
    er["q"] = pd.PeriodIndex(er["print_quarter"], freq="Q")
    er = er.set_index("q")
    for c in er.columns:
        if c not in ("print_quarter", "print_date", "reaction_date"):
            ev[c] = er[c]

    a = pd.read_csv(OUT / "08_panel_quarterly.csv", index_col=0)
    a.index = pd.PeriodIndex(a.index, freq="Q")
    for c in ["pr_hotel_revpar_yoy", "bl_funds_yoy_lag1", "eu_platform_yoy_lag1",
              "ia_reviews_ltm_matched_yoy", "bl_unearned_yoy_lag1"]:
        ev[c] = a[c].reindex(ev.index) if c in a.columns else np.nan

    # point-in-time hotel RevPAR: average only the peers that had already reported at the ABNB print
    pp = pd.read_csv(PROC / "predictive/02_peer_prints.csv")
    pp["q"] = pd.PeriodIndex(pp["quarter"], freq="Q")
    pp = pp.set_index("q")
    mar = pd.to_numeric(pp["mar_revpar_yoy"], errors="coerce").where(
        pd.to_numeric(pp["mar_lead_days"], errors="coerce") > 0)
    hlt = pd.to_numeric(pp["hlt_revpar_yoy"], errors="coerce").where(
        pd.to_numeric(pp["hlt_lead_days"], errors="coerce") > 0)
    ev["pr_hotel_revpar_yoy_pit"] = pd.concat([mar, hlt], axis=1).mean(axis=1).reindex(ev.index)
    ev["pr_hotel_revpar_n_peers_pit"] = pd.concat([mar, hlt], axis=1).notna().sum(axis=1).reindex(ev.index)

    g = pd.read_csv(PROC / "abnb_revenue_guidance_vs_actual.csv")
    g["q"] = pd.PeriodIndex(g["guided_quarter"], freq="Q")
    g = g.set_index("q")
    ev["cushion_pct"] = g["actual_vs_mid_pct"].reindex(ev.index)
    ev["guide_mid_musd"] = g["guide_mid_musd"].reindex(ev.index)

    # point-in-time engineered features
    ev["f_guide_vs_street_lag1"] = ev["guide_vs_street_pct"].shift(1)
    ev["f_guide_cushion_trail4"] = ev["cushion_pct"].shift(1).rolling(4, min_periods=2).mean()

    # consensus vintage
    cs = pd.read_csv(OUT / "04_consensus_sources.csv", parse_dates=["published"])
    vin = {}
    for pq, gs in cs.groupby("print_quarter"):
        rev = gs[gs.metric == "revenue"].sort_values("published")
        nig = gs[gs.metric == "nights"].sort_values("published")
        vin[pq] = dict(
            cons_rev_vintage=str(rev["published"].min().date()) if len(rev) else "",
            cons_rev_publisher=str(rev["publisher"].iloc[0]) if len(rev) else "",
            cons_nights_vintage=str(nig["published"].min().date()) if len(nig) else "",
            cons_nights_vendor=str(nig["vendor"].iloc[0]) if len(nig) else "")
    v = pd.DataFrame(vin).T
    v.index = pd.PeriodIndex(v.index, freq="Q")
    for c in v.columns:
        ev[c] = v[c].reindex(ev.index)
    pit = []
    for a1, b1 in zip(ev["cons_rev_vintage"], ev["print_date"]):
        try:
            pit.append(bool(pd.Timestamp(a1) <= b1 + pd.Timedelta(days=2)))
        except Exception:
            pit.append(False)
    ev["cons_rev_vintage_is_point_in_time"] = pit
    ev.attrs["panel_src"] = panel_src
    return ev


# ---------------------------------------------------------------- the two tasks
def run_tasks(ev):
    """Pure function of ev, so the perturbation check can call it on a corrupted copy."""
    A, B = [], []
    for target in PRE_TARGETS:
        e = add_baselines(ev.copy(), target,
                          "revenue_surprise" if target.startswith("revenue") else "other")
        # target-specific autoregressive features: last quarter's own surprise and its trailing mean
        e["f_prior_surprise"] = e[target].shift(1)
        e["f_surprise_trail4"] = e[target].shift(1).rolling(4, min_periods=2).mean()
        for feat in list(PRIMARY_FEATURES) + list(COMPARISON_FEATURES):
            if feat not in e.columns:
                continue
            d = expanding_eval(e, feat, target)
            if not len(d):
                continue
            for bl in BASELINES_PRE:
                d["bl_" + bl] = [e.at[pd.Period(q), "BL_" + bl] for q in d.print_quarter]
            d["primary"] = feat in PRIMARY_FEATURES
            d["entry_convention"] = "n/a (forecast task)"
            A.append(d)
    for target in POST_TARGETS + POST_TARGETS_COMPARE:
        if target not in ev.columns:
            continue
        e = add_baselines(ev.copy(), target, "other")
        for feat in POST_FEATURES:
            d = expanding_eval(e, feat, target)
            if not len(d):
                continue
            for bl in BASELINES_POST:
                d["bl_" + bl] = [e.at[pd.Period(q), "BL_" + bl] for q in d.print_quarter]
            d["entry_convention"] = ("executable: open of the reaction session"
                                     if target.startswith("open_") else
                                     "executable: close of the reaction session"
                                     if target.startswith("postclose_") else
                                     "legacy: pre-release close entry (NOT executable)")
            d["primary"] = target in POST_TARGETS
            B.append(d)
    A = pd.concat(A, ignore_index=True) if A else pd.DataFrame()
    B = pd.concat(B, ignore_index=True) if B else pd.DataFrame()
    return A, B


def summarise(df, ev, task, baselines):
    """One row per (task, target, model, evaluation window). All baselines are scored on exactly
    the events the model predicted, inside the same window (A03 item 3)."""
    rows = []
    if not len(df):
        return pd.DataFrame()
    for (feat, tgt), g0 in df.groupby(["feature", "target"]):
        for wlab, w0 in [("all_evaluated", None)] + list(EVAL_WINDOWS.items()):
            g = g0 if w0 is None else g0[g0.print_quarter.map(lambda q: pd.Period(q) >= w0)]
            if len(g) < 3:
                continue
            r = dict(task=task, target=tgt, model=feat, eval_window=wlab, n_events=len(g),
                     first_event=g.print_quarter.min(), last_event=g.print_quarter.max(),
                     min_n_train=int(g.n_train.min()), rmse=rmse(g.pred, g.actual),
                     mae=float(np.nanmean(np.abs(g.pred - g.actual))))
            for bl in baselines:
                r["rmse_" + bl] = rmse(g["bl_" + bl], g.actual)
            cand = [b for b in baselines if not np.isnan(r["rmse_" + b])]
            best = min(cand, key=lambda b: r["rmse_" + b]) if cand else None
            r["best_baseline"] = best or ""
            r["rmse_ratio_vs_best_baseline"] = r["rmse"] / r["rmse_" + best] if best else np.nan
            r["rmse_ratio_vs_zero"] = r["rmse"] / r["rmse_zero"] if r.get("rmse_zero") else np.nan
            r["beats_all_baselines"] = bool(best and r["rmse"] < r["rmse_" + best])
            # a near-constant prediction is an intercept shift, not a signal
            r["pred_sd"] = float(np.std(g.pred.values, ddof=1)) if len(g) > 1 else np.nan
            r["actual_sd"] = float(np.std(g.actual.values, ddof=1)) if len(g) > 1 else np.nan
            r["pred_sd_over_actual_sd"] = (r["pred_sd"] / r["actual_sd"]) if r["actual_sd"] else np.nan
            ch_a = np.sign(g.actual.values)
            ch_p = np.sign(g.pred.values)
            m = ch_a != 0
            r["sign_acc_vs_zero"] = float((ch_a[m] == ch_p[m]).mean()) if m.any() else np.nan
            r["sign_n"] = int(m.sum())
            # supplementary, NOT out-of-sample: full-sample LOO on the same evaluation window
            if feat in ev.columns and tgt in ev.columns:
                full = ev[[feat, tgt]].dropna()
                if w0 is not None:
                    full = full[full.index >= w0]
            else:
                full = pd.DataFrame()
            r["supp_loo_r2_in_window"] = loo_r2(full[feat], full[tgt]) if len(full) >= 6 else np.nan
            r["supp_loo_n"] = len(full)
            if "entry_convention" in g:
                r["entry_convention"] = g["entry_convention"].iloc[0]
                r["primary_spec"] = bool(g["primary"].iloc[0])
            rows.append(r)
    return pd.DataFrame(rows)


def main():
    ev = build_events()
    A, B = run_tasks(ev)
    A.to_csv(OUT / "20_pre_earnings_forecasts.csv", index=False)
    B.to_csv(OUT / "20_postrelease_drift.csv", index=False)

    sA = summarise(A, ev, "A_pre_earnings_forecast", BASELINES_PRE)
    sB = summarise(B, ev, "B_post_release_drift", BASELINES_POST)
    pd.concat([sA, sB], ignore_index=True).round(4).to_csv(OUT / "20_task_summary.csv", index=False)

    # ---------------- prediction ledger (A02 acceptance check 3) -------------
    led = []
    for df, task in [(A, "A_pre_earnings_forecast"), (B, "B_post_release_drift")]:
        for _, r in df.iterrows():
            e = ev.loc[pd.Period(r.print_quarter)]
            is_b = task.startswith("B")
            tgt5 = r.target.endswith("_5d_pct")
            conv = r.get("entry_convention", "")
            entry_t = (e.get("entry_open_time", "") if str(conv).startswith("executable: open")
                       else e.get("entry_postclose_time", "") if str(conv).startswith("executable: close")
                       else "%s 16:00 ET (pre-release close - NOT executable)" % e["print_date"].date()
                       if is_b else "n/a (forecast task, no position)")
            entry_p = (e.get("entry_open_px", np.nan) if str(conv).startswith("executable: open")
                       else e.get("entry_postclose_px", np.nan) if str(conv).startswith("executable: close")
                       else e.get("pre_close", np.nan) if is_b else np.nan)
            led.append(dict(
                task=task, print_quarter=r.print_quarter, target=r.target, model=r.feature,
                decision_time=r.decision_time,
                decision_time_note=("post-release: the feature IS the released surprise, so the "
                                    "decision time is the release, not the pre-release close"
                                    if is_b else
                                    "pre-release: only prior prints, the standing guide and "
                                    "pre-cutoff alt data are used"),
                last_training_label_quarter=r.last_training_label_quarter,
                last_training_label_known_at=r.last_training_label_known_at,
                n_train=r.n_train, feature_value=r.x, forecast=r.pred, actual=r.actual, error=r.err,
                consensus_vintage_revenue=e.get("cons_rev_vintage", ""),
                consensus_publisher_revenue=e.get("cons_rev_publisher", ""),
                consensus_vintage_nights=e.get("cons_nights_vintage", ""),
                consensus_vendor_nights=e.get("cons_nights_vendor", ""),
                consensus_point_in_time=bool(e.get("cons_rev_vintage_is_point_in_time", False)),
                entry_convention=conv, entry_time=entry_t, entry_price=entry_p,
                return_endpoint=("close %s" % e.get("exit_date_5d", "") if (is_b and tgt5) else
                                 "close %s" % e.get("exit_date_20d", "") if is_b else "n/a"),
                exit_price=(e.get("exit_px_5d", np.nan) if (is_b and tgt5) else
                            e.get("exit_px_20d", np.nan) if is_b else np.nan),
                bl_zero=r.get("bl_zero", np.nan),
                bl_last_quarter=r.get("bl_last_quarter", np.nan),
                bl_expanding_mean=r.get("bl_expanding_mean", np.nan),
                bl_guide=r.get("bl_guide", np.nan),
                bl_guide_plus_cushion=r.get("bl_guide_plus_cushion", np.nan)))
    led = pd.DataFrame(led)
    led.round(4).to_csv(OUT / "20_prediction_ledger.csv", index=False)

    # ---------------- perturbation check (A02 acceptance check 4) ------------
    checks = []
    for cut in [pd.Period("2024Q4"), pd.Period("2025Q2")]:
        pev = ev.copy()
        rng = np.random.default_rng(7)
        cols = sorted({c for c in list(PRIMARY_FEATURES) + PRE_TARGETS + POST_TARGETS
                       + POST_FEATURES + ["guide_vs_street_pct", "cushion_pct"]
                       if c in pev.columns})
        mask = pev.index > cut
        for c in cols:
            pev.loc[mask, c] = pev.loc[mask, c] * -3.0 + rng.normal(0, 50, int(mask.sum()))
        pev["f_guide_vs_street_lag1"] = pev["guide_vs_street_pct"].shift(1)
        pev["f_guide_cushion_trail4"] = pev["cushion_pct"].shift(1).rolling(4, min_periods=2).mean()
        pA, pB = run_tasks(pev)
        for df0, df1, task in [(A, pA, "A_pre_earnings_forecast"), (B, pB, "B_post_release_drift")]:
            k = ["print_quarter", "feature", "target"]
            m = df0.merge(df1, on=k, suffixes=("", "_p"))
            early = m[m.print_quarter.map(lambda q: pd.Period(q) <= cut)]
            dmax = float(np.nanmax(np.abs(early.pred - early.pred_p))) if len(early) else np.nan
            ok = bool(len(early)) and dmax < 1e-9
            checks.append(dict(
                task=task, perturbed_after=str(cut), n_predictions_checked=len(early),
                max_abs_pred_difference=dmax, invariant=ok,
                note="every feature and every label in quarters after the cut multiplied by -3 and "
                     "given N(0,50) noise; predictions dated on or before the cut must be identical"))
            assert ok, "LEAKAGE: %s predictions changed after perturbing quarters > %s" % (task, cut)
    pd.DataFrame(checks).to_csv(OUT / "20_perturbation_check.csv", index=False)

    # ---------------- convention restatement (A02 item 5) -------------------
    rest = []
    ev2 = ev.copy()
    ev2["guide_below_street"] = np.where(ev2["guide_vs_street_pct"] < 0, 1.0,
                                         np.where(ev2["guide_vs_street_pct"].notna(), 0.0, np.nan))
    ev2.loc[pd.Period("2021Q3"), "guide_below_street"] = 1.0  # direction known (Reuters), size not
    for conv, cols in [
            ("legacy: pre-release close entry (NOT executable)",
             ["legacy_1d_pct", "legacy_5d_pct", "legacy_20d_pct"]),
            ("executable: open of the reaction session",
             ["open_1d_pct", "open_5d_pct", "open_20d_pct"]),
            ("executable: close of the reaction session",
             ["postclose_5d_pct", "postclose_20d_pct"])]:
        for c in cols:
            d = ev2.loc[ev2["guide_below_street"] == 1, c].dropna()
            allq = ev2[c].dropna()
            if not len(d):
                continue
            base = float((allq < 0).mean())
            neg = int((d < 0).sum())
            rest.append(dict(
                finding="guide midpoint BELOW next-quarter Street", convention=conv, target=c,
                n=len(d), n_negative=neg, share_negative=round(neg / len(d), 3),
                mean_pct=round(float(d.mean()), 2), median_pct=round(float(d.median()), 2),
                base_rate_negative=round(base, 3), base_rate_n=len(allq),
                binom_p_vs_coin=round(stats.binomtest(neg, len(d), 0.5, alternative="greater").pvalue, 4),
                binom_p_vs_base_rate=round(stats.binomtest(neg, len(d), base, alternative="greater").pvalue, 4)))
    for conv, c in [("legacy: pre-release close entry (NOT executable)", "legacy_20d_pct"),
                    ("executable: open of the reaction session", "open_20d_pct"),
                    ("executable: close of the reaction session", "postclose_20d_pct"),
                    ("legacy: pre-release close entry (NOT executable)", "legacy_5d_pct"),
                    ("executable: open of the reaction session", "open_5d_pct")]:
        d = ev2[["nights_surprise_pct", c]].dropna()
        if len(d) < 6:
            continue
        r, p = stats.pearsonr(d["nights_surprise_pct"], d[c])
        wf = B[(B.feature == "nights_surprise_pct") & (B.target == c)] if len(B) else pd.DataFrame()
        rest.append(dict(
            finding="nights surprise -> post-print drift", convention=conv, target=c, n=len(d),
            pearson_r=round(r, 3), pearson_p=round(p, 4), r2=round(r * r, 4),
            supp_loo_r2=round(loo_r2(d["nights_surprise_pct"].values, d[c].values), 4),
            wf_n=len(wf),
            wf_rmse=round(rmse(wf.pred, wf.actual), 3) if len(wf) else np.nan,
            wf_rmse_zero=round(rmse(wf["bl_zero"], wf.actual), 3) if len(wf) else np.nan,
            wf_rmse_expanding_mean=round(rmse(wf["bl_expanding_mean"], wf.actual), 3) if len(wf) else np.nan))
    pd.DataFrame(rest).to_csv(OUT / "20_convention_restatement.csv", index=False)

    # ---------------- frozen 5 Nov 2026 rows --------------------------------
    a = pd.read_csv(OUT / "08_panel_quarterly.csv", index_col=0)
    a.index = pd.PeriodIndex(a.index, freq="Q")
    q3 = NEXT_PRINT_Q
    gvs = float(ev.at[pd.Period("2026Q2"), "guide_vs_street_pct"])
    cush = float(ev["cushion_pct"].dropna().iloc[-4:].mean())
    fvals = {"f_guide_vs_street_lag1": gvs, "f_guide_cushion_trail4": cush,
             "pr_hotel_revpar_yoy_pit": np.nan}   # MAR/HLT report 3Q26 in late Oct, after this freeze
    for c in ["bl_funds_yoy_lag1", "eu_platform_yoy_lag1", "ia_reviews_ltm_matched_yoy"]:
        fvals[c] = float(a.at[q3, c]) if (q3 in a.index and pd.notna(a.at[q3, c])) else np.nan
    frozen = []
    for target in PRE_TARGETS:
        hist = ev[target].dropna()
        fvals["f_prior_surprise"] = float(hist.iloc[-1])
        fvals["f_surprise_trail4"] = float(hist.iloc[-4:].mean())
        e = ev.copy()
        e["f_prior_surprise"] = e[target].shift(1)
        e["f_surprise_trail4"] = e[target].shift(1).rolling(4, min_periods=2).mean()
        for feat in PRIMARY_FEATURES:
            if feat not in e.columns:
                continue
            tr = e[[feat, target]].dropna()
            if len(tr) < MIN_TRAIN:
                continue
            x = fvals.get(feat, np.nan)
            b = ols(tr[feat].values, tr[target].values)
            resid = tr[target].values - (b[0] + b[1] * tr[feat].values)
            frozen.append(dict(
                print_quarter=str(q3), print_date=NEXT_PRINT_DATE, target=target, model=feat,
                decision_time="2026-09-06 spec freeze; refit allowed only on labels through 2026Q2",
                last_training_label_quarter=str(tr.index.max()),
                feature_value=x,
                feature_status="observed" if pd.notna(x) else "PENDING at 2026-09-06",
                forecast=(float(b[0] + b[1] * x) if pd.notna(x) else np.nan),
                resid_sd=float(np.std(resid, ddof=2)), n_train=len(tr),
                bl_zero=0.0, bl_last_quarter=float(hist.iloc[-1]),
                bl_expanding_mean=float(hist.mean()),
                bl_trailing4_mean=float(hist.iloc[-4:].mean()),
                bl_trailing8_mean=float(hist.iloc[-8:].mean()),
                designated_primary=False,
                bl_guide=(gvs if target == "revenue_surprise_pct" else np.nan),
                bl_guide_plus_cushion=((((1 + gvs / 100) * (1 + cush / 100)) - 1) * 100
                                       if target == "revenue_surprise_pct" else np.nan),
                consensus_vintage="guide-vs-Street +%.3f%% set 6-Aug-26 (LSEG $4,610m next-Q vs "
                                  "$4,730m midpoint). Zacks $4,740m (4-Sep-26) is a LATER vintage "
                                  "and is not the feature. The realised target is measured against "
                                  "the print-day (5-Nov-26) consensus." % gvs,
                note="frozen before the 5 Nov 2026 print; the feature set must not be re-selected "
                     "after the print"))
    # The DESIGNATED prediction for 5 Nov. Under the protocol above no primary feature beat every
    # baseline in BOTH evaluation windows, so the frozen forecast is the best surviving baseline
    # (trailing-4-quarter mean of the same surprise), and the feature rows above are recorded only
    # so their prospective errors can be scored against it.
    cons = {"revenue_surprise_pct": (4740.0, "musd", "Zacks 7-estimate revenue consensus, 4-Sep-26"),
            "nights_surprise_pct": (145.0, "m nights", "implied Street nights bar 144-146m "
                                    "(04_q3_2026_breakeven.csv); no published nights consensus")}
    for target in PRE_TARGETS:
        hist = ev[target].dropna()
        pt = float(hist.iloc[-4:].mean())
        lvl, unit, note = cons[target]
        sd = float(hist.iloc[-8:].std(ddof=1))
        frozen.append(dict(
            print_quarter=str(q3), print_date=NEXT_PRINT_DATE, target=target,
            model="BASELINE trailing4_mean", designated_primary=True,
            decision_time="2026-09-06 spec freeze",
            last_training_label_quarter=str(hist.index.max()),
            feature_value=pt, feature_status="observed", forecast=pt, resid_sd=sd, n_train=4,
            bl_zero=0.0, bl_last_quarter=float(hist.iloc[-1]),
            bl_expanding_mean=float(hist.mean()), bl_trailing4_mean=pt,
            bl_trailing8_mean=float(hist.iloc[-8:].mean()),
            bl_guide=(gvs if target == "revenue_surprise_pct" else np.nan),
            bl_guide_plus_cushion=((((1 + gvs / 100) * (1 + cush / 100)) - 1) * 100
                                   if target == "revenue_surprise_pct" else np.nan),
            consensus_vintage=note,
            note="DESIGNATED 5 Nov 2026 forecast: %+.2f%% surprise on a Street bar of %.0f %s "
                 "implies a print of %.1f %s. 1-sd band %+.2f to %+.2f pp."
                 % (pt, lvl, unit, lvl * (1 + pt / 100), unit, pt - sd, pt + sd)))
    fz = pd.DataFrame(frozen)
    fz.round(4).to_csv(OUT / "20_frozen_q3_2026.csv", index=False)

    # ---------------- console ------------------------------------------------
    pd.set_option("display.width", 260)
    print("panel source:", ev.attrs.get("panel_src"))
    for wl in ["all_evaluated", "2023Q1+", "2024Q1+"]:
        print("\n--- Task A: pre-earnings forecast (expanding, min train 8) | window %s ---" % wl)
        print(sA[sA.eval_window == wl][
            ["target", "model", "n_events", "first_event", "last_event", "rmse", "rmse_zero",
             "rmse_last_quarter", "rmse_ar1", "rmse_trailing4_mean", "rmse_guide",
             "rmse_guide_plus_cushion", "best_baseline", "rmse_ratio_vs_best_baseline",
             "pred_sd_over_actual_sd", "beats_all_baselines"]].round(3).to_string(index=False))
    print("\n--- Task B: post-release drift, PRIMARY (executable open entry), all evaluated ---")
    print(sB[(sB.eval_window == "all_evaluated") & (sB.primary_spec)][
        ["target", "model", "n_events", "first_event", "rmse", "rmse_zero", "rmse_expanding_mean",
         "rmse_trailing4_mean", "rmse_ratio_vs_best_baseline", "beats_all_baselines",
         "sign_acc_vs_zero", "sign_n", "supp_loo_r2_in_window"]].round(3).to_string(index=False))
    print("\n--- Task B: same test under each entry convention (nights surprise) ---")
    print(sB[(sB.eval_window == "all_evaluated") & (sB.model == "nights_surprise_pct")][
        ["target", "entry_convention", "n_events", "rmse", "rmse_zero",
         "rmse_ratio_vs_best_baseline", "supp_loo_r2_in_window"]].round(3).to_string(index=False))
    print("\n--- convention restatement ---")
    print(pd.read_csv(OUT / "20_convention_restatement.csv").to_string(index=False))
    print("\n--- frozen 5 Nov rows ---")
    print(fz[["target", "model", "feature_value", "feature_status", "forecast", "resid_sd",
              "n_train"]].round(3).to_string(index=False))
    print("\nledger rows:", len(led), "| Task A rows:", len(A), "| Task B rows:", len(B))
    print("perturbation invariant:",
          pd.read_csv(OUT / "20_perturbation_check.csv")["invariant"].tolist())


if __name__ == "__main__":
    main()
