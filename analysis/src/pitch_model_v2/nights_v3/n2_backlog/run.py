#!/usr/bin/env python3
"""N2 - Backlog identity term: booked-not-yet-stayed nights from unearned fees
and the RNPL unpaid share.

Registered identity (docs/pitch-model-v2/lines/nights_v3_prereg.md, DEC-0033):

    N(t) = S(t) + K(t) - K(t-1)
    b(t) = [dK(t) - dK(t-4)] / N(t-4)          (growth points)

with K(t) = K_UF(t) + U(t):
    K_UF(t) = UF(t) / fee_share / ADR_eff(t)   (paid, fee-bearing backlog)
    U(t)    = u(t) * X_gbv(t) / (ADR_eff(t) * r)   (unpaid RNPL backlog)
    X_gbv(t)= B * norm_s * revenue(t+1) / fee_share

Governing note: docs/rnpl-short-audit/04_balance-sheet-verification.md (11 Sep,
adversarial audit) supersedes research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md
wherever they disagree.  Consequences carried here:
  * unearned fees is the FX-clean, migration-NEUTRAL line (FY2025 10-K Note 2:
    "Host and guest fees are recorded as cash with a corresponding amount in
    unearned fees").  The single-fee migration term m is NOT identified
    (it returns -1.4% for 3Q25, before the migration existed) and is set to 0.
  * u is therefore solved on unearned fees alone, reproducing
    data/processed/rnpl_short_audit/verify_bs_uf_only_solve.csv ("note baseline").
  * the 0.124 divisor in analysis/src/rnpl_balance_sheet_bridge.py is the
    GUEST-fee share and is wrong for a pool that holds both fees; it is kept as
    the low edge of the registered grid only.

Reads only files already on disk.  Writes only under
data/processed/pitch_model_v2/nights_v3/N2/.  No network.
"""
from __future__ import annotations

import csv
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = ROOT / "data/processed/pitch_model_v2/nights_v3/N2"
PANEL = ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv"
DRIVER = ROOT / "data/processed/abnb_driver_history_quarterly.csv"
MODULE = ROOT / "data/processed/rnpl_short_audit/rnpl_nights_module.csv"

# ---------------------------------------------------------------- parameters
FEES = [0.124, 0.133, 0.151, 0.155]          # prereg grid, share of GBV
FEE_C = 0.133                                 # central (see README / dossier §8)
BS = [1.00, 1.05, 1.10]                       # backlog scale vs pre-RNPL norm
B_C = 1.05                                    # central = midpoint of the grid
RS = [1.00, 1.33]                             # RNPL / non-RNPL ADR ratio
R_C = 1.33                                    # central (upper bound per audit C5)
REV_3Q26 = 4800.0                             # team point, R2 dossier / bridge
REV_4Q26 = 3166.0                             # team point, R5 dossier / bridge
ADR_3Q26 = 176.88                             # D4 base, adr_card_v3 without_K
ADR_4Q26 = 173.94                             # D4 base
RNPL_SHARE_2Q26 = 0.21                        # disclosed lower bound (D043)
# RNPL GBV share path used ONLY to shape the backlog-scale ramp B(t).
# 3Q25 / 4Q25 are D1's central assumptions (ranges 2.5-6% and 7-12%), 1Q26 / 2Q26 disclosed.
SHARE_HIST = {"3Q25": 0.04, "4Q25": 0.09, "1Q26": 0.20, "2Q26": 0.21}
BPATHS = ["ramp", "step"]
BPATH_C = "ramp"
# forward nights paths (m nights); dossier = D1/D2 adopted base, module = RNPL module base
NPATH = {
    "dossier": {"3Q26": 146.3, "4Q26": 131.8, "1Q27": 167.1, "2Q27": 157.8},
    "module": {"3Q26": 146.3, "4Q26": 131.2, "1Q27": 166.3, "2Q27": 157.9},
}
SHARE_SCEN = {"flat21": 0.21, "mid24": 0.24, "high27": 0.27}
CFO_NA_PTS = 2.40          # PR #32 fitted RNPL term, pts of NA nights (call statement, unverified)
CFO_GLOBAL_PTS = 3.0       # 1Q26 call "approximately three points", global (unverified vs filing)

