import subprocess
from pitch_model_v2 import recalc as rc

def test_recalc_returns_false_on_timeout(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(rc, "_excel_available", lambda: True)

    def _raise(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="osascript", timeout=300)

    monkeypatch.setattr(rc.subprocess, "run", _raise)
    assert rc.recalc(tmp_path / "m.xlsx") is False
    assert "timed out" in capsys.readouterr().out
