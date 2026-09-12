"""WS-K, step 1: quarterly migrated-cohort share, 1Q23 to 4Q26, by region and blended.

The cohort that matters for a reprice is the set of listings that moved from the SPLIT fee
(3% host + separate guest fee) to the SINGLE 15.5% host fee. A second, pre-existing cohort was
already on a ~15% single fee (voluntary from May 2019; mandatory for software-connected hosts
outside US, Canada, Mexico, Bahamas, Argentina, Taiwan, Uruguay from December 2020) and moved
to 15.5% on 1 December 2025: a 0.5 pp fee change, not a 12 pp one. Both are carried.

Every step is labelled sourced / assumed. The blended series is anchored on the two disclosed
listing shares (over a quarter at the 7 May 2026 call, about half at the 6 Aug 2026 call) and on
the dated tranches. Regional splits and the pre-existing level are assumed; low and high
variants move the pre-existing level and the nights-per-listing factor.

Output: data/processed/adrv3/K/K1_migrated_cohort_share.csv (one row per quarter x region x
basis x variant) and K1_assumptions.csv.

py -3.13 analysis/src/adrv3/K1_cohort_share.py
"""
import os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "K")
os.makedirs(OUT, exist_ok=True)

QUARTERS = [f"{q}Q{y}" for y in (23, 24, 25, 26) for q in (1, 2, 3, 4)]
REGIONS = ["na", "emea", "latam", "apac"]

# ------------------------------------------------------------------------------------------
# nights shares by region (sourced: data/processed/adr/04_regional_quarterly_wide.csv, from the
# letters' regional buckets), 3Q26 and 4Q26 carry the prior-year quarter (assumed)
# ------------------------------------------------------------------------------------------
w = pd.read_csv(os.path.join(ROOT, "data", "processed", "adr", "04_regional_quarterly_wide.csv")).set_index("quarter")
shares = {}
for q in QUARTERS:
    src = q if q in w.index else f"{q[:2]}{int(q[2:]) - 1}"
    row = w.loc[src]
    s = np.array([row[f"nights_share_{r}_pct"] for r in REGIONS], dtype=float)
    shares[q] = (s / s.sum(), "sourced (04 regional shares)" if q in w.index else "assumed (prior-year quarter share)")

# ------------------------------------------------------------------------------------------
# assumptions, one table
# ------------------------------------------------------------------------------------------
A = []
def a(name, central, low, high, label, source):
    A.append({"parameter": name, "central": central, "low": low, "high": high, "label": label, "source": source})
    return {"central": central, "low": low, "high": high}

# pre-existing single-fee share of active listings before October 2025, by region
pre = {
    "na": a("pre-existing single-fee listing share, NA", 0.03, 0.01, 0.05, "assumed",
            "host-only fee voluntary only in US/Canada (exempt from the Dec 2020 mandate), 06_fee_timeline.csv and host_only_fee_history note section 1"),
    "emea": a("pre-existing single-fee listing share, EMEA", 0.20, 0.10, 0.28, "assumed",
              "Dec 2020 mandate for software-connected hosts in most countries; PMS share of European supply not disclosed"),
    "latam": a("pre-existing single-fee listing share, LatAm", 0.08, 0.04, 0.12, "assumed",
               "Mexico, Argentina, Uruguay exempt from the Dec 2020 mandate; rest of the region covered"),
    "apac": a("pre-existing single-fee listing share, APAC", 0.15, 0.08, 0.22, "assumed",
              "Australia mandatory from Nov 2020 (trade press), Taiwan exempt"),
}
# tranche 1, 27 October 2025: existing software-connected hosts still on the split fee. These sit
# mostly in the countries exempted in 2020 (US, Canada, Mexico, Argentina, Uruguay, Taiwan, Bahamas).
t1 = {
    "na": a("tranche-1 migrants (split PMS hosts), NA listing share", 0.30, 0.22, 0.36, "assumed, calibrated",
            "set so the blended share reaches the disclosed 'over a quarter' (27%) at the 7 May 2026 call; US professional-manager share of supply not disclosed"),
    "emea": a("tranche-1 migrants, EMEA listing share", 0.02, 0.01, 0.04, "assumed", "residual split-fee PMS hosts after the 2020 mandate"),
    "latam": a("tranche-1 migrants, LatAm listing share", 0.10, 0.06, 0.14, "assumed", "Mexico, Argentina, Uruguay PMS hosts (exempt in 2020)"),
    "apac": a("tranche-1 migrants, APAC listing share", 0.01, 0.005, 0.02, "assumed", "Taiwan PMS hosts (exempt in 2020)"),
}
new_pms = a("new software-connected hosts defaulting to the single fee, blended pp per quarter from 3Q25", 0.004, 0.002, 0.008, "assumed",
            "Guesty notice: from 25 Aug 2025 new PMS-connected hosts default to the single fee (fee-churn catalyst note)")
