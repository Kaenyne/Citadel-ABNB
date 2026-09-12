"""rnpl-short-audit: what B3's FY27 driver base actually embeds, and where RNPL enters.

    cd "<repo root>"
    /Users/theomachado/.venvs/citadel-abnb/bin/python \
        analysis/src/rnpl_short_audit/fy27_rnpl_channels.py

READ-ONLY on every existing artefact.  Writes ONLY to
`data/processed/rnpl_short_audit/`.  Nothing under `forecast_methods/`,
`registry/` or any tracked note is opened for writing, and `harness/score.py`
is not run.  Companion note:
`docs/rnpl-short-audit/02_fy27-decomposition-rnpl-synergy.md`.

WHAT IT DOES, in five blocks:

 1. TRACE.  Rebuilds the quarterly Nights-and-Seats and blended-ADR path that
    sits behind B3 v2's g_N = +9.4558% and g_ADR = +1.8777%, from the SAME two
    inputs B3 uses -- the printed 1H26 regional panel
    (`l1_panel_quarterly.csv`) and the FY27 driver scenario
    (`l1_fy27_regional_scenario_driver.csv`).  The point is to show what the
    quarterly SHAPE of that N is, because B3 publishes only the annual number.

 2. LAP GRID.  Prices a product-bundle lap against B3's N at the three lap
    schedules the repo argues over (none / NA-only / global), and against
    PR #32's FY27 nights readings, so the lap can be quoted as a delta from
    B3 rather than as a free-standing number.

 3. KAPPA ANATOMY.  Splits kappa_w into its LAG channel and its PRINT channel
    exactly as `l1_reconciliation_v2.project.kernel_kappa` does, and then asks
    the question B3's own caveat 1 raises and does not answer: how much of the
    published 2.34pp kernel-weight band survives a SELF-CONSISTENT re-fit of
    lambda at each w?  This is the object the RNPL lead-time evidence bears on.

 4. CHANNEL LEDGER.  Every RNPL -> FY27-growth channel with a low/high band in
    growth points and an evidence label, priced off repo primitives only.

 5. PHASING.  FY27 quarterly nights / ADR / kappa / reported revenue growth on
    B3's own path and on an RNPL-aware path, against the FY26 comps, and the
    EV/EBITDA turns at +0.48 per point applied ONCE.

EVERY number written out carries a `status` in
{measured, derived, assumed, unidentified} and a `source` path.  Nothing here
is registered with the harness; nothing here is a scored object.
"""
from __future__ import annotations

import pathlib
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).resolve()
REPO = HERE.parents[3]
PROC = REPO / "data" / "processed"
FM = PROC / "forecast_methods"
V1 = FM / "l1_reconciliation"
V2 = FM / "l1_reconciliation_v2"
OUT = PROC / "rnpl_short_audit"
OUT.mkdir(parents=True, exist_ok=True)

LOG: list[str] = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.append(s)


def qorder(q: str) -> int:
    return int(q[:4]) * 4 + int(q[5]) - 1


def qadd(q: str, k: int) -> str:
    o = qorder(q) + k
    return f"{o // 4}Q{o % 4 + 1}"


def canon(q: str) -> str:
    q = str(q).strip()
    if "Q" in q and q[0].isdigit() and len(q) == 4:
        return f"20{q[2:]}Q{q[0]}"
    return q


# ===========================================================================
# 1. TRACE -- rebuild the quarterly N and ADR path behind B3 v2's annual pair
# ===========================================================================
say("=" * 78)
say("1. WHAT B3 v2's DRIVER-BASE N ACTUALLY EMBEDS")
say("=" * 78)

panel = pd.read_csv(V1 / "l1_panel_quarterly.csv")          # printed / reconciled history
scen = pd.read_csv(V1 / "l1_fy27_regional_scenario_driver.csv")  # 2026Q3 -> 2027Q4
kpi = pd.read_csv(PROC / "overnight" / "02_kpi_panel_quarterly.csv")
kpi["quarter"] = kpi["quarter"].map(canon)
kpi["gbv_musd"] = kpi["gbv_busd"] * 1000.0

hist = panel[["quarter", "region", "nights_m", "gbv_musd"]].copy()
fwd = scen[["quarter", "region", "nights_m", "gbv_musd", "nights_yoy_pct", "adr_yoy_pct"]].copy()
full = pd.concat([hist[~hist.quarter.isin(set(fwd.quarter))], fwd], ignore_index=True)

q_tot = (full.groupby("quarter")
             .agg(nights_m=("nights_m", "sum"), gbv_musd=("gbv_musd", "sum"))
             .reset_index())
q_tot["adr_usd"] = q_tot["gbv_musd"] / q_tot["nights_m"]
q_tot = q_tot.sort_values("quarter", key=lambda s: s.map(qorder)).reset_index(drop=True)
q_tot = q_tot.set_index("quarter")

rows = []
for q in [f"{y}Q{i}" for y in (2026, 2027) for i in range(1, 5)]:
    q4 = qadd(q, -4)
    src = ("printed_panel" if q in ("2026Q1", "2026Q2")
           else "driver_scenario_flat_regional_yoy")
    rows.append(dict(
        quarter=q,
        nights_m=q_tot.loc[q, "nights_m"],
        nights_yoy_pct=100 * (q_tot.loc[q, "nights_m"] / q_tot.loc[q4, "nights_m"] - 1),
        adr_usd=q_tot.loc[q, "adr_usd"],
        adr_yoy_pct=100 * (q_tot.loc[q, "adr_usd"] / q_tot.loc[q4, "adr_usd"] - 1),
        gbv_musd=q_tot.loc[q, "gbv_musd"],
        gbv_yoy_pct=100 * (q_tot.loc[q, "gbv_musd"] / q_tot.loc[q4, "gbv_musd"] - 1),
        n_source=src, status="derived",
        source="l1_panel_quarterly.csv (1H26 printed) + l1_fy27_regional_scenario_driver.csv"))
