"""WS-F step 2: turn F1's daily aggregates into a pace read, a y/y comparison and a backtest.

Inputs (all from F1, which is the only thing that touches raw dumps):
  F1_daily_levels.csv        market x vintage x stay_date, every listing in the dump
  F1_daily_transitions.csv   market x vintage pair x stay_date, listings in both dumps
  F1_pairs.csv               per pair coverage
Plus the main tree, read only: Theo's booking_curves_by_market.csv and the disclosed
quarterly KPI history.

Outputs in data/processed/q3nowcast/F/:
  F2_levels_by_horizon.csv     blocked share by horizon bucket, Theo's definition
  F2_theo_reconciliation.csv   ours vs Theo on the overlapping market x snapshot x horizon
  F2_transitions_by_horizon.csv  the pace metric: new blocks, reopenings, net change
  F2_yoy_levels.csv            y/y blocked share, calendar-matched vintage pairs
  F2_yoy_flows.csv             y/y of the net-blocking flow, calendar-matched pair of pairs
  F2_q3_in_progress.csv        late-quarter demand read for stay dates 15 Aug to 30 Sep
  F2_region_summary.csv        the above rolled to region, two weightings
  F2_backtest.csv              y/y flow against disclosed nights growth by quarter

Definitions. blocked share is a STOCK: blocked listing-nights over listing-nights, where
blocked = available='f' and so mixes bookings, host blocks and inactive or long-term-rental
calendars. new_block_rate is new blocks over nights that were available at v0; reopen_rate
is reopenings over nights blocked at v0; net_change_pp is the change in blocked share in
percentage points on the same listings and the same forward stay dates. None of these is a
booking count, and none can be validated against reported Nights and Seats Booked at the
level; only the y/y change in a flow has any chance of tracking the reported y/y.

Run: py -3.13 analysis/src/q3nowcast/F2_pace_metrics.py
"""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MAIN_TREE = Path(r"C:\Users\krish\citadel-abnb")
OUT = ROOT / "data/processed/q3nowcast/F"
THEO = MAIN_TREE / "data/processed/booking_curves_by_market.csv"
KPI = MAIN_TREE / "data/processed/abnb_driver_history_quarterly.csv"

LEVEL_BUCKETS = [("h000_030", 0, 30), ("h031_060", 31, 60), ("h061_090", 61, 90),
                 ("h091_180", 91, 180), ("h181_372", 181, 372)]
FLOW_BUCKETS = [("d001_030", 1, 30), ("d031_060", 31, 60), ("d061_090", 61, 90),
                ("d091_180", 91, 180), ("d001_180", 1, 180)]
# A y/y vintage pair must be about 365 days apart. The window has to be wide because the
# pair the brief names, Sep 2025 against Aug 2026, is only 330 to 350 days apart; the new
# 2025 monthlies give tight pairs too, so every row carries vintage_offset_days and a
# tight_pair flag (|offset| <= 10 days) and the note reports both.
YEAR_LO, YEAR_HI = 330, 400
TWO_YEAR_LO, TWO_YEAR_HI = 330 + 365, 400 + 365
TIGHT_OFFSET = 10
INTERVAL_TOL = 21                    # the two booking intervals within 3 weeks
Q3_WINDOW = ("08-15", "09-30")       # the late-quarter window the brief asks for


def read_path(stem):
    """F1 writes the daily tables gzipped; fall back to plain csv if one is lying around."""
    gz = OUT / f"{stem}.csv.gz"
    return gz if gz.exists() else OUT / f"{stem}.csv"


def wavg(frame, value, weight):
    w = frame[weight].sum()
    return float((frame[value] * frame[weight]).sum() / w) if w else np.nan


# ------------------------------------------------------------------ A. levels by horizon
def levels_by_horizon(levels):
    frames = []
    for name, lo, hi in LEVEL_BUCKETS:
        sub = levels[levels.days_ahead.between(lo, hi)]
        g = (sub.groupby(["market", "region", "snapshot_date"], dropna=False)
             [["listing_nights", "blocked_nights"]].sum().reset_index())
        g["horizon"] = name
        frames.append(g)
    out = pd.concat(frames, ignore_index=True)
    out["blocked_share"] = out.blocked_nights / out.listing_nights
    # listings per dump is not recoverable from a daily aggregate; use peak nights as scale
    scale = (levels.groupby(["market", "snapshot_date"]).listing_nights.max()
             .rename("max_listings_any_night").reset_index())
    out = out.merge(scale, on=["market", "snapshot_date"], how="left")
    return out.sort_values(["market", "snapshot_date", "horizon"])


