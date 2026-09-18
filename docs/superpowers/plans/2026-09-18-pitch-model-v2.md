# Pitch Model v2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `model/pitch_model_v2/ABNB_pitch_model_v2.xlsx`, the 2 Oct submission model, in which every input is reproduced from repo code by a digger subagent, carries its evidence, and every other cell is a live formula, with the long/short call decided last as a derived output.

**Architecture:** Two tracks run in parallel. Track A is a small Python toolchain: a YAML spec of lines, a reproduction wrapper that lets diggers re-run package scripts without dirtying the tree, a dossier linter, a workbook builder that emits defined names and real formulas, an Excel recalculation step, a QA gate, and a tie-out generator. Track B is the dossier programme: thirty lines dug by Opus and Sonnet subagents in four waves, each dossier reviewed here with Theo, each decision logged, each decided line entered into the spec. The workbook is regenerated after every wave.

**Tech Stack:** Python 3.13 (`python3`), pandas 3.0 with a pandas 2.3 fallback venv, openpyxl 3.1.5, PyYAML, pytest, `osascript` driving the installed Microsoft Excel for recalculation, git worktrees, the Agent tool for diggers.

**Spec:** `docs/superpowers/specs/2026-09-18-pitch-model-v2-design.md`

## Global Constraints

- Workspace is `~/Citadel-ABNB` on branch `theo/pitch-model-v2` (main at `88a5dfc`). Never work in the OneDrive checkout.
- Copy, never overwrite: all new code under `analysis/src/pitch_model_v2/`, spec under `model/pitch_model_v2/spec/`, workbook under `model/pitch_model_v2/`, dossiers under `docs/pitch-model-v2/dossiers/`, receipts under `data/processed/pitch_model_v2/receipts/<id>/`. Frozen: `analysis/src/forecast_methods/harness/`, `.../L0/`, `data/processed/overnight/20_frozen_q3_2026.csv`.
- A value enters the spec only with grade A or B from a dossier whose receipt shows exit code 0 and a numeric match within the dossier's stated tolerance.
- Point-in-time or it does not count: W1 from 1Q23 (n 14), W2 from 1Q24 (n 10). Consensus values carry vendor and timestamp.
- Nothing from the kill lists (`docs/revenue-forecast-strategy/AGENT_BRIEF.md` §6, `docs/margin-build/SYNTHESIS.md` §9) is quoted as ours.
- Diggers never run `harness/score.py` or the margin scorer; never run two margin_build packages concurrently; never scrape airbnb.com; never type credentials; write only to their own dossier file and receipt folder.
- Never commit to `main`; never commit licensed raw exports; the workbook binary is committed.
- Run every Python command from the clone root with `python3`; if a package script fails on a pandas 3 API, use `.venv-pd2/bin/python` (pandas 2.3.3).
- Commit after every task with the attribution line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

---

## File structure

```
analysis/src/pitch_model_v2/
  __init__.py
  spec.py            # load + validate lines.yaml; expression parser; topological order
  repro.py           # reproduction wrapper: snapshot, run, diff vs HEAD, restore, receipt.json
  dossier_lint.py    # checks a dossier has the ten sections, a grade, and a matching receipt
  decisions.py       # parse docs/pitch-model-v2/DECISIONS.md into rows
  build.py           # spec -> workbook (tabs, defined names, formulas, Scenario Data)
  recalc.py          # osascript: open in Excel, full calculate, save
  qa.py              # gate: formula errors, provenance, name resolution, receipt tie, licensed data
  tieout.py          # spec vs memo v3 / L4 numbers -> docs/pitch-model-v2/TIEOUT.md
  tests/
    test_spec.py test_repro.py test_dossier_lint.py test_decisions.py
    test_build.py test_qa.py test_tieout.py
    fixtures/ (small spec, dossier, receipt, tieout targets)
model/pitch_model_v2/spec/lines.yaml
model/pitch_model_v2/spec/tieout_targets.csv
model/pitch_model_v2/ABNB_pitch_model_v2.xlsx
docs/pitch-model-v2/
  DOSSIER_TEMPLATE.md  DIGGER_BRIEF_TEMPLATE.md  LINES.md  DECISIONS.md  TIEOUT.md
  dossiers/<id>_<slug>.md
data/processed/pitch_model_v2/receipts/<id>/receipt.json, stdout.txt, stderr.txt, diffs/
```

Interfaces that every task relies on:

- `spec.load(path) -> Spec` with `Spec.meta` (dict: `price_date`, `spot`, `scenarios: list[str]`, `periods: list[str]` in chronological order), `Spec.lines: dict[str, Line]`, `Spec.order: list[str]` (topological). `Line` fields: `id`, `label`, `unit`, `block`, `kind` (`"input"|"formula"`), `periods: list[str]`, `values: dict[scenario, dict[period, float]]` (inputs), `expr: str` (formulas), `provenance: dict` (inputs: `dossier`, `receipt`, `grade`, `decision`, `tolerance`).
- `spec.parse_expr(expr) -> list[Token]` and `spec.to_excel(expr, period, periods) -> str` producing a formula in defined names, e.g. `to_excel("LAM * (2/3*D6[-1] + 1/3*D6[-2])", "3Q26", [...]) == "LAM_3Q26*(2/3*D6_2Q26+1/3*D6_1Q26)"`.
- `repro.run(id, cmd, watch, timeout, restore=True) -> Receipt` writing `receipt.json` with keys `id, commit, cmd, exit_code, wall_s, changed[], new_files[], restored`.
- `dossier_lint.lint(path) -> list[str]` (empty list means clean).
- `decisions.load(path) -> list[Decision]` with fields `id, line, period, scenario, value, reason, rejected, date`.
- `build.build(spec_path, out_path, recalc=True) -> Path`; `qa.check(workbook_path, spec_path) -> list[str]`; `tieout.write(spec_path, targets_csv, decisions_path, out_md) -> Path`.

Defined-name convention: `<ID>_<PERIOD>` (e.g. `D1_3Q26`, `R5_FY26`). Scenario selector cell: `Scenario` (defined name on `Cover!B4`).

---
# Track A: toolchain

### Task A1: Environment: pandas 2.3 fallback venv and the untracked-work worktree

**Files:**
- Create: `.venv-pd2/` (gitignored by the existing `venv/`-style rule? No: add a line to `.gitignore`)
- Modify: `.gitignore` (append `.venv-pd2/`)
- Create: branch `theo/local-untracked-2026-09-15` with the staged OneDrive files; worktree `~/Citadel-ABNB-untracked/`

**Interfaces:**
- Produces: `.venv-pd2/bin/python` (pandas 2.3.3, pyarrow, scipy, statsmodels, openpyxl) for scripts that break on pandas 3; `~/Citadel-ABNB-untracked/` readable path for diggers.

- [ ] **Step 1: Create the fallback venv**

```bash
cd ~/Citadel-ABNB
python3 -m venv .venv-pd2
.venv-pd2/bin/python -m pip install --quiet "pandas==2.3.3" "numpy<3" pyarrow scipy statsmodels openpyxl pyyaml pytest duckdb
.venv-pd2/bin/python -c "import pandas; print(pandas.__version__)"
```
Expected: `2.3.3`

- [ ] **Step 2: Ignore it**

```bash
printf '\n# pandas-2.3 fallback interpreter for reproductions (pitch_model_v2)\n.venv-pd2/\n' >> .gitignore
git add .gitignore && git commit -q -m "pitch_model_v2: ignore the pandas-2.3 fallback venv

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

- [ ] **Step 3: Confirm the OneDrive staging copy finished**

Run: `S=/private/tmp/claude-501/-Users-theomachado-Library-CloudStorage-OneDrive-UniversityofFlorida-Young--Willem-K--s-files---Citadel---ABNB/517269ac-8ba5-4875-8aad-11a7b566283e/scratchpad; echo "$(find $S/untracked_staging -type f | wc -l) of $(wc -l < $S/untracked_list.txt)"; cat $S/copy_failed.txt | sort -u | head`
Expected: `738 of 738` and an empty failed list. If files are missing, re-run the copy loop for the missing paths only (the loop skips files already staged) before continuing.

- [ ] **Step 4: Commit the staged files on their own branch and expose them as a worktree**

```bash
cd ~/Citadel-ABNB
git checkout -b theo/local-untracked-2026-09-15 main
rsync -a "$S/untracked_staging/" ./
git add -A analysis/src/forecast_methods data/processed/forecast_methods docs/revenue-forecast-strategy/05_backtests START_HERE_2026-09-15.md
git commit -q -m "Untracked OneDrive work as of 15 Sep 2026: 10 forecast_methods packages, 24 notes, START_HERE (copied 18 Sep, no edits)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
git checkout theo/pitch-model-v2
git worktree add ~/Citadel-ABNB-untracked theo/local-untracked-2026-09-15
ls ~/Citadel-ABNB-untracked/analysis/src/forecast_methods | grep -c _v1
```
Expected: the worktree lists the ten `_v1` packages; `git status` on `theo/pitch-model-v2` is clean.

- [ ] **Step 5: Smoke-test the frozen harness on this machine**

Run: `cd ~/Citadel-ABNB && python3 -m pytest analysis/src/forecast_methods/harness/tests -q 2>&1 | tail -3`
Expected: all tests pass (the repo reports 27). If pandas 3 breaks them, re-run with `.venv-pd2/bin/python -m pytest ...` and record which interpreter passed in `docs/pitch-model-v2/LINES.md` under "Environment".

---

### Task A2: Spec loader and expression parser

**Files:**
- Create: `analysis/src/pitch_model_v2/__init__.py` (empty)
- Create: `analysis/src/pitch_model_v2/spec.py`
- Create: `analysis/src/pitch_model_v2/tests/__init__.py` (empty), `analysis/src/pitch_model_v2/tests/test_spec.py`, `analysis/src/pitch_model_v2/tests/fixtures/spec_small.yaml`

**Interfaces:**
- Produces: `load(path) -> Spec`, `parse_expr(expr) -> list[Token]`, `to_excel(expr, period, periods) -> str`, `SpecError`.

- [ ] **Step 1: Write the fixture**

`analysis/src/pitch_model_v2/tests/fixtures/spec_small.yaml`:
```yaml
meta:
  price_date: "2026-09-16"
  spot: 167.51
  scenarios: [base, short]
  periods: [1Q26, 2Q26, 3Q26, 4Q26, FY26]
lines:
  - id: D1
    label: Nights (m)
    unit: m
    block: drivers
    kind: input
    periods: [1Q26, 2Q26, 3Q26, 4Q26]
    values:
      base:  {1Q26: 143.1, 2Q26: 134.4, 3Q26: 146.3, 4Q26: 133.2}
      short: {1Q26: 143.1, 2Q26: 134.4, 3Q26: 145.0, 4Q26: 131.0}
    provenance: {dossier: docs/pitch-model-v2/dossiers/D1_nights.md, receipt: data/processed/pitch_model_v2/receipts/D1/receipt.json, grade: A, decision: DEC-0001, tolerance: 0.1}
  - id: D4T
    label: ADR ($)
    unit: usd
    block: drivers
    kind: input
    periods: [1Q26, 2Q26, 3Q26, 4Q26]
    values:
      base:  {1Q26: 176.0, 2Q26: 179.4, 3Q26: 176.9, 4Q26: 171.0}
      short: {1Q26: 176.0, 2Q26: 179.4, 3Q26: 174.6, 4Q26: 169.0}
    provenance: {dossier: docs/pitch-model-v2/dossiers/D4_adr.md, receipt: data/processed/pitch_model_v2/receipts/D4/receipt.json, grade: B, decision: DEC-0002, tolerance: 0.5}
  - id: D6
    label: GBV ($M)
    unit: musd
    block: drivers
    kind: formula
    periods: [1Q26, 2Q26, 3Q26, 4Q26]
    expr: "D1 * D4T"
  - id: LAM
    label: Lambda by season
    unit: pct
    block: revenue
    kind: input
    periods: [3Q26, 4Q26]
    values:
      base:  {3Q26: 0.1724, 4Q26: 0.1203}
      short: {3Q26: 0.1724, 4Q26: 0.1203}
    provenance: {dossier: docs/pitch-model-v2/dossiers/R1_kernel.md, receipt: data/processed/pitch_model_v2/receipts/R1/receipt.json, grade: A, decision: DEC-0003, tolerance: 0.0001}
  - id: R2
    label: Revenue, kernel ($M)
    unit: musd
    block: revenue
    kind: formula
    periods: [3Q26, 4Q26]
    expr: "LAM * (2/3*D6[-1] + 1/3*D6[-2])"
  - id: R5FY
    label: FY26 revenue ($M)
    unit: musd
    block: revenue
    kind: formula
    periods: [FY26]
    expr: "R2@3Q26 + R2@4Q26"
