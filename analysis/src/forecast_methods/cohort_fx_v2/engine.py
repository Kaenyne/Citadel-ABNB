"""Auditable cohort FX replacement. No fitting, demand, cancellation or hedge model."""
from __future__ import annotations

import re
import numpy as np
import pandas as pd

KEY = ["quarter", "booking_quarter", "currency"]
META = ["information_date", "source_ref", "evidence_status", "reference_basis"]


def information_cutoff(value):
    """Date-only vintages mean UTC close; explicit instants keep their precision."""
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        raise ValueError("Missing information cutoff")
    ts = ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")
    return ts + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(value)) else ts


def period(value):
    value = str(value)
    if re.fullmatch(r"\d{4}Q[1-4]", value):
        return pd.Period(value, freq="Q")
    if re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value):
        return pd.Period(value, freq="M")
    raise ValueError(f"Invalid monthly or quarterly period: {value}")


def check_frame(frame, keys, numeric, as_of, meta=True):
    need = keys + numeric + (META if meta else [])
    if set(need) - set(frame) or frame.empty:
        raise ValueError(f"Required nonempty table columns: {need}")
    if frame[keys].isna().any().any() or frame.duplicated(keys).any():
        raise ValueError(f"Null or duplicate keys: {keys}")
    for c in numeric:
        if not pd.api.types.is_numeric_dtype(frame[c]) or not np.isfinite(frame[c]).all():
            raise ValueError(f"Nonfinite or nonnumeric {c}")
    if meta:
        for c in META:
            if frame[c].isna().any() or frame[c].astype(str).str.strip().eq("").any():
                raise ValueError(f"Missing provenance: {c}")
        dates = pd.to_datetime(frame.information_date, errors="coerce", utc=True, format="mixed")
        if dates.isna().any() or (dates > information_cutoff(as_of)).any():
            raise ValueError("Information-date leakage")


class RateBook:
    def __init__(self, rates, as_of):
        check_frame(rates, ["period", "currency"], ["usd_per_unit", "reference_usd_per_unit"], as_of)
        need = {"rate_status", "quote_cutoff"}
        if need - set(rates):
            raise ValueError("Rates require rate_status and quote_cutoff")
        if (rates[["usd_per_unit", "reference_usd_per_unit"]] <= 0).any().any():
            raise ValueError("FX rates must be positive")
        if not rates.currency.str.fullmatch("[A-Z]{3}").all():
            raise ValueError("Not a currency; indices and unrelated levels are inadmissible")
        if len(set(rates.reference_basis)) != 1:
            raise ValueError("Reference basis mismatch")
        for c, g in rates.groupby("currency"):
            if g.reference_usd_per_unit.nunique() != 1:
                raise ValueError("Fixed reference requires one reference rate per currency")
            if c == "USD" and not np.allclose(g[["usd_per_unit", "reference_usd_per_unit"]], 1, atol=1e-12, rtol=0):
                raise ValueError("USD quotes must equal one")
        for r in rates.itertuples():
            p = period(r.period)
            cutoff = pd.to_datetime(r.quote_cutoff, errors="coerce", utc=True)
            if pd.isna(cutoff) or cutoff > information_cutoff(as_of):
                raise ValueError("Future or missing quote cutoff")
            source_cutoff = information_cutoff(r.information_date)
            if cutoff > source_cutoff:
                raise ValueError("Quote cutoff after source information date")
            if r.rate_status == "observed" and p.end_time.tz_localize("UTC") > min(information_cutoff(as_of), source_cutoff):
                raise ValueError("Future period cannot be fully observed")
            if r.rate_status == "observed" and not p.start_time.tz_localize("UTC") <= cutoff <= p.end_time.tz_localize("UTC"):
                raise ValueError("Observed quote cutoff outside its period")
            if r.rate_status not in {"observed", "observed_plus_flat", "flat_assumption", "synthetic"}:
                raise ValueError("Unknown rate status")
        self.frame = rates.set_index(["period", "currency"])
        self.basis = rates.reference_basis.iloc[0]

    def get(self, p, c):
        try:
            r = self.frame.loc[(p, c)]
        except KeyError as exc:
            raise ValueError(f"Missing FX rate: {p}/{c}") from exc
        return float(r.usd_per_unit / r.reference_usd_per_unit), r


