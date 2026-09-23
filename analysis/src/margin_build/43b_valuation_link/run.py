"""43b. How the cost leg (thesis point 3) enters the target price, in dollars per share.

Run from the repo root:  py -3.13 -X utf8 analysis/src/margin_build/43b_valuation_link/run.py
Exit code 0. Writes data/processed/margin_build/43b_valuation_link/*.csv. Reads only; changes nothing else.

Five blocks:
  1. trace      - where $143 / $148 / $150 / $125 come from (the reverse-DCF joint solve, workstream A) and what
                  multiple each pays on the Street's, the official v2's and the 40 short case's FY27 EBITDA.
  2. bridge     - downside from spot to the official v2 case decomposed into (a) revenue below the Street with
                  costs flexing at M6's elasticity, (b) costs not flexing, (c) costs above the Street's path (41),
                  (d) multiple compression on DEC-0014's slope. Consistent EV / FY27 adj. EBITDA basis, spot convention.
  3. montecarlo - FY27 margin = 1 - costs / revenue with costs drawn from a cost-growth distribution anchored on 41
                  and only weakly responsive to revenue (M6); multiple linked to growth on DEC-0014's slope and CI.
                  Jessie's 7 Sep MC (07_scenarios_montecarlo.R) replicated and re-scored at today's spot.
  4. reverse dcf- the constant FY27+ margin today's price implies at Street growth on the repo's fade_dcf.
  5. scenarios  - scenario -> FY27 EBITDA -> EV/EBITDA -> $/share table for the memo.

Every anchor is a repo number with its file named in ANCHORS below. Nothing is fitted here.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta as beta_dist
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT / "data" / "processed" / "margin_build" / "43b_valuation_link"
OUT.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------------------------------------------------
# ANCHORS (all read from repo files; the file is named on each line)
# ----------------------------------------------------------------------------------------------------------------------
SPOT = 166.84            # close 21 Sep 2026 (task brief; DEC-0015 leaves the memo's $167.51 of 16 Sep provisional)
SPOT_MEMO = 167.51       # memo v3 / DEC-0015
SHARES = 597.0           # 2Q26 diluted, spot convention (reverse_dcf/market/market_implied_params.json)
NET_CASH = 9593.0        # 2Q26 net cash ex float, $m (same file)
A_INTERCEPT, A_SLOPE = 12.533, 0.3955   # joint solve spec A: EV/NTM EBITDA = a + b x NTM growth % (A_joint_solve.csv)
LTM_REV, LTM_MARGIN = 13159.0, 0.350862527547686   # joint-solve base (market_implied_params.json)
NTM_TO_FY27_SPREAD = 1.421                          # proportional mapping: FY27 growth = NTM growth - spread (same file)

# DEC-0014 (docs/pitch-model-v2/DECISIONS.md; dossier V2_v2_multiple.md): 16.5x at the 5 Sep base growth 12.269%,
# slope +0.4860 turns per point of FY27 revenue growth, HAC 95% CI [0.3172, 0.6548], n 35, descriptive.
DEC14_MID, DEC14_G0 = 16.5, 12.269
DEC14_SLOPE, DEC14_CI = 0.4860, (0.3172, 0.6548)
DEC14_SLOPE_SE = (DEC14_CI[1] - DEC14_CI[0]) / (2 * 1.96)

# Street, LSEG 11 Sep 2026 pull, n 44 (data/processed/margin_build/03_consensus_pit/03_current_consensus.csv)
STREET = dict(fy26_rev=14189.55705, fy26_ebitda=5053.72214, fy27_rev=15819.33924, fy27_ebitda=5766.09917,
              fy28_rev=17535.09557, fy28_ebitda=6602.71735)
STREET["fy26_costs"] = STREET["fy26_rev"] - STREET["fy26_ebitda"]
STREET["fy27_costs"] = STREET["fy27_rev"] - STREET["fy27_ebitda"]
STREET["fy27_growth"] = 100 * (STREET["fy27_rev"] / STREET["fy26_rev"] - 1)
STREET["fy27_cost_growth"] = 100 * (STREET["fy27_costs"] / STREET["fy26_costs"] - 1)
STREET["fy28_growth"] = 100 * (STREET["fy28_rev"] / STREET["fy27_rev"] - 1)

# Official v2 income statement (docs/pitch-model-v2/lines/final_income_statement.md; model/ABNB_official_model_complete.xlsx)
OFFICIAL = dict(fy26_rev=14117.72, fy26_ebitda=4948.09, fy27_rev=15424.73, fy27_ebitda=5240.32)
OFFICIAL["fy26_costs"] = OFFICIAL["fy26_rev"] - OFFICIAL["fy26_ebitda"]
OFFICIAL["fy27_costs"] = OFFICIAL["fy27_rev"] - OFFICIAL["fy27_ebitda"]
OFFICIAL["fy27_growth"] = 100 * (OFFICIAL["fy27_rev"] / OFFICIAL["fy26_rev"] - 1)
OFFICIAL["fy27_cost_growth"] = 100 * (OFFICIAL["fy27_costs"] / OFFICIAL["fy26_costs"] - 1)
OFFICIAL["flex_memo_fy27"] = 80.2 + 68.1 + 78.3 + 28.5   # workbook memo rows 43-44: EBITDA if costs flexed to hold the line build's margin

# 40_line_build (data/processed/margin_build/40_line_build/40_annual.csv, 40_short_case_summary.csv)
LB = dict(base_fy27_rev=15828.6066, base_fy27_ebitda=5644.204235, base_fy26_rev=14268.1433, base_fy26_ebitda=5098.514141,
          rev_bear_fy26=14164.807, rev_bear_fy27=14948.3339, rev_bull_fy26=14391.9366, rev_bull_fy27=16570.7436,
          short_fy27_rev=14913.511524, short_fy27_ebitda=4761.435390, short_fy26_rev=13932.767674)
LB["rev_bear_growth"] = 100 * (LB["rev_bear_fy27"] / LB["rev_bear_fy26"] - 1)
LB["rev_bull_growth"] = 100 * (LB["rev_bull_fy27"] / LB["rev_bull_fy26"] - 1)
LB["short_growth"] = 100 * (LB["short_fy27_rev"] / LB["short_fy26_rev"] - 1)

# 41_cost_leg (data/processed/margin_build/41_cost_leg/41_fy27_scenarios.csv, 41_annual_cost_growth.csv)
COST_PATHS = {"Street (+10.0%)": 10.041831633754871, "Street + recent surprise (+11.0%)": 11.032680493461555,
              "Line build base (+11.1%)": 11.06667661770766, "FY24-25 average (+12.6%)": 12.61440511195724,
              "FY26E Street repeated (+15.0%)": 15.002957074521639}
STREET_FY28_COST_GROWTH = 8.7    # 41 note, annual table: the lowest cost growth anywhere on the tape

# M6_cycle_flex (data/processed/margin_build/M6_cycle_flex/M6_cycle_flex_k_table.csv, sample 1Q22+, rw)
K_TOTAL, K_TOTAL_T = 0.3641734264213614, 6.575391625417262     # total cash costs, lag0, n 18
K_TOTAL_SE = K_TOTAL / K_TOTAL_T
K_UP_TOTAL, K_DN_TOTAL, K_DN_P = 0.5813290527719499, -0.2601897058508933, 0.08236314452460172   # asym_up_dn, n 16
K_UP_SM, K_DN_SM = 1.8250939390945706, -0.12061750992951237

# Delivered-case FCF conversion for the reverse DCF (reverse_dcf/A_common.py: FCF_TO_EBITDA_FY27 = 1.024; SBC $1,935.7m)
FCF_TO_EBITDA = 5940.573 / 5800.957
SBC_FY27 = 1935.731

# Jessie's MC inputs (origin/jessie/r-stats analysis/r_stats/R/07_scenarios_montecarlo.R; 00_setup.R SPOT 181.94)
JESSIE_SPOT = 181.94
JESSIE_MULT = (13.5, 16.5, 18.5)
JESSIE_SEED, JESSIE_N, JESSIE_RHO = 2026, 20000, 0.5

N_DRAWS, SEED = 20000, 2026
SEED_CHECK = 20260922


def ev_at(price: float) -> float:
    return price * SHARES - NET_CASH


def price_from(ebitda: np.ndarray | float, mult: np.ndarray | float) -> np.ndarray | float:
    return (ebitda * mult + NET_CASH) / SHARES


def joint_solve_growth(price: float) -> float:
    """NTM growth g (%) such that (a + b g) x LTM_REV x (1 + g/100) x LTM_MARGIN = EV(price). Spec A, root in range."""
    ev = ev_at(price)
    # (a + b g)(1 + g/100) K = ev, K = LTM_REV x LTM_MARGIN  ->  (b/100) g^2 + (a/100 + b) g + (a - ev/K) = 0
    K = LTM_REV * LTM_MARGIN
    qa, qb, qc = A_SLOPE / 100, A_INTERCEPT / 100 + A_SLOPE, A_INTERCEPT - ev / K
    disc = qb * qb - 4 * qa * qc
    return (-qb + np.sqrt(disc)) / (2 * qa)


def joint_solve_price(g_ntm: float) -> float:
    mult = A_INTERCEPT + A_SLOPE * g_ntm
    return price_from(LTM_REV * (1 + g_ntm / 100) * LTM_MARGIN, mult)


def pert(u: np.ndarray, lo: float, mode: float, hi: float) -> np.ndarray:
    if hi <= lo:
        return np.full_like(np.asarray(u, dtype=float), mode)
    a = 1 + 4 * (mode - lo) / (hi - lo)
    b = 1 + 4 * (hi - mode) / (hi - lo)
    return lo + (hi - lo) * beta_dist.ppf(u, a, b)


def fade_dcf(fcf27, g0, wacc=0.10, tg=0.03, years=10):
    """Copied verbatim in form from analysis/src/reverse_dcf/A_common.py (PV as of 30 Sep 2026, mid-year, 10-year fade)."""
    pv, f = 0.0, fcf27
    for y in range(1, years + 1):
        if y > 1:
            g = g0 + (tg - g0) * (y - 2) / (years - 2)
            f = f * (1 + g)
        pv += f / (1 + wacc) ** (y - 0.25)
    tv = f * (1 + tg) / (wacc - tg)
    pv += tv / (1 + wacc) ** (years - 0.25)
    return pv


def bisect(fn, target, lo, hi, iters=100):
    for _ in range(iters):
        mid = (lo + hi) / 2
        if fn(mid) < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def summarise(price: np.ndarray, extra: dict | None = None) -> dict:
    q = np.quantile(price, [0.05, 0.25, 0.5, 0.75, 0.95])
    d = dict(n=len(price), mean=price.mean(), p5=q[0], p25=q[1], median=q[2], p75=q[3], p95=q[4],
             p_below_spot=float((price < SPOT).mean()), p_below_143=float((price < 143).mean()),
             p_below_150=float((price < 150).mean()), p_above_spot=float((price > SPOT).mean()),
             p_above_jessie_spot=float((price > JESSIE_SPOT).mean()),
             median_vs_spot_pct=100 * (q[2] / SPOT - 1))
    if extra:
        d.update(extra)
    return d


# ======================================================================================================================
# 1. TRACE: where the targets come from
# ======================================================================================================================
def block_trace() -> pd.DataFrame:
    rows = []
    mult_spot_street = ev_at(SPOT) / STREET["fy27_ebitda"]
    for price, label in [(SPOT, "spot 21 Sep 2026"), (SPOT_MEMO, "memo v3 spot 16 Sep"), (170.19, "A's price, 11 Sep"),
                         (150.0, "memo: base range top / bear tape"), (148.0, "memo: probability-weighted target"),
                         (143.0, "memo: base target"), (138.0, "memo: base range bottom"), (125.0, "memo: short case"),
                         (121.0, "memo: team bear low at 16.5x"), (137.0, "memo: team bear high at 16.5x")]:
        g = joint_solve_growth(price)
        ev = ev_at(price)
        rows.append(dict(price=price, label=label, ev_musd=ev,
                         joint_solve_ntm_growth_pct=g, joint_solve_ev_ntm_ebitda_x=A_INTERCEPT + A_SLOPE * g,
                         joint_solve_ntm_ebitda_musd=LTM_REV * (1 + g / 100) * LTM_MARGIN,
                         fy27_growth_proportional_pct=g - NTM_TO_FY27_SPREAD,
                         margin_in_solve_pct=100 * LTM_MARGIN,
                         ev_to_street_fy27_ebitda_x=ev / STREET["fy27_ebitda"],
                         ev_to_official_v2_fy27_ebitda_x=ev / OFFICIAL["fy27_ebitda"],
                         ev_to_short_case_fy27_ebitda_x=ev / LB["short_fy27_ebitda"],
                         ev_to_history_cost_fy27_ebitda_x=ev / (OFFICIAL["fy27_rev"] - STREET["fy26_costs"] * (1 + COST_PATHS["FY24-25 average (+12.6%)"] / 100)),
                         dec14_multiple_at_official_growth_x=DEC14_MID + DEC14_SLOPE * (OFFICIAL["fy27_growth"] - DEC14_G0),
                         price_official_ebitda_at_dec14_literal=price_from(OFFICIAL["fy27_ebitda"], DEC14_MID + DEC14_SLOPE * (OFFICIAL["fy27_growth"] - DEC14_G0)),
                         price_official_ebitda_at_spot_anchored=price_from(OFFICIAL["fy27_ebitda"], mult_spot_street + DEC14_SLOPE * (OFFICIAL["fy27_growth"] - STREET["fy27_growth"]))))
    df = pd.DataFrame(rows)
    # what growth the memo's stated numbers reproduce
    checks = pd.DataFrame([
        dict(check="joint solve at 7.0% NTM", price=joint_solve_price(7.0)),
        dict(check="joint solve at 7.5% NTM (memo says ~$143)", price=joint_solve_price(7.5)),
        dict(check="joint solve at 8.6% NTM (memo says $150)", price=joint_solve_price(8.6)),
        dict(check="joint solve at 12.9% NTM (A: $170.19)", price=joint_solve_price(12.93)),
        dict(check="official v2 EBITDA x DEC-0014 literal multiple", price=df.loc[df.price == SPOT, "price_official_ebitda_at_dec14_literal"].iloc[0]),
        dict(check="official v2 EBITDA x spot-anchored DEC-0014 multiple", price=df.loc[df.price == SPOT, "price_official_ebitda_at_spot_anchored"].iloc[0]),
        dict(check="official v2 EBITDA x 16.5x (fixed mid)", price=price_from(OFFICIAL["fy27_ebitda"], 16.5)),
        dict(check="short case EBITDA (40) x 16.5x", price=price_from(LB["short_fy27_ebitda"], 16.5)),
        dict(check="short case EBITDA (40) x 13.5x (bear)", price=price_from(LB["short_fy27_ebitda"], 13.5)),
        dict(check="short case EBITDA x spot-anchored DEC-0014 at short growth", price=price_from(LB["short_fy27_ebitda"], mult_spot_street + DEC14_SLOPE * (LB["short_growth"] - STREET["fy27_growth"]))),
        dict(check="Street FY27 EBITDA x DEC-0014 literal at Street growth", price=price_from(STREET["fy27_ebitda"], DEC14_MID + DEC14_SLOPE * (STREET["fy27_growth"] - DEC14_G0))),
        dict(check="Street FY27 EBITDA x 16.5x", price=price_from(STREET["fy27_ebitda"], 16.5)),
    ])
    df.to_csv(OUT / "43b_target_trace.csv", index=False)
    checks.to_csv(OUT / "43b_target_checks.csv", index=False)
    return df, checks


# ======================================================================================================================
# 2. BRIDGE: spot -> target decomposed
# ======================================================================================================================
def bridge(cost_path_label: str, flex_mode: str, slope: float, rev27: float, rev_label: str) -> tuple[pd.DataFrame, dict]:
    """Sequential bridge on EV / FY27 adj. EBITDA, spot convention.
    flex_mode: 'm6'  -> costs flex to revenue with k = K_TOTAL (cost growth moves k x the revenue-growth gap)
               'full'-> costs flex to hold the Street's FY27 margin (the workbook's memo-row convention)
    """
    mult_spot = ev_at(SPOT) / STREET["fy27_ebitda"]           # what the market pays for the Street's FY27, today
    g_street = STREET["fy27_growth"]
    g_ours = 100 * (rev27 / OFFICIAL["fy26_rev"] - 1)         # growth on the official FY26 base
    d_rev_pct = 100 * (rev27 / STREET["fy27_rev"] - 1)
    c_street = STREET["fy27_costs"]
    if flex_mode == "m6":
        d_cost_flex = K_TOTAL * (d_rev_pct / 100) * c_street   # cost dollars that would follow revenue at k
    else:
        d_cost_flex = d_rev_pct / 100 * c_street               # costs fall pro rata (margin held)
    cost_growth = COST_PATHS[cost_path_label]
    # 41's growth rates applied to the official v2 FY26 cost base ($9,170m; the Street's is $9,136m, 41's FY26 gap +$34m),
    # so the line-build path reproduces the official v2 FY27 costs ($10,184m) exactly and step (c) includes the FY26 base gap
    c_path = OFFICIAL["fy26_costs"] * (1 + cost_growth / 100)
    steps = []
    e0 = STREET["fy27_ebitda"]
    p0 = price_from(e0, mult_spot)
    steps.append(dict(step="0 Street FY27 at the multiple the price pays today", ebitda=e0, multiple=mult_spot, price=p0, d_price=0.0))
    e1 = e0 + (rev27 - STREET["fy27_rev"]) - d_cost_flex       # (a) revenue shortfall with costs flexing
    p1 = price_from(e1, mult_spot)
    steps.append(dict(step="(a) revenue below the Street, costs flexing", ebitda=e1, multiple=mult_spot, price=p1, d_price=p1 - p0))
    e2 = e1 + d_cost_flex                                      # (b) they do not flex (DEC-0022 / thesis 3 mechanism)
    p2 = price_from(e2, mult_spot)
    steps.append(dict(step="(b) costs do not flex with revenue", ebitda=e2, multiple=mult_spot, price=p2, d_price=p2 - p1))
    e3 = rev27 - c_path                                        # (c) the cost path itself above the Street
    p3 = price_from(e3, mult_spot)
    steps.append(dict(step=f"(c) costs above the Street: {cost_path_label}", ebitda=e3, multiple=mult_spot, price=p3, d_price=p3 - p2))
    m4 = mult_spot + slope * (g_ours - g_street)               # (d) multiple on DEC-0014's slope, spot-anchored
    p4 = price_from(e3, m4)
    steps.append(dict(step="(d) multiple compression, DEC-0014 slope x growth gap", ebitda=e3, multiple=m4, price=p4, d_price=p4 - p3))
    df = pd.DataFrame(steps)
    df.insert(0, "revenue_case", rev_label)
    df.insert(1, "cost_path", cost_path_label)
    df.insert(2, "flex_mode", flex_mode)
    df.insert(3, "slope", slope)
    df["margin_pct"] = 100 * df["ebitda"] / rev27
    df.loc[0, "margin_pct"] = 100 * e0 / STREET["fy27_rev"]
    total = p4 - p0
    thesis3 = (p2 - p1) + (p3 - p2)
    summ = dict(revenue_case=rev_label, cost_path=cost_path_label, flex_mode=flex_mode, slope=slope, fy27_revenue=rev27,
                fy27_growth_pct=g_ours, rev_gap_vs_street_pct=d_rev_pct, cost_growth_pct=cost_growth,
                fy27_ebitda=e3, fy27_margin_pct=100 * e3 / rev27, multiple_x=m4, target=p4, downside_total=total,
                a_revenue=p1 - p0, b_no_flex=p2 - p1, c_cost_path=p3 - p2, d_multiple=p4 - p3,
                thesis3_b_plus_c=thesis3, thesis3_share_pct=100 * thesis3 / total if total != 0 else np.nan,
                mult_spot_street_x=mult_spot)
    return df, summ


def block_bridge() -> tuple[pd.DataFrame, pd.DataFrame]:
    dfs, summs = [], []
    rev_cases = [(OFFICIAL["fy27_rev"], "official v2 ($15,425m)"), (LB["short_fy27_rev"], "40 short case ($14,914m)"),
                 (LB["rev_bear_fy27"], "40 rev_bear ($14,948m)")]
    for rev27, rev_label in rev_cases:
        for cp in ["Street (+10.0%)", "Line build base (+11.1%)", "FY24-25 average (+12.6%)", "FY26E Street repeated (+15.0%)"]:
            for fm in ["m6", "full"]:
                for slope in [DEC14_SLOPE, DEC14_CI[0], DEC14_CI[1]]:
                    df, s = bridge(cp, fm, slope, rev27, rev_label)
                    dfs.append(df)
                    summs.append(s)
    steps = pd.concat(dfs, ignore_index=True)
    summary = pd.DataFrame(summs)
    steps.to_csv(OUT / "43b_bridge_steps.csv", index=False)
    summary.to_csv(OUT / "43b_bridge_summary.csv", index=False)
    return steps, summary


# ======================================================================================================================
# 3. MONTE CARLO
# ======================================================================================================================
def mc_corrected(seed: int, n: int, cost_lo: float, cost_mode: float, cost_hi: float, k_mode: str = "sym",
                 mult_anchor: str = "spot", mult_noise_sd: float = 0.0, growth=(None, None, None), base: str = "official") -> tuple[np.ndarray, dict]:
    rng = np.random.default_rng(seed)
    base_rev26, base_costs26 = (OFFICIAL["fy26_rev"], OFFICIAL["fy26_costs"]) if base == "official" else (STREET["fy26_rev"], STREET["fy26_costs"])
    g_lo = growth[0] if growth[0] is not None else LB["rev_bear_growth"]
    g_mode = growth[1] if growth[1] is not None else OFFICIAL["fy27_growth"]
    g_hi = growth[2] if growth[2] is not None else LB["rev_bull_growth"]
    g = pert(rng.uniform(size=n), g_lo, g_mode, g_hi)                     # FY27 revenue growth, %
    c = pert(rng.uniform(size=n), cost_lo, cost_mode, cost_hi)            # FY27 cost growth at base revenue growth, %
    if k_mode == "sym":
        k = rng.normal(K_TOTAL, K_TOTAL_SE, size=n)
    elif k_mode == "asym":
        # M6 asym_up_dn: k_up 0.58; k_dn -0.26 (p 0.08) clipped at 0 = costs do not come down when revenue slows
        k = np.where(g >= g_mode, K_UP_TOTAL, max(K_DN_TOTAL, 0.0))
    elif k_mode == "zero":
        k = np.zeros(n)
    elif k_mode == "one":
        k = np.ones(n)
    else:
        raise ValueError(k_mode)
    cost_growth = c + k * (g - g_mode)
    rev27 = base_rev26 * (1 + g / 100)
    costs27 = base_costs26 * (1 + cost_growth / 100)
    ebitda27 = rev27 - costs27
    margin = 100 * ebitda27 / rev27
    b = rng.normal(DEC14_SLOPE, DEC14_SLOPE_SE, size=n)
    if mult_anchor == "spot":
        m0, g0 = ev_at(SPOT) / STREET["fy27_ebitda"], STREET["fy27_growth"]
    elif mult_anchor == "dec14":
        m0, g0 = DEC14_MID, DEC14_G0
    else:
        raise ValueError(mult_anchor)
    mult = m0 + b * (g - g0)
    if mult_noise_sd > 0:
        mult = mult + rng.normal(0, mult_noise_sd, size=n)
    mult = np.clip(mult, 6.0, None)
    price = price_from(ebitda27, mult)
    marg = dict(median_growth=float(np.median(g)), median_cost_growth=float(np.median(cost_growth)),
                median_margin=float(np.median(margin)), p5_margin=float(np.quantile(margin, 0.05)),
                p95_margin=float(np.quantile(margin, 0.95)), median_ebitda=float(np.median(ebitda27)),
                median_multiple=float(np.median(mult)), p_margin_below_street=float((margin < 100 * STREET["fy27_ebitda"] / STREET["fy27_rev"]).mean()),
                p_cost_growth_above_street=float((cost_growth > STREET["fy27_cost_growth"]).mean()),
                corr_growth_costgrowth=float(np.corrcoef(g, cost_growth)[0, 1]), corr_growth_multiple=float(np.corrcoef(g, mult)[0, 1]),
                corr_margin_price=float(np.corrcoef(margin, price)[0, 1]))
    draws = pd.DataFrame(dict(growth=g, cost_growth=cost_growth, k=k, revenue=rev27, costs=costs27, ebitda=ebitda27,
                              margin=margin, multiple=mult, price=price))
    return price, marg, draws


def mc_jessie(seed: int = JESSIE_SEED, n: int = JESSIE_N) -> tuple[np.ndarray, dict]:
    """Replicates 07_scenarios_montecarlo.R in numpy (R's set.seed stream is not reproduced; the summary is)."""
    model_a = pd.read_csv(ROOT / "data" / "processed" / "overnight" / "13_model_annual.csv")
    grid = pd.read_csv(ROOT / "data" / "processed" / "overnight" / "13_scenario_grid.csv")
    gg = grid.sort_values(["fy27_revenue_growth_pct", "fy27_margin_pct", "exit_ev_ebitda_x"]).copy()
    gg["ev_ebitda"] = gg["fy27_adj_ebitda_musd"] * gg["exit_ev_ebitda_x"]
    grp = gg.groupby(["fy27_revenue_growth_pct", "fy27_margin_pct"])
    gg["shares"] = (gg["ev_ebitda"] - grp["ev_ebitda"].shift()) / (gg["price"] - grp["price"].shift())
    shares = gg["shares"].median()
    netcash = (gg["price"] * shares - gg["ev_ebitda"]).median()
    sc27 = model_a[model_a.year == 2027].set_index("scenario")
    rev26 = float(model_a[(model_a.scenario == "Base") & (model_a.year == 2026)]["revenue"].iloc[0])
    rng_g = (sc27.loc["Bear", "revenue_yoy_pct"], sc27.loc["Base", "revenue_yoy_pct"], sc27.loc["Bull", "revenue_yoy_pct"])
    rng_m = (sc27.loc["Bear", "adj_ebitda_margin_pct"], sc27.loc["Base", "adj_ebitda_margin_pct"], sc27.loc["Bull", "adj_ebitda_margin_pct"])
    rng = np.random.default_rng(seed)
    cov = np.full((3, 3), JESSIE_RHO)
    np.fill_diagonal(cov, 1.0)
    z = rng.multivariate_normal(np.zeros(3), cov, size=n)
    u = norm.cdf(z)
    growth = pert(u[:, 0], *rng_g)
    margin = pert(u[:, 1], *rng_m)
    mult = pert(u[:, 2], *JESSIE_MULT)
    rev27 = rev26 * (1 + growth / 100)
    ebitda27 = rev27 * margin / 100
    price = (ebitda27 * mult + netcash) / shares
    info = dict(implied_shares_m=float(shares), implied_net_cash_musd=float(netcash), rev26_base=rev26,
                growth_bear=rng_g[0], growth_base=rng_g[1], growth_bull=rng_g[2],
                margin_bear=rng_m[0], margin_base=rng_m[1], margin_bull=rng_m[2],
                median_margin=float(np.median(margin)), median_growth=float(np.median(growth)), median_multiple=float(np.median(mult)),
                median_ebitda=float(np.median(ebitda27)))
    return price, info


def block_mc() -> pd.DataFrame:
    rows = []
    variants = [
        ("corrected: primary", dict(cost_lo=STREET_FY28_COST_GROWTH, cost_mode=COST_PATHS["Line build base (+11.1%)"], cost_hi=COST_PATHS["FY26E Street repeated (+15.0%)"], k_mode="sym", mult_anchor="spot")),
        ("corrected: asymmetric k (k_up 0.58, k_dn 0)", dict(cost_lo=STREET_FY28_COST_GROWTH, cost_mode=COST_PATHS["Line build base (+11.1%)"], cost_hi=COST_PATHS["FY26E Street repeated (+15.0%)"], k_mode="asym", mult_anchor="spot")),
        ("corrected: + multiple residual sd 1.5 turns", dict(cost_lo=STREET_FY28_COST_GROWTH, cost_mode=COST_PATHS["Line build base (+11.1%)"], cost_hi=COST_PATHS["FY26E Street repeated (+15.0%)"], k_mode="sym", mult_anchor="spot", mult_noise_sd=1.5)),
        ("corrected: cost centred on the Street (8.7/10.0/12.6)", dict(cost_lo=STREET_FY28_COST_GROWTH, cost_mode=COST_PATHS["Street (+10.0%)"], cost_hi=COST_PATHS["FY24-25 average (+12.6%)"], k_mode="sym", mult_anchor="spot")),
        ("corrected: cost centred on history (10.0/12.6/15.0)", dict(cost_lo=COST_PATHS["Street (+10.0%)"], cost_mode=COST_PATHS["FY24-25 average (+12.6%)"], cost_hi=COST_PATHS["FY26E Street repeated (+15.0%)"], k_mode="sym", mult_anchor="spot")),
        ("corrected: DEC-0014 literal anchor (16.5x at 12.27%)", dict(cost_lo=STREET_FY28_COST_GROWTH, cost_mode=COST_PATHS["Line build base (+11.1%)"], cost_hi=COST_PATHS["FY26E Street repeated (+15.0%)"], k_mode="sym", mult_anchor="dec14")),
        ("corrected: costs fully variable (k = 1), for contrast", dict(cost_lo=STREET_FY28_COST_GROWTH, cost_mode=COST_PATHS["Line build base (+11.1%)"], cost_hi=COST_PATHS["FY26E Street repeated (+15.0%)"], k_mode="one", mult_anchor="spot")),
        ("corrected: growth centred on the Street (5.5/11.5/15.1)", dict(cost_lo=STREET_FY28_COST_GROWTH, cost_mode=COST_PATHS["Line build base (+11.1%)"], cost_hi=COST_PATHS["FY26E Street repeated (+15.0%)"], k_mode="sym", mult_anchor="spot", growth=(None, STREET["fy27_growth"], None))),
        ("thesis 3 alone: Street FY26 base and FY27 revenue, costs uncertain", dict(cost_lo=STREET_FY28_COST_GROWTH, cost_mode=COST_PATHS["Line build base (+11.1%)"], cost_hi=COST_PATHS["FY26E Street repeated (+15.0%)"], k_mode="sym", mult_anchor="spot", growth=(STREET["fy27_growth"], STREET["fy27_growth"], STREET["fy27_growth"]), base="street")),
        ("thesis 3 alone, history-centred costs (10.0/12.6/15.0), Street revenue", dict(cost_lo=COST_PATHS["Street (+10.0%)"], cost_mode=COST_PATHS["FY24-25 average (+12.6%)"], cost_hi=COST_PATHS["FY26E Street repeated (+15.0%)"], k_mode="sym", mult_anchor="spot", growth=(STREET["fy27_growth"], STREET["fy27_growth"], STREET["fy27_growth"]), base="street")),
        ("revenue thesis alone: costs at the Street's +10.0%, revenue uncertain", dict(cost_lo=COST_PATHS["Street (+10.0%)"], cost_mode=COST_PATHS["Street (+10.0%)"], cost_hi=COST_PATHS["Street (+10.0%)"], k_mode="sym", mult_anchor="spot")),
        ("revenue thesis alone, costs fully variable (k = 1): no cost mechanism at all", dict(cost_lo=COST_PATHS["Street (+10.0%)"], cost_mode=COST_PATHS["Street (+10.0%)"], cost_hi=COST_PATHS["Street (+10.0%)"], k_mode="one", mult_anchor="spot")),
    ]
    draws_primary = None
    for label, kw in variants:
        for seed in (SEED, SEED_CHECK):
            price, marg, draws = mc_corrected(seed, N_DRAWS, **kw)
            rows.append(dict(variant=label, seed=seed, **summarise(price, marg)))
            if label == "corrected: primary" and seed == SEED:
                draws_primary = draws
    # Jessie's, replicated at her spot and re-scored at today's
    jp, jinfo = mc_jessie()
    rows.append(dict(variant="Jessie 7 Sep MC (replicated), scored at $181.94 and at $166.84", seed=JESSIE_SEED, **summarise(jp, jinfo)))
    jp2, _ = mc_jessie(seed=SEED_CHECK)
    rows.append(dict(variant="Jessie 7 Sep MC (replicated), second seed", seed=SEED_CHECK, **summarise(jp2, jinfo)))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "43b_mc_summary.csv", index=False)
    qs = [0.05, 0.25, 0.5, 0.75, 0.95]
    marg = draws_primary.quantile(qs).T.reset_index().rename(columns={"index": "variable"})
    marg.columns = ["variable"] + [f"p{int(q * 100)}" for q in qs]
    marg.to_csv(OUT / "43b_mc_primary_marginals.csv", index=False)
    draws_primary.sample(2000, random_state=SEED).to_csv(OUT / "43b_mc_primary_draws_sample.csv", index=False)
    # price by cost-growth bucket, primary
    d = draws_primary.copy()
    d["cost_bucket"] = pd.cut(d["cost_growth"], [-np.inf, 10.0, 11.1, 12.6, 15.0, np.inf], labels=["<10.0 (below Street)", "10.0-11.1", "11.1-12.6", "12.6-15.0", ">15.0"])
    d["growth_bucket"] = pd.cut(d["growth"], [-np.inf, 7.5, 9.26, 11.5, np.inf], labels=["<7.5", "7.5-9.26", "9.26-11.5 (to Street)", ">11.5 (above Street)"])
    ct = d.groupby(["growth_bucket", "cost_bucket"], observed=True).agg(n=("price", "size"), median_price=("price", "median"), median_margin=("margin", "median"),
                                                                     p_below_spot=("price", lambda x: float((x < SPOT).mean())), p_below_143=("price", lambda x: float((x < 143).mean()))).reset_index()
    ct.to_csv(OUT / "43b_mc_primary_by_bucket.csv", index=False)
    return df


