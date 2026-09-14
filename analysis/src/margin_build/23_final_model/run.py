"""WS23 final model — rebuild everything end to end.

    py -3.13 analysis/src/margin_build/23_final_model/run.py

Steps
  1 combine.py      the leave-future-out combination; registers final-margin__combined
                    and final-margin__combined_dollar_from_margin (the adopted dollar object)
  2 diagnostics.py  leave-one-member-out, Street-independent variant, shock vs calm
  3 forecast.py     line decomposition, the full forecast set, cyclicality, the 5 Nov card
  4 workbook.py     model/ABNB_margin_model.xlsx
  4b checks()       reconciliation assertions (WS31 audit 02/03/04/07/15)
  5 score.py        the margin harness scorer, run ONCE (skip with MARGIN_SKIP_SCORE=1)

Never run this while another agent is running a method package: several of them shell
out to score.py and the two collide (WS20 section 10).

MARGIN_VERIFY_ONLY=1 (WS31 audit 18) recomputes the whole build into
data/processed/margin_build/23_final_model/_verify/, writes NO committed output and no
registry row, runs the same assertions, and prints a per-file comparison against the
committed CSVs. Use it to audit the build without touching anything.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PY = [sys.executable]
SCORE = ROOT / "analysis" / "src" / "margin_build" / "10_harness_margin" / "score.py"
PROC = ROOT / "data" / "processed" / "margin_build"
OUT = PROC / "23_final_model"
VERIFY = os.environ.get("MARGIN_VERIFY_ONLY") == "1"
VOUT = OUT / "_verify"
TOL = 1e-6


def rp(name):
    return (VOUT / name) if VERIFY else (OUT / name)


def step(name, args):
    t0 = time.time()
    print(f"\n=== {name} ===", flush=True)
    r = subprocess.run(PY + args, cwd=str(ROOT))
    if r.returncode != 0:
        print(f"!! {name} exited {r.returncode}")
        sys.exit(r.returncode)
    print(f"--- {name} ok ({time.time() - t0:.0f}s)")


# --------------------------------------------------------------------- assertions
def _fail(msg):
    print(f"!! RECONCILIATION FAILED: {msg}")
    sys.exit(2)


def _ok(msg, worst):
    print(f"   ok  {msg} (worst |gap| {worst:.3e})")


def checks():
    """Every identity the Codex/Astra audit found broken, asserted on the built CSVs."""
    print("\n=== 4b reconciliation checks ===")
    lines = pd.read_csv(rp("23_lines_quarterly.csv"))
    pl = pd.read_csv(rp("23_forecast_quarterly.csv"))
    ann = pd.read_csv(rp("23_forecast_annual.csv"))
    bands = pd.read_csv(rp("23_bands.csv"))
    card = pd.read_csv(rp("23_card_5nov.csv"))
    tg = pd.read_csv(ROOT / "data" / "processed" / "margin_build" / "10_harness_margin"
                     / "targets.csv").set_index("quarter")
    L = ["cor", "ops", "pd", "sm", "ga"]

    # 02/03 — one add-back schedule: sum(lines) - add-backs = total cash costs, and
    #         revenue - total cash costs = adj EBITDA, on the same rows.
    f = lines[lines.scenario != "actual"]
    g1 = (f[[f"{x}_cash_musd" for x in L]].sum(axis=1) - f.addbacks_musd
          - f.total_cash_costs_musd).abs().max()
    if g1 > 1e-6:
        _fail(f"line stack does not reconcile to total cash costs ({g1})")
    g2 = (f.revenue_musd - f.total_cash_costs_musd - f.adj_ebitda_musd).abs().max()
    if g2 > 1e-6:
        _fail(f"revenue - total cash costs != adj EBITDA ({g2})")
    _ok("02/03 cost stack reconciles (five lines - D&A add-back = total cash costs)",
        max(g1, g2))

    # 03 — the GAAP bridge uses the SAME schedule: op income = adj EBITDA - SBC - D&A,
    #      and D&A is the add-back the cost stack carried.
    g3 = (pl.adj_ebitda_musd - pl.sbc_musd - pl.da_musd - pl.op_income_musd).abs().max()
    g4 = (pl.da_musd - pl.addbacks_musd).abs().max()
    if max(g3, g4) > 1e-6:
        _fail(f"GAAP bridge and cost stack use different add-backs ({g3}, {g4})")
    _ok("03 one add-back schedule in both bridges", max(g3, g4))

    # 07 — CFO is rebuilt from net income, not moved pretax:
    #      CFO = NI + D&A + SBC + (working capital + other)
    g5 = (pl.net_income_musd + pl.da_musd + pl.sbc_musd + pl.cfo_wc_and_other_musd
          - pl.cfo_musd_diagnostic).abs().max()
    if g5 > 1e-6:
        _fail(f"CFO does not rebuild from net income ({g5})")
    _ok("07 CFO = NI + D&A + SBC + working capital + other", g5)

    # 15 — annual tax and net income are the sum of the quarters
    worst = 0.0
    for sc in ["base", "bear", "bull"]:
        q = pl[pl.scenario == sc].set_index("quarter")
        a = ann[(ann.scenario == sc)].set_index("period")
        h1_ni = float(tg.loc[["2026Q1", "2026Q2"], "net_income_musd"].sum())
        h1_tax = float(tg.loc[["2026Q1", "2026Q2"], "tax_provision_musd"].sum())
        for per, qs, h_ni, h_tax in (("FY26", ["2026Q3", "2026Q4"], h1_ni, h1_tax),
                                     ("FY27", ["2027Q1", "2027Q2", "2027Q3", "2027Q4"], 0.0, 0.0)):
            d_ni = abs(float(q.loc[qs, "net_income_musd"].sum()) + h_ni
                       - float(a.loc[per, "net_income_musd"]))
            d_tx = abs(float(q.loc[qs, "tax_provision_musd"].sum()) + h_tax
                       - float(a.loc[per, "tax_provision_musd"]))
            worst = max(worst, d_ni, d_tx)
            if max(d_ni, d_tx) > 1e-6:
                _fail(f"{per}/{sc} annual NI or tax is not the sum of the quarters "
                      f"({d_ni}, {d_tx})")
    _ok("15 annual net income and tax = sum of quarters (FY26 incl. 1H26 actuals)", worst)

    # 04 — the dollar band and P(beat) come from ONE object
    q3e = float(pl[(pl.scenario == "base") & (pl.quarter == "2026Q3")]["adj_ebitda_musd"].iloc[0])
    qh = float(bands[(bands.target == "adj_ebitda_musd_from_margin")
                     & (bands.horizon_q == 0)
                     & (bands.calibration == "recent_2024Q1plus")]["qhat80"].iloc[0])
    row = card[card.item == "3Q26 adj EBITDA"].iloc[0]
    lo, hi = [float(x) for x in str(row.band80).split(" - ")]
    if abs((lo + hi) / 2 - q3e) > 1.0 or abs((hi - lo) / 2 - qh) > 1.0:
        _fail("the card's dollar band is not the adopted object's own conformal band")
    from math import erf, sqrt
    sd = qh / 1.2816
    st = 2361.52179
    p_expected = 0.5 * (1 + erf((q3e - st) / (sd * sqrt(2))))
    p_card = float(card[card.item == "P(3Q26 adj EBITDA beats Street)"]["value"].iloc[0])
    if abs(p_card - p_expected) > 1e-6:
        _fail(f"P(beat) {p_card:.4f} is not the band-consistent figure {p_expected:.4f}")
    _ok("04 band and P(beat) come from the same registered object", abs(p_card - p_expected))

    # 05 — bear/bull are NOT at the base margin any more
    m = pl[pl.quarter == "2026Q3"].set_index("scenario")["adj_ebitda_margin_pct"]
    if abs(float(m["bear"]) - float(m["base"])) < 1e-9:
        _fail("bear and base 3Q26 margins are identical: the scenario P&L is still "
              "constant-margin")
    print(f"   ok  05 scenario margins differ (3Q26 bear/base/bull "
          f"{m['bear']:.4f} / {m['base']:.4f} / {m['bull']:.4f})")

    # 06 — the EPS band is wider than the EBITDA-only band
    b = pl[(pl.scenario == "base") & (pl.quarter == "2026Q3")].iloc[0]
    if not (b.eps_q90 - b.eps_q10) > (b.eps_q90_ebitda_only - b.eps_q10_ebitda_only):
        _fail("the EPS band does not carry the bridge error")
    print(f"   ok  06 EPS band is joint (${b.eps_q10:.3f}-{b.eps_q90:.3f} vs EBITDA-only "
          f"${b.eps_q10_ebitda_only:.3f}-{b.eps_q90_ebitda_only:.3f})")
    print("all reconciliation checks passed")


# --------------------------------------------------------------------- verify diff
def verify_report():
    print("\n=== MARGIN_VERIFY_ONLY comparison (recomputed vs committed) ===")
    rows = []
    for f in sorted(VOUT.glob("*.csv")):
        ref = OUT / f.name
        if not ref.exists():
            rows.append((f.name, "NEW (no committed file)", np.nan))
            continue
        a, b = pd.read_csv(ref), pd.read_csv(f)
        if list(a.columns) != list(b.columns) or len(a) != len(b):
            rows.append((f.name, f"shape/columns differ: {a.shape}->{b.shape}", np.nan))
            continue
        num = [c for c in a.columns if pd.api.types.is_numeric_dtype(a[c])
               and pd.api.types.is_numeric_dtype(b[c])]
        d = (a[num] - b[num]).abs().to_numpy()
        worst = float(np.nanmax(d)) if d.size else 0.0
        rows.append((f.name, "identical" if worst <= TOL else "DIFFERS", worst))
    w = max(len(r[0]) for r in rows) if rows else 10
    for name, status, worst in rows:
        print(f"  {name:<{w}}  {status:<28}  {'' if np.isnan(worst) else f'max|d|={worst:.6g}'}")
    print(f"({len(rows)} files compared; nothing was written outside {VOUT})")


def main():
    if VERIFY:
        print("*** MARGIN_VERIFY_ONLY=1: no committed output, no registry write ***")
        VOUT.mkdir(parents=True, exist_ok=True)
    step("1 combine", [str(HERE / "combine.py")])
    step("2 diagnostics", [str(HERE / "diagnostics.py")])
    step("3 forecast", [str(HERE / "forecast.py")])
    step("4 workbook", [str(HERE / "workbook.py")])
    checks()
    if VERIFY:
        verify_report()
        print("\nWS23 verify-only done (score.py skipped).")
        return
    if os.environ.get("MARGIN_SKIP_SCORE") == "1":
        print("\n=== 5 score.py SKIPPED (MARGIN_SKIP_SCORE=1) ===")
    else:
        step("5 score.py", [str(SCORE)])
    print("\nWS23 done.")


if __name__ == "__main__":
    main()
