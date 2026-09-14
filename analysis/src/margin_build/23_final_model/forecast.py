"""WS23 step 2-5: line decomposition, the full forecast set, cyclicality, and the 5 Nov card.

Consumes 23_combination_*.csv (step 1), M1's LIVE line path, M6's cost-response k's,
M7's below-EBITDA bridge parameters, the WS06 v2b revenue path and the WS03 consensus.

Outputs (data/processed/margin_build/23_final_model/)
  23_path_rule.csv             which object supplies which quarter, and why
  23_bands.csv                 conformal bands by horizon, two calibration windows
  23_lines_quarterly.csv       reconciled six-line stack, history + forecast, 3 scenarios
  23_forecast_quarterly.csv    revenue -> lines -> adj EBITDA -> GAAP -> EPS -> FCF, 3 scenarios
  23_forecast_annual.csv       FY26 / FY27 / FY28
  23_vs_consensus.csv          vs LSEG + Bloomberg + management + the prior team numbers
  23_scenarios.csv             bear / base / bull x cost-response variant
  23_seasonality.csv           quarterly seasonal profile with the mechanical/discretionary split
  23_macro_sensitivity.csv     margin change per 1pt of revenue growth shortfall
  23_fy26_floor_breakeven.csv  how big a 2H26 revenue miss the 35.5% floor survives
  23_card_5nov.csv             the 5 Nov card
Interpreter: py -3.13
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

import os

ROOT = Path(__file__).resolve().parents[4]
PROC = ROOT / "data" / "processed" / "margin_build"
HDIR = PROC / "10_harness_margin"
OUT = PROC / "23_final_model"
OUT.mkdir(parents=True, exist_ok=True)

# WS31 audit 18: no-write verification mode (see combine.py)
VERIFY = os.environ.get("MARGIN_VERIFY_ONLY") == "1"
VOUT = OUT / "_verify"
if VERIFY:
    VOUT.mkdir(parents=True, exist_ok=True)


def wpath(name):
    return (VOUT if VERIFY else OUT) / name


def rpath(name):
    if VERIFY and (VOUT / name).exists():
        return VOUT / name
    return OUT / name

QF = ["2026Q3", "2026Q4", "2027Q1", "2027Q2", "2027Q3", "2027Q4"]
LINES = ["cor", "ops", "pd", "sm", "ga"]
DISCRETIONARY = ["pd", "sm", "ga"]
# W1 h=0 PIT error variance of M1 lines_v2|b_elastic_rw (harness scoreboard_by_quarter)
LINE_ERR_VAR = {"cor": 667.102, "ops": 425.629, "pd": 211.225, "sm": 1721.347, "ga": 314.624}
K_TOTAL_FLEX = 0.364173     # M6 k on total cash costs, 1Q22+, rw, lag0 (t 6.58)
K_LINE = {"cor": 0.561589, "ops": 0.438174, "pd": -0.210634, "sm": 0.418480, "ga": -0.110228}
FY26_FLOOR = 35.5
NOV_SENTENCE_FY26 = 36.0    # M3: numeric floor + 50bp, exact 2 of 2
Q3_25_MARGIN = 50.085470
# WS31 audit 06: M7's measured below-EBITDA bridge error, W2 h=0 with EBITDA known
# (docs/margin-build/notes/M7_below_ebitda.md, M7_discussion_blend_eps.csv). The EPS band
# is the EBITDA term and this term combined in quadrature.
M7_BRIDGE_EPS_SD = 0.083
# WS31 audit 05: bear/bull statements are built at M6's fitted cost response, not at the
# base margin. `held` (k=0) and `full_flex` (k=1) stay in 23_scenarios.csv as sensitivities.
SCENARIO_COST_RESPONSE_K = 0.364173


def load():
    d = {}
    d["live"] = pd.read_csv(rpath("23_combination_live.csv"))
    d["bt"] = pd.read_csv(rpath("23_combination_by_quarter.csv"))
    d["dfm"] = pd.read_csv(rpath("23_dollar_from_margin_by_quarter.csv"))
    d["dfm_live"] = pd.read_csv(rpath("23_dollar_from_margin_live.csv"))
    d["tg"] = pd.read_csv(HDIR / "targets.csv")
    rev = pd.read_csv(PROC / "06_fy27_path_v2" / "06_revenue_path_3q26_4q27_v2b.csv")
    rv = rev[rev.line == "revenue_musd"].pivot(index="quarter", columns="scenario", values="value")
    rv.index = [f"20{x[2:]}Q{x[0]}" if len(x) == 4 and x[1] == "Q" else x for x in rv.index]
    d["rev"] = rv
    d["revq"] = rev
    d["ann"] = pd.read_csv(PROC / "06_fy27_path_v2" / "06_annual_fy26_fy28_v2b.csv")
    d["m1"] = pd.read_csv(PROC / "M1_driver_lines" / "M1_driver_lines_live_quarterly.csv")
    d["m7q"] = pd.read_csv(PROC / "M7_below_ebitda" / "M7_live_waterfall_quarterly.csv")
    d["m7a"] = pd.read_csv(PROC / "M7_below_ebitda" / "M7_below_ebitda_annual_forecasts.csv")
    d["cons"] = pd.read_csv(PROC / "03_consensus_pit" / "03_current_consensus.csv")
    d["cons27"] = pd.read_csv(PROC / "06_fy27_path_v2" / "06_consensus_quarterly_2027.csv")
    return d


# --------------------------------------------------------------------- 1. the path
def build_path(d):
    live = d["live"]
    comb = live[(live.spec_id == "stack_clip") & (live.target == "adj_ebitda_margin_pct")] \
        .set_index("quarter")
    combusd = live[(live.spec_id == "stack_clip") & (live.target == "adj_ebitda_musd")] \
        .set_index("quarter")
    street_q = {"2026Q3": 49.775747, "2026Q4": 28.897437}
    m3 = {"2026Q3": 50.085470, "2026Q4": 29.904833, "2027Q1": 17.621216,
          "2027Q2": 33.191192, "2027Q3": 48.326551, "2027Q4": 28.145914}
    rows = []
    for q in QF:
        hz = QF.index(q)
        if q == "2026Q3":
            src, m, why = "final-margin|combined|stack_clip (h=0)", comb.loc[q, "point"], \
                "h=0: the combination beats seasonal_naive 0.50x (W1) / 0.40x (W2) and the Street 0.71x / 0.60x, both windows, both weightings"
        elif q == "2026Q4":
            src, m, why = "baselines-margin|street (h=1)", street_q[q], \
                "h=1: the combination beats seasonal_naive (0.83x / 0.81x) but LOSES to the raw Street by 20-28%; the pre-registered secondary test fails, so the Street carries the quarter"
        else:
            src, m, why = "final-margin|combined|stack_clip (h>=2, SCENARIO)", comb.loc[q, "point"], \
                "h=2: the combination is 0.91x seasonal_naive in W1 but 1.02x in W2 - it fails. 2027 is a scenario, not a forecast"
        rows.append(dict(quarter=q, horizon_q=hz, margin_pct=float(m), source=src, rationale=why,
                         combination_pct=float(comb.loc[q, "point"]),
                         combination_raw_pct=float(comb.loc[q, "raw_point"]),
                         clip=comb.loc[q, "clip"],
                         street_pct=street_q.get(q, np.nan),
                         m3_sentence_pct=m3.get(q, np.nan),
                         combination_ebitda_musd=float(combusd.loc[q, "point"])
                         if q in combusd.index else np.nan))
    p = pd.DataFrame(rows)
    p.to_csv(wpath("23_path_rule.csv"), index=False)
    return p


# --------------------------------------------------------------------- 2. bands
def build_bands(d):
    bt = d["bt"]
    dfm = d["dfm"]
    rows = []
    # WS31 audit 04: `adj_ebitda_musd_from_margin` is the ADOPTED dollar construction
    # (the margin combination x the revenue leg) — the object the card's band and
    # P(beat) both come from. `adj_ebitda_musd` is the four-member dollar combination,
    # kept as a labelled cross-check.
    for target in ["adj_ebitda_margin_pct", "adj_ebitda_musd", "adj_ebitda_musd_from_margin"]:
        for hz in [0, 1, 2]:
            if target == "adj_ebitda_musd_from_margin":
                s = dfm[(dfm.window == "W1") & (dfm.horizon_q == hz)
                        & (dfm.prior_basis == "PIT")
                        & (dfm.spec_id == "stack_clip")].sort_values("quarter")
                s = s.dropna(subset=["err"])
            else:
                s = bt[(bt.target == target) & (bt.window == "W1") & (bt.horizon_q == hz)
                       & (bt.prior_basis == "PIT") & (bt.spec_id == "stack_clip")].sort_values("quarter")
            for cal, e in (("W1_all_n14", s["err"].values),
                           ("recent_2024Q1plus", s[s.quarter >= "2024Q1"]["err"].values)):
                a = np.sort(np.abs(e))
                n = len(a)
                if n == 0:
                    continue
                k80 = int(np.ceil((n + 1) * 0.8))
                k90 = int(np.ceil((n + 1) * 0.9))
                q80 = a[min(k80, n) - 1] * (1.0 if k80 <= n else (n + 1) / n)
                q90 = a[min(k90, n) - 1] * (1.0 if k90 <= n else (n + 1) / n)
                mae = np.abs(e).mean()
                rows.append(dict(target=target, horizon_q=hz, calibration=cal, n=n,
                                 qhat80=q80, qhat90=q90,
                                 # WS31 audit 11: these two are the THEORETICAL rank
                                 # resolution of a split-conformal interval at this n --
                                 # the grid the attainable coverage sits on. They are NOT
                                 # a measurement of coverage, and they say nothing about
                                 # future coverage for selected, expanding-window
                                 # time-series forecasts. Observed coverage is the cov80
                                 # column of the scoreboard (h=0: 13/14 W1, 10/10 W2).
                                 rank_grid_cov80_lo=min(k80, n) / (n + 1),
                                 rank_grid_cov80_hi=min(k80 + 1, n + 1) / (n + 1),
                                 gaussian_from_mae_80=1.2816 * 1.2533 * mae,
                                 gaussian_sd_from_qhat80=q80 / 1.2816,
                                 mae=mae, bias=e.mean(),
                                 bias_last5=e[-5:].mean() if n >= 5 else np.nan))
    b = pd.DataFrame(rows)
    b.to_csv(wpath("23_bands.csv"), index=False)
    return b


# --------------------------------------------------------------------- 3. lines
def build_lines(d, path):
    """Reconcile M1's line stack to the adopted adj EBITDA path.

    WS31 audit 02/03: ONE add-back schedule. The only add-back carried between the cash
    cost stack and adj EBITDA is D&A, taken from the same M7 bridge the GAAP walk uses:

        sum(five cash lines) - D&A = total cash costs = revenue - adj EBITDA
        adj EBITDA - SBC - D&A     = GAAP operating income

    M1's own `other_net` rule (0.68% of revenue, $32.5M in 3Q26) carried ~$11.9M of
    non-D&A add-backs that the GAAP bridge did not subtract. On actuals 2024Q1-2026Q2
    `other_net - D&A` runs -12 to +6 with a mean of -1.2, so D&A alone is the schedule
    the data supports. `m1_other_net_musd` is kept as a column for the diff.

    WS31 audit 05: bear/bull carry M6's fitted cost response (k on total cash costs), so
    the scenario statements are no longer the base margin on a different revenue.
    """
    m1 = d["m1"]
    m7 = d["m7q"]
    da_map = {}
    for q in QF:
        b = m7[(m7.quarter == q) & (m7.ebitda_source == "driver-lines") & (m7.scenario == "base")]
        da_map[q] = float(b.iloc[0].da_musd) if len(b) else 0.0
    base_rev, base_tcc = {}, {}
    out = []
    for sc in ["base", "bear", "bull"]:
        s = m1[(m1.spec_id == "b_elastic_rw") & (m1.scenario == sc) & (m1.prior_basis == "PIT")] \
            .set_index("quarter")
        rev = d["rev"][sc] if sc in d["rev"].columns else d["rev"]["base"]
        for q in QF:
            if q not in s.index:
                continue
            R = float(rev[q]) if q in rev.index and np.isfinite(rev[q]) else float(s.loc[q, "revenue"])
            if sc == "base":
                m = float(path.set_index("quarter").loc[q, "margin_pct"])
                ebitda = m / 100.0 * R
                base_rev[q], base_tcc[q] = R, R - ebitda
                cost_basis = "adopted margin path"
            else:
                # M6 cost response: total cash costs move by k x the revenue delta
                dl = R / base_rev[q] - 1.0
                C = base_tcc[q] * (1 + SCENARIO_COST_RESPONSE_K * dl)
                ebitda = R - C
                m = ebitda / R * 100.0
                cost_basis = f"flex k={SCENARIO_COST_RESPONSE_K:.6f} on total cash costs (M6)"
            other_net = float(s.loc[q, "other_net"])
            addbacks = da_map[q]
            model_lines = {l: float(s.loc[q, l]) for l in LINES}
            # scale M1's lines to the scenario revenue on their own driver elasticity
            if sc != "base":
                Rb = float(s.loc[q, "revenue"])
                dlm = (R / Rb - 1.0)
                for l in LINES:
                    model_lines[l] = model_lines[l] * (1 + K_LINE[l] * dlm)
            target_sum = R - ebitda + addbacks      # the five lines must sum to this
            resid = target_sum - sum(model_lines.values())
            vshare = {l: LINE_ERR_VAR[l] for l in DISCRETIONARY}
            tot = sum(vshare.values())
            rec = dict(quarter=q, scenario=sc, revenue_musd=R,
                       adj_ebitda_musd=ebitda, adj_ebitda_margin_pct=m,
                       scenario_cost_basis=cost_basis,
                       addbacks_musd=addbacks, m1_other_net_musd=other_net,
                       addback_diff_vs_m1_rule_musd=other_net - addbacks,
                       residual_allocated_musd=resid)
            for l in LINES:
                add = resid * vshare[l] / tot if l in DISCRETIONARY else 0.0
                rec[f"{l}_cash_musd"] = model_lines[l] + add
                rec[f"{l}_model_musd"] = model_lines[l]
                rec[f"{l}_alloc_musd"] = add
            rec["total_cash_costs_musd"] = R - ebitda
            rec["sum_five_lines_musd"] = sum(rec[f"{l}_cash_musd"] for l in LINES)
            # the reconciliation, displayed rather than implied
            rec["recon_lines_minus_addbacks_musd"] = rec["sum_five_lines_musd"] - addbacks
            rec["recon_gap_musd"] = rec["recon_lines_minus_addbacks_musd"] - rec["total_cash_costs_musd"]
            rec["sum_lines_check"] = rec["sum_five_lines_musd"]
            for l in LINES:
                rec[f"{l}_pct_rev"] = rec[f"{l}_cash_musd"] / R * 100
            out.append(rec)
    f = pd.DataFrame(out)
    # history
    tg = d["tg"]
    h = tg[(tg.quarter >= "2021Q1") & (tg.quarter <= "2026Q2")].copy()
    hist = pd.DataFrame(dict(
        quarter=h.quarter, scenario="actual", revenue_musd=h.revenue_musd,
        adj_ebitda_musd=h.adj_ebitda_musd, adj_ebitda_margin_pct=h.adj_ebitda_margin_pct,
        cor_cash_musd=h.cor_cash_musd, ops_cash_musd=h.ops_cash_musd, pd_cash_musd=h.pd_cash_musd,
        sm_cash_musd=h.sm_cash_musd, ga_cash_musd=h.ga_cash_ex_reserves_musd,
        total_cash_costs_musd=h.total_cash_costs_musd))
    for l in LINES:
        hist[f"{l}_pct_rev"] = hist[f"{l}_cash_musd"] / hist.revenue_musd * 100
    allf = pd.concat([hist, f], ignore_index=True)
    allf.to_csv(wpath("23_lines_quarterly.csv"), index=False)
    return f


# --------------------------------------------------------------------- 4. full P&L
def eps_halfwidth(qh, revenue, etr, shares):
    """80% EPS half-width: the EBITDA term and M7's measured bridge error, in quadrature.
    WS31 audit 06 — the published band used the EBITDA term alone."""
    if qh is None or not np.isfinite(qh.qhat80):
        return np.nan
    sd_ebitda = (qh.qhat80 / 1.2816) / 100.0 * revenue * (1 - etr) / shares
    return 1.2816 * float(np.sqrt(sd_ebitda ** 2 + M7_BRIDGE_EPS_SD ** 2))


def build_pl(d, path, lines):
    m7 = d["m7q"]
    rows = []
    bands = pd.read_csv(rpath("23_bands.csv"))
    bm = bands[(bands.target == "adj_ebitda_margin_pct") & (bands.calibration == "recent_2024Q1plus")] \
        .set_index("horizon_q")
    bdm = bands[(bands.target == "adj_ebitda_musd_from_margin")
                & (bands.calibration == "recent_2024Q1plus")].set_index("horizon_q")
    for _, r in lines.iterrows():
        q, sc = r.quarter, r.scenario
        b = m7[(m7.quarter == q) & (m7.ebitda_source == "driver-lines")
               & (m7.scenario == (sc if sc in ("base", "bear", "bull") else "base"))]
        if b.empty:
            b = m7[(m7.quarter == q) & (m7.ebitda_source == "driver-lines") & (m7.scenario == "base")]
        b = b.iloc[0]
        E = r.adj_ebitda_musd
        da, sbc = float(b.da_musd), float(b.sbc_musd)
        ii, ie, oi = float(b.interest_income_musd), float(b.interest_expense_musd), float(b.other_income_musd)
        etr, sh = float(b.tax_rate_pct) / 100.0, float(b.diluted_shares_m)
        op = E - da - sbc
        pre = op + ii - ie + oi
        tax = pre * etr
        ni = pre - tax
        eps = ni / sh
        # FCF: M7's quarterly object FAILED its pre-registered line; carried as a diagnostic only.
        # WS31 audit 07: CFO is REBUILT from the updated net income, not moved by the pretax
        # EBITDA delta. M7's identity is CFO = NI + D&A + SBC + d(unearned fees) + other, so the
        # working-capital-and-other block is carried across unchanged and NI is ours.
        wc_other = float(b.cfo_musd) - (float(b.net_income_musd) + float(b.da_musd)
                                        + float(b.sbc_musd))
        cfo_diag = ni + da + sbc + wc_other
        capex = float(b.capex_musd)
        hz = QF.index(q)
        qh = bm.loc[min(hz, 2)] if min(hz, 2) in bm.index else None
        qd = bdm.loc[min(hz, 2)] if min(hz, 2) in bdm.index else None
        rows.append(dict(
            quarter=q, scenario=sc, horizon_q=hz, revenue_musd=r.revenue_musd,
            cor_cash_musd=r.cor_cash_musd, ops_cash_musd=r.ops_cash_musd,
            pd_cash_musd=r.pd_cash_musd, sm_cash_musd=r.sm_cash_musd, ga_cash_musd=r.ga_cash_musd,
            # WS31 audit 02: the reconciliation is displayed, not implied
            sum_five_lines_musd=r.sum_five_lines_musd, addbacks_musd=r.addbacks_musd,
            total_cash_costs_musd=r.total_cash_costs_musd,
            recon_gap_musd=r.recon_gap_musd, scenario_cost_basis=r.scenario_cost_basis,
            adj_ebitda_musd=E, adj_ebitda_margin_pct=r.adj_ebitda_margin_pct,
            margin_q10=r.adj_ebitda_margin_pct - (qh.qhat80 if qh is not None else np.nan),
            margin_q90=r.adj_ebitda_margin_pct + (qh.qhat80 if qh is not None else np.nan),
            margin_q05=r.adj_ebitda_margin_pct - (qh.qhat90 if qh is not None else np.nan),
            margin_q95=r.adj_ebitda_margin_pct + (qh.qhat90 if qh is not None else np.nan),
            # WS31 audit 04: the dollar band is the ADOPTED dollar object's own conformal
            # band, the same one the card and P(beat) use. The margin-implied version is
            # kept beside it, labelled.
            ebitda_q10=E - (qd.qhat80 if qd is not None else np.nan),
            ebitda_q90=E + (qd.qhat80 if qd is not None else np.nan),
            ebitda_q05=E - (qd.qhat90 if qd is not None else np.nan),
            ebitda_q95=E + (qd.qhat90 if qd is not None else np.nan),
            ebitda_q10_margin_implied=(r.adj_ebitda_margin_pct - (qh.qhat80 if qh is not None else np.nan)) / 100 * r.revenue_musd,
            ebitda_q90_margin_implied=(r.adj_ebitda_margin_pct + (qh.qhat80 if qh is not None else np.nan)) / 100 * r.revenue_musd,
            sbc_musd=sbc, da_musd=da, op_income_musd=op,
            op_margin_pct=op / r.revenue_musd * 100,
            interest_income_musd=ii, interest_expense_musd=ie, other_income_musd=oi,
            pretax_income_musd=pre, tax_rate_pct=etr * 100, tax_provision_musd=tax,
            net_income_musd=ni, diluted_shares_m=sh, eps_diluted_gaap=eps,
            eps_street_def=eps,
            # WS31 audit 06: the EPS band now carries BOTH the EBITDA term and M7's
            # measured below-EBITDA bridge error (sd $0.083), combined in quadrature.
            # `eps_q10/q90` are the joint band; `*_ebitda_only` is the old conditional one.
            eps_q10=eps - eps_halfwidth(qh, r.revenue_musd, etr, sh),
            eps_q90=eps + eps_halfwidth(qh, r.revenue_musd, etr, sh),
            eps_q10_ebitda_only=(ni - (qh.qhat80 if qh is not None else 0) / 100 * r.revenue_musd * (1 - etr)) / sh,
            eps_q90_ebitda_only=(ni + (qh.qhat80 if qh is not None else 0) / 100 * r.revenue_musd * (1 - etr)) / sh,
            eps_band_bridge_sd=M7_BRIDGE_EPS_SD,
            eps_band_basis="joint: EBITDA conformal qhat80 (x (1-ETR)/shares) and M7 bridge sd 0.083, in quadrature",
            cfo_musd_diagnostic=cfo_diag, cfo_wc_and_other_musd=wc_other, capex_musd=capex,
            fcf_musd_diagnostic=cfo_diag - capex,
            fcf_margin_pct_diagnostic=(cfo_diag - capex) / r.revenue_musd * 100))
    pl = pd.DataFrame(rows)
    pl.to_csv(wpath("23_forecast_quarterly.csv"), index=False)
    return pl


# --------------------------------------------------------------------- 5. annual
def build_annual(d, pl):
    tg = d["tg"].set_index("quarter")
    h1_26_rev = float(tg.loc["2026Q1", "revenue_musd"] + tg.loc["2026Q2", "revenue_musd"])
    h1_26_e = float(tg.loc["2026Q1", "adj_ebitda_musd"] + tg.loc["2026Q2", "adj_ebitda_musd"])
    H1 = ["2026Q1", "2026Q2"]
    h1_26_da = float(tg.loc[H1, "da_musd"].sum())
    h1_26_sbc = float(tg.loc[H1, "sbc_musd"].sum())
    h1_26_op = float(tg.loc[H1, "op_income_musd"].sum())
    h1_26_ii = float(tg.loc[H1, "interest_income_musd"].sum())
    h1_26_pre = float(tg.loc[H1, "pretax_income_musd"].sum())
    h1_26_tax = float(tg.loc[H1, "tax_provision_musd"].sum())
    h1_26_ni = float(tg.loc[H1, "net_income_musd"].sum())
    ann = d["ann"]
    m7a = d["m7a"]
    rows = []
    for sc in ["base", "bear", "bull"]:
        p = pl[pl.scenario == sc].set_index("quarter")
        rev26 = float(ann[(ann.period == "FY26") & (ann.scenario == sc)]["revenue_musd"].iloc[0])
        e26 = h1_26_e + float(p.loc["2026Q3", "adj_ebitda_musd"]) + float(p.loc["2026Q4", "adj_ebitda_musd"])
        q27 = [q for q in ["2027Q1", "2027Q2", "2027Q3", "2027Q4"] if q in p.index]
        rev27 = float(ann[(ann.period == "FY27") & (ann.scenario == sc)]["revenue_musd"].iloc[0])
        e27 = float(p.loc[q27, "adj_ebitda_musd"].sum())
        m27 = e27 / rev27 * 100
        a28 = ann[(ann.period == "FY28") & (ann.scenario == sc)]
        if not len(a28):
            a28 = ann[(ann.period == "FY28") & (ann.scenario == "base")]
        rev28 = float(a28["revenue_musd"].iloc[0]) if len(a28) else np.nan
        m28 = m27          # flat roll-forward, M6 R15 rule, labelled
        e28 = m28 / 100 * rev28 if np.isfinite(rev28) else np.nan
        for per, rev, e, m, basis in (
                ("FY26", rev26, e26, e26 / rev26 * 100, "1H26 actual + 3Q26 combination + 4Q26 Street"),
                ("FY27", rev27, e27, m27, "sum of the four 2027 combination quarters (SCENARIO: h>=2 fails its test)"),
                ("FY28", rev28, e28, m28, "FY27 margin rolled flat onto FY28 base revenue (M6 R15 rule); NOT a forecast")):
            sub = m7a[(m7a.period == f"FY20{per[2:]}") & (m7a.ebitda_source == "driver-lines")
                      & (m7a.scenario == sc)]
            if sub.empty:
                sub = m7a[(m7a.period == f"FY20{per[2:]}") & (m7a.ebitda_source == "driver-lines")
                          & (m7a.scenario == "base")]
            # WS31 audit 15: for the periods we actually build quarter by quarter, the
            # annual tax provision and net income are the SUM OF THE QUARTERS (1H26
            # actuals + our forecast quarters for FY26), and the annual ETR is derived
            # afterwards. FY28 has no quarterly build and keeps the rate approach, said so
            # in `ni_basis`.
            qs_per = (["2026Q3", "2026Q4"] if per == "FY26"
                      else q27 if per == "FY27" else [])
            if len(sub) and np.isfinite(e):
                s = sub.iloc[0]
                da, sbc = float(s.da_musd), float(s.sbc_musd)
                ii, ie, oi = float(s.interest_income_musd), float(s.interest_expense_musd), float(s.other_income_musd)
                sh = float(s.diluted_shares_m)
                if qs_per:
                    da = float(p.loc[qs_per, "da_musd"].sum()) + (h1_26_da if per == "FY26" else 0.0)
                    sbc = float(p.loc[qs_per, "sbc_musd"].sum()) + (h1_26_sbc if per == "FY26" else 0.0)
                    op = float(p.loc[qs_per, "op_income_musd"].sum()) + (h1_26_op if per == "FY26" else 0.0)
                    ii = float(p.loc[qs_per, "interest_income_musd"].sum()) + (h1_26_ii if per == "FY26" else 0.0)
                    pre = float(p.loc[qs_per, "pretax_income_musd"].sum()) + (h1_26_pre if per == "FY26" else 0.0)
                    tax = float(p.loc[qs_per, "tax_provision_musd"].sum()) + (h1_26_tax if per == "FY26" else 0.0)
                    ni = float(p.loc[qs_per, "net_income_musd"].sum()) + (h1_26_ni if per == "FY26" else 0.0)
                    etr = tax / pre if pre else np.nan
                    ni_basis = ("sum of quarters (1H26 actual + 3Q26/4Q26 forecast)" if per == "FY26"
                                else "sum of the four forecast quarters")
                    # CFO from the updated net income (WS31 audit 07), M7's working-capital
                    # and other block carried across
                    wc_other = float(s.cfo_musd) - (float(s.net_income_musd) + float(s.da_musd)
                                                    + float(s.sbc_musd))
                    cfo = ni + da + sbc + wc_other
                    fcf_m7 = cfo - float(s.capex_musd)
                else:
                    etr = float(s.tax_rate_pct) / 100.0
                    op = e - da - sbc
                    pre = op + ii - ie + oi
                    tax = pre * etr
                    ni = pre - tax
                    ni_basis = "annual ETR on annual pretax (no quarterly build for this period)"
                    wc_other = float(s.cfo_musd) - (float(s.net_income_musd) + float(s.da_musd)
                                                    + float(s.sbc_musd))
                    cfo = ni + da + sbc + wc_other
                    fcf_m7 = cfo - float(s.capex_musd)
                eps = ni / sh
                m7_ni = float(s.net_income_musd)
            else:
                da = sbc = ii = ie = oi = op = pre = ni = eps = fcf_m7 = np.nan
                etr = sh = tax = cfo = m7_ni = np.nan
                ni_basis = "not built"
            rows.append(dict(period=per, scenario=sc, basis=basis, revenue_musd=rev,
                             adj_ebitda_musd=e, adj_ebitda_margin_pct=m, sbc_musd=sbc, da_musd=da,
                             op_income_musd=op, op_margin_pct=op / rev * 100 if np.isfinite(op) else np.nan,
                             interest_income_musd=ii, interest_expense_musd=ie,
                             pretax_income_musd=pre, tax_provision_musd=tax,
                             tax_rate_pct=etr * 100 if np.isfinite(etr) else np.nan,
                             net_income_musd=ni, ni_basis=ni_basis,
                             m7_annual_net_income_musd=m7_ni,
                             diluted_shares_m=sh, eps_diluted=eps,
                             cfo_musd=cfo,
                             fcf_musd_range_mid=fcf_m7,
                             fcf_musd_bias_adjusted=fcf_m7 - 399.0 if np.isfinite(fcf_m7) else np.nan,
                             fcf_margin_pct=fcf_m7 / rev * 100 if np.isfinite(fcf_m7) else np.nan))
    a = pd.DataFrame(rows)
    a.to_csv(wpath("23_forecast_annual.csv"), index=False)
    return a


# --------------------------------------------------------------------- 6. consensus
def build_vs_consensus(d, pl, ann):
    c = d["cons"]
    ls = c[c.vendor == "LSEG"].set_index("period")
    bb = c[c.vendor.astype(str).str.startswith("Bloomberg")].set_index("period")
    c27 = d["cons27"].set_index("quarter")
    QMAP = {"2026Q3": "3Q26", "2026Q4": "4Q26", "2027Q1": "1Q27",
            "2027Q2": "2Q27", "2027Q3": "3Q27", "2027Q4": "4Q27"}
    base = pl[pl.scenario == "base"].set_index("quarter")
    abase = ann[ann.scenario == "base"].set_index("period")
    rows = []
    for q in QF:
        qk = QMAP[q]
        ce = float(c27.loc[qk, "ebitda_mean_musd"]) if qk in c27.index else np.nan
        cr = float(c27.loc[qk, "revenue_mean_musd"]) if qk in c27.index else np.nan
        cn = float(c27.loc[qk, "ebitda_n"]) if qk in c27.index else np.nan
        rows.append(dict(period=q, kind="quarter",
                         model_revenue_musd=float(base.loc[q, "revenue_musd"]),
                         model_ebitda_musd=float(base.loc[q, "adj_ebitda_musd"]),
                         model_margin_pct=float(base.loc[q, "adj_ebitda_margin_pct"]),
                         model_eps=float(base.loc[q, "eps_diluted_gaap"]),
                         lseg_revenue_musd=cr, lseg_ebitda_musd=ce,
                         lseg_margin_pct=ce / cr * 100 if np.isfinite(ce) and np.isfinite(cr) else np.nan,
                         lseg_n=cn,
                         # WS31 audit 14: revenue and EBITDA dispersion are separate columns.
                         # The old single `lseg_sd_musd` carried revenue sd on quarterly rows
                         # and EBITDA sd on annual rows.
                         lseg_revenue_sd_musd=float(c27.loc[qk, "revenue_sd_musd"]) if qk in c27.index else np.nan,
                         lseg_ebitda_sd_musd=(float(ls.loc[qk, "ebitda_sd"])
                                              if qk in ls.index and np.isfinite(ls.loc[qk, "ebitda_sd"])
                                              else np.nan),
                         gap_ebitda_musd=float(base.loc[q, "adj_ebitda_musd"]) - ce if np.isfinite(ce) else np.nan,
                         gap_margin_pp=float(base.loc[q, "adj_ebitda_margin_pct"]) - (ce / cr * 100) if np.isfinite(ce) and np.isfinite(cr) else np.nan))
    for per in ["FY26", "FY27", "FY28"]:
        ce = float(ls.loc[per, "ebitda_mean"]); cr = float(ls.loc[per, "revenue_mean"])
        rows.append(dict(period=per, kind="annual",
                         model_revenue_musd=float(abase.loc[per, "revenue_musd"]),
                         model_ebitda_musd=float(abase.loc[per, "adj_ebitda_musd"]),
                         model_margin_pct=float(abase.loc[per, "adj_ebitda_margin_pct"]),
                         model_eps=float(abase.loc[per, "eps_diluted"]),
                         lseg_revenue_musd=cr, lseg_ebitda_musd=ce, lseg_margin_pct=ce / cr * 100,
                         lseg_n=float(ls.loc[per, "ebitda_n"]),
                         lseg_revenue_sd_musd=float(ls.loc[per, "revenue_sd"]),
                         lseg_ebitda_sd_musd=float(ls.loc[per, "ebitda_sd"]),
                         lseg_eps=float(ls.loc[per, "eps_mean"]),
                         bloomberg_ebitda_musd=float(bb.loc[per, "ebitda_mean"]) if per in bb.index and np.isfinite(bb.loc[per, "ebitda_mean"]) else np.nan,
                         gap_ebitda_musd=float(abase.loc[per, "adj_ebitda_musd"]) - ce,
                         gap_margin_pp=float(abase.loc[per, "adj_ebitda_margin_pct"]) - ce / cr * 100,
                         gap_eps=float(abase.loc[per, "eps_diluted"]) - float(ls.loc[per, "eps_mean"])))
    v = pd.DataFrame(rows)
    v.to_csv(wpath("23_vs_consensus.csv"), index=False)
    return v


# --------------------------------------------------------------------- 7. scenarios
def build_scenarios(d, pl):
    """Revenue scenario x cost-response variant (M6): costs flex at k, or are held."""
    base = pl[pl.scenario == "base"].set_index("quarter")
    rev = d["rev"]
    rows = []
    for q in QF:
        Rb = float(base.loc[q, "revenue_musd"])
        Cb = float(base.loc[q, "total_cash_costs_musd"])
        for sc in ["bear", "base", "bull"]:
            if q not in rev.index or sc not in rev.columns or not np.isfinite(rev.loc[q, sc]):
                continue
            R = float(rev.loc[q, sc])
            dlt = R / Rb - 1.0
            for var, k in (("held", 0.0), ("flex", K_TOTAL_FLEX), ("full_flex", 1.0)):
                C = Cb * (1 + k * dlt)
                E = R - C
                rows.append(dict(quarter=q, revenue_scenario=sc, cost_response=var, k=k,
                                 revenue_musd=R, revenue_delta_pct=dlt * 100,
                                 total_cash_costs_musd=C, adj_ebitda_musd=E,
                                 adj_ebitda_margin_pct=E / R * 100,
                                 margin_vs_base_pp=E / R * 100 - float(base.loc[q, "adj_ebitda_margin_pct"])))
    s = pd.DataFrame(rows)
    s.to_csv(wpath("23_scenarios.csv"), index=False)
    return s


# --------------------------------------------------------------------- 8. cyclicality
def build_cyclicality(d, pl, lines):
    tg = d["tg"]
    h = tg[(tg.quarter >= "2022Q1") & (tg.quarter <= "2026Q2")].copy()
    h["qn"] = h.quarter.str[-1].astype(int)
    prof = h.groupby("qn").agg(
        n=("adj_ebitda_margin_pct", "size"),
        margin_mean=("adj_ebitda_margin_pct", "mean"),
        margin_sd=("adj_ebitda_margin_pct", "std"),
        rev_share=("revenue_musd", "mean"))
    prof["rev_share"] = prof["rev_share"] / prof["rev_share"].sum() * 100
    base = pl[pl.scenario == "base"].copy()
    base["qn"] = base.quarter.str[-1].astype(int)
    rows = []
    for q in QF:
        r = base[base.quarter == q].iloc[0]
        R = r.revenue_musd
        mech = (r.cor_cash_musd + r.ops_cash_musd) / R * 100
        disc = (r.pd_cash_musd + r.sm_cash_musd + r.ga_cash_musd) / R * 100
        qn = int(q[-1])
        rows.append(dict(quarter=q, quarter_of_year=qn,
                         revenue_musd=R, margin_pct=r.adj_ebitda_margin_pct,
                         mechanical_cost_pct_rev=mech, discretionary_cost_pct_rev=disc,
                         hist_margin_mean_2022_26=float(prof.loc[qn, "margin_mean"]),
                         hist_margin_sd=float(prof.loc[qn, "margin_sd"]),
                         hist_rev_share_pct=float(prof.loc[qn, "rev_share"])))
    # history rows for the same split
    for _, r in h.iterrows():
        R = r.revenue_musd
        rows.append(dict(quarter=r.quarter, quarter_of_year=int(r.qn), revenue_musd=R,
                         margin_pct=r.adj_ebitda_margin_pct,
                         mechanical_cost_pct_rev=(r.cor_cash_musd + r.ops_cash_musd) / R * 100,
                         discretionary_cost_pct_rev=(r.pd_cash_musd + r.sm_cash_musd
                                                     + r.ga_cash_ex_reserves_musd) / R * 100,
                         hist_margin_mean_2022_26=np.nan, hist_margin_sd=np.nan,
                         hist_rev_share_pct=np.nan))
    s = pd.DataFrame(rows).sort_values("quarter")
    s.to_csv(wpath("23_seasonality.csv"), index=False)

    # macro sensitivity: margin change per 1pt of revenue growth shortfall
    rows = []
    base_i = pl[pl.scenario == "base"].set_index("quarter")
    for per, qs, rev_key in (("2H26", ["2026Q3", "2026Q4"], None),
                             ("FY26", ["2026Q3", "2026Q4"], "FY26"),
                             ("FY27", ["2027Q1", "2027Q2", "2027Q3", "2027Q4"], "FY27")):
        Rb = float(base_i.loc[qs, "revenue_musd"].sum())
        Cb = float(base_i.loc[qs, "total_cash_costs_musd"].sum())
        Eb = Rb - Cb
        h1e = 0.0
        h1r = 0.0
        if rev_key == "FY26":
            tgi = d["tg"].set_index("quarter")
            h1e = float(tgi.loc["2026Q1", "adj_ebitda_musd"] + tgi.loc["2026Q2", "adj_ebitda_musd"])
            h1r = float(tgi.loc["2026Q1", "revenue_musd"] + tgi.loc["2026Q2", "revenue_musd"])
        for var, k in (("held", 0.0), ("flex", K_TOTAL_FLEX), ("full_flex", 1.0)):
            for shock in [-3, -2, -1, 1, 2]:
                R = Rb * (1 + shock / 100)
                C = Cb * (1 + k * shock / 100)
                E = R - C
                m0 = (Eb + h1e) / (Rb + h1r) * 100
                m1 = (E + h1e) / (R + h1r) * 100
                rows.append(dict(period=per, cost_response=var, k=k,
                                 revenue_shock_pct=shock,
                                 margin_base_pct=m0, margin_shocked_pct=m1,
                                 margin_delta_pp=m1 - m0,
                                 pp_per_1pct_revenue=(m1 - m0) / shock))
    ms = pd.DataFrame(rows)
    ms.to_csv(wpath("23_macro_sensitivity.csv"), index=False)

    # FY26 floor break-even
    tgi = d["tg"].set_index("quarter")
    h1e = float(tgi.loc["2026Q1", "adj_ebitda_musd"] + tgi.loc["2026Q2", "adj_ebitda_musd"])
    h1r = float(tgi.loc["2026Q1", "revenue_musd"] + tgi.loc["2026Q2", "revenue_musd"])
    Rb = float(base_i.loc[["2026Q3", "2026Q4"], "revenue_musd"].sum())
    Cb = float(base_i.loc[["2026Q3", "2026Q4"], "total_cash_costs_musd"].sum())
    rows = []
    for var, k in (("held", 0.0), ("flex", K_TOTAL_FLEX), ("full_flex", 1.0)):
        lo, hi = -25.0, 5.0
        for _ in range(200):
            mid = (lo + hi) / 2
            R = Rb * (1 + mid / 100); C = Cb * (1 + k * mid / 100)
            m = (h1e + R - C) / (h1r + R) * 100
            if m > FY26_FLOOR:
                hi = mid
            else:
                lo = mid
        rows.append(dict(cost_response=var, k=k, floor_pct=FY26_FLOOR,
                         fy26_margin_base_pct=(h1e + Rb - Cb) / (h1r + Rb) * 100,
                         cushion_pp=(h1e + Rb - Cb) / (h1r + Rb) * 100 - FY26_FLOOR,
                         breakeven_2h26_shortfall_pct=-mid,
                         breakeven_2h26_shortfall_musd=-mid / 100 * Rb))
    fb = pd.DataFrame(rows)
    fb.to_csv(wpath("23_fy26_floor_breakeven.csv"), index=False)
    return s, ms, fb


# --------------------------------------------------------------------- 9. the card
def build_card(d, path, pl, ann, bands, fb):
    base = pl[pl.scenario == "base"].set_index("quarter")
    ab = ann[ann.scenario == "base"].set_index("period")
    bm = bands[(bands.target == "adj_ebitda_margin_pct") & (bands.horizon_q == 0)].set_index("calibration")
    bu = bands[(bands.target == "adj_ebitda_musd") & (bands.horizon_q == 0)].set_index("calibration")
    tgi_card = d["tg"].set_index("quarter")
    h1e_card = float(tgi_card.loc["2026Q1", "adj_ebitda_musd"] + tgi_card.loc["2026Q2", "adj_ebitda_musd"])
    q3m = float(base.loc["2026Q3", "adj_ebitda_margin_pct"])
    q3e = float(base.loc["2026Q3", "adj_ebitda_musd"])
    q3r = float(base.loc["2026Q3", "revenue_musd"])
    # WS31 audit 04: the dollar band AND P(beat) both come from the ADOPTED dollar
    # construction (`final-margin|combined_dollar_from_margin` = the margin combination x
    # revenue), calibrated on its own PIT errors. The four-member dollar combination is a
    # labelled cross-check only. The old 0.77 (a band from one object, an sd from another)
    # is retired.
    bd = bands[(bands.target == "adj_ebitda_musd_from_margin") & (bands.horizon_q == 0)] \
        .set_index("calibration")
    st_e, st_m, st_eps = 2361.52179, 49.775747, 2.84539
    qh80 = float(bm.loc["recent_2024Q1plus", "qhat80"])
    qh80_14 = float(bm.loc["W1_all_n14", "qhat80"])
    bias5 = float(bm.loc["W1_all_n14", "bias_last5"])
    sd = qh80 / 1.2816
    from scipy.stats import norm
    p_beat_m = 1 - norm.cdf((st_m - q3m) / sd)
    qh80_e = float(bd.loc["recent_2024Q1plus", "qhat80"])
    sd_e = qh80_e / 1.2816
    p_beat_e = 1 - norm.cdf((st_e - q3e) / sd_e)
    q3e_dollar_object = float(d["live"][(d["live"].spec_id == "stack_clip")
                                        & (d["live"].target == "adj_ebitda_musd")
                                        & (d["live"].quarter == "2026Q3")]["point"].iloc[0])
    rows = [
        dict(item="3Q26 adj EBITDA margin", value=q3m, unit="%",
             band80=f"{q3m - qh80:.2f} - {q3m + qh80:.2f}", vs="Street 49.78%",
             note="combination stack_clip, h=0; bias-corrected on the last 5 PIT errors -> "
                  f"{q3m - bias5:.2f}%, which the 'down slightly' sentence caps at {Q3_25_MARGIN:.2f}%"),
        dict(item="3Q26 adj EBITDA", value=q3e, unit="USD m",
             band80=f"{q3e - qh80_e:.0f} - {q3e + qh80_e:.0f}",
             vs=f"Street {st_e:.0f} (n 36, EBITDA sd 20.0)",
             note=("final-margin|combined_dollar_from_margin (the margin combination x bridge-v3 "
                   f"revenue 4,804), band = its OWN conformal qhat80 {qh80_e:.1f} on the 2024Q1+ "
                   f"calibration; W1/W2 h=0 MAE 30.7 / 25.8. Cross-check: the four-member dollar "
                   f"combination reads {q3e_dollar_object:.0f}")),
        dict(item="3Q26 beat vs Street, $", value=q3e - st_e, unit="USD m", band80="",
             vs="", note="M5 flow-through arithmetic: 0.464 x (4,804 - 4,744) + 16 = +$44M"),
        dict(item="P(3Q26 adj EBITDA beats Street)", value=p_beat_e, unit="probability", band80="",
             vs="", note=(f"Gaussian, sd = qhat80/1.2816 = {sd_e:.1f}, on the SAME object as the "
                          "band (WS31 audit 04). The previously published 0.77 mixed a band from "
                          "the margin route with an sd from the four-member dollar object and is "
                          "withdrawn. Descriptive, not a validated probability: the calibration "
                          "pool is n=10 and the object was selected after seeing the scoreboard")),
        dict(item="P(3Q26 margin beats Street margin)", value=p_beat_m, unit="probability",
             band80="", vs="", note="Gaussian on the margin object's own conformal sd; same caveat"),
        dict(item="3Q26 EPS (GAAP diluted)", value=float(base.loc["2026Q3", "eps_diluted_gaap"]),
             unit="USD", band80=f"{float(base.loc['2026Q3', 'eps_q10']):.2f} - {float(base.loc['2026Q3', 'eps_q90']):.2f}",
             vs=f"Street {st_eps:.2f}",
             note=("M7 bridge, ETR 18.0%, 591.7m shares; $0.001386 of EPS per $M of EBITDA. "
                   "Band is JOINT (WS31 audit 06): EBITDA conformal term and M7's measured "
                   "bridge sd $0.083 in quadrature, not EBITDA-only")),
        dict(item="4Q26 adj EBITDA margin", value=float(base.loc["2026Q4", "adj_ebitda_margin_pct"]),
             unit="%", band80="", vs="Street 28.90%",
             note="h=1 rule: the Street is unbeaten; combination 29.04%, M3 sentence path 29.90%"),
        dict(item="FY26 adj EBITDA margin", value=float(ab.loc["FY26", "adj_ebitda_margin_pct"]),
             unit="%", band80="", vs=f"floor {FY26_FLOOR}%, Street 35.62%",
             note="1H26 actual + 3Q26 combination + 4Q26 Street, on bridge v3 revenue"),
        dict(item="FY26 adj EBITDA", value=float(ab.loc["FY26", "adj_ebitda_musd"]), unit="USD m",
             band80="", vs="Street 5,053.7", note=""),
        dict(item="5 Nov FY26 margin sentence (forecast)", value=NOV_SENTENCE_FY26, unit="%",
             band80="", vs="", note="M3: the November sentence has been the numeric floor + 50bp, exact 2 of 2; "
                                    "p ~0.45-0.50. 'Approximately 36%'"),
        dict(item="4Q26 margin implied by the 36.0% sentence at our 3Q26",
             value=(NOV_SENTENCE_FY26 / 100 * float(ab.loc["FY26", "revenue_musd"]) - h1e_card
                    - q3m / 100 * q3r) / float(base.loc["2026Q4", "revenue_musd"]) * 100,
             unit="%", band80="", vs="Street 28.90%",
             note="M3 budget identity: 1pp of FY26 = 4.49pp of 4Q26; 1pp of 3Q26 = -1.51pp of 4Q26"),
        dict(item="FY27 adj EBITDA margin (SCENARIO)", value=float(ab.loc["FY27", "adj_ebitda_margin_pct"]),
             unit="%", band80="", vs="Street 36.45%",
             note="h>=2 fails its test; this is a spending scenario, not a forecast"),
    ]
    card = pd.DataFrame(rows)
    card.to_csv(wpath("23_card_5nov.csv"), index=False)

    # budget identity: 1pp of Q3 = -X pp of Q4 at a given FY sentence
    tgi = d["tg"].set_index("quarter")
    h1e = float(tgi.loc["2026Q1", "adj_ebitda_musd"] + tgi.loc["2026Q2", "adj_ebitda_musd"])
    R26 = float(ab.loc["FY26", "revenue_musd"])
    R4 = float(base.loc["2026Q4", "revenue_musd"])
    rows = []
    for fy in [35.5, 35.75, 36.0, 36.25, 36.5]:
        for q3 in [49.4, 49.94, 50.085, 50.5]:
            E = fy / 100 * R26
            resid = E - h1e - q3 / 100 * q3r
            # WS31 audit 12: a FLOOR sentence ("at least X") makes the implied 4Q26 margin a
            # LOWER BOUND, not a point forecast. Only a "point"/"approximately" sentence
            # makes it an equality.
            kind = "lower bound on 4Q26 (the FY sentence is a floor)" if fy == FY26_FLOOR \
                else "equality if the FY sentence is a point/'approximately' statement"
            rows.append(dict(fy26_sentence_pct=fy, q3_margin_pct=q3, fy26_ebitda_musd=E,
                             q3_ebitda_musd=q3 / 100 * q3r, q4_ebitda_musd=resid,
                             q4_margin_pct=resid / R4 * 100,
                             q4_margin_reading=kind,
                             pp_of_q4_per_1pp_of_q3=-q3r / R4,
                             pp_of_q4_per_1pp_of_fy=R26 / R4))
    bi = pd.DataFrame(rows)
    bi.to_csv(wpath("23_card_budget_identity.csv"), index=False)
    return card, bi


def main():
    d = load()
    path = build_path(d)
    bands = build_bands(d)
    lines = build_lines(d, path)
    pl = build_pl(d, path, lines)
    ann = build_annual(d, pl)
    v = build_vs_consensus(d, pl, ann)
    sc = build_scenarios(d, pl)
    seas, ms, fb = build_cyclicality(d, pl, lines)
    card, bi = build_card(d, path, pl, ann, bands, fb)

    pd.set_option("display.width", 240)
    print("\n--- adopted path ---")
    print(path[["quarter", "margin_pct", "combination_pct", "street_pct", "m3_sentence_pct", "clip", "source"]].to_string(index=False))
    print("\n--- quarterly P&L (base) ---")
    print(pl[pl.scenario == "base"][["quarter", "revenue_musd", "adj_ebitda_musd",
                                     "adj_ebitda_margin_pct", "margin_q10", "margin_q90",
                                     "op_income_musd", "net_income_musd", "eps_diluted_gaap"]].round(2).to_string(index=False))
    print("\n--- annual ---")
    print(ann[["period", "scenario", "revenue_musd", "adj_ebitda_musd", "adj_ebitda_margin_pct",
               "eps_diluted", "fcf_musd_range_mid"]].round(2).to_string(index=False))
    print("\n--- vs consensus ---")
    print(v[["period", "model_ebitda_musd", "lseg_ebitda_musd", "gap_ebitda_musd",
             "model_margin_pct", "lseg_margin_pct", "gap_margin_pp"]].round(2).to_string(index=False))
    print("\n--- floor break-even ---")
    print(fb.round(3).to_string(index=False))
    print("\n--- card ---")
    print(card.to_string(index=False))


if __name__ == "__main__":
    main()
