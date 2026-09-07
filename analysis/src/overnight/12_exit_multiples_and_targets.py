"""
Workstream 12, parts 3 and 5: an evidence-based exit-multiple set for the FY27 grid, and the sell-side target book.

Part 3 asks one question: when the driver model exits FY2027E at 18x / 22x / 25.5x EV / adj. EBITDA, is that supported?
It answers with four independent lines of evidence, all reduced to the same unit (EV / forward adj. EBITDA on FY27E):
  (a) time series      what ABNB itself paid-for when its forward growth and margin looked like each scenario (monthly panel);
  (b) cross-section    the peer log-linear fits from 12_peer_multiples.py evaluated at each scenario's growth and margin;
  (c) intrinsic/DCF    the multiple a 10-year fade DCF supports at the FY2027 exit date, per scenario, at WACC 9/10/11%;
  (d) today            the multiple the market pays right now (4 Sep 2026) and its 2023-26 range.
Part 5 reads the analyst action feed pulled by workstream 09, builds the current target book (latest action per firm),
the rating mix, the post-2Q26 revisions, and the FY27 EV/EBITDA every target implies.

Reads
  data/processed/overnight/12_abnb_multiples_history.csv     quarterly multiple history (this workstream)
  data/processed/overnight/12_abnb_multiples_monthly.csv     monthly point-in-time multiples (this workstream)
  data/processed/overnight/12_peer_multiples.csv             cross-section, 4 Sep 2026 (this workstream)
  data/processed/overnight/12_peer_regressions.csv           cross-sectional fits and scenario-implied multiples
  data/processed/overnight/12_abnb_print_decomposition.csv   day-1 move split (this workstream)
  data/processed/overnight/09_analyst_actions.csv            yfinance/Benzinga upgrades-downgrades feed, pulled 6 Sep 2026 (workstream 09)
  data/processed/abnb_valuation_scenarios.csv                driver-model FY26-28 bear/base/bull
  data/processed/abnb_multiples_today.csv                    ABNB EV, LTM figures at $181.94
  data/processed/abnb_reverse_dcf.csv                        reverse-DCF implied growth at the current EV

Writes
  data/processed/overnight/12_exit_multiple_evidence.csv     one row per (scenario, method) with the implied exit multiple
  data/processed/overnight/12_exit_multiple_recommendation.csv  recommended exit multiple set and the price it gives
  data/processed/overnight/12_price_sensitivity.csv          FY27E price grid, scenario x exit multiple, on four cash-flow bases
  data/processed/overnight/12_analyst_targets.csv            latest target and rating per firm with implied FY27 multiples
  data/processed/overnight/12_analyst_target_summary.csv     dispersion, rating mix, post-2Q26 revision stats
  data/processed/overnight/12_print_move_attribution.csv     how much of the day-1 move is multiple vs estimate
  data/processed/overnight/12_regime_decomposition.csv       each regime's price move split into EBITDA growth vs re-rating
  analysis/figures/overnight/12_exit_multiple_evidence.png
  analysis/figures/overnight/12_analyst_targets.png

Run: py -3.13 analysis/src/overnight/12_exit_multiples_and_targets.py    (from the repo root)
"""
import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
P = lambda *a: os.path.join(ROOT, *a)
OUT = P("data", "processed", "overnight"); FIG = P("analysis", "figures", "overnight")
os.makedirs(OUT, exist_ok=True); os.makedirs(FIG, exist_ok=True)
LAST_PRICE = 181.94
PRINT_2Q26 = pd.Timestamp("2026-08-07")   # 2Q26 reaction session, from abnb_earnings_reactions.csv

Q = pd.read_csv(os.path.join(OUT, "12_abnb_multiples_history.csv"))
M = pd.read_csv(os.path.join(OUT, "12_abnb_multiples_monthly.csv"), parse_dates=["month_end"])
PEER = pd.read_csv(os.path.join(OUT, "12_peer_multiples.csv"))
PREG = pd.read_csv(os.path.join(OUT, "12_peer_regressions.csv"))
PDEC = pd.read_csv(os.path.join(OUT, "12_abnb_print_decomposition.csv"))
sc = pd.read_csv(P("data", "processed", "abnb_valuation_scenarios.csv"))
today = pd.read_csv(P("data", "processed", "abnb_multiples_today.csv")).iloc[0]
SCEN = ["Bear", "Base", "Bull"]
s27 = sc[sc.period == "FY2027E"].set_index("scenario")
s28 = sc[sc.period == "FY2028E"].set_index("scenario")
ASSUMED = {"Bear": 18.0, "Base": 22.0, "Bull": 25.5}      # driver-model football field, research/notes/2026-09-05_driver-model.md s.5

