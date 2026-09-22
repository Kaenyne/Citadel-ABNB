from __future__ import annotations
import json, re, sys
from pathlib import Path

HEADINGS = ["## 1. Header", "## 2. The number", "## 3. Derivation chain", "## 4. Governing sources",
            "## 5. Reproduction receipt", "## 6. Test record", "## 7. Kill list and consistency",
            "## 8. Open choices", "## 9. Judge Q&A", "## 10. Grade"]
GRADE_RE = re.compile(r"^Grade:\s*([ABC])\b", re.M)
RECEIPT_RE = re.compile(r"`(data/processed/pitch_model_v2/receipts/[^`]+/receipt\.json)`")
MATCH_RE = re.compile(r"\*\*Match:\s*(yes|no)\*\*", re.I)
QLINE_RE = re.compile(r"^\s*\d+\.\s*Q:", re.M)

def _section(text: str, heading: str, next_heading: str | None = None) -> str:
    i = text.find(heading)
    if i < 0:
        return ""
    start = i + len(heading)
    if next_heading is None:
        return text[start:]
    j = text.find(next_heading, start)
    if j < 0:
        return text[start:]
    return text[start:j]

def lint(path: str | Path, root: str | Path | None = None) -> list[str]:
    root = Path(root or Path.cwd()); text = Path(path).read_text(); msgs = []
    pos = 0
    for h in HEADINGS:
        i = text.find(h, pos)
        if i < 0:
            msgs.append(f"missing or out-of-order heading: {h}"); continue
        pos = i
    section10 = _section(text, "## 10. Grade")
    g = GRADE_RE.search(section10)
    if not g:
        msgs.append("no 'Grade: A|B|C' line under §10"); return msgs
    grade = g.group(1)
    if grade in ("A", "B"):
        section5 = _section(text, "## 5. Reproduction receipt", "## 6. Test record")
        r = RECEIPT_RE.search(section5); m = MATCH_RE.search(section5)
        if not r:
            msgs.append("grade A/B needs a receipt path in §5")
        else:
            rp = root / r.group(1)
            if not rp.exists():
                msgs.append(f"receipt not found: {r.group(1)}")
            else:
                rec = json.loads(rp.read_text())
                if rec.get("exit_code") != 0:
                    msgs.append(f"grade {grade} but receipt exit_code={rec.get('exit_code')}")
        if not m or m.group(1).lower() != "yes":
            msgs.append(f"grade {grade} needs '**Match: yes**' in §5")
    section9 = _section(text, "## 9. Judge Q&A", "## 10. Grade")
    if len(QLINE_RE.findall(section9)) < 3:
        msgs.append("§9 needs three judge questions")
    return msgs

if __name__ == "__main__":
    problems = lint(sys.argv[1])
    print("\n".join(problems) if problems else "dossier clean")
    sys.exit(1 if problems else 0)