def from_reported_contributions(contributions, rates, as_of):
    """Normalize currency-split reported kernel dollars, never add a full FX factor."""
    check_frame(contributions, KEY, ["reported_contribution_usd", "rnpl_share"], as_of)
    if (contributions.reported_contribution_usd < 0).any():
        raise ValueError("Negative reported contribution")
    rb = RateBook(rates, as_of)
    if set(contributions.reference_basis) != {rb.basis}:
        raise ValueError("Reference basis mismatch")
    out = contributions.copy()
    out["reference_contribution_usd"] = [
        r.reported_contribution_usd / rb.get(r.booking_quarter, r.currency)[0]
        if r.reported_contribution_usd else 0.0 for r in contributions.itertuples()
    ]
    return out


def apply_timing(cohorts, allocations, rates, as_of, *, basis_status="normalized_kernel_hedge_unresolved"):
    """Return detail, allocation audit and aggregate scenarios; dollar units are USD."""
    check_frame(cohorts, KEY, ["reference_contribution_usd", "rnpl_share"], as_of)
    check_frame(allocations, KEY + ["fx_period"], ["p"], as_of)
    if basis_status not in {"normalized_kernel_hedge_unresolved", "certified_prehedge_reference"}:
        raise ValueError("Unknown hedge/basis status")
    if "timing_hypothesis" not in allocations:
        raise ValueError("Missing timing hypothesis")
    if (cohorts.reference_contribution_usd < 0).any() or not cohorts.rnpl_share.between(0, 1).all():
        raise ValueError("Invalid contribution or RNPL share")
    if not allocations.p.between(0, 1).all():
        raise ValueError("Invalid RNPL allocation")
    rb = RateBook(rates, as_of)
    if set(cohorts.reference_basis) != {rb.basis} or set(allocations.reference_basis) != {rb.basis}:
        raise ValueError("Reference basis mismatch")
    if set(map(tuple, cohorts[KEY].values)) != set(map(tuple, allocations[KEY].values)):
        raise ValueError("Cohort/allocation keys mismatch")
    sums = allocations.groupby(KEY).p.sum()
    if not np.allclose(sums, 1, atol=1e-10, rtol=0):
        raise ValueError("RNPL p must sum to one for every cohort/currency")
    totals = cohorts.groupby("quarter").reference_contribution_usd.sum()
    if (totals <= 0).any():
        raise ValueError("A target must have positive total reference exposure")
    detail, audit = [], []
    for r in cohorts.itertuples():
        target, booked = period(r.quarter), period(r.booking_quarter)
        if target.freqstr[0] != "Q" or booked.freqstr[0] != "Q" or booked >= target:
            raise ValueError("Quarterly booking cohort must precede target")
        C0, u = r.reference_contribution_usd, r.rnpl_share
        w = C0 / totals.loc[r.quarter]
        fb, br = rb.get(r.booking_quarter, r.currency) if C0 else (1., None)
        a = allocations
        for k in KEY:
            a = a[a[k] == getattr(r, k)]
        retimed_factor = 0.
        for x in a.itertuples():
            fxp = period(x.fx_period)
            if x.timing_hypothesis == "recognition_month":
                if fxp.start_time < target.start_time or fxp.end_time > target.end_time:
                    raise ValueError("Recognition period outside target quarter")
            elif x.timing_hypothesis == "payment_fixing_proxy":
                if fxp.start_time <= booked.start_time or fxp.end_time > target.end_time:
                    raise ValueError("Fixing proxy before booking or after recognition quarter")
            else:
                raise ValueError("Unknown timing hypothesis")
            fm, mr = rb.get(x.fx_period, r.currency) if C0*u*x.p else (fb, None)
            retimed_factor += x.p*fm
            audit.append({**{k:getattr(r,k) for k in KEY}, "fx_period":x.fx_period,
                "timing_hypothesis":x.timing_hypothesis, "w_reference":w,
                "rnpl_share":u, "p":x.p, "rnpl_reference_exposure_weight":w*u*x.p,
                "rnpl_reference_contribution_usd":C0*u*x.p,
                "rnpl_translated_contribution_usd":C0*u*x.p*fm,
                "booking_fx_factor":fb, "timing_fx_factor":fm,
                "information_date":str(as_of), "reference_basis":rb.basis,
                "source_ref":r.source_ref+"; "+x.source_ref,
                "evidence_status":r.evidence_status+"; "+x.evidence_status,
                "rate_status":mr.rate_status if mr is not None else "not_required_zero_exposure"})
        booking = C0*fb
        ordinary = C0*(1-u)*fb
        rnpl = C0*u*retimed_factor
        detail.append({**{k:getattr(r,k) for k in KEY}, "reference_contribution_usd":C0,
            "w_reference":w,"rnpl_share":u,"ordinary_exposure_weight":w*(1-u),
            "rnpl_exposure_weight":w*u,"booking_fx_factor":fb,
            "rnpl_fx_factor":retimed_factor,"booking_contribution_usd":booking,
            "ordinary_paid_contribution_usd":ordinary,"rnpl_retimed_contribution_usd":rnpl,
            "retimed_contribution_usd":ordinary+rnpl,
            "incremental_replacement_usd":ordinary+rnpl-booking,
            **{m:getattr(r,m) for m in META}})
    d, a = pd.DataFrame(detail), pd.DataFrame(audit)
    out = []
    for q, x in d.groupby("quarter", sort=True):
        R0=x.reference_contribution_usd.sum(); B=x.booking_contribution_usd.sum(); T=x.retimed_contribution_usd.sum()
        if not np.isfinite([R0, B, T]).all() or min(R0,B,T)<=0:
            raise ValueError("Invalid/overflowed aggregate")
        out.append(dict(quarter=q, reference_revenue_usd=R0, booking_revenue_usd=B,
            retimed_revenue_usd=T, booking_level_multiplier=B/R0,
            retimed_level_multiplier=T/R0, replacement_multiplier=T/B,
            booking_fx_usd=B-R0,retimed_fx_usd=T-R0,incremental_replacement_usd=T-B,
            reference_basis=rb.basis, basis_status=basis_status, hedge_status="unspecified_no_hedge_added",
            reported_revenue_including_hedges_usd=np.nan,
            total_weight=x.w_reference.sum(),rnpl_weight=x.rnpl_exposure_weight.sum(),
            information_date=str(as_of), evidence_status="conditional_sensitivity_not_identified"))
    return {"detail":d,"allocations":a,"summary":pd.DataFrame(out)}


