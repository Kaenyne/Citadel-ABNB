# 16_merge_and_rerun.py
#
# Workstream 16 (web gap fill), refactored by workstream 24 for audit finding A11 (6 Sep 2026).
#
# Applies sourced consensus cells to a COPY of WS04's consensus file, recomputes every derived
# surprise/sign field from its primitives, then re-runs WS04's reaction script unmodified (its
# source is patched for output filenames only) so WS04's own outputs are never overwritten.
#
# TWO MODES
#   patch mode   (default)  applies data/processed/overnight/16_consensus_additions.csv, which only
#                           fills cells of quarters WS04 already carries. Reproduces the shipped
#                           16_* outputs byte for byte.
#   append mode  (--append additions.csv)  adds a previously unseen print quarter - the intended
#                           path after the 5 Nov 2026 Q3 print. Before anything is written the
#                           pre-event frozen forecast is copied aside and is never overwritten; the
#                           post-event refit is written under its own prefix (16_post_<quarter>_*).
#
# READS
#   data/processed/overnight/04_consensus_at_print.csv     (WS04, untouched)
#   data/processed/overnight/16_consensus_additions.csv    (sourced cells; --additions to override)
#   <--append file>                                        (a new event, append mode only)
#   analysis/src/overnight/04_reaction_vs_consensus.py     (executed with patched filenames)
#
# WRITES (patch mode; append mode uses the 16_post_<quarter>_ prefix instead of 16_)
#   data/processed/overnight/16_consensus_at_print_merged.csv
#   data/processed/overnight/16_reaction_panel.csv
#   data/processed/overnight/16_reaction_tests.csv
#   data/processed/overnight/16_q3_2026_breakeven.csv
#   data/processed/overnight/16_rerun_delta.csv             (04 vs this run, test by test)
#   data/processed/overnight/16_frozen_pre_<quarter>_*.csv  (append mode, written once, never again)
#
# RUN
#   py -3.13 analysis/src/overnight/16_merge_and_rerun.py
#   py -3.13 analysis/src/overnight/16_merge_and_rerun.py --append data/processed/overnight/16_2026Q3_event.csv
#   py -3.13 analysis/src/overnight/24_test_merge_rerun.py       (the tests for this module)
#
# Every added cell carries a source URL, a publication date (the vintage) and a verbatim quote in
# the additions file.
#
# ---------------------------------------------------------------------------------------------
# WS24 / audit finding A11. The defects this replaces:
#   1. the script ran at import time, so importing it executed the whole pipeline;
#   2. ROOT was one machine's absolute path;
#   3. it could only patch cells of quarters that already existed - a new quarter raised
#      SystemExit("unknown quarter ..."), which is exactly what the WS16 note promised it could do
#      after the next print;
#   4. it recomputed a derived surprise ONLY when that cell was already blank, so revising a
#      consensus input left the stale surprise and its sign in place;
#   5. it had no notion of a frozen pre-event forecast, so a post-print rerun would have silently
#      overwritten the prediction it was supposed to be scored against.
#
# POLICY on derived fields: sourced primitives win, derived fields are always recomputed. A derived
# value supplied by an additions file is kept (sourced beats calculated) but is cross-checked
# against the recomputation and reported as a conflict when the two disagree. The one deliberate
# suppression is WS04's: eps_surprise_pct stays blank when eps_comparable == 0 (2023Q3 and 2023Q4,
# where the GAAP EPS carries a one-off tax item that the consensus was not on).

from __future__ import annotations

import argparse
import os
import shutil

import numpy as np
import pandas as pd


class SchemaError(ValueError):
    """An additions table that cannot be trusted: bad schema, duplicate keys, missing sources."""


def project_root(start: str | None = None) -> str:
    """The project root, found relative to this file: <root>/analysis/src/overnight/this.py."""
    here = os.path.dirname(os.path.abspath(start or __file__))
    return os.path.abspath(os.path.join(here, "..", "..", ".."))


