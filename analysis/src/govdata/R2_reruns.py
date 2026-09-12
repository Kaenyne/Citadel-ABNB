"""R2: reviewer re-runs of the V and P survivors, short-window survivors and coverage-eliminated survivors from
the cached panels, plus the sources R1 recovered, all through analysis/src/adrq3/I0_protocol.py unchanged.

Workstream R, government data survey, 12 Sep 2026. Krishang Surapaneni (compiled with Claude Code).

For each (feature, target) the script reports, per window (2022Q1+ scored from 1Q23, 2023Q1+ scored from 1Q24,
and a reviewer window 2024Q1+ scored from 1Q25 that drops the 2022 to 2023 normalisation quarters from both the
fit and the score): walk-forward RMSE ratio vs naive, vs an expanding-mean benchmark (the target's own mean to
date, which is what a flat-slope level model collapses to), jackknife min and max, the sign of the final OLS
slope, Pearson r and permutation p. Outputs data/processed/govdata/R/R_reruns.csv and R_duplicates.csv.

Run: py -3.13 analysis/src/govdata/R2_reruns.py
"""
from __future__ import annotations

import os
import sys
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "analysis", "src", "adrq3"))
import I0_protocol as I0  # noqa: E402

GD = os.path.join(ROOT, "data", "processed", "govdata")
OUT = os.path.join(GD, "R")
RAW = os.path.join(OUT, "raw")
os.makedirs(OUT, exist_ok=True)
Q = I0.QORDER
qi = {q: i for i, q in enumerate(Q)}
LAST_Q = "2Q26"
WINDOWS = {"2022Q1+": ("1Q22", "1Q23"), "2023Q1+": ("1Q23", "1Q24"), "2024Q1+ (reviewer)": ("1Q24", "1Q25")}


def qlab(p):
    return f"{p.quarter}Q{p.year % 100:02d}"


# ------------------------------------------------------------------------------------------ targets
def v_targets():
    d = pd.read_csv(os.path.join(ROOT, "data", "processed", "abnb_driver_history_quarterly.csv")).set_index("quarter")
    r = pd.read_csv(os.path.join(ROOT, "data", "processed", "overnight", "10_regional_panel_quarterly.csv")).set_index("quarter")
    t = pd.concat([d["nights_m_yoy_pct"].rename("total_nights_yoy"), r[["na_nights_yoy_mid", "emea_nights_yoy_mid", "latam_nights_yoy_mid", "apac_nights_yoy_mid"]]], axis=1)
    return t.loc[[q for q in Q if q in t.index]]


def p_targets():
    H = pd.read_csv(os.path.join(ROOT, "data", "processed", "q3nowcast", "H", "adr_history_components.csv")).set_index("quarter")
    hist = pd.read_csv(os.path.join(ROOT, "data", "processed", "adr", "02b_adr_history_extended.csv")).set_index("quarter")
    reg = pd.read_csv(os.path.join(ROOT, "data", "processed", "adr", "04_regional_quarterly_wide.csv")).set_index("quarter")
    t = pd.DataFrame(index=Q)
    t["residual_pricing_pp"] = H["residual_pricing_pp"]
    t["adr_exfx_yoy_pp"] = hist["adr_yoy_exfx_final"]
    t["adr_reported_yoy_pp"] = hist["adr_yoy_reported_pct"]
    for r in ("na", "emea", "latam", "apac"):
        t[f"adr_exfx_{r}_pp"] = reg[f"adr_yoy_exfx_{r}_pct"]
    return t


# ------------------------------------------------------------------------------------------ protocol plus reviewer extras
def wf_detail(x, y, start, min_fit=4):
    x = np.asarray(x, float); y = np.asarray(y, float)
    ef, en, em, ts, slopes = [], [], [], [], []
    for t in range(start, len(y)):
        xs, ys = x[:t], y[:t]
        ok = np.isfinite(xs) & np.isfinite(ys)
        if ok.sum() < min_fit or not np.isfinite(x[t]) or not np.isfinite(y[t]) or not np.isfinite(y[t - 1]):
            continue
        b, a = I0.ols(xs[ok], ys[ok])
        pred = a + b * x[t]
        if not np.isfinite(pred):
            continue
        ef.append(pred - y[t]); en.append(y[t - 1] - y[t]); em.append(np.nanmean(ys) - y[t]); ts.append(t); slopes.append(b)
    return np.array(ef), np.array(en), np.array(em), ts, slopes


