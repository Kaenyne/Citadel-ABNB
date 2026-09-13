"""Protect the append-only boundary using isolated temporary registers."""
from __future__ import annotations

import csv
import importlib.util
import io
import json
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("consensus_stamp_v2_run", Path(__file__).with_name("run.py"))
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


@pytest.fixture
def append_case(tmp_path, monkeypatch):
    fields = "register_id,vendor,period,metric,value,unit,n_estimates,as_of_timestamp,url,source_path,role,pit_usable,vendor_attributed,note".split(",")
    old_row = dict(zip(fields, ["PG-2026Q3-revenue", "LSEG", "2026Q3", "revenue", "4610", "musd", "", "2026-08-06", "https://example.com", "source.json", "pre_guide", "True", "True", "protected"]))
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fields, lineterminator="\r\n")
    writer.writeheader()
    writer.writerow(old_row)
    original = b"# Original comment\r\n" + buffer.getvalue().encode()
    register, backup = tmp_path / "register.csv", tmp_path / "backup.csv"
    register.write_bytes(original)
    backup.write_bytes(original)
    (tmp_path / "source.json").write_text("{}")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "OUT", tmp_path / "output")
    monkeypatch.setattr(module, "REGISTER", register)
    candidate = dict(old_row, register_id="current-1", vendor="Yahoo Finance", role="current", pit_usable=True, vendor_attributed=True,
                     as_of_timestamp=module.utc()[:16] + "Z", n_estimates=36, value=4744.88, capture_method="public capture")
    return tmp_path, register, backup, original, candidate


def invoke(case, rows):
    root, _, backup, _, _ = case
    candidates = root / "candidates.json"
    candidates.write_text(json.dumps(rows))
    module.append(candidates, backup)


def test_byte_prefix_and_protected_row_are_preserved(append_case):
    _, register, _, original, candidate = append_case
    invoke(append_case, [candidate])
    assert register.read_bytes().startswith(original)
    assert len(module.read_register(register.read_bytes())) == 2
    module.verify()


def test_stale_backup_rejected_without_writing(append_case):
    _, register, _, original, candidate = append_case
    changed = original + b"# Concurrent change\n"
    register.write_bytes(changed)
    with pytest.raises(ValueError, match="differs from backup"):
        invoke(append_case, [candidate])
    assert register.read_bytes() == changed


def test_git_line_ending_normalization_is_explicit(append_case, capsys):
    _, register, backup, _, candidate = append_case
    invoke(append_case, [candidate])
    register.write_bytes(register.read_bytes().replace(b"\r\n", b"\n"))
    backup.write_bytes(backup.read_bytes().replace(b"\r\n", b"\n"))
    module.verify()
    assert '"rebuild_encoding_mode": "git_text_normalized"' in capsys.readouterr().out


@pytest.mark.parametrize("changes", [{"n_estimates": 0}, {"n_estimates": None}, {"as_of_timestamp": "2026-08-06T12:00Z"}, {"source_path": "missing.json"}])
def test_invalid_candidate_never_partially_appends(append_case, changes):
    _, register, _, original, candidate = append_case
    invalid = dict(candidate, register_id="invalid-2", **changes)
    with pytest.raises((ValueError, TypeError)):
        invoke(append_case, [candidate, invalid])
    assert register.read_bytes() == original


def test_duplicate_id_never_partially_appends(append_case):
    _, register, _, original, candidate = append_case
    with pytest.raises(ValueError, match="Duplicate"):
        invoke(append_case, [candidate, candidate])
    assert register.read_bytes() == original