# =====================================================================================================
# Part 3a. Time series: what did ABNB trade at when forward growth and margin looked like each scenario?
# =====================================================================================================
# The exit is at end-FY2027, so the relevant multiple is EV / forward EBITDA with FY2027 growth and margin
# already in the base. Match on the monthly point-in-time panel using the NTM growth proxy and LTM margin.
Mv = M[M.ev_ntm_ebitda_x.notna() & (M.ltm_revenue_growth_pct < 60)].copy()
Mv["year"] = Mv.month_end.dt.year
POST23 = Mv[Mv.month_end >= "2023-01-01"]

ev_rows = []
def add(scenario, method, multiple, lo, hi, n, detail):
    ev_rows.append(dict(scenario=scenario, method=method, exit_ev_fwd_ebitda_x=multiple,
                        low_x=lo, high_x=hi, n=n, detail=detail))

for s in SCEN:
    g, mgn = s27.loc[s, "rev_growth_pct"], s27.loc[s, "adj_ebitda_margin_pct"]
    # (i) nearest-neighbour band on the NTM growth proxy, 2023-2026 only (2021-22 is a different rate and growth regime)
    band = 4.0
    nb = POST23[(POST23.ntm_growth_proxy_pct >= g - band) & (POST23.ntm_growth_proxy_pct <= g + band)]
    if len(nb) < 5:                                     # widen until at least 5 months match
        band = 8.0
        nb = POST23[(POST23.ntm_growth_proxy_pct >= g - band) & (POST23.ntm_growth_proxy_pct <= g + band)]
    add(s, "Time series: months 2023-26 with NTM growth within band, median",
        nb.ev_ntm_ebitda_x.median(), nb.ev_ntm_ebitda_x.quantile(0.25), nb.ev_ntm_ebitda_x.quantile(0.75), len(nb),
        f"NTM growth {g:.1f}% +/- {band:.0f}pts, {nb.month_end.min():%b %Y}-{nb.month_end.max():%b %Y}")
    # (ii) OLS of EV/NTM EBITDA on NTM growth and LTM margin, 2023-2026 monthly, evaluated at the scenario
    d = POST23[["ev_ntm_ebitda_x", "ntm_growth_proxy_pct", "ltm_ebitda_margin_pct"]].dropna()
    m = sm.OLS(d.ev_ntm_ebitda_x, sm.add_constant(d[["ntm_growth_proxy_pct", "ltm_ebitda_margin_pct"]])).fit(
        cov_type="HAC", cov_kwds={"maxlags": 6})
    pred = float(m.params.iloc[0] + m.params.iloc[1] * g + m.params.iloc[2] * mgn)
    se = float(np.sqrt(np.array([1, g, mgn]) @ m.cov_params().values @ np.array([1, g, mgn])))
    add(s, "Time series: OLS on NTM growth + margin, 2023-26 monthly", pred, pred - 1.96 * se, pred + 1.96 * se, int(m.nobs),
        f"b_growth {m.params.iloc[1]:+.3f} (t {m.tvalues.iloc[1]:.1f}), b_margin {m.params.iloc[2]:+.3f} (t {m.tvalues.iloc[2]:.1f}), R2 {m.rsquared:.2f}, Newey-West 6")

# =====================================================================================================
# Part 3b. Cross-section: peer fits at each scenario's fundamentals (already computed in 12_peer_multiples.py)
# =====================================================================================================
XS_FITS = {
    "Cross-section: peers, EV/NTM EBITDA on growth": ("ev_ntm_adj_ebitda_x", "ntm_revenue_growth_pct"),
    "Cross-section: peers, EV/NTM EBITDA on growth + margin": ("ev_ntm_adj_ebitda_x", "ntm_revenue_growth_pct+adj_ebitda_margin_pct"),
    "Cross-section: peers, EV/NTM EBITDA on growth + margin + SBC + conversion": ("ev_ntm_adj_ebitda_x", "ntm_revenue_growth_pct+adj_ebitda_margin_pct+sbc_pct_rev+fcf_conversion_pct"),
}
for label, (dep, regs) in XS_FITS.items():
    for samp_key, samp_lab in [("all", "all peers"), ("travel", "travel + marketplace")]:
        sub = PREG[(PREG.dependent == dep) & (PREG.regressors == regs) & PREG.fit.str.contains("travel" if samp_key == "travel" else "all ", regex=False)]
        sub = sub[sub.fit.str.contains("travel") == (samp_key == "travel")]
        if sub.empty:
            continue
        r = sub.iloc[0]
        for s in SCEN:
            add(s, f"{label} ({samp_lab})", r[f"implied_{s.lower()}_fy27"], np.nan, np.nan, int(r.n),
                f"log-linear fit R2 {r.r2:.2f}; ABNB actual {r.abnb_actual:.1f}x vs fitted {r.abnb_fitted:.1f}x ({r.abnb_premium_pct:+.0f}%)")

