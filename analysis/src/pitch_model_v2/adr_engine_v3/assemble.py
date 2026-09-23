"""adr_engine / assemble.py — reported ADR path = ex-FX mechanism + ex-ante FX; levels chained on disclosed year-ago ADR
(3Q27/4Q27 on the engine's own 3Q26/4Q26); GBV cross-check on the nights line; the view against the Street."""
from __future__ import annotations
import numpy as np
import pandas as pd
from scipy import stats
from . import config as C
from . import exfx as X

ADR_HIST = {"3Q25": 171.29, "4Q25": 167.51, "1Q26": 186.82, "2Q26": 183.73}


def build(fx_asof: str = "2026-09-21") -> pd.DataFrame:
    fc = pd.read_csv(C.OUT / "fx_forecast_asof.csv"); fc = fc[fc["asof"] == fx_asof].set_index("quarter")
    base = X.forward(); env = X.envelope(fc.sd)
    card = pd.read_csv(C.CARD_V3); card = card[(card.variant == "v3_without_K") & (card.fx_estimator == "midpoint")].drop_duplicates("quarter").set_index("quarter")
    rows = []; level = dict(ADR_HIST); level_v1 = dict(ADR_HIST)
    for q in C.FORWARD_QUARTERS:
        fx = float(fc.loc[q, "fx_pp_point_spot_held"]); ex = float(base.loc[q, "exfx_yoy"]); rep = ex + fx
        bq = C.prior_quarter(q, 4); lvl = level[bq] * (1 + rep / 100); level[q] = lvl
        half = float(env.loc[q, "reported_half_band_pp"]); sd = half   # RSS half-band treated as one sd for the tail arithmetic
        st = C.STREET_ADR.get(q); street = st[0] if st else np.nan
        street_yoy = (street / level[bq] - 1) * 100 if st else np.nan
        z = (rep - street_yoy) / sd if st else np.nan
        p_ge_street = float(1 - stats.norm.cdf((street_yoy - rep) / sd)) if st else np.nan
        # audit fix (a): the registered V1 variant's FX beside V0's, on its own chain (V0 stays the leg)
        fx1 = float(fc.loc[q, "fx_pp_point_v1"]); rep1 = ex + fx1; lvl1 = level_v1[bq] * (1 + rep1 / 100); level_v1[q] = lvl1
        street_yoy1 = (street / level_v1[bq] - 1) * 100 if st else np.nan
        p1 = float(1 - stats.norm.cdf((street_yoy1 - rep1) / sd)) if st else np.nan
        nights = C.NIGHTS_BASE_M[q]
        rows.append({"quarter": q, "adr_yoy_exfx_pct": ex, "fx_pp": fx, "adr_yoy_reported_pct": rep, "adr_usd": lvl, "adr_usd_base_year": level[bq],
                     "band_half_pp": half, "adr_usd_lo": level[bq] * (1 + (rep - half) / 100), "adr_usd_hi": level[bq] * (1 + (rep + half) / 100),
                     "fx_p10": float(fc.loc[q, "p10"]), "fx_p90": float(fc.loc[q, "p90"]), "fx_obs_frac": float(fc.loc[q, "obs_frac_at_asof"]),
                     "street_adr_usd": street, "street_yoy_pct": street_yoy, "z_vs_street": z, "p_print_ge_street": p_ge_street,
                     "street_n": st[3] if st else np.nan,
                     "fx_pp_v1": fx1, "adr_usd_fx_v1": lvl1, "p_print_ge_street_fx_v1": p1,
                     "card_v3_adr_usd": float(card.loc[q, "adr_usd_point"]) if q in card.index else np.nan,
                     "card_v3_exfx_pct": float(card.loc[q, "adr_exfx_yoy_pp"]) if q in card.index else np.nan,
                     "card_v3_fx_pp": float(card.loc[q, "fx_effect_pp"]) if q in card.index else np.nan,
                     "nights_m": nights, "gbv_busd": nights * lvl / 1000.0,
                     "street_gbv_busd": (st[0] * {"3Q26": 149.0, "4Q26": 134.0}[q] / 1000.0) if st else np.nan})
    d = pd.DataFrame(rows).set_index("quarter")
    d.loc["FY27", "adr_usd"] = float((d.loc[["1Q27", "2Q27", "3Q27", "4Q27"], "adr_usd"] * d.loc[["1Q27", "2Q27", "3Q27", "4Q27"], "nights_m"]).sum() / d.loc[["1Q27", "2Q27", "3Q27", "4Q27"], "nights_m"].sum())
    d.loc["FY27", "gbv_busd"] = float(d.loc[["1Q27", "2Q27", "3Q27", "4Q27"], "gbv_busd"].sum())
    d.loc["FY27", "nights_m"] = float(d.loc[["1Q27", "2Q27", "3Q27", "4Q27"], "nights_m"].sum())
    fy26_adr = (156.2 * 186.82 + 148.3 * 183.73 + 146.8 * d.loc["3Q26", "adr_usd"] + 131.8 * d.loc["4Q26", "adr_usd"]) / (156.2 + 148.3 + 146.8 + 131.8)
    d.loc["FY26", "adr_usd"] = fy26_adr; d.loc["FY26", "nights_m"] = 583.1; d.loc["FY26", "gbv_busd"] = (29.2 + 27.2 + d.loc["3Q26", "gbv_busd"] + d.loc["4Q26", "gbv_busd"])
    d.loc["FY27", "adr_yoy_reported_pct"] = (d.loc["FY27", "adr_usd"] / fy26_adr - 1) * 100
    return d


def scenario_table(fx_asof: str = "2026-09-21") -> pd.DataFrame:
    """Every ex-FX rule × the FX point, as reported ADR $ and GBV, 3Q26 and 4Q26 — the alternatives beside the base."""
    fc = pd.read_csv(C.OUT / "fx_forecast_asof.csv"); fc = fc[fc["asof"] == fx_asof].set_index("quarter")
    alts = X.alternatives(); alts = alts[~alts.rule.str.startswith("K4")]
    rows = []
    for rule, g in alts.groupby("rule", sort=False):
        g = g.set_index("quarter")
        for q in ["3Q26", "4Q26", "1Q27", "2Q27"]:
            ex = float(g.loc[q, "exfx_yoy_pct"]); fx = float(fc.loc[q, "fx_pp_point_spot_held"]); bq = C.prior_quarter(q, 4)
            lvl = ADR_HIST[bq] * (1 + (ex + fx) / 100)
            fx1 = float(fc.loc[q, "fx_pp_point_v1"]); lvl1 = ADR_HIST[bq] * (1 + (ex + fx1) / 100)
            rows.append({"rule": rule, "quarter": q, "exfx_pct": ex, "fx_pp": fx, "reported_pct": ex + fx, "adr_usd": lvl,
                         "gbv_busd": C.NIGHTS_BASE_M[q] * lvl / 1000.0, "vs_base_usd": np.nan,
                         "fx_pp_v1": fx1, "adr_usd_fx_v1": lvl1})
    d = pd.DataFrame(rows)
    base = d[d.rule.str.startswith("base:")].set_index("quarter").adr_usd
    d["vs_base_usd"] = d.adr_usd.values - base.loc[d.quarter].values
    return d