# ---------------------------------------------------------------- B. Theo reconciliation
def theo_reconcile(ours):
    if not THEO.exists():
        return pd.DataFrame()
    theo = pd.read_csv(THEO)
    theo = theo.rename(columns={"blocked_rate": "theo_blocked_rate",
                                "listing_nights": "theo_listing_nights",
                                "listings": "theo_listings"})
    merged = ours.merge(theo[["market", "snapshot_date", "horizon", "theo_listing_nights",
                              "theo_listings", "theo_blocked_rate"]],
                        on=["market", "snapshot_date", "horizon"], how="inner")
    merged["diff_pp"] = (merged.blocked_share - merged.theo_blocked_rate) * 100
    merged["night_ratio"] = merged.listing_nights / merged.theo_listing_nights
    return merged.sort_values(["market", "horizon"])


# ------------------------------------------------------- C. the pace metric, by horizon
def transitions_by_horizon(trans):
    frames = []
    for name, lo, hi in FLOW_BUCKETS:
        sub = trans[trans.days_ahead_v1.between(lo, hi)]
        g = (sub.groupby(["market", "region", "snapshot0", "snapshot1", "regime"], dropna=False)
             [["matched_nights", "blocked_v0", "blocked_v1", "new_blocks", "reopenings"]]
             .sum().reset_index())
        g["horizon"] = name
        frames.append(g)
    out = pd.concat(frames, ignore_index=True)
    out["interval_days"] = ((pd.to_datetime(out.snapshot1) - pd.to_datetime(out.snapshot0))
                            .dt.days)
    out["available_v0"] = out.matched_nights - out.blocked_v0
    out["blocked_share_v0"] = out.blocked_v0 / out.matched_nights
    out["blocked_share_v1"] = out.blocked_v1 / out.matched_nights
    out["net_change_pp"] = (out.blocked_share_v1 - out.blocked_share_v0) * 100
    out["new_block_rate_pct"] = out.new_blocks / out.available_v0.replace(0, np.nan) * 100
    out["reopen_rate_pct"] = out.reopenings / out.blocked_v0.replace(0, np.nan) * 100
    out["net_change_pp_per_30d"] = out.net_change_pp / out.interval_days * 30
    out["new_block_rate_pct_per_30d"] = out.new_block_rate_pct / out.interval_days * 30
    return out.sort_values(["market", "snapshot1", "regime", "horizon"])


# ---------------------------------------------------- D. year over year, levels, matched
def yoy_vintage_pairs(snapshots):
    """[(market, early, late, offset_days)] for vintage pairs about 365 days apart."""
    pairs = []
    for market, dates in snapshots.items():
        ds = sorted(pd.to_datetime(dates).unique())
        for late in ds:
            for early in ds:
                gap = (late - early).days
                if YEAR_LO <= gap <= YEAR_HI:
                    pairs.append((market, str(early.date()), str(late.date()), gap - 365))
    return pairs


def yoy_levels(lv):
    snapshots = lv.groupby("market").snapshot_date.unique().to_dict()
    pairs = yoy_vintage_pairs(snapshots)
    idx = lv.set_index(["market", "snapshot_date", "horizon"])
    rows = []
    for market, early, late, offset in pairs:
        region = lv.loc[lv.market == market, "region"].iloc[0]
        for name, _, _ in LEVEL_BUCKETS:
            try:
                a = idx.loc[(market, early, name)]
                b = idx.loc[(market, late, name)]
            except KeyError:
                continue
            rows.append(dict(market=market, region=region, horizon=name,
                             snapshot_prior=early, snapshot_current=late,
                             vintage_offset_days=offset,
                             tight_pair=bool(abs(offset) <= TIGHT_OFFSET),
                             listing_nights_prior=int(a.listing_nights),
                             listing_nights_current=int(b.listing_nights),
                             blocked_share_prior=float(a.blocked_share),
                             blocked_share_current=float(b.blocked_share),
                             yoy_diff_pp=float(b.blocked_share - a.blocked_share) * 100,
                             yoy_rel_pct=float(b.blocked_share / a.blocked_share - 1) * 100,
                             # a level y/y is contaminated by supply: a new listing arrives
                             # with an empty calendar and pushes the blocked share down
                             # mechanically, so this column has to be read beside it
                             listing_nights_change_pct=float(
                                 b.listing_nights / a.listing_nights - 1) * 100))
    out = pd.DataFrame(rows)
    return out.sort_values(["snapshot_current", "market", "horizon"]) if len(out) else out


