from pathlib import Path
from pitch_model_v2 import tieout

FIX = Path(__file__).parent / "fixtures" / "spec_small.yaml"

def test_tieout_table(tmp_path):
    targets = tmp_path / "t.csv"
    targets.write_text("line,period,scenario,source,value,note\nD1,3Q26,base,memo_v3,146.3,x\nD1,3Q26,short,memo_v3,144.0,y\n")
    dec = tmp_path / "DECISIONS.md"
    dec.write_text("| id | line | period | scenario | value | reason | rejected | date |\n|---|---|---|---|---|---|---|---|\n| DEC-0009 | D1 | 3Q26 | short | 145.0 | cohort engine | 144.0 | 2026-09-19 |\n")
    out = tieout.write(FIX, targets, dec, tmp_path / "TIEOUT.md", check_paths=False)
    txt = out.read_text()
    assert "| D1 | 3Q26 | base | 146.3 | 146.3 | 0.0 |" in txt
    assert "DEC-0009" in txt and "UNEXPLAINED" not in txt.split("short")[1].split("\n")[0]