```

- [ ] **Step 2: Write the failing tests**

`analysis/src/pitch_model_v2/tests/test_spec.py`:
```python
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
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/tests/test_spec.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'pitch_model_v2'`

- [ ] **Step 4: Implement `spec.py`**

```python
"""Load and validate model/pitch_model_v2/spec/lines.yaml.

A line is either an input (values per scenario and period, provenance with grade A/B)
or a formula (an expression in other line ids). Expressions: ids, ids with a relative
period shift `ID[-n]`, ids with an absolute period `ID@PERIOD`, numbers, + - * / and
parentheses. Nothing else, so every cell in the workbook is traceable by name.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
import yaml

ID_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
TOKEN_RE = re.compile(r"\s*(?:(?P<num>\d+\.?\d*)|(?P<id>[A-Z][A-Z0-9_]*)(?:\[(?P<shift>-\d+)\]|@(?P<abs>[0-9A-Z]+))?|(?P<op>[-+*/()]))")

class SpecError(ValueError):
    pass

@dataclass
class Token:
    kind: str            # "num" | "id" | "op"
    text: str
    shift: int = 0
    abs_period: str | None = None

@dataclass
class Line:
    id: str
    label: str
    unit: str
    block: str
    kind: str
    periods: list[str]
    values: dict[str, dict[str, float]] = field(default_factory=dict)
    expr: str = ""
    provenance: dict = field(default_factory=dict)

@dataclass
class Spec:
    meta: dict
    lines: dict[str, Line]
    order: list[str]

def parse_expr(expr: str) -> list[Token]:
    pos, out = 0, []
    while pos < len(expr):
        m = TOKEN_RE.match(expr, pos)
        if not m or m.end() == pos:
            raise SpecError(f"cannot parse expression at {expr[pos:]!r}")
        pos = m.end()
        if m.group("num"):
            out.append(Token("num", m.group("num")))
        elif m.group("id"):
            out.append(Token("id", m.group("id"), int(m.group("shift") or 0), m.group("abs")))
        else:
            out.append(Token("op", m.group("op")))
    return out

def ref_period(tok: Token, period: str, periods: list[str]) -> str:
    if tok.abs_period:
        if tok.abs_period not in periods:
            raise SpecError(f"unknown period {tok.abs_period} in reference {tok.text}@{tok.abs_period}")
        return tok.abs_period
    i = periods.index(period) + tok.shift
    if i < 0 or i >= len(periods):
        raise SpecError(f"reference {tok.text}[{tok.shift}] from {period} falls outside the period list")
    return periods[i]

def to_excel(expr: str, period: str, periods: list[str]) -> str:
    parts = []
    for t in parse_expr(expr):
        if t.kind == "id":
            parts.append(f"{t.text}_{ref_period(t, period, periods)}")
        else:
            parts.append(t.text)
    return "".join(parts)

def _line(d: dict) -> Line:
    for k in ("id", "label", "unit", "block", "kind", "periods"):
        if k not in d:
            raise SpecError(f"line {d.get('id','?')}: missing {k}")
    if not ID_RE.match(d["id"]):
        raise SpecError(f"bad id {d['id']!r}")
    if d["kind"] not in ("input", "formula"):
        raise SpecError(f"{d['id']}: kind must be input or formula")
    return Line(d["id"], d["label"], d["unit"], d["block"], d["kind"], list(d["periods"]),
                d.get("values", {}), d.get("expr", ""), d.get("provenance", {}))

def load(path: str | Path, check_paths: bool = True) -> Spec:
    root = Path(path).resolve().parents[3]   # <repo>/model/pitch_model_v2/spec/lines.yaml
    raw = yaml.safe_load(Path(path).read_text())
    meta = raw["meta"]; periods = list(meta["periods"]); scenarios = list(meta["scenarios"])
    lines: dict[str, Line] = {}
    for d in raw["lines"]:
        ln = _line(d)
        if ln.id in lines:
            raise SpecError(f"duplicate id {ln.id}")
        for p in ln.periods:
            if p not in periods:
                raise SpecError(f"{ln.id}: period {p} not in meta.periods")
        if ln.kind == "input":
            if ln.expr:
                raise SpecError(f"{ln.id}: input may not carry expr")
            prov = ln.provenance
            if prov.get("grade") not in ("A", "B"):
                raise SpecError(f"{ln.id}: input needs grade A or B, got {prov.get('grade')!r}")
            for k in ("dossier", "receipt", "decision", "tolerance"):
                if k not in prov:
                    raise SpecError(f"{ln.id}: provenance missing {k}")
            if check_paths:
                for k in ("dossier", "receipt"):
                    if not (root / prov[k]).exists():
                        raise SpecError(f"{ln.id}: {k} not found at {prov[k]}")
            for sc in scenarios:
                for p in ln.periods:
                    if p not in ln.values.get(sc, {}):
                        raise SpecError(f"{ln.id}: missing value for scenario {sc} period {p}")
        else:
            if not ln.expr:
                raise SpecError(f"{ln.id}: formula needs expr")
        lines[ln.id] = ln
    # resolve references and order
    deps: dict[str, set[str]] = {}
    for ln in lines.values():
        deps[ln.id] = set()
        if ln.kind == "formula":
            for p in ln.periods:
                for t in parse_expr(ln.expr):
                    if t.kind != "id":
                        continue
                    if t.text not in lines:
                        raise SpecError(f"{ln.id}: references unknown id {t.text}")
                    try:
                        rp = ref_period(t, p, periods)
                    except SpecError as e:
                        raise SpecError(f"{ln.id}: {e}") from e
                    if rp not in lines[t.text].periods:
                        raise SpecError(f"{ln.id}: {t.text} has no period {rp}")
                    deps[ln.id].add(t.text)
    order, seen, temp = [], set(), set()
    def visit(n: str):
        if n in seen:
            return
        if n in temp:
            raise SpecError(f"cycle through {n}")
        temp.add(n)
        for m in sorted(deps[n]):
            visit(m)
        temp.discard(n); seen.add(n); order.append(n)
    for n in lines:
        visit(n)
    return Spec(meta, lines, order)
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/tests/test_spec.py -q`
Expected: `7 passed`

- [ ] **Step 6: Commit**

```bash
git add analysis/src/pitch_model_v2
git commit -q -m "pitch_model_v2: spec loader, expression parser, topological order

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---
### Task A3: Reproduction wrapper `repro.py`

Diggers must re-run package scripts, but those scripts overwrite tracked outputs under `data/processed/` and some call scorers. The wrapper snapshots the watched paths, runs the command, diffs every changed CSV against `HEAD`, writes a receipt, and restores the tree. Every receipt in this programme comes from this wrapper.

**Files:**
- Create: `analysis/src/pitch_model_v2/repro.py`
- Create: `analysis/src/pitch_model_v2/tests/test_repro.py`

**Interfaces:**
- Produces: `run(id, cmd, watch, timeout=1800, restore=True, root=None) -> dict` (the receipt), CLI `python3 analysis/src/pitch_model_v2/repro.py --id D1 --watch <path> [--watch <path>] --cmd "<shell command>" [--timeout 1800] [--no-restore]`.
- Receipt JSON keys: `id, commit, cmd, cwd, started, exit_code, wall_s, watch, changed: [{path, kind, max_abs_diff, rows_head, rows_new, cols_added, cols_removed}], new_files: [path], restored: bool, interpreter`.
- Receipt folder: `data/processed/pitch_model_v2/receipts/<id>/` with `receipt.json`, `stdout.txt`, `stderr.txt`, `diffs/<basename>.csv` (row-level numeric diffs for changed CSVs, at most 200 rows each).

- [ ] **Step 1: Write the failing test**

`analysis/src/pitch_model_v2/tests/test_repro.py`:
```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/tests/test_repro.py -q`
Expected: FAIL with `cannot import name 'repro'` or `AttributeError`

- [ ] **Step 3: Implement `repro.py`**

```python
"""Run a reproduction command without dirtying the tree, and write a receipt.

Usage:
  python3 analysis/src/pitch_model_v2/repro.py --id D1 \
      --watch data/processed/forecast_methods/kernel_lambda \
      --cmd "python3 analysis/src/forecast_methods/kernel_lambda/run.py"
