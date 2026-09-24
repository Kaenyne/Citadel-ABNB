"""los_nowcast / worldcup.py — did the World Cup shorten stays in host cities, and what is that worth globally?
(prereg section 3). Construction S at the June 2026 vintages, occupancy-weighted, triple difference:
[host (tournament window - post window), y/y] - [control (tournament - post), y/y], in LOS pp."""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import config as C
from .build import bucket_stats, weights, SHIFT


def _share(stats: list[dict]) -> dict:
    tot = sum(s[f"w_nights_{b}"] for s in stats for b in C.BUCKETS)
    return {b: sum(s[f"w_nights_{b}"] for s in stats) / tot for b in C.BUCKETS} if tot else None


def _los(late: dict, old: dict) -> float:
    return sum((late[b] - old[b]) * (C.RATIO[b] - 1) for b in C.BUCKETS) * 100


def run(pairs: pd.DataFrame, stock_runs) -> tuple[pd.DataFrame, pd.DataFrame]:
    jun = pairs[pairs.quarter.eq("2Q26")]
    rows = []
    for p in jun.itertuples():
        grp = "host" if p.market in C.WC_HOSTS else ("control" if p.market in C.WC_CONTROLS else None)
        if grp is None:
            continue
        lt, ot = pd.Timestamp(p.late), pd.Timestamp(p.old)
        t0 = max(lt + pd.Timedelta(days=C.LEAD[0]), ot + SHIFT + pd.Timedelta(days=C.LEAD[0])); t1 = pd.Timestamp(C.WC_END)
        if (t1 - t0).days < 7:
            continue
        wins = {"tournament": (t0, t1), "post": (pd.Timestamp(C.WC_POST[0]), pd.Timestamp(C.WC_POST[1]))}
        for wname, (a, b) in wins.items():
            for side, v, shift in (("late", p.late, pd.Timedelta(0)), ("old", p.old, SHIFT)):
                r = stock_runs(p.market, v); r = r[(r.start >= a - shift) & (r.start <= b - shift)]
                wdf, _ = weights(p.market, v)
                rows.append(dict(market=p.market, group=grp, window=wname, side=side, win_start=str((a - shift).date()),
                                 win_end=str((b - shift).date()), **bucket_stats(r, wdf)))
    mw = pd.DataFrame(rows)
    res = []
    los = {}
    for grp in ("host", "control"):
        for w in ("tournament", "post"):
            s = mw[mw.group.eq(grp) & mw.window.eq(w)]
            late = _share(s[s.side.eq("late")].to_dict("records")); old = _share(s[s.side.eq("old")].to_dict("records"))
            los[(grp, w)] = _los(late, old)
            res.append(dict(group=grp, window=w, n_markets=s.market.nunique(), los_yoy_pp=los[(grp, w)],
                            ge28_late=late["ge28"], ge28_old=old["ge28"], lt7_late=late["lt7"], lt7_old=old["lt7"]))
    ddd = (los[("host", "tournament")] - los[("host", "post")]) - (los[("control", "tournament")] - los[("control", "post")])
    # per-host DDD against the pooled control
    for h in sorted(set(mw[mw.group.eq("host")].market)):
        lh = {}
        for w in ("tournament", "post"):
            s = mw[mw.market.eq(h) & mw.window.eq(w)]
            lh[w] = _los(_share(s[s.side.eq("late")].to_dict("records")), _share(s[s.side.eq("old")].to_dict("records")))
        res.append(dict(group=f"host:{h}", window="DDD vs pooled control", n_markets=1,
                        los_yoy_pp=(lh["tournament"] - lh["post"]) - (los[("control", "tournament")] - los[("control", "post")])))
    res.append(dict(group="host - control", window="DDD", n_markets=mw.market.nunique(), los_yoy_pp=ddd))
    tr = []
    for cov, nm in C.WC_NIGHTS_M.items():
        for f in C.WC_F2Q26:
            tr.append(dict(nights=cov, f_2Q26=f, host_share_of_2Q26_nights=nm * f / C.Q2_NIGHTS_M,
                           global_2Q26_los_pp=ddd * nm * f / C.Q2_NIGHTS_M))
    tr = pd.DataFrame(tr)
    return pd.concat([pd.DataFrame(res)], ignore_index=True), tr, mw
