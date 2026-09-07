"""Base rates for Airbnb earnings prints, 2020Q4 to 2026Q2 (23 prints).

Builds one row per print with: revenue vs the guide it was measured against,
the direction the next-quarter revenue guide implied versus the just-reported
growth, nights acceleration, Adjusted EBITDA margin versus the direction guided
on the prior call, the FY margin floor action, and 1/5/20-day excess returns
versus QQQ. Then writes a summary block of base rates with n for every cell,
plus a few diagnostic correlations with permutation p-values so the team can
see what "not predictive on 23 prints" looks like.

Outputs (both under data\\processed\\predictive):
  01_print_base_rates.csv          one row per print
  01_print_base_rates_summary.csv  base-rate cells and diagnostics

Inputs:
  data\\processed\\abnb_revenue_guidance_vs_actual.csv   (from Theo's guidance set)
  data\\external\\abnb_earnings_reactions.csv            (ABNB and QQQ 1/5/20-day moves)
  data\\processed\\abnb_quarterly_kpis_from_study.csv    (nights, revenue, adj EBITDA, take rate)
  data\\processed\\abnb_quarterly_cost_stack_exsbc.csv   (adj EBITDA margin)
  theos-past-research\\research\\guidance\\data\\normalized\\quarterly_actuals.csv (revenue y/y)
  research\\notes\\2026-09-05_margin-drivers.md section 5 (margin guide and FY floor, hand-coded below)

Hand-entered items are marked HAND in comments and flagged in the
source_flags column. Run:  python analysis\\src\\predictive\\01_print_base_rates.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT_DIR = os.path.join(ROOT, "data", "processed", "predictive")
RNG = np.random.default_rng(20261105)
N_PERM = 20000


def P(*parts: str) -> str:
    return os.path.join(ROOT, *parts)


# --------------------------------------------------------------------------
# Hand-coded inputs (sources named). Keep these small and visible.
# --------------------------------------------------------------------------

# 2020 quarterly nights (millions). Source: Airbnb shareholder letters Q1-Q4 2021
# state y/y growth of +13%, +197%, +29%, +59% against 64.4/83.1/79.7/73.4, which
# back out to these values; FY2020 letter total 193.2M. HAND.
NIGHTS_2020 = {"2020Q1": 56.9, "2020Q2": 28.0, "2020Q3": 61.8, "2020Q4": 46.3}
# Q3 2020 nights y/y (-28%) and Q4 2020 (-39%): Q3/Q4 2020 shareholder letters;
# Q4 figure also in data\external\abnb_major_moves_events.csv row 6. HAND.
NIGHTS_YOY_2020 = {"2020Q3": -28.0, "2020Q4": -39.0}
# Q4 2020 Adjusted EBITDA, $M. Source: Q4 2020 shareholder letter. HAND.
ADJ_EBITDA_2020Q4 = -21.0
REVENUE_2020Q4 = 859.0

# What the PRIOR call guided for this quarter's Adjusted EBITDA margin, and how
# the print compared. Coding rule: 'above' = margin better than the guided
# direction or level; 'in_line' = as guided; 'below' = worse than guided.
# Source: research\notes\2026-09-05_margin-drivers.md, section 5 table
# (forward-guidance column of the prior row, outcome column of this row).
MARGIN_GUIDE = {
    "2020Q4": ("none (IPO quarter)", None),
    "2021Q1": ("Q1 lowest margin of year; H1 below H2", "in_line"),
    "2021Q2": ("breakeven to slightly positive", "above"),
    "2021Q3": ("highest EBITDA dollars and margin ever", "in_line"),
    "2021Q4": ("Q4 y/y margin expansion greater than Q3's", "in_line"),
    "2022Q1": ("first positive Q1 ever", "above"),
    "2022Q2": ("margin up low-double-digit points y/y", "above"),
    "2022Q3": ("at or slightly below 49%", "above"),
    "2022Q4": ("in line to modestly above 22%", "above"),
    "2023Q1": ("slightly down (brand pull-forward)", "in_line"),
    "2023Q2": ("EBITDA similar nominal, margin lower", "in_line"),
    "2023Q3": ("record EBITDA, margin above Q3 2022", "in_line"),
    "2023Q4": ("record EBITDA, margin above Q4 2022", "in_line"),
    "2024Q1": ("margin up (Easter timing)", "in_line"),
    "2024Q2": ("nominal flat to up, margin down", "above"),
    "2024Q3": ("EBITDA about flat nominal, margin down", "in_line"),
    "2024Q4": ("margin down several points", "in_line"),
    "2025Q1": ("margin down (calendar, FX)", "in_line"),
    "2025Q2": ("flat to slightly down", "above"),
    "2025Q3": ("EBITDA above $2.0B, margin below Q3 2024", "in_line"),
    "2025Q4": ("EBITDA flat to down, margin down", "in_line"),
    "2026Q1": ("margin flat", "above"),
    "2026Q2": ("EBITDA and margin up y/y", "in_line"),
}

# What THIS call did to the full-year Adjusted EBITDA margin guide.
# 'introduced' = first guide for a new fiscal year; 'raised'; 'held'; 'none'.
# Source: margin note section 5 (bold items) and section 7.
FY_FLOOR = {
    "2020Q4": ("none", "no FY guide; 30%+ long-term aspiration"),
    "2021Q1": ("none", ""),
    "2021Q2": ("none", "30%+ long-term aspiration repeated"),
    "2021Q3": ("none", ""),
    "2021Q4": ("introduced", "FY22 directionally in line with 2021 (27%)"),
    "2022Q1": ("raised", "FY22 modest expansion"),
    "2022Q2": ("held", "FY22 expansion"),
    "2022Q3": ("held", "no change"),
    "2022Q4": ("introduced", "FY23 flat with 2022 (35%)"),
    "2023Q1": ("held", "FY23 broadly in line with 2022"),
    "2023Q2": ("raised", "FY23 modestly higher than 2022"),
    "2023Q3": ("raised", "FY23 about 150 bps above 2022"),
    "2023Q4": ("introduced", "FY24 at least 35% (first numeric floor)"),
    "2024Q1": ("held", "FY24 at least 35%"),
    "2024Q2": ("held", "FY24 at least 35%"),
    "2024Q3": ("raised", "FY24 about 35.5%"),
    "2024Q4": ("introduced", "FY25 at least 34.5%"),
    "2025Q1": ("held", "FY25 at least 34.5%"),
    "2025Q2": ("held", "FY25 at least 34.5%"),
    "2025Q3": ("raised", "FY25 about 35%"),
    "2025Q4": ("introduced", "FY26 stable (about 35%)"),
    "2026Q1": ("raised", "FY26 at least 35%"),
    "2026Q2": ("raised", "FY26 at least 35.5%"),
}


def q_to_std(q: str) -> str:
    """'1Q21' -> '2021Q1'."""
    return f"20{q[2:]}Q{q[0]}"


def prior_q(q: str) -> str:
    y, n = int(q[:4]), int(q[-1])
    return f"{y - 1}Q4" if n == 1 else f"{y}Q{n - 1}"


def next_q(q: str) -> str:
    y, n = int(q[:4]), int(q[-1])
    return f"{y + 1}Q1" if n == 4 else f"{y}Q{n + 1}"


def year_ago(q: str) -> str:
    return f"{int(q[:4]) - 1}Q{q[-1]}"


def direction(delta: float, tol: float = 0.5) -> str | None:
    if pd.isna(delta):
        return None
    if delta > tol:
        return "accel"
    if delta < -tol:
        return "decel"
    return "flat"


def perm_p_diff_means(a: np.ndarray, b: np.ndarray) -> float:
    """Two-sided permutation p-value for a difference in means."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    obs = a.mean() - b.mean()
    pool = np.concatenate([a, b])
    n_a = len(a)
    cnt = 0
    for _ in range(N_PERM):
        RNG.shuffle(pool)
        d = pool[:n_a].mean() - pool[n_a:].mean()
        if abs(d) >= abs(obs) - 1e-12:
            cnt += 1
    return (cnt + 1) / (N_PERM + 1)