qpath = pd.DataFrame(rows)

n26 = qpath[qpath.quarter.str.startswith("2026")].nights_m.sum()
n27 = qpath[qpath.quarter.str.startswith("2027")].nights_m.sum()
g26 = qpath[qpath.quarter.str.startswith("2026")].gbv_musd.sum()
g27 = qpath[qpath.quarter.str.startswith("2027")].gbv_musd.sum()
gN = 100 * (n27 / n26 - 1)
gADR = 100 * ((g27 / n27) / (g26 / n26) - 1)
gGBV = 100 * (g27 / g26 - 1)

say(f"\nFY26 N {n26:,.2f}M -> FY27 N {n27:,.2f}M   g_N = {gN:+.6f}%   "
    f"(B3 v2 publishes +9.455783%)")
say(f"FY26 GBV ${g26:,.1f}M -> FY27 ${g27:,.1f}M   g_GBV = {gGBV:+.6f}%   "
    f"(B3 v2 publishes +11.511084%)")
say(f"g_ADR = {gADR:+.6f}%   (B3 v2 publishes +1.877745%)")
say("\nQUARTERLY SHAPE of the N that B3 publishes only as an annual number:")
say(qpath[["quarter", "nights_m", "nights_yoy_pct", "adr_yoy_pct",
           "gbv_yoy_pct", "n_source"]].to_string(index=False,
                                                 float_format=lambda v: f"{v:10.3f}"))

reg27 = scen[scen.quarter.str.startswith("2027")][["region", "nights_yoy_pct"]].drop_duplicates()
say("\nREGIONAL CELLS -- the ONLY exogenous nights inputs in the FY27 path.")
say("Each is a SINGLE ANNUAL RATE applied FLAT to all four 2027 quarters:")
say(reg27.to_string(index=False))
say("source: data/processed/overnight/10_regional_forecast.csv, period FY27, scenario 'base'")
say("        (bear NA+3/EMEA+4/LatAm+12/APAC+11 -> TOTAL +5.82%;")
say("         bull NA+8/EMEA+9/LatAm+19/APAC+18 -> TOTAL +11.48%)")
say("\nNO quarterly phasing, NO lap schedule, NO RNPL term, NO cancellation term,")
say("NO pull-forward term exists anywhere in this path.  The FY27 quarterly nights")
say("growth varies ONLY because the regional mix drifts between quarters.")

# ===========================================================================
# 2. LAP GRID -- price a bundle lap as a delta from B3's N
# ===========================================================================
say("\n" + "=" * 78)
say("2. THE LAP GRID -- B3's N against the three lap schedules the repo argues over")
say("=" * 78)

LAPS = [
    dict(schedule="none (B3 v2 as published)", fy27_nights_yoy_pct=gN,
         status="derived",
         source="l1_fy27_regional_scenario_driver.csv; flat regional y/y, no lap term",
         note="NA +6.0 / EMEA +7.0 / LatAm +16.0 / APAC +15.0 applied flat to 4Q27"),
    dict(schedule="NA-only bundle lap (PR #32)", fy27_nights_yoy_pct=8.2,
         status="derived",
         source="git show origin/krish/nights-quarterly:research/notes/nights_quarterly.md",
         note="US RNPL anniversary from 3Q26; bundle contribution removed from the NA cells"),
    dict(schedule="global bundle lap (PR #32)", fy27_nights_yoy_pct=6.4,
         status="derived",
         source="git show origin/krish/nights-quarterly:research/notes/nights_quarterly.md",
         note="global RNPL anniversary from 1Q27 (17 Feb 2026 rollout) on top of the US lap"),
    dict(schedule="29-bridge FY27 walk", fy27_nights_yoy_pct=9.2,
         status="derived",
         source="research/notes/overnight/29_q4-fy27-bridge.md",
         note="Krish's FY27 walk; sits between B3 and the NA-only lap"),
]
lapdf = pd.DataFrame(LAPS)
lapdf["delta_vs_b3_pp"] = lapdf["fy27_nights_yoy_pct"] - gN
# GBV growth if only N moves and the ADR line is held at B3's +1.8777%
lapdf["implied_gbv_growth_pct"] = (
    (1 + lapdf["fy27_nights_yoy_pct"] / 100) * (1 + gADR / 100) - 1) * 100
lapdf["delta_gbv_vs_b3_pp"] = lapdf["implied_gbv_growth_pct"] - gGBV
say(lapdf[["schedule", "fy27_nights_yoy_pct", "delta_vs_b3_pp",
           "implied_gbv_growth_pct", "delta_gbv_vs_b3_pp", "status"]]
    .to_string(index=False, float_format=lambda v: f"{v:9.3f}"))
say("\nThe lap is therefore worth  0.00pp (B3 as published)  to  -3.06pp of FY27 nights")
say("growth, i.e. up to -3.12pp of GBV growth.  B3 carries NONE of it.")

# ===========================================================================
# 3. KAPPA ANATOMY -- lag channel vs print channel, and the lambda re-fit test
# ===========================================================================
say("\n" + "=" * 78)
say("3. KAPPA ANATOMY -- how much of the 2.34pp w-band is economics?")
say("=" * 78)

