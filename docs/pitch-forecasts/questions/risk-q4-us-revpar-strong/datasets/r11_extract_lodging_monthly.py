"""R11 revision 2 (A12-03 fix): build the US monthly hotel RevPAR y/y series BY PARSING the saved
Lodging Magazine reprints of CoStar's monthly US release, instead of typing a list into the model.

Input : ../sources/lodging_monthly/*.html   (58 snapshots, fetched 2026-09-17, each carrying its own
        publication date and CoStar's "U.S. Hotel Performance <Month> <Year>" block)
Output: us_revpar_monthly_yoy_measured.csv  (one row per month actually found, with the file it came from)
        r11_extract_report.txt             (every file, what was found, and why a file was rejected)

Run:   py -3.13 docs/pitch-forecasts/questions/risk-q4-us-revpar-strong/datasets/r11_extract_lodging_monthly.py
Stdlib only. Writes nothing outside this directory.
"""
import re, csv, json, os
from pathlib import Path

HERE = Path(os.path.dirname(os.path.abspath(__file__)))
SRC = HERE.parent / "sources" / "lodging_monthly"

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]
MNUM = {m: i + 1 for i, m in enumerate(MONTHS)}


def text_of(path):
    h = path.read_text(encoding="utf-8", errors="ignore")
    h = re.sub(r"<script.*?</script>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<style.*?</style>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<[^>]+>", " ", h)
    h = h.replace("&#8217;", "'").replace("&nbsp;", " ").replace("&amp;", "&")
    h = re.sub(r"&#\d+;", " ", h)
    return re.sub(r"\s+", " ", h)


# Lodging reprints CoStar's MONTHLY US release in four templates that differ only in chrome:
#   lead      "... according to October 2025 data from CoStar."            (every monthly; weeklies
#             instead say "according to CoStar's latest data through October 19, 2024")
#   header    "U.S. Hotel Performance October 2025" or just "January 2024"
#   base line "Percentage change from October 2024" / "(percentage change from July 2025)"
#   RevPAR    "RevPAR: $110.35 (down 0.9 percent)" | "RevPAR : $119.77 (up 8.2 percent)"
#             | "RevPAR: $106.30 (+0.1%)" | "RevPAR: $111.18 (flat)"
# Anchoring on the LEAD sentence is what dates the observation and what rejects the weeklies and the
# monthly P&L (GOPPAR/TRevPAR) release; the month-over-month base line is then required as a second gate.
# "according to October 2025 data from CoStar" and "according to August 2023 hotel performance data
# from CoStar" are the two wordings; up to three filler words are allowed between year and "data".
LEAD = re.compile(r"according to\s+(" + "|".join(MONTHS) + r")\s+(20\d\d)\s+(?:\w+\s+){0,3}data from\s+CoStar", re.I)
# the September-2024 reprint carries a typo, "Percentage change from September 202)", so the year is
# optional here; the weeklies are already excluded by the LEAD gate ("latest data through <date>").
IS_MONTHLY = re.compile(r"percentage change from\s+(" + "|".join(MONTHS) + r")\s*(20\d{0,3})", re.I)
REVPAR = re.compile(r"(?<![A-Za-z])RevPAR\s*:\s*\$?([\d,.]+)\s*\(([^)]{0,40})\)", re.I)
OCC = re.compile(r"Occupancy:\s*([\d.]+)\s*percent\s*\(([^)]{0,40})\)", re.I)
ADR = re.compile(r"(?<![A-Za-z])ADR\s*:\s*\$?([\d,.]+)\s*\(([^)]{0,40})\)", re.I)
PUB = re.compile(r"By\s+LODGING Staff\s+(" + "|".join(MONTHS) + r")\s+(\d{1,2}),\s*(20\d\d)")


def pct(paren):
    """'down 0.9 percent' | 'up 8.2 percent' | 'flat' | '+0.1%' | '-2.3%' -> signed float or None."""
    s = paren.strip().lower()
    if s.startswith("flat"):
        return 0.0
    m = re.match(r"(up|down)\s*([\d.]+)\s*percent", s)
    if m:
        v = float(m.group(2))
        return -v if m.group(1) == "down" else v
    m = re.match(r"([+-])\s*([\d.]+)\s*%", s)
    if m:
        v = float(m.group(2))
        return -v if m.group(1) == "-" else v
    return None


