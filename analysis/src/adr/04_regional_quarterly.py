"""04. Quarterly regional ADR panel, 1Q21-2Q26: NA / EMEA / LatAm / APAC.

Produces regional ADR levels, reported y/y, ex-FX y/y and nights shares, with a
basis flag on every cell (disclosed / derived / modelled). Nothing is smoothed
into a number the disclosure does not support: where a cell is modelled it says
so, and the reconciliation file quantifies what that costs.

WHAT IS ACTUALLY DISCLOSED
--------------------------
Steps 01-03 took regional ADR y/y from the KPI panel. That panel is incomplete.
This step re-reads the 23 shareholder letters in data/raw/letters/ and rebuilds
the disclosure map from the Geographic Mix section of each. Three corrections:

  * EMEA reported ADR y/y is disclosed from 1Q23, not 2Q23 ("In EMEA, Nights and
    Experiences Booked grew 21% ... while ADR grew 8% year-over-year", 1Q23).
  * LatAm and APAC are disclosed from 4Q24, not 1Q25 (4Q24 letter: LatAm ADR
    "declined 5% ... On an FX-neutral basis, ADR increased 4%"; APAC "increased
    1% ... On an FX-neutral basis, ADR increased 2%"). The KPI panel has neither.
  * 3Q23 and 4Q23 EMEA disclose ONLY the ex-FX figure (+6%). Reported EMEA ADR
    for those two quarters is DERIVED as ex-FX + basket x pass-through, not
    disclosed, and is flagged that way.

One further distinction the KPI panel loses: from 4Q23 to 3Q24 the NA and EMEA
constant-currency figures are stated as "excluding the impact of FX AND MIX
SHIFT". That is not an ex-FX number and is not used as one. It is carried in its
own metric, adr_yoy_exfx_exmix_pct, flagged "disclosed (ex-FX and mix shift)".

METHOD
------
1. Regional quarterly nights, via RAS (biproportional fitting), per calendar year
   - row targets     = 10-K annual regional nights (01_regional_annual.csv)
   - column targets  = disclosed global quarterly nights (letters, via KPI panel)
   - seed            = prior-year same quarter grown by the DISCLOSED regional
                       nights y/y where a letter gives one, else by the annual
                       regional growth rate
   This uses no ADR anywhere, so the shares it produces are a legitimate weight
   for reconciling regional ADR back to global ADR. WS10's estimated quarterly
   nights shares are NOT used as an input: they were themselves built off a fixed
   regional ADR index (NA 1.42 / EMEA 0.97 / LatAm 0.68 / APAC 0.59), so feeding
   them into an ADR panel and then checking the panel against global ADR would be
   circular. They are compared against at the end, and the comparison is reported.
   2026 has no 10-K row target, so 1Q26/2Q26 are seed-and-column-scale only and
   are flagged derived rather than modelled-to-anchor.

2. Seasonal shape
   ABNB nights and ADR are both dated at BOOKING, so Q1 is the high-ADR quarter
   (summer entire-home stays are booked in Q1) and Q4 the low one. A smooth
   interpolation of the annual anchors would erase a swing of roughly +/-4%.
   The global quarterly ADR pattern is NOT the within-region seasonal, because
   part of it is quarterly regional mix: NA ADR is about 1.5x global, so a Q3
   shift toward EMEA depresses global ADR with no within-region seasonality at
   all. So the mix is divided out first:

       S_q = ADR_q / sum_r ( w_rq * A_r,year )

   with w from step 1 and A the 10-K annual regional ADR. S_q is the common
   within-region seasonal index.

   REGION-SPECIFIC seasonal factors are NOT IDENTIFIED. Every regional ADR
   disclosure is a y/y growth rate, and y/y is seasonality-free by construction,
   so no disclosed number carries information about the level shape within a year
   for a single region. A common S_q is used, and the assumption is tested rather
   than assumed away: the reconciliation residual is decomposed by fiscal quarter
   at the end. If regional seasonals genuinely differed, the residual over the
   disclosure era would carry a systematic quarterly signature.

3. Regional ADR levels
   modelled quarters   ADR_rq = A_r,year * S_q
   disclosed quarters  ADR_rq = ADR_r,q-4 * (1 + g_rq)   chained forward in time
   The chain is NOT re-based to the 10-K annual anchor afterwards. Forcing it
   would destroy the disclosed y/y; leaving it lets the drift be measured. The
   drift against the annual anchor is reported per region-year in the "annual"
   block of 04_reconciliation.csv.

4. ex-FX
   disclosed where the letter gives one, otherwise
       adr_yoy_exfx = adr_yoy_reported - basket_r_yoy * passthrough_r
   Pass-through from WS10: EMEA 1.04, LatAm 0.62, APAC 0.86, NA NOT IDENTIFIED
   (1.00 assumed; the NA basket is under 1% in absolute terms in every quarter of
   the panel, so the assumption moves nothing). Those pass-throughs are
   independently re-tested here against the quarters where a letter gives BOTH
   reported and ex-FX regional ADR -- see the "passthrough" block of
   04_reconciliation.csv.

5. Two level series are published
   adr_usd           the primary: honours every disclosed y/y exactly, drifts
                     against the 10-K annual anchor by up to 2.2% (LatAm 2025)
   adr_usd_anchored  the same series rescaled per region-year to hit the 10-K
                     annual anchor; use it when a level must tie to the filing,
                     accepting that the disclosed y/y is then off by tenths

REJECTED VARIANTS (recorded, not used)
--------------------------------------
* Reseeding NA's 2021-2022 within-year share with the disclosed quarterly US
  revenue share (57.6% in 1Q21 to 39.1% in 4Q21). It doubles the reconciliation
  residual, 0.31% to 0.61%, and implies a 4Q22 NA nights share of 24% against
  33.8% for full-year 2022 in the FY2022 10-K. US revenue is stay-dated and US is
  not NA; the series is moving on the international reopening, not on NA's share
  of booked nights. See sensitivity().
* Solving the modelled regions' ADR as the residual that closes global ADR every
  quarter. It would make the reconciliation exact and therefore worthless as a
  check, and the check is the deliverable.

CAVEATS
-------
* Annual regional nights are rounded to whole millions from FY2022, so the
  computed annual regional ADR carries up to ~0.8% error for APAC. Where the 10-K
  states regional ADR directly (2020-2022) the stated figure is used.
* Every disclosed regional ADR y/y is rounded to a whole percent. Chaining up to
  14 of them compounds rounding into the 2026 levels; treat the 2026 regional
  levels as accurate to roughly +/-1%, and the y/y as exact.
* Several regional nights y/y are verbal buckets ("mid-single digits", "low-20s")
  already reduced to midpoints upstream; the share basis field says so.
* Reconciliation is uninformative before 1Q23. Before the first regional ADR
  disclosure the levels are A_r,y * S_q by construction, so the share-weighted
  regional ADR equals global ADR to machine precision. Those rows are marked
  informative=0 and must not be read as validation.

Outputs
  data/processed/adr/04_regional_quarterly.csv       long: quarter, region, metric, value, basis
  data/processed/adr/04_regional_quarterly_wide.csv  convenience wide view
  data/processed/adr/04_reconciliation.csv           quarterly + annual + passthrough checks
"""

