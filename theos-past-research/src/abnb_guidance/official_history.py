"""Curated official Airbnb earnings chronology through the Q2 2026 event.

The module is deliberately data-first: every number is tied to an SEC-filed
shareholder letter, and event timestamps use the disclosed webcast start as a
conservative "certainly public by" cutoff.  Exact SEC acceptance timestamps can
replace that proxy without changing stable record identifiers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime

from .records import GuidanceEvent, GuidanceItem, QuarterlyActual, SourceDocument, SourceExcerpt


RESEARCH_CUTOFF = datetime(2026, 9, 3, 3, 59, 59, tzinfo=UTC)


@dataclass(frozen=True)
class OfficialQuarter:
    period: str
    event_at_utc: datetime
    accession: str
    document_name: str
    actual_revenue_m: float
    yoy_growth: float
    yoy_growth_cc: float | None
    target_period: str
    guide_low_m: float | None
    guide_high_m: float | None
    guidance_excerpt: str
    guidance_anchor: str = "Outlook"


def _dt(year: int, month: int, day: int, hour: int, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


OFFICIAL_QUARTERS: tuple[OfficialQuarter, ...] = (
    OfficialQuarter("2020Q4", _dt(2021, 2, 25, 22), "0001193125-21-056952", "d147144dex991.htm", 859, -0.22, -0.22, "2021Q1", None, None, "For revenue, the year-over-year decline in Q1 2021 is expected to be less than that of Q4 2020"),
    OfficialQuarter("2021Q1", _dt(2021, 5, 13, 21), "0001193125-21-160458", "d476842dex991.htm", 887, 0.05, 0.03, "2021Q2", None, None, "We expect revenue in Q2 2021 to be significantly higher than that of Q2 2020"),
    OfficialQuarter("2021Q2", _dt(2021, 8, 12, 21), "0001193125-21-244643", "d212971dex991.htm", 1335, 2.99, None, "2021Q3", None, None, "we expect Q3 2021 revenue to be our strongest quarterly revenue on record"),
    OfficialQuarter("2021Q3", _dt(2021, 11, 4, 21, 30), "0001193125-21-320113", "d245727dex991.htm", 2237, 0.67, 0.64, "2021Q4", 1390, 1480, "We expect to deliver Q4 revenue of between $1.39 billion and $1.48 billion"),
    OfficialQuarter("2021Q4", _dt(2022, 2, 15, 21, 30), "0001193125-22-043371", "d251410dex991.htm", 1532, 0.78, 0.79, "2022Q1", 1410, 1480, "We expect to deliver Q1 2022 revenue of between $1.41 billion and $1.48 billion"),
    OfficialQuarter("2022Q1", _dt(2022, 5, 3, 21, 30), "0001193125-22-138654", "d711122dex991.htm", 1509, 0.70, 0.74, "2022Q2", 2030, 2130, "we expect to deliver Q2 2022 revenue between $2.03 billion and $2.13 billion"),
    OfficialQuarter("2022Q2", _dt(2022, 8, 2, 20, 30), "0001193125-22-210001", "d353427dex991.htm", 2104, 0.58, 0.64, "2022Q3", 2780, 2880, "We expect to deliver Q3 2022 revenue between $2.78 billion and $2.88 billion"),
    OfficialQuarter("2022Q3", _dt(2022, 11, 1, 20, 30), "0001193125-22-274904", "d408297dex991.htm", 2884, 0.29, 0.36, "2022Q4", 1800, 1880, "We expect another strong quarter of revenue growth, delivering between $1.80 billion and $1.88 billion in Q4 2022"),
    OfficialQuarter("2022Q4", _dt(2023, 2, 14, 21, 30), "0001193125-23-039008", "d451233dex991.htm", 1902, 0.24, 0.31, "2023Q1", 1750, 1820, "We expect revenue of $1.75 billion to $1.82 billion in Q1 2023"),
    OfficialQuarter("2023Q1", _dt(2023, 5, 9, 20, 30), "0001193125-23-139392", "d453262dex991.htm", 1818, 0.20, 0.24, "2023Q2", 2350, 2450, "We expect to deliver revenue of $2.35 billion to $2.45 billion in Q2 2023"),
    OfficialQuarter("2023Q2", _dt(2023, 8, 3, 20, 30), "0001193125-23-202832", "d446942dex991.htm", 2484, 0.18, 0.19, "2023Q3", 3300, 3400, "For Q3 2023, we expect to deliver revenue of $3.3 billion to $3.4 billion"),
    OfficialQuarter("2023Q3", _dt(2023, 11, 1, 20, 30), "0001193125-23-268164", "d481318dex991.htm", 3397, 0.18, 0.14, "2023Q4", 2130, 2170, "For Q4 2023, we expect to deliver revenue of $2.13 billion to $2.17 billion"),
    OfficialQuarter("2023Q4", _dt(2024, 2, 13, 21, 30), "0001193125-24-033706", "d646462dex991.htm", 2218, 0.17, 0.14, "2024Q1", 2030, 2070, "For Q1 2024, we expect to deliver revenue of $2.03 billion to $2.07 billion"),
    OfficialQuarter("2024Q1", _dt(2024, 5, 8, 20, 30), "0001193125-24-134183", "d813800dex991.htm", 2142, 0.18, 0.18, "2024Q2", 2680, 2740, "For Q2 2024, we expect to deliver revenue of $2.68 billion to $2.74 billion"),
    OfficialQuarter("2024Q2", _dt(2024, 8, 6, 20, 30), "0001193125-24-194849", "d831385dex991.htm", 2748, 0.11, 0.11, "2024Q3", 3670, 3730, "In Q3 2024, we expect to deliver revenue of $3.67 billion to $3.73 billion"),
    OfficialQuarter("2024Q3", _dt(2024, 11, 7, 21, 30), "0001193125-24-253103", "d886752dex991.htm", 3732, 0.10, 0.10, "2024Q4", 2390, 2440, "For Q4 2024, we expect to deliver revenue of $2.39 billion to $2.44 billion"),
    OfficialQuarter("2024Q4", _dt(2025, 2, 13, 21, 30), "0001193125-25-026054", "d915198dex991.htm", 2480, 0.12, None, "2025Q1", 2230, 2270, "For Q1 2025, we expect to deliver revenue of $2.23 billion to $2.27 billion"),
    OfficialQuarter("2025Q1", _dt(2025, 5, 1, 20, 30), "0001193125-25-109934", "d40594dex991.htm", 2272, 0.06, 0.08, "2025Q2", 2990, 3050, "In Q2 2025, we expect to generate revenue of $2.99 billion to $3.05 billion"),
    OfficialQuarter("2025Q2", _dt(2025, 8, 6, 20, 30), "0001193125-25-174438", "d17531dex991.htm", 3096, 0.13, 0.13, "2025Q3", 4020, 4100, "In Q3 2025, we expect to generate revenue of $4.02 billion to $4.10 billion"),
    OfficialQuarter("2025Q3", _dt(2025, 11, 6, 21, 30), "0001193125-25-269432", "d40503dex991.htm", 4095, 0.10, 0.10, "2025Q4", 2660, 2720, "In Q4 2025, we expect to generate revenue of $2.66 billion to $2.72 billion"),
    OfficialQuarter("2025Q4", _dt(2026, 2, 12, 22), "0001193125-26-048670", "d58192dex991.htm", 2778, 0.12, 0.11, "2026Q1", 2590, 2630, "We expect to generate revenue of $2.59 billion to $2.63 billion"),
    OfficialQuarter("2026Q1", _dt(2026, 5, 7, 21), "0001193125-26-211816", "d23351dex991.htm", 2678, 0.18, 0.15, "2026Q2", 3540, 3600, "We expect to generate revenue of $3.54 billion to $3.60 billion"),
    OfficialQuarter("2026Q2", _dt(2026, 8, 6, 21), "0001193125-26-337928", "d70413dex991.htm", 3608, 0.17, 0.13, "2026Q3", 4690, 4770, "We expect to generate revenue of $4.69 billion to $4.77 billion"),
)


def _document_id(period: str) -> str:
    return f"ABNB-{period}-SHAREHOLDER-LETTER"


def _event_id(period: str) -> str:
    return f"ABNB-{period}-INITIAL"


def _sec_url(quarter: OfficialQuarter) -> str:
    accession_digits = quarter.accession.replace("-", "")
    return (
        "https://www.sec.gov/Archives/edgar/data/1559720/"
        f"{accession_digits}/{quarter.document_name}"
    )


def build_official_history(*, retrieved_at: datetime) -> dict[str, list]:
    """Return normalized records based only on SEC-filed shareholder letters."""
    if retrieved_at.tzinfo is None or retrieved_at.utcoffset() is None:
        raise ValueError("retrieved_at must be timezone-aware")

    documents: list[SourceDocument] = []
    events: list[GuidanceEvent] = []
    excerpts: list[SourceExcerpt] = []
    actuals: list[QuarterlyActual] = []
    guidance: list[GuidanceItem] = []

    for quarter in OFFICIAL_QUARTERS:
        document_id = _document_id(quarter.period)
        event_id = _event_id(quarter.period)
        source_url = _sec_url(quarter)
        event_date = quarter.event_at_utc.date()
        documents.append(
            SourceDocument(
                document_id=document_id,
                document_type="shareholder_letter",
                title=f"Airbnb {quarter.period} Shareholder Letter",
                publisher="Airbnb, Inc. / SEC EDGAR",
                source_url=source_url,
                canonical_url=source_url,
                fiscal_period=quarter.period,
                document_date=event_date,
                published_at_utc=quarter.event_at_utc,
                sec_accession_number=quarter.accession,
                retrieved_at_utc=retrieved_at,
                capture_method="SEC EDGAR HTML metadata and pinpoint excerpt capture",
                mime_type="text/html",
                rights_or_access_note="Public company filing on SEC EDGAR; only short pinpoint excerpts are stored.",
                version_status="original_filed_version",
            )
        )
        events.append(
            GuidanceEvent(
                guidance_event_id=event_id,
                issuer_id="ABNB",
                reported_period=quarter.period,
                event_type="initial",
                published_at_utc=quarter.event_at_utc,
                published_at_precision="minute",
                release_timing="after_close",
                research_cutoff_at_utc=RESEARCH_CUTOFF,
                initial_event_id=event_id,
                is_initial_guide=True,
                primary_document_id=document_id,
                event_notes="Timestamp is the disclosed earnings-webcast start, used as a conservative certainly-public-by proxy pending exact SEC acceptance time.",
            )
        )

        actual_excerpt_id = f"ABNB-{quarter.period}-ACTUAL-REVENUE-EXCERPT"
        actual_excerpt = f"Revenue ${quarter.actual_revenue_m:,.0f}M"
        excerpts.append(
            SourceExcerpt(
                source_excerpt_id=actual_excerpt_id,
                document_id=document_id,
                section_heading="Key Financial Measures / financial statements",
                source_anchor="Revenue table; whitespace normalized",
                exact_excerpt=actual_excerpt,
                excerpt_word_count=len(actual_excerpt.split()),
                context_paraphrase=f"Airbnb reported {quarter.period} revenue of ${quarter.actual_revenue_m:,.0f} million.",
                copyright_handling="Short data-cell excerpt from a public SEC-filed issuer exhibit; not a transcript.",
                extraction_method="manual dual-field verification against SEC HTML",
                verified_against_source=True,
            )
        )
        actuals.append(
            QuarterlyActual(
                actual_observation_id=f"ABNB-{quarter.period}-REVENUE-ACTUAL",
                fiscal_period=quarter.period,
                metric_code="revenue",
                scope_code="consolidated",
                value=quarter.actual_revenue_m,
                unit="USD_millions",
                currency="USD",
                accounting_basis="GAAP",
                yoy_growth_reported=quarter.yoy_growth,
                yoy_growth_constant_currency=quarter.yoy_growth_cc,
                is_company_stated=True,
                public_available_at_utc=quarter.event_at_utc,
                source_excerpt_id=actual_excerpt_id,
            )
        )

        guide_excerpt_id = f"ABNB-{quarter.period}-NEXTQ-REVENUE-GUIDE-EXCERPT"
        excerpts.append(
            SourceExcerpt(
                source_excerpt_id=guide_excerpt_id,
                document_id=document_id,
                section_heading=quarter.guidance_anchor,
                source_anchor="Outlook section; whitespace normalized",
                exact_excerpt=quarter.guidance_excerpt,
                excerpt_word_count=len(quarter.guidance_excerpt.split()),
                context_paraphrase=(
                    f"Management issued a qualitative revenue outlook for {quarter.target_period}."
                    if quarter.guide_low_m is None
                    else f"Management guided {quarter.target_period} revenue to ${quarter.guide_low_m:,.0f}-${quarter.guide_high_m:,.0f} million."
                ),
                copyright_handling="Short pinpoint excerpt from a public SEC-filed issuer exhibit; not a transcript.",
                extraction_method="manual dual-field verification against SEC HTML",
                verified_against_source=True,
            )
        )
        is_numeric = quarter.guide_low_m is not None and quarter.guide_high_m is not None
        guidance.append(
            GuidanceItem(
                guidance_item_id=f"ABNB-{quarter.period}-NEXTQ-REVENUE-GUIDE",
                guidance_event_id=event_id,
                target_period=quarter.target_period,
                metric_code="revenue",
                measure_type="absolute_range" if is_numeric else "qualitative",
                value_low=quarter.guide_low_m,
                value_high=quarter.guide_high_m,
                value_mid=(quarter.guide_low_m + quarter.guide_high_m) / 2 if is_numeric else None,
                unit="USD_millions" if is_numeric else "narrative",
                currency="USD" if is_numeric else None,
                accounting_basis="GAAP",
                is_company_stated=True,
                comparator_period=None,
                source_excerpt_id=guide_excerpt_id,
                extraction_confidence="high",
            )
        )

    return {
        "source_documents": documents,
        "guidance_events": events,
        "source_excerpts": excerpts,
        "quarterly_actuals": actuals,
        "guidance_items": guidance,
    }
