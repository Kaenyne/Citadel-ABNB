"""L0 file 3 — L0_vintage_register.csv: a NEW consensus vintage register.

This is NOT the existing data/processed/overnight/20_vintage_register.csv. That file is a
SERIES-LINEAGE register (columns: series, native_freq, release_lag_days,
vintage_reconstructible, how, lag_applied, approximation_label) and carries no consensus
values at all. Its schema is incompatible with what Card 0 asks for, so it is neither
overwritten nor extended; it is cited here as provenance and left alone.

Schema: vendor, period, metric, value, n_estimates, as_of_timestamp, url, source_path
(+ unit, role, pit_usable, vendor_attributed, register_id, note).

Roles:
  at_print    the consensus the print was scored against, quoted on the print-day article
  pre_guide   the next-quarter consensus quoted on the print morning, BEFORE the guide.
              This is the Street baseline every gate must use. The 6 Aug 2026 3Q26 value
              is LSEG $4,610M -- NOT Zacks $4,740M, which is a 4 Sep 2026 vintage and
              post-dates the guide by four weeks.
  current     a live vendor snapshot dated 2026-09-03 / 09-04 / 09-11

pit_usable == False whenever as_of_timestamp is missing (vintage_unknown) or the value is
missing. Such rows are never usable point-in-time and pit_consensus() will not return them.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

from _paths import OUT, OVERNIGHT, rel  # noqa: E402

SRC_PRINT = OVERNIGHT / "04_consensus_at_print.csv"
SRC_MERGED = OVERNIGHT / "16_consensus_at_print_merged.csv"
SRC_CURRENT = OVERNIGHT / "04_current_consensus.csv"
SRC_LINEAGE = OVERNIGHT / "20_vintage_register.csv"
SRC_FACTS = "docs/revenue-forecast-strategy/01_ground-truth/04_recent_facts.md"

COLS = ["register_id", "vendor", "period", "metric", "value", "unit", "n_estimates",
        "as_of_timestamp", "url", "source_path", "role", "pit_usable",
        "vendor_attributed", "note"]

UNATTRIBUTED = ("unattributed", "Yahoo/unattributed", "CNBC unattributed", "derived")

# Alpha Vantage EARNINGS_ESTIMATES, retrieved 2026-09-11, transcribed from
# docs/revenue-forecast-strategy/01_ground-truth/04_recent_facts.md section
# "Consensus Revenue Estimates (Alpha Vantage as of 2026-09-11)".
ALPHA_VANTAGE = [
    ("2026Q3", "revenue", 4737.0, 36, "consensus $4,737M vs guide $4,690-4,770M"),
    ("2026Q4", "revenue", 3158.0, 36, "the 36-analyst 4Q26 value; the other live 4Q26 anchor is Zacks $3,200M (4 Sep, 10 estimates)"),
    ("FY2026", "revenue", 14155.0, 43, "+30 up / 4 down revisions over 30d"),
    ("FY2027", "revenue", 15758.0, 44, "+25 up / 9 down revisions over 30d; implies +11.3% FY26-27"),
]
AV_URL = "http://www.alphavantage.co"
AV_ASOF = "2026-09-11"


def _pq_to_period(pq: str) -> str:
    """'2026Q3' stays as is; the ledger's '3Q26' style is normalised to '2026Q3'."""
    pq = str(pq)
    if "Q" in pq and pq[0].isdigit() and len(pq) == 4 and not pq.startswith("20"):
        return f"20{pq[2:]}Q{pq[0]}"
    return pq


