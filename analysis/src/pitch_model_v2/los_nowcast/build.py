"""los_nowcast / build.py — pairs, per-market bucket nights, regional and global LOS terms, the 2Q26 -> 3Q26 change,
the band and the market bootstrap (docs/pitch-model-v2/lines/los_nowcast_prereg.md section 2)."""
from __future__ import annotations
import re
import numpy as np
import pandas as pd
from . import config as C
from .runs import vintages

SHIFT = pd.Timedelta(days=C.SHIFT_DAYS)
_WCACHE: dict = {}


# ---------------------------------------------------------------- weights (I2b / 14c convention)
def weights(market: str, date: str):
    key = (market, date)
    if key in _WCACHE:
        return _WCACHE[key]
    p = C.BYL / f"{market}_{date}.parquet"
    if p.exists():
        d = pd.read_parquet(p, columns=["listing_id", "active", "w"]).drop_duplicates("listing_id").set_index("listing_id")
        res = (d, f"14c:{date}")
    else:
        fs = list(C.LST.glob(f"{market}_*_listings.csv.gz"))
        ds = sorted((abs((pd.Timestamp(re.search(r"_(\d{4}-\d{2}-\d{2})_listings", f.name).group(1)) - pd.Timestamp(date)).days), f) for f in fs)
        if not ds or ds[0][0] > 60:
            res = (None, "none")
        else:
            f = ds[0][1]
            L = pd.read_csv(f, usecols=lambda c: c in ("id", "number_of_reviews_ltm", "estimated_occupancy_l365d"), low_memory=False)
            L = L.rename(columns={"id": "listing_id"}).drop_duplicates("listing_id").set_index("listing_id")
            d = pd.DataFrame(index=L.index)
            d["active"] = pd.to_numeric(L.get("number_of_reviews_ltm"), errors="coerce").fillna(0) > 0
            d["w"] = pd.to_numeric(L.get("estimated_occupancy_l365d"), errors="coerce").clip(0, 0.7 * 365)
            res = (d, f"listings:{re.search(r'_(\d{4}-\d{2}-\d{2})_listings', f.name).group(1)}")
    _WCACHE[key] = res
    return res


def bucket_stats(r: pd.DataFrame, wdf) -> dict:
    """I2b window_stats on an already-windowed run table: cap, active filter, unweighted and occupancy-weighted nights."""
    n_over = int((r.len > C.CAP).sum())
    r = r[r.len <= C.CAP]
    if wdf is not None:
        r = r.join(wdf, on="listing_id", how="left"); r = r[r.active.eq(True)]
    else:
        r = r.assign(w=np.nan)
    r = r.assign(b=np.select([r.len < 7, r.len < 28], ["lt7", "n7_27"], "ge28"))
    out = dict(n_runs=int(len(r)), n_listings=int(r.listing_id.nunique()), n_runs_over90=n_over, nights=float(r.len.sum()),
               mean_run=float(r.len.mean()) if len(r) else np.nan)
    nb = r.groupby("b").len.sum()
    for b in C.BUCKETS:
        out[f"nights_{b}"] = float(nb.get(b, 0.0))
    ok = r[r.w.notna() & (r.w > 0)]
    if len(ok):
        tot = ok.groupby("listing_id").len.transform("sum")
        ok = ok.assign(wn=ok.len * ok.w / tot); wb = ok.groupby("b").wn.sum()
        for b in C.BUCKETS:
            out[f"w_nights_{b}"] = float(wb.get(b, 0.0))
    else:
        for b in C.BUCKETS:
            out[f"w_nights_{b}"] = np.nan
    return out


# ---------------------------------------------------------------- pairs
def s_pairs() -> pd.DataFrame:
    """I2b pairs_for, 2026 late vintages only; old candidates restricted to I2a's 2025 window (2025-05-01..09-30)."""
    rows = []
    for m in C.REGION:
        vs = vintages(m)
        olds = [v for v in vs if "2025-05-01" <= v <= "2025-09-30"]
        for q, (a, b) in C.S_KIND_2026.items():
            for late in [v for v in vs if a <= v <= b]:
                lt = pd.Timestamp(late)
                cands = [(v, (pd.Timestamp(v) - (lt - SHIFT)).days) for v in olds if abs((pd.Timestamp(v) - (lt - SHIFT)).days) <= C.TOL_S]
                if not cands:
                    continue
                wstart = pd.Timestamp("2025-07-01") if q == "2Q26" else pd.Timestamp("2025-09-01")
                cands.sort(key=lambda c: (pd.Timestamp(c[0]) > wstart, abs(c[1])))
                rows.append(dict(construction="S", quarter=q, market=m, region=C.REGION[m], late=late, old=cands[0][0]))
    return pd.DataFrame(rows)