# ----------------------------------------------------- F. year over year, the flow pairs
def yoy_flows(tr):
    """Compare a 2026 vintage pair with the same-season pair a year earlier."""
    key = tr[["market", "region", "snapshot0", "snapshot1", "interval_days"]].drop_duplicates()
    key["s0"] = pd.to_datetime(key.snapshot0)
    key["s1"] = pd.to_datetime(key.snapshot1)
    idx = tr.set_index(["market", "snapshot0", "snapshot1", "regime", "horizon"])
    rows = []
    for market, g in key.groupby("market"):
        for _, cur in g.iterrows():
            for _, pri in g.iterrows():
                g0 = (cur.s0 - pri.s0).days
                g1 = (cur.s1 - pri.s1).days
                ok_one = YEAR_LO <= g0 <= YEAR_HI and YEAR_LO <= g1 <= YEAR_HI
                ok_two = (TWO_YEAR_LO <= g0 <= TWO_YEAR_HI
                          and TWO_YEAR_LO <= g1 <= TWO_YEAR_HI)
                if not (ok_one or ok_two):
                    continue
                if abs(cur.interval_days - pri.interval_days) > INTERVAL_TOL:
                    continue
                for regime in ("all", "screened"):
                    for name, _, _ in FLOW_BUCKETS:
                        try:
                            a = idx.loc[(market, pri.snapshot0, pri.snapshot1, regime, name)]
                            b = idx.loc[(market, cur.snapshot0, cur.snapshot1, regime, name)]
                        except KeyError:
                            continue
                        rows.append(dict(
                            market=market, region=cur.region, regime=regime, horizon=name,
                            prior_pair=f"{pri.snapshot0}->{pri.snapshot1}",
                            current_pair=f"{cur.snapshot0}->{cur.snapshot1}",
                            prior_interval_days=int(pri.interval_days),
                            current_interval_days=int(cur.interval_days),
                            years_back=int(round(g0 / 365)),
                            start_offset_days=g0 - 365 * round(g0 / 365),
                            end_offset_days=g1 - 365 * round(g1 / 365),
                            match_score=(abs(g0 - 365 * round(g0 / 365))
                                         + abs(g1 - 365 * round(g1 / 365))
                                         + abs(cur.interval_days - pri.interval_days)),
                            tight_pair=bool(abs(g0 - 365 * round(g0 / 365)) <= TIGHT_OFFSET
                                            and abs(g1 - 365 * round(g1 / 365)) <= TIGHT_OFFSET),
                            matched_nights_prior=int(a.matched_nights),
                            matched_nights_current=int(b.matched_nights),
                            net_change_pp_prior=float(a.net_change_pp_per_30d),
                            net_change_pp_current=float(b.net_change_pp_per_30d),
                            net_change_yoy_pp=float(b.net_change_pp_per_30d - a.net_change_pp_per_30d),
                            new_block_rate_prior=float(a.new_block_rate_pct_per_30d),
                            new_block_rate_current=float(b.new_block_rate_pct_per_30d),
                            new_block_rate_yoy_pct=float(
                                b.new_block_rate_pct_per_30d / a.new_block_rate_pct_per_30d - 1) * 100
                            if a.new_block_rate_pct_per_30d else np.nan,
                            reopen_rate_prior=float(a.reopen_rate_pct),
                            reopen_rate_current=float(b.reopen_rate_pct)))
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    # Several prior pairs can sit near one anniversary once a market has monthly dumps.
    # Keep only the closest, so nothing is counted twice downstream.
    keep = ["market", "regime", "horizon", "current_pair", "years_back"]
    out = (out.sort_values(keep + ["match_score"])
           .drop_duplicates(keep, keep="first").reset_index(drop=True))
    return out


