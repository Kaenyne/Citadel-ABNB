"""
WS-N, memo 2: the 4Q26 lap decision.

Lays out two cases for the 4Q26 nights y/y baseline side by side:
  Case A: team baseline / PR #32 as reconciled (NA-only lap of the RNPL,
    cancellation-redesign and single-fee bundle). 4Q26 +8.9% (132.7mm).
  Case B: WS-D's dated-disclosure case (cancellation redesign and single-fee
    tranche 1 were global from October 2025, not NA-only; the ex-NA fee and
    cancellation legs are pinned at 40-50% of the ex-NA bundle by an
    out-of-sample check against the 4Q25 "over 200bps" disclosure). 4Q26
    8.03-8.2% (131.7-131.9mm).

For each case: nights y/y, nights mm, implied GBV and revenue at card v2's
4Q26 ADR (three FX estimators plus the midpoint memo 1 recommends), and the
distance to the 4Q26 revenue guide arithmetic from the H1-to-H2 bridge note.

Every number is read from an existing, committed CSV; this script does no new
fitting. Nights, ADR, take rate and revenue-base inputs are sourced; the
40-50% ex-NA split is WS-D's pinned assumption (not this script's).

Output: data/processed/adrv3/N/N2_q4_lap_cases.csv

py -3.13, offline.
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ADRQ3_J = os.path.join(ROOT, "data", "processed", "adrq3", "J")
OVERNIGHT2_D = os.path.join(ROOT, "data", "processed", "overnight2", "D")
OUT = os.path.join(ROOT, "data", "processed", "adrv3", "N")
os.makedirs(OUT, exist_ok=True)

# sourced: 4Q25 disclosed nights (research/notes/2026-09-10_nights-baseline-reconciliation.md, "fixed inputs")
NIGHTS_4Q25_MM = 121.9
# sourced: same-quarter-prior-year take rate and revenue base, as used by J3's card v2
# (analysis/src/adrq3/J3_residual_nowcast_card_v2.py, TAKE / REV_BASE dicts)
TAKE_4Q26 = 0.1362
REV_BASE_4Q26_MUSD = 2778.0


def main():
    j = pd.read_csv(os.path.join(ADRQ3_J, "adr_card_v2.csv"))
    j4 = j[j.quarter == "4Q26"].set_index("fx_estimator")
    gap = pd.read_csv(os.path.join(OVERNIGHT2_D, "D1_exna_4q26_gap.csv"))

    # --- the two nights cases -------------------------------------------------
    cases = []
    # Case A: team baseline, PR #32 NA-only lap (sourced: reconciliation note)
    nights_a = 132.7
    yoy_a = round(100 * (nights_a / NIGHTS_4Q25_MM - 1), 2)
    cases.append({
        "case": "A: team baseline (PR #32, NA-only lap)",
        "basis": "sourced: research/notes/2026-09-10_nights-baseline-reconciliation.md reconciled team baseline; PR #32 fits RNPL +2.4pp and cancellation+fee redesign +2.3pp on NA-only observations",
        "nights_yoy_pct": yoy_a,
        "nights_mm": nights_a,
        "exna_split_assumed_pct": None,
    })

    # Case B: WS-D global dating, ex-NA split 40% and 50% (sourced dates, assumed/pinned split)
    for _, r in gap.iterrows():
        split_label = r["scenario"]
        split_pct = int(split_label.split("are ")[1].split("%")[0])
        if split_pct not in (40, 50):
            continue  # 70/100 are inconsistent with the 4Q25 disclosure per WS-D; kept out of the headline case
        cases.append({
            "case": f"B: WS-D global lap ({split_pct}% ex-NA split)",
            "basis": "sourced dates (cancellation redesign and single-fee tranche 1 global from Oct 2025, 4Q25/1Q26 letters); ex-NA fee+cancellation share of the ex-NA bundle ASSUMED at pinned value, cross-checked out-of-sample against 4Q25 'over 200bps' disclosure",
            "nights_yoy_pct": r["adjusted_4q26_pct"],
            "nights_mm": r["adjusted_4q26_nights_mm"],
            "exna_split_assumed_pct": split_pct,
        })

    # Case B point (midpoint of the pinned 40-50% range, i.e. 45%): interpolate
    nights_b_lo = gap.loc[gap.scenario.str.contains("50%"), "adjusted_4q26_nights_mm"].values[0]
    nights_b_hi = gap.loc[gap.scenario.str.contains("40%"), "adjusted_4q26_nights_mm"].values[0]
    nights_b_mid = round((nights_b_lo + nights_b_hi) / 2, 2)
    yoy_b_mid = round(100 * (nights_b_mid / NIGHTS_4Q25_MM - 1), 2)
    cases.append({
        "case": "B: WS-D global lap, point (45% ex-NA split, midpoint of pinned 40-50% range)",
        "basis": "ASSUMED: midpoint of WS-D's pinned 40-50% range, for a single point estimate",
        "nights_yoy_pct": yoy_b_mid,
        "nights_mm": nights_b_mid,
        "exna_split_assumed_pct": 45,
    })

    cases_df = pd.DataFrame(cases)

    # --- GBV and revenue at card v2's 4Q26 ADR, all three FX estimators ------
    rows = []
    for _, c in cases_df.iterrows():
        for est in ("eur_fit", "baskets", "midpoint"):
            adr = j4.loc[est, "adr_usd_point"]
            nights_mm = c["nights_yoy_pct"] and c["nights_mm"]
            gbv_busd = round(c["nights_mm"] * adr / 1000.0, 3)
            revenue_musd = round(gbv_busd * 1000.0 * TAKE_4Q26, 1)
            revenue_yoy_pct = round(100 * (revenue_musd / REV_BASE_4Q26_MUSD - 1), 2)
            rows.append({
                "case": c["case"],
                "nights_yoy_pct": c["nights_yoy_pct"],
                "nights_mm": c["nights_mm"],
                "exna_split_assumed_pct": c["exna_split_assumed_pct"],
                "fx_estimator": est,
                "adr_usd_4q26": adr,
                "gbv_busd": gbv_busd,
                "revenue_musd": revenue_musd,
                "revenue_yoy_pct": revenue_yoy_pct,
            })
    out = pd.DataFrame(rows)

    # --- distance to the Q4 revenue guide arithmetic --------------------------
    # sourced: research/notes/2026-09-10_h1-to-h2-bridge.md section 7 and
    # data/processed/h2_bridge/h2_bridge_revenue_dollars.csv, 4Q26 row
    guide_arith_musd_lo = 3050.0  # sourced: bridge note, "guide midpoint near $3.05B to $3.10B"
    guide_arith_musd_hi = 3100.0
    consensus_musd = 3200.0  # sourced: Zacks, 4 Sep 2026 vintage, per h2_bridge_revenue_dollars.csv
    bridge_actual_point_musd = 3165.64  # sourced: h2_bridge_revenue_dollars.csv, 4Q26 revenue_musd (old driver-model point, descriptive only, not this memo's model)

    out["distance_to_guide_arith_lo_musd"] = round(out["revenue_musd"] - guide_arith_musd_lo, 1)
    out["distance_to_guide_arith_hi_musd"] = round(out["revenue_musd"] - guide_arith_musd_hi, 1)
    out["distance_to_consensus_musd"] = round(out["revenue_musd"] - consensus_musd, 1)
    out["guide_arith_lo_musd_sourced"] = guide_arith_musd_lo
    out["guide_arith_hi_musd_sourced"] = guide_arith_musd_hi
    out["consensus_musd_sourced"] = consensus_musd
    out["bridge_driver_model_point_musd_descriptive"] = bridge_actual_point_musd

    out.to_csv(os.path.join(OUT, "N2_q4_lap_cases.csv"), index=False)

    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