# ======================================================================================================================
# 4. REVERSE DCF at Street growth: the margin the price implies
# ======================================================================================================================
def block_reverse_dcf() -> pd.DataFrame:
    ev = ev_at(SPOT)
    rows = []
    # (i) multiple-line reading, FY27 only
    m_lit = DEC14_MID + DEC14_SLOPE * (STREET["fy27_growth"] - DEC14_G0)
    e_lit = ev / m_lit
    rows.append(dict(method="DEC-0014 literal line at Street FY27 growth", wacc_pct=np.nan, terminal_growth_pct=np.nan, fcf_basis="n/a",
                     implied_fy27_ebitda=e_lit, implied_fy27_margin_pct=100 * e_lit / STREET["fy27_rev"],
                     implied_fy27_cost_growth_pct=100 * ((STREET["fy27_rev"] - e_lit) / STREET["fy26_costs"] - 1),
                     implied_multiple_x=m_lit, note="EV / M(g_street); margin does not enter the multiple (A, WS12: t 0.4)"))
    g_ntm = joint_solve_growth(SPOT)
    rows.append(dict(method="Joint solve A at spot (NTM basis, margin held at LTM 35.1%)", wacc_pct=np.nan, terminal_growth_pct=np.nan, fcf_basis="n/a",
                     implied_fy27_ebitda=np.nan, implied_fy27_margin_pct=100 * LTM_MARGIN, implied_fy27_cost_growth_pct=np.nan,
                     implied_multiple_x=A_INTERCEPT + A_SLOPE * g_ntm, note=f"implies NTM growth {g_ntm:.2f}% (FY27 proportional {g_ntm - NTM_TO_FY27_SPREAD:.2f}%); it solves for growth, not margin"))
    # (ii) fade DCF at Street growth: constant margin m from FY27, FY28 growth = Street FY28 revenue growth, fading to tg
    for basis in ("reported FCF (delivered conversion 1.024)", "SBC-adjusted FCF"):
        for wacc in (0.09, 0.10, 0.11):
            for tg in (0.025, 0.03):
                def pv_of_margin(m):
                    ebitda = STREET["fy27_rev"] * m
                    fcf = ebitda * FCF_TO_EBITDA - (SBC_FY27 if basis.startswith("SBC") else 0.0)
                    return fade_dcf(fcf, STREET["fy28_growth"] / 100, wacc, tg)
                m = bisect(pv_of_margin, ev, 0.05, 0.80)
                e = STREET["fy27_rev"] * m
                rows.append(dict(method="fade DCF at Street revenue growth (FY27 +11.5%, FY28 +10.9% fading to tg over 10y), constant margin",
                                 wacc_pct=100 * wacc, terminal_growth_pct=100 * tg, fcf_basis=basis,
                                 implied_fy27_ebitda=e, implied_fy27_margin_pct=100 * m,
                                 implied_fy27_cost_growth_pct=100 * ((STREET["fy27_rev"] - e) / STREET["fy26_costs"] - 1),
                                 implied_multiple_x=ev / e, note="repo fade_dcf (A_common.py), PV at 30 Sep 2026"))
    df = pd.DataFrame(rows)
    # (iii) the inverse: at each cost-leg margin held from FY27, what FY28 starting FCF growth does the price need (reported FCF, 10%/3%)
    inv = []
    for label, margin in [("Street 36.45%", 100 * STREET["fy27_ebitda"] / STREET["fy27_rev"]), ("line build base 35.66%", 100 * LB["base_fy27_ebitda"] / LB["base_fy27_rev"]),
                          ("history cost growth at Street revenue 34.96%", 100 * (STREET["fy27_rev"] - STREET["fy26_costs"] * (1 + COST_PATHS["FY24-25 average (+12.6%)"] / 100)) / STREET["fy27_rev"]),
                          ("official v2 33.97%", 100 * OFFICIAL["fy27_ebitda"] / OFFICIAL["fy27_rev"]),
                          ("40 short case 31.93%", 100 * LB["short_fy27_ebitda"] / LB["short_fy27_rev"])]:
        for wacc in (0.09, 0.10, 0.11):
            fcf = STREET["fy27_rev"] * margin / 100 * FCF_TO_EBITDA
            g0 = bisect(lambda g: fade_dcf(fcf, g, wacc, 0.03), ev, -0.30, 0.60)
            inv.append(dict(margin_case=label, fy27_margin_pct=margin, wacc_pct=100 * wacc, terminal_growth_pct=3.0,
                            fy27_fcf_at_street_revenue=fcf, required_fy28_starting_fcf_growth_pct=100 * g0,
                            street_fy28_revenue_growth_pct=STREET["fy28_growth"], gap_vs_street_growth_pp=100 * g0 - STREET["fy28_growth"]))
    pd.DataFrame(inv).to_csv(OUT / "43b_reverse_dcf_required_growth.csv", index=False)
    df.to_csv(OUT / "43b_reverse_dcf_implied_margin.csv", index=False)
    return df, pd.DataFrame(inv)


