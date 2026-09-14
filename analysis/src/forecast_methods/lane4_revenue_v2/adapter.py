"""Thin forecast-input adapter. K0 v2 owns lambda estimation and lag policy."""
from __future__ import annotations

from datetime import date
import math
import re
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from kernel_engine_v2 import engine as k0


def quarter(q):
    if not isinstance(q, str) or not re.fullmatch(r"\d{4}Q[1-4]", q):
        raise ValueError(f"Expected YYYYQn, got {q!r}")
    return q


def shift(q, n):
    quarter(q)
    i = int(q[:4]) * 4 + int(q[-1]) - 1 + n
    return f"{i // 4}Q{i % 4 + 1}"


def number(value, name, positive=False):
    if isinstance(value, bool):
        raise ValueError(f"{name}: boolean is not numeric")
    try:
        x = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{name}: missing/non-numeric") from exc
    if not math.isfinite(x) or (positive and x <= 0):
        raise ValueError(f"{name}: invalid value {value}")
    return x


def dated(value, as_of):
    if not value:
        raise ValueError("Missing information_date")
    # This package uses daily vintages. Same-day information is admitted explicitly.
    d, cutoff = date.fromisoformat(str(value)[:10]), date.fromisoformat(str(as_of)[:10])
    if d > cutoff:
        raise ValueError(f"Future information: {value} > {as_of}")
    return d.isoformat()


def forecast(target, as_of, inputs, cushion_decimal, lambda_info=None):
    """inputs contain actual or forecast GBV rows, kept outside K0's reported panel."""
    quarter(target)
    lam = lambda_info or k0.pit_lambda(int(target[-1]), as_of)
    dated(lam["knowable_from"], as_of)
    coefficient = number(lam["lambda_pct"], "lambda_pct", positive=True) / 100
    cushion = number(cushion_decimal, "cushion")
    if cushion <= -1:
        raise ValueError("Cushion must exceed -1")
    lookup = {}
    for row in inputs:
        q = quarter(row["quarter"])
        if q in lookup:
            raise ValueError(f"Duplicate GBV quarter {q}")
        dated(row["information_date"], as_of)
        gbv = number(row["gbv_musd"], "gbv_musd", positive=True)
        if row.get("kind") not in {"reported", "forecast"}:
            raise ValueError("GBV kind must distinguish reported from forecast")
        if row["kind"] == "reported" and q >= target:
            raise ValueError("Target/contemporaneous reported inputs are unavailable")
        if row.get("nights_m") is not None and row.get("adr_usd") is not None:
            identity = number(row["nights_m"], "nights_m", True) * number(row["adr_usd"], "adr_usd", True)
            if not math.isclose(gbv, identity, abs_tol=1e-8, rel_tol=0):
                raise ValueError("Nights times ADR must equal GBV exactly")
        lookup[q] = row
    parts = []
    for lag, weight in [(1, k0.WEIGHT), (2, 1 - k0.WEIGHT)]:
        q = shift(target, -lag)
        if q not in lookup:
            raise ValueError(f"Missing required GBV lag {q}")
        row = lookup[q]
        weighted = weight * float(row["gbv_musd"])
        parts.append(dict(target_quarter=target, booking_quarter=q, lag=lag,
                          kernel_coefficient=weight, gbv_musd=float(row["gbv_musd"]),
                          weighted_gbv_musd=weighted, revenue_contribution_musd=weighted * coefficient,
                          gbv_kind=row["kind"], information_date=row["information_date"],
                          source_ref=row["source_ref"]))
    base = sum(p["weighted_gbv_musd"] for p in parts)
    for p in parts:
        p["usd_baseline_contribution_weight"] = p["weighted_gbv_musd"] / base
        p["reference_currency_weight_status"] = "L3 scenario-only weights accepted as research; USD contribution is not an identified constant-FX currency weight"
    revenue = coefficient * base
    return dict(quarter=target, as_of=as_of, revenue_musd=revenue,
                guide_musd=revenue / (1 + cushion), kernel_base_musd=base,
                lambda_pct=lam["lambda_pct"], lambda_variant=lam["variant"],
                lambda_n_train=lam["n_train"], lambda_training_quarters=";".join(lam["training_quarters"]),
                lambda_knowable_from=lam["knowable_from"], cushion_decimal=cushion,
                information_date=max([p["information_date"] for p in parts] + [lam["knowable_from"]]),
                n_lag_cohorts=2, n_forecast_gbv=sum(p["gbv_kind"] == "forecast" for p in parts)), parts
