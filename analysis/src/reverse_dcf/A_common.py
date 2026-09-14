"""
Shared anchors and solvers for workstream A (market-implied operating case). Every number here is an ANCHOR from
docs/reverse_dcf/BRIEF.md or data/processed/reverse_dcf/mgmt_implied_summary.csv unless labelled otherwise.
"""
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT = os.path.join(ROOT, "data", "processed", "reverse_dcf", "A")
OVN = os.path.join(ROOT, "data", "processed", "overnight")
os.makedirs(OUT, exist_ok=True)

# ---- price points (BRIEF) ------------------------------------------------------------------------------------------
PRICE_POINTS = [
    (150.00, "bear tape"),
    (165.00, "p25 sell-side target"),
    (170.19, "price, close 11 Sep 2026"),
    (179.50, "mean sell-side target"),
    (185.00, "median yfinance target"),
    (197.50, "p75 sell-side target"),
    (220.00, "top sell-side target"),
]
PRICE = 170.19

# ---- capital structure today (BRIEF, 2Q26 10-Q) --------------------------------------------------------------------
SHARES_M = 597.0              # diluted WA 2Q26
NET_CASH = 9593.0             # cash + ST investments less senior notes; funds held for clients excluded
# end-FY27 convention used by the management note's target prices (Delivered case)
SHARES_END_FY27_M = 570.663
NET_CASH_END_FY27 = 10608.664


def ev_spot(price):
    return price * SHARES_M - NET_CASH


def ev_end_fy27(price):
    return price * SHARES_END_FY27_M - NET_CASH_END_FY27


# ---- history (02_kpi_panel_quarterly.csv via the management model) -------------------------------------------------
LTM_REV = 13159.0             # 3Q25-2Q26
LTM_EBITDA = 4617.0
LTM_MARGIN = LTM_EBITDA / LTM_REV
H1_26_REV = 2678.0 + 3608.0   # 6,286
FY25_REV = 12241.0
FY25_NIGHTS_M = 533.0
FY25_GBV_MUSD = 91292.0
H1_26_NIGHTS_M = 156.2 + 148.3
H1_26_GBV_MUSD = 29200.0 + 27200.0
Q3_25_REV, Q4_25_REV = 4095.0, 2778.0
Q3_25_NIGHTS, Q4_25_NIGHTS = 133.6, 121.9
Q3_25_GBV, Q4_25_GBV = 22900.0, 20400.0
Q3_25_TAKE, Q4_25_TAKE = 4095.0 / 22892.0, 2778.0 / 20400.0   # 3Q25 GBV $22,892m exact (management model, 10-Q); the KPI panel rounds it to $22.9bn (1bp of take rate, audit finding 11)

# ---- management cases FY26 / FY27 (mgmt_implied_summary.csv) --------------------------------------------------------
MGMT = {
    "Literal":   dict(fy26_rev=14077.150, fy26_nights=583.722, fy27_rev=15630.400, fy27_growth=11.03, fy27_ebitda=5548.792, fy27_margin=35.5, fy27_eps=5.723, fy27_fcf=5738.124, fy27_nights=636.256, fy27_nights_growth=9.0, ntm_rev=4730.0 + 3061.15 + 2962.076 + 3998.79, ntm_ebitda=2340.663 + 876.726 + 573.903 + 1397.377),
    "Delivered": dict(fy26_rev=14231.303, fy26_nights=588.164, fy27_rev=16024.742, fy27_growth=12.60, fy27_ebitda=5800.957, fy27_margin=36.2, fy27_eps=6.078, fy27_fcf=5940.573, fy27_nights=646.98, fy27_nights_growth=10.0, ntm_rev=4815.14 + 3130.163 + 3003.832 + 4055.161, ntm_ebitda=2406.87 + 964.861 + 581.924 + 1416.982),
    "Ambition":  dict(fy26_rev=14356.237, fy26_nights=591.328, fy27_rev=16790.638, fy27_growth=16.96, fy27_ebitda=6212.536, fy27_margin=37.0, fy27_eps=6.681, fy27_fcf=6346.656, fy27_nights=662.287, fy27_nights_growth=12.0, ntm_rev=4882.182 + 3188.055 + 3120.003 + 4211.948, ntm_ebitda=2459.91 + 1000.116 + 620.015 + 1492.809),
}
FY26_REV_BASE = MGMT["Delivered"]["fy26_rev"]        # base for FY27 growth (BRIEF: use the delivered case)
FY26_NIGHTS_BASE = MGMT["Delivered"]["fy26_nights"]
MARGIN_BASE, MARGIN_LO, MARGIN_HI = 0.362, 0.355, 0.370
DELIVERED_2H26_REV = 4815.14 + 3130.163
DELIVERED_SBC_FY27 = 1935.731
DELIVERED_SHARES_FY27_AVG = 577.051
DELIVERED_NET_INTEREST_FY27 = 4 * 160 - 4 * 31     # $516m
TAX_RATE = 0.18
DA_PCT_REV = 0.0065
FCF_TO_EBITDA_FY27 = MGMT["Delivered"]["fy27_fcf"] / MGMT["Delivered"]["fy27_ebitda"]   # 1.024
# NTM (3Q26-2Q27) to FY27 mapping: the Delivered case's NTM growth less its FY27 growth (14.02 - 12.60 = 1.42pp)
NTM_TO_FY27_SPREAD_PP = (MGMT["Delivered"]["ntm_rev"] / LTM_REV - 1) * 100 - MGMT["Delivered"]["fy27_growth"]
# guide-proxy bias: mean (proxy - realised NTM growth) over the 12 vintages 3Q22-2Q25, MEASURED in A_01 (A_ntm_proxy_vs_realised.csv); RMSE 2.9pp
PROXY_BIAS_PP = 1.37


