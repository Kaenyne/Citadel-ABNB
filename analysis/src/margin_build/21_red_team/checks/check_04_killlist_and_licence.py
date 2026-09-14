"""WS21 check 04: kill-list phrases, licensed-data leakage into tracked paths, and 'close to known' language.

1. Scans docs/margin-build/notes/*.md and data/processed/margin_build/**/*.{csv,md,json} for the
   AGENT_BRIEF section 6 kill-list strings and for phrases the standards ban.
2. Flags any tracked (committed) file under data/processed/margin_build that contains raw licensed
   vendor rows: a Bloomberg/FactSet/Third Bridge marker, or an LSEG per-broker/raw dump (as opposed to
   a derived consensus value with a vendor + timestamp, which is allowed).
3. Reports whether data/raw/margin_build is gitignored and whether any data/raw path is staged/tracked.

Usage: py -3.13 analysis/src/margin_build/21_red_team/checks/check_04_killlist_and_licence.py
"""
from __future__ import annotations
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
NOTES = REPO / "docs" / "margin-build"
PROC = REPO / "data" / "processed" / "margin_build"

KILL = [
    (r"-?3\.4\s*pp.{0,40}FX", "the -3.4pp Q4 FX step"),
    (r"82\s*%.{0,40}(FX|determined)", "'82% of Q4 FX already determined'"),
    (r"\+?4\.05\s*%", "'+4.05% fee uplift' as measured"),
    (r"9\s*/\s*9.{0,60}(drift|below[- ]Street)", "the 9/9 guide-below-Street drift rule"),
    (r"half of ADR growth", "'half of ADR growth is bigger units'"),
    (r"nothing beats guide\s*[x×*]\s*cushion", "'nothing beats guide x cushion'"),
    (r"hierarchical cushion", "M5's hierarchical cushion model"),
    (r"120[- ]market panel", "the 120-market panel as a nights measurement"),
    (r"1\.71\s*M quote panel.{0,40}fee[- ]inclusive", "the 1.71M quote panel as fee-inclusive"),
    (r"Stan state space", "the Stan state space for the prelim"),
]
BANNED_LANGUAGE = [
    (r"close to known", "a quarter described as 'close to known'"),
    (r"essentially known", "a quarter described as 'essentially known'"),
    (r"already (?:effectively )?(?:known|locked)", "a quarter described as already known/locked"),
]
LICENCE = [
    (r"bbg_extracted_long", "Bloomberg extract filename"),
    (r"BEST_(SALES|EBITDA|EPS)", "Bloomberg BEST_* field"),
    (r"third\s*bridge", "Third Bridge"),
    (r"factset", "FactSet"),
    (r"broker_name|analyst_name|per_broker|estimate_detail", "per-broker vendor detail"),
]


def scan(paths, patterns, label):
    hits = []
    for p in paths:
        try:
            txt = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for rx, desc in patterns:
            for m in re.finditer(rx, txt, flags=re.I):
                line = txt[:m.start()].count("\n") + 1
                ctx = txt[max(0, m.start() - 70):m.end() + 70].replace("\n", " ")
                hits.append((label, str(p.relative_to(REPO)), line, desc, ctx))
    return hits


def main() -> int:
    notes = sorted(NOTES.rglob("*.md"))
    proc = [p for p in PROC.rglob("*") if p.suffix.lower() in (".csv", ".md", ".json") and p.is_file()]
    code = sorted((REPO / "analysis" / "src" / "margin_build").rglob("*.py"))
    hits = scan(notes + code, KILL, "KILL") + scan(notes, BANNED_LANGUAGE, "LANGUAGE") + \
        scan(notes + proc, LICENCE, "LICENCE")
    if not hits:
        print("no kill-list phrase, banned-language phrase or licensed-data marker found "
              f"in {len(notes)} notes, {len(code)} scripts, {len(proc)} processed files")
    for lab, f, ln, desc, ctx in hits:
        print(f"[{lab}] {f}:{ln}  {desc}\n        ...{ctx}...")
    print("\n--- data/raw exposure ---")
    r = subprocess.run(["git", "ls-files", "data/raw"], cwd=REPO, capture_output=True, text=True)
    tracked = [x for x in r.stdout.splitlines() if x.strip()]
    print(f"tracked files under data/raw: {len(tracked)}")
    for x in tracked[:20]:
        print("   ", x)
    r2 = subprocess.run(["git", "check-ignore", "-v", "data/raw/margin_build/M7_below_ebitda/fred_DTB3.csv"],
                        cwd=REPO, capture_output=True, text=True)
    print("check-ignore on an M7 raw pull:", (r2.stdout.strip() or "NOT IGNORED"))
    r3 = subprocess.run(["git", "status", "--porcelain", "data/processed/margin_build",
                         "analysis/src/margin_build", "docs/margin-build"], cwd=REPO, capture_output=True, text=True)
    print(f"uncommitted margin_build paths: {len(r3.stdout.splitlines())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
