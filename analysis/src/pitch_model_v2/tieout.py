from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
from . import spec as specmod
from . import decisions as decmod

def write(spec_path, targets_csv, decisions_path, out_md, check_paths: bool = True) -> Path:
    s = specmod.load(spec_path, check_paths=check_paths)
    decs = decmod.load(decisions_path) if Path(decisions_path).exists() else []
    by_key = {}
    for d in decs:
        by_key.setdefault((d.line, d.period, d.scenario), []).append(d.id)
    lines = ["# Tie-out — spec vs memo v3 / L4", "", "| line | period | scenario | spec | target | diff | diff % | source | explained by |", "|---|---|---|---|---|---|---|---|---|"]
    unexplained = 0
    with open(targets_csv, newline="") as f:
        for row in csv.DictReader(f):
            lid, p, sc = row["line"], row["period"], row["scenario"]
            ln = s.lines.get(lid)
            sv = None
            if ln and ln.kind == "input" and p in ln.values.get(sc, {}):
                sv = float(ln.values[sc][p])
            tv = float(row["value"])
            if sv is None:
                lines.append(f"| {lid} | {p} | {sc} | (formula or absent) | {tv} | | | {row['source']} | see workbook |"); continue
            diff = round(sv - tv, 4); pct = round(100 * diff / tv, 2) if tv else 0.0
            expl = ", ".join(by_key.get((lid, p, sc), [])) if abs(diff) > 1e-9 else "match"
            if expl == "":
                expl = "UNEXPLAINED"; unexplained += 1
            lines.append(f"| {lid} | {p} | {sc} | {sv} | {tv} | {diff} | {pct} | {row['source']} | {expl} |")
    lines += ["", f"Unexplained differences: {unexplained}"]
    out = Path(out_md); out.write_text("\n".join(lines) + "\n"); return out

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="model/pitch_model_v2/spec/lines.yaml")
    ap.add_argument("--targets", default="model/pitch_model_v2/spec/tieout_targets.csv")
    ap.add_argument("--decisions", default="docs/pitch-model-v2/DECISIONS.md")
    ap.add_argument("--out", default="docs/pitch-model-v2/TIEOUT.md")
    a = ap.parse_args(argv); print("wrote", write(a.spec, a.targets, a.decisions, a.out)); return 0

if __name__ == "__main__":
    sys.exit(main())
