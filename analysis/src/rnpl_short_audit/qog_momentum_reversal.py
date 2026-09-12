"""Object 4 of the RNPL quality-of-growth study: the momentum and reversal object.

Builds, from repo data only (no Bloomberg yet):

  1. qog_momentum_print_panel.csv      one row per ABNB earnings print, 4Q20-2Q26:
                                       reaction split (gap / intraday / close-to-close),
                                       5/20/60-day post-print excess vs QQQ on two entry
                                       conventions, the KPI state at the print, the
                                       consensus surprise, the next-quarter guide, an
                                       estimate-direction proxy and the FCF-margin delta.
  2. qog_momentum_reconciliation.csv   this build vs the repo's own event-study numbers.
  3. qog_momentum_cells.csv            conditional statistics for the thesis states.
  4. qog_momentum_cell_members.csv     the individual prints inside every cell (n is small).
  5. qog_momentum_state_today.csv      3/6/12-month momentum and its cross-sectional rank.
  6. qog_momentum_bloomberg_spec.csv   the extraction that closes this object.
  7. qog_momentum_return_path.csv      the bear/base/bull return-path skeleton.

Conventions
-----------
Benchmark:   QQQ, arithmetic excess (ABNB return minus QQQ return over identical dates).
             This is the repo convention in 09_stock_behaviour.py and 20_executable_returns.py.
Entry:       `legacy_*` enters at the close of the print date (NOT executable - the release
             is after that close). `open_*` enters at the open of the reaction session and
             is the primary executable convention (WS20/A02).
Drift:       `drift_*` starts at the close of the reaction session, i.e. day 1 is excluded.
             This is workstream 09's convention.
Tags:        every output column is tagged measured / derived / assumed in
             qog_momentum_field_tags.csv-style comments in the note; nothing here is fitted.

Read-only on every input. Writes only data/processed/rnpl_short_audit/qog_momentum_*.csv.

Run:  /Users/theomachado/.venvs/citadel-abnb/bin/python \
        analysis/src/rnpl_short_audit/qog_momentum_reversal.py
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------- paths

HERE = Path(__file__).resolve()
REPO = HERE.parents[3]
OV = REPO / "data" / "processed" / "overnight"
RNPL = REPO / "data" / "processed" / "rnpl_short_audit"
OUT = RNPL


def to_kpi_quarter(q: str) -> str:
    """'2025Q3' -> '3Q25' (the 02_kpi_panel_quarterly label convention)."""
    if not isinstance(q, str) or "Q" not in q:
        return np.nan
    y, n = q.split("Q")
    return f"{n}Q{y[-2:]}"


def prev_quarter(q: str, k: int = 1) -> str:
    """'2025Q3' shifted back k quarters, same label style."""
    y, n = int(q[:4]), int(q[-1])
    idx = y * 4 + (n - 1) - k
    return f"{idx // 4}Q{idx % 4 + 1}"


def next_quarter(q: str, k: int = 1) -> str:
    return prev_quarter(q, -k)


# ---------------------------------------------------------------- inputs


def load_inputs() -> dict:
    px = pd.read_csv(OV / "20_prices_ohlc.csv", parse_dates=["date"]).sort_values("date")
    px = px.reset_index(drop=True)

    panel = pd.read_csv(OV / "04_reaction_panel.csv", parse_dates=["print_date", "reaction_date"])
    execu = pd.read_csv(OV / "20_executable_returns.csv", parse_dates=["print_date", "reaction_date"])
    drift = pd.read_csv(OV / "09_earnings_drift_by_print.csv", parse_dates=["reaction_date"])
    kpi = pd.read_csv(OV / "02_kpi_panel_quarterly.csv")
    actions = pd.read_csv(OV / "09_analyst_actions.csv", parse_dates=["date"])
    daily = pd.read_csv(OV / "09_prices_daily.csv", parse_dates=["Date"]).sort_values("Date")
    si = pd.read_csv(OV / "09_positioning_short_interest.csv", parse_dates=["settlement_date"])
    gled = pd.read_csv(OV / "02_guidance_ledger.csv")
    return dict(px=px, panel=panel, execu=execu, drift=drift, kpi=kpi,
                actions=actions, daily=daily, si=si, gled=gled)


# ---------------------------------------------------------------- returns


def excess_windows(px: pd.DataFrame, reaction_date: pd.Timestamp) -> dict:
    """Every return this object needs, recomputed from 20_prices_ohlc.csv.

    All excess numbers are arithmetic ABNB-minus-QQQ over identical dates, in percent.
    """
    d = px.dropna(subset=["abnb_close", "qqq_close"]).reset_index(drop=True)
    hits = d.index[d["date"] == reaction_date]
    if len(hits) == 0:
        return {}
    i = int(hits[0])
    if i == 0:
        return {}

    a_pre, q_pre = d.at[i - 1, "abnb_close"], d.at[i - 1, "qqq_close"]
    a_op, q_op = d.at[i, "abnb_open"], d.at[i, "qqq_open"]
    a_cl, q_cl = d.at[i, "abnb_close"], d.at[i, "qqq_close"]

    out = {}
    out["pre_close"] = a_pre
    out["reaction_open"] = a_op
    out["reaction_close"] = a_cl
    out["raw_1d_pct"] = (a_cl / a_pre - 1) * 100
    out["excess_1d_pct"] = out["raw_1d_pct"] - (q_cl / q_pre - 1) * 100
    out["gap_pct"] = (a_op / a_pre - 1) * 100
    out["gap_excess_pct"] = out["gap_pct"] - (q_op / q_pre - 1) * 100
    out["intraday_pct"] = (a_cl / a_op - 1) * 100
    out["intraday_excess_pct"] = out["intraday_pct"] - (q_cl / q_op - 1) * 100
    denom = abs(out["raw_1d_pct"])
    out["gap_share_of_day1_abs"] = abs(out["gap_pct"]) / denom * 100 if denom > 1e-9 else np.nan

    # drift: from the reaction-session CLOSE, day 1 excluded (workstream 09 convention)
    for h in (5, 20, 60):
        j = i + h
        if j < len(d):
            out[f"drift_{h}d_excess_pct"] = ((d.at[j, "abnb_close"] / a_cl - 1)
                                             - (d.at[j, "qqq_close"] / q_cl - 1)) * 100
        else:
            out[f"drift_{h}d_excess_pct"] = np.nan

    # executable: from the reaction-session OPEN to the close of the h-th session
    for h in (1, 5, 20, 60):
        j = i + h - 1
        if j < len(d):
            out[f"open_{h}d_excess_pct"] = ((d.at[j, "abnb_close"] / a_op - 1)
                                            - (d.at[j, "qqq_close"] / q_op - 1)) * 100
        else:
            out[f"open_{h}d_excess_pct"] = np.nan

    # run-up: 20 sessions ending at the print-date close
    k = i - 1 - 20
    if k >= 0:
        out["runup_20d_excess_pct"] = ((a_pre / d.at[k, "abnb_close"] - 1)
                                       - (q_pre / d.at[k, "qqq_close"] - 1)) * 100
    else:
        out["runup_20d_excess_pct"] = np.nan
    return out


# ---------------------------------------------------------------- panel


def build_panel(inp: dict) -> pd.DataFrame:
    panel, kpi, px = inp["panel"], inp["kpi"], inp["px"]
    kpi = kpi.set_index("quarter")

    rows = []
    for _, r in panel.iterrows():
        q = r["print_quarter"]
        kq = to_kpi_quarter(q)
        row = {
            "print_quarter": q,
            "kpi_quarter": kq,
            "print_date": r["print_date"].date(),
            "reaction_date": r["reaction_date"].date(),
            "in_requested_window": q >= "2021Q1",
        }
        row.update(excess_windows(px, r["reaction_date"]))

        # ---- KPI state at the print (measured; 02_kpi_panel_quarterly.csv)
        def kget(quarter, col):
            try:
                v = kpi.at[quarter, col]
            except KeyError:
                return np.nan
            return v if pd.notna(v) else np.nan

        row["nights_m"] = kget(kq, "nights_m")
        row["nights_yoy_pct"] = kget(kq, "nights_yoy_pct")
        row["nights_accel_vs_prior_q_pts"] = kget(kq, "nights_yoy_accel_pts")
        yq = to_kpi_quarter(prev_quarter(q, 4))
        ny_prior_year = kget(yq, "nights_yoy_pct")
        row["nights_accel_vs_prior_year_pts"] = (
            row["nights_yoy_pct"] - ny_prior_year
            if pd.notna(row["nights_yoy_pct"]) and pd.notna(ny_prior_year) else np.nan)
        row["gbv_yoy_pct"] = kget(kq, "gbv_yoy_pct")
        row["adr_yoy_pct"] = kget(kq, "adr_yoy_pct")
        row["revenue_yoy_pct"] = kget(kq, "revenue_yoy_pct")
        row["fcf_margin_pct"] = kget(kq, "fcf_margin_pct")
        fcf_prior_year = kget(yq, "fcf_margin_pct")
        row["fcf_margin_yoy_chg_pts"] = (
            row["fcf_margin_pct"] - fcf_prior_year
            if pd.notna(row["fcf_margin_pct"]) and pd.notna(fcf_prior_year) else np.nan)

        # ---- consensus at the print (measured where a vendor quote exists)
        row["cons_revenue_musd"] = r["cons_revenue_musd"]
        row["cons_revenue_vendor"] = r["cons_revenue_vendor"]
        row["revenue_surprise_pct"] = r["revenue_surprise_pct"]
        row["cons_nights_m"] = r["cons_nights_m"]
        row["nights_surprise_pct"] = r["nights_surprise_pct"]
        row["gbv_surprise_pct"] = r["gbv_surprise_pct"]

        # ---- next-quarter guide vs Street (measured) and the growth it implies (derived)
        nq = r["next_quarter"] if isinstance(r["next_quarter"], str) else np.nan
        row["next_quarter"] = nq
        row["next_q_cons_revenue_musd"] = r["next_q_cons_revenue_musd"]
        row["next_q_cons_vendor"] = r["next_q_cons_vendor"]
        row["next_q_guide_mid_musd"] = r["next_q_guide_mid_musd"]
        row["guide_vs_street_pct"] = r["guide_vs_street_pct"]
        if isinstance(nq, str) and pd.notna(r["next_q_guide_mid_musd"]):
            base = kget(to_kpi_quarter(prev_quarter(nq, 4)), "revenue_musd")
            row["guide_implied_next_q_rev_yoy_pct"] = (
                (r["next_q_guide_mid_musd"] / base - 1) * 100 if pd.notna(base) else np.nan)
        else:
            row["guide_implied_next_q_rev_yoy_pct"] = np.nan
        row["guide_implied_rev_decel_pts"] = (
            row["guide_implied_next_q_rev_yoy_pct"] - row["revenue_yoy_pct"]
            if pd.notna(row["guide_implied_next_q_rev_yoy_pct"])
            and pd.notna(row["revenue_yoy_pct"]) else np.nan)
        rows.append(row)

    out = pd.DataFrame(rows)
    out = add_estimate_direction_proxy(out, inp["actions"])
    out["point_in_time_consensus_revision_direction"] = "MISSING - needs Bloomberg BEst"
    # WS09's own convention, carried alongside so the two can be compared row by row
    out = out.merge(ws09_replication(inp), on="print_quarter", how="left")
    return out


def add_estimate_direction_proxy(panel: pd.DataFrame, actions: pd.DataFrame) -> pd.DataFrame:
    """Proxy for 'were estimates rising into the print?'.

    The repo carries no point-in-time consensus VINTAGE history, so the true
    estimate-revision direction is not derivable here (that is the Bloomberg ask).
    What the repo does carry is 466 dated sell-side actions with price-target
    direction (09_analyst_actions.csv, yfinance/Benzinga feed, pulled 2026-09-06).
    Net price-target raises over the 60 calendar days BEFORE the print date is the
    closest available proxy. Tag: derived, proxy, NOT the estimate series.
    """
    a = actions.dropna(subset=["date"]).copy()
    raises, cuts, nets = [], [], []
    for _, r in panel.iterrows():
        pd_date = pd.Timestamp(r["print_date"])
        win = a[(a["date"] >= pd_date - pd.Timedelta(days=60)) & (a["date"] < pd_date)]
        up = int((win["priceTargetAction"] == "Raises").sum())
        dn = int((win["priceTargetAction"] == "Lowers").sum())
        raises.append(up)
        cuts.append(dn)
        nets.append(up - dn)
    panel["pt_raises_60d_pre"] = raises
    panel["pt_cuts_60d_pre"] = cuts
    panel["pt_net_60d_pre"] = nets
    panel["estimate_direction_proxy"] = np.where(
        np.array(nets) > 0, "rising",
        np.where(np.array(nets) < 0, "falling", "flat/none"))
    return panel


def ws09_replication(inp: dict) -> pd.DataFrame:
    """Reproduce workstream 09's drift numbers on its own convention.

    WS09 does NOT use holding-period excess returns. It builds an event-time path
    anchored 21 sessions before the reaction day as
        path_t = cumprod(1+r_ABNB) - cumprod(1+r_QQQ),  both from the anchor,
    on the ADJUSTED closes in 09_prices_daily.csv, and reports
        day1     = path[0]  - path[-1]
        drift_h  = path[+h] - path[0]
        run-up   = path[-1] - 0.
    That is a different (and larger-magnitude) object than close-to-close excess.
    Reproducing it exactly is the check; the panel's primary numbers stay on the
    holding-period convention, which is what 20_executable_returns.csv uses.
    """
    d = inp["daily"].sort_values("Date").reset_index(drop=True)
    ra = d["ABNB"].pct_change()
    rq = d["QQQ"].pct_change()
    rows = []
    for _, r in inp["drift"].iterrows():
        hit = d.index[d["Date"] == r["reaction_date"]]
        if len(hit) == 0:
            continue
        i = int(hit[0])
        a = i - 21
        path = ((1 + ra.iloc[a + 1:]).cumprod() - (1 + rq.iloc[a + 1:]).cumprod()) * 100
        rec = {"print_quarter": r["quarter"]}
        rec["ws09_day1_excess_pct"] = path.get(i, np.nan) - path.get(i - 1, np.nan)
        rec["ws09_runup_20d_excess_pct"] = path.get(i - 1, np.nan)
        for h in (5, 20, 60):
            rec[f"ws09_drift_{h}d_excess_pct"] = (path.get(i + h, np.nan)
                                                  - path.get(i, np.nan))
        rows.append(rec)
    return pd.DataFrame(rows)


def reconcile(panel: pd.DataFrame, inp: dict) -> pd.DataFrame:
    """Reproduce the repo's own event-study numbers; record every discrepancy."""
    ex = inp["execu"].copy()
    ex["print_quarter"] = ex["print_quarter"].astype(str)
    dr = inp["drift"].copy()
    dr = dr.rename(columns={"quarter": "print_quarter"})
    rp = inp["panel"][["print_quarter", "excess_1d_pct", "excess_5d_pct", "excess_20d_pct"]]

    m = panel[["print_quarter", "excess_1d_pct", "gap_excess_pct",
               "open_5d_excess_pct", "open_20d_excess_pct",
               "drift_5d_excess_pct", "drift_20d_excess_pct", "drift_60d_excess_pct",
               "runup_20d_excess_pct"]].copy()
    m = m.merge(ex[["print_quarter", "legacy_1d_pct", "gap_excess_pct",
                    "open_5d_pct", "open_20d_pct"]],
                on="print_quarter", how="left", suffixes=("", "_repo20"))
    m = m.merge(dr[["print_quarter", "day1_excess_pct", "drift_5d_excess_pct",
                    "drift_20d_excess_pct", "drift_60d_excess_pct",
                    "runup_20d_excess_pct"]],
                on="print_quarter", how="left", suffixes=("", "_repo09"))
    m = m.merge(rp, on="print_quarter", how="left", suffixes=("", "_repo04"))

    m = m.merge(ws09_replication(inp), on="print_quarter", how="left")

    checks = [
        ("day-1 excess vs 20_executable_returns.legacy_1d_pct",
         "excess_1d_pct", "legacy_1d_pct", "same convention - must be exact"),
        ("gap excess vs 20_executable_returns.gap_excess_pct",
         "gap_excess_pct", "gap_excess_pct_repo20", "same convention - must be exact"),
        ("executable 5d vs 20_executable_returns.open_5d_pct",
         "open_5d_excess_pct", "open_5d_pct", "same convention - must be exact"),
        ("executable 20d vs 20_executable_returns.open_20d_pct",
         "open_20d_excess_pct", "open_20d_pct", "same convention - must be exact"),
        ("day-1 excess vs 04_reaction_panel.excess_1d_pct",
         "excess_1d_pct", "excess_1d_pct_repo04",
         "04 stores the same number rounded to 0.1pp"),
        ("day-1 excess vs 09_earnings_drift.day1_excess_pct (DIFFERENT convention)",
         "excess_1d_pct", "day1_excess_pct",
         "09 uses an anchored cumulative-product spread path on adjusted closes; expect a gap"),
        ("drift 20d vs 09_earnings_drift (DIFFERENT convention)",
         "drift_20d_excess_pct", "drift_20d_excess_pct_repo09",
         "same reason"),
        ("drift 60d vs 09_earnings_drift (DIFFERENT convention)",
         "drift_60d_excess_pct", "drift_60d_excess_pct_repo09",
         "same reason"),
        ("run-up 20d vs 09_earnings_drift",
         "runup_20d_excess_pct", "runup_20d_excess_pct_repo09",
         "the run-up node coincides on the two conventions"),
        ("WS09 REPLICATION: day-1 on 09's own convention",
         "ws09_day1_excess_pct", "day1_excess_pct", "must be exact"),
        ("WS09 REPLICATION: drift 5d on 09's own convention",
         "ws09_drift_5d_excess_pct", "drift_5d_excess_pct_repo09", "must be exact"),
        ("WS09 REPLICATION: drift 20d on 09's own convention",
         "ws09_drift_20d_excess_pct", "drift_20d_excess_pct_repo09",
         "exact except 2026Q1 - see the 25 May 2026 note"),
        ("WS09 REPLICATION: drift 60d on 09's own convention",
         "ws09_drift_60d_excess_pct", "drift_60d_excess_pct_repo09",
         "exact except 2026Q1 - see the 25 May 2026 note"),
    ]
    rows = []
    for label, mine, theirs, note in checks:
        if theirs not in m.columns or mine not in m.columns:
            continue
        d = (m[mine] - m[theirs]).abs()
        rows.append({
            "check": label,
            "n_compared": int(d.notna().sum()),
            "max_abs_diff_pp": round(float(d.max()), 6) if d.notna().any() else np.nan,
            "mean_abs_diff_pp": round(float(d.mean()), 6) if d.notna().any() else np.nan,
            "worst_print": m.loc[d.idxmax(), "print_quarter"] if d.notna().any() else np.nan,
            "n_prints_over_0p01pp": int((d > 0.01).sum()),
            "note": note,
        })
    rows.append({
        "check": "DISCREPANCY FOUND: 09_prices_daily.csv carries an all-NaN row for "
                 "2026-05-25 (Memorial Day, a market holiday). 20_prices_ohlc.csv "
                 "correctly omits it.",
        "n_compared": 1, "max_abs_diff_pp": np.nan, "mean_abs_diff_pp": np.nan,
        "worst_print": "2026Q1", "n_prints_over_0p01pp": 1,
        "note": "It is the only print whose +20 and +60 windows span that date, so it is the "
                "only print where WS09's event-time clock is shifted by one session. WS09 "
                "drift_20d 2026Q1 = -6.26%; on a clean session index it is -3.39% on WS09's "
                "own convention and -5.67% on the holding-period convention used here. "
                "Nothing in WS09's published aggregates moves materially (one print of 23), "
                "but the 2026Q1 row should not be quoted on its own from 09_earnings_drift_by_print.csv.",
    })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- cells

