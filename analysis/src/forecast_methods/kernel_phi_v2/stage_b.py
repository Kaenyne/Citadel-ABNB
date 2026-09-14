"""Stage B — the PAID backlog and its conversion into next-quarter revenue.

Definitions, taken from the 10-Q / 10-K language as quoted in
`docs/revenue-forecast-strategy/01_ground-truth/03_insider_mechanics.md` 1.1 and 1.3
and in `docs/rnpl-short-audit/04_balance-sheet-verification.md` C2:

  unearned fees  "Service fees collected from customers prior to check-in are
                 recorded as unearned fees on the consolidated balance sheets...
                 not considered contract balances, as they are subject to refund
                 in the event of a cancellation."  FY2025 10-K Note 2 adds:
                 "Host and guest fees are recorded as cash with a corresponding
                 amount in unearned fees."   -> FEE-denominated; it is the
                 already-collected part of FUTURE REVENUE.

  funds payable  "The Company records guest payments, net of service fees, as
                 funds receivable and amounts held on behalf of customers with a
                 corresponding amount in funds payable and amounts payable to
                 customers when cash is received in advance of check-in."
                 -> BOOKING-AMOUNT denominated, the host's share held.  Funds
                 receivable == funds payable on the face of the balance sheet, so
                 only the level is informative.

  PAID BACKLOG = unearned fees + funds payable.

The circular `unearned_fees_restated = reported / (1 - d_q)` series is NOT used.
"""
from __future__ import annotations

import os
import numpy as np
import pandas as pd

from common import OUT, SEASON_NAME, GUIDE_3Q26_MID
from phi_fit import phi_of

# quarter-ends at which each regime starts
RNPL_FROM = "2025Q3"      # US launch, beginning of 3Q25
SINGLE_FEE_FROM = "2025Q4"  # October 2025 PMS / December 2025 remaining hosts
NORM_WINDOW = ("2022Q1", "2025Q2")   # 2022 - 1H25, pre-RNPL


def build(panel: pd.DataFrame, fit, kmax: int = 4) -> pd.DataFrame:
    d = panel.copy()
    d["rnpl_era"] = d["q"] >= RNPL_FROM
    d["single_fee_era"] = d["q"] >= SINGLE_FEE_FROM
    d["next_season"] = ((d["season"] % 4) + 1).astype(int)

    # Kernel-implied allocation of the FEE stock standing at quarter-end q.
    #   Bookings made in q-j still release  sum_{k>j} phi_k  of their revenue after q.
    #   The piece that checks in during q+i is  phi_{j+i} , and it is monetised at the
    #   seasonal conversion of the quarter it lands in, c_{s(q+i)}.
    #   R_i = sum_j phi_{j+i} * G_{q-j}   ,   fees_i = c_{s(q+i)}/100 * R_i
    rel, tot, carried = [], [], []
    for _, row in d.iterrows():
        g = [row.get(f"gbv_l{j}", np.nan) for j in range(0, kmax)]   # G_q, G_{q-1}, ...
        if any(not np.isfinite(x) for x in g):
            rel.append(np.nan); tot.append(np.nan); carried.append(np.nan); continue
        s0 = int(row["season"])
        fees = []
        for i in range(1, kmax + 1):
            s_i = ((s0 + i - 1) % 4) + 1
            phi_i = phi_of(fit, s_i)
            R_i = sum(phi_i[j + i] * g[j] for j in range(kmax) if j + i <= kmax)
            fees.append(fit["c"][s_i] / 100.0 * R_i)
        rel.append(fees[0] / (fit["c"][((s0) % 4) + 1] / 100.0))     # R_1 in GBV terms
        tot.append(float(np.sum(fees)))                              # total fee stock, $M
        carried.append(fees[0])                                      # fees releasing into q+1
    d["kernel_release_base_musd"] = rel
    d["kernel_fee_stock_musd"] = tot
    d["carried_next_revenue_musd"] = carried
    d["alloc_factor"] = np.array(carried) / np.array(tot)

    # B = share of next-quarter revenue driven by GBV BOOKED on or before quarter-end
    d["booked_share_next"] = d["carried_next_revenue_musd"] / d["next_revenue_musd"]
    # P = share of next-quarter revenue whose FEE is already collected (on the ledger)
    d["ledger_share_next"] = d["cov_uf"] * d["alloc_factor"]
    d["wedge_booked_minus_paid"] = d["booked_share_next"] - d["ledger_share_next"]
    d["implied_paid_share_of_booked"] = d["ledger_share_next"] / d["booked_share_next"]
    d["implied_unpaid_share_u"] = 1.0 - d["implied_paid_share_of_booked"]
    d["inquarter_share_next"] = 1.0 - d["booked_share_next"]
    # stock-only version: needs NO next-quarter revenue at all, so it is available
    # at 2Q26 without touching the 3Q26 guide.  p = collected fees / model fee stock.
    d["prepay_share_stock"] = d["unearned_fees_musd"] / d["kernel_fee_stock_musd"]
    d["unpaid_share_stock_u"] = 1.0 - d["prepay_share_stock"]
    return d


