"""Independently check B2 PIT cells, returned revisions and return legs."""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
from kernel_engine_v2 import engine as K

parser = argparse.ArgumentParser()
parser.add_argument("--run", required=True)
args = parser.parse_args()
folder = ROOT / args.run
data = ROOT / "data/processed/forecast_methods"
cells = pd.read_csv(folder / "cells.csv")
cells = cells[cells.prior_basis.eq("PIT") & np.isclose(cells.weight, 2/3)].copy()
vintages = pd.read_csv(data / "L0/L0_vintage_register.csv", comment="#").set_index("register_id")
returns = pd.read_csv(data / "returns_v1/earnings_reactions_open_v1.csv").set_index("event_date")
checks = 0
for row in cells.itertuples():
    for prefix, role, date in (("c_pre", "pre_guide", row.event_date), ("c_next", "at_print", row.next_event_date)):
        source_id = getattr(row, prefix + "_register_id")
        if pd.isna(source_id):
            continue
        source = vintages.loc[source_id]
        assert source.role == role and source.period == row.guided_quarter
        assert str(source.pit_usable).lower() == str(source.vendor_attributed).lower() == "true"
        assert str(source.as_of_timestamp)[:10] == date
        assert source.vendor == getattr(row, prefix + "_vendor")
        assert source.value == getattr(row, prefix + "_value")
    if np.isfinite(row.revision_pct):
        np.testing.assert_allclose(100*(row.c_next_value/row.c_pre_value-1), row.revision_pct, rtol=0, atol=1e-9)
    if np.isfinite(row.k_q1_musd):
        k = K.kernel_guide(row.guided_quarter, pd.Timestamp(row.event_date)+pd.Timedelta(days=1))
        np.testing.assert_allclose(k["point"], row.k_q1_musd, rtol=0, atol=1e-8)
        assert pd.Timestamp(k["knowable_from"]) <= pd.Timestamp(row.event_date)
        checks += 1
    for h in (20, 60):
        field = f"excess_open_{h}d_pct"
        np.testing.assert_allclose(getattr(row, field), returns.loc[row.event_date, field], rtol=0, atol=1e-9, equal_nan=True)
        assert returns.loc[row.event_date, "entry_date"] > row.event_date
stats = pd.read_csv(folder / "statistics.csv")
summary = []
for window, start in (("W1", "2023Q1"), ("W2", "2024Q1")):
    sample = cells[cells.guided_quarter.ge(start)].dropna(subset=["s1_pct", "revision_pct"])
    selected = sample[sample.s1_pct.abs().gt(.5)]
    hits = int((np.sign(selected.s1_pct) == np.sign(selected.revision_pct)).sum())
    corr = sample.s1_pct.corr(sample.revision_pct)
    saved = stats[stats.window.eq(window) & stats.prior_basis.eq("PIT") & stats.signal.eq("s1_pct")].iloc[0]
    assert (len(sample), len(selected), hits) == (saved.n_pairs, saved.n_strong, saved.hits)
    np.testing.assert_allclose(corr, saved["corr"], rtol=0, atol=1e-10)
    summary.append({"window": window, "evaluable": len(sample), "high_signal": len(selected), "hits": hits, "correlation": corr})
report = {"verdict": "PASS", "saved_run": args.run, "candidate_origins": len(cells),
          "imported_K0_guides_recomputed": checks, "return_cells": 2*len(cells), "statistics": summary}
(data / "lane2_validation_v1/b2_independent_review.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report, indent=2))
