"""Weekly options ledger for SIG vs peers (built 2026-09-02).

For each ticker and for two expiries (the first expiry after the Sept 9 print and the next
monthly), pulls the yfinance chain, keeps quotes with a live bid/ask, and computes:
  - spot, expiry, days to expiry
  - ATM implied vol (avg of nearest call/put) and the ATM straddle as % of spot (the "implied move" to expiry)
  - 25-delta put and call IVs (Black-Scholes deltas from each quote's IV) and the skew (put IV - call IV)
  - put/call ratios on open interest and volume
  - event-implied move: variance differencing between the near expiry (contains the print) and the far
    expiry (diffusion baseline): sigma_event^2 = sigma_near^2 * T_near - sigma_far^2 * T_near  (floored at 0),
    reported as sqrt(var_event) * 0.8 (straddle-equivalent). Labelled as an approximation.
Appends one row per ticker/expiry to options_ledger.csv with the run date. Run weekly; run on Sept 8 pre-print.
Caveat: yfinance implied volatilities are Yahoo's; after-hours quotes without bid/ask are dropped.
"""
import math, datetime as dt, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import yfinance as yf
from math import log, sqrt, exp
from statistics import NormalDist

HERE = r"C:\Users\krish\BAM_comp\SIG\research\data"
TICKERS = ["SIG", "GAP", "M", "URBN", "ANF", "AEO", "BRLT", "XRT"]
NEAR_TARGET = "2026-09-18"   # first listed expiry after the Sept 9 print
FAR_TARGET = "2026-10-16"    # next monthly
N = NormalDist()

def bs_delta(S, K, T, sigma, call, r=0.04):
    if T <= 0 or sigma <= 0: return np.nan
    d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    return N.cdf(d1) if call else N.cdf(d1) - 1

def pick_expiry(exps, target):
    return min(exps, key=lambda e: abs((pd.Timestamp(e) - pd.Timestamp(target)).days))

def chain_stats(tk, exp, spot, today):
    t = yf.Ticker(tk)
    ch = t.option_chain(exp)
    c = ch.calls.copy(); p = ch.puts.copy()
    for d in (c, p):
        d["mid"] = (d["bid"] + d["ask"]) / 2
    c = c[(c["bid"] > 0) & (c["ask"] > 0) & (c["impliedVolatility"] > 0.02)]
    p = p[(p["bid"] > 0) & (p["ask"] > 0) & (p["impliedVolatility"] > 0.02)]
    if len(c) < 3 or len(p) < 3: return None
    T = max((pd.Timestamp(exp) - today).days, 1) / 365
    kc = c.iloc[(c["strike"] - spot).abs().argsort()[:1]]; kp = p.iloc[(p["strike"] - spot).abs().argsort()[:1]]
    atm_iv = float((kc["impliedVolatility"].iloc[0] + kp["impliedVolatility"].iloc[0]) / 2)
    straddle = float(kc["mid"].iloc[0] + kp["mid"].iloc[0])
    c["delta"] = [bs_delta(spot, k, T, s, True) for k, s in zip(c["strike"], c["impliedVolatility"])]
    p["delta"] = [bs_delta(spot, k, T, s, False) for k, s in zip(p["strike"], p["impliedVolatility"])]
    c25 = c.iloc[(c["delta"] - 0.25).abs().argsort()[:1]]; p25 = p.iloc[(p["delta"] + 0.25).abs().argsort()[:1]]
    iv_c25 = float(c25["impliedVolatility"].iloc[0]); iv_p25 = float(p25["impliedVolatility"].iloc[0])
    oi_pc = float(p["openInterest"].sum() / max(c["openInterest"].sum(), 1))
    vol_pc = float(p["volume"].fillna(0).sum() / max(c["volume"].fillna(0).sum(), 1))
    return dict(expiry=exp, dte=int(T * 365), atm_iv_pct=round(atm_iv * 100, 1), straddle_pct_spot=round(straddle / spot * 100, 2),
                iv_put25_pct=round(iv_p25 * 100, 1), k_put25=float(p25["strike"].iloc[0]), iv_call25_pct=round(iv_c25 * 100, 1),
                k_call25=float(c25["strike"].iloc[0]), skew25_pts=round((iv_p25 - iv_c25) * 100, 1),
                put_call_oi=round(oi_pc, 2), put_call_vol=round(vol_pc, 2), n_calls=len(c), n_puts=len(p), T=T)

def main():
    today = pd.Timestamp(dt.date.today())
    rows = []
    for tk in TICKERS:
        try:
            t = yf.Ticker(tk); spot = float(t.fast_info["last_price"]); exps = list(t.options)
            if not exps: print(tk, "no options"); continue
            near = pick_expiry(exps, NEAR_TARGET); far = pick_expiry([e for e in exps if e > near] or exps, FAR_TARGET)
            sn = chain_stats(tk, near, spot, today); sf = chain_stats(tk, far, spot, today) if far != near else None
            if sn is None: print(tk, "thin chain"); continue
            ev = np.nan
            if sf:
                var_ev = (sn["atm_iv_pct"] / 100) ** 2 * sn["T"] - (sf["atm_iv_pct"] / 100) ** 2 * sn["T"]
                ev = round(sqrt(max(var_ev, 0)) * 0.8 * 100, 2)
            for s in ([sn] + ([sf] if sf else [])):
                s = {k: v for k, v in s.items() if k != "T"}
                rows.append(dict(run_date=today.date().isoformat(), ticker=tk, spot=round(spot, 2), **s,
                                 event_implied_move_pct=(ev if s["expiry"] == near else np.nan)))
            print(f"{tk:5s} spot {spot:7.2f} | {near}: straddle {sn['straddle_pct_spot']:5.2f}% atm iv {sn['atm_iv_pct']:5.1f}% skew25 {sn['skew25_pts']:+5.1f} P/C oi {sn['put_call_oi']:.2f}"
                  + (f" | {far}: straddle {sf['straddle_pct_spot']:5.2f}% atm iv {sf['atm_iv_pct']:5.1f}% | event-implied ~{ev:.1f}%" if sf else ""))
        except Exception as e:
            print(tk, "ERR", str(e)[:120])
    df = pd.DataFrame(rows)
    path = f"{HERE}\\options_ledger.csv"
    try:
        old = pd.read_csv(path); df = pd.concat([old, df], ignore_index=True)
    except FileNotFoundError:
        pass
    df.to_csv(path, index=False)
    print("saved", path, len(df), "rows")

if __name__ == "__main__":
    main()