def rerun(x, y, labels, wf0):
    start = labels.index(wf0)
    r0, p, n = I0.perm_p(x, y)
    ef, en, em, ts, slopes = wf_detail(x, y, start)
    out = dict(n=n, r=r0, perm_p=p, wf_n=len(ef))
    if len(ef) < 3:
        return out
    rm = lambda e: float(np.sqrt(np.mean(e ** 2)))
    out.update(ratio_vs_naive=rm(ef) / rm(en), ratio_vs_expanding_mean=rm(ef) / rm(em), mean_vs_naive=rm(em) / rm(en),
               final_slope=float(slopes[-1]), slope_sign_stable=bool(all(np.sign(s) == np.sign(slopes[-1]) for s in slopes)),
               scored_from=labels[ts[0]], scored_to=labels[ts[-1]])
    if len(ef) >= 4:
        rats = []
        for i in range(len(ef)):
            m = np.ones(len(ef), bool); m[i] = False
            rats.append(rm(ef[m]) / rm(en[m]))
        out.update(jk_min=float(min(rats)), jk_max=float(max(rats)), jk_n_below_1=int(sum(r < 1 for r in rats)))
    return out


def run_pairs(panel, targets, pairs, ws):
    rows = []
    both = panel.join(targets, how="outer")
    both = both.loc[[q for q in Q if q in both.index]]
    for feat, tcol, note in pairs:
        if feat not in both.columns:
            rows.append(dict(workstream=ws, feature=feat, target=tcol, note=note + " | FEATURE MISSING"))
            continue
        for wname, (w0, wf0) in WINDOWS.items():
            labels = [q for q in Q if qi[w0] <= qi[q] <= qi[LAST_Q]]
            x = both.reindex(labels)[feat].values; y = both.reindex(labels)[tcol].values
            if np.isfinite(y).sum() < 5 or np.isfinite(x).sum() < 5:
                rows.append(dict(workstream=ws, feature=feat, target=tcol, window=wname, note=note + " | too few points"))
                continue
            r = rerun(x, y, labels, wf0)
            r.update(workstream=ws, feature=feat, target=tcol, window=wname, note=note,
                     target_distinct_values=int(pd.Series(y[labels.index(wf0):]).dropna().nunique()))
            rows.append(r)
    return rows


# ------------------------------------------------------------------------------------------ V re-runs
def v_pairs():
    return [
        ("br_air_pax_domestic_lag1", "latam_nights_yoy_mid", "V rank 1 survivor"),
        ("br_air_pax_domestic_lag1", "total_nights_yoy", "V rank 1 on total"),
        ("br_pms_lodging_volume_lag1", "latam_nights_yoy_mid", "V rank 2 survivor"),
        ("ca_liia_land_us_plated_vehicles_entering_full", "total_nights_yoy", "V rank 3 short-window"),
        ("ca_liia_air_us_residents_overnight_m2", "total_nights_yoy", "V rank 3 m2 vintage"),
        ("ca_liia_air_us_residents_overnight_full", "na_nights_yoy_mid", "V rank 3 on NA bucket"),
        ("jp_arrivals_taiwan_lag1", "total_nights_yoy", "V rank 4 short-window"),
        ("jp_foreign_nights_m1", "total_nights_yoy", "V rank 5 short-window"),
        ("au_st_visitors_arriving_full", "total_nights_yoy", "V rank 6 short-window"),
        ("nz_guest_nights_full", "total_nights_yoy", "V rank 7 short-window"),
        ("es_apt_nights_foreign_lag1", "total_nights_yoy", "V rank 8 corroboration"),
        ("es_apt_nights_full", "emea_nights_yoy_mid", "V rank 8 on EMEA bucket"),
        ("us_qss_721_rev_full", "total_nights_yoy", "V rank 16 no coverage, both-window survivor"),
        ("eurostat_eu27_i551_full", "emea_nights_yoy_mid", "V rank 17 no coverage, both-window survivor on EMEA"),
        ("eurostat_pt_i552_full", "total_nights_yoy", "V rank 17 Portugal I552 both-window survivor"),
        ("eurostat_pt_i552_full", "emea_nights_yoy_mid", "V rank 17 Portugal I552 on EMEA bucket"),
        ("eurostat_eu27_i552_full", "emea_nights_yoy_mid", "V rank 17 EU27 I552 on EMEA bucket"),
        ("us_inbound_canada_full", "total_nights_yoy", "V rank 19 no coverage, both-window survivor"),
        ("co_foreign_entries_m1", "latam_nights_yoy_mid", "V rank 20 no coverage"),
        ("avia_it_full", "emea_nights_yoy_mid", "V rank 18 no coverage"),
        ("ca_canadians_returning_from_other_overnight_lag1", "na_nights_yoy_mid", "V rank 10 duplicate, best feature"),
    ]


