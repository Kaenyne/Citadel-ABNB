"""Stage C — the RNPL cancellation adjustment to the kernel.

    Revenue_q = c_s * [ phi-weighted GBV ]_q * (1 - L_q)

L_q is the EXTRA leakage from RNPL bookings that were counted in a prior quarter's
GBV (net of the cancellations that had happened by then) and then cancel before
check-in, so they never become revenue.

Two facts fix the shape:
  * GBV is booking-dated and "net of cancellations and alterations that occurred
    during that period" (FY2025 10-K KPI definition).  A booking made in q-1 and
    cancelled in q reduces GBV_q, not GBV_{q-1}.  So a cancellation of a carried
    booking is a pure leak out of the kernel base in the quarter it happens, and
    it is only PARTLY refunded to the model one quarter later, when the negative
    lands in GBV_q and is carried forward with weight phi_1.
  * RNPL payment falls due "shortly before the end of the listing's free
    cancellation period" (D002), i.e. days before check-in.  So essentially the
    whole excess cancellation risk on a carried RNPL booking is still ahead of it
    at the start of the recognition quarter:  L_q ~= s_backlog * delta_c.
"""
from __future__ import annotations

import os
import numpy as np
import pandas as pd

from common import OUT, SEASON_NAME, D1, GBV_2Q26, GBV_1Q26

W_PUB = 2.0 / 3.0

# RNPL share of the live (booked, unstayed) backlog.  Three sourced anchors.
SHARE_ANCHORS = {
    "nights_share_16.7pct": 0.167,   # 03_insider_mechanics 1.6: 20% GBV @1.25x ADR
    "gbv_share_21pct": 0.21,         # D031 "roughly 20%" 1Q26, D043 ">20%" 2Q26
    "backlog_share_23.1pct": 0.231,  # 1.6: 20% GBV share at 1.5x dwell time
}
# incremental RNPL cancellation propensity, in points, from D1's grid
DELTA_C = [0.01, 0.02, 0.04, 0.06]
DELTA_LABEL = {0.01: "+1pt", 0.02: "+2pt", 0.04: "+4pt (D central)",
               0.06: "+6pt (management-implied)"}

# RNPL GBV share at the time the bookings feeding each quarter were made.
# 3Q25 / 4Q25 are the tracker-backlog RESEARCHER ramp (no disclosure of any kind);
# 1Q26 = 20% is management's own floor (D031); 2Q26 = 22% is a researcher point pick
# inside the ">20%" floor (D043).  Flagged as such wherever it is used.
RNPL_GBV_SHARE_BOOKED = {"2025Q3": 0.05, "2025Q4": 0.12, "2026Q1": 0.20,
                         "2026Q2": 0.22, "2026Q3": 0.23, "2026Q4": 0.23}
SHARE_PROVENANCE = {"2025Q3": "researcher ramp, NO disclosure",
                    "2025Q4": "researcher ramp, NO disclosure",
                    "2026Q1": "management floor '~20%' (D031)",
                    "2026Q2": "researcher pick inside '>20%' floor (D043)",
                    "2026Q3": "researcher extrapolation",
                    "2026Q4": "researcher extrapolation"}


def lam_series(panel: pd.DataFrame, w: float = W_PUB) -> pd.DataFrame:
    d = panel.dropna(subset=["revenue_musd", "gbv_l1", "gbv_l2"]).copy()
    d["base_musd"] = w * d["gbv_l1"] + (1 - w) * d["gbv_l2"]
    d["lambda_pct"] = 100.0 * d["revenue_musd"] / d["base_musd"]
    return d


def season_stats(lam: pd.DataFrame, lo="2023Q1", hi="2025Q4") -> pd.DataFrame:
    w = lam[(lam["q"] >= lo) & (lam["q"] <= hi)]
    rows = []
    for s, g in w.groupby("season"):
        v = g["lambda_pct"]
        rows.append(dict(season=SEASON_NAME[s], n=len(v), mean=float(v.mean()),
                         sd=float(v.std(ddof=1)) if len(v) > 1 else np.nan,
                         cells="; ".join(f"{a} {b:.3f}" for a, b in
                                         zip(g["label"], g["lambda_pct"])),
                         window=f"{lo}-{hi}"))
    return pd.DataFrame(rows)


