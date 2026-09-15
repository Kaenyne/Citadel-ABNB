"""Add frozen release-origin forecasts and labelled LIVE research points only."""
from pathlib import Path
import argparse
import hashlib
import importlib
import json
import os
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
METHOD = "gbv-decision-0915-v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_rows(p):
    records = []
    p = p[p.model.isin(["joint", "fixed", "guide_growth", "revenue_growth"])].copy()
    if p.duplicated(["model", "target", "horizon_quarters", "origin_date"]).any():
        raise ValueError("Duplicate production point")
    for r in p.itertuples():
        if not r.point_in_time_eligible or r.oracle_future_information_used:
            raise ValueError("Oracle/future information cannot register")
        origin = pd.Timestamp(r.origin_date)
        if pd.Timestamp(r.knowable_from) > origin:
            raise ValueError("Future information date")
        if not r.is_live and origin >= pd.Timestamp(r.guide_event_date):
            raise ValueError("Guide already issued at historical forecast origin")
        if r.is_live and (r.origin_date != "2026-09-15" or r.target not in ["2026Q4", "2027Q1", "2027Q2"]):
            raise ValueError("Unexpected LIVE strip")
        horizon = pd.Period(r.target, freq="Q").ordinal - origin.to_period("Q").ordinal
        windows = ["LIVE"] if r.is_live else ["W1"] + (["W2"] if r.target >= "2024Q1" else [])
        objects = [("guide", "guide_mid", r.guide_mid_musd, r.n_params_guide)]
        if r.model in ["joint", "fixed"]:
            objects.append(("revenue", "revenue_musd", r.revenue_musd, r.n_params_revenue))
        for window in windows:
            for label, target, value, params in objects:
                if not np.isfinite(value) or value <= 0 or horizon < 0:
                    raise ValueError("Invalid point or horizon")
                records.append(dict(method=METHOD, object=f"{r.model}-p{r.horizon_quarters}-{label}",
                    target=target, quarter=r.target, vintage_date=r.origin_date, horizon_q=horizon,
                    point=float(value), q50=float(value), window=window, prior_basis="PIT",
                    n_params=int(params), n_train=int(r.n_train), knowable_from=r.knowable_from,
                    spec_id=f"frozen_{r.model}_p_plus_{r.horizon_quarters}_guide_race_v1",
                    notes="Research only; not promoted. Historical points use prior release dates; LIVE calculation uses September15 "
                          "with company information through August6. Shared trailing-eight mean cushion where applicable. "
                          "Simple growth rules fit no regression and report n_train=0; source anchors are separately recorded. "
                          "q50 is point-format placeholder; no calibrated distribution. Cohort dollars are model allocations. "
                          "Use local same-origin comparisons because frozen scorer baseline join omits forecast origin."))
    d = pd.DataFrame(records)
    if d.empty or d.duplicated(["object", "quarter", "vintage_date", "window"]).any():
        raise ValueError("Empty or duplicate registry payload")
    return d


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Use a new output directory")
    data = build_rows(pd.read_csv(args.predictions))
    os.environ["CITADEL_ABNB_RUN_DATE"] = "2026-09-15"
    sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
    reg = importlib.import_module("harness_v1_1.registry")
    original = reg.P.REGISTRY_DIR
    planned = [reg.registry_path(METHOD, obj) for obj in data.object.unique()]
    if any(path.exists() for path in planned):
        raise FileExistsError("Existing registry object must not be replaced")
    stage = args.out.resolve() / "prepared_registry"
    stage.mkdir(parents=True)
    try:
        reg.P.REGISTRY_DIR = stage
        for _, frame in data.groupby("object"):
            reg.register(frame, allow_single_replay=True, quiet=True)
    finally:
        reg.P.REGISTRY_DIR = original
    if args.write:
        for path in planned:
            with path.open("xb") as f:
                f.write((stage / path.name).read_bytes())
    receipt = dict(mode="registered" if args.write else "prepared_only", rows=len(data), objects=len(planned),
                   rows_by_window={key: int(value) for key, value in data.groupby("window").size().items()},
                   source_sha256=sha(args.predictions), code_sha256=sha(__file__),
                   staged_sha256={p.name: sha(p) for p in sorted(stage.iterdir())},
                   oracle_rows_registered=0, non_earnings_historical_rows_registered=0,
                   promotion=False, predictive_intervals=False,
                   caveat="PIT reconstruction on reused historical data with inherited input vintages; not independently certified live archive")
    (args.out / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