# ------------------------------------------------- E. the late-quarter in-progress read
def window_read(levels, trans, window=Q3_WINDOW, years=(2025, 2026)):
    """Blocked share for a fixed calendar stay window, at the latest vintage of each year
    that precedes the window end.

    Two things have to be equalised or the y/y is an artefact. First the stay window: the
    2026 dumps land in late August and the 2025 dumps for some markets only in mid
    September, so the window is trimmed to the day-of-year range both years can cover, per
    market. Second the lead time: even with the same stay dates the 2026 read sits a few
    days further from the stay date than the 2025 read, or nearer, and the blocked stock
    builds as the stay date approaches. That offset is priced with a slope measured on the
    market's own forward pair over the same stay dates, not with a borrowed curve.
    """
    lv = levels.copy()
    lv["stay"] = pd.to_datetime(lv.stay_date)
    lv["snap"] = pd.to_datetime(lv.snapshot_date)
    rows = []
    for (market, region), g in lv.groupby(["market", "region"], dropna=False):
        # The current year uses its latest vintage before the window closes. The prior year
        # uses the vintage closest to the SAME month and day, not its own latest, because
        # matching lead time matters more than squeezing out a few more stay dates.
        current = max(years)
        chosen = {}
        end_cur = pd.Timestamp(f"{current}-{window[1]}")
        cands = [d for d in sorted(g.snap.unique()) if d <= end_cur]
        if not cands:
            continue
        chosen[current] = pd.Timestamp(cands[-1])
        anchor = chosen[current].dayofyear
        for year in years:
            if year == current:
                continue
            end_ts = pd.Timestamp(f"{year}-{window[1]}")
            pool = [pd.Timestamp(d) for d in sorted(g.snap.unique())
                    if pd.Timestamp(d) <= end_ts and pd.Timestamp(d).year == year]
            if not pool:
                continue
            chosen[year] = min(pool, key=lambda d: abs(d.dayofyear - anchor))
        if len(chosen) < len(years):
            continue
        # Common calendar window. Align on month and day, not day of year, and trim the
        # start forward until the window is a whole number of weeks, because a window with
        # an unbalanced weekday mix moves the blocked share by about a point on its own.
        latest_md = max((snap.month, snap.day) for snap in chosen.values())
        nominal_md = tuple(int(x) for x in window[0].split("-"))
        start_md = max(latest_md, nominal_md)
        end_md = tuple(int(x) for x in window[1].split("-"))
        lengths = []
        for year in chosen:
            first = pd.Timestamp(year=year, month=start_md[0], day=start_md[1])
            last = pd.Timestamp(year=year, month=end_md[0], day=end_md[1])
            lengths.append((last - first).days + 1)
        length = min(lengths)
        length -= length % 7
        if length < 7:
            continue
        per_year = {}
        for year, snap in chosen.items():
            last = pd.Timestamp(year=year, month=end_md[0], day=end_md[1])
            first = last - pd.Timedelta(days=length - 1)
            sub = g[(g.snap == snap) & g.stay.between(first, last)]
            if sub.empty or sub.listing_nights.sum() == 0:
                per_year = {}
                break
            nights = sub.listing_nights.sum()
            per_year[year] = dict(
                snapshot=str(snap.date()), first=str(first.date()), last=str(last.date()),
                stay_days=int(len(sub)), listing_nights=int(nights),
                blocked_share=float(sub.blocked_nights.sum() / nights),
                mean_days_ahead=float((sub.days_ahead * sub.listing_nights).sum() / nights))
        if not per_year:
            continue
        rec = dict(market=market, region=region, window_length_days=int(length))
        for year, v in per_year.items():
            for k, val in v.items():
                rec[f"{k}_{year}"] = val
        rows.append(rec)
    panel = pd.DataFrame(rows)
    if panel.empty:
        return panel
    lo, hi = min(years), max(years)
    panel["yoy_diff_pp"] = (panel[f"blocked_share_{hi}"] - panel[f"blocked_share_{lo}"]) * 100
    panel["yoy_rel_pct"] = (panel[f"blocked_share_{hi}"] / panel[f"blocked_share_{lo}"] - 1) * 100
    panel["horizon_offset_days"] = (panel[f"mean_days_ahead_{hi}"]
                                    - panel[f"mean_days_ahead_{lo}"])
    panel["stay_days_match"] = panel[f"stay_days_{hi}"] == panel[f"stay_days_{lo}"]
    panel = panel.merge(horizon_slope(trans, window, hi), on="market", how="left")
    panel["offset_adjustment_pp"] = panel.slope_pp_per_day * panel.horizon_offset_days
    panel["yoy_diff_pp_adjusted"] = panel.yoy_diff_pp - panel.offset_adjustment_pp
    return panel


