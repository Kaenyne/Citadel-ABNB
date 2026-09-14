"""WS20 step 3: the LIVE comparison table.

Every method LIVE forecast (vintage 2026-09-11, the harness TODAY) for 3Q26, 4Q26, FY26,
1Q27-4Q27, FY27 (+ FY28 where a method registered 2028 quarters), side by side with WS03
consensus (LSEG 11 Sep, Bloomberg 5 Sep pull), the management floor, the WS31b forward
profiles and the WS30 margin walk.

FY aggregation convention (stated so it can be checked): FY EBITDA $ = sum of the quarterly
LIVE points, plus the realised 1Q26/2Q26 actuals for FY26. FY margin = FY EBITDA $ over ONE
common revenue denominator, the harness PIT revenue leg at TODAY, so the table compares
margin models and not revenue legs. Quarterly margins are each method own point.
"""
from pathlib import Path
import glob
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
HARN = ROOT / "data" / "processed" / "margin_build" / "10_harness_margin"
REG = ROOT / "data" / "processed" / "margin_build" / "registry"
OUT = ROOT / "data" / "processed" / "margin_build" / "20_scoreboard"
TODAY = "2026-09-11"
TARGETS = ["adj_ebitda_musd", "adj_ebitda_margin_pct", "eps_diluted", "fcf_musd",
           "op_income_musd", "net_income_musd"]
QORDER = ["2026Q3", "2026Q4", "2027Q1", "2027Q2", "2027Q3", "2027Q4",
          "2028Q1", "2028Q2", "2028Q3", "2028Q4"]
ORACLE = "revknown|nightsknown|ebitda_known"


def load_live():
    rows = []
    for f in glob.glob(str(REG / "*.csv")):
        d = pd.read_csv(f)
        d = d[(d.window == "LIVE") & (d.vintage_date == TODAY) & (d.target.isin(TARGETS))]
        if len(d):
            rows.append(d)
    r = pd.concat(rows, ignore_index=True)
    r["spec_id"] = r["spec_id"].fillna("(none)")
    if "PIT" in set(r.prior_basis):
        r = r[r.prior_basis == "PIT"]
    return r


def preferred_specs(master, live_specs=None):
    """Per (method, object, target) pick ONE spec to carry into the LIVE table.

    Rule (pre-registered): among non-oracle specs with n>=6 at W2 h=0, PIT, prefer those
    with survives_both_windows == True; take the lowest W2 h=0 equal-weighted MAE among
    them. Fall back to the lowest W2 MAE ignoring survival, then to W1 h=0."""
    m = master[(master.weighting == "equal") & (master.horizon_q == 0)
               & (~master.spec_id.str.contains(ORACLE, case=False, na=False))].copy()
    if live_specs is not None:
        m = m[[(a, b, c, d) in live_specs for a, b, c, d in
               zip(m.method, m.object, m.target, m.spec_id)]]
    m["surv"] = m["survives_both_windows"].astype(str).str.lower().isin(["true", "yes", "1"])
    best = {}
    passes = [(m[(m.window == "W2") & (m.n >= 6) & m.surv], "W2+survives"),
              (m[(m.window == "W2") & (m.n >= 6)], "W2"),
              (m[(m.window == "W1") & (m.n >= 8)], "W1")]
    for d, label in passes:
        d = d.sort_values("mae")
        for (meth, obj, tgt), g in d.groupby(["method", "object", "target"]):
            best.setdefault((meth, obj, tgt), (g.iloc[0]["spec_id"], label, float(g.iloc[0]["mae"])))
    return best


