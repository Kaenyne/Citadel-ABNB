"""
Workstream A, step 2: what each share price implies for FY27 / NTM revenue growth and EBITDA.

Methods
1. Joint solve (Krish's preferred): EV(price) = M(g) x EBITDA(g), with M(g) the fitted EV/NTM EBITDA multiple as a function
   of NTM revenue growth (re-estimated in A_01 from the WS12 monthly panel) and EBITDA(g) = base revenue x (1+g) x margin.
   Run on the regression-native NTM basis (LTM revenue $13,159m x (1+g) x LTM margin 35.1%, i.e. exactly how the panel's
   NTM EBITDA was built) and on the direct FY27 basis (FY26 delivered revenue $14,231m x (1+g) x 36.2%). NTM answers are
   mapped to FY27 three ways (proportional, chained through the Street's 2H26, chained through the Delivered 2H26).
   Also solved on the WS12 cross-section peer fits (log-linear).
2. Simple holds: hold the multiple (EV/EBITDA 13.5 / 15.9 / 16.5 / 18.5x; P/E 22 / 27 / 30x; EV/FCF 14 / 17 / 20x) and
   the margin, solve for FY27 revenue growth; hold the Street / Delivered FY27 numbers, solve for the implied multiple.
3. Reverse DCF: 10-year fade (WACC 10%, terminal 3%, sensitivities) on Delivered FY27 FCF $5,941m and SBC-adjusted $4,005m.

Run from the repo root:  py -3.13 analysis/src/reverse_dcf/A_02_market_implied_solves.py   (after A_01)
Outputs under data/processed/reverse_dcf/A/: A_price_points.csv, A_joint_solve.csv, A_joint_solve_peer_crosssection.csv,
A_simple_holds_grid.csv, A_simple_holds_long.csv, A_implied_multiples.csv, A_reverse_dcf.csv
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from A_common import *  # noqa: F401,F403,E402

pd.set_option("display.width", 250)
m = pd.read_csv(os.path.join(OVN, "12_abnb_multiples_monthly.csv"), parse_dates=["month_end"])
base = m[(m["month_end"] >= "2023-01-01")].dropna(subset=["ev_ntm_ebitda_x", "ntm_growth_proxy_pct"]).reset_index(drop=True)

# ---- price points ------------------------------------------------------------------------------------------------------
pp = pd.DataFrame(PRICE_POINTS, columns=["price_usd", "label"])
pp["market_cap_musd"] = pp["price_usd"] * SHARES_M
pp["ev_spot_musd"] = pp["price_usd"].map(ev_spot)
pp["ev_end_fy27_convention_musd"] = pp["price_usd"].map(ev_end_fy27)
pp["ev_to_fy27_ebitda_delivered_x"] = pp["ev_spot_musd"] / MGMT["Delivered"]["fy27_ebitda"]
pp["ev_to_fy27_ebitda_street_36.2pct_x"] = pp["ev_spot_musd"] / (STREET["fy27_rev"] * MARGIN_BASE)
pp["ev_to_ntm_ebitda_delivered_x"] = pp["ev_spot_musd"] / MGMT["Delivered"]["ntm_ebitda"]
pp["ev_to_ntm_ebitda_ws12_guide_proxy_x"] = pp["ev_spot_musd"] / (m["ntm_revenue_proxy_musd"].iloc[-1] * LTM_MARGIN)
pp["pe_fy27_delivered_x"] = pp["price_usd"] / MGMT["Delivered"]["fy27_eps"]
pp["pe_fy27_street_x"] = pp["price_usd"] / STREET["fy27_eps"]
pp["ev_to_fy27_fcf_delivered_x"] = pp["ev_spot_musd"] / MGMT["Delivered"]["fy27_fcf"]
pp["upside_vs_price_pct"] = (pp["price_usd"] / PRICE - 1) * 100
pp.round(3).to_csv(os.path.join(OUT, "A_price_points.csv"), index=False)

# ---- 1. joint solve -----------------------------------------------------------------------------------------------------
# Regression specs used (re-fit here so the solve is self-contained; identical to A_01 rows)
def fit(df, regs, lags=6):
    X = np.column_stack([np.ones(len(df))] + [df[r].values for r in regs])
    return ols_nw(df["ev_ntm_ebitda_x"].values, X, lags)


specs = {}
# each spec: a = intercept with controls at their latest value, b = growth slope, V = Newey-West covariance of all coefficients,
# x_ctrl = the control values used in a (so the fitted-line s.e. at growth g is sqrt([1, g, x_ctrl] V [1, g, x_ctrl]'))
r1 = fit(base, ["ntm_growth_proxy_pct"])
specs["A. levels 2023-26, growth only (primary)"] = dict(a=r1["b"][0], b=r1["b"][1], se=r1["se"][1], t=r1["t"][1], r2=r1["r2"], n=r1["n"], V=r1["V"], x_ctrl=[], resid_sd=r1["resid_sd"])
r2 = fit(base, ["ntm_growth_proxy_pct", "ltm_ebitda_margin_pct"])
specs["B. levels 2023-26, growth + margin (margin at 35.1% LTM)"] = dict(a=r2["b"][0] + r2["b"][2] * LTM_MARGIN * 100, b=r2["b"][1], se=r2["se"][1], t=r2["t"][1], r2=r2["r2"], n=r2["n"], V=r2["V"], x_ctrl=[LTM_MARGIN * 100], resid_sd=r2["resid_sd"])
r3 = fit(base, ["ntm_growth_proxy_pct", "ltm_ebitda_margin_pct", "dgs10_pct", "ndx_fwd_pe"])
x3 = [LTM_MARGIN * 100, base["dgs10_pct"].iloc[-1], base["ndx_fwd_pe"].iloc[-1]]
specs["C. levels 2023-26, growth + margin + 10y + NDX (controls at 4 Sep 2026)"] = dict(
    a=r3["b"][0] + r3["b"][2] * x3[0] + r3["b"][3] * x3[1] + r3["b"][4] * x3[2], b=r3["b"][1], se=r3["se"][1], t=r3["t"][1], r2=r3["r2"], n=r3["n"], V=r3["V"], x_ctrl=x3, resid_sd=r3["resid_sd"])
b25 = base[base["month_end"] < "2026-01-01"]
r4 = fit(b25, ["ntm_growth_proxy_pct"])
specs["D. levels 2023-25 only (out of sample for 2026), growth only"] = dict(a=r4["b"][0], b=r4["b"][1], se=r4["se"][1], t=r4["t"][1], r2=r4["r2"], n=r4["n"], V=r4["V"], x_ctrl=[], resid_sd=r4["resid_sd"])
first = base.groupby("last_reported_quarter", sort=False).first().reset_index().sort_values("month_end")
r5 = fit(first, ["ntm_growth_proxy_pct"], lags=2)
specs["E. one observation per print (first month after), growth only"] = dict(a=r5["b"][0], b=r5["b"][1], se=r5["se"][1], t=r5["t"][1], r2=r5["r2"], n=r5["n"], V=r5["V"], x_ctrl=[], resid_sd=r5["resid_sd"])
# SUPERSEDED (audit finding 1): slope-only band, line rotated about the sample means, carries no level uncertainty. Kept for comparison.
gbar, mbar = base["ntm_growth_proxy_pct"].mean(), base["ev_ntm_ebitda_x"].mean()
for tag, bb in [("A-low. SUPERSEDED slope-only band: primary slope minus 1 s.e., line rotated about sample means", r1["b"][1] - r1["se"][1]),
                ("A-high. SUPERSEDED slope-only band: primary slope plus 1 s.e., line rotated about sample means", r1["b"][1] + r1["se"][1])]:
    specs[tag] = dict(a=mbar - bb * gbar, b=bb, se=r1["se"][1], t=np.nan, r2=np.nan, n=r1["n"], V=None, x_ctrl=[], resid_sd=np.nan)
# WS12's published slope, anchored so the line passes through today's 4 Sep point (18.2x at 17.8% proxy) and the 0.48 slope
specs["F. WS12 published slope 0.48, line through the 4 Sep 2026 point (18.2x, 17.8%)"] = dict(a=18.209 - 0.48 * 17.788, b=0.48, se=np.nan, t=np.nan, r2=np.nan, n=np.nan, V=None, x_ctrl=[], resid_sd=np.nan)

delivered_ntm_growth = (MGMT["Delivered"]["ntm_rev"] / LTM_REV - 1) * 100
ntm_to_fy27_spread_pp = NTM_TO_FY27_SPREAD_PP     # 14.0 - 12.6 = 1.4pp in the Delivered case


def fitted_line_se(s, g):
    """Delta-method s.e. of the fitted multiple at growth g (turns), from the Newey-West covariance. Audit finding 1."""
    if s.get("V") is None:
        return np.nan
    x = np.array([1.0, g] + list(s["x_ctrl"]))
    return float(np.sqrt(x @ s["V"] @ x))


def mappings(ntm_rev, g_ntm):
    """FY27 growth under the mappings. Returns dict. Growth on the fixed Delivered FY26 base except base-consistent."""
    out = dict(prop=g_ntm - ntm_to_fy27_spread_pp,
               chain_street=((ntm_rev - STREET_2H26_REV) / H1_26_REV - 1) * 100,
               chain_deliv=((ntm_rev - DELIVERED_2H26_REV) / H1_26_REV - 1) * 100)
    out["base_consistent"], out["fy27_rev_base_consistent"], out["fy26_rev_base_consistent"] = fy27_growth_base_consistent(ntm_rev)
    return out


rows = []
for sname, s in specs.items():
    for price, label in PRICE_POINTS:
        ev = ev_spot(price)
        g_ntm = solve_joint_linear(s["a"], s["b"], ev, LTM_REV, LTM_MARGIN)
        M_ntm = s["a"] + s["b"] * g_ntm
        ntm_rev = LTM_REV * (1 + g_ntm / 100)
        ntm_ebitda = ntm_rev * LTM_MARGIN
        mp = mappings(ntm_rev, g_ntm)
        g27_prop, g27_chain_street, g27_chain_deliv = mp["prop"], mp["chain_street"], mp["chain_deliv"]
        # fitted-line band (delta method on the NW covariance at the solved g), re-solved on the shifted line
        se_fit = fitted_line_se(s, g_ntm)
        if not np.isnan(se_fit):
            g_lo = solve_joint_linear(s["a"] - se_fit, s["b"], ev, LTM_REV, LTM_MARGIN)   # lower fitted line: lower multiple for a given g, so higher implied g
            g_hi = solve_joint_linear(s["a"] + se_fit, s["b"], ev, LTM_REV, LTM_MARGIN)
            g_lo, g_hi = min(g_lo, g_hi), max(g_lo, g_hi)
            g_rlo = solve_joint_linear(s["a"] - s["resid_sd"], s["b"], ev, LTM_REV, LTM_MARGIN)
            g_rhi = solve_joint_linear(s["a"] + s["resid_sd"], s["b"], ev, LTM_REV, LTM_MARGIN)
            g_rlo, g_rhi = min(g_rlo, g_rhi), max(g_rlo, g_rhi)
        else:
            g_lo = g_hi = g_rlo = g_rhi = np.nan
        mlo, mhi = mappings(LTM_REV * (1 + g_lo / 100), g_lo) if not np.isnan(g_lo) else None, mappings(LTM_REV * (1 + g_hi / 100), g_hi) if not np.isnan(g_hi) else None
        # mis-specified direct FY27 basis (NTM-fitted multiple applied to FY27 EBITDA at 36.2%; audit finding 2), kept to show the ~2pp gap
        g27_direct = solve_joint_linear(s["a"], s["b"], ev, FY26_REV_BASE, MARGIN_BASE)
        row = dict(spec=sname, price_usd=price, label=label, ev_musd=round(ev, 0), intercept=round(s["a"], 3), slope_turns_per_pt=round(s["b"], 4),
                   slope_t_nw=round(s["t"], 2) if not np.isnan(s["t"]) else np.nan, r2=round(s["r2"], 3) if not np.isnan(s["r2"]) else np.nan, n=s["n"],
                   implied_ntm_growth_pct=round(g_ntm, 2), implied_ev_ntm_ebitda_x=round(M_ntm, 2), implied_ntm_revenue_musd=round(ntm_rev, 0), implied_ntm_ebitda_musd=round(ntm_ebitda, 0),
                   fitted_line_se_turns=round(se_fit, 3) if not np.isnan(se_fit) else np.nan,
                   implied_ntm_growth_lo_pct=round(g_lo, 2) if not np.isnan(g_lo) else np.nan, implied_ntm_growth_hi_pct=round(g_hi, 2) if not np.isnan(g_hi) else np.nan,
                   regression_resid_sd_turns=round(s["resid_sd"], 3) if not np.isnan(s["resid_sd"]) else np.nan,
                   implied_ntm_growth_resid_sd_lo_pct=round(g_rlo, 2) if not np.isnan(g_rlo) else np.nan, implied_ntm_growth_resid_sd_hi_pct=round(g_rhi, 2) if not np.isnan(g_rhi) else np.nan,
                   implied_ntm_growth_realised_units_pct=round(g_ntm - PROXY_BIAS_PP, 2),
                   fy27_growth_proportional_pct=round(g27_prop, 2),
                   fy27_growth_proportional_lo_pct=round(mlo["prop"], 2) if mlo else np.nan, fy27_growth_proportional_hi_pct=round(mhi["prop"], 2) if mhi else np.nan,
                   fy27_growth_proportional_realised_units_pct=round(g27_prop - PROXY_BIAS_PP, 2),
                   fy27_growth_chained_street_2h26_pct=round(g27_chain_street, 2),
                   fy27_growth_chained_street_2h26_lo_pct=round(mlo["chain_street"], 2) if mlo else np.nan, fy27_growth_chained_street_2h26_hi_pct=round(mhi["chain_street"], 2) if mhi else np.nan,
                   fy27_growth_chained_delivered_2h26_pct=round(g27_chain_deliv, 2),
                   fy27_growth_base_consistent_pct=round(mp["base_consistent"], 2),
                   fy27_growth_base_consistent_lo_pct=round(mlo["base_consistent"], 2) if mlo else np.nan, fy27_growth_base_consistent_hi_pct=round(mhi["base_consistent"], 2) if mhi else np.nan,
                   fy27_revenue_base_consistent_musd=round(mp["fy27_rev_base_consistent"], 0), fy26_revenue_base_consistent_musd=round(mp["fy26_rev_base_consistent"], 0),
                   fy27_growth_mapping_range_low_pct=round(min(g27_prop, g27_chain_street), 2), fy27_growth_mapping_range_high_pct=round(max(g27_prop, g27_chain_street), 2),
                   fy27_growth_direct_fy27_basis_pct=round(g27_direct, 2),
                   fy27_growth_direct_fy27_basis_note="mis-specified: NTM-fitted multiple applied to FY27 EBITDA at 36.2% (audit finding 2); not a mapping")
        for mtag, mg in [("36.2", MARGIN_BASE), ("35.5", MARGIN_LO), ("37.0", MARGIN_HI)]:
            rev27 = FY26_REV_BASE * (1 + g27_prop / 100)
            row[f"fy27_revenue_proportional_musd"] = round(rev27, 0)
            row[f"fy27_ebitda_proportional_margin_{mtag}_musd"] = round(rev27 * mg, 0)
            row[f"implied_ev_fy27_ebitda_margin_{mtag}_x"] = round(ev / (rev27 * mg), 2)
        row["fy27_eps_proportional_margin_36.2_usd"] = round(eps_from_revenue(FY26_REV_BASE * (1 + g27_prop / 100), MARGIN_BASE), 2)
        rev27_chain = FY26_REV_BASE * (1 + g27_chain_street / 100)
        row["fy27_revenue_chained_street_musd"] = round(rev27_chain, 0)
        row["fy27_ebitda_chained_street_margin_36.2_musd"] = round(rev27_chain * MARGIN_BASE, 0)
        row["implied_ev_fy27_ebitda_chained_street_x"] = round(ev / (rev27_chain * MARGIN_BASE), 2)
        rows.append(row)
js = pd.DataFrame(rows)
js.to_csv(os.path.join(OUT, "A_joint_solve.csv"), index=False)

# monotonicity and sensibility checks; plus the split of an EV move between multiple and EBITDA per pp of growth at the price (audit finding 6)
chk = []
for sname, s in specs.items():
    d = js[js.spec == sname].sort_values("price_usd")
    g170 = d.loc[d.price_usd == PRICE, "implied_ntm_growth_pct"].iloc[0]
    dlnM = s["b"] / (s["a"] + s["b"] * g170) * 100          # % change in the multiple per pp of growth
    dlnE = 1 / (1 + g170 / 100)                             # % change in EBITDA per pp of growth
    chk.append(dict(spec=sname, monotone_in_price=bool((np.diff(d["implied_ntm_growth_pct"]) > 0).all()), ntm_growth_at_170=g170,
                    fy27_growth_at_170_proportional=d.loc[d.price_usd == PRICE, "fy27_growth_proportional_pct"].iloc[0],
                    in_8_to_16_band=bool(8 <= g170 <= 16), ntm_growth_at_150=d["implied_ntm_growth_pct"].iloc[0], ntm_growth_at_220=d["implied_ntm_growth_pct"].iloc[-1],
                    ev_move_share_from_multiple_pct_at_price=round(dlnM / (dlnM + dlnE) * 100, 1), ev_move_share_from_ebitda_pct_at_price=round(dlnE / (dlnM + dlnE) * 100, 1),
                    usd_per_share_per_pp_fy27_growth_joint=round((ev_spot(PRICE) * (dlnM + dlnE) / 100) / SHARES_M, 2),
                    # one point of FY27 nights = 1% of FY27 revenue ($159m at the price), x 36.2% margin, x the implied EV/FY27 EBITDA (16.0x), per share (audit finding 5: $1.54)
                    usd_per_share_per_pt_nights_fixed_multiple=round(FY26_REV_BASE * (1 + d.loc[d.price_usd == PRICE, "fy27_growth_proportional_pct"].iloc[0] / 100) * 0.01 * MARGIN_BASE
                                                                     * (ev_spot(PRICE) / (FY26_REV_BASE * (1 + d.loc[d.price_usd == PRICE, "fy27_growth_proportional_pct"].iloc[0] / 100) * MARGIN_BASE)) / SHARES_M, 2)))
chk = pd.DataFrame(chk)
chk.to_csv(os.path.join(OUT, "A_joint_solve_checks.csv"), index=False)

# ---- 1b. cross-section peer fits (log-linear: ln(EV/NTM EBITDA) = a + b x growth) ---------------------------------------
peer = pd.read_csv(os.path.join(OVN, "12_peer_regressions.csv"))
peer = peer[(peer.dependent == "ev_ntm_adj_ebitda_x") & (peer.regressors == "ntm_revenue_growth_pct")]
prow = []
for _, p in peer.iterrows():
    for price, label in PRICE_POINTS:
        ev = ev_spot(price)
        g = solve_joint_log(p["b_const"], p["b_ntm_revenue_growth_pct"], ev, LTM_REV, LTM_MARGIN)
        # with ABNB's observed premium to the fit (4 Sep: actual 18.5x vs fitted) carried as a constant
        prem = np.log(p["abnb_actual"] / p["abnb_fitted"])
        g_prem = solve_joint_log(p["b_const"] + prem, p["b_ntm_revenue_growth_pct"], ev, LTM_REV, LTM_MARGIN)
        prow.append(dict(fit=p["fit"], n=p["n"], r2=p["r2"], b_const=p["b_const"], b_growth_log_per_pt=p["b_ntm_revenue_growth_pct"], t_growth=p["t_ntm_revenue_growth_pct"],
                         abnb_premium_to_fit_pct=round(p["abnb_premium_pct"], 1), price_usd=price, label=label,
                         implied_ntm_growth_no_premium_pct=round(g, 1) if not np.isnan(g) else np.nan,
                         implied_ev_ntm_ebitda_no_premium_x=round(np.exp(p["b_const"] + p["b_ntm_revenue_growth_pct"] * g), 2) if not np.isnan(g) else np.nan,
                         implied_ntm_growth_with_abnb_premium_pct=round(g_prem, 1) if not np.isnan(g_prem) else np.nan,
                         fy27_growth_proportional_no_premium_pct=round(g - ntm_to_fy27_spread_pp, 1) if not np.isnan(g) else np.nan,
                         fy27_growth_proportional_with_premium_pct=round(g_prem - ntm_to_fy27_spread_pp, 1) if not np.isnan(g_prem) else np.nan))
pj = pd.DataFrame(prow)
pj.to_csv(os.path.join(OUT, "A_joint_solve_peer_crosssection.csv"), index=False)

# ---- 2. simple holds --------------------------------------------------------------------------------------------------------
lenses = []
for mult in (13.5, round(TODAY_EV_EBITDA_DELIVERED, 2), 16.5, 18.5):
    for mtag, mg in [("36.2", MARGIN_BASE)] + ([("35.5", MARGIN_LO), ("37.0", MARGIN_HI)] if mult == 16.5 else []):
        lenses.append((f"EV/FY27 EBITDA {mult}x, margin {mtag}%", "ev_ebitda", mult, mg))
for pe in PE_SET:
    lenses.append((f"P/FY27 EPS {pe:.0f}x, margin 36.2%", "pe", pe, MARGIN_BASE))
for fm in EV_FCF_SET:
    lenses.append((f"EV/FY27 FCF {fm:.0f}x, FCF/EBITDA 1.02, margin 36.2%", "ev_fcf", fm, MARGIN_BASE))
lenses.append(("EV/FY27 EBITDA 16.5x, end-FY27 convention (570.7m sh, $10.6bn net cash, management note)", "ev_ebitda_fy27conv", 16.5, MARGIN_BASE))

hold_rows = []
for lname, kind, mult, mg in lenses:
    for price, label in PRICE_POINTS:
        ev = ev_end_fy27(price) if kind == "ev_ebitda_fy27conv" else ev_spot(price)
        if kind in ("ev_ebitda", "ev_ebitda_fy27conv"):
            ebitda = ev / mult
            rev = ebitda / mg
        elif kind == "pe":
            eps = price / mult
            rev = revenue_from_eps(eps, mg)
            ebitda = rev * mg
        else:
            fcf = ev / mult
            ebitda = fcf / FCF_TO_EBITDA_FY27
            rev = ebitda / mg
        g = (rev / FY26_REV_BASE - 1) * 100
        hold_rows.append(dict(lens=lname, kind=kind, multiple_x=mult, margin_pct=mg * 100, price_usd=price, label=label, ev_musd=round(ev, 0),
                              implied_fy27_revenue_musd=round(rev, 0), implied_fy27_growth_pct=round(g, 2), implied_fy27_ebitda_musd=round(ebitda, 0),
                              implied_fy27_eps_usd=round(eps_from_revenue(rev, mg), 2), implied_fy27_fcf_musd=round(ebitda * FCF_TO_EBITDA_FY27, 0),
                              implied_fy27_nights_growth_adr3_fxm06_pct=round(implied_nights_growth(g), 2)))
hl = pd.DataFrame(hold_rows)
hl.to_csv(os.path.join(OUT, "A_simple_holds_long.csv"), index=False)
grid = hl.pivot(index="lens", columns="price_usd", values="implied_fy27_growth_pct")
grid = grid.loc[[l[0] for l in lenses]]
grid.columns = [f"fy27_growth_pct_at_${c:.2f}" for c in grid.columns]
grid.reset_index().to_csv(os.path.join(OUT, "A_simple_holds_grid.csv"), index=False)

# hold the Street / Delivered FY27 numbers, solve for the multiple
im_rows = []
for price, label in PRICE_POINTS:
    ev = ev_spot(price)
    im_rows.append(dict(price_usd=price, label=label, ev_musd=round(ev, 0),
                        ev_fy27_ebitda_street_x=round(ev / (STREET["fy27_rev"] * MARGIN_BASE), 2),
                        ev_fy27_ebitda_delivered_x=round(ev / MGMT["Delivered"]["fy27_ebitda"], 2),
                        ev_fy27_ebitda_literal_x=round(ev / MGMT["Literal"]["fy27_ebitda"], 2),
                        ev_fy27_ebitda_ambition_x=round(ev / MGMT["Ambition"]["fy27_ebitda"], 2),
                        ev_fy27_ebitda_team_base_x=round(ev / TEAM["fy27_ebitda"], 2),
                        pe_fy27_street_x=round(price / STREET["fy27_eps"], 2), pe_fy27_delivered_x=round(price / MGMT["Delivered"]["fy27_eps"], 2), pe_fy27_team_base_x=round(price / TEAM["fy27_eps"], 2),
                        ev_fy27_fcf_delivered_x=round(ev / MGMT["Delivered"]["fy27_fcf"], 2),
                        ev_fy27_fcf_street_proxy_x=round(ev / (STREET["fy27_rev"] * MARGIN_BASE * FCF_TO_EBITDA_FY27), 2),
                        ev_fy27_sbc_adj_fcf_delivered_x=round(ev / (MGMT["Delivered"]["fy27_fcf"] - DELIVERED_SBC_FY27), 2),
                        ev_ntm_ebitda_delivered_x=round(ev / MGMT["Delivered"]["ntm_ebitda"], 2),
                        ev_fy26_ebitda_delivered_x=round(ev / (MGMT["Delivered"]["fy26_rev"] * 0.362), 2)))
im = pd.DataFrame(im_rows)
im.to_csv(os.path.join(OUT, "A_implied_multiples.csv"), index=False)

# ---- 3. reverse DCF ----------------------------------------------------------------------------------------------------------
fcf_bases = {"Delivered reported FCF": MGMT["Delivered"]["fy27_fcf"], "Delivered SBC-adjusted FCF": MGMT["Delivered"]["fy27_fcf"] - DELIVERED_SBC_FY27,
             "Literal reported FCF": MGMT["Literal"]["fy27_fcf"], "Ambition reported FCF": MGMT["Ambition"]["fy27_fcf"]}
dcf_rows = []
for fname, f27 in fcf_bases.items():
    for wacc in (0.09, 0.10, 0.11):
        for tg in (0.025, 0.03, 0.035):
            for price, label in PRICE_POINTS:
                ev = ev_spot(price)
                g = implied_dcf_growth(ev, f27, wacc, tg) * 100
                dcf_rows.append(dict(fcf_basis=fname, fy27_fcf_musd=round(f27, 0), wacc_pct=wacc * 100, terminal_growth_pct=tg * 100, price_usd=price, label=label, ev_musd=round(ev, 0),
                                     implied_fy28_starting_fcf_growth_pct=round(g, 2), fy27_fcf_yield_on_ev_pct=round(f27 / ev * 100, 2)))
dcf = pd.DataFrame(dcf_rows)
dcf.to_csv(os.path.join(OUT, "A_reverse_dcf.csv"), index=False)
# verification against the management note (4.6% reported / 16.0% SBC-adjusted at $170.19, WACC 10%, g 3%)
v = dcf[(dcf.price_usd == PRICE) & (dcf.wacc_pct == 10) & (dcf.terminal_growth_pct == 3)]
print("Reverse DCF check at $170.19, WACC 10 / g 3:")
print(v[["fcf_basis", "fy27_fcf_musd", "implied_fy28_starting_fcf_growth_pct"]].to_string(index=False))
print("  management note: Delivered 4.6% reported, 16.0% SBC-adjusted; Literal 5.6 / 17.5; Ambition 2.7 / 13.0")

# ---- console ---------------------------------------------------------------------------------------------------------------
print("\nPrice points:\n", pp[["price_usd", "label", "ev_spot_musd", "ev_to_fy27_ebitda_delivered_x", "ev_to_ntm_ebitda_delivered_x", "ev_to_ntm_ebitda_ws12_guide_proxy_x", "pe_fy27_street_x"]].round(2).to_string(index=False))
print("\nDelivered NTM growth %.2f%%, FY27 %.2f%%, spread %.2fpp" % (delivered_ntm_growth, MGMT["Delivered"]["fy27_growth"], ntm_to_fy27_spread_pp))
print("Street 2H26 revenue $%.0fm; Delivered 2H26 $%.0fm" % (STREET_2H26_REV, DELIVERED_2H26_REV))
print("\nJoint solve specs:")
for k, s in specs.items():
    print("  %-90s a=%7.3f b=%6.4f se=%s t=%s R2=%s n=%s" % (k, s["a"], s["b"], "%.3f" % s["se"] if not np.isnan(s["se"]) else "-", "%.2f" % s["t"] if not np.isnan(s["t"]) else "-", "%.3f" % s["r2"] if not np.isnan(s["r2"]) else "-", s["n"]))
print("\nJoint solve, NTM basis -> FY27 (proportional) by price and spec:")
print(js.pivot(index="spec", columns="price_usd", values="implied_ntm_growth_pct").round(1).to_string())
print(js.pivot(index="spec", columns="price_usd", values="fy27_growth_proportional_pct").round(1).to_string())
print("\nPrimary spec detail:")
print(js[js.spec.str.startswith("A. ")][["price_usd", "implied_ntm_growth_pct", "fitted_line_se_turns", "implied_ntm_growth_lo_pct", "implied_ntm_growth_hi_pct", "implied_ntm_growth_resid_sd_lo_pct", "implied_ntm_growth_resid_sd_hi_pct",
                                          "implied_ev_ntm_ebitda_x", "fy27_growth_proportional_pct", "fy27_growth_proportional_lo_pct", "fy27_growth_proportional_hi_pct", "fy27_growth_chained_street_2h26_pct", "fy27_growth_base_consistent_pct", "fy27_growth_direct_fy27_basis_pct",
                                          "fy27_revenue_proportional_musd", "fy27_revenue_chained_street_musd", "implied_ev_fy27_ebitda_margin_36.2_x", "implied_ev_fy27_ebitda_chained_street_x"]].to_string(index=False))
print("\nBand by spec at each price (NTM lo / hi):")
print(js.pivot(index="spec", columns="price_usd", values="implied_ntm_growth_lo_pct").round(1).to_string())
print(js.pivot(index="spec", columns="price_usd", values="implied_ntm_growth_hi_pct").round(1).to_string())
print("\nChecks:\n", chk.to_string(index=False))
print("\nPeer cross-section joint solve (NTM growth, %):")
print(pj.pivot(index="fit", columns="price_usd", values="implied_ntm_growth_no_premium_pct").to_string())
print(pj.pivot(index="fit", columns="price_usd", values="implied_ntm_growth_with_abnb_premium_pct").to_string())
print("\nSimple holds grid (implied FY27 revenue growth, %):")
print(grid.round(1).to_string())
print("\nImplied multiples:\n", im.to_string(index=False))
print("\nReverse DCF (WACC 10, g 3):")
print(dcf[(dcf.wacc_pct == 10) & (dcf.terminal_growth_pct == 3)].pivot(index="fcf_basis", columns="price_usd", values="implied_fy28_starting_fcf_growth_pct").round(1).to_string())
