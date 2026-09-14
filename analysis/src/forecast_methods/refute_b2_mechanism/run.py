"""Independent B2 mechanism audit. Read-only inputs; new timestamped output per run."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "data/processed/forecast_methods"
B2 = DATA / "alpha_b2/run_20260913T171654_499731Z"
INPUTS = {
    "cells": B2 / "cells.csv",
    "guidance": ROOT / "data/processed/overnight/02_guidance_ledger.csv",
    "returns": DATA / "returns_v1/earnings_reactions_open_v1.csv",
    "vintages": DATA / "L0/L0_vintage_register.csv",
}


def corr(x, y):
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    return float(np.corrcoef(x, y)[0, 1]) if len(x) >= 3 and np.ptp(x) > 1e-12 and np.ptp(y) > 1e-12 else None


def residual(y, *xs):
    design = np.column_stack([np.ones(len(y)), *xs])
    if np.linalg.matrix_rank(design) != design.shape[1]:
        raise ValueError("Rank deficient diagnostic")
    return np.asarray(y) - design @ np.linalg.lstsq(design, y, rcond=None)[0]


def hits(x, y):
    return int(np.sum(np.sign(x) == np.sign(y)))


def main():
    started = time.perf_counter()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    out = DATA / "refute_b2_mechanism" / ("run_" + stamp)
    out.mkdir(parents=True, exist_ok=False)
    frames = {k: pd.read_csv(v, comment="#") for k, v in INPUTS.items()}
    cells = frames["cells"]
    cells = cells[cells.prior_basis.eq("PIT") & np.isclose(cells.weight, 2 / 3)].copy()
    assert not cells.event_date.duplicated().any()
    vintages = frames["vintages"].set_index("register_id", verify_integrity=True)
    for prefix, role in (("c_pre", "pre_guide"), ("c_next", "at_print")):
        for row in cells.dropna(subset=[prefix + "_register_id"]).to_dict("records"):
            source = vintages.loc[row[prefix + "_register_id"]]
            assert source.role == role
            assert str(source.pit_usable).lower() == "true"
            assert str(source.vendor_attributed).lower() == "true"
            assert source.vendor == row[prefix + "_vendor"]
            assert str(source.as_of_timestamp) == row[prefix + "_as_of_timestamp"]
            assert np.isclose(source.value, row[prefix + "_value"], atol=1e-10, rtol=0)
    cells["s_rebuilt"] = 100 * (cells.k_q1_musd / cells.c_pre_value - 1)
    cells["r_rebuilt"] = 100 * (cells.c_next_value / cells.c_pre_value - 1)
    assert np.allclose(cells.s1_pct, cells.s_rebuilt, atol=1e-10, rtol=0, equal_nan=True)
    assert np.allclose(cells.revision_pct, cells.r_rebuilt, atol=1e-10, rtol=0, equal_nan=True)
    guide = frames["guidance"]
    guide = guide[guide.metric.eq("revenue_usd_m") & guide.horizon_quarters.eq(1)].copy()
    guide["guided_quarter"] = guide.target_period.map(lambda q: "20" + q[2:] + "Q" + q[0])
    guide = guide[["print_date", "guided_quarter", "value_low", "value_high", "value_mid", "source_file"]]
    cells = cells.merge(guide, left_on=["event_date", "guided_quarter"], right_on=["print_date", "guided_quarter"], how="left", validate="one_to_one")
    assert cells.value_mid.notna().all()
    assert np.allclose(cells.value_mid, (cells.value_low + cells.value_high) / 2)
    raw_returns = frames["returns"].set_index("event_date", verify_integrity=True)
    for h in (20, 60):
        col = f"excess_open_{h}d_pct"
        assert np.allclose(cells[col], raw_returns.loc[cells.event_date, col], atol=1e-10, rtol=0, equal_nan=True)
        cells[f"raw_open_{h}d_pct"] = raw_returns.loc[cells.event_date, f"open_{h}d_pct"].to_numpy()
    assert np.allclose(cells.value_mid, raw_returns.loc[cells.event_date, "guide_mid_musd"])
    cells["guide_gap"] = 100 * (cells.value_mid / cells.c_pre_value - 1)
    cells["kernel_vs_guide"] = cells.s_rebuilt - cells.guide_gap
    cells["revision_beyond_guide"] = cells.r_rebuilt - cells.guide_gap
    cells["consensus_moved_closer_to_guide"] = (cells.c_next_value - cells.value_mid).abs() < (cells.c_pre_value - cells.value_mid).abs()
    cells.to_csv(out / "audit_cells.csv", index=False)
    summaries, return_rows, loo_rows = [], [], []
    for window, first in (("W1", "2023Q1"), ("W2", "2024Q1")):
        paired = cells[cells.guided_quarter.ge(first)].dropna(subset=["s_rebuilt", "r_rebuilt"]).copy()
        strong = paired[paired.s_rebuilt.abs().gt(.5)]
        moving = strong[strong.r_rebuilt.ne(0)]
        s, r, g = [paired[col].to_numpy() for col in ("s_rebuilt", "r_rebuilt", "guide_gap")]
        rss_guide = float(np.sum(residual(r, g) ** 2))
        rss_both = float(np.sum(residual(r, g, s) ** 2))
        sst = float(np.sum((r - r.mean()) ** 2))
        summaries.append(dict(window=window, paired_n=len(paired), strong_n=len(strong), kernel_hits=hits(strong.s_rebuilt, strong.r_rebuilt),
            guide_hits_on_kernel_strong=hits(strong.guide_gap, strong.r_rebuilt),
            kernel_guide_sign_agreement_strong=hits(strong.s_rebuilt, strong.guide_gap),
            kernel_revision_corr=corr(s, r), guide_revision_corr=corr(g, r), kernel_guide_corr=corr(s, g),
            kernel_revision_partial_corr_given_guide=corr(residual(s, g), residual(r, g)),
            guide_only_r_squared=1 - rss_guide / sst, guide_plus_kernel_r_squared=1 - rss_both / sst,
            beyond_guide_kernel_gap_corr=corr(paired.kernel_vs_guide, paired.revision_beyond_guide),
            beyond_guide_kernel_gap_sign_hits=hits(paired.kernel_vs_guide, paired.revision_beyond_guide),
            moving_revision_strong_n=len(moving), moving_revision_kernel_hits=hits(moving.s_rebuilt, moving.r_rebuilt),
            zero_revision_strong_n=int(strong.r_rebuilt.eq(0).sum()),
            moved_closer_to_guide_n=int(paired.consensus_moved_closer_to_guide.sum()),
            median_abs_initial_guide_gap_pct=float(paired.guide_gap.abs().median()),
            median_abs_remaining_guide_gap_pct=float(paired.revision_beyond_guide.abs().median())))
        # Original return estimand: threshold signal on all nonmissing return pairs.
        signal_rows = cells[cells.guided_quarter.ge(first)].dropna(subset=["s_rebuilt"])
        signal_rows = signal_rows[signal_rows.s_rebuilt.abs().gt(.5)]
        for h in (20, 60):
            col = f"excess_open_{h}d_pct"
            sample = signal_rows.dropna(subset=[col]).copy()
            aligned = np.sign(sample.s_rebuilt) * sample[col]
            raw_aligned = np.sign(sample.s_rebuilt) * sample[f"raw_open_{h}d_pct"]
            loo = []
            for idx, row in sample.iterrows():
                mean = float(aligned.drop(index=idx).mean())
                loo.append(mean)
                loo_rows.append(dict(window=window, horizon=h, omitted_event=row.event_date, remaining_n=len(sample)-1, aligned_excess_mean_pct=mean))
            return_rows.append(dict(window=window, horizon=h, n=len(sample), aligned_excess_mean_pct=float(aligned.mean()),
                aligned_raw_mean_pct=float(raw_aligned.mean()), aligned_positive_count=int(aligned.gt(0).sum()),
                guide_aligned_excess_mean_same_cells_pct=float((np.sign(sample.guide_gap) * sample[col]).mean()),
                leave_one_out_min_pct=min(loo), leave_one_out_max_pct=max(loo), leave_one_out_positive_count=sum(x > 0 for x in loo)))
    pd.DataFrame(summaries).to_csv(out / "mechanism_statistics.csv", index=False)
    pd.DataFrame(return_rows).to_csv(out / "return_statistics.csv", index=False)
    pd.DataFrame(loo_rows).to_csv(out / "return_leave_one_out.csv", index=False)
    manifest = {k: {"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for k, p in INPUTS.items()}
    (out / "input_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    assert [(x["kernel_hits"], x["strong_n"]) for x in summaries] == [(5, 9), (4, 7)]
    assert all(x["aligned_excess_mean_pct"] < 0 for x in return_rows)
    result = {"elapsed_seconds": time.perf_counter() - started, "output_directory": str(out.relative_to(ROOT)), "mechanism": summaries, "returns": return_rows,
        "assertions": "Source IDs, source values, roles, attribution, timestamps, paired arithmetic, unique joins, guide midpoint, return cells and exact claim verified"}
    (out / "summary.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
