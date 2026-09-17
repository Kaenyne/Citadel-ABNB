"""Disk-truth state for the pitch-forecasts run.

Usage: py -3.13 analysis/src/pitch_forecasts/state.py [--json]

For each batch in docs/pitch-forecasts/batches.json, reports which stage is complete based on files present:
  forecast : every question in the batch has questions/<slug>/research-log.md and forecasts/2026-09-17-forecast.json
  audit    : docs/pitch-forecasts/audits/<batch>-research-audit.md exists and audits/<batch>.done exists
  response : every question's research-log.md contains "revision: 2" (or "Revision 2") and
             docs/pitch-forecasts/audits/<batch>-audit-response.md exists
Prints the next pending stage per batch. Never writes.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PF = ROOT / "docs" / "pitch-forecasts"
QREG = PF / "QUESTIONS.md"
BATCHES = json.loads((PF / "batches.json").read_text(encoding="utf-8"))


def slugs():
    txt = QREG.read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^\| (\w\d\d) \| ([a-z0-9\-]+) \|", txt, flags=re.M):
        out[m.group(1)] = m.group(2)
    return out


def main():
    S = slugs()
    rows = []
    for batch, qids in BATCHES.items():
        fc_ok = True
        rev2_ok = True
        missing = []
        for q in qids:
            slug = S.get(q)
            if slug is None:
                fc_ok = False; rev2_ok = False; missing.append(f"{q}:no-slug"); continue
            qd = PF / "questions" / slug
            log = qd / "research-log.md"
            fj = qd / "forecasts" / "2026-09-17-forecast.json"
            if not (log.exists() and fj.exists()):
                fc_ok = False; missing.append(f"{q}:{'log' if not log.exists() else 'json'}")
                rev2_ok = False
                continue
            t = log.read_text(encoding="utf-8", errors="replace")
            if not re.search(r"revision:\s*2|Revision 2|revision 2", t, flags=re.I):
                rev2_ok = False
        audit = PF / "audits" / f"{batch}-research-audit.md"
        done = PF / "audits" / f"{batch}.done"
        resp = PF / "audits" / f"{batch}-audit-response.md"
        audit_ok = audit.exists() and done.exists() and audit.stat().st_size > 500
        resp_ok = resp.exists() and rev2_ok
        if not fc_ok:
            stage = "forecast"
        elif not audit_ok:
            stage = "audit"
        elif not resp_ok:
            stage = "response"
        else:
            stage = "done"
        rows.append({"batch": batch, "questions": qids, "forecast": fc_ok, "audit": audit_ok,
                     "response": resp_ok, "next": stage, "missing": missing})
    if "--json" in sys.argv:
        print(json.dumps(rows, indent=1))
        return
    print(f"{'batch':6} {'questions':22} {'forecast':9} {'audit':6} {'response':9} next")
    for r in rows:
        print(f"{r['batch']:6} {','.join(r['questions']):22} {str(r['forecast']):9} {str(r['audit']):6} {str(r['response']):9} {r['next']}  {' '.join(r['missing'])}")
    pending = [r for r in rows if r["next"] != "done"]
    print(f"\n{len(rows) - len(pending)} of {len(rows)} batches done; next stages: " +
          ", ".join(f"{r['batch']}:{r['next']}" for r in pending))


if __name__ == "__main__":
    main()
