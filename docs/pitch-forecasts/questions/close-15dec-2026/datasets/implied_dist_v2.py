"""Revision-2 options anchor (audit A07 findings 03, 04, 11, 17).
Replaces the quadratic-smile Breeden-Litzenberger density (which had negative mass: 1.54% at 18 Dec, 0.47% at the
Jan/Mar interpolation before clipping) with an arbitrage-free two-lognormal mixture risk-neutral density fitted to
the same OTM mids (Bahra 1997 / Melick-Thomas 1997), forward-constrained, per expiry (18 Dec 2026, 15 Jan 2027,
19 Mar 2027). The 15 Dec anchor is the 18 Dec mixture; the 12 Feb anchor is the log-quantile interpolation of the
Jan and Mar mixtures at the calendar weight w = 28/63 plus the missing (1 - w) share of a 9.5% February event
(A07-11), i.e. a normal convolution in log space. Both are then shifted by the real-world equity premium
(EQUITY_PREMIUM over the cash rate already in the forward; A07-17: the same total-drift convention as the v2 path
model, 3.97% cash + 3.0% premium). Also reports the negative-mass diagnostic of the revision-1 smile.
Inputs: the revision-1 chain capture in ../sources (2026-09-17T03:12Z, 16 Sep close). Writes implied_dist_v2.json,
anchor_cdf_v2.csv. Run from the repo root: py -3.13 docs/pitch-forecasts/questions/close-15dec-2026/datasets/implied_dist_v2.py
"""
import json, math, pathlib
import numpy as np, pandas as pd
from scipy.stats import norm
from scipy.optimize import minimize
HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE.parent / "sources"
S = 167.51; R = 0.0397; EQUITY_PREMIUM = 0.03; ASOF = pd.Timestamp("2026-09-16")
EVENT_SD_FEB = 0.095          # B note central; R14's Jan/Mar-implied 8.5-9.5%
GRID = np.arange(60, 340, 0.25)
QS = (5, 10, 25, 50, 75, 90, 95)
ch = pd.read_csv(sorted(SRC.glob("yfinance_option_chain_*.csv"))[-1])
ch["mid"] = (ch.bid + ch.ask) / 2; ch["spread_rel"] = (ch.ask - ch.bid) / ch.mid


def b76(F, K, T, sig, cp):
    sig = max(sig, 1e-4) if np.isscalar(sig) else np.maximum(sig, 1e-4)
    d1 = (np.log(F / K) + 0.5 * sig * sig * T) / (sig * np.sqrt(T)); d2 = d1 - sig * np.sqrt(T)
    return np.where(cp == "call", F * norm.cdf(d1) - K * norm.cdf(d2), K * norm.cdf(-d2) - F * norm.cdf(-d1))


def fit_mixture(expiry):
    g = ch[(ch.expiry == expiry) & (ch.bid > 0) & (ch.ask >= ch.bid) & (ch.mid >= 0.10) & (ch.spread_rel <= 0.60)].copy()
    T = (pd.Timestamp(expiry) - ASOF).days / 365
    c = g[g.type == "call"].set_index("strike").mid; p = g[g.type == "put"].set_index("strike").mid
    ks = sorted(set(c.index) & set(p.index)); near = [k for k in ks if abs(k / S - 1) < 0.12]
    F = float(np.median([k + (c[k] - p[k]) * math.exp(R * T) for k in near]))
    otm = g[((g.type == "call") & (g.strike > F)) | ((g.type == "put") & (g.strike < F))].copy()
    otm = otm[np.abs(np.log(otm.strike / F)) <= 0.45]
    K = otm.strike.to_numpy(); cp = otm.type.to_numpy(); mid = otm.mid.to_numpy() * math.exp(R * T)
    wgt = 1 / np.maximum(otm.spread_rel.to_numpy(), 0.05)

    def unpack(x):
        w = 1 / (1 + math.exp(-x[0])); F1 = math.exp(x[1]); s1 = 0.05 + abs(x[2]); s2 = 0.05 + abs(x[3])
        F2 = (F - w * F1) / (1 - w)      # forward constraint: w F1 + (1 - w) F2 = F
        return w, F1, s1, F2, s2

    def loss(x):
        w, F1, s1, F2, s2 = unpack(x)
        if F2 <= 0 or w < 0.02 or w > 0.98: return 1e9
        pr = w * b76(F1, K, T, s1, cp) + (1 - w) * b76(F2, K, T, s2, cp)
        return float(np.sum(wgt * (pr - mid) ** 2))
    best = None
    for w0 in (0.3, 0.6, 0.8):
        for dl in (-0.1, -0.2, -0.3):
            x0 = [math.log(w0 / (1 - w0)), math.log(F) + dl, 0.45, 0.20]
            rr = minimize(loss, x0, method="Nelder-Mead", options=dict(maxiter=6000, xatol=1e-7, fatol=1e-10))
            if best is None or rr.fun < best.fun: best = rr
    w, F1, s1, F2, s2 = unpack(best.x)
    pr = w * b76(F1, K, T, s1, cp) + (1 - w) * b76(F2, K, T, s2, cp)
    cdf = lambda x: w * norm.cdf((np.log(x) - (math.log(F1) - 0.5 * s1 * s1 * T)) / (s1 * math.sqrt(T))) \
        + (1 - w) * norm.cdf((np.log(x) - (math.log(F2) - 0.5 * s2 * s2 * T)) / (s2 * math.sqrt(T)))
    return dict(expiry=expiry, T=T, F=F, n_quotes=int(len(otm)), w=w, F1=F1, s1=s1, F2=F2, s2=s2,
                rmse_usd=float(np.sqrt(np.mean((pr - mid) ** 2))), max_abs_err_usd=float(np.max(np.abs(pr - mid)))), cdf