def p_pairs():
    return [
        ("hicp_CP112_PT_RCH_A|level|0", "adr_exfx_emea_pp", "P rank 1 survivor"),
        ("hicp_CP112_EA_RCH_A|level|0", "adr_exfx_emea_pp", "P rank 1 euro-area comparator (J2 held)"),
        ("bea_export_travel_price|diff|0", "residual_pricing_pp", "P rank 2 short-window (residual has no long window)"),
        ("bea_export_travel_price|diff|0", "adr_exfx_yoy_pp", "P rank 2 on blended ex-FX"),
        ("hicp_CP11202_CH_RCH_A|level|0", "residual_pricing_pp", "P rank 3 wrong-sign flag"),
        ("nz_cpi_CPIQ.SE9096_accommodation_services_nan|level|0", "adr_exfx_apac_pp", "P rank 4 short-window"),
        ("abs_cpi_40102_Q|level|0", "adr_exfx_apac_pp", "P rank 5 short-window"),
        ("hicp_CP11201_EL_RCH_A|level|0", "adr_reported_yoy_pp", "P rank 6 wrong-sign flag"),
        ("ine_hotel_revpar_EOT16471|level|0", "adr_exfx_emea_pp", "P rank 7 short-window"),
        ("ons_cpi_11201_hotels_index|level|0", "adr_exfx_emea_pp", "P rank 8 short-window"),
        ("japan_cpi_hotel_charges_index|diff|1", "adr_exfx_apac_pp", "P rank 9 short-window"),
        ("ine_rtapi_rural_EOT12767|diff|0", "adr_reported_yoy_pp", "P rank 24 survivor by the letter, wrong sign"),
        ("ine_rtapi_rural_EOT12767|diff|0", "adr_exfx_emea_pp", "P rank 24 on EMEA ex-FX"),
        ("sppi_I55_PT_PCH_SM|level|0", "adr_exfx_emea_pp", "P rank 20 no coverage, both-window survivor"),
        ("ine_hdpi_holiday_dwellings_EOT8077|level|0", "adr_reported_yoy_pp", "P rank 11 corroboration, wrong sign"),
        ("ine_hdpi_holiday_dwellings_EOT8077|level|0", "adr_exfx_emea_pp", "P rank 11 on EMEA ex-FX"),
        ("hawaii_vr_adr_state_yoy_reported_pct|level|0", "adr_reported_yoy_pp", "P rank 10 corroboration, basis breaks"),
        ("bls_CUUR0000SEHB02|diff|0", "adr_exfx_yoy_pp", "P rank 16 corroboration"),
    ]


def p_panel_with_transforms():
    panel = pd.read_csv(os.path.join(GD, "P", "P_feature_quarterly_panel.csv"), index_col=0)
    panel = panel.loc[[q for q in Q if q in panel.index]]
    cols = {}
    for c in panel.columns:
        s = panel[c].astype(float)
        for tr in ("level", "diff"):
            f = s.diff() if tr == "diff" else s
            for lag in (0, 1):
                cols[f"{c}|{tr}|{lag}"] = f.shift(lag)
    return pd.DataFrame(cols, index=panel.index)


