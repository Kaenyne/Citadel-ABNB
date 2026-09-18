import json, subprocess, textwrap
from pathlib import Path
from pitch_model_v2 import repro

def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True).stdout

def _toy_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"; (repo / "data" / "processed" / "pkg").mkdir(parents=True)
    (repo / "data/processed/pkg/out.csv").write_text("q,v\n3Q26,10.0\n4Q26,20.0\n")
    (repo / "run.py").write_text(textwrap.dedent("""
        from pathlib import Path
        Path('data/processed/pkg/out.csv').write_text('q,v\\n3Q26,10.0\\n4Q26,20.5\\n')
        Path('data/processed/pkg/new.csv').write_text('a\\n1\\n')
        print('done')
    """))
    _git(repo, "init", "-q"); _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "init")
    return repo

def test_run_diffs_and_restores(tmp_path):
    repo = _toy_repo(tmp_path)
    rec = repro.run("T1", "python3 run.py", ["data/processed/pkg"], root=repo, timeout=60)
    assert rec["exit_code"] == 0
    assert rec["restored"] is True
    changed = {c["path"]: c for c in rec["changed"]}
    assert "data/processed/pkg/out.csv" in changed
    assert abs(changed["data/processed/pkg/out.csv"]["max_abs_diff"] - 0.5) < 1e-9
    assert rec["new_files"] == ["data/processed/pkg/new.csv"]
    # tree restored
    assert (repo / "data/processed/pkg/out.csv").read_text().endswith("20.0\n")
    assert not (repo / "data/processed/pkg/new.csv").exists()
    # receipt written
    rdir = repo / "data/processed/pitch_model_v2/receipts/T1"
    assert json.loads((rdir / "receipt.json").read_text())["id"] == "T1"
    assert (rdir / "stdout.txt").read_text().strip() == "done"
    assert (rdir / "diffs/out.csv").exists()

def test_run_records_nonzero_exit(tmp_path):
    repo = _toy_repo(tmp_path)
    rec = repro.run("T2", "python3 -c 'import sys; sys.exit(3)'", ["data/processed/pkg"], root=repo, timeout=60)
    assert rec["exit_code"] == 3 and rec["changed"] == []
