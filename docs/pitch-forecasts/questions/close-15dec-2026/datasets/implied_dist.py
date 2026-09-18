"""Own Black-76 IVs from the fresh yfinance chain (mids, parity forward, r from ^IRX), quadratic smile
per expiry, ATM IV, straddles, event sd (16 Oct vs 20 Nov pair and 18 Dec), and the lognormal /
smile implied distributions at 15 Dec 2026 (18 Dec expiry) and 12 Feb 2027 (Jan 15 / Mar 19 interpolation).
Replicates the method of research/notes/reverse_dcf/B_options-implied.md on the 16 Sep 2026 close."""
import glob, json, math, pathlib, sys
import numpy as np, pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq
here = pathlib.Path(__file__).resolve().parent.parent
src = here / "sources"; out = here / "datasets"
chain_f = sorted(src.glob("yfinance_option_chain_*.csv"))[-1]
ts = chain_f.stem.split("_")[-1]
ch = pd.read_csv(chain_f)
hist = pd.read_csv(sorted(src.glob("yfinance_abnb_history_2y_*.csv"))[-1], index_col=0)
S = float(hist["Close"].iloc[-1]); r = 0.0397
asof = pd.Timestamp("2026-09-16")
def b76(F, K, T, sig, cp):
    d1 = (math.log(F/K) + 0.5*sig*sig*T)/(sig*math.sqrt(T)); d2 = d1 - sig*math.sqrt(T)
    df = math.exp(-r*T)
    return df*(F*norm.cdf(d1) - K*norm.cdf(d2)) if cp == "call" else df*(K*norm.cdf(-d2) - F*norm.cdf(-d1))
def iv(price, F, K, T, cp):
    try: return brentq(lambda s: b76(F, K, T, s, cp) - price, 1e-3, 5.0)
    except Exception: return np.nan
ch["mid"] = (ch.bid + ch.ask)/2; ch["spread_rel"] = (ch.ask - ch.bid)/ch.mid
rows = []; dists = {}
for e, g in ch.groupby("expiry"):
    T = (pd.Timestamp(e) - asof).days/365.0
    g = g[(g.bid > 0) & (g.ask >= g.bid) & (g.mid >= 0.10) & (g.spread_rel <= 0.60)].copy()
    c = g[g.type == "call"].set_index("strike").mid; p = g[g.type == "put"].set_index("strike").mid
    ks = sorted(set(c.index) & set(p.index))
    near = [k for k in ks if abs(k/S - 1) < 0.12]
    Fs = [k + (c[k] - p[k])*math.exp(r*T) for k in near]
    F = float(np.median(Fs)) if Fs else S*math.exp(r*T)
    g["F"] = F; g["x"] = np.log(g.strike/F)
    otm = g[((g.type == "call") & (g.strike > F)) | ((g.type == "put") & (g.strike < F))].copy()
    otm = otm[otm.x.abs() <= 0.45]
    otm["iv"] = [iv(m, F, k, T, t) for m, k, t in zip(otm.mid, otm.strike, otm.type)]
    otm = otm.dropna(subset=["iv"])
    if len(otm) >= 4:
        w = (1/np.maximum(otm.spread_rel, 0.05)).to_numpy()
        A = np.vstack([np.ones(len(otm)), otm.x.to_numpy(), otm.x.to_numpy()**2]).T
        coef = np.linalg.lstsq(A*w[:, None], otm.iv.to_numpy()*w, rcond=None)[0]
        atm = coef[0]; rmse = float(np.sqrt(np.mean((A@coef - otm.iv.to_numpy())**2)))
    else:
        coef = None; atm = float(otm.iv.median()) if len(otm) else np.nan; rmse = np.nan
    k0 = min(ks, key=lambda k: abs(k - S)) if ks else np.nan
    strad = (c[k0] + p[k0]) if ks else np.nan
    rows.append(dict(expiry=e, days=(pd.Timestamp(e)-asof).days, T=T, F=F, n_usable_otm=len(otm), atm_iv=atm*100 if atm==atm else np.nan,
                     smile_b=coef[1] if coef is not None else np.nan, smile_c=coef[2] if coef is not None else np.nan, smile_rmse_volpts=rmse*100 if rmse==rmse else np.nan,
                     straddle_strike=k0, straddle_mid=strad, straddle_pct_spot=strad/S*100 if strad==strad else np.nan,
                     rr25_proxy_volpts=(coef[1]*2*0.25*atm*math.sqrt(T))*100 if coef is not None else np.nan))
    dists[e] = dict(T=T, F=F, coef=coef.tolist() if coef is not None else None, atm=atm)