import os

import numpy as np
import pandas as pd

OUT = "data/processed/adr"
OVN = "data/processed/overnight"
REGIONS = ["na", "emea", "latam", "apac"]

# WS10 regional FX pass-through into reported ADR. NA is not identified.
PASSTHROUGH = {"emea": 1.04, "latam": 0.62, "apac": 0.86, "na": 1.00}
PASSTHROUGH_BASIS = {
    "emea": "WS10 fitted 1.04",
    "latam": "WS10 fitted 0.62",
    "apac": "WS10 fitted 0.86",
    "na": "NOT IDENTIFIED; 1.00 assumed (NA basket <1% every quarter)",
}

# ---------------------------------------------------------------------------
# Disclosure map, read off the Geographic Mix section of each shareholder letter
# in data/raw/letters/. Values are whole percent as printed in the letter.
# ---------------------------------------------------------------------------
# reported (as-reported USD) regional ADR y/y, %
ADR_YOY_DISCLOSED = {
    ("1Q23", "emea"): 8.0,
    ("2Q23", "na"): -1.0, ("2Q23", "emea"): 8.0,
    ("3Q23", "na"): -1.0,
    ("4Q23", "na"): 0.0,
    ("1Q24", "na"): 3.0, ("1Q24", "emea"): 7.0,
    ("2Q24", "na"): 4.0, ("2Q24", "emea"): 4.0,
    ("3Q24", "na"): 3.0, ("3Q24", "emea"): 6.0,
    ("4Q24", "na"): 3.0, ("4Q24", "emea"): 6.0, ("4Q24", "latam"): -5.0, ("4Q24", "apac"): 1.0,
    ("1Q25", "na"): 2.0, ("1Q25", "emea"): 2.0, ("1Q25", "latam"): -7.0, ("1Q25", "apac"): -1.0,
    ("2Q25", "na"): 3.0, ("2Q25", "emea"): 9.0, ("2Q25", "latam"): -3.0, ("2Q25", "apac"): 2.0,
    ("3Q25", "na"): 5.0, ("3Q25", "emea"): 10.0, ("3Q25", "latam"): 4.0, ("3Q25", "apac"): 2.0,
    ("4Q25", "na"): 5.0, ("4Q25", "emea"): 12.0, ("4Q25", "latam"): 9.0, ("4Q25", "apac"): 2.0,
    ("1Q26", "na"): 7.0, ("1Q26", "emea"): 15.0, ("1Q26", "latam"): 10.0, ("1Q26", "apac"): 6.0,
    ("2Q26", "na"): 7.0, ("2Q26", "emea"): 7.0, ("2Q26", "latam"): 9.0, ("2Q26", "apac"): 1.0,
}
# true ex-FX (constant currency, no mix adjustment) regional ADR y/y, %
ADR_EXFX_DISCLOSED = {
    ("3Q23", "emea"): 6.0,
    ("4Q23", "emea"): 6.0,
    ("4Q24", "emea"): 6.0, ("4Q24", "latam"): 4.0, ("4Q24", "apac"): 2.0,
    ("1Q25", "na"): 3.0, ("1Q25", "emea"): 4.0, ("1Q25", "latam"): 2.0, ("1Q25", "apac"): 3.0,
    ("2Q25", "emea"): 3.0, ("2Q25", "latam"): 2.0, ("2Q25", "apac"): 1.0,
    ("3Q25", "emea"): 4.0, ("3Q25", "latam"): 3.0, ("3Q25", "apac"): 3.0,
    ("4Q25", "emea"): 4.0, ("4Q25", "latam"): 3.0, ("4Q25", "apac"): 2.0,
    ("1Q26", "emea"): 4.0, ("1Q26", "latam"): 3.0, ("1Q26", "apac"): 2.0,
    ("2Q26", "emea"): 5.0, ("2Q26", "latam"): 2.0,
}
# "excluding the impact of FX AND MIX SHIFT" -- a different basis, kept separate
ADR_EXFX_EXMIX_DISCLOSED = {
    ("4Q23", "na"): -2.0,
    ("1Q24", "na"): 0.0, ("1Q24", "emea"): 4.0,
    ("2Q24", "na"): 1.0, ("2Q24", "emea"): 3.0,
    ("3Q24", "na"): 1.0, ("3Q24", "emea"): 3.0,
}
# qualitative regional ADR sign statements, used as a direction check only
ADR_SIGN_STATEMENTS = {
    ("2Q22", "all"): "ex-FX up across all major regions",
    ("3Q22", "all"): "ex-FX up across all major regions",
    ("4Q22", "all"): "ex-FX up across all regions",
    ("1Q23", "all"): "ex-FX flat to up across all regions",
    ("2Q23", "na"): "ex-FX down", ("2Q23", "latam"): "ex-FX down",
    ("2Q23", "emea"): "ex-FX up", ("2Q23", "apac"): "ex-FX up",
    ("3Q23", "na"): "ex-FX down", ("3Q23", "latam"): "ex-FX down",
    ("3Q23", "emea"): "ex-FX up", ("3Q23", "apac"): "ex-FX up",
    ("4Q23", "na"): "ex-FX flat", ("4Q23", "latam"): "ex-FX flat",
    ("4Q23", "emea"): "ex-FX up", ("4Q23", "apac"): "ex-FX up",
    ("1Q24", "all"): "ex-FX up across all regions",
    ("2Q24", "all"): "ex-FX up across all regions",
    ("3Q24", "all"): "ex-FX flat to up across all regions",
    ("4Q24", "all"): "ex-FX up across all regions",
    ("1Q25", "all"): "ex-FX up across all regions",
    ("2Q25", "all"): "ex-FX up across all regions",
    ("3Q25", "all"): "ex-FX up across all regions",
    ("4Q25", "all"): "ex-FX up across all regions",
    ("1Q26", "all"): "ex-FX up across all regions",
    ("2Q26", "all"): "ex-FX up across all regions",
}


