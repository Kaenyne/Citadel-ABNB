"""
WS-P (ADR v3, 11 Sep 2026), step 2: the 5 November score sheet.

Takes the printed 3Q26 numbers as command-line arguments and prints a scored table against the
pre-print record: the reviews-index nights band, card v3 (both variants), card v2, the H card, the
naive, the three FX estimators, the residual scenarios from K, the S harness extended by one
quarter (3Q26 added to the walk-forward, v3 ratio and jackknife recomputed on n 11 and n 10), the
4Q26 guide against N's two nights cases and D's pre-registered thresholds, and the bundle
checklist line.

Usage (every argument after --nights and --adr is optional):

  py -3.13 analysis/src/adrv3/P2_score_sheet.py --nights 146.8 --adr 177.17
      [--fx -0.43]                 disclosed ADR FX effect, pp (letter: "ex-FX ADR grew X%", the
                                   difference to reported is the FX effect)
      [--exfx 4]                   disclosed ex-FX ADR y/y, pp (whole points in the letter)
      [--regional NA=7 EMEA=8 LatAm=20 APAC=18]
                                   regional nights (or stays) y/y buckets, pct, if the letter gives them
      [--q4-nights-guide 8.1]      4Q26 nights guide, pct y/y (or mm if above 50; converted on 121.9mm)
      [--q4-revenue-guide 3134]    4Q26 revenue guide, $mm (midpoint of the range)
      [--bundle-figure 2.0]        management's quantified product-bundle nights contribution for
                                   3Q26, points; omit if not restated
      [--variant with_K]           which card v3 variant is the point (with_K default; without_K)
      [--out path]                 also write the sheet to this text file

Nothing here is an input to any forecast; the sheet scores the record that was fixed before the
print. Dry run (card's own point, format only):

  py -3.13 analysis/src/adrv3/P2_score_sheet.py --nights 146.8 --adr 177.17 --fx -0.43 --exfx 4
      --q4-nights-guide 8.1 --q4-revenue-guide 3134
      --out data/processed/adrv3/P/P2_score_sheet_dry_run.txt
"""
from __future__ import annotations

import argparse
import io
import os
import sys
from datetime import date

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import S1_scoring as S  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
P = lambda *a: os.path.join(ROOT, "data", "processed", *a)  # noqa: E731

# ----------------------------------------------------------------------------------
# the pre-print record (sourced from committed files; a few numbers quoted from notes)
# ----------------------------------------------------------------------------------
NIGHTS_BASE_3Q25 = 133.6           # H components (sourced)
NIGHTS_BASE_4Q25 = 121.9           # H components (sourced)
ADR_BASE_3Q25 = 171.29             # H components (sourced)
REVIEWS_BAND = (8.5, 11.0)         # docs/q3nowcast/SYNTHESIS.md, E reviews stays index (descriptive)
REVIEWS_POINT = (9.5, 10.0)        # same
TEAM_NIGHTS_BASELINE = 9.9         # bridge and PR #32 (team baseline, comparison)
Q4_CASES = {"B_global_lap_baseline": (8.12, 131.8), "A_team_baseline_top_of_band": (8.86, 132.7)}  # N memo 2
Q4_GUIDE_ARITH = (3050.0, 3100.0)  # research/notes/2026-09-10_h1-to-h2-bridge.md section 7, via N
TAKE_4Q26 = 0.1362                 # J3 same-quarter-prior-year take rate
FX_EST_3Q26 = {"eur": -1.12, "baskets": 0.26, "midpoint": -0.43}   # N1 card (H card values), fixed before the print
NAIVE_EXFX = 4.0                   # last disclosed ex-FX (2Q26 letter)
EXFX_CARD_V2 = 3.46
RESIDUAL_MIDPOINT_SPLIT = None     # set below: midpoint of mean reversion and last_q


