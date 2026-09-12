#!/usr/bin/env python
"""COPY THIS. Minimal example of registering a package's forecasts with the harness.

  /Users/theomachado/.venvs/citadel-abnb/bin/python analysis/src/forecast_methods/harness/EXAMPLE.py

It writes nothing: it builds a frame, validates it, prints it, and stops. Delete the
`dry_run` guard at the bottom and call `register(df)` from your own package's run.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from harness import (GUIDE_EVENTS_ALL, TARGET_TO_GUIDE_DATE, window_of_target,  # noqa: E402
                     history_as_of, load_targets, validate_registry_frame, register,
                     baseline_naive, quarters as Q)


def my_forecast(vintage_date, target_quarter, prior_basis):
    """Replace this with your model. Must use ONLY the information set at vintage_date."""
    hist = history_as_of(vintage_date, "revenue_musd")      # print_date <= vintage_date
    lag4 = Q.shift(target_quarter, -4)
    base = float(hist.loc[hist["quarter"] == lag4, "revenue_musd"].iloc[0])
    point = base * 1.15
    sd = point * 0.025
    return {"point": point, "q50": point,
            "q10": point - 1.2816 * sd, "q90": point + 1.2816 * sd, "sd": sd,
            "n_train": len(hist), "n_params": 1}


def build(dry_run: bool = True):
    rows = []
    for gdate, tq in GUIDE_EVENTS_ALL:
        for win in window_of_target(tq):          # a 2024Q1+ target is in BOTH W1 and W2
            for basis in ("PIT", "full_sample"):  # BOTH replays are mandatory
                f = my_forecast(gdate, tq, basis)
                rows.append({
                    "method": "example-package", "object": "demo",
                    "target": "revenue_musd", "quarter": tq, "vintage_date": gdate,
                    "horizon_q": Q.to_index(tq) - Q.to_index(Q.quarter_of_date(gdate)),
                    "window": win, "prior_basis": basis,
                    "spec_id": "demo|v1", "notes": "example only",
                    **f})
    df = pd.DataFrame(rows)
    clean = validate_registry_frame(df)     # raises on any format or PIT violation
    print(clean.head(4).to_string())
    print(f"\n{len(clean)} rows validated OK "
          f"({clean['window'].value_counts().to_dict()})")
    if not dry_run:
        register(df)                         # -> registry/example-package__demo.csv
    else:
        print("\n(dry run: nothing written. call register(df) from your own run.py)")


if __name__ == "__main__":
    build(dry_run=True)
