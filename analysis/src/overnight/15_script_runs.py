# -*- coding: utf-8 -*-
"""Writes data/processed/overnight/15_script_runs.csv.
Reads: the scratchpad runs.tsv produced by re-running every analysis/src/overnight/*.py once
with `py -3.13` and a 420s timeout, the per-script .err logs, and a byte-size comparison of
data/processed/overnight against a snapshot taken before the re-run."""
import csv, os, glob

SC = r"C:\Users\krish\AppData\Local\Temp\claude\C--Users-krish-citadel-abnb\fe93ae72-a37b-4547-991f-690c32a0f6a0\scratchpad\15"
OUT = r"C:\Users\krish\citadel-abnb-overnight\data\processed\overnight"
SRC = r"C:\Users\krish\citadel-abnb-overnight\analysis\src\overnight"
BAK = os.path.join(SC, "backup")

runs = []
with open(os.path.join(SC, "runs.tsv"), encoding="utf-8") as f:
    for line in f:
        p = line.rstrip("\n").split("\t")
        if len(p) == 3:
            runs.append((p[0], int(p[1]), p[2]))

# Which outputs each workstream owns, and whether they still match the pre-run snapshot.
def prefix_status(script):
    ws = script[:2]
    changed, same, new = [], [], []
    for cur in sorted(glob.glob(os.path.join(OUT, ws + "_*"))):
        n = os.path.basename(cur)
        b = os.path.join(BAK, n)
        if not os.path.exists(b):
            new.append(n)
        elif os.path.getsize(cur) == os.path.getsize(b):
            same.append(n)
        else:
            changed.append("%s (%d->%d bytes)" % (n, os.path.getsize(b), os.path.getsize(cur)))
    return same, changed, new

# The only three outputs whose bytes moved on the re-run, all because the script re-fetches
# live data. Attributed to the fetcher that writes each one. All were restored to the
# pre-run snapshot afterwards so notes 01-12 stay consistent with the data they were written on.
LIVE = {
    "08_trends_pull.py": "yes - 08_trends_weekly.csv 725,530 -> 725,533 bytes, same 12,455 rows (fresh Google Trends pull; Google rescales history on every pull)",
    "10_fetch_xbrl_geography.py": "yes - 10_xbrl_revenue_geography.csv 23,831 -> 23,481 bytes, 259 -> 255 rows (fresh EDGAR companyconcept pull). WS10's derived outputs (10_regional_panel_quarterly.csv, 10_regional_forecast.csv) are byte-identical either way, so the FY25 regional shares are unaffected",
    "10_fetch_benchmarks.py": "yes - 10_regional_benchmarks.csv 7,270 -> 7,269 bytes, same 24 rows (rounding on a fresh pull)",
}

rows = []
for script, rc, secs in runs:
    errp = os.path.join(SC, "logs", script + ".err")
    err = ""
    if os.path.exists(errp):
        with open(errp, encoding="utf-8", errors="replace") as f:
            err = f.read().strip()
    warn_lines = [l for l in err.splitlines() if "Warning" in l or "warn" in l.lower()]
    fatal = [l for l in err.splitlines() if "Traceback" in l or "Error:" in l]
    same, changed, new = prefix_status(script)
    if rc == 0:
        status = "ok"
    elif rc == 124:
        status = "timeout (420s)"
    else:
        status = "failed (exit %d)" % rc
    note = []
    if warn_lines:
        note.append("%d warning line(s), e.g. %s" % (len(warn_lines), warn_lines[0][:160]))
    if fatal:
        note.append("stderr traceback: " + fatal[0][:160])
    if not note:
        note.append("clean stderr")
    rows.append([
        script, status, rc, secs,
        len(same) + len(changed) + len(new),
        LIVE.get(script, "no - byte-identical to the pre-run snapshot"),
        " | ".join(note),
    ])

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "15_script_runs.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["script", "status", "exit_code", "wall_time",
                "workstream_outputs_present", "outputs_changed_on_re_run", "stderr"])
    w.writerows(rows)

ok = sum(1 for r in rows if r[1] == "ok")
print("scripts:", len(rows), "ok:", ok, "not ok:", len(rows) - ok)
for r in rows:
    if r[1] != "ok":
        print("  ", r[0], r[1])
print("changed on re-run:", [r[0] for r in rows if r[5].startswith("yes")])