# EV / NTM revenue fit on growth + margin, restated as an EV / EBITDA multiple by dividing by the scenario margin.
# This is the cross-section spec that can price margin expansion: regressing EV/EBITDA on the margin loads a mechanical
# -1/margin term (fitted b = -0.024 per pt vs the pure artefact -1/36.5 = -0.027), so that spec measures the artefact.
rev_fit = PREG[(PREG.dependent == "ev_ntm_revenue_x") & (PREG.regressors == "ntm_revenue_growth_pct+adj_ebitda_margin_pct")]
for _, r in rev_fit.iterrows():
    lab = "travel + marketplace" if "travel" in r.fit else "all peers"
    for s in SCEN:
        mgn = s27.loc[s, "adj_ebitda_margin_pct"]
        add(s, f"Cross-section: EV/NTM revenue fit on growth + margin, restated on adj. EBITDA ({lab})",
            r[f"implied_{s.lower()}_fy27"] / (mgn / 100), np.nan, np.nan, int(r.n),
            f"implied EV/NTM revenue {r[f'implied_{s.lower()}_fy27']:.2f}x / {mgn:.1f}% margin; fit R2 {r.r2:.2f}, b_margin {r.b_adj_ebitda_margin_pct:+.3f} (t {r.t_adj_ebitda_margin_pct:.1f}); ABNB actual {r.abnb_actual:.2f}x vs fitted {r.abnb_fitted:.2f}x ({r.abnb_premium_pct:+.0f}%)")

# Nearest observed comparables: travel + marketplace names whose consensus growth is closest to the scenario's.
TM = PEER[PEER.group.isin(["OTA", "Marketplace", "Hotel franchisor"]) & PEER.ev_ntm_adj_ebitda_x.notna()].copy()
for s in SCEN:
    g = s27.loc[s, "rev_growth_pct"]
    nn = TM.assign(dist=(TM.ntm_revenue_growth_pct - g).abs()).nsmallest(4, "dist")
    add(s, "Cross-section: 4 nearest travel/marketplace comps by growth, median observed multiple",
        nn.ev_ntm_adj_ebitda_x.median(), nn.ev_ntm_adj_ebitda_x.min(), nn.ev_ntm_adj_ebitda_x.max(), len(nn),
        "; ".join(f"{r.ticker} {r.ntm_revenue_growth_pct:.0f}% growth, {r.adj_ebitda_margin_pct:.0f}% margin, {r.ev_ntm_adj_ebitda_x:.1f}x" for _, r in nn.iterrows()))

# SBC-adjusted repeat: EV / NTM SBC-burdened (GAAP) EBITDA fit, converted back to an adj.-EBITDA multiple
gaap = PREG[(PREG.dependent == "ev_ntm_gaap_ebitda_x") & PREG.regressors.str.contains("gaap_ebitda_margin_pct")]
for _, r in gaap.iterrows():
    lab = "travel + marketplace" if "travel" in r.fit else "all peers"
    for s in SCEN:
        gm = s27.loc[s, "adj_ebitda_margin_pct"] - s27.loc[s, "sbc_pct_rev"]
        conv = gm / s27.loc[s, "adj_ebitda_margin_pct"]      # SBC-burdened EBITDA as a share of adj. EBITDA
        add(s, f"Cross-section SBC-adjusted: EV/NTM GAAP EBITDA fit, restated on adj. EBITDA ({lab})",
            r[f"implied_{s.lower()}_fy27"] * conv, np.nan, np.nan, int(r.n),
            f"fitted {r[f'implied_{s.lower()}_fy27']:.1f}x on SBC-burdened EBITDA, margin {gm:.1f}% vs adj {s27.loc[s,'adj_ebitda_margin_pct']:.1f}%, x{conv:.2f}")

# =====================================================================================================
# Part 3c. Intrinsic: the exit multiple a 10-year fade DCF supports at end-FY2027
# =====================================================================================================
# At the FY2027 exit, value the FY2028+ cash flows: growth starts at the scenario's FY2028 revenue growth,
# fades linearly to terminal g over 10 years, FCF margin held at the scenario's FY2027 level (so FCF/EBITDA
# conversion is the scenario's own), then a Gordon terminal. Divide by FY2027E adj. EBITDA.
def intrinsic_multiple(fcf0, growth0, wacc, term_g, years=10, ebitda=None):
    g = np.linspace(growth0, term_g, years + 1)[1:]
    pv, cf = 0.0, fcf0
    for i, gi in enumerate(g, start=1):
        cf *= (1 + gi / 100)
        pv += cf / (1 + wacc / 100) ** i
    tv = cf * (1 + term_g / 100) / (wacc / 100 - term_g / 100)
    ev = pv + tv / (1 + wacc / 100) ** years
    return ev / ebitda, ev

