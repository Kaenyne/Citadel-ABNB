"""worldcup_premium / calendar.py — PREREG section 5 (V1 excess booked share, V2 match-night spike, V3 booking timing,
V3b 2025 placebo) and section 7 (A1 Paris 2024 analog). "Unavailable" = booked or host-blocked (not separable)."""
from __future__ import annotations
import duckdb
import numpy as np
import pandas as pd
import statsmodels.api as sm
from . import config as C

ROUNDS = {  # PREREG section 5: December / March / June snapshots
    "los-angeles": {"Dec": "2025-12-04", "Mar": "2026-03-16", "Jun": "2026-06-15"},
    "mexico-city": {"Dec": "2025-12-29", "Mar": "2026-03-30", "Jun": "2026-06-15"},
    "chicago": {"Dec": "2025-12-25", "Mar": "2026-03-27", "Jun": "2026-06-24"},
    "austin": {"Dec": "2025-12-22", "Mar": "2026-03-25", "Jun": "2026-06-22"},
    "nashville": {"Dec": "2025-12-27", "Mar": "2026-03-28", "Jun": "2026-06-26"},
    "new-orleans": {"Dec": "2025-12-12", "Mar": "2026-03-19", "Jun": "2026-06-16"},
}
PLACEBO_2025 = {"los-angeles": "2025-03-01", "chicago": "2025-03-11", "austin": "2025-03-06", "nashville": "2025-03-15"}
V3_COMMON_FROM = pd.Timestamp("2026-06-27")    # after the latest June snapshot (26 Jun): T nights common to all rounds

_con = duckdb.connect()


def _read(f, with_price=False) -> str:
    cols = "listing_id, date::DATE AS date, (available = 'f')::INT AS unavail" + (", price" if with_price else "")
    return (f"SELECT {cols} FROM read_csv('{f.as_posix()}', header=true, quote='\"', escape='\"', all_varchar=true, "
            f"strict_mode=false, null_padding=true)")


def daily_unavail(market: str, snap: str, lo: str, hi: str) -> pd.DataFrame:
    """U(m, s, d) over active listings for dates lo..hi, plus the active-listing count."""
    f = C.IA_CAL / f"{market}_{snap}_calendar.csv.gz"
    q = f"""
    WITH c AS ({_read(f)}),
    act AS (SELECT listing_id FROM c GROUP BY listing_id
            HAVING avg(unavail) < {C.ACTIVE_MAX_BLOCKED} AND min(unavail) = 0)
    SELECT date, avg(unavail) AS U, count(*) AS n_active
    FROM c JOIN act USING (listing_id)
    WHERE date BETWEEN DATE '{lo}' AND DATE '{hi}' GROUP BY date ORDER BY date"""
    d = _con.execute(q).df()
    d["date"] = pd.to_datetime(d.date); d["market"] = market; d["snap"] = pd.Timestamp(snap)
    return d


def _x_stat(d: pd.DataFrame, t0, t1, a_windows) -> float:
    t = d[(d.date >= t0) & (d.date <= t1)].U.mean()
    a = d[C.in_windows(d.date, a_windows)].U.mean()
    return float(t - a)


