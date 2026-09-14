"""l1-reconciliation: the constrained least-squares reconciliation.

Design (why the 72 exact cells are HARD and not penalised)
----------------------------------------------------------
Free parameters are (i) K-1 = 3 softmax logits per quarter for the regional home
nights shares and (ii) 3 time-invariant regional take-rate tilts (apac is the
reference, so the level is absorbed by the printed total).  Everything else is
SOLVED, not fitted:

  s_{r,q}   = softmax(a_{.,q})                       -> regions sum to 1 EXACTLY
  n_{r,q}   = s_{r,q} * n_home_q                     -> nights identity EXACT
  tr_q      = [sum_r Rev_{r,q}/(1+d_r)] / HomeGBV_q  -> closed form
  GBV_{r,q} = Rev_{r,q} / (tr_q (1+d_r))             -> 72 filed cells EXACT
  ADR_{r,q} = GBV_{r,q} / n_{r,q}                    -> OUTPUT
  blended   = sum_r s_{r,q} ADR_{r,q}                -> geographic mix is an OUTPUT
  dilution  = GBV_q/N_q over p_home                  -> seats/hotel drag is an OUTPUT

So the -0.41pp calibration plug is retired by reparameterisation (shares cannot
fail to sum to one) and the +0.19pp current-weighting index bias is impossible
(the blend is the share-weighted sum by construction).

The objective is the hinge distance to the interval-censored disclosures plus a
random-walk smoothness penalty on the logits.  Bands are NEVER entered at their
midpoint; letter integers are scored on [x-0.5, x+0.5]; basis == 'derived' rows
never enter.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from . import data as D

REGIONS = D.REGIONS
FREE_R = [r for r in REGIONS if r != D.REF_REGION]  # na, emea, latam

W_ANNUAL = 3.0
W_NIGHTS_YOY = 1.0
W_ADR_REP = 1.0
W_ADR_EXFX = 1.0
W_SMOOTH_DEFAULT = 3.0
W_RIDGE = 0.5
TOL = 1e-3   # feasibility tolerance: 0.001M nights and 0.001pp


def hinge(v, lo, hi):
    return np.maximum(lo - v, 0.0) + np.maximum(v - hi, 0.0)


class Recon:
    def __init__(self, quarters, exact_rev, denom, intervals, fxpp,
                 w_smooth=W_SMOOTH_DEFAULT, drift=False):
        self.q = list(quarters)
        self.T = len(self.q)
        self.qi = {q: i for i, q in enumerate(self.q)}
        self.w_smooth = w_smooth
        self.drift = bool(drift)
        # exact regional revenue as a T x 4 matrix
        piv = exact_rev.pivot_table(index="quarter", columns="region",
                                    values="revenue_musd", aggfunc="first")
        self.REV = piv.reindex(index=self.q, columns=REGIONS).to_numpy(float)
        dn = denom.set_index("quarter").reindex(self.q)
        # Regional shares are shares of TOTAL Nights-and-Seats, because the 10-K
        # regional table and the letters' regional ADR sentences are on that basis
        # (see research/notes/2026-09-09_seats-dilution.md).  The home/seat split is
        # applied at the TOTAL level only, which is where the dilution OUTPUT lives.
        self.units = dn["nights_total_m"].to_numpy(float)
        self.gbv_tot = dn["gbv_musd"].to_numpy(float)
        self.n_home = dn["n_home_m"].to_numpy(float)
        self.home_gbv = dn["home_gbv_musd"].to_numpy(float)
        self.p_home = dn["p_home_usd"].to_numpy(float)
        self.denom = dn.reset_index()
        self._build_constraints(intervals, fxpp)
        self.n_params = 3 * self.T + 3 + (3 if self.drift else 0)

    # ------------------------------------------------------------ constraints
    def _build_constraints(self, intervals, fxpp):
        iv = intervals
        # (A) annual 10-K regional nights, FY within the panel
        ann = []
        for _, r in iv[(iv.metric == "nights_m") & (iv.is_annual)].iterrows():
            yr = int(str(r.quarter_or_year)[2:])
            qs = [f"{yr}Q{i}" for i in range(1, 5)]
            if all(x in self.qi for x in qs) and r.region in REGIONS:
                ann.append((tuple(self.qi[x] for x in qs), REGIONS.index(r.region),
                            float(r.lo), float(r.hi), r.obs_id))
        self.ann = ann
        # (B) regional nights y/y
        ny = []
        for _, r in iv[(iv.metric == "nights_yoy_pct") & (~iv.is_annual)].iterrows():
            q, q4 = r.quarter, D.qadd(r.quarter, -4)
            if q in self.qi and q4 in self.qi and r.region in REGIONS:
                ny.append((self.qi[q], self.qi[q4], REGIONS.index(r.region),
                           float(r.lo), float(r.hi), r.obs_id, r.basis))
        self.ny = ny
        # (C) regional ADR y/y reported and ex-FX
        fx = {(a, b): c for a, b, c in
              zip(fxpp.quarter, fxpp.region, fxpp.fx_pp)}
        ar, ax = [], []
        for _, r in iv[(iv.metric.isin(["adr_yoy_reported_pct", "adr_yoy_exfx_pct"]))
                       & (~iv.is_annual)].iterrows():
            q, q4 = r.quarter, D.qadd(r.quarter, -4)
            if q not in self.qi or q4 not in self.qi or r.region not in REGIONS:
                continue
            rec = (self.qi[q], self.qi[q4], REGIONS.index(r.region),
                   float(r.lo), float(r.hi), r.obs_id)
            if r.metric == "adr_yoy_reported_pct":
                ar.append(rec)
            else:
                f = fx.get((q, r.region), np.nan)
                if np.isfinite(f):
                    ax.append(rec + (float(f),))
        self.ar, self.ax = ar, ax

    # ------------------------------------------------------------ forward map
    def unpack(self, theta):
        A = np.zeros((self.T, 4))
        A[:, :3] = theta[:3 * self.T].reshape(self.T, 3)  # na, emea, latam
        g = np.zeros(4)
        g[:3] = theta[3 * self.T:3 * self.T + 3]
        tt = (np.arange(self.T) - (self.T - 1) / 2.0) / max(self.T - 1, 1)
        if self.drift:
            h = np.zeros(4)
            h[:3] = theta[3 * self.T + 3:3 * self.T + 6]
            M_ = np.exp(g[None, :] + np.outer(tt, h))     # T x 4
        else:
            M_ = np.exp(np.tile(g, (self.T, 1)))
        return A, M_

    def forward(self, theta):
        A, Mm = self.unpack(theta)
        E = np.exp(A - A.max(axis=1, keepdims=True))
        S = E / E.sum(axis=1, keepdims=True)
        N = S * self.units[:, None]
        onep = Mm
        tr = (self.REV / onep).sum(axis=1) / self.gbv_tot           # closed form
        GBV = self.REV / (tr[:, None] * onep)
        ADR = GBV / N
        return S, N, tr, GBV, ADR

    # ------------------------------------------------------------ residuals
    def residuals(self, theta, wt=None):
        S, N, tr, GBV, ADR = self.forward(theta)
        res = []
        wa = 1.0 if wt is None else None
        for qs, ri, lo, hi, _ in self.ann:
            v = sum(N[i, ri] for i in qs)
            w = W_ANNUAL * (1.0 if wt is None else wt[qs[0]])
            res.append(w * hinge(v, lo, hi) / 0.5)
        for i, i4, ri, lo, hi, _, _ in self.ny:
            v = 100.0 * (N[i, ri] / N[i4, ri] - 1.0)
            w = W_NIGHTS_YOY * (1.0 if wt is None else wt[i])
            res.append(w * hinge(v, lo, hi) / 0.5)
        for i, i4, ri, lo, hi, _ in self.ar:
            v = 100.0 * (ADR[i, ri] / ADR[i4, ri] - 1.0)
            w = W_ADR_REP * (1.0 if wt is None else wt[i])
            res.append(w * hinge(v, lo, hi) / 0.5)
        for i, i4, ri, lo, hi, _, f in self.ax:
            v = 100.0 * (ADR[i, ri] / ADR[i4, ri] - 1.0) - f
            w = W_ADR_EXFX * (1.0 if wt is None else wt[i])
            res.append(w * hinge(v, lo, hi) / 0.5)
        A, Mm = self.unpack(theta)
        dif = np.diff(A[:, :3], axis=0).ravel()
        res.extend(list(self.w_smooth * dif))
        res.extend(list(W_RIDGE * np.log(Mm[0, :3]) * 10.0))
        if self.drift:
            res.extend(list(W_RIDGE * theta[3 * self.T + 3:3 * self.T + 6] * 10.0))
        return np.asarray(res, float)

    def n_obs(self):
        return len(self.ann) + len(self.ny) + len(self.ar) + len(self.ax)

    # ------------------------------------------------------------ fit
    def fit(self, theta0=None, wt=None, max_nfev=4000):
        if theta0 is None:
            theta0 = self.theta0()
        k = 3 if self.drift else 0
        lo = np.concatenate([np.full(3 * self.T, -6.0), np.full(3, -0.55), np.full(k, -0.60)])
        hi = np.concatenate([np.full(3 * self.T, 6.0), np.full(3, 0.55), np.full(k, 0.60)])
        theta0 = np.clip(theta0, lo + 1e-6, hi - 1e-6)
        f = least_squares(lambda t: self.residuals(t, wt), theta0, method="trf",
                          bounds=(lo, hi), max_nfev=max_nfev, xtol=1e-12, ftol=1e-12)
        return f.x, f

    def theta0(self):
        """Initialise the logits at the 10-K annual nights shares for the year."""
        ann = pd.read_csv(D.DATA / "adr" / "01_regional_annual.csv")
        sh = ann.pivot_table(index="year", columns="region", values="nights_m")
        sh = sh.div(sh.sum(axis=1), axis=0)
        A = np.zeros((self.T, 3))
        for i, q in enumerate(self.q):
            yr = int(q[:4])
            yr = yr if yr in sh.index else int(sh.index.max())
            base = float(sh.loc[yr, D.REF_REGION])
            for j, r in enumerate(FREE_R):
                A[i, j] = np.log(max(float(sh.loc[yr, r]), 1e-6) / max(base, 1e-6))
        return np.concatenate([A.ravel(), np.zeros(3 + (3 if self.drift else 0))])

    # ------------------------------------------------------------ reporting
    def panel(self, theta):
        S, N, tr, GBV, ADR = self.forward(theta)
        rows = []
        for i, q in enumerate(self.q):
            for j, r in enumerate(REGIONS):
                rows.append(dict(quarter=q, region=r, nights_m=N[i, j],
                                 share_pct=100 * S[i, j], adr_reported_usd=ADR[i, j],
                                 gbv_musd=GBV[i, j], revenue_musd=self.REV[i, j],
                                 take_rate_pct=100 * tr[i] * self.unpack(theta)[1][i, j]))
        return pd.DataFrame(rows)

    def residual_report(self, theta):
        S, N, tr, GBV, ADR = self.forward(theta)
        rows = []
        for i, q in enumerate(self.q):  # 72 exact cells
            for j, r in enumerate(REGIONS):
                fit = GBV[i, j] * tr[i] * self.unpack(theta)[1][i, j]
                rows.append(dict(cls="exact_regional_revenue", obs_id=f"{q}-{r}",
                                 quarter=q, region=r, lo=self.REV[i, j],
                                 hi=self.REV[i, j], fitted=fit,
                                 resid=fit - self.REV[i, j], inside=True))
        for qs, ri, lo, hi, oid in self.ann:
            v = sum(N[k, ri] for k in qs)
            rows.append(dict(cls="annual_regional_nights", obs_id=oid,
                             quarter=self.q[qs[0]][:4], region=REGIONS[ri], lo=lo, hi=hi,
                             fitted=v, resid=hinge(v, lo, hi), inside=hinge(v, lo, hi) <= TOL))
        for i, i4, ri, lo, hi, oid, bas in self.ny:
            v = 100.0 * (N[i, ri] / N[i4, ri] - 1.0)
            rows.append(dict(cls="regional_nights_yoy", obs_id=oid, quarter=self.q[i],
                             region=REGIONS[ri], lo=lo, hi=hi, fitted=v,
                             resid=hinge(v, lo, hi), inside=hinge(v, lo, hi) <= TOL))
        for i, i4, ri, lo, hi, oid in self.ar:
            v = 100.0 * (ADR[i, ri] / ADR[i4, ri] - 1.0)
            rows.append(dict(cls="regional_adr_yoy_reported", obs_id=oid, quarter=self.q[i],
                             region=REGIONS[ri], lo=lo, hi=hi, fitted=v,
                             resid=hinge(v, lo, hi), inside=hinge(v, lo, hi) <= TOL))
        for i, i4, ri, lo, hi, oid, f in self.ax:
            v = 100.0 * (ADR[i, ri] / ADR[i4, ri] - 1.0) - f
            rows.append(dict(cls="regional_adr_yoy_exfx", obs_id=oid, quarter=self.q[i],
                             region=REGIONS[ri], lo=lo, hi=hi, fitted=v,
                             resid=hinge(v, lo, hi), inside=hinge(v, lo, hi) <= TOL))
        return pd.DataFrame(rows)


def block_bootstrap(rec, theta_hat, n_rep=60, block=4, seed=7, max_nfev=400):
    """Weighted block bootstrap: resample 4-quarter blocks of the panel with
    multinomial weights, refit, and keep the reconstructed panel."""
    rng = np.random.default_rng(seed)
    T = rec.T
    nb = int(np.ceil(T / block))
    starts = [b * block for b in range(nb)]
    keep = []
    for _ in range(n_rep):
        cnt = rng.multinomial(nb, np.ones(nb) / nb)
        wt = np.zeros(T)
        for b, c in zip(starts, cnt):
            wt[b:b + block] += c
        wt = np.maximum(wt, 1e-3)
        th, fit = rec.fit(theta0=theta_hat, wt=wt, max_nfev=max_nfev)
        if not fit.success:
            th, fit = rec.fit(theta0=th, wt=wt, max_nfev=2000)
        if not fit.success:
            raise RuntimeError(f"Bootstrap convergence failure: {fit.message}")
        S, N, tr, GBV, ADR = rec.forward(th)
        keep.append((S, N, GBV, ADR))
    return keep
