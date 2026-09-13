"""Read-only source-manifest and matched-cell arithmetic audit for C2."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
folder = ROOT / "data/processed/forecast_methods/macro_pulls/review_capture"
manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
total = published = 0
counts = {}
for meta in manifest["sources"]:
    path = folder / meta["normalized_file"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == meta["normalized_sha256"]
    d = pd.read_csv(path)
    assert len(d) == meta["rows"]
    assert {"published_on", "pit_usable", "knowable_from", "unit", "source_url"}.issubset(d)
    assert not d.pit_usable.astype(str).str.lower().eq("true").any()
    assert np.isfinite(d.value.astype(float)).all()
    assert not d.duplicated(["series", "period", "origin", "metric"]).any()
    dated = d[d.published_on.notna()]
    assert (pd.to_datetime(dated.published_on) <= pd.to_datetime(dated.knowable_from)).all()
    total += len(d)
    published += len(dated)
    counts[meta["series"]] = len(d)
assert (len(counts), total, published) == (14, 35124, 124)

cells = pd.read_csv(folder / "ntto_replay_cells.csv")
summary = pd.read_csv(folder / "ntto_replay_summary.csv")
ratios = []
for window in ("W1", "W2"):
    d = cells[cells.source.eq("new_download_calendar_aligned") & cells.window.eq(window) & cells.feature.eq("ntto_total_full")]
    rmse = np.sqrt(np.mean((d.pred_nights_m-d.actual_nights_m)**2))
    base = np.sqrt(np.mean((d.harness_naive_nights_m-d.actual_nights_m)**2))
    target = summary[summary.source.eq("new_download_calendar_aligned") & summary.window.eq(window)
                     & summary.feature.eq("ntto_total_full") & summary.target.eq("nights_m")
                     & summary.baseline.eq("frozen_harness_naive")].iloc[0]
    assert len(d) == target.n
    np.testing.assert_allclose(rmse/base, target.ratio, rtol=0, atol=1e-12)
    ratios.append({"window": window, "n": len(d), "nights_level_rmse_ratio": rmse/base})
assert not cells.historical_pit_admissible.astype(str).str.lower().eq("true").any()
report = {"verdict": "PASS", "manifest_sources": len(counts), "normalized_rows": total,
          "verified_publication_date_rows": published, "historical_PIT_rows": 0,
          "by_source": counts, "independent_ratio_arithmetic": ratios,
          "limit": "This checks capture integrity and arithmetic, not archival release vintages or a predictive edge."}
path = ROOT / "data/processed/forecast_methods/lane2_validation_v1/c2_independent_review.json"
path.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report, indent=2))
