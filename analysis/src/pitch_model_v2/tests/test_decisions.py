from pitch_model_v2 import decisions

def test_parse_rows(tmp_path):
    p = tmp_path / "DECISIONS.md"
    p.write_text("# x\n\n| id | line | period | scenario | value | reason | rejected | date |\n|---|---|---|---|---|---|---|---|\n"
                 "| DEC-0001 | D1 | 3Q26 | base | 146.3 | reviews index point | 149.0 (MODL mean) | 2026-09-19 |\n")
    rows = decisions.load(p)
    assert rows[0].id == "DEC-0001" and rows[0].line == "D1" and rows[0].value == 146.3
