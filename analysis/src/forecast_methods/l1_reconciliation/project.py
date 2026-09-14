"""l1-reconciliation: projection, the kernel hand-off, and the FY27 decomposition.

ONE object crosses the boundary: gbv_musd, booking-dated, one number per quarter.
Revenue is then the kernel convolution of ALREADY-PRINTED GBV, per the architect:
    Revenue_q = lambda_season(q) * [ w * GBV_{q-1} + (1-w) * GBV_{q-2} ]
with w = 2/3 published and 0.33..0.667 propagated as the mandatory sensitivity.
No FX pp is ever added to revenue: booking-date FX is inside the lagged GBV base.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import data as D

KERNEL_W_PUBLISHED = 2.0 / 3.0
KERNEL_W_GRID = [0.33, 0.50, 2.0 / 3.0]

# Carried, NOT rebuilt tonight (decisions doc: FY27 lines are placeholders).
ASSUMED_FY27 = {
    "fee_take_rate_mechanism_pp": 0.9,   # half-weight fee step, owned by fee-takerate
    "new_lines_pp": 0.2,
    "regulation_pp": -0.3,
    "hedge_pp": 0.0,                     # hedge is in dollars, added ONCE, by kernel-lambda
}
BEDROOM_ELASTICITY = 0.23                # do NOT use the +2pp Street mapping


def seasonal_lambda(kpi: pd.DataFrame, w: float = KERNEL_W_PUBLISHED,
                    years=(2023, 2024, 2025, 2026)) -> dict:
    """lambda_s = Revenue_q / [w*GBV_{q-1} + (1-w)*GBV_{q-2}], averaged by season."""
    k = kpi.set_index("quarter")
    out = {}
    for s in range(1, 5):
        vals = []
        for yr in years:
            q = f"{yr}Q{s}"
            q1, q2 = D.qadd(q, -1), D.qadd(q, -2)
            if all(x in k.index for x in (q, q1, q2)):
                base = w * k.loc[q1, "gbv_musd"] + (1 - w) * k.loc[q2, "gbv_musd"]
                if base > 0 and np.isfinite(k.loc[q, "revenue_musd"]):
                    vals.append(100.0 * k.loc[q, "revenue_musd"] / base)
        out[s] = dict(mean=float(np.mean(vals)), n=len(vals),
                      sd=float(np.std(vals, ddof=1)) if len(vals) > 1 else np.nan,
                      values=[round(v, 3) for v in vals])
    return out


def kernel_revenue(gbv: dict, quarter: str, lam: dict, w: float) -> float:
    q1, q2 = D.qadd(quarter, -1), D.qadd(quarter, -2)
    if q1 not in gbv or q2 not in gbv:
        return np.nan
    s = int(quarter[5])
    return lam[s]["mean"] / 100.0 * (w * gbv[q1] + (1 - w) * gbv[q2])


def project_regional(panel: pd.DataFrame, quarters_out: list[str],
                     nights_yoy: dict | None, adr_yoy: dict | None,
                     trailing_n: int = 4) -> pd.DataFrame:
    """Roll regional nights and regional ADR forward on y/y growth.

    `nights_yoy` / `adr_yoy` are {region: pct} overrides (the driver-model scenario).
    When None, the region's own trailing-`trailing_n` mean y/y from the reconstruction
    is used -- the data-only continuation.
    """
    piv_n = panel.pivot_table(index="quarter", columns="region", values="nights_m")
    piv_a = panel.pivot_table(index="quarter", columns="region", values="adr_reported_usd")
    piv_n = piv_n.reindex(sorted(piv_n.index, key=D.qorder))
    piv_a = piv_a.reindex(sorted(piv_a.index, key=D.qorder))
    n = {(q, r): float(piv_n.loc[q, r]) for q in piv_n.index for r in piv_n.columns}
    a = {(q, r): float(piv_a.loc[q, r]) for q in piv_a.index for r in piv_a.columns}

    def trail(tbl, r, last):
        g = []
        qs = sorted({q for (q, rr) in tbl if rr == r}, key=D.qorder)
        for q in qs[-trailing_n:]:
            q4 = D.qadd(q, -4)
            if (q4, r) in tbl and tbl[(q4, r)] > 0:
                g.append(100.0 * (tbl[(q, r)] / tbl[(q4, r)] - 1.0))
        return float(np.mean(g)) if g else 0.0

    rows = []
    for q in quarters_out:
        for r in D.REGIONS:
            q4 = D.qadd(q, -4)
            gn = nights_yoy[r] if nights_yoy else trail(n, r, q)
            ga = adr_yoy[r] if adr_yoy else trail(a, r, q)
            n[(q, r)] = n[(q4, r)] * (1 + gn / 100.0)
            a[(q, r)] = a[(q4, r)] * (1 + ga / 100.0)
            rows.append(dict(quarter=q, region=r, nights_m=n[(q, r)],
                             adr_reported_usd=a[(q, r)],
                             gbv_musd=n[(q, r)] * a[(q, r)],
                             nights_yoy_pct=gn, adr_yoy_pct=ga))
    return pd.DataFrame(rows)


def annual_adr_decomposition(panel: pd.DataFrame, fxpp: pd.DataFrame) -> pd.DataFrame:
    """Blended reported ADR y/y split into within-region (reported and ex-FX) and
    geographic mix.  Geographic mix is an OUTPUT of the share-weighted identity:
    blended ADR == sum_r share_r * ADR_r, exactly, so there is no index-bias plug."""
    p = panel.copy()
    p["year"] = p["quarter"].str[:4].astype(int)
    ann = p.groupby(["year", "region"]).agg(nights_m=("nights_m", "sum"),
                                            gbv_musd=("gbv_musd", "sum")).reset_index()
    ann["adr"] = ann["gbv_musd"] / ann["nights_m"]
    fx = fxpp.copy()
    fx["year"] = fx["quarter"].str[:4].astype(int)
    fxa = fx.groupby(["year", "region"])["fx_pp"].mean().reset_index()
    ann = ann.merge(fxa, on=["year", "region"], how="left")
    out = []
    for yr in sorted(ann.year.unique()):
        if yr - 1 not in set(ann.year):
            continue
        cur = ann[ann.year == yr].set_index("region")
        prv = ann[ann.year == yr - 1].set_index("region")
        wprv = prv["nights_m"] / prv["nights_m"].sum()
        wcur = cur["nights_m"] / cur["nights_m"].sum()
        blend_prv = float((wprv * prv["adr"]).sum())
        blend_cur = float((wcur * cur["adr"]).sum())
        within_rep = float((wprv * (cur["adr"] - prv["adr"])).sum()) / blend_prv * 100
        mix = float(((wcur - wprv) * prv["adr"]).sum()) / blend_prv * 100
        cross = (blend_cur - blend_prv) / blend_prv * 100 - within_rep - mix
        fxterm = float((wprv * prv["adr"] * cur["fx_pp"].fillna(0) / 100).sum()) / blend_prv * 100
        out.append(dict(year=yr, blended_adr_yoy_pct=(blend_cur / blend_prv - 1) * 100,
                        within_region_reported_pp=within_rep,
                        within_region_exfx_pp=within_rep - fxterm,
                        fx_pp=fxterm, geographic_mix_pp=mix, cross_term_pp=cross,
                        n_regions=len(cur)))
    return pd.DataFrame(out)
