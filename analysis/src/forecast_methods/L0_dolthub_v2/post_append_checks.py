"""Post-append hard-rule checks and the vendor=None behaviour-change measurement (G1b step 6).

    python analysis/src/forecast_methods/L0_dolthub_v2/post_append_checks.py

Writes data/processed/forecast_methods/L0_dolthub_v2/post_append_checks.json and
.../pit_consensus_vendor_none_delta.csv. Exit 0 if every hard-rule invariant holds, 1 otherwise.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
L0_DIR = REPO / "analysis/src/forecast_methods/L0"
REG = REPO / "data/processed/forecast_methods/L0/L0_vintage_register.csv"
BACKUP = REPO / "data/processed/forecast_methods/L0/L0_vintage_register.backup_2026-09-14.csv"
CAL = REPO / "data/processed/forecast_methods/harness/calendar.csv"
OUT_DIR = REPO / "data/processed/forecast_methods/L0_dolthub_v2"

sys.path.insert(0, str(L0_DIR))
import l0  # noqa: E402


def _load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, comment="#")
    df["pit_usable"] = df["pit_usable"].astype(str).str.lower().isin(("true", "1"))
    return df


def select(df: pd.DataFrame, metric: str, period: str, as_of: str):
    """Same selection as l0.pit_consensus(vendor=None): pit_usable, metric, period, vintage
    strictly before as_of; ties broken toward larger n_estimates then vendor name."""
    d = df[df["pit_usable"] & (df["metric"] == metric) & (df["period"] == period)
           & (df["as_of_timestamp"].astype(str) < str(as_of))]
    if d.empty:
        return None
    d = d.assign(_n=pd.to_numeric(d["n_estimates"], errors="coerce").fillna(-1))
    d = d.sort_values(["as_of_timestamp", "_n", "vendor"])
    r = d.iloc[-1]
    return {"vendor": r["vendor"], "value": float(r["value"]), "as_of": str(r["as_of_timestamp"])}


def next_q(q: str) -> str:
    y, n = int(q[:4]), int(q[5])
    return f"{y + (n == 4)}Q{n % 4 + 1}"


def main() -> int:
    res, ok = {}, True

    # 1. byte-identical prefix
    b = BACKUP.read_bytes()
    n = REG.read_bytes()
    res["backup_bytes"] = len(b); res["register_bytes"] = len(n)
    res["prefix_byte_identical"] = n[:len(b)] == b
    ok &= res["prefix_byte_identical"]

    # 2. duplicate ids, 3. vendor string
    reg = _load(REG)
    res["data_rows"] = int(len(reg))
    res["duplicate_register_ids"] = int(reg["register_id"].duplicated().sum())
    ok &= res["duplicate_register_ids"] == 0
    dh = reg[reg["register_id"].str.contains("-DHPNP-")]
    res["dolthub_rows"] = int(len(dh))
    res["dolthub_vendor_strings"] = sorted(dh["vendor"].unique().tolist())
    res["any_dolthub_vendor_contains_zacks"] = bool(dh["vendor"].str.lower().str.contains("zacks").any())
    ok &= not res["any_dolthub_vendor_contains_zacks"]

    # 4-7. l0 lookups (l0 reads its fixed path, which is this worktree's register)
    pg = l0.pre_guide_street("2026Q3")
    res["pre_guide_street_2026Q3"] = pg
    ok &= pg is not None and pg["vendor"] == "LSEG" and pg["value"] == 4610.0 and pg["as_of_timestamp"] == "2026-08-06"
    z0806 = l0.pit_consensus("revenue", "2026Q3", "2026-08-06", vendor="Zacks")
    res["pit_zacks_2026Q3_asof_0806"] = z0806
    ok &= z0806 is None
    d0806 = l0.pit_consensus("revenue", "2026Q3", "2026-08-06", vendor="DoltHub")
    res["pit_dolthub_2026Q3_asof_0806"] = d0806
    ok &= d0806 is not None and d0806["as_of_timestamp"] == "2026-08-02"
    z0911 = l0.pit_consensus("revenue", "2026Q3", "2026-09-11", vendor="Zacks")
    res["pit_zacks_2026Q3_asof_0911"] = z0911
    ok &= z0911 is not None and z0911["value"] == 4740.0
    # also: what vendor=None now returns on the hard-rule date
    res["pit_vendor_none_2026Q3_asof_0806"] = l0.pit_consensus("revenue", "2026Q3", "2026-08-06")
    res["pit_vendor_none_2026Q3_asof_0807"] = l0.pit_consensus("revenue", "2026Q3", "2026-08-07")

    # behaviour change, vendor=None, backup vs new
    old = _load(BACKUP)
    cal = pd.read_csv(CAL)
    cal = cal[cal["is_forecast_row"].astype(str).str.lower() != "true"]
    rows = []
    for r in cal.itertuples():
        if isinstance(r.guide_date, str) and r.guide_date:
            q = next_q(r.print_quarter)
            a, bnew = select(old, "revenue", q, r.guide_date), select(reg, "revenue", q, r.guide_date)
            rows.append({"kind": "guide_date", "date": r.guide_date, "period": q,
                         "old": a, "new": bnew})
        if isinstance(r.print_date, str) and r.print_date and r.print_date_basis == "ledger":
            q = r.print_quarter
            a, bnew = select(old, "revenue", q, r.print_date), select(reg, "revenue", q, r.print_date)
            rows.append({"kind": "print_date", "date": r.print_date, "period": q,
                         "old": a, "new": bnew})
    out = []
    for x in rows:
        o, nw = x["old"], x["new"]
        changed = (o is None) != (nw is None) or (o is not None and nw is not None and
                                                  (o["value"] != nw["value"] or o["vendor"] != nw["vendor"]))
        rel = (nw["value"] - o["value"]) / o["value"] * 100 if (o and nw) else None
        out.append({"kind": x["kind"], "date": x["date"], "period": x["period"],
                    "old_vendor": o["vendor"] if o else None, "old_value": o["value"] if o else None,
                    "old_as_of": o["as_of"] if o else None,
                    "new_vendor": nw["vendor"] if nw else None, "new_value": nw["value"] if nw else None,
                    "new_as_of": nw["as_of"] if nw else None,
                    "changed": changed, "rel_change_pct": rel})
    delta = pd.DataFrame(out)
    delta.to_csv(OUT_DIR / "pit_consensus_vendor_none_delta.csv", index=False)
    summ = {}
    for kind, g in delta.groupby("kind"):
        rel = g["rel_change_pct"].dropna()
        summ[kind] = {"n": int(len(g)), "changed": int(g["changed"].sum()),
                      "old_none_new_value": int((g["old_value"].isna() & g["new_value"].notna()).sum()),
                      "both_values_changed": int(rel.ne(0).sum()),
                      "largest_abs_rel_change_pct": float(rel.abs().max()) if len(rel) else None,
                      "largest_rel_change_row": (g.loc[rel.abs().idxmax()].to_dict()
                                                 if len(rel) else None)}
    res["vendor_none_behaviour_change"] = summ
    res["all_hard_rules_hold"] = bool(ok)
    (OUT_DIR / "post_append_checks.json").write_text(json.dumps(res, indent=1, default=str))
    print(json.dumps(res, indent=1, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
