"""V2: note-08 walk-forward backtests of every V1 series against Airbnb total nights y/y and
the regional nights buckets (NA, EMEA, LatAm, APAC), via analysis/src/adrq3/I0_protocol.py.

Workstream V, government data survey, 12 Sep 2026. Krishang Surapaneni (compiled with Claude Code).

Protocol (research/notes/overnight/08_altdata-index-and-backtests.md, implemented in I0):
  - features: calendar-quarter y/y of the monthly level (sum of the three months), plus a
    "_m1" vintage (first month of the quarter y/y, the part observable on 12 Sep 2026 for
    series that have July), plus "_lag1" (prior quarter, always knowable)
  - two windows: 2022Q1+ (walk-forward scored from 2023Q1) and 2023Q1+ (scored from 2024Q1),
    both ending 2026Q2; expanding OLS refit strictly before each scored quarter
  - RMSE ratio vs naive last quarter, vs prior year, vs AR(1); 1,000-shuffle permutation p
  - jackknife: the ratio vs naive recomputed with each scored quarter dropped in turn
  - knowable-before-print flag per feature (5 Nov 2026)
Targets: total nights y/y from data/processed/abnb_driver_history_quarterly.csv; regional mids
from data/processed/overnight/10_regional_panel_quarterly.csv (3Q22 onward; earlier quarters are
derived, later ones are management buckets, see that file's basis columns).
Outputs: data/processed/govdata/V/V_backtests.csv, V_feature_panel.csv, V_readings_3q26.csv.
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

OUT = os.path.join(ROOT, "data", "processed", "govdata", "V")
RAW = os.path.join(OUT, "raw")
LAST_Q = "2Q26"
NOW_Q = "3Q26"
WINDOWS = {"2022Q1+": ("1Q22", "1Q23"), "2023Q1+": ("1Q23", "1Q24")}


def log(*a):
    print(*a, flush=True)


def qlab(p):  # pandas Period Q -> '3Q26'
    return f"{p.quarter}Q{p.year % 100:02d}"


# ------------------------------------------------------------------ targets
def targets():
    d = pd.read_csv(os.path.join(ROOT, "data", "processed", "abnb_driver_history_quarterly.csv"))
    t = d.set_index("quarter")["nights_m_yoy_pct"].rename("total_nights_yoy")
    r = pd.read_csv(os.path.join(ROOT, "data", "processed", "overnight", "10_regional_panel_quarterly.csv")).set_index("quarter")
    reg = r[["na_nights_yoy_mid", "emea_nights_yoy_mid", "latam_nights_yoy_mid", "apac_nights_yoy_mid"]]
    out = pd.concat([t, reg], axis=1)
    out = out.loc[[q for q in I0.QORDER if q in out.index]]
    return out


# ------------------------------------------------------------------ feature builders
def monthly_to_q(s: pd.Series, how="sum"):
    """s indexed by 'YYYY-MM' strings -> quarterly level (complete quarters only) and first-month level."""
    s = s.dropna().copy()
    s.index = pd.PeriodIndex(s.index, freq="M")
    s = s[~s.index.duplicated()].sort_index()
    q = s.index.asfreq("Q")
    full = s.groupby(q).sum() if how == "sum" else s.groupby(q).mean()
    n = s.groupby(q).size()
    full = full.where(n == 3)
    m1 = s[s.index.month % 3 == 1]
    m1.index = m1.index.asfreq("Q")
    return full, m1


def first_two_months(s: pd.Series):
    s = s.dropna().copy()
    s.index = pd.PeriodIndex(s.index, freq="M")
    s = s[~s.index.duplicated()].sort_index()
    m12 = s[s.index.month % 3 != 0]
    q = m12.index.asfreq("Q")
    out = m12.groupby(q).sum()
    n = m12.groupby(q).size()
    return out.where(n == 2)


def yoy(level: pd.Series):
    v = (level / level.shift(4) - 1) * 100
    v.index = [qlab(p) for p in v.index]
    return v


def add(feats, name, level_full, level_m1, how_note):
    f = yoy(level_full)
    feats[name + "_full"] = f
    feats[name + "_lag1"] = f.shift(1)
    if level_m1 is not None:
        feats[name + "_m1"] = yoy(level_m1)
    META[name] = how_note


META: dict[str, dict] = {}


def build_features():
    feats = {}

    def load(fn):
        p = os.path.join(RAW, fn)
        return pd.read_csv(p) if os.path.exists(p) else None

    # Eurostat nights by NACE
    d = load("eurostat_tour_occ_nim_monthly.csv")
    if d is not None:
        for geo in ["EU27_2020", "ES", "IT", "FR", "PT", "EL", "HR", "DE"]:
            for nace in ["I552", "I551", "I551-I553"]:
                s = d[(d.geo == geo) & (d.nace_r2 == nace)].set_index("period")["value"]
                if s.dropna().empty:
                    continue
                full, m1 = monthly_to_q(s)
                add(feats, f"eurostat_{geo.lower().replace('27_2020', '27')}_{nace.replace('-', '_').lower()}", full, m1,
                    dict(source="eurostat_tour_occ_nim", region="EMEA", asset="short-stay accommodation nights (NACE I552)" if nace == "I552" else ("hotel nights (I551)" if nace == "I551" else "all collective accommodation nights"),
                         knowable="partial (Jul and Aug by late Oct; Sep after the print)", last=str(s.dropna().index.max())))
    # Eurostat air passengers
    d = load("eurostat_avia_paoc_monthly.csv")
    if d is not None:
        for geo in ["EU27_2020", "ES", "IT"]:
            s = d[d.geo == geo].set_index("period")["value"]
            full, m1 = monthly_to_q(s)
            add(feats, f"avia_{geo.lower().replace('27_2020', '27')}", full, m1, dict(source="eurostat_avia_paoc", region="EMEA", asset="air passengers", knowable="no (3 to 8 month lag)", last=str(s.dropna().index.max())))
    # Spain INE EOAP holiday apartments
    d = load("ine_eoap_1998_monthly.csv")
    if d is not None:
        for nm, tag in [("National. National. Holiday apartments. Overnight stays. Total.", "es_apt_nights"),
                        ("National. National. Holiday apartments. Overnight stays. Residents abroad.", "es_apt_nights_foreign"),
                        ("National. National. Holiday apartments. Overnight stays. Residents in Spain.", "es_apt_nights_domestic"),
                        ("National. National. Holiday apartments. Travellers. Total.", "es_apt_travellers")]:
            s = d[d.name.str.strip() == nm].set_index("period")["value"]
            if s.empty:
                continue
            full, m1 = monthly_to_q(s)
            add(feats, tag, full, m1, dict(source="ine_eoap_1998", region="EMEA", asset="tourist-apartment nights (Spain EOAP)", knowable="yes (Sep release about 23 Oct)", last=str(s.dropna().index.max())))
    # StatCan
    d = load("statcan_24100053_monthly.csv")
    if d is not None:
        for tag in ["us_residents_entering_overnight", "canadians_returning_from_us_overnight", "nonresident_visitors_overnight",
                    "other_country_residents_entering_overnight", "canadians_returning_from_other_overnight", "international_travellers_total"]:
            s = d[d.series == tag].set_index("period")["value"]
            full, m1 = monthly_to_q(s)
            add(feats, "ca_" + tag, full, m1, dict(source="statcan_24100053", region="NA", asset="border arrivals", knowable="partial (Jul and Aug by mid Oct; Sep about 20 Nov)", last=str(s.dropna().index.max())))
    # StatCan leading indicator (air by residence; land by plate), reaches Aug 2026 today
    d = load("statcan_liia_monthly.csv")
    if d is not None:
        for tag in ["liia_air_us_residents_overnight", "liia_air_us_residents_total", "liia_air_nonresident_visitors_overnight",
                    "liia_air_other_country_residents_overnight", "liia_air_intl_visitors_and_returning_total", "liia_land_us_plated_vehicles_entering", "liia_land_vehicles_entering_total"]:
            s = d[d.series == tag].set_index("period")["value"]
            if s.empty:
                continue
            full, m1 = monthly_to_q(s)
            add(feats, "ca_" + tag, full, m1, dict(source="statcan_liia", region="NA", asset="border arrivals (leading indicator, air by residence or land by plate)", knowable="yes (Sep leading indicator about 10 Oct)", last=str(s.dropna().index.max())))
            feats["ca_" + tag + "_m2"] = yoy(first_two_months(s))
    # Census QSS (already quarterly)
    d = load("census_qss_721_quarterly.csv")
    if d is not None:
        for cat, tag in [("721T", "us_qss_721_rev"), ("7211T", "us_qss_7211_rev")]:
            s = d[(d.cat_code == cat) & (d.dt_code == "QREV") & (d.is_adj == 0)].set_index("quarter")["val"]
            s = s.loc[[q for q in I0.QORDER if q in s.index]]
            y = (s / s.shift(4) - 1) * 100
            feats[tag + "_full"] = y
            feats[tag + "_lag1"] = y.shift(1)
            META[tag] = dict(source="census_qss", region="NA", asset="accommodation revenue (NAICS " + cat[:-1] + ")", knowable="no (3Q26 advance 19 Nov)", last=str(s.index[-1]))
    # JNTO
    d = load("jnto_arrivals_monthly.csv")
    if d is not None:
        for mk in ["total", "usa", "korea", "china", "taiwan"]:
            s = d[d.market == mk].set_index("period")["arrivals"]
            full, m1 = monthly_to_q(s)
            add(feats, f"jp_arrivals_{mk}", full, m1, dict(source="jnto_arrivals", region="APAC", asset="inbound arrivals", knowable="yes (Sep release mid Oct)", last=str(s.dropna().index.max())))
    # JTA nights
    d = load("jta_accommodation_nights_monthly.csv")
    if d is not None:
        for tag in ["total_nights", "foreign_nights"]:
            s = d[d.series == tag].set_index("period")["value"]
            full, m1 = monthly_to_q(s)
            add(feats, "jp_" + tag, full, m1, dict(source="jta_nights", region="APAC", asset="all-accommodation guest nights (hotels, ryokan, other)", knowable="tight (Sep preliminary about 31 Oct)", last=str(s.dropna().index.max())))
    # ABS
    d = load("abs_340101_arrivals_monthly.csv")
    if d is not None:
        for tag in ["st_visitors_arriving", "st_residents_returning"]:
            s = d[d.series == tag].set_index("period")["value"]
            full, m1 = monthly_to_q(s)
            add(feats, "au_" + tag, full, m1, dict(source="abs_340101", region="APAC", asset="border arrivals", knowable="partial (Aug by mid Oct; Sep about 12 Nov)", last=str(s.dropna().index.max())))
    # NTTO country
    d = load("ntto_arrivals_by_country_monthly.csv")
    if d is not None:
        for c in ["CANADA", "MEXICO"]:
            s = d[d.country == c].set_index("period")["arrivals"]
            full, m1 = monthly_to_q(s)
            add(feats, f"us_inbound_{c.lower()}", full, m1, dict(source="ntto_country", region="NA", asset="I-94 arrivals to the US (Canada and Mexico rows lag two months; the preliminary file covers overseas only)", knowable="partial (Jul by late Sep, Aug by late Oct; Sep about 20 Nov)", last=str(s.dropna().index.max())))
    # ANAC Brazil
    d = load("anac_brazil_passengers_monthly.csv")
    if d is not None:
        for nat, tag in [("DOMÉSTICA", "br_air_pax_domestic"), ("INTERNACIONAL", "br_air_pax_international")]:
            s = d[d.nature.str.upper().str.startswith(nat[:3])].set_index("period")["paying_passengers"]
            if s.empty:
                continue
            full, m1 = monthly_to_q(s)
            add(feats, tag, full, m1, dict(source="anac_brazil", region="LatAm", asset="air passengers", knowable="yes (Sep data late Oct)", last=str(s.dropna().index.max())))
    # Colombia
    d = load("colombia_foreign_entries_monthly.csv")
    if d is not None:
        s = d.set_index("period")["foreign_entries"]
        full, m1 = monthly_to_q(s)
        add(feats, "co_foreign_entries", full, m1, dict(source="colombia_migracion", region="LatAm", asset="border arrivals", knowable="partial (Aug by late Sep; Sep late Oct)", last=str(s.dropna().index.max())))
    # IBGE PMS
    d = load("ibge_pms_accommodation_monthly.csv")
    if d is not None:
        s = d[(d.activity.str.startswith("1.1 ")) & (d.variable == "PMS - Número-índice (2022=100)")].set_index("period")["value"]
        full, m1 = monthly_to_q(s, how="mean")
        add(feats, "br_pms_lodging_food_volume", full, m1, dict(source="ibge_pms_8688", region="LatAm", asset="accommodation and food services volume index", knowable="partial (Aug by mid Oct; Sep about 12 Nov)", last=str(s.dropna().index.max())))
        s2 = d[(d.activity.str.startswith("1.1.1")) & (d.variable == "PMS - Número-índice (2022=100)")].set_index("period")["value"]
        if len(s2.dropna()) > 20:
            full, m1 = monthly_to_q(s2, how="mean")
            add(feats, "br_pms_lodging_volume", full, m1, dict(source="ibge_pms_8688", region="LatAm", asset="accommodation volume index (from 2022)", knowable="partial (Aug by mid Oct; Sep about 12 Nov)", last=str(s2.dropna().index.max())))
    # NZ ADP
    d = load("nz_adp_national_monthly.csv")
    if d is not None:
        for meas, tag in [("Total guest nights", "nz_guest_nights"), ("International guest nights", "nz_intl_guest_nights"), ("Domestic guest nights", "nz_dom_guest_nights")]:
            s = d[(d.property == "Total") & (d.measure == meas)].set_index("period")["value"]
            if s.empty:
                continue
            full, m1 = monthly_to_q(s)
            add(feats, tag, full, m1, dict(source="nz_mbie_adp", region="APAC", asset="commercial accommodation guest nights", knowable="partial (Aug by late Sep; Sep late Oct)", last=str(s.dropna().index.max())))
    # Hawaii VR (short history)
    d = load("hawaii_vacation_rental_monthly.csv")
    if d is not None:
        for meas, tag in [("unit_demand", "hi_vr_demand"), ("unit_supply", "hi_vr_supply"), ("adr", "hi_vr_adr")]:
            s = d[d.series == meas].set_index("period")["value"]
            if s.empty:
                continue
            full, m1 = monthly_to_q(s, how="mean" if meas == "adr" else "sum")
            add(feats, tag, full, m1, dict(source="hawaii_vacation_rental", region="NA", asset="vacation rental unit nights (Transparent data via DBEDT)", knowable="yes (Sep report late Oct)", last=str(s.dropna().index.max())))
    # FRED air RPMs
    for sid, tag in [("AIRRPMTSID11", "us_air_rpm_domestic"), ("AIRRPMTSII11", "us_air_rpm_international")]:
        d = load(f"fred_{sid}_monthly.csv")
        if d is not None:
            s = d.set_index("period")["value"]
            full, m1 = monthly_to_q(s)
            add(feats, tag, full, m1, dict(source=f"fred_{sid}", region="NA", asset="air revenue passenger miles", knowable="no (about 3 month lag)", last=str(s.dropna().index.max())))

    panel = pd.DataFrame(feats)
    panel = panel.loc[[q for q in I0.QORDER if q in panel.index]]
    return panel


# ------------------------------------------------------------------ jackknife on the same walk-forward
def wf_errors(x, y, start, min_fit=4):
    x = np.asarray(x, float); y = np.asarray(y, float)
    out = []
    for t in range(start, len(y)):
        xs, ys = x[:t], y[:t]
        ok = np.isfinite(xs) & np.isfinite(ys)
        if ok.sum() < min_fit or not np.isfinite(x[t]) or not np.isfinite(y[t]) or not np.isfinite(y[t - 1]):
            continue
        b, a = I0.ols(xs[ok], ys[ok])
        pred = a + b * x[t]
        if not np.isfinite(pred):
            continue
        out.append((t, pred - y[t], y[t - 1] - y[t]))
    return out


def jackknife(x, y, start):
    e = wf_errors(x, y, start)
    if len(e) < 4:
        return dict(jk_ratio_min=np.nan, jk_ratio_max=np.nan, jk_n_below_1=np.nan)
    ratios = []
    for i in range(len(e)):
        keep = [r for j, r in enumerate(e) if j != i]
        ef = np.array([r[1] for r in keep]); en = np.array([r[2] for r in keep])
        ratios.append(np.sqrt(np.mean(ef ** 2)) / np.sqrt(np.mean(en ** 2)))
    return dict(jk_ratio_min=float(min(ratios)), jk_ratio_max=float(max(ratios)), jk_n_below_1=int(sum(r < 1 for r in ratios)))


REGION_TARGETS = {"NA": "na_nights_yoy_mid", "EMEA": "emea_nights_yoy_mid", "LatAm": "latam_nights_yoy_mid", "APAC": "apac_nights_yoy_mid"}


def main():
    tg = targets()
    panel = build_features()
    both = panel.join(tg, how="outer")
    both = both.loc[[q for q in I0.QORDER if q in both.index]]
    both.to_csv(os.path.join(OUT, "V_feature_panel.csv"), index_label="quarter")
    log(f"panel {both.shape}; features {panel.shape[1]}")

    rows = []
    for feat in panel.columns:
        base = feat.rsplit("_", 1)[0]
        meta = META.get(base, {})
        vint = feat.rsplit("_", 1)[1]
        know = meta.get("knowable", "unknown")
        if vint == "lag1":
            know = "yes (prior quarter already published)"
        elif vint in ("m1", "m2"):
            has_now = NOW_Q in panel.index and pd.notna(panel.at[NOW_Q, feat])
            months = "July 2026" if vint == "m1" else "July and August 2026"
            know = f"yes ({months} observable on 12 Sep 2026)" if has_now else f"yes ({months} vintage, not yet published for 3Q26)"
        tlist = ["total_nights_yoy"] + [REGION_TARGETS[meta["region"]]] if meta.get("region") in REGION_TARGETS else ["total_nights_yoy"]
        for tcol in tlist:
            for wname, (w0, wf0) in WINDOWS.items():
                labels = [q for q in I0.QORDER if I0.qkey(w0) <= I0.qkey(q) <= I0.qkey(LAST_Q)]
                x = both.reindex(labels)[feat].values
                y = both.reindex(labels)[tcol].values
                r = I0.score(feat, x, y, labels, wf0, know)
                r.update(target=tcol, window=wname, source=meta.get("source", ""), region=meta.get("region", ""), asset=meta.get("asset", ""), vintage=vint, last_period=meta.get("last", ""))
                if r.get("wf_n"):
                    r.update(jackknife(x, y, labels.index(wf0)))
                rows.append(r)
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(OUT, "V_backtests.csv"), index=False)
    ev = res[res.wf_n.fillna(0) >= 6]
    log(f"{len(res)} tests; {len(ev)} with wf_n>=6; beat naive: {(ev.wf_ratio_vs_naive < 1).sum()}")
    cols = ["feature", "target", "window", "n", "wf_n", "r", "perm_p", "wf_ratio_vs_naive", "wf_ratio_vs_ar1", "jk_ratio_max", "jk_n_below_1", "knowable_before_print"]
    log(ev[ev.wf_ratio_vs_naive < 1].sort_values("wf_ratio_vs_naive")[cols].head(40).to_string(index=False))

    # ---------------------------------------------------------------- 3Q26 readings
    rd = []
    for feat in panel.columns:
        if NOW_Q not in panel.index:
            continue
        v = panel.at[NOW_Q, feat]
        if pd.isna(v):
            continue
        base = feat.rsplit("_", 1)[0]
        meta = META.get(base, {})
        v2 = panel.at[LAST_Q, feat] if LAST_Q in panel.index else np.nan
        tlist = ["total_nights_yoy"] + ([REGION_TARGETS[meta["region"]]] if meta.get("region") in REGION_TARGETS else [])
        for tcol in tlist:
            labels = [q for q in I0.QORDER if I0.qkey("1Q23") <= I0.qkey(q) <= I0.qkey(LAST_Q)]
            d = both.reindex(labels)[[feat, tcol]].dropna()
            pred = np.nan
            if len(d) >= 6:
                b, a = I0.ols(d[feat].values, d[tcol].values)
                pred = a + b * v
            bt = res[(res.feature == feat) & (res.target == tcol) & (res.window == "2023Q1+")]
            rd.append(dict(feature=feat, source=meta.get("source"), region=meta.get("region"), target=tcol, value_2q26=v2, value_3q26=v, delta_pp=v - v2 if pd.notna(v2) else np.nan,
                           naive_3q26=both[tcol].dropna().iloc[-1], insample_pred_3q26=pred,
                           wf_ratio_vs_naive_2023=bt.wf_ratio_vs_naive.iloc[0] if len(bt) else np.nan, wf_n=bt.wf_n.iloc[0] if len(bt) else np.nan,
                           note="in-sample OLS on 1Q23 to 2Q26, first-month vintage" if feat.endswith("_m1") else "in-sample OLS on 1Q23 to 2Q26"))
    rdd = pd.DataFrame(rd)
    rdd.to_csv(os.path.join(OUT, "V_readings_3q26.csv"), index=False)
    log("\n3Q26 readings (features with a July 2026 value):")
    if len(rdd):
        log(rdd[rdd.target == "total_nights_yoy"][["feature", "value_2q26", "value_3q26", "delta_pp", "insample_pred_3q26", "wf_ratio_vs_naive_2023"]].to_string(index=False))


if __name__ == "__main__":
    main()