def fy27_growth_base_consistent(ntm_rev):
    """Scale the whole Delivered quarterly path (3Q26-4Q27) by implied NTM / Delivered NTM, so the FY26 base moves too.
    Returns (FY27 growth %, FY27 revenue $m, FY26 revenue $m). Audit finding 2."""
    s = ntm_rev / MGMT["Delivered"]["ntm_rev"]
    fy27 = s * MGMT["Delivered"]["fy27_rev"]
    fy26 = H1_26_REV + s * DELIVERED_2H26_REV
    return (fy27 / fy26 - 1) * 100, fy27, fy26

# ---- Street (BRIEF: Bloomberg FA 4 Sep, Zacks 4 Sep, S&P 3 Sep) ----------------------------------------------------
STREET = dict(
    q3_26_rev=4744.0, q3_26_nights=148.9, q3_26_nights_growth=11.1, q3_26_gbv=26350.0, q3_26_gbv_growth=15.1, q3_26_adr=177.0, q3_26_adr_growth=3.3, q3_26_ebitda=2360.0, q3_26_eps=2.875,
    q4_26_rev_lo=3154.0, q4_26_rev_hi=3200.0, q4_26_nights=134.2, q4_26_nights_growth=10.1, q4_26_gbv=23000.0, q4_26_gbv_growth=12.7, q4_26_adr=171.3, q4_26_adr_growth=2.3, q4_26_ebitda=915.0, q4_26_eps=0.835,
    fy26_rev_lo=14100.0, fy26_rev_hi=14160.0, fy26_eps_lo=5.23, fy26_eps_hi=5.28, fy26_fcf=5350.0,
    fy27_rev_lo=15730.0, fy27_rev_hi=15760.0, fy27_eps_lo=6.02, fy27_eps_hi=6.14,
)
STREET["q4_26_rev"] = (STREET["q4_26_rev_lo"] + STREET["q4_26_rev_hi"]) / 2
STREET["fy26_rev"] = (STREET["fy26_rev_lo"] + STREET["fy26_rev_hi"]) / 2
STREET["fy27_rev"] = (STREET["fy27_rev_lo"] + STREET["fy27_rev_hi"]) / 2
STREET["fy27_eps"] = (STREET["fy27_eps_lo"] + STREET["fy27_eps_hi"]) / 2
STREET_2H26_REV = STREET["q3_26_rev"] + STREET["q4_26_rev"]

# ---- team base (WS29/30) -------------------------------------------------------------------------------------------
TEAM = dict(fy26_rev=14167.89, fy26_margin=36.19, fy27_rev=15803.69, fy27_growth=11.55, fy27_ebitda=5757.93, fy27_margin=36.43, fy27_eps=5.90,
            fy27_nights_growth=9.2, q3_26_nights_growth=9.9, q4_26_nights_growth=8.9, q3_26_rev=4771.0, q4_26_rev=3111.0)

# ---- decomposition anchors ------------------------------------------------------------------------------------------
ADR_EXFX_FY27 = 3.0          # management / team H note
FX_FY27_PP = -0.6            # WS29 consensus EUR path, revenue FX after hedging
TAKE_RATE_CHANGE_FY27 = 0.0
RESIDUAL_FY27 = 0.0

# ---- multiples (BRIEF) -----------------------------------------------------------------------------------------------
EV_EBITDA_SET = (13.5, 16.5, 18.5)
PE_SET = (22.0, 27.0, 30.0)
EV_FCF_SET = (14.0, 17.0, 20.0)
TODAY_EV_EBITDA_DELIVERED = ev_spot(PRICE) / MGMT["Delivered"]["fy27_ebitda"]   # 15.86x


