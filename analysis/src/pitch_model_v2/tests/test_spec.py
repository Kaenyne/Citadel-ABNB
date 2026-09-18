from pathlib import Path
import pytest
from pitch_model_v2 import spec

FIX = Path(__file__).parent / "fixtures" / "spec_small.yaml"

def test_load_orders_formulas_after_inputs():
    s = spec.load(FIX, check_paths=False)
    assert s.order.index("D6") > s.order.index("D1")
    assert s.order.index("R2") > s.order.index("D6")
    assert s.lines["D1"].kind == "input"
    assert s.lines["D6"].kind == "formula"

def test_to_excel_shifts_periods():
    periods = ["1Q26", "2Q26", "3Q26", "4Q26", "FY26"]
    out = spec.to_excel("LAM * (2/3*D6[-1] + 1/3*D6[-2])", "3Q26", periods)
    assert out == "LAM_3Q26*(2/3*D6_2Q26+1/3*D6_1Q26)"

def test_to_excel_absolute_period():
    periods = ["3Q26", "4Q26", "FY26"]
    assert spec.to_excel("R2@3Q26 + R2@4Q26", "FY26", periods) == "R2_3Q26+R2_4Q26"

def test_rejects_unknown_id(tmp_path):
    bad = FIX.read_text().replace("D1 * D4T", "D1 * NOPE")
    p = tmp_path / "bad.yaml"; p.write_text(bad)
    with pytest.raises(spec.SpecError, match="NOPE"):
        spec.load(p, check_paths=False)

def test_rejects_grade_c(tmp_path):
    bad = FIX.read_text().replace("grade: B", "grade: C")
    p = tmp_path / "bad.yaml"; p.write_text(bad)
    with pytest.raises(spec.SpecError, match="grade"):
        spec.load(p, check_paths=False)

def test_rejects_missing_scenario_value(tmp_path):
    bad = FIX.read_text().replace("short: {3Q26: 0.1724, 4Q26: 0.1203}", "short: {3Q26: 0.1724}")
    p = tmp_path / "bad.yaml"; p.write_text(bad)
    with pytest.raises(spec.SpecError, match="LAM.*4Q26"):
        spec.load(p, check_paths=False)

def test_rejects_shift_out_of_range(tmp_path):
    bad = """
meta:
  periods: [1Q26, 2Q26]
  scenarios: [base]
lines:
  - id: D1
    label: Driver
    unit: m
    block: drivers
    kind: input
    periods: [1Q26, 2Q26]
    values:
      base: {1Q26: 1.0, 2Q26: 2.0}
    provenance: {dossier: d.md, receipt: r.json, grade: A, decision: DEC-0001, tolerance: 0.1}
  - id: F
    label: Formula
    unit: m
    block: drivers
    kind: formula
    periods: [1Q26]
    expr: "D1[-1]"
"""
    p = tmp_path / "bad.yaml"; p.write_text(bad)
    with pytest.raises(spec.SpecError, match="falls outside the period list"):
        spec.load(p, check_paths=False)

def test_rejects_duplicate_id(tmp_path):
    d1_block = (
        "  - id: D1\n"
        "    label: Nights (m)\n"
        "    unit: m\n"
        "    block: drivers\n"
        "    kind: input\n"
        "    periods: [1Q26, 2Q26, 3Q26, 4Q26]\n"
        "    values:\n"
        "      base:  {1Q26: 143.1, 2Q26: 134.4, 3Q26: 146.3, 4Q26: 133.2}\n"
        "      short: {1Q26: 143.1, 2Q26: 134.4, 3Q26: 145.0, 4Q26: 131.0}\n"
        "    provenance: {dossier: docs/pitch-model-v2/dossiers/D1_nights.md, receipt: data/processed/pitch_model_v2/receipts/D1/receipt.json, grade: A, decision: DEC-0001, tolerance: 0.1}\n"
    )
    bad = FIX.read_text().replace("  - id: D4T", d1_block + "  - id: D4T", 1)
    p = tmp_path / "bad.yaml"; p.write_text(bad)
    with pytest.raises(spec.SpecError, match="duplicate id D1"):
        spec.load(p, check_paths=False)