# ------------------------------------------------------------------------------------------ Hawaii volume from P's within-vintage cache
def hawaii_volume_features():
    h = pd.read_csv(os.path.join(GD, "P", "raw", "hawaii_dbedt_vacation_rental_monthly.csv"))
    st = h[(h.region.str.contains("State")) & (h.parse_ok)].copy()
    st["demand_yoy"] = (st.demand_cur / st.demand_cmp - 1) * 100
    st["supply_yoy"] = (st.supply_cur / st.supply_cmp - 1) * 100
    st["adr_yoy"] = (st.adr_cur / st.adr_cmp - 1) * 100
    st["occ_pts"] = (st.occ_cur - st.occ_cmp) * 100
    st.index = pd.PeriodIndex(st.vintage, freq="M")
    qm = st[["demand_yoy", "supply_yoy", "adr_yoy", "occ_pts"]].groupby(st.index.asfreq("Q")).agg(["mean", "size"])
    feats = {}
    for c in ("demand_yoy", "supply_yoy", "adr_yoy", "occ_pts"):
        full = qm[(c, "mean")].where(qm[(c, "size")] == 3)
        full.index = [qlab(p) for p in full.index]
        feats[f"hi_vr_{c}_withinvintage_full"] = full
        feats[f"hi_vr_{c}_withinvintage_lag1"] = full.shift(1)
        m1 = st[st.index.month % 3 == 1][c]
        m1.index = [qlab(p.asfreq("Q")) for p in m1.index]
        feats[f"hi_vr_{c}_withinvintage_m1"] = m1
    f = pd.DataFrame(feats)
    f = f.loc[[q for q in Q if q in f.index]]
    st[["vintage", "demand_cur", "demand_cmp", "supply_cur", "supply_cmp", "adr_cur", "adr_cmp", "occ_cur", "occ_cmp", "demand_yoy", "supply_yoy", "adr_yoy", "occ_pts"]].to_csv(
        os.path.join(RAW, "hawaii_vr_state_withinvintage_monthly.csv"), index=False)
    return f


# ------------------------------------------------------------------------------------------ recovered sources (R1 caches), built into quarterly y/y features
def monthly_level_to_q(s: pd.Series, how="sum"):
    s = s.dropna().copy()
    s.index = pd.PeriodIndex(s.index, freq="M")
    s = s[~s.index.duplicated()].sort_index()
    q = s.index.asfreq("Q")
    full = (s.groupby(q).sum() if how == "sum" else s.groupby(q).mean()).where(s.groupby(q).size() == 3)
    m1 = s[s.index.month % 3 == 1]; m1.index = m1.index.asfreq("Q")
    yo = lambda lv: ((lv / lv.shift(4) - 1) * 100).rename(index=qlab)
    return yo(full), yo(m1)