def summarise(cdf_vals, label):
    pct = {str(q): float(np.interp(q / 100, cdf_vals, GRID)) for q in QS}
    thr = {"P(<=143)": float(np.interp(143, GRID, cdf_vals)), "P(<=150)": float(np.interp(150, GRID, cdf_vals)),
           "P(>=180)": float(1 - np.interp(180, GRID, cdf_vals)), "P(<100)": float(np.interp(100, GRID, cdf_vals)),
           "P(>260)": float(1 - np.interp(260, GRID, cdf_vals))}
    # log-sd of the distribution on the grid (from the density)
    dens = np.gradient(cdf_vals, GRID); dens = np.clip(dens, 0, None); dens /= np.trapezoid(dens, GRID)
    m = np.trapezoid(np.log(GRID) * dens, GRID); sd = math.sqrt(np.trapezoid((np.log(GRID) - m) ** 2 * dens, GRID))
    return dict(label=label, percentiles=pct, thresholds=thr, log_sd_pct=sd * 100)


def negative_mass_rev1(expiry_first, expiry_second, target):
    """Reproduce A07-04: integrated negative density of the revision-1 quadratic-smile RND before clipping."""
    term = pd.read_csv(sorted(HERE.glob("implied_term_structure_*.csv"))[-1]).set_index("expiry")
    T = (pd.Timestamp(target) - ASOF).days / 365; z = term.loc[expiry_first]
    coef = np.array([z.atm_iv / 100, z.smile_b, z.smile_c])
    if expiry_second:
        z2 = term.loc[expiry_second]; wt = (T - z["T"]) / (z2["T"] - z["T"])
        coef = (1 - wt) * coef + wt * np.array([z2.atm_iv / 100, z2.smile_b, z2.smile_c])
    F = S * math.exp(R * T); Ks = np.linspace(60, 320, 2601); xs = np.clip(np.log(Ks / F), -0.45, 0.45)
    ivs = np.clip(coef[0] + coef[1] * xs + coef[2] * xs ** 2, 0.05, 2.0)
    Cs = b76(F, Ks, T, ivs, np.array(["call"] * len(Ks)))
    dens = np.gradient(np.gradient(Cs, Ks), Ks)
    return float(np.trapezoid(np.clip(-dens, 0, None), Ks))


fits = {}; cdfs = {}
for e in ("2026-12-18", "2027-01-15", "2027-03-19"):
    fits[e], cdfs[e] = fit_mixture(e)
    print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in fits[e].items()}))

# 15 Dec anchor: 18 Dec mixture (T 0.2548 vs 0.2466 to 15 Dec; the three-day gap is inside the fit error), risk-neutral
T_dec = (pd.Timestamp("2026-12-15") - ASOF).days / 365
cdf_dec_rn = cdfs["2026-12-18"](GRID)
cdf_dec_rw = cdfs["2026-12-18"](GRID / math.exp(EQUITY_PREMIUM * T_dec))        # shift the whole distribution up by the premium

