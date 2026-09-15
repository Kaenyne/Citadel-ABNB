"""C2: use the daio repo's git history (one commit per daily data update since June 2022) for
(a) a revision check: how much do the last 7 days of a yearly file change between commits about
    a week apart (median absolute revision, eu40 and eu_core flt_da);
(b) a true point-in-time qtd75 reading per quarter: days 1 to 75 of the quarter vs the same 75
    calendar days a year earlier, read from the yearly file(s) as of the first commit whose data
    reaches day 75 (the vintage observable on about day 76).

Build C of the GitHub alt-data integration plan, 14 Sep 2026 (compiled with Claude Code).
Mirror: C:/Users/krish/abnb_ia_capture/euctrl_daio_git (git clone https://github.com/euctrl-pru/daio).
Outputs: data/processed/govdata_v2/git_commits.csv, revision_check.csv, revision_summary.csv,
qtd75_pit.csv.
Run: python analysis/src/govdata_v2/C2_vintages.py
"""
from __future__ import annotations

import io
import os
import subprocess
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from C1_collect import EU_CORE, read_daio  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "govdata_v2")
MIRROR = os.environ.get("DAIO_GIT", os.path.join(os.path.expanduser("~"), "abnb_ia_capture", "euctrl_daio_git"))
QTD_DAYS = 75


def log(*a):
    print(*a, flush=True)


def git(*args):
    return subprocess.run(["git", "-C", MIRROR, *args], capture_output=True, check=True).stdout


def commits():
    txt = git("log", "--format=%H|%cI", "--date-order").decode()
    rows = [dict(commit=l.split("|")[0], committed=l.split("|")[1]) for l in txt.strip().splitlines()]
    c = pd.DataFrame(rows)
    c["committed"] = pd.to_datetime(c.committed, utc=True)
    c = c.sort_values("committed").reset_index(drop=True)
    c["files"] = ""
    c.to_csv(os.path.join(OUT, "git_commits.csv"), index=False)
    return c


_cache: dict[tuple[str, int], pd.DataFrame | None] = {}


def file_at(commit, year):
    key = (commit, year)
    if key not in _cache:
        try:
            raw = git("show", f"{commit}:daio_{year}.csv")
            d = read_daio(io.BytesIO(raw))
            core = d[d.country_name.isin(EU_CORE)]
            agg = pd.DataFrame({"eu40_flt_da": d.groupby("entry_date").flt_da.sum(),
                                "eu_core_flt_da": core.groupby("entry_date").flt_da.sum(),
                                "n_states": d.groupby("entry_date").country_name.nunique()}).sort_index()
            _cache[key] = agg
        except subprocess.CalledProcessError:
            _cache[key] = None
    return _cache[key]


# ------------------------------------------------------------------ (a) revision check
def revision_check(c):
    rows = []
    anchors = []
    last = None
    for i, r in c.iterrows():
        if last is None or (r.committed - last).days >= 7:
            anchors.append(i)
            last = r.committed
    log(f"revision check: {len(anchors)} anchor commits")
    for i in anchors:
        t0 = c.at[i, "committed"]
        later = c[(c.committed >= t0 + pd.Timedelta(days=5)) & (c.committed <= t0 + pd.Timedelta(days=10))]
        if later.empty:
            continue
        j = later.index[0]
        year = t0.year
        a = file_at(c.at[i, "commit"], year)
        b = file_at(c.at[j, "commit"], year)
        if a is None or b is None or a.empty:
            continue
        days = a.index[-7:]
        for dday in days:
            if dday not in b.index:
                continue
            rows.append(dict(commit_a=c.at[i, "commit"][:10], date_a=t0.date(), commit_b=c.at[j, "commit"][:10], date_b=c.at[j, "committed"].date(),
                             entry_date=dday.date(), days_before_commit_a=(t0.tz_convert(None).normalize() - dday).days,
                             eu40_a=a.at[dday, "eu40_flt_da"], eu40_b=b.at[dday, "eu40_flt_da"],
                             eu_core_a=a.at[dday, "eu_core_flt_da"], eu_core_b=b.at[dday, "eu_core_flt_da"]))
    rv = pd.DataFrame(rows)
    rv["eu40_rev"] = rv.eu40_b - rv.eu40_a
    rv["eu40_rev_pct"] = 100 * rv.eu40_rev / rv.eu40_a
    rv["eu_core_rev"] = rv.eu_core_b - rv.eu_core_a
    rv["eu_core_rev_pct"] = 100 * rv.eu_core_rev / rv.eu_core_a
    rv.to_csv(os.path.join(OUT, "revision_check.csv"), index=False)
    summ = []
    for label, sub in [("all 7 days", rv), ("last day only", rv[rv.days_before_commit_a == rv.groupby("commit_a").days_before_commit_a.transform("min")]),
                       ("2025 onward", rv[pd.to_datetime(rv.entry_date) >= "2025-01-01"])]:
        summ.append(dict(subset=label, n_pairs=sub.commit_a.nunique(), n_days=len(sub),
                         eu40_median_abs_rev=sub.eu40_rev.abs().median(), eu40_median_abs_rev_pct=sub.eu40_rev_pct.abs().median(),
                         eu40_p90_abs_rev_pct=sub.eu40_rev_pct.abs().quantile(0.9), eu40_share_nonzero=(sub.eu40_rev != 0).mean(),
                         eu_core_median_abs_rev=sub.eu_core_rev.abs().median(), eu_core_median_abs_rev_pct=sub.eu_core_rev_pct.abs().median(),
                         eu_core_p90_abs_rev_pct=sub.eu_core_rev_pct.abs().quantile(0.9), mean_signed_rev_pct_eu40=sub.eu40_rev_pct.mean()))
    summ = pd.DataFrame(summ)
    summ.to_csv(os.path.join(OUT, "revision_summary.csv"), index=False)
    log(summ.to_string(index=False))
    return rv, summ


