from pathlib import Path
import subprocess
import tomllib


ROOT = Path(__file__).resolve().parents[1]


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


def test_scraping_extra_declares_scrapling() -> None:
    with (ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]

    assert any(
        dependency.startswith("scrapling>=")
        for dependency in project["optional-dependencies"]["scraping"]
    )
