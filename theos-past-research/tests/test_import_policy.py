from pathlib import Path

from abnb_alt_data.import_policy import MAX_BYTES, collect_violations


def write_file(path: Path, content: bytes = b"x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def test_collect_violations_rejects_prohibited_asset_classes(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    safe = write_file(project_root / "research/source_registry.csv")
    pdf = write_file(project_root / "EARNING-TRANSCRIPTS/example.pdf")
    transcript = write_file(
        project_root / "data/licensed/earnings_transcripts/clean_md/example.md"
    )
    parquet = write_file(project_root / "results.parquet")
    cache = write_file(project_root / ".venv/token.txt")

    violations = collect_violations(project_root, [safe, pdf, transcript, parquet, cache])

    assert len(violations) == 4
    assert not any("source_registry.csv" in violation for violation in violations)


def test_collect_violations_rejects_files_over_50_mib(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    oversized = project_root / "large.bin"
    oversized.parent.mkdir(parents=True)
    oversized.touch()
    oversized.write_bytes(b"x")
    with oversized.open("r+b") as handle:
        handle.truncate(MAX_BYTES + 1)

    assert any("50 MiB" in violation for violation in collect_violations(project_root, [oversized]))


def test_collect_violations_rejects_absolute_local_paths(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    unix_path = write_file(
        project_root / "unix.md",
        ("/" + "Users/" + "someone/file").encode(),
    )
    windows_path = write_file(
        project_root / "windows.txt",
        ("C:" + "\\Users\\" + "someone\\file").encode(),
    )
    local_interpreter = write_file(
        project_root / "validation_log.md",
        ("/" + "opt/anaconda3/bin/python").encode(),
    )

    violations = collect_violations(project_root, [unix_path, windows_path, local_interpreter])

    assert len(violations) == 3
    assert all("absolute local path" in violation for violation in violations)


def test_collect_violations_rejects_nonblank_secret_assignments(tmp_path: Path) -> None:
    project_root = tmp_path / "project"
    secret = write_file(
        project_root / "settings.toml",
        ("API_" + "KEY" + "=real-value\n").encode(),
    )
    template = write_file(
        project_root / ".env.example",
        ("API_" + "KEY" + "=real-value\n").encode(),
    )

    violations = collect_violations(project_root, [secret, template])

    assert len(violations) == 1
    assert "settings.toml" in violations[0]