# ======================================================================================================================
# 5. SCENARIO TABLE for the memo
# ======================================================================================================================
def block_scenarios() -> pd.DataFrame:
    mult_spot = ev_at(SPOT) / STREET["fy27_ebitda"]
    g_street = STREET["fy27_growth"]

    def m_of(g):
        return mult_spot + DEC14_SLOPE * (g - g_street)

    rows = []
    hist = COST_PATHS["FY24-25 average (+12.6%)"]
    cases = [
        ("Street (LSEG FY27, n 44)", STREET["fy27_rev"], STREET["fy27_costs"], g_street),
        ("Street revenue, history cost growth +12.6% (41)", STREET["fy27_rev"], STREET["fy26_costs"] * (1 + hist / 100), g_street),
        ("Official v2 base (revenue -2.5%, line-build costs)", OFFICIAL["fy27_rev"], OFFICIAL["fy27_costs"], OFFICIAL["fy27_growth"]),
        ("Official v2 revenue, history cost growth +12.6%", OFFICIAL["fy27_rev"], STREET["fy26_costs"] * (1 + hist / 100), OFFICIAL["fy27_growth"]),
        ("40 short case (costs at budget)", LB["short_fy27_rev"], LB["short_fy27_rev"] - LB["short_fy27_ebitda"], LB["short_growth"]),
        ("40 rev_bear x cost_bear (both_bear)", LB["rev_bear_fy27"], LB["rev_bear_fy27"] - 4409.176119, LB["rev_bear_growth"]),
        ("40 rev_bull (line-build costs)", LB["rev_bull_fy27"], LB["rev_bull_fy27"] - 6253.344980, LB["rev_bull_growth"]),
    ]
    for label, rev, costs, g in cases:
        e = rev - costs
        for mlabel, m in [("spot-anchored DEC-0014 line", m_of(g)), ("DEC-0014 literal line", DEC14_MID + DEC14_SLOPE * (g - DEC14_G0)), ("fixed 16.5x", 16.5), ("fixed 13.5x", 13.5)]:
            rows.append(dict(scenario=label, fy27_revenue=rev, fy27_growth_pct=g, fy27_costs=costs, fy27_ebitda=e, fy27_margin_pct=100 * e / rev,
                             multiple_basis=mlabel, ev_ebitda_x=m, price=price_from(e, m), vs_spot_pct=100 * (price_from(e, m) / SPOT - 1)))
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "43b_scenario_table.csv", index=False)
    return df


