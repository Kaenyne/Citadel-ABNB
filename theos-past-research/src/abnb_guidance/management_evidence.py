"""Curated, cited management signals disclosed at the guidance date."""

from __future__ import annotations

from dataclasses import dataclass

from .records import (
    DriverObservation,
    EvidenceClaim,
    GuidanceEvent,
    GuidanceItem,
    SourceDocument,
    SourceExcerpt,
)


DRIVER_FAMILIES = {
    "nights_booked_yoy": "demand_volume",
    "forward_booking_momentum": "demand_volume",
    "gbv_yoy": "booking_economics",
    "adr_yoy": "booking_economics",
    "take_rate": "booking_economics",
    "fee_structure_change": "booking_economics",
    "regional_mix": "mix",
    "cross_border_growth": "mix",
    "urban_mix": "mix",
    "booking_lead_time": "booking_behavior",
    "cancellation_rate": "booking_behavior",
    "bookings_on_books": "booking_behavior",
    "demand_volatility": "booking_behavior",
    "active_listings_yoy": "supply",
    "marketing_expense": "commercial_activity",
    "product_investment_intensity": "commercial_activity",
    "fx_revenue_impact": "external_conditions",
    "consumer_confidence_change": "external_conditions",
    "regulatory_pressure": "external_conditions",
    "target_quarter": "calendar_effects",
    "easter_shift": "calendar_effects",
    "leap_year": "calendar_effects",
    "major_holiday_shift": "calendar_effects",
}


@dataclass(frozen=True)
class Signal:
    code: str
    value: float
    category: str
    direction: str
    strength: str = "contributor"
    stance: str = "supporting"


@dataclass(frozen=True)
class EvidenceExcerpt:
    period: str
    text: str
    signals: tuple[Signal, ...]
    anchor: str = "Outlook"