frac_4q25 = a("fraction of 4Q25 bookings confirmed after the 27 Oct 2025 tranche-1 date", 66 / 92, 66 / 92, 66 / 92, "sourced date, descriptive arithmetic",
              "27 Oct to 31 Dec is 66 of 92 days; fee applies by booking confirmation date (host notice via fee-churn note)")
# tranche 2: 2026 expansion. Anchors: 27% at 7 May, 50% at 6 Aug, UK 22 Jun, deadlines 15 Sep (non-EEA) and 13 Oct (EEA/CH), complete by year-end.
share_call_1q26 = a("single-fee listing share at the 7 May 2026 call", 0.27, 0.26, 0.30, "sourced (over a quarter, D041)", "1Q26 call via stockanalysis mirror")
share_call_2q26 = a("single-fee listing share at the 6 Aug 2026 call", 0.50, 0.45, 0.55, "sourced (approximately half, D047)", "2Q26 call via stockanalysis mirror")
# quarter-average total single-fee share of listings, tranche 2 path (blended), by month then averaged
month_path = a("tranche-2 monthly path: total single-fee share at end of Apr/May/Jun/Jul/Aug/Sep/Oct/Nov/Dec 2026",
               "27/27/36/45/52/75/92/98/100", "26/26/32/40/47/65/85/95/100", "30/32/42/52/60/85/96/100/100", "assumed, anchored",
               "flat to the 7 May call, UK 22 Jun step, ramp to the 15 Sep non-EEA deadline, 13 Oct EEA/CH deadline, complete by year-end (2Q26 letter, host notice)")
# regional timing of tranche 2: EMEA carries the EEA (13 Oct) deadline so lags the rest of the world in 3Q26; UK moves early
t2_region_lag = a("EMEA tranche-2 share of its eventual migration reached by end-Sep 2026", 0.55, 0.45, 0.70, "assumed",
                  "EEA/CH deadline 13 Oct vs 15 Sep elsewhere; UK-resident hosts 22 Jun")
nights_factor_t1 = a("nights per listing, tranche-1 (PMS) cohort relative to average", 1.3, 1.0, 1.6, "assumed",
                     "professionally managed listings run higher occupancy and availability; no disclosure")
nights_factor_t2 = a("nights per listing, tranche-2 cohort relative to average", 1.0, 1.0, 1.0, "assumed", "the remainder of the base")
nights_factor_pre = a("nights per listing, pre-existing single-fee cohort relative to average", 1.3, 1.0, 1.6, "assumed", "same as tranche 1: software-connected")

CALIBRATED = {}

# ------------------------------------------------------------------------------------------
# build
# ------------------------------------------------------------------------------------------
VARIANTS = {  # which assumption column each named variant draws: pre-existing level, other tranche-1 regions, path, nights factors
    "central": {"pre": "central", "t1": "central", "path": "central", "nf": "central"},
    "low_migrant": {"pre": "high", "t1": "low", "path": "low", "nf": "low"},   # high pre-existing cohort => small split-to-single cohort
    "high_migrant": {"pre": "low", "t1": "high", "path": "high", "nf": "high"},  # low pre-existing cohort => large split-to-single cohort
}
CALIB_TARGET = {"central": 0.26, "low_migrant": 0.26, "high_migrant": 0.26}  # blended total single-fee listing share, 1Q26 quarter average, so that the 7 May call reads 'over a quarter'


