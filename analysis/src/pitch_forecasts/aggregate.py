"""Aggregate every question's forecast JSON into one table for the synthesis.

Usage: py -3.13 analysis/src/pitch_forecasts/aggregate.py
Writes docs/pitch-forecasts/forecast_table.csv and prints a compact view. Never modifies question folders.
"""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PF = ROOT / "docs" / "pitch-forecasts"
BATCHES = json.loads((PF / "batches.json").read_text(encoding="utf-8"))
Q2B = {q: b for b, qs in BATCHES.items() for q in qs}


def slugs():
    txt = (PF / "QUESTIONS.md").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^\| (\w\d\d) \| ([a-z0-9\-]+) \| ([^|]+) \| ([^|]+) \|", txt, flags=re.M):
        out[m.group(1)] = (m.group(2), m.group(3).strip(), m.group(4).strip())
    return out


def fmt_final(j):
    f = j.get("final", {})
    if "p" in f:
        ci = f.get("ci") or [None, None]
        return f"{f['p']:.2f}", f"{ci[0]}-{ci[1]}" if ci[0] is not None else ""
    if "vector" in f:
        v = f["vector"]
        return " / ".join(f"{k[:14]} {p:.2f}" for k, p in v.items()), ""
    if "percentiles" in f:
        p = f["percentiles"]
        keys = ["5", "25", "50", "75", "95"]
        unit = f.get("unit", "")
        return "p5/25/50/75/95 " + "/".join(str(p.get(k, "")) for k in keys) + f" {unit}", ""
    return json.dumps(f)[:80], ""


def main():
    S = slugs()
    rows = []
    for qid, (slug, qtype, group) in S.items():
        d = PF / "questions" / slug
        fj = d / "forecasts" / "2026-09-17-forecast.json"
        batch = Q2B.get(qid, "")
        audit_only = (PF / "audits" / f"{batch}.audit_only").exists()
        row = {"id": qid, "batch": batch, "slug": slug, "type": qtype, "group": group,
               "revision": "", "final": "", "ci": "", "anchor": "", "final_minus_anchor": "",
               "ev_usd_per_share": "", "material": "", "audit_only": "yes" if audit_only else ""}
        if fj.exists():
            try:
                j = json.loads(fj.read_text(encoding="utf-8"))
            except Exception as e:
                row["final"] = f"JSON ERROR {e}"; rows.append(row); continue
            row["revision"] = j.get("revision", "")
            row["final"], row["ci"] = fmt_final(j)
            est = j.get("estimates", {}) or {}
            a = est.get("anchor")
            row["anchor"] = "" if a is None else a
            f = j.get("final", {})
            if "p" in f and isinstance(a, (int, float)):
                row["final_minus_anchor"] = f"{f['p'] - a:+.2f}"
            imp = j.get("impact") or {}
            if imp:
                row["ev_usd_per_share"] = imp.get("ev_stock_usd_per_share", "")
                row["material"] = imp.get("material", "")
        else:
            row["final"] = "MISSING"
        rows.append(row)
    out = PF / "forecast_table.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"wrote {out} ({len(rows)} rows)")
    for r in rows:
        print(f"{r['id']:4} {r['batch']:4} rev{str(r['revision']):2} {r['slug'][:36]:36} {str(r['final'])[:60]:60} ev={r['ev_usd_per_share']} mat={r['material']} {r['audit_only']}")


if __name__ == "__main__":
    main()