for s in SCEN:
    fcf27 = s27.loc[s, "fcf_musd"]; eb27 = s27.loc[s, "adj_ebitda_musd"]; g28 = s28.loc[s, "rev_growth_pct"]
    vals = {}
    for wacc in [9.0, 10.0, 11.0]:
        for tg in [2.5, 3.0]:
            x, _ = intrinsic_multiple(fcf27, g28, wacc, tg, ebitda=eb27)
            vals[(wacc, tg)] = x
    mid = vals[(10.0, 3.0)]
    add(s, "Intrinsic: 10y fade DCF at the FY27 exit, reported FCF, WACC 10% / g 3%", mid,
        min(vals.values()), max(vals.values()), 1,
        f"FY27 FCF ${fcf27/1000:.1f}B on FY27 EBITDA ${eb27/1000:.1f}B (conversion {100*fcf27/eb27:.0f}%), FY28 growth {g28:.1f}% fading to g; range = WACC 9-11%, g 2.5-3.0%")
    # SBC-adjusted repeat: value SBC-adjusted FCF instead
    sfcf27 = s27.loc[s, "sbc_adj_fcf_musd"]
    svals = {(w, t): intrinsic_multiple(sfcf27, g28, w, t, ebitda=eb27)[0] for w in [9.0, 10.0, 11.0] for t in [2.5, 3.0]}
    add(s, "Intrinsic SBC-adjusted: same DCF on SBC-adjusted FCF, WACC 10% / g 3%", svals[(10.0, 3.0)],
        min(svals.values()), max(svals.values()), 1,
        f"FY27 SBC-adj FCF ${sfcf27/1000:.1f}B (SBC {s27.loc[s,'sbc_pct_rev']:.0f}% of revenue); range = WACC 9-11%, g 2.5-3.0%")

# =====================================================================================================
# Part 3d. Today's multiple and the recent range
# =====================================================================================================
now_fwd = float(Q[Q.quarter == "3Q26"].ev_ntm_ebitda_x.iloc[0])
now_ltm = float(Q[Q.quarter == "3Q26"].ev_ltm_ebitda_x.iloc[0])
for s in SCEN:
    add(s, "Today: EV / NTM EBITDA at $181.94 (4 Sep 2026)", now_fwd,
        POST23.ev_ntm_ebitda_x.min(), POST23.ev_ntm_ebitda_x.max(), len(POST23),
        f"EV/LTM EBITDA {now_ltm:.1f}x; 2023-26 monthly range {POST23.ev_ntm_ebitda_x.min():.1f}-{POST23.ev_ntm_ebitda_x.max():.1f}x, median {POST23.ev_ntm_ebitda_x.median():.1f}x")
E = pd.DataFrame(ev_rows)
E["assumed_x"] = E.scenario.map(ASSUMED)
E["vs_assumed_x"] = E.exit_ev_fwd_ebitda_x - E.assumed_x
E.to_csv(os.path.join(OUT, "12_exit_multiple_evidence.csv"), index=False, float_format="%.3f")

# ---------------- recommendation: median of the headline method per family, then rounded ------------
# Only the defensible specs go into the blend. The EV/EBITDA-on-margin fits (cross-section) are kept in the evidence
# CSV as diagnostics because their margin coefficient is essentially the mechanical -1/margin, and the four-regressor
# fit adds an SBC penalty on n=12-18, which is more than that sample can carry.
FAMILY = {
    "Time series": ["Time series: months 2023-26 with NTM growth within band, median",
                    "Time series: OLS on NTM growth + margin, 2023-26 monthly"],
    "Cross-section": ["Cross-section: peers, EV/NTM EBITDA on growth (all peers)",
                      "Cross-section: peers, EV/NTM EBITDA on growth (travel + marketplace)",
                      "Cross-section: EV/NTM revenue fit on growth + margin, restated on adj. EBITDA (all peers)",
                      "Cross-section: EV/NTM revenue fit on growth + margin, restated on adj. EBITDA (travel + marketplace)",
                      "Cross-section: 4 nearest travel/marketplace comps by growth, median observed multiple"],
    "Intrinsic": ["Intrinsic: 10y fade DCF at the FY27 exit, reported FCF, WACC 10% / g 3%"],
}
IN_BLEND = {m for v in FAMILY.values() for m in v}
E["used_in_blend"] = E.method.isin(IN_BLEND)
E.to_csv(os.path.join(OUT, "12_exit_multiple_evidence.csv"), index=False, float_format="%.3f")
rec = []
for s in SCEN:
    fam = {k: E[(E.scenario == s) & E.method.isin(v)].exit_ev_fwd_ebitda_x.median() for k, v in FAMILY.items()}
    blend = float(np.mean(list(fam.values())))
    recommended = round(blend * 2) / 2                      # to the nearest half turn
    eb27 = s27.loc[s, "adj_ebitda_musd"]; nc27 = s27.loc[s, "net_cash_musd"]; sh27 = s27.loc[s, "diluted_shares_m"]
    price_rec = (recommended * eb27 + nc27) / sh27
    price_ass = (ASSUMED[s] * eb27 + nc27) / sh27
    rec.append(dict(scenario=s, fy27_rev_growth_pct=s27.loc[s, "rev_growth_pct"], fy27_margin_pct=s27.loc[s, "adj_ebitda_margin_pct"],
                    fy27_sbc_pct_rev=s27.loc[s, "sbc_pct_rev"], fy27_adj_ebitda_musd=eb27, fy27_net_cash_musd=nc27,
                    fy27_diluted_shares_m=sh27,
                    time_series_x=fam["Time series"], cross_section_x=fam["Cross-section"], intrinsic_x=fam["Intrinsic"],
                    blend_x=blend, recommended_x=recommended, assumed_x=ASSUMED[s],
                    price_at_recommended=price_rec, price_at_assumed=price_ass,
                    upside_at_recommended_pct=100 * (price_rec / LAST_PRICE - 1), upside_at_assumed_pct=100 * (price_ass / LAST_PRICE - 1)))