def perm_p_corr(x: np.ndarray, y: np.ndarray) -> float:
    """Two-sided permutation p-value for Pearson r."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    obs = np.corrcoef(x, y)[0, 1]
    cnt = 0
    yy = y.copy()
    for _ in range(N_PERM):
        RNG.shuffle(yy)
        if abs(np.corrcoef(x, yy)[0, 1]) >= abs(obs) - 1e-12:
            cnt += 1
    return (cnt + 1) / (N_PERM + 1)


def main() -> None:
    guide = pd.read_csv(P("data", "processed", "abnb_revenue_guidance_vs_actual.csv"))
    react = pd.read_csv(P("data", "external", "abnb_earnings_reactions.csv")).set_index("quarter")
    kpi = pd.read_csv(P("data", "processed", "abnb_quarterly_kpis_from_study.csv"))
    cost = pd.read_csv(P("data", "processed", "abnb_quarterly_cost_stack_exsbc.csv"))
    actual = pd.read_csv(
        P("theos-past-research", "research", "guidance", "data", "normalized", "quarterly_actuals.csv")
    )

    kpi["q"] = kpi["quarter"].map(q_to_std)
    cost["q"] = cost["quarter"].map(q_to_std)
    kpi = kpi.set_index("q")
    margin = cost.set_index("q")["adj_ebitda_margin_pct"]

    rev = actual[actual["metric_code"] == "revenue"].set_index("fiscal_period")
    revenue = rev["value"].astype(float)
    rev_yoy = (rev["yoy_growth_reported"].astype(float) * 100).round(1)

    nights = pd.concat([pd.Series(NIGHTS_2020), kpi["nights_m"]])
    nights_yoy = {}
    for q in nights.index:
        ya = year_ago(q)
        if ya in nights.index:
            nights_yoy[q] = round((nights[q] / nights[ya] - 1) * 100, 1)
    nights_yoy.update(NIGHTS_YOY_2020)
    nights_yoy = pd.Series(nights_yoy)

    g_by_guided = guide.set_index("guided_quarter")
    g_by_issuer = guide.set_index("issued_on_call")

    prints = list(react.index)
    assert len(prints) == 23, len(prints)
    rows = []
    for q in prints:
        r = react.loc[q]
        row = {
            "print_quarter": q,
            "reaction_date": r["reaction_date"],
            "revenue_musd": revenue.get(q, np.nan),
            "revenue_yoy_pct": rev_yoy.get(q, np.nan),
        }
        # --- revenue vs the guide for this quarter
        if q in g_by_guided.index:
            g = g_by_guided.loc[q]
            row.update(
                guide_mid_musd=g["guide_mid_musd"],
                guide_high_musd=g["guide_high_musd"],
                rev_vs_mid_pct=g["actual_vs_mid_pct"],
                rev_vs_high_pct=g["actual_vs_high_pct"],
                beat_mid=int(g["actual_vs_mid_pct"] > 0),
                beat_top=int(g["actual_vs_high_pct"] > 0),
            )
        else:
            row.update(
                guide_mid_musd=np.nan, guide_high_musd=np.nan, rev_vs_mid_pct=np.nan,
                rev_vs_high_pct=np.nan, beat_mid=np.nan, beat_top=np.nan,
            )
        # --- next-quarter guide issued on this call
        nq = next_q(q)
        if q in g_by_issuer.index:
            gi = g_by_issuer.loc[q]
            base = revenue.get(year_ago(nq), np.nan)
            implied = (gi["guide_mid_musd"] / base - 1) * 100
            row["next_q_guide_mid_musd"] = gi["guide_mid_musd"]
            row["next_q_guide_implied_yoy_pct"] = round(implied, 1)
            row["guide_vs_reported_yoy_pp"] = round(implied - row["revenue_yoy_pct"], 1)
            row["guide_direction"] = direction(row["guide_vs_reported_yoy_pp"])
            # cushion-adjusted: add the mean beat vs midpoint over guides already
            # resolved at or before this print (point-in-time; nothing later)
            prior_beats = guide[guide["guided_quarter"] <= q]["actual_vs_mid_pct"].dropna()
            if len(prior_beats) >= 3:
                cushion = prior_beats.mean()
                adj = implied + cushion
                row["trailing_cushion_pct"] = round(cushion, 2)
                row["guide_implied_yoy_cushion_adj_pct"] = round(adj, 1)
                row["guide_direction_cushion_adj"] = direction(adj - row["revenue_yoy_pct"])
            else:
                row["trailing_cushion_pct"] = np.nan
                row["guide_implied_yoy_cushion_adj_pct"] = np.nan
                row["guide_direction_cushion_adj"] = None
        else:
            for k in ("next_q_guide_mid_musd", "next_q_guide_implied_yoy_pct", "guide_vs_reported_yoy_pp",
                      "trailing_cushion_pct", "guide_implied_yoy_cushion_adj_pct"):
                row[k] = np.nan
            row["guide_direction"] = "qualitative"
            row["guide_direction_cushion_adj"] = None
        # --- nights
        row["nights_m"] = nights.get(q, np.nan)
        row["nights_yoy_pct"] = nights_yoy.get(q, np.nan)
        row["nights_yoy_prior_q_pct"] = nights_yoy.get(prior_q(q), np.nan)
        acc = row["nights_yoy_pct"] - row["nights_yoy_prior_q_pct"]
        row["nights_accel_pp"] = round(acc, 1) if pd.notna(acc) else np.nan
        row["nights_direction"] = direction(acc)
        # --- margin
        m = ADJ_EBITDA_2020Q4 / REVENUE_2020Q4 * 100 if q == "2020Q4" else margin[q]
        row["adj_ebitda_margin_pct"] = round(m, 1)
        ya = year_ago(q)
        row["margin_yoy_pp"] = round(m - margin[ya], 1) if ya in margin.index else np.nan
        row["take_rate_pct"] = kpi["take_rate_pct"].get(q, np.nan)
        txt, coded = MARGIN_GUIDE[q]
        row["margin_guided_direction"] = txt
        row["margin_vs_guide"] = coded
        row["margin_met"] = np.nan if coded is None else int(coded in ("above", "in_line"))
        row["fy_floor_action"], row["fy_floor_detail"] = FY_FLOOR[q]
        # --- returns
        for w in ("1d", "5d", "20d"):
            row[f"abnb_{w}_pct"] = r[f"abnb_{w}_pct"]
            row[f"qqq_{w}_pct"] = r[f"qqq_{w}_pct"]
            row[f"excess_{w}_pct"] = r[f"excess_{w}_pct"]
        rows.append(row)

    df = pd.DataFrame(rows)
    df["source_flags"] = ""
    early = df["print_quarter"].isin(["2020Q4", "2021Q1", "2021Q2", "2021Q3", "2021Q4"])
    df.loc[early, "source_flags"] = "nights_yoy uses HAND 2020 nights"
    df.loc[df["print_quarter"] == "2020Q4", "source_flags"] += "; margin uses HAND Q4 2020 adj EBITDA -21"
    os.makedirs(OUT_DIR, exist_ok=True)
    df.to_csv(os.path.join(OUT_DIR, "01_print_base_rates.csv"), index=False)

    # ----------------------------------------------------------------------
    # Summary block
    # ----------------------------------------------------------------------
    S: list[dict] = []

    def add(block, cell, n, value, note=""):
        S.append({"block": block, "cell": cell, "n": int(n), "value": value, "note": note})

    def rate(block, cell, series, cond):
        s = series.dropna()
        add(block, cell, len(s), round(float(cond(s).mean()), 3))

    U = "unconditional"
    rate(U, "P(revenue beat guide midpoint)", df["rev_vs_mid_pct"], lambda s: s > 0)
    rate(U, "P(revenue beat top of range)", df["rev_vs_high_pct"], lambda s: s > 0)
    rate(U, "P(revenue beat top of range | 2024Q1 on)", df[df["print_quarter"] >= "2024Q1"]["rev_vs_high_pct"], lambda s: s > 0)
    add(U, "mean revenue beat vs midpoint, %", df["rev_vs_mid_pct"].notna().sum(), round(df["rev_vs_mid_pct"].mean(), 2))
    add(U, "median revenue beat vs midpoint, %", df["rev_vs_mid_pct"].notna().sum(), round(df["rev_vs_mid_pct"].median(), 2))
    add(U, "mean revenue beat vs midpoint, last 8 guides, %", 8, round(df["rev_vs_mid_pct"].dropna().tail(8).mean(), 2))
    add(U, "min revenue beat vs midpoint, %", df["rev_vs_mid_pct"].notna().sum(), round(df["rev_vs_mid_pct"].min(), 2))
    add(U, "mean revenue beat vs top, %", df["rev_vs_high_pct"].notna().sum(), round(df["rev_vs_high_pct"].mean(), 2))
    add(U, "mean revenue beat vs top, Q3 guides only, %", int((df["print_quarter"].str.endswith("Q3") & df["rev_vs_high_pct"].notna()).sum()),
        round(df[df["print_quarter"].str.endswith("Q3")]["rev_vs_high_pct"].mean(), 2), "seasonally large quarter; smallest cushions")
    rate(U, "P(excess 1d > 0)", df["excess_1d_pct"], lambda s: s > 0)
    rate(U, "P(excess 5d > 0)", df["excess_5d_pct"], lambda s: s > 0)
    rate(U, "P(excess 20d > 0)", df["excess_20d_pct"], lambda s: s > 0)
    rate(U, "P(|ABNB 1d| > 7%)", df["abnb_1d_pct"], lambda s: s.abs() > 7)
    rate(U, "P(|excess 1d| > 7%)", df["excess_1d_pct"], lambda s: s.abs() > 7)
    rate(U, "P(|ABNB 1d| > 10%)", df["abnb_1d_pct"], lambda s: s.abs() > 10)
    rate(U, "P(ABNB 1d > +7%)", df["abnb_1d_pct"], lambda s: s > 7)
    rate(U, "P(ABNB 1d < -7%)", df["abnb_1d_pct"], lambda s: s < -7)
    for w in ("1d", "5d", "20d"):
        s = df[f"excess_{w}_pct"].dropna()
        add(U, f"mean excess {w}, %", len(s), round(s.mean(), 2))
        add(U, f"median excess {w}, %", len(s), round(s.median(), 2))
        add(U, f"std excess {w}, %", len(s), round(s.std(ddof=1), 2))
    s = df["abnb_1d_pct"].abs()
    add(U, "mean |ABNB 1d|, %", len(s), round(s.mean(), 2))
    add(U, "median |ABNB 1d|, %", len(s), round(s.median(), 2))
    rate(U, "P(margin at or better than guided direction)", df["margin_met"], lambda s: s == 1)
    rate(U, "P(margin above guided direction)", df["margin_vs_guide"].dropna(), lambda s: s == "above")
    rate(U, "P(nights y/y accelerated vs prior quarter)", df["nights_direction"].dropna(), lambda s: s == "accel")
    rate(U, "P(nights y/y accelerated | 2023Q1 on)", df[df["print_quarter"] >= "2023Q1"]["nights_direction"], lambda s: s == "accel")
    rate(U, "P(next-q guide implied accel vs reported y/y)", df.loc[df["guide_direction"] != "qualitative", "guide_direction"], lambda s: s == "accel")
    rate(U, "P(next-q guide implied decel vs reported y/y)", df.loc[df["guide_direction"] != "qualitative", "guide_direction"], lambda s: s == "decel")
    rate(U, "P(next-q guide implied accel, cushion-adjusted)", df["guide_direction_cushion_adj"].dropna(), lambda s: s == "accel")
    fy = df["fy_floor_action"]
    for a in ("raised", "held", "introduced", "none"):
        add(U, f"count FY floor action = {a}", (fy == a).sum(), int((fy == a).sum()))
    num_era = df[df["print_quarter"] >= "2023Q4"]
    rate(U, "P(FY floor raised | numeric-floor era, 2023Q4 on)", num_era["fy_floor_action"], lambda s: s == "raised")
    mid_year = num_era[~num_era["print_quarter"].str.endswith("Q4")]
    rate(U, "P(FY floor raised | numeric-floor era, non-February calls)", mid_year["fy_floor_action"], lambda s: s == "raised")
    q3_calls = df[df["print_quarter"].str.endswith("Q3") & (df["print_quarter"] >= "2023Q3")]
    rate(U, "P(FY floor raised | Q3 print, 2023 on)", q3_calls["fy_floor_action"], lambda s: s == "raised")

    R = "regime_2024Q1_on"
    rec = df[df["print_quarter"] >= "2024Q1"]
    rate(R, "P(excess 1d > 0)", rec["excess_1d_pct"], lambda s: s > 0)
    rate(R, "P(|ABNB 1d| > 7%)", rec["abnb_1d_pct"], lambda s: s.abs() > 7)
    add(R, "mean excess 1d, %", len(rec), round(rec["excess_1d_pct"].mean(), 2))
    add(R, "median excess 1d, %", len(rec), round(rec["excess_1d_pct"].median(), 2))
    add(R, "mean revenue beat vs midpoint, %", rec["rev_vs_mid_pct"].notna().sum(), round(rec["rev_vs_mid_pct"].mean(), 2))
    add(R, "mean revenue beat vs top, %", rec["rev_vs_high_pct"].notna().sum(), round(rec["rev_vs_high_pct"].mean(), 2))

    def bucket_block(block, col, order):
        sub = df[df[col].notna() & (df[col] != "qualitative")]
        groups = {}
        for lvl in order:
            g = sub[sub[col] == lvl]
            if len(g) == 0:
                add(block, f"{lvl}: n", 0, 0)
                continue
            groups[lvl] = g
            for w in ("1d", "5d", "20d"):
                s = g[f"excess_{w}_pct"].dropna()
                add(block, f"{lvl}: mean excess {w}, %", len(s), round(s.mean(), 2))
                add(block, f"{lvl}: median excess {w}, %", len(s), round(s.median(), 2))
            s1 = g["excess_1d_pct"].dropna()
            add(block, f"{lvl}: P(excess 1d > 0)", len(s1), round(float((s1 > 0).mean()), 3))
            add(block, f"{lvl}: P(|ABNB 1d| > 7%)", len(s1), round(float((g["abnb_1d_pct"].abs() > 7).mean()), 3))
        if len(groups) == 2:
            (la, ga), (lb, gb) = list(groups.items())
            pa = perm_p_diff_means(ga["excess_1d_pct"].values, gb["excess_1d_pct"].values)
            add(block, f"perm p, mean excess 1d {la} vs {lb}", len(ga) + len(gb), round(pa, 3), f"{N_PERM} shuffles, two-sided")
            table = [
                [int((ga["excess_1d_pct"] > 0).sum()), int((ga["excess_1d_pct"] <= 0).sum())],
                [int((gb["excess_1d_pct"] > 0).sum()), int((gb["excess_1d_pct"] <= 0).sum())],
            ]
            fe = stats.fisher_exact(table)
            add(block, f"Fisher p, P(excess 1d>0) {la} vs {lb}", len(ga) + len(gb), round(float(fe[1]), 3))

    df["beat_bucket"] = np.where(df["beat_top"].isna(), None, np.where(df["beat_top"] == 1, "beat_top", "beat_mid_only"))
    bucket_block("by_beat_bucket", "beat_bucket", ["beat_top", "beat_mid_only"])
    med = df["rev_vs_mid_pct"].median()
    df["beat_size_bucket"] = np.where(df["rev_vs_mid_pct"].isna(), None, np.where(df["rev_vs_mid_pct"] > med, "big_beat", "small_beat"))
    bucket_block("by_beat_size_median_split", "beat_size_bucket", ["big_beat", "small_beat"])
    add("by_beat_size_median_split", "median beat used as split, %", df["rev_vs_mid_pct"].notna().sum(), round(med, 2))
    bucket_block("by_guide_direction_raw", "guide_direction", ["accel", "flat", "decel"])
    bucket_block("by_guide_direction_cushion_adj", "guide_direction_cushion_adj", ["accel", "flat", "decel"])
    bucket_block("by_nights_direction", "nights_direction", ["accel", "flat", "decel"])
    # post-COVID-lap version: 2022Q2 on, so the 2021 reopening swings do not drive the buckets
    df["nights_direction_post_lap"] = np.where(df["print_quarter"] >= "2022Q2", df["nights_direction"], None)
    bucket_block("by_nights_direction_2022Q2_on", "nights_direction_post_lap", ["accel", "flat", "decel"])
    # two-bucket version so a permutation and Fisher p can be attached
    df["nights_accel_binary"] = np.where(df["nights_direction"].isna(), None,
                                         np.where(df["nights_direction"] == "accel", "accel", "not_accel"))
    bucket_block("by_nights_accel_binary", "nights_accel_binary", ["accel", "not_accel"])
    df["nights_accel_binary_post_lap"] = np.where(df["print_quarter"] >= "2022Q2", df["nights_accel_binary"], None)
    bucket_block("by_nights_accel_binary_2022Q2_on", "nights_accel_binary_post_lap", ["accel", "not_accel"])
    bucket_block("by_margin_vs_guide", "margin_vs_guide", ["above", "in_line", "below"])
    bucket_block("by_fy_floor_action", "fy_floor_action", ["raised", "held", "introduced", "none"])

    D = "diagnostic_corr_vs_excess_1d"

    def corr_block(name, x, y, block=D):
        m = x.notna() & y.notna()
        xx, yy = x[m].values.astype(float), y[m].values.astype(float)
        n = len(xx)
        pr, pp = stats.pearsonr(xx, yy)
        sr, sp = stats.spearmanr(xx, yy)
        pperm = perm_p_corr(xx, yy)
        add(block, f"{name}: Pearson r", n, round(pr, 3), f"p={pp:.3f}")
        add(block, f"{name}: Spearman rho", n, round(sr, 3), f"p={sp:.3f}")
        add(block, f"{name}: permutation p (Pearson)", n, round(pperm, 3), f"{N_PERM} shuffles")

    corr_block("revenue beat vs midpoint %", df["rev_vs_mid_pct"], df["excess_1d_pct"])
    corr_block("revenue beat vs top %", df["rev_vs_high_pct"], df["excess_1d_pct"])
    corr_block("next-q guide implied yoy minus reported yoy, pp", df["guide_vs_reported_yoy_pp"], df["excess_1d_pct"])
    corr_block("nights acceleration, pp", df["nights_accel_pp"], df["excess_1d_pct"])
    corr_block("nights y/y, %", df["nights_yoy_pct"], df["excess_1d_pct"])
    corr_block("margin y/y change, pp", df["margin_yoy_pp"], df["excess_1d_pct"])
    corr_block("revenue y/y, %", df["revenue_yoy_pct"], df["excess_1d_pct"])
    corr_block("excess 1d vs excess 20d (post-print drift?)", df["excess_1d_pct"], df["excess_20d_pct"])
    corr_block("excess 1d vs excess 5d", df["excess_1d_pct"], df["excess_5d_pct"])

    # Baseline demonstration for protocol 4.3: revenue forecast error of three
    # naive forecasters on prints with a numeric guide and >=3 prior resolved guides.
    B = "baseline_demo_revenue_forecast"
    errs = {"guide_midpoint": [], "guide_mid_plus_prior_cushion": [], "seasonal_naive": []}
    for _, rr in df.iterrows():
        q = rr["print_quarter"]
        if pd.isna(rr["guide_mid_musd"]):
            continue
        prior = guide[(guide["guided_quarter"] < q)]["actual_vs_mid_pct"].dropna()
        if len(prior) < 3:
            continue
        act = rr["revenue_musd"]
        f_mid = rr["guide_mid_musd"]
        f_cush = f_mid * (1 + prior.mean() / 100)
        ya, pq = year_ago(q), prior_q(q)
        f_sn = revenue[ya] * (1 + rev_yoy[pq] / 100)
        for k, f in (("guide_midpoint", f_mid), ("guide_mid_plus_prior_cushion", f_cush), ("seasonal_naive", f_sn)):
            errs[k].append((f / act - 1) * 100)
    for k, e in errs.items():
        e = np.array(e)
        add(B, f"{k}: MAE %", len(e), round(float(np.abs(e).mean()), 2), "prints 2022Q3 to 2026Q2; forecast minus actual, % of actual")
        add(B, f"{k}: RMSE %", len(e), round(float(np.sqrt((e ** 2).mean())), 2))
        add(B, f"{k}: max abs error %", len(e), round(float(np.abs(e).max()), 2))
        add(B, f"{k}: mean signed error %", len(e), round(float(e.mean()), 2), "negative = forecast below actual")

    n_tests = sum(1 for s in S if s["block"] == D and "Pearson r" in s["cell"])
    add("multiple_comparisons", "number of correlation tests in this file", n_tests, n_tests,
        "expected false 5% hits at alpha=0.05 is n_tests*0.05; Bonferroni alpha is 0.05/n_tests")
    add("multiple_comparisons", "Bonferroni alpha for this file", n_tests, round(0.05 / n_tests, 4))
    add("multiple_comparisons", "smallest detectable |r| at p<0.05, n=23 (two-sided)", 23, 0.413,
        "r_crit = t_crit/sqrt(t_crit^2+n-2), t_crit(21 df)=2.080")
    add("multiple_comparisons", "smallest detectable |r| at p<0.05, n=19 (two-sided)", 19, 0.456)

    pd.DataFrame(S).to_csv(os.path.join(OUT_DIR, "01_print_base_rates_summary.csv"), index=False)

    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 60)
    cols = ["print_quarter", "revenue_yoy_pct", "rev_vs_mid_pct", "rev_vs_high_pct", "guide_direction",
            "guide_direction_cushion_adj", "nights_yoy_pct", "nights_accel_pp", "adj_ebitda_margin_pct",
            "margin_vs_guide", "fy_floor_action", "abnb_1d_pct", "excess_1d_pct", "excess_5d_pct", "excess_20d_pct"]
    print(df[cols].to_string(index=False))
    print()
    print(pd.DataFrame(S).to_string(index=False, max_colwidth=75))


if __name__ == "__main__":
    sys.exit(main())