"""
from __future__ import annotations
import argparse, io, json, os, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

RECEIPTS = Path("data/processed/pitch_model_v2/receipts")

def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True).stdout

def _tracked(root: Path, watch: list[str]) -> set[str]:
    out = _git(root, "ls-files", "--", *watch)
    return set(l for l in out.splitlines() if l)

def _all_files(root: Path, watch: list[str]) -> set[str]:
    found = set()
    for w in watch:
        p = root / w
        if p.is_file():
            found.add(w)
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file():
                    found.add(str(f.relative_to(root)))
    return found

def _csv_diff(root: Path, path: str) -> tuple[dict, pd.DataFrame | None]:
    head_txt = _git(root, "show", f"HEAD:{path}")
    try:
        a = pd.read_csv(io.StringIO(head_txt)); b = pd.read_csv(root / path)
    except Exception as e:  # not a parseable CSV
        return {"kind": "text", "max_abs_diff": None, "rows_head": None, "rows_new": None,
                "cols_added": [], "cols_removed": [], "note": f"not parsed: {e}"}, None
    num = [c for c in a.columns if c in b.columns and pd.api.types.is_numeric_dtype(a[c]) and pd.api.types.is_numeric_dtype(b[c])]
    n = min(len(a), len(b))
    mad = 0.0; rows = []
    for c in num:
        d = (b[c].iloc[:n].astype(float).to_numpy() - a[c].iloc[:n].astype(float).to_numpy())
        d = pd.Series(d).abs().fillna(0.0)
        if len(d):
            mad = max(mad, float(d.max()))
            for i in d[d > 0].index[:200]:
                rows.append({"row": int(i), "col": c, "head": float(a[c].iloc[i]), "new": float(b[c].iloc[i]), "diff": float(d[i])})
    info = {"kind": "csv", "max_abs_diff": mad, "rows_head": int(len(a)), "rows_new": int(len(b)),
            "cols_added": [c for c in b.columns if c not in a.columns],
            "cols_removed": [c for c in a.columns if c not in b.columns]}
    return info, (pd.DataFrame(rows) if rows else None)

def run(id: str, cmd: str, watch: list[str], timeout: int = 1800, restore: bool = True, root: str | Path | None = None) -> dict:
    root = Path(root or Path.cwd()).resolve()
    rdir = root / RECEIPTS / id; (rdir / "diffs").mkdir(parents=True, exist_ok=True)
    tracked = _tracked(root, watch)
    before = _all_files(root, watch)
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    t0 = time.time()
    proc = subprocess.run(cmd, shell=True, cwd=root, capture_output=True, text=True, timeout=timeout)
    wall = round(time.time() - t0, 1)
    (rdir / "stdout.txt").write_text(proc.stdout); (rdir / "stderr.txt").write_text(proc.stderr)
    after = _all_files(root, watch)
    modified = [l for l in _git(root, "status", "--porcelain", "--", *watch).splitlines() if l[:2].strip() in ("M", "MM", "AM")]
    changed_paths = sorted(l[3:] for l in modified if l[3:] in tracked)
    changed = []
    for p in changed_paths:
        info, rows = _csv_diff(root, p) if p.endswith(".csv") else ({"kind": "binary_or_text", "max_abs_diff": None, "rows_head": None, "rows_new": None, "cols_added": [], "cols_removed": []}, None)
        info["path"] = p; changed.append(info)
        if rows is not None:
            rows.to_csv(rdir / "diffs" / Path(p).name, index=False)
    new_files = sorted(after - before)
    restored = False
    if restore:
        if changed_paths:
            subprocess.run(["git", "checkout", "--", *changed_paths], cwd=root, check=True)
        for nf in new_files:
            (root / nf).unlink(missing_ok=True)
        restored = True
    rec = {"id": id, "commit": _git(root, "rev-parse", "HEAD").strip(), "cmd": cmd, "cwd": str(root), "started": started,
           "exit_code": proc.returncode, "wall_s": wall, "watch": watch, "changed": changed, "new_files": new_files,
           "restored": restored, "interpreter": sys.executable}
    (rdir / "receipt.json").write_text(json.dumps(rec, indent=2))
    return rec

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True); ap.add_argument("--cmd", required=True)
    ap.add_argument("--watch", action="append", required=True); ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--no-restore", action="store_true")
    a = ap.parse_args(argv)
    rec = run(a.id, a.cmd, a.watch, a.timeout, restore=not a.no_restore)
    print(json.dumps({k: rec[k] for k in ("id", "exit_code", "wall_s", "restored")}))
    print("changed:", [(c["path"], c.get("max_abs_diff")) for c in rec["changed"]])
    print("new_files:", rec["new_files"])
    return 0 if rec["exit_code"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/tests/test_repro.py -q`
Expected: `2 passed`

- [ ] **Step 5: Prove it on a real package, read-only**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id SMOKE --watch data/processed/forecast_methods/guidance_policy --cmd "python3 analysis/src/forecast_methods/guidance_policy/run.py" --timeout 900; git status --short | head -5`
Expected: exit 0, a `changed:` list whose `max_abs_diff` values are all 0 or tiny (< 1e-6) if the package reproduces on this machine, and an empty `git status`. If the script fails under pandas 3, re-run with `--cmd ".venv-pd2/bin/python analysis/src/forecast_methods/guidance_policy/run.py"` and record which interpreter worked in `docs/pitch-model-v2/LINES.md`. Delete `data/processed/pitch_model_v2/receipts/SMOKE/` afterwards.

- [ ] **Step 6: Commit**

```bash
git add analysis/src/pitch_model_v2
git commit -q -m "pitch_model_v2: reproduction wrapper with receipts and tree restore

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task A4: Dossier template, digger brief template, decision log, and the linter

**Files:**
- Create: `docs/pitch-model-v2/DOSSIER_TEMPLATE.md`
- Create: `docs/pitch-model-v2/DIGGER_BRIEF_TEMPLATE.md`
- Create: `docs/pitch-model-v2/DECISIONS.md` (header only)
- Create: `analysis/src/pitch_model_v2/dossier_lint.py`, `analysis/src/pitch_model_v2/decisions.py`
- Create: `analysis/src/pitch_model_v2/tests/test_dossier_lint.py`, `analysis/src/pitch_model_v2/tests/test_decisions.py`, `analysis/src/pitch_model_v2/tests/fixtures/dossier_ok.md`

**Interfaces:**
- Produces: `dossier_lint.lint(path, root) -> list[str]`; `decisions.load(path) -> list[Decision]` (`id, line, period, scenario, value, reason, rejected, date`).

- [ ] **Step 1: Write the dossier template**

`docs/pitch-model-v2/DOSSIER_TEMPLATE.md` (the ten headings are fixed; the linter checks them in this order):
```markdown
# <ID> — <line label>

## 1. Header
- Line: <ID> · Judge's question: "<one sentence>"
- Digger: <opus|sonnet> · Date: <YYYY-MM-DD> · Commit: <hash>

## 2. The number
| scenario | period | point | low | high | unit | vintage |
|---|---|---|---|---|---|---|
| base | 3Q26 | | | | | |

## 3. Derivation chain
1. <raw KPI or filing path> →
2. <processed CSV path> →
3. <package script path> →
4. <output file path, column, row>

## 4. Governing sources
| date | note or package | claim | status (governs / superseded by …) |
|---|---|---|---|

## 5. Reproduction receipt
- Receipt: `data/processed/pitch_model_v2/receipts/<ID>/receipt.json`
- Command: `…` · Exit: <n> · Wall: <s> · Interpreter: <python3 | .venv-pd2>
- Output: `<path>` cell `<column, row>` = <value> · Committed value: <value> · Tolerance: <±x> · **Match: yes|no**
- If no: why, and what was reproducible instead.

## 6. Test record
| window | n | metric | this line | naive | guide+cushion | Street | pre-registered pass line | pass/fail |
|---|---|---|---|---|---|---|---|---|
Strongest known failure: <one sentence>.

## 7. Kill list and consistency
- Kill-list check: <none | list>
- Conflicts: <with line X / with memo v3 §… / none>

## 8. Open choices
1. <choice> — options: (a) … (b) … — recommendation: … — why: …

## 9. Judge Q&A
1. Q: … A: …
2. Q: … A: …
3. Q: … A: …

## 10. Grade
Grade: <A|B|C> — <one sentence justification>
```

- [ ] **Step 2: Write the digger brief template**

`docs/pitch-model-v2/DIGGER_BRIEF_TEMPLATE.md`:
```markdown
You are a digger on the ABNB pitch model v2. Your job is one line of the model: **{ID} — {LABEL}**.
Judge's question: "{JUDGE_QUESTION}"

Workspace: `~/Citadel-ABNB` (branch `theo/pitch-model-v2`, commit {COMMIT}). Run every command from that root with `python3`.
If a script fails on a pandas 3 API, use `.venv-pd2/bin/python`. Untracked local work from 15 Sep is readable at `~/Citadel-ABNB-untracked/`.

Read first, in this order: `CLAUDE.md`, `docs/revenue-forecast-strategy/AGENT_BRIEF.md` §2 and §6, then the sources below. The later audit always wins over the earlier claim; say which note governs and which it superseded.

Where this line lives today: {SOURCES}
Reproduction entry points: {REPRO}
Packages you may touch when reproducing (and no others): {PACKAGES}
Known conflicts to resolve or flag: {CONFLICTS}

Rules, all hard:
1. Reproduce through the wrapper only:
   `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id {ID} --watch <path> --cmd "<command>"`
   It restores the tree afterwards. Never run `harness/score.py` or any margin scorer. Prefer a package's verify-only mode when it has one (e.g. `MARGIN_VERIFY_ONLY=1`).
2. Write only two things: `docs/pitch-model-v2/dossiers/{ID}_{SLUG}.md` (copy `docs/pitch-model-v2/DOSSIER_TEMPLATE.md`, keep all ten headings in order) and files under `data/processed/pitch_model_v2/receipts/{ID}/`. Do not edit anything else. Do not commit.
3. Repo first, web second. Web only for public filings and press releases, at most five fetches, each logged in §4. Never fetch airbnb.com pages. Never type credentials.
4. Nothing from the kill lists may be quoted as ours. If the governing note quotes a withdrawn number, say so in §7.
5. Grade honestly: A only if the receipt shows exit 0 and a match within tolerance AND the object survives both W1 and W2 against its pre-registered line; B if reproduced but single-window or descriptive; C otherwise. A grade-C dossier is a valid, useful output. Do not stretch.
6. You do not decide. §8 lists the choices for the humans with options and a recommendation.
7. Finish by running `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/dossier_lint.py docs/pitch-model-v2/dossiers/{ID}_{SLUG}.md` and fixing anything it reports.

Your final message: the dossier path, the grade, the point value(s) per scenario and period, the strongest failure in one sentence, and the open choices as a numbered list. Nothing else.
```

- [ ] **Step 3: Write the decision log header**

`docs/pitch-model-v2/DECISIONS.md`:
```markdown
# Decisions — pitch model v2

One row per decided (line, period, scenario). `value` is what entered the spec. `rejected` names the options not taken.

| id | line | period | scenario | value | reason | rejected | date |
|---|---|---|---|---|---|---|---|
```

- [ ] **Step 4: Write the failing tests**

`analysis/src/pitch_model_v2/tests/fixtures/dossier_ok.md`: the template above filled with plausible text, `Grade: B`, and a receipt path `data/processed/pitch_model_v2/receipts/T1/receipt.json`.

`analysis/src/pitch_model_v2/tests/test_dossier_lint.py`:
```python
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
```

`analysis/src/pitch_model_v2/tests/test_decisions.py`:
```python
from pitch_model_v2 import decisions

def test_parse_rows(tmp_path):
    p = tmp_path / "DECISIONS.md"
    p.write_text("# x\n\n| id | line | period | scenario | value | reason | rejected | date |\n|---|---|---|---|---|---|---|---|\n"
                 "| DEC-0001 | D1 | 3Q26 | base | 146.3 | reviews index point | 149.0 (MODL mean) | 2026-09-19 |\n")
    rows = decisions.load(p)
    assert rows[0].id == "DEC-0001" and rows[0].line == "D1" and rows[0].value == 146.3
```

- [ ] **Step 5: Run tests to verify they fail**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/tests/test_dossier_lint.py analysis/src/pitch_model_v2/tests/test_decisions.py -q`
Expected: FAIL on import

- [ ] **Step 6: Implement `dossier_lint.py` and `decisions.py`**

```python
# dossier_lint.py
from __future__ import annotations
import json, re, sys
from pathlib import Path

HEADINGS = ["## 1. Header", "## 2. The number", "## 3. Derivation chain", "## 4. Governing sources",
            "## 5. Reproduction receipt", "## 6. Test record", "## 7. Kill list and consistency",
            "## 8. Open choices", "## 9. Judge Q&A", "## 10. Grade"]
GRADE_RE = re.compile(r"^Grade:\s*([ABC])\b", re.M)
RECEIPT_RE = re.compile(r"`(data/processed/pitch_model_v2/receipts/[^`]+/receipt\.json)`")
MATCH_RE = re.compile(r"\*\*Match:\s*(yes|no)\*\*", re.I)

def lint(path: str | Path, root: str | Path | None = None) -> list[str]:
    root = Path(root or Path.cwd()); text = Path(path).read_text(); msgs = []
    pos = 0
    for h in HEADINGS:
        i = text.find(h, pos)
        if i < 0:
            msgs.append(f"missing or out-of-order heading: {h}"); continue
        pos = i
    g = GRADE_RE.search(text)
    if not g:
        msgs.append("no 'Grade: A|B|C' line under §10"); return msgs
    grade = g.group(1)
    if grade in ("A", "B"):
        r = RECEIPT_RE.search(text); m = MATCH_RE.search(text)
        if not r:
            msgs.append("grade A/B needs a receipt path in §5")
        else:
            rp = root / r.group(1)
            if not rp.exists():
                msgs.append(f"receipt not found: {r.group(1)}")
            else:
                rec = json.loads(rp.read_text())
                if rec.get("exit_code") != 0:
                    msgs.append(f"grade {grade} but receipt exit_code={rec.get('exit_code')}")
        if not m or m.group(1).lower() != "yes":
            msgs.append(f"grade {grade} needs '**Match: yes**' in §5")
    if text.count("Q:") < 3:
        msgs.append("§9 needs three judge questions")
    return msgs

if __name__ == "__main__":
    problems = lint(sys.argv[1])
    print("\n".join(problems) if problems else "dossier clean")
    sys.exit(1 if problems else 0)
```

```python
# decisions.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Decision:
    id: str; line: str; period: str; scenario: str; value: float | str; reason: str; rejected: str; date: str

def load(path: str | Path) -> list[Decision]:
    rows = []
    for ln in Path(path).read_text().splitlines():
        if not ln.startswith("| DEC-"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) != 8:
            raise ValueError(f"bad decision row: {ln}")
        try:
            val: float | str = float(cells[4])
        except ValueError:
            val = cells[4]
        rows.append(Decision(cells[0], cells[1], cells[2], cells[3], val, cells[5], cells[6], cells[7]))
    return rows
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/tests -q`
Expected: all tests pass (spec 7, repro 2, lint 4, decisions 1)

- [ ] **Step 8: Commit**

```bash
git add analysis/src/pitch_model_v2 docs/pitch-model-v2
git commit -q -m "pitch_model_v2: dossier template, digger brief, decision log, linter

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---
### Task A5: Workbook builder

**Files:**
- Create: `analysis/src/pitch_model_v2/build.py`
- Create: `analysis/src/pitch_model_v2/tests/test_build.py`

**Interfaces:**
- Consumes: `spec.load`, `spec.to_excel`, `decisions.load`.
- Produces: `build(spec_path, out_path, decisions_path=None, recalc=False) -> Path`. Tabs: `Cover`, `Drivers`, `Revenue and Guide`, `Costs and Earnings`, `Valuation and Call`, `5 Nov Event Card`, `Street`, `Evidence`, `Decision Log`, `Scenario Data`. Defined names `<ID>_<PERIOD>` on the block tab cells and `Scenario` on `Cover!B4`.

- [ ] **Step 1: Write the failing test**

`analysis/src/pitch_model_v2/tests/test_build.py`:
```python
from pathlib import Path
from openpyxl import load_workbook
from pitch_model_v2 import build

FIX = Path(__file__).parent / "fixtures" / "spec_small.yaml"

def test_build_names_and_formulas(tmp_path):
    out = build.build(FIX, tmp_path / "m.xlsx", check_paths=False)
    wb = load_workbook(out)
    names = set(wb.defined_names.keys())
    assert {"D1_3Q26", "D6_3Q26", "R2_4Q26", "R5FY_FY26", "Scenario"} <= names
    ws = wb["Drivers"]
    # find the D6 / 3Q26 cell through its defined name
    dest = wb.defined_names["D6_3Q26"].attr_text  # "'Drivers'!$G$5" style
    sheet, ref = dest.split("!"); cell = wb[sheet.strip("'")][ref.replace("$", "")]
    assert cell.value == "=D1_3Q26*D4T_3Q26"
    r2 = wb.defined_names["R2_3Q26"].attr_text.split("!")
    assert wb[r2[0].strip("'")][r2[1].replace("$", "")].value == "=LAM_3Q26*(2/3*D6_2Q26+1/3*D6_1Q26)"
    d1 = wb.defined_names["D1_3Q26"].attr_text.split("!")
    v = wb[d1[0].strip("'")][d1[1].replace("$", "")].value
    assert v.startswith("=INDEX('Scenario Data'!") and "MATCH(Scenario," in v
    sd = wb["Scenario Data"]
    assert sd["A1"].value == "id" and sd["E1"].value == "base" and sd["F1"].value == "short"
    ev = wb["Evidence"]
    ids = [ev.cell(row=r, column=1).value for r in range(2, ev.max_row + 1)]
    assert "D1" in ids and "D6" in ids
    assert wb.calculation.fullCalcOnLoad is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/tests/test_build.py -q`
Expected: FAIL on import

- [ ] **Step 3: Implement `build.py`**

```python
"""Build the pitch model workbook from the spec. Every input is a named cell fed by the
Scenario Data tab through the Scenario selector; every other cell is a formula in names."""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation
from . import spec as specmod
from . import decisions as decmod

TABS = {"drivers": "Drivers", "revenue": "Revenue and Guide", "costs": "Costs and Earnings",
        "valuation": "Valuation and Call", "event": "5 Nov Event Card", "street": "Street"}
ORDER = ["Cover", "Drivers", "Revenue and Guide", "Costs and Earnings", "Valuation and Call",
         "5 Nov Event Card", "Street", "Evidence", "Decision Log", "Scenario Data"]
FMT = {"pct": "0.00%", "musd": "#,##0", "usd": "0.00", "m": "0.0", "x": "0.0x", "prob": "0.00", "usd_share": "0.00"}
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")   # yellow: an input, named, fed by Scenario Data
FORMULA_FILL = PatternFill("solid", fgColor="FFFFFF")
HEAD = Font(bold=True)

def _name(wb: Workbook, name: str, sheet: str, col: int, row: int) -> None:
    wb.defined_names[name] = DefinedName(name, attr_text=f"'{sheet}'!${get_column_letter(col)}${row}")

def build(spec_path: str | Path, out_path: str | Path, decisions_path: str | Path | None = None,
          recalc: bool = False, check_paths: bool = True) -> Path:
    s = specmod.load(spec_path, check_paths=check_paths)
    periods, scenarios = list(s.meta["periods"]), list(s.meta["scenarios"])
    wb = Workbook(); wb.remove(wb.active)
    cover = wb.create_sheet("Cover")
    cover["A1"] = "Airbnb (ABNB) — pitch model v2"; cover["A1"].font = Font(bold=True, size=14)
    cover["A2"] = f"Price date {s.meta['price_date']} · spot ${s.meta['spot']}"
    cover["A4"] = "Scenario"; cover["A4"].font = HEAD; cover["B4"] = scenarios[0]; cover["B4"].fill = INPUT_FILL
    dv = DataValidation(type="list", formula1='"' + ",".join(scenarios) + '"', allow_blank=False)
    cover.add_data_validation(dv); dv.add("B4"); _name(wb, "Scenario", "Cover", 2, 4)
    cover["A6"] = "Yellow cells are inputs; each carries a defined name (id_period), a grade, and a decision id. Every other number is a formula in those names: use Formulas > Trace Precedents."
    # Scenario Data
    sd = wb.create_sheet("Scenario Data")
    for j, h in enumerate(["id", "period", "label", "unit", *scenarios], start=1):
        sd.cell(row=1, column=j, value=h).font = HEAD
    sd_row = {}
    r = 2
    for lid in s.order:
        ln = s.lines[lid]
        if ln.kind != "input":
            continue
        for p in ln.periods:
            sd.cell(row=r, column=1, value=lid); sd.cell(row=r, column=2, value=p)
            sd.cell(row=r, column=3, value=ln.label); sd.cell(row=r, column=4, value=ln.unit)
            for k, sc in enumerate(scenarios):
                sd.cell(row=r, column=5 + k, value=float(ln.values[sc][p]))
            sd_row[(lid, p)] = r; r += 1
    first_sc, last_sc = get_column_letter(5), get_column_letter(4 + len(scenarios))
    # block tabs
    sheets = {b: wb.create_sheet(t) for b, t in TABS.items()}
    rows = {b: 2 for b in TABS}
    for b, ws in sheets.items():
        for j, h in enumerate(["id", "line", "unit", "grade · decision", *periods], start=1):
            ws.cell(row=1, column=j, value=h).font = HEAD
        ws.freeze_panes = "E2"; ws.column_dimensions["B"].width = 44; ws.column_dimensions["D"].width = 18
    for lid in s.order:
        ln = s.lines[lid]
        if ln.block not in sheets:
            raise specmod.SpecError(f"{lid}: unknown block {ln.block}")
        ws = sheets[ln.block]; row = rows[ln.block]; rows[ln.block] += 1
        ws.cell(row=row, column=1, value=lid); ws.cell(row=row, column=2, value=ln.label); ws.cell(row=row, column=3, value=ln.unit)
        if ln.kind == "input":
            pv = ln.provenance; ws.cell(row=row, column=4, value=f"{pv['grade']} · {pv['decision']}")
        else:
            ws.cell(row=row, column=4, value="formula: " + ln.expr)
        for p in ln.periods:
            col = 5 + periods.index(p); c = ws.cell(row=row, column=col)
            if ln.kind == "input":
                sr = sd_row[(lid, p)]
                c.value = f"=INDEX('Scenario Data'!${first_sc}${sr}:${last_sc}${sr},MATCH(Scenario,'Scenario Data'!${first_sc}$1:${last_sc}$1,0))"
                c.fill = INPUT_FILL
            else:
                c.value = "=" + specmod.to_excel(ln.expr, p, periods)
            c.number_format = FMT.get(ln.unit, "General")
            _name(wb, f"{lid}_{p}", ws.title, col, row)
    # Evidence
    ev = wb.create_sheet("Evidence")
    for j, h in enumerate(["id", "line", "kind", "grade", "decision", "tolerance", "dossier", "receipt", "expr"], start=1):
        ev.cell(row=1, column=j, value=h).font = HEAD
    for i, lid in enumerate(s.order, start=2):
        ln = s.lines[lid]; pv = ln.provenance
        vals = [lid, ln.label, ln.kind, pv.get("grade", ""), pv.get("decision", ""), pv.get("tolerance", ""),
                pv.get("dossier", ""), pv.get("receipt", ""), ln.expr]
        for j, v in enumerate(vals, start=1):
            ev.cell(row=i, column=j, value=v)
    # Decision Log
    dl = wb.create_sheet("Decision Log")
    for j, h in enumerate(["id", "line", "period", "scenario", "value", "reason", "rejected", "date"], start=1):
        dl.cell(row=1, column=j, value=h).font = HEAD
    if decisions_path and Path(decisions_path).exists():
        for i, d in enumerate(decmod.load(decisions_path), start=2):
            for j, v in enumerate([d.id, d.line, d.period, d.scenario, d.value, d.reason, d.rejected, d.date], start=1):
                dl.cell(row=i, column=j, value=v)
    wb._sheets = [wb[n] for n in ORDER if n in wb.sheetnames]
    wb.active = 0
    wb.calculation.fullCalcOnLoad = True
    out = Path(out_path); out.parent.mkdir(parents=True, exist_ok=True); wb.save(out)
    if recalc:
        from . import recalc as rc
        rc.recalc(out)
    return out

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="model/pitch_model_v2/spec/lines.yaml")
    ap.add_argument("--out", default="model/pitch_model_v2/ABNB_pitch_model_v2.xlsx")
    ap.add_argument("--decisions", default="docs/pitch-model-v2/DECISIONS.md")
    ap.add_argument("--no-recalc", action="store_true")
    a = ap.parse_args(argv)
    out = build(a.spec, a.out, a.decisions, recalc=not a.no_recalc)
    print("built", out); return 0

if __name__ == "__main__":
    sys.exit(main())
```

Note on the test: it calls `build.build(FIX, ..., check_paths=False)`; the signature above accepts it.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/tests/test_build.py -q`
Expected: `1 passed`

- [ ] **Step 5: Commit**

```bash
git add analysis/src/pitch_model_v2
git commit -q -m "pitch_model_v2: workbook builder with named inputs, live formulas, scenario selector

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task A6: Excel recalculation and the QA gate

**Files:**
- Create: `analysis/src/pitch_model_v2/recalc.py`, `analysis/src/pitch_model_v2/qa.py`
- Create: `analysis/src/pitch_model_v2/tests/test_qa.py`

**Interfaces:**
- Produces: `recalc.recalc(path) -> bool`; `qa.check(workbook_path, spec_path, root, allow_uncalculated=False) -> list[str]` (empty = pass); CLI `python3 -m pitch_model_v2.qa --wb <xlsx> --spec <yaml>` exits 1 on any message.

- [ ] **Step 1: Write the failing test**

`analysis/src/pitch_model_v2/tests/test_qa.py`:
```python
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

def test_qa_flags_value_not_in_dossier(tmp_path):
    _dossiers(tmp_path)
    (tmp_path / "docs/pitch-model-v2/dossiers/D1_nights.md").write_text("## 2. The number\n| scenario | period | point |\n|---|---|---|\n| base | 3Q26 | 140.0 |\n")
    out = build.build(FIX, tmp_path / "m.xlsx", check_paths=False)
    msgs = qa.check(out, FIX, root=tmp_path, allow_uncalculated=True)
    assert any("D1" in m and "3Q26" in m for m in msgs)

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/tests/test_qa.py -q`
Expected: FAIL on import

- [ ] **Step 3: Implement `recalc.py`**

```python
"""Open the workbook in the installed Microsoft Excel, force a full calculation, save.
Used so that viewers without a calc engine (and openpyxl data_only reads) see values."""
from __future__ import annotations
import shutil, subprocess, sys
from pathlib import Path

SCRIPT = '''
tell application "Microsoft Excel"
    set wbk to open workbook workbook file name POSIX file "{path}"
    try
        calculate full rebuild
    on error
        calculate
    end try
    save wbk
    close wbk saving no
end tell
'''

def recalc(path: str | Path) -> bool:
    p = Path(path).resolve()
    if not Path("/Applications/Microsoft Excel.app").exists() or shutil.which("osascript") is None:
        print("Excel or osascript not available; skipping recalculation"); return False
    r = subprocess.run(["osascript", "-e", SCRIPT.format(path=str(p))], capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print("recalc failed:", r.stderr.strip()); return False
    return True

if __name__ == "__main__":
    sys.exit(0 if recalc(sys.argv[1]) else 1)
```

- [ ] **Step 4: Implement `qa.py`**

```python
"""QA gate for the built workbook. Every message is a failure."""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from openpyxl import load_workbook
from . import spec as specmod

ERR = ("#REF!", "#NAME?", "#DIV/0!", "#VALUE!", "#N/A", "#NUM!", "#NULL!")
NAME_RE = re.compile(r"\b([A-Z][A-Z0-9_]*_[0-9A-Z]+)\b")
BUILTIN = {"INDEX", "MATCH", "SUM", "MIN", "MAX", "IF", "ABS"}
LICENSED = re.compile(r"(BEST_|BDH\(|BDP\(|=BDS|LSEG Workspace export|Third Bridge)", re.I)
ROW_RE = re.compile(r"^\|\s*(\w+)\s*\|\s*([0-9A-Z]+)\s*\|\s*([-+]?\d*\.?\d+)")

def _dossier_points(path: Path) -> dict[tuple[str, str], float]:
    pts = {}
    if not path.exists():
        return pts
    in_sec = False
    for ln in path.read_text().splitlines():
        if ln.startswith("## 2."):
            in_sec = True; continue
        if in_sec and ln.startswith("## "):
            break
        if in_sec:
            m = ROW_RE.match(ln)
            if m and m.group(1) not in ("scenario", "---"):
                pts[(m.group(1), m.group(2))] = float(m.group(3))
    return pts

def check(workbook_path: str | Path, spec_path: str | Path, root: str | Path | None = None, allow_uncalculated: bool = False) -> list[str]:
    root = Path(root or Path.cwd()); msgs: list[str] = []
    s = specmod.load(spec_path, check_paths=False)
    wbf = load_workbook(workbook_path); wbv = load_workbook(workbook_path, data_only=True)
    names = set(wbf.defined_names.keys())
    # 1. error cells and calculation state
    uncalculated = 0
    for ws in wbf.worksheets:
        wsv = wbv[ws.title]
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if isinstance(v, str) and v.strip() in ERR:
                    msgs.append(f"{ws.title}!{c.coordinate}: error literal {v.strip()}")
                if isinstance(v, str) and v.startswith("="):
                    vv = wsv[c.coordinate].value
                    if vv is None:
                        uncalculated += 1
                    elif isinstance(vv, str) and vv.strip() in ERR:
                        msgs.append(f"{ws.title}!{c.coordinate}: evaluates to {vv.strip()}")
                    for n in NAME_RE.findall(v):
                        if n not in names and n.split("_")[0] not in BUILTIN:
                            msgs.append(f"{ws.title}!{c.coordinate}: unresolved name {n}")
                if isinstance(v, str) and LICENSED.search(v):
                    msgs.append(f"{ws.title}!{c.coordinate}: looks like licensed export content: {v[:60]!r}")
    if uncalculated and not allow_uncalculated:
        msgs.append(f"{uncalculated} formula cells have no cached value: run recalc")
    # 2. every spec input: name, provenance files, receipt exit 0, value present in dossier §2
    for lid in s.order:
        ln = s.lines[lid]
        for p in ln.periods:
            if f"{lid}_{p}" not in names:
                msgs.append(f"{lid}_{p}: defined name missing")
        if ln.kind != "input":
            continue
        pv = ln.provenance
        dpath, rpath = root / pv["dossier"], root / pv["receipt"]
        if not dpath.exists():
            msgs.append(f"{lid}: dossier missing {pv['dossier']}"); continue
        if not rpath.exists():
            msgs.append(f"{lid}: receipt missing {pv['receipt']}")
        else:
            rec = json.loads(rpath.read_text())
            if rec.get("exit_code") != 0:
                msgs.append(f"{lid}: receipt exit_code {rec.get('exit_code')}")
        pts = _dossier_points(dpath); tol = float(pv.get("tolerance", 0))
        for sc, per_vals in ln.values.items():
            for p, v in per_vals.items():
                if (sc, p) not in pts:
                    msgs.append(f"{lid} {sc} {p}: value {v} not stated in dossier §2")
                elif abs(pts[(sc, p)] - float(v)) > tol:
                    msgs.append(f"{lid} {sc} {p}: spec {v} vs dossier {pts[(sc, p)]} exceeds tolerance {tol}")
    return msgs

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--wb", required=True); ap.add_argument("--spec", required=True)
    ap.add_argument("--allow-uncalculated", action="store_true")
    a = ap.parse_args(argv)
    msgs = check(a.wb, a.spec, allow_uncalculated=a.allow_uncalculated)
    print("\n".join(msgs) if msgs else "QA clean"); return 1 if msgs else 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/tests -q`
Expected: all pass

- [ ] **Step 6: Smoke the recalc on the fixture build**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -c "from pitch_model_v2 import build; print(build.build('analysis/src/pitch_model_v2/tests/fixtures/spec_small.yaml', '/tmp/pm2_smoke.xlsx', check_paths=False, recalc=True))" && PYTHONPATH=analysis/src python3 -c "from openpyxl import load_workbook; wb=load_workbook('/tmp/pm2_smoke.xlsx', data_only=True); print(wb['Drivers']['G4'].value)"`
Expected: a number, not `None` (Excel opened, calculated, saved). If Excel shows a dialog, accept once; the script runs headless afterwards.

- [ ] **Step 7: Commit**

```bash
git add analysis/src/pitch_model_v2
git commit -q -m "pitch_model_v2: Excel recalculation and the QA gate

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task A7: Tie-out against memo v3 and the L4 workbook

**Files:**
- Create: `analysis/src/pitch_model_v2/tieout.py`, `model/pitch_model_v2/spec/tieout_targets.csv`
- Create: `analysis/src/pitch_model_v2/tests/test_tieout.py`

**Interfaces:**
- Consumes: `spec.load`, `decisions.load`.
- Produces: `tieout.write(spec_path, targets_csv, decisions_path, out_md) -> Path`. Targets CSV columns: `line,period,scenario,source,value,note`.

- [ ] **Step 1: Seed the targets file with memo v3's estimates table**

`model/pitch_model_v2/spec/tieout_targets.csv` (values from `deck/drafts/memo_v3_short_2026-09-17.md`, "Estimates vs consensus"; the L4 rows are added by the executor from `model/lane4_v2/outputs/lane4_model/snapshot_v2/ABNB_L4_review.xlsx` after opening it read-only):
```csv
line,period,scenario,source,value,note
D1,3Q26,base,memo_v3,146.3,"team base, +9.5%"
D1,3Q26,short,memo_v3,145.0,"short case, +8.5%"
R2,3Q26,base,memo_v3,4804,"team base revenue $M"
R2,3Q26,short,memo_v3,4681,"short case revenue $M"
C6,3Q26,base,memo_v3,2420,"adj. EBITDA $M, 50.4%"
C6,3Q26,short,memo_v3,2290,"adj. EBITDA $M, 48.9%"
R5,4Q26,base,memo_v3,3178,"4Q26 revenue $M (bridge v3)"
R5,4Q26,short,memo_v3,2966,"4Q26 revenue $M short"
R6,FY27,base,memo_v3,15800,"FY27 revenue $M, +10.9%"
R6,FY27,short,memo_v3,14900,"FY27 revenue $M, +4.5%"
C6,FY27,base,memo_v3,5644,"FY27 adj. EBITDA $M, 35.7%"
C6,FY27,short,memo_v3,4761,"FY27 adj. EBITDA $M, 31.9%"
C7,FY27,base,memo_v3,5.93,"FY27 EPS"
C7,FY27,short,memo_v3,4.58,"FY27 EPS short"
```

- [ ] **Step 2: Write the failing test**

`analysis/src/pitch_model_v2/tests/test_tieout.py`:
```python
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
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/tests/test_tieout.py -q`
Expected: FAIL on import

- [ ] **Step 4: Implement `tieout.py`**

```python
from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
from . import spec as specmod
from . import decisions as decmod

def write(spec_path, targets_csv, decisions_path, out_md, check_paths: bool = True) -> Path:
    s = specmod.load(spec_path, check_paths=check_paths)
    decs = decmod.load(decisions_path) if Path(decisions_path).exists() else []
    by_key = {}
    for d in decs:
        by_key.setdefault((d.line, d.period, d.scenario), []).append(d.id)
    lines = ["# Tie-out — spec vs memo v3 / L4", "", "| line | period | scenario | spec | target | diff | diff % | source | explained by |", "|---|---|---|---|---|---|---|---|---|"]
    unexplained = 0
    with open(targets_csv, newline="") as f:
        for row in csv.DictReader(f):
            lid, p, sc = row["line"], row["period"], row["scenario"]
            ln = s.lines.get(lid)
            sv = None
            if ln and ln.kind == "input" and p in ln.values.get(sc, {}):
                sv = float(ln.values[sc][p])
            tv = float(row["value"])
            if sv is None:
                lines.append(f"| {lid} | {p} | {sc} | (formula or absent) | {tv} | | | {row['source']} | see workbook |"); continue
            diff = round(sv - tv, 4); pct = round(100 * diff / tv, 2) if tv else 0.0
            expl = ", ".join(by_key.get((lid, p, sc), [])) if abs(diff) > 1e-9 else "match"
            if expl == "":
                expl = "UNEXPLAINED"; unexplained += 1
            lines.append(f"| {lid} | {p} | {sc} | {sv} | {tv} | {diff} | {pct} | {row['source']} | {expl} |")
    lines += ["", f"Unexplained differences: {unexplained}"]
    out = Path(out_md); out.write_text("\n".join(lines) + "\n"); return out

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="model/pitch_model_v2/spec/lines.yaml")
    ap.add_argument("--targets", default="model/pitch_model_v2/spec/tieout_targets.csv")
    ap.add_argument("--decisions", default="docs/pitch-model-v2/DECISIONS.md")
    ap.add_argument("--out", default="docs/pitch-model-v2/TIEOUT.md")
    a = ap.parse_args(argv); print("wrote", write(a.spec, a.targets, a.decisions, a.out)); return 0

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd ~/Citadel-ABNB && PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/tests -q`
Expected: all pass

- [ ] **Step 6: Commit**

```bash
git add analysis/src/pitch_model_v2 model/pitch_model_v2/spec/tieout_targets.csv
git commit -q -m "pitch_model_v2: tie-out generator against memo v3 and L4

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---
# Track B: the dossier programme

Track B is executed by the brain session (this Claude session with Theo), not by a fresh implementer. Tasks B1 to B5 are procedures; each ends with a green build and a commit.

### Task B0: `LINES.md`, the registry that fills every digger brief

**Files:**
- Create: `docs/pitch-model-v2/LINES.md`

Every block below is pasted into `DIGGER_BRIEF_TEMPLATE.md` at `{SOURCES}`, `{REPRO}`, `{PACKAGES}`, `{CONFLICTS}`, with `{JUDGE_QUESTION}` from the first line. H0 is added to the spec's thirty lines: printed history, without which the kernel formulas have nothing to lag.

- [ ] **Step 1: Write `docs/pitch-model-v2/LINES.md` with this content**

```markdown
# Lines — registry for digger briefs

Environment: `python3` = 3.13 / pandas 3.0; fallback `.venv-pd2/bin/python` = pandas 2.3.3. Record here which interpreter each package needed.

## H0 — Printed history 1Q23–2Q26 (Sonnet, wave 1)
Judge: "Do your historicals tie to the filings, line by line?"
Sources: `data/processed/airbnb_quarterly_kpis.csv`; `data/processed/abnb_edgar_quarterly_kpis.csv`; `data/processed/abnb_quarterly_costlines.csv`; `data/processed/margin_build/02_financial_panel/02_panel_quarterly.csv`; `data/processed/abnb_driver_history_quarterly.csv`; 10-Q/10-K figures quoted in `docs/margin-build/notes/40_line_build.md`.
Repro: `analysis/src/abnb_costlines_from_xbrl.py`; `analysis/src/nights_quarterly.py`; `analysis/src/margin_build/02_financial_panel/` (read-only comparison of the three KPI files against each other and against one filing per year, quoted).
Packages: `data/processed/` KPI files above (read); `analysis/src/margin_build/02_financial_panel`.
Conflicts: G&A is on the ex-lodging-reserve basis in the pitch workbook (4Q23 ~$1bn reserve in a reconciling line); three KPI files exist and must agree; nights, ADR, GBV, revenue, take rate, adj. EBITDA, the five cash cost lines, SBC, D&A, share count.

## D1 — 3Q26 nights, level and y/y (Opus, wave 1)
Judge: "Why 146.3m when 28 sell-side estimates average 148.9m and the lowest is 147.0m?"
Sources: `docs/q3nowcast/SYNTHESIS.md`; `analysis/src/q3nowcast/E4_build_index.py`, `E5_backtest.py`, `E6_nowcast.py`, `G2_external_backtests.py`, `G3_rank_sources.py`; `data/processed/q3nowcast/`; `analysis/src/q3nowcast_v2/E/` and `data/processed/q3nowcast_v2/E/`; `docs/revenue-forecast-strategy/05_backtests/WPK_reviews-index-2023-vintage.md`; `SR_QUARTER_SUBMISSION_READINESS_v1.md` ("reviews revalidation"); `data/processed/nights_baseline_reconciliation.csv`; `docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/` and `risk-q3-nights-accelerates/`; `deck/drafts/memo_v3_short_2026-09-17.md` "Nights".
Repro: `E5_backtest.py` and `E6_nowcast.py` from the processed review counts (the raw 2023 mirror lives on Krish's machine; `~/abnb_ia_capture/` holds Theo's daily capture; state exactly what was reproducible without raw); `G2_external_backtests.py` for the external stack.
Packages: `analysis/src/q3nowcast`, `analysis/src/q3nowcast_v2/E`, `data/processed/q3nowcast`, `data/processed/q3nowcast_v2`.
Conflicts: memo v3 quotes the reviews index at 0.68x naive; WPK-A finds 0.68 was W2-only with stale training and the honest re-run is 0.76/0.84, failing the 0.75 hurdle; the SR note says not to present 0.68x as validated. The 148.9m bar is Bloomberg MODL (quote as an aggregate with date only). Calendar pace failed its backtest (sign inverted).

## D2 — 4Q26 nights and the RNPL / ex-NA lap (Opus, wave 1 follow-on; wave 2)
Judge: "How much of the 2026 re-acceleration laps in 4Q26, and how do you know it is not demand?"
Sources: `analysis/src/overnight2/` D module and `docs/overnight2/SYNTHESIS.md`; `data/processed/overnight2/D/D1_rnpl_cohort_scenarios.csv`; `analysis/src/na_nights_reconciliation.py` and `data/processed/na_nights_lap_scenarios.csv`, `na_nights_decomposition.csv`; `05_backtests/B3_FY27_DECOMPOSITION.md`; `05_backtests/ALPHA_F_RNPL.md` and `analysis/src/forecast_methods/rnpl_v2/`; `docs/pitch-forecasts/questions/risk-q4-nights-print-meets-street/` (adopted Q4 object, mean 8.61, sd 2.28); `research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md`.
Repro: `analysis/src/na_nights_reconciliation.py`; `rnpl_v2/run.py`; the overnight2 D scripts.
Packages: `analysis/src/overnight2`, `analysis/src/forecast_methods/rnpl_v2`, `data/processed/overnight2`, `data/processed/forecast_methods/rnpl_v2`.
Conflicts: D-08 (adopt the ex-NA lap, 8.0–8.2%) is an open team decision; D-11 says chaining the 4Q26 ex-NA lap with PR #32's 1Q27 lap double-counts ~0.8pp; the cohort engine bounds the cancellation drag at −0.2 to −0.9pt; the 34-market calendar test found no cancellation signature.

## D3 — FY27 nights path (Sonnet, wave 2)
Judge: "What does FY27 nights growth have to be for your revenue, and what is it made of?"
Sources: `analysis/src/margin_build/06_fy27_path_v2/` and `data/processed/margin_build/06_fy27_path_v2/06_revenue_path_3q26_4q27_v2b.csv`; `analysis/src/h1_to_h2_bridge_v3.py` and `data/processed/h2_bridge_v3/`; `05_backtests/REBASE_h2_bridge_v3_nights_adr.md`.
Repro: `analysis/src/h1_to_h2_bridge_v3.py`; `06_fy27_path_v2/run.py` (or its script; read its README).
Packages: `analysis/src/margin_build/06_fy27_path_v2`, `data/processed/margin_build/06_fy27_path_v2`, `data/processed/h2_bridge_v3`.
Conflicts: memo v3 gives FY27 nights +6.4% (global lap) to +8.2% (NA-only) against +8–9% in the price; bridge v3 base is +10.9% revenue. State which nights path each revenue number uses.

## D4 — ADR ex-FX and its decomposition (Opus, wave 1)
Judge: "Your ADR sits on consensus for 3Q26; where does the price leg come from and how much is mix?"
Sources: `docs/adrv3/`, `analysis/src/adrv3/`, `data/processed/adrv3/`; `research/notes/2026-09-07_adr-decomposition.md`; `model/ADR_decomposition.xlsx`; `05_backtests/L3_ADR_HOTEL_RESULTS.md`, `L3_ADR_HOTEL_AUDIT_REPAIR_v1.md`, `L3_ADR_HOTEL_PREREG.md`; `analysis/src/adr/05_size_mix.py`; `data/processed/abnb_size_regression.csv`, `insideairbnb_price_by_accommodates.csv`; `docs/pitch-forecasts/questions/risk-adr-residual-persists/`, `bonus-adr-residual-reverts/`.
Repro: `analysis/src/adrv3/` run script (read its README); `analysis/src/adr/05_size_mix.py` (rebuilds a cache in ~30 s).
Packages: `analysis/src/adrv3`, `analysis/src/adr`, `data/processed/adrv3`, `data/processed/adr`.
Conflicts: "half of ADR growth is bigger units" is on the kill list (it is +0.46–0.8pp; bedroom elasticity 0.23); the like-for-like price residual (+2.8–3.6pp) is unidentified; the L3 ADR audit found historical inputs unavailable at guide dates, so the decomposition is descriptive, not a validated forecast; the ADR nowcast does not beat naive.

## D5 — ADR FX and revenue FX by quarter (Sonnet, wave 1)
Judge: "How much of 4Q26 revenue growth is FX, and is it already known?"
Sources: `analysis/src/forecast_methods/fx_lag_v2/` (`run.py`, `README.md`); `data/processed/forecast_methods/fx_lag_v2/`; `data/processed/overnight/05_fx_schedule.csv`; `05_backtests/B4_FX_EXHIBIT.md`, `fx-lag.md`, `VERIFY_fx-lag_r1.md`, `FXSWAP_h2_bridge_kernel_fx.md`; `docs/pitch-forecasts/questions/q3-revenue-fx-integer/`, `risk-dollar-weakens/`.
Repro: `python3 analysis/src/forecast_methods/fx_lag_v2/run.py` using the cached `fx_daily_2026-09-11.csv` (do not run `fetch_fx_v2.py`; it calls FRED).
Packages: `analysis/src/forecast_methods/fx_lag_v2`, `data/processed/forecast_methods/fx_lag_v2`.
Conflicts: the −3.4pp Q4 FX step and "82% of Q4 FX already determined" are on the kill list; adopted numbers are 4Q26 revenue FX +1.0pp (CS +0.3–2.2) and an effective lag of 0.4–0.5 quarters; memo v3 says revenue FX is "84% observed for 4Q26", which must be reconciled with the kill-list wording.

## D6 — GBV and the regional cross-check (Sonnet, wave 2)
Judge: "Does nights times ADR give your GBV, and does the regional build sum to it?"
Sources: identity; `05_backtests/X_REGIONAL_KERNEL_OD_FX.md`, `R_REGIONAL_REFRESH.md`; `analysis/src/forecast_methods/regional_kernel_v1/`; `data/processed/airbnb_regional_revenue_quarterly.csv`; `05_backtests/PREREG_ABNB-INT-v1.md` D-04 (block ii: 147.38M nights / $180.15 / $26,550M).
Repro: `regional_kernel_v1/run.py`; recompute the identity from H0 and the D1/D4 decided values.
Packages: `analysis/src/forecast_methods/regional_kernel_v1`, `data/processed/forecast_methods/regional_kernel_v1`.
Conflicts: the object-by-object hybrid breaks the GBV identity by −3.1pp (D-04); WP-X returned underpowered.

## D7 — Take rate and the fee migration (Opus, wave 2)
Judge: "Is take rate an input or an output, and what does the single host fee do to it?"
Sources: `05_backtests/B1_TAKE_RATE_RECONCILIATION.md`; `fee-takerate.md`; `analysis/src/forecast_methods/fee_takerate/`, `fee_panels/`, `fee_panel_v1/`; `05_backtests/L3_FEE_RESULTS_v1.md`, `L3_FEE_AUDIT_CLOSE_v3.md`, `A3_fee_panels.md`, `N_THETA_DID.md` (if present); `data/processed/airbnb_adr_takerate_quarterly.csv`; `docs/pitch-forecasts/questions/q3-take-rate-above-1810/`, `risk-single-fee-take-rate-accretion-stated/`, `bonus-take-rate-guided-down/`.
Repro: `fee_takerate/run.py`; recompute 3Q26 take rate 18.14% and P(≥18.10%) by GBV band from B1's inputs.
Packages: `analysis/src/forecast_methods/fee_takerate`, `fee_panels`, `fee_panel_v1` and their `data/processed` folders.
Conflicts: pass-through θ is unidentified ("0.83–1.41" was a detection window); "+4.05% fee uplift" is on the kill list; the 1.71M quote panel is not fee-inclusive; no detectable fee effect on the printed take rate through 2Q26 (n 20).

## R1 — Kernel: λ by season and the lag weights (Opus, wave 1)
Judge: "Why should revenue be two-thirds last quarter's bookings plus one-third the quarter before?"
Sources: `analysis/src/forecast_methods/kernel_lambda/` (`run.py`, `kernel.py`, `README.md`); `kernel_engine_v2/`; `kernel_phi_v2/`; `kernel_leadtime_v2/`; notes `kernel-lambda.md`, `VERIFY_kernel-lambda_r1.md`, `K1_KERNEL_WEIGHTS_AND_BACKLOG.md`, `K2_KERNEL_FROM_LEAD_TIMES.md`, `K0_KERNEL_ENGINE_v2.md`, `GD_DECISION_REPORT_v2.md`, `GD_HORIZON_RESULTS_v1.md`, `GD_HORIZON_ELIGIBILITY_ADDENDUM_v1.md`; `data/processed/forecast_methods/gbv_decision_0915_v1/`; `~/Citadel-ABNB-untracked/.../net_gbv_reverse_v1` and `NET_GBV_REVERSE_HANDOFF_v1.md`.
Repro: `python3 analysis/src/forecast_methods/kernel_lambda/run.py` through the wrapper (it re-registers; the wrapper restores); `kernel_engine_v2/run.py`.
Packages: `kernel_lambda`, `kernel_engine_v2`, `kernel_phi_v2` under `analysis/src/forecast_methods/` and `data/processed/forecast_methods/`.
Conflicts: fixed (⅔/⅓, 4 seasonal parameters) vs joint (7 parameters) — Willem's audit finds joint beats fixed but loses to a simple guide-growth baseline at the next guide; the ⅔ weight is PIT-optimal (0.65–0.70), not identified from the ledger (φ₁+φ₂ 0.58–0.64); λ_Q4 12.03% with a three-year range of 0.17pp.

## R2 — 3Q26 revenue: kernel vs guide+cushion vs bridge (Opus, wave 2)
Judge: "You say 3Q26 revenue beats and you do not trade it; what is the number and why three of them?"
Sources: `K1_KERNEL_WEIGHTS_AND_BACKLOG.md` ($4,795M ledger-only, $4,816M combined); `B1_TAKE_RATE_RECONCILIATION.md`; `data/processed/h2_bridge_v3/` ($4,804M); `analysis/src/forecast_methods/live_block_v2/`; `PREREG_ABNB-INT-v1.md` D-01; `05_backtests/SCOREBOARD_v2.md` (guide×cushion RMSE ratio 0.377/0.319); LSEG 3Q26 $4,744M via `L0_vintage_register.csv`; guide $4,690–4,770M.
Repro: `live_block_v2/run.py`; recompute kernel 3Q26 from H0 GBV and R1 λ; recompute guide×(1+cushion) from R3.
Packages: `analysis/src/forecast_methods/live_block_v2`, `data/processed/forecast_methods/live_block_v2`.
Conflicts: D-01 is open (guide+cushion $4,816M vs kernel $4,804M as the card value); memo v3 uses $4,804M.

## R3 — Guide cushion, trailing eight (Sonnet, wave 1)
Judge: "Airbnb beat its guide 19 of 19 times; how much of that is mechanics?"
Sources: `analysis/src/forecast_methods/guidance_policy/` (`run.py`, `lib.py`); `data/processed/forecast_methods/guidance_policy/`; notes `guidance-policy.md`, `VERIFY_guidance-policy_r1.md`, `_r2.md`; `data/processed/abnb_revenue_guidance_vs_actual.csv`; `data/processed/overnight/02_guidance_ledger.csv`.
Repro: `python3 analysis/src/forecast_methods/guidance_policy/run.py` through the wrapper.
Packages: `analysis/src/forecast_methods/guidance_policy`, `data/processed/forecast_methods/guidance_policy`.
Conflicts: the 9/9 guide-below-Street drift rule as a tradeable signal, any p-value for it, and M5's hierarchical cushion model are on the kill list; cushion mean +1.86%, median +1.79%, sd 1.006pp.

## R4 — 4Q26 guide midpoint the model implies (Opus, wave 2)
Judge: "What guide do you expect on 5 Nov, and what is the Street's number for the same object?"
Sources: `05_backtests/B2_Q4_GUIDE_EXHIBIT.md` ($3,161M, 80% $3,012–3,312); `analysis/src/forecast_methods/guidance_policy_v2/`; `data/processed/h2_bridge_v3/` (implied guide mid $3,059M); `docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/` (C01 0.72; guide mid p50 $3,100M); `GD_DECISION_REPORT_v2.md`; `data/processed/forecast_methods/gbv_decision_0915_v1/`; `A1_consensus_vintages.md` (Street revenue ≠ guide consensus).
Repro: `guidance_policy_v2/run.py`; recompute the implied guide from R2 and R3.
Packages: `analysis/src/forecast_methods/guidance_policy_v2`, `data/processed/forecast_methods/guidance_policy_v2`, `gbv_decision_0915_v1`.
Conflicts: three midpoints in the record ($3,161M B2; $3,059M bridge v3; $3,100M pitch-forecasts p50) against a Street revenue mean of $3,157–3,162M that is not a guide consensus; D-07 (no-fee-step guide as headline) is open.

## R5 — 4Q26 and FY26 revenue (Sonnet, wave 2)
Judge: "Walk me from 3Q26 to FY26 revenue."
Sources: `analysis/src/h1_to_h2_bridge_v3.py`; `data/processed/h2_bridge_v3/`; `REBASE_h2_bridge_v3_nights_adr.md`; `06_fy27_path_v2` quarterly path.
Repro: `python3 analysis/src/h1_to_h2_bridge_v3.py` through the wrapper.
Packages: `data/processed/h2_bridge_v3`.
Conflicts: 4Q26 $3,178M (bridge v3) vs the Street $3,157–3,162M; memo's short case $2,966M comes from `40_line_build` §8b, not the bridge.

## R6 — FY27 revenue and its band (Opus, wave 3)
Judge: "FY27 +11% is the Street; you have +10.9% base and +4.5% short. Which is the pitch, and what is the honest band?"
Sources: `05_backtests/B3_FY27_DECOMPOSITION.md` (+9.18 to +11.52% across w); `06_fy27_path_v2`; `ALPHA_F_RNPL.md` (FY27 nights +6.4%); `docs/pitch-forecasts/questions/q1-27-revenue-guide-growth/`, `q1-27-nights-guide-above-82/`; `40_line_build` short case revenue path; `citadel-abnb-rnpl-balance-sheet` memory note: B3 has no lap and its w-band collapses on λ re-fit.
Repro: the B3 package (find under `analysis/src/forecast_methods/` by grep "B3"); `06_fy27_path_v2`.
Packages: the B3 package and `06_fy27_path_v2`.
Conflicts: "any FY27 level edge without the +9.2–11.5% band" is on the kill list; the short case (+4.5%) is a scenario, not a forecast; the run's F02 median 1Q27 guide growth is +10.5%.

## C1 — Cost of revenue · C2 — Operations and support · C3 — Product development · C5 — G&A ex lodging reserve (Sonnet, wave 2; one digger per line)
Judge: "What drives this cost line, and what did the 10-Q say about it?"
Sources: `analysis/src/margin_build/40_line_build/run.py`; `data/processed/margin_build/40_line_build/40_params.csv`, `40_lines_quarterly.csv`, `40_annual.csv`, `40_backcast.csv`; `docs/margin-build/notes/40_line_build.md`; `docs/margin-build/audit/CODEX_LINE_BUILD_CHECK.md`; `data/processed/abnb_quarterly_costlines.csv`; `analysis/src/margin_build/M1_driver_lines/`, `M6_cycle_flex/`; `docs/pitch-forecasts/questions/bonus-ai-hosting-cost-step/` (C1).
Repro: `python3 analysis/src/margin_build/40_line_build/run.py` through the wrapper, watching `data/processed/margin_build/40_line_build` and `model/ABNB_margin_line_build.xlsx` (~40 s). Only one of C1/C2/C3/C5 runs it; the others read its committed outputs and recompute their line from `40_params.csv` in a scratch script saved under their receipt folder.
Packages: `analysis/src/margin_build/40_line_build`, `data/processed/margin_build/40_line_build`.
Conflicts: the line build says 3Q26 costs grow 11.5% at budget; every parameter must name its 10-Q source; cash lines are GAAP less SBC and still contain D&A.

## C4 — Sales and marketing, the swing line (Opus, wave 1)
Judge: "Why is S&M the whole FY27 disagreement, and what if management just cuts it?"
Sources: everything in C1's list, plus `analysis/src/margin_build/23_final_model/` (`README.md`; `MARGIN_VERIFY_ONLY=1` mode), `data/processed/margin_build/23_final_model/`, `docs/margin-build/SYNTHESIS.md` (§1, §4, §9 kill list, §11), `docs/margin-build/audit/AUDIT_RESPONSE.md`, `M5_street_bias/`, `M3_guide_policy_margin/`, `docs/pitch-forecasts/questions/fy27-sm-share-above-219/`, `bonus-marketing-cut-signalled/`.
Repro: `MARGIN_VERIFY_ONLY=1 python3 analysis/src/margin_build/23_final_model/run.py` (~4 min; writes only `_verify/`; delete it after saving its comparison output to the receipt folder); `40_line_build/run.py` if C1's digger has not already run it this wave (coordinate: never concurrently).
Packages: `analysis/src/margin_build/23_final_model`, `40_line_build`, `M3_guide_policy_margin`, `M5_street_bias` and their data folders.
Conflicts: 3Q26 S&M $781M +33.5% (post-audit) vs $790M +35% (pre-audit); FY27 S&M 21.9–23.5% of revenue vs the Street's implied 21.04%; peer cost elasticity k 0.14 with SE ≈ 0.30 is imprecise, not zero; cash-cost elasticity 0.364; the combination fails its test at h ≥ 2, so FY27 is a spending scenario.

## C6 — Adjusted EBITDA and margin, 3Q26 to FY27 (Opus, wave 2)
Judge: "Pick one FY27 margin. Why 34.6% or 35.7%, and what does the Street's 36.5% require?"
Sources: `23_final_model` outputs (`final-margin__combined`, `combined_dollar_from_margin`), `docs/margin-build/SYNTHESIS.md` §2, §5–§8, §11; `40_line_build/40_annual.csv`; `docs/pitch-forecasts/questions/fy26-margin-sentence/`, `q4-margin-direction-sentence/`, `fy27-margin-guide/`, `risk-q3-margin-sandbagged/`; `analysis/src/margin_build/10_harness_margin/` (read only; never run its scorer); `data/processed/margin_build/20_scoreboard/`.
Repro: `MARGIN_VERIFY_ONLY=1` run if C4's digger has not already saved one this wave (share the receipt; do not run concurrently); recompute 3Q26 margin 49.9% and dollars $2,399M from the committed member scores and weights.
Packages: `analysis/src/margin_build/23_final_model`, `data/processed/margin_build/23_final_model`, `20_scoreboard`.
Conflicts: FY27 34.64% (calibrated run) vs 35.7% (line build) vs 36.45% Street; 3Q26 49.9% (run) vs 50.4% (line build in memo v3); "nothing in this build forecasts the margin ratio better than the Street beyond h=0".

## C7 — SBC, D&A, interest, tax, share count, EPS (Sonnet, wave 3)
Judge: "How do you get from EBITDA to $5.93 and $4.58 of EPS?"
Sources: `analysis/src/margin_build/M7_below_ebitda/` and `data/processed/margin_build/M7_below_ebitda/M7_parameter_sheet.csv`; `40_line_build` (`40_annual.csv`, `40_short_case_summary.csv`, `40_short_case_quarterly.csv`); `data/processed/abnb_capital_return_quarterly.csv` and `analysis/src/capital_return_panel.py`; `analysis/src/abnb_exsbc_stack.py`; `docs/pitch-forecasts/questions/bonus-sbc-step-up/`, `bonus-interest-income-falls/`, `risk-buyback-upsize/`.
Repro: `M7_below_ebitda` run script; `capital_return_panel.py`; recompute EPS from decided C6 and the M7 rules.
Packages: `analysis/src/margin_build/M7_below_ebitda`, `data/processed/margin_build/M7_below_ebitda`, `analysis/src/capital_return_panel.py` outputs.
Conflicts: adjusted EBITDA excludes $1.8bn of FY26 SBC (35% of EBITDA); share count 597m diluted at 16 Sep; buyback renewal at pace is already in the count.

## C8 — FCF and SBC-adjusted FCF (Sonnet, wave 3)
Judge: "What does the stock yield on cash, and is FCF timing or level?"
Sources: `analysis/src/abnb_fcf_bridge.py`, `data/processed/abnb_fcf_bridge.csv`; `abnb_exsbc_stack.py`, `data/processed/abnb_quarterly_cost_stack_exsbc.csv`; grep `research/notes/` for "FCF" and "quality of growth" (the study found FCF misread in timing, ~$106M permanent).
Repro: `python3 analysis/src/abnb_fcf_bridge.py` through the wrapper.
Packages: `data/processed/abnb_fcf_bridge.csv`, `data/processed/abnb_quarterly_cost_stack_exsbc.csv`.
Conflicts: memo says "~3% SBC-adjusted FCF yield, needs 16% FCF growth on a reverse DCF"; tie to V3.

## V1 — Street rows, vendor and date stamped (Sonnet, wave 1)
Judge: "Which consensus, from whom, as of when?"
Sources: `data/processed/forecast_methods/L0/L0_vintage_register.csv` (frozen; read only); `analysis/src/forecast_methods/L0/`, `L0_dolthub_v2/`, `consensus_stamp_v2/`; notes `A1_consensus_vintages.md`, `M_CONSENSUS_2026-09-13.md`, `G1b_dolthub_consensus_history.md`, `LANE2_DATA_CONVENTION_AUDIT.md`, `docs/thesis-kernel-topdown/lane2/CONVENTION.md`; `data/processed/margin_build/03_consensus_pit/`; memo v3 for the Bloomberg MODL aggregates (28 estimates, 148.9m mean, 12 Sep).
Repro: `L0/test_l0.py` (pytest; read-only); `consensus_stamp_v2/run.py` if it is offline-capable (read its README first; no network stamping in this programme).
Packages: `analysis/src/forecast_methods/consensus_stamp_v2`, `L0_dolthub_v2` (read), `data/processed/forecast_methods/consensus_stamp_v2`.
Conflicts: Yahoo = Alpha Vantage = one LSEG-family panel; Zacks Q4 $3,200M vs LSEG $3,158M; never a September value at a historical date; DoltHub quoted externally as Zacks needs a human decision (WP-O G1b); Bloomberg figures enter only as dated aggregates.

## V2 — Exit multiple and the turns-per-point rule (Opus, wave 1)
Judge: "Why 16.5x, and why does one point of growth move the multiple half a turn?"
Sources: `analysis/src/forecast_methods/valuation_v1/` (`run.py` without `--refresh`, `valuation_page.md`, `tests/`); `05_backtests/V_VALUATION_RECONCILIATION.md`, `REFUTE_V_*.md`; `docs/overnight/FINAL_SUMMARY.md`; `research/notes/overnight/` valuation note (12_ or 13_; grep "football"); `data/processed/abnb_valuation_scenarios.csv`, `abnb_valuation_sensitivity.csv`, `abnb_multiples_today.csv`, `abnb_vs_bkng_annual.csv`; `deck/drafts/memo_v0_2026-09-11.md` branch analogues.
Repro: `python3 analysis/src/forecast_methods/valuation_v1/run.py` and its pytest through the wrapper.
Packages: `analysis/src/forecast_methods/valuation_v1`, `data/processed/forecast_methods/valuation_v1`.
Conflicts: fair exit 13.5/16.5/18.5x replaced the old 18/22/25.5x ($248 base was the multiple, not the business); +0.48 turns per point of forward growth is a descriptive regression with four parameters and inherited vintages; memo v3 uses 15.7x Street / 19.0x short-case EV/FY27 EBITDA at $167.51.

## V3 — Reverse DCF, market-implied and management-implied (Sonnet, wave 3)
Judge: "What growth is the price paying for?"
Sources: `analysis/src/reverse_dcf/` (mgmt_implied_*, market, A–E scripts), `data/processed/reverse_dcf/`, `docs/reverse_dcf/`; `model/ABNB_management_implied.xlsx`, `model/ABNB_market_implied.xlsx`; `data/processed/abnb_reverse_dcf.csv`.
Repro: the reverse_dcf run script(s) through the wrapper.
Packages: `analysis/src/reverse_dcf`, `data/processed/reverse_dcf`.
Conflicts: the joint-solve prices in memo v3 ($143 at ~7.5% NTM growth; $150 at 8.6%) come from this package; the short-case price is not in the run and was interpolated.

## V4 — Scenario prices and their probabilities (Opus, wave 3)
Judge: "Where do 26/45/29 and $148 come from, and why is the December median only $166?"
Sources: `docs/pitch-forecasts/questions/scenario-probabilities/` (X01), `close-15dec-2026/` (S02), `day1-move-5nov/` (S01), `close-12feb-2027/` (S03); `docs/pitch-forecasts/SYNTHESIS.md`; `docs/pitch-forecasts/audits/`; `analysis/src/pitch_forecasts/`; `adopted_print_states_v2.json` and `x01_joint.py` (find under the question folders); memo v3 "Scenarios" and "5 Nov disclosure gates".
Repro: `x01_joint.py` and the S02 reaction-function script through the wrapper (they should be deterministic; if seeded Monte Carlo, record the seed).
Packages: `docs/pitch-forecasts/questions/*` (read; write nothing there), `analysis/src/pitch_forecasts`.
Conflicts: print partition 26/45/29 (12-month object) vs disclosure gates 14/17/55/14 (5 Nov object); the −8 to −13% event claim was withdrawn; probability-weighted 15 Dec close $167.3 vs 12-month fundamental $148.

## V5 — The call (Theo and Claude, wave 4)
Judge: "Long or short, target, horizon, and what makes you wrong?"
Sources: the decided V1–V4 lines and the workbook's implied return by scenario; `05_backtests/PREREG_ABNB-INT-v1.md`; `deck/drafts/lane4_v2/review_v2/decision_register.md`; memo v3 recommendation block.
Repro: none; a formula line (`V5 = probability-weighted target / spot − 1`) plus a recorded decision.
Conflicts: WP-H is still `human` on the workboard; START_HERE (15 Sep) records no adopted direction; memo v3 asserts SHORT $143.

## E1 — 5 Nov print partition (Sonnet, wave 3)
Judge: "What is the probability the print accelerates, and on what distribution?"
Sources: `docs/pitch-forecasts/questions/risk-q3-nights-meets-guide/` and `risk-q3-nights-accelerates/` (R01 0.39, R02 0.26); `a09_v2_print_distribution.py` and `adopted_print_states_v2.json` (find under `docs/pitch-forecasts/` or `analysis/src/pitch_forecasts/`); N(9.5, 1.70).
Repro: run `a09_v2_print_distribution.py` through the wrapper; recompute P(<10.0) 0.614, P(10.0–10.6) 0.126, P(≥10.6) 0.260 from N(9.5, 1.70).
Packages: `analysis/src/pitch_forecasts`.
Conflicts: management-delivery constructions give 0.57–0.82 and are published at zero weight; Kalshi mids untraded since 29 Jul.

## E2 — Guide-below-Street, descriptor, FY-sentence probabilities (Opus, wave 2)
Judge: "0.72 that the guide comes in below the Street: below what, and how was it built?"
Sources: `docs/pitch-forecasts/questions/q4-revenue-guide-vs-street/` (C01), `q4-nights-bucket/` (C02), `fy26-margin-sentence/` (C04), `fy26-revenue-guide-language/` (C03), their audits and audit responses under `docs/pitch-forecasts/audits/`; `GD_DECISION_REPORT_v2.md`; `data/processed/overnight/02_guidance_ledger.csv`; `guidance_policy` nights-bucket words.
Repro: the C01 research log's computation (reproduce its P(below) given nights < 10.0 = 0.795 and ≥ 10.6 = 0.567 from its stated inputs) through the wrapper.
Packages: `analysis/src/pitch_forecasts`; question folders read-only.
Conflicts: C01 leans on kernel arithmetic that Willem's GD audit finds loses to a guide-growth baseline at the next guide; the Street mean used ($3,161M, LSEG family) is a revenue consensus, not a guide consensus; 8 of 17 historical descriptors resolve to the "moderate" word.

## E3 — Day-1 and 15 Dec reaction (Opus, wave 3)
Judge: "If you are right on 5 Nov, what does the stock do, and on how many observations?"
Sources: `analysis/src/abnb_guidance_reaction.py`; `data/processed/abnb_guidance_reaction_panel.csv`, `abnb_guidance_reaction_results.csv`, `abnb_earnings_reactions.csv`, `abnb_reaction_regression.csv`, `abnb_reaction_regression_loo.csv`, `abnb_big_moves_7pct.csv`; `analysis/src/big_move_reaction_stats.py`; `analysis/src/forecast_methods/returns_v1/` (23 next-open events); `docs/pitch-forecasts/questions/day1-move-5nov/` (S01), `close-15dec-2026/` (S02); `data/processed/abnb_options_ledger.csv` (event sd 9.0%).
Repro: `python3 analysis/src/abnb_guidance_reaction.py` and `returns_v1/run.py` through the wrapper; the S01 joint draw script.
Packages: `analysis/src/forecast_methods/returns_v1`, `data/processed/forecast_methods/returns_v1`, reaction CSVs above.
Conflicts: the historical "guide below and nights guided lower" cell is n 5 (4 of 5 down, median −10.9%) and is a base rate, not the model; the run's base-case day is median −5.1%, P(≤−8%) 0.37; unconditional day median −2.1%.

## E4 — Flip rules and thresholds (Sonnet, wave 3)
Judge: "What number on 5 Nov makes you cover?"
Sources: `05_backtests/PREREG_ABNB-INT-v1.md`; `D_CARD_ADDENDUM_LAMBDA.md`; `data/processed/forecast_methods/kernel_phi_v2/C5_control_chart_5nov.csv`; `LANE2_LIVE_SCORE_SHEET.md`; memo v3 "5 Nov score sheet" and "Risks" item 1 (flip: nights ≥10.3% with a bundle figure ≥2.5pt); AGENT_BRIEF §4 flip rule (take rate ≥18.10% on GBV ≥$26.3bn and Q4 nights "low double digit").
Repro: recompute the λ thresholds (λ_Q3 < 17.09% warning, < 16.93% escalate, on $27,867M) and the take-rate/GBV pair from the decided R1, D6, D7.
Packages: none to run; read-only.
Conflicts: two flip rules in the record (AGENT_BRIEF §4 vs memo v3 risk 1); D-10's refutation condition was written two incompatible ways.
```

- [ ] **Step 2: Commit**

```bash
git add docs/pitch-model-v2/LINES.md
git commit -q -m "pitch_model_v2: LINES.md registry for the thirty-one digger briefs

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```

---

### Task B1: Wave 1 — H0, D1, D4, D5, R1, R3, C4, V1, V2

**Files:**
- Create: nine dossiers under `docs/pitch-model-v2/dossiers/`, nine receipt folders, first rows of `docs/pitch-model-v2/DECISIONS.md`, `model/pitch_model_v2/spec/lines.yaml` (first version), first workbook.

**Interfaces:**
- Consumes: Track A tools (A1–A7 complete), `LINES.md`, `DIGGER_BRIEF_TEMPLATE.md`.
- Produces: spec entries for H0 (inputs, grade A), D1, D4T (total ADR) and D4X (ex-FX ADR), D5, LAM (R1), CUSH (R3), C4, V1 rows (STREET_REV, STREET_NIGHTS…), V2 (MULT, TURNS).

- [ ] **Step 1: Compose the nine briefs**

For each line: take `DIGGER_BRIEF_TEMPLATE.md`, replace `{ID}`, `{LABEL}`, `{JUDGE_QUESTION}`, `{SOURCES}`, `{REPRO}`, `{PACKAGES}`, `{CONFLICTS}` from the line's block in `LINES.md`, `{COMMIT}` with `git rev-parse --short HEAD`, `{SLUG}` with a short lowercase slug (`h0_history`, `d1_nights_3q26`, `d4_adr`, `d5_fx`, `r1_kernel`, `r3_cushion`, `c4_sales_marketing`, `v1_street`, `v2_multiple`). Save each composed brief to `docs/pitch-model-v2/briefs/<ID>.md` (committed, so the brief that produced each dossier is on record).

- [ ] **Step 2: Launch the diggers in the background, all nine at once**

Agent tool, one call per line, in one message:
- `subagent_type: general-purpose`, `model: opus` for D1, D4, R1, C4, V2; `model: sonnet` for H0, D5, R3, V1.
- `prompt`: the composed brief text verbatim, followed by one line: `Work only inside ~/Citadel-ABNB (and read ~/Citadel-ABNB-untracked). Start by running: cd ~/Citadel-ABNB && git rev-parse --short HEAD`.
- `description`: `Dig <ID> <label>`.
The margin constraint: C4 is the only wave-1 digger allowed to run anything under `analysis/src/margin_build/`.

- [ ] **Step 3: On each completion, gate the dossier**

```bash
cd ~/Citadel-ABNB
PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/dossier_lint.py docs/pitch-model-v2/dossiers/<ID>_<slug>.md
git status --porcelain | grep -vE "^\?\? (docs/pitch-model-v2/dossiers/<ID>_|data/processed/pitch_model_v2/receipts/<ID>/|docs/pitch-model-v2/briefs/)" 
```
Expected: `dossier clean` and an empty second output. If the second output lists anything, the digger wrote outside its lane: `git checkout -- <tracked paths>`, delete stray untracked files, and send the digger a follow-up with SendMessage naming the violation. If the lint fails, send the lint output as a follow-up to the same digger.

- [ ] **Step 4: Bring each line to Theo as a one-screen brief**

Format, in chat, one line per message batch of at most three:
```
<ID> <label> — grade <A|B|C>
Number: <point per scenario and period>
Chain: <three lines from §3>
Strongest failure: <§6 last line>
Kill/consistency: <§7>
Open choices: 1. … (rec: …) 2. …
My recommendation: <value(s), scenario treatment, grade accepted or challenged>
```
Theo decides. Disagreement or a request for depth: SendMessage to the same digger with the exact question; re-brief when it answers.

- [ ] **Step 5: Record each decision**

Append to `docs/pitch-model-v2/DECISIONS.md` one row per (line, period, scenario) with the next `DEC-nnnn`, and add or update the line's entry in `model/pitch_model_v2/spec/lines.yaml` using the input format from Task A2's fixture (values per scenario and period; provenance with dossier, receipt, grade, decision, tolerance). Scenarios in `meta.scenarios` for this programme: `base`, `short`, `breaker`. Periods in `meta.periods`, in order: `1Q23 … 2Q26` (history), `3Q26`, `4Q26`, `1Q27`, `2Q27`, `3Q27`, `4Q27`, `FY26`, `FY27`. H0 supplies every history period as inputs with `grade: A`, `receipt` the H0 receipt, `tolerance` 0.5 for $M lines and 0.01 for percentages.

- [ ] **Step 6: Build, QA, commit**

```bash
cd ~/Citadel-ABNB
PYTHONPATH=analysis/src python3 -m pitch_model_v2.build
PYTHONPATH=analysis/src python3 -m pitch_model_v2.qa --wb model/pitch_model_v2/ABNB_pitch_model_v2.xlsx --spec model/pitch_model_v2/spec/lines.yaml
git add docs/pitch-model-v2 data/processed/pitch_model_v2 model/pitch_model_v2
git commit -q -m "pitch_model_v2: wave 1 — history, nights, ADR, FX, kernel, cushion, S&M, Street, multiple

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
```
Expected: `QA clean`. Open the workbook once in Excel and confirm the Scenario dropdown switches D1_3Q26 between base and short.

---

### Task B2: Wave 2 — D2, D3, D6, D7, R2, R4, R5, C1, C2, C3, C5, C6, E2

Same six steps as B1 with these differences: thirteen briefs, launched in two batches of at most eight (batch 1: D2, D7, R2, R4, C6, E2 on Opus plus C1 and D3 on Sonnet; batch 2: D6, R5, C2, C3, C5 on Sonnet). Within a batch only C1 (batch 1) runs `40_line_build/run.py`; C6 runs `23_final_model` in verify-only mode and no other margin script; C2, C3, C5 recompute from committed `40_params.csv`. Spec additions: D2/D3 extend D1 to 4Q26 and 1Q27–4Q27; D6 is a formula (`D1 * D4T`); D7 a formula for history (`R_actual / D6`) and an input for forecast periods; R2 a formula (`LAM * (2/3*D6[-1] + 1/3*D6[-2])`) with a named alternative line `R2B` for the bridge value as an input; R4 a formula (`R5 / (1 + CUSH)`); R5 an input from bridge v3; C1–C5 inputs per period; C6 a formula (`R5 - C1 - C2 - C3 - C4 - C5 + DA`) with `DA` an input; E2 inputs (probabilities, unit `prob`). Commit message: `pitch_model_v2: wave 2 — revenue, guide, costs, EBITDA, guide probabilities`.

---

### Task B3: Wave 3 — R6, C7, C8, V3, V4, E1, E3, E4

Same six steps. Eight briefs, one batch (R6, V4, E3 on Opus; C7, C8, V3, E1, E4 on Sonnet). Spec additions: R6 inputs by scenario for FY27 quarters; C7 inputs (SBC, DA, INT, TAX, SHARES) and formula `EPS = (C6 - DA - SBC + INT) * (1 - TAX) / SHARES`; C8 formulas from C6 and inputs (capex, working capital); V3 inputs (implied growth); V4 inputs (probabilities per scenario, target per scenario) and formula `PW_TARGET = sum over scenarios`; E1, E3, E4 inputs. Commit message: `pitch_model_v2: wave 3 — FY27, earnings, valuation, event card`.

---

### Task B4: Adversarial review before the call

**Files:**
- Create: `docs/pitch-model-v2/ADVERSARIAL_REVIEW_v1.md`

- [ ] **Step 1: Launch one fresh Opus reviewer**

Agent tool, `model: opus`, prompt:
```
You are an independent reviewer for the ABNB pitch model v2 in ~/Citadel-ABNB (branch theo/pitch-model-v2). You have not seen the dossiers and must not read docs/pitch-model-v2/dossiers/ until step 3.
1. Read model/pitch_model_v2/spec/lines.yaml and docs/pitch-model-v2/DECISIONS.md.
2. Pick the five inputs whose value moves the probability-weighted target the most (use the Evidence tab of model/pitch_model_v2/ABNB_pitch_model_v2.xlsx and the formulas; openpyxl is installed).
3. For each, try to break it: re-run its receipt command through analysis/src/pitch_model_v2/repro.py with --id REVIEW_<ID>, read its dossier, find the strongest counter-evidence in the repo (later audits, kill lists in docs/revenue-forecast-strategy/AGENT_BRIEF.md §6 and docs/margin-build/SYNTHESIS.md §9, refuter notes REFUTE_*.md), and state whether the grade is justified.
4. Write docs/pitch-model-v2/ADVERSARIAL_REVIEW_v1.md: per line, verdict (stands / downgrade to B / downgrade to C / value wrong), the evidence, and the one sentence a judge would use against it. Write nothing else. Do not commit.
```

- [ ] **Step 2: Act on the verdicts with Theo**

Each downgrade or value challenge becomes a decision row (accepted or rejected with reason). Any accepted downgrade to C removes the input from the spec and replaces it with a labelled scenario line or a footnote in the Evidence tab. Rebuild, QA, commit: `pitch_model_v2: adversarial review v1 applied`.

---

### Task B5: Wave 4 — the call, tie-out, closing note, PR

- [ ] **Step 1: Add V5 as a formula and decide the direction**

Spec: `V5 = PW_TARGET / SPOT - 1` with `SPOT` an input from `meta.spot` (grade A, receipt: the price file `data/processed/abnb_daily_close.csv` row for the price date). Open the workbook, read V5 by scenario and probability-weighted. Theo records the direction, target, horizon, and the disconfirming evidence as `DEC-` rows with scenario `all` and line `V5`. The Cover tab gets three cells: `Direction`, `Target`, `Horizon`, each a formula or a named input pointing at the decision.

- [ ] **Step 2: Tie out**

```bash
cd ~/Citadel-ABNB
PYTHONPATH=analysis/src python3 -m pitch_model_v2.tieout
grep -c UNEXPLAINED docs/pitch-model-v2/TIEOUT.md
```
Expected: `0`. Every difference from memo v3 is explained by a decision id, or a `DEC-` row is added saying the memo is wrong and why.

- [ ] **Step 3: Closing note and workboard row**

Create `docs/revenue-forecast-strategy/05_backtests/PITCH_MODEL_v2_BUILD.md` using the AGENT_BRIEF §7 template: verdict, what ran (every receipt command, exit codes, wall times), results (grade table for all lines with n), what failed (every grade C and why), interpretation, harness change requests, RESUME. Append one row to `docs/revenue-forecast-strategy/WORKBOARD.md` (WP `PM2`, status `done`, output the note). Commit.

- [ ] **Step 4: Final build, QA, push, PR**

```bash
cd ~/Citadel-ABNB
PYTHONPATH=analysis/src python3 -m pytest analysis/src/pitch_model_v2/tests -q
PYTHONPATH=analysis/src python3 -m pitch_model_v2.build
PYTHONPATH=analysis/src python3 -m pitch_model_v2.qa --wb model/pitch_model_v2/ABNB_pitch_model_v2.xlsx --spec model/pitch_model_v2/spec/lines.yaml
git push -u origin theo/pitch-model-v2
gh pr create --title "Pitch model v2: reproduced, evidence-carrying submission workbook" --body-file docs/revenue-forecast-strategy/05_backtests/PITCH_MODEL_v2_BUILD.md
```
Expected: tests pass, `QA clean`, PR opened for one teammate's review per `CONTRIBUTING.md`. The PR body ends with `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.

---

## Self-review against the spec

- Spec §3 workspace → A1. §4 line list → B0 (with H0 added; every one of the thirty appears in B1–B3 or B5). §5 dossier contract → A4 template and linter; grade gate enforced in `spec.load`. §6 decision loop → B1 steps 3–5, repeated in B2–B3; reopen rule applies by re-running steps 5–6 for the earlier line. §7 spec and builder → A2, A5, A6 (recalc, QA). §8 orchestration → B1 step 2–3 (models, background, lane check, SendMessage follow-ups). §9 verification → A6 QA, A7 tie-out, B4 adversarial review, B5 closing note and PR. §10 schedule → B1 by 20 Sep, B2 by 24 Sep, B3 by 27 Sep, B4–B5 by 29 Sep.
- Placeholder scan: no TBD/TODO; entry points that name a directory rather than a script are deliberate (the digger reads that package's README, which every package carries per CLAUDE.md).
- Type consistency: `spec.load(path, check_paths=)`, `Spec.order`, `Line.kind/values/expr/provenance`, `to_excel(expr, period, periods)`, `repro.run(id, cmd, watch, timeout, restore, root)`, `dossier_lint.lint(path, root)`, `decisions.load(path) -> Decision(id, line, period, scenario, value, reason, rejected, date)`, `build.build(spec_path, out_path, decisions_path, recalc, check_paths)`, `qa.check(workbook_path, spec_path, root, allow_uncalculated)`, `tieout.write(spec_path, targets_csv, decisions_path, out_md, check_paths)` are used with the same names in every task.