def norms(d: pd.DataFrame) -> pd.DataFrame:
    w = d[(d["q"] >= NORM_WINDOW[0]) & (d["q"] <= NORM_WINDOW[1])]
    rows = []
    for s, g in w.groupby("season"):
        for col, lab in [("cov_uf", "unearned fees / next-Q revenue"),
                         ("cov_fp", "funds payable / next-Q revenue"),
                         ("cov_total", "paid backlog / next-Q revenue"),
                         ("ledger_share_next", "ledger share of next-Q revenue (paid)"),
                         ("booked_share_next", "booked share of next-Q revenue"),
                         ("wedge_booked_minus_paid", "wedge (booked - paid)"),
                         ("implied_unpaid_share_u", "implied unpaid share u"),
                         ("prepay_share_stock", "prepaid share of the model fee stock"),
                         ("unpaid_share_stock_u", "unpaid share of the model fee stock")]:
            v = g[col].dropna()
            rows.append(dict(season=SEASON_NAME[s], metric=col, metric_label=lab,
                             n=len(v), mean=float(v.mean()) if len(v) else np.nan,
                             sd=float(v.std(ddof=1)) if len(v) > 1 else np.nan,
                             lo=float(v.min()) if len(v) else np.nan,
                             hi=float(v.max()) if len(v) else np.nan,
                             window=f"{NORM_WINDOW[0]}-{NORM_WINDOW[1]}"))
    return pd.DataFrame(rows)