def horizon_slope(trans, window, year):
    """d(blocked share)/d(days ahead), in pp per day, measured on the SAME stay dates from
    the market's own latest vintage pair that spans the window. This is the only honest way
    to price a vintage-date offset: it does not borrow a cross-sectional curve."""
    t = trans[trans.regime == "all"].copy()
    t["stay"] = pd.to_datetime(t.stay_date)
    start, end = pd.Timestamp(f"{year}-{window[0]}"), pd.Timestamp(f"{year}-{window[1]}")
    t = t[t.stay.between(start, end)]
    if t.empty:
        return pd.DataFrame(columns=["market", "slope_pp_per_day", "slope_pair"])
    t["interval"] = (pd.to_datetime(t.snapshot1) - pd.to_datetime(t.snapshot0)).dt.days
    rows = []
    for market, g in t.groupby("market"):
        last = g.snapshot1.max()
        g = g[g.snapshot1 == last]
        nights = g.matched_nights.sum()
        if not nights:
            continue
        s0 = g.blocked_v0.sum() / nights
        s1 = g.blocked_v1.sum() / nights
        interval = int(g.interval.iloc[0])
        # v1 is interval days closer to the stay date, so the slope against days ahead is
        # negative when the blocked stock builds as the stay date approaches.
        rows.append(dict(market=market, slope_pp_per_day=(s0 - s1) * 100 / interval,
                         slope_pair=f"{g.snapshot0.iloc[0]}->{last}"))
    return pd.DataFrame(rows)


# ----------------------------------------------------------------- G. region roll-up
ROLLUP_KEYS = ("region", "horizon", "current_pair", "snapshot_current", "regime",
               "years_back", "tight_pair")


def region_rollup(frame, value_cols, weight=None, label=""):
    """Roll market rows to region. Two weightings are reported because neither is right:
    the nights-weighted figure is weighted by Inside Airbnb listing coverage, which is not
    Airbnb's market mix, and the median treats a 300-listing wine region and London alike."""
    keys_present = [c for c in ROLLUP_KEYS if c in frame.columns]
    rows = []
    for keys, g in frame.groupby(keys_present, dropna=False):
        rec = dict(zip(keys_present, keys if isinstance(keys, tuple) else (keys,)))
        rec["metric_set"] = label
        rec["n_markets"] = int(g.market.nunique())
        for col in value_cols:
            if col not in g:
                continue
            rec[f"{col}_median"] = float(g[col].median())
            if weight and weight in g:
                rec[f"{col}_wtd"] = wavg(g.dropna(subset=[col, weight]), col, weight)
        rows.append(rec)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------- H. backtest