def recovered_features():
    feats, pairs = {}, []

    def add(name, full, m1, targets_, note):
        feats[name + "_full"] = full; feats[name + "_lag1"] = full.shift(1)
        if m1 is not None:
            feats[name + "_m1"] = m1
        for t in targets_:
            pairs.append((name + "_full", t, note)); pairs.append((name + "_lag1", t, note + " (lag1)"))
            if m1 is not None:
                pairs.append((name + "_m1", t, note + " (m1)"))

    p = os.path.join(RAW, "eurostat_bop_c6_m_travel_credit_monthly.csv")
    if os.path.exists(p):
        d = pd.read_csv(p)
        for g in d.geo.unique():
            s = d[d.geo == g].set_index("time")["value"]
            if s.dropna().shape[0] < 60:
                continue
            full, m1 = monthly_level_to_q(s)
            add(f"bop_travel_credit_{g.lower()}", full, m1, ["emea_nights_yoy_mid", "total_nights_yoy"], f"R gap: Eurostat bop_c6_m travel credit {g} (EUR receipts, nominal)")
    p = os.path.join(RAW, "bcb_sgs_travel_selected_monthly.csv")
    if os.path.exists(p):
        d = pd.read_csv(p)
        for name in ["viagens_mensal_despesa", "viagens_mensal_receita", "viagens_pessoais_outros_inclusive_turismo_mensal_despesa",
                     "viagens_pessoais_outros_inclusive_turismo_mensal_receita", "viagens_com_uso_de_cart_es_internacionais_mensal_despesa"]:
            if name not in set(d.series):
                continue
            s = d[d.series == name].set_index("period")["value"]
            full, m1 = monthly_level_to_q(s)
            add(f"bcb_{name}", full, m1, ["latam_nights_yoy_mid", "total_nights_yoy"], f"R gap: BCB BoP travel {name} (USD, nominal)")
    for sid, tag in [("AIRRPMTSID11", "us_air_rpm_domestic"), ("AIRRPMTSII11", "us_air_rpm_international")]:
        p = os.path.join(RAW, f"fred_{sid}_monthly.csv")
        if os.path.exists(p):
            d = pd.read_csv(p)
            s = d.set_index("period")["value"]
            full, m1 = monthly_level_to_q(s)
            add(tag, full, m1, ["na_nights_yoy_mid", "total_nights_yoy"], f"R retry: FRED {sid} BTS revenue passenger miles")
    p = os.path.join(RAW, "ine_pt_nights_by_type_monthly.csv")
    if os.path.exists(p):
        d = pd.read_csv(p)
        for name in d.series.unique():
            s = d[d.series == name].set_index("period")["value"]
            full, m1 = monthly_level_to_q(s)
            add(f"pt_ine_{name}", full, m1, ["emea_nights_yoy_mid", "total_nights_yoy"], f"R retry: INE Portugal nights {name}")
    p = os.path.join(RAW, "us_monthly_travel_trade.csv")
    if os.path.exists(p):
        d = pd.read_csv(p)
        for name in d.series.unique():
            s = d[d.series == name].set_index("period")["value"]
            full, m1 = monthly_level_to_q(s)
            add(f"us_{name}", full, m1, ["na_nights_yoy_mid", "total_nights_yoy"], f"R gap: BEA monthly trade in services, {name} (USD, nominal)")
    p = os.path.join(RAW, "eurostat_hicp_cp11203_monthly.csv")
    f = pd.DataFrame(feats)
    return (f.loc[[q for q in Q if q in f.index]] if len(f) else f), pairs


def cp11203_features():
    """Price features from the CP11203 pull (already an annual rate): quarter mean, level and diff, lags 0 and 1."""
    p = os.path.join(RAW, "eurostat_hicp_cp11203_monthly.csv")
    if not os.path.exists(p):
        return pd.DataFrame(), []
    d = pd.read_csv(p)
    feats, pairs = {}, []
    for g in d.geo.unique():
        s = d[d.geo == g].dropna(subset=["value"]).set_index("time")["value"]
        if len(s) < 40:
            continue
        s.index = pd.PeriodIndex(s.index, freq="M")
        q = s.groupby(s.index.asfreq("Q")).mean(); q.index = [qlab(x) for x in q.index]
        for tr in ("level", "diff"):
            f = q.diff() if tr == "diff" else q
            for lag in (0, 1):
                nm = f"hicp_CP11203_{g}|{tr}|{lag}"
                feats[nm] = f.shift(lag)
                for t in ("residual_pricing_pp", "adr_exfx_yoy_pp", "adr_reported_yoy_pp", "adr_exfx_emea_pp"):
                    pairs.append((nm, t, f"R retry: Eurostat HICP CP11203 other establishments {g}"))
    f = pd.DataFrame(feats)
    return f.loc[[q for q in Q if q in f.index]], pairs


