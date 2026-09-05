from pathlib import Path
import subprocess
import tomllib
import io
import json
import os
import tarfile
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
REACTION_GENERATOR = (
    ROOT
    / "outputs"
    / "reproducibility"
    / "us-europe-guidance"
    / "build_abnb_edge_guidance_reaction.mjs"
)
PORTABLE_ARTIFACT_GENERATORS = (
    ROOT
    / "research/forecasting/runs/20260903T224632Z_50_source_guidance_format/build_workbook.mjs",
    ROOT
    / "research/forecasting/runs/20260903T233712Z_us_europe_guidance_comparison/build_workbook.mjs",
    ROOT
    / "research/edge-discovery/20260903T062839Z_abnb_edge_discovery/supply_scarcity_web_edge/e1_disposition/build_postfreeze_replay.mjs",
)


def is_ignored(relative_path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "-q", relative_path],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 0


def test_proprietary_transcripts_are_ignored() -> None:
    assert is_ignored("EARNING-TRANSCRIPTS/example.pdf")
    assert is_ignored("data/licensed/earnings_transcripts/clean_md/example.md")


def test_research_metadata_is_trackable() -> None:
    assert not is_ignored("research/transcripts/transcript_index.csv")
    assert not is_ignored("research/transcripts/guidance_facts.csv")


def test_local_environment_secrets_are_ignored_but_template_is_trackable() -> None:
    assert is_ignored(".env")
    assert is_ignored(".env.local")
    assert is_ignored(".env.production")
    assert not is_ignored(".env.example")


def test_raw_and_build_outputs_are_ignored_but_review_artifacts_are_trackable() -> None:
    for path in (
        "outputs/global-lodging-map/raw/inside-airbnb/london.csv",
        "outputs/reproducibility/us-europe-guidance/previews/summary.png",
        "outputs/reproducibility/us-europe-guidance/abnb_nasdaq_history.json",
        "outputs/reproducibility/us-europe-guidance/spy_nasdaq_history.json",
        "research/edge-discovery/20260903T211121Z_50_source_expansion/processed/new_observations.csv",
        "results.parquet",
        "source-payload.zip",
        "report.aux",
        "report.fdb_latexmk",
        "report.fls",
        "report.log",
        "report.out",
    ):
        assert is_ignored(path)

    for path in (
        "research/provenance/omitted-data-manifest.csv",
        "research/provenance/restricted-data-manifest.csv",
        "outputs/reports/abnb_macro_to_equity_ic_brief.pdf",
        "outputs/workbooks/abnb_us_europe_guidance_comparison.xlsx",
    ):
        assert not is_ignored(path)


def test_review_workbooks_contain_no_machine_local_paths() -> None:
    workbook_dir = ROOT / "outputs/workbooks"
    unix_markers = tuple(
        "/" + prefix for prefix in ("Users/", "private/", "home/", "opt/")
    )
    windows_marker = "C:" + "\\" + "Users" + "\\"

    for workbook_path in sorted(workbook_dir.glob("*.xlsx")):
        with ZipFile(workbook_path) as archive:
            xml_text = "\n".join(
                archive.read(member.filename).decode("utf-8", errors="replace")
                for member in archive.infolist()
                if member.filename.endswith((".xml", ".rels"))
            )
        assert not any(marker in xml_text for marker in unix_markers), workbook_path.name
        assert windows_marker not in xml_text, workbook_path.name


def test_synthetic_transcript_fixture_is_tracked_and_archived() -> None:
    relative = "tests/fixtures/synthetic_callstreet_layout.txt"
    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", relative],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    archived = subprocess.run(
        ["git", "archive", "--format=tar", "HEAD", relative],
        cwd=ROOT,
        check=False,
        capture_output=True,
    )

    assert tracked.returncode == 0, tracked.stderr
    assert archived.returncode == 0, archived.stderr.decode(errors="replace")