EVIDENCE_EXCERPTS: tuple[EvidenceExcerpt, ...] = (
    EvidenceExcerpt("2020Q4", "Due to typical seasonal patterns, our revenue is usually the lowest in Q1", (Signal("target_quarter", -1, "Q1 seasonal low", "negative"),)),
    EvidenceExcerpt("2020Q4", "it is too early to predict overall recovery trends for the travel industry", (Signal("consumer_confidence_change", -1, "pandemic uncertainty", "negative", "risk"), Signal("demand_volatility", -1, "limited visibility", "negative", "risk"))),
    EvidenceExcerpt("2021Q1", "booking lead times start to lengthen when compared with Q4 2020", (Signal("booking_lead_time", 1, "lengthening", "positive"),)),
    EvidenceExcerpt("2021Q1", "continued uncertainty of travel restrictions and lockdowns in EMEA", (Signal("regional_mix", -1, "EMEA restrictions", "negative", "risk"), Signal("consumer_confidence_change", -1, "travel restrictions", "negative", "risk"))),
    EvidenceExcerpt("2021Q2", "The stronger than expected recovery in Nights and Experiences Booked through Q2, and the elevated ADR year-to-date have created a strong GBV backlog", (Signal("nights_booked_yoy", 1, "stronger than expected", "positive", "driver"), Signal("adr_yoy", 1, "elevated", "positive", "driver"), Signal("bookings_on_books", 1, "strong backlog", "positive", "driver"))),
    EvidenceExcerpt("2021Q2", "we anticipate that the impact of COVID-19 and the introduction and spread of new variants of the virus", (Signal("cancellation_rate", -1, "variant risk", "negative", "risk"), Signal("demand_volatility", -1, "pandemic volatility", "negative", "risk"))),
    EvidenceExcerpt("2021Q2", "we expect ADR to gradually moderate based on the anticipated shift in regional composition and return to urban destinations", (Signal("adr_yoy", -1, "moderating", "negative", "driver"), Signal("regional_mix", -1, "lower-ADR recovery", "negative"), Signal("urban_mix", 1, "urban recovery", "mixed", stance="mixed"))),
    EvidenceExcerpt("2021Q3", "we continue to see the positive effect of travel restrictions being lifted and global vaccination progress", (Signal("cross_border_growth", 1, "reopening", "positive", "driver"), Signal("consumer_confidence_change", 1, "vaccination progress", "positive"))),
    EvidenceExcerpt("2021Q3", "we expect our ADR will be relatively stable in Q4 2021 relative to Q3 2021", (Signal("adr_yoy", 0, "stable", "neutral"),)),
    EvidenceExcerpt("2021Q3", "Q4 revenue—in both absolute dollars and as a percentage of GBV—will decrease from Q3 due to travel seasonality", (Signal("target_quarter", -1, "Q4 seasonal decline", "negative", "driver"), Signal("take_rate", -1, "seasonal decline", "negative"))),
    EvidenceExcerpt("2021Q4", "highlighting strong growth in nights stayed and ADR relative to both Q1 2021 and Q1 2019", (Signal("nights_booked_yoy", 1, "strong growth", "positive", "driver"), Signal("adr_yoy", 1, "strong", "positive", "driver"))),
    EvidenceExcerpt("2021Q4", "Due to the seasonally long lead times for Q1 Nights and Experiences Booked", (Signal("booking_lead_time", 1, "seasonally long", "positive"), Signal("target_quarter", -1, "Q1 seasonality", "negative"))),
    EvidenceExcerpt("2022Q1", "we have seen lead times for bookings normalize with a substantial number of bookings in Q1 2022 already made for peak travel season", (Signal("booking_lead_time", 1, "normalized", "positive"), Signal("bookings_on_books", 1, "substantial peak backlog", "positive", "driver"))),
    EvidenceExcerpt("2022Q1", "further improvement in EMEA, meaningful recovery in Asia Pacific, a normalization of cancellations, and incremental growth from cross-border travel", (Signal("regional_mix", 1, "EMEA and APAC recovery", "positive"), Signal("cancellation_rate", 1, "normalizing", "positive"), Signal("cross_border_growth", 1, "incremental growth", "positive"))),
    EvidenceExcerpt("2022Q1", "We expect ADR to be flat in Q2 2022 on a year-over-year basis", (Signal("adr_yoy", 0, "flat", "neutral"),)),
    EvidenceExcerpt("2022Q2", "we anticipate slightly higher ADRs than we had in Q3 2021 resulting in a modest acceleration in GBV growth", (Signal("adr_yoy", 1, "slightly higher", "positive", "driver"), Signal("gbv_yoy", 1, "modest acceleration", "positive", "driver"))),
    EvidenceExcerpt("2022Q2", "This revenue outlook includes a significant headwind from foreign exchange fluctuations relative to last year", (Signal("fx_revenue_impact", -1, "significant headwind", "negative", "risk"),)),
    EvidenceExcerpt("2022Q3", "promising trends in cross-border travel, renewed interest in urban stays, stabilizing cancellations, as well as a strong backlog of future bookings", (Signal("cross_border_growth", 1, "promising", "positive"), Signal("urban_mix", 1, "renewed interest", "positive"), Signal("cancellation_rate", 1, "stabilizing", "positive"), Signal("bookings_on_books", 1, "strong", "positive", "driver"))),
    EvidenceExcerpt("2022Q3", "ADR will face some pressure from FX headwinds and business mix", (Signal("adr_yoy", -1, "pressure", "negative", "risk"), Signal("fx_revenue_impact", -1, "headwind", "negative", "risk"), Signal("regional_mix", -1, "mix pressure", "negative", stance="mixed"))),
    EvidenceExcerpt("2022Q4", "European guests booking their summer travel earlier this year, the market share gains we are seeing in Latin America", (Signal("booking_lead_time", 1, "earlier summer bookings", "positive"), Signal("regional_mix", 1, "European and Latin American strength", "positive"))),
    EvidenceExcerpt("2022Q4", "we anticipate slightly lower ADR than we had in Q1 2022", (Signal("adr_yoy", -1, "slightly lower", "negative", "risk"),)),
    EvidenceExcerpt("2023Q1", "We expect year-over-year growth in Nights and Experiences Booked in Q2 2023 to be lower than our revenue growth", (Signal("nights_booked_yoy", -1, "below revenue growth", "negative", "risk"),)),
    EvidenceExcerpt("2023Q1", "we anticipate a slightly lower ADR in Q2 2023 than Q2 2022 driven by mix shifts", (Signal("adr_yoy", -1, "slightly lower", "negative", "risk"), Signal("regional_mix", -1, "mix headwind", "negative"))),
    EvidenceExcerpt("2023Q1", "Sales and Marketing expense in Q2 2023 will be approximately 400 basis points higher as a percent of revenue", (Signal("marketing_expense", -1, "400bp higher share", "negative", "contextual_correlation"),)),
    EvidenceExcerpt("2023Q2", "We expect a modest sequential increase in the year-over-year growth rate of Nights and Experiences Booked", (Signal("nights_booked_yoy", 1, "modest acceleration", "positive", "driver"),)),
    EvidenceExcerpt("2023Q2", "we expect upward pressure on ADR from FX rates and listing type mix shift", (Signal("adr_yoy", 1, "upward pressure", "positive", "driver"), Signal("fx_revenue_impact", 1, "tailwind", "positive"), Signal("regional_mix", 1, "listing mix tailwind", "positive"))),
    EvidenceExcerpt("2023Q3", "We are seeing greater volatility early in Q4, and are closely monitoring macroeconomic trends and geopolitical conflicts", (Signal("demand_volatility", -1, "greater volatility", "negative", "risk"), Signal("consumer_confidence_change", -1, "macro and geopolitical risk", "negative", "risk"))),
    EvidenceExcerpt("2023Q3", "we expect ADR in Q4 2023 to be stable to slightly up compared to the same period last year", (Signal("adr_yoy", 0.5, "stable to slightly up", "positive"),)),
    EvidenceExcerpt("2023Q4", "Year-over-year revenue growth in Q1 2024 will benefit due to the timing of Easter", (Signal("easter_shift", 1, "one-to-two-point benefit", "positive", "driver"), Signal("take_rate", 1, "calendar-driven uplift", "positive"))),
    EvidenceExcerpt("2023Q4", "we expect the growth rate of nights booked in Q1 2024 to moderate relative to Q4 2023", (Signal("nights_booked_yoy", -1, "moderating", "negative", "risk"),)),
    EvidenceExcerpt("2024Q1", "year-over-year revenue growth in Q2 2024 will face a significant sequential headwind primarily due to the timing of the Easter holiday", (Signal("easter_shift", -1, "reversal headwind", "negative", "driver"),)),
    EvidenceExcerpt("2024Q1", "the inclusion of Leap Day in Q1 2024, and the impact of FX rate changes", (Signal("leap_year", -1, "comparison headwind", "negative"), Signal("fx_revenue_impact", -1, "headwind", "negative", "risk"))),
    EvidenceExcerpt("2024Q1", "we are already experiencing robust demand for travel around international events such as the Olympics and Euro Cup", (Signal("major_holiday_shift", 1, "major-event demand", "positive"), Signal("forward_booking_momentum", 1, "robust", "positive", "driver"))),
    EvidenceExcerpt("2024Q2", "we are seeing shorter booking lead times globally and some signs of slowing demand from U.S. guests", (Signal("booking_lead_time", -1, "shorter", "negative", "risk"), Signal("regional_mix", -1, "U.S. slowing", "negative", "risk"), Signal("consumer_confidence_change", -1, "U.S. softness", "negative", "risk"))),
    EvidenceExcerpt("2024Q2", "our implied take rate in Q3 2024 will be higher on a year-over-year basis, primarily due to the timing of bookings", (Signal("take_rate", 1, "higher", "positive", "driver"),)),
    EvidenceExcerpt("2024Q2", "cross-currency transaction fees, partially offset by investments in customer service", (Signal("fee_structure_change", 1, "cross-currency fee", "positive", "driver"), Signal("product_investment_intensity", -1, "contra-revenue investment", "negative", "risk", "contradictory"))),
    EvidenceExcerpt("2024Q3", "strong demand trends in Q4 2024 across core and expansion markets for both long and short lead times", (Signal("forward_booking_momentum", 1, "strong", "positive", "driver"), Signal("booking_lead_time", 1, "broad-based", "positive"), Signal("regional_mix", 1, "core and expansion strength", "positive"))),
    EvidenceExcerpt("2024Q3", "we expect ADR to increase modestly on a year-over-year basis, driven by continued demand for larger and higher priced listings", (Signal("adr_yoy", 1, "modest increase", "positive", "driver"), Signal("regional_mix", 1, "larger-listing mix", "positive"))),
    EvidenceExcerpt("2024Q3", "our implied take rate in Q4 2024 will be slightly lower on a year-over-year basis", (Signal("take_rate", -1, "slightly lower", "negative", "risk"),)),
    EvidenceExcerpt("2024Q4", "creating an unfavorable comparison of approximately three percentage points on a year-over-year basis in Q1 2025", (Signal("easter_shift", -1, "comparison headwind", "negative", "driver"), Signal("leap_year", -1, "comparison headwind", "negative"))),
    EvidenceExcerpt("2024Q4", "we expect ADR to decline slightly on a year-over-year basis, largely driven by FX headwinds", (Signal("adr_yoy", -1, "slight decline", "negative", "driver"), Signal("fx_revenue_impact", -1, "headwind", "negative", "driver"))),
    EvidenceExcerpt("2024Q4", "we plan to invest $200 million to $250 million towards launching and scaling new businesses", (Signal("product_investment_intensity", 1, "large planned investment", "neutral", "contextual_correlation"),)),
    EvidenceExcerpt("2025Q1", "strong results despite recent global economic volatility, highlighting the resilience and adaptability of our business", (Signal("consumer_confidence_change", -1, "economic volatility", "negative", "risk"), Signal("forward_booking_momentum", 1, "resilient", "positive", stance="mixed"))),
    EvidenceExcerpt("2025Q1", "Latin America–which remains our fastest growing region", (Signal("regional_mix", 1, "Latin America strength", "positive"),)),
    EvidenceExcerpt("2025Q1", "in the U.S., we’ve seen relatively softer results, which we believe has been largely driven by broader economic uncertainties", (Signal("regional_mix", -1, "U.S. softness", "negative", "risk"), Signal("consumer_confidence_change", -1, "economic uncertainty", "negative", "risk"))),
    EvidenceExcerpt("2025Q1", "Revenue growth in Q2 2025 includes a benefit of approximately two percentage points related to the timing of Easter", (Signal("easter_shift", 1, "two-point benefit", "positive", "driver"), Signal("take_rate", 1, "calendar uplift", "positive"))),
    EvidenceExcerpt("2025Q2", "we expect a tougher year-over-year comparison toward the end of the quarter", (Signal("demand_volatility", -1, "tougher comparison", "negative", "risk"),)),
    EvidenceExcerpt("2025Q2", "we expect year-over-year growth of Nights and Seats Booked to be relatively stable compared to Q2 2025", (Signal("nights_booked_yoy", 0, "stable", "neutral"),)),
    EvidenceExcerpt("2025Q2", "we expect ADR to increase modestly on a year-over-year basis, primarily driven by FX", (Signal("adr_yoy", 1, "modest increase", "positive"), Signal("fx_revenue_impact", 1, "tailwind", "positive", "driver"))),
    EvidenceExcerpt("2025Q3", "we're seeing strength in longer lead time bookings, partly driven by our Reserve Now, Pay Later offering", (Signal("booking_lead_time", 1, "lengthening", "positive", "driver"), Signal("product_investment_intensity", 1, "Reserve Now Pay Later", "positive", "driver"))),
    EvidenceExcerpt("2025Q3", "we expect our GBV to grow low-double digits year-over-year", (Signal("gbv_yoy", 1, "low-double-digit", "positive", "driver"),)),
    EvidenceExcerpt("2025Q3", "a modest increase in ADR, primarily due to price appreciation and FX", (Signal("adr_yoy", 1, "modest increase", "positive"), Signal("fx_revenue_impact", 1, "tailwind", "positive"))),
    EvidenceExcerpt("2025Q4", "product improvements supported double-digit growth across our key top-line metrics in Q4", (Signal("product_investment_intensity", 1, "top-line support", "positive", "driver"),)),
    EvidenceExcerpt("2025Q4", "GBV to increase in the low teens year-over-year, driven by high-single-digit growth in Nights and Seats Booked", (Signal("gbv_yoy", 1, "low teens", "positive", "driver"), Signal("nights_booked_yoy", 1, "high single digits", "positive", "driver"))),
    EvidenceExcerpt("2025Q4", "inclusive of an approximate three point foreign exchange tailwind", (Signal("fx_revenue_impact", 1, "three-point tailwind", "positive", "driver"),)),
    EvidenceExcerpt("2026Q1", "continued momentum in our core business—particularly strong nights booked growth in North America and Latin America", (Signal("nights_booked_yoy", 1, "strong", "positive", "driver"), Signal("regional_mix", 1, "North America and Latin America strength", "positive", "driver"))),
    EvidenceExcerpt("2026Q1", "assuming an estimated roughly 100bps headwind related to the conflict in the Middle East", (Signal("cancellation_rate", -1, "conflict-related", "negative", "risk"), Signal("consumer_confidence_change", -1, "geopolitical headwind", "negative", "risk"))),
    EvidenceExcerpt("2026Q1", "improvements to monetization through a simplified fee structure and our insurance programs", (Signal("fee_structure_change", 1, "monetization uplift", "positive", "driver"), Signal("take_rate", 1, "expected uplift", "positive", "driver"))),
    EvidenceExcerpt("2026Q2", "The uplift in revenue growth and margin reflects the strong demand on our platform", (Signal("forward_booking_momentum", 1, "strong demand", "positive", "driver"),)),
    EvidenceExcerpt("2026Q2", "benefits from investments we’ve made in talent, technology, and marketing as well as strong execution across our product roadmap", (Signal("marketing_expense", 1, "growth investment", "positive"), Signal("product_investment_intensity", 1, "product execution", "positive", "driver"))),
    EvidenceExcerpt("2026Q2", "GBV growth to be in the mid teens, driven by low double-digit growth in Nights and Seats Booked", (Signal("gbv_yoy", 1, "mid teens", "positive", "driver"), Signal("nights_booked_yoy", 1, "low double digits", "positive", "driver"))),
    EvidenceExcerpt("2026Q2", "inclusive of an approximate three percentage point FX tailwind", (Signal("fx_revenue_impact", 1, "three-point tailwind", "positive", "driver"),)),
)