def main() -> int:
    print(f"43b valuation link. spot ${SPOT}, shares {SHARES}m, net cash ${NET_CASH}m, EV ${ev_at(SPOT):,.0f}m")
    print(f"  Street FY27 growth {STREET['fy27_growth']:.2f}%, cost growth {STREET['fy27_cost_growth']:.2f}%; official v2 growth {OFFICIAL['fy27_growth']:.2f}%, cost growth {OFFICIAL['fy27_cost_growth']:.2f}%")
    print(f"  market pays {ev_at(SPOT) / STREET['fy27_ebitda']:.2f}x the Street's FY27 EBITDA, {ev_at(SPOT) / OFFICIAL['fy27_ebitda']:.2f}x official v2, {ev_at(SPOT) / LB['short_fy27_ebitda']:.2f}x the 40 short case")
    trace, checks = block_trace()
    print("\n-- trace --")
    print(trace[["price", "label", "joint_solve_ntm_growth_pct", "joint_solve_ev_ntm_ebitda_x", "fy27_growth_proportional_pct", "ev_to_street_fy27_ebitda_x", "ev_to_official_v2_fy27_ebitda_x", "ev_to_short_case_fy27_ebitda_x"]].round(2).to_string(index=False))
    print(checks.round(2).to_string(index=False))
    steps, summary = block_bridge()
    print("\n-- bridge (official v2 revenue, line build costs, M6 flex, mid slope) --")
    sel = steps[(steps.revenue_case.str.startswith("official")) & (steps.cost_path == "Line build base (+11.1%)") & (steps.flex_mode == "m6") & (np.isclose(steps.slope, DEC14_SLOPE))]
    print(sel[["step", "ebitda", "margin_pct", "multiple", "price", "d_price"]].round(2).to_string(index=False))
    s = summary[(summary.revenue_case.str.startswith("official")) & (summary.flex_mode == "m6") & (np.isclose(summary.slope, DEC14_SLOPE))]
    print(s[["cost_path", "target", "downside_total", "a_revenue", "b_no_flex", "c_cost_path", "d_multiple", "thesis3_b_plus_c", "thesis3_share_pct"]].round(2).to_string(index=False))
    mc = block_mc()
    print("\n-- monte carlo --")
    print(mc[["variant", "seed", "median", "mean", "p5", "p25", "p75", "p95", "p_below_spot", "p_below_143", "p_above_jessie_spot", "median_margin", "median_multiple"]].round(3).to_string(index=False))
    rd, inv = block_reverse_dcf()
    print("\n-- reverse dcf --")
    print(rd[["method", "wacc_pct", "terminal_growth_pct", "fcf_basis", "implied_fy27_margin_pct", "implied_fy27_cost_growth_pct", "implied_multiple_x"]].round(2).to_string(index=False))
    print(inv.round(2).to_string(index=False))
    sc = block_scenarios()
    print("\n-- scenario table (spot-anchored line) --")
    print(sc[sc.multiple_basis == "spot-anchored DEC-0014 line"][["scenario", "fy27_ebitda", "fy27_margin_pct", "ev_ebitda_x", "price", "vs_spot_pct"]].round(2).to_string(index=False))
    meta = dict(spot=SPOT, shares=SHARES, net_cash=NET_CASH, n_draws=N_DRAWS, seeds=[SEED, SEED_CHECK], jessie_seed=JESSIE_SEED,
                discounting="none: FY27 EBITDA x multiple at the spot EV convention, the same convention as the joint solve and Jessie's MC",
                growth_pert=[LB["rev_bear_growth"], OFFICIAL["fy27_growth"], LB["rev_bull_growth"]],
                cost_pert_primary=[STREET_FY28_COST_GROWTH, COST_PATHS["Line build base (+11.1%)"], COST_PATHS["FY26E Street repeated (+15.0%)"]],
                k=[K_TOTAL, K_TOTAL_SE], slope=[DEC14_SLOPE, DEC14_SLOPE_SE], fitted_parameters_here=0)
    (OUT / "43b_meta.json").write_text(json.dumps(meta, indent=2))
    print(f"\nwrote {len(list(OUT.glob('*.csv')))} csv files to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