R = pd.DataFrame(rec)
R.to_csv(os.path.join(OUT, "12_exit_multiple_recommendation.csv"), index=False, float_format="%.3f")

# ---------------- price sensitivity grid -----------------------------------------------------------
grid = []
MULT_GRID = [12, 14, 16, 18, 20, 22, 24, 26]
for s in SCEN:
    eb27, nc27, sh27 = s27.loc[s, "adj_ebitda_musd"], s27.loc[s, "net_cash_musd"], s27.loc[s, "diluted_shares_m"]
    fcf27, sfcf27, ni27 = s27.loc[s, "fcf_musd"], s27.loc[s, "sbc_adj_fcf_musd"], s27.loc[s, "net_income_proxy_musd"]
    for x in MULT_GRID:
        grid.append(dict(scenario=s, multiple_x=x,
                         price_on_ev_ebitda=(x * eb27 + nc27) / sh27,
                         price_on_ev_fcf=(x * fcf27 + nc27) / sh27,
                         price_on_p_sbc_adj_fcf=x * sfcf27 / sh27,
                         price_on_p_earnings_proxy=x * ni27 / sh27,
                         upside_on_ev_ebitda_pct=100 * ((x * eb27 + nc27) / sh27 / LAST_PRICE - 1)))
G = pd.DataFrame(grid)
G.to_csv(os.path.join(OUT, "12_price_sensitivity.csv"), index=False, float_format="%.2f")

# =====================================================================================================
# Part 4b (finish): how much of the day-1 move is multiple, how much is estimate
# =====================================================================================================
p = PDEC.dropna(subset=["ret_1d_pct", "estimate_change_pct", "multiple_change_pct"]).copy()
p["good"] = p.ret_1d_pct > 0
att = []
for lab, sub in [("all prints", p), ("up days", p[p.good]), ("down days", p[~p.good]),
                 ("moves >= 7%", p[p.ret_1d_pct.abs() >= 7]), ("2023-26 prints", p[p.reaction_date >= "2023-01-01"])]:
    att.append(dict(sample=lab, n=len(sub), mean_ret_1d_pct=sub.ret_1d_pct.mean(),
                    mean_abs_ret_1d_pct=sub.ret_1d_pct.abs().mean(),
                    mean_estimate_change_pct=sub.estimate_change_pct.mean(),
                    mean_abs_estimate_change_pct=sub.estimate_change_pct.abs().mean(),
                    mean_multiple_change_pct=sub.multiple_change_pct.mean(),
                    mean_abs_multiple_change_pct=sub.multiple_change_pct.abs().mean(),
                    share_of_abs_move_from_multiple=sub.multiple_change_pct.abs().mean() / (sub.multiple_change_pct.abs().mean() + sub.estimate_change_pct.abs().mean()),
                    corr_ret_estimate=sub.ret_1d_pct.corr(sub.estimate_change_pct),
                    corr_ret_multiple=sub.ret_1d_pct.corr(sub.multiple_change_pct)))
A = pd.DataFrame(att)
A.to_csv(os.path.join(OUT, "12_print_move_attribution.csv"), index=False, float_format="%.3f")

# =====================================================================================================
# Part 1 (finish): decompose each regime's price move into fundamental growth vs re-rating
# =====================================================================================================
# EV = multiple x LTM adj. EBITDA, so d log EV = d log multiple + d log EBITDA exactly. Price is then EV plus net
# cash over the diluted count, so the share-count and net-cash contributions are the residual.
Qi = Q.set_index("quarter")
REGIMES = [("4Q21", "4Q22", "2022 de-rating: rates up, COVID base laps"),
           ("4Q22", "1Q24", "2023 recovery: margin peaks, AI-travel optimism"),
           ("1Q24", "1Q26", "2024-25 de-rating: nights growth to single digits"),
           ("1Q26", "3Q26", "2026 re-rating: 2Q26 print and the reacceleration"),
           ("4Q21", "1Q26", "peak to trough, whole de-rating"),
           ("4Q21", "3Q26", "peak to today")]
drows = []
for a, b in [(a, b) for a, b, _ in REGIMES]:
    pass
