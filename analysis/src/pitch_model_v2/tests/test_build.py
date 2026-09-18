from pathlib import Path
import pytest
import yaml
from openpyxl import load_workbook
from pitch_model_v2 import build
from pitch_model_v2 import spec as specmod

FIX = Path(__file__).parent / "fixtures" / "spec_small.yaml"

def _prov(decision):
    return {"dossier": "docs/pitch-model-v2/dossiers/x.md",
            "receipt": "data/processed/pitch_model_v2/receipts/x/receipt.json",
            "grade": "A", "decision": decision, "tolerance": 0.1}

def test_build_names_and_formulas(tmp_path):
    out = build.build(FIX, tmp_path / "m.xlsx", check_paths=False)
    wb = load_workbook(out)
    names = set(wb.defined_names.keys())
    assert {"D1_3Q26", "D6_3Q26", "R2_4Q26", "R5FY_FY26", "Scenario"} <= names
    ws = wb["Drivers"]
    # find the D6 / 3Q26 cell through its defined name
    dest = wb.defined_names["D6_3Q26"].attr_text  # "'Drivers'!$G$5" style
    sheet, ref = dest.split("!"); cell = wb[sheet.strip("'")][ref.replace("$", "")]
    assert cell.value == "=D1_3Q26*D4T_3Q26"
    r2 = wb.defined_names["R2_3Q26"].attr_text.split("!")
    assert wb[r2[0].strip("'")][r2[1].replace("$", "")].value == "=LAM_3Q26*(2/3*D6_2Q26+1/3*D6_1Q26)"
    d1 = wb.defined_names["D1_3Q26"].attr_text.split("!")
    v = wb[d1[0].strip("'")][d1[1].replace("$", "")].value
    assert v.startswith("=INDEX('Scenario Data'!") and "MATCH(Scenario," in v
    sd = wb["Scenario Data"]
    assert sd["A1"].value == "id" and sd["E1"].value == "base" and sd["F1"].value == "short"
    ev = wb["Evidence"]
    ids = [ev.cell(row=r, column=1).value for r in range(2, ev.max_row + 1)]
    assert "D1" in ids and "D6" in ids
    assert wb.calculation.fullCalcOnLoad is True


def test_build_all_tabs_decisions_validation_and_formats(tmp_path):
    raw = yaml.safe_load(FIX.read_text())
    raw["lines"] += [
        {"id": "C1", "label": "Opex ($M)", "unit": "musd", "block": "costs", "kind": "input",
         "periods": ["3Q26"], "values": {"base": {"3Q26": 100.0}, "short": {"3Q26": 95.0}},
         "provenance": _prov("DEC-0010")},
        {"id": "VX1", "label": "EV/EBITDA (x)", "unit": "x", "block": "valuation", "kind": "input",
         "periods": ["3Q26"], "values": {"base": {"3Q26": 12.5}, "short": {"3Q26": 11.0}},
         "provenance": _prov("DEC-0011")},
        {"id": "EV1", "label": "P(beat) (%)", "unit": "prob", "block": "event", "kind": "input",
         "periods": ["3Q26"], "values": {"base": {"3Q26": 0.35}, "short": {"3Q26": 0.30}},
         "provenance": _prov("DEC-0012")},
        {"id": "ST1", "label": "Street PT ($)", "unit": "usd", "block": "street", "kind": "input",
         "periods": ["3Q26"], "values": {"base": {"3Q26": 150.25}, "short": {"3Q26": 148.0}},
         "provenance": _prov("DEC-0013")},
    ]
    spec_path = tmp_path / "spec_ext.yaml"
    spec_path.write_text(yaml.dump(raw))
    dec_path = tmp_path / "DECISIONS.md"
    dec_path.write_text(
        "# Decisions\n\n"
        "| id | line | period | scenario | value | reason | rejected | date |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| DEC-0001 | D1 | 3Q26 | base | 146.3 | reason | 149.0 | 2026-09-19 |\n"
    )
    out = build.build(spec_path, tmp_path / "m2.xlsx", decisions_path=dec_path, check_paths=False)
    wb = load_workbook(out)

    assert wb.sheetnames == build.ORDER

    dl = wb["Decision Log"]
    assert dl.cell(row=2, column=1).value == "DEC-0001"
    assert dl.cell(row=2, column=5).value == 146.3

    dvs = list(wb["Cover"].data_validations.dataValidation)
    assert len(dvs) == 1
    assert dvs[0].formula1 == '"base,short"'
    assert "B4" in dvs[0].sqref

    for lid, tab in [("C1", "Costs and Earnings"), ("VX1", "Valuation and Call"),
                     ("EV1", "5 Nov Event Card"), ("ST1", "Street")]:
        name = f"{lid}_3Q26"
        assert name in set(wb.defined_names.keys())
        assert wb.defined_names[name].attr_text.startswith(f"'{tab}'!")

    lam = wb.defined_names["LAM_3Q26"].attr_text.split("!")
    assert wb[lam[0].strip("'")][lam[1].replace("$", "")].number_format == "0.00%"
    vx1 = wb.defined_names["VX1_3Q26"].attr_text.split("!")
    assert wb[vx1[0].strip("'")][vx1[1].replace("$", "")].number_format == "0.0x"

    d1 = wb.defined_names["D1_3Q26"].attr_text.split("!")
    cell = wb[d1[0].strip("'")][d1[1].replace("$", "")]
    assert cell.fill.fgColor.rgb in ("00FFF2CC", "FFF2CC")