RET_COLS = [
    ("excess_1d_pct", "day-1 close-to-close excess (NOT executable)"),
    ("open_1d_excess_pct", "day-1 executable (reaction open -> reaction close)"),
    ("gap_excess_pct", "overnight gap excess (not executable)"),
    ("drift_5d_excess_pct", "+1..+5 drift from reaction close"),
    ("drift_20d_excess_pct", "+1..+20 drift from reaction close"),
    ("drift_60d_excess_pct", "+1..+60 drift from reaction close"),
    ("open_20d_excess_pct", "executable 20 sessions from reaction open"),
]


def cell_stats(df: pd.DataFrame, cell: str, definition: str) -> list[dict]:
    out = []
    for col, desc in RET_COLS:
        s = df[col].dropna()
        out.append({
            "cell": cell,
            "definition": definition,
            "metric": col,
            "metric_desc": desc,
            "n": int(len(s)),
            "mean_pct": round(float(s.mean()), 2) if len(s) else np.nan,
            "median_pct": round(float(s.median()), 2) if len(s) else np.nan,
            "hit_rate_negative": round(float((s < 0).mean()), 3) if len(s) else np.nan,
            "hit_rate_positive": round(float((s > 0).mean()), 3) if len(s) else np.nan,
            "min_pct": round(float(s.min()), 2) if len(s) else np.nan,
            "max_pct": round(float(s.max()), 2) if len(s) else np.nan,
            "sd_pct": round(float(s.std(ddof=1)), 2) if len(s) > 1 else np.nan,
            # descriptive only. No p-value is quoted anywhere in this object: the
            # RED_TEAM ruling on the guide-below-Street rule (three incompatible
            # p-values in circulation) applies to every cell here, all of which are
            # post-hoc conditionings on the same 22 prints.
            "se_pct": round(float(s.std(ddof=1) / np.sqrt(len(s))), 2) if len(s) > 1 else np.nan,
            "mean_over_se": round(float(s.mean() / (s.std(ddof=1) / np.sqrt(len(s)))), 2)
            if len(s) > 1 and s.std(ddof=1) > 0 else np.nan,
            "separable_from_noise": (
                "no - |mean| < 1 standard error"
                if len(s) > 1 and s.std(ddof=1) > 0
                and abs(s.mean()) < s.std(ddof=1) / np.sqrt(len(s))
                else ("weak - |mean| between 1 and 2 standard errors"
                      if len(s) > 1 and s.std(ddof=1) > 0
                      and abs(s.mean()) < 2 * s.std(ddof=1) / np.sqrt(len(s))
                      else ("|mean| > 2 standard errors, but this is one of many "
                            "post-hoc cells on 22 prints - treat as a base rate"
                            if len(s) > 1 else "n too small"))),
        })
    return out