# 12 Feb anchor: log-quantile interpolation of the Jan and Mar mixtures at the calendar weight, then the missing
# (1 - w) share of the February event variance (A07-11), then the premium shift
T_feb = (pd.Timestamp("2027-02-12") - ASOF).days / 365
w_cal = (T_feb - fits["2027-01-15"]["T"]) / (fits["2027-03-19"]["T"] - fits["2027-01-15"]["T"])
u = np.linspace(0.0005, 0.9995, 4001)
qJ = np.interp(u, cdfs["2027-01-15"](GRID), GRID); qM = np.interp(u, cdfs["2027-03-19"](GRID), GRID)
q_interp = np.exp((1 - w_cal) * np.log(qJ) + w_cal * np.log(qM))
rng = np.random.default_rng(20260917)
draws = np.interp(rng.uniform(size=1_000_000), u, q_interp)
missing_event_var = (1 - w_cal) * EVENT_SD_FEB ** 2
draws_ev = draws * np.exp(math.sqrt(missing_event_var) * rng.standard_normal(len(draws)) - 0.5 * missing_event_var)
cdf_feb_interp = np.searchsorted(np.sort(draws), GRID) / len(draws)
cdf_feb_rn = np.searchsorted(np.sort(draws_ev), GRID) / len(draws_ev)
cdf_feb_rw = np.searchsorted(np.sort(draws_ev * math.exp(EQUITY_PREMIUM * T_feb)), GRID) / len(draws_ev)

# rev-1 lognormal check of the event correction (A07-11 arithmetic): 24.06% -> 25.08%
term = pd.read_csv(sorted(HERE.glob("implied_term_structure_*.csv"))[-1]).set_index("expiry")
var_interp = (1 - w_cal) * (term.loc["2027-01-15"].atm_iv / 100) ** 2 * term.loc["2027-01-15"]["T"] \
    + w_cal * (term.loc["2027-03-19"].atm_iv / 100) ** 2 * term.loc["2027-03-19"]["T"]

out = {"method": "two-lognormal mixture RND per expiry, forward-constrained, weighted least squares on OTM mids (weights 1/max(rel spread, 0.05)); "
                 "12 Feb = log-quantile interpolation Jan/Mar at w_cal + N(0, (1-w_cal) x 0.095^2) event top-up in log space; real-world = risk-neutral x exp(0.03 T)",
       "spot": S, "r": R, "equity_premium": EQUITY_PREMIUM, "event_sd_feb": EVENT_SD_FEB, "w_cal": w_cal,
       "fits": fits,
       "rev1_smile_negative_mass": {"dec15": negative_mass_rev1("2026-12-18", None, "2026-12-15"),
                                    "feb12": negative_mass_rev1("2027-01-15", "2027-03-19", "2027-02-12")},
       "rev1_lognormal_event_correction": {"log_sd_interp_pct": math.sqrt(var_interp) * 100,
                                           "log_sd_with_event_pct": math.sqrt(var_interp + missing_event_var) * 100},
       "dec15": {"T_years": T_dec, "risk_neutral": summarise(cdf_dec_rn, "15 Dec, 18 Dec mixture RND"),
                 "real_world": summarise(cdf_dec_rw, "15 Dec, + 3% premium")},
       "feb12": {"T_years": T_feb, "interp_only": summarise(cdf_feb_interp, "12 Feb, Jan/Mar log-quantile interpolation"),
                 "risk_neutral": summarise(cdf_feb_rn, "12 Feb, + missing Feb event variance"),
                 "real_world": summarise(cdf_feb_rw, "12 Feb, + 3% premium")}}
print(json.dumps({k: out[k] for k in ("rev1_smile_negative_mass", "rev1_lognormal_event_correction", "dec15", "feb12")}, indent=1))
json.dump(out, open(HERE / "implied_dist_v2.json", "w"), indent=1)
pd.DataFrame({"price": GRID, "cdf_dec15_rn": cdf_dec_rn, "cdf_dec15_rw": cdf_dec_rw,
              "cdf_feb12_interp": cdf_feb_interp, "cdf_feb12_rn": cdf_feb_rn, "cdf_feb12_rw": cdf_feb_rw}).to_csv(HERE / "anchor_cdf_v2.csv", index=False)