def qkey(q):
    """1Q23 -> (2023, 1). Sorts quarters chronologically."""
    return (2000 + int(q[2:]), int(q[0]))


def qyear(q):
    return 2000 + int(q[2:])


def lag4(q):
    """Same quarter of the prior year."""
    return f"{q[0]}Q{int(q[2:]) - 1:02d}"


# ---------------------------------------------------------------------------
# inputs
# ---------------------------------------------------------------------------

def load_inputs():
    ann = pd.read_csv(f"{OUT}/01_regional_annual.csv")
    ann = ann[ann.region != "total"].copy()
    # 10-K stated regional ADR where the filing gives it; whole-million nights
    # rounding from FY2022 makes the computed figure drift up to ~0.8%.
    ann["adr"] = ann.adr_stated.fillna(ann.adr_computed)
    ann["adr_basis"] = np.where(
        ann.adr_stated.notna(), "10-K stated", "10-K computed GBV/nights")

    kpi = pd.read_csv(f"{OVN}/02_kpi_panel_quarterly.csv")
    kpi = kpi[["quarter", "nights_m", "gbv_busd", "adr_usd",
               "nights_yoy_na_pct", "nights_yoy_emea_pct",
               "nights_yoy_latam_pct", "nights_yoy_apac_pct"]].copy()
    kpi = kpi[kpi.quarter.map(qkey) >= (2021, 1)].sort_values(
        "quarter", key=lambda s: s.map(qkey)).reset_index(drop=True)

    fx = pd.read_csv(f"{OUT}/02_fx_basket_quarterly.csv")
    fx = fx.pivot(index="quarter", columns="region", values="basket_yoy_pct")

    ws10 = pd.read_csv(f"{OVN}/10_regional_panel_quarterly.csv")
    return ann, kpi, fx, ws10


# ---------------------------------------------------------------------------
# 1. regional quarterly nights via RAS
# ---------------------------------------------------------------------------

def ras(seed, row_targets, col_targets, tol=1e-10, maxit=500):
    """Biproportional fit of `seed` to given row and column margins."""
    m = seed.astype(float).copy()
    for _ in range(maxit):
        r = row_targets / m.sum(axis=1)
        m = m * r[:, None]
        c = col_targets / m.sum(axis=0)
        m = m * c[None, :]
        if np.max(np.abs(m.sum(axis=1) - row_targets)) < tol:
            break
    return m


