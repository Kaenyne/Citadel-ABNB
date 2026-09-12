"""fx_lag_v2 / baskets.py  -- COPY of fx_lag/baskets.py, re-pointed at the
2026-09-11 FX refresh (fx_daily_2026-09-11.csv) instead of the overnight file.
Stage (a): the daily booking-date currency basket X^B.

Sources
-------
data/processed/forecast_methods/fx_lag_v2/fx_daily_2026-09-11.csv
                                            FRED bilateral dailies, USD per unit,
                                            9 currencies + DTWEXBGS broad USD,
                                            2018-01-02 .. 2026-09-04 (H.10 lag)
data/processed/overnight/10_fx_basket.csv   currency weights within each region
                                            (JUDGEMENT weights, vintage = the
                                            overnight build; documented, not fitted)
data/processed/forecast_methods/L0/L0_exact_regional_revenue.csv
                                            filed regional revenue -> the regional
                                            weights of the global revenue-weighted
                                            basket (trailing-4-quarter shares,
                                            PIT-legal: every cell is a filed 10-Q/10-K
                                            number with a knowable_from date)
USD_BROAD rows of the same file          broad trade-weighted USD index

Convention: every basket is expressed as y/y % change in USD per unit of foreign
currency, so a POSITIVE number is a WEAKER dollar and a POSITIVE revenue tailwind.
USD legs carry 0 y/y by construction.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import OVN, L0, FX_DAILY, to_period, short, write

FRED_CACHE = OVN / "05_fred_cache"
REGIONS = ["na", "emea", "latam", "apac"]


def _daily_bilaterals() -> pd.DataFrame:
    """The refreshed daily file, bilaterals only (USD_BROAD is an index level and
    is handled separately in broad_usd_quarterly)."""
    d = pd.read_csv(FX_DAILY, parse_dates=["date"])
    return d[d["unit"] == "usd_per_foreign_unit"].copy()


def currency_quarterly() -> pd.DataFrame:
    d = _daily_bilaterals()
    d["q"] = d["date"].dt.to_period("Q")
    avg = d.groupby(["ccy", "q"])["usd_per_unit"].mean().unstack(0)
    nobs = d.groupby(["ccy", "q"])["usd_per_unit"].size().unstack(0)
    yoy = (avg / avg.shift(4) - 1.0) * 100.0
    out = yoy.reset_index().rename(columns={"q": "quarter_p"})
    out.insert(0, "quarter", [short(p) for p in out["quarter_p"]])
    out = out.drop(columns=["quarter_p"])
    out["n_days_min"] = nobs.min(axis=1).values
    return out, avg, yoy


def basket_weights() -> pd.DataFrame:
    b = pd.read_csv(OVN / "10_fx_basket.csv")
    w = b[(b["currency"] != "BASKET") & (b["region"].isin(REGIONS))].copy()
    # proxy_series maps synthetic legs onto a traded currency
    w["ccy_used"] = np.where(w["proxy_series"].notna(), w["proxy_series"], w["currency"])
    return w[["region", "currency", "ccy_used", "weight", "fred_id"]]


def regional_baskets(yoy: pd.DataFrame, w: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for region, g in w.groupby("region"):
        tot = g["weight"].sum()
        s = pd.Series(0.0, index=yoy.index)
        for _, r in g.iterrows():
            leg = 0.0 if r["ccy_used"] == "USD" else yoy[r["ccy_used"]]
            s = s + r["weight"] * leg
        rows.append(pd.Series(s / tot, name=region))
    out = pd.concat(rows, axis=1)
    return out


def regional_revenue_weights() -> pd.DataFrame:
    """Trailing-4-quarter filed regional revenue shares from the L0 spine.

    PIT CAVEAT (named by the round-1 verifier, documented here and in the note):
    this function is NOT filtered on L0 `knowable_from`.  It therefore uses the
    current vintage of the regional revenue split for every historical quarter.
    The quarterly basket series built on top of it (`02_basket_quarterly.csv`) is
    the source of the TRAINING FEATURES b_lag1/2/3 and eur_lag1/2 used in the PIT
    expanding-window fits, so those features are not vintage-stamped the way the
    target quarter's own lag-0 basket is (`pit_fx.regional_shares_asof`, which IS
    filtered on knowable_from).  Practical risk is low: FRED bilateral spot rates
    never revise, and L0_exact_regional_revenue.csv carries basis in {filed,
    back_out} with no restated rows, so the shares a contemporaneous forecaster
    would have seen are the same numbers.  It is an asymmetry, not a measured leak;
    it is recorded in 00_pit_caveats.csv.
    """
    l0 = pd.read_csv(L0 / "L0_exact_regional_revenue.csv")
    l0["p"] = [to_period(q) for q in l0["quarter"]]
    piv = l0.pivot_table(index="p", columns="region", values="revenue_musd", aggfunc="sum")
    piv = piv[REGIONS]
    t4 = piv.rolling(4).sum()
    sh = t4.div(t4.sum(axis=1), axis=0)
    return sh


def broad_usd_quarterly() -> pd.Series:
    """Broad trade-weighted USD (DTWEXBGS) y/y, from the 2026-09-11 refresh rather
    than the stale FRED cache.  POSITIVE = STRONGER dollar = revenue headwind."""
    b = pd.read_csv(FX_DAILY, parse_dates=["date"])
    b = b[b["unit"] == "index_level_usd_strength"].dropna(subset=["usd_per_unit"])
    b["q"] = b["date"].dt.to_period("Q")
    avg = b.groupby("q")["usd_per_unit"].mean()
    return (avg / avg.shift(4) - 1.0) * 100.0


def build() -> dict:
    cq, avg, yoy = currency_quarterly()
    write(cq, "01_currency_quarterly_yoy.csv")

    w = basket_weights()
    wtab = w.copy()
    wtab["weight_vintage"] = "10_fx_basket.csv, overnight build; JUDGEMENT weights"
    write(wtab, "01b_basket_weights_used.csv")

    rb = regional_baskets(yoy, w)
    shares = regional_revenue_weights()

    idx = rb.index
    # shares are trailing-4 filed revenue; the first is 4Q22. Before that we hold
    # the earliest filed share constant (bfill) -- documented, not fitted, and it
    # only affects pre-4Q22 quarters, which enter no likelihood.
    sh = shares.reindex(idx).ffill().bfill()
    glob = (rb[REGIONS] * sh[REGIONS]).sum(axis=1)

    broad = broad_usd_quarterly().reindex(idx)

    panel = pd.DataFrame({
        "quarter": [short(p) for p in idx],
        "quarter_canon": [f"{p.year}Q{p.quarter}" for p in idx],
        "basket_na_yoy_pct": rb["na"].values,
        "basket_emea_yoy_pct": rb["emea"].values,
        "basket_latam_yoy_pct": rb["latam"].values,
        "basket_apac_yoy_pct": rb["apac"].values,
        "basket_global_rev_wtd_yoy_pct": glob.values,
        "eurusd_yoy_pct": yoy["EUR"].values,
        "usd_broad_yoy_pct": broad.values,
        "w_na": sh["na"].values, "w_emea": sh["emea"].values,
        "w_latam": sh["latam"].values, "w_apac": sh["apac"].values,
    })
    # quarter-end (last observation) global basket, for the "spot at quarter end" read
    last = _daily_bilaterals()
    last["q"] = last["date"].dt.to_period("Q")
    qend = last.sort_values("date").groupby(["ccy", "q"])["usd_per_unit"].last().unstack(0)
    qend_yoy = (qend / qend.shift(4) - 1.0) * 100.0
    rbe = regional_baskets(qend_yoy, w)
    she = shares.reindex(rbe.index).ffill().bfill()
    panel["basket_global_qend_yoy_pct"] = (rbe[REGIONS] * she[REGIONS]).sum(axis=1).reindex(idx).values

    panel = panel[panel["quarter_canon"] >= "2019Q1"].reset_index(drop=True)
    write(panel, "02_basket_quarterly.csv")

    # ---- reconciliation against the published 10_fx_basket.csv headline values
    pub = pd.read_csv(OVN / "10_fx_basket.csv")
    pubb = pub[pub["currency"] == "BASKET"].set_index("region")
    rec = []
    for q, col in [("1Q26", "usd_per_unit_yoy_1Q26_pct"),
                   ("2Q26", "usd_per_unit_yoy_2Q26_pct"),
                   ("3Q26", "usd_per_unit_yoy_3Q26_pct")]:
        row = panel[panel["quarter"] == q].iloc[0]
        for region in REGIONS + ["global_revenue_weighted"]:
            key = "basket_global_rev_wtd_yoy_pct" if region == "global_revenue_weighted" else f"basket_{region}_yoy_pct"
            rec.append({"quarter": q, "series": region,
                        "published_pct": float(pubb.loc[region, col]),
                        "rebuilt_pct": round(float(row[key]), 4),
                        "diff_pp": round(float(row[key]) - float(pubb.loc[region, col]), 4)})
    rec = pd.DataFrame(rec)
    rec["note"] = np.where(
        rec["quarter"] == "3Q26",
        "3Q26 published = QTD to 2026-08-28; rebuilt = QTD to 2026-09-04 (the refresh). "
        "A difference here is the refresh, not a reconciliation failure.",
        "1Q26/2Q26 are complete quarters; these must reconcile.")
    write(rec, "03_basket_reconciliation.csv")
    return {"panel": panel, "recon": rec, "currency_yoy": cq}


if __name__ == "__main__":
    build()