rows, report = [], []
for p in sorted(SRC.glob("*.html")):
    t = text_of(p)
    lead = LEAD.search(t)
    if not lead:
        why = "no '... according to <Month> <Year> data from CoStar' lead: weekly release, P&L/GOPPAR release or a non-release article"
        report.append((p.name, "REJECT", why))
        continue
    month_name, year = lead.group(1), lead.group(2)
    tail = t[lead.end():lead.end() + 900]
    base = IS_MONTHLY.search(tail)
    if not base:
        report.append((p.name, "REJECT", "no 'percentage change from <Month> <Year>' month-over-month base line"))
        continue
    rp = REVPAR.search(tail)
    if not rp or pct(rp.group(2)) is None:
        report.append((p.name, "REJECT", "no parsable US RevPAR line after the header"))
        continue
    occ, adr, pub = OCC.search(tail), ADR.search(tail), PUB.search(t)
    pub_date = ("%s-%02d-%02d" % (pub.group(3), MNUM[pub.group(1).capitalize()], int(pub.group(2)))
                if pub else "")
    key = "%s-%02d" % (year, MNUM[month_name.capitalize()])
    # sanity: the release is published after the month it covers, and US aggregate RevPAR is $60-$140
    revpar_usd = float(rp.group(1).replace(",", ""))
    if pub_date and pub_date[:7] <= key:
        report.append((p.name, "REJECT", "published %s, before %s closed: not the monthly release" % (pub_date, key)))
        continue
    if not (55.0 <= revpar_usd <= 145.0):
        report.append((p.name, "REJECT", "RevPAR $%.2f outside the US aggregate range: a market or a different metric" % revpar_usd))
        continue
    rows.append(dict(
        month=key,
        revpar_yoy_pct=round(pct(rp.group(2)), 2),
        revpar_usd=revpar_usd,
        adr_yoy_pct=pct(adr.group(2)) if adr else None,
        occ_yoy_pct=pct(occ.group(2)) if occ else None,
        published=pub_date,
        snapshot="sources/lodging_monthly/" + p.name))
    report.append((p.name, "OK", "%s RevPAR $%.2f %+0.1f%%" % (key, revpar_usd, pct(rp.group(2)))))

# de-duplicate: a month can appear in more than one snapshot (a revision or a re-post). Keep the
# EARLIEST published snapshot, and record any disagreement.
by_month, dupes = {}, []
for r in sorted(rows, key=lambda r: (r["month"], r["published"])):
    if r["month"] in by_month:
        prev = by_month[r["month"]]
        if abs(prev["revpar_yoy_pct"] - r["revpar_yoy_pct"]) > 0.05:
            dupes.append((r["month"], prev["revpar_yoy_pct"], prev["snapshot"],
                          r["revpar_yoy_pct"], r["snapshot"]))
        continue
    by_month[r["month"]] = r

out = [by_month[k] for k in sorted(by_month)]
with (HERE / "us_revpar_monthly_yoy_measured.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["month", "revpar_yoy_pct", "revpar_usd", "adr_yoy_pct",
                                      "occ_yoy_pct", "published", "snapshot"])
    w.writeheader()
    w.writerows(out)

with (HERE / "r11_extract_report.txt").open("w", encoding="utf-8") as f:
    f.write("A12 response / R11 revision 2: parse of %d saved Lodging Magazine snapshots\n" % len(list(SRC.glob("*.html"))))
    f.write("months extracted: %d  (%s to %s)\n\n" % (len(out), out[0]["month"], out[-1]["month"]))
    for name, status, why in report:
        f.write("%-6s %-88s %s\n" % (status, name, why))
    if dupes:
        f.write("\nmonths appearing twice with different values:\n")
        for d in dupes:
            f.write("  %s: %.1f (%s) vs %.1f (%s)\n" % d)
    else:
        f.write("\nno month appears twice with a different value\n")

print("months extracted:", len(out))
for r in out:
    print("  %s  RevPAR %+6.1f%%  $%7.2f  pub %s" % (r["month"], r["revpar_yoy_pct"], r["revpar_usd"], r["published"]))
print("rejected files:", sum(1 for _, s, _ in report if s == "REJECT"))
print(json.dumps({"n_months": len(out), "dupes": dupes}, indent=1))
