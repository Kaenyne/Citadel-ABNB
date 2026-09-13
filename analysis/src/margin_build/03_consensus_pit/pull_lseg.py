"""WS03 raw pull: point-in-time consensus history for ABNB (daily) and BKNG/EXPE (monthly) from the
LSEG Workspace desktop session. Run with `py -3.13` (lseg-data 2.1.1). Never prints the app key.

Raw output (licensed, gitignored): data/raw/margin_build/03_consensus_pit/*.csv
Manifest (committed):              data/manifests/margin_build/03_consensus_pit.csv

Design (verified by probes on 13 Sep 2026, see docs/margin-build/notes/03_consensus_pit.md):
* `Period=FQn/FYn` is RELATIVE TO THE ROW DATE. FQ1 rolls to the next quarter ON the print date
  itself (e.g. 2023-02-14 already shows FY2023Q1). The absolute period comes from `.fperiod`
  (e.g. 'FY2023Q1') and `.periodenddate`; the row date comes from `.calcdate`.
* Every mean/median/actual field carries its own `.date` = the date the value last changed, so
  staleness = calcdate - date is measurable per field.
* Daily frames hold one row per trading day (about 250 a year).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import os
import sys
import time
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
RAW = REPO / "data" / "raw" / "margin_build" / "03_consensus_pit"
MANIFEST = REPO / "data" / "manifests" / "margin_build" / "03_consensus_pit.csv"

SDATE, EDATE = "2021-01-01", "2026-09-13"

G_EBITDA = ["TR.EBITDAMean", "TR.EBITDAMedian", "TR.EBITDAHigh", "TR.EBITDALow", "TR.EBITDAStdDev",
            "TR.EBITDANumOfEst", "TR.EBITDAMarginMean", "TR.EBITDAReportedMean"]
G_REVEPS = ["TR.RevenueMean", "TR.RevenueMedian", "TR.RevenueHigh", "TR.RevenueLow", "TR.RevenueStdDev",
            "TR.RevenueNumOfEst", "TR.EPSMean", "TR.EPSMedian", "TR.EPSStdDev", "TR.EPSNumOfEst"]
G_OTHER = ["TR.EBITMean", "TR.NetProfitMean", "TR.FCFMean", "TR.COGSMean", "TR.GrossIncomeMean",
           "TR.PreTaxProfitMean", "TR.CAPEXMean", "TR.DPSMean"]
G_OTHER_N = ["TR.EBITNumOfEst", "TR.NetProfitNumOfEst"]  # FCF/COGS have no NumOfEst field (probe 13 Sep)
G_ACT = ["TR.EBITDAActValue", "TR.RevenueActValue", "TR.EPSActValue", "TR.EBITActValue",
         "TR.NetProfitActValue", "TR.FCFActValue"]
G_PEER = ["TR.EBITDAMean", "TR.EBITDANumOfEst", "TR.RevenueMean", "TR.RevenueNumOfEst", "TR.EBITDAMarginMean",
          "TR.EBITDAActValue", "TR.RevenueActValue"]
G_PEER_ACT = ["TR.EBITDAActValue", "TR.RevenueActValue"]

PERIODS_Q = ["FQ1", "FQ2", "FQ3", "FQ4"]
PERIODS_Y = ["FY1", "FY2", "FY3"]


def colname(f: str) -> str:
    return (f.replace("TR.", "").replace(".periodenddate", "_pe").replace(".calcdate", "_calcdate")
            .replace(".fperiod", "_fperiod").replace(".date", "_date").lower())


def expand(fields: list[str]) -> list[str]:
    out = []
    for i, f in enumerate(fields):
        out.append(f)
        if f.endswith("Mean") or f.endswith("ActValue") or f.endswith("Median"):
            out.append(f + ".date")
        if i == 0:
            out += [f + ".calcdate", f + ".fperiod", f + ".periodenddate"]
    return out


def pull(ld, ric: str, fields: list[str], period: str, frq: str) -> pd.DataFrame:
    fl = expand(fields)
    df = ld.get_data(ric, fl, {"SDate": SDATE, "EDate": EDATE, "Frq": frq, "Period": period})
    names = ["ric"] + [colname(f) for f in fl]
    if df.shape[1] != len(names):
        raise RuntimeError(f"{ric} {period} {frq}: got {df.shape[1]} cols, expected {len(names)}: {list(df.columns)}")
    df.columns = names
    df.insert(1, "period_label", period)
    df.insert(2, "frq", frq)
    return df


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    import lseg.data as ld
    key = os.environ.get("LSEG_APP_KEY")
    if not key:
        print("LSEG_APP_KEY not set; cannot pull", file=sys.stderr)
        return 2
    RAW.mkdir(parents=True, exist_ok=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    s = ld.session.desktop.Definition(app_key=key).get_session()
    s.open()
    ld.session.set_default(s)
    jobs = []
    for p in PERIODS_Q + PERIODS_Y:
        jobs.append(("ABNB.O", "ebitda", G_EBITDA, p, "D"))
        jobs.append(("ABNB.O", "reveps", G_REVEPS, p, "D"))
        jobs.append(("ABNB.O", "other", G_OTHER, p, "D"))
    jobs.append(("ABNB.O", "other_n", G_OTHER_N, "FQ1", "D"))
    jobs.append(("ABNB.O", "other_n", G_OTHER_N, "FY1", "D"))
    jobs.append(("ABNB.O", "actual", G_ACT, "FQ0", "D"))
    jobs.append(("ABNB.O", "actual", G_ACT, "FY0", "D"))
    for ric in ("BKNG.O", "EXPE.O"):
        for p in ("FQ1", "FY1", "FY2"):
            jobs.append((ric, "peer", G_PEER, p, "M"))
        for p in ("FQ0", "FY0"):
            jobs.append((ric, "peer_actual", G_PEER_ACT, p, "M"))
    manifest_rows = []
    for ric, grp, fields, period, frq in jobs:
        out = RAW / f"{ric.split('.')[0].lower()}_{grp}_{period}_{frq}.csv"
        status, err = "OK", ""
        if out.exists():
            print(f"  skip (exists) {out.name}")
        else:
            t0 = time.time()
            try:
                df = pull(ld, ric, fields, period, frq)
                df.to_csv(out, index=False)
                print(f"  ok {out.name} rows={len(df)} {time.time() - t0:.1f}s")
            except Exception as e:  # noqa: BLE001
                status, err = "FAIL", repr(e)[:200]
                print(f"  FAIL {ric} {grp} {period} {frq}: {err}")
        manifest_rows.append({
            "file": out.name, "ric": ric, "group": grp, "period": period, "frq": frq,
            "fields": ";".join(expand(fields)), "status": status, "error": err,
            "pulled_at_utc": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            "rows": (sum(1 for _ in open(out, encoding="utf-8")) - 1) if out.exists() else 0,
            "sha256": sha256(out) if out.exists() else "",
        })
    s.close()
    m = pd.DataFrame(manifest_rows)
    m.insert(0, "source", "LSEG Workspace desktop session, lseg-data 2.1.1, ld.get_data")
    m.insert(1, "url", "lseg://desktop/get_data (licensed; no public URL)")
    m.insert(2, "sdate", SDATE)
    m.insert(3, "edate", EDATE)
    m.to_csv(MANIFEST, index=False)
    print(f"manifest -> {MANIFEST} ({len(m)} rows, {int((m.status == 'OK').sum())} OK)")
    return 0 if (m.status == "OK").any() else 1


if __name__ == "__main__":
    sys.exit(main())
