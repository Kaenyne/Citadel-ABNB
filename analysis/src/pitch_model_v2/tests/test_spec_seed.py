import json
from pathlib import Path
import pytest
import yaml
from pitch_model_v2 import spec, spec_seed


def _write_dossiers(root: Path):
    d = root / "docs/pitch-model-v2/dossiers"
    d.mkdir(parents=True, exist_ok=True)
    (d / "H_hist.md").write_text(
        "## 2. The number\n\n"
        "### 2a. Model inputs (machine-readable)\n\n"
        "| item | scenario | period | point | unit | note |\n"
        "|---|---|---|---|---|---|\n"
        "| nights_m | actual | 1Q26 | 143.1 | m | note |\n"
        "| nights_m | actual | 2Q26 | 134.4 | m | note |\n"
    )
    (d / "R_kernel.md").write_text(
        "## 2. The number\n\n"
        "### 2a. Model inputs (machine-readable)\n\n"
        "| item | scenario | period | point | unit | note |\n"
        "|---|---|---|---|---|---|\n"
        "| lambda_q3_pct | base | all | 17.24 | pct | note |\n"
    )
    (d / "F_forecast.md").write_text(
        "### 2a. Model inputs (machine-readable)\n\n"
        "| item | scenario | period | point | unit | note |\n"
        "|---|---|---|---|---|---|\n"
        "| nights_m | base | 3Q26 | 146.3 | m | note |\n"
        "| nights_m | short | 3Q26 | 145.0 | m | note |\n"
        "| nights_m | breaker | 3Q26 | 147.0 | m | note |\n"
    )
    for lid in ("H", "R", "F"):
        rd = root / f"data/processed/pitch_model_v2/receipts/{lid}"
        rd.mkdir(parents=True, exist_ok=True)
        (rd / "receipt.json").write_text(json.dumps({"id": lid, "exit_code": 0}))


MAPPING = """
meta:
  price_date: "2026-09-16"
  spot: 167.51
  scenarios: [base, short, breaker]
  periods: [1Q26, 2Q26, 3Q26, ALL]

lines:
  - id: NIGHTS
    label: Nights (m)
    unit: m
    block: drivers
    kind: input
    periods: [1Q26, 2Q26, 3Q26]
    provenance:
      - periods: [1Q26, 2Q26]
        item: nights_m
        dossier: docs/pitch-model-v2/dossiers/H_hist.md
        receipt: data/processed/pitch_model_v2/receipts/H/receipt.json
        grade: B
        decision: DEC-0001
        tolerance: 0.1
        scenario_map: {base: actual, short: actual, breaker: actual}
      - periods: [3Q26]
        item: nights_m
        dossier: docs/pitch-model-v2/dossiers/F_forecast.md
        receipt: data/processed/pitch_model_v2/receipts/F/receipt.json
        grade: B
        decision: DEC-0002
        tolerance: 0.1
  - id: LAM_Q3
    label: Lambda Q3 (pct)
    unit: pct
    block: revenue
    kind: input
    periods: [ALL]
    provenance:
      - periods: [ALL]
        item: lambda_q3_pct
        dossier: docs/pitch-model-v2/dossiers/R_kernel.md
        receipt: data/processed/pitch_model_v2/receipts/R/receipt.json
        grade: B
        decision: DEC-0003
        tolerance: 0.01
        scenario_map: {base: base, short: base, breaker: base}
  - id: GBV
    label: GBV ($M)
    unit: musd
    block: drivers
    kind: formula
    periods: [1Q26, 2Q26, 3Q26]
    expr: "NIGHTS * NIGHTS"
"""


def _write_mapping(root: Path) -> Path:
    p = root / "model/pitch_model_v2/spec/mapping.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(MAPPING)
    return p


def test_generates_lines_yaml_that_loads_and_carries_values(tmp_path):
    _write_dossiers(tmp_path)
    mapping_path = _write_mapping(tmp_path)
    out_path = tmp_path / "model/pitch_model_v2/spec/lines.yaml"
    spec_seed.write(mapping_path, out_path, root=tmp_path)

    s = spec.load(out_path, check_paths=False)
    nights = s.lines["NIGHTS"]
    assert nights.values["base"]["1Q26"] == 143.1
    assert nights.values["base"]["2Q26"] == 134.4
    assert nights.values["base"]["3Q26"] == 146.3
    assert nights.values["short"]["3Q26"] == 145.0
    assert nights.values["breaker"]["3Q26"] == 147.0

    lam = s.lines["LAM_Q3"]
    for sc in ("base", "short", "breaker"):
        assert lam.values[sc]["ALL"] == 17.24

    gbv = s.lines["GBV"]
    assert gbv.kind == "formula"
    raw_lines = yaml.safe_load(out_path.read_text())["lines"]
    raw_gbv = next(d for d in raw_lines if d["id"] == "GBV")
    assert "values" not in raw_gbv


def test_missing_item_raises_needs_context(tmp_path):
    _write_dossiers(tmp_path)
    mapping_path = _write_mapping(tmp_path)
    bad = mapping_path.read_text().replace(
        "item: nights_m\n        dossier: docs/pitch-model-v2/dossiers/F_forecast.md",
        "item: nights_m_typo\n        dossier: docs/pitch-model-v2/dossiers/F_forecast.md",
    )
    mapping_path.write_text(bad)
    out_path = tmp_path / "model/pitch_model_v2/spec/lines.yaml"
    with pytest.raises(spec_seed.SpecSeedError, match="NEEDS_CONTEXT"):
        spec_seed.write(mapping_path, out_path, root=tmp_path)