def backtest(flows):
    """Assign each flow pair to the quarter its booking window mostly falls in, then put
    the pooled y/y flow next to disclosed nights growth for that quarter."""
    if flows.empty:
        return pd.DataFrame()
    f = flows[(flows.regime == "screened") & (flows.horizon == "d001_180")
              & (flows.years_back == 1)].copy()
    if f.empty:
        return pd.DataFrame()
    f[["c0", "c1"]] = f.current_pair.str.split("->", expand=True)
    mid = pd.to_datetime(f.c0) + (pd.to_datetime(f.c1) - pd.to_datetime(f.c0)) / 2
    f["quarter"] = mid.dt.year.astype(str) + "Q" + mid.dt.quarter.astype(str)
    # One market can offer several booking windows inside a quarter once it has monthly
    # dumps. Keep the best-matched window per market and quarter so the pooled figure is not
    # a weighted average of overlapping windows.
    f = (f.sort_values(["market", "quarter", "match_score"])
         .drop_duplicates(["market", "quarter"], keep="first"))
    kpi = pd.read_csv(KPI)
    kpi["q_key"] = kpi.year.astype(str) + "Q" + kpi.q.astype(str)
    target = kpi.set_index("q_key")[["nights_m", "nights_m_yoy_pct"]]
    rows = []
    for quarter, g in f.groupby("quarter"):
        rec = dict(quarter=quarter,
                   current_pairs=";".join(sorted(g.current_pair.unique())),
                   n_markets=int(g.market.nunique()),
                   markets=",".join(sorted(g.market.unique())),
                   n_tight=int(g.tight_pair.sum()),
                   median_match_score_days=float(g.match_score.median()),
                   net_change_yoy_pp_median=float(g.net_change_yoy_pp.median()),
                   net_change_yoy_pp_wtd=wavg(g.dropna(subset=["net_change_yoy_pp"]),
                                              "net_change_yoy_pp", "matched_nights_current"),
                   new_block_rate_yoy_pct_median=float(g.new_block_rate_yoy_pct.median()),
                   new_block_rate_yoy_pct_wtd=wavg(g.dropna(subset=["new_block_rate_yoy_pct"]),
                                                   "new_block_rate_yoy_pct",
                                                   "matched_nights_current"))
        if quarter in target.index:
            rec["disclosed_nights_yoy_pct"] = float(target.loc[quarter, "nights_m_yoy_pct"])
            pos = list(target.index).index(quarter)
            if pos >= 1:
                rec["naive_prior_quarter_yoy_pct"] = float(
                    target.iloc[pos - 1]["nights_m_yoy_pct"])
            if pos >= 4:
                rec["naive_prior_year_same_quarter_yoy_pct"] = float(
                    target.iloc[pos - 4]["nights_m_yoy_pct"])
        rows.append(rec)
    out = pd.DataFrame(rows).sort_values("quarter")
    # A walk-forward RMSE ratio is not computable here: the flow y/y exists for a handful of
    # quarters in four markets, so the naive columns are printed for comparison only and no
    # skill statistic is claimed.
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    levels = pd.read_csv(read_path("F1_daily_levels"))
    trans = pd.read_csv(read_path("F1_daily_transitions"))
    print(f"levels {len(levels):,} rows, {levels.market.nunique()} markets, "
          f"{levels.groupby('market').snapshot_date.nunique().sum()} vintages", flush=True)
    print(f"transitions {len(trans):,} rows", flush=True)

    lv = levels_by_horizon(levels)
    lv.to_csv(OUT / "F2_levels_by_horizon.csv", index=False)
    print(f"F2_levels_by_horizon.csv {len(lv):,} rows", flush=True)

    rec = theo_reconcile(lv)
    rec.to_csv(OUT / "F2_theo_reconciliation.csv", index=False)
    if len(rec):
        print(f"Theo reconciliation: {rec.market.nunique()} markets, {len(rec)} cells, "
              f"median |diff| {rec.diff_pp.abs().median():.3f} pp, "
              f"max |diff| {rec.diff_pp.abs().max():.3f} pp, "
              f"median night ratio {rec.night_ratio.median():.4f}", flush=True)

    tb = transitions_by_horizon(trans)
    tb.to_csv(OUT / "F2_transitions_by_horizon.csv", index=False)
    print(f"F2_transitions_by_horizon.csv {len(tb):,} rows", flush=True)

    yl = yoy_levels(lv)
    yl.to_csv(OUT / "F2_yoy_levels.csv", index=False)
    print(f"F2_yoy_levels.csv {len(yl):,} rows, "
          f"{yl.market.nunique() if len(yl) else 0} markets", flush=True)

    yf = yoy_flows(tb)
    yf.to_csv(OUT / "F2_yoy_flows.csv", index=False)
    print(f"F2_yoy_flows.csv {len(yf):,} rows, "
          f"{yf.market.nunique() if len(yf) else 0} markets", flush=True)

    q3 = window_read(levels, trans)
    q3.to_csv(OUT / "F2_q3_in_progress.csv", index=False)
    print(f"F2_q3_in_progress.csv {len(q3):,} rows", flush=True)

    summaries = []
    if len(yl):
        summaries.append(region_rollup(yl, ["yoy_diff_pp", "yoy_rel_pct",
                                            "blocked_share_current", "blocked_share_prior"],
                                       weight="listing_nights_current", label="yoy_levels"))
    if len(yf):
        summaries.append(region_rollup(yf, ["net_change_yoy_pp", "new_block_rate_yoy_pct",
                                            "net_change_pp_current", "net_change_pp_prior"],
                                       weight="matched_nights_current", label="yoy_flows"))
    if len(q3):
        q3r = q3.copy()
        q3r["horizon"] = "stay_aug15_sep30"
        summaries.append(region_rollup(q3r, ["yoy_diff_pp", "yoy_diff_pp_adjusted",
                                             "horizon_offset_days", "offset_adjustment_pp"],
                                       weight="listing_nights_2026", label="q3_window"))
    if summaries:
        reg = pd.concat(summaries, ignore_index=True)
        reg.to_csv(OUT / "F2_region_summary.csv", index=False)
        print(f"F2_region_summary.csv {len(reg):,} rows", flush=True)

    bt = backtest(yf)
    bt.to_csv(OUT / "F2_backtest.csv", index=False)
    print(f"F2_backtest.csv {len(bt):,} rows", flush=True)
    if len(bt):
        print(bt[["quarter", "n_markets", "n_tight", "net_change_yoy_pp_wtd",
                  "new_block_rate_yoy_pct_wtd", "disclosed_nights_yoy_pct"]]
              .to_string(index=False), flush=True)


if __name__ == "__main__":
    main()
