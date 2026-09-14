"""Registry format v1.0 -- validator, writer and loader.

The format is frozen and documented in README.md, which is authoritative.
"""
from __future__ import annotations

import datetime as _dt
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from . import paths as P
from . import quarters as Q
from . import windows as W

FORMAT_VERSION = "1.0"

REQUIRED_COLUMNS = [
    "method", "object", "target", "quarter", "vintage_date", "horizon_q",
    "point", "q50", "window", "prior_basis", "n_params", "n_train",
]
QUANTILE_COLUMNS = ["q05", "q10", "q25", "q50", "q75", "q90", "q95"]
QUANTILE_LEVELS = {"q05": 0.05, "q10": 0.10, "q25": 0.25, "q50": 0.50,
                   "q75": 0.75, "q90": 0.90, "q95": 0.95}
OPTIONAL_COLUMNS = [
    "q05", "q10", "q25", "q75", "q90", "q95", "sd",
    "base_naive", "base_ar1", "base_trailing4", "base_guide_cushion", "base_street",
    "street_vendor", "street_as_of", "knowable_from", "spec_id", "notes",
]
REGISTRY_COLUMNS = REQUIRED_COLUMNS + [c for c in OPTIONAL_COLUMNS
                                       if c not in REQUIRED_COLUMNS]

VALID_WINDOWS = {"W1", "W2", "LIVE"}
VALID_PRIOR_BASIS = {"PIT", "full_sample"}

_SLUG = re.compile(r"[^a-z0-9_-]+")


class RegistryError(ValueError):
    """Raised when a registry frame violates the frozen format or a PIT rule."""


class StreetVintageError(RegistryError):
    """Raised when a consensus value postdates the vintage date it is used at."""


def slug(s: str) -> str:
    s = _SLUG.sub("-", str(s).strip().lower())
    if "__" in s:
        raise RegistryError(f"'__' is the filename separator and may not appear in {s!r}")
    return s


def registry_path(method: str, object_: str) -> Path:
    return P.REGISTRY_DIR / f"{slug(method)}__{slug(object_)}.csv"