def test_required_research_snapshots_are_present() -> None:
    required = (
        "research/edge-discovery/20260903T211121Z_50_source_expansion/build_50_source_panel.py",
        "research/edge-discovery/20260903T211121Z_50_source_expansion/verify_50_source_panel.py",
        "research/edge-discovery/20260903T211121Z_50_source_expansion/processed/new_source_manifest.csv",
        "research/readiness/20260903T053309Z_abnb_readiness/target_panel.csv",
        "research/forecasting/runs/20260903T224632Z_50_source_guidance_format/build_guidance_inputs.py",
        "research/forecasting/runs/20260903T224632Z_50_source_guidance_format/guidance_history.csv",
        "research/forecasting/runs/20260903T233712Z_us_europe_guidance_comparison/build_analysis.py",
        "research/forecasting/runs/20260903T233712Z_us_europe_guidance_comparison/guidance_enriched.csv",
        "research/provenance/source-boundary-inventory.csv",
    )

    assert [relative for relative in required if not (ROOT / relative).is_file()] == []


def source_rows_block(source: str) -> str:
    start = source.index("const sourceRows = [")
    end = source.index("\nsources.getRange(", start)
    return source[start:end]


def reaction_generator_policy_violations(source: str) -> list[str]:
    violations: list[str] = []
    canonical_output = (
        'const canonicalOutputPath = path.join(workspace, "outputs", "workbooks", '
        '"ABNB_edge_guidance_stock_reaction.xlsx");'
    )
    if canonical_output not in source:
        violations.append("generator output is not the canonical review workbook")
    if "await xlsx.save(outputPath);" not in source:
        violations.append("XLSX save does not use the canonical outputPath")

    rows = source_rows_block(source)
    for source_id, logical_name, resolved_name in (
        ("GUIDANCE_PANEL", "guidance", "guidance"),
        ("TRANSCRIPT_INDEX", "transcriptIndex", "transcriptIndex"),
        ("HYPOTHESIS_LEDGER", "hypothesisLedger", "hypothesisLedger"),
    ):
        row_start = rows.index(f'["{source_id}"')
        row_end = rows.index("],", row_start) + 2
        row = rows[row_start:row_end]
        if f"logicalSourcePaths.{logical_name}" not in row:
            violations.append(f"{source_id} source row is not logical")
        if f"paths.{resolved_name}" in row:
            violations.append(f"{source_id} source row uses a resolved path")
    return violations


def test_reaction_generator_uses_tracked_output_and_logical_source_paths() -> None:
    source = REACTION_GENERATOR.read_text(encoding="utf-8")
    unix_marker = "/" + "Users/"
    windows_marker = "C:" + "\\" + "Users" + "\\"

    assert reaction_generator_policy_violations(source) == []
    assert unix_marker not in source
    assert windows_marker not in source


def test_workbook_runtime_is_exactly_pinned() -> None:
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))

    assert package["engines"]["node"] == "24.19.0"
    assert package["peerDependencies"]["@oai/artifact-tool"] == "2.8.59"
    assert package["peerDependenciesMeta"]["@oai/artifact-tool"]["optional"] is True
    assert package["workbookRuntimeDependencies"]["@oai/artifact-tool"]["version"] == "2.8.59"
    assert (ROOT / ".node-version").read_text(encoding="utf-8").strip() == "24.19.0"


def test_all_artifact_generators_use_the_portable_pinned_runtime() -> None:
    for generator in (REACTION_GENERATOR, *PORTABLE_ARTIFACT_GENERATORS):
        source = generator.read_text(encoding="utf-8")

        assert 'from "@oai/artifact-tool"' not in source, generator
        assert "loadArtifactTool" in source, generator
        assert "process.cwd()" not in source, generator