def regional_nights(ann, kpi, na_shape=None):
    """Quarterly regional nights, fitted to 10-K annual rows and letter columns.

    Returns a (quarter x region) frame of nights in millions plus a basis frame.
    No ADR is used anywhere in this function -- that is the point of it.

    na_shape: optional {quarter: relative factor} applied to the NA seed row in
    2021-2022 before fitting. Used only by the sensitivity run, which reshapes NA
    with the disclosed quarterly US revenue share; see sensitivity().
    """
    nights_yoy = {r: dict(zip(kpi.quarter, kpi[f"nights_yoy_{r}_pct"])) for r in REGIONS}
    ann_n = ann.pivot(index="year", columns="region", values="nights_m")
    ann_share = ann.pivot(index="year", columns="region", values="nights_share_pct") / 100.0

    fitted, basis = {}, {}
    for year in range(2021, 2027):
        qs = [q for q in kpi.quarter if qyear(q) == year]
        if not qs:
            continue
        col = kpi.set_index("quarter").loc[qs, "nights_m"].to_numpy(float)

        if year == 2021:
            # No prior quarterly regional level to grow. A flat within-year share
            # is the least-informative seed; RAS then leaves shares flat, which
            # is the honest answer given no 2021 regional quarterly disclosure.
            seed = np.outer(ann_share.loc[year, REGIONS].to_numpy(float), col)
            seed_basis = "modelled (flat 10-K annual share within year)"
        else:
            prev = np.array([[fitted[lag4(q)][r] for q in qs] for r in REGIONS], dtype=float)
            g = np.ones_like(prev)
            src = np.empty(prev.shape, dtype=object)
            for i, r in enumerate(REGIONS):
                ann_g = (ann_n.loc[year, r] / ann_n.loc[year - 1, r] - 1.0) if year <= 2025 else np.nan
                for j, q in enumerate(qs):
                    v = nights_yoy[r].get(q, np.nan)
                    if pd.notna(v):
                        g[i, j] = 1.0 + v / 100.0
                        src[i, j] = "letter"
                    else:
                        g[i, j] = 1.0 + (ann_g if pd.notna(ann_g) else 0.0)
                        src[i, j] = "annual"
            seed = prev * g
            seed_basis = None

        if na_shape is not None and year in (2021, 2022):
            f = np.array([na_shape.get(q, 1.0) for q in qs], dtype=float)
            seed = seed.copy()
            seed[REGIONS.index("na")] *= f / f.mean()

        if year <= 2025:
            row = ann_n.loc[year, REGIONS].to_numpy(float)
            row = row * (col.sum() / row.sum())   # letters vs 10-K rounding, <0.5%
            m = ras(seed, row, col)
        else:
            # No annual anchor for 2026: scale each quarter's column to the
            # disclosed global nights and leave the seed's cross-section alone.
            m = seed * (col / seed.sum(axis=0))[None, :]

        for j, q in enumerate(qs):
            fitted[q] = {r: m[i, j] for i, r in enumerate(REGIONS)}
            if year == 2021:
                basis[q] = {r: seed_basis for r in REGIONS}
            else:
                for i, r in enumerate(REGIONS):
                    tag = ("disclosed nights y/y" if src[i, j] == "letter"
                           else "10-K annual growth")
                    anchor = ("RAS to 10-K annual + letter quarterly nights" if year <= 2025
                              else "scaled to letter quarterly nights (no 2026 annual anchor)")
                    basis.setdefault(q, {})[r] = f"derived ({tag}; {anchor})"

    n = pd.DataFrame(fitted).T[REGIONS]
    b = pd.DataFrame(basis).T[REGIONS]
    n = n.loc[sorted(n.index, key=qkey)]
    b = b.loc[n.index]
    return n, b


# ---------------------------------------------------------------------------
# 2-3. seasonal index and regional ADR levels
# ---------------------------------------------------------------------------

def seasonal_index(nights, kpi, ann):
    """Common within-region ADR seasonal S_q, with quarterly regional mix removed.

    S_q = ADR_q / sum_r ( w_rq * A_r,year ).  Only defined for 2021-2025, where
    there is a 10-K annual regional ADR to sit under the mix.
    """
    adr_ann = ann.pivot(index="year", columns="region", values="adr")
    adr_q = kpi.set_index("quarter").adr_usd
    w = nights.div(nights.sum(axis=1), axis=0)
    rows = []
    for q in nights.index:
        y = qyear(q)
        if y not in adr_ann.index:
            rows.append((q, np.nan, np.nan, np.nan))
            continue
        mix = float((w.loc[q, REGIONS] * adr_ann.loc[y, REGIONS]).sum())
        rows.append((q, adr_q[q] / mix, mix, adr_q[q]))
    s = pd.DataFrame(rows, columns=["quarter", "S", "mix_adr", "adr_global"]).set_index("quarter")
    return s


def regional_adr(nights, kpi, ann, seas):
    """Regional ADR levels: modelled off the anchors, then chained on disclosure."""
    adr_ann = ann.pivot(index="year", columns="region", values="adr")
    lvl = pd.DataFrame(index=nights.index, columns=REGIONS, dtype=float)
    bas = pd.DataFrame(index=nights.index, columns=REGIONS, dtype=object)

    for r in REGIONS:
        for q in nights.index:
            y = qyear(q)
            key = (q, r)
            if key in ADR_YOY_DISCLOSED:
                base = lvl.at[lag4(q), r] if lag4(q) in lvl.index else np.nan
                lvl.at[q, r] = base * (1.0 + ADR_YOY_DISCLOSED[key] / 100.0)
                bas.at[q, r] = "derived (disclosed y/y chained onto modelled base)"
            elif key in ADR_EXFX_DISCLOSED:
                # ex-FX only (EMEA 3Q23/4Q23): rebuild the reported y/y
                g = ADR_EXFX_DISCLOSED[key] + FX_PP.at[q, r]
                lvl.at[q, r] = lvl.at[lag4(q), r] * (1.0 + g / 100.0)
                bas.at[q, r] = "derived (disclosed ex-FX y/y + basket x pass-through, chained)"
            elif y in adr_ann.index and pd.notna(seas.at[q, "S"]):
                lvl.at[q, r] = adr_ann.at[y, r] * seas.at[q, "S"]
                bas.at[q, r] = "modelled (10-K annual anchor x mix-adjusted global seasonal)"
            else:
                lvl.at[q, r] = np.nan
                bas.at[q, r] = "not available"
    return lvl, bas


# ---------------------------------------------------------------------------

