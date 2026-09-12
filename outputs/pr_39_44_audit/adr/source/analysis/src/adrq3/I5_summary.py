"""I5. One-row-per-term summary of the three measured mix terms for 3Q26, for workstream J.

Writes data/processed/adrq3/I/I_mix_terms_3q26.csv with columns
  term, 3Q26_to_date_value, unit, adr_contribution_pp, lo, hi, basis, source_file
plus comparison rows (2Q26 and 3Q25 on the identical construction, the H card and WS-C cells).
Measured 3Q26 rows carry quarter "3Q26" exactly (J3 reads only those, via point_pp/lo/hi);
comparison rows carry other labels so J3 ignores them.

Selection rules (fixed before the outputs were read):
  unit size      point = 3q26_to_date, vintage-matched, fixed-2019 weights, global booked-capacity y/y
                 x 0.592; lo/hi = min/max over {vmatch, within} x {fixed_2019, equal, reviews} x
                 {3q26_to_date, jul26} constructions, widened to the market bootstrap 5-95 band and
                 the listed-basis elasticity (0.577)
  LOS mix        point = median of the eight 2026 global 10-K-weighted rows (Jun and Aug pairs x
                 lead-matched and calendar windows x occupancy-weighted and unweighted); lo/hi = min/max over windows x weighting
  geographic mix point = E vintage-matched review-weighted split, g = 0; lo/hi = min/max over
                 {E vmatch cw, E vmatch eq} x {g zero, g 2Q26 disclosed}
Run: py -3.13 analysis/src/adrq3/I5_summary.py
"""
from pathlib import Path
import numpy as np, pandas as pd

WT = Path(__file__).resolve().parents[3]
OUT = WT / "data/processed/adrq3/I"


