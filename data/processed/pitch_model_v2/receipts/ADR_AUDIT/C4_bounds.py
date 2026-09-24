"""C4 bounds — what a broadened Latin-American comparator WOULD do, without the Mexico/Chile series.

The pre-stated blend (receipt §0) is brazil 0.368 / mexico 0.440 / chile 0.192 on the disclosed LatAm quarters.
Write the blended comparator as  c = w_BR * BR + (1 - w_BR) * X  where X is the Mexico+Chile component we could
not fetch.  Then the LatAm within slope of y on mix is

    b_y = b_exfx - w_BR * b_BR - (1 - w_BR) * b_X - b_size - b_los

with b_* the within-LatAm OLS slopes of each component on the mix term.  Everything but b_X is measured.  This
script (1) traces the pooled slope over w_BR with X neutral (b_X = 0, i.e. X uncorrelated with the mix term),
(2) solves for the b_X that would keep the pooled slope at 1.0, 0.5 and inside the band, and (3) tests the
mechanism: is Brazil's IPCA hospedagem co-moving with Brazil's own stays boom (which is what makes the mix term
negative)?

Run (from the audit worktree root):
  py -3.13 data/processed/pitch_model_v2/receipts/ADR_AUDIT/C4_bounds.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
MAIN = Path(r"C:\Users\krish\citadel-abnb")          # main tree holds the govdata raw store
ENG = ROOT / "data/processed/pitch_model_v2/adr_engine"
sys.path.insert(0, str(HERE))
from C4_audit import crv_summary, within_slope, loro, WEBB, wild_cluster, BAND  # noqa: E402

W_BR3 = 0.368       # pre-stated, three-country blend
W_BR_MX = 0.455     # Brazil + Mexico only
W_BR_CL = 0.657     # Brazil + Chile only


def main():
    pd.set_option("display.width", 220)
    lines = []
    P = lambda s="": (print(s), lines.append(s))
    d_all = pd.read_csv(ENG / "reconcile_pooled_cells.csv")
    disc = d_all[d_all.is_disclosed].copy().sort_values(["region", "qi"]).reset_index(drop=True)
    la = disc[disc.region == "LatAm"]

    # ---------------------------------------------------------------- 1. slope vs Brazil weight, X neutral
    P("=" * 100); P("1. POOLED SLOPE AS A FUNCTION OF THE BRAZIL WEIGHT IN THE LATAM COMPARATOR (X neutral)"); P("=" * 100)
    # X neutral = Brazil's own 7-quarter mean (a constant): keeps the LatAm level, removes the co-movement
    br_mean = la.cpi_p1_pct.mean()
    rows = []
    for w in [1.0, 0.9, 0.8, 0.7, W_BR_CL, 0.6, 0.5, W_BR_MX, 0.4, W_BR3, 0.3, 0.2, 0.1, 0.0]:
        dd = disc.copy()
        dd["cpi_alt"] = np.where(dd.region == "LatAm", w * dd.cpi_p1_pct + (1 - w) * br_mean, dd.cpi_p1_pct)
        dd["y_alt"] = dd.disclosed_exfx_pct - dd.cpi_alt - dd.global_unit_size_pp - dd.global_los_pp
        s = crv_summary(dd, "y_alt")
        bl, rl = within_slope(dd[dd.region == "LatAm"], "y_alt")
        tag = {1.0: "as published", W_BR3: "BR+MX+CL blend", W_BR_MX: "BR+MX blend", W_BR_CL: "BR+CL blend", 0.0: "no Brazil"}.get(w, "")
        rows.append(dict(w_brazil=w, blend=tag, pooled_b=s["b"], se_crv=s["se_crv"], p_b0_crv=s["p_b0_crv"],
                         p_b1_crv=s["p_b1_crv"], ci90_lo=s["ci90_lo"], ci90_hi=s["ci90_hi"],
                         latam_b=bl, latam_r=rl, in_band=BAND[0] <= s["b"] <= BAND[1]))
    cur = pd.DataFrame(rows)
    P(cur.round(3).to_string(index=False))
    cur.to_csv(HERE / "C4_brazil_weight_curve.csv", index=False)

    # ---------------------------------------------------------------- 2. what b_X would have to be
    P(""); P("=" * 100); P("2. REQUIRED CO-MOVEMENT OF THE MEXICO+CHILE COMPONENT WITH THE MIX TERM"); P("=" * 100)
    b_exfx, _ = within_slope(la, "disclosed_exfx_pct")
    b_br, r_br = within_slope(la, "cpi_p1_pct")
    b_sz, _ = within_slope(la, "global_unit_size_pp")
    b_los, _ = within_slope(la, "global_los_pp")
    P(f"within-LatAm slopes on mix: ex-FX {b_exfx:+.3f}, Brazil CPI {b_br:+.3f} (r {r_br:+.3f}), size {b_sz:+.3f}, LOS {b_los:+.3f}")
    # the pooled slope is a within-variance-weighted average of the region slopes; get the map pooled_b(latam_b)
    # numerically: it is linear in latam_b, so two points suffice
    def pooled_for_bx(w, bx):
        dd = disc.copy()
        # synthetic X with exactly slope bx on the LatAm mix and no other variation: X = mean + bx * (mix - mean)
        x_syn = br_mean + bx * (la.mix_pp - la.mix_pp.mean())
        dd["cpi_alt"] = dd.cpi_p1_pct.astype(float)
        dd.loc[dd.region == "LatAm", "cpi_alt"] = (w * la.cpi_p1_pct + (1 - w) * x_syn).to_numpy()
        dd["y_alt"] = dd.disclosed_exfx_pct - dd.cpi_alt - dd.global_unit_size_pp - dd.global_los_pp
        return crv_summary(dd, "y_alt")["b"]
    rows = []
    for w, lab in ((W_BR3, "BR+MX+CL (w_BR 0.368)"), (W_BR_MX, "BR+MX (0.455)"), (W_BR_CL, "BR+CL (0.657)")):
        b0, b1 = pooled_for_bx(w, 0.0), pooled_for_bx(w, -1.0)
        slope = b1 - b0          # d pooled_b / d b_X
        need = {tgt: (tgt - b0) / slope for tgt in (1.0, 0.5, 1.127)}
        rows.append(dict(blend=lab, pooled_b_if_X_neutral=b0, d_pooled_per_unit_bX=slope,
                         bX_for_pooled_1_0=need[1.0], bX_for_pooled_0_5=need[0.5], bX_for_pooled_1_127=need[1.127],
                         brazil_bX_actual=b_br))
    req = pd.DataFrame(rows)
    P(req.round(3).to_string(index=False))
    req.to_csv(HERE / "C4_required_bX.csv", index=False)
    P("  reading: b_X is the slope of the Mexico+Chile accommodation-CPI y/y on the LatAm mix term. Brazil's own is "
      f"{b_br:+.2f}pp of CPI per pp of mix. For the blended comparator to keep the pooled slope at the band floor "
      "the unobserved component must co-move at least as shown; at 1.0 it must co-move roughly as Brazil does.")

    # ---------------------------------------------------------------- 3. the mechanism: Brazil boom vs Brazil CPI
    P(""); P("=" * 100); P("3. MECHANISM: BRAZIL STAYS GROWTH vs BRAZIL HOTEL INFLATION vs THE LATAM MIX TERM"); P("=" * 100)
    v = pd.read_csv(ENG / "stays_yoy_by_country_vmatch.csv")
    br = v[(v.country == "brazil") & (v.q <= "2026Q2")].set_index("quarter").stays_yoy_pct
    ib = pd.read_csv(MAIN / "data/processed/govdata/P/raw/ibge_ipca_hospedagem_monthly.csv")
    ib = ib[ib.variable == "yoy12m"].copy()
    ib["q"] = pd.PeriodIndex(ib.month, freq="M").asfreq("Q").astype(str)
    ibq = ib.groupby("q").value.mean()
    ibq.index = [f"{p[-1]}Q{p[2:4]}" for p in ibq.index]
    mix = pd.read_csv(ENG / "geomix_within_region.csv")
    mix = mix[mix.region == "LatAm"].set_index("quarter").mix_pp
    j = pd.concat([br.rename("brazil_stays_yoy"), ibq.rename("ibge_hosp_yoy"), mix.rename("latam_mix_pp")], axis=1).dropna()
    j = j.loc[[q for q in j.index if int(q[-2:]) >= 22]]           # 1Q22 on: the govdata window the note uses
    j["disclosed"] = j.index.isin(la.quarter)
    P(j.round(2).to_string())
    for lab, sub in (("1Q22 on", j), ("disclosed 4Q24-2Q26", j[j.disclosed])):
        c = sub[["brazil_stays_yoy", "ibge_hosp_yoy", "latam_mix_pp"]].corr()
        P(f"  {lab} (n {len(sub)}): r(Brazil stays y/y, IBGE hosp) {c.loc['brazil_stays_yoy','ibge_hosp_yoy']:+.3f}; "
          f"r(Brazil stays y/y, LatAm mix) {c.loc['brazil_stays_yoy','latam_mix_pp']:+.3f}; "
          f"r(IBGE hosp, LatAm mix) {c.loc['ibge_hosp_yoy','latam_mix_pp']:+.3f}")
    j.to_csv(HERE / "C4_brazil_mechanism.csv")

    # ---------------------------------------------------------------- 4. the same regression on ALL chained LatAm cells (n 7 -> ?)
    P(""); P("=" * 100); P("4. FOR THE RECORD: LatAm cells outside the disclosed set"); P("=" * 100)
    lac = d_all[(d_all.region == "LatAm")][["quarter", "basis_04", "is_disclosed", "in_chained_sample", "disclosed_exfx_pct", "mix_pp", "cpi_p1_pct", "y_full_p1"]]
    P(lac.round(3).to_string(index=False))
    P("  (every LatAm chained cell is also a disclosed cell: there is no wider LatAm sample to test on)")

    (HERE / "C4_bounds_output.txt").write_text("\n".join(lines), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