def build(na_shape=None, write=True):
    global FX_PP
    ann, kpi, fx, ws10 = load_inputs()
    nights, nights_basis = regional_nights(ann, kpi, na_shape=na_shape)
    quarters = list(nights.index)

    # FX contribution to reported regional ADR y/y, pp
    FX_PP = pd.DataFrame(
        {r: fx.loc[quarters, r] * PASSTHROUGH[r] for r in REGIONS}, index=quarters)

    seas = seasonal_index(nights, kpi, ann)
    lvl, lvl_basis = regional_adr(nights, kpi, ann, seas)

    share = nights.div(nights.sum(axis=1), axis=0) * 100.0

    # y/y from the levels; disclosed where disclosed
    yoy = pd.DataFrame(index=quarters, columns=REGIONS, dtype=float)
    yoy_basis = pd.DataFrame(index=quarters, columns=REGIONS, dtype=object)
    exfx = pd.DataFrame(index=quarters, columns=REGIONS, dtype=float)
    exfx_basis = pd.DataFrame(index=quarters, columns=REGIONS, dtype=object)
    for r in REGIONS:
        for q in quarters:
            p = lag4(q)
            if (q, r) in ADR_YOY_DISCLOSED:
                yoy.at[q, r] = ADR_YOY_DISCLOSED[(q, r)]
                yoy_basis.at[q, r] = "disclosed (shareholder letter)"
            elif (q, r) in ADR_EXFX_DISCLOSED:
                yoy.at[q, r] = ADR_EXFX_DISCLOSED[(q, r)] + FX_PP.at[q, r]
                yoy_basis.at[q, r] = "derived (disclosed ex-FX + basket x pass-through)"
            elif p in lvl.index and pd.notna(lvl.at[p, r]) and pd.notna(lvl.at[q, r]):
                yoy.at[q, r] = (lvl.at[q, r] / lvl.at[p, r] - 1.0) * 100.0
                yoy_basis.at[q, r] = "modelled (from modelled levels)"
            else:
                yoy_basis.at[q, r] = "not available"

            if (q, r) in ADR_EXFX_DISCLOSED:
                exfx.at[q, r] = ADR_EXFX_DISCLOSED[(q, r)]
                exfx_basis.at[q, r] = "disclosed (shareholder letter)"
            elif pd.notna(yoy.at[q, r]):
                exfx.at[q, r] = yoy.at[q, r] - FX_PP.at[q, r]
                src = ("disclosed reported y/y" if (q, r) in ADR_YOY_DISCLOSED
                       else "modelled reported y/y")
                exfx_basis.at[q, r] = (
                    f"derived ({src} - basket x pass-through [{PASSTHROUGH_BASIS[r]}])")
            else:
                exfx_basis.at[q, r] = "not available"

    # Anchored level variant: the same series rescaled so each region-year's
    # nights-weighted quarterly ADR equals the 10-K annual regional ADR. This
    # removes the chaining drift but no longer honours the disclosed y/y exactly,
    # so it is published alongside, never instead. 2026 has no anchor and is
    # carried through unchanged.
    adr_ann_lu = ann.pivot(index="year", columns="region", values="adr")
    anch = lvl.copy()
    anch_basis = pd.DataFrame(index=quarters, columns=REGIONS, dtype=object)
    for r in REGIONS:
        k_last = 1.0
        for year in range(2021, 2027):
            qs = [q for q in quarters if qyear(q) == year]
            if not qs:
                continue
            if year in adr_ann_lu.index:
                fitted = float((nights.loc[qs, r] * lvl.loc[qs, r]).sum() /
                               nights.loc[qs, r].sum())
                k = float(adr_ann_lu.at[year, r]) / fitted
                k_last = k
                tag = (f"derived (level rescaled x{k:.4f} to the 10-K annual "
                       f"regional ADR; disclosed y/y no longer exact)")
            else:
                # No 2026 anchor: carry the last known rescaling so the anchored
                # series still reproduces the disclosed 2026 y/y exactly.
                k = k_last
                tag = (f"derived (no 2026 annual anchor; FY2025 rescaling x{k:.4f} "
                       f"carried forward)")
            for q in qs:
                anch.at[q, r] = lvl.at[q, r] * k
                anch_basis.at[q, r] = tag

    # ---------------- long output ----------------
    long_rows = []
    packs = [
        ("adr_usd", lvl, lvl_basis),
        ("adr_usd_anchored", anch, anch_basis),
        ("adr_yoy_reported_pct", yoy, yoy_basis),
        ("adr_yoy_exfx_pct", exfx, exfx_basis),
        ("nights_share_pct", share, nights_basis),
        ("nights_m", nights, nights_basis),
    ]
    for name, vals, bs in packs:
        for q in quarters:
            for r in REGIONS:
                long_rows.append({"quarter": q, "region": r, "metric": name,
                                  "value": vals.at[q, r], "basis": bs.at[q, r]})
    # FX contribution
    for q in quarters:
        for r in REGIONS:
            long_rows.append({
                "quarter": q, "region": r, "metric": "fx_contribution_pp",
                "value": FX_PP.at[q, r],
                "basis": f"derived (02 basket x pass-through [{PASSTHROUGH_BASIS[r]}])"})
    # ex-FX-and-mix, only where the letter states it
    for (q, r), v in ADR_EXFX_EXMIX_DISCLOSED.items():
        long_rows.append({"quarter": q, "region": r,
                          "metric": "adr_yoy_exfx_exmix_pct", "value": v,
                          "basis": "disclosed (ex-FX AND mix shift -- not an ex-FX figure)"})
    # qualitative sign statements
    for (q, r), txt in ADR_SIGN_STATEMENTS.items():
        for rr in (REGIONS if r == "all" else [r]):
            long_rows.append({"quarter": q, "region": rr,
                              "metric": "adr_sign_statement", "value": np.nan,
                              "basis": f"disclosed qualitative: {txt}"})
    long = pd.DataFrame(long_rows)
    long = long.sort_values(["quarter", "metric", "region"],
                            key=lambda s: s.map(qkey) if s.name == "quarter" else s)
    if write:
        long.to_csv(f"{OUT}/04_regional_quarterly.csv", index=False)

    # ---------------- wide output ----------------
    wide = pd.DataFrame({"quarter": quarters}).set_index("quarter")
    wide["adr_global_usd"] = kpi.set_index("quarter").adr_usd
    wide["nights_global_m"] = kpi.set_index("quarter").nights_m
    wide["seasonal_index"] = seas["S"]
    for r in REGIONS:
        wide[f"adr_{r}_usd"] = lvl[r]
        wide[f"adr_{r}_usd_anchored"] = anch[r]
        wide[f"adr_yoy_{r}_pct"] = yoy[r]
        wide[f"adr_yoy_exfx_{r}_pct"] = exfx[r]
        wide[f"fx_pp_{r}"] = FX_PP[r]
        wide[f"nights_share_{r}_pct"] = share[r]
        wide[f"basis_adr_{r}"] = lvl_basis[r].map(
            lambda s: "disclosed-chained" if isinstance(s, str) and "disclosed" in s
            else ("modelled" if isinstance(s, str) and s.startswith("modelled") else s))
    if write:
        wide.round(4).to_csv(f"{OUT}/04_regional_quarterly_wide.csv")

    # ---------------- reconciliation ----------------
    recon = []
    w = share / 100.0
    adr_q = kpi.set_index("quarter").adr_usd
    for q in quarters:
        rec = float((w.loc[q, REGIONS] * lvl.loc[q, REGIONS]).sum())
        act = float(adr_q[q])
        p = lag4(q)
        rec_yoy = np.nan
        if p in quarters:
            rec_prev = float((w.loc[p, REGIONS] * lvl.loc[p, REGIONS]).sum())
            rec_yoy = (rec / rec_prev - 1.0) * 100.0
        act_yoy = (act / adr_q[p] - 1.0) * 100.0 if p in adr_q.index else np.nan
        n_disc = sum(1 for r in REGIONS if (q, r) in ADR_YOY_DISCLOSED)
        n_der = sum(1 for r in REGIONS if (q, r) not in ADR_YOY_DISCLOSED
                    and (q, r) in ADR_EXFX_DISCLOSED)
        recon.append({
            "block": "quarterly", "quarter": q, "region": "total",
            "weighted_regional_adr_usd": rec, "disclosed_global_adr_usd": act,
            "residual_usd": rec - act, "residual_pct": (rec / act - 1.0) * 100.0,
            "weighted_regional_adr_yoy_pct": rec_yoy,
            "disclosed_global_adr_yoy_pct": act_yoy,
            "residual_yoy_pp": rec_yoy - act_yoy if pd.notna(rec_yoy) else np.nan,
            "n_regions_disclosed": n_disc, "n_regions_derived": n_der,
            "n_regions_modelled": 4 - n_disc - n_der,
            "informative": int(n_disc + n_der > 0),
            "note": ("regional ADR is A_r,y x S_q by construction here, so the "
                     "residual is zero mechanically -- not a validation"
                     if n_disc + n_der == 0 else ""),
        })

    # annual: nights-weighted quarterly regional ADR vs the 10-K anchor
    adr_ann = ann.pivot(index="year", columns="region", values="adr")
    for year in range(2021, 2026):
        qs = [q for q in quarters if qyear(q) == year]
        for r in REGIONS:
            num = float((nights.loc[qs, r] * lvl.loc[qs, r]).sum())
            den = float(nights.loc[qs, r].sum())
            fitted = num / den
            anchor = float(adr_ann.at[year, r])
            n_disc = sum(1 for q in qs if (q, r) in ADR_YOY_DISCLOSED)
            n_der = sum(1 for q in qs if (q, r) in ADR_EXFX_DISCLOSED
                        and (q, r) not in ADR_YOY_DISCLOSED)
            recon.append({
                "block": "annual", "quarter": str(year), "region": r,
                "weighted_regional_adr_usd": fitted,
                "disclosed_global_adr_usd": anchor,
                "residual_usd": fitted - anchor,
                "residual_pct": (fitted / anchor - 1.0) * 100.0,
                "n_regions_disclosed": n_disc, "n_regions_derived": n_der,
                "n_regions_modelled": 4 - n_disc - n_der,
                "informative": int(n_disc + n_der > 0),
                "note": "nights-weighted quarterly ADR vs 10-K annual regional ADR",
            })

    # pass-through: implied from the quarters that disclose reported AND ex-FX
    for (q, r), rep in ADR_YOY_DISCLOSED.items():
        if (q, r) not in ADR_EXFX_DISCLOSED:
            continue
        basket = float(fx.at[q, r])
        implied = (rep - ADR_EXFX_DISCLOSED[(q, r)]) / basket if abs(basket) > 1.0 else np.nan
        recon.append({
            "block": "passthrough", "quarter": q, "region": r,
            "weighted_regional_adr_usd": implied,
            "disclosed_global_adr_usd": PASSTHROUGH[r],
            "residual_usd": implied - PASSTHROUGH[r] if pd.notna(implied) else np.nan,
            "residual_pct": np.nan,
            "informative": int(pd.notna(implied)),
            "note": (f"implied pass-through = (reported {rep:+.0f} - exFX "
                     f"{ADR_EXFX_DISCLOSED[(q, r)]:+.0f}) / basket {basket:+.2f}"
                     + ("" if abs(basket) > 1.0 else
                        "; basket <1% so 1pp rounding dominates -- not usable")),
        })

    rec_df = pd.DataFrame(recon)
    if write:
        rec_df.to_csv(f"{OUT}/04_reconciliation.csv", index=False)
    return long, wide, rec_df, nights, lvl, yoy, exfx, share, seas, ws10