def pooled_rel_sigma(lam: pd.DataFrame, lo="2023Q1", hi="2025Q4") -> float:
    """Pooled relative dispersion of lambda about its own season mean."""
    w = lam[(lam["q"] >= lo) & (lam["q"] <= hi)]
    dev = np.concatenate([(g["lambda_pct"] / g["lambda_pct"].mean() - 1.0).values
                          for _, g in w.groupby("season")])
    S = w["season"].nunique()
    return float(np.sqrt((dev ** 2).sum() / (len(dev) - S)))


def run(panel: pd.DataFrame, boot_seed=20260911, n_boot=4000):
    os.makedirs(OUT, exist_ok=True)
    lam = lam_series(panel)
    lam[["label", "q", "season_name", "revenue_musd", "gbv_l1", "gbv_l2",
         "base_musd", "lambda_pct"]].to_csv(
        os.path.join(OUT, "C1_lambda_series.csv"), index=False)

    st = season_stats(lam)                       # 2023-2025, pre-RNPL-affected cells
    sig = pooled_rel_sigma(lam)
    st["pooled_rel_sigma"] = sig
    st.to_csv(os.path.join(OUT, "C2_lambda_season_norms.csv"), index=False)

    # ---- leakage grid ------------------------------------------------------
    rows = []
    lam_q3 = float(st.loc[st.season == "Q3", "mean"].iloc[0])
    lam_q4 = float(st.loc[st.season == "Q4", "mean"].iloc[0])
    base_3q26 = W_PUB * GBV_2Q26 + (1 - W_PUB) * GBV_1Q26
    for sname, s in SHARE_ANCHORS.items():
        for dc in DELTA_C:
            L = s * dc
            rows.append(dict(share_anchor=sname, rnpl_backlog_share=s,
                             delta_c=dc, delta_c_label=DELTA_LABEL[dc],
                             leakage_L=L, leakage_L_pct=100 * L,
                             lambda_Q3_hist=lam_q3,
                             lambda_Q3_adj=lam_q3 * (1 - L),
                             lambda_Q3_drop_pp=lam_q3 * L,
                             lambda_Q4_hist=lam_q4,
                             lambda_Q4_adj=lam_q4 * (1 - L),
                             lambda_Q4_drop_pp=lam_q4 * L,
                             revenue_3q26_musd=base_3q26 * lam_q3 * (1 - L) / 100.0,
                             revenue_3q26_drop_musd=base_3q26 * lam_q3 * L / 100.0))
    c3 = pd.DataFrame(rows)
    c3.to_csv(os.path.join(OUT, "C3_leakage_grid.csv"), index=False)

    # ---- does 1H26 already show it? ---------------------------------------
    rng = np.random.default_rng(boot_seed)
    chk = []
    for q, lab in [("2026Q1", "1Q26"), ("2026Q2", "2Q26")]:
        r = lam[lam["q"] == q].iloc[0]
        s = SEASON_NAME[int(r["season"])]
        hist = lam[(lam["q"] >= "2023Q1") & (lam["q"] <= "2025Q4") &
                   (lam["season"] == r["season"])]["lambda_pct"].values
        mu = float(hist.mean())
        # bootstrap the season mean (n=3 cells) and add one-draw dispersion
        draws = rng.choice(hist, size=(n_boot, len(hist)), replace=True).mean(axis=1)
        pred = draws * (1.0 + rng.normal(0, sig, n_boot))
        # the RNPL share that was live when the bookings feeding q were made
        s_booked = (W_PUB * RNPL_GBV_SHARE_BOOKED[_prev(q, 1)] +
                    (1 - W_PUB) * RNPL_GBV_SHARE_BOOKED[_prev(q, 2)])
        chk.append(dict(
            quarter=lab, season=s, lambda_actual=float(r["lambda_pct"]),
            season_mean_2023_25=mu,
            dev_pp=float(r["lambda_pct"]) - mu,
            dev_pct=100.0 * (float(r["lambda_pct"]) / mu - 1.0),
            band80_lo=float(np.percentile(pred, 10)), band80_hi=float(np.percentile(pred, 90)),
            band95_lo=float(np.percentile(pred, 2.5)), band95_hi=float(np.percentile(pred, 97.5)),
            inside_80=bool(np.percentile(pred, 10) <= r["lambda_pct"] <= np.percentile(pred, 90)),
            implied_L_pct=100.0 * (1.0 - float(r["lambda_pct"]) / mu),
            rnpl_share_of_feeding_gbv=s_booked,
            implied_delta_c_pp=100.0 * (1.0 - float(r["lambda_pct"]) / mu) / s_booked
            if s_booked > 0 else np.nan,
            share_provenance=f"{_prev(q,1)}: {SHARE_PROVENANCE[_prev(q,1)]}; "
                             f"{_prev(q,2)}: {SHARE_PROVENANCE[_prev(q,2)]}"))
    c4 = pd.DataFrame(chk)
    c4.to_csv(os.path.join(OUT, "C4_1h26_lambda_check.csv"), index=False)

    # ---- the 5 November control chart -------------------------------------
    # At 5 Nov both GBV lags are printed, so lambda_Q3 is an IDENTITY on the print.
    sd_q3 = float(st.loc[st.season == "Q3", "sd"].iloc[0])
    ctl = []
    for sig_name, se in [("pooled_rel_sigma_all_seasons",
                          lam_q3 * np.sqrt(sig ** 2 * (1 + 1.0 / 3.0))),
                         ("Q3_own_sd_n3", sd_q3 * np.sqrt(1 + 1.0 / 3.0))]:
        for z, lab in [(1.0, "1 sigma"), (1.645, "90% one-sided"), (2.0, "2 sigma"),
                       (2.576, "99% two-sided")]:
            lo = lam_q3 - z * se
            ctl.append(dict(sigma_basis=sig_name, rule=lab, z=z,
                            lambda_centre=lam_q3, se_pp=se, lambda_lower=lo,
                            revenue_lower_musd=base_3q26 * lo / 100.0,
                            implied_L_pct=100.0 * (1 - lo / lam_q3),
                            implied_delta_c_pp_at_21pct_share=
                            100.0 * (1 - lo / lam_q3) / 0.21))
    c5 = pd.DataFrame(ctl)
    c5.to_csv(os.path.join(OUT, "C5_control_chart_5nov.csv"), index=False)

    # ---- read the D1 grid for the corroborating nights-side range ----------
    try:
        d1 = pd.read_csv(D1)
        g = d1[d1["delta_pp_applied"] > 0]
        c6 = pd.DataFrame([dict(
            source="D1_rnpl_cohort_scenarios.csv", n_cells=len(d1),
            q3_growth_delta_min=float(g["3Q26_growth_delta_pts"].min()),
            q3_growth_delta_max=float(g["3Q26_growth_delta_pts"].max()),
            q4_growth_delta_min=float(g["4Q26_growth_delta_pts"].min()),
            q4_growth_delta_max=float(g["4Q26_growth_delta_pts"].max()),
            q3_central_4pp=float(d1[(d1.share_path == "share_central") &
                                    (d1.adr_ratio == "adr_plus25") &
                                    (d1.delta_scenario == "delta_4pp") &
                                    (d1.lead_time == "lead_2.2") &
                                    (d1.lead_uplift == "uplift_7") &
                                    (d1.rebook_offset == 0.25)]["3Q26_growth_delta_pts"].iloc[0]),
            q4_central_4pp=float(d1[(d1.share_path == "share_central") &
                                    (d1.adr_ratio == "adr_plus25") &
                                    (d1.delta_scenario == "delta_4pp") &
                                    (d1.lead_time == "lead_2.2") &
                                    (d1.lead_uplift == "uplift_7") &
                                    (d1.rebook_offset == 0.25)]["4Q26_growth_delta_pts"].iloc[0]))])
    except Exception as e:                                            # pragma: no cover
        c6 = pd.DataFrame([dict(source="D1", error=str(e))])
    c6.to_csv(os.path.join(OUT, "C6_d1_nights_crosscheck.csv"), index=False)
    return lam, st, c3, c4, c5, c6, sig


def _prev(q: str, k: int) -> str:
    y, s = int(q[:4]), int(q[-1])
    i = y * 4 + (s - 1) - k
    return f"{i // 4}Q{i % 4 + 1}"
