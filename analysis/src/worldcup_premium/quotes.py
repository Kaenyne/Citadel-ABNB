"""worldcup_premium / quotes.py — PREREG section 2 (geography) and section 4 (price: P1, P2, P3).
Asking prices only: price_quote_price_per_night on the quoted stay [check-in, check-out), 2026 pre-fee basis."""
from __future__ import annotations
import itertools
import re
import numpy as np
import pandas as pd
from . import config as C
from .fe import ols_fe, lincomb

SNAP_RE = re.compile(r"^(united-states|canada|mexico)_(.+)_(\d{4}-\d{2}-\d{2})_listings\.csv\.gz$")
USE = ["id", "latitude", "longitude", "room_type", "accommodates", "bedrooms", "neighbourhood_cleansed",
       "price_quote_checkin_date", "price_quote_checkout_date", "price_quote_price_per_night", "estimated_occupancy_l365d"]


def snapshot_files() -> pd.DataFrame:
    rows = []
    for f in sorted(C.IA_SNAP.glob("*_2026-*_listings.csv.gz")):
        m = SNAP_RE.match(f.name)
        if m:
            rows.append({"file": f, "market": m.group(2).split("_")[-1], "market_key": f"{m.group(1)}_{m.group(2)}",
                         "scrape": pd.Timestamp(m.group(3))})
    return pd.DataFrame(rows)


def geography(snaps: pd.DataFrame) -> pd.DataFrame:
    """Market centroid from its 2026 listings; nearest venue; host / ring / control (PREREG section 2)."""
    rows = []
    for _, r in snaps.iterrows():
        x = pd.read_csv(r.file, usecols=["latitude", "longitude"])
        lat, lon = float(x.latitude.mean()), float(x.longitude.mean())
        v, km = C.nearest_venue(lat, lon)
        rows.append({"market": r.market, "market_key": r.market_key, "scrape": r.scrape.date(), "lat": lat, "lon": lon,
                     "nearest_venue": v, "km": km, "cls": C.classify(km)})
    return pd.DataFrame(rows)


def _stay_shares(q: pd.DataFrame, venue_of: dict[str, str], sched: pd.DataFrame) -> pd.DataFrame:
    """Per quote: share of its nights in T, on match nights of the market's nearest venue, and on Fri/Sat."""
    mn = {v: C.match_nights(v, sched) for v in set(venue_of.values())}
    ci, co = q.ci.to_numpy(), q.co.to_numpy()
    los = ((co - ci) / np.timedelta64(1, "D")).astype(int)
    idx = np.repeat(np.arange(len(q)), los)
    off = np.concatenate([np.arange(n) for n in los]) if len(los) else np.array([], int)
    nights = pd.to_datetime(ci[idx]) + pd.to_timedelta(off, unit="D")
    mk = q.market.to_numpy()[idx]
    inT = (nights >= C.T_START) & (nights <= C.T_END)
    isM = np.array([n in mn[venue_of[m]] for n, m in zip(nights, mk)], dtype=bool)
    wkd = np.isin(nights.dayofweek, [4, 5])
    agg = pd.DataFrame({"i": idx, "T": inT, "M": isM, "W": wkd}).groupby("i").mean()
    q = q.copy()
    q["T_share"] = agg["T"].to_numpy(); q["M_share"] = agg["M"].to_numpy(); q["weekend_share"] = agg["W"].to_numpy()
    q["los"] = los
    return q