GBV = {q: float(q_tot.loc[q, "gbv_musd"]) for q in q_tot.index}
for q in kpi.quarter:
    if q not in GBV:
        GBV[q] = float(kpi.loc[kpi.quarter == q, "gbv_musd"].iloc[0])
# the L1 spine pins 2026Q1/2026Q2 GBV to the letters; keep the KPI values for history
for q in kpi.quarter:
    if qorder(q) < qorder("2026Q1"):
        GBV[q] = float(kpi.loc[kpi.quarter == q, "gbv_musd"].iloc[0])

REV = {str(canon(r.quarter)): float(r.revenue_musd)
       for r in kpi.itertuples() if np.isfinite(r.revenue_musd)}
ACTUALS = {"2026Q1": 2678.0, "2026Q2": 3608.0}       # printed, per B3 v2 section 1
Y0 = [f"2026Q{i}" for i in range(1, 5)]
Y1 = [f"2027Q{i}" for i in range(1, 5)]
W_GRID = [0.33, 0.50, 2.0 / 3.0]


def lam_fit(w: float, years=(2023, 2024, 2025, 2026)) -> dict:
    """lambda_s = Revenue_q / [w GBV_{q-1} + (1-w) GBV_{q-2}], season-averaged.
    Exactly project.seasonal_lambda, re-implemented so it can be re-fit at each w."""
    out = {}
    for s in range(1, 5):
        vals = []
        for yr in years:
            q = f"{yr}Q{s}"
            q1, q2 = qadd(q, -1), qadd(q, -2)
            if q in REV and q1 in GBV and q2 in GBV:
                base = w * GBV[q1] + (1 - w) * GBV[q2]
                if base > 0:
                    vals.append(100.0 * REV[q] / base)
        out[s] = float(np.mean(vals)) if vals else np.nan
    return out


def year_rev(lam: dict, w: float, quarters, use_actuals=True):
    tot, parts = 0.0, {}
    for q in quarters:
        base = w * GBV[qadd(q, -1)] + (1 - w) * GBV[qadd(q, -2)]
        modelled = lam[int(q[5])] / 100.0 * base
        used = ACTUALS[q] if (use_actuals and q in ACTUALS) else modelled
        parts[q] = dict(modelled=modelled, used=used)
        tot += used
    return tot, parts


kap_rows = []
for w in W_GRID:
    lam_fixed = lam_fit(2.0 / 3.0)          # B3's convention: lambda fit at w = 2/3, held
    lam_self = lam_fit(w)                   # the self-consistent re-fit B3 caveat 1 names
    for tag, lam in (("lambda_fixed_at_w=2/3 (B3 convention)", lam_fixed),
                     ("lambda_REFIT_at_this_w (B3 caveat 1)", lam_self)):
        r0, _ = year_rev(lam, w, Y0, use_actuals=True)
        r1, _ = year_rev(lam, w, Y1, use_actuals=True)
        r0k, _ = year_rev(lam, w, Y0, use_actuals=False)
        g_rev = r1 / r0 - 1
        g_gbv = sum(GBV[q] for q in Y1) / sum(GBV[q] for q in Y0) - 1
        kap = (1 + g_rev) / (1 + g_gbv) - 1
        kap_lag = (1 + r1 / r0k - 1) / (1 + g_gbv) - 1
        kap_rows.append(dict(
            kernel_w=w, lambda_convention=tag,
            lambda_q1=lam[1], lambda_q2=lam[2], lambda_q3=lam[3], lambda_q4=lam[4],
            fy26_revenue_musd=r0, fy26_all_kernel_musd=r0k, fy27_revenue_musd=r1,
            fy27_growth_pct=100 * g_rev, gbv_growth_pct=100 * g_gbv,
            kappa_pct=100 * kap, kappa_lag_pct=100 * kap_lag,
            kappa_print_pct=100 * (kap - kap_lag),
            kappa_pp_of_growth=100 * ((1 + g_gbv) * (1 + kap) - (1 + g_gbv)),
            status="derived",
            source="recomputed from l1_reconciliation_v2/project.py kernel_kappa logic"))
kap = pd.DataFrame(kap_rows)

for tag in kap.lambda_convention.unique():
    sub = kap[kap.lambda_convention == tag]
    say(f"\n--- {tag}")
    say(sub[["kernel_w", "lambda_q2", "fy26_revenue_musd", "fy27_revenue_musd",
             "fy27_growth_pct", "kappa_pct", "kappa_lag_pct", "kappa_print_pct"]]
        .to_string(index=False, float_format=lambda v: f"{v:11.4f}"))
    band = sub.fy27_growth_pct.max() - sub.fy27_growth_pct.min()
    say(f"    FY27 growth band across w in [0.33, 2/3]: {band:.3f}pp"
        f"   -> EV/EBITDA turns +/- {0.48 * band / 2:.3f}")

fixed = kap[kap.lambda_convention.str.startswith("lambda_fixed")]
refit = kap[kap.lambda_convention.str.startswith("lambda_REFIT")]
band_fixed = fixed.fy27_growth_pct.max() - fixed.fy27_growth_pct.min()
band_refit = refit.fy27_growth_pct.max() - refit.fy27_growth_pct.min()
lag_band = fixed.kappa_lag_pct.max() - fixed.kappa_lag_pct.min()

say("\nTHE FINDING B3's OWN CAVEAT 1 POINTS AT AND DOES NOT PRICE:")
say(f"  published band (lambda fixed at w = 2/3)          {band_fixed:6.3f}pp"
    f"   = +/- {0.48 * band_fixed / 2:.3f} turns")
say(f"  self-consistent band (lambda re-fit at each w)    {band_refit:6.3f}pp"
    f"   = +/- {0.48 * band_refit / 2:.3f} turns")