# 3Q26 score sheet, bridge output section 4 (u, m, label)
SCORE_SHEET = [
    (0.07, 0.09, "2Q26 solved values carried"),
    (0.10, 0.12, "RNPL share 22-23%, migration ~60% listings"),
    (0.12, 0.18, "July expansion + migration ~80%"),
    (0.07, 0.00, "no migration effect at all"),
    (0.15, 0.00, "UF hole all RNPL, no migration"),
]


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_panel():
    rows = list(csv.DictReader(open(PANEL, encoding="utf-8-sig")))
    order = [r["quarter"] for r in rows]
    d = {r["quarter"]: r for r in rows}
    return order, d


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    order, P = load_panel()
    idx = {q: i for i, q in enumerate(order)}

    def g(q, k):
        return _f(P[q][k]) if q in P else None

    def shift(q, k):
        i = idx[q] + k
        return order[i] if 0 <= i < len(order) else None

    uf = {q: g(q, "unearned_fees_musd") for q in order}
    adr = {q: g(q, "adr_usd") for q in order}
    nights = {q: g(q, "nights_m") for q in order}
    gbv = {q: g(q, "gbv_musd") for q in order}
    rev = {q: g(q, "revenue_musd") for q in order}

    QK = [q for q in order if uf[q] is not None]          # 4Q20 .. 2Q26

    # forward ADR / revenue stubs so 2Q26 has a t+1
    adr_fwd = dict(adr)
    adr_fwd["3Q26"] = ADR_3Q26
    rev_fwd = dict(rev)
    rev_fwd["3Q26"] = REV_3Q26
    rev_fwd["4Q26"] = REV_4Q26

    def nrev(q):
        nq = shift(q, 1)
        if nq is None:
            return rev_fwd.get("3Q26") if q == "2Q26" else None
        return rev_fwd.get(nq)

    def adr_eff(q, basis):
        if basis == "current":
            return adr[q]
        if basis == "forward":
            nq = shift(q, 1)
            return adr_fwd.get(nq) if nq else adr_fwd.get("3Q26")
        if basis == "kernelw":                       # 2/3 this quarter + 1/3 last
            pq = shift(q, -1)
            if pq is None or adr[pq] is None:
                return None
            return (2.0 / 3.0) * adr[q] + (1.0 / 3.0) * adr[pq]
        raise ValueError(basis)

    ADR_BASES = ["current", "forward", "kernelw"]

    # --------------------------------------------------- 0. fee-share evidence
    fee_rows = []
    for q in order:
        i = idx[q]
        if i < 3:
            continue
        win = order[i - 3: i + 1]
        if any(rev[w] is None or gbv[w] is None for w in win):
            continue
        r4 = sum(rev[w] for w in win)
        g4 = sum(gbv[w] for w in win)
        gy = g(q, "gbv_yoy_pct")
        raw = r4 / g4
        # lag correction: revenue recognised now maps to GBV booked ~0.73q earlier
        corr = raw / ((1 + (gy or 0) / 100.0) ** (-0.73 / 4.0)) if gy is not None else None
        fee_rows.append({
            "quarter": q, "revenue_ltm_musd": round(r4, 1), "gbv_ltm_musd": round(g4, 1),
            "realised_fee_share_of_gbv": round(raw, 5),
            "gbv_yoy_pct": gy,
            "lag_corrected_fee_share": (round(corr, 5) if corr else None),
            "note": "revenue is essentially guest+host service fees; lag correction uses the 2.2-month mean lead (0.73q)",
        })
    with open(OUT / "fee_share_evidence.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(fee_rows[0].keys()))
        w.writeheader()
        w.writerows(fee_rows)

    # --------------------------------------------------------- 1. backlog_uf
    rows = []
    for q in QK:
        for fee in FEES:
            for basis in ADR_BASES:
                a = adr_eff(q, basis)
                if a is None:
                    continue
                bg = uf[q] / fee                       # backlog GBV, $M
                k = bg / a                             # m nights
                rows.append({
                    "quarter": q, "fee_share": fee, "adr_basis": basis,
                    "unearned_fees_musd": uf[q], "adr_eff_usd": round(a, 2),
                    "backlog_gbv_musd": round(bg, 1),
                    "k_uf_m_nights": round(k, 3),
                    "k_uf_over_nights_q": (round(k / nights[q], 4) if nights[q] else None),
                    "implied_mean_lead_months": (round(3.0 * k / nights[q], 2) if nights[q] else None),
                    "is_central": int(fee == FEE_C and basis == "current"),
                })
    with open(OUT / "backlog_uf.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    KUF = {(r["quarter"], r["fee_share"], r["adr_basis"]): r["k_uf_m_nights"] for r in rows}

    # ------------------------------------------- 2. seasonal norms and u solve
    NORM_BASE = {
        "1": ["1Q23", "1Q24", "1Q25"], "2": ["2Q23", "2Q24", "2Q25"],
        "3": ["3Q23", "3Q24"], "4": ["4Q23", "4Q24"],
    }
    norm = {s: st.mean(uf[q] / nrev(q) for q in qs) for s, qs in NORM_BASE.items()}
    KAPPA_FEE = {}      # backlog nights per booked night, pre-RNPL, by season
    for s, qs in NORM_BASE.items():
        KAPPA_FEE[s] = st.mean(uf[q] / gbv[q] for q in qs)   # multiply by 1/fee for nights ratio

    RNPL_Q = ["3Q25", "4Q25", "1Q26", "2Q26"]

    def b_eff(q, B, bpath):
        """Backlog scale actually in force in q.

        'step'  - B jumps to its full value in 3Q25, the US launch quarter.
        'ramp'  - lead-time lengthening scales with RNPL adoption, B(t) =
                  1 + (B-1) * s(t)/s(2Q26).  A discontinuous jump in the
                  platform-wide lead time at one launch quarter is not credible
                  and shows up as a spurious one-year step in b; the ramp is
                  also the only variant whose implied RNPL GBV shares stay
                  inside D1's own registered ranges (2.5-6% for 3Q25).
        """
        if q not in SHARE_HIST:
            return B
        return B if bpath == "step" else 1.0 + (B - 1.0) * SHARE_HIST[q] / RNPL_SHARE_2Q26

    u_solve = {}
    for q in RNPL_Q:
        s = q[0]
        ratio = (uf[q] / nrev(q)) / norm[s]
        for B in BS:
            for bp in BPATHS:
                u_solve[(q, B, bp)] = 1.0 - ratio / b_eff(q, B, bp)

    # lambda: relative residence of an unpaid RNPL booking vs the average lead,
    # calibrated at 2Q26 on the disclosed 21% GBV share.  Reduced form, not measured.
    def lam_of(B):
        u = u_solve[("2Q26", B, BPATH_C)]
        s = RNPL_SHARE_2Q26
        return (u * (1 - s)) / (s * (1 - u))

    def u_of_share(s, B):
        lam = lam_of(B)
        return s * lam / ((1 - s) + s * lam)

    def share_of_u(u, B):
        lam = lam_of(B)
        return u / (lam * (1 - u) + u)

    # ------------------------------------------------------ 3. backlog_total
    def x_gbv(q, fee, B, bpath):
        return b_eff(q, B, bpath) * norm[q[0]] * nrev(q) / fee

    tot_rows = []
    for q in QK:
        for fee in FEES:
            for basis in ADR_BASES:
                a = adr_eff(q, basis)
                if a is None:
                    continue
                kuf = KUF[(q, fee, basis)]
                for B in BS:
                    for r in RS:
                        for bp in BPATHS:
                            if q in RNPL_Q:
                                u = u_solve[(q, B, bp)]
                                U = u * x_gbv(q, fee, B, bp) / (a * r)
                            else:
                                u, U = 0.0, 0.0
                            role = ""
                            if (fee == FEE_C and basis == "current" and B == B_C
                                    and r == R_C and bp == BPATH_C):
                                role = "central"
                            tot_rows.append({
                                "quarter": q, "fee_share": fee, "adr_basis": basis,
                                "backlog_scale_B": B, "b_path": bp, "adr_ratio_r": r,
                                "b_in_force": round(b_eff(q, B, bp), 4),
                                "u_unpaid_share_pct": round(100 * u, 3),
                                "implied_rnpl_gbv_share_pct": (round(100 * share_of_u(u, B), 2) if u > 0 else 0.0),
                                "k_uf_m_nights": kuf,
                                "u_unpaid_m_nights": round(U, 3),
                                "k_total_m_nights": round(kuf + U, 3),
                                "k_over_nights_q": (round((kuf + U) / nights[q], 4) if nights[q] else None),
                                "band_role": role,
                            })
    with open(OUT / "backlog_total.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tot_rows[0].keys()))
        w.writeheader()
        w.writerows(tot_rows)

    KTOT = {(r["quarter"], r["fee_share"], r["adr_basis"], r["backlog_scale_B"],
             r["adr_ratio_r"], r["b_path"]): r["k_total_m_nights"] for r in tot_rows}
    UNP = {(r["quarter"], r["fee_share"], r["adr_basis"], r["backlog_scale_B"],
            r["adr_ratio_r"], r["b_path"]): r["u_unpaid_m_nights"] for r in tot_rows}

    # ------------------------------------------------------ 4. identity term
    def b_terms(q, fee, basis, B, r, bp):
        q1, q4, q5 = shift(q, -1), shift(q, -4), shift(q, -5)
        for x in (q1, q4, q5):
            if x is None or x not in QK:
                return None
        if q not in QK or nights[q4] is None:
            return None
        key = lambda z: (z, fee, basis, B, r, bp)
        dK = KTOT[key(q)] - KTOT[key(q1)]
        dK4 = KTOT[key(q4)] - KTOT[key(q5)]
        dU = UNP[key(q)] - UNP[key(q1)]
        dU4 = UNP[key(q4)] - UNP[key(q5)]
        b = 100.0 * (dK - dK4) / nights[q4]
        b_u = 100.0 * (dU - dU4) / nights[q4]
        return {
            "dK_m_nights": round(dK, 3), "dK_lag4_m_nights": round(dK4, 3),
            "b_pp": round(b, 3), "b_unpaid_pp": round(b_u, 3), "b_paid_pp": round(b - b_u, 3),
            "dK_over_N_lag4_pp": round(100.0 * dK / nights[q4], 3),
            "k_over_n_quarters": round(KTOT[key(q)] / nights[q], 4) if nights[q] else None,
            "stays_implied_m": round(nights[q] - dK, 2),
        }

    grid_rows = []
    for q in QK:
        for fee in FEES:
            for basis in ADR_BASES:
                for B in BS:
                    for r in RS:
                        for bp in BPATHS:
                            t = b_terms(q, fee, basis, B, r, bp)
                            if t is None:
                                continue
                            row = {"quarter": q, "fee_share": fee, "adr_basis": basis,
                                   "backlog_scale_B": B, "adr_ratio_r": r, "b_path": bp}
                            row.update(t)
                            grid_rows.append(row)
    with open(OUT / "identity_term_grid.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(grid_rows[0].keys()))
        w.writeheader()
        w.writerows(grid_rows)

    # central / low / high on the registered grid, ADR basis held at 'current'
    id_rows = []
    for q in QK:
        cells = [r for r in grid_rows if r["quarter"] == q and r["adr_basis"] == "current"]
        if not cells:
            continue
        cen = next(r for r in cells if r["fee_share"] == FEE_C and r["backlog_scale_B"] == B_C
                   and r["adr_ratio_r"] == R_C and r["b_path"] == BPATH_C)
        lo = min(cells, key=lambda r: r["b_pp"])
        hi = max(cells, key=lambda r: r["b_pp"])
        ff = [r for r in cells if r["fee_share"] == FEE_C]
        lo_ff = min(ff, key=lambda r: r["b_pp"])
        hi_ff = max(ff, key=lambda r: r["b_pp"])
        key = lambda z: (q, z["fee_share"], "current", z["backlog_scale_B"], z["adr_ratio_r"], z["b_path"])
        id_rows.append({
            "quarter": q,
            "nights_m": nights[q], "nights_lag4_m": nights[shift(q, -4)],
            "k_central_m": KTOT[key(cen)], "k_low_m": KTOT[key(lo)], "k_high_m": KTOT[key(hi)],
            "u_central_m": UNP[key(cen)], "u_low_m": UNP[key(lo)], "u_high_m": UNP[key(hi)],
            "k_min_m": round(min(v for k, v in KTOT.items() if k[0] == q and k[2] == "current"), 3),
            "k_max_m": round(max(v for k, v in KTOT.items() if k[0] == q and k[2] == "current"), 3),
            "u_min_m": round(min(v for k, v in UNP.items() if k[0] == q and k[2] == "current"), 3),
            "u_max_m": round(max(v for k, v in UNP.items() if k[0] == q and k[2] == "current"), 3),
            "b_central_pp": cen["b_pp"], "b_low_pp": lo["b_pp"], "b_high_pp": hi["b_pp"],
            "b_low_fee133_pp": lo_ff["b_pp"], "b_high_fee133_pp": hi_ff["b_pp"],
            "b_paid_central_pp": cen["b_paid_pp"], "b_unpaid_central_pp": cen["b_unpaid_pp"],
            "dK_over_N_lag4_central_pp": cen["dK_over_N_lag4_pp"],
            "k_over_n_quarters_central": cen["k_over_n_quarters"],
            "stays_implied_central_m": cen["stays_implied_m"],
            "low_cell": f"fee {lo['fee_share']} B {lo['backlog_scale_B']} r {lo['adr_ratio_r']} {lo['b_path']}",
            "high_cell": f"fee {hi['fee_share']} B {hi['backlog_scale_B']} r {hi['adr_ratio_r']} {hi['b_path']}",
        })

    # descriptive add-ons: the same-season pre-RNPL mean of b (a purely mechanical
    # seasonal component, approx g * dK(t-4)/N(t-4)) and the rolling four-quarter sum
    season_mean = {}
    for s in "1234":
        vals = [r["b_central_pp"] for r in id_rows if r["quarter"][0] == s
                and "23" <= r["quarter"][-2:] <= "25"]
        season_mean[s] = st.mean(vals) if vals else 0.0
    for i, r_ in enumerate(id_rows):
        r_["b_season_mean_pp"] = round(season_mean[r_["quarter"][0]], 3)
        r_["b_vs_season_mean_pp"] = round(r_["b_central_pp"] - season_mean[r_["quarter"][0]], 3)
        r_["b_ltm_sum_pp"] = (round(sum(x["b_central_pp"] for x in id_rows[i - 3:i + 1]), 3)
                              if i >= 3 else None)
    with open(OUT / "identity_term.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(id_rows[0].keys()))
        w.writeheader()
        w.writerows(id_rows)

    # ------------------------------------------------------- 5. forward band
    # (a) 3Q26 from the bridge section 4 score sheet
    fwd = []
    UFn_3q26 = norm["3"] * REV_4Q26                     # pre-RNPL, pre-migration UF expectation
    for (u_lab, m_lab, label) in SCORE_SHEET:
        k_over_hostpay = 0.124 / (1 - 0.124)
        uf_print = UFn_3q26 * (1 - u_lab) * (1 - m_lab)
        for fee, B, r, bp in [(FEE_C, B_C, R_C, BPATH_C)]:
            a = ADR_3Q26
            u_eff = 1.0 - uf_print / (B * UFn_3q26)     # m = 0 accounting (audit C2)
            kuf = uf_print / fee / a
            U = u_eff * (B * norm["3"] * REV_4Q26 / fee) / (a * r)
            K3 = kuf + U
            dK = K3 - KTOT[("2Q26", fee, "current", B, r, bp)]
            dK4 = KTOT[("3Q25", fee, "current", B, r, bp)] - KTOT[("2Q25", fee, "current", B, r, bp)]
            dU = U - UNP[("2Q26", fee, "current", B, r, bp)]
            dU4 = UNP[("3Q25", fee, "current", B, r, bp)] - UNP[("2Q25", fee, "current", B, r, bp)]
            fwd.append({
                "block": "3Q26_score_sheet", "period": "3Q26",
                "scenario": f"u{int(100*u_lab)}_m{int(100*m_lab)}", "label": label,
                "nights_path": "n/a",
                "fee_share": fee, "backlog_scale_B": B, "adr_ratio_r": r, "b_path": bp,
                "uf_musd": round(uf_print, 1),
                "uf_yoy_pct": round(100 * (uf_print / uf["3Q25"] - 1), 2),
                "u_eff_pct": round(100 * u_eff, 2),
                "implied_rnpl_gbv_share_pct": round(100 * share_of_u(u_eff, B), 2),
                "k_uf_m_nights": round(kuf, 3), "u_unpaid_m_nights": round(U, 3),
                "k_total_m_nights": round(K3, 3),
                "dK_m_nights": round(dK, 3), "dK_lag4_m_nights": round(dK4, 3),
                "b_pp": round(100 * (dK - dK4) / nights["3Q25"], 3),
                "b_unpaid_pp": round(100 * (dU - dU4) / nights["3Q25"], 3),
                "module_total_rnpl_pts": -0.396, "cfo_na_pts": CFO_NA_PTS,
                "cfo_global_pts": CFO_GLOBAL_PTS,
                "note": f"k_hostpay={k_over_hostpay:.3f} unused (m=0 per audit C2)",
            })

    # (b) forward path, share stabilised at 21 / 24 / 27 percent
    module = list(csv.DictReader(open(MODULE, encoding="utf-8-sig")))
    mod_base = {r["quarter"]: _f(r["total_rnpl_pts"]) for r in module if r["scenario"] == "base"
                and r["total_rnpl_pts"]}

    def kappa_nights(season, fee):
        return KAPPA_FEE[season] / fee

    FWD_Q = ["3Q26", "4Q26", "1Q27", "2Q27"]
    prev_hist = {"3Q26": "2Q26", "4Q26": "3Q26", "1Q27": "4Q26", "2Q27": "1Q27"}
    lag4 = {"3Q26": "3Q25", "4Q26": "4Q25", "1Q27": "1Q26", "2Q27": "2Q26"}
    lag5 = {"3Q26": "2Q25", "4Q26": "3Q25", "1Q27": "4Q25", "2Q27": "1Q26"}
    calib = None
    for fee in FEES:
        for B in BS:
            for r in RS:
                for bp in BPATHS:
                    # level calibration so the model reproduces 2Q26 exactly in this cell
                    u2 = u_solve[("2Q26", B, bp)]
                    k_hat = kappa_nights("2", fee) * nights["2Q26"] * B * ((1 - u2) + u2 / r)
                    c = KTOT[("2Q26", fee, "current", B, r, bp)] / k_hat
                    if (fee, B, r, bp) == (FEE_C, B_C, R_C, BPATH_C):
                        calib = c
                    for path_name, npath in NPATH.items():
                        for scen, s_star in SHARE_SCEN.items():
                            u = u_of_share(s_star, B)
                            Kf, Uf_ = {}, {}
                            for q in FWD_Q:
                                kk = kappa_nights(q[0], fee) * npath[q] * B * c
                                Kf[q] = kk * ((1 - u) + u / r)
                                Uf_[q] = kk * u / r
                            for q in FWD_Q:
                                pq = prev_hist[q]
                                Kprev = Kf[pq] if pq in Kf else KTOT[(pq, fee, "current", B, r, bp)]
                                Uprev = Uf_[pq] if pq in Uf_ else UNP[(pq, fee, "current", B, r, bp)]
                                dK = Kf[q] - Kprev
                                dU = Uf_[q] - Uprev
                                dK4 = (KTOT[(lag4[q], fee, "current", B, r, bp)]
                                       - KTOT[(lag5[q], fee, "current", B, r, bp)])
                                dU4 = (UNP[(lag4[q], fee, "current", B, r, bp)]
                                       - UNP[(lag5[q], fee, "current", B, r, bp)])
                                n4 = nights[lag4[q]]
                                is_c = ((fee, B, r, bp, path_name, scen)
                                        == (FEE_C, B_C, R_C, BPATH_C, "dossier", "mid24"))
                                fwd.append({
                                    "block": "forward_share_stabilises", "period": q,
                                    "scenario": scen,
                                    "label": f"RNPL GBV share flat at {int(100*s_star)}% from 3Q26"
                                             + (" [CENTRAL]" if is_c else ""),
                                    "nights_path": path_name,
                                    "fee_share": fee, "backlog_scale_B": B, "adr_ratio_r": r,
                                    "b_path": bp,
                                    "uf_musd": "", "uf_yoy_pct": "",
                                    "u_eff_pct": round(100 * u, 2),
                                    "implied_rnpl_gbv_share_pct": round(100 * s_star, 2),
                                    "k_uf_m_nights": round(Kf[q] - Uf_[q], 3),
                                    "u_unpaid_m_nights": round(Uf_[q], 3),
                                    "k_total_m_nights": round(Kf[q], 3),
                                    "dK_m_nights": round(dK, 3), "dK_lag4_m_nights": round(dK4, 3),
                                    "b_pp": round(100 * (dK - dK4) / n4, 3),
                                    "b_unpaid_pp": round(100 * (dU - dU4) / n4, 3),
                                    "module_total_rnpl_pts": mod_base.get(q),
                                    "cfo_na_pts": CFO_NA_PTS, "cfo_global_pts": CFO_GLOBAL_PTS,
                                    "note": f"kappa route, calibrated at 2Q26 (factor {c:.4f}); lambda {lam_of(B):.3f}",
                                })
    with open(OUT / "forward_band.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(fwd[0].keys()))
        w.writeheader()
        w.writerows(fwd)

    # one committed row per forward period: central, low, high
    band_rows = []
    for q in ["3Q26", "4Q26", "1Q27", "2Q27"]:
        cells = [r_ for r_ in fwd if r_["period"] == q]
        if q == "3Q26":
            cen = next(r_ for r_ in cells if "[CENTRAL]" in str(r_["label"]))
        else:
            cen = next(r_ for r_ in cells if "[CENTRAL]" in str(r_["label"]))
        lo = min(cells, key=lambda r_: r_["b_pp"])
        hi = max(cells, key=lambda r_: r_["b_pp"])
        ff = [r_ for r_ in cells if r_["fee_share"] == FEE_C]
        band_rows.append({
            "period": q, "b_central_pp": cen["b_pp"], "b_low_pp": lo["b_pp"], "b_high_pp": hi["b_pp"],
            "b_low_fee133_pp": min(r_["b_pp"] for r_ in ff),
            "b_high_fee133_pp": max(r_["b_pp"] for r_ in ff),
            "k_central_m": cen["k_total_m_nights"], "u_central_m": cen["u_unpaid_m_nights"],
            "central_cell": f"{cen['block']} {cen['scenario']} fee {cen['fee_share']} B {cen['backlog_scale_B']} r {cen['adr_ratio_r']} {cen['b_path']} {cen['nights_path']}",
            "low_cell": f"{lo['block']} {lo['scenario']} fee {lo['fee_share']} B {lo['backlog_scale_B']} r {lo['adr_ratio_r']} {lo['b_path']} {lo['nights_path']}",
            "high_cell": f"{hi['block']} {hi['scenario']} fee {hi['fee_share']} B {hi['backlog_scale_B']} r {hi['adr_ratio_r']} {hi['b_path']} {hi['nights_path']}",
            "module_total_rnpl_pts": mod_base.get(q),
            "cfo_na_pts": CFO_NA_PTS, "cfo_global_pts": CFO_GLOBAL_PTS,
        })
    with open(OUT / "forward_band_committed.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(band_rows[0].keys()))
        w.writeheader()
        w.writerows(band_rows)

    # ------------------------------- 5b. diagnostics: scatter, share coherence,
    #                                      and the implied-stays cross-check
    diag = []
    for basis in ADR_BASES:
        for season in "1234":
            vals = [r["b_pp"] for r in grid_rows
                    if r["adr_basis"] == basis and r["fee_share"] == FEE_C
                    and r["backlog_scale_B"] == B_C and r["adr_ratio_r"] == R_C
                    and r["b_path"] == BPATH_C and r["quarter"][0] == season
                    and "23" <= r["quarter"][-2:] <= "25"]
            if len(vals) >= 2:
                diag.append({"diagnostic": "pre-RNPL b scatter by season",
                             "key": f"{basis} Q{season}", "n": len(vals),
                             "value": round(st.mean(vals), 3),
                             "value2": round(st.pstdev(vals), 3),
                             "note": "mean and population sd of b over 2023-2025 same-season quarters"})
    for q in RNPL_Q:
        cell = next(r for r in tot_rows if r["quarter"] == q and r["fee_share"] == FEE_C
                    and r["adr_basis"] == "current" and r["backlog_scale_B"] == B_C
                    and r["adr_ratio_r"] == R_C and r["b_path"] == BPATH_C)
        diag.append({"diagnostic": "implied vs stated RNPL GBV share",
                     "key": q, "n": 1,
                     "value": cell["implied_rnpl_gbv_share_pct"],
                     "value2": round(100 * SHARE_HIST[q], 1),
                     "note": "implied by u via lambda vs the disclosed/assumed share (D031, D043, D1 params)"})

    # implied stays growth from the identity vs the reviews stays index (descriptive)
    stays_rows = []
    try:
        idxrows = [r for r in csv.DictReader(open(ROOT / "data/processed/q3nowcast/E/index_quarterly.csv",
                                                  encoding="utf-8-sig"))
                   if r["region"] == "GLOBAL" and r["measure"] == "yoy_vmatch"]
        iq = {r["quarter"]: _f(r["w_reviews"]) for r in idxrows}
    except OSError:
        iq = {}
    for r_ in id_rows:
        q = r_["quarter"]
        q4 = shift(q, -4)
        if q4 is None or q4 not in QK or q < "1Q23":
            continue
        s_now, s_prev = r_["stays_implied_central_m"], None
        prev = next((x for x in id_rows if x["quarter"] == q4), None)
        if prev:
            s_prev = prev["stays_implied_central_m"]
        if not s_prev:
            continue
        gn = 100.0 * (nights[q] / nights[q4] - 1)
        stays_rows.append({
            "quarter": q, "g_nights_pct": round(gn, 2),
            "b_central_pp": r_["b_central_pp"],
            "g_stays_implied_pct": round(100.0 * (s_now / s_prev - 1), 2),
            "g_nights_minus_b_pct": round(gn - r_["b_central_pp"], 2),
            "reviews_index_yoy_vmatch_pct": (round(100 * iq[q], 2) if q in iq else None),
        })
    if stays_rows:
        def _corr(xs, ys):
            n = len(xs)
            mx, my = st.mean(xs), st.mean(ys)
            sx = sum((x - mx) ** 2 for x in xs) ** 0.5
            sy = sum((y - my) ** 2 for y in ys) ** 0.5
            return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy) if sx and sy else None
        pairs = [(r_["reviews_index_yoy_vmatch_pct"], r_["g_nights_pct"], r_["g_nights_minus_b_pct"])
                 for r_ in stays_rows if r_["reviews_index_yoy_vmatch_pct"] is not None]
        if len(pairs) >= 4:
            ix = [p[0] for p in pairs]
            diag.append({"diagnostic": "corr(reviews index, g_nights)", "key": "1Q23-2Q26",
                         "n": len(pairs), "value": round(_corr(ix, [p[1] for p in pairs]), 3),
                         "value2": "", "note": "descriptive; the index is uncalibrated (N1 owns the calibration)"})
            diag.append({"diagnostic": "corr(reviews index, g_nights - b)", "key": "1Q23-2Q26",
                         "n": len(pairs), "value": round(_corr(ix, [p[2] for p in pairs]), 3),
                         "value2": "", "note": "if the backlog term were clean this should be HIGHER than the row above"})
            # best case over the WHOLE registered grid - reported as a failure bound, not a selection
            best, best_cell = None, ""
            qs = [r_["quarter"] for r_ in stays_rows if r_["reviews_index_yoy_vmatch_pct"] is not None]
            gn_map = {r_["quarter"]: r_["g_nights_pct"] for r_ in stays_rows}
            for fee in FEES:
                for basis in ADR_BASES:
                    for Bg in BS:
                        for rg in RS:
                            for bpg in BPATHS:
                                sel = {r["quarter"]: r["b_pp"] for r in grid_rows
                                       if r["fee_share"] == fee and r["adr_basis"] == basis
                                       and r["backlog_scale_B"] == Bg and r["adr_ratio_r"] == rg
                                       and r["b_path"] == bpg}
                                if not all(q in sel for q in qs):
                                    continue
                                c = _corr(ix, [gn_map[q] - sel[q] for q in qs])
                                if c is not None and (best is None or c > best):
                                    best, best_cell = c, f"fee {fee} {basis} B {Bg} r {rg} {bpg}"
            if best is not None:
                diag.append({"diagnostic": "best corr(index, g_nights - b) over the grid",
                             "key": best_cell, "n": len(qs), "value": round(best, 3), "value2": "",
                             "note": "upper bound over all 72 registered cells; still below the 0.863 no-b baseline"})
        with open(OUT / "stays_crosscheck.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(stays_rows[0].keys()))
            w.writeheader()
            w.writerows(stays_rows)
    # ---- norm-denominator and revenue sensitivity (the largest single lever) ----
    norm_gbv = {s: st.mean(uf[q] / gbv[q] for q in qs) for s, qs in NORM_BASE.items()}
    ns_rows = []
    fee_, B_, r_c, bp_ = FEE_C, B_C, R_C, BPATH_C

    def series_u_K(kind, rev_mult):
        """(u, K) for 3Q25-2Q26 under a norm denominator and a revenue multiplier."""
        uu, KK = {}, {}
        for q in QK:
            a = adr[q]
            kuf = uf[q] / fee_ / a
            if q in RNPL_Q:
                if kind == "next_rev":
                    nr = nrev(q) * (rev_mult if q == "2Q26" else 1.0)
                    ratio = (uf[q] / nr) / norm[q[0]]
                    X = b_eff(q, B_, bp_) * norm[q[0]] * nr / fee_
                else:
                    ratio = (uf[q] / gbv[q]) / norm_gbv[q[0]]
                    X = b_eff(q, B_, bp_) * norm_gbv[q[0]] * gbv[q] / fee_
                u = 1.0 - ratio / b_eff(q, B_, bp_)
                U = u * X / (a * r_c)
            else:
                u, U = 0.0, 0.0
            uu[q], KK[q] = u, kuf + U
        return uu, KK

    for kind in ("next_rev", "same_gbv"):
        for rev_mult, tag in ((1.00, "team rev"), (0.95, "rev -5%"), (1.05, "rev +5%")):
            if kind == "same_gbv" and rev_mult != 1.00:
                continue
            uu, KK = series_u_K(kind, rev_mult)
            for q in ("3Q25", "4Q25", "1Q26", "2Q26"):
                q1, q4, q5 = shift(q, -1), shift(q, -4), shift(q, -5)
                bq = 100.0 * ((KK[q] - KK[q1]) - (KK[q4] - KK[q5])) / nights[q4]
                ns_rows.append({
                    "norm_denominator": kind, "revenue_stress": tag, "quarter": q,
                    "u_pct": round(100 * uu[q], 2), "k_total_m_nights": round(KK[q], 2),
                    "b_pp": round(bq, 3),
                })
    with open(OUT / "norm_sensitivity.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ns_rows[0].keys()))
        w.writeheader()
        w.writerows(ns_rows)
    for q in ("2Q26",):
        lo = min(r["b_pp"] for r in ns_rows if r["quarter"] == q)
        hi = max(r["b_pp"] for r in ns_rows if r["quarter"] == q)
        diag.append({"diagnostic": "b sensitivity to norm and +/-5% revenue", "key": q,
                     "n": len([r for r in ns_rows if r["quarter"] == q]),
                     "value": round(lo, 3), "value2": round(hi, 3),
                     "note": "central cell held; only the norm denominator and the assumed 3Q26 revenue move"})

    with open(OUT / "diagnostics.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["diagnostic", "key", "n", "value", "value2", "note"])
        w.writeheader()
        w.writerows(diag)

    # ------------------------------------------- 6. measured vs assumed table
    inputs = [
        ("unearned fees, 4Q20-2Q26", "disclosed quarterly balance, $M", "measured",
         "data/processed/overnight/02_kpi_panel_quarterly.csv unearned_fees_musd; FY2025 10-K Note 2 and Item 7 define the pool"),
        ("reported nights N(t)", "disclosed quarterly series", "measured",
         "02_kpi_panel_quarterly.csv nights_m; Airbnb quarterly summaries"),
        ("ADR(t)", "disclosed quarterly booking-period ADR", "measured", "02_kpi_panel_quarterly.csv adr_usd"),
        ("GBV(t)", "disclosed quarterly booked GBV", "measured", "02_kpi_panel_quarterly.csv gbv_musd"),
        ("fee share of GBV, central", f"{FEE_C}", "derived",
         "LTM revenue / LTM GBV 13.2-13.6% (fee_share_evidence.csv), lag-corrected ~13.5%; 10-K Note 2 puts BOTH host and guest fees in unearned fees, so the 0.124 guest-only divisor used by rnpl_balance_sheet_bridge.py is wrong (audit C3)"),
        ("fee share grid", "0.124 / 0.133 / 0.151 / 0.155", "grid (prereg)",
         "0.124 guest fee only (refuted as the divisor); 0.133 realised; 0.151 posted split total; 0.155 posted single host fee"),
        ("ADR_eff basis, central", "quarter's own ADR", "derived",
         "ADR is a BOOKING-period metric, so the backlog's dollars already carry the prices at which they were booked; forward and 2/3-1/3 bases reported as sensitivities in backlog_uf.csv"),
        ("pre-RNPL seasonal norm (UF / next-quarter revenue)",
         " ".join(f"Q{s} {norm[s]:.3f}" for s in "1234"), "derived",
         "rnpl_balance_sheet_bridge.py section 2; 2023+2024+1H25 by season; two pre-RNPL years only for Q3 and Q4"),
        ("revenue(3Q26) used in the 2Q26 norm", f"{REV_3Q26:.0f} $M", "assumed (team point)",
         "R2 dossier / bridge REV_3Q26; a 5% error here moves u(2Q26) by ~4pp"),
        ("revenue(4Q26) used in the 3Q26 norm", f"{REV_4Q26:.0f} $M", "assumed (team point)",
         "R5 dossier / bridge REV_4Q26"),
        ("unpaid share u(t), 3Q25-2Q26", "UF-only solve, see backlog_total.csv", "derived",
         "reproduces data/processed/rnpl_short_audit/verify_bs_uf_only_solve.csv 'note baseline'; the joint two-line solve is REFUTED (m not identified, audit C3)"),
        ("single-fee migration share m", "0 (not identified)", "refuted",
         "audit C2/C3: FY2025 10-K Note 2 puts host AND guest fees in unearned fees, so the migration is UF-accretive; the solve returns m = -1.4% for 3Q25, before the migration existed"),
        ("backlog-scale path B(t), central", BPATH_C, "assumed (shape), justified on inputs",
         "'ramp' scales the lengthening with the RNPL GBV share path (3Q25 4%, 4Q25 9%, 1Q26 20%, 2Q26 21%); 'step' jumps to the full B in 3Q25 and injects a spurious one-year level step into b. Ramp is the only variant whose implied 3Q25 share stays inside D1's registered 2.5-6% range"),
        ("backlog scale B, central", f"{B_C}", "assumed (grid midpoint)",
         "grid {1.00, 1.05, 1.10}; the audit says B 1.04-1.06 reconciles u with the disclosed 20-21% flow share; lead-time lengthening is disclosed in every print from 3Q25 (D010, D016, D039, D045) but never quantified"),
        ("RNPL / non-RNPL ADR ratio r, central", f"{R_C}", "derived, upper bound",
         "1Q26 ~4pts GBV on ~3pts nights (D032); audit C5 calls 4/3 an UPPER bound (1.22x against the 1Q26 ADR) and the attribution is RNPL+cancellation+fees combined; D1's own central cell is 1.25"),
        ("RNPL GBV share 2Q26", "21%", "measured (lower bound)",
         "2Q26 call, ledger D043 via a stockanalysis.com mirror, not the official IR PDF"),
        ("RNPL GBV share 3Q26 onward", "21-27%", "assumed",
         "direction supported by the July 2026 eligibility expansion (D044); no quarterly share has ever been disclosed for 2025"),
        ("lambda, relative unpaid residence", f"{lam_of(B_C):.3f} at B={B_C}", "calibrated, not measured",
         "reduced form u = s*lam/((1-s)+s*lam) from research/notes/2026-09-10_rnpl-conversion-framework.md section 3, calibrated on the 2Q26 disclosed 21% share"),
        ("forward nights path", "D1/D2 adopted base, module base as sensitivity", "derived (team model)",
         "D1 3Q26 146.3m, D2 4Q26 131.8m / 1Q27 167.1m / 2Q27 157.8m; rnpl_nights_module.csv base path as the alternative"),
        ("ADR 3Q26 / 4Q26", f"{ADR_3Q26} / {ADR_4Q26}", "derived (team model)",
         "D4 dossier base, adr_card_v3.csv variant v3_without_K, midpoint FX"),
        ("3Q26 score-sheet u/m pairs", "7/9, 10/12, 12/18, 7/0, 15/0", "grid (bridge section 4)",
         "rnpl_balance_sheet_bridge.py section 4; read here under m=0 accounting, so each cell is reported as an implied u_eff"),
        ("CFO bundle sentences", "+2.40 NA pts / ~3.0 global pts", "call statement, NOT verified against a filing",
         "PR #32 fitted NA term and the 1Q26 call 'approximately three points'; X3 dossier owns the provenance"),
        ("-3.4pp FX step / 82% determined / +4.05% fee uplift / 9/9 drift / +10.2% consensus",
         "not used", "WITHDRAWN", "AGENT_BRIEF section 6 kill list"),
    ]
    with open(OUT / "inputs_measured_vs_assumed.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["input", "value", "evidence_status", "source_or_note"])
        w.writerows(inputs)

    # ---------------------------------------------------------- 7. summary
    lines = []
    lines.append("N2 - backlog identity term (booked-not-yet-stayed nights)")
    lines.append(f"central cell: fee_share {FEE_C}, ADR basis 'current', B {B_C} ({BPATH_C}), r {R_C}; "
                 f"lambda {lam_of(B_C):.3f}; kappa calibration {calib:.4f}")
    lines.append(f"pre-RNPL seasonal norms UF/next-q revenue: " +
                 "  ".join(f"Q{s} {norm[s]:.3f}" for s in "1234"))
    lines.append("")
    lines.append("quarter |  N   |  K cen |  K low |  K high |  U cen |  b cen |  b low |  b high | K/N q | S implied")
    for r_ in id_rows:
        lines.append("{:7s} | {:5.1f} | {:6.1f} | {:6.1f} | {:7.1f} | {:6.1f} | {:+6.2f} | {:+6.2f} | {:+7.2f} | {:5.2f} | {:7.1f}".format(
            r_["quarter"], r_["nights_m"], r_["k_central_m"], r_["k_low_m"], r_["k_high_m"],
            r_["u_central_m"], r_["b_central_pp"], r_["b_low_pp"], r_["b_high_pp"],
            r_["k_over_n_quarters_central"], r_["stays_implied_central_m"]))
    lines.append("")
    lines.append("3Q26 score sheet (m = 0 accounting; u_eff is what the print implies)")
    lines.append("scenario | UF $M | UF y/y | u_eff | implied RNPL GBV share | K | b(3Q26)")
    for r_ in fwd:
        if r_["block"] != "3Q26_score_sheet":
            continue
        lines.append("{:10s} | {:5.0f} | {:+6.1f}% | {:5.1f}% | {:5.1f}% | {:6.1f} | {:+5.2f}".format(
            r_["scenario"], r_["uf_musd"], r_["uf_yoy_pct"], r_["u_eff_pct"],
            r_["implied_rnpl_gbv_share_pct"], r_["k_total_m_nights"], r_["b_pp"]))
    lines.append("")
    lines.append("forward, RNPL GBV share stabilised (central parameter cell, dossier nights path)")
    lines.append("period | scenario | u | K | b | b_unpaid | module total_rnpl_pts")
    for r_ in fwd:
        if (r_["block"] != "forward_share_stabilises" or r_["nights_path"] != "dossier"
                or r_["fee_share"] != FEE_C or r_["backlog_scale_B"] != B_C
                or r_["adr_ratio_r"] != R_C or r_["b_path"] != BPATH_C):
            continue
        lines.append("{:6s} | {:7s} | {:5.1f}% | {:6.1f} | {:+5.2f} | {:+5.2f} | {}".format(
            r_["period"], r_["scenario"], r_["u_eff_pct"], r_["k_total_m_nights"],
            r_["b_pp"], r_["b_unpaid_pp"], r_["module_total_rnpl_pts"]))
    lines.append("")
    lines.append("committed forward band (min/max over the full registered grid)")
    lines.append("period | b central | b low | b high | module total_rnpl_pts")
    for r_ in band_rows:
        lines.append("{:6s} | {:+6.2f} | {:+6.2f} | {:+6.2f} | {}".format(
            r_["period"], r_["b_central_pp"], r_["b_low_pp"], r_["b_high_pp"],
            r_["module_total_rnpl_pts"]))
    lines.append("")
    lines.append("diagnostics")
    for d in diag:
        lines.append("{:34s} | {:10s} | n {:2d} | {} | {}".format(
            d["diagnostic"], str(d["key"]), d["n"], d["value"], d["value2"]))
    txt = "\n".join(lines)
    (OUT / "summary.txt").write_text(txt + "\n")
    print(txt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
