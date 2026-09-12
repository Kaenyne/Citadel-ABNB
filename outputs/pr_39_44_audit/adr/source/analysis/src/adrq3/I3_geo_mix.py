"""I3. Geographic-mix term of ex-FX ADR for 3Q26, measured from the regional stays split.

Method (identical to H1_adr_card.py's quarterly geo-mix cell, which is the annual 07 method
applied per quarter): with year-ago regional ADR levels A0 (constant currency, 04 panel
`adr_<r>_usd_anchored` at 3Q25), year-ago regional nights shares s0 (3Q25) and regional
ex-FX ADR growth g,
    within  = sum(s0 A0 (1+g)) / sum(s0 A0) - 1
    total   = sum(s1 A0 (1+g)) / sum(s0 A0) - 1
    geo mix = total - within                      (pp of blended ex-FX ADR y/y)
where s1 = s0 (1+n_r) / sum(s0 (1+n_r)) are the current-quarter shares implied by regional
nights growth n_r. Only the RELATIVE growth across regions moves the term.

Regional growth cells for 3Q26 (all labelled in the output):
  E_vmatch_cw / E_vmatch_eq   E_aug vintage-matched review-weighted / equal-weighted stays,
                              3Q26 to date (measured, reviews = stays proxy)
  E_yoy_all_cw                E_aug within-vintage 3Q26-to-date regional index (measured)
  WSC_index_model / WSC_persistence / WS10_base   overnight-2 WS-C cells (modelled)
  disclosed_2Q26              the 2Q26 letter's regional buckets carried flat (assumed)
Regional ex-FX ADR growth g: zero (pure mix) and 2Q26 disclosed carried flat; the term moves
by under 0.1 pp between the two.

Backtest: for 1Q24-2Q26 the same construction with s1 projected from E's regional index
(vintage-matched and within-vintage) instead of the disclosed shares, against H's geo_mix_pp
(built on disclosed shares) and against ex-FX ADR itself with the note-08 protocol.

Outputs data/processed/adrq3/I/
  I3_geo_mix_3q26.csv        the 3Q26 term by growth source and g case
  I3_geo_mix_history.csv     1Q24-2Q26 measured-share versions vs H's disclosed-share term
  I3_geo_mix_backtest.csv    note-08 scoreboard rows
Run: py -3.13 analysis/src/adrq3/I3_geo_mix.py
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[3]
MAIN = Path(r"C:\Users\krish\citadel-abnb")
OUT = WT / "data/processed/adrq3/I"
sys.path.insert(0, str(WT / "analysis/src/adrq3"))
from I0_protocol import score, qkey, QORDER  # noqa: E402

REG = ["na", "emea", "latam", "apac"]
EMAP = {"NAM": "na", "EMEA": "emea", "LatAm": "latam", "APAC": "apac"}


def geo_mix(s0, a0, g, n):
    """s0, a0, g, n dicts by region; g and n in percent. Returns (geo_mix_pp, within_pp, total_pp)."""
    s1 = {r: s0[r] * (1 + n[r] / 100) for r in REG}
    tot = sum(s1.values())
    s1 = {r: s1[r] / tot * sum(s0.values()) for r in REG}
    base = sum(s0[r] * a0[r] for r in REG)
    within = sum(s0[r] * a0[r] * (1 + g[r] / 100) for r in REG) / base - 1
    total = sum(s1[r] * a0[r] * (1 + g[r] / 100) for r in REG) / base - 1
    return 100 * (total - within), 100 * within, 100 * total


def main():
    wide = pd.read_csv(MAIN / "data/processed/adr/04_regional_quarterly_wide.csv").set_index("quarter")
    H = pd.read_csv(WT / "data/processed/q3nowcast/H/adr_history_components.csv").set_index("quarter")
    E = WT / "data/processed/q3nowcast/E_aug"
    vm = pd.read_csv(E / "vintage_matched_nowcast.csv")
    mn = pd.read_csv(E / "monthly_nowcast_2026.csv")
    iq = pd.read_csv(E / "index_quarterly.csv")
    C5 = pd.read_csv(MAIN / "data/processed/overnight2/C/C5_regional_split_forecast.csv")
    C5 = C5[C5.period.eq("3Q26")].set_index("region")
    tp = pd.read_csv(MAIN / "data/processed/overnight2/C/regional_target_panel.csv")
    tp = tp[tp.metric.eq("nights_yoy_pct_destination")]

    # --- 3Q26 -----------------------------------------------------------------------------
    s0 = {r: wide.at["3Q25", f"nights_share_{r}_pct"] for r in REG}
    a0 = {r: wide.at["3Q25", f"adr_{r}_usd_anchored"] for r in REG}
    g_cases = {"g_zero": {r: 0.0 for r in REG},
               "g_2Q26_disclosed": {r: wide.at["2Q26", f"adr_yoy_exfx_{r}_pct"] for r in REG}}
    v3 = vm[vm.period.eq("3q26_to_date")].set_index("region")
    m3 = mn[mn.period.eq("2026-07")].set_index("region")  # within-vintage July, for reference
    growth = {
        "E_vmatch_cw": ({EMAP[k]: 100 * v3.at[k, "vmatch_cw"] for k in EMAP}, "measured: E_aug vintage-matched, review-weighted, 3Q26 to date"),
        "E_vmatch_eq": ({EMAP[k]: 100 * v3.at[k, "vmatch_eq"] for k in EMAP}, "measured: E_aug vintage-matched, equal-weighted markets, 3Q26 to date"),
        "E_within_cw": ({EMAP[k]: 100 * v3.at[k, "within_cw"] for k in EMAP}, "measured: E_aug within-vintage, review-weighted, 3Q26 to date (survivorship-biased level)"),
        "WSC_index_model": ({r: C5.at[r, "index_growth_pct"] for r in REG}, "modelled: overnight-2 WS-C relative-strength index split"),
        "WSC_persistence": ({r: C5.at[r, "persistence_growth_pct"] for r in REG}, "modelled: overnight-2 WS-C persistence split"),
        "WS10_base": ({r: C5.at[r, "comparison_ws10_base_pct"] for r in REG}, "modelled: WS10 base cells"),
        "disclosed_2Q26_flat": ({r: float(tp[tp.quarter.eq("2Q26") & tp.region.eq(r)].value.iloc[0]) for r in REG}, "assumed: 2Q26 letter regional buckets carried flat"),
    }
    rows = []
    for gname, (n, basis) in growth.items():
        for gcase, g in g_cases.items():
            mix, within, total = geo_mix(s0, a0, g, n)
            rows.append(dict(quarter="3Q26", growth_source=gname, g_case=gcase, geo_mix_pp=mix,
                             within_region_pp=within, total_pp=total,
                             **{f"nights_yoy_{r}_pct": n[r] for r in REG},
                             **{f"share_3q25_{r}_pct": s0[r] for r in REG}, basis=basis))
    r3 = pd.DataFrame(rows)
    r3["H_card_geo_mix_pp"] = -1.19
    r3["WSC_C5_index_model_pp"] = -1.24
    r3["actual_2025_pp"] = -1.58
    r3.to_csv(OUT / "I3_geo_mix_3q26.csv", index=False)

    # --- history 1Q24-2Q26: measured shares vs disclosed shares ---------------------------
    hist = []
    for q in [x for x in wide.index if qkey(x) >= qkey("1Q24") and x in H.index]:
        p = QORDER[qkey(q) - 4]
        if p not in wide.index:
            continue
        s0q = {r: wide.at[p, f"nights_share_{r}_pct"] for r in REG}
        a0q = {r: wide.at[p, f"adr_{r}_usd_anchored"] for r in REG}
        gq = {r: wide.at[q, f"adr_yoy_exfx_{r}_pct"] for r in REG}
        s1_disc = {r: wide.at[q, f"nights_share_{r}_pct"] for r in REG}
        n_disc = {r: 100 * (s1_disc[r] / s0q[r] - 1) for r in REG}  # relative growth implied by the disclosed shares
        row = dict(quarter=q, H_geo_mix_pp=H.at[q, "geo_mix_pp"],
                   rebuilt_from_disclosed_shares_pp=geo_mix(s0q, a0q, gq, n_disc)[0])
        for meas in ["yoy_vmatch", "yoy_all"]:
            for w in ["w_reviews", "w_equal"]:
                sub = iq[iq.quarter.eq(q) & iq.measure.eq(meas) & iq.region.isin(EMAP)]
                if len(sub) < 4 or sub[w].isna().any():
                    row[f"{meas}_{w}_pp"] = np.nan
                    continue
                n = {EMAP[k]: 100 * v for k, v in zip(sub.region, sub[w])}
                row[f"{meas}_{w}_pp"] = geo_mix(s0q, a0q, gq, n)[0]
                row[f"{meas}_{w}_g0_pp"] = geo_mix(s0q, a0q, {r: 0 for r in REG}, n)[0]
        # letters' regional nights buckets (what 04's shares rest on)
        sub = tp[tp.quarter.eq(q)].set_index("region")
        if all(r in sub.index for r in REG):
            row["letter_buckets_pp"] = geo_mix(s0q, a0q, gq, {r: float(sub.at[r, "value"]) for r in REG})[0]
        row["adr_exfx_yoy_pp"] = H.at[q, "adr_exfx_yoy_pp"]
        hist.append(row)
    hist = pd.DataFrame(hist)
    hist.to_csv(OUT / "I3_geo_mix_history.csv", index=False)

    # --- backtest ----------------------------------------------------------------------
    bt = []
    labels = list(hist.quarter)
    for col in ["yoy_vmatch_w_reviews_pp", "yoy_vmatch_w_equal_pp", "yoy_all_w_reviews_pp", "yoy_all_w_equal_pp", "letter_buckets_pp"]:
        if col not in hist:
            continue
        x, y = hist[col].values, hist.H_geo_mix_pp.values
        m = np.isfinite(x) & np.isfinite(y)
        row = score(f"{col} vs H geo_mix (disclosed shares)", x, y, labels, "1Q25", "yes")
        row["rmse_vs_H_pp"] = float(np.sqrt(np.mean((x[m] - y[m]) ** 2)))
        row["mean_diff_pp"] = float(np.mean(x[m] - y[m]))
        row["target"] = "H geo_mix_pp"
        bt.append(row)
        row2 = score(f"{col} vs ex-FX ADR y/y", x, hist.adr_exfx_yoy_pp.values, labels, "1Q25", "yes")
        row2["target"] = "adr_exfx_yoy_pp"
        bt.append(row2)
    row3 = score("H geo_mix_pp (disclosed shares) vs ex-FX ADR y/y", hist.H_geo_mix_pp.values,
                 hist.adr_exfx_yoy_pp.values, labels, "1Q25", "no (needs the print's regional lines)")
    row3["target"] = "adr_exfx_yoy_pp"
    bt.append(row3)
    bt = pd.DataFrame(bt)
    bt.to_csv(OUT / "I3_geo_mix_backtest.csv", index=False)

    pd.set_option("display.width", 250)
    print(r3[["growth_source", "g_case", "geo_mix_pp"] + [f"nights_yoy_{r}_pct" for r in REG]].round(2).to_string(index=False))
    print(hist.round(2).to_string(index=False))
    print(bt.round(3).to_string(index=False))


if __name__ == "__main__":
    main()