def yoy_bridge(current, prior):
    """Same fixed reference required. Distinguish ratios, dollar differences and pp."""
    if current["reference_basis"] != prior["reference_basis"]:
        raise ValueError("YoY reference basis mismatch")
    if period(current["quarter"]) - 4 != period(prior["quarter"]):
        raise ValueError("YoY requires year-ago quarter")
    R0, R0y = current["reference_revenue_usd"], prior["reference_revenue_usd"]
    B, By = current["booking_revenue_usd"], prior["booking_revenue_usd"]
    T, Ty = current["retimed_revenue_usd"], prior["retimed_revenue_usd"]
    if not np.isfinite([R0,R0y,B,By,T,Ty]).all() or min(R0,R0y,B,By,T,Ty)<=0:
        raise ValueError("Positive YoY levels required")
    return dict(quarter=current["quarter"], prior_quarter=prior["quarter"],
        reference_yoy_pct=100*(R0/R0y-1), booking_yoy_pct=100*(B/By-1),
        retimed_yoy_pct=100*(T/Ty-1),
        fx_growth_gap_pp=100*(T/Ty-R0/R0y),
        timing_growth_gap_pp=100*(T/Ty-B/By),
        incremental_current_dollars_pp_of_prior_booking=100*(T-B)/By,
        current_level_fx_pct=100*(T/R0-1), prior_booking_usd=By,
        prior_retimed_usd=Ty, prior_rnpl_weight=prior["rnpl_weight"],
        reference_basis=current["reference_basis"],
        evidence_status="conditional_model_to_model_yoy_not_management_constant_currency")
