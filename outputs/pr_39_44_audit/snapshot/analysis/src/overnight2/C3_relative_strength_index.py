"""
Workstream C, step 3. Consumer relative strength by origin region.

Country composite: each indicator is z-scored within country over a fixed window that EXCLUDES
2020 and 2021 (the COVID collapse and rebound would otherwise set the scale), signed so that
higher always means a stronger consumer, then averaged over the indicators that country has.
Region index = origin-weighted mean of its country composites. Relative strength = region index
less the global origin-weighted index, so the four regions are relative to each other by
construction and the global level drops out.

Origin weights are an ASSUMPTION, documented in WEIGHTS below and stress tested with three
alternatives. Airbnb does not disclose origin nights shares; its regional disclosure is by
listing location.

Reads:  data/processed/overnight2/C/consumer_panel_monthly.csv
Writes: data/processed/overnight2/C/country_strength_monthly.csv
        data/processed/overnight2/C/regional_strength_monthly.csv
        data/processed/overnight2/C/regional_strength_quarterly.csv
        data/processed/overnight2/C/C3_weights.csv
        data/processed/overnight2/C/C3_weight_sensitivity.csv
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[3] / "data/processed/overnight2/C"

# sign: +1 means higher value = stronger consumer
SIGNS = {
    "cci": +1,
    "unemp_rate": -1,
    "retail_vol_yoy": +1,
    "real_wage_yoy": +1,
    "equity_yoy": +1,
    "saving_rate": -1,          # precautionary saving rises when households retrench
    "real_hh_income_pc_yoy": +1,
    "cpi_yoy": -1,              # partly double counts real_wage_yoy; sensitivity drops it
}

VARIANTS = {
    "base": list(SIGNS),
    "no_cpi": [k for k in SIGNS if k != "cpi_yoy"],
    "no_saving": [k for k in SIGNS if k != "saving_rate"],
    "core4": ["cci", "unemp_rate", "retail_vol_yoy", "equity_yoy"],
}

# Within-region origin weights. Judgement, anchored on: the 10-K Geographic Mix; the letters'
# named core markets (US, UK, France, Canada, Australia) and expansion markets (Brazil, Mexico,
# Japan, India, Korea, Germany, Italy, Spain); and the fact that Airbnb closed its China
# domestic business in July 2022 and now serves China outbound only, so CHN is held small.
WEIGHTS = {
    "na":    {"USA": 0.88, "CAN": 0.12},
    "emea":  {"GBR": 0.17, "FRA": 0.15, "DEU": 0.15, "ESP": 0.12, "ITA": 0.12, "NLD": 0.06,
              "POL": 0.04, "PRT": 0.04, "IRL": 0.03, "SWE": 0.03, "CHE": 0.03, "TUR": 0.03,
              "ISR": 0.015, "ZAF": 0.015},
    "latam": {"BRA": 0.40, "MEX": 0.35, "ARG": 0.08, "CHL": 0.07, "COL": 0.07, "CRI": 0.03},
    "apac":  {"JPN": 0.28, "AUS": 0.22, "KOR": 0.18, "IND": 0.15, "CHN": 0.08, "IDN": 0.05,
              "NZL": 0.04},
}

# Region origin weights. Proxy: FY2025 10-K nights shares by LISTING location (NA 29.6,
# EMEA 40.3, LatAm 16.9, APAC 13.1). Exact for domestic nights, roughly right for intra-region
# cross-border, wrong for inter-region flows, which is why the tilt variant exists.
REGION_W = {"base": {"na": 0.296, "emea": 0.403, "latam": 0.169, "apac": 0.131},
            "tilt_na_down": {"na": 0.266, "emea": 0.418, "latam": 0.174, "apac": 0.142},
            "equal": {"na": 0.25, "emea": 0.25, "latam": 0.25, "apac": 0.25}}

Z_EXCLUDE = (pd.Timestamp("2020-01-01"), pd.Timestamp("2021-12-31"))
Z_START = pd.Timestamp("2018-01-01")


def country_composite(panel: pd.DataFrame, indicators: list[str]) -> pd.DataFrame:
    p = panel[panel["indicator"].isin(indicators)].copy()
    wide = p.pivot_table(index=["country", "date"], columns="indicator", values="value")
    zs = {}
    for ind in indicators:
        if ind not in wide:
            continue
        s = wide[ind]
        frame = s.reset_index()
        mask = (frame["date"] >= Z_START) & ~frame["date"].between(*Z_EXCLUDE)
        stats = frame[mask].groupby("country")[ind].agg(["mean", "std"])
        j = frame.join(stats, on="country")
        z = (j[ind] - j["mean"]) / j["std"].replace(0.0, np.nan)
        zs[ind] = pd.Series(z.values * SIGNS[ind],
                            index=pd.MultiIndex.from_frame(j[["country", "date"]]))
    z = pd.DataFrame(zs)
    out = pd.DataFrame({
        "z_mean": z.mean(axis=1, skipna=True),
        "n_ind": z.notna().sum(axis=1),
    }).reset_index()
    return out[out["n_ind"] >= 2]


def regionalise(comp: pd.DataFrame, region_w: dict[str, float]) -> pd.DataFrame:
    rows = []
    for region, cw in WEIGHTS.items():
        sub = comp[comp["country"].isin(cw)].copy()
        sub["w"] = sub["country"].map(cw)
        g = sub.groupby("date").apply(
            lambda d: pd.Series({
                "index_z": np.average(d["z_mean"], weights=d["w"]),
                "weight_covered": d["w"].sum(),
                "n_countries": len(d),
            }), include_groups=False)
        g["region"] = region
        rows.append(g.reset_index())
    r = pd.concat(rows, ignore_index=True)
    piv = r.pivot(index="date", columns="region", values="index_z")
    gw = pd.Series(region_w)
    glob = (piv[gw.index] * gw).sum(axis=1) / gw.sum()
    r = r.merge(glob.rename("global_z").reset_index(), on="date")
    r["relative_z"] = r["index_z"] - r["global_z"]
    return r.sort_values(["date", "region"])


def to_quarterly(r: pd.DataFrame) -> pd.DataFrame:
    r = r.copy()
    r["q"] = pd.PeriodIndex(r["date"], freq="Q")
    q = r.groupby(["q", "region"], as_index=False).agg(
        index_z=("index_z", "mean"), global_z=("global_z", "mean"),
        relative_z=("relative_z", "mean"), n_months=("date", "size"))
    q["quarter"] = q["q"].apply(lambda p: f"{p.quarter}Q{str(p.year)[2:]}")
    q = q.sort_values(["q", "region"])
    # 2-quarter change in relative strength
    q["relative_z_chg2q"] = q.groupby("region")["relative_z"].transform(lambda s: s - s.shift(2))
    q["relative_z_chg1q"] = q.groupby("region")["relative_z"].transform(lambda s: s - s.shift(1))
    return q.drop(columns="q")


if __name__ == "__main__":
    panel = pd.read_csv(OUT / "consumer_panel_monthly.csv", parse_dates=["date"])

    comp = country_composite(panel, VARIANTS["base"])
    comp.to_csv(OUT / "country_strength_monthly.csv", index=False)

    reg = regionalise(comp, REGION_W["base"])
    reg.to_csv(OUT / "regional_strength_monthly.csv", index=False)
    q = to_quarterly(reg)
    q.to_csv(OUT / "regional_strength_quarterly.csv", index=False)

    wrows = [{"level": "region", "region": k, "unit": k, "weight": v, "basis": "FY2025 10-K nights share by listing location, used as an origin proxy"}
             for k, v in REGION_W["base"].items()]
    for region, cw in WEIGHTS.items():
        for c, w in cw.items():
            wrows.append({"level": "country", "region": region, "unit": c, "weight": w,
                          "basis": "judgement, anchored on letters' named core and expansion markets"})
    pd.DataFrame(wrows).to_csv(OUT / "C3_weights.csv", index=False)

    # ---- sensitivity: indicator set x region weighting x equal country weights
    sens = []
    for vname, inds in VARIANTS.items():
        c = country_composite(panel, inds)
        for rwname, rw in REGION_W.items():
            rr = to_quarterly(regionalise(c, rw))
            for _, row in rr[rr["quarter"].isin(["1Q26", "2Q26", "3Q26"])].iterrows():
                sens.append({"variant": vname, "region_weights": rwname, "country_weights": "judgement",
                             "quarter": row["quarter"], "region": row["region"],
                             "relative_z": round(row["relative_z"], 3)})
    # equal country weights inside each region
    saved = {k: dict(v) for k, v in WEIGHTS.items()}
    for k in WEIGHTS:
        WEIGHTS[k] = {c: 1.0 / len(saved[k]) for c in saved[k]}
    c = country_composite(panel, VARIANTS["base"])
    rr = to_quarterly(regionalise(c, REGION_W["base"]))
    for _, row in rr[rr["quarter"].isin(["1Q26", "2Q26", "3Q26"])].iterrows():
        sens.append({"variant": "base", "region_weights": "base", "country_weights": "equal",
                     "quarter": row["quarter"], "region": row["region"],
                     "relative_z": round(row["relative_z"], 3)})
    for k in WEIGHTS:
        WEIGHTS[k] = saved[k]
    pd.DataFrame(sens).to_csv(OUT / "C3_weight_sensitivity.csv", index=False)

    print("=== relative strength, z units, quarterly ===")
    show = q.pivot(index="quarter", columns="region", values="relative_z").round(2)
    order = [f"{qq}Q{yy}" for yy in ["22", "23", "24", "25", "26"] for qq in [1, 2, 3, 4]]
    show = show.reindex([o for o in order if o in show.index])
    print(show.to_string())
    print()
    print("=== 2026 YTD (Jan-Aug) mean relative z ===")
    ytd = reg[reg["date"] >= "2026-01-01"].groupby("region")["relative_z"].mean().round(3)
    print(ytd.to_string())
    print()
    print("=== months covered per region in 3Q26 to date ===")
    print(reg[reg["date"] >= "2026-07-01"].groupby("region").agg(
        n=("date", "size"), cov=("weight_covered", "mean"), nc=("n_countries", "mean")).to_string())
    print()
    print("=== sensitivity spread of 2026 readings ===")
    s = pd.DataFrame(pd.read_csv(OUT / "C3_weight_sensitivity.csv"))
    print(s.pivot_table(index=["quarter", "region"], columns=["variant", "region_weights", "country_weights"],
                        values="relative_z").round(2).to_string())

