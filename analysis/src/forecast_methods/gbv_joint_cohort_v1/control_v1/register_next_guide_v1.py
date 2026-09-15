"""Register a reviewed same-cutoff joint/fixed next-guide snapshot, additively."""
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
METHOD = "gbv-joint-next-guide-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_rows(points):
    if len(points) != 2 or set(points.model) != {"joint", "fixed"}:
        raise ValueError("Exactly one joint and one fixed point are required")
    for field in ["quarter", "origin_date", "last_company_publication", "cushion_pct"]:
        if points[field].nunique(dropna=False) != 1:
            raise ValueError(f"Methods must share {field}")
    records = []
    for r in points.itertuples():
        if r.quarter != "2026Q4" or r.origin_date != "2026-09-15":
            raise ValueError("Unexpected target or registered calculation date")
        if pd.Timestamp(r.last_company_publication) > pd.Timestamp(r.origin_date):
            raise ValueError("Publication cannot postdate the calculation cutoff")
        if int(r.n_params_guide) != (8 if r.model == "joint" else 5):
            raise ValueError("Frozen parameter count changed")
        if int(r.n_train) <= 0 or not np.isfinite(r.guide_mid_musd) or r.guide_mid_musd <= 0:
            raise ValueError("Invalid training sample or guide point")
        if not np.isclose(r.guide_mid_musd * (1 + r.cushion_pct / 100), r.revenue_musd,
                          rtol=1e-11, atol=1e-7):
            raise ValueError("Revenue/guide/cushion identity failed")
        records.append(dict(method=METHOD, object=f"{r.model}-guide", target="guide_mid",
            quarter=r.quarter, vintage_date=r.origin_date,
            horizon_q=pd.Period(r.quarter, freq="Q").ordinal-pd.Timestamp(r.origin_date).to_period("Q").ordinal,
            point=float(r.guide_mid_musd), q50=float(r.guide_mid_musd), window="LIVE", prior_basis="PIT",
            n_params=int(r.n_params_guide), n_train=int(r.n_train), knowable_from=r.last_company_publication,
            spec_id=f"frozen_{r.model}_rule_same_cutoff_q4_2026_v1",
            notes="Research snapshot, not promoted; calculation vintage 2026-09-15 using last published company inputs "
                  + str(r.last_company_publication)
                  + "; current Q3 and target Q4 GBV are projected where needed; historical replay rule unchanged; "
                  "shared trailing-eight mean cushion; q50 is a point-only format placeholder, no calibrated interval; "
                  "no same-date Street edge established; cohort allocation is not physical survival"))
    return pd.DataFrame(records)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--points", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--write", action="store_true")
    a = p.parse_args()
    if a.out.exists():
        raise FileExistsError("Use a fresh output directory")
    rows = build_rows(pd.read_csv(a.points))
    os.environ["CITADEL_ABNB_RUN_DATE"] = "2026-09-15"
    sys.path.insert(0, str(ROOT / "analysis/src/forecast_methods"))
    reg = importlib.import_module("harness_v1_1.registry")
    original = reg.P.REGISTRY_DIR
    destinations = [original / f"{METHOD}__{obj}.csv" for obj in rows.object]
    if any(path.exists() for path in destinations):
        raise FileExistsError("Refusing to replace a registered forecast")
    stage = a.out.resolve() / "prepared_registry"
    stage.mkdir(parents=True)
    try:
        reg.P.REGISTRY_DIR = stage
        for _, group in rows.groupby("object"):
            reg.register(group, quiet=True)
    finally:
        reg.P.REGISTRY_DIR = original
    if a.write:
        for path in destinations:
            with path.open("xb") as f:
                f.write((stage / path.name).read_bytes())
    receipt = dict(status="registered" if a.write else "prepared_only", method=METHOD,
                   rows=len(rows), source_sha256=sha(a.points), script_sha256=sha(Path(__file__)),
                   staged_sha256={path.name: sha(path) for path in sorted(stage.glob("*.csv"))},
                   forecast_promoted=False, calibrated_intervals=False, street_comparison=False)
    (a.out / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