def build_management_evidence(
    *, events: list[GuidanceEvent], official_documents: list[SourceDocument]
) -> dict[str, list]:
    event_by_period = {event.reported_period: event for event in events}
    document_by_period = {document.fiscal_period: document for document in official_documents}
    excerpts: list[SourceExcerpt] = []
    observations: list[DriverObservation] = []
    claims: list[EvidenceClaim] = []

    for excerpt_number, item in enumerate(EVIDENCE_EXCERPTS, start=1):
        event = event_by_period[item.period]
        document = document_by_period[item.period]
        excerpt_id = f"ABNB-{item.period}-DRIVER-{excerpt_number:03d}"
        excerpts.append(
            SourceExcerpt(
                source_excerpt_id=excerpt_id,
                document_id=document.document_id,
                section_heading=item.anchor,
                source_anchor="Outlook or earnings discussion; whitespace normalized",
                exact_excerpt=item.text,
                excerpt_word_count=len(item.text.split()),
                context_paraphrase="Management described one or more inputs, risks, or offsets relevant to its forward outlook.",
                copyright_handling="Short pinpoint excerpt from a public SEC-filed issuer exhibit; not a transcript.",
                extraction_method="manual dual-field verification against SEC HTML",
                verified_against_source=True,
            )
        )
        for signal_number, signal in enumerate(item.signals, start=1):
            record_suffix = f"{excerpt_number:03d}-{signal_number:02d}"
            observations.append(
                DriverObservation(
                    driver_observation_id=f"ABNB-{item.period}-OBS-{record_suffix}",
                    guidance_event_id=event.guidance_event_id,
                    driver_family=DRIVER_FAMILIES[signal.code],
                    driver_code=signal.code,
                    value_numeric=signal.value,
                    value_category=signal.category,
                    unit="management_direction_ordinal",
                    scope_code="next_quarter_outlook",
                    direction_interpretation=signal.direction,
                    availability_class="contemporaneous_management_known",
                    known_to_management_by_utc=event.published_at_utc,
                    public_available_at_utc=event.published_at_utc,
                    is_derived=False,
                    source_excerpt_id=excerpt_id,
                    quality_grade="A",
                    leakage_risk="low",
                    leakage_notes="Eligible for management-information view at the guidance event; not public-prior view.",
                )
            )
            claims.append(
                EvidenceClaim(
                    evidence_claim_id=f"ABNB-{item.period}-CLAIM-{record_suffix}",
                    guidance_event_id=event.guidance_event_id,
                    source_excerpt_id=excerpt_id,
                    driver_family=DRIVER_FAMILIES[signal.code],
                    driver_code=signal.code,
                    claim_type="explicit_management_outlook_rationale",
                    evidence_stance=signal.stance,
                    direction=signal.direction,
                    attribution_strength=signal.strength,
                    time_horizon="next_quarter",
                    scope_code="consolidated",
                    coder_confidence="high",
                )
            )

    # Explicit omission audit: the outlook sections rarely attribute quarterly revenue
    # ranges directly to supply or regulation.  Store the negative evidence rather
    # than silently dropping candidate variables.
    omission_period = "2024Q2"
    source_excerpt_id = next(
        excerpt.source_excerpt_id
        for excerpt in excerpts
        if excerpt.document_id == document_by_period[omission_period].document_id
    )
    for number, code in enumerate(("active_listings_yoy", "regulatory_pressure"), start=1):
        claims.append(
            EvidenceClaim(
                evidence_claim_id=f"ABNB-{omission_period}-OMISSION-{number:02d}",
                guidance_event_id=event_by_period[omission_period].guidance_event_id,
                source_excerpt_id=source_excerpt_id,
                driver_family=DRIVER_FAMILIES[code],
                driver_code=code,
                claim_type="full_outlook_section_omission_audit",
                evidence_stance="negative_evidence",
                direction="not_attributed",
                attribution_strength="no_attribution",
                time_horizon="next_quarter",
                scope_code="consolidated",
                coder_confidence="medium",
                adjudication_note="Candidate was reviewed but was not explicitly tied to the next-quarter revenue range in this outlook section.",
            )
        )

    return {
        "source_excerpts": excerpts,
        "driver_observations": observations,
        "evidence_claims": claims,
    }