say(f"  pure LAG channel span (the only economics in it)  {lag_band:6.3f}pp")
say("  The PRINT channel -- FY26 1H is the printed number while FY26 2H and all of")
say("  FY27 are kernel -- carries "
    f"{100 * (1 - lag_band / band_fixed):.1f}% of the published band.")

# 2Q26 reconstruction error by w: a direct read on which w the prints support
rec = []
for w in W_GRID:
    for tag, lam in (("fixed@2/3", lam_fit(2.0 / 3.0)), ("refit", lam_fit(w))):
        for q in ("2026Q1", "2026Q2"):
            base = w * GBV[qadd(q, -1)] + (1 - w) * GBV[qadd(q, -2)]
            mod = lam[int(q[5])] / 100.0 * base
            rec.append(dict(kernel_w=w, lambda_convention=tag, quarter=q,
                            printed_musd=ACTUALS[q], kernel_musd=mod,
                            err_pct=100 * (mod / ACTUALS[q] - 1),
                            status="derived",
                            source="printed 1H26 revenue vs the kernel at this w"))
recdf = pd.DataFrame(rec)
say("\nWHICH w DO THE PRINTED 1H26 QUARTERS SUPPORT?  (lambda fixed at 2/3, B3 convention)")
say(recdf[recdf.lambda_convention == "fixed@2/3"]
    .to_string(index=False, float_format=lambda v: f"{v:10.2f}"))
say("  -> at w = 0.33 the kernel misses printed 2Q26 by ~-11%; at w = 2/3 by ~-0.2%.")
say("  -> but lambda was FIT at w = 2/3, so this test is partly circular; the re-fit")
say("     column below is the non-circular version.")
say(recdf[recdf.lambda_convention == "refit"]
    .to_string(index=False, float_format=lambda v: f"{v:10.2f}"))

# ===========================================================================
# 4. CHANNEL LEDGER -- every RNPL -> FY27 growth channel, banded and labelled
# ===========================================================================
say("\n" + "=" * 78)
say("4. RNPL -> FY27 REVENUE GROWTH: THE CHANNEL LEDGER")
say("=" * 78)

# cancellation-tail primitive: repo's own sensitivity, annualised onto FY26 N
CANC_PP_PER_M_NIGHTS = np.mean([0.75, 0.82])   # 03_insider_mechanics.md 1.6
canc_1pp_nights_m = 0.01 * n26                 # +1pp of platform cancellation on FY26 N
canc_1pp_growth_pp = -100 * canc_1pp_nights_m / n26