ts_df = pd.DataFrame(rows); print(ts_df.round(3).to_string())
ts_df.to_csv(out / f"implied_term_structure_{ts}.csv", index=False)
# event sd: pair pre (16 Oct if present else nearest pre-print) vs 20 Nov; also vs 18 Dec
pre = ts_df[ts_df.expiry < "2026-11-05"].dropna(subset=["atm_iv"]); pre = pre[pre.n_usable_otm >= 6].iloc[-1]
ev = {}
for post_e in ("2026-11-20", "2026-12-18", "2027-01-15"):
    post = ts_df[ts_df.expiry == post_e].iloc[0]
    E = float(post["T"])*((float(post["atm_iv"])/100)**2 - (float(pre["atm_iv"])/100)**2)
    ev[post_e] = math.sqrt(max(E, 0))*100
print("pre leg", pre.expiry, pre.atm_iv, "event sd by post leg", ev)
# lognormal + smile distributions at target dates
def dist_at(target, e1, e2=None, label=""):
    Tt = (pd.Timestamp(target) - asof).days/365.0
    if e2 is None:
        d = dists[e1]; sig = d["atm"]; F = S*math.exp(r*Tt); coef = d["coef"]
    else:
        d1, d2 = dists[e1], dists[e2]; w = (Tt - d1["T"])/(d2["T"] - d1["T"])
        var = (1-w)*d1["atm"]**2*d1["T"] + w*d2["atm"]**2*d2["T"]; sig = math.sqrt(var/Tt); F = S*math.exp(r*Tt)
        coef = [(1-w)*a + w*b for a, b in zip(d1["coef"], d2["coef"])]
    # lognormal percentiles
    pct = {}
    for q in (5, 10, 25, 50, 75, 90, 95):
        pct[q] = F*math.exp(-0.5*sig*sig*Tt + sig*math.sqrt(Tt)*norm.ppf(q/100))
    # smile RND via Breeden-Litzenberger on the fitted smile
    Ks = np.linspace(60, 320, 2601); xs = np.log(Ks/F)
    ivs = np.clip(coef[0] + coef[1]*np.clip(xs, -0.45, 0.45) + coef[2]*np.clip(xs, -0.45, 0.45)**2, 0.05, 2.0)
    Cs = np.array([b76(F, K, Tt, s, "call") for K, s in zip(Ks, ivs)])*math.exp(r*Tt)
    dens = np.gradient(np.gradient(Cs, Ks), Ks); dens = np.clip(dens, 0, None); dens /= np.trapezoid(dens, Ks)
    cdf = np.cumsum(dens)*(Ks[1]-Ks[0])
    spct = {q: float(np.interp(q/100, cdf, Ks)) for q in (5, 10, 25, 50, 75, 90, 95)}
    thr = {f"P(<={t})": float(np.interp(t, Ks, cdf)) for t in (143, 150, 180)}
    thr_ln = {f"P(<={t})": float(norm.cdf((math.log(t/F) + 0.5*sig*sig*Tt)/(sig*math.sqrt(Tt)))) for t in (143, 150, 180)}
    res = dict(label=label, target=target, T_years=Tt, forward=F, sigma_pct=sig*100, lognormal=pct, smile_rnd=spct, thr_smile=thr, thr_lognormal=thr_ln)
    print(json.dumps(res, indent=1, default=float)); return res
res = {"dec15": dist_at("2026-12-15", "2026-12-18", label="15 Dec 2026, from 18 Dec expiry smile"),
       "feb12": dist_at("2027-02-12", "2027-01-15", "2027-03-19", label="12 Feb 2027, Jan/Mar variance interpolation")}
res["event_sd_pct"] = ev; res["pre_leg"] = dict(expiry=pre.expiry, atm_iv=float(pre.atm_iv)); res["spot"] = S; res["r"] = r; res["chain_ts"] = ts
json.dump(res, open(out / f"implied_dist_{ts}.json", "w"), indent=1, default=float)
