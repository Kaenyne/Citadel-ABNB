"""Workstream B: what the options market prices for ABNB (live yfinance chain, 11 Sep 2026 close).

Reads  : data/processed/reverse_dcf/B/raw_chain_<stamp>.csv (from B_pull_chains.py), B_pull_meta.json,
         data/processed/overnight/20_executable_returns.csv, 04_consensus_at_print.csv,
         02_kpi_panel_quarterly.csv
Writes : data/processed/reverse_dcf/B/B_*.csv (every table in the note)
Run    : py -3.13 analysis/src/reverse_dcf/B_options_implied.py

Conventions
  - valuation time = 11 Sep 2026 16:00 ET (the pull was made 12 Sep 04:49 UTC, i.e. Friday close quotes)
  - r = 4.0% continuous (3-month T-bill ^IRX closed 3.91% on 11 Sep; brief says 4.0-4.2%); no dividends
  - T in calendar years /365 to 16:00 ET on the expiry date
  - every IV used numerically is recomputed here from mid quotes with Black-76 on the parity-implied
    forward; yfinance's own impliedVolatility column is kept for comparison only
  - a "straddle" is a same-strike call + put, both two-sided
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "processed" / "reverse_dcf" / "B"
OVN = ROOT / "data" / "processed" / "overnight"
META = json.load(open(OUT / "B_pull_meta.json"))
RAW = pd.read_csv(OUT / META["raw_file"])
SPOT = float(META["spot_last_close"])
R = 0.040
VAL = pd.Timestamp("2026-09-11 16:00", tz="America/New_York")
PRINT_DATES = {  # release after the close; the expiry "contains" a print if it settles after 16:05 ET that day
    "2026-11-05": "5 Nov 2026 (Zacks expected date; not company-confirmed)",
    "2027-02-11": "est. 4Q26 print, pattern (12-13 Feb in 2025-26)",
    "2027-05-06": "est. 1Q27 print, pattern (1-8 May)",
    "2027-08-05": "est. 2Q27 print, pattern (6 Aug)",
    "2027-11-04": "est. 3Q27 print, pattern (5-7 Nov)",
}
PRICE_POINTS = [150.0, 165.0, 170.19, 179.5, 185.0, 197.5, 220.0]
BRIEF_LABELS = {150.0: "bear tape", 165.0: "p25 target", 170.19: "price", 179.5: "mean target",
                185.0: "median yfinance target", 197.5: "p75 target", 220.0: "top target"}


# ------------------------------------------------------------------ Black-76 helpers
def b76(F, K, T, sig, r, call):
    if T <= 0 or sig <= 0:
        return max(0.0, (F - K) if call else (K - F)) * math.exp(-r * T)
    d1 = (math.log(F / K) + 0.5 * sig * sig * T) / (sig * math.sqrt(T)); d2 = d1 - sig * math.sqrt(T)
    if call:
        return math.exp(-r * T) * (F * norm.cdf(d1) - K * norm.cdf(d2))
    return math.exp(-r * T) * (K * norm.cdf(-d2) - F * norm.cdf(-d1))


def iv(price, F, K, T, r, call):
    intrinsic = max(0.0, (F - K) if call else (K - F)) * math.exp(-r * T)
    if price <= intrinsic + 1e-9:
        return np.nan
    try:
        return brentq(lambda s: b76(F, K, T, s, r, call) - price, 1e-4, 5.0, xtol=1e-8)
    except ValueError:
        return np.nan


def delta(F, K, T, sig, call):
    d1 = (math.log(F / K) + 0.5 * sig * sig * T) / (sig * math.sqrt(T))
    return norm.cdf(d1) if call else norm.cdf(d1) - 1.0


def T_years(expiry):
    settle = pd.Timestamp(f"{expiry} 16:00", tz="America/New_York")
    return (settle - VAL).total_seconds() / (365.0 * 86400.0)


def prints_inside(expiry):
    settle = pd.Timestamp(f"{expiry} 16:00", tz="America/New_York")
    return sum(1 for d in PRINT_DATES if pd.Timestamp(f"{d} 16:05", tz="America/New_York") < settle)


# ------------------------------------------------------------------ 1. clean the chain
def clean_chain():
    d = RAW.copy()
    d["two_sided"] = (d.bid > 0) & (d.ask >= d.bid)
    d["mid"] = (d.bid + d.ask) / 2
    d["rel_spread"] = (d.ask - d.bid) / d.mid.replace(0, np.nan)
    d["T"] = d.expiry.map(T_years)
    d["moneyness"] = d.strike / SPOT
    rows, fwd_rows, parity_rows = [], [], []
    for e, g in d.groupby("expiry"):
        T = g["T"].iloc[0]
        c = g[(g.side == "call") & g.two_sided].set_index("strike")
        p = g[(g.side == "put") & g.two_sided].set_index("strike")
        common = sorted(set(c.index) & set(p.index))
        # parity-implied forward from near-ATM common strikes
        near = [k for k in common if abs(k / SPOT - 1) <= 0.12]
        Fk = {k: k + (c.loc[k, "mid"] - p.loc[k, "mid"]) * math.exp(R * T) for k in near}
        F = float(np.median(list(Fk.values()))) if Fk else SPOT * math.exp(R * T)
        F_theory = SPOT * math.exp(R * T)
        for k in near:
            # parity bounds: C - P must sit between (bidC-askP) and (askC-bidP); forward outside means stale
            lo = (c.loc[k, "bid"] - p.loc[k, "ask"]) * math.exp(R * T) + k
            hi = (c.loc[k, "ask"] - p.loc[k, "bid"]) * math.exp(R * T) + k
            parity_rows.append(dict(expiry=e, strike=k, F_from_strike=round(Fk[k], 3),
                                    F_bid_ask_low=round(lo, 3), F_bid_ask_high=round(hi, 3),
                                    F_theory_spot_carry=round(F_theory, 3),
                                    theory_inside_bid_ask=bool(lo <= F_theory <= hi),
                                    dev_from_median_pct=round((Fk[k] / F - 1) * 100, 3)))
        fwd_rows.append(dict(expiry=e, T=round(T, 5), days=round(T * 365), n_parity_strikes=len(near),
                             F_parity_median=round(F, 3), F_theory_spot_carry=round(F_theory, 3),
                             F_parity_minus_theory_pct=round((F / F_theory - 1) * 100, 3),
                             F_parity_strike_range_pct=round((max(Fk.values()) - min(Fk.values())) / SPOT * 100, 3) if Fk else np.nan,
                             n_theory_outside_bid_ask=int(sum(1 for r_ in parity_rows if r_["expiry"] == e and not r_["theory_inside_bid_ask"]))))
        for _, r_ in g[g.two_sided].iterrows():
            call = r_.side == "call"
            otm = (r_.strike >= F) if call else (r_.strike <= F)
            s_mid = iv(r_.mid, F, r_.strike, T, R, call)
            s_bid = iv(r_.bid, F, r_.strike, T, R, call)
            s_ask = iv(r_.ask, F, r_.strike, T, R, call)
            rows.append(dict(expiry=e, T=T, side=r_.side, strike=r_.strike, bid=r_.bid, ask=r_.ask, mid=r_.mid,
                             rel_spread=r_.rel_spread, volume=r_.volume, openInterest=r_.openInterest,
                             lastTradeDate=r_.lastTradeDate, yf_iv=r_.impliedVolatility, F=F,
                             log_moneyness=math.log(r_.strike / F), otm=otm, iv_mid=s_mid, iv_bid=s_bid, iv_ask=s_ask,
                             usable=bool(otm and np.isfinite(s_mid) and r_.rel_spread <= 0.6 and
                                         abs(math.log(r_.strike / F)) <= 0.45 and r_.mid >= 0.10)))
    ch = pd.DataFrame(rows)
    fwd = pd.DataFrame(fwd_rows)
    par = pd.DataFrame(parity_rows)
    ch.to_csv(OUT / "B_chain_clean.csv", index=False)
    fwd.to_csv(OUT / "B_forwards.csv", index=False)
    par.to_csv(OUT / "B_parity_check.csv", index=False)
    return ch, fwd


# ------------------------------------------------------------------ 2. smile fit per expiry (quadratic in log-moneyness)
def fit_smile(g):
    """Weighted LS of iv_mid on (1, x, x^2), x = ln(K/F), OTM two-sided quotes only.  Weights = 1/spread in vol."""
    u = g[g.usable].copy()
    if len(u) < 4:
        return None
    w = 1.0 / np.clip((u.iv_ask - u.iv_bid).fillna(0.2).abs(), 0.01, None)
    X = np.column_stack([np.ones(len(u)), u.log_moneyness, u.log_moneyness ** 2])
    W = np.sqrt(w.values)
    coef, *_ = np.linalg.lstsq(X * W[:, None], u.iv_mid.values * W, rcond=None)
    fitted = X @ coef
    return dict(a=coef[0], b=coef[1], c=coef[2], n=len(u), xmin=u.log_moneyness.min(), xmax=u.log_moneyness.max(),
                rmse_volpts=float(np.sqrt(np.mean((u.iv_mid.values - fitted) ** 2)) * 100))


def smile_iv(sm, x):
    x = np.clip(x, sm["xmin"], sm["xmax"])  # flat extrapolation outside the quoted range
    return np.maximum(sm["a"] + sm["b"] * x + sm["c"] * x * x, 0.05)


def smile_from_params(a, b, c, xmin, xmax, n=0, rmse=np.nan):
    return dict(a=a, b=b, c=c, xmin=xmin, xmax=xmax, n=n, rmse_volpts=rmse)


# ------------------------------------------------------------------ 3. risk-neutral density from a smile (Breeden-Litzenberger on the smooth call curve)
def rnd_from_smile(sm, F, T, r, kmin=40.0, kmax=500.0, n=4601):
    K = np.linspace(kmin, kmax, n)
    sig = smile_iv(sm, np.log(K / F))
    C = np.array([b76(F, k, T, s, r, True) for k, s in zip(K, sig)])
    dK = K[1] - K[0]
    f = np.exp(r * T) * np.gradient(np.gradient(C, dK), dK)
    neg_mass = float(np.sum(np.clip(f, None, 0)) * dK)
    f = np.clip(f, 0, None)
    f /= np.sum(f) * dK
    cdf = np.cumsum(f) * dK
    return K, f, cdf, neg_mass


def pct_from_cdf(K, cdf, q):
    return float(np.interp(q, cdf, K))


def prob_above(K, cdf, x):
    return float(1.0 - np.interp(x, K, cdf))


def rnd_from_mids(g, F, T, r):
    """Direct Breeden-Litzenberger on observed OTM mids converted to calls via parity, after a light
    monotone smoothing (cubic spline on call prices in K).  Used only as a cross-check on one expiry."""
    from scipy.interpolate import UnivariateSpline
    u = g[g.usable].copy()
    u["call_px"] = np.where(u.side == "call", u.mid, u.mid + (F - u.strike) * math.exp(-r * T))
    u = u.sort_values("strike").groupby("strike", as_index=False).call_px.mean()
    w = np.ones(len(u))
    spl = UnivariateSpline(u.strike.values, u.call_px.values, w=w, k=3, s=len(u) * 0.05)
    K = np.linspace(u.strike.min(), u.strike.max(), 2001)
    f = np.exp(r * T) * spl.derivative(2)(K)
    dK = K[1] - K[0]
    neg_mass = float(np.sum(np.clip(f, None, 0)) * dK)
    f = np.clip(f, 0, None)
    mass = float(np.sum(f) * dK)  # mass inside the quoted strike range (tails are not observed)
    return K, f, neg_mass, mass, u


# ------------------------------------------------------------------ 4. term structure table
def term_structure(ch, fwd):
    rows, smiles = [], {}
    for e, g in ch.groupby("expiry"):
        T = g["T"].iloc[0]; F = g.F.iloc[0]
        sm = fit_smile(g); smiles[e] = sm
        # ATM IV three ways: (i) smile at x=0, (ii) linear interpolation of OTM IVs at K=F, (iii) yfinance mean of nearest call/put
        atm_smile = float(smile_iv(sm, 0.0)) if sm else np.nan
        u = g[g.usable].sort_values("strike")
        atm_interp = float(np.interp(F, u.strike, u.iv_mid)) if len(u) >= 2 else np.nan
        # same-strike straddle nearest spot
        c = g[(g.side == "call")].set_index("strike"); p = g[(g.side == "put")].set_index("strike")
        common = sorted(set(c.index) & set(p.index))
        k = min(common, key=lambda x: abs(x - SPOT)) if common else np.nan
        if common:
            st_mid = c.loc[k, "mid"] + p.loc[k, "mid"]; st_bid = c.loc[k, "bid"] + p.loc[k, "bid"]; st_ask = c.loc[k, "ask"] + p.loc[k, "ask"]
            yf_atm = (c.loc[k, "yf_iv"] + p.loc[k, "yf_iv"]) / 2
            own_atm_c, own_atm_p = c.loc[k, "iv_mid"], p.loc[k, "iv_mid"]
        else:
            st_mid = st_bid = st_ask = yf_atm = own_atm_c = own_atm_p = np.nan
        # model (forward) ATM straddle: same-strike at K=F using the smile
        if sm:
            s0 = atm_smile
            st_model = b76(F, F, T, s0, R, True) + b76(F, F, T, s0, R, False)
        else:
            st_model = np.nan
        rows.append(dict(expiry=e, days=round(T * 365), T=round(T, 5), F=round(F, 2), n_prints_inside=prints_inside(e),
                         n_usable_otm_quotes=int(g.usable.sum()), n_two_sided=len(g),
                         open_interest_total=int(g.openInterest.fillna(0).sum()),
                         atm_iv_smile_pct=round(atm_smile * 100, 2), atm_iv_interp_pct=round(atm_interp * 100, 2),
                         atm_iv_yf_nearest_strike_pct=round(yf_atm * 100, 2),
                         straddle_strike=k, straddle_moneyness_pct=round((k / SPOT - 1) * 100, 2) if common else np.nan,
                         straddle_mid=round(st_mid, 3), straddle_bid=round(st_bid, 3), straddle_ask=round(st_ask, 3),
                         straddle_mid_pct_spot=round(st_mid / SPOT * 100, 3), straddle_bid_pct_spot=round(st_bid / SPOT * 100, 3),
                         straddle_ask_pct_spot=round(st_ask / SPOT * 100, 3),
                         straddle_call_iv_own_pct=round(own_atm_c * 100, 2), straddle_put_iv_own_pct=round(own_atm_p * 100, 2),
                         model_atm_fwd_straddle_pct_spot=round(st_model / SPOT * 100, 3),
                         smile_slope_b=round(sm["b"], 4) if sm else np.nan, smile_curv_c=round(sm["c"], 4) if sm else np.nan,
                         smile_rmse_volpts=round(sm["rmse_volpts"], 2) if sm else np.nan,
                         smile_x_range=f"{sm['xmin']:.3f}..{sm['xmax']:.3f}" if sm else ""))
    ts = pd.DataFrame(rows).sort_values("T").reset_index(drop=True)
    ts.to_csv(OUT / "B_term_structure.csv", index=False)
    return ts, smiles


# ------------------------------------------------------------------ 5. event variance
def event_variance(ts):
    """Model: sigma_i^2 T_i = b T_i + E n_i, n_i = number of prints inside expiry i.

    Identification assumption A1: one background (diffusive) variance rate b across the maturities used.
    A2: each print carries the same event variance E, and nothing else scheduled differentiates the maturities.
    A3: ATM IV (smile at x=0) proxies the expiry's total variance.  A4: quotes are contemporaneous (Friday close).
    """
    t = ts[ts.atm_iv_smile_pct.notna()].copy()
    t["sig"] = t.atm_iv_smile_pct / 100
    t["w"] = t.sig ** 2 * t["T"]
    res = []

    def pair(pre, post, label):
        a = t[t.expiry == pre].iloc[0]; b_ = t[t.expiry == post].iloc[0]
        b_bg = a.sig ** 2  # background from the pre-event expiry
        fwd_var = b_.w - a.w  # total variance between the two expiries (brief's formula): event + diffusion
        diffusion = b_bg * (b_["T"] - a["T"])
        E = b_.w - b_bg * b_["T"]  # = T_post (sig_post^2 - sig_pre^2)
        res.append(dict(spec=label, method="pair: E = T_post*(sig_post^2 - sig_pre^2); background b = sig_pre^2",
                        maturities=f"{pre} (pre, {a.days}d) + {post} (post, {b_.days}d)", n_maturities=2,
                        background_vol_pct=round(math.sqrt(b_bg) * 100, 2),
                        fwd_var_between_expiries_brief_formula=round(fwd_var, 6),
                        diffusion_share_of_fwd_var=round(diffusion, 6),
                        event_var=round(E, 6), event_sd_pct=round(math.sqrt(E) * 100, 2) if E > 0 else np.nan,
                        event_exp_abs_move_pct=round(math.sqrt(E) * math.sqrt(2 / math.pi) * 100, 2) if E > 0 else np.nan,
                        fwd_var_sd_pct_if_all_called_event=round(math.sqrt(fwd_var) * 100, 2) if fwd_var > 0 else np.nan,
                        loo_range="", note=""))

    for pre in ["2026-10-16", "2026-10-09", "2026-10-02", "2026-10-23"]:
        if pre in set(t.expiry):
            pair(pre, "2026-11-20", f"pair_{pre}_vs_20Nov")
    pair("2026-10-16", "2026-12-18", "pair_16Oct_vs_18Dec")

    def ls(sub, label, slope=False):
        T = sub["T"].values; n = sub.n_prints_inside.values.astype(float); y = sub.w.values
        X = np.column_stack([T, n] + ([T * T] if slope else []))
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        b0, E = coef[0], coef[1]
        resid = y - X @ coef
        loo = []
        if len(sub) >= 4:
            for i in range(len(sub)):
                m = np.ones(len(sub), bool); m[i] = False
                cf, *_ = np.linalg.lstsq(X[m], y[m], rcond=None)
                if cf[1] > 0: loo.append(math.sqrt(cf[1]) * 100)
        res.append(dict(spec=label, method=("LS: sig^2 T = b0 T + b1 T^2 + E n" if slope else "LS: sig^2 T = b T + E n"),
                        maturities=", ".join(sub.expiry), n_maturities=len(sub),
                        background_vol_pct=round(math.sqrt(b0) * 100, 2) if b0 > 0 else np.nan,
                        fwd_var_between_expiries_brief_formula=np.nan, diffusion_share_of_fwd_var=np.nan,
                        event_var=round(E, 6), event_sd_pct=round(math.sqrt(E) * 100, 2) if E > 0 else np.nan,
                        event_exp_abs_move_pct=round(math.sqrt(E) * math.sqrt(2 / math.pi) * 100, 2) if E > 0 else np.nan,
                        fwd_var_sd_pct_if_all_called_event=np.nan,
                        loo_range=f"{min(loo):.2f}..{max(loo):.2f}" if loo else "",
                        note=(f"b1={coef[2]:.5f} (background var slope per year); " if slope else "") +
                             f"resid rmse (var units) {np.sqrt(np.mean(resid**2)):.5f}"))

    liquid = t[(t.n_usable_otm_quotes >= 6) & (t.expiry != "2026-10-23")]
    ls(liquid[liquid["T"] <= 0.4], "LS_to_Jan27_one_print_max")
    ls(liquid, "LS_all_maturities_multi_print")
    ls(liquid, "LS_all_maturities_multi_print_slope_bg", slope=True)
    two_post = t[t.expiry.isin(["2026-11-20", "2026-12-18"])]
    ls(two_post, "pair_20Nov_vs_18Dec_both_post")
    df = pd.DataFrame(res)
    df.to_csv(OUT / "B_event_variance.csv", index=False)

    # sensitivity: hold the 20 Nov quote, sweep the assumed background
    nov = t[t.expiry == "2026-11-20"].iloc[0]
    pre_ivs = t[(t["T"] < nov["T"]) & (t.expiry != "2026-10-23")].atm_iv_smile_pct / 100
    sens = []
    for bg in np.arange(0.26, 0.44, 0.01):
        E = nov.w - bg ** 2 * nov["T"]
        sens.append(dict(assumed_background_vol_pct=round(bg * 100, 1), event_var=round(E, 6),
                         event_sd_pct=round(math.sqrt(E) * 100, 2) if E > 0 else np.nan,
                         event_exp_abs_move_pct=round(math.sqrt(E) * math.sqrt(2 / math.pi) * 100, 2) if E > 0 else np.nan,
                         inside_observed_pre_event_range=bool(pre_ivs.min() <= bg <= pre_ivs.max())))
    pd.DataFrame(sens).to_csv(OUT / "B_event_sensitivity.csv", index=False)
    # +/- 1 vol point on either leg of the 16 Oct / 20 Nov pair (audit finding 7)
    oct16 = t[t.expiry == "2026-10-16"].iloc[0]
    leg = []
    for dpre in (-1, 0, 1):
        for dpost in (-1, 0, 1):
            sp, sq = oct16.sig + dpre / 100, nov.sig + dpost / 100
            E = nov["T"] * (sq ** 2 - sp ** 2)
            leg.append(dict(d_pre_volpts=dpre, d_post_volpts=dpost, sig_pre_pct=round(sp * 100, 2), sig_post_pct=round(sq * 100, 2),
                            event_sd_pct=round(math.sqrt(E) * 100, 2) if E > 0 else np.nan))
    pd.DataFrame(leg).to_csv(OUT / "B_event_sd_leg_sensitivity.csv", index=False)
    return df, pd.DataFrame(sens), nov


# ------------------------------------------------------------------ 6. skew
def skew_table(ch, ts, smiles):
    rows = []
    for e in ["2026-10-16", "2026-11-20", "2026-12-18", "2027-03-19", "2027-06-17", "2027-09-17", "2027-12-17", "2028-01-21"]:
        sm = smiles.get(e)
        if not sm: continue
        g = ch[ch.expiry == e]; T = g["T"].iloc[0]; F = g.F.iloc[0]
        # 25-delta strikes from the fitted smile (fixed point on delta)
        def k_for_delta(target, call):
            k = F
            for _ in range(50):
                s = float(smile_iv(sm, math.log(k / F)))
                # invert delta for k given s
                z = norm.ppf(target) if call else norm.ppf(1 + target)
                k_new = F * math.exp(-(z * s * math.sqrt(T) - 0.5 * s * s * T))
                if abs(k_new - k) < 1e-6: break
                k = k_new
            return k, float(smile_iv(sm, math.log(k / F)))
        kc, sc = k_for_delta(0.25, True); kp, sp = k_for_delta(-0.25, False)
        s0 = float(smile_iv(sm, 0.0))
        # 10% OTM call vs put (model at exactly 0.9/1.1 spot, and nearest actual strikes)
        kc10, kp10 = SPOT * 1.10, SPOT * 0.90
        c10 = b76(F, kc10, T, float(smile_iv(sm, math.log(kc10 / F))), R, True)
        p10 = b76(F, kp10, T, float(smile_iv(sm, math.log(kp10 / F))), R, False)
        c10_flat = b76(F, kc10, T, s0, R, True); p10_flat = b76(F, kp10, T, s0, R, False)  # zero-skew benchmark
        u = g[g.usable]
        ca = u[(u.side == "call")].iloc[(u[u.side == "call"].strike - kc10).abs().argsort()[:1]] if (u.side == "call").any() else None
        pa = u[(u.side == "put")].iloc[(u[u.side == "put"].strike - kp10).abs().argsort()[:1]] if (u.side == "put").any() else None
        K, f, cdf, neg = rnd_from_smile(sm, F, T, R)
        p_up_rnd = prob_above(K, cdf, SPOT)
        p_up_logn = 1 - norm.cdf((math.log(SPOT / F) + 0.5 * s0 * s0 * T) / (s0 * math.sqrt(T)))
        rows.append(dict(expiry=e, days=round(T * 365), F=round(F, 2), atm_iv_pct=round(s0 * 100, 2),
                         k_put25=round(kp, 1), iv_put25_pct=round(sp * 100, 2), k_call25=round(kc, 1), iv_call25_pct=round(sc * 100, 2),
                         rr25_call_minus_put_volpts=round((sc - sp) * 100, 2), bf25_volpts=round(((sc + sp) / 2 - s0) * 100, 2),
                         iv_90pct_strike=round(float(smile_iv(sm, math.log(0.9 * SPOT / F))) * 100, 2),
                         iv_110pct_strike=round(float(smile_iv(sm, math.log(1.1 * SPOT / F))) * 100, 2),
                         skew_90_110_volpts=round((float(smile_iv(sm, math.log(0.9 * SPOT / F))) - float(smile_iv(sm, math.log(1.1 * SPOT / F)))) * 100, 2),
                         call10_otm_model_px=round(c10, 3), put10_otm_model_px=round(p10, 3), call10_over_put10_model=round(c10 / p10, 3),
                         call10_over_put10_flat_smile_benchmark=round(c10_flat / p10_flat, 3),
                         call10_over_put10_relative_to_flat=round((c10 / p10) / (c10_flat / p10_flat), 3),
                         call10_nearest_strike=float(ca.strike.iloc[0]) if ca is not None and len(ca) else np.nan,
                         call10_nearest_mid=float(ca.mid.iloc[0]) if ca is not None and len(ca) else np.nan,
                         put10_nearest_strike=float(pa.strike.iloc[0]) if pa is not None and len(pa) else np.nan,
                         put10_nearest_mid=float(pa.mid.iloc[0]) if pa is not None and len(pa) else np.nan,
                         call10_over_put10_actual=round(float(ca.mid.iloc[0]) / float(pa.mid.iloc[0]), 3) if (ca is not None and pa is not None and len(ca) and len(pa)) else np.nan,
                         p_above_spot_rnd=round(p_up_rnd, 3), p_above_spot_lognormal=round(p_up_logn, 3),
                         p_above_fwd_rnd=round(prob_above(K, cdf, F), 3),
                         rnd_neg_mass_clipped=round(neg, 4), smile_n=sm["n"], smile_rmse_volpts=round(sm["rmse_volpts"], 2)))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "B_skew.csv", index=False)
    return df


# ------------------------------------------------------------------ 7. 12-month distribution
def dist_12m(ch, ts, smiles):
    T12 = 1.0
    F12 = SPOT * math.exp(R * T12)
    # bracketing expiries for 11 Sep 2027: 17 Jun 2027 and 17 Dec 2027 (both reasonably quoted); Sep 2027 thin, used as check
    e_lo, e_hi = "2027-06-17", "2027-12-17"
    t_lo, t_hi = ts.set_index("expiry").loc[e_lo, "T"], ts.set_index("expiry").loc[e_hi, "T"]
    sm_lo, sm_hi = smiles[e_lo], smiles[e_hi]
    wgt = (T12 - t_lo) / (t_hi - t_lo)

    def interp_smile_iv(x):
        w_lo = smile_iv(sm_lo, x) ** 2 * t_lo; w_hi = smile_iv(sm_hi, x) ** 2 * t_hi
        return np.sqrt((w_lo * (1 - wgt) + w_hi * wgt) / T12)
    sm12 = dict(a=0, b=0, c=0, xmin=min(sm_lo["xmin"], sm_hi["xmin"]), xmax=max(sm_lo["xmax"], sm_hi["xmax"]))
    # build a table-driven smile object by sampling
    xs = np.linspace(-0.8, 0.8, 321); ivs = interp_smile_iv(xs)
    class TableSmile(dict):
        pass
    sm12 = TableSmile(xmin=float(xs.min()), xmax=float(xs.max()), xs=xs, ivs=ivs)
    global smile_iv  # temporarily allow table smiles in rnd_from_smile
    _orig = smile_iv
    def smile_iv_any(sm, x):
        if "xs" in sm:
            return np.interp(np.clip(x, sm["xmin"], sm["xmax"]), sm["xs"], sm["ivs"])
        return _orig(sm, x)
    smile_iv = smile_iv_any
    s12 = float(smile_iv(sm12, 0.0))
    sep = ts.set_index("expiry").loc["2027-09-17"]
    rows, pts = [], []
    # (a) lognormal with ATM IV
    def logn_pct(q, s, T, F):
        return F * math.exp(-0.5 * s * s * T + s * math.sqrt(T) * norm.ppf(q))
    def logn_above(x, s, T, F):
        return 1 - norm.cdf((math.log(x / F) + 0.5 * s * s * T) / (s * math.sqrt(T)))
    # (b) skew-adjusted RND at 12M
    K, f, cdf, neg = rnd_from_smile(sm12, F12, T12, R)
    mean_rnd = float(np.sum(K * f) * (K[1] - K[0]))
    # (c) two-sided lognormal: put-side IV (25d put) below the forward, call-side IV above
    sp = float(smile_iv(sm12, math.log(0.9 / 1.0)))  # ~10% down
    sc = float(smile_iv(sm12, math.log(1.1 / 1.0)))
    def two_sided_pct(q):
        s = sp if q < 0.5 else sc
        return logn_pct(q, s, T12, F12)
    def two_sided_above(x):
        s = sp if x < F12 else sc
        return logn_above(x, s, T12, F12)
    for label, pct_fn, above_fn in [
        ("lognormal_atm_iv_12m_interp", lambda q: logn_pct(q, s12, T12, F12), lambda x: logn_above(x, s12, T12, F12)),
        ("lognormal_atm_iv_sep27_direct", lambda q: logn_pct(q, sep.atm_iv_smile_pct / 100, sep["T"], sep.F), lambda x: logn_above(x, sep.atm_iv_smile_pct / 100, sep["T"], sep.F)),
        ("two_sided_lognormal_10pct_wings", two_sided_pct, two_sided_above),
        ("skew_adjusted_rnd_smile_interp", lambda q: pct_from_cdf(K, cdf, q), lambda x: prob_above(K, cdf, x)),
    ]:
        rows.append(dict(method=label, p05=round(pct_fn(0.05), 1), p10=round(pct_fn(0.10), 1), p25=round(pct_fn(0.25), 1),
                         p50=round(pct_fn(0.50), 1), p75=round(pct_fn(0.75), 1), p90=round(pct_fn(0.90), 1), p95=round(pct_fn(0.95), 1),
                         atm_iv_pct=round(s12 * 100, 2) if "sep27" not in label else round(sep.atm_iv_smile_pct, 2),
                         forward=round(F12, 2) if "sep27" not in label else round(sep.F, 2)))
        for x in PRICE_POINTS + [125.0]:
            pts.append(dict(method=label, price_point=x, label=BRIEF_LABELS.get(x, "below $125"),
                            pct_vs_spot=round((x / SPOT - 1) * 100, 1), p_above=round(above_fn(x), 3), p_below=round(1 - above_fn(x), 3)))
    dist = pd.DataFrame(rows); ptsdf = pd.DataFrame(pts)
    dist.to_csv(OUT / "B_dist_12m_percentiles.csv", index=False)
    ptsdf.to_csv(OUT / "B_dist_12m_price_points.csv", index=False)
    pd.DataFrame(dict(K=K, density=f, cdf=cdf)).iloc[::10].to_csv(OUT / "B_rnd_12m_grid.csv", index=False)
    meta = dict(T12=T12, F12=F12, atm_iv_12m_interp_pct=s12 * 100, bracketing=[e_lo, e_hi], weight_on_far=wgt,
                rnd_neg_mass_clipped=neg, rnd_mean=mean_rnd, iv_10pct_down=sp * 100, iv_10pct_up=sc * 100,
                smile_rmse_lo=sm_lo["rmse_volpts"], smile_rmse_hi=sm_hi["rmse_volpts"])
    smile_iv = _orig
    return dist, ptsdf, meta


def bl_check(ch, ts, smiles, expiry="2027-06-17"):
    """Breeden-Litzenberger directly on observed mids (one expiry) versus the smile-model density at the same expiry."""
    g = ch[ch.expiry == expiry]; T = g["T"].iloc[0]; F = g.F.iloc[0]
    K1, f1, neg1, mass1, u = rnd_from_mids(g, F, T, R)
    K2, f2, cdf2, neg2 = rnd_from_smile(smiles[expiry], F, T, R)
    dK1 = K1[1] - K1[0]
    cdf1_inside = np.cumsum(f1) * dK1
    # put the unobserved tail mass where the smile model puts it: mass below Kmin from the smile cdf
    below = float(np.interp(K1.min(), K2, cdf2)); above = 1 - float(np.interp(K1.max(), K2, cdf2))
    inside_target = 1 - below - above
    cdf1 = below + cdf1_inside / max(mass1, 1e-9) * inside_target
    rows = []
    for q in [0.10, 0.25, 0.50, 0.75, 0.90]:
        rows.append(dict(expiry=expiry, quantile=q, bl_direct_on_mids=round(float(np.interp(q, cdf1, K1)), 1),
                         smile_model=round(pct_from_cdf(K2, cdf2, q), 1)))
    out = pd.DataFrame(rows)
    out["note"] = (f"direct BL: spline on {len(u)} OTM-mid call prices {u.strike.min():.0f}-{u.strike.max():.0f}, "
                   f"neg density mass clipped {neg1:.3f}, in-range mass {mass1:.3f}; tails outside quoted strikes taken "
                   f"from the smile model ({below:.3f} below, {above:.3f} above)")
    out.to_csv(OUT / f"B_bl_check_{expiry}.csv", index=False)
    return out


# ------------------------------------------------------------------ 8. historical print base rates
def base_rates():
    """Two return series per print (audit finding 1):
         raw_cc_1d_pct    = entry_postclose_px / pre_close - 1  (pre-print close to reaction-day close, raw)
         excess_cc_1d_pct = legacy_1d_pct in 20_executable_returns = the same return less QQQ (WS20 'legacy day-1 excess')
       The options market prices the raw move, so raw is the like-for-like series; excess is kept because earlier notes use it."""
    e = pd.read_csv(OVN / "20_executable_returns.csv")
    c = pd.read_csv(OVN / "04_consensus_at_print.csv")
    k = pd.read_csv(OVN / "02_kpi_panel_quarterly.csv")
    k["print_quarter"] = "20" + k.quarter.str[-2:] + "Q" + k.quarter.str[0]  # "3Q20" -> "2020Q3"
    m = e.merge(c[["print_quarter", "revenue_surprise_pct", "eps_surprise_pct", "nights_surprise_pct", "guide_vs_street_pct", "guide_vs_street_sign"]], on="print_quarter", how="left")
    m = m.merge(k[["print_quarter", "nights_yoy_pct", "nights_yoy_accel_pts"]], on="print_quarter", how="left")
    m["raw_cc_1d_pct"] = (m.entry_postclose_px / m.pre_close - 1) * 100
    m["excess_cc_1d_pct"] = m.legacy_1d_pct
    m["qqq_1d_pct_implied"] = m.raw_cc_1d_pct - m.excess_cc_1d_pct
    m["open_to_close_1d_pct"] = m.open_1d_pct   # executable: next open -> close
    keep = ["print_quarter", "print_date", "reaction_date", "pre_close", "entry_open_px", "entry_postclose_px", "gap_pct",
            "raw_cc_1d_pct", "excess_cc_1d_pct", "qqq_1d_pct_implied", "open_to_close_1d_pct", "revenue_surprise_pct", "eps_surprise_pct",
            "nights_surprise_pct", "nights_yoy_pct", "nights_yoy_accel_pts", "guide_vs_street_pct", "guide_vs_street_sign"]
    m[keep].round(3).to_csv(OUT / "B_print_moves.csv", index=False)

    def stats(sub, label, col):
        x = sub[col]
        return dict(sample=label, series=col.replace("_cc_1d_pct", ""), n=len(sub), mean_abs_pct=round(x.abs().mean(), 2), median_abs_pct=round(x.abs().median(), 2),
                    rms_pct=round(math.sqrt((x ** 2).mean()), 2), mean_signed_pct=round(x.mean(), 2),
                    share_abs_ge_7pct=round((x.abs() >= 7).mean(), 2), share_abs_ge_10pct=round((x.abs() >= 10).mean(), 2),
                    share_abs_le_2pct=round((x.abs() <= 2).mean(), 2), n_up=int((x > 0).sum()), n_down=int((x < 0).sum()),
                    mean_up_pct=round(x[x > 0].mean(), 2) if (x > 0).any() else np.nan, mean_down_pct=round(x[x < 0].mean(), 2) if (x < 0).any() else np.nan,
                    mean_abs_gap_pct=round(sub.gap_pct.abs().mean(), 2), mean_abs_open_to_close_pct=round(sub.open_1d_pct.abs().mean(), 2),
                    p10=round(x.quantile(0.10), 2), p25=round(x.quantile(0.25), 2), p75=round(x.quantile(0.75), 2), p90=round(x.quantile(0.90), 2))
    rs = m.revenue_surprise_pct; ac = m.nights_yoy_accel_pts
    samples = [("all_23_prints", m), ("last_8_prints", m.tail(8)), ("last_12_prints", m.tail(12)),
               ("prints_since_2024", m[m.print_date >= "2024-01-01"]), ("Q3_prints_only_(Nov)", m[m.print_quarter.str.endswith("Q3")]),
               (f"revenue_beat_above_median_({rs.median():.2f}pct)", m[rs >= rs.median()]), ("revenue_beat_below_median", m[rs < rs.median()]),
               ("nights_accelerated_yoy_in_reported_q_(gt_0)", m[ac > 0]), ("nights_decelerated_yoy_in_reported_q_(le_0)", m[ac <= 0]),
               ("nights_accel_gt_0.25pt_(C_dead_band)", m[ac > 0.25]), ("nights_flat_within_0.25pt_(C_dead_band)", m[(ac <= 0.25) & (ac >= -0.25)]),
               ("nights_decel_lt_-0.25pt_(C_dead_band)", m[ac < -0.25]),
               ("next_q_rev_guide_above_street", m[m.guide_vs_street_sign > 0]), ("next_q_rev_guide_below_street", m[m.guide_vs_street_sign < 0]),
               ("nights_beat", m[m.nights_surprise_pct > 0]), ("nights_miss_or_inline", m[m.nights_surprise_pct <= 0])]
    rows = []
    for label, sub in samples:
        for col in ("raw_cc_1d_pct", "excess_cc_1d_pct"):
            rows.append(stats(sub, label, col))
    br = pd.DataFrame(rows)
    br.to_csv(OUT / "B_print_base_rates.csv", index=False)
    return m, br


# ------------------------------------------------------------------ main
if __name__ == "__main__":
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60)
    ch, fwd = clean_chain()
    print("FORWARDS\n", fwd.to_string(index=False))
    ts, smiles = term_structure(ch, fwd)
    print("\nTERM STRUCTURE\n", ts.drop(columns=["smile_x_range"]).to_string(index=False))
    ev, sens, nov = event_variance(ts)
    print("\nEVENT VARIANCE\n", ev.to_string(index=False))
    print("\nSENSITIVITY\n", sens.to_string(index=False))
    sk = skew_table(ch, ts, smiles)
    print("\nSKEW\n", sk.to_string(index=False))
    dist, pts, meta = dist_12m(ch, ts, smiles)
    print("\n12M DIST\n", dist.to_string(index=False)); print(pts.pivot(index="price_point", columns="method", values="p_above").to_string())
    print(meta)
    bl = bl_check(ch, ts, smiles, "2027-06-17"); print("\nBL CHECK\n", bl.to_string(index=False))
    bl2 = bl_check(ch, ts, smiles, "2028-01-21"); print(bl2.to_string(index=False))
    m, br = base_rates()
    print("\nBASE RATES\n", br.to_string(index=False))
    print(pd.read_csv(OUT / "B_event_sd_leg_sensitivity.csv").to_string(index=False))
    json.dump({k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in meta.items()}, open(OUT / "B_dist_12m_meta.json", "w"), indent=2)