def build_cells(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    p = panel[panel["in_requested_window"]].copy()

    cells: dict[str, tuple[pd.DataFrame, str]] = {}
    cells["all prints 1Q21-2Q26"] = (p, "every print in the requested window")

    acc = p[p["nights_accel_vs_prior_q_pts"] > 0]
    dec = p[p["nights_accel_vs_prior_q_pts"] < 0]
    cells["(a) nights ACCELERATING vs prior quarter"] = (
        acc, "nights_yoy_accel_pts > 0 (02_kpi_panel_quarterly.csv)")
    cells["(a) nights DECELERATING vs prior quarter"] = (
        dec, "nights_yoy_accel_pts < 0")

    # post-2022 subsample: the COVID-rebound accelerations are not comparable states
    cells["(a) nights ACCELERATING, 2023+"] = (
        acc[acc["print_quarter"] >= "2023Q1"], "nights accel > 0 and print_quarter >= 2023Q1")
    cells["(a) nights DECELERATING, 2023+"] = (
        dec[dec["print_quarter"] >= "2023Q1"], "nights accel < 0 and print_quarter >= 2023Q1")

    b = p[(p["nights_accel_vs_prior_q_pts"] < 0) & (p["revenue_surprise_pct"] > 0)]
    cells["(b) nights DECELERATED while revenue BEAT"] = (
        b, "nights_yoy_accel_pts < 0 AND revenue_surprise_pct > 0 (the thesis state)")

    b2 = p[(p["nights_accel_vs_prior_q_pts"] < 0) & (p["revenue_surprise_pct"] > 0)
           & (p["estimate_direction_proxy"] == "rising")]
    cells["(b') as (b) and PT revisions rising into the print"] = (
        b2, "(b) AND pt_net_60d_pre > 0 - PROXY for rising estimates, not the estimate series")

    c = p[p["guide_implied_rev_decel_pts"] < 0]
    cells["(c) next-quarter guide implied DECELERATION"] = (
        c, "guide-implied next-quarter revenue y/y < just-reported revenue y/y")
    c2 = p[(p["guide_implied_rev_decel_pts"] < -2)]
    cells["(c') guide implied deceleration > 2 pts"] = (
        c2, "guide-implied next-quarter revenue y/y at least 2pp below the reported y/y")

    ru = p[p["runup_20d_excess_pct"] > 0]
    rd = p[p["runup_20d_excess_pct"] <= 0]
    cells["(d) print after a POSITIVE 20d run-up"] = (
        ru, "runup_20d_excess_pct > 0 (recomputed; matches 09_runup_vs_reaction inputs)")
    cells["(d) print after a NEGATIVE 20d run-up"] = (
        rd, "runup_20d_excess_pct <= 0")
    if p["runup_20d_excess_pct"].notna().sum() >= 6:
        hi = p["runup_20d_excess_pct"].quantile(2 / 3)
        cells["(d') top-third run-up"] = (
            p[p["runup_20d_excess_pct"] >= hi],
            f"runup_20d_excess_pct >= {hi:.2f} (top tercile of this sample)")

    # the combined thesis state: decel + beat + guide implies further deceleration
    t = p[(p["nights_accel_vs_prior_q_pts"] < 0) & (p["revenue_surprise_pct"] > 0)
          & (p["guide_implied_rev_decel_pts"] < 0)]
    cells["(e) decel + beat + guide implies further decel"] = (
        t, "the full 5-Nov/February analogue state")

    stat_rows, member_rows = [], []
    for name, (df, definition) in cells.items():
        stat_rows += cell_stats(df, name, definition)
        for _, r in df.iterrows():
            member_rows.append({
                "cell": name,
                "print_quarter": r["print_quarter"],
                "reaction_date": r["reaction_date"],
                "nights_yoy_pct": round(r["nights_yoy_pct"], 2) if pd.notna(r["nights_yoy_pct"]) else np.nan,
                "nights_accel_pts": round(r["nights_accel_vs_prior_q_pts"], 2)
                if pd.notna(r["nights_accel_vs_prior_q_pts"]) else np.nan,
                "revenue_surprise_pct": r["revenue_surprise_pct"],
                "guide_vs_street_pct": r["guide_vs_street_pct"],
                "guide_implied_rev_decel_pts": round(r["guide_implied_rev_decel_pts"], 2)
                if pd.notna(r["guide_implied_rev_decel_pts"]) else np.nan,
                "estimate_direction_proxy": r["estimate_direction_proxy"],
                "raw_1d_pct": round(r["raw_1d_pct"], 2),
                "excess_1d_pct": round(r["excess_1d_pct"], 2),
                "open_1d_excess_pct": round(r["open_1d_excess_pct"], 2),
                "drift_20d_excess_pct": round(r["drift_20d_excess_pct"], 2)
                if pd.notna(r["drift_20d_excess_pct"]) else np.nan,
                "drift_60d_excess_pct": round(r["drift_60d_excess_pct"], 2)
                if pd.notna(r["drift_60d_excess_pct"]) else np.nan,
            })
    return pd.DataFrame(stat_rows), pd.DataFrame(member_rows)


# ---------------------------------------------------------------- today


def momentum_today(inp: dict) -> pd.DataFrame:
    d = inp["daily"].set_index("Date").sort_index()
    asof = d.index.max()
    tickers = ["ABNB", "QQQ", "SPY", "MTUM", "IWM", "IVE", "IVW", "XLY",
               "BKNG", "EXPE", "MAR", "HLT", "H", "TRIP", "UBER", "DASH", "JETS"]
    horizons = {"3m": 63, "6m": 126, "12m": 252}
    rows = []
    for h, n in horizons.items():
        if len(d) <= n:
            continue
        base_date = d.index[-(n + 1)]
        rets = {}
        for t in tickers:
            if t not in d.columns:
                continue
            a, b = d[t].iloc[-(n + 1)], d[t].iloc[-1]
            if pd.notna(a) and pd.notna(b) and a > 0:
                rets[t] = (b / a - 1) * 100
        ser = pd.Series(rets).sort_values(ascending=False)
        rank = int(list(ser.index).index("ABNB")) + 1
        for t, v in ser.items():
            rows.append({
                "as_of": asof.date(), "horizon": h, "sessions": n,
                "window_start": base_date.date(),
                "ticker": t, "price_return_pct": round(v, 2),
                "abnb_rank_in_window": rank if t == "ABNB" else np.nan,
                "n_in_window": len(ser),
                "abnb_minus_qqq_pp": round(rets["ABNB"] - rets["QQQ"], 2)
                if t == "ABNB" and "QQQ" in rets else np.nan,
                "abnb_minus_mtum_pp": round(rets["ABNB"] - rets["MTUM"], 2)
                if t == "ABNB" and "MTUM" in rets else np.nan,
            })
    return pd.DataFrame(rows)


def since_the_print(inp: dict) -> pd.DataFrame:
    px = inp["px"].dropna(subset=["abnb_close"]).reset_index(drop=True)
    i = int(px.index[px["date"] == pd.Timestamp("2026-08-07")][0])
    pre = int(px.index[px["date"] == pd.Timestamp("2026-08-06")][0])
    last = len(px) - 1
    rows = [
        {"item": "pre-print close 6 Aug 2026", "value": round(px.at[pre, "abnb_close"], 2), "unit": "usd"},
        {"item": "reaction-session open 7 Aug 2026", "value": round(px.at[i, "abnb_open"], 2), "unit": "usd"},
        {"item": "reaction-session close 7 Aug 2026", "value": round(px.at[i, "abnb_close"], 2), "unit": "usd"},
        {"item": "day-1 raw close-to-close", "value": round((px.at[i, "abnb_close"] / px.at[pre, "abnb_close"] - 1) * 100, 2), "unit": "pct"},
        {"item": "day-1 QQQ-excess close-to-close", "value": round(((px.at[i, "abnb_close"] / px.at[pre, "abnb_close"]) - (px.at[i, "qqq_close"] / px.at[pre, "qqq_close"])) * 100, 2), "unit": "pct"},
        {"item": "overnight gap (raw)", "value": round((px.at[i, "abnb_open"] / px.at[pre, "abnb_close"] - 1) * 100, 2), "unit": "pct"},
        {"item": "intraday on the reaction day (raw)", "value": round((px.at[i, "abnb_close"] / px.at[i, "abnb_open"] - 1) * 100, 2), "unit": "pct"},
        {"item": "gap share of the day-1 move", "value": round(abs(px.at[i, "abnb_open"] / px.at[pre, "abnb_close"] - 1) / abs(px.at[i, "abnb_close"] / px.at[pre, "abnb_close"] - 1) * 100, 1), "unit": "pct of |move|"},
        {"item": "last close in the file", "value": round(px.at[last, "abnb_close"], 2), "unit": "usd"},
        {"item": "last date in the file", "value": str(px.at[last, "date"].date()), "unit": "date"},
        {"item": "sessions since the reaction day", "value": last - i, "unit": "sessions"},
        {"item": "raw return since the reaction-day close", "value": round((px.at[last, "abnb_close"] / px.at[i, "abnb_close"] - 1) * 100, 2), "unit": "pct"},
        {"item": "QQQ-excess since the reaction-day close", "value": round(((px.at[last, "abnb_close"] / px.at[i, "abnb_close"]) - (px.at[last, "qqq_close"] / px.at[i, "qqq_close"])) * 100, 2), "unit": "pct"},
        {"item": "executable: reaction open to last close, raw", "value": round((px.at[last, "abnb_close"] / px.at[i, "abnb_open"] - 1) * 100, 2), "unit": "pct"},
        {"item": "high close since the print", "value": round(px.loc[i:last, "abnb_close"].max(), 2), "unit": "usd"},
        {"item": "date of the high close", "value": str(px.loc[i:last, "date"][px.loc[i:last, "abnb_close"].idxmax()].date()), "unit": "date"},
        {"item": "drawdown from that high to the last close", "value": round((px.at[last, "abnb_close"] / px.loc[i:last, "abnb_close"].max() - 1) * 100, 2), "unit": "pct"},
    ]
    si = inp["si"].sort_values("settlement_date")
    rows.append({"item": f"short interest, {si['settlement_date'].iloc[-1].date()}",
                 "value": round(float(si["si_pct_shares"].iloc[-1]), 2), "unit": "pct of shares out"})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- bloomberg spec


def bloomberg_spec() -> pd.DataFrame:
    rows = [
        # field/function, tickers, frequency, date range, purpose, test fed, certainty
        ("BDH(BEST_SALES, BEST_FPERIOD_OVERRIDE=1BF..8BF and FY1..FY3)",
         "ABNB US Equity", "daily (or weekly)", "1 Jan 2021 - live",
         "point-in-time revenue consensus by fiscal period; the true 'estimates still rising' series",
         "task-2 cell (b'), perception test 3, momentum test 4", "BEST_SALES verified; period-override syntax verify in FLDS"),
        ("BDH(BEST_EBITDA, BEST_FPERIOD_OVERRIDE)", "ABNB US Equity", "daily", "1 Jan 2021 - live",
         "point-in-time adj. EBITDA consensus; feeds the EV/EBITDA exit rule",
         "return-path multiple rule; object 3", "BEST_EBITDA verified"),
        ("BDH(BEST_EPS, BEST_FPERIOD_OVERRIDE)", "ABNB US Equity", "daily", "1 Jan 2021 - live",
         "point-in-time EPS consensus; the surprise series the repo only has for 23 prints",
         "print panel revenue/EPS surprise columns", "BEST_EPS verified"),
        ("BEST_CAPEX / BEST_FCF or BEST_CASH_FLOW_PER_SH",
         "ABNB US Equity", "daily", "1 Jan 2021 - live",
         "point-in-time FCF consensus - the object-3 numerator in 'did FCF estimates move with KPI estimates'",
         "perception test 3 (FY27 FCF vs FY27 revenue revisions since 6 Aug 2026)",
         "verify in FLDS - Bloomberg FCF consensus coverage for ABNB is not guaranteed"),
        ("KPI consensus: BEST_<custom KPI> via ANR / Estimates > KPI, or Visible Alpha add-in",
         "ABNB US Equity", "quarterly", "1Q21 - live",
         "Street GBV and Nights-and-Seats-Booked consensus by quarter; the repo has nights consensus for only 19 of 23 prints and none for 3Q26",
         "task-1 nights surprise column; the 5 Nov wedge test",
         "verify in FLDS - Bloomberg may not carry ABNB KPI consensus at all; if absent, say so and fall back to Zacks (which publishes nights/ADR/GBV 2-3 days pre-print)"),
        ("BEST_ANALYST_RECS / number of estimates up vs down: EE ratings screen, or BDH(BEST_ANALYST_RATING)",
         "ABNB US Equity", "daily", "1 Jan 2021 - live",
         "revision BREADTH - how many estimates moved up vs down in the 30/60 days around each print",
         "replaces the price-target proxy in the print panel's estimate-direction column",
         "verify in FLDS"),
        ("BEST_ESTIMATE_STD_DEV / BEST_SALES_HI, BEST_SALES_LO, BEST_SALES_NUMEST",
         "ABNB US Equity", "daily", "1 Jan 2021 - live",
         "estimate dispersion and panel size per period; dispersion is the state variable for how violent a guide-miss reaction is",
         "reaction-magnitude conditioning; the 5 Nov card", "verify in FLDS"),
        ("BEST_TARGET_PRICE, BEST_TARGET_PRICE_MEDIAN, plus the ANR ratings history",
         "ABNB US Equity", "daily", "1 Jan 2021 - live",
         "point-in-time target and rating history; the repo has only a live snapshot plus a Benzinga action feed",
         "task-3 'Street is behind the stock' and the sell-side-capitulation flip rule", "BEST_TARGET_PRICE verified"),
        ("SHORT_INT, SI_PERCENT_EQUITY_FLOAT, SHORT_INT_RATIO (days to cover)",
         "ABNB US Equity", "semi-monthly", "1 Jan 2021 - live",
         "positioning into each print and into 5 Nov; days to cover is the squeeze risk on a short",
         "sizing discipline in the return path; task-3 state", "SHORT_INT verified; days-to-cover mnemonic verify in FLDS"),
        ("HIST_CALL_IMP_VOL / 30DAY_IMPVOL_100.0%MNY_DF; 3MTH_IMPVOL_100.0%MNY_DF",
         "ABNB US Equity", "daily", "1 Jan 2021 - live",
         "30-day and 3-month at-the-money implied vol into every print; lets the repo's 7.1% mean absolute day-1 base rate be compared to what was priced",
         "replaces the withdrawn event-premium estimate (audit A08); the 5 Nov trade structure",
         "verify in FLDS - the MNY_DF family names change by version"),
        ("30DAY_IMPVOL_90.0%MNY_DF minus 30DAY_IMPVOL_110.0%MNY_DF (put-call skew)",
         "ABNB US Equity", "daily", "1 Jan 2021 - live",
         "skew into each print; whether downside is already paid for",
         "same as above; the bear-leg cost in the return path", "verify in FLDS"),
        ("TOT_RETURN_INDEX_GROSS_DVDS (BDH)",
         "ABNB US Equity; QQQ US Equity; SPY US Equity; NDX Index; SPX Index",
         "daily", "10 Dec 2020 - live",
         "true total-return series - the repo's momentum is price-only and the benchmark's dividend is a small, one-sided drag",
         "task-3 momentum ranks restated on total return", "TOT_RETURN_INDEX_GROSS_DVDS verified"),
        ("TOT_RETURN_INDEX_GROSS_DVDS (BDH) - momentum index proxies",
         "SP500MUP Index (S&P 500 Momentum); M1USMOM Index or MXUSMOM (MSCI USA Momentum); MTUM US Equity",
         "daily", "1 Jan 2021 - live",
         "ABNB's beta to the momentum FACTOR through time; the repo finds beta_MOM = -0.77 in 2026 on Ken French data and needs a tradable index cross-check",
         "task-3 momentum-exposure claim; the 'crowded momentum unwind' branch of the bear case",
         "verify in FLDS - index tickers for the momentum indices are the item most likely to be wrong"),
        ("Earnings history: ERN / BDH(IS_COMP_SALES, BEST_SALES_SURPRISE_PCT), plus the announcement timestamp",
         "ABNB US Equity", "quarterly", "1Q21 - live",
         "vendor-stamped surprise history and the exact release timestamp, so the executable-entry convention can be audited",
         "task-1 panel; reconciles the repo's 23-print hand-built consensus", "ERN screen verified; surprise mnemonic verify in FLDS"),
        ("Peer print read-across: same BEst block plus day-1 reaction",
         "BKNG US Equity; EXPE US Equity; MAR US Equity; HLT US Equity",
         "quarterly / daily", "1 Jan 2021 - live",
         "does a KPI deceleration with an estimate beat hurt the OTA complex generally, or only ABNB? n=23 on ABNB alone cannot answer it",
         "the only route to a sample big enough to separate (b) from noise", "no special mnemonic"),
        ("Factor exposure history: PORT > Factor Exposure, or FACTOR_EXPOSURE fields; export to Excel",
         "ABNB US Equity vs a momentum-factor model", "monthly", "1 Jan 2021 - live",
         "ABNB's loading on the momentum factor as Bloomberg measures it, to corroborate the Ken French result",
         "task-3; the momentum-unwind branch",
         "verify in FLDS - PORT exposures may not be exportable via BDH on this licence; a manual export is acceptable"),
        ("Index membership and weight in the momentum indices",
         "SP500MUP Index; M1USMOM Index", "at each rebalance", "1 Jan 2021 - live",
         "is ABNB actually IN a momentum index today? If it is, a KPI reversal creates a mechanical seller at the next rebalance",
         "the bear-case flow leg of the return path",
         "verify in FLDS - use MEMB on the index; rebalance dates matter more than the field name"),
        ("Guidance history: GUID / company guidance fields",
         "ABNB US Equity", "quarterly", "1Q21 - live",
         "vendor-stamped guide midpoints to cross-check the repo's 194-row hand-built guidance ledger",
         "task-1 guide-vs-Street column", "GUID screen verified; BDH guidance mnemonics verify in FLDS"),
    ]
    cols = ["field_or_function", "tickers", "frequency", "date_range",
            "purpose", "test_it_feeds", "mnemonic_certainty"]
    return pd.DataFrame(rows, columns=cols)


# ---------------------------------------------------------------- return path


def return_path_skeleton(panel: pd.DataFrame, cells: pd.DataFrame) -> pd.DataFrame:
    """Every input labelled; the multiple rule applied exactly once; blanks left blank."""

    def cell(name, metric, stat):
        m = cells[(cells["cell"] == name) & (cells["metric"] == metric)]
        return float(m[stat].iloc[0]) if len(m) else np.nan

    rows = [
        dict(line="A. Starting point: ABNB close 4 Sep 2026",
             tag="measured", source="data/processed/overnight/20_prices_ohlc.csv",
             bear=181.94, base=181.94, bull=181.94, unit="usd",
             note="last session in the price file"),
        dict(line="B. 4Q26 nights y/y, RNPL module",
             tag="derived", source="data/processed/rnpl_short_audit/rnpl_nights_module.csv",
             bear=6.58, base=7.61, bull=8.35, unit="pct",
             note="team baseline 8.90; guide language today is 'low double digits' for 3Q26 nights"),
        dict(line="C. 1Q27 nights y/y, RNPL module",
             tag="derived", source="data/processed/rnpl_short_audit/rnpl_nights_module.csv",
             bear=5.28, base=6.47, bull=7.34, unit="pct",
             note="against a +17.9% 1Q26 comp; module falsified if the 1Q27 guide is >= +8.2%"),
        dict(line="D. Implied 4Q26 nights guide vs the current 'low double digits' frame",
             tag="derived", source="B minus 10.0 (bottom of the 'low double' bucket, 02_guidance_ledger.csv)",
             bear=6.58 - 10.0, base=7.61 - 10.0, bull=8.35 - 10.0, unit="pp",
             note="the size of the KPI-language step-down the Street would have to absorb"),
        dict(line="E. Revenue-growth step implied by D",
             tag="", source="", bear=np.nan, base=np.nan, bull=np.nan, unit="pp",
             note="BLANK - needs the ADR and take-rate legs held flat or moved explicitly; "
                  "fill from data/processed/rnpl_short_audit/fy27_quarterly_phasing_rnpl_aware.csv "
                  "once the ADR path is agreed"),
        dict(line="F. Multiple effect: +0.48 turns of EV/EBITDA per point of forward revenue growth",
             tag="measured (repo regression)",
             source="research/notes/overnight/12_valuation-multiple-regime.md b=+0.48, t 8.3, 2023-26 monthly",
             bear=np.nan, base=np.nan, bull=np.nan, unit="turns",
             note="BLANK until E is filled. Applied ONCE, to E, and never also to a margin line "
                  "(margin's coefficient is statistically zero)."),
        dict(line="G. Reaction at the 5 Nov print - day-1 executable, from the analogue cell",
             tag="base rate",
             source="qog_momentum_cells.csv, cell '(b) nights DECELERATED while revenue BEAT'",
             bear=cell("(b) nights DECELERATED while revenue BEAT", "open_1d_excess_pct", "min_pct"),
             base=cell("(b) nights DECELERATED while revenue BEAT", "open_1d_excess_pct", "median_pct"),
             bull=cell("(b) nights DECELERATED while revenue BEAT", "open_1d_excess_pct", "max_pct"),
             unit="pct excess vs QQQ",
             note="executable entry. Day-one direction is NOT predictable (73% of the legacy day-1 "
                  "number is the untradable overnight gap); this is a dispersion, not a forecast."),
        dict(line="H. 20-session drift after the print, from the analogue cell",
             tag="base rate",
             source="qog_momentum_cells.csv, same cell, drift_20d_excess_pct",
             bear=cell("(b) nights DECELERATED while revenue BEAT", "drift_20d_excess_pct", "min_pct"),
             base=cell("(b) nights DECELERATED while revenue BEAT", "drift_20d_excess_pct", "median_pct"),
             bull=cell("(b) nights DECELERATED while revenue BEAT", "drift_20d_excess_pct", "max_pct"),
             unit="pct excess vs QQQ",
             note="quote as a base rate with a story; no p-value (RED_TEAM ruling)"),
        dict(line="I. 60-session drift after the print, same cell",
             tag="base rate",
             source="qog_momentum_cells.csv, same cell, drift_60d_excess_pct",
             bear=cell("(b) nights DECELERATED while revenue BEAT", "drift_60d_excess_pct", "min_pct"),
             base=cell("(b) nights DECELERATED while revenue BEAT", "drift_60d_excess_pct", "median_pct"),
             bull=cell("(b) nights DECELERATED while revenue BEAT", "drift_60d_excess_pct", "max_pct"),
             unit="pct excess vs QQQ",
             note="the 3-month leg of the path"),
        dict(line="J. February (1Q27 guide) print - the trade the audit prefers",
             tag="", source="", bear=np.nan, base=np.nan, bull=np.nan, unit="pct excess vs QQQ",
             note="BLANK - the analogue cell for 'guide implies a KPI deceleration against a hard comp' "
                  "has too few members to quote separately; fill from cell (c') once a Bloomberg "
                  "peer sample (BKNG/EXPE) widens n"),
        dict(line="K. Estimate-revision leg: FY27 revenue consensus change over the path",
             tag="", source="", bear=np.nan, base=np.nan, bull=np.nan, unit="pct",
             note="BLANK - needs Bloomberg BEst point-in-time FY27 revenue history (spec row 1). "
                  "Today's level is FY27 revenue $15,730M Zacks n=13 as of 11 Sep 2026 15:44 ET and "
                  "$15,757.8M Alpha Vantage n=44 same day (A1_consensus_vintages.md); no history."),
        dict(line="L. Total 3-to-12-month expected excess return",
             tag="", source="", bear=np.nan, base=np.nan, bull=np.nan, unit="pct",
             note="BLANK - it is F + H/I + K, and two of the three are blank. Do not sum G into it: "
                  "G is a one-day dispersion, not an expected return."),
        dict(line="M. Position sizing",
             tag="assumed",
             source="docs/rnpl-short-audit/00_SYNTHESIS.md item 7 (note 03)",
             bear=1.0, base=1.5, bull=2.0, unit="pct notional",
             note="underwrite to a +17% day: 7 Aug 2026 was +17.4% raw. 1-2% notional."),
        dict(line="N. Flip rule",
             tag="pre-registered",
             source="docs/rnpl-short-audit/00_SYNTHESIS.md section 2, D1_prereg_thresholds.csv",
             bear=np.nan, base=np.nan, bull=np.nan, unit="",
             note="3Q26 nights >= 10.3% or a 4Q26 nights guide >= 9.5% weakens; a 1Q27 guide "
                  ">= +8.2% falsifies the module outright."),
    ]
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- main


def main() -> None:
    inp = load_inputs()
    OUT.mkdir(parents=True, exist_ok=True)

    panel = build_panel(inp)
    recon = reconcile(panel, inp)
    cells, members = build_cells(panel)
    mom = momentum_today(inp)
    since = since_the_print(inp)
    spec = bloomberg_spec()
    path = return_path_skeleton(panel, cells)

    writes = {
        "qog_momentum_print_panel.csv": panel,
        "qog_momentum_reconciliation.csv": recon,
        "qog_momentum_cells.csv": cells,
        "qog_momentum_cell_members.csv": members,
        "qog_momentum_state_today.csv": mom,
        "qog_momentum_since_2026q2_print.csv": since,
        "qog_momentum_bloomberg_spec.csv": spec,
        "qog_momentum_return_path.csv": path,
    }
    for name, df in writes.items():
        if not name.startswith("qog_momentum_"):
            raise SystemExit(f"this script may only write qog_momentum_*.csv, got {name}")
        p = OUT / name
        df.to_csv(p, index=False)
        print(f"wrote {p}  ({len(df)} rows)")

    # console summary
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 60)
    print("\n--- reconciliation vs the repo ---")
    print(recon.to_string(index=False))
    print("\n--- headline cells (day-1 executable and 20d drift) ---")
    show = cells[cells["metric"].isin(["open_1d_excess_pct", "excess_1d_pct",
                                       "drift_20d_excess_pct", "drift_60d_excess_pct"])]
    print(show[["cell", "metric", "n", "mean_pct", "median_pct",
                "hit_rate_negative", "min_pct", "max_pct"]].to_string(index=False))
    print("\n--- the (b) cell, print by print ---")
    print(members[members["cell"] == "(b) nights DECELERATED while revenue BEAT"].to_string(index=False))
    print("\n--- momentum today ---")
    print(mom[mom["ticker"] == "ABNB"].to_string(index=False))
    print("\n--- since the 7 Aug 2026 print ---")
    print(since.to_string(index=False))

    w = panel[panel["in_requested_window"]]
    print("\n--- day-1 decomposition, 22 prints ---")
    print(f"mean |raw day-1|            {w['raw_1d_pct'].abs().mean():.2f}%")
    print(f"median |raw day-1|          {w['raw_1d_pct'].abs().median():.2f}%")
    print(f"mean |QQQ-excess day-1|     {w['excess_1d_pct'].abs().mean():.2f}%")
    print(f"mean |overnight gap|        {w['gap_pct'].abs().mean():.2f}%")
    print(f"mean |executable day-1|     {w['open_1d_excess_pct'].abs().mean():.2f}%")
    print(f"median gap share of |move|  {w['gap_share_of_day1_abs'].median():.1f}%")
    corr = w[['gap_excess_pct', 'excess_1d_pct']].corr().iloc[0, 1]
    print(f"corr(gap excess, day-1 excess) {corr:.3f}; "
          f"R^2 = {corr ** 2:.3f} (WS20 reports 0.89 / 73% on 23 prints)")


if __name__ == "__main__":
    main()
