"""M5 — backtest tables, the post-guide h=1 supplementary test, the LIVE forecast and the 5 Nov card.

Reads the grid written by build.py; writes the note's tables to
data/processed/margin_build/M5_street_bias/.  Interpreter: py -3.13.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats as st

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"))
from harness_margin import W, TODAY, load_targets  # noqa: E402

OUT = REPO / "data" / "processed" / "margin_build" / "M5_street_bias"
WS03 = REPO / "data" / "processed" / "margin_build" / "03_consensus_pit"
EBITDA, MARGIN, REVENUE = "adj_ebitda_musd", "adj_ebitda_margin_pct", "revenue_musd"
HALF_LIFE, KAPPA_B = 4.0, 2.0


def rwts(qs):
    idx = np.array([int(q[:4]) * 4 + int(q[-1]) for q in qs], dtype=float)
    return 0.5 ** ((idx.max() - idx) / HALF_LIFE)


# ------------------------------------------------------------------ 1. backtest vs street
def backtest_table():
    g = pd.read_csv(OUT / "M5_grid_all_vintages.csv")
    g["vintage_date"] = pd.to_datetime(g["vintage_date"]).dt.date
    g = g[(g["scenario"] == "base") & g["actual"].notna() & (g["src"] == "street_pit")]
    rows = []
    for win, vds, tgts in (("W1", set(W.GUIDE_DATES_W1), set(W.W1_TARGETS)),
                           ("W2", set(W.GUIDE_DATES_W2), set(W.W2_TARGETS))):
        sub = g[g["vintage_date"].isin(vds) & g["quarter"].isin(tgts)]
        for tgt in (EBITDA, MARGIN):
            for h in (0, 1):
                s = sub[(sub["target"] == tgt) & (sub["horizon_q"] == h)]
                if not len(s):
                    continue
                base = s.drop_duplicates(["quarter", "vintage_date"])
                be = np.abs(base["street"] - base["actual"]).to_numpy(float)
                wb = rwts(base["quarter"].tolist())
                b_mae, b_rw = float(be.mean()), float(np.sum(wb * be) / wb.sum())
                b_bias = float((base["street"] - base["actual"]).mean())
                rows.append(dict(window=win, target=tgt, horizon_q=h, object="street(raw baseline)",
                                 spec_id="-", n=len(base), mae=b_mae, rw_mae=b_rw, bias=b_bias,
                                 mae_ratio_street=1.0, rw_mae_ratio_street=1.0, passes=False))
                for (obj, spec), gg in s.groupby(["object", "spec_id"]):
                    e = np.abs(gg["err"]).to_numpy(float)
                    w = rwts(gg["quarter"].tolist())
                    mae, rw = float(e.mean()), float(np.sum(w * e) / w.sum())
                    rows.append(dict(window=win, target=tgt, horizon_q=h, object=obj, spec_id=spec,
                                     n=len(gg), mae=mae, rw_mae=rw, bias=float(gg["err"].mean()),
                                     mae_ratio_street=mae / b_mae, rw_mae_ratio_street=rw / b_rw,
                                     passes=bool(mae < b_mae and rw < b_rw)))
    t = pd.DataFrame(rows)
    t.to_csv(OUT / "M5_backtest_vs_street.csv", index=False)
    # pass-line verdict per (object, spec): needs all 8 cells (2 targets x 2 h x 2 windows)
    v = []
    for (obj, spec), gg in t[t["object"] != "street(raw baseline)"].groupby(["object", "spec_id"]):
        cells = gg[["window", "target", "horizon_q", "passes"]]
        v.append(dict(object=obj, spec_id=spec, cells=len(gg), cells_passed=int(gg["passes"].sum()),
                      pass_line=bool(gg["passes"].all()),
                      h0_cells_passed=int(gg[gg.horizon_q == 0]["passes"].sum()),
                      h0_all=bool(gg[gg.horizon_q == 0]["passes"].all()),
                      h1_all=bool(gg[gg.horizon_q == 1]["passes"].all())))
    v = pd.DataFrame(v).sort_values(["object", "spec_id"])
    v.to_csv(OUT / "M5_passline_verdict.csv", index=False)
    return t, v


# ------------------------------------------------------------------ 2. post-guide h=1
def post_guide_h1():
    """Supplementary (NOT registrable): the h=1 Street 5 trading days AFTER the guide.

    The stamp is later than the guide date, so it fails the harness PIT rule at that vintage and
    cannot be registered. It is the right comparison for 4Q26 at TODAY (11 Sep 2026), which sits
    five weeks after the 6 Aug guide and has already absorbed the post-guide revision.
    """
    d = pd.read_csv(WS03 / "03_consensus_at_dates.csv")
    d = d[d["found"].astype(str).str.lower() == "true"]
    t = load_targets()
    act = t[t["has_actual"]].set_index("quarter")
    rows = []
    for role, lab in (("next_q_pre_guide", "pre_guide"), ("next_q_post_guide_5td", "post_guide_5td")):
        for r in d[d["target_role"] == role].itertuples():
            q = r.target_period
            if q not in act.index or not np.isfinite(r.ebitda_mean):
                continue
            a = act.loc[q]
            rows.append(dict(basis=lab, guide_date=r.date, quarter=q,
                             street_ebitda=float(r.ebitda_mean),
                             street_margin=float(r.implied_margin_pct),
                             actual_ebitda=float(a[EBITDA]), actual_margin=float(a[MARGIN]),
                             s_usd=float(a[EBITDA] - r.ebitda_mean),
                             s_pt=float(a[MARGIN] - r.implied_margin_pct)))
    x = pd.DataFrame(rows)
    x.to_csv(OUT / "M5_h1_preguide_vs_postguide.csv", index=False)
    summ = []
    for (lab, win, q0) in [(l, w, q) for l in ("pre_guide", "post_guide_5td")
                           for w, q in (("all", "2021Q1"), ("W1", "2023Q1"), ("W2", "2024Q1"),
                                        ("last8", "2024Q3"))]:
        s = x[(x["basis"] == lab) & (x["quarter"] >= q0)]
        if not len(s):
            continue
        w_ = rwts(s["quarter"].tolist())
        summ.append(dict(basis=lab, window=win, n=len(s), mean_pt=s["s_pt"].mean(),
                         sd_pt=s["s_pt"].std(), rw_mean_pt=float(np.sum(w_ * s["s_pt"]) / w_.sum()),
                         mae_pt=s["s_pt"].abs().mean(), mean_usd=s["s_usd"].mean(),
                         mae_usd=s["s_usd"].abs().mean(),
                         share_beats=float((s["s_pt"] > 0).mean())))
    # bias-corrected post-guide backtest (PIT: only quarters printed before this guide date)
    bt = []
    pg = x[x["basis"] == "post_guide_5td"].sort_values("quarter").reset_index(drop=True)
    pdm = {r.quarter: r.print_date for r in t.itertuples() if pd.notna(r.print_date)}
    pg["print_date"] = pg["quarter"].map(pdm)
    pg["guide_date_d"] = pd.to_datetime(pg["guide_date"]).dt.date
    for i, r in pg.iterrows():
        pool = pg[(pg["print_date"] <= r["guide_date_d"]) & (pg["quarter"] >= "2022Q1")]
        if len(pool) < 3:
            continue
        w_ = rwts(pool["quarter"].tolist())
        n_eff = w_.sum()
        b_pt = float(np.sum(w_ * pool["s_pt"]) / (n_eff + KAPPA_B))
        # $ correction is the margin-point bias applied to the Street's own revenue mean.
        # (A % bias is unusable here: the h=1 pool contains Q1s whose Street EBITDA is ~$70-300M,
        #  so 2022Q1's +209% surprise dominates any percentage average.)
        rev_impl = 100.0 * r["street_ebitda"] / r["street_margin"]
        corr_usd = (r["street_margin"] + b_pt) / 100.0 * rev_impl
        bt.append(dict(quarter=r["quarter"], guide_date=r["guide_date"], n_pool=len(pool),
                       b_pt=b_pt, street_revenue_impl=rev_impl,
                       street_pt=r["street_margin"], corr_pt=r["street_margin"] + b_pt,
                       actual_pt=r["actual_margin"],
                       err_street_pt=r["street_margin"] - r["actual_margin"],
                       err_corr_pt=r["street_margin"] + b_pt - r["actual_margin"],
                       street_usd=r["street_ebitda"], corr_usd=corr_usd,
                       actual_usd=r["actual_ebitda"],
                       err_street_usd=r["street_ebitda"] - r["actual_ebitda"],
                       err_corr_usd=corr_usd - r["actual_ebitda"]))
    bt = pd.DataFrame(bt)
    bt.to_csv(OUT / "M5_h1_postguide_backtest.csv", index=False)
    pgs = []
    for win, q0 in (("W1", "2023Q1"), ("W2", "2024Q1")):
        s = bt[bt["quarter"] >= q0]
        if not len(s):
            continue
        w_ = rwts(s["quarter"].tolist())
        for lab, es, ec in (("margin_pt", s["err_street_pt"], s["err_corr_pt"]),
                            ("ebitda_musd", s["err_street_usd"], s["err_corr_usd"])):
            pgs.append(dict(window=win, target=lab, n=len(s),
                            street_mae=es.abs().mean(), corr_mae=ec.abs().mean(),
                            street_rw_mae=float(np.sum(w_ * es.abs()) / w_.sum()),
                            corr_rw_mae=float(np.sum(w_ * ec.abs()) / w_.sum()),
                            ratio=ec.abs().mean() / es.abs().mean(),
                            rw_ratio=float(np.sum(w_ * ec.abs()) / np.sum(w_ * es.abs()))))
    pgs = pd.DataFrame(pgs)
    summary = pd.DataFrame(summ)
    summary.to_csv(OUT / "M5_h1_basis_summary.csv", index=False)
    pgs.to_csv(OUT / "M5_h1_postguide_scoreboard.csv", index=False)
    return summary, pgs, bt, x


# ------------------------------------------------------------------ 3. LIVE and the card
def live_table(pgs_bias):
    g = pd.read_csv(OUT / "M5_grid_all_vintages.csv")
    g["vintage_date"] = pd.to_datetime(g["vintage_date"]).dt.date
    live = g[(g["vintage_date"] == TODAY)].copy()
    keep = live[live["spec_id"].isin(["rw_hl4", "rw_hl4_med"])]
    keep.to_csv(OUT / "M5_live_all_specs.csv", index=False)
    return keep


REG = REPO / "data" / "processed" / "margin_build" / "registry"
QC = ["q05", "q10", "q25", "q50", "q75", "q90", "q95"]


def street_current():
    cur = pd.read_csv(WS03 / "03_current_consensus.csv")
    cur = cur[cur["vendor"].astype(str).str.strip() == "LSEG"].copy()
    cur["period"] = cur["period"].astype(str).str.upper()
    c = cur.drop_duplicates("period").set_index("period")
    out = {}
    for p in ("3Q26", "4Q26", "FY26", "FY27", "FY28"):
        if p in c.index:
            out[p] = dict(street_ebitda=float(c.loc[p, "ebitda_mean"]),
                          street_revenue=float(c.loc[p, "revenue_mean"]),
                          street_margin=float(c.loc[p, "implied_margin_pct"]),
                          n_est=None if pd.isna(c.loc[p, "ebitda_n"]) else float(c.loc[p, "ebitda_n"]),
                          street_sd=None if pd.isna(c.loc[p, "ebitda_sd"]) else float(c.loc[p, "ebitda_sd"]))
    return out


def live_card():
    """LIVE table (3Q26, 4Q26, 1Q27-4Q27), P(beat) and the annual roll-up."""
    reg = pd.concat([pd.read_csv(REG / f"street-bias__{o}.csv")
                     for o in ("street_plus_bias", "street_plus_flowthrough",
                               "dispersion_conditioned")], ignore_index=True)
    reg = reg[(reg["window"] == "LIVE") & (reg["prior_basis"] == "PIT") &
              (reg["vintage_date"].astype(str) == str(TODAY))]
    g = pd.read_csv(OUT / "M5_grid_all_vintages.csv")
    g = g[(g["vintage_date"].astype(str) == str(TODAY))]
    sc = street_current()

    # LIVE point table with quantiles (base scenario, both primary specs)
    tbl = reg[reg["spec_id"].str.startswith(("rw_hl4", "rw_hl4_med"))].copy()
    tbl = tbl[["object", "spec_id", "target", "quarter", "horizon_q", "point", "sd"] + QC + ["notes"]]
    tbl.to_csv(OUT / "M5_live_forecasts.csv", index=False)

    # P(beat the Street) for 3Q26 and 4Q26, per object/spec/scenario
    rows = []
    for (obj, spec, q, tgt), gg in g[g["spec_id"].isin(["rw_hl4", "rw_hl4_med"])].groupby(
            ["object", "spec_id", "quarter", "target"]):
        if q not in ("2026Q3", "2026Q4"):
            continue
        per = "3Q26" if q == "2026Q3" else "4Q26"
        r0 = reg[(reg["object"] == obj) & (reg["spec_id"] == spec) & (reg["quarter"] == q) &
                 (reg["target"] == tgt)]
        if not len(r0):
            continue
        sd = float(r0["sd"].iloc[0])
        street = sc[per]["street_ebitda"] if tgt == EBITDA else sc[per]["street_margin"]
        for r in gg.itertuples():
            p_beat = float(1.0 - st.norm.cdf((street - r.point) / sd)) if sd > 0 else np.nan
            rows.append(dict(period=per, target=tgt, object=obj, spec_id=spec, scenario=r.scenario,
                             point=r.point, street=street, surprise=r.point - street, sd=sd,
                             p_beat_street=p_beat))
    pb = pd.DataFrame(rows).sort_values(["period", "target", "object", "spec_id", "scenario"])
    pb.to_csv(OUT / "M5_prob_beat.csv", index=False)

    # annual roll-up: FY26 = 1H26 actual + 3Q26 + 4Q26 forecast; FY27 = the four 2027 quarters
    t = load_targets()
    h1 = t[t["quarter"].isin(["2026Q1", "2026Q2"])]
    h1_e, h1_r = float(h1[EBITDA].sum()), float(h1[REVENUE].sum())
    ws06 = pd.read_csv(REPO / "data" / "processed" / "margin_build" / "06_fy27_path_v2" /
                       "06_revenue_path_3q26_4q27_v2b.csv")
    ws06 = ws06[ws06["line"] == "revenue_musd"]
    rev = {(r.quarter, r.scenario): float(r.value) for r in ws06.itertuples()}
    ann = []
    for obj in ("street_plus_bias", "street_plus_flowthrough", "dispersion_conditioned"):
        for spec in ("rw_hl4", "rw_hl4_med"):
            for scen in ("base", "bear", "bull"):
                sub = g[(g["object"] == obj) & (g["spec_id"] == spec) & (g["target"] == EBITDA) &
                        (g["scenario"] == scen)]
                if not len(sub):
                    continue
                e = {r.quarter: r.point for r in sub.itertuples()}
                if "2026Q3" not in e or "2026Q4" not in e:
                    continue
                r26 = h1_r + sum(rev.get((f"{q[-1]}Q26", scen), np.nan) for q in ("2026Q3", "2026Q4"))
                fy26_e = h1_e + e["2026Q3"] + e["2026Q4"]
                row = dict(object=obj, spec_id=spec, scenario=scen, fy="FY26",
                           ebitda_musd=fy26_e, revenue_musd=r26, margin_pct=100 * fy26_e / r26,
                           street_ebitda=sc["FY26"]["street_ebitda"],
                           street_margin=sc["FY26"]["street_margin"],
                           basis="1H26 actual + 3Q26 (h=0) + 4Q26 (h=1) forecasts")
                ann.append(row)
                q27 = [f"2027Q{i}" for i in (1, 2, 3, 4)]
                if all(q in e for q in q27) and scen == "base":
                    e27 = sum(e[q] for q in q27)
                    r27 = sum(rev.get((f"{q[-1]}Q27", "base"), np.nan) for q in q27)
                    ann.append(dict(object=obj, spec_id=spec, scenario=scen, fy="FY27",
                                    ebitda_musd=e27, revenue_musd=r27,
                                    margin_pct=100 * e27 / r27,
                                    street_ebitda=sc["FY27"]["street_ebitda"],
                                    street_margin=sc["FY27"]["street_margin"],
                                    basis="4 x 2027 quarters, Street leg allocated from the FY27 "
                                          "consensus with PIT seasonal shares (spec _fyalloc)"))
    ann = pd.DataFrame(ann)
    ann.to_csv(OUT / "M5_street_bias_annual_forecasts.csv", index=False)
    json.dump(sc, open(OUT / "M5_street_current.json", "w"), indent=2)
    return tbl, pb, ann, sc


PASS_SPECS = [("dispersion_conditioned", "rw_hl4"), ("dispersion_conditioned", "rw_hl4_med"),
              ("dispersion_conditioned", "rw_hl4_usd"), ("street_plus_flowthrough", "rw_hl4_med")]


def card_composite():
    """Equal-weight composite of the (object, spec) pairs that beat Street in all four h=0 cells."""
    reg = pd.concat([pd.read_csv(REG / f"street-bias__{o}.csv")
                     for o in ("street_plus_bias", "street_plus_flowthrough",
                               "dispersion_conditioned")], ignore_index=True)
    reg = reg[(reg["window"] == "LIVE") & (reg["prior_basis"] == "PIT") &
              (reg["vintage_date"].astype(str) == str(TODAY))]
    sc = street_current()
    rows = []
    for q, per in (("2026Q3", "3Q26"), ("2026Q4", "4Q26")):
        for tgt, key in ((EBITDA, "street_ebitda"), (MARGIN, "street_margin")):
            pts, sds = [], []
            for obj, spec in PASS_SPECS:
                r = reg[(reg["object"] == obj) & (reg["spec_id"] == spec) &
                        (reg["quarter"] == q) & (reg["target"] == tgt)]
                if len(r):
                    pts.append(float(r["point"].iloc[0]))
                    sds.append(float(r["sd"].iloc[0]))
            if not pts:
                continue
            pt, sd, sp = float(np.mean(pts)), float(np.mean(sds)), sc[per][key]
            rows.append(dict(period=per, target=tgt, n_specs=len(pts), point=pt, lo=min(pts),
                             hi=max(pts), sd=sd, street=sp, surprise=pt - sp,
                             p_beat=float(1 - st.norm.cdf((sp - pt) / sd)),
                             q10=pt - 1.2815515655 * sd, q90=pt + 1.2815515655 * sd,
                             validated="yes (h=0)" if q == "2026Q3"
                             else "NO (h=1 fails the pass line)"))
    c = pd.DataFrame(rows)
    c.to_csv(OUT / "M5_card_composite.csv", index=False)
    return c


def main():
    t, v = backtest_table()
    summary, pgs, bt, x = post_guide_h1()
    keep = live_table(pgs)
    print("\n=== pass-line verdict (all 8 cells) ===")
    print(v.to_string(index=False))
    print("\n=== h=0 only ===")
    print(t[(t.horizon_q == 0) & (t.spec_id.isin(["rw_hl4", "rw_hl4_med", "-"]))]
          .sort_values(["target", "window", "object"])
          [["window", "target", "object", "spec_id", "n", "mae", "rw_mae", "bias",
            "mae_ratio_street", "rw_mae_ratio_street", "passes"]].round(3).to_string(index=False))
    print("\n=== h=1 pre-guide vs post-guide Street ===")
    print(summary.round(3).to_string(index=False))
    print("\n=== post-guide h=1 bias-corrected backtest ===")
    print(pgs.round(3).to_string(index=False))
    print("\n=== LIVE (TODAY) ===")
    print(keep[keep.scenario == "base"][["quarter", "horizon_q", "object", "spec_id", "target",
                                         "point", "street", "src"]].round(2).to_string(index=False))
    tbl, pb, ann, sc = live_card()
    comp = card_composite()
    print("\n=== 5 Nov card composite (4 h=0-validated specs) ===")
    print(comp.round(3).to_string(index=False))
    print("\n=== LIVE with quantiles (rw_hl4) ===")
    print(tbl[tbl.spec_id == "rw_hl4"][["object", "target", "quarter", "point", "sd",
                                        "q10", "q50", "q90"]].round(2).to_string(index=False))
    print("\n=== P(beat the Street) ===")
    print(pb.round(3).to_string(index=False))
    print("\n=== annual ===")
    print(ann.round(2).to_string(index=False))
    print(json.dumps(sc, indent=2))
    # LIVE parameter values
    d = pd.read_csv(OUT / "M5_parameters_by_vintage.csv")
    print("\n=== LIVE parameters (TODAY) ===")
    print(d[d.vintage_date.astype(str) == str(TODAY)].round(4).to_string(index=False))
    return t, v, summary, pgs, keep, tbl, pb, ann


if __name__ == "__main__":
    main()