CH = [
    dict(id="a", channel="volume N -- product-bundle lap (US 3Q26, global 1Q27, "
                         "Jul-26 types expansion)",
         lo_pp=-3.06, hi_pp=0.00, central_pp=-1.26, acts_on="N -> GBV -> revenue",
         status="derived",
         source="PR #32 nights_quarterly.md (+8.2% NA-only / +6.4% global) vs B3 v2 "
                "g_N +9.4558%; dates from 01_ground-truth/03_insider_mechanics.md 1.6",
         in_b3="NO -- B3's N carries no lap term of any kind",
         double_count_flag="YES -- the +3pt nights / +4pt GBV is the BUNDLE (RNPL + "
                           "cancellation redesign + SINGLE FEE). The single-fee leg is "
                           "also the ASSUMED fee line (+0.90pp carried, +0.36 to +0.59pp "
                           "restated) and the -0.62pp GBV subtraction. Subtract a bundle "
                           "lap in N AND carry the fee line and the fee leg is counted "
                           "twice. 03_insider_mechanics.md 1.6 says so in terms."),
    dict(id="b", channel="volume N -- RNPL cancellation tail and rising propensity "
                         "(platform ~16% -> ~17%)",
         lo_pp=-0.90, hi_pp=0.00, central_pp=-0.30, acts_on="N -> GBV -> revenue",
         status="derived",
         source="Jessie plateau-plus-drag: FY27 cancel term -0.90pp vs FY26 -0.60pp "
                "(git show origin/jessie/backlog-conversion:research/notes/"
                "choice_nights_driver.md, nights_simple.csv, cancel_rate 17.00% 2026 -> "
                "17.75% 2027); D1 cohort grid tail -0.15 to -0.93pp per quarter in "
                "3Q26/4Q26 (D1_rnpl_cohort_scenarios.csv); 2Q26 10-Q 'have experienced "
                f"higher cancellation rates'.  +1pp of platform cancellation on FY26 N = "
                f"{canc_1pp_nights_m:.2f}M nights = {canc_1pp_growth_pp:.2f}pp of growth",
         in_b3="NO",
         double_count_flag="YES with (a), and this is the most likely error in practice. "
                           "PR #32's global lap gives FY27 nights +6.42% with NO "
                           "cancellation term; Jessie's plateau-plus-drag gives +6.52% "
                           "with a lap of ZERO and a -0.90pp cancellation term. Two "
                           "routes to the SAME total, 0.10pp apart -- not two additive "
                           "effects. Adding them gives ~+5.5% and is a double count. "
                           "Separately: the 16->17% step is a LEVEL already inside "
                           "printed FY25/FY26 net nights; only a FURTHER rise hits FY27 "
                           "growth."),
    dict(id="c", channel="volume N -- pull-forward reversal (lead-time lengthening)",
         lo_pp=-1.80, hi_pp=0.00, central_pp=-0.90, acts_on="GBV timing (booking-dated)",
         status="unidentified",
         source="scaled from the US-cohort calculation in "
                "research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md (3Q25 US "
                "RNPL nights share 3.3-5.0% x 7-15% lead-time uplift on a 2.2-month mean "
                "lead time = 0.17-0.55% of nights booked early, which the comp gives "
                "back; -0.2 to -0.4pp applied to 3Q26). The ex-NA cohort laps in FY27 at "
                "a ~16.7% RNPL NIGHTS share (21% GBV share / 1.33x ADR ratio, derived "
                "from 4pts GBV on 3pts nights, 1Q26), i.e. ~3-5x the US cohort. 2Q26 "
                "10-Q: GBV/revenue/cash timing 'may become less correlated'. The "
                "night-weighted RNPL cancellation curve and the lead-time DISTRIBUTION "
                "are UNIDENTIFIED (only the mean is anchored).",
         in_b3="NO",
         double_count_flag="YES with (e) -- a booking-dated pull-forward and a kernel "
                           "lead-time shift are the SAME object seen from two sides. "
                           "Price it in N or in kappa_w, never in both. And note the "
                           "additive sum of (a)+(b)+(c) puts FY27 nights BELOW every "
                           "published construction, which is itself evidence of overlap."),
    dict(id="d", channel="ADR line -- RNPL larger-home mix and the pricing residual; "
                         "TWO-SIDED, and B3 already sits at the mean-reversion end",
         lo_pp=-2.00, hi_pp=1.78, central_pp=0.00, acts_on="ADR -> GBV -> revenue",
         status="assumed",
         source="adrq3/J_adr-pricing-residual-and-card-v2.md: residual 3.70 (4Q25) -> "
                "4.38 (1Q26) -> 4.85 (2Q26), 1H26 mean 4.61 = the PERSISTENCE case; "
                "2023-25 mean 2.40 (IQR 2.04-2.93, full range 0.83-3.70) = the MEAN-"
                "REVERSION case; sd of quarterly residual changes 0.93pp. B3's own "
                "unidentified remainder is +2.83pp (fy27_adr_attribution_v2.csv), i.e. "
                "ALREADY at the mean-reversion end: upside to persistence +1.78pp, "
                "downside to the 0.83 floor -2.00pp. Unit-size mix +0.63pp is the 2Q26 "
                "29-market measurement (elasticity 0.23); the 2025 ANNUAL unit-size line "
                "is -0.25pp, a basis mismatch B3 caveat 4 half-concedes.",
         in_b3="ATTRIBUTION ONLY -- zero weight. B3's ADR line is pinned by the driver "
               "assumption 'every region +3.00% ex-FX'. To make this channel bite you "
               "must restate the +3.00%. B3's +2.83pp remainder means B3 is NOT exposed "
               "to residual mean reversion -- it assumes it. The unpriced risk is the "
               "OTHER way.",
         double_count_flag="NO if stated as a restatement of the +3.00%. But note the "
                           "ATTRIBUTION GAP: NEITHER ADR note names RNPL anywhere, while "
                           "the residual stepped +1.15pp across exactly the two quarters "
                           "management credits the bundle with ~3pts nights / ~4pts GBV. "
                           "The bedroom-count part of RNPL's larger-homes effect is "
                           "inside the +0.63pp unit-size line; the trade-up-at-same-"
                           "bedroom-count and lead-time-into-peak-dates parts are inside "
                           "the +2.83pp remainder, UNATTRIBUTED."),
    dict(id="e", channel="kernel recognition kappa_w -- longer booking-to-stay lag "
                         "argues for LOWER w",
         lo_pp=-2.34, hi_pp=0.00, central_pp=-0.02, acts_on="kappa_w",
         status="derived",
         source="B3 v2 kappa band -2.3316 / -1.1564 / +0.0117pp at w = 0.33 / 0.50 / 2/3 "
                "(fy27_kernel_band_v2.csv); LAG channel alone spans only "
                f"{lag_band:.3f}pp; MORNING_REPORT 07 line 13 'either the effective lag "
                "lengthened in the RNPL / hedging era or n = 3 is noise'",
         in_b3="THE BAND IS IN B3; the RNPL-based ARGUMENT for where to sit in it is not.",
         double_count_flag="YES with (c). And note: the honest size of this channel is "
                           f"~{lag_band:.2f}pp, not 2.34pp -- see block 3."),
    dict(id="f", channel="fee line x RNPL on unearned fees",
         lo_pp=0.36, hi_pp=0.90, central_pp=0.59, acts_on="revenue, outside computed GBV",
         status="assumed",
         source="fee-takerate.md restatement (+0.36 to +0.59pp at half weight vs the "
                "+0.90pp carried); unearned fees -0.9% y/y 2Q26 vs GBV +15.7%, restated "
                "+15.4% on the dated distortion series 0.9/3.8/16.2/16.5% "
                "(03_insider_mechanics.md 1.5)",
         in_b3="ASSUMED BLOCK -- explicitly OUTSIDE the computed $15,720-15,838M.",
         double_count_flag="YES, twice over. (i) fee-takerate also takes -0.62pp OFF FY27 "
                           "GBV growth and B3's GBV build does not carry it. (ii) the "
                           "single-fee leg is inside the bundle lap in (a). The unearned-"
                           "fee signal cannot separate the RNPL deferral leg from the "
                           "single-fee migration leg -- 03_insider_mechanics.md 1.5 calls "
                           "the fee leg UNIDENTIFIED."),
    dict(id="g", channel="take-rate timing residual (2Q26 13.26%, FY26 guided flat)",
         lo_pp=0.00, hi_pp=0.00, central_pp=0.00, acts_on="nothing -- take rate is an OUTPUT",
         status="measured",
         source="02_kpi_panel_quarterly.csv 2Q26 take_rate_pct 13.26; 08_THESIS_MAP.html "
                "'0 of 8 take-rate objects beat a seasonal naive'; take rate = revenue / "
                "GBV falls out of the identity",
         in_b3="NO, and correctly so.",
         double_count_flag="YES if quoted as a driver -- the take rate is revenue / GBV, "
                           "so any take-rate 'lever' added to a build that already models "
                           "revenue and GBV is counted twice. The 3Q26 >= 18.10% "
                           "pre-registration is a TEST of the fee mechanism, not an input."),
]
chan = pd.DataFrame(CH)
say(chan[["id", "channel", "lo_pp", "hi_pp", "central_pp", "status", "in_b3"]]
    .to_string(index=False))