def _clean(q: pd.DataFrame, scrape_col: str = "scrape") -> pd.DataFrame:
    q = q.rename(columns={"price_quote_checkin_date": "ci", "price_quote_checkout_date": "co", "price_quote_price_per_night": "ppn"})
    q["ci"] = pd.to_datetime(q.ci, errors="coerce"); q["co"] = pd.to_datetime(q.co, errors="coerce")
    q["ppn"] = pd.to_numeric(q.ppn, errors="coerce")
    q = q.dropna(subset=["ci", "co", "ppn"])
    q["lead"] = (q.ci - q[scrape_col]).dt.days
    los = (q.co - q.ci).dt.days
    keep = (los >= C.LOS_MIN) & (los <= C.LOS_MAX) & (q.lead >= 0) & (q.lead <= C.LEAD_MAX) & (q.ppn >= C.PPN_MIN) & (q.ppn <= C.PPN_MAX)
    q = q[keep].copy()
    q["lead_bin"] = pd.cut(q.lead, C.LEAD_BINS).astype(str)
    q["logp"] = np.log(q.ppn)
    return q


# ------------------------------------------------------------------------------------------------------------------ #
def p1_panel(geo: pd.DataFrame, sched: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for m in C.P1_HOSTS + C.P1_CONTROLS:
        for f in sorted(C.IA_MONTHLY.glob(f"{m}_2026-*_listings.parquet")):
            x = pd.read_parquet(f, columns=["id", "price_basis", "price_quote_checkin_date", "price_quote_checkout_date", "price_quote_price_per_night"])
            x = x[x.price_basis == "quote_per_night"].drop(columns="price_basis")
            if x.empty:
                continue
            x["market"] = m; x["scrape"] = pd.Timestamp(re.search(r"(\d{4}-\d{2}-\d{2})", f.name).group(1))
            rows.append(x)
    q = _clean(pd.concat(rows, ignore_index=True))
    venue_of = geo.drop_duplicates("market").set_index("market").nearest_venue.to_dict()
    q = _stay_shares(q, venue_of, sched)
    q["host"] = q.market.isin(C.P1_HOSTS).astype(float)
    q["host_T"] = q.host * q.T_share; q["host_M"] = q.host * q.M_share
    q["listing"] = q.market + "_" + q.id.astype(str)
    q["ci_week"] = q.ci.dt.to_period("W").astype(str)
    q["ci_month"] = q.ci.dt.to_period("M").astype(str)
    return q


def m_bar(market: str, geo: pd.DataFrame, sched: pd.DataFrame) -> float:
    v = geo.set_index("market").nearest_venue.to_dict()[market]
    t = pd.date_range(C.T_START, C.T_END)
    return float(np.mean([d in C.match_nights(v, sched) for d in t]))


def _p1_fit(q: pd.DataFrame, absorb: list[str]) -> pd.DataFrame:
    return ols_fe(q, "logp", ["weekend_share", "T_share", "M_share", "host_T", "host_M"], absorb, cluster="listing")


def run_p1(q: pd.DataFrame, geo: pd.DataFrame, sched: pd.DataFrame) -> dict:
    absorb = ["listing", "los", "lead_bin", "ci_week"]
    res = _p1_fit(q, absorb)
    out = {"coef": res, "n": res.attrs["n"], "clusters": res.attrs["clusters"], "by_host": {}}
    for h in C.P1_HOSTS:
        mb = m_bar(h, geo, sched)
        est, lo, hi = lincomb(res, {"host_T": 1.0, "host_M": mb})
        out["by_host"][h] = {"m_bar": mb, "log_premium": est, "lo": lo, "hi": hi,
                             "premium": np.expm1(est), "premium_lo": np.expm1(lo), "premium_hi": np.expm1(hi)}
    mb = float(np.mean([m_bar(h, geo, sched) for h in C.P1_HOSTS]))
    est, lo, hi = lincomb(res, {"host_T": 1.0, "host_M": mb})
    out["pooled"] = {"m_bar": mb, "premium": np.expm1(est), "premium_lo": np.expm1(lo), "premium_hi": np.expm1(hi), "log_premium": est}
    # leave-one-control-out
    loco = {}
    for c in C.P1_CONTROLS:
        r = _p1_fit(q[q.market != c], absorb); e, _, _ = lincomb(r, {"host_T": 1.0, "host_M": mb}); loco[c] = float(np.expm1(e))
    out["loco"] = loco
    # permutation: every 2-market pseudo-treated pair among the six markets
    mk = C.P1_HOSTS + C.P1_CONTROLS; perm = {}
    for pair in itertools.combinations(mk, 2):
        z = q.copy(); z["host"] = z.market.isin(pair).astype(float)
        z["host_T"] = z.host * z.T_share; z["host_M"] = z.host * z.M_share
        mbp = float(np.mean([m_bar(p, geo, sched) for p in pair]))
        r = _p1_fit(z, absorb); e, _, _ = lincomb(r, {"host_T": 1.0, "host_M": mbp}); perm["+".join(pair)] = float(e)
    obs = perm["+".join(C.P1_HOSTS)]
    out["perm"] = perm; out["perm_rank"] = int(sum(v >= obs for v in perm.values()))   # 1 = largest of 15
    # P3 robustness: controls get market x check-in-month FE, hosts none; no check-in-week FE
    z = q.copy(); z["season"] = np.where(z.host == 1, "hosts", z.market + "_" + z.ci_month)
    r3 = _p1_fit(z, ["listing", "los", "lead_bin", "season"]); e, lo, hi = lincomb(r3, {"host_T": 1.0, "host_M": mb})
    out["p3"] = {"premium": np.expm1(e), "premium_lo": np.expm1(lo), "premium_hi": np.expm1(hi), "coef": r3}
    return out


# ------------------------------------------------------------------------------------------------------------------ #
def p2_cross(geo: pd.DataFrame, snaps: pd.DataFrame, sched: pd.DataFrame) -> pd.DataFrame:
    g = geo.set_index("market_key")
    rows = []
    for _, r in snaps.iterrows():
        cls = g.loc[r.market_key, "cls"]
        if r.market in C.NYC_EXCLUDED_FROM_PRICE or r.market in C.POST_TOURNAMENT_PLACEBO or cls == "ring":
            continue
        if cls == "control" and not (C.P2_CONTROL_SCRAPE[0] <= r.scrape <= C.P2_CONTROL_SCRAPE[1]):
            continue
        x = pd.read_csv(r.file, usecols=lambda c: c in USE, low_memory=False)
        x["market"] = r.market; x["scrape"] = r.scrape; x["cls"] = cls
        rows.append(x)
    q = _clean(pd.concat(rows, ignore_index=True))
    q = q[q.ci <= C.T_END].copy()
    venue_of = geo.drop_duplicates("market").set_index("market").nearest_venue.to_dict()
    q = _stay_shares(q, venue_of, sched)
    q["host"] = (q.cls == "host").astype(float); q["host_M"] = q.host * q.M_share
    q["acc_c"] = pd.to_numeric(q.accommodates, errors="coerce").clip(upper=16)
    q["bed_c"] = pd.to_numeric(q.bedrooms, errors="coerce").fillna(1).clip(upper=6)
    q["nbhd"] = q.market + "_" + q.neighbourhood_cleansed.astype(str)
    return q


def run_p2(q: pd.DataFrame) -> dict:
    absorb = ["nbhd", "los", "lead_bin", "room_type"]
    x = ["weekend_share", "acc_c", "bed_c", "M_share", "host_M"]
    res = ols_fe(q, "logp", x, absorb, cluster="market")
    out = {"coef": res, "n": res.attrs["n"], "clusters": res.attrs["clusters"]}
    loho = {}
    for h in sorted(q[q.host == 1].market.unique()):
        r = ols_fe(q[q.market != h], "logp", x, absorb, cluster="market")
        loho[h] = float(r.set_index("term").loc["host_M", "coef"])
    out["leave_one_host_out"] = loho
    out["hosts"] = sorted(q[q.host == 1].market.unique()); out["controls"] = sorted(q[q.host == 0].market.unique())
    out["host_match_quotes"] = int(((q.host == 1) & (q.M_share > 0)).sum())
    return out
