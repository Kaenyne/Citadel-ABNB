import json
from pathlib import Path
from openpyxl import load_workbook
from pitch_model_v2 import build, qa

FIX = Path(__file__).parent / "fixtures" / "spec_small.yaml"

def _dossiers(root: Path):
    for lid, val, per in [("D1", "146.3", "3Q26"), ("D4", "176.9", "3Q26"), ("R1", "0.1724", "3Q26")]:
        d = root / "docs/pitch-model-v2/dossiers"; d.mkdir(parents=True, exist_ok=True)
        rd = root / f"data/processed/pitch_model_v2/receipts/{lid}"; rd.mkdir(parents=True, exist_ok=True)
        (rd / "receipt.json").write_text(json.dumps({"id": lid, "exit_code": 0}))
    (root / "docs/pitch-model-v2/dossiers/D1_nights.md").write_text("## 2. The number\n| scenario | period | point |\n|---|---|---|\n| base | 3Q26 | 146.3 |\n| base | 4Q26 | 133.2 |\n| short | 3Q26 | 145.0 |\n| short | 4Q26 | 131.0 |\n| base | 1Q26 | 143.1 |\n| base | 2Q26 | 134.4 |\n| short | 1Q26 | 143.1 |\n| short | 2Q26 | 134.4 |\n")
    (root / "docs/pitch-model-v2/dossiers/D4_adr.md").write_text("## 2. The number\n| scenario | period | point |\n|---|---|---|\n| base | 1Q26 | 176.0 |\n| base | 2Q26 | 179.4 |\n| base | 3Q26 | 176.9 |\n| base | 4Q26 | 171.0 |\n| short | 1Q26 | 176.0 |\n| short | 2Q26 | 179.4 |\n| short | 3Q26 | 174.6 |\n| short | 4Q26 | 169.0 |\n")
    (root / "docs/pitch-model-v2/dossiers/R1_kernel.md").write_text("## 2. The number\n| scenario | period | point |\n|---|---|---|\n| base | 3Q26 | 0.1724 |\n| base | 4Q26 | 0.1203 |\n| short | 3Q26 | 0.1724 |\n| short | 4Q26 | 0.1203 |\n")

def test_qa_passes_on_clean_build(tmp_path):
    _dossiers(tmp_path)
    out = build.build(FIX, tmp_path / "m.xlsx", check_paths=False)
    assert qa.check(out, FIX, root=tmp_path, allow_uncalculated=True) == []

def test_qa_flags_value_outside_tolerance(tmp_path):
    _dossiers(tmp_path)
    (tmp_path / "docs/pitch-model-v2/dossiers/D1_nights.md").write_text("## 2. The number\n| scenario | period | point |\n|---|---|---|\n| base | 3Q26 | 140.0 |\n")
    out = build.build(FIX, tmp_path / "m.xlsx", check_paths=False)
    msgs = qa.check(out, FIX, root=tmp_path, allow_uncalculated=True)
    assert any("D1" in m and "3Q26" in m for m in msgs)

def test_qa_flags_value_not_stated_in_dossier(tmp_path):
    _dossiers(tmp_path)
    (tmp_path / "docs/pitch-model-v2/dossiers/D1_nights.md").write_text("## 2. The number\n| scenario | period | point |\n|---|---|---|\n| base | 3Q26 | 146.3 |\n| base | 4Q26 | 133.2 |\n| short | 3Q26 | 145.0 |\n| base | 1Q26 | 143.1 |\n| base | 2Q26 | 134.4 |\n| short | 1Q26 | 143.1 |\n| short | 2Q26 | 134.4 |\n")
    out = build.build(FIX, tmp_path / "m.xlsx", check_paths=False)
    msgs = qa.check(out, FIX, root=tmp_path, allow_uncalculated=True)
    assert any("not stated in dossier" in m for m in msgs)

def test_qa_flags_error_cells(tmp_path):
    _dossiers(tmp_path)
    out = build.build(FIX, tmp_path / "m.xlsx", check_paths=False)
    wb = load_workbook(out); wb["Drivers"]["Z2"] = "#REF!"; wb.save(out)
    assert any("#REF!" in m for m in qa.check(out, FIX, root=tmp_path, allow_uncalculated=True))

def test_qa_flags_unresolved_name(tmp_path):
    _dossiers(tmp_path)
    out = build.build(FIX, tmp_path / "m.xlsx", check_paths=False)
    wb = load_workbook(out); wb["Drivers"]["Z3"] = "=NOPE_3Q26*2"; wb.save(out)
    assert any("NOPE_3Q26" in m for m in qa.check(out, FIX, root=tmp_path, allow_uncalculated=True))