def run(panel: pd.DataFrame, fit, kmax: int = 4):
    os.makedirs(OUT, exist_ok=True)
    d = build(panel, fit, kmax=kmax)
    cols = ["label", "q", "season_name", "unearned_fees_musd",
            "funds_held_for_clients_musd", "paid_backlog_musd", "gbv_musd",
            "revenue_musd", "next_revenue_musd", "cov_uf", "cov_fp", "cov_total",
            "alloc_factor", "booked_share_next", "ledger_share_next",
            "wedge_booked_minus_paid", "implied_unpaid_share_u",
            "kernel_fee_stock_musd", "prepay_share_stock", "unpaid_share_stock_u",
            "inquarter_share_next", "unearned_fees_yoy_pct", "funds_held_yoy_pct",
            "paid_backlog_yoy_pct", "gbv_yoy_pct", "revenue_yoy_pct",
            "rnpl_era", "single_fee_era"]
    b1 = d[cols].copy()
    b1.to_csv(os.path.join(OUT, "B1_paid_backlog_panel.csv"), index=False)

    nm = norms(d)
    nm.to_csv(os.path.join(OUT, "B2_coverage_norms.csv"), index=False)

    # deviations of every quarter from its own pre-RNPL seasonal norm
    key = nm.set_index(["season", "metric"])["mean"].to_dict()
    dev = []
    for _, r in d.iterrows():
        s = SEASON_NAME.get(int(r["season"]))
        for col in ("cov_uf", "cov_fp", "cov_total", "ledger_share_next",
                    "booked_share_next", "implied_unpaid_share_u",
                    "prepay_share_stock", "unpaid_share_stock_u"):
            n0 = key.get((s, col), np.nan)
            if not np.isfinite(r[col]) or not np.isfinite(n0):
                continue
            dev.append(dict(label=r["label"], q=r["q"], season=s, metric=col,
                            actual=float(r[col]), norm=float(n0),
                            dev_abs=float(r[col] - n0),
                            dev_pct_of_norm=100.0 * float(r[col] / n0 - 1.0),
                            rnpl_era=bool(r["rnpl_era"]),
                            single_fee_era=bool(r["single_fee_era"])))
    b3 = pd.DataFrame(dev)
    b3.to_csv(os.path.join(OUT, "B3_coverage_deviations.csv"), index=False)

    # 2Q26 quarter-end applied to the 3Q26 GUIDE MIDPOINT (marked as a guide, not a print)
    r26 = d[d["q"] == "2026Q2"].iloc[0]
    live = pd.DataFrame([dict(
        quarter_end="2Q26", basis="3Q26 GUIDE MIDPOINT (not printed)",
        next_revenue_musd=GUIDE_3Q26_MID,
        unearned_fees_musd=r26["unearned_fees_musd"],
        funds_payable_musd=r26["funds_held_for_clients_musd"],
        paid_backlog_musd=r26["paid_backlog_musd"],
        cov_uf=r26["unearned_fees_musd"] / GUIDE_3Q26_MID,
        cov_fp=r26["funds_held_for_clients_musd"] / GUIDE_3Q26_MID,
        cov_total=r26["paid_backlog_musd"] / GUIDE_3Q26_MID,
        alloc_factor=r26["alloc_factor"],
        ledger_share_next=r26["unearned_fees_musd"] / GUIDE_3Q26_MID * r26["alloc_factor"],
        booked_share_next=r26["carried_next_revenue_musd"] / GUIDE_3Q26_MID,
        prepay_share_stock=r26["prepay_share_stock"],
        unpaid_share_stock_u=r26["unpaid_share_stock_u"],
        norm_prepay_share_stock_Q2=key.get(("Q2", "prepay_share_stock"), np.nan),
        norm_unpaid_share_stock_Q2=key.get(("Q2", "unpaid_share_stock_u"), np.nan),
        norm_cov_uf_Q2=key.get(("Q2", "cov_uf"), np.nan),
        norm_ledger_share_Q2=key.get(("Q2", "ledger_share_next"), np.nan))])
    live["wedge_booked_minus_paid"] = live["booked_share_next"] - live["ledger_share_next"]
    live["implied_unpaid_share_u"] = 1.0 - live["ledger_share_next"] / live["booked_share_next"]
    live.to_csv(os.path.join(OUT, "B4_live_2q26_ledger.csv"), index=False)

    # B5 - the three-way decomposition of next-quarter revenue, by season.
    #      1 = paid-on-the-ledger + booked-but-unpaid + not-yet-booked
    rows = []
    for s in ("Q1", "Q2", "Q3", "Q4"):
        P = key.get((s, "ledger_share_next"), np.nan)
        B = key.get((s, "booked_share_next"), np.nan)
        rows.append(dict(quarter_end_season=s, window=f"{NORM_WINDOW[0]}-{NORM_WINDOW[1]}",
                         paid_on_ledger=P, booked_but_unpaid=B - P,
                         not_yet_booked_phi0=1 - B, booked_total=B, check=P + (B - P) + (1 - B)))
    lr = live.iloc[0]
    rows.append(dict(quarter_end_season="2Q26 (vs 3Q26 GUIDE mid, not a print)",
                     window="live", paid_on_ledger=float(lr["ledger_share_next"]),
                     booked_but_unpaid=float(lr["booked_share_next"] - lr["ledger_share_next"]),
                     not_yet_booked_phi0=float(1 - lr["booked_share_next"]),
                     booked_total=float(lr["booked_share_next"]), check=1.0))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "B5_three_way_decomposition.csv"), index=False)
    return d, nm, b3, live
