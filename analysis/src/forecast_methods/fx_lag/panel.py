"""fx_lag / panel.py -- the analysis panel: disclosed FX points + baskets + hedge."""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import OVN, OUT, to_period, short, write


def load_panel() -> pd.DataFrame:
    k = pd.read_csv(OVN / "02_kpi_panel_quarterly.csv")
    k["p"] = [to_period(q) for q in k["quarter"]]
    keep = ["p", "revenue_musd", "gbv_busd", "fx_pts_adr", "fx_pts_revenue",
            "revenue_yoy_exfx_pct", "gbv_yoy_exfx_pct", "adr_yoy_exfx_pct"]
    k = k[[c for c in keep if c in k.columns]]

    b = pd.read_csv(OUT / "02_basket_quarterly.csv")
    b["p"] = [to_period(q) for q in b["quarter"]]
    b = b.drop(columns=["quarter", "quarter_canon"])

    h = pd.read_csv(OVN / "28_fx_hedge_disclosures.csv")
    h["p"] = [to_period(q) for q in h["quarter"]]
    h = h[["p", "stated_revenue_fx_pp", "gross_fx_ex_hedge_pp", "stated_adr_fx_pp",
           "hedge_effect_on_revenue_growth_pp", "reclassified_to_revenue_musd",
           "non_usd_revenue_share", "revenue_musd", "revenue_prior_year_musd"]]
    h = h.rename(columns={"revenue_musd": "revenue_musd_hedgefile"})

    m = pd.read_csv(OVN / "05_macro_quarterly_panel.csv")
    m["p"] = pd.PeriodIndex(m["quarter"], freq="Q")
    m = m[["p", "eurusd", "usd_broad", "rev_fx_pts"]].rename(
        columns={"eurusd": "eurusd_yoy_macro", "usd_broad": "usd_broad_yoy_macro",
                 "rev_fx_pts": "rev_fx_pts_macro"})

    d = b.merge(k, on="p", how="outer").merge(h, on="p", how="left").merge(m, on="p", how="left")
    d = d.sort_values("p").reset_index(drop=True)
    d["quarter"] = [short(p) for p in d["p"]]
    d["quarter_canon"] = [f"{p.year}Q{p.quarter}" for p in d["p"]]

    B = "basket_global_rev_wtd_yoy_pct"
    for L in (0, 1, 2, 3):
        d[f"b_lag{L}"] = d[B].shift(L)
        d[f"eur_lag{L}"] = d["eurusd_yoy_pct"].shift(L)
        d[f"brd_lag{L}"] = d["usd_broad_yoy_pct"].shift(L)
        d[f"adrfx_lag{L}"] = d["fx_pts_adr"].shift(L)

    # GBV in $m, and the Phi kernel base 2/3 GBV(q-1) + 1/3 GBV(q-2)
    d["gbv_musd"] = d["gbv_busd"] * 1000.0
    d["kernel_base_musd"] = (2.0 / 3.0) * d["gbv_musd"].shift(1) + (1.0 / 3.0) * d["gbv_musd"].shift(2)
    d["lambda_pct"] = 100.0 * d["revenue_musd"] / d["kernel_base_musd"]
    return d


def build():
    d = load_panel()
    write(d, "04_analysis_panel.csv")
    return d


if __name__ == "__main__":
    build()
