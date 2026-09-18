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
    bad = FIX.read_text().replace('periods: [3Q26, 4Q26]\n    expr: "LAM', 'periods: [1Q26]\n    expr: "LAM')
    p = tmp_path / "bad.yaml"; p.write_text(bad)
    with pytest.raises(spec.SpecError, match="R2"):
        spec.load(p, check_paths=False)