# ------------------------------------------------------------------ (b) PIT qtd75
def quarter_starts(first="2022-07-01", last="2026-07-01"):
    return pd.date_range(first, last, freq="QS")


def qlab(ts):
    return f"{(ts.month - 1) // 3 + 1}Q{ts.year % 100:02d}"


def qtd75_from(agg_cur, agg_prev, q0):
    """agg_cur: daily frame holding the quarter's year; agg_prev: holding the prior year (may be the same frame)."""
    d_cur = pd.date_range(q0, periods=QTD_DAYS)
    d_prev = pd.date_range(q0 - pd.DateOffset(years=1), periods=QTD_DAYS)
    cur = agg_cur.reindex(d_cur)
    prev = agg_prev.reindex(d_prev)
    out = {}
    for col in ["eu40_flt_da", "eu_core_flt_da"]:
        ok = cur[col].notna().sum() == QTD_DAYS and prev[col].notna().sum() == QTD_DAYS
        out[col + "_cur"] = cur[col].sum() if ok else np.nan
        out[col + "_prev"] = prev[col].sum() if ok else np.nan
        out[col + "_yoy"] = (100 * (cur[col].sum() / prev[col].sum() - 1)) if ok else np.nan
    out["days_cur_present"] = int(cur["eu40_flt_da"].notna().sum())
    return out


def pit_qtd75(c):
    rows = []
    for q0 in quarter_starts():
        day75 = q0 + pd.Timedelta(days=QTD_DAYS - 1)
        # the first commit whose file reaches day 75 (search commits from day 75 onward)
        cand = c[c.committed >= pd.Timestamp(day75, tz="UTC")]
        picked = None
        for _, r in cand.head(40).iterrows():
            a = file_at(r.commit, q0.year)
            if a is not None and day75 in a.index:
                picked = r
                break
        if picked is None:
            rows.append(dict(quarter=qlab(q0), q_start=q0.date(), day75=day75.date(), commit="", commit_date=None, lag_days=np.nan, note="no commit with day 75 present"))
            continue
        a = file_at(picked.commit, q0.year)
        prev_year = q0.year - 1 if q0.month == 1 else q0.year
        # the prior-year window for Q1 lies in the previous year's file; for Q2-Q4 in the same file? no: same calendar days one year earlier -> previous year's file
        b = file_at(picked.commit, q0.year - 1)
        vals = qtd75_from(a, b if b is not None else a, q0)
        rows.append(dict(quarter=qlab(q0), q_start=q0.date(), day75=day75.date(), commit=picked.commit[:10], commit_date=picked.committed.date(),
                         lag_days=(picked.committed.tz_convert(None).normalize() - day75).days, last_entry_in_file=a.index.max().date(),
                         note="", **vals))
    p = pd.DataFrame(rows)
    p.to_csv(os.path.join(OUT, "qtd75_pit.csv"), index=False)
    log(p[["quarter", "day75", "commit", "commit_date", "lag_days", "eu40_flt_da_yoy", "eu_core_flt_da_yoy", "note"]].to_string(index=False))
    return p


def main():
    c = commits()
    log(f"{len(c)} commits, {c.committed.min().date()} to {c.committed.max().date()}")
    revision_check(c)
    pit_qtd75(c)


if __name__ == "__main__":
    main()
