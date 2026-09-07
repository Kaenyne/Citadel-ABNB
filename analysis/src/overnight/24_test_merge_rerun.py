"""Workstream 24: tests for 16_merge_and_rerun.py (audit finding A11).

Every test runs against a throwaway sandbox project root built from copies of the real inputs, so
nothing in data/processed/overnight is touched. The four acceptance criteria of A11:

  T1  appending a previously unseen quarter succeeds without altering prior primitives
  T2  changing an existing consensus recomputes the dependent surprise (and its sign)
  T3  duplicate keys - and the other schema violations - fail loudly
  T4  the pre-event frozen forecast is written once and never overwritten by a post-event refit

READS   data/processed/overnight/04_consensus_at_print.csv
        data/processed/overnight/16_consensus_additions.csv
        data/processed/overnight/16_q3_2026_breakeven.csv, 16_reaction_tests.csv
        data/processed/abnb_daily_close.csv, abnb_revenue_guidance_vs_actual.csv,
        data/processed/predictive/04_print_features.csv
        analysis/src/overnight/04_reaction_vs_consensus.py
WRITES  nothing in the repository (a temporary directory only)

RUN     py -3.13 analysis/src/overnight/24_test_merge_rerun.py
        exit 0 = all tests pass, exit 1 = at least one failed.
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import os
import shutil
import sys
import tempfile
import traceback
from contextlib import redirect_stdout

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OD = os.path.join(ROOT, "data", "processed", "overnight")

_spec = importlib.util.spec_from_file_location("mr16", os.path.join(HERE, "16_merge_and_rerun.py"))
MR = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(MR)

# a plausible Q3 2026 event: the numbers are placeholders for a print that has not happened, which
# is the point - the test is about the append machinery, not about forecasting the quarter.
APPEND_ROWS = [
    dict(print_quarter="2026Q3", print_date="2026-11-05", column="print_date",
         new_value="2026-11-05", vendor="reported", source_publisher="Airbnb IR",
         source_date="2026-11-05", source_url="https://investors.airbnb.com/",
         confidence="high", notes="test fixture"),
    dict(print_quarter="2026Q3", print_date="2026-11-05", column="reaction_date",
         new_value="2026-11-06", vendor="reported", source_publisher="Airbnb IR",
         source_date="2026-11-05", source_url="https://investors.airbnb.com/",
         confidence="high", notes="test fixture"),
    dict(print_quarter="2026Q3", print_date="2026-11-05", column="actual_revenue_musd",
         new_value=4800.0, vendor="reported", source_publisher="Airbnb 8-K Ex.99.1",
         source_date="2026-11-05", source_url="https://investors.airbnb.com/",
         confidence="high", notes="test fixture"),
    dict(print_quarter="2026Q3", print_date="2026-11-05", column="cons_revenue_musd",
         new_value=4740.0, vendor="Zacks", source_publisher="Zacks",
         source_date="2026-09-04", source_url="https://www.zacks.com/stock/quote/ABNB",
         confidence="high", notes="the pre-print Street bar in 16_q3_2026_breakeven.csv"),
    dict(print_quarter="2026Q3", print_date="2026-11-05", column="cons_revenue_vendor",
         new_value="Zacks", vendor="Zacks", source_publisher="Zacks",
         source_date="2026-09-04", source_url="https://www.zacks.com/stock/quote/ABNB",
         confidence="high", notes="test fixture"),
    dict(print_quarter="2026Q3", print_date="2026-11-05", column="next_q_guide_mid_musd",
         new_value=3300.0, vendor="reported", source_publisher="Airbnb 8-K Ex.99.1",
         source_date="2026-11-05", source_url="https://investors.airbnb.com/",
         confidence="high", notes="test fixture"),
    dict(print_quarter="2026Q3", print_date="2026-11-05", column="next_q_cons_revenue_musd",
         new_value=3200.0, vendor="Zacks", source_publisher="Zacks",
         source_date="2026-09-04", source_url="https://www.zacks.com/stock/quote/ABNB",
         confidence="medium", notes="Q4-26 Street bar"),
    # the post-print reaction, knowable only after the event - this is what makes the refit a
    # different object from the frozen pre-event forecast
    dict(print_quarter="2026Q3", print_date="2026-11-05", column="excess_1d_pct",
         new_value=4.5, vendor="derived", source_publisher="derived",
         source_date="2026-11-06", source_url="", confidence="high", notes="test fixture"),
    dict(print_quarter="2026Q3", print_date="2026-11-05", column="excess_5d_pct",
         new_value=3.0, vendor="derived", source_publisher="derived",
         source_date="2026-11-12", source_url="", confidence="high", notes="test fixture"),
    dict(print_quarter="2026Q3", print_date="2026-11-05", column="excess_20d_pct",
         new_value=-1.0, vendor="derived", source_publisher="derived",
         source_date="2026-12-03", source_url="", confidence="high", notes="test fixture"),
]

PRIMITIVES = ["cons_revenue_musd", "actual_revenue_musd", "cons_eps_usd", "actual_eps_usd",
              "cons_adj_ebitda_musd", "actual_adj_ebitda_musd", "cons_nights_m", "actual_nights_m",
              "cons_gbv_busd", "actual_gbv_busd", "next_q_cons_revenue_musd",
              "next_q_guide_mid_musd", "eps_comparable", "print_date", "reaction_date"]

RESULTS = []


def sandbox(with_rerun_inputs=False):
    """A minimal project root: enough files for --no-rerun, optionally enough for the full re-run."""
    d = tempfile.mkdtemp(prefix="ws24_")
    od = os.path.join(d, "data", "processed", "overnight")
    sd = os.path.join(d, "analysis", "src", "overnight")
    os.makedirs(od)
    os.makedirs(sd)
    for n in ("04_consensus_at_print.csv", "16_consensus_additions.csv",
              "16_q3_2026_breakeven.csv", "16_reaction_tests.csv",
              "16_consensus_at_print_merged.csv", "04_reaction_tests.csv"):
        p = os.path.join(OD, n)
        if os.path.exists(p):
            shutil.copyfile(p, os.path.join(od, n))
    if with_rerun_inputs:
        dp = os.path.join(d, "data", "processed")
        os.makedirs(os.path.join(dp, "predictive"), exist_ok=True)
        for n in ("abnb_daily_close.csv", "abnb_revenue_guidance_vs_actual.csv"):
            shutil.copyfile(os.path.join(ROOT, "data", "processed", n), os.path.join(dp, n))
        shutil.copyfile(os.path.join(ROOT, "data", "processed", "predictive",
                                     "04_print_features.csv"),
                        os.path.join(dp, "predictive", "04_print_features.csv"))
        shutil.copyfile(os.path.join(HERE, "04_reaction_vs_consensus.py"),
                        os.path.join(sd, "04_reaction_vs_consensus.py"))
    return d


def write_csv(rows, path):
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def quiet(fn, *a, **k):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = fn(*a, **k)
    return rc, buf.getvalue()


def check(name, cond, detail=""):
    RESULTS.append((name, "PASS" if cond else "FAIL", detail))
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    return cond


# ------------------------------------------------------------------------------------------ T1
def t1_append_new_quarter():
    print("\nT1  appending an unseen quarter succeeds and leaves prior primitives untouched")
    d = sandbox()
    od = os.path.join(d, "data", "processed", "overnight")
    add = write_csv(APPEND_ROWS, os.path.join(od, "new_event.csv"))

    rc, _ = quiet(MR.main, ["--root", d, "--no-rerun"])                    # patch-mode reference
    ref = pd.read_csv(os.path.join(od, "16_consensus_at_print_merged.csv")).set_index("print_quarter")

    rc, log = quiet(MR.main, ["--root", d, "--append", add, "--no-rerun"])
    check("T1.1 append exits 0", rc == 0, f"rc={rc}")
    out_path = os.path.join(od, "16_post_2026Q3_consensus_at_print_merged.csv")
    if not check("T1.2 the append writes its own output file", os.path.exists(out_path)):
        return
    new = pd.read_csv(out_path).set_index("print_quarter")
    check("T1.3 exactly one row added", len(new) == len(ref) + 1, f"{len(ref)} -> {len(new)}")
    check("T1.4 the new quarter is present", "2026Q3" in new.index)

    changed = []
    for q in ref.index:
        for col in PRIMITIVES:
            if col not in ref.columns:
                continue
            a, b = ref.at[q, col], new.at[q, col]
            if pd.isna(a) and pd.isna(b):
                continue
            try:                       # numeric compare: int64 1 and float 1.0 are the same value
                same = abs(float(a) - float(b)) < 1e-12
            except (TypeError, ValueError):
                same = str(a) == str(b)
            if not same:
                changed.append((q, col, a, b))
    check("T1.5 no prior primitive changed", not changed, str(changed[:5]))

    exp = round((4800.0 - 4740.0) / 4740.0 * 100.0, 3)
    check("T1.6 the new revenue surprise is computed from its primitives",
          abs(float(new.at["2026Q3", "revenue_surprise_pct"]) - exp) < 1e-9,
          f"{new.at['2026Q3', 'revenue_surprise_pct']} vs {exp}")
    expg = round((3300.0 - 3200.0) / 3200.0 * 100.0, 3)
    check("T1.7 the new guide-vs-street and its sign are computed",
          abs(float(new.at["2026Q3", "guide_vs_street_pct"]) - expg) < 1e-9
          and float(new.at["2026Q3", "guide_vs_street_sign"]) == 1.0,
          f"{new.at['2026Q3', 'guide_vs_street_pct']}, sign "
          f"{new.at['2026Q3', 'guide_vs_street_sign']}")
    shutil.rmtree(d, ignore_errors=True)


# ------------------------------------------------------------------------------------------ T2
def t2_revised_consensus_recomputes():
    print("\nT2  revising an existing, non-blank consensus recomputes the dependent surprise")
    d = sandbox()
    od = os.path.join(d, "data", "processed", "overnight")

    base = pd.read_csv(os.path.join(od, "04_consensus_at_print.csv")).set_index("print_quarter")
    q = "2026Q2"
    old_cons = float(base.at[q, "cons_revenue_musd"])
    old_sur = float(base.at[q, "revenue_surprise_pct"])
    actual = float(base.at[q, "actual_revenue_musd"])
    new_cons = round(old_cons * 1.01, 1)           # a 1% higher Street bar
    check("T2.0 the surprise being revised was NOT blank to start with", old_sur == old_sur,
          f"{q} revenue_surprise_pct = {old_sur}")

    write_csv([dict(print_quarter=q, print_date=str(base.at[q, "print_date"]),
                    column="cons_revenue_musd", new_value=new_cons, vendor="TestVendor",
                    source_publisher="test", source_date="2026-09-06",
                    source_url="https://example.invalid/revision", confidence="high",
                    notes="T2 fixture")],
              os.path.join(od, "revision.csv"))
    rc, log = quiet(MR.main, ["--root", d, "--additions", os.path.join(od, "revision.csv"),
                              "--no-rerun"])
    check("T2.1 revision exits 0", rc == 0, f"rc={rc}")
    out = pd.read_csv(os.path.join(od, "16_consensus_at_print_merged.csv")).set_index("print_quarter")
    exp = round((actual - new_cons) / abs(new_cons) * 100.0, 3)
    got = float(out.at[q, "revenue_surprise_pct"])
    check("T2.2 the surprise moved off its stale value", abs(got - old_sur) > 1e-9,
          f"{old_sur} -> {got}")
    check("T2.3 the surprise equals (actual - new consensus) / |new consensus|",
          abs(got - exp) < 1e-9, f"{got} vs {exp}")
    check("T2.4 the recomputation is reported in the log", "recomputed" in log)

    # and the same for a sign field driven by a revised guide-vs-street primitive
    d2 = sandbox()
    od2 = os.path.join(d2, "data", "processed", "overnight")
    b2 = pd.read_csv(os.path.join(od2, "04_consensus_at_print.csv")).set_index("print_quarter")
    cand = [x for x in b2.index
            if pd.notna(b2.at[x, "next_q_guide_mid_musd"])
            and pd.notna(b2.at[x, "next_q_cons_revenue_musd"])
            and float(b2.at[x, "guide_vs_street_sign"]) == 1.0]
    if cand:
        qq = cand[0]
        flip = float(b2.at[qq, "next_q_guide_mid_musd"]) * 2.0   # push the Street far above the guide
        write_csv([dict(print_quarter=qq, print_date=str(b2.at[qq, "print_date"]),
                        column="next_q_cons_revenue_musd", new_value=flip, vendor="TestVendor",
                        source_publisher="test", source_date="2026-09-06",
                        source_url="https://example.invalid/revision", confidence="high",
                        notes="T2 fixture")],
                  os.path.join(od2, "revision2.csv"))
        quiet(MR.main, ["--root", d2, "--additions", os.path.join(od2, "revision2.csv"),
                        "--no-rerun"])
        o2 = pd.read_csv(os.path.join(od2, "16_consensus_at_print_merged.csv")).set_index("print_quarter")
        check("T2.5 the derived SIGN follows the recomputed magnitude",
              float(o2.at[qq, "guide_vs_street_sign"]) == -1.0
              and float(o2.at[qq, "guide_vs_street_pct"]) < 0,
              f"{qq}: sign {o2.at[qq, 'guide_vs_street_sign']}, "
              f"pct {o2.at[qq, 'guide_vs_street_pct']}")
    shutil.rmtree(d, ignore_errors=True)
    shutil.rmtree(d2, ignore_errors=True)


# ------------------------------------------------------------------------------------------ T3
def t3_bad_tables_fail():
    print("\nT3  duplicate keys and other schema violations fail")
    d = sandbox()
    od = os.path.join(d, "data", "processed", "overnight")

    def expect_exit(name, rows, append=False, path="bad.csv"):
        p = write_csv(rows, os.path.join(od, path))
        argv = ["--root", d, "--no-rerun"] + (["--append", p] if append else ["--additions", p])
        try:
            quiet(MR.main, argv)
        except SystemExit as exc:
            return check(name, True, str(exc)[:110])
        return check(name, False, "no SystemExit raised")

    dup = [dict(APPEND_ROWS[3]), dict(APPEND_ROWS[3])]
    expect_exit("T3.1 duplicate (quarter, column, vendor) records fail", dup, append=True,
                path="dup_key.csv")

    dup2 = [dict(APPEND_ROWS[3]), dict(APPEND_ROWS[3], vendor="Visible Alpha", new_value=4700.0)]
    expect_exit("T3.2 two vendors writing the same cell fail", dup2 + APPEND_ROWS[:3],
                append=True, path="dup_cell.csv")

    expect_exit("T3.3 a new quarter on the patch path fails with an instruction",
                APPEND_ROWS, append=False, path="new_on_patch.csv")

    seen = [dict(r, print_quarter="2026Q2") for r in APPEND_ROWS]
    expect_exit("T3.4 --append on a quarter that already exists fails", seen, append=True,
                path="already_seen.csv")

    lacking = [r for r in APPEND_ROWS if r["column"] != "cons_revenue_musd"]
    expect_exit("T3.5 a new event without a consensus fails", lacking, append=True,
                path="no_cons.csv")

    lacking2 = [r for r in APPEND_ROWS if r["column"] != "next_q_guide_mid_musd"]
    expect_exit("T3.6 a new event without the guide fails", lacking2, append=True,
                path="no_guide.csv")

    nosrc = [dict(r) for r in APPEND_ROWS]
    for r in nosrc:
        if r["column"] == "cons_revenue_musd":
            r["source_url"] = ""
    expect_exit("T3.7 a vendor-sourced value without a source URL fails", nosrc, append=True,
                path="no_src.csv")

    novint = [dict(r) for r in APPEND_ROWS]
    for r in novint:
        if r["column"] == "cons_revenue_musd":
            r["source_date"] = ""
    expect_exit("T3.8 a vendor-sourced value without a vintage fails", novint, append=True,
                path="no_vintage.csv")

    unknown = [dict(APPEND_ROWS[3], column="cons_revenue_in_galleons")]
    expect_exit("T3.9 a column that does not exist in the panel fails", unknown + APPEND_ROWS[:3],
                append=True, path="unknown_col.csv")
    shutil.rmtree(d, ignore_errors=True)


# ------------------------------------------------------------------------------------------ T4
def t4_frozen_forecast_survives():
    print("\nT4  the pre-event frozen forecast is not overwritten by the post-event refit")
    d = sandbox(with_rerun_inputs=True)
    od = os.path.join(d, "data", "processed", "overnight")
    add = write_csv(APPEND_ROWS, os.path.join(od, "new_event.csv"))

    pre_breakeven = md5(os.path.join(od, "16_q3_2026_breakeven.csv"))
    pre_tests = md5(os.path.join(od, "16_reaction_tests.csv"))

    rc, log = quiet(MR.main, ["--root", d, "--append", add])       # full refit, not --no-rerun
    check("T4.1 the post-print refit exits 0", rc == 0, f"rc={rc}")

    frozen_be = os.path.join(od, "16_frozen_pre_2026Q3_q3_2026_breakeven.csv")
    frozen_tests = os.path.join(od, "16_frozen_pre_2026Q3_reaction_tests.csv")
    check("T4.2 the pre-event forecast card was frozen", os.path.exists(frozen_be))
    check("T4.3 the pre-event reaction tests were frozen", os.path.exists(frozen_tests))
    check("T4.4 the frozen card is the pre-event card", md5(frozen_be) == pre_breakeven)
    check("T4.5 the shipped pre-event card was not overwritten by the refit",
          md5(os.path.join(od, "16_q3_2026_breakeven.csv")) == pre_breakeven)
    check("T4.6 the shipped pre-event tests were not overwritten by the refit",
          md5(os.path.join(od, "16_reaction_tests.csv")) == pre_tests)

    post_tests = os.path.join(od, "16_post_2026Q3_reaction_tests.csv")
    check("T4.7 the refit wrote its own tests file", os.path.exists(post_tests))
    check("T4.8 the refit is a different object from the frozen forecast",
          os.path.exists(post_tests) and md5(post_tests) != md5(frozen_tests))
    frozen_panel = os.path.join(od, "16_frozen_pre_2026Q3_consensus_at_print_merged.csv")
    post_panel = os.path.join(od, "16_post_2026Q3_consensus_at_print_merged.csv")
    check("T4.8b the frozen panel predates the new event, the refit panel contains it",
          "2026Q3" not in set(pd.read_csv(frozen_panel).print_quarter)
          and "2026Q3" in set(pd.read_csv(post_panel).print_quarter))

    # a second append must not re-freeze over the first freeze
    with open(frozen_be, "a", encoding="utf-8") as fh:
        fh.write("sentinel,0,,marker written between runs\n")
    sentinel = md5(frozen_be)
    rc2, log2 = quiet(MR.main, ["--root", d, "--append", add, "--no-rerun"])
    check("T4.9 a second append leaves the existing frozen file byte-identical",
          md5(frozen_be) == sentinel)
    check("T4.10 the second run says it kept the existing freeze", "kept existing" in log2)
    shutil.rmtree(d, ignore_errors=True)


def main():
    for fn in (t1_append_new_quarter, t2_revised_consensus_recomputes, t3_bad_tables_fail,
               t4_frozen_forecast_survives):
        try:
            fn()
        except Exception:                                                   # noqa: BLE001
            RESULTS.append((fn.__name__, "ERROR", traceback.format_exc(limit=3)))
            print(f"  [ERROR] {fn.__name__}\n{traceback.format_exc(limit=3)}")
    npass = sum(1 for _, s, _ in RESULTS if s == "PASS")
    nfail = len(RESULTS) - npass
    print(f"\n{npass}/{len(RESULTS)} checks passed, {nfail} failed")
    for n, s, det in RESULTS:
        if s != "PASS":
            print(f"  {s}  {n}  {det[:200]}")
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
