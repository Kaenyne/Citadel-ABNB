"""Public Nasdaq historical-price parsing and event-return construction."""

from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re

import pandas as pd

from .market import compute_total_return, reaction_session
from .records import GuidanceEvent, MarketReturn, SourceDocument
from .sources import sha256_file
from .storage import load_table, write_table


NASDAQ_ABNB_HISTORY_URL = "https://www.nasdaq.com/market-activity/stocks/abnb/historical"
NASDAQ_QQQ_HISTORY_URL = "https://www.nasdaq.com/market-activity/etf/qqq/historical"


def parse_nasdaq_history(payload: dict) -> pd.Series:
    """Parse the public historical table response into an ascending close series."""
    rows = ((payload.get("data") or {}).get("tradesTable") or {}).get("rows") or []
    parsed: dict = {}
    for row in rows:
        raw_date = row.get("date")
        raw_close = row.get("close")
        if not raw_date or raw_close in {None, "", "N/A"}:
            continue
        close = float(re.sub(r"[^0-9.\-]", "", str(raw_close)))
        parsed[pd.to_datetime(raw_date).date()] = close
    if not parsed:
        raise ValueError("Nasdaq response contained no historical rows")
    return pd.Series(parsed, dtype=float).sort_index()


def build_market_returns(
    events: list[GuidanceEvent],
    abnb_prices: pd.Series,
    benchmark_prices: pd.Series,
    *,
    as_of: datetime,
    windows: tuple[int, ...] = (1, 5, 20),
) -> list[MarketReturn]:
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("as_of must be timezone-aware")
    common_sessions = sorted(set(abnb_prices.index) & set(benchmark_prices.index))
    records: list[MarketReturn] = []
    for event in events:
        session = reaction_session(event.published_at_utc, common_sessions)
        for window in windows:
            record_id = f"{event.guidance_event_id}-ABNB-QQQ-{window}D"
            try:
                raw = round(compute_total_return(abnb_prices, session, window), 12)
                benchmark = round(
                    compute_total_return(benchmark_prices, session, window), 12
                )
                records.append(
                    MarketReturn(
                        market_return_id=record_id,
                        guidance_event_id=event.guidance_event_id,
                        instrument="ABNB",
                        benchmark="QQQ",
                        reaction_session_date=session,
                        window_sessions=window,
                        price_adjustment="unadjusted_official_close",
                        raw_total_return=raw,
                        benchmark_total_return=benchmark,
                        excess_return=round(raw - benchmark, 12),
                        price_source=f"Nasdaq historical pages: {NASDAQ_ABNB_HISTORY_URL} and {NASDAQ_QQQ_HISTORY_URL}",
                        source_as_of_utc=as_of,
                        quality_grade="B",
                    )
                )
            except ValueError as error:
                records.append(
                    MarketReturn(
                        market_return_id=record_id,
                        guidance_event_id=event.guidance_event_id,
                        instrument="ABNB",
                        benchmark="QQQ",
                        reaction_session_date=session,
                        window_sessions=window,
                        price_adjustment="unadjusted_official_close",
                        raw_total_return=None,
                        benchmark_total_return=None,
                        excess_return=None,
                        price_source=f"Nasdaq historical pages: {NASDAQ_ABNB_HISTORY_URL} and {NASDAQ_QQQ_HISTORY_URL}",
                        source_as_of_utc=as_of,
                        quality_grade="D",
                        value_status="missing",
                        missing_reason=f"insufficient price history at research cutoff: {error}",
                    )
                )
    return records


def ingest_nasdaq_market_data(
    research_root: Path,
    abnb_json_path: Path,
    qqq_json_path: Path,
    *,
    as_of: datetime,
) -> dict[str, int]:
    """Persist event returns plus immutable source hashes, not raw price history."""
    root = Path(research_root)
    abnb_path = Path(abnb_json_path)
    qqq_path = Path(qqq_json_path)
    abnb_prices = parse_nasdaq_history(json.loads(abnb_path.read_text(encoding="utf-8")))
    qqq_prices = parse_nasdaq_history(json.loads(qqq_path.read_text(encoding="utf-8")))
    events_frame = load_table("guidance_events", root)
    events = [GuidanceEvent.model_validate(row) for row in events_frame.to_dict("records")]
    records = build_market_returns(events, abnb_prices, qqq_prices, as_of=as_of)
    write_table(
        "market_returns",
        pd.DataFrame([record.model_dump(mode="json") for record in records]),
        root,
    )

    documents = load_table("source_documents", root)
    price_documents = [
        SourceDocument(
            document_id="ABNB-NASDAQ-PRICE-HISTORY",
            document_type="market_price_history",
            title="ABNB Historical Closing Prices",
            publisher="Nasdaq",
            source_url=NASDAQ_ABNB_HISTORY_URL,
            canonical_url=NASDAQ_ABNB_HISTORY_URL,
            retrieved_at_utc=as_of,
            capture_method="Public Nasdaq historical-data JSON response; derived returns retained, raw response not redistributed",
            mime_type="application/json",
            sha256=sha256_file(abnb_path),
            rights_or_access_note="Publicly accessible historical quote table; retain derived event returns and source hash only.",
            version_status="as_retrieved",
        ),
        SourceDocument(
            document_id="QQQ-NASDAQ-PRICE-HISTORY",
            document_type="market_price_history",
            title="QQQ Historical Closing Prices",
            publisher="Nasdaq",
            source_url=NASDAQ_QQQ_HISTORY_URL,
            canonical_url=NASDAQ_QQQ_HISTORY_URL,
            retrieved_at_utc=as_of,
            capture_method="Public Nasdaq historical-data JSON response; derived returns retained, raw response not redistributed",
            mime_type="application/json",
            sha256=sha256_file(qqq_path),
            rights_or_access_note="Publicly accessible historical quote table; retain derived event returns and source hash only.",
            version_status="as_retrieved",
        ),
    ]
    documents = documents[
        ~documents["document_id"].isin({document.document_id for document in price_documents})
    ]
    documents = pd.concat(
        [documents, pd.DataFrame([document.model_dump(mode="json") for document in price_documents])],
        ignore_index=True,
    )
    write_table("source_documents", documents, root)
    return {
        "market_return_count": len(records),
        "missing_market_return_count": sum(
            record.value_status != "observed" for record in records
        ),
    }