for a, b, lab in REGIMES:
    ra, rb = Qi.loc[a], Qi.loc[b]
    drows.append(dict(from_quarter=a, to_quarter=b, regime=lab,
                      price_from=ra.price, price_to=rb.price, price_change_pct=100 * (rb.price / ra.price - 1),
                      ev_ltm_ebitda_from_x=ra.ev_ltm_ebitda_x, ev_ltm_ebitda_to_x=rb.ev_ltm_ebitda_x,
                      multiple_change_pct=100 * (rb.ev_ltm_ebitda_x / ra.ev_ltm_ebitda_x - 1),
                      ltm_ebitda_from_musd=ra.ltm_adj_ebitda_musd, ltm_ebitda_to_musd=rb.ltm_adj_ebitda_musd,
                      ebitda_change_pct=100 * (rb.ltm_adj_ebitda_musd / ra.ltm_adj_ebitda_musd - 1),
                      shares_from_m=ra.diluted_shares_m, shares_to_m=rb.diluted_shares_m,
                      share_count_change_pct=100 * (rb.diluted_shares_m / ra.diluted_shares_m - 1),
                      ltm_growth_from_pct=ra.ltm_revenue_growth_pct, ltm_growth_to_pct=rb.ltm_revenue_growth_pct,
                      ntm_growth_from_pct=ra.ntm_growth_proxy_pct, ntm_growth_to_pct=rb.ntm_growth_proxy_pct,
                      margin_from_pct=ra.ltm_ebitda_margin_pct, margin_to_pct=rb.ltm_ebitda_margin_pct,
                      dgs10_from_pct=ra.dgs10_pct, dgs10_to_pct=rb.dgs10_pct,
                      ndx_fwd_pe_from_x=ra.ndx_fwd_pe, ndx_fwd_pe_to_x=rb.ndx_fwd_pe,
                      log_share_from_multiple=np.log(rb.ev_ltm_ebitda_x / ra.ev_ltm_ebitda_x) / np.log(rb.ev_musd / ra.ev_musd) if rb.ev_musd != ra.ev_musd else np.nan))
DR = pd.DataFrame(drows)
DR.to_csv(os.path.join(OUT, "12_regime_decomposition.csv"), index=False, float_format="%.3f")

# =====================================================================================================
# Part 5. Sell-side target book
# =====================================================================================================
aa = pd.read_csv(os.path.join(OUT, "09_analyst_actions.csv"), parse_dates=["grade_datetime", "date"])
aa = aa[aa.date <= "2026-09-06"].sort_values("grade_datetime")
aa["target"] = aa.currentPriceTarget.replace(0, np.nan)
# current book: the latest action per firm, keeping only firms that have acted in the last 12 months
latest = aa.sort_values("grade_datetime").groupby("Firm").tail(1).copy()
latest = latest[latest.date >= "2025-09-06"]
BUCKET = {"Buy": "Buy", "Strong Buy": "Buy", "Outperform": "Buy", "Overweight": "Buy", "Positive": "Buy", "Market Outperform": "Buy",
          "Sector Outperform": "Buy", "Add": "Buy", "Accumulate": "Buy", "Neutral": "Hold", "Hold": "Hold", "Equal-Weight": "Hold",
          "Market Perform": "Hold", "Sector Perform": "Hold", "In-Line": "Hold", "Peer Perform": "Hold", "Sector Weight": "Hold",
          "Underweight": "Sell", "Underperform": "Sell", "Sell": "Sell", "Sector Underperform": "Sell", "Reduce": "Sell"}
latest["rating_bucket"] = latest.ToGrade.map(BUCKET).fillna("Other")
eb27b, nc27b, sh27b = s27.loc["Base", "adj_ebitda_musd"], s27.loc["Base", "net_cash_musd"], s27.loc["Base", "diluted_shares_m"]
fcf27b, sfcf27b = s27.loc["Base", "fcf_musd"], s27.loc["Base", "sbc_adj_fcf_musd"]
latest["implied_ev_musd"] = latest.target * sh27b - nc27b
latest["implied_ev_fy27_ebitda_x"] = latest.implied_ev_musd / eb27b
latest["implied_ev_fy27_fcf_x"] = latest.implied_ev_musd / fcf27b
latest["implied_p_fy27_sbc_adj_fcf_x"] = latest.target * sh27b / sfcf27b
latest["implied_ev_ltm_ebitda_x"] = (latest.target * today.diluted_shares_m - today.net_cash_ex_float_musd) / today.ltm_adj_ebitda_musd
latest["upside_vs_181_94_pct"] = 100 * (latest.target / LAST_PRICE - 1)
T = latest[["Firm", "date", "ToGrade", "rating_bucket", "Action", "priceTargetAction", "target", "priorPriceTarget",
            "upside_vs_181_94_pct", "implied_ev_fy27_ebitda_x", "implied_ev_fy27_fcf_x", "implied_p_fy27_sbc_adj_fcf_x",
            "implied_ev_ltm_ebitda_x", "source"]].sort_values("target", ascending=False)
T.to_csv(os.path.join(OUT, "12_analyst_targets.csv"), index=False, float_format="%.3f")

