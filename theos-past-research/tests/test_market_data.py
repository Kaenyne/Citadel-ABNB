from datetime import UTC, date, datetime
import json

import pandas as pd

from abnb_guidance.dataset import build_research_dataset
from abnb_guidance.market_data import (
    build_market_returns,
    ingest_nasdaq_market_data,
    parse_nasdaq_history,
)
from abnb_guidance.records import GuidanceEvent
from abnb_guidance.storage import load_table, validate_dataset


def event() -> GuidanceEvent:
    return GuidanceEvent.model_validate(
        {
            "guidance_event_id": "ABNB-2024Q3-INITIAL",
            "issuer_id": "ABNB",
            "reported_period": "2024Q3",
            "event_type": "initial",
            "published_at_utc": datetime(2024, 11, 7, 21, 30, tzinfo=UTC),
            "published_at_precision": "minute",
            "release_timing": "after_close",
            "research_cutoff_at_utc": datetime(2026, 9, 3, 3, 59, 59, tzinfo=UTC),
            "is_initial_guide": True,
        }
    )


def test_parse_nasdaq_history_normalizes_currency_and_order():
    payload = {
        "data": {
            "tradesTable": {
                "rows": [
                    {"date": "11/11/2024", "close": "$140.00"},
                    {"date": "11/08/2024", "close": "$135.50"},
                ]
            }
        }
    }

    prices = parse_nasdaq_history(payload)

    assert list(prices.index) == [date(2024, 11, 8), date(2024, 11, 11)]
    assert prices.iloc[0] == 135.5


def test_build_market_returns_uses_next_session_after_after_close_event():
    dates = pd.to_datetime(
        ["2024-11-07", "2024-11-08", "2024-11-11", "2024-11-12", "2024-11-13", "2024-11-14"]
    ).date
    abnb = pd.Series([100, 110, 112, 114, 116, 120], index=dates)
    qqq = pd.Series([100, 101, 102, 103, 104, 105], index=dates)

    rows = build_market_returns(
        [event()], abnb, qqq, as_of=datetime(2024, 11, 15, tzinfo=UTC), windows=(1, 5)
    )

    assert rows[0].reaction_session_date == date(2024, 11, 8)
    assert rows[0].raw_total_return == 0.10
    assert rows[0].benchmark_total_return == 0.01
    assert round(rows[0].excess_return, 10) == 0.09
    assert rows[1].raw_total_return == 0.20


def test_insufficient_long_window_is_preserved_as_missing_not_dropped():
    dates = pd.to_datetime(["2024-11-07", "2024-11-08"]).date
    prices = pd.Series([100, 110], index=dates)

    rows = build_market_returns(
        [event()], prices, prices, as_of=datetime(2024, 11, 9, tzinfo=UTC), windows=(20,)
    )

    assert len(rows) == 1
    assert rows[0].value_status == "missing"
    assert "insufficient" in rows[0].missing_reason


def test_ingest_nasdaq_market_data_updates_normalized_table_and_manifest(tmp_path):
    as_of = datetime(2026, 9, 2, 16, tzinfo=UTC)
    build_research_dataset(tmp_path, retrieved_at=as_of)
    sessions = pd.bdate_range("2020-12-09", "2026-09-02")

    def payload(start):
        return {
            "data": {
                "tradesTable": {
                    "rows": [
                        {
                            "date": stamp.strftime("%m/%d/%Y"),
                            "close": f"${start + number / 10:.2f}",
                        }
                        for number, stamp in enumerate(reversed(sessions))
                    ]
                }
            }
        }

    abnb_json = tmp_path / "abnb.json"
    qqq_json = tmp_path / "qqq.json"
    abnb_json.write_text(json.dumps(payload(100)), encoding="utf-8")
    qqq_json.write_text(json.dumps(payload(200)), encoding="utf-8")

    result = ingest_nasdaq_market_data(
        tmp_path, abnb_json, qqq_json, as_of=as_of
    )

    assert result["market_return_count"] == 69
    assert len(load_table("market_returns", tmp_path)) == 69
    documents = load_table("source_documents", tmp_path)
    assert len(documents[documents["document_type"] == "market_price_history"]) == 2
    assert validate_dataset(tmp_path) == []