def f_pairs() -> pd.DataFrame:
    rows = []
    for m in C.REGION:
        vs = vintages(m)
        v26 = {v[5:7]: v for v in vs if v.startswith("2026")}
        v25 = [v for v in vs if v.startswith("2025")]
        for q, (m1, m2) in C.F_PAIRS_2026.items():
            if m1 not in v26 or m2 not in v26:
                continue
            a, b = pd.Timestamp(v26[m1]), pd.Timestamp(v26[m2])
            best = None
            for u1 in v25:
                for u2 in v25:
                    if u2 <= u1:
                        continue
                    g1 = abs((pd.Timestamp(u1) - (a - SHIFT)).days); g2 = abs((pd.Timestamp(u2) - (b - SHIFT)).days)
                    len_ok = abs((pd.Timestamp(u2) - pd.Timestamp(u1)).days - (b - a).days) <= C.LEN_TOL_F   # amendment 1
                    if g1 <= C.TOL_F and g2 <= C.TOL_F and len_ok and (best is None or g1 + g2 < best[2]):
                        best = (u1, u2, g1 + g2)
            if best:
                rows.append(dict(construction="F", quarter=q, market=m, region=C.REGION[m], late_v1=v26[m1], late_v2=v26[m2],
                                 old_v1=best[0], old_v2=best[1], gap_days=best[2],
                                 len_late=(b - a).days, len_old=(pd.Timestamp(best[1]) - pd.Timestamp(best[0])).days))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- per-market stats
def s_market_stats(p, stock_runs) -> list[dict]:
    out = []
    for side, v in (("late", p.late), ("old", p.old)):
        t = pd.Timestamp(v); r = stock_runs(p.market, v)
        r = r[(r.start >= t + pd.Timedelta(days=C.LEAD[0])) & (r.start <= t + pd.Timedelta(days=C.LEAD[1]))]
        wdf, src = weights(p.market, v)
        out.append(dict(construction="S", quarter=p.quarter, market=p.market, region=p.region, side=side, vintage=v, weights_src=src,
                        **bucket_stats(r, wdf)))
    return out


def f_market_stats(p, flow_runs) -> list[dict]:
    out = []
    for side, v1, v2 in (("late", p.late_v1, p.late_v2), ("old", p.old_v1, p.old_v2)):
        r = flow_runs(p.market, v1, v2)
        n_edge = int(r.edge.sum())
        tot = r.groupby("listing_id").len.transform("sum")
        closed = r[tot > C.CLOSURE].listing_id.nunique()
        r = r[~r.edge & (tot <= C.CLOSURE)]
        wdf, src = weights(p.market, v2)
        out.append(dict(construction="F", quarter=p.quarter, market=p.market, region=p.region, side=side, vintage=f"{v1}>{v2}",
                        weights_src=src, n_edge_dropped=n_edge, n_closed_listings=int(closed), **bucket_stats(r, wdf)))
    return out


# ---------------------------------------------------------------- aggregation
def los_term(ms: pd.DataFrame, pre: str, markets=None, require_all=False) -> dict:
    """Regional pooled shares (late vs old), LOS pp per region and the 10-K weighted global. pre '' unweighted, 'w_' W1."""
    g = ms[~ms.market.isin(C.REG_MIN)]
    if markets is not None:
        g = g[g.market.isin(markets)]
    reg = {}
    for r, gr in g.groupby("region"):
        sh = {}
        for side in ("late", "old"):
            s = gr[gr.side.eq(side)]
            tot = s[[f"{pre}nights_{b}" for b in C.BUCKETS]].sum().sum()
            sh[side] = {b: s[f"{pre}nights_{b}"].sum() / tot if tot else np.nan for b in C.BUCKETS}
        reg[r] = dict(los_pp=sum((sh["late"][b] - sh["old"][b]) * (C.RATIO[b] - 1) for b in C.BUCKETS) * 100,
                      d_ge28_pp=100 * (sh["late"]["ge28"] - sh["old"]["ge28"]), n=gr.market.nunique())
    cov = [r for r in C.TENK_W if r in reg and np.isfinite(reg[r]["los_pp"])]
    if require_all and len(cov) < 4:
        glob_ = np.nan
    else:
        wsum = sum(C.TENK_W[r] for r in cov)
        glob_ = sum(C.TENK_W[r] * reg[r]["los_pp"] for r in cov) / wsum if cov else np.nan
    return {"global": glob_, "regions": reg, "covered": cov}


def panel(ms: pd.DataFrame) -> list[str]:
    g = ms[~ms.market.isin(C.REG_MIN)]
    q2 = set(g[g.quarter.eq("2Q26")].market); q3 = set(g[g.quarter.eq("3Q26")].market)
    return sorted(q2 & q3)


def delta(ms: pd.DataFrame, pre: str, markets) -> tuple[float, float, float]:
    a = los_term(ms[ms.quarter.eq("2Q26")], pre, markets)["global"]; b = los_term(ms[ms.quarter.eq("3Q26")], pre, markets)["global"]
    return a, b, b - a


def bootstrap(msF: pd.DataFrame, msS: pd.DataFrame, pF, pS, use_f: bool) -> np.ndarray:
    rng = np.random.default_rng(C.BOOT_SEED)
    regF = {r: [m for m in pF if C.REGION[m] == r] for r in C.TENK_W}
    regS = {r: [m for m in pS if C.REGION[m] == r] for r in C.TENK_W}

    def draw(ms, regm):
        pick = []
        for r, mk in regm.items():
            if mk:
                pick += list(rng.choice(mk, size=len(mk), replace=True))
        # duplicate markets: relabel so pooled sums count them twice
        rows = []
        for i, m in enumerate(pick):
            x = ms[ms.market.eq(m)].copy(); x["market"] = f"{m}#{i}"; x["region"] = C.REGION[m]; rows.append(x)
        return pd.concat(rows)

    out = []
    for _ in range(C.BOOT_N):
        dS = delta(draw(msS, regS), "w_", None)[2]
        if use_f:
            dF = delta(draw(msF, regF), "w_", None)[2]; out.append((dF + dS) / 2)
        else:
            out.append(dS)
    return np.array(out)