vol = chan[chan.id.isin(["a", "b", "c"])]
say(f"\nVolume channels (a+b+c) sum ADDITIVELY to {vol.lo_pp.sum():+.2f}pp .. "
    f"{vol.hi_pp.sum():+.2f}pp (central {vol.central_pp.sum():+.2f}pp).")
say(f"  That would put FY27 nights at {gN + vol.lo_pp.sum():.2f}% .. {gN:.2f}%, i.e. BELOW")
say("  every published construction. The additive sum OVER-COUNTS and must not be quoted.")
say("\nTHE DEFENSIBLE FY27 NIGHTS RANGE is anchored on the three independent constructions:")
for lbl, v, st in (("B3 v2 / WS10 driver base (no lap, no RNPL term)", gN, "derived"),
                   ("PR #32, NA-only lap", 8.2, "derived, FITTED on 4 NA obs, branch-only"),
                   ("29-bridge FY27 walk (imports WS10 gross)", 9.2, "derived"),
                   ("PR #32, global lap", 6.4, "derived, FITTED, branch-only"),
                   ("Jessie plateau-plus-drag (lap 0 + cancel -0.90)", 6.52,
                    "derived, annual only, branch-only")):
    say(f"   {v:6.2f}%   {lbl:52s}  [{st}]")
say("  -> RNPL-SUPPORTED FY27 NIGHTS RANGE: +6.4% to +8.2%, and B3's +9.46% is ABOVE it.")
say("  -> The low end is reached by TWO independent constructions 0.12pp apart, which is")
say("     corroboration; but both are UNMERGED BRANCH artefacts and neither is registered.")

# ===========================================================================
# 5. PHASING -- FY27 quarterly path, B3 vs RNPL-aware, and the turns
# ===========================================================================
say("\n" + "=" * 78)
say("5. FY27 QUARTERLY PHASING AND THE MULTIPLE")
say("=" * 78)

grid = pd.read_csv(V1 / "l1_fy27_revenue_grid.csv")
grid = grid[grid.scenario == "driver_base"]

COMPS = {"2027Q1": 17.87, "2027Q2": 16.54, "2027Q3": 16.60, "2027Q4": 12.00}
COMPS_SRC = ("1Q26 2678/2272-1 = +17.87% and 2Q26 3608/3096-1 = +16.54% are PRINTED "
             "(02_kpi_panel_quarterly.csv); 3Q26 +16.6% is 10_regional_forecast.csv base "
             "scenario revenue_yoy_pct; 4Q26 +12.0% is the kernel's own 4Q26 at w = 2/3 "
             "(3111.2/2778-1). The kernel's 3Q26 at w = 2/3 is +17.32% (4804.0/4095-1) and "
             "the guide midpoint is +15.5% -- three different 3Q26 comps, stated not netted.")

# B3's own quarterly reported-revenue growth, at each w
ph = []
for _, r in grid.iterrows():
    w = r.kernel_w
    fy26q = {"2026Q1": 2678.0, "2026Q2": 3608.0,
             "2026Q3": r.rev_2026Q3, "2026Q4": r.rev_2026Q4}
    fy27q = {f"2027Q{i}": r[f"rev_2027Q{i}"] for i in range(1, 5)}
    for i in range(1, 5):
        q, q4 = f"2027Q{i}", f"2026Q{i}"
        ph.append(dict(kernel_w=w, quarter=q,
                       fy26_comp_musd=fy26q[q4], fy27_musd=fy27q[q],
                       rev_growth_pct=100 * (fy27q[q] / fy26q[q4] - 1),
                       fy26_comp_growth_pct=COMPS[q],
                       nights_yoy_pct=float(qpath.loc[qpath.quarter == q, "nights_yoy_pct"].iloc[0]),
                       adr_yoy_pct=float(qpath.loc[qpath.quarter == q, "adr_yoy_pct"].iloc[0]),
                       gbv_yoy_pct=float(qpath.loc[qpath.quarter == q, "gbv_yoy_pct"].iloc[0]),
                       status="derived",
                       source="l1_fy27_revenue_grid.csv scenario driver_base"))
phdf = pd.DataFrame(ph)
phdf["kappa_q_pp"] = phdf["rev_growth_pct"] - phdf["gbv_yoy_pct"]

for w in W_GRID:
    sub = phdf[np.isclose(phdf.kernel_w, w)]
    say(f"\n--- B3 driver_base quarterly path, w = {w:.3f}")
    say(sub[["quarter", "nights_yoy_pct", "adr_yoy_pct", "gbv_yoy_pct",
             "kappa_q_pp", "rev_growth_pct", "fy26_comp_growth_pct"]]
        .to_string(index=False, float_format=lambda v: f"{v:10.2f}"))

