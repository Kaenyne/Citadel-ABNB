"""WS21 check 01: mechanical PIT rules over every registry file in the margin registry.

Runs against a SNAPSHOT of the registry (default: the live registry) and reports, per
(method, object, spec_id):
  A. knowable_from > vintage_date            (an input dated after the vintage)
  B. street_as_of  > vintage_date            (the kill-list "September consensus at a historical date")
  C. the target quarter had already PRINTED on or before the vintage date (forecasting the past)
  D. horizon_q inconsistent with vintage_date and quarter
  E. window / vintage-date consistency (W1 rows at W1 guide dates, etc.)
  F. quantile monotonicity q05<=q10<=...<=q95 and q50 vs point
  G. duplicated keys (method, object, target, quarter, vintage_date, horizon_q, window, prior_basis, spec_id)
  H. the two-replay rule per (object, target, spec_id)

Usage:  py -3.13 analysis/src/margin_build/21_red_team/checks/check_01_registry_pit_rules.py [registry_dir]
"""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
sys.path.insert(0, str(REPO / "analysis" / "src" / "margin_build" / "10_harness_margin"))
from harness_margin import Q, W, TODAY, load_targets  # noqa: E402

REG = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "data/processed/margin_build/registry"
QC = ["q05", "q10", "q25", "q50", "q75", "q90", "q95"]
KEY = ["method", "object", "target", "quarter", "vintage_date", "horizon_q", "window", "prior_basis", "spec_id"]


def main() -> int:
    t = load_targets()
    pdm = {r.quarter: r.print_date for r in t.itertuples() if pd.notna(r.print_date)}
    rows = []
    for f in sorted(REG.glob("*__*.csv")):
        d = pd.read_csv(f)
        d["vintage_date"] = pd.to_datetime(d["vintage_date"]).dt.date
        d["quarter"] = d["quarter"].map(Q.canon)
        if "spec_id" not in d.columns:
            d["spec_id"] = ""
        d["spec_id"] = d["spec_id"].fillna("")
        for c in ("knowable_from", "street_as_of"):
            d[c] = pd.to_datetime(d[c], errors="coerce").dt.date if c in d.columns else None
        kf = d["knowable_from"] if "knowable_from" in d.columns else pd.Series([None] * len(d))
        sa = d["street_as_of"] if "street_as_of" in d.columns else pd.Series([None] * len(d))
        a = sum(1 for k, v in zip(kf, d["vintage_date"]) if pd.notna(k) and k > v)
        b = sum(1 for k, v in zip(sa, d["vintage_date"]) if pd.notna(k) and k > v)
        c = sum(1 for q, v in zip(d["quarter"], d["vintage_date"])
                if pdm.get(q) is not None and pd.notna(pdm[q]) and pdm[q] <= v)
        dd = sum(1 for q, v, h in zip(d["quarter"], d["vintage_date"], d["horizon_q"])
                 if Q.to_index(q) - Q.to_index(Q.quarter_of_date(v)) != int(h))
        e = 0
        for r in d.itertuples():
            if r.window == "W1" and r.vintage_date not in W.GUIDE_DATES_W1:
                e += 1
            if r.window == "W2" and r.vintage_date not in W.GUIDE_DATES_W2:
                e += 1
            if r.window == "LIVE" and r.vintage_date not in (W.GUIDE_DATE_LIVE, TODAY):
                e += 1
        have = [q for q in QC if q in d.columns]
        fviol = 0
        if len(have) >= 2:
            qm = d[have].to_numpy(dtype=float)
            fviol = int((qm[:, 1:] < qm[:, :-1] - 1e-9).any(axis=1).sum())
        g = int(d.duplicated([k for k in KEY if k in d.columns]).sum())
        reps = d.groupby([k for k in ["object", "target", "spec_id", "horizon_q"] if k in d.columns]
                         )["prior_basis"].nunique()
        h = int((reps < 2).sum())
        rows.append(dict(file=f.name, n_rows=len(d), specs=d["spec_id"].nunique(),
                         A_knowable_after_vintage=a, B_street_as_of_after_vintage=b,
                         C_quarter_already_printed=c, D_horizon_mismatch=dd, E_window_vintage=e,
                         F_quantiles_non_monotone=fviol, G_duplicate_keys=g, H_single_replay_groups=h))
    out = pd.DataFrame(rows)
    with pd.option_context("display.width", 220, "display.max_columns", 30):
        print(out.to_string(index=False))
    bad = out[(out[[c for c in out.columns if c[0] in "ABCDEFGH" and "_" in c]].sum(axis=1)) > 0]
    print(f"\nfiles with at least one violation: {len(bad)} of {len(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
