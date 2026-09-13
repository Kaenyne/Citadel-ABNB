"""Meaningful guards for units, release dates, and calendar-aligned growth."""
import importlib.util
import io
import json
from pathlib import Path
import zipfile

import pandas as pd
import pytest

spec = importlib.util.spec_from_file_location("macro_pulls_run", Path(__file__).with_name("run.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_month_header_preserves_preliminary_and_rejects_percent():
    assert m.month_from_header("2026-07\nPreliminary") == "2026-07"
    assert m.month_from_header(pd.Timestamp("2000-01-02")) == "2000-01"
    assert m.month_from_header("2026-13") is None
    assert m.month_from_header("Y/Y change") is None


def test_missing_month_does_not_shift_yoy_comparator():
    months = pd.period_range("2023-01", "2024-12", freq="M")
    d = pd.DataFrame({"origin": "TOTAL ALL COUNTRIES", "period": months.astype(str), "value": [100] * 12 + [200] * 12})
    d = d[d.period.ne("2023-04")]
    features = m.ntto_features(d)
    assert pd.isna(features.loc["2024Q2", "ntto_total_qtd1m"])
    assert features.loc["2024Q3", "ntto_total_qtd1m"] == 100


def test_incomplete_quarter_not_counted_as_full():
    d = pd.DataFrame({"origin": "TOTAL ALL COUNTRIES", "period": ["2023-01", "2023-02", "2024-01", "2024-02", "2024-03"], "value": [100] * 5})
    features = m.ntto_features(d)
    assert pd.isna(features.loc["2024Q1", "ntto_total_full"])


def test_datatur_filters_count_unit_not_ingresos_label():
    d = pd.DataFrame({"Tipo": ["Ingresos", "Ingresos", "Egresos"], "DescripcionNivel03": ["Ingresos", "Número de Viajeros", "Número de Viajeros"],
                      "DescripcionNivel04": ["Turistas internacionales"] * 3, "DescripcionNivel05": ["Turistas no fronterizos"] * 3,
                      "DescripcionNivel06": ["Vía aérea"] * 3, "kano": [2026] * 3, "MesText": ["jun"] * 3, "Valor": [1000000, 250, 50]})
    x = io.BytesIO()
    d.to_excel(x, index=False)
    z = io.BytesIO()
    with zipfile.ZipFile(z, "w") as archive:
        archive.writestr("test.xlsx", x.getvalue())
    rows = m.parse_datatur(z.getvalue())
    assert len(rows) == 1
    assert rows[0]["value"] == 250
    assert rows[0]["unit"] == "persons"


def test_bls_missing_placeholder_is_not_zero():
    source = next(s for s in m.SOURCES if s["series"] == "bls_cpi_lodging")
    payload = {"status": "REQUEST_SUCCEEDED", "Results": {"series": [{"data": [
        {"year": "2026", "period": "M08", "value": "185.9"},
        {"year": "2026", "period": "M07", "value": "-"},
        {"year": "2026", "period": "M13", "value": "180.0"}]}]}}
    rows, _ = m.parse_payload(source, json.dumps(payload).encode())
    assert len(rows) == 1
    assert rows[0]["period"] == "2026-08"


def test_ine_excludes_ytd_rates_and_annual_aggregates():
    payload = [{"Nombre": n, "Data": [{"Anyo": 2026, "FK_Periodo": period, "Valor": 10}]} for n, period in [
        ("Total expenditure. National Total. Tourist. Base data.", 7), ("Total expenditure. Year-to-date data.", 7), ("Total expenditure. Annual variation rate.", 7), ("Total expenditure. National Total. Tourist. Base data.", 28), ("Average daily expenditure. Base data.", 7)]]
    rows = m.parse_ine(json.dumps(payload).encode(), "ine_egatur")
    assert len(rows) == 1
    assert rows[0]["unit"] == "EUR_millions"


def test_unknown_publication_is_not_invented_or_pit():
    spec = next(s for s in m.SOURCES if s["series"] == "ntto")
    row = dict(period="2023-01", value=1, origin="TOTAL ALL COUNTRIES", metric="international_arrivals")
    d = m.finalize_rows(spec, [row], "2026-09-13T17:00:00+00:00")
    assert pd.isna(d.published_on.iloc[0])
    assert not d.pit_usable.iloc[0]
    assert d.knowable_from.iloc[0] == "2026-09-13"


def test_known_calendar_date_does_not_certify_revised_value():
    spec = next(s for s in m.SOURCES if s["series"] == "bls_cpi_lodging")
    d = m.finalize_rows(spec, [dict(period="2026-08", value=100, origin="ALL", metric="CUSR0000SEHB")], "2026-09-13T17:00:00+00:00")
    assert d.published_on.iloc[0] == "2026-09-11"
    assert not d.pit_usable.iloc[0]


def test_duplicate_observation_rejected():
    spec = next(s for s in m.SOURCES if s["series"] == "ntto")
    row = dict(period="2023-01", value=1, origin="ALL", metric="arrivals")
    with pytest.raises(ValueError, match="Duplicate"):
        m.finalize_rows(spec, [row.copy(), row.copy()], "2026-09-13T17:00:00+00:00")
