"""l1-reconciliation-v2: projection, the kernel hand-off, and the FY27 decomposition.

COPY of `l1_reconciliation/project.py` (task B3), MODIFIED.  The v1 functions are
left byte-identical; everything below the marker `# ===== v2 additions` is new.

WHAT CHANGED AND WHY (RED_TEAM F1).  v1 published 14 ADDITIVE pp lines.  Two of
them -- geographic mix -1.09pp and unit-size/LOS +0.38pp -- are already inside the
volume and price lines, the volume x price cross term was omitted, and the closing
"kernel timing +0.1674pp identity" was a plug.  v2 rebuilds the object
MULTIPLICATIVELY on the L1 spine's own identities:

    GBV_q            == N_q * ADR_blend_q                     (exact, by construction)
    1 + g_GBV        == (1 + g_N) * (1 + g_ADR)               (exact)
    1 + g_revenue    == (1 + g_GBV) * (1 + kappa_w)           (exact, kappa COMPUTED)

with kappa_w the kernel recognition/timing effect implied by
Revenue_q = lambda_s * [w*GBV_{q-1} + (1-w)*GBV_{q-2}].  Everything that is not
one of those three factors is ATTRIBUTION (zero weight) or ASSUMED (outside the
computed dollar).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import data as D

# ---- v1 module docstring, retained verbatim for provenance:
_V1_DOC = """

ONE object crosses the boundary: gbv_musd, booking-dated, one number per quarter.
Revenue is then the kernel convolution of ALREADY-PRINTED GBV, per the architect:
    Revenue_q = lambda_season(q) * [ w * GBV_{q-1} + (1-w) * GBV_{q-2} ]
