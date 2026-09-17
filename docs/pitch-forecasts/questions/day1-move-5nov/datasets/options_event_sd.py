"""Options-implied 5 Nov event sd from the fresh yfinance chain (sources/yfinance_abnb_chain_*.csv).
Method follows research/notes/reverse_dcf/B_options-implied.md section 3.2: Black-76 IV from bid/ask mids on the
parity forward, quadratic smile in log-moneyness fitted to OTM quotes, ATM IV read at the forward,
E = T_post * (sig_post^2 - sig_pre^2) for pre/post-print expiry pairs, plus a one-print LS fit.
Run: py -3.13 docs/pitch-forecasts/questions/day1-move-5nov/datasets/options_event_sd.py
"""
import glob, json, math, pathlib, sys
import numpy as np, pandas as pd
from scipy.optimize import brentq
from scipy.stats import norm

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "sources"
chain_file = sorted(glob.glob(str(SRC / "yfinance_abnb_chain_2*.csv")))[-1]
meta = json.load(open(sorted(glob.glob(str(SRC / "yfinance_abnb_chain_meta_*.json")))[-1]))
ch = pd.read_csv(chain_file)
S = meta["spot"]; r = 0.04
PRINT = pd.Timestamp("2026-11-05")
asof = pd.Timestamp(meta["spot_date"])

def b76(F, K, T, sig, cp):
    d1 = (math.log(F / K) + 0.5 * sig * sig * T) / (sig * math.sqrt(T)); d2 = d1 - sig * math.sqrt(T)
    df = math.exp(-r * T)
    return df * (F * norm.cdf(d1) - K * norm.cdf(d2)) if cp == "call" else df * (K * norm.cdf(-d2) - F * norm.cdf(-d1))

def iv(px, F, K, T, cp):
    try:
        return brentq(lambda s: b76(F, K, T, s, cp) - px, 0.02, 3.0)
    except Exception:
        return np.nan

rows = []
for e, g in ch.groupby("expiry"):
    T = (pd.Timestamp(e) - asof).days / 365.0
    if T <= 0: continue
    g = g[(g.bid > 0) & (g.ask >= g.bid)].copy()
    g["mid"] = (g.bid + g.ask) / 2; g["rel"] = (g.ask - g.bid) / g["mid"]
    g = g[(g.rel <= 0.6) & (g["mid"] >= 0.10)]
    # parity forward from strikes with both sides
    c = g[g.type == "call"].set_index("strike")["mid"]; p = g[g.type == "put"].set_index("strike")["mid"]
    both = c.index.intersection(p.index)
    both = [k for k in both if abs(math.log(k / S)) < 0.10]
    if len(both) >= 2:
        F = float(np.median([k + (c[k] - p[k]) * math.exp(r * T) for k in both]))
    else:
        F = S * math.exp(r * T)
    g["F"] = F; g["T"] = T
    g["x"] = np.log(g.strike / F)
    otm = g[((g.type == "call") & (g.strike > F)) | ((g.type == "put") & (g.strike < F))].copy()
    otm = otm[otm.x.abs() <= 0.45]
    otm["iv"] = [iv(m, F, k, T, t) for m, k, t in zip(otm["mid"], otm.strike, otm.type)]
    otm = otm.dropna(subset=["iv"])
    n_us = len(otm)
    atm = np.nan; rmse = np.nan; iv90 = iv110 = np.nan
    if n_us >= 4:
        w = 1.0 / (otm.rel + 0.05)
        X = np.vstack([np.ones(n_us), otm.x, otm.x ** 2]).T
        beta = np.linalg.lstsq(X * w.values[:, None], otm.iv.values * w.values, rcond=None)[0]
        atm = beta[0]; rmse = float(np.sqrt(np.mean((X @ beta - otm.iv.values) ** 2)))
        iv90 = beta[0] + beta[1] * math.log(0.9) + beta[2] * math.log(0.9) ** 2
        iv110 = beta[0] + beta[1] * math.log(1.1) + beta[2] * math.log(1.1) ** 2
    # same-strike straddle nearest spot
    ks = sorted(set(c.index) & set(p.index), key=lambda k: abs(k - S))
    strad = np.nan; kst = np.nan; sb = sa = np.nan
    if ks:
        kst = ks[0]
        cc = g[(g.type == "call") & (g.strike == kst)].iloc[0]; pp = g[(g.type == "put") & (g.strike == kst)].iloc[0]
        strad = (cc.mid + pp.mid) / S * 100; sb = (cc.bid + pp.bid) / S * 100; sa = (cc.ask + pp.ask) / S * 100
    n_prints = int(pd.Timestamp(e) >= PRINT)
    rows.append(dict(expiry=e, days=(pd.Timestamp(e) - asof).days, T=T, F=round(F, 2), n_prints_inside=n_prints,
                     n_usable_otm=n_us, atm_iv_pct=round(atm * 100, 2) if atm == atm else np.nan,
                     smile_rmse_volpts=round(rmse * 100, 2) if rmse == rmse else np.nan,
                     iv90_pct=round(iv90 * 100, 2) if iv90 == iv90 else np.nan, iv110_pct=round(iv110 * 100, 2) if iv110 == iv110 else np.nan,
                     skew_90_110_volpts=round((iv90 - iv110) * 100, 2) if iv90 == iv90 else np.nan,
                     straddle_strike=kst, straddle_mid_pct_spot=round(strad, 3), straddle_bid_pct=round(sb, 3), straddle_ask_pct=round(sa, 3),
                     open_interest=int(g.openInterest.fillna(0).sum())))