def build(variant):
    V = VARIANTS[variant]
    v = variant
    path = [float(x) / 100 for x in month_path[V["path"]].split("/")]  # Apr..Dec 2026 end-of-month total share
    PRE = {r: pre[r][V["pre"]] for r in REGIONS}
    T1 = {r: t1[r][V["t1"]] for r in REGIONS}
    NP = new_pms[V["t1"]]
    NF = {"pre": nights_factor_pre[V["nf"]], "t1": nights_factor_t1[V["nf"]], "t2": nights_factor_t2[V["nf"]]}
    # calibrate the NA tranche-1 share so the blended 1Q26 total hits the target (sourced anchor)
    s26, _ = shares["1Q26"]
    other = sum(s26[j] * (PRE[rr] + (T1[rr] if rr != "na" else 0.0)) for j, rr in enumerate(REGIONS)) + NP * 3
    T1["na"] = max(0.0, min(0.6, (CALIB_TARGET[v] - other) / s26[0] - PRE["na"]))
    CALIBRATED[v] = T1["na"]
    rows = []
    for q in QUARTERS:
        yr = 2000 + int(q[2:]); qn = int(q[0])
        s_reg, s_lab = shares[q]
        reg = {}
        for i, r in enumerate(REGIONS):
            p = PRE[r]
            m1 = 0.0  # tranche-1 migrant share (split -> single), quarter average
            m2 = 0.0  # tranche-2 migrant share (split -> single), quarter average
            step = ""
            if (yr, qn) < (2025, 3):
                step = "pre-migration: pre-existing cohort only (sourced dates, assumed level)"
            elif (yr, qn) == (2025, 3):
                m1 = NP * 0.4  # 25 Aug start, about 5 of 13 weeks
                step = "25 Aug 2025 new PMS-connected hosts default to single fee (sourced date, assumed size)"
            elif (yr, qn) == (2025, 4):
                m1 = T1[r] * frac_4q25["central"] + NP * 2
                step = "27 Oct 2025 tranche 1 (PMS split-fee hosts), 66/92 of bookings; 1 Dec pre-existing 15% -> 15.5% (sourced dates)"
            elif (yr, qn) == (2026, 1):
                m1 = T1[r] + NP * 3
                step = "tranche 1 complete; 'over a quarter' of listings at 7 May call (sourced level)"
            else:
                m1 = T1[r] + NP * (3 + (qn - 1) * 3 if yr == 2026 else 0)
                # tranche 2: total blended path minus the blended level after tranche 1
                blended_after_t1 = sum(shares[q][0][j] * (PRE[rr] + T1[rr]) for j, rr in enumerate(REGIONS)) + NP * 3
                months = {2: path[0:3], 3: path[3:6], 4: path[6:9]}[qn]
                # quarter average of the end-of-month path, using the prior month end as the start
                prev_end = {2: share_call_1q26["central"], 3: path[2], 4: path[5]}[qn]
                pts = [prev_end] + list(months)
                qavg_total = float(np.mean([(pts[k] + pts[k + 1]) / 2 for k in range(3)]))
                t2_blended = max(0.0, qavg_total - blended_after_t1)
                # distribute tranche 2 to regions in proportion to each region's remaining split-fee base,
                # with EMEA lagged in 3Q26 (EEA deadline 13 Oct) and caught up in 4Q26
                remaining = {rr: max(0.0, 1 - PRE[rr] - T1[rr]) for rr in REGIONS}
                wts = {rr: shares[q][0][j] * remaining[rr] for j, rr in enumerate(REGIONS)}
                if qn == 3:
                    wts["emea"] *= t2_region_lag[V["t1"]]
                tot = sum(wts.values())
                m2 = t2_blended * (wts[r] / tot) / shares[q][0][i] if tot > 0 else 0.0
                m2 = min(m2, remaining[r])
                step = {2: "tranche 2 begins: testing expansion, UK-resident hosts 22 Jun (sourced dates); quarter path assumed",
                        3: "tranche 2: 15 Sep non-EEA deadline inside the quarter, EEA lags to 13 Oct (sourced dates); path assumed",
                        4: "tranche 2: 13 Oct EEA/CH deadline, complete by year-end (sourced); path assumed"}[qn]
            pre_lvl = p
            reg[r] = (pre_lvl, m1, m2, step)
        # regional rows
        for i, r in enumerate(REGIONS):
            pre_lvl, m1, m2, step = reg[r]
            for basis in ("listings", "nights"):
                if basis == "listings":
                    f_pre, f1, f2 = 1.0, 1.0, 1.0
                else:
                    f_pre, f1, f2 = NF["pre"], NF["t1"], NF["t2"]
                mig = min(1.0, m1 * f1 + m2 * f2)
                pre_n = min(1.0 - mig, pre_lvl * f_pre)
                rows.append({"quarter": q, "region": r, "basis": basis, "variant": v,
                             "nights_share_of_region_in_global": s_reg[i], "nights_share_label": s_lab,
                             "pre_existing_single_fee_share": pre_n,
                             "migrated_split_to_single_share": mig,
                             "migrated_tranche1_share": min(1.0, m1 * f1), "migrated_tranche2_share": min(1.0, m2 * f2),
                             "total_single_fee_share": min(1.0, pre_n + mig),
                             "step_label": step})
        # blended rows
        for basis in ("listings", "nights"):
            sub = [x for x in rows if x["quarter"] == q and x["basis"] == basis and x["variant"] == v and x["region"] in REGIONS]
            def blend(col):
                return float(sum(x[col] * x["nights_share_of_region_in_global"] for x in sub))
            rows.append({"quarter": q, "region": "blended", "basis": basis, "variant": v,
                         "nights_share_of_region_in_global": 1.0, "nights_share_label": s_lab,
                         "pre_existing_single_fee_share": blend("pre_existing_single_fee_share"),
                         "migrated_split_to_single_share": blend("migrated_split_to_single_share"),
                         "migrated_tranche1_share": blend("migrated_tranche1_share"),
                         "migrated_tranche2_share": blend("migrated_tranche2_share"),
                         "total_single_fee_share": blend("total_single_fee_share"),
                         "step_label": sub[0]["step_label"]})
    return pd.DataFrame(rows)