def report(long, wide, rec, nights, lvl, yoy, exfx, share, seas, ws10):
    quarters = list(lvl.index)
    pd.set_option("display.width", 220)
    print("=" * 100)
    print("REGIONAL ADR LEVELS, $ (D = chained on disclosed y/y, m = modelled)")
    t = pd.DataFrame(index=lvl.index, columns=REGIONS, dtype=object)
    for q in quarters:
        for r in REGIONS:
            tag = "D" if (q, r) in ADR_YOY_DISCLOSED or (q, r) in ADR_EXFX_DISCLOSED else "m"
            t.at[q, r] = f"{lvl.at[q, r]:7.1f}{tag}"
    t["global"] = wide.adr_global_usd.map(lambda v: f"{v:7.2f}")
    t["S_q"] = seas["S"].map(lambda v: f"{v:5.3f}" if pd.notna(v) else "   . ")
    print(t.to_string())

    print()
    print("REPORTED ADR Y/Y, %")
    print(yoy.round(1).to_string())
    print()
    print("EX-FX ADR Y/Y, %")
    print(exfx.round(1).to_string())
    print()
    print("NIGHTS SHARE, % (RAS: 10-K annual rows x letter quarterly columns)")
    print(share.round(1).to_string())

    q = rec[rec.block == "quarterly"]
    print()
    print("RECONCILIATION vs DISCLOSED GLOBAL ADR")
    print(q[["quarter", "weighted_regional_adr_usd", "disclosed_global_adr_usd",
             "residual_usd", "residual_pct", "residual_yoy_pp",
             "n_regions_disclosed", "n_regions_derived", "n_regions_modelled",
             "informative"]].round(3).to_string(index=False))
    inf = q[q.informative == 1]
    print(f"\ninformative quarters (>=1 region disclosed/derived): {len(inf)}")
    print(f"  mean abs residual   {inf.residual_pct.abs().mean():.3f}%")
    print(f"  max  abs residual   {inf.residual_pct.abs().max():.3f}%  "
          f"({inf.loc[inf.residual_pct.abs().idxmax(), 'quarter']})")
    print(f"  mean abs y/y resid  {inf.residual_yoy_pp.abs().mean():.3f} pp")

    # is the residual seasonal? if regional seasonals differed from the common
    # S_q, the residual would carry a fiscal-quarter signature
    d = inf.copy()
    d["fq"] = d.quarter.str[0]
    print("\nresidual by fiscal quarter (tests the common-seasonal assumption):")
    print(d.groupby("fq").residual_pct.agg(["count", "mean", "std"]).round(3).to_string())
    print("  residual path within each fiscal quarter (a fixed regional seasonal")
    print("  would give a flat path; a rising path is cumulative chaining drift):")
    for fq in sorted(d.fq.unique()):
        sub = d[d.fq == fq]
        print("   Q" + fq + "  " + "  ".join(
            f"{q}:{v:+.2f}%" for q, v in zip(sub.quarter, sub.residual_pct)))

    print()
    print("ANNUAL CHECK: nights-weighted quarterly ADR vs 10-K annual regional ADR")
    a = rec[rec.block == "annual"].pivot(index="quarter", columns="region",
                                         values="residual_pct")
    print(a[REGIONS].round(2).to_string())

    print()
    print("FX PASS-THROUGH, implied from letters that give reported AND ex-FX")
    p = rec[(rec.block == "passthrough") & (rec.informative == 1)]
    print(p.groupby("region").weighted_regional_adr_usd.agg(
        ["count", "mean", "median", "std"]).round(3).to_string())
    print("assumed:", PASSTHROUGH)

    # Sign check. The letters make qualitative claims about the direction of ex-FX
    # regional ADR in quarters where they give no number. Any modelled or derived
    # ex-FX that contradicts one is a failure of the model, not of the company.
    print()
    print("SIGN CHECK: derived/modelled ex-FX ADR vs the letters' qualitative claims")
    fails = []
    for (q, r), txt in ADR_SIGN_STATEMENTS.items():
        for rr in (REGIONS if r == "all" else [r]):
            if (q, rr) in ADR_EXFX_DISCLOSED or q not in exfx.index:
                continue
            v = exfx.at[q, rr]
            if pd.isna(v):
                continue
            up = "up" in txt and "flat to up" not in txt and "down" not in txt
            down = "down" in txt
            flat_up = "flat to up" in txt
            bad = (up and v < -0.5) or (down and v > 0.5) or (flat_up and v < -0.5)
            if bad:
                fails.append({"quarter": q, "region": rr, "model_exfx_pct": round(v, 1),
                              "letter_says": txt,
                              "cell": ("modelled" if (q, rr) not in ADR_YOY_DISCLOSED
                                       else "derived from disclosed reported y/y")})
    if fails:
        f = pd.DataFrame(fails).sort_values(["quarter", "region"], key=lambda s:
                                            s.map(qkey) if s.name == "quarter" else s)
        print(f.to_string(index=False))
        print(f"  {len(f)} contradictions out of "
              f"{sum(1 for k in ADR_SIGN_STATEMENTS for _ in (REGIONS if k[1] == 'all' else [k[1]]))}"
              " sign claims")
    else:
        print("  none")

    print()
    print("WS10 estimated nights shares vs this RAS fit (WS10 is ADR-informed; "
          "shown as a cross-check only, never used as an input)")
    ws = ws10.set_index("quarter")
    cmp_rows = []
    for q in quarters:
        if q not in ws.index:
            continue
        for r in REGIONS:
            v = ws.at[q, f"{r}_nights_share_est_pct"]
            if pd.notna(v):
                cmp_rows.append({"quarter": q, "region": r, "ws10": v,
                                 "ras": share.at[q, r], "diff_pp": share.at[q, r] - v})
    c = pd.DataFrame(cmp_rows)
    if len(c):
        print(c.groupby("region").diff_pp.agg(["count", "mean", "min", "max"]).round(2).to_string())

    # The index WS10 used to build those shares, checked against the 10-K.
    print()
    print("WS10 regional ADR index (used to derive its nights shares) vs the 10-K")
    ws10_index = {"na": 1.42, "emea": 0.97, "latam": 0.68, "apac": 0.59}
    g = wide.adr_global_usd
    idx = pd.DataFrame({
        "ws10_index": pd.Series(ws10_index),
        "this_panel_2025": pd.Series(
            {r: float((lvl.loc[[q for q in quarters if qyear(q) == 2025], r] *
                       nights.loc[[q for q in quarters if qyear(q) == 2025], r]).sum() /
                      nights.loc[[q for q in quarters if qyear(q) == 2025], r].sum() /
                      (g.loc[[q for q in quarters if qyear(q) == 2025]] *
                       wide.nights_global_m.loc[[q for q in quarters if qyear(q) == 2025]]).sum() *
                      wide.nights_global_m.loc[[q for q in quarters if qyear(q) == 2025]].sum())
             for r in REGIONS}),
    })
    idx["diff"] = idx.this_panel_2025 - idx.ws10_index
    print(idx.round(3).to_string())
    print("  NOTE: WS10 ranks LatAm ADR ABOVE APAC (0.68 vs 0.59). The FY2025 10-K")
    print("  ranks them the other way (LatAm $94.9 vs APAC $118.2, i.e. 0.55 vs 0.69).")
    print("  WS10's estimated quarterly nights shares are built on that index, which")
    print("  is a second reason not to use them as an ADR-panel input.")