# RNPL-aware path.  The two legs have DIFFERENT phasing and must not be merged:
#  NA leg  -- US RNPL laps 3Q26, NA fee + cancellation redesign laps 4Q26, so by
#             1Q27 the NA lap is already fully in the FY26 base: PR #32 carries it
#             as a FLAT -0.98pp of total nights in every FY27 quarter.
#  ex-NA   -- 17 Feb 2026 worldwide (UK 18 Feb, AU/APAC 23 Feb, CA 4 Mar), so the
#             anniversary falls ~48% of the way through 1Q27: PARTIAL in 1Q27,
#             FULL from 2Q27.  The D note refutes PR #32's flat -1.75 from 1Q27 as
#             "too large in 1Q27 and about right from 2Q27".
NA_LEG_PP = -1.256          # B3 g_N +9.4558% -> PR #32 NA-only +8.2%
EXNA_LEG_PP = -1.800        # PR #32 NA-only +8.2% -> global +6.4%
EXNA_LOAD = {"2027Q1": 0.52, "2027Q2": 1.00, "2027Q3": 1.00, "2027Q4": 1.00}
LAP_LOAD_SRC = ("NA leg FLAT (PR #32 nights_quarterly_total.csv carries "
                "na_contribution_delta_pts = -0.98 in every FY27 quarter); ex-NA leg "
                "PARTIAL in 1Q27 at 0.52 of full (17 Feb 2026 worldwide go-live is ~48% "
                "through 1Q27; UK 18 Feb, AU/APAC 23 Feb, CA 4 Mar) and FULL from 2Q27, "
                "per research/notes/overnight2/D_rnpl-statement-ledger-and-cohort-"
                "scenarios.md, which refutes PR #32's flat -1.75 from 1Q27")

rn = []
for tag, na_on, exna_on in (("NA-only lap (to PR #32 +8.2%)", True, False),
                            ("global lap (to PR #32 +6.4%)", True, True)):
    scale = 4 / sum(EXNA_LOAD.values()) if exna_on else 1.0
    for i in range(1, 5):
        q = f"2027Q{i}"
        base = phdf[np.isclose(phdf.kernel_w, 2.0 / 3.0) & (phdf.quarter == q)].iloc[0]
        dn = (NA_LEG_PP if na_on else 0.0)
        dn += (EXNA_LEG_PP * EXNA_LOAD[q] * scale) if exna_on else 0.0
        n_new = base.nights_yoy_pct + dn
        gbv_new = ((1 + n_new / 100) * (1 + base.adr_yoy_pct / 100) - 1) * 100
        rn.append(dict(lap_case=tag, quarter=q,
                       nights_yoy_b3_pct=base.nights_yoy_pct,
                       lap_drag_pp=dn, nights_yoy_rnpl_pct=n_new,
                       adr_yoy_pct=base.adr_yoy_pct, gbv_yoy_rnpl_pct=gbv_new,
                       kappa_q_pp=base.kappa_q_pp,
                       rev_growth_rnpl_pct=gbv_new + base.kappa_q_pp,
                       rev_growth_b3_pct=base.rev_growth_pct,
                       fy26_comp_growth_pct=COMPS[q],
                       status="derived", source="B3 quarterly path + dated lap phasing"))
rndf = pd.DataFrame(rn)
for tag in rndf.lap_case.unique():
    sub = rndf[rndf.lap_case == tag]
    say(f"\n--- RNPL-AWARE path, {tag}, at w = 2/3")
    say(sub[["quarter", "nights_yoy_b3_pct", "lap_drag_pp", "nights_yoy_rnpl_pct",
             "adr_yoy_pct", "kappa_q_pp", "rev_growth_rnpl_pct", "rev_growth_b3_pct",
             "fy26_comp_growth_pct"]].to_string(index=False,
                                                float_format=lambda v: f"{v:9.2f}"))

# --- The Street FY27, phased like FY26.  FY26 quarterly revenue shares come from
# the kernel's own FY26 at w = 2/3 (1H printed, 2H kernel), which is the same base
# B3 divides by.  Proportional phasing gives the SAME growth in every quarter --
# that is the point: the Street's FY27 is a flat ~+11% line across four quarters
# whose comps are +17.9 / +16.5 / +16.6 / +12.0.
fy26q = {"2026Q1": 2678.0, "2026Q2": 3608.0,
         "2026Q3": float(grid[np.isclose(grid.kernel_w, 2 / 3)].rev_2026Q3.iloc[0]),
         "2026Q4": float(grid[np.isclose(grid.kernel_w, 2 / 3)].rev_2026Q4.iloc[0])}
fy26_tot = sum(fy26q.values())
st_rows = []
for lo_hi, tot in (("Street lo $15,740M", 15740.0), ("Street hi $15,790M", 15790.0)):
    for i in range(1, 5):
        q, q4 = f"2027Q{i}", f"2026Q{i}"
        implied = tot * fy26q[q4] / fy26_tot
        st_rows.append(dict(street_case=lo_hi, quarter=q, implied_musd=implied,
                            implied_growth_pct=100 * (implied / fy26q[q4] - 1),
                            fy26_comp_growth_pct=COMPS[q], status="derived",
                            source="Street FY27 total phased on the FY26 quarterly "
                                   "revenue shares at kernel w = 2/3"))
stdf = pd.DataFrame(st_rows)
say("\n--- THE STREET'S FY27, PHASED LIKE FY26")
say(stdf.to_string(index=False, float_format=lambda v: f"{v:10.2f}"))
say("  Proportional phasing is flat by construction: the Street's FY27 is ~+11% in")
say("  EVERY quarter, including 1Q27 against a +17.9% comp and 2Q27 against +16.5%.")