def test_rejects_cycle(tmp_path):
    bad = """
meta:
  periods: [1Q26]
  scenarios: []
lines:
  - id: A
    label: A
    unit: m
    block: drivers
    kind: formula
    periods: [1Q26]
    expr: "B"
  - id: B
    label: B
    unit: m
    block: drivers
    kind: formula
    periods: [1Q26]
    expr: "A"
"""
    p = tmp_path / "bad.yaml"; p.write_text(bad)
    with pytest.raises(spec.SpecError, match="cycle through"):
        spec.load(p, check_paths=False)

def test_to_excel_functions():
    periods = ["2Q26", "3Q26", "4Q26"]
    expr = "EXP(SEASQ4 + BETA * LN(0.4*D6 + 0.4*D6[-1] + 0.2*D6[-2]))"
    out = spec.to_excel(expr, "4Q26", periods)
    assert out == "EXP(SEASQ4_4Q26+BETA_4Q26*LN(0.4*D6_4Q26+0.4*D6_3Q26+0.2*D6_2Q26))"

def test_rejects_function_without_paren():
    with pytest.raises(spec.SpecError, match="EXP"):
        spec.parse_expr("EXP + D1")

def test_load_formula_with_functions(tmp_path):
    y = """
meta:
  periods: [2Q26, 3Q26, 4Q26]
  scenarios: [base]
lines:
  - id: D6
    label: GBV
    unit: musd
    block: drivers
    kind: input
    periods: [2Q26, 3Q26, 4Q26]
    values:
      base: {2Q26: 100.0, 3Q26: 110.0, 4Q26: 120.0}
    provenance: {dossier: d.md, receipt: r.json, grade: A, decision: DEC-0001, tolerance: 0.1}
  - id: SEASQ4
    label: Seasonal Q4 term
    unit: pct
    block: revenue
    kind: input
    periods: [4Q26]
    values:
      base: {4Q26: 0.1}
    provenance: {dossier: d.md, receipt: r.json, grade: A, decision: DEC-0002, tolerance: 0.01}
  - id: BETA
    label: Beta coefficient
    unit: x
    block: revenue
    kind: input
    periods: [4Q26]
    values:
      base: {4Q26: 1.2}
    provenance: {dossier: d.md, receipt: r.json, grade: A, decision: DEC-0003, tolerance: 0.01}
  - id: R4
    label: Log-linear guide
    unit: musd
    block: revenue
    kind: formula
    periods: [4Q26]
    expr: "EXP(SEASQ4 + BETA * LN(0.4*D6 + 0.4*D6[-1] + 0.2*D6[-2]))"
"""
    p = tmp_path / "ok.yaml"; p.write_text(y)
    s = spec.load(p, check_paths=False)
    assert s.order[-1] == "R4"

def test_rejects_id_equal_to_function_name(tmp_path):
    y = """
meta:
  periods: [1Q26]
  scenarios: [base]
lines:
  - id: LN
    label: Bad id
    unit: m
    block: drivers
    kind: input
    periods: [1Q26]
    values:
      base: {1Q26: 1.0}
    provenance: {dossier: d.md, receipt: r.json, grade: A, decision: DEC-0001, tolerance: 0.1}
"""
    p = tmp_path / "bad.yaml"; p.write_text(y)
    with pytest.raises(spec.SpecError, match="LN"):
        spec.load(p, check_paths=False)

def test_check_paths_true_requires_provenance_files(tmp_path):
    spec_dir = tmp_path / "model" / "pitch_model_v2" / "spec"
    spec_dir.mkdir(parents=True)
    p = spec_dir / "lines.yaml"
    p.write_text(FIX.read_text())
    with pytest.raises(spec.SpecError, match="not found"):
        spec.load(p)
    for rel in (
        "docs/pitch-model-v2/dossiers/D1_nights.md",
        "data/processed/pitch_model_v2/receipts/D1/receipt.json",
        "docs/pitch-model-v2/dossiers/D4_adr.md",
        "data/processed/pitch_model_v2/receipts/D4/receipt.json",
        "docs/pitch-model-v2/dossiers/R1_kernel.md",
        "data/processed/pitch_model_v2/receipts/R1/receipt.json",
    ):
        full = tmp_path / rel
        full.parent.mkdir(parents=True, exist_ok=True)
        full.touch()
    s_checked = spec.load(p)
    s_unchecked = spec.load(p, check_paths=False)
    assert s_checked.order == s_unchecked.order