tg = T.target.dropna()
post = aa[(aa.date >= PRINT_2Q26) & aa.target.notna() & (aa.priorPriceTarget > 0)].copy()
post["change_pct"] = 100 * (post.target / post.priorPriceTarget - 1)
summ = [
    dict(metric="firms with an action in the last 12 months", value=len(T), unit="count", detail="yfinance/Benzinga feed via 09_analyst_actions.csv, pulled 6 Sep 2026"),
    dict(metric="firms with a live price target", value=len(tg), unit="count", detail="target > 0 on the latest action"),
    dict(metric="mean target", value=tg.mean(), unit="USD", detail="cross-check: stockanalysis.com 3 Sep 2026 average $178.96 across 46 analysts"),
    dict(metric="median target", value=tg.median(), unit="USD", detail=""),
    dict(metric="high target", value=tg.max(), unit="USD", detail=", ".join(T[T.target == tg.max()].Firm)),
    dict(metric="low target", value=tg.min(), unit="USD", detail=", ".join(T[T.target == tg.min()].Firm)),
    dict(metric="high/low spread", value=tg.max() / tg.min(), unit="x", detail=f"{tg.max():.0f} vs {tg.min():.0f}"),
    dict(metric="dispersion (sd / mean)", value=tg.std() / tg.mean(), unit="ratio", detail=""),
    dict(metric="mean target vs spot $181.94", value=100 * (tg.mean() / LAST_PRICE - 1), unit="%", detail="spot is above the average target"),
    dict(metric="share of targets below spot", value=100 * (tg < LAST_PRICE).mean(), unit="%", detail=""),
    dict(metric="implied EV / FY27E base EBITDA at the mean target", value=(tg.mean() * sh27b - nc27b) / eb27b, unit="x", detail=f"FY27E base adj. EBITDA ${eb27b/1000:.2f}B, net cash ${nc27b/1000:.1f}B, {sh27b:.0f}M shares"),
    dict(metric="implied EV / FY27E base EBITDA at the high target", value=(tg.max() * sh27b - nc27b) / eb27b, unit="x", detail=""),
    dict(metric="implied EV / FY27E base EBITDA at the low target", value=(tg.min() * sh27b - nc27b) / eb27b, unit="x", detail=""),
    dict(metric="price-target revisions since the 2Q26 print (7 Aug 2026)", value=len(post), unit="count", detail=f"{(post.change_pct > 0).sum()} raises, {(post.change_pct < 0).sum()} cuts"),
    dict(metric="median revision since the 2Q26 print", value=post.change_pct.median(), unit="%", detail=f"mean {post.change_pct.mean():.1f}%, range {post.change_pct.min():.1f}% to {post.change_pct.max():.1f}%"),
    dict(metric="stock move on the 2Q26 print day", value=float(PDEC[PDEC.quarter == "2Q26"].ret_1d_pct.iloc[0]), unit="%", detail="7 Aug 2026"),
]
for b in ["Buy", "Hold", "Sell", "Other"]:
    n = int((T.rating_bucket == b).sum())
    summ.append(dict(metric=f"rating mix: {b}", value=n, unit="count",
                     detail=f"{100*n/len(T):.0f}% of the {len(T)}-firm book"))
S = pd.DataFrame(summ)
S.to_csv(os.path.join(OUT, "12_analyst_target_summary.csv"), index=False, float_format="%.3f")

# =====================================================================================================
# Figures
# =====================================================================================================
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(1, 2, figsize=(13, 5.2), gridspec_kw={"width_ratios": [1.35, 1]})
COL = {"Time series": "#1f4e79", "Cross-section": "#c55a11", "Intrinsic": "#548235", "Today": "#7f7f7f",
       "Cross-section SBC-adjusted": "#e08a4a", "Intrinsic SBC-adjusted": "#94b96b"}
def fam_of(m):
    for k in ["Cross-section SBC-adjusted", "Intrinsic SBC-adjusted", "Time series", "Cross-section", "Intrinsic", "Today"]:
        if m.startswith(k):
            return k
    return "Today"
E["family"] = E.method.map(fam_of)
for i, s in enumerate(SCEN):
    sub = E[E.scenario == s]
    for _, r in sub.iterrows():
        ax[0].scatter(i + np.random.uniform(-0.16, 0.16), r.exit_ev_fwd_ebitda_x, color=COL[r.family], s=34, zorder=3, alpha=0.85)
    ax[0].hlines(ASSUMED[s], i - 0.3, i + 0.3, color="black", lw=2.2, zorder=4)
    ax[0].hlines(R[R.scenario == s].recommended_x.iloc[0], i - 0.3, i + 0.3, color="#c00000", lw=2.2, ls="--", zorder=4)
