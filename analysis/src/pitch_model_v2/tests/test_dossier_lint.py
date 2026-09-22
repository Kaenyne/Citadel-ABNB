import json
import re
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

def test_judge_questions_scoped_to_section9(tmp_path):
    # Two decoy "Q:" occurrences in §4 prose must not count toward the three
    # judge questions required in §9; cutting §9 to one real numbered
    # question must still trigger the message.
    _receipt(tmp_path)
    text = FIX.read_text()
    text = text.replace(
        "## 4. Governing sources\n",
        "## 4. Governing sources\nQ: is this note still governing? Q: has it been superseded?\n",
        1,
    )
    text = re.sub(
        r"(## 9\. Judge Q&A\n)(.*?)(\n## 10\. Grade)",
        lambda mo: mo.group(1) + mo.group(2).splitlines()[0] + mo.group(3),
        text,
        flags=re.S,
    )
    p = tmp_path / "d.md"; p.write_text(text)
    assert any("§9 needs three judge questions" in m for m in dossier_lint.lint(p, root=tmp_path))

def test_grade_search_scoped_to_section10(tmp_path):
    # A stray "Grade: A" line planted in §8 prose must not be picked up as
    # the dossier's grade; the real grade line lives in §10.
    _receipt(tmp_path)
    text = FIX.read_text().replace(
        "## 8. Open choices\n",
        "## 8. Open choices\nGrade: A\n",
        1,
    )
    p = tmp_path / "d.md"; p.write_text(text)
    assert dossier_lint.lint(p, root=tmp_path) == []

def test_receipt_and_match_scoped_to_section5(tmp_path):
    # A receipt path mentioned in §3's derivation chain must not satisfy
    # the §5 receipt requirement.
    _receipt(tmp_path)
    text = FIX.read_text()
    text = text.replace(
        "- Receipt: `data/processed/pitch_model_v2/receipts/T1/receipt.json`\n",
        "",
        1,
    )
    text = text.replace(
        "## 3. Derivation chain\n",
        "## 3. Derivation chain\nSee also `data/processed/pitch_model_v2/receipts/T1/receipt.json`.\n",
        1,
    )
    p = tmp_path / "d.md"; p.write_text(text)
    msgs = dossier_lint.lint(p, root=tmp_path)
    assert any("needs a receipt path in §5" in m for m in msgs)