def build(verbose: bool = True) -> tuple[pd.DataFrame, dict]:
    diag: dict = {}
    rows: list[dict] = []

    # guard: never touch the incompatible lineage register
    lin = pd.read_csv(SRC_LINEAGE, nrows=1)
    assert "series" in lin.columns and "value" not in lin.columns, (
        "20_vintage_register.csv unexpectedly looks like a value register; stop and re-check")
    diag["lineage_register_left_untouched"] = rel(SRC_LINEAGE)

    # ---- at-print and pre-guide consensus --------------------------------
    # 16_* is the merged superset; fall back to 04_* only if a column is missing there.
    p = pd.read_csv(SRC_MERGED, parse_dates=["print_date"])
    base = pd.read_csv(SRC_PRINT, parse_dates=["print_date"])
    assert set(base["print_quarter"]) <= set(p["print_quarter"]), "04_ has prints 16_ lacks"
    src = rel(SRC_MERGED)

    # INTEGRITY FLAG. 16_consensus_at_print_merged.csv carries next-quarter consensus values
    # that 04_consensus_at_print.csv does not, with no as-of timestamp and no url. For the
    # 2024Q2 print the merged file supplies next_q $3,840M (LSEG) while that same row's own
    # notes column still reads "NEXT-QUARTER CONSENSUS NOT FOUND ... no other contemporaneous
    # source retrievable". A value whose provenance contradicts its own note is not
    # point-in-time usable, so it is registered with pit_usable = False, not dropped.
    b_nq = base.set_index("print_quarter")["next_q_cons_revenue_musd"]
    merged_only = set()
    for _, r in p.iterrows():
        pq = str(r["print_quarter"])
        if pd.notna(r.get("next_q_cons_revenue_musd")) and (
                pq not in b_nq.index or pd.isna(b_nq.loc[pq])):
            merged_only.add(pq)
    diag["next_q_values_present_only_in_merged_file"] = sorted(merged_only)

    for _, r in p.iterrows():
        pq = str(r["print_quarter"])
        asof = r["print_date"].strftime("%Y-%m-%d") if pd.notna(r["print_date"]) else ""
        # at-print revenue consensus
        for col, metric, unit in (("cons_revenue_musd", "revenue", "musd"),
                                  ("cons_eps_usd", "eps_adj", "usd"),
                                  ("cons_adj_ebitda_musd", "adj_ebitda", "musd"),
                                  ("cons_nights_m", "nights", "m_nights"),
                                  ("cons_gbv_busd", "gbv", "busd")):
            v = r.get(col)
            if pd.isna(v):
                continue
            # Only the revenue consensus carries a vendor in the source files; the EPS,
            # EBITDA, nights and GBV cells do not, so they are registered unattributed
            # rather than inheriting the revenue vendor they may not come from.
            vendor = (str(r.get("cons_revenue_vendor", "")) if metric == "revenue"
                      else "vendor_not_recorded")
            rows.append({
                "register_id": f"AP-{pq}-{metric}",
                "vendor": vendor, "period": pq, "metric": metric, "value": float(v),
                "unit": unit, "n_estimates": pd.NA, "as_of_timestamp": asof,
                "url": "", "source_path": src, "role": "at_print",
                "pit_usable": bool(asof), "vendor_attributed": not any(u in vendor for u in UNATTRIBUTED),
                "note": f"consensus quoted on the print-day article; confidence={r.get('confidence')}",
            })
        # pre-guide next-quarter consensus -- the Street baseline
        nq, nv = r.get("next_quarter"), r.get("next_q_cons_revenue_musd")
        if pd.notna(nq) and pd.notna(nv):
            vendor = str(r.get("next_q_cons_vendor", "") or "")
            contested = pq in merged_only
            note = ("PRE-GUIDE Street, quoted on the morning of the print that carried the guide. "
                    "Use this, never a later vendor snapshot, as the Street baseline.")
            if contested:
                note = ("vintage_unknown: this value appears only in 16_consensus_at_print_merged.csv, "
                        "is absent from 04_consensus_at_print.csv, carries no as-of timestamp or url, "
                        "and the same row's notes column says NEXT-QUARTER CONSENSUS NOT FOUND. "
                        "Registered for audit; excluded from every PIT use.")
            rows.append({
                "register_id": f"PG-{_pq_to_period(nq)}-revenue",
                "vendor": vendor or "unattributed", "period": _pq_to_period(nq),
                "metric": "revenue", "value": float(nv), "unit": "musd",
                "n_estimates": pd.NA, "as_of_timestamp": ("" if contested else asof), "url": "",
                "source_path": src, "role": "pre_guide",
                "pit_usable": bool(asof) and not contested,
                "vendor_attributed": bool(vendor) and not any(u in vendor for u in UNATTRIBUTED),
                "note": note,
            })
        elif pd.notna(nq):
            rows.append({
                "register_id": f"PG-{_pq_to_period(nq)}-revenue",
                "vendor": "", "period": _pq_to_period(nq), "metric": "revenue",
                "value": pd.NA, "unit": "musd", "n_estimates": pd.NA,
                "as_of_timestamp": "", "url": "", "source_path": src,
                "role": "pre_guide", "pit_usable": False, "vendor_attributed": False,
                "note": "vintage_unknown: no contemporaneous next-quarter consensus retrievable; excluded from PIT use",
            })

    # ---- current vendor snapshots ----------------------------------------
    cur = pd.read_csv(SRC_CURRENT)
    for i, r in cur.iterrows():
        vendor = str(r["vendor"])
        val = r["value"]
        asof = str(r["as_of"]) if pd.notna(r["as_of"]) else ""
        ok = bool(asof) and pd.notna(val)
        rows.append({
            "register_id": f"CU-{r['period']}-{r['metric']}-{vendor.split()[0][:12]}-{i}",
            "vendor": vendor, "period": str(r["period"]), "metric": str(r["metric"]),
            "value": float(val) if pd.notna(val) else pd.NA, "unit": str(r["unit"]),
            "n_estimates": r["n_estimates"] if pd.notna(r["n_estimates"]) else pd.NA,
            "as_of_timestamp": asof, "url": str(r["url"]) if pd.notna(r["url"]) else "",
            "source_path": rel(SRC_CURRENT), "role": "current",
            "pit_usable": ok,
            "vendor_attributed": not any(u in vendor for u in UNATTRIBUTED),
            "note": ("" if ok else "vintage_unknown or value missing; excluded from PIT use. ")
                    + str(r["quote"])[:220],
        })

    # ---- Alpha Vantage 11 Sep 2026 ---------------------------------------
    for period, metric, value, n, note in ALPHA_VANTAGE:
        rows.append({
            "register_id": f"CU-{period}-{metric}-AlphaVantage",
            "vendor": "Alpha Vantage (aggregated sell-side panel)", "period": period,
            "metric": metric, "value": value, "unit": "musd", "n_estimates": n,
            "as_of_timestamp": AV_ASOF, "url": AV_URL, "source_path": SRC_FACTS,
            "role": "current", "pit_usable": True, "vendor_attributed": True,
            "note": note,
        })

    reg = pd.DataFrame(rows)[COLS]
    assert reg["register_id"].is_unique, "duplicate register_id"

    # ---------------- seed assertions --------------------------------------
    def one(period, metric, role, vendor_sub=None):
        m = (reg["period"] == period) & (reg["metric"] == metric) & (reg["role"] == role)
        if vendor_sub:
            m &= reg["vendor"].str.contains(vendor_sub, na=False)
        return reg[m]

    pg = one("2026Q3", "revenue", "pre_guide")
    assert len(pg) == 1, f"expected one 3Q26 pre-guide row, got {len(pg)}"
    assert abs(float(pg["value"].iloc[0]) - 4610.0) < 1e-6, "3Q26 pre-guide is not $4,610M"
    assert pg["vendor"].iloc[0] == "LSEG", f"3Q26 pre-guide vendor is {pg['vendor'].iloc[0]}, expected LSEG"
    assert pg["as_of_timestamp"].iloc[0] == "2026-08-06", "3Q26 pre-guide is not stamped 2026-08-06"

    zq3 = one("2026Q3", "revenue", "current", "Zacks")
    assert len(zq3) == 1 and abs(float(zq3["value"].iloc[0]) - 4740.0) < 1e-6
    assert zq3["as_of_timestamp"].iloc[0] == "2026-09-04"

    av = one("2026Q4", "revenue", "current", "Alpha Vantage")
    assert len(av) == 1 and abs(float(av["value"].iloc[0]) - 3158.0) < 1e-6
    assert int(av["n_estimates"].iloc[0]) == 36

    sp26 = one("FY2026", "revenue", "current", "S&P Global Market Intelligence")
    sp27 = one("FY2027", "revenue", "current", "S&P Global Market Intelligence")
    assert len(sp26) == 1 and abs(float(sp26["value"].iloc[0]) - 14160.0) < 1e-6
    assert len(sp27) == 1 and abs(float(sp27["value"].iloc[0]) - 15760.0) < 1e-6
    assert sp26["as_of_timestamp"].iloc[0] == "2026-09-03"

    diag["rows_total"] = int(len(reg))
    diag["rows_by_role"] = reg["role"].value_counts().to_dict()
    diag["rows_pit_usable"] = int(reg["pit_usable"].sum())
    diag["vintage_unknown_rows"] = int((~reg["pit_usable"]).sum())
    diag["vendors"] = reg["vendor"].value_counts().to_dict()
    diag["preguide_3q26"] = {"vendor": "LSEG", "value_musd": 4610.0, "as_of": "2026-08-06"}
    diag["q4_26_anchor_spread_musd"] = 3200.0 - 3158.0

    out = OUT / "L0_vintage_register.csv"
    header = (
        "# L0_vintage_register.csv -- NEW consensus value register (Card 0 file 3).\n"
        "# This does NOT replace data/processed/overnight/20_vintage_register.csv, which is a\n"
        "# series-lineage register with an incompatible schema and is left untouched.\n"
        "# HARD RULE: the 6 Aug 2026 pre-guide 3Q26 Street is LSEG $4,610M (role=pre_guide).\n"
        "# Zacks $4,740M is a 2026-09-04 vintage and must never be used as the 6 Aug pre-guide value.\n"
        "# pit_usable == False means vintage_unknown or value missing: excluded from every PIT use.\n"
    )
    with open(out, "w") as fh:
        fh.write(header)
        reg.to_csv(fh, index=False)

    if verbose:
        print(f"[L0.3] wrote {rel(out)}  rows={len(reg)}  pit_usable={diag['rows_pit_usable']}  "
              f"vintage_unknown={diag['vintage_unknown_rows']}")
        print(f"[L0.3] roles: {diag['rows_by_role']}")
        print("[L0.3] 3Q26 pre-guide Street = LSEG $4,610M @ 2026-08-06 (NOT Zacks $4,740M @ 2026-09-04)")
        print(f"[L0.3] live 4Q26 anchors disagree by ${diag['q4_26_anchor_spread_musd']:.0f}M "
              "(Zacks 3,200 4 Sep vs Alpha Vantage 3,158 11 Sep)")
    return reg, diag


if __name__ == "__main__":
    build()
