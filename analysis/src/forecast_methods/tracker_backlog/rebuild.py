"""(a) Rebuild the booked-base tracker: unearned fees, funds held, GBV, revenue,
y/y growth, quarterly since 4Q20, plus the identity that links them.

Identity (03_insider_mechanics.md sec 1.2, reproduced here algebraically; the terms
marked [not disclosed] cannot be populated from public data -- Airbnb discloses none
of gross bookings, cancellations, or the booking-to-check-in lag distribution
numerically):

  Nights_q       = GrossNights_q - SUM_{b<=q} CancelledNights(b,q) +/- Alterations_q   [not disclosed]
  GBV_q          = G_q - SUM_{b<=q} c(b,q)*G_b +/- Alterations_q                        [not disclosed]
  UnearnedFees_q = UnearnedFees_{q-1} + tau*p(q)*G_q - Revenue_q - RefundedFees_q
                   +/- FX translation                                                   [p(q), RefundedFees_q not disclosed]
  FundsHeld_q    = FundsHeld_{q-1} + GuestCashReceived_q - HostPayouts_q - GuestRefunds_q [components not disclosed separately]

Only the LEVELS (UnearnedFees_q, FundsHeld_q, GBV_q, Revenue_q, Nights_m) and their
y/y growth are observable and rebuilt here, quarterly since 4Q20 (24 quarters,
abnb_backlog_indicators.csv). The identity is written out for completeness and
auditability, not fitted -- the decomposition terms on its right-hand side are not
public, which is exactly why Airbnb's own balance sheet items are the only usable
proxy and why the RNPL-era distortion (sec 1.5 / circularity.py) hits them without a
public counter-check.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from common import (COVERAGE_NORM_FULL_SAMPLE, ensure_out_dir, load_backlog_indicators,
                    OUT_DIR)


def _season(q: str) -> int:
    return int(q[0])


def run() -> pd.DataFrame:
    ensure_out_dir()
    b = load_backlog_indicators().copy()
    b = b.sort_values("quarter_end").reset_index(drop=True)
    b["season"] = b["quarter"].map(_season)
    b["coverage_norm_full_sample"] = b["season"].map(COVERAGE_NORM_FULL_SAMPLE)

    # derived (basis='derived', per ruling): restated unearned fees, multiply form,
    # using the FULL-SAMPLE norm -- descriptive only, NEVER a forecast feature (see
    # circularity.py). Only computed where next_q_revenue is known (i.e. not 2Q26,
    # whose next-quarter value is a guide, not a print).
    b["next_q_is_actual"] = b["quarter"] != "2Q26"
    implied = b["coverage_norm_full_sample"] * b["next_q_revenue_musd"]
    gap = implied - b["unearned_fees_musd"]
    b["d_q_pct_derived"] = np.where(b["next_q_revenue_musd"].notna(),
                                    100.0 * gap / b["unearned_fees_musd"], np.nan)
    b["unearned_fees_restated_derived_musd"] = np.where(
        b["next_q_revenue_musd"].notna(),
        b["unearned_fees_musd"] * (1.0 + b["d_q_pct_derived"] / 100.0), np.nan)
    b["restatement_basis"] = np.where(b["next_q_is_actual"], "derived (multiply form; "
        "circular -- see circularity.py, do not use as a forecast feature)",
        "derived (multiply form; uses 3Q26 GUIDE MIDPOINT, doubly circular)")

    # identity checks that ARE testable from disclosed levels alone
    b["funds_held_to_gbv_pct"] = 100.0 * b["funds_held_musd"] / b["gbv_musd"]
    b["unearned_to_gbv_pct"] = 100.0 * b["unearned_fees_musd"] / b["gbv_musd"]
    b["unearned_to_next_q_revenue_recomputed"] = (
        b["unearned_fees_musd"] / b["next_q_revenue_musd"])
    # cross-check against the pre-existing column in the source file
    b["coverage_recompute_matches_source"] = (
        (b["unearned_to_next_q_revenue_recomputed"] - b["unearned_to_next_q_revenue"])
        .abs() < 0.002)

    cols = [
        "quarter_end", "quarter", "season", "rnpl_era",
        "unearned_fees_musd", "unearned_fees_musd_yoy_pct",
        "funds_held_musd", "funds_held_musd_yoy_pct",
        "gbv_musd", "gbv_musd_yoy_pct", "nights_m",
        "revenue_musd", "revenue_musd_yoy_pct",
        "next_q_revenue_musd", "next_q_revenue_yoy_pct", "next_q_is_actual",
        "unearned_to_next_q_revenue", "unearned_to_next_q_revenue_recomputed",
        "coverage_recompute_matches_source", "coverage_norm_full_sample",
        "unearned_to_gbv_pct", "funds_held_to_gbv_pct",
        "d_q_pct_derived", "unearned_fees_restated_derived_musd", "restatement_basis",
    ]
    out = b[cols].copy()
    out.to_csv(OUT_DIR / "01_backlog_rebuild.csv", index=False)

    n_mismatch = int((~out["coverage_recompute_matches_source"].fillna(True)).sum())
    return out, n_mismatch


IDENTITY_TEXT = """\
Identity (see docstring): Nights_q, GBV_q net of cancellations; UnearnedFees_q and
FundsHeld_q roll forward from cash flows and revenue recognition. The cancellation,
booking-vs-check-in split (p(q)), and refund terms are NOT disclosed by Airbnb at any
frequency -- confirmed by grep across the KPI panel, the 10-Q/10-K MD&A text pulled
into 03_insider_mechanics.md, and the guidance ledger. What CAN be and IS rebuilt here
from disclosed levels: UnearnedFees_q, FundsHeld_q, GBV_q, Revenue_q, Nights_q and
their y/y growth, quarterly since 4Q20 (abnb_backlog_indicators.csv, 24 quarters).
"""

if __name__ == "__main__":
    out, n_mismatch = run()
    print(out.tail(10).to_string(index=False))
    print(f"\ncoverage recompute mismatches vs source column: {n_mismatch}")
    print(IDENTITY_TEXT)