def test_reaction_generator_executes_from_clean_archive(tmp_path: Path) -> None:
    archive = subprocess.run(
        ["git", "archive", "--format=tar", "HEAD", "theos-past-research"],
        cwd=ROOT.parent,
        check=True,
        capture_output=True,
    )
    archive_root = tmp_path / "archive"
    archive_root.mkdir()
    with tarfile.open(fileobj=io.BytesIO(archive.stdout), mode="r:") as bundle:
        bundle.extractall(archive_root, filter="data")
    clean_root = archive_root / "theos-past-research"

    bundled_node = (
        Path.home()
        / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
    )
    node = bundled_node if bundled_node.is_file() else Path("node")
    bundled_artifact_tool = (
        Path.home()
        / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules"
        / "@oai/artifact-tool"
    )
    assert bundled_artifact_tool.is_dir()
    clean_env = os.environ.copy()
    clean_env["ARTIFACT_TOOL_PACKAGE_ROOT"] = str(bundled_artifact_tool)
    output = tmp_path / "generated.xlsx"
    generator = (
        clean_root
        / "outputs/reproducibility/us-europe-guidance/build_abnb_edge_guidance_reaction.mjs"
    )
    result = subprocess.run(
        [str(node), str(generator), "--output", str(output), "--skip-previews"],
        cwd=clean_root,
        check=False,
        capture_output=True,
        text=True,
        env=clean_env,
        timeout=120,
    )

    assert result.returncode == 0, result.stderr
    assert output.is_file()
    with ZipFile(output) as workbook:
        names = workbook.namelist()
        xml_text = "\n".join(
            workbook.read(name).decode("utf-8", errors="replace")
            for name in names
            if name.endswith((".xml", ".rels"))
        )
    assert "[Content_Types].xml" in names
    assert len([name for name in names if name.startswith("xl/worksheets/sheet")]) == 9
    local_markers = tuple(
        "/" + prefix for prefix in ("Users/", "private/", "home/", "opt/")
    )
    assert not any(marker in xml_text for marker in local_markers)


def test_reaction_generator_policy_check_rejects_unsafe_mutations() -> None:
    source = REACTION_GENERATOR.read_text(encoding="utf-8")
    rows = source_rows_block(source)
    unsafe_rows = rows.replace("logicalSourcePaths.guidance", "paths.guidance", 1)
    unsafe_source = source.replace(rows, unsafe_rows).replace(
        "await xlsx.save(outputPath);", "await xlsx.save(previewDir);"
    )

    violations = reaction_generator_policy_violations(unsafe_source)

    assert "XLSX save does not use the canonical outputPath" in violations
    assert "GUIDANCE_PANEL source row is not logical" in violations
    assert "GUIDANCE_PANEL source row uses a resolved path" in violations


def test_active_docs_name_normalized_outputs_and_validation_modes() -> None:
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    data_readme = (ROOT / "data/README.md").read_text(encoding="utf-8")
    brief_readme = (ROOT / "docs/forecasting/abnb_ic_brief/README.md").read_text(
        encoding="utf-8"
    )
    public_command = (
        "python scripts/validate_project.py --root . --expected-transcripts 23 "
        "--metadata-only"
    )

    for document in (root_readme, data_readme, brief_readme):
        assert public_command in document
        assert "--private-checksums" in document
        assert "--private-input-root" in document

    assert "output/pdf" not in brief_readme
    assert "outputs/reports/abnb_macro_to_equity_ic_brief.pdf" in brief_readme
    assert "outputs/workbooks/ABNB_edge_guidance_stock_reaction.xlsx" in brief_readme
    assert "outputs/reproducibility/us-europe-guidance" in brief_readme


def test_portable_workbook_build_is_fully_documented() -> None:
    readme = (
        ROOT / "outputs/reproducibility/us-europe-guidance/README.md"
    ).read_text(encoding="utf-8")

    assert ".node-version" in readme
    assert "Node 24.19.0" in readme
    assert "@oai/artifact-tool 2.8.59" in readme
    assert "ARTIFACT_TOOL_PACKAGE_ROOT" in readme
    assert "ABNB_WORKSPACE_NODE" in readme
    assert "nasdaq_public_market_history.csv" in readme
    assert "--skip-previews" in readme


def test_scraping_extra_declares_scrapling() -> None:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]

    assert any(
        dependency.startswith("scrapling>=")
        for dependency in project["optional-dependencies"]["scraping"]
    )