# Columns every additions table must carry.  source_url + source_date are the source and vintage
# fields: source_date is when the number was published, which is what makes it point-in-time
# checkable against the print date.
REQUIRED_ADDITION_COLS = ["print_quarter", "column", "new_value", "source_url", "confidence"]
REQUIRED_APPEND_COLS = REQUIRED_ADDITION_COLS + ["print_date", "vendor", "source_date"]

# The uniqueness key of a record in an additions table.
UNIQUE_KEY = ["print_quarter", "column", "vendor"]

# A new event is not admissible without a date, an actual, a consensus it can be scored against,
# and the guide that the next quarter's guide-vs-street test needs.
REQUIRED_NEW_EVENT_METRICS = [
    "print_date",                # when the print happened
    "actual_revenue_musd",       # actual
    "cons_revenue_musd",         # consensus
    "next_q_guide_mid_musd",     # guide
]

# derived column -> (actual, consensus) primitives. Mirrors 04_consensus_at_print.py's sur():
# (actual - consensus) / abs(consensus) * 100, rounded to 3dp.
DERIVED = {
    "revenue_surprise_pct": ("actual_revenue_musd", "cons_revenue_musd"),
    "eps_surprise_pct": ("actual_eps_usd", "cons_eps_usd"),
    "ebitda_surprise_pct": ("actual_adj_ebitda_musd", "cons_adj_ebitda_musd"),
    "nights_surprise_pct": ("actual_nights_m", "cons_nights_m"),
    "gbv_surprise_pct": ("actual_gbv_busd", "cons_gbv_busd"),
    "guide_vs_street_pct": ("next_q_guide_mid_musd", "next_q_cons_revenue_musd"),
}

# derived column -> (gate column, value the gate must hold for the field to be computed at all)
SUPPRESS_UNLESS = {"eps_surprise_pct": ("eps_comparable", 1)}

# artifacts that are frozen before an append: the prospective forecast must survive the refit
FREEZE_ARTIFACTS = ("q3_2026_breakeven", "reaction_tests", "consensus_at_print_merged")

TOL = 1e-6


def sur(a, c):
    """The surprise convention of 04_consensus_at_print.py."""
    if pd.isna(a) or pd.isna(c) or float(c) == 0:
        return np.nan
    return round((float(a) - float(c)) / abs(float(c)) * 100.0, 3)


