import json
from pathlib import Path
from pitch_model_v2 import dossier_lint

FIX = Path(__file__).parent / "fixtures" / "dossier_ok.md"

def _receipt(root: Path, exit_code=0):
    d = root / "data/processed/pitch_model_v2/receipts/T1"; d.mkdir(parents=True)
    (d / "receipt.json").write_text(json.dumps({"id": "T1", "exit_code": exit_code, "changed": []}))

def test_clean_dossier(tmp_path):
    _receipt(tmp_path)
    assert dossier_lint.lint(FIX, root=tmp_path) == []

def test_missing_heading(tmp_path):
    _receipt(tmp_path)
    p = tmp_path / "d.md"; p.write_text(FIX.read_text().replace("## 6. Test record", "## 6. Tests"))
    assert any("6. Test record" in m for m in dossier_lint.lint(p, root=tmp_path))

def test_grade_a_requires_match_and_exit_zero(tmp_path):
    _receipt(tmp_path, exit_code=1)
    p = tmp_path / "d.md"; p.write_text(FIX.read_text().replace("Grade: B", "Grade: A"))
    msgs = dossier_lint.lint(p, root=tmp_path)
    assert any("exit" in m for m in msgs)

def test_grade_c_allowed_without_receipt(tmp_path):
    p = tmp_path / "d.md"; p.write_text(FIX.read_text().replace("Grade: B", "Grade: C").replace("**Match: yes**", "**Match: no**"))
    assert dossier_lint.lint(p, root=tmp_path) == []
