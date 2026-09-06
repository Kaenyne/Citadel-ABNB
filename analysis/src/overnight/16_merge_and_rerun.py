# 16_merge_and_rerun.py
#
# Workstream 16 (web gap fill). Applies the consensus cells recovered by web research
# to a COPY of WS04's consensus file, then re-runs WS04's reaction script unmodified
# (source-patched only for filenames) so 04's own outputs are never overwritten.
#
# READS
#   data/processed/overnight/04_consensus_at_print.csv   (WS04, untouched)
#   data/processed/overnight/16_consensus_additions.csv  (this workstream, hand-built from sources)
#   analysis/src/overnight/04_reaction_vs_consensus.py   (executed with patched filenames)
#
# WRITES
#   data/processed/overnight/16_consensus_at_print_merged.csv
#   data/processed/overnight/16_reaction_panel.csv
#   data/processed/overnight/16_reaction_tests.csv
#   data/processed/overnight/16_q3_2026_breakeven.csv
#   data/processed/overnight/16_rerun_delta.csv          (04 vs 16 test-by-test comparison)
#
# Every added cell carries a source URL and a verbatim quote in 16_consensus_additions.csv.

import os
import pandas as pd
import numpy as np

ROOT = r"C:\Users\krish\citadel-abnb-overnight"
DP = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(DP, "overnight")
SRC = os.path.join(ROOT, "analysis", "src", "overnight")

# ---------------------------------------------------------------- merge
base = pd.read_csv(os.path.join(OUT, "04_consensus_at_print.csv"))
add = pd.read_csv(os.path.join(OUT, "16_consensus_additions.csv"))

base = base.set_index("print_quarter")
applied = []
for _, r in add.iterrows():
    q, col, val = r["print_quarter"], r["column"], r["new_value"]
    if q not in base.index:
        raise SystemExit(f"unknown quarter {q}")
    if col not in base.columns:
        raise SystemExit(f"unknown column {col}")
    old = base.at[q, col]
    # numeric columns get floats, text columns stay text
    try:
        val_cast = float(val)
        if col in ("guide_vs_street_sign",):
            val_cast = float(val_cast)
    except (TypeError, ValueError):
        val_cast = val
    base.at[q, col] = val_cast
    applied.append((q, col, old, val_cast))

# derived cells that WS04 computes rather than sources
for q in add["print_quarter"].unique():
    gm = base.at[q, "next_q_guide_mid_musd"]
    st = base.at[q, "next_q_cons_revenue_musd"]
    if pd.notna(gm) and pd.notna(st) and pd.isna(base.at[q, "guide_vs_street_pct"]):
        base.at[q, "guide_vs_street_pct"] = round((gm / st - 1.0) * 100.0, 3)
        base.at[q, "guide_vs_street_sign"] = 1.0 if gm >= st else -1.0

base = base.reset_index()
merged_path = os.path.join(OUT, "16_consensus_at_print_merged.csv")
base.to_csv(merged_path, index=False)
print(f"merged file written: {merged_path}")
for q, col, old, new in applied:
    print(f"  {q:8s} {col:28s} {old!r:>12} -> {new!r}")

# ---------------------------------------------------------------- re-run WS04 on the merged copy
src = open(os.path.join(SRC, "04_reaction_vs_consensus.py"), encoding="utf-8").read()
patched = (src
           .replace('"04_consensus_at_print.csv"', '"16_consensus_at_print_merged.csv"')
           .replace('"04_reaction_panel.csv"', '"16_reaction_panel.csv"')
           .replace('"04_reaction_tests.csv"', '"16_reaction_tests.csv"')
           .replace('"04_q3_2026_breakeven.csv"', '"16_q3_2026_breakeven.csv"'))
assert "16_consensus_at_print_merged.csv" in patched
ns = {"__name__": "__main__", "__file__": os.path.join(SRC, "04_reaction_vs_consensus.py")}
exec(compile(patched, "04_reaction_vs_consensus.py(patched)", "exec"), ns)

# ---------------------------------------------------------------- compare
a = pd.read_csv(os.path.join(OUT, "04_reaction_tests.csv"))
b = pd.read_csv(os.path.join(OUT, "16_reaction_tests.csv"))
keys = [c for c in ("block", "target", "label", "spec", "test") if c in a.columns]
num = [c for c in a.columns if a[c].dtype.kind in "fi" and c in b.columns]
m = a.merge(b, on=keys, suffixes=("_04", "_16"), how="outer")
rows = []
for _, r in m.iterrows():
    changed = {}
    for c in num:
        x, y = r.get(c + "_04"), r.get(c + "_16")
        if pd.isna(x) and pd.isna(y):
            continue
        if pd.isna(x) or pd.isna(y) or abs(float(x) - float(y)) > 1e-6:
            changed[c] = (x, y)
    if changed:
        row = {k: r[k] for k in keys}
        for c, (x, y) in changed.items():
            row[c + "_04"] = x
            row[c + "_16"] = y
        rows.append(row)
delta = pd.DataFrame(rows)
delta.to_csv(os.path.join(OUT, "16_rerun_delta.csv"), index=False)
print(f"\n{len(delta)} of {len(a)} tests changed; delta -> 16_rerun_delta.csv")