def cast(val, col):
    """Numeric columns get floats, text columns stay text."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return val


# --------------------------------------------------------------------------------- validation
def validate_additions(add, base_columns, *, append_mode=False, known_quarters=()):
    """Raise SchemaError unless `add` is a well-formed additions table.

    Checks, in order: required columns; uniqueness on (print_quarter, column, vendor) and on the
    target cell (print_quarter, column); columns that exist in the base panel; source and vintage
    present on every non-derived row; and, in append mode, that the quarter is genuinely new and
    carries the required actual / consensus / guide primitives.
    """
    need = REQUIRED_APPEND_COLS if append_mode else REQUIRED_ADDITION_COLS
    missing = [c for c in need if c not in add.columns]
    if missing:
        raise SchemaError(f"additions table is missing required columns: {missing}")
    if add.empty:
        raise SchemaError("additions table has no rows")

    key = [c for c in UNIQUE_KEY if c in add.columns]
    dup = add.duplicated(subset=key, keep=False)
    if dup.any():
        raise SchemaError("duplicate (print_quarter, column, vendor) records in the additions "
                          "table:\n" + add.loc[dup, key].to_string(index=False))
    # two vendors cannot both write the same cell either: one target cell, one record
    dupcell = add.duplicated(subset=["print_quarter", "column"], keep=False)
    if dupcell.any():
        raise SchemaError("two records target the same cell (print_quarter, column):\n"
                          + add.loc[dupcell, ["print_quarter", "column"]].to_string(index=False))

    unknown_cols = sorted(set(add["column"]) - set(base_columns))
    if unknown_cols:
        raise SchemaError(f"unknown column(s) in the additions table: {unknown_cols}")

    if append_mode:
        vendor = add["vendor"].fillna("").astype(str).str.strip().str.lower()
        sourced = add[~vendor.isin(("derived", "reported", ""))]
        def blank(v):
            # pandas reads an empty CSV cell as NaN, and NaN is truthy, so `v or ""` is not enough
            return v is None or (isinstance(v, float) and pd.isna(v)) or not str(v).strip()

        for _, r in sourced.iterrows():
            if blank(r.get("source_url")):
                raise SchemaError(f"{r['print_quarter']} {r['column']}: source_url is required "
                                  f"for a vendor-sourced value")
            if blank(r.get("source_date")):
                raise SchemaError(f"{r['print_quarter']} {r['column']}: source_date (vintage) is "
                                  f"required for a vendor-sourced value")
        new_q = sorted(set(add["print_quarter"]) - set(known_quarters))
        seen_q = sorted(set(add["print_quarter"]) & set(known_quarters))
        if seen_q:
            raise SchemaError(f"--append is for unseen quarters; {seen_q} already exist in the "
                              f"base panel. Use the patch path (--additions) to revise them.")
        if len(new_q) != 1:
            raise SchemaError(f"--append takes exactly one new quarter per file, got {new_q}")
        q = new_q[0]
        rows_q = add[add["print_quarter"] == q]
        supplied = set(rows_q["column"])
        if "print_date" not in supplied and not rows_q["print_date"].notna().any():
            raise SchemaError(f"new quarter {q}: no print_date, either as its own additions row or "
                              f"in the print_date column")
        lack = [m for m in REQUIRED_NEW_EVENT_METRICS
                if m != "print_date" and m not in supplied]
        if lack:
            raise SchemaError(f"new quarter {q} is missing required actual/consensus/guide "
                              f"value(s): {lack}")
        return q
    return None


# --------------------------------------------------------------------------------- derived fields
def recompute_derived(base, sourced=frozenset()):
    """Recompute every derived field of EVERY row from its primitives.

    `sourced` is the set of (quarter, column) pairs an additions table supplied explicitly; those
    are left alone (sourced beats calculated) but cross-checked. Returns (recomputed, conflicts).
    """
    recomputed, conflicts = [], []
    for q in base.index:
        for dcol, (acol, ccol) in DERIVED.items():
            if dcol not in base.columns or acol not in base.columns or ccol not in base.columns:
                continue
            calc = sur(base.at[q, acol], base.at[q, ccol])
            gate = SUPPRESS_UNLESS.get(dcol)
            if gate is not None:
                gcol, gval = gate
                if gcol in base.columns:
                    g = base.at[q, gcol]
                    if pd.isna(g) or float(g) != float(gval):
                        calc = np.nan          # WS04 deliberately drops this one; keep it dropped
            have = base.at[q, dcol]
            if (q, dcol) in sourced:
                if not pd.isna(calc) and not pd.isna(have) and abs(float(have) - calc) > TOL:
                    conflicts.append((q, dcol, have, calc))
                continue
            if pd.isna(calc) and pd.isna(have):
                continue
            if pd.isna(have) or pd.isna(calc) or abs(float(have) - calc) > TOL:
                recomputed.append((q, dcol, have, calc))
                base.at[q, dcol] = calc
        if "guide_vs_street_sign" in base.columns and (q, "guide_vs_street_sign") not in sourced:
            g = base.at[q, "guide_vs_street_pct"]
            if not pd.isna(g):
                new_sign = 1.0 if float(g) > 0 else (-1.0 if float(g) < 0 else 0.0)
                cur = base.at[q, "guide_vs_street_sign"]
                if pd.isna(cur) or float(cur) != new_sign:
                    recomputed.append((q, "guide_vs_street_sign", cur, new_sign))
                    base.at[q, "guide_vs_street_sign"] = new_sign
    return recomputed, conflicts


def merge_additions(base, add, *, append_mode=False):
    """Apply `add` to `base` (indexed by print_quarter) and recompute every derived field.

    Returns (base, applied, appended, recomputed, conflicts). Primitives of quarters the additions
    table does not mention are never touched.
    """
    new_q = validate_additions(add, base.columns, append_mode=append_mode,
                               known_quarters=set(base.index))

    appended = []
    if append_mode:
        rows_q = add[add["print_quarter"] == new_q]
        base.loc[new_q] = np.nan
        if "print_date" not in set(rows_q["column"]):
            base.at[new_q, "print_date"] = rows_q["print_date"].dropna().iloc[0]
        appended.append(new_q)
    else:
        unseen = sorted(set(add["print_quarter"]) - set(base.index))
        if unseen:
            raise SchemaError(f"unknown quarter(s) {unseen} in the additions table. A new print is "
                              f"added with --append, which validates the extra fields a new event "
                              f"needs; the patch path only revises quarters that already exist.")

    applied = []
    for _, r in add.iterrows():
        q, col = r["print_quarter"], r["column"]
        old = base.at[q, col]
        base.at[q, col] = cast(r["new_value"], col)
        applied.append((q, col, old, base.at[q, col]))

    sourced = {(r["print_quarter"], r["column"]) for _, r in add.iterrows()}
    recomputed, conflicts = recompute_derived(base, sourced)
    return base, applied, appended, recomputed, conflicts


# --------------------------------------------------------------------------------- frozen forecast
def freeze_pre_event(out_dir, quarter, prefix="16"):
    """Copy the pre-event forecast artifacts aside before an append. Never overwrites.

    The 5 Nov card is a prospective forecast; a refit that has seen the actual is a different
    object and must not be able to replace it. Returns [(path, 'frozen'|'kept existing')].
    """
    done = []
    for name in FREEZE_ARTIFACTS:
        src = os.path.join(out_dir, f"{prefix}_{name}.csv")
        dst = os.path.join(out_dir, f"16_frozen_pre_{quarter}_{name}.csv")
        if not os.path.exists(src):
            continue
        if os.path.exists(dst):
            done.append((dst, "kept existing"))
            continue
        shutil.copyfile(src, dst)
        done.append((dst, "frozen"))
    return done


# --------------------------------------------------------------------------------- the run
def run_reaction_script(src_dir, out_prefix, root):
    """Execute 04_reaction_vs_consensus.py with its output filenames repointed at `out_prefix`."""
    path = os.path.join(src_dir, "04_reaction_vs_consensus.py")
    with open(path, encoding="utf-8") as fh:
        src = fh.read()
    patched = (src
               .replace('"04_consensus_at_print.csv"', f'"{out_prefix}_consensus_at_print_merged.csv"')
               .replace('"04_reaction_panel.csv"', f'"{out_prefix}_reaction_panel.csv"')
               .replace('"04_reaction_tests.csv"', f'"{out_prefix}_reaction_tests.csv"')
               .replace('"04_q3_2026_breakeven.csv"', f'"{out_prefix}_q3_2026_breakeven.csv"'))
    assert f"{out_prefix}_consensus_at_print_merged.csv" in patched
    os.environ["ABNB_ROOT"] = root
    ns = {"__name__": "__main__", "__file__": path}
    exec(compile(patched, "04_reaction_vs_consensus.py(patched)", "exec"), ns)


def compare_tests(a_path, b_path, out_path):
    a = pd.read_csv(a_path)
    b = pd.read_csv(b_path)
    keys = [c for c in ("block", "target", "label", "spec", "test") if c in a.columns]
    num = [c for c in a.columns if a[c].dtype.kind in "fi" and c in b.columns]
    m = a.merge(b, on=keys, suffixes=("_04", "_16"), how="outer")
    rows = []
    for _, r in m.iterrows():
        changed = {}
        for c in num:
            x, y = r.get(c + "_04"), r.get(c + "_16")
            if pd.isna(x) and pd.isna(y):
                continue
            if pd.isna(x) or pd.isna(y) or abs(float(x) - float(y)) > TOL:
                changed[c] = (x, y)
        if changed:
            row = {k: r[k] for k in keys}
            for c, (x, y) in changed.items():
                row[c + "_04"] = x
                row[c + "_16"] = y
            rows.append(row)
    delta = pd.DataFrame(rows)
    delta.to_csv(out_path, index=False)
    return len(delta), len(a)


def build_parser():
    p = argparse.ArgumentParser(
        description="Merge sourced consensus cells into WS04's panel and re-run the reaction "
                    "tests. Use --append to add a new print quarter.")
    p.add_argument("--root", default=project_root(),
                   help="project root (default: found relative to this script file)")
    p.add_argument("--additions", default=None,
                   help="patch-mode additions CSV "
                        "(default: data/processed/overnight/16_consensus_additions.csv)")
    p.add_argument("--append", default=None, metavar="ADDITIONS.CSV",
                   help="append a previously unseen print quarter from this CSV")
    p.add_argument("--prefix", default=None,
                   help="output filename prefix (default: 16, or 16_post_<quarter> when appending)")
    p.add_argument("--no-rerun", action="store_true",
                   help="write the merged panel only; skip the WS04 reaction re-run")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = os.path.abspath(args.root)
    out = os.path.join(root, "data", "processed", "overnight")
    src_dir = os.path.join(root, "analysis", "src", "overnight")
    for p in (out, src_dir):
        if not os.path.isdir(p):
            raise SystemExit(f"not a project root ({p} missing): {root}")

    base_path = os.path.join(out, "04_consensus_at_print.csv")
    base = pd.read_csv(base_path).set_index("print_quarter")
    n_before = len(base)

    curated = args.additions or os.path.join(out, "16_consensus_additions.csv")
    prefix = args.prefix or "16"
    frozen = []

    try:
        # the curated historical cells always apply first, so the panel a new event lands in is the
        # same panel the shipped run used
        add = pd.read_csv(curated)
        base, applied, appended, recomputed, conflicts = merge_additions(base, add)

        if args.append:
            new_add = pd.read_csv(args.append)
            probe = validate_additions(new_add, base.columns, append_mode=True,
                                       known_quarters=set(base.index))
            frozen = freeze_pre_event(out, probe, prefix="16")
            prefix = args.prefix or f"16_post_{probe}"
            base, a2, ap2, rc2, cf2 = merge_additions(base, new_add, append_mode=True)
            applied += a2
            appended += ap2
            recomputed += rc2
            conflicts += cf2
    except SchemaError as exc:
        raise SystemExit(f"additions table rejected: {exc}")

    base = base.reset_index().rename(columns={"index": "print_quarter"})
    base = base.sort_values("print_quarter").reset_index(drop=True)
    merged_path = os.path.join(out, f"{prefix}_consensus_at_print_merged.csv")
    base.to_csv(merged_path, index=False)
    print(f"merged file written: {merged_path}  ({n_before} events in, {len(base)} out)")
    for q, col, old, new in applied:
        print(f"  {q:8s} {col:28s} {old!r:>12} -> {new!r}")
    if appended:
        print(f"  appended new quarter(s): {appended}")
    for path, what in frozen:
        print(f"  {what}: {os.path.basename(path)}")
    for q, col, old, new in recomputed:
        print(f"  recomputed {q:8s} {col:28s} {old!r:>12} -> {new!r}")
    for q, col, have, calc in conflicts:
        print(f"  WARNING sourced-vs-calculated disagreement {q} {col}: sourced {have}, "
              f"primitives imply {calc}")

    if args.no_rerun:
        return 0

    run_reaction_script(src_dir, prefix, root)
    n_changed, n_tests = compare_tests(os.path.join(out, "04_reaction_tests.csv"),
                                       os.path.join(out, f"{prefix}_reaction_tests.csv"),
                                       os.path.join(out, f"{prefix}_rerun_delta.csv"))
    print(f"\n{n_changed} of {n_tests} tests changed; delta -> {prefix}_rerun_delta.csv")
    if frozen:
        print("pre-event forecast preserved at: "
              + ", ".join(os.path.basename(p) for p, _ in frozen))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