TRANSCRIPT_EVIDENCE = (
    (
        "2025Q3",
        "Ellie Mertz",
        "yes, there are increased cancellations, but we're highly confident that the net impact of the product is a lift to net bookings",
        "cancellation_rate",
        "mixed",
        "mixed",
    ),
    (
        "2026Q1",
        "Ellie Mertz",
        "The upward revision to our revenue outlook reflects meaningful progress across our growth initiatives and improvements to monetization through a simplified fee structure",
        "fee_structure_change",
        "positive",
        "supporting",
    ),
)


def build_transcript_evidence(
    *, events: list[GuidanceEvent], transcript_documents: list[SourceDocument]
) -> dict[str, list]:
    """Create a deliberately small transcript evidence supplement.

    Full transcript text is never returned or persisted.  Each stored excerpt is
    capped at 25 words and each transcript contributes far less than 100 words.
    """
    event_by_period = {event.reported_period: event for event in events}
    document_by_period = {document.fiscal_period: document for document in transcript_documents}
    excerpts: list[SourceExcerpt] = []
    claims: list[EvidenceClaim] = []
    for number, (period, speaker, text, code, direction, stance) in enumerate(
        TRANSCRIPT_EVIDENCE, start=1
    ):
        if period not in document_by_period:
            continue
        event = event_by_period[period]
        document = document_by_period[period]
        excerpt_id = f"ABNB-{period}-TRANSCRIPT-DRIVER-{number:02d}"
        excerpts.append(
            SourceExcerpt(
                source_excerpt_id=excerpt_id,
                document_id=document.document_id,
                section_heading="Questions and Answers" if period == "2025Q3" else "Prepared Remarks",
                speaker=speaker,
                source_anchor="Pinpoint phrase verified against user-supplied corrected transcript",
                exact_excerpt=text,
                excerpt_word_count=len(text.split()),
                context_paraphrase=(
                    "Management acknowledged higher cancellations but said the payment product still lifted net bookings."
                    if period == "2025Q3"
                    else "Management attributed a raised outlook partly to monetization and fee-structure work."
                ),
                copyright_handling="third_party_transcript",
                extraction_method="manual pinpoint verification; no full text retained",
                verified_against_source=True,
            )
        )
        claims.append(
            EvidenceClaim(
                evidence_claim_id=f"ABNB-{period}-TRANSCRIPT-CLAIM-{number:02d}",
                guidance_event_id=event.guidance_event_id,
                source_excerpt_id=excerpt_id,
                driver_family=DRIVER_FAMILIES[code],
                driver_code=code,
                claim_type="transcript_management_explanation",
                evidence_stance=stance,
                direction=direction,
                attribution_strength="driver",
                time_horizon="next_quarter_or_full_year",
                scope_code="consolidated",
                coder_confidence="high",
            )
        )
    return {"source_excerpts": excerpts, "evidence_claims": claims}