def main():
    master = pd.read_csv(OUT / "20_scoreboard_master.csv")
    r = load_live()
    live_specs = set(zip(r.method, r.object, r.target, r.spec_id))
    best = preferred_specs(master, live_specs)

    rev = pd.read_csv(HARN / "revenue_leg_pit.csv")
    rev = rev[(rev.vintage_date == TODAY) & (rev.prior_basis == "PIT")]
    revq = dict(zip(rev.quarter, rev.revenue_musd_forecast))
    tg = pd.read_csv(HARN / "targets.csv")
    act = tg.set_index("quarter")
    revq["2026Q1"] = float(act.loc["2026Q1", "revenue_musd"])
    revq["2026Q2"] = float(act.loc["2026Q2", "revenue_musd"])

    recs = []
    for (meth, obj, spec, tgt), g in r.groupby(["method", "object", "spec_id", "target"]):
        b = best.get((meth, obj, tgt))
        pref = bool(b and b[0] == spec)
        bw = b[1] if b else ""
        bm = b[2] if b else np.nan
        qs = dict(zip(g.quarter, g.point))
        sd = dict(zip(g.quarter, g.sd)) if "sd" in g.columns else {}
        base = dict(source_type="baseline" if meth == "baselines-margin" else "method",
                    source=f"{meth}|{obj}|{spec}", method=meth, object=obj, spec_id=spec,
                    preferred_spec=pref, backtest_win=bw, backtest_mae=bm, vintage=TODAY)
        for q in QORDER:
            if q in qs:
                recs.append(dict(base, target=tgt, period=q, value=qs[q],
                                 sd=sd.get(q, np.nan), note=""))
        if tgt == "adj_ebitda_musd":
            if all(q in qs for q in ("2026Q3", "2026Q4")):
                fy26 = (float(act.loc["2026Q1", "adj_ebitda_musd"])
                        + float(act.loc["2026Q2", "adj_ebitda_musd"])
                        + qs["2026Q3"] + qs["2026Q4"])
                den = revq["2026Q1"] + revq["2026Q2"] + revq["2026Q3"] + revq["2026Q4"]
                recs.append(dict(base, target="adj_ebitda_musd", period="FY26", value=fy26,
                                 sd=np.nan, note="1H26 actual + method 3Q/4Q"))
                recs.append(dict(base, target="adj_ebitda_margin_pct", period="FY26",
                                 value=100 * fy26 / den, sd=np.nan,
                                 note="EBITDA sum / common PIT revenue leg"))
            q27 = ["2027Q1", "2027Q2", "2027Q3", "2027Q4"]
            if all(q in qs for q in q27):
                fy27 = sum(qs[q] for q in q27)
                den = sum(revq[q] for q in q27)
                recs.append(dict(base, target="adj_ebitda_musd", period="FY27", value=fy27,
                                 sd=np.nan, note="sum of method 1Q27-4Q27"))
                recs.append(dict(base, target="adj_ebitda_margin_pct", period="FY27",
                                 value=100 * fy27 / den, sd=np.nan,
                                 note="EBITDA sum / common PIT revenue leg"))
            q28 = ["2028Q1", "2028Q2", "2028Q3", "2028Q4"]
            if all(q in qs for q in q28):
                recs.append(dict(base, target="adj_ebitda_musd", period="FY28",
                                 value=sum(qs[q] for q in q28), sd=np.nan,
                                 note="sum of method 1Q28-4Q28"))
    live = pd.DataFrame(recs)

    # ---- external comparators ------------------------------------------------
    ext = []
    cc = pd.read_csv(ROOT / "data" / "processed" / "margin_build" / "03_consensus_pit"
                     / "03_current_consensus.csv")
    pmap = {"3Q26": "2026Q3", "4Q26": "2026Q4", "FY26": "FY26", "FY27": "FY27", "FY28": "FY28"}
    for _, row in cc.iterrows():
        per = pmap.get(str(row["period"]))
        if per is None or not isinstance(row["vendor"], str):
            continue
        if row["vendor"].startswith("LSEG"):
            vend = "LSEG"
        elif row["vendor"].startswith("Bloomberg"):
            vend = "Bloomberg"
        else:
            continue
        for tgt, col in (("adj_ebitda_musd", "ebitda_mean"),
                         ("adj_ebitda_margin_pct", "implied_margin_pct"),
                         ("eps_diluted", "eps_mean"), ("fcf_musd", "fcf_mean"),
                         ("op_income_musd", "ebit_mean"), ("net_income_musd", "netprofit_mean")):
            v = row.get(col)
            if pd.notna(v):
                ext.append(dict(source_type="consensus", source=f"{vend}", method=vend,
                                object="consensus", spec_id="", target=tgt, period=per,
                                value=float(v),
                                sd=(row.get("ebitda_sd") if tgt == "adj_ebitda_musd" else np.nan),
                                preferred_spec=True, backtest_win="", backtest_mae=np.nan,
                                vintage=str(row["as_of_row_date"]), note=str(row["vendor"])[:60]))
    ext.append(dict(source_type="management", source="FY2026 floor (2Q26 letter 2026-08-06)",
                    method="management", object="guide", spec_id="floor",
                    target="adj_ebitda_margin_pct", period="FY26", value=35.5, sd=np.nan,
                    preferred_spec=True, backtest_win="", backtest_mae=np.nan,
                    vintage="2026-08-06", note="at least 35.5 pct - a floor, not a point"))
    ext.append(dict(source_type="management", source="3Q26 sentence (2Q26 letter 2026-08-06)",
                    method="management", object="guide", spec_id="ceiling",
                    target="adj_ebitda_margin_pct", period="2026Q3", value=50.085470, sd=np.nan,
                    preferred_spec=True, backtest_win="", backtest_mae=np.nan,
                    vintage="2026-08-06",
                    note="margin down slightly vs 3Q25 -> ceiling at the 3Q25 actual 50.09 pct"))

    p31 = pd.read_csv(ROOT / "data" / "processed" / "overnight"
                      / "31b_forward_margin_by_profile.csv")
    qmap = {"3Q26": "2026Q3", "4Q26": "2026Q4", "1Q27": "2027Q1", "2Q27": "2027Q2",
            "3Q27": "2027Q3", "4Q27": "2027Q4", "FY26": "FY26", "FY27": "FY27", "FY28": "FY28",
            "2026": "FY26", "2027": "FY27", "2028": "FY28"}
    for _, row in p31.iterrows():
        per = qmap.get(str(row["period"]))
        if per is None:
            continue
        if row["line"] == "adj_ebitda":
            tgt, val = "adj_ebitda_musd", row["value_musd"]
        elif row["line"] == "margin":
            tgt, val = "adj_ebitda_margin_pct", row["pct_of_revenue"]
        else:
            continue
        if pd.isna(val):
            continue
        ext.append(dict(source_type="profile_ws31b", source=f"WS31b {row['profile']}/{row['scenario']}",
                        method="ws31b", object=str(row["profile"]), spec_id=str(row["scenario"]),
                        target=tgt, period=per, value=float(val), sd=np.nan,
                        preferred_spec=(str(row["scenario"]) == "base"), backtest_win="",
                        backtest_mae=np.nan, vintage="2026-09-08",
                        note="overnight/31b_forward_margin_by_profile.csv"))

    w30 = ROOT / "data" / "processed" / "overnight" / "30_margin_walk.csv"
    if w30.exists():
        d = pd.read_csv(w30)
        cand = [c for c in d.columns if "margin" in c.lower() or "ebitda" in c.lower()]
        pcol = "quarter" if "quarter" in d.columns else d.columns[0]
        for _, row in d.iterrows():
            per = qmap.get(str(row[pcol]), str(row[pcol]))
            for c in cand:
                v = row.get(c)
                if pd.isna(v):
                    continue
                tgt = "adj_ebitda_margin_pct" if "margin" in c.lower() else "adj_ebitda_musd"
                ext.append(dict(source_type="walk_ws30", source=f"WS30 {c}", method="ws30",
                                object="walk", spec_id=c, target=tgt, period=per,
                                value=float(v), sd=np.nan, preferred_spec=False,
                                backtest_win="", backtest_mae=np.nan, vintage="2026-09-08",
                                note="overnight/30_margin_walk.csv"))

    allrows = pd.concat([live, pd.DataFrame(ext)], ignore_index=True)
    allrows = allrows[allrows.period.isin(QORDER + ["FY26", "FY27", "FY28"])]
    allrows.to_csv(OUT / "20_live_comparison.csv", index=False)

    # spread across the preferred spec of each METHOD object (baselines excluded: the
    # seasonal / pct-of-revenue baselines are not candidate forecasts and blow the range up)
    sp = allrows[(allrows.source_type == "method") & (allrows.preferred_spec)]
    g = sp.groupby(["target", "period"])["value"]
    spread = pd.DataFrame({"n_objects": g.count(), "min": g.min(), "median": g.median(),
                           "mean": g.mean(), "max": g.max()}).reset_index()
    spread["spread_max_minus_min"] = spread["max"] - spread["min"]
    spb = allrows[(allrows.source_type.isin(["method", "baseline"])) & (allrows.preferred_spec)]
    gb = spb.groupby(["target", "period"])["value"]
    spread = spread.merge(pd.DataFrame({"n_incl_baselines": gb.count(),
                                        "min_incl_baselines": gb.min(),
                                        "max_incl_baselines": gb.max()}).reset_index(),
                          on=["target", "period"], how="left")
    for vend in ["LSEG", "Bloomberg"]:
        c = (allrows[allrows.method == vend][["target", "period", "value"]]
             .rename(columns={"value": vend.lower()}).drop_duplicates(["target", "period"]))
        spread = spread.merge(c, on=["target", "period"], how="left")
    spread["median_minus_lseg"] = spread["median"] - spread["lseg"]

    # FY margin is denominator-sensitive: the harness naive revenue leg for 2027 is well
    # above Street. Recompute the FY margin of the method median on Street revenue.
    rev_lseg = {"FY26": float(cc[(cc.period == "FY26") & (cc.vendor.astype(str).str.startswith("LSEG"))]["revenue_mean"].iloc[0]),
                "FY27": float(cc[(cc.period == "FY27") & (cc.vendor.astype(str).str.startswith("LSEG"))]["revenue_mean"].iloc[0])}
    rev_harness = {"FY26": revq["2026Q1"] + revq["2026Q2"] + revq["2026Q3"] + revq["2026Q4"],
                   "FY27": sum(revq[q] for q in ["2027Q1", "2027Q2", "2027Q3", "2027Q4"])}
    extra = []
    for fy in ["FY26", "FY27"]:
        med = spread[(spread.target == "adj_ebitda_musd") & (spread.period == fy)]["median"]
        if len(med):
            extra.append(dict(period=fy, method_median_ebitda_musd=float(med.iloc[0]),
                              revenue_harness_leg=rev_harness[fy], revenue_lseg=rev_lseg[fy],
                              margin_on_harness_leg=100 * float(med.iloc[0]) / rev_harness[fy],
                              margin_on_lseg_revenue=100 * float(med.iloc[0]) / rev_lseg[fy]))
    pd.DataFrame(extra).to_csv(OUT / "20_live_fy_margin_denominator.csv", index=False)

    spread.to_csv(OUT / "20_live_spread.csv", index=False)
    print("live", allrows.shape, "spread", spread.shape)


if __name__ == "__main__":
    main()