def _as_date(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    if isinstance(x, _dt.datetime):
        return x.date()
    if isinstance(x, _dt.date):
        return x
    s = str(x).strip()
    if not s or s.lower() in ("nan", "nat", "none", "<na>"):
        return None
    return pd.to_datetime(s).date()


def _print_date_map() -> dict:
    from .loaders import load_calendar
    cal = load_calendar()
    return {r.print_quarter: _as_date(r.print_date) for r in cal.itertuples()}


def validate_registry_frame(df: pd.DataFrame, *, strict_windows: bool = True) -> pd.DataFrame:
    """Validate and normalise. Raises RegistryError on any violation. Returns a clean copy."""
    if df is None or len(df) == 0:
        raise RegistryError("empty registry frame")
    d = df.copy()

    missing = [c for c in REQUIRED_COLUMNS if c not in d.columns]
    if missing:
        raise RegistryError(f"missing required columns: {missing}")

    for c in REGISTRY_COLUMNS:
        if c not in d.columns:
            d[c] = pd.NA
    extra = [c for c in d.columns if c not in REGISTRY_COLUMNS]
    if extra:
        raise RegistryError(
            f"unknown columns {extra}; the format is frozen (v{FORMAT_VERSION}). "
            "Put anything else in `notes` or open a harness change request.")

    if d["method"].nunique() != 1 or d["object"].nunique() != 1:
        raise RegistryError("one registry file holds exactly one (method, object) pair; "
                            f"got methods={sorted(d['method'].unique())} "
                            f"objects={sorted(d['object'].unique())}")

    d["quarter"] = d["quarter"].map(Q.canon)
    d["window"] = d["window"].astype(str).str.upper()
    bad = sorted(set(d["window"]) - VALID_WINDOWS)
    if bad:
        raise RegistryError(f"window must be one of {sorted(VALID_WINDOWS)}; got {bad}")
    bad = sorted(set(d["prior_basis"].astype(str)) - VALID_PRIOR_BASIS)
    if bad:
        raise RegistryError(f"prior_basis must be one of {sorted(VALID_PRIOR_BASIS)}; got {bad}")

    d["vintage_date"] = d["vintage_date"].map(_as_date)
    for c in ("street_as_of", "knowable_from"):
        d[c] = d[c].map(_as_date)

    allowed_vintages = set(W.GUIDE_DATES_ALL) | {P.TODAY}
    badv = sorted({v for v in d["vintage_date"] if v not in allowed_vintages})
    if badv:
        raise RegistryError(
            f"vintage_date must be a guide date from calendar.csv or TODAY={P.TODAY}; got {badv}")

    for c in ("point", "q50", "n_params", "n_train", "horizon_q"):
        if d[c].isna().any():
            raise RegistryError(f"required column {c} has nulls")
    for c in ("point", "q50"):
        v = pd.to_numeric(d[c], errors="coerce")
        if not np.isfinite(v).all():
            raise RegistryError(f"{c} must be finite")

    # PIT RULE: a forecast may not be made on or after the print of its target quarter.
    pmap = _print_date_map()
    viol = []
    for r in d.itertuples():
        pdte = pmap.get(r.quarter)
        if pdte is not None and r.vintage_date is not None and r.vintage_date >= pdte:
            viol.append((r.quarter, r.vintage_date, pdte))
    if viol:
        raise RegistryError(
            "POINT-IN-TIME VIOLATION: vintage_date is on/after the target quarter's print date "
            f"for {viol[:6]}{' ...' if len(viol) > 6 else ''}")

    for c, label in (("street_as_of", "street_as_of"), ("knowable_from", "knowable_from")):
        for r in d.itertuples():
            v = getattr(r, c)
            if v is not None and r.vintage_date is not None and v > r.vintage_date:
                raise StreetVintageError(
                    f"{label}={v} postdates vintage_date={r.vintage_date} for "
                    f"{r.method}/{r.object} {r.target} {r.quarter}. "
                    "A later-vintage consensus may not be used as an earlier pre-guide Street.")

    # quantile monotonicity
    present = [c for c in QUANTILE_COLUMNS if d[c].notna().any()]
    present.sort(key=lambda c: QUANTILE_LEVELS[c])
    if len(present) > 1:
        qm = d[present].apply(pd.to_numeric, errors="coerce")
        rows = qm.notna().sum(axis=1) > 1
        diffs = qm.diff(axis=1).iloc[:, 1:]
        bad_rows = (diffs < -1e-9).any(axis=1) & rows
        if bad_rows.any():
            raise RegistryError(
                f"quantiles must be non-decreasing; {int(bad_rows.sum())} row(s) violate this, "
                f"first at index {int(np.argmax(bad_rows.values))}")

    if strict_windows:
        for r in d.itertuples():
            wins = W.window_of_target(r.quarter)
            if r.window not in wins:
                raise RegistryError(
                    f"window={r.window} is inconsistent with quarter={r.quarter}; "
                    f"that quarter belongs to {wins}. (The 2026-08-06 guide is LIVE only.)")

    d["horizon_q"] = d["horizon_q"].astype(int)
    d["n_params"] = d["n_params"].astype(int)
    d["n_train"] = d["n_train"].astype(int)
    d["format_version"] = FORMAT_VERSION
    return d[REGISTRY_COLUMNS + ["format_version"]].reset_index(drop=True)


def check_replays(d: pd.DataFrame) -> list:
    """Two-replay rule: warn loudly if an object carries only one prior_basis."""
    msgs = []
    scored = d[d["window"] != "LIVE"]
    if len(scored) == 0:
        return msgs
    for (m, o), g in scored.groupby(["method", "object"]):
        bases = set(g["prior_basis"].astype(str))
        if bases != VALID_PRIOR_BASIS:
            msgs.append(
                f"!! TWO-REPLAY RULE: {m}/{o} carries prior_basis={sorted(bases)}; "
                "both 'PIT' and 'full_sample' replays must be published side by side.")
    return msgs


def check_window_coverage(d: pd.DataFrame) -> list:
    msgs = []
    want = {"W1": 14, "W2": 10}
    for (m, o, tgt, win, pb), g in d.groupby(
            ["method", "object", "target", "window", "prior_basis"]):
        if win not in want:
            continue
        n = g["quarter"].nunique()
        if n != want[win]:
            msgs.append(f"!  COVERAGE: {m}/{o} {tgt} {win} {pb} covers {n} quarters, "
                        f"expected {want[win]}.")
    return msgs


def register(df: pd.DataFrame, *, allow_single_replay: bool = False,
             strict_windows: bool = True, quiet: bool = False) -> Path:
    """Validate `df` and write it to the registry. Returns the path written."""
    P.ensure_dirs()
    d = validate_registry_frame(df, strict_windows=strict_windows)
    warns = check_replays(d) + check_window_coverage(d)
    for w in warns:
        if not quiet:
            print(w)
        warnings.warn(w, stacklevel=2)
    replay_problem = [w for w in warns if w.startswith("!! TWO-REPLAY")]
    if replay_problem and not allow_single_replay:
        raise RegistryError(replay_problem[0] +
                            "  Pass allow_single_replay=True to override deliberately.")
    path = registry_path(d["method"].iloc[0], d["object"].iloc[0])
    d.to_csv(path, index=False)
    if not quiet:
        print(f"registered {len(d):4d} rows -> {path.name}")
    return path


def load_registry(method: str | None = None, object_: str | None = None) -> pd.DataFrame:
    P.ensure_dirs()
    pat = f"{slug(method)}__*" if method else "*__*"
    if method and object_:
        pat = f"{slug(method)}__{slug(object_)}.csv"
    files = sorted(P.REGISTRY_DIR.glob(pat if pat.endswith(".csv") else pat + ".csv"))
    frames = []
    for f in files:
        try:
            x = pd.read_csv(f)
            x["_source_file"] = f.name
            frames.append(x)
        except Exception as e:  # pragma: no cover
            warnings.warn(f"could not read {f.name}: {e}")
    if not frames:
        return pd.DataFrame(columns=REGISTRY_COLUMNS + ["_source_file"])
    out = pd.concat(frames, ignore_index=True)
    out["vintage_date"] = out["vintage_date"].map(_as_date)
    out["quarter"] = out["quarter"].map(Q.canon)
    return out