def sensitivity(lvl_base, rec_base, share_base):
    """How much does the flat-share 2021 seed matter?

    2021 gets no regional nights disclosure, so the RAS seed holds each region's
    share flat inside the year. The disclosed quarterly US revenue share says that
    is wrong: it runs 57.6% in 1Q21 to 39.1% in 4Q21, and 51.2% to 36.7% through
    2022, as international travel reopened behind the US. (US revenue is
    stay-dated and US is not NA, so it cannot be converted into a nights share --
    it is used here only as a within-year SHAPE for the NA seed row, after which
    RAS restores the 10-K annual row total.)

    The point of the run is not to pick a winner. It is to measure how far the
    2023-2026 disclosure-era panel moves when the weakest assumption in the build
    is replaced by a different, equally arguable one.
    """
    ws10 = pd.read_csv(f"{OVN}/10_regional_panel_quarterly.csv").set_index("quarter")
    shape = {q: v for q, v in ws10.us_revenue_share_pct.items() if pd.notna(v)}
    out = build(na_shape=shape, write=False)
    lvl_s, share_s, rec_s = out[4], out[7], out[2]
    era = [q for q in lvl_base.index if qkey(q) >= (2023, 1)]

    print()
    print("SENSITIVITY: reseed NA 2021-2022 with the disclosed US revenue share shape")
    d_lvl = (lvl_s.loc[era] / lvl_base.loc[era] - 1.0) * 100.0
    d_shr = share_s.loc[era] - share_base.loc[era]
    print("  disclosure-era (1Q23+) ADR level change, %:")
    print(d_lvl.agg(["mean", "min", "max"]).round(2).to_string())
    print("  disclosure-era nights share change, pp:")
    print(d_shr.agg(["mean", "min", "max"]).round(2).to_string())
    q0 = rec_base[(rec_base.block == "quarterly") & (rec_base.informative == 1)]
    q1 = rec_s[(rec_s.block == "quarterly") & (rec_s.informative == 1)]
    print(f"  mean abs reconciliation residual: base {q0.residual_pct.abs().mean():.3f}% "
          f"-> reseeded {q1.residual_pct.abs().mean():.3f}%")
    print("  2021-2022 NA nights share, base vs reseeded:")
    pre = [q for q in lvl_base.index if qkey(q) < (2023, 1)]
    print(pd.DataFrame({"base": share_base.loc[pre, "na"],
                        "reseeded": share_s.loc[pre, "na"]}).round(1).to_string())
    print("  VERDICT: REJECTED as the primary. It doubles the reconciliation")
    print("  residual and implies a 4Q22 NA nights share of 24%, against a 33.8%")
    print("  full-year 2022 figure in the FY2022 10-K -- the US revenue share is")
    print("  moving on the international reopening and on stay-date timing, not on")
    print("  NA's share of booked nights. The flat-share seed is kept. What the run")
    print("  does establish is the size of the exposure: swapping the weakest")
    print("  assumption in the build moves individual 1Q23 levels by up to 8%, so")
    print("  the 2021-2022 regional ADR levels are the least reliable part of this")
    print("  panel and the 2023+ disclosure-chained levels inherit that base.")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    res = build()
    report(*res)
    sensitivity(res[4], res[2], res[7])
    print("\nwrote:")
    for f in ("04_regional_quarterly.csv", "04_regional_quarterly_wide.csv",
              "04_reconciliation.csv"):
        print(" ", f"{OUT}/{f}")