df = pd.concat([build(v) for v in ("central", "low_migrant", "high_migrant")], ignore_index=True)
A.append({"parameter": "tranche-1 migrants (split PMS hosts), NA listing share, calibrated per variant", "central": round(CALIBRATED["central"], 4),
          "low": round(CALIBRATED["low_migrant"], 4), "high": round(CALIBRATED["high_migrant"], 4), "label": "assumed, calibrated",
          "source": "solved so the blended 1Q26 quarter-average total single-fee listing share is 0.26 (call: over a quarter on 7 May 2026)"})
pd.DataFrame(A).to_csv(os.path.join(OUT, "K1_assumptions.csv"), index=False)
# y/y change in the migrated share (the quantity a y/y ADR residual responds to)
df = df.sort_values(["variant", "basis", "region", "quarter"], key=lambda s: s.map(QUARTERS.index) if s.name == "quarter" else s)
df["migrated_share_yoy_change"] = df.groupby(["variant", "basis", "region"])["migrated_split_to_single_share"].diff(4).fillna(0.0)
df["pre_existing_share_yoy_change"] = df.groupby(["variant", "basis", "region"])["pre_existing_single_fee_share"].diff(4).fillna(0.0)
# the 1 Dec 2025 0.5 pp step applies to the pre-existing cohort: flag the quarters where it is inside the y/y window
df["pre_existing_fee_step_in_yoy_window"] = df["quarter"].map(lambda q: 1.0 if q in ("1Q26", "2Q26", "3Q26") else (1 / 3 if q == "4Q25" else 0.0))
df["label"] = np.where(df["quarter"].map(lambda q: (2000 + int(q[2:]), int(q[0]))) < (2025, 3), "assumed level, sourced dates (no migration in window)",
                       np.where(df["quarter"].isin(["4Q25", "1Q26", "2Q26"]), "sourced dates and disclosed listing shares, assumed regional split",
                                "assumed path anchored on sourced deadlines"))
cols = ["quarter", "region", "basis", "variant", "nights_share_of_region_in_global", "nights_share_label",
        "pre_existing_single_fee_share", "migrated_tranche1_share", "migrated_tranche2_share", "migrated_split_to_single_share",
        "total_single_fee_share", "migrated_share_yoy_change", "pre_existing_share_yoy_change", "pre_existing_fee_step_in_yoy_window",
        "step_label", "label"]
df = df[cols]
df.to_csv(os.path.join(OUT, "K1_migrated_cohort_share.csv"), index=False)

b = df[(df.region == "blended")].pivot_table(index="quarter", columns=["variant", "basis"], values=["migrated_split_to_single_share", "total_single_fee_share"])
b = b.reindex(QUARTERS)
pd.set_option("display.width", 250)
print(b.round(3).to_string())
chk = df[(df.region == "blended") & (df.basis == "listings") & (df.variant == "central")].set_index("quarter")
print("\ncentral blended listing basis, total single-fee share at 1Q26 / 2Q26 quarter average:",
      round(chk.loc["1Q26", "total_single_fee_share"], 3), round(chk.loc["2Q26", "total_single_fee_share"], 3),
      "(disclosed: over a quarter at 7 May, about half at 6 Aug)")
print("wrote", os.path.join(OUT, "K1_migrated_cohort_share.csv"))