ax[0].set_xticks(range(3)); ax[0].set_xticklabels([f"{s}\n{s27.loc[s,'rev_growth_pct']:.0f}% growth, {s27.loc[s,'adj_ebitda_margin_pct']:.1f}% margin" for s in SCEN])
ax[0].set_ylabel("Exit EV / forward adj. EBITDA (x)")
ax[0].set_title("FY2027E exit multiple: every method (black = model's 18/22/25.5x, red dash = recommended)")
for k, c in COL.items():
    ax[0].scatter([], [], color=c, label=k)
ax[0].legend(frameon=False, fontsize=7.5, ncol=2)
ax[0].axhline(now_fwd, color="#7f7f7f", lw=0.8, ls=":")
ax[0].annotate(f"today {now_fwd:.1f}x", (2.35, now_fwd), fontsize=7.5, color="#7f7f7f")
for s, c in zip(SCEN, ["#c55a11", "#1f4e79", "#548235"]):
    sub = G[G.scenario == s]
    ax[1].plot(sub.multiple_x, sub.price_on_ev_ebitda, color=c, label=f"{s} FY27E")
    rr = R[R.scenario == s].iloc[0]
    ax[1].scatter([rr.recommended_x], [rr.price_at_recommended], color=c, s=45, zorder=4)
ax[1].axhline(LAST_PRICE, color="black", lw=0.8, ls="--"); ax[1].annotate("$181.94", (12.2, LAST_PRICE + 6), fontsize=8)
ax[1].set_xlabel("Exit EV / FY2027E adj. EBITDA (x)"); ax[1].set_ylabel("Implied price ($)")
ax[1].set_title("Price sensitivity to the exit multiple (dots = recommended)"); ax[1].legend(frameon=False)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "12_exit_multiple_evidence.png"), dpi=150); plt.close()

fig, ax = plt.subplots(1, 2, figsize=(13, 5.4), gridspec_kw={"width_ratios": [1.5, 1]})
tt = T.dropna(subset=["target"]).sort_values("target")
cb = {"Buy": "#1f4e79", "Hold": "#7f7f7f", "Sell": "#c00000", "Other": "#c55a11"}
ax[0].barh(range(len(tt)), tt.target, color=[cb[b] for b in tt.rating_bucket])
ax[0].set_yticks(range(len(tt))); ax[0].set_yticklabels([f"{f} ({d:%b-%y})" for f, d in zip(tt.Firm, tt.date)], fontsize=7)
ax[0].axvline(LAST_PRICE, color="black", lw=1.2); ax[0].annotate("spot $181.94", (LAST_PRICE + 2, 0.5), fontsize=8, rotation=90)
ax[0].axvline(tt.target.mean(), color="#c00000", lw=1, ls="--"); ax[0].annotate(f"mean ${tt.target.mean():.0f}", (tt.target.mean() + 2, len(tt) - 6), fontsize=8, color="#c00000", rotation=90)
ax2 = ax[0].twiny()
ax2.set_xlim([(x * sh27b - nc27b) / eb27b for x in ax[0].get_xlim()])
ax2.set_xlabel("implied EV / FY2027E base-case adj. EBITDA (x)", fontsize=8)
ax[0].set_xlabel("Price target ($)"); ax[0].set_title("ABNB sell-side targets, latest action per firm (colour = rating)")
from matplotlib.patches import Patch
ax[0].legend(handles=[Patch(facecolor=cb[b], label=b) for b in ["Buy", "Hold", "Sell"] if (tt.rating_bucket == b).any()],
             frameon=False, fontsize=8, loc="lower right")
ax[1].scatter(p.estimate_change_pct, p.ret_1d_pct, color="#7f7f7f", s=34, label="estimate change")
ax[1].scatter(p.multiple_change_pct, p.ret_1d_pct, color="#1f4e79", s=34, label="multiple change")
for _, r in p.iterrows():
    if abs(r.ret_1d_pct) > 8:
        ax[1].annotate(r.quarter, (r.multiple_change_pct, r.ret_1d_pct), fontsize=7, xytext=(3, 2), textcoords="offset points")
ax[1].axhline(0, color="k", lw=0.5); ax[1].axvline(0, color="k", lw=0.5)
ax[1].set_xlabel("change on the print day (%)"); ax[1].set_ylabel("day-1 return (%)")
ax[1].set_title("Day-1 moves are re-ratings, not estimate changes"); ax[1].legend(frameon=False)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "12_analyst_targets.png"), dpi=150); plt.close()

pd.set_option("display.width", 260); pd.set_option("display.max_columns", 40); pd.set_option("display.max_colwidth", 90)
print("=== exit-multiple evidence ===");
print(E[["scenario", "method", "exit_ev_fwd_ebitda_x", "low_x", "high_x", "n", "assumed_x", "vs_assumed_x"]].round(2).to_string())
print("\n=== recommendation ==="); print(R.round(2).to_string())
print("\n=== price sensitivity ==="); print(G.round(1).to_string())
print("\n=== print-move attribution ==="); print(A.round(2).to_string())
print("\n=== analyst targets ==="); print(T.drop(columns=["source"]).round(2).to_string())
print("\n=== target summary ==="); print(S.round(2).to_string())
