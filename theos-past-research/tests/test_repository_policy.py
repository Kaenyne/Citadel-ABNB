from pathlib import Path
import subprocess
import tomllib
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
REACTION_GENERATOR = (
    ROOT
    / "outputs"
    / "reproducibility"
    / "us-europe-guidance"
    / "build_abnb_edge_guidance_reaction.mjs"
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
    unix_marker = "/" + "Users/"
    windows_marker = "C:" + "\\" + "Users" + "\\"

    for workbook_path in sorted(workbook_dir.glob("*.xlsx")):
        with ZipFile(workbook_path) as archive:
            xml_text = "\n".join(
                archive.read(member.filename).decode("utf-8", errors="replace")
                for member in archive.infolist()
                if member.filename.endswith((".xml", ".rels"))
            )
        assert unix_marker not in xml_text, workbook_path.name
        assert windows_marker not in xml_text, workbook_path.name


def source_rows_block(source: str) -> str:
    start = source.index("const sourceRows = [")
    end = source.index("\nsources.getRange(", start)
    return source[start:end]


def reaction_generator_policy_violations(source: str) -> list[str]:
    violations: list[str] = []
    canonical_output = (
        'const outputPath = path.join(workspace, "outputs", "workbooks", '
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


def test_scraping_extra_declares_scrapling() -> None:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]

    assert any(
        dependency.startswith("scrapling>=")
        for dependency in project["optional-dependencies"]["scraping"]
    )