with w = 2/3 published and 0.33..0.667 propagated as the mandatory sensitivity.
No FX pp is ever added to revenue: booking-date FX is inside the lagged GBV base.
"""


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


# ===== v2 additions =========================================================
# Nothing above this marker was changed.  Everything below rebuilds the FY27
# object multiplicatively and separates COMPUTED from ASSUMED.

# --- ATTRIBUTION inputs.  ZERO weight in the total.  Each carries its source.
# These are measurements of the REPORTED-ADR channel taken elsewhere in the repo.
# They are NOT forecast inputs and they may not be added to any growth total.
ADR_ATTRIBUTION_SOURCES = {
    "unit_size_mix_pp": dict(
        pp=0.63,
        source="research/notes/2026-09-07_adr-decomposition.md §0.3 (direct measurement, "
               "29 markets, bedroom-count elasticity 0.23); restated in "
               "docs/.../01_ground-truth/01_data_inventory.md line 160",
        basis="measured", note="the Street's +2pp bedroom-nights -> +2pp ADR mapping is NOT used"),
    "los_mix_pp": dict(
        pp=0.04,
        source="research/notes/2026-09-07_adr-decomposition.md §0 via 01_data_inventory.md "
               "line 160 (LOS mix +0.04pp, 2025 decomposition)",
        basis="measured", note="the ADR workbook's rival +0.30pp LOS term is a different "
                               "construction (02_model_audit.md line 142) and is not mixed in"),
    "seats_hotel_dilution_pp": dict(
        pp=-0.50,
        source="00_IMPLEMENTATION_DECISIONS.md §8.1 / 00_INTEGRATED_SYSTEM.md §3(d), from "
               "research/notes/2026-09-09_seats-dilution.md (structure measured, ticket "
               "prices assumed)",
        basis="assumed_structure_measured",
        note="OUTPUT of N = n_home + n_hotel + s_exp + s_svc.  It moves reported ADR and the "
             "unit count in OPPOSITE directions, so it nets to ZERO in GBV and in revenue.  "
             "The v2 FY27 build itself carries 0.00 here because the non-home composition is "
             "held flat through 2027; -0.50pp is the plan's y/y assumption, shown for "
             "attribution only.  The l1 build's measured 2026 LEVEL of dilution is -3.52pp."),
    "booking_fx_phi_pp": dict(
        pp=0.00,
        source="l1-reconciliation §6 (FY27 FX is a FLAT-SPOT CARRY: FX inputs end 2026Q3) "
               "-- rival reading fx-lag +0.2pp (OPTIMAL_MIX.md §4.4)",
        basis="assumed_flat_spot_carry",
        note="already inside the lagged USD GBV base; NEVER added to revenue a second time"),
}

# --- ASSUMED revenue lines.  OUTSIDE the computed dollar.  pp of FY27 growth.
ASSUMED_FY27_V2 = {
    "fee_take_rate_mechanism_pp": dict(
        pp=0.90, lo=0.36, hi=0.59, central=0.59,
        source="00_IMPLEMENTATION_DECISIONS.md §8.1 (+0.9pp at half weight, theta implicitly 1); "
               "restated from primitives in fee-takerate.md 'FY27 contribution and the +0.9pp "
               "line' (n=3): half weight +0.36pp (11.5pp-jump case) to +0.59pp (central "
               "theta=0.833), i.e. 0.31pp BELOW the +0.90pp line",
        note="fee-takerate also finds that at central theta the migration subtracts -0.62pp "
             "from FY27 GBV growth.  The computed GBV build below does NOT carry that -0.62pp, "
             "so adding the fee line on top of it is itself a disguised double count unless the "
             "GBV side is restated.  Stated, not silently netted."),
    "new_lines_pp": dict(
        pp=0.20, lo=0.20, hi=0.20, central=0.20,
        source="00_IMPLEMENTATION_DECISIONS.md §8.1 (ads $0 FY26, Services excess; nb_incr "
               "netting as built at 13_driver_model.py:437)",
        note="outside GBV by construction"),
    "regulation_pp": dict(
        pp=-0.30, lo=-0.30, hi=-0.30, central=-0.30,
        source="00_IMPLEMENTATION_DECISIONS.md §8.1 (dated DiD on EMEA nights; replaces "
               "REG_DRAG_PP x 1.67, which is deleted)",
        note="model-based, not rebuilt in v2"),
    "hedge_pp": dict(
        pp=0.00, lo=0.00, hi=0.00, central=0.00,
        source="00_IMPLEMENTATION_DECISIONS.md §5.2.3 (hedge Lambda_q is in DOLLARS and is "
               "added ONCE, by kernel-lambda)",
        note="zero in pp by construction here; do not add it twice"),
}


def annual_regional(panel: pd.DataFrame, years=(2026, 2027)) -> pd.DataFrame:
    """Annual regional nights / GBV / ADR from a quarterly regional panel."""
    p = panel.copy()
    p["year"] = p["quarter"].str[:4].astype(int)
    a = (p[p.year.isin(years)]
         .groupby(["year", "region"])
         .agg(nights_m=("nights_m", "sum"), gbv_musd=("gbv_musd", "sum"))
         .reset_index())
    a["adr_usd"] = a["gbv_musd"] / a["nights_m"]
    return a


def gbv_factorisation(ann: pd.DataFrame, y0: int = 2026, y1: int = 2027) -> dict:
    """The two EXACT factorisations of GBV growth, and the bridge between them.

    Basis B (published): GBV == N x ADR_blend, so
        (1 + g_N) * (1 + g_ADR) == 1 + g_GBV      exactly.
      g_N    total Nights-and-Seats growth
      g_ADR  blended REPORTED ADR growth (geographic mix is an OUTPUT inside it)

    Basis A (the red team's index basis):
        (1 + Q) * (1 + P) == 1 + g_GBV            exactly, where
      Q  fixed-PRICE (Laspeyres quantity) index growth -- this ALREADY CONTAINS
         geographic mix, which is precisely why v1 double counted: v1 took the
         volume line from basis A and then added the mix line from basis B.
      P  fixed-QUANTITY (Laspeyres price) index growth = within-region price.
    """
    cur = ann[ann.year == y1].set_index("region")
    prv = ann[ann.year == y0].set_index("region")
    G0, G1 = float(prv.gbv_musd.sum()), float(cur.gbv_musd.sum())
    N0, N1 = float(prv.nights_m.sum()), float(cur.nights_m.sum())
    A0, A1 = G0 / N0, G1 / N1
    g_gbv, g_n, g_adr = G1 / G0 - 1, N1 / N0 - 1, A1 / A0 - 1
    Q = float((cur.nights_m * prv.adr_usd).sum()) / G0 - 1
    P = float((prv.nights_m * cur.adr_usd).sum()) / G0 - 1
    w0 = prv.nights_m / N0
    w1 = cur.nights_m / N1
    mix = float(((w1 - w0) * prv.adr_usd).sum()) / A0
    within = float((w0 * (cur.adr_usd - prv.adr_usd)).sum()) / A0
    return dict(
        gbv_y0=G0, gbv_y1=G1, nights_y0=N0, nights_y1=N1, adr_y0=A0, adr_y1=A1,
        g_gbv=g_gbv, g_nights=g_n, g_adr=g_adr, cross_nights_adr=g_n * g_adr,
        lasp_quantity_Q=Q, lasp_price_P=P, cross_QP=Q * P,
        adr_geo_mix=mix, adr_within_region=within,
        adr_cross=g_adr - mix - within,
        regional=pd.DataFrame(dict(
            nights_yoy_pct=100 * (cur.nights_m / prv.nights_m - 1),
            adr_yoy_pct=100 * (cur.adr_usd / prv.adr_usd - 1),
            gbv_share_y0_pct=100 * prv.gbv_musd / G0,
            nights_share_y0_pct=100 * w0, nights_share_y1_pct=100 * w1)),
    )


def kernel_year(gbv: dict, lam: dict, w: float, quarters: list[str],
                actuals: dict | None = None) -> dict:
    """Kernel revenue for a set of quarters.  `actuals` overrides a quarter with a
    printed number (FY26 1H is PRINTED, not modelled) -- stated, never hidden."""
    parts = {}
    for q in quarters:
        q1, q2 = D.qadd(q, -1), D.qadd(q, -2)
        base = w * gbv[q1] + (1 - w) * gbv[q2]
        modelled = lam[int(q[5])]["mean"] / 100.0 * base
        used = float(actuals[q]) if (actuals and q in actuals) else modelled
        parts[q] = dict(kernel_base_musd=base, lambda_pct=lam[int(q[5])]["mean"],
                        modelled_musd=modelled, used_musd=used,
                        source="printed" if (actuals and q in actuals) else "kernel")
    return parts


def kernel_kappa(gbv: dict, lam: dict, w: float, actuals: dict,
                 y0_quarters: list[str], y1_quarters: list[str]) -> dict:
    """kappa_w -- the kernel RECOGNITION/TIMING effect, COMPUTED, never a residual.

    Revenue is a convolution of ALREADY-BOOKED GBV, so a calendar year's revenue
    is a lambda-weighted sum of LAGGED GBV, not of that year's GBV.  kappa_w is
    exactly the gap between those two growth rates:

        1 + g_revenue == (1 + g_GBV) * (1 + kappa_w)
        kappa_w       == (1 + g_revenue) / (1 + g_GBV) - 1

    Both sides are built from lambda and the GBV path; nothing is solved for.
    """
    p0 = kernel_year(gbv, lam, w, y0_quarters, actuals)
    p1 = kernel_year(gbv, lam, w, y1_quarters, actuals)
    r0 = sum(v["used_musd"] for v in p0.values())
    r1 = sum(v["used_musd"] for v in p1.values())
    G0 = sum(gbv[q] for q in y0_quarters)
    G1 = sum(gbv[q] for q in y1_quarters)
    g_rev, g_gbv = r1 / r0 - 1, G1 / G0 - 1
    kap = (1 + g_rev) / (1 + g_gbv) - 1
    # the two named channels inside kappa, both computed:
    #  (i) LAG: the lambda-weighted lagged-GBV base grows at a different rate than
    #      the calendar-year GBV itself;
    #  (ii) PRINT: FY26 1H is the PRINTED number, not the kernel's own.
    r0_all_kernel = sum(v["modelled_musd"] for v in p0.values())
    kap_lag = (1 + r1 / r0_all_kernel - 1) / (1 + g_gbv) - 1
    return dict(w=w, fy_y0_revenue_musd=r0, fy_y1_revenue_musd=r1,
                fy_y0_revenue_all_kernel_musd=r0_all_kernel,
                g_revenue=g_rev, g_gbv=g_gbv, kappa=kap,
                kappa_lag_channel=kap_lag, kappa_print_channel=kap - kap_lag,
                parts_y0=p0, parts_y1=p1)