cmp_rows = []
for tag in rndf.lap_case.unique():
    for i in range(1, 5):
        q = f"2027Q{i}"
        ours = float(rndf[(rndf.lap_case == tag) & (rndf.quarter == q)]
                     .rev_growth_rnpl_pct.iloc[0])
        for sc in stdf.street_case.unique():
            st = float(stdf[(stdf.street_case == sc) & (stdf.quarter == q)]
                       .implied_growth_pct.iloc[0])
            cmp_rows.append(dict(lap_case=tag, street_case=sc, quarter=q,
                                 ours_pct=ours, street_pct=st, gap_pp=ours - st,
                                 status="derived"))
cmpdf = pd.DataFrame(cmp_rows)
say("\n--- RNPL-AWARE vs STREET-PHASED, by quarter (gap in pp)")
say(cmpdf.pivot_table(index="quarter", columns=["lap_case", "street_case"],
                      values="gap_pp").to_string(float_format=lambda v: f"{v:8.2f}"))

# --- Turns.  Street-implied FY27 GROWTH is each vendor's own FY27 / own FY26,
# per B3 v2 Table 3 -- never a ratio across vintages.
STREET_GROWTH_LO, STREET_GROWTH_HI = 11.322421, 11.631206   # fy27_street_edges_v2.csv
TURNS_PER_PP = 0.48
turn_rows = []
for tag, lo, hi in [
    ("B3 computed band, w 0.33 -> 2/3 (as published)", 9.179456, 11.522821),
    ("B3 at w = 2/3 + RNPL NA-only lap in N",
     11.522821 - 1.256 * (1 + gADR / 100), 11.522821 - 1.256 * (1 + gADR / 100)),
    ("B3 at w = 2/3 + RNPL global lap in N",
     11.522821 - 3.056 * (1 + gADR / 100), 11.522821 - 3.056 * (1 + gADR / 100)),
    ("B3 at w = 2/3 + RNPL lap band (global .. NA-only)",
     11.522821 - 3.056 * (1 + gADR / 100), 11.522821 - 1.256 * (1 + gADR / 100)),
]:
    for street, sname in ((STREET_GROWTH_LO, "Street-implied lo +11.32%"),
                          (STREET_GROWTH_HI, "Street-implied hi +11.63%")):
        turn_rows.append(dict(case=tag, our_lo_pct=lo, our_hi_pct=hi,
                              street_pct=street, street_name=sname,
                              edge_lo_pp=lo - street, edge_hi_pp=hi - street,
                              turns_lo=TURNS_PER_PP * (lo - street),
                              turns_hi=TURNS_PER_PP * (hi - street),
                              status="derived",
                              source="+0.48 turns per point of forward growth, applied ONCE "
                                     "(overnight/12_valuation-multiple-regime.md via "
                                     "OPTIMAL_MIX 4.5); street range from "
                                     "fy27_street_edges_v2.csv, vendor-stamped"))
turns = pd.DataFrame(turn_rows)
say("\nTURNS AT +0.48 PER POINT OF FORWARD GROWTH, APPLIED ONCE:")
say(turns[["case", "street_name", "edge_lo_pp", "edge_hi_pp", "turns_lo", "turns_hi"]]
    .to_string(index=False, float_format=lambda v: f"{v:9.3f}"))
say("\nB3's own benchmark: the w-indeterminacy is 2.343pp of growth, which B3 quotes")
say(f"as +/-1.12 turns (0.48 x {band_fixed:.3f} = {0.48 * band_fixed:.3f} turns of SPREAD;")
say("  B3 labels the full spread '+/-1.12', which is loose but is its published figure).")
say(f"  self-consistent re-fit of lambda:  {band_refit:.3f}pp = "
    f"{0.48 * band_refit:.3f} turns of spread.")
rnpl_spread = abs(-3.056 * (1 + gADR / 100) - (-1.256 * (1 + gADR / 100)))
say(f"  RNPL lap band (global vs NA-only): {rnpl_spread:.3f}pp = "
    f"{0.48 * rnpl_spread:.3f} turns of spread.")
say(f"  RNPL lap CENTRAL effect vs B3 as published (NA-only): "
    f"{-1.256 * (1 + gADR / 100):.3f}pp = {0.48 * -1.256 * (1 + gADR / 100):.3f} turns.")

# ===========================================================================
# write
# ===========================================================================
qpath.to_csv(OUT / "b3_n_quarterly_trace.csv", index=False)
lapdf.to_csv(OUT / "fy27_nights_lap_grid.csv", index=False)
kap.to_csv(OUT / "kappa_anatomy_and_lambda_refit.csv", index=False)
recdf.to_csv(OUT / "kernel_1h26_reconstruction_by_w.csv", index=False)
chan.to_csv(OUT / "rnpl_channel_ledger.csv", index=False)
phdf.to_csv(OUT / "fy27_quarterly_phasing_b3.csv", index=False)
rndf.to_csv(OUT / "fy27_quarterly_phasing_rnpl_aware.csv", index=False)
turns.to_csv(OUT / "turns_vs_street_and_w_band.csv", index=False)
pd.DataFrame([
    dict(key="fy26_comps_source", value=COMPS_SRC),
    dict(key="lap_load_source", value=LAP_LOAD_SRC),
    dict(key="read_only", value="no existing file was modified; harness/score.py not run"),
    dict(key="quote_rule", value="quote the FY27 band, never a point"),
]).to_csv(OUT / "notes_and_provenance.csv", index=False)
(OUT / "run_log.txt").write_text("\n".join(LOG) + "\n")
say(f"\nwrote 9 files to {OUT}")
