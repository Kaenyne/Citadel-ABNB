"""
consensus_history_loader.py -- turn a point-in-time consensus export into L0 vintage-register rows.

WHY THIS EXISTS
---------------
Every "current" consensus row in L0_vintage_register.csv is a snapshot someone happened to take on
the day they looked. The guide-vs-Street backtest needs the opposite: for each fiscal period, what the
Street mean WAS on each historical date. That is a point-in-time (PIT) series, and no free vendor
publishes it. I/B/E/S Summary History on WRDS does: one row per (ticker, measure, fiscal period,
STATPERS) where STATPERS is the monthly statistics date.

STATUS AS OF 2026-09-11: no export exists yet -- WRDS access at UF is faculty/PhD-only and needs an
account request (see docs/revenue-forecast-strategy/05_backtests/A1_consensus_vintages.md). This loader
is written and self-tested against a synthetic fixture so that the moment a CSV lands in
data/raw/consensus/ibes/ it is a one-command job:

    python analysis/src/forecast_methods/L0/consensus_history_loader.py \
        --export data/raw/consensus/ibes/ibes_statsum_ABNB.csv \
        --append

Run without --append first; it prints what it would write and writes nothing.

EXPECTED EXPORT SCHEMA (WRDS I/B/E/S Summary Statistics, unadjusted)
--------------------------------------------------------------------
Column names are matched case-insensitively; extra columns are ignored.

    TICKER    IBES ticker (NOT necessarily the exchange ticker -- verify against CUSIP 009066101)
    CUSIP     8-digit IBES cusip; Airbnb's 9-digit CUSIP is 009066101 -> IBES carries 00906610
    STATPERS  statistics date == THE VINTAGE DATE. Becomes as_of_timestamp.
    MEASURE   SAL = sales/revenue, EBS = EBITDA, EBI = EBIT, EPS = earnings per share
              *** NOTE: the runbook said "REV" and "EBI"; in IBES the codes are SAL and EBS.
                  EBI is EBIT, not EBITDA. Pull SAL + EBS (+ EBI if you want the EBIT bridge). ***
    FISCALP   'ANN' or 'QTR'
    FPEDATS   forecast period END date -- this is what we map to a period label, NOT FPI,
              because FPI is relative to the statistics date and drifts as quarters roll.
    NUMEST    number of estimates in the panel
    MEANEST   consensus mean
    MEDEST    consensus median   (free vendors never publish this -- it is a real gain from IBES)
    HIGHEST / LOWEST / STDEV     dispersion
    CURCODE   currency; rows that are not USD are dropped with a warning

UNITS: IBES reports US sales and EBITDA in MILLIONS, which is already the register's 'musd'.
Verify on the first real export by checking that FY2025 SAL lands near 12240, not 12.24 or 1.224e10.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
REGISTER = REPO / "data/processed/forecast_methods/L0/L0_vintage_register.csv"

HEADER = ["register_id", "vendor", "period", "metric", "value", "unit", "n_estimates",
          "as_of_timestamp", "url", "source_path", "role", "pit_usable", "vendor_attributed", "note"]

# IBES MEASURE -> (register metric, register unit)
MEASURE_MAP = {
    "SAL": ("revenue", "musd"),
    "EBS": ("adj_ebitda", "musd"),
    "EBI": ("operating_income", "musd"),
    "EPS": ("eps_adj", "usd"),
}

VENDOR = "I/B/E/S (Refinitiv) Summary History via WRDS"
URL = "WRDS IBES export"


def _norm(row: dict) -> dict:
    """Upper-case and strip keys so wrds/pandas/manual exports all parse."""
    return {(k or "").strip().upper(): (v.strip() if isinstance(v, str) else v)
            for k, v in row.items()}


def period_label(fpedats: str, fiscalp: str) -> str:
    """Map a forecast-period end date to the register's period label.

    Airbnb's fiscal year is the calendar year, so FY == calendar year and the quarter is
    taken from the month of the period end date. Guard against a non-Dec fiscal year end
    so this blows up loudly rather than silently mislabelling if reused for another name.
    """
    d = fpedats.replace("/", "-").strip()
    # accept YYYY-MM-DD and DDMMMYYYY (SAS-style) exports
    if len(d) >= 10 and d[4] == "-":
        year, month = int(d[0:4]), int(d[5:7])
    elif len(d) == 9:  # e.g. 31DEC2026
        months = dict(JAN=1, FEB=2, MAR=3, APR=4, MAY=5, JUN=6,
                      JUL=7, AUG=8, SEP=9, OCT=10, NOV=11, DEC=12)
        year, month = int(d[5:9]), months[d[2:5].upper()]
    else:
        raise ValueError(f"unrecognised FPEDATS format: {fpedats!r}")

    if fiscalp.upper().startswith("ANN"):
        if month != 12:
            raise ValueError(
                f"FY period ending month {month} != 12 for {fpedats!r}; Airbnb's FY is the calendar "
                "year. Refusing to guess -- check the export.")
        return f"FY{year}"
    return f"{year}Q{(month - 1) // 3 + 1}"


def iso_date(value: str) -> str:
    d = value.replace("/", "-").strip()
    if len(d) >= 10 and d[4] == "-":
        return d[:10]
    if len(d) == 9:
        months = dict(JAN="01", FEB="02", MAR="03", APR="04", MAY="05", JUN="06",
                      JUL="07", AUG="08", SEP="09", OCT="10", NOV="11", DEC="12")
        return f"{d[5:9]}-{months[d[2:5].upper()]}-{d[0:2]}"
    raise ValueError(f"unrecognised date format: {value!r}")


def build_rows(export_path: Path, source_path: str | None = None) -> list[dict]:
    src = source_path or str(export_path.relative_to(REPO)) if export_path.is_absolute() \
        else str(export_path)
    out, skipped = [], {"measure": 0, "currency": 0, "no_mean": 0}

    with open(export_path, newline="") as f:
        for raw in csv.DictReader(f):
            r = _norm(raw)
            measure = (r.get("MEASURE") or "").upper()
            if measure not in MEASURE_MAP:
                skipped["measure"] += 1
                continue
            cur = (r.get("CURCODE") or "USD").upper()
            if cur not in ("USD", ""):
                skipped["currency"] += 1
                continue

            metric, unit = MEASURE_MAP[measure]
            period = period_label(r["FPEDATS"], r.get("FISCALP", "ANN"))
            statpers = iso_date(r["STATPERS"])
            n = r.get("NUMEST") or ""

            def emit(kind: str, value: str, extra_note: str = "") -> None:
                if value in (None, "", "."):
                    return
                stat = "" if kind == "mean" else "_median"
                out.append({
                    "register_id": f"PIT-{period}-{metric}{stat}-IBES-{statpers.replace('-', '')}",
                    "vendor": VENDOR,
                    "period": period,
                    "metric": metric + stat,
                    "value": float(value),
                    "unit": unit,
                    "n_estimates": n,
                    "as_of_timestamp": statpers,      # the STATPERS vintage, not the download date
                    "url": URL,
                    "source_path": src,
                    "role": "pit_history",
                    "pit_usable": True,
                    "vendor_attributed": True,
                    "note": (f"IBES {measure} {r.get('FISCALP', '')} panel; "
                             f"high {r.get('HIGHEST', '')} / low {r.get('LOWEST', '')} / "
                             f"stdev {r.get('STDEV', '')}{extra_note}").strip(),
                })

            if not (r.get("MEANEST") or "").strip():
                skipped["no_mean"] += 1
            emit("mean", r.get("MEANEST", ""))
            emit("median", r.get("MEDEST", ""))

    print(f"parsed {export_path}: {len(out)} register rows; "
          f"skipped {skipped['measure']} off-measure, {skipped['currency']} non-USD, "
          f"{skipped['no_mean']} missing MEANEST", file=sys.stderr)
    return out


def append(rows: list[dict], register: Path = REGISTER) -> None:
    """Append only. Never rewrites or reorders what is already in the register."""
    existing_ids = set()
    with open(register, newline="") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            existing_ids.add(next(csv.reader([line]))[0])

    fresh = [r for r in rows if r["register_id"] not in existing_ids]
    dupes = len(rows) - len(fresh)
    with open(register, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, lineterminator="\n")
        for r in fresh:
            w.writerow(r)
    print(f"appended {len(fresh)} rows ({dupes} already present, skipped)", file=sys.stderr)


def _self_test() -> int:
    """Runs with no export present, so the mapping logic is verifiable today."""
    assert period_label("2026-12-31", "ANN") == "FY2026"
    assert period_label("31DEC2026", "ANN") == "FY2026"
    assert period_label("2026-09-30", "QTR") == "2026Q3"
    assert period_label("2026-12-31", "QTR") == "2026Q4"
    assert period_label("2027-03-31", "QTR") == "2027Q1"
    assert iso_date("18JUN2026") == "2026-06-18"
    assert iso_date("2026-06-18") == "2026-06-18"
    try:
        period_label("2026-06-30", "ANN")
    except ValueError:
        pass
    else:
        raise AssertionError("expected a non-December FY end to raise")

    import tempfile
    fixture = ("TICKER,CUSIP,STATPERS,MEASURE,FISCALP,FPEDATS,NUMEST,MEANEST,MEDEST,HIGHEST,LOWEST,STDEV,CURCODE\n"
               "ABNB,00906610,2026-08-20,SAL,QTR,2026-09-30,34,4705.5,4702.0,4780,4640,38.2,USD\n"
               "ABNB,00906610,2026-08-20,SAL,ANN,2026-12-31,41,14120.0,14115.0,14290,13810,120.5,USD\n"
               "ABNB,00906610,2026-08-20,EBS,ANN,2026-12-31,22,5020.0,5015.0,5200,4880,90.1,USD\n"
               "ABNB,00906610,2026-08-20,XXX,ANN,2026-12-31,5,1.0,1.0,1,1,0,USD\n")
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
        fh.write(fixture)
        p = Path(fh.name)
    rows = build_rows(p, source_path="data/raw/consensus/ibes/<fixture>")
    assert len(rows) == 6, rows                      # 3 usable rows x (mean + median)
    by_id = {r["register_id"]: r for r in rows}
    q3 = by_id["PIT-2026Q3-revenue-IBES-20260820"]
    assert q3["period"] == "2026Q3" and q3["value"] == 4705.5 and q3["n_estimates"] == "34"
    assert q3["as_of_timestamp"] == "2026-08-20" and q3["unit"] == "musd"
    assert q3["role"] == "pit_history"
    assert by_id["PIT-FY2026-adj_ebitda-IBES-20260820"]["metric"] == "adj_ebitda"
    assert by_id["PIT-2026Q3-revenue_median-IBES-20260820"]["value"] == 4702.0
    assert set(rows[0]) == set(HEADER)
    p.unlink()
    print("self-test OK: period mapping, measure mapping, median emission, schema all pass")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--export", type=Path, help="WRDS IBES summary-statistics CSV")
    ap.add_argument("--append", action="store_true",
                    help="write to the register (default is a dry run that writes nothing)")
    ap.add_argument("--self-test", action="store_true", help="run the built-in fixture test")
    a = ap.parse_args()

    if a.self_test or not a.export:
        if not a.export:
            print("no --export given; running self-test instead\n", file=sys.stderr)
        return _self_test()

    rows = build_rows(a.export)
    if not rows:
        print("nothing to write", file=sys.stderr)
        return 1
    if a.append:
        append(rows)
    else:
        print("DRY RUN -- nothing written. First 3 rows:", file=sys.stderr)
        for r in rows[:3]:
            print("   ", {k: r[k] for k in ("register_id", "period", "metric", "value",
                                            "n_estimates", "as_of_timestamp")}, file=sys.stderr)
        print(f"    ... {len(rows)} rows total. Re-run with --append to write.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
