"""Stage D: why the staggered DiD is not the evidence. Pre-trend of US vs never-treated controls, minimum
detectable effect from pre-period placebo launches and permutation, and an EXPLORATORY event study on the
US arm (never-treated controls, single cohort), cluster-bootstrap bands. No coefficient is a claim."""
import numpy as np, pandas as pd
import config as C


def _yoy_panel(my, measure="yoy_vmatch"):
    from index import MEASURES
    num, den = MEASURES[measure]
    d = my.dropna(subset=[num, den]); d = d[d[den] > 0]
    p = d.assign(v=np.log(d[num] / d[den])).pivot_table(index="ymi", columns="market_key", values="v")
    return p


def _arms(my):
    cty = my.groupby("market_key").country.first()
    us = cty.index[cty == "united-states"]; ct = cty.index[cty.isin(C.NEVER_TREATED)]
    return list(us), list(ct)


def _did(y, tr, co, t0, pre, post):
    w = y.loc[t0 - pre: t0 + post - 1]; ip = w.index >= t0
    e = w.loc[ip].mean() - w.loc[~ip].mean(); return float(e[tr].mean() - e[co].mean())


def run_stage_d(my, B=150, seed=20260918):
    rng = np.random.default_rng(seed)
    y = _yoy_panel(my); us, ct = _arms(my); us = [m for m in us if m in y.columns]; ct = [m for m in ct if m in y.columns]
    gap = ((y[us].mean(axis=1) - y[ct].mean(axis=1)) * 100).loc[C.ymi(2024, 1): C.ymi(2026, 6)]
    pre = gap.loc[: C.RNPL_US_LAUNCH_YMI - 1]
    rows = [dict(item="US_minus_controls_pretrend_mean_pp", value=float(pre.mean()), detail="2024-01..2025-07, y/y log stays")]
    allm = np.array(us + ct); dates = range(C.ymi(2024, 7), C.ymi(2025, 2) + 1)
    real = np.array([_did(y, us, ct, d, 6, 6) for d in dates])
    perm = np.array([_did(y, s[: len(us)], s[len(us):], d, 6, 6) for d in dates for s in (rng.permutation(allm) for _ in range(B))])
    rows += [dict(item="MDE_pp_permutation", value=float(2.8 * perm.std() * 100), detail="alpha .05 two-sided, power .8; 6 pre / 6 post; normalised window"),
             dict(item="MDE_pp_placebo_dates", value=float(2.8 * real.std() * 100), detail="same, true assignment across placebo dates"),
             dict(item="effect_looked_for_pp", value=3.0, detail="upper end of the disclosed bundle lift on bookings")]
    # exploratory event study: e in -12..+10 relative to Aug 2025; ATT(e) = mean_US[y_e - ybar_pre] - mean_CT[same]
    base = y.loc[C.RNPL_US_LAUNCH_YMI - 12: C.RNPL_US_LAUNCH_YMI - 1].mean()
    es = []
    for e in range(-12, 11):
        m = C.RNPL_US_LAUNCH_YMI + e
        if m not in y.index: continue
        dev = y.loc[m] - base
        att = float(dev[us].mean() - dev[ct].mean())
        boots = [float(dev[rng.choice(us, len(us))].mean() - dev[rng.choice(ct, len(ct))].mean()) for _ in range(300)]
        es.append(dict(event_month=e, ymi=m, att_pp=att * 100, lo90=np.quantile(boots, .05) * 100, hi90=np.quantile(boots, .95) * 100))
    return pd.DataFrame(rows), gap.rename("us_minus_controls_pp").reset_index(), pd.DataFrame(es)