OTHER_GUIDANCE_CODES = {"nights_booked_yoy", "gbv_yoy", "adr_yoy", "take_rate"}


def build_other_guidance_items(
    *,
    events: list[GuidanceEvent],
    revenue_guidance: list[GuidanceItem],
    driver_observations: list[DriverObservation],
) -> list[GuidanceItem]:
    """Represent non-revenue operating outlook without pretending narrative is a range."""
    target_by_event = {
        item.guidance_event_id: item.target_period
        for item in revenue_guidance
        if item.metric_code == "revenue"
    }
    seen: set[tuple[str, str]] = set()
    result: list[GuidanceItem] = []
    for observation in driver_observations:
        key = (observation.guidance_event_id, observation.driver_code)
        if observation.driver_code not in OTHER_GUIDANCE_CODES or key in seen:
            continue
        seen.add(key)
        result.append(
            GuidanceItem(
                guidance_item_id=(
                    f"{observation.guidance_event_id}-{observation.driver_code.upper()}-GUIDE"
                ),
                guidance_event_id=observation.guidance_event_id,
                target_period=target_by_event[observation.guidance_event_id],
                metric_code=observation.driver_code,
                measure_type="qualitative_direction",
                unit="narrative",
                accounting_basis="operating",
                is_company_stated=True,
                source_excerpt_id=observation.source_excerpt_id,
                extraction_confidence="high" if observation.quality_grade == "A" else "medium",
            )
        )
    return result