ts = pd.DataFrame(rows).sort_values("expiry")
ts.to_csv(HERE / "options_term_structure.csv", index=False)
print(ts.to_string(index=False))

# event variance: pairs
def pair(pre, post):
    a = ts[ts.expiry == pre].iloc[0]; b = ts[ts.expiry == post].iloc[0]
    E = b["T"] * ((b.atm_iv_pct / 100) ** 2 - (a.atm_iv_pct / 100) ** 2)
    return E
out = []
for pre in ["2026-10-16", "2026-10-23", "2026-10-30"]:
    for post in ["2026-11-20", "2026-12-18"]:
        if pd.isna(ts[ts.expiry == pre].atm_iv_pct.iloc[0]) or pd.isna(ts[ts.expiry == post].atm_iv_pct.iloc[0]): continue
        E = pair(pre, post)
        out.append(dict(spec=f"pair {pre} vs {post}", event_var=E, event_sd_pct=round(math.sqrt(max(E, 0)) * 100, 2) if E > 0 else np.nan))
# LS one-print-max: sig^2 T = b T + E n over expiries to Jan 27 with atm
sub = ts[(ts.expiry <= "2027-01-15") & ts.atm_iv_pct.notna() & (ts.n_usable_otm >= 4)]
X = np.vstack([sub["T"].values, sub.n_prints_inside.values]).T; y = ((sub.atm_iv_pct / 100) ** 2 * sub["T"]).values
b, E = np.linalg.lstsq(X, y, rcond=None)[0]
out.append(dict(spec=f"LS one-print-max on {list(sub.expiry)}", event_var=E, event_sd_pct=round(math.sqrt(max(E, 0)) * 100, 2), background_vol_pct=round(math.sqrt(b) * 100, 2)))
# LOO
loo = []
for i in range(len(sub)):
    s2 = sub.drop(sub.index[i]); X2 = np.vstack([s2["T"].values, s2.n_prints_inside.values]).T; y2 = ((s2.atm_iv_pct / 100) ** 2 * s2["T"]).values
    if len(s2) >= 3 and s2.n_prints_inside.nunique() > 1:
        _, E2 = np.linalg.lstsq(X2, y2, rcond=None)[0]; loo.append(math.sqrt(max(E2, 0)) * 100)
out.append(dict(spec="LS one-print-max LOO range", event_sd_pct=f"{min(loo):.2f}..{max(loo):.2f}" if loo else ""))
# 1 vol point leg sensitivity on 30 Oct / 20 Nov pair
a = ts[ts.expiry == "2026-10-30"].iloc[0]; bb = ts[ts.expiry == "2026-11-20"].iloc[0]
for dpre in (-1, 0, 1):
    for dpost in (-1, 0, 1):
        E = bb["T"] * (((bb.atm_iv_pct + dpost) / 100) ** 2 - ((a.atm_iv_pct + dpre) / 100) ** 2)
        out.append(dict(spec=f"pair 30Oct/20Nov leg sensitivity dpre {dpre} dpost {dpost}", event_var=E, event_sd_pct=round(math.sqrt(max(E, 0)) * 100, 2)))
ev = pd.DataFrame(out); ev.to_csv(HERE / "options_event_sd.csv", index=False)
print(ev.to_string(index=False))
print("pull_utc", meta["pull_utc"], "spot", S, "as of close", meta["spot_date"])
