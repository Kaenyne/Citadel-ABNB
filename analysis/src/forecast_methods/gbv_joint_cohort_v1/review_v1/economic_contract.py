"""Independent matrix arithmetic; not an estimator of physical booking cohorts."""
from __future__ import annotations

import numpy as np


def matrix_views(allocations, booking_denominators, corporate_revenue):
    """Rows are booking cohorts; columns are recognition quarters.

    Do not pass accommodation value while labelling it corporate fee revenue.
    The caller supplies measurement lineage; arithmetic cannot establish it.
    """
    a = np.asarray(allocations, dtype=float)
    b = np.asarray(booking_denominators, dtype=float)
    r = np.asarray(corporate_revenue, dtype=float)
    if a.ndim != 2 or b.shape != (a.shape[0],) or r.shape != (a.shape[1],):
        raise ValueError("booking-row/recognition-column dimensions disagree")
    if not (np.isfinite(a).all() and np.isfinite(b).all() and np.isfinite(r).all()):
        raise ValueError("non-finite matrix or denominator")
    if (a < 0).any() or (b <= 0).any() or (r <= 0).any():
        raise ValueError("allocation must be nonnegative and denominators positive")
    allocated = a.sum(axis=0)
    conditional = np.divide(a, allocated, out=np.full_like(a, np.nan), where=allocated > 0)
    return {
        "allocated_revenue": allocated,
        "residual_dollars": r - allocated,
        "conditional_allocated_shares": conditional,
        "corporate_revenue_shares": a / r,
        "residual_revenue_share": (r - allocated) / r,
        "effective_forward_rates": a / b[:, None],
        "observed_row_rate_sum": a.sum(axis=1) / b,
    }


def joint_variance(quarter_by_component):
    """Sample dollar variance retaining every off-diagonal covariance term."""
    x = np.asarray(quarter_by_component, dtype=float)
    if x.ndim != 2 or len(x) < 2 or not np.isfinite(x).all():
        raise ValueError("need at least two complete independent-period rows")
    covariance = np.atleast_2d(np.cov(x, rowvar=False, ddof=1))
    diagonal = float(np.trace(covariance))
    off_diagonal = float(covariance.sum() - diagonal)
    direct = float(np.var(x.sum(axis=1), ddof=1))
    return {"n": len(x), "covariance": covariance, "diagonal": diagonal,
            "off_diagonal": off_diagonal, "direct_total_variance": direct,
            "identity_error": direct - diagonal - off_diagonal}
