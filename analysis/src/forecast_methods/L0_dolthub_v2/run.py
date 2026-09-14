"""L0_dolthub_v2/run.py -- DoltHub post-no-preference/earnings ABNB revenue-consensus snapshots
into the L0 vintage register as a second, vintage-stamped vendor (package G1b).

    python analysis/src/forecast_methods/L0_dolthub_v2/run.py             # dry run, writes the panel + diagnostics only
    python analysis/src/forecast_methods/L0_dolthub_v2/run.py --append    # also appends to the register
    python analysis/src/forecast_methods/L0_dolthub_v2/run.py --append --only-latest   # T0 FAIL branch: latest snapshot only

Source: the sample CSV pulled 14 Sep 2026 from the keyless DoltHub SQL API (see the manifest next to
it). ABNB slice = the complete sales_estimate table for the ticker (1,160 rows, 290 weekly snapshots,
2021-02-07 to 2026-09-13, four period slots, consensus in whole USD).

What is appended: ABNB revenue rows only, role=pit_history, vendor 'DoltHub post-no-preference/earnings'
(the string must NOT contain 'zacks': l0.pit_consensus filters vendor with str.contains(case=False)
and the frozen test expects a Zacks lookup as of 2026-08-06 to return None). No EPS rows (basis differs
from the register's press-quote adjusted EPS). No NCLH rows (the register is ABNB-only).

The append goes through the frozen loader's append() (imported from L0/, never copied), which is
append-only and skips register_ids already present. Never edit the register by hand.

Outputs (data/processed/forecast_methods/L0_dolthub_v2/):
    dolthub_weekly_panel.csv   date, slot, period, value_musd, n, high_musd, low_musd, year_ago_musd
    build_diagnostics.json     counts, dropped rows, T0 status, what was appended
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
L0_DIR = REPO / "analysis/src/forecast_methods/L0"
SAMPLE_DIR = REPO / "data/processed/github_altdata/samples/dolthub-post-no-preference-earnings-consensus-vintages"
SAMPLE = SAMPLE_DIR / "sales_estimate_ABNB_BKNG_EXPE.csv"
MANIFEST = SAMPLE_DIR / "manifest.json"
OUT_DIR = REPO / "data/processed/forecast_methods/L0_dolthub_v2"
PANEL = OUT_DIR / "dolthub_weekly_panel.csv"
DIAG = OUT_DIR / "build_diagnostics.json"
T0_FILES = [OUT_DIR / "t0_provenance.json", OUT_DIR / "t0_provenance_attempt2.json"]

VENDOR = "DoltHub post-no-preference/earnings"
assert "zacks" not in VENDOR.lower()
ID_TAG = "DHPNP"


def _load_loader():
    """Import the frozen L0 loader by path (reuse HEADER, period_label, append; never copy it)."""
    spec = importlib.util.spec_from_file_location("consensus_history_loader",
                                                  L0_DIR / "consensus_history_loader.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _t0_status() -> dict:
    """Read the T0 provenance verdicts written by t0_provenance.py (both attempts)."""
    out = {}
    for f in T0_FILES:
        if f.exists():
            j = json.loads(f.read_text())
            out[f.name] = {"verdict": j.get("verdict"), "n_requests": j.get("n_requests"),
                           "checks": [{"snapshot": c["snapshot"], "commit": c["commit"],
                                       "match": c["match"], "n_rows_as_of": len(c["rows_as_of"] or [])}
                                      for c in j.get("snapshot_checks", [])]}
    return out


def build(loader, only_latest: bool = False) -> tuple[list[dict], pd.DataFrame, dict]:
    manifest = json.loads(MANIFEST.read_text())
    urls = [u for u in manifest["source_urls"] if "sales_estimate" in u and "ABNB" in u]
    assert len(urls) == 2, urls   # offset 0 and offset 1000 of the ABNB pull
    src_rel = SAMPLE.relative_to(REPO).as_posix()

    df = pd.read_csv(SAMPLE)
    abnb = df[df["act_symbol"] == "ABNB"].reset_index(drop=True)
    abnb["pull_idx"] = range(len(abnb))           # order of the paginated pull (date, period)
    n_all = len(abnb)
    dropped = abnb[abnb["consensus"].isna()]
    abnb = abnb[abnb["consensus"].notna()].copy()
    assert not abnb.duplicated(["date", "period"]).any()

    t0 = _t0_status()
    verdicts = {k: v["verdict"] for k, v in t0.items()}
    provenance = ("verified" if "PASS" in verdicts.values()
                  else "unverified" if not verdicts else "T0 inconclusive: " + ", ".join(
                      f"{k}={v}" for k, v in verdicts.items()))

    latest = abnb["date"].max()
    if only_latest:
        abnb = abnb[abnb["date"] == latest].copy()

    rows, panel = [], []
    for r in abnb.itertuples(index=False):
        fiscalp = "ANN" if "Year" in r.period else "QTR"
        period = loader.period_label(r.period_end_date, fiscalp)   # asserts month 12 for FY slots
        snap = str(r.date)[:10]
        dow = dt.date.fromisoformat(snap).strftime("%A")
        val = round(float(r.consensus) / 1e6, 4)
        hi = round(float(r.high) / 1e6, 4) if pd.notna(r.high) else ""
        lo = round(float(r.low) / 1e6, 4) if pd.notna(r.low) else ""
        ya = round(float(r.year_ago) / 1e6, 4) if pd.notna(r.year_ago) else ""
        n = int(r.count) if pd.notna(r.count) else ""
        cadence = "weekly Sunday snapshot" if dow == "Sunday" else f"weekly snapshot (non-Sunday: {dow})"
        note = (f"{cadence}; slot={r.period}; high {hi} / low {lo} / year_ago {ya}; "
                "mirror of the Zacks free-page consensus (13 Sep 2026 snapshot equals the 11 Sep Zacks "
                "capture in this register to the dollar and count)"
                f"; provenance {provenance}")
        rows.append({
            "register_id": f"PIT-{period}-revenue-{ID_TAG}-{snap.replace('-', '')}",
            "vendor": VENDOR,
            "period": period,
            "metric": "revenue",
            "value": val,
            "unit": "musd",
            "n_estimates": n,
            "as_of_timestamp": snap,
            "url": urls[0] if r.pull_idx < 1000 else urls[1],
            "source_path": src_rel,
            "role": "pit_history",
            "pit_usable": True,
            "vendor_attributed": True,
            "note": note,
        })
        panel.append({"date": snap, "slot": r.period, "period": period, "value_musd": val,
                      "n": n, "high_musd": hi, "low_musd": lo, "year_ago_musd": ya})

    ids = [r["register_id"] for r in rows]
    assert len(ids) == len(set(ids)), "register_id collision inside the DoltHub build"
    assert set(rows[0]) == set(loader.HEADER)
    assert all("zacks" not in r["vendor"].lower() for r in rows)

    diag = {
        "built_at": dt.datetime.now().isoformat(timespec="seconds"),
        "source": src_rel, "vendor": VENDOR,
        "abnb_rows_in_sample": int(n_all), "rows_dropped_no_consensus": dropped[
            ["date", "period", "period_end_date"]].to_dict("records"),
        "snapshots": int(abnb["date"].nunique()), "first_snapshot": str(abnb["date"].min()),
        "last_snapshot": str(latest), "only_latest": only_latest,
        "non_sunday_snapshots": sorted(set(
            s for s in abnb["date"].astype(str) if dt.date.fromisoformat(s[:10]).weekday() != 6)),
        "register_rows_built": len(rows),
        "periods": sorted(set(r["period"] for r in rows)),
        "t0_provenance": t0, "provenance_status": provenance,
    }
    return rows, pd.DataFrame(panel), diag


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--append", action="store_true", help="append to the register (default: dry run)")
    ap.add_argument("--only-latest", action="store_true",
                    help="build/append only the latest snapshot (the T0 FAIL branch)")
    a = ap.parse_args()

    loader = _load_loader()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows, panel, diag = build(loader, only_latest=a.only_latest)
    panel.to_csv(PANEL, index=False)

    register = loader.REGISTER
    assert register == REPO / "data/processed/forecast_methods/L0/L0_vintage_register.csv", register
    before = sum(1 for ln in open(register) if ln.strip() and not ln.startswith("#")) - 1
    diag["register_data_rows_before"] = before

    if a.append:
        loader.append(rows)          # append-only; skips ids already present
        after = sum(1 for ln in open(register) if ln.strip() and not ln.startswith("#")) - 1
        diag["register_data_rows_after"] = after
        diag["rows_appended"] = after - before
        print(f"appended {after - before} rows: register {before} -> {after} data rows", file=sys.stderr)
    else:
        print("DRY RUN -- register untouched. First 5 rows:", file=sys.stderr)
        for r in rows[:5]:
            print("   ", {k: r[k] for k in ("register_id", "period", "value", "n_estimates",
                                            "as_of_timestamp", "vendor")}, file=sys.stderr)
        print(f"    ... {len(rows)} rows total. Re-run with --append to write.", file=sys.stderr)

    DIAG.write_text(json.dumps(diag, indent=1, default=str))
    print(f"panel -> {PANEL} ({len(panel)} rows); diagnostics -> {DIAG}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