def test_build_evidence_and_grade_cell_for_multi_entry_input(tmp_path):
    raw = yaml.safe_load(FIX.read_text())
    d1 = raw["lines"][0]
    assert d1["id"] == "D1"
    d1["provenance"] = [
        {"dossier": "docs/pitch-model-v2/dossiers/H0_history.md",
         "receipt": "data/processed/pitch_model_v2/receipts/H0/receipt.json",
         "grade": "A", "decision": "DEC-0001", "tolerance": 0.1,
         "periods": ["1Q26", "2Q26"], "item": "nights_m"},
        {"dossier": "docs/pitch-model-v2/dossiers/D1_nights.md",
         "receipt": "data/processed/pitch_model_v2/receipts/D1/receipt.json",
         "grade": "B", "decision": "DEC-0002", "tolerance": 0.1,
         "periods": ["3Q26", "4Q26"], "item": "nights_m"},
    ]
    spec_path = tmp_path / "spec_multi.yaml"
    spec_path.write_text(yaml.dump(raw))
    out = build.build(spec_path, tmp_path / "m4.xlsx", check_paths=False)
    wb = load_workbook(out)

    ev = wb["Evidence"]
    assert [ev.cell(row=1, column=j).value for j in range(1, 11)] == [
        "id", "line", "kind", "periods", "grade", "decision", "tolerance", "dossier", "receipt", "expr"]
    ev_rows = [
        [ev.cell(row=r, column=j).value for j in range(1, 11)]
        for r in range(2, ev.max_row + 1)
    ]
    d1_rows = [r for r in ev_rows if r[0] == "D1"]
    assert len(d1_rows) == 2
    assert d1_rows[0][3] == "1Q26–2Q26" and d1_rows[0][4] == "A" and d1_rows[0][5] == "DEC-0001"
    assert d1_rows[1][3] == "3Q26–4Q26" and d1_rows[1][4] == "B" and d1_rows[1][5] == "DEC-0002"

    ws = wb["Drivers"]
    d1_row = next(r for r in range(2, ws.max_row + 1) if ws.cell(row=r, column=1).value == "D1")
    assert ws.cell(row=d1_row, column=4).value == "A · DEC-0001 / B · DEC-0002"


def test_build_rejects_unknown_block(tmp_path):
    raw = yaml.safe_load(FIX.read_text())
    raw["lines"][0]["block"] = "nowhere"
    spec_path = tmp_path / "spec_bad.yaml"
    spec_path.write_text(yaml.dump(raw))
    with pytest.raises(specmod.SpecError, match="unknown block"):
        build.build(spec_path, tmp_path / "m3.xlsx", check_paths=False)