def main():
    rows = []
    vt = v_targets()
    vpanel = pd.read_csv(os.path.join(GD, "V", "V_feature_panel.csv"), index_col=0)
    vpanel = vpanel.loc[[q for q in Q if q in vpanel.index]].drop(columns=[c for c in vt.columns if c in vpanel.columns])
    rows += run_pairs(vpanel, vt, v_pairs(), "V")
    hv = hawaii_volume_features()
    hpairs = [(c, t, "R re-test: Hawaii VR within-vintage y/y from P's 2023-06+ cache (V said history starts 2024-01)")
              for c in hv.columns for t in ("total_nights_yoy", "na_nights_yoy_mid")]
    rows += run_pairs(hv, vt, hpairs, "R")
    rf, rpairs = recovered_features()
    if len(rf):
        rows += run_pairs(rf, vt, rpairs, "R")
    pt = p_targets()
    pp = p_panel_with_transforms()
    rows += run_pairs(pp, pt, p_pairs(), "P")
    cf, cpairs = cp11203_features()
    if len(cf):
        rows += run_pairs(cf, pt, cpairs, "R")
    res = pd.DataFrame(rows)
    cols = ["workstream", "feature", "target", "window", "note", "n", "wf_n", "scored_from", "scored_to", "r", "perm_p", "ratio_vs_naive", "ratio_vs_expanding_mean", "mean_vs_naive",
            "jk_min", "jk_max", "jk_n_below_1", "final_slope", "slope_sign_stable", "target_distinct_values"]
    res = res.reindex(columns=cols)
    res.to_csv(os.path.join(OUT, "R_reruns.csv"), index=False)
    pd.set_option("display.width", 260); pd.set_option("display.max_rows", 400)
    print(res.drop(columns=["note"]).round(3).to_string())

    # duplicate correlations
    v = pd.read_csv(os.path.join(GD, "V", "V_feature_panel.csv"), index_col=0)
    pairs = [("statcan_24100053 vs statcan_liia", "ca_us_residents_entering_overnight_full", "ca_liia_air_us_residents_overnight_full"),
             ("statcan_24100053 vs statcan_liia", "ca_us_residents_entering_overnight_full", "ca_liia_land_us_plated_vehicles_entering_full"),
             ("statcan_24100053 vs statcan_liia", "ca_nonresident_visitors_overnight_full", "ca_liia_air_nonresident_visitors_overnight_full"),
             ("statcan_24100053 vs statcan_liia", "ca_other_country_residents_entering_overnight_full", "ca_liia_air_other_country_residents_overnight_full"),
             ("statcan_24100053 vs statcan_liia", "ca_canadians_returning_from_us_overnight_full", "ca_liia_air_intl_visitors_and_returning_total_full"),
             ("statcan_24100053 vs statcan_liia", "ca_canadians_returning_from_other_overnight_full", "ca_liia_air_intl_visitors_and_returning_total_full"),
             ("ntto_country vs statcan_24100053", "us_inbound_canada_full", "ca_canadians_returning_from_us_overnight_full"),
             ("ntto_country vs statcan_liia", "us_inbound_canada_full", "ca_liia_air_intl_visitors_and_returning_total_full"),
             ("eurostat PT I552 vs EU27 I552", "eurostat_pt_i552_full", "eurostat_eu27_i552_full"),
             ("eurostat IT I552 vs EU27 I552", "eurostat_it_i552_full", "eurostat_eu27_i552_full"),
             ("eurostat FR I552 vs EU27 I552", "eurostat_fr_i552_full", "eurostat_eu27_i552_full"),
             ("eurostat HR I552 vs EU27 I552", "eurostat_hr_i552_full", "eurostat_eu27_i552_full"),
             ("eurostat ES I552 vs INE EOAP apartments", "eurostat_es_i552_full", "es_apt_nights_full")]
    drows = []
    for claim, a, b in pairs:
        for w in ("1Q22", "1Q23"):
            x = v.loc[[q for q in Q if qi[w] <= qi[q] <= qi[LAST_Q]], [a, b]].dropna()
            drows.append(dict(claim=claim, series_a=a, series_b=b, window_from=w, n=len(x), r=float(x.corr().iloc[0, 1]) if len(x) > 3 else np.nan,
                              mean_abs_gap_pp=float((x[a] - x[b]).abs().mean()) if len(x) else np.nan))
    dd = pd.DataFrame(drows)
    dd.to_csv(os.path.join(OUT, "R_duplicates.csv"), index=False)
    print("\nduplicate checks\n", dd.round(3).to_string())


if __name__ == "__main__":
    main()