def run_v(geo: pd.DataFrame, sched: pd.DataFrame) -> dict:
    venue_of = geo.drop_duplicates("market").set_index("market").nearest_venue.to_dict()
    daily = []
    for m, rs in ROUNDS.items():
        for rnd, s in rs.items():
            d = daily_unavail(m, s, "2026-05-14", "2026-08-16"); d["round"] = rnd; daily.append(d)
    daily = pd.concat(daily, ignore_index=True)
    daily["host"] = daily.market.isin(C.CAL_HOSTS)
    daily["match_night"] = [dt in C.match_nights(venue_of[m], sched) for dt, m in zip(daily.date, daily.market)]

    # V1 (literal PREREG: T and A nights on or after s + 1, per market)
    v1 = []
    for (m, rnd), d in daily.groupby(["market", "round"]):
        s = d.snap.iloc[0]; dd = d[d.date > s]
        v1.append({"market": m, "round": rnd, "snap": s.date(), "host": m in C.CAL_HOSTS,
                   "X": _x_stat(dd, C.T_START, C.T_END, C.A_WINDOWS), "n_active": int(d.n_active.median())})
    v1 = pd.DataFrame(v1)
    did = []
    for rnd in ["Dec", "Mar", "Jun"]:
        r = v1[v1["round"] == rnd]; ctl = r[~r.host].X.mean()
        for h in C.CAL_HOSTS:
            did.append({"round": rnd, "host": h, "X_host": float(r[r.market == h].X.iloc[0]), "X_controls_mean": float(ctl),
                        "excess_pp": 100 * float(r[r.market == h].X.iloc[0] - ctl)})
    v1_did = pd.DataFrame(did)

    # V3 booking timing on the common date set (T nights >= 27 Jun; A = the post window only, common to all rounds)
    v3 = []
    for (m, rnd), d in daily.groupby(["market", "round"]):
        v3.append({"market": m, "round": rnd, "host": m in C.CAL_HOSTS,
                   "X": _x_stat(d, V3_COMMON_FROM, C.T_END, [C.A_WINDOWS[1]])})
    v3 = pd.DataFrame(v3)
    tim = []
    for h in C.CAL_HOSTS:
        ex = {}
        for rnd in ["Dec", "Mar", "Jun"]:
            r = v3[v3["round"] == rnd]
            ex[rnd] = float(r[r.market == h].X.iloc[0] - r[~r.host].X.mean())
        tim.append({"host": h, **{f"excess_{k}_pp": 100 * v for k, v in ex.items()},
                    "share_before_Dec": ex["Dec"] / ex["Jun"] if ex["Jun"] else np.nan,
                    "share_Dec_to_Mar": (ex["Mar"] - ex["Dec"]) / ex["Jun"] if ex["Jun"] else np.nan,
                    "share_Mar_to_Jun": (ex["Jun"] - ex["Mar"]) / ex["Jun"] if ex["Jun"] else np.nan})
    timing = pd.DataFrame(tim)

    # V2 match-night spike (T nights after the snapshot; weekday + week FE), hosts and controls (pseudo)
    v2 = []
    for (m, rnd), d in daily.groupby(["market", "round"]):
        s = d.snap.iloc[0]
        dd = d[(d.date > s) & (d.date >= C.T_START) & (d.date <= C.T_END)].copy()
        if len(dd) < 12 or dd.match_night.nunique() < 2:
            continue
        X = pd.get_dummies(dd.date.dt.dayofweek.astype(str), prefix="dow", drop_first=True).astype(float)
        X = X.join(pd.get_dummies(dd.date.dt.isocalendar().week.astype(str), prefix="wk", drop_first=True).astype(float))
        X["match_night"] = dd.match_night.astype(float); X = sm.add_constant(X)
        r = sm.OLS(dd.U.to_numpy(), X.to_numpy()).fit(cov_type="HC1")
        k = list(X.columns).index("match_night")
        v2.append({"market": m, "round": rnd, "host": m in C.CAL_HOSTS, "n_dates": len(dd), "k_pp": 100 * r.params[k],
                   "lo_pp": 100 * r.conf_int(0.10)[k][0], "hi_pp": 100 * r.conf_int(0.10)[k][1], "p": r.pvalues[k]})
    v2 = pd.DataFrame(v2)

    # V3b placebo: the same X on the 2025 dates of T and A, March 2025 snapshots
    sh = pd.Timedelta(days=364); pl = []
    for m, s in PLACEBO_2025.items():
        d = daily_unavail(m, s, str((C.A_WINDOWS[0][0] - sh).date()), str((C.A_WINDOWS[1][1] - sh).date()))
        pl.append({"market": m, "snap": s, "host": m in C.CAL_HOSTS,
                   "X": _x_stat(d[d.date > d.snap], C.T_START - sh, C.T_END - sh, [(a - sh, b - sh) for a, b in C.A_WINDOWS])})
    pl = pd.DataFrame(pl)
    placebo = {"X_LA": float(pl[pl.host].X.iloc[0]), "X_controls_mean": float(pl[~pl.host].X.mean()),
               "excess_pp": 100 * float(pl[pl.host].X.iloc[0] - pl[~pl.host].X.mean()), "table": pl}
    return {"daily": daily, "v1": v1, "v1_did": v1_did, "v2": v2, "v3": v3, "timing": timing, "placebo_2025": placebo}


# ------------------------------------------------------------------------------------------------------------------ #
def run_a1() -> pd.DataFrame:
    """Paris 2024 Olympics vs Rome: same-listing listed-price premium and unavailable-share excess, per snapshot."""
    rows = []
    for city, snaps in (("paris", C.PARIS_SNAPS), ("rome", C.ROME_SNAPS)):
        for s in snaps:
            f = C.IA_CAL / f"{city}_{s}_calendar.csv.gz"
            (a1lo, a1hi), (a2lo, a2hi) = C.OLY_A
            q = f"""
            WITH c AS ({_read(f, with_price=True)}),
            act AS (SELECT listing_id FROM c GROUP BY listing_id HAVING avg(unavail) < {C.ACTIVE_MAX_BLOCKED} AND min(unavail) = 0),
            d AS (SELECT c.*, TRY_CAST(replace(replace(price, '$', ''), ',', '') AS DOUBLE) AS p,
                         CASE WHEN date BETWEEN DATE '{C.OLY[0].date()}' AND DATE '{C.OLY[1].date()}' THEN 'O'
                              WHEN date BETWEEN DATE '{a1lo.date()}' AND DATE '{a1hi.date()}'
                                OR date BETWEEN DATE '{a2lo.date()}' AND DATE '{a2hi.date()}' THEN 'A' END AS w
                  FROM c JOIN act USING (listing_id)),
            l AS (SELECT listing_id,
                         avg(CASE WHEN w = 'O' AND p > 0 THEN ln(p) END) AS lpO, avg(CASE WHEN w = 'A' AND p > 0 THEN ln(p) END) AS lpA,
                         avg(CASE WHEN w = 'O' THEN unavail END) AS uO, avg(CASE WHEN w = 'A' THEN unavail END) AS uA
                  FROM d WHERE w IS NOT NULL GROUP BY listing_id)
            SELECT count(*) AS n_listings, avg(lpO - lpA) AS dlogp, median(lpO - lpA) AS dlogp_median,
                   avg(uO) AS U_oly, avg(uA) AS U_adj FROM l WHERE lpO IS NOT NULL AND lpA IS NOT NULL"""
            r = _con.execute(q).df().iloc[0].to_dict()
            rows.append({"city": city, "snap": s, **r})
    a = pd.DataFrame(rows)
    a["premium"] = np.expm1(a.dlogp); a["U_excess_pp"] = 100 * (a.U_oly - a.U_adj)
    p = a[a.city == "paris"].reset_index(drop=True); r = a[a.city == "rome"].reset_index(drop=True)
    did = pd.DataFrame({"round": ["Mar", "May", "Jun"], "paris_snap": p.snap, "rome_snap": r.snap,
                        "price_premium_did": np.expm1(p.dlogp - r.dlogp), "U_excess_did_pp": p.U_excess_pp - r.U_excess_pp})
    return a, did