def load_record():
    card = pd.read_csv(P("adrv3", "P", "adr_card_v3.csv"))
    terms = pd.read_csv(P("adrv3", "P", "P1_card_v3_terms.csv"))
    v2 = pd.read_csv(P("adrq3", "J", "adr_card_v2.csv"))
    hc = pd.read_csv(P("q3nowcast", "H", "adr_forecast_card.csv"))
    k4 = pd.read_csv(P("adrv3", "K", "K4_residual_nowcast.csv"))
    dthr = pd.read_csv(P("overnight2", "D", "D1_prereg_thresholds.csv"))
    return card, terms, v2, hc, k4, dthr


def fmt(x, nd=2, sign=True):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "n/a"
    return f"{x:+.{nd}f}" if sign else f"{x:.{nd}f}"


def main(argv=None):
    ap = argparse.ArgumentParser(description="5 November 2026 ADR / nights score sheet (WS-P)")
    ap.add_argument("--nights", type=float, required=True, help="3Q26 Nights and Seats Booked, millions")
    ap.add_argument("--adr", type=float, required=True, help="3Q26 reported ADR, dollars")
    ap.add_argument("--fx", type=float, default=None, help="disclosed ADR FX effect, pp")
    ap.add_argument("--exfx", type=float, default=None, help="disclosed ex-FX ADR y/y, pp (whole points)")
    ap.add_argument("--regional", nargs="*", default=None, help="regional nights y/y buckets, e.g. NA=7 EMEA=8 LatAm=20 APAC=18")
    ap.add_argument("--q4-nights-guide", type=float, default=None, help="4Q26 nights guide, pct y/y (or mm)")
    ap.add_argument("--q4-revenue-guide", type=float, default=None, help="4Q26 revenue guide, $mm")
    ap.add_argument("--bundle-figure", type=float, default=None, help="restated bundle nights contribution for 3Q26, points")
    ap.add_argument("--variant", choices=["with_K", "without_K"], default="with_K")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    card, terms, v2, hc, k4, dthr = load_record()
    buf = io.StringIO()
    out = lambda *s: print(*s, file=buf)  # noqa: E731
    var = {"with_K": "v3_with_K", "without_K": "v3_without_K"}[a.variant]
    other = {"with_K": "v3_without_K", "without_K": "v3_with_K"}[a.variant]
    c3 = card[(card.quarter == "3Q26") & (card.fx_estimator == "midpoint")].set_index("variant")
    v2_3 = v2[(v2.quarter == "3Q26") & (v2.fx_estimator == "midpoint")].iloc[0]
    hc_3 = hc[(hc.quarter == "3Q26") & (hc.route == "headline_mean_of_routes") & (hc.fx_estimator == "midpoint")].iloc[0]
    t3 = terms[(terms.quarter == "3Q26") & (terms.variant == var)].set_index("term")
    mix_terms = ["geographic_mix", "unit_size_party", "length_of_stay_mix", "new_business_seats", "interaction"]
    mix_sum = float(t3.loc[mix_terms, "point_pp"].sum())
    k_line = float(t3.loc["fee_migration_mechanics_K", "point_pp"]) if "fee_migration_mechanics_K" in t3.index else 0.0

    out(f"5 NOVEMBER 2026 SCORE SHEET, 3Q26 print against the pre-print record (WS-P, generated {date.today().isoformat()})")
    out("Every row: printed value | record value | difference | verdict. Record values were fixed before the print; nothing here feeds a forecast.")
    out("=" * 132)

    # 1. nights
    n_yoy = 100 * (a.nights / NIGHTS_BASE_3Q25 - 1)
    lo, hi = REVIEWS_BAND
    pos = "inside" if lo <= n_yoy <= hi else ("below" if n_yoy < lo else "above")
    out("\n1. NIGHTS (3Q26 Nights and Seats Booked, y/y on the 3Q25 base of 133.6mm)")
    out(f"   printed {a.nights:.1f}mm = {n_yoy:+.2f}% y/y")
    out(f"   reviews-index band {lo:.1f} to {hi:.1f} (point {REVIEWS_POINT[0]:.1f} to {REVIEWS_POINT[1]:.1f}): print is {pos} the band, {n_yoy - (lo + hi) / 2:+.2f} pp from its centre")
    out(f"   team baseline {TEAM_NIGHTS_BASELINE:.1f}% (146.8mm): print is {n_yoy - TEAM_NIGHTS_BASELINE:+.2f} pp, {a.nights - 146.8:+.1f}mm from baseline")
    d = dthr[dthr.metric.str.startswith("3Q26 reported Nights")].iloc[0]
    n_verdict = "supports the RNPL drag hypothesis (D threshold: at or below 8.5%)" if n_yoy <= 8.5 else (
        "weakens the drag hypothesis (D threshold: at or above 10.3%)" if n_yoy >= 10.3 else "inconclusive on the drag hypothesis (D band 8.6 to 10.2%)")
    out(f"   D pre-registered thresholds: {n_verdict}")

    # 2. reported ADR
    r_yoy = 100 * (a.adr / ADR_BASE_3Q25 - 1)
    out("\n2. REPORTED ADR (3Q26, y/y on 3Q25 $171.29)")
    out(f"   printed ${a.adr:.2f} = {r_yoy:+.2f}% y/y")
    rows = [
        (f"card v3 point ({a.variant}), midpoint FX", c3.at[var, "adr_reported_yoy_pp"], c3.at[var, "adr_reported_central_lo_pp"], c3.at[var, "adr_reported_central_hi_pp"], c3.at[var, "adr_reported_wide_lo_pp"], c3.at[var, "adr_reported_wide_hi_pp"]),
        (f"card v3 ({other.replace('v3_', '')}), midpoint FX", c3.at[other, "adr_reported_yoy_pp"], c3.at[other, "adr_reported_central_lo_pp"], c3.at[other, "adr_reported_central_hi_pp"], c3.at[other, "adr_reported_wide_lo_pp"], c3.at[other, "adr_reported_wide_hi_pp"]),
        ("card v2 (J3, persistence), midpoint FX", v2_3.adr_reported_yoy_pp, v2_3.adr_reported_central_lo_pp, v2_3.adr_reported_central_hi_pp, v2_3.adr_reported_wide_lo_pp, v2_3.adr_reported_wide_hi_pp),
        ("H card headline, midpoint FX", hc_3.adr_reported_yoy_pp, hc_3.adr_reported_central_lo_pp, hc_3.adr_reported_central_hi_pp, hc_3.adr_reported_wide_lo_pp, hc_3.adr_reported_wide_hi_pp),
        ("naive: last disclosed ex-FX 4 + midpoint FX -0.43", NAIVE_EXFX + FX_EST_3Q26["midpoint"], np.nan, np.nan, np.nan, np.nan),
    ]
    out(f"   {'record':52s} {'point':>8s} {'error':>8s} {'central band':>16s} {'wide band':>16s}  verdict")
    for name, pt, clo, chi, wlo, whi in rows:
        err = r_yoy - pt
        if np.isfinite(clo):
            v = "inside central" if clo <= r_yoy <= chi else ("inside wide" if wlo <= r_yoy <= whi else "OUTSIDE wide")
            out(f"   {name:52s} {pt:+8.2f} {err:+8.2f} {clo:+7.2f} to {chi:+6.2f} {wlo:+7.2f} to {whi:+6.2f}  {v}")
        else:
            out(f"   {name:52s} {pt:+8.2f} {err:+8.2f} {'':>16s} {'':>16s}  {'model beat naive' if abs(r_yoy - c3.at[var, 'adr_reported_yoy_pp']) < abs(err) else 'naive beat model'} on the dollar target")
    out(f"   dollars: card v3 ({a.variant}) ${c3.at[var, 'adr_usd_point']:.2f} (central ${c3.at[var, 'adr_usd_central_lo']:.2f} to ${c3.at[var, 'adr_usd_central_hi']:.2f}); card v2 ${v2_3.adr_usd_point:.2f}; H card ${hc_3.adr_usd_point:.2f}; print ${a.adr:.2f}")

    # 3. FX
    out("\n3. FX EFFECT (disclosed ADR FX effect against the three estimators fixed before the print; N named the midpoint)")
    if a.fx is not None:
        errs = {k: a.fx - v for k, v in FX_EST_3Q26.items()}
        best = min(errs, key=lambda k: abs(errs[k]))
        for k, v in FX_EST_3Q26.items():
            out(f"   {k:10s} estimate {v:+.2f} pp | disclosed {a.fx:+.2f} | error {errs[k]:+.2f} pp{'  <- closest' if k == best else ''}")
        out(f"   verdict: {best} closest this quarter; one more point in a 17-quarter sample (N: not by itself a reason to change the midpoint recommendation)")
    else:
        out("   FX effect not supplied (--fx); the letter usually states ex-FX ADR growth, from which FX = reported minus ex-FX")

    # 4. ex-FX and target 1
    out("\n4. EX-FX ADR (3Q26)")
    if a.exfx is not None:
        exfx, exfx_src = a.exfx, "disclosed"
    elif a.fx is not None:
        exfx, exfx_src = r_yoy - a.fx, "solved: reported minus disclosed FX"
    else:
        exfx, exfx_src = r_yoy - FX_EST_3Q26["midpoint"], "ESTIMATED: reported minus the midpoint FX estimate (-0.43); supply --exfx or --fx for the real number"
    out(f"   ex-FX {exfx:+.2f} pp ({exfx_src})")
    ex_rows = [(f"card v3 ({a.variant})", c3.at[var, "adr_exfx_yoy_pp"]), (f"card v3 ({other.replace('v3_', '')})", c3.at[other, "adr_exfx_yoy_pp"]),
               ("card v2 (J3), about +3.5", EXFX_CARD_V2), ("naive: last disclosed", NAIVE_EXFX)]
    for name, pt in ex_rows:
        out(f"   {name:40s} record {pt:+.2f} | error {exfx - pt:+.2f} pp")
    if a.exfx is not None:
        m_round = S.round_half_away(c3.at[var, "adr_exfx_yoy_pp"])
        out(f"   target 1 (integer-fair): model rounds to {m_round:+.0f}, naive {NAIVE_EXFX:+.0f}, disclosed {a.exfx:+.0f}: "
            f"{'model exact' if m_round == a.exfx else 'model off by ' + fmt(m_round - a.exfx, 0)}; {'naive exact' if NAIVE_EXFX == a.exfx else 'naive off by ' + fmt(NAIVE_EXFX - a.exfx, 0)}")

    # 5. residual, solved the H way
    resid = exfx - mix_sum
    out("\n5. PRICING RESIDUAL (solved the H way: ex-FX minus the measured mix terms and fills used in the card)")
    out(f"   mix and fills in the card: geo {t3.at['geographic_mix', 'point_pp']:+.2f}, size {t3.at['unit_size_party', 'point_pp']:+.2f}, LOS {t3.at['length_of_stay_mix', 'point_pp']:+.2f}, "
        f"new business {t3.at['new_business_seats', 'point_pp']:+.2f}, interaction {t3.at['interaction', 'point_pp']:+.2f} = {mix_sum:+.2f}")
    out(f"   solved residual {resid:+.2f} pp" + (" (carries the +/- 0.5 pp rounding of a whole-point ex-FX disclosure)" if a.exfx is not None and float(a.exfx).is_integer() else ""))
    scen = {
        "last_q (v3 rule, 2Q26 value)": float(k4[(k4.scenario == "last_q (v3 rule)") & (k4.quarter == "3Q26")].residual_pp.iloc[0]),
        "K rule: last_q + 0.007 x share change": float(k4[(k4.scenario.str.startswith("cohort mechanics, central")) & (k4.quarter == "3Q26")].residual_pp.iloc[0]),
        "persistence (v2 rule)": float(k4[(k4.scenario == "persistence (v2 rule)") & (k4.quarter == "3Q26")].residual_pp.iloc[0]),
        "AR(1) on the residual": float(k4[(k4.scenario == "AR(1) on the residual") & (k4.quarter == "3Q26")].residual_pp.iloc[0]),
        "lap + tranche 2, central": float(k4[(k4.scenario == "lap + tranche 2, central") & (k4.quarter == "3Q26")].residual_pp.iloc[0]),
        "lap only, residual steps": float(k4[(k4.scenario == "lap only, residual steps") & (k4.quarter == "3Q26")].residual_pp.iloc[0]),
        "mean reversion (2023-25 mean)": float(k4[(k4.scenario == "mean reversion") & (k4.quarter == "3Q26")].residual_pp.iloc[0]),
    }
    nearest = min(scen, key=lambda k: abs(scen[k] - resid))
    for name, v in scen.items():
        out(f"   {name:40s} {v:+.2f} | error {resid - v:+.2f}{'  <- nearest' if name == nearest else ''}")
    split = 0.5 * (scen["mean reversion (2023-25 mean)"] + scen["last_q (v3 rule, 2Q26 value)"])
    case = "PERSISTENCE case" if resid >= split else "MEAN-REVERSION case"
    out(f"   case: {case} (split at {split:.2f}, halfway between mean reversion {scen['mean reversion (2023-25 mean)']:.2f} and last_q {scen['last_q (v3 rule, 2Q26 value)']:.2f})")
    if resid >= 4.5:
        out("   K reading: near 5.0, the rule stands and the reprice question stays open; 4Q26 residual band stays 3.1 to 5.2 around 4.85")
    elif 3.6 <= resid < 4.5:
        out("   K reading: 3.9 to 4.1 is the lap arithmetic; the 4Q26 residual should move to the 3.1 to 3.8 band (lap only to disclosed-bundle lap)")
    else:
        out("   K reading: below the lap arithmetic; J's mean-reversion downside is in play; the last_q rule is retired for 4Q26 and the 4Q26 residual should be re-set from this print")

    # 6. regional buckets
    out("\n6. REGIONAL NIGHTS BUCKETS (if given) against the split I used for the geo-mix term")
    e_split = {"NA": 6.9, "EMEA": 0.9, "LatAm": 27.5, "APAC": 10.0}   # I3, E_aug vintage-matched stays split (measured)
    c_split = {"NA": 6.7, "EMEA": 5.9, "LatAm": 19.5, "APAC": 17.1}   # WS-C index model (modelled)
    if a.regional:
        reg = {}
        for tok in a.regional:
            k, v = tok.split("=")
            reg[k.strip()] = float(v)
        for k in ("NA", "EMEA", "LatAm", "APAC"):
            if k in reg:
                out(f"   {k:6s} printed {reg[k]:+.1f}% | I / E split {e_split[k]:+.1f} | WS-C {c_split[k]:+.1f} | error vs E {reg[k] - e_split[k]:+.1f} pp")
        slow = [k for k in ("LatAm", "APAC") if k in reg and reg[k] < e_split[k]]
        out("   reading: " + ("LatAm / APAC printed slower than E's split, so the measured geo drag (-1.43) was too large and the residual solved above is overstated by the same amount"
                             if slow else "expansion regions at or above E's split, so the -1.43 geo drag was not too large; the solved residual stands"))
        out("   (the geo term is not recomputed here: it needs anchored regional ADR and 3Q25 shares; re-run I3 with the printed split if a revised term is wanted)")
    else:
        out(f"   not supplied (--regional); the record's split was E: NA {e_split['NA']:+.1f}, EMEA {e_split['EMEA']:+.1f}, LatAm {e_split['LatAm']:+.1f}, APAC {e_split['APAC']:+.1f} (geo term -1.43)")

    # 7. walk-forward extended by one quarter
    out("\n7. WALK-FORWARD EXTENDED BY ONE QUARTER (S harness, target 2: reported dollar ADR y/y; 3Q26 added; model = card ex-FX + the same FX estimator as the naive)")
    out("   historical rows are the harness paths (measured mix, S prior-year fills, residual rule strictly before t); the 3Q26 row is the card's own ex-FX (J3 fills)")
    paths = pd.read_csv(P("adrv3", "P", "P1_card_v3_backtest_paths.csv"))
    mcol = {"with_K": "v3_point_last_q_plus_K_line_measured_mix", "without_K": "v3_last_q_measured_mix"}
    d = S.load_inputs()
    rep_hist = d["reported_yoy"]
    ext_rows = []
    for est in ("eur", "baskets", "midpoint"):
        tf = paths[(paths.target == "t2_reported_usd_yoy") & (paths.fx_estimator == est)].set_index("quarter")
        # extend the reported series for the AR(1) benchmark and the prior-year row
        rep_ext = rep_hist.copy()
        rep_ext["3Q26"] = r_yoy
        ar1 = S._ar1_expanding(rep_ext, "3Q26")
        new = {"actual": r_yoy, "naive": NAIVE_EXFX + FX_EST_3Q26[est], "prior_year": float(rep_hist["3Q25"]), "ar1": ar1}
        for vname, col in mcol.items():
            new[col] = float(c3.at[{"with_K": "v3_with_K", "without_K": "v3_without_K"}[vname], "adr_exfx_yoy_pp"]) + FX_EST_3Q26[est]
        tf2 = pd.concat([tf[["actual", "naive", "prior_year", "ar1"] + list(mcol.values())], pd.DataFrame([new], index=["3Q26"])])
        for wname, first in (("1Q24-3Q26", "1Q24"), ("2Q24-3Q26", "2Q24")):
            idx = [q for q in tf2.index if S.QI[q] >= S.QI[first]]
            w = tf2.loc[idx]
            for vname, col in mcol.items():
                blk = S._score_block(w[col], w)
                e_new = new[col] - r_yoy
                ext_rows.append({"variant": vname, "fx_estimator": est, "window": wname, "n": blk["n"], "rmse_pp": blk["rmse_pp"], "rmse_naive_pp": blk["rmse_naive_pp"],
                                 "ratio_vs_naive": blk["ratio_vs_naive"], "jk_min": blk["jackknife_ratio_min"], "jk_max": blk["jackknife_ratio_max"],
                                 "jk_below_1": blk["jackknife_below_1"], "err_3q26_model_pp": e_new, "err_3q26_naive_pp": new["naive"] - r_yoy})
    ext = pd.DataFrame(ext_rows)
    ref = pd.read_csv(P("adrv3", "P", "P1_card_v3_backtest.csv"))
    for vname, col in mcol.items():
        out(f"   variant {vname}:")
        out(f"   {'estimator':10s} {'window':11s} {'n':>3s} {'ratio':>7s} {'was':>7s} {'jk min':>7s} {'jk max':>7s} {'was':>7s} {'below 1':>8s} {'3Q26 err model':>15s} {'naive':>7s}")
        for _, r in ext[ext.variant == vname].iterrows():
            was = ref[(ref.model == col) & (ref.target == "t2_reported_usd_yoy") & (ref.fx_estimator == r.fx_estimator) & (ref.window == r.window.replace("3Q26", "2Q26"))].iloc[0]
            out(f"   {r.fx_estimator:10s} {r.window:11s} {r.n:3d} {r.ratio_vs_naive:7.3f} {was.ratio_vs_naive:7.3f} {r.jk_min:7.3f} {r.jk_max:7.3f} {was.jackknife_ratio_max:7.3f} {r.jk_below_1:5d}/{r.n:<2d} {r.err_3q26_model_pp:+15.2f} {r.err_3q26_naive_pp:+7.2f}")
        crit = ext[(ext.variant == vname) & (ext.fx_estimator.isin(["eur", "baskets"]))]
        ok = bool((crit.ratio_vs_naive < 1).all() and (crit.jk_max < 1).all())
        out(f"   pre-registered v3 criterion on n 11 / n 10 (ratio < 1 and jackknife max < 1 under eur and baskets, both windows): {'PASS' if ok else 'FAIL'} "
            f"({int(((crit.ratio_vs_naive < 1) & (crit.jk_max < 1)).sum())} of 4 checks); binding jackknife max {crit.jk_max.max():.3f}")

    # 8. 4Q26 guide
    out("\n8. 4Q26 GUIDE against N's two nights cases and D's pre-registered thresholds")
    if a.q4_nights_guide is not None:
        g = a.q4_nights_guide
        g_pct = 100 * (g / NIGHTS_BASE_4Q25 - 1) if g > 50 else g
        g_mm = g if g > 50 else NIGHTS_BASE_4Q25 * (1 + g / 100)
        d4 = "supports the global-lap / drag reading (D: 7.5% or below)" if g_pct <= 7.5 else ("weakens it (D: 9.5% or above)" if g_pct >= 9.5 else "inconclusive (D band 7.6 to 9.4%; both N cases sit inside it)")
        near = min(Q4_CASES, key=lambda k: abs(Q4_CASES[k][0] - g_pct))
        out(f"   nights guide {g_pct:+.2f}% ({g_mm:.1f}mm) | case B baseline {Q4_CASES['B_global_lap_baseline'][0]:+.2f}% ({Q4_CASES['B_global_lap_baseline'][1]}mm) | case A top of band {Q4_CASES['A_team_baseline_top_of_band'][0]:+.2f}% ({Q4_CASES['A_team_baseline_top_of_band'][1]}mm) | nearer case {near}")
        out(f"   D thresholds: {d4}")
    else:
        out("   nights guide not supplied (--q4-nights-guide)")
    c4 = card[(card.quarter == "4Q26") & (card.fx_estimator == "midpoint") & (card.variant == var)].set_index("nights_case")
    if a.q4_revenue_guide is not None:
        rg = a.q4_revenue_guide
        out(f"   revenue guide ${rg:,.0f}mm | anticipated guide arithmetic ${Q4_GUIDE_ARITH[0]:,.0f} to ${Q4_GUIDE_ARITH[1]:,.0f}mm | "
            f"card v3 ({a.variant}) revenue at case B ${c4.at['N_case_B_global_lap_baseline', 'revenue_musd_same_q_take']:,.0f}mm, at case A ${c4.at['N_case_A_team_baseline_top_of_band', 'revenue_musd_same_q_take']:,.0f}mm (same-quarter take {TAKE_4Q26})")
        if a.q4_nights_guide is not None:
            adr_impl = rg / TAKE_4Q26 / g_mm
            out(f"   ADR implied by the guide at its own nights and the same-quarter take: ${adr_impl:.2f} = {100 * (adr_impl / 167.51 - 1):+.2f}% y/y, against card v3 4Q26 ${c4.at['N_case_B_global_lap_baseline', 'adr_usd_point']:.2f} ({c4.at['N_case_B_global_lap_baseline', 'adr_reported_yoy_pp']:+.2f}%)")
    else:
        out("   revenue guide not supplied (--q4-revenue-guide)")

    # 9. bundle checklist
    out("\n9. CHECKLIST: did management restate the product-bundle contribution figure for 3Q26?")
    out("   record: 4Q25 'over 200 bp nights, roughly 300 bp GBV'; 1Q26 'about 3 points nights, 4 points GBV'; 2Q26 none (D ledger D014, D032)")
    if a.bundle_figure is not None:
        b = a.bundle_figure
        v = ("consistent with the ex-NA anniversary already biting: N case B (global lap) holds" if b <= 1.5 else
             "consistent with the bundle still adding regardless of geography: favours N case A (NA-only lap), move the 4Q26 nights point toward 8.9%" if b >= 2.5 else
             "between the D thresholds (1.5 and 2.5 points): inconclusive, keep case B with case A as the top of the band")
        out(f"   restated: YES, {b:.1f} points of nights. {v}")
    else:
        out("   restated: NO (or not supplied via --bundle-figure). D reads a missing figure as consistent with the anniversary arriving; case B stays on its sourced dates. "
            "If a qualitative update only was given, that is what 2Q26 gave: inconclusive.")
    out("   also check: RNPL GBV share for 3Q26 (D: flat or down vs 2Q26 with nights decelerating supports the drag; at or above 25% with nights at or above 10% weakens it); "
        "any migrated-share or take-rate-lift figure for the fee migration updates K1 directly")

    out("\n" + "=" * 132)
    out("Sources: adr_card_v3.csv and P1_card_v3_terms.csv (P), adr_card_v2.csv (J3), adr_forecast_card.csv (H), K4_residual_nowcast.csv (K), N1 / N2 (N), "
        "D1_prereg_thresholds.csv (D), docs/q3nowcast/SYNTHESIS.md (reviews band), S1_scoring (harness). Labels: printed = sourced at the print; record = as labelled in the source file.")
    text = buf.getvalue()
    print(text)
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print("written:", a.out)


if __name__ == "__main__":
    main()