def main():
    rows = []
    # ---- unit size -------------------------------------------------------------------------
    ps = pd.read_csv(OUT / "I1_party_size_windows.csv")
    g = ps[ps.region.eq("global")]
    pt = g[g.window.eq("3q26_to_date") & g.construction.eq("vmatch") & g.weighting.eq("fixed_2019")].iloc[0]
    alt = g[g.window.isin(["3q26_to_date", "jul26"]) & g.construction.isin(["vmatch", "within"])]
    lo = min(alt.size_term_pp.min(), pt.size_term_bs_lo_pp, pt.size_term_listed_basis_pp)
    hi = max(alt.size_term_pp.max(), pt.size_term_bs_hi_pp, pt.size_term_pp)
    rows.append(dict(term="unit_size", quarter="3Q26", **{"3Q26_to_date_value": pt.accommodates_mean_yoy_pct},
                     unit="booked capacity (accommodates per reviewed stay) y/y, log pct, fixed-2019 weights, 123 markets",
                     adr_contribution_pp=pt.size_term_pp, lo=lo, hi=hi,
                     basis=f"measured: reviews dated {pt.win_start}..{pt.win_end} in the Aug-2026 dumps vs the same window 364 d earlier in each market's 2025 dump; "
                           f"x 0.592 (hedonic 0.399 + 0.140 x 1.374); {int(pt.n_markets)} markets, {int(pt.reviews_cur):,} reviews; band = constructions x weightings x windows, market bootstrap, listed-basis coefficient",
                     evidence_status="measured; level term, not validated as a timing signal (r -0.17 vs ex-FX ADR, walk-forward loses to naive)",
                     source_file="I1_party_size_windows.csv"))
    for w, cons, lab in [("2q26", "vmatch", "2Q26"), ("3q25_to_date", "oldvintage", "3Q25_to_date"), ("3q25_full", "within", "3Q25_full")]:
        s = g[g.window.eq(w) & g.construction.eq(cons) & g.weighting.eq("fixed_2019")]
        if len(s):
            s = s.iloc[0]
            rows.append(dict(term="unit_size", quarter=lab, **{"3Q26_to_date_value": s.accommodates_mean_yoy_pct},
                             unit="booked capacity y/y, log pct", adr_contribution_pp=s.size_term_pp, lo=s.size_term_bs_lo_pp, hi=s.size_term_bs_hi_pp,
                             basis=f"comparison column, identical construction ({cons}, {s.win_start}..{s.win_end}), {int(s.n_markets)} markets",
                             evidence_status="measured", source_file="I1_party_size_windows.csv"))
    rows.append(dict(term="unit_size", quarter="3Q26 (H card)", **{"3Q26_to_date_value": 1.25}, unit="booked capacity y/y pct (13 base case)",
                     adr_contribution_pp=0.74, lo=0.0, hi=0.98, basis="comparison column: H card / 13_party_size_adr_forecast base", evidence_status="assumed (trailing 8q)",
                     source_file="data/processed/q3nowcast/H/adr_forecast_card.csv"))

    # ---- LOS -------------------------------------------------------------------------------
    lt = pd.read_csv(OUT / "I2_los_term.csv")
    gl = lt[lt.region.eq("global_10k_weighted")]
    g26 = gl[gl.year.eq(2026)]
    occ = g26[g26.weighting.eq("occupancy_weighted")]
    pt = float(g26.los_mix_pp.median())  # median over the eight 2026 global rows (2 pairs x 2 windows x 2 weightings)
    d28 = float(occ.d_share_ge28_pp.median())
    rows.append(dict(term="los_mix", quarter="3Q26", **{"3Q26_to_date_value": d28},
                     unit="change in 28+ share of blocked-run nights, pp y/y, same stay window and lead, occupancy-weighted, global 10-K weights",
                     adr_contribution_pp=pt, lo=float(g26.los_mix_pp.min()), hi=float(g26.los_mix_pp.max()),
                     basis=f"measured on blocked runs (NOT bookings): Jun/Aug-2026 calendars vs each market's 2025 vintage 364 d earlier, {int(occ.n_markets.max())} markets ex NYC/LA; "
                           f"ratios 14a (7-27n 0.966, 28+ 0.852); band = windows (lead-matched, calendar Q3, calendar Sep) x weighting",
                     evidence_status="measured but unvalidated (no quarterly history of the same construction; 14b's disclosure-based term to 4Q25 is +0.2 to +0.45)",
                     source_file="I2_los_term.csv"))
    g25 = gl[gl.year.eq(2025)]
    if len(g25):
        o25 = g25[g25.weighting.eq("occupancy_weighted")]
        rows.append(dict(term="los_mix", quarter="3Q25 (2025 vs 2024, 4 markets)", **{"3Q26_to_date_value": float(o25.d_share_ge28_pp.median()) if len(o25) else np.nan},
                         unit="change in 28+ share, pp", adr_contribution_pp=float(o25.los_mix_pp.median()) if len(o25) else np.nan,
                         lo=float(g25.los_mix_pp.min()), hi=float(g25.los_mix_pp.max()),
                         basis="comparison column: same construction on the 2025 Jun vintages vs 2024 (Austin, Nashville, Paris, Rome only; regions missing so no 10-K roll-up unless all four regions present)",
                         evidence_status="measured, four markets", source_file="I2_los_term.csv"))
    rows.append(dict(term="los_mix", quarter="3Q26 (H card)", **{"3Q26_to_date_value": -2.0}, unit="d(28+ share) pp, assumed",
                     adr_contribution_pp=0.30, lo=0.0, hi=0.45, basis="comparison column: H card / 14 synthesis base", evidence_status="assumed",
                     source_file="data/processed/q3nowcast/H/adr_forecast_card.csv"))

    # ---- geographic mix ---------------------------------------------------------------------
    gm = pd.read_csv(OUT / "I3_geo_mix_3q26.csv")
    e = gm[gm.growth_source.isin(["E_vmatch_cw", "E_vmatch_eq"])]
    pt = e[e.growth_source.eq("E_vmatch_cw") & e.g_case.eq("g_zero")].iloc[0]
    rows.append(dict(term="geo_mix", quarter="3Q26",
                     **{"3Q26_to_date_value": f"NA {pt.nights_yoy_na_pct:+.1f} / EMEA {pt.nights_yoy_emea_pct:+.1f} / LatAm {pt.nights_yoy_latam_pct:+.1f} / APAC {pt.nights_yoy_apac_pct:+.1f}"},
                     unit="regional stays y/y pct (E vintage-matched, review-weighted) applied to 3Q25 nights shares and anchored regional ADR",
                     adr_contribution_pp=pt.geo_mix_pp, lo=float(e.geo_mix_pp.min()), hi=float(e.geo_mix_pp.max()),
                     basis="measured split (E_aug) x 07/H method; band = review- vs equal-weighted split x regional ex-FX ADR growth zero vs 2Q26 carried",
                     evidence_status="measured; the E-projected shares reproduce H's disclosed-share term only loosely (RMSE 0.4-0.7 pp, r 0.4, n 10); the term itself does not beat naive on ex-FX ADR",
                     source_file="I3_geo_mix_3q26.csv"))
    for src, lab in [("WSC_index_model", "WS-C index model"), ("WS10_base", "WS10 base cells"), ("disclosed_2Q26_flat", "2Q26 letter buckets flat")]:
        s = gm[gm.growth_source.eq(src) & gm.g_case.eq("g_zero")].iloc[0]
        rows.append(dict(term="geo_mix", quarter=f"3Q26 ({lab})", **{"3Q26_to_date_value": f"NA {s.nights_yoy_na_pct:+.1f} / EMEA {s.nights_yoy_emea_pct:+.1f} / LatAm {s.nights_yoy_latam_pct:+.1f} / APAC {s.nights_yoy_apac_pct:+.1f}"},
                         unit="regional nights y/y pct", adr_contribution_pp=s.geo_mix_pp, lo=np.nan, hi=np.nan,
                         basis="comparison column, same arithmetic on the modelled/assumed split", evidence_status="modelled" if "WS" in src else "assumed",
                         source_file="I3_geo_mix_3q26.csv"))
    rows.append(dict(term="geo_mix", quarter="3Q26 (H card)", **{"3Q26_to_date_value": ""}, unit="", adr_contribution_pp=-1.19, lo=-1.64, hi=-1.04,
                     basis="comparison column: H card (WS-C C5, 10-K FY25 shares)", evidence_status="modelled", source_file="data/processed/q3nowcast/H/adr_forecast_card.csv"))

    df = pd.DataFrame(rows)
    df["point_pp"] = df["adr_contribution_pp"]  # alias J3 reads (it looks for point_pp; rows with quarter exactly "3Q26" are the measured ones)
    df = df[["term", "quarter", "3Q26_to_date_value", "unit", "adr_contribution_pp", "point_pp", "lo", "hi", "basis", "evidence_status", "source_file"]]
    df.to_csv(OUT / "I_mix_terms_3q26.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
    print(df[["term", "quarter", "3Q26_to_date_value", "adr_contribution_pp", "lo", "hi", "evidence_status"]].round(2).to_string(index=False))


if __name__ == "__main__":
    main()

