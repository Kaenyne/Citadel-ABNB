import json, subprocess, textwrap, time
from pathlib import Path
import pandas as pd
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
    # diff CSVs are named by relative path with "/" -> "__", not just the basename
    assert (rdir / "diffs/data__processed__pkg__out.csv").exists()

def test_run_records_nonzero_exit(tmp_path):
    repo = _toy_repo(tmp_path)
    rec = repro.run("T2", "python3 -c 'import sys; sys.exit(3)'", ["data/processed/pkg"], root=repo, timeout=60)
    assert rec["exit_code"] == 3 and rec["changed"] == []

# --- C1: deleted tracked watched files must still be restored -------------

def test_run_restores_deleted_tracked_file(tmp_path):
    repo = _toy_repo(tmp_path)
    (repo / "del.py").write_text(textwrap.dedent("""
        from pathlib import Path
        Path('data/processed/pkg/out.csv').unlink()
    """))
    rec = repro.run("T3", "python3 del.py", ["data/processed/pkg"], root=repo, timeout=60)
    assert rec["restored"] is True
    assert (repo / "data/processed/pkg/out.csv").exists()
    assert (repo / "data/processed/pkg/out.csv").read_text().endswith("20.0\n")
    changed = {c["path"]: c for c in rec["changed"]}
    assert changed["data/processed/pkg/out.csv"]["kind"] == "deleted"
    assert changed["data/processed/pkg/out.csv"]["max_abs_diff"] is None

# --- C2: a hung command must be killed (whole process group) and still ----
# --- produce a normal receipt with exit_code 124 ---------------------------

def test_run_kills_on_timeout(tmp_path):
    repo = _toy_repo(tmp_path)
    t0 = time.time()
    rec = repro.run("T4", "python3 -c \"import time; time.sleep(30)\"",
                     ["data/processed/pkg"], root=repo, timeout=1)
    elapsed = time.time() - t0
    assert rec["exit_code"] == 124
    assert rec["restored"] is True
    assert (repo / "data/processed/pitch_model_v2/receipts/T4/receipt.json").exists()
    assert elapsed < 10, f"took {elapsed}s -- process group was not killed promptly"

# --- I1: the 200-row cap is per file (across all columns), not per column -

def test_csv_diff_caps_total_rows_at_200_across_columns(tmp_path):
    repo = _toy_repo(tmp_path)
    head_rows = "\n".join(f"{i},{i},{i}" for i in range(150))
    (repo / "data/processed/pkg/wide.csv").write_text("a,b,c\n" + head_rows + "\n")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "wide")
    (repo / "run2.py").write_text(textwrap.dedent("""
        from pathlib import Path
        rows = "\\n".join(f"{i+1},{i+1},{i+1}" for i in range(150))
        Path('data/processed/pkg/wide.csv').write_text("a,b,c\\n" + rows + "\\n")
    """))
    rec = repro.run("T5", "python3 run2.py", ["data/processed/pkg"], root=repo, timeout=60)
    changed = {c["path"]: c for c in rec["changed"]}
    assert "data/processed/pkg/wide.csv" in changed
    diffs_path = repo / "data/processed/pitch_model_v2/receipts/T5/diffs/data__processed__pkg__wide.csv"
    assert diffs_path.exists()
    diffs = pd.read_csv(diffs_path)
    assert len(diffs) == 200

# --- I2: a number<->NaN change forces max_abs_diff to +inf -----------------

def test_csv_diff_nan_change_forces_inf(tmp_path):
    repo = _toy_repo(tmp_path)
    (repo / "data/processed/pkg/nan.csv").write_text("q,v\n3Q26,20.0\n")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "nan")
    (repo / "run3.py").write_text(textwrap.dedent("""
        from pathlib import Path
        Path('data/processed/pkg/nan.csv').write_text('q,v\\n3Q26,\\n')
    """))
    rec = repro.run("T6", "python3 run3.py", ["data/processed/pkg"], root=repo, timeout=60)
    changed = {c["path"]: c for c in rec["changed"]}
    info = changed["data/processed/pkg/nan.csv"]
    assert info["max_abs_diff"] == float("inf")
    diffs_path = repo / "data/processed/pitch_model_v2/receipts/T6/diffs/data__processed__pkg__nan.csv"
    diffs = pd.read_csv(diffs_path)
    assert (diffs["diff"] == "nan_change").any()

# --- I3: quoted/non-ASCII filenames parse correctly and are restored ------

def test_run_handles_non_ascii_and_spaced_filenames(tmp_path):
    repo = _toy_repo(tmp_path)
    tricky = "data/processed/pkg/café report.csv"
    (repo / tricky).write_text("q,v\n3Q26,10.0\n")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "tricky")
    (repo / "run4.py").write_text(textwrap.dedent(f"""
        from pathlib import Path
        p = Path({tricky!r})
        p.write_text('q,v\\n3Q26,11.0\\n')
    """))
    rec = repro.run("T7", "python3 run4.py", ["data/processed/pkg"], root=repo, timeout=60)
    changed_paths = [c["path"] for c in rec["changed"]]
    assert tricky in changed_paths
    assert rec["restored"] is True
    assert (repo / tricky).read_text().endswith("10.0\n")

# --- I4: receipt.json is always written, even if the restore itself fails -

def test_run_writes_receipt_even_if_restore_fails(tmp_path, monkeypatch):
    repo = _toy_repo(tmp_path)
    real_run = subprocess.run

    def fake_run(args, *a, **kw):
        if isinstance(args, list) and args[:2] == ["git", "checkout"]:
            raise subprocess.CalledProcessError(1, args, stderr="boom")
        return real_run(args, *a, **kw)

    monkeypatch.setattr(repro.subprocess, "run", fake_run)
    rec = repro.run("T8", "python3 run.py", ["data/processed/pkg"], root=repo, timeout=60)
    assert rec["restored"] is False
    rdir = repo / "data/processed/pitch_model_v2/receipts/T8"
    assert (rdir / "receipt.json").exists()
    assert json.loads((rdir / "receipt.json").read_text())["restored"] is False
