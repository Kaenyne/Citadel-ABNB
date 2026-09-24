"""worldcup_premium / translate.py — PREREG section 6 (V4 realised stays) and section 8 (translation into the ADR
line), with the section 11 amendments."""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import config as C

R_M = {"2Q26": {"na": 280.75 / 183.73, "latam": 102.80 / 183.73}, "4Q25": {"na": 247.21 / 167.51, "latam": 95.51 / 167.51}}
DEC_FRAC = {"los-angeles": 27 / 102, "mexico-city": 2 / 91}     # amendment 4


def v4_reviews(geo: pd.DataFrame) -> pd.DataFrame:
    e = pd.read_csv(C.E_PANEL, encoding="latin-1")
    e["market"] = e.market_key.str.split("_").str[-1]
    cls = geo.drop_duplicates("market").set_index("market").cls
    e = e[e.market.isin(cls.index)].copy(); e["cls"] = e.market.map(cls)
    e = e[e.cls.isin(["host", "control"])]
    e["dump_date"] = pd.to_datetime(e.dump_date)
    last = e.groupby("market").dump_date.transform("max"); e = e[e.dump_date == last]
    e["month_end"] = pd.PeriodIndex(e.ym, freq="M").end_time.normalize()
    months = ["2026-03", "2026-04", "2026-05", "2026-06", "2026-07"]
    e = e[e.ym.isin(months) & (e.dump_date >= e.month_end + pd.Timedelta(days=10))]      # amendment 6
    g = e.groupby(["cls", "ym"])[["n_vm_cur", "n_vm_prior"]].sum()
    g["yoy_pct"] = 100 * (g.n_vm_cur / g.n_vm_prior - 1)
    g["n_markets"] = e.groupby(["cls", "ym"]).market.nunique()
    return g.reset_index()


def v4_summary(g: pd.DataFrame) -> dict:
    pre, ev = ["2026-03", "2026-04", "2026-05"], ["2026-06", "2026-07"]
    def pooled(cls, ms):
        x = g[(g.cls == cls) & g.ym.isin(ms)]
        return 100 * (x.n_vm_cur.sum() / x.n_vm_prior.sum() - 1) if len(x) else np.nan
    h_pre, h_ev, c_pre, c_ev = pooled("host", pre), pooled("host", ev), pooled("control", pre), pooled("control", ev)
    return {"host_pre": h_pre, "host_event": h_ev, "control_pre": c_pre, "control_event": c_ev,
            "did_pp": (h_ev - h_pre) - (c_ev - c_pre)}


def host_nights(geo: pd.DataFrame, snaps: pd.DataFrame, sched: pd.DataFrame) -> pd.DataFrame:
    """N_T,m = sum of estimated_occupancy_l365d x 39/365 over each host market's 2026 snapshot listings."""
    hosts = geo[geo.cls == "host"].drop_duplicates("market_key")
    rows = []
    for _, h in hosts.iterrows():
        f = snaps.set_index("market_key").loc[h.market_key, "file"]
        occ = pd.read_csv(f, usecols=["estimated_occupancy_l365d"]).estimated_occupancy_l365d
        rows.append({"market": h.market, "venue": h.nearest_venue, "km": h.km, "occ_nights_365": float(occ.sum()),
                     "N_T_central": float(occ.sum()) * C.T_DAYS / 365, "country": h.market_key.split("_")[0]})
    return pd.DataFrame(rows)


def translate(hn: pd.DataFrame, timing: pd.DataFrame, p1: dict, sched: pd.DataFrame) -> dict:
    covered_venues = sorted(hn.venue.unique())
    matches_covered = int(sched.stadium.isin(covered_venues).sum())
    scale = 104 / matches_covered
    tm = timing.set_index("host")
    f = {}
    for h in C.CAL_HOSTS:
        t = tm.loc[h]; dec = DEC_FRAC[h]
        f[h] = {"4Q25": t.share_before_Dec + t.share_Dec_to_Mar * dec, "1Q26": t.share_Dec_to_Mar * (1 - dec), "2Q26": t.share_Mar_to_Jun}
    prem = {"low": p1["pooled"]["premium_lo"], "central": p1["pooled"]["premium"], "high": p1["pooled"]["premium_hi"]}
    cover = {"low": 1.0, "central": (1.0 + scale) / 2, "high": scale}                    # amendment 1
    out = {"matches_covered": matches_covered, "scale": scale, "f": f, "premium": prem, "cover": cover, "rows": []}
    for q in ("4Q25", "2Q26"):
        for case in ("low", "central", "high"):
            tot = 0.0
            for _, r in hn.iterrows():
                timing_host = "mexico-city" if r.country == "mexico" else "los-angeles"
                reg = "latam" if r.country == "mexico" else "na"
                n = r.N_T_central * C.SUMMER_FACTOR[case] * cover[case]
                tot += n * f[timing_host][q] * R_M[q][reg] * prem[case]
            out["rows"].append({"quarter": q, "case": case, "effect_pp": 100 * tot / C.NIGHTS_Q[q]})
    eff = pd.DataFrame(out["rows"]).pivot(index="case", columns="quarter", values="effect_pp")
    eff["overstatement_4Q26_pp"] = eff["2Q26"] + eff["4Q25"]
    eff["adr_4Q26_move_usd_from_base"] = -167.51 * eff.overstatement_4Q26_pp / 100
    eff["adr_4Q26_filed_base"] = 173.034 + eff.adr_4Q26_move_usd_from_base
    eff["adr_4Q26_audit_consistent_row"] = 172.456 + eff.adr_4Q26_move_usd_from_base
    out["effects"] = eff
    lo = float(eff.loc["low", "2Q26"]); ce = float(eff.loc["central", "2Q26"])
    out["label"] = ("measured composition term" if lo >= C.LABEL_LINE_PP else
                    "direction only" if ce >= C.LABEL_LINE_PP else "not distinguishable from zero")
    return out