# ---- econometrics ----------------------------------------------------------------------------------------------------
def ols_nw(y, X, lags):
    """OLS with Newey-West (Bartlett) standard errors. X must include the constant column."""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    n, k = X.shape
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    e = y - X @ b
    S = (X * e[:, None]).T @ (X * e[:, None])
    for l in range(1, lags + 1):
        w = 1 - l / (lags + 1)
        G = (X[l:] * e[l:, None]).T @ (X[:-l] * e[:-l, None])
        S += w * (G + G.T)
    V = XtX_inv @ S @ XtX_inv
    se = np.sqrt(np.diag(V))
    tss = ((y - y.mean()) ** 2).sum()
    r2 = 1 - (e ** 2).sum() / tss
    return dict(b=b, t=b / se, se=se, V=V, r2=r2, adj_r2=1 - (1 - r2) * (n - 1) / (n - k),
                dw=(np.diff(e) ** 2).sum() / (e ** 2).sum(), n=n, resid=e, resid_sd=np.sqrt((e ** 2).sum() / (n - k)))


def bisect(f, lo, hi, it=100):
    if f(lo) * f(hi) > 0:
        return np.nan
    for _ in range(it):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def solve_joint_linear(a, b, ev, base_rev, margin):
    """g (in %) such that (a + b*g) * base_rev * (1+g/100) * margin = ev, multiple linear in growth (percentage points)."""
    return bisect(lambda g: (a + b * g) * base_rev * (1 + g / 100) * margin - ev, -50, 100)


def solve_joint_log(a, b, ev, base_rev, margin):
    """g (in %) such that exp(a + b*g) * base_rev * (1+g/100) * margin = ev (cross-section log-linear fits)."""
    return bisect(lambda g: np.exp(a + b * g) * base_rev * (1 + g / 100) * margin - ev, -50, 150)


# ---- fade DCF, identical to analysis/src/reverse_dcf/mgmt_implied_model.py ------------------------------------------
def fade_dcf(fcf27, g0, wacc=0.10, tg=0.03, years=10):
    """PV as of 30 Sep 2026 of FY27..FY36 FCF plus a Gordon terminal; FY28 growth g0 fades linearly to tg by FY36.
    Year-y cash flow is discounted from its mid-point (y - 0.25 years out); the terminal from end-FY36 (years - 0.25)."""
    pv = 0.0
    f = fcf27
    for y in range(1, years + 1):
        if y > 1:
            g = g0 + (tg - g0) * (y - 2) / (years - 2) if years > 2 else tg
            f = f * (1 + g)
        pv += f / (1 + wacc) ** (y - 0.25)
    tv = f * (1 + tg) / (wacc - tg)
    pv += tv / (1 + wacc) ** (years - 0.25)
    return pv


def implied_dcf_growth(ev_target, fcf27, wacc=0.10, tg=0.03):
    lo, hi = -0.30, 0.60
    for _ in range(80):
        mid = (lo + hi) / 2
        if fade_dcf(fcf27, mid, wacc, tg) < ev_target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---- FY27 P&L translation (Delivered-case mechanics) ------------------------------------------------------------------
def eps_from_revenue(rev, margin):
    ebitda = rev * margin
    opinc = ebitda - DELIVERED_SBC_FY27 - DA_PCT_REV * rev
    return (opinc + DELIVERED_NET_INTEREST_FY27) * (1 - TAX_RATE) / DELIVERED_SHARES_FY27_AVG


def revenue_from_eps(eps, margin):
    return (eps * DELIVERED_SHARES_FY27_AVG / (1 - TAX_RATE) - DELIVERED_NET_INTEREST_FY27 + DELIVERED_SBC_FY27) / (margin - DA_PCT_REV)


# ---- log-additive decomposition ------------------------------------------------------------------------------------
def implied_nights_growth(rev_growth_pct, adr_exfx_pct=ADR_EXFX_FY27, fx_pp=FX_FY27_PP, take_rate_chg_pct=TAKE_RATE_CHANGE_FY27, residual_pp=RESIDUAL_FY27):
    """revenue growth = nights + ADR ex-FX + FX + take-rate change + residual, in logs; returns nights growth in %."""
    ln = np.log(1 + rev_growth_pct / 100) - np.log(1 + adr_exfx_pct / 100) - np.log(1 + fx_pp / 100) - np.log(1 + take_rate_chg_pct / 100) - residual_pp / 100
    return (np.exp(ln) - 1) * 100
