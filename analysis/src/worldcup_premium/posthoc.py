"""worldcup_premium / posthoc.py — checks added AFTER the pre-registered run (labelled as such in the note).
    PYTHONPATH=analysis/src py -3.13 -m worldcup_premium.posthoc
(1) Event study of the P1 price gap by check-in week: is the host premium confined to the tournament (event-shaped)
    or a summer plateau (seasonal)? Same sample and FE as P1 minus the check-in-week FE and the treatment terms.
(2) P1 re-estimated with Chicago as the only control (the one control whose summer is high season, like LA's).
(3) Translation recomputed with bounded booking-timing scenarios, because the pre-registered V3 timing shares fell
    outside [0, 1] (the June excess was <= 0 on the common date set) and are not interpretable."""
from __future__ import annotations
import json
import numpy as np
import pandas as pd
from . import config as C, quotes as Q
from .fe import demean, ols_fe, lincomb


def event_study(q: pd.DataFrame) -> pd.DataFrame:
    d = q.dropna(subset=["logp"]).copy()
    d = d[d.groupby("listing").listing.transform("size") > 1]
    X = pd.get_dummies(d[["los", "lead_bin"]].astype(str), drop_first=True).astype(float)
    X["weekend_share"] = d.weekend_share.to_numpy()
    M = demean(np.column_stack([d.logp.to_numpy(), X.to_numpy()]), [d.listing.to_numpy()])
    b, *_ = np.linalg.lstsq(M[:, 1:], M[:, 0], rcond=None)
    d["resid"] = M[:, 0] - M[:, 1:] @ b
    w = d.groupby(["market", "ci_week"]).agg(r=("resid", "mean"), n=("resid", "size")).reset_index()
    w = w[w.n >= 30]
    piv = w.pivot(index="ci_week", columns="market", values="r")
    out = pd.DataFrame({"week": piv.index})
    out["week_start"] = pd.PeriodIndex(out.week, freq="W").start_time
    ctl = piv[[c for c in C.P1_CONTROLS if c in piv]].mean(axis=1).to_numpy()
    for h in C.P1_HOSTS:
        out[f"{h}_minus_controls"] = piv[h].to_numpy() - ctl
    out["chicago_only_LA"] = piv["los-angeles"].to_numpy() - piv["chicago"].to_numpy()
    out["in_T"] = (out.week_start + pd.Timedelta(days=6) >= C.T_START) & (out.week_start <= C.T_END)
    return out


def window_means(es: pd.DataFrame) -> pd.DataFrame:
    """Mean gap in three windows: before T (weeks starting 1 Apr - 3 Jun), T, after T (weeks starting 20 Jul - 31 Aug)."""
    pre = (es.week_start >= "2026-04-01") & (es.week_start <= "2026-06-03")
    post = (es.week_start >= "2026-07-20") & (es.week_start <= "2026-08-31")
    rows = []
    for col in [c for c in es.columns if c.endswith("controls") or c.startswith("chicago")]:
        a, t, p = es.loc[pre, col].mean(), es.loc[es.in_T, col].mean(), es.loc[post, col].mean()
        rows.append({"series": col, "pre_T": a, "T": t, "post_T": p, "T_minus_avg_pre_post": t - np.nanmean([a, p]),
                     "n_weeks_pre": int(pre.sum()), "n_weeks_T": int(es.in_T.sum()), "n_weeks_post": int(post.sum())})
    return pd.DataFrame(rows)


def main() -> None:
    sched = C.load_schedule()
    geo = pd.read_csv(C.OUT / "01_geography.csv")
    q = Q.p1_panel(geo, sched)
    es = event_study(q); es.to_csv(C.OUT / "60_posthoc_event_study.csv", index=False)
    wm = window_means(es); wm.to_csv(C.OUT / "60_posthoc_event_windows.csv", index=False)
    print(es.round(4).to_string(index=False)); print(wm.round(4).to_string(index=False))

    # (2) Chicago-only control
    z = q[q.market.isin(C.P1_HOSTS + ["chicago"])]
    r = ols_fe(z, "logp", ["weekend_share", "T_share", "M_share", "host_T", "host_M"], ["listing", "los", "lead_bin", "ci_week"], cluster="listing")
    mb = float(np.mean([Q.m_bar(h, geo, sched) for h in C.P1_HOSTS]))
    e, lo, hi = lincomb(r, {"host_T": 1.0, "host_M": mb})
    chi = {"premium": float(np.expm1(e)), "lo": float(np.expm1(lo)), "hi": float(np.expm1(hi)), "n": r.attrs["n"]}
    print("P1 with Chicago as the only control:", chi)

    # (3) translation under bounded timing scenarios (f = share of event-window nights booked in the quarter)
    hn = pd.read_csv(C.OUT / "50_host_nights.csv")
    summ = json.loads((C.OUT / "00_summary.json").read_text())
    scale = summ["translation"]["scale"]
    rna, rla = 280.75 / 183.73, 102.80 / 183.73
    base = float(sum(n * (rla if c == "mexico" else rna) for n, c in zip(hn.N_T_central, hn.country)))
    rows = []
    for prem_lab, prem in (("P1 pooled 11.1%", summ["p1"]["pooled"]["premium"]), ("P1 Chicago-only", chi["premium"]),
                           ("P2 match nights only (8.9% x m_bar 0.32)", 0.0891 * 0.3205)):
        for f_lab, f in (("f_2Q26 = 1.0 (all in 2Q26)", 1.0), ("f_2Q26 = 0.5", 0.5)):
            for cov_lab, cov, summer in (("covered, summer 1.0", 1.0, 1.0), ("central cover, summer 1.0", (1 + scale) / 2, 1.0),
                                         ("scaled, summer 1.3", scale, 1.3)):
                pp = 100 * base * cov * summer * f * prem / C.NIGHTS_Q["2Q26"]
                rows.append({"premium_source": prem_lab, "premium": prem, "timing": f_lab, "coverage": cov_lab, "effect_2Q26_pp": pp,
                             "adr_4Q26_usd_move": -167.51 * pp / 100})
    t = pd.DataFrame(rows); t.to_csv(C.OUT / "61_posthoc_translation.csv", index=False)
    print(t.round(3).to_string(index=False))
    (C.OUT / "62_posthoc_summary.json").write_text(json.dumps({"chicago_only": chi, "window_means": wm.to_dict("records")}, indent=2, default=float))


if __name__ == "__main__":
    main()
