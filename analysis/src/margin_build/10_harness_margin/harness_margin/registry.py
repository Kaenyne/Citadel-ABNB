"""Margin registry: FORMAT 1.0 (frozen) validator, wrapped; files under
data/processed/margin_build/registry/<method>__<object>.csv.

What is reused from the frozen revenue harness (imported, never copied):
  validate_registry_frame   column set, slugging, vintage-date rule, PIT rule against the
                            frozen calendar, street_as_of / knowable_from <= vintage_date,
                            quantile monotonicity.
  check_replays             the two-replay rule (PIT and full_sample side by side).
  check_window_coverage     14 / 10 unique quarters per W1 / W2 object.
What this wrapper adds:
  * `target` must be a column of the MARGIN targets.csv (targets_units.csv lists them).
  * Window rule applied here rather than by the frozen strict check, because the frozen
    LIVE list contains only 2026Q3 (its README says "2026Q3 or later"; its code disagrees,
    and every package that registered 2026Q4 used strict_windows=False). Margin rule:
    W1 -> quarter in 2023Q1..2026Q2, W2 -> 2024Q1..2026Q2, LIVE -> 2026Q3 or later.
  * Per-horizon coverage warning (h=0 rows should cover 14 W1 / 10 W2 vintage dates).
  * Writes to the margin registry folder, not the frozen one.
"""
from __future__ import annotations

import datetime as _dt
import warnings
from pathlib import Path

import pandas as pd

from . import paths as P
from .frozen import (Q, W, TODAY, REGISTRY_COLUMNS, RegistryError, StreetVintageError,  # noqa: F401
                     validate_registry_frame, check_replays, check_window_coverage, slug_part)
from .panel import TARGET_METRICS

LIVE_FIRST_QUARTER = "2026Q3"


def registry_path(method: str, object_: str) -> Path:
    return P.REGISTRY_DIR / f"{slug_part(method)}__{slug_part(object_)}.csv"


def window_ok(window: str, quarter: str) -> bool:
    q = Q.canon(quarter)
    if window == "W1":
        return q in W.W1_TARGETS
    if window == "W2":
        return q in W.W2_TARGETS
    if window == "LIVE":
        return q >= LIVE_FIRST_QUARTER
    return False


def windows_for(vintage_date, quarter: str) -> list:
    """Windows a (vintage_date, quarter) row belongs to under the margin rule."""
    q = Q.canon(quarter)
    vd = pd.to_datetime(vintage_date).date()
    out = []
    if vd in W.GUIDE_DATES_W1 and q in W.W1_TARGETS:
        out.append("W1")
    if vd in W.GUIDE_DATES_W2 and q in W.W2_TARGETS:
        out.append("W2")
    if vd in (W.GUIDE_DATE_LIVE, TODAY) and q >= LIVE_FIRST_QUARTER:
        out.append("LIVE")
    return out


def check_horizon_coverage(d: pd.DataFrame) -> list:
    msgs = []
    want = {"W1": 14, "W2": 10}
    for (m, o, tgt, win, pb, h), g in d.groupby(
            ["method", "object", "target", "window", "prior_basis", "horizon_q"]):
        if win not in want or int(h) != 0:
            continue
        n = g["vintage_date"].nunique()
        if n != want[win]:
            msgs.append(f"!  H0 COVERAGE: {m}/{o} {tgt} {win} {pb} h=0 covers {n} vintage dates, "
                        f"expected {want[win]}.")
    return msgs


def validate_margin_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Frozen validator (non-strict windows) + margin target and window rules."""
    d = validate_registry_frame(df, strict_windows=False)
    bad_t = sorted(set(d["target"].astype(str)) - set(TARGET_METRICS))
    if bad_t:
        raise RegistryError(f"target must be a column of the margin targets.csv; unknown: {bad_t}. "
                            f"See targets_units.csv.")
    viol = [(r.window, r.quarter) for r in d.itertuples() if not window_ok(r.window, r.quarter)]
    if viol:
        raise RegistryError("window inconsistent with quarter (W1: 2023Q1..2026Q2, W2: 2024Q1..2026Q2, "
                            f"LIVE: >= {LIVE_FIRST_QUARTER}); first violations {sorted(set(viol))[:6]}")
    # a W1/W2 row must be made at a guide date of that window
    for r in d.itertuples():
        if r.window == "W1" and r.vintage_date not in W.GUIDE_DATES_W1:
            raise RegistryError(f"W1 row has vintage_date {r.vintage_date}, not a W1 guide date")
        if r.window == "W2" and r.vintage_date not in W.GUIDE_DATES_W2:
            raise RegistryError(f"W2 row has vintage_date {r.vintage_date}, not a W2 guide date")
        if r.window == "LIVE" and r.vintage_date not in (W.GUIDE_DATE_LIVE, TODAY):
            raise RegistryError(f"LIVE row has vintage_date {r.vintage_date}; LIVE vintages are "
                                f"{W.GUIDE_DATE_LIVE} and TODAY={TODAY}")
    return d


def register(df: pd.DataFrame, *, allow_single_replay: bool = False, quiet: bool = False) -> Path:
    """Validate and write one (method, object) file to the margin registry. Raises on error."""
    P.ensure_dirs()
    d = validate_margin_frame(df)
    warns = check_replays(d) + check_window_coverage(d) + check_horizon_coverage(d)
    for w in warns:
        if not quiet:
            print(w)
        warnings.warn(w, stacklevel=2)
    replay_problem = [w for w in warns if w.startswith("!! TWO-REPLAY")]
    if replay_problem and not allow_single_replay:
        raise RegistryError(replay_problem[0] + "  Pass allow_single_replay=True to override deliberately.")
    path = registry_path(d["method"].iloc[0], d["object"].iloc[0])
    d.to_csv(path, index=False)
    if not quiet:
        print(f"registered {len(d):5d} rows -> {path.relative_to(P.REPO_ROOT)}")
    return path


def _as_date(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    if isinstance(x, _dt.datetime):
        return x.date()
    if isinstance(x, _dt.date):
        return x
    s = str(x).strip()
    if not s or s.lower() in ("nan", "nat", "none", "<na>"):
        return None
    return pd.to_datetime(s).date()


def load_registry(method: str | None = None, object_: str | None = None) -> pd.DataFrame:
    P.ensure_dirs()
    if method and object_:
        files = [registry_path(method, object_)]
        files = [f for f in files if f.exists()]
    elif method:
        files = sorted(P.REGISTRY_DIR.glob(f"{slug_part(method)}__*.csv"))
    else:
        files = sorted(P.REGISTRY_DIR.glob("*__*.csv"))
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
    out["window"] = out["window"].astype(str).str.upper()
    return out
