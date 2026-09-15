"""WS05 (margin build, 13-14 Sep 2026): management statements v2 and the November guide-language pattern.

Rebuilds every output from raw text. Extends workstream 31a (194 statements from letters, earnings calls and
five conferences) with (i) every investor-conference appearance reachable on stockanalysis.com, including
Goldman Communacopia 8 Sep 2026, (ii) the 10-K and 10-Q MD&A cost commentary (all 17 10-Qs 1Q21-2Q26 pulled from
EDGAR), (iii) the non-earnings 8-Ks with cost content (Italian tax settlement, the 2021 converts, the Mar 2026
notes), and (iv) earnings-call sentences 31a left out. It then builds the pattern of how the November print
words the full-year margin guide and what Q4 margin that sentence implies.

Reads (raw; nothing here is modified)
  data/raw/letters/<q>Q<yy>_*.htm                         23 shareholder letters 4Q20..2Q26
  data/raw/regulatory/transcripts/<yyyy>-Q<n>.pdf|.json    FactSet corrected transcripts 1Q23..1Q26
  data/raw/transcripts/web/<tag>.html                      stockanalysis.com: 4Q20..4Q22 and 2Q26 calls, 5 conferences
  data/raw/margin_build/05_mgmt_statements_v2/web/         GS26 (Communacopia 2026) + two 2021 product events (pulled 14 Sep 2026)
  data/raw/margin_build/05_mgmt_statements_v2/10q/         17 10-Qs 1Q21..2Q26 (EDGAR, pulled 14 Sep 2026)
  data/raw/margin_build/05_mgmt_statements_v2/8k/          8 non-earnings 8-Ks
  data/raw/filings/txt/abnb_10k_FY20xx.txt                 10-Ks FY2020..FY2025
  data/processed/overnight/31a_mgmt_margin_statements.csv  the 194 rows this file is a superset of (ids kept)
  data/processed/overnight/02_guidance_ledger.csv          letter guides (Q4 revenue ranges, FY margin sentences)
  data/processed/abnb_quarterly_costlines.csv              quarterly revenue, adj. EBITDA, cost lines 1Q20..2Q26
  data/processed/abnb_fcf_bridge.csv                       FY free-cash-flow margins

Writes  data/processed/margin_build/05_mgmt_statements_v2/
  05_statements.csv              superset: 194 31a rows (ids kept) + new hand-verified rows + 10-Q MD&A rows
  05_guide_language_pattern.csv  one row per print 3Q21..2Q26: FY sentence, type, Q4 revenue guide, implied Q4 margin, actuals
  05_guide_language_stats.csv    beat-vs-floor / beat-vs-point distributions
  05_nov2026_scenarios.csv       what each candidate 5 Nov 2026 sentence implies for the 4Q26 margin
  05_fy27_hints.csv              everything said that bears on FY27 costs
  05_reliability_by_line.csv     kept / partly / missed by line, and mean miss where a number was guided
  05_reliability_by_event.csv    the same by event type and speaker

Quote discipline: every new `verbatim` is checked to be an exact substring of its source document after whitespace
normalisation (curly quotes/dashes -> ASCII). Failures are printed and the script exits 1. 31a rows keep 31a's
own verification flag. Verbatims are capped at 300 characters. stockanalysis transcripts are audio-aligned, not
corrector-reviewed; those rows carry confidence <= medium on wording.

Run (from the worktree root):  py -3.13 analysis/src/margin_build/05_mgmt_statements_v2/run.py
Needs: pandas; pdftotext on PATH (falls back to the pypdf JSON next to each PDF if it is not).
Free parameters: 0 fitted. Judgement calls: verdicts, line mapping, the 3Q26 margin assumption in the scenario table (stated).
"""
import csv
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
RAW5 = ROOT / "data" / "raw" / "margin_build" / "05_mgmt_statements_v2"
OUT = ROOT / "data" / "processed" / "margin_build" / "05_mgmt_statements_v2"
OUT.mkdir(parents=True, exist_ok=True)

# ------------------------------------------------------------------------------------------------ text helpers
TAGRE = re.compile(r"<[^>]+>")


def norm(s):
    s = s.replace(" ", " ")
    s = (s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
          .replace("–", "-").replace("—", "-").replace("�", "-"))
    return re.sub(r"\s+", " ", s).strip()


def detag(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|div|h\d|li|tr)>", "\n", s, flags=re.I)
    s = TAGRE.sub(" ", s)
    return html.unescape(s)


def pdf_text(path):
    """FactSet PDF -> text. pdftotext (UTF-8, layout) as 31a did; else the pypdf JSON WS-regulatory wrote."""
    if shutil.which("pdftotext"):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as fh:
            tmp = Path(fh.name)
        subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(path), str(tmp)], check=True)
        txt = tmp.read_text(encoding="utf-8", errors="replace")
        tmp.unlink(missing_ok=True)
        return txt
    js = path.with_suffix(".json")
    if js.exists():
        return "\n".join(p["text"] for p in json.loads(js.read_text(encoding="utf-8")))
    raise FileNotFoundError(f"no pdftotext and no JSON for {path}")


def parse_sa(raw):
    """stockanalysis.com transcript page -> [(speaker, title, text)]."""
    m = re.search(r'id="transcript-panel-full"(.*?)(?:id="transcript-panel|<footer)', raw, re.S)
    body = m.group(1) if m else raw
    out = []
    for b in re.split(r'<div class="border-t border-sharp pt-5 first:border-t-0 first:pt-0">', body)[1:]:
        sm = re.search(r'<div class="text-lg font-bold[^"]*">(.*?)</div>', b, re.S)
        if not sm:
            continue
        speaker = norm(detag(sm.group(1)))
        tm = re.search(r'<div class="text-sm italic text-muted">(.*?)</div>', b, re.S)
        title = norm(detag(tm.group(1))) if tm else ""
        sents = re.findall(r'<span class="transcript-sentence[^"]*"[^>]*>(.*?)</span>', b, re.S)
        text = norm(" ".join(detag(s) for s in sents))
        if text:
            out.append((speaker, title, text))
    return out


# ------------------------------------------------------------------------------------------------ calendar
PRINT_DATE = {
    "4Q20": "2021-02-25", "1Q21": "2021-05-13", "2Q21": "2021-08-12", "3Q21": "2021-11-04",
    "4Q21": "2022-02-15", "1Q22": "2022-05-03", "2Q22": "2022-08-02", "3Q22": "2022-11-01",
    "4Q22": "2023-02-14", "1Q23": "2023-05-09", "2Q23": "2023-08-03", "3Q23": "2023-11-01",
    "4Q23": "2024-02-13", "1Q24": "2024-05-08", "2Q24": "2024-08-06", "3Q24": "2024-11-07",
    "4Q24": "2025-02-13", "1Q25": "2025-05-01", "2Q25": "2025-08-06", "3Q25": "2025-11-06",
    "4Q25": "2026-02-12", "1Q26": "2026-05-07", "2Q26": "2026-08-06",
}
CONF_DATE = {"MS23": "2023-03-07", "MS24": "2024-03-05", "BERN24": "2024-05-30", "GS24": "2024-09-10",
             "GS25": "2025-09-09", "GS26": "2026-09-08", "SPEC6516": "2021-05-24", "SPEC10758": "2021-11-09"}
CONF_NAME = {"MS23": "Morgan Stanley TMT 2023", "MS24": "Morgan Stanley TMT 2024",
             "BERN24": "Bernstein Strategic Decisions 2024", "GS24": "Goldman Communacopia 2024",
             "GS25": "Goldman Communacopia 2025", "GS26": "Goldman Communacopia 2026",
             "SPEC6516": "Airbnb 2021 Summer Release (product event)", "SPEC10758": "Airbnb 2021 Winter Release (product event)"}
TENQ_DATE = {"1Q21": "2021-05-14", "2Q21": "2021-08-13", "3Q21": "2021-11-05", "1Q22": "2022-05-09", "2Q22": "2022-08-03",
             "3Q22": "2022-11-03", "1Q23": "2023-05-09", "2Q23": "2023-08-03", "3Q23": "2023-11-01", "1Q24": "2024-05-08",
             "2Q24": "2024-08-06", "3Q24": "2024-11-07", "1Q25": "2025-05-01", "2Q25": "2025-08-06", "3Q25": "2025-11-06",
             "1Q26": "2026-05-07", "2Q26": "2026-08-06"}
TENK_DATE = {"FY2020": "2021-02-26", "FY2021": "2022-02-25", "FY2022": "2023-02-17", "FY2023": "2024-02-16",
             "FY2024": "2025-02-13", "FY2025": "2026-02-12"}
SA_URL = "https://stockanalysis.com/stocks/abnb/transcripts/"
SA_SLUG = {"GS26": "739626-goldman-sachs-communacopia-technology-conference-2026",
           "SPEC10758": "10758-special-announcement", "SPEC6516": "6516-special-announcement",
           "MS23": "57627-morgan-stanley-technology-media-telecom-conference",
           "MS24": "171572-morgan-stanley-s-technology-media-telecom-conference-2024",
           "BERN24": "196271-bernstein-s-40th-annual-strategic-decisions-conference",
           "GS24": "228753-goldman-sachs-communacopia-technology-conference",
           "GS25": "382567-goldman-sachs-communicopia-technology-conference-2025"}


def build_corpus():
    docs = {}
    for p in sorted((ROOT / "data/raw/letters").glob("*.htm")):
        tag = p.name.split("_")[0]
        docs[f"letter:{tag}"] = {"raw": f"data/raw/letters/{p.name}", "text": norm(detag(p.read_text(encoding="utf-8", errors="replace")))}
    reg = ROOT / "data/raw/regulatory/transcripts"
    for yy in ("23", "24", "25", "26"):
        for q in "1234":
            tag, per = f"{q}Q{yy}", f"20{yy}-Q{q}"
            if (reg / f"{per}.pdf").exists():
                docs[f"call:{tag}"] = {"raw": f"data/raw/regulatory/transcripts/{per}.pdf", "text": norm(pdf_text(reg / f"{per}.pdf"))}
    for p in sorted((ROOT / "data/raw/transcripts/web").glob("*.html")):
        tag = p.stem
        key = f"conf:{tag}" if tag in CONF_DATE else f"call:{tag}"
        if key in docs:
            continue
        turns = parse_sa(p.read_text(encoding="utf-8", errors="replace"))
        docs[key] = {"raw": f"data/raw/transcripts/web/{p.name}", "text": " ".join(t[2] for t in turns), "turns": turns}
    for p in sorted((RAW5 / "web").glob("*.html")):
        turns = parse_sa(p.read_text(encoding="utf-8", errors="replace"))
        docs[f"conf:{p.stem}"] = {"raw": f"data/raw/margin_build/05_mgmt_statements_v2/web/{p.name} | {SA_URL}{SA_SLUG[p.stem]}/",
                                  "text": " ".join(t[2] for t in turns), "turns": turns}
    for p in sorted((ROOT / "data/raw/filings/txt").glob("abnb_10k_FY*.txt")):
        docs[f"10k:{p.stem[-6:]}"] = {"raw": f"data/raw/filings/txt/{p.name}", "text": norm(p.read_text(encoding="utf-8", errors="replace"))}
    for p in sorted((RAW5 / "10q").glob("*.htm")):
        body = detag(p.read_text(encoding="utf-8", errors="replace"))
        paras = [norm(x) for x in body.split("\n") if len(x.split()) > 6]
        docs[f"10q:{p.name[4:8]}"] = {"raw": f"data/raw/margin_build/05_mgmt_statements_v2/10q/{p.name} | https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001559720&type=10-Q",
                                      "text": norm(body), "paras": paras}
    for p in sorted((RAW5 / "8k").glob("*.htm")):
        docs[f"8k:{p.name[3:13]}"] = {"raw": f"data/raw/margin_build/05_mgmt_statements_v2/8k/{p.name} | https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001559720&type=8-K",
                                      "text": norm(detag(p.read_text(encoding="utf-8", errors="replace")))}
    return docs


# ------------------------------------------------------------------------------------------------ 31a -> v2 schema
LINE_MAP = {"total_margin": "margin_total", "brand_marketing": "sm_brand", "field_ops": "sm_field", "cost_of_revenue": "cor",
            "ops_support": "ops", "product_dev": "pd", "g_and_a": "ga", "sbc": "sbc", "take_rate": "take_rate", "fx": "other",
            "other": "other"}
LINE_OVERRIDE = {  # 31a filed these under the P&L line; the v2 taxonomy has finer buckets
    "S140": "ai", "S155": "ai", "S162": "ai", "S168": "ai", "S167": "capex", "S181": "capex",
    "S148": "tax", "S157": "tax", "S103": "tax", "S134": "tax",
}
NEXT_Q = {"4Q": "1Q", "1Q": "2Q", "2Q": "3Q", "3Q": "4Q"}


def period_from(print_tag, horizon, quote):
    yrs = [int(y) for y in re.findall(r"\b(20[2-3]\d)\b", quote)]
    if print_tag in PRINT_DATE:
        q, yy = print_tag[:2], 2000 + int(print_tag[2:])
        fy = yy + 1 if q == "4Q" else yy
        if horizon == "next-quarter":
            nq = NEXT_Q[q]
            return f"{nq}{(yy + 1) % 100:02d}" if q == "4Q" else f"{nq}{yy % 100:02d}"
        if horizon == "full-year":
            fut = [y for y in yrs if y >= fy]
            return f"FY{fut[0]}" if fut else f"FY{fy}"
    if horizon in ("multi-year", "structural"):
        fut = [y for y in yrs if y >= 2021]
        return f"FY{fut[0]}+" if fut and horizon == "multi-year" else horizon
    return horizon


def load_31a():
    rows = []
    with (ROOT / "data/processed/overnight/31a_mgmt_margin_statements.csv").open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            src = r["source"]
            et = "letter" if src == "letter" else ("conference" if src.startswith("conference") else "earnings_call")
            line = LINE_OVERRIDE.get(r["statement_id"], LINE_MAP[r["cost_line"]])
            ev = r["print"] if r["print"] in PRINT_DATE else CONF_NAME.get(r["print"], r["print"])
            rows.append({
                "statement_id": r["statement_id"], "date": r["date"], "event_type": et, "event": ev,
                "source_detail": src, "speaker": r["speaker"], "line": line, "line_31a": r["cost_line"],
                "period_referenced": period_from(r["print"], r["horizon"], r["quote"]), "horizon": r["horizon"],
                "direction": r["implied_direction_for_margin"], "quantified": r["quantified"], "value": "", "unit": "",
                "verbatim": r["quote"][:300], "quote_verified": r["quote_verified"], "source_path_or_url": r["source_file"],
                "locator": r["locator"], "confidence": "high" if not src.endswith("-sa") else "medium",
                "verdict": r["verdict"], "kept_or_missed": f'{r["verdict"]}: {r["outcome_if_closed"]}' if r["verdict"] in ("kept", "partly", "missed") else r["verdict"],
                "implied_metric": r["implied_metric"], "theme": r["theme"], "origin": "31a",
            })
    return rows


# ------------------------------------------------------------------------------------------------ new hand rows
# (id, doc, speaker, line, period, horizon, direction(+/-/0 for margin), quantified, value, unit, verbatim, confidence,
#  verdict, outcome, implied_metric, theme)
NEW = [
 # ---- conferences ---------------------------------------------------------------------------------------------
 ("V001", "conf:MS23", "Brian Chesky", "sm_perf", "FY2019", "structural", "+", "yes", 1000, "usd_m per year",
  "We were spending about $1 billion a year on marketing. The vast majority was performance marketing",
  "medium", "kept", "FY2019 S&M $1,622m incl. payroll (10-K FY2020); the performance-marketing majority is consistent with the 2019 cost structure. Statement of the pre-2020 baseline the reset was measured against.",
  "pre-pandemic marketing ~$1bn, mostly performance", "marketing_reset"),
 ("V002", "conf:MS23", "Brian Chesky", "sm_perf", "structural", "structural", "+", "no", "", "",
  "We were spending a lot of money on performance marketing, which is basically selling our product as a commodity.",
  "medium", "kept", "Performance marketing has stayed the minority of spend (S174, Bernstein May 2024; 'nearly 90% of traffic direct or organic', GS26).",
  "performance marketing stays a minority channel", "marketing_reset"),
 ("V003", "conf:MS24", "Ellie Mertz", "pd", "multi-year", "multi-year", "0", "no", "", "",
  "there's, you know, a time horizon ahead of us that's not tomorrow in terms of, realizing those efficiencies",
  "medium", "kept", "AI productivity in product development explicitly not near-term; PD % of revenue rose 17.36 (FY23) -> 18.52 (FY24) -> 19.23 (FY25) -> 20.84 (1H26). Known 6 Aug 2026.",
  "no near-term AI productivity leverage in PD", "ai_productivity"),
 ("V004", "conf:MS24", "Ellie Mertz", "margin_total", "FY2024", "full-year", "-", "no", "", "",
  "It's to give us some room and some flexibility to invest where we see growth opportunities.",
  "medium", "kept", "The 35% FY24 floor was set to leave room to invest; FY24 printed 36.40% (+140bp over the floor). Known 13 Feb 2025.",
  "floor = flexibility to invest, not a target", "floor_rule"),
 ("V005", "conf:MS24", "Ellie Mertz", "other", "structural", "structural", "0", "no", "", "",
  "Through both the repurchase program as well as our net settlement of RSUs, we've been very good stewards of our cap table and managing overall dilution.",
  "medium", "kept", "Fully diluted share count down ~10% since 3Q22 on >$16bn of buybacks and RSU tax settlement (2Q26 letter). Known 6 Aug 2026.",
  "buyback + net settlement offsets SBC dilution", "capital_return"),
 ("V006", "conf:BERN24", "Ellie Mertz", "take_rate", "FY2023", "structural", "-", "no", "", "",
  "what we decided to do was lower take rates for that long duration over 3 months",
  "medium", "kept", "Statement of a 2023 pricing change (long-stay fee cut); management says volume rose as intended. Not independently verifiable in filed numbers; recorded as the only disclosed take-rate cut.",
  "take rate cut on stays >3 months", "take_rate"),
 ("V007", "conf:BERN24", "Ellie Mertz", "margin_total", "FY2024", "full-year", "-", "no", "", "",
  "that is the driver of the, the modest guide down in terms of, a modest amount of margin compression this year",
  "medium", "kept", "FY2024 adj. EBITDA margin 36.40% vs 36.84% FY2023: -44bp, i.e. modest compression as guided. Known 13 Feb 2025.",
  "FY24 margin down modestly on reinvestment", "reinvestment_rule"),
 ("V008", "conf:BERN24", "Ellie Mertz", "sm_field", "FY2025+", "multi-year", "-", "no", "", "",
  "now is the time where we really begin reinvesting in them to make them scaled over time",
  "medium", "kept", "FY2025 field-operations cash cost +43% ($693m -> $993m, 10-K FY2025); 4Q24 letter sized new-business investment at $200-250m. Known 12 Feb 2026.",
  "adjacency (new business) investment restarts", "new_business_investment"),
 ("V009", "conf:BERN24", "Ellie Mertz", "sm_perf", "FY2024", "full-year", "-", "no", "", "",
  "A variety of improvements on our end have allowed us to spend modestly more through that channel and maintain great efficiencies.",
  "medium", "unverifiable", "Performance-marketing spend is never disclosed separately from brand; the brand+performance line grew 10% in FY2024 (10-K).",
  "modestly more Google spend at stable ROI", "performance_marketing"),
 ("V010", "conf:BERN24", "Ellie Mertz", "fcf", "structural", "structural", "+", "yes", 40, "pct of revenue",
  "over 40% free cash flow margin allow us to do all three",
  "medium", "partly", "FCF margin FY2023 41.2%, FY2024 40.6%; FY2025 fell below 40% (abnb_fcf_bridge.csv, FY2025 row). The claim held for the year it was made and slipped the next.",
  "FCF margin >40%", "fcf"),
 ("V011", "conf:GS24", "Ellie Mertz", "margin_total", "FY2024", "full-year", "-", "no", "", "",
  "intent with the guidance for the current year in terms of pulling back a bit on the the margins, was to invest in short, medium, and long-term levers for growth",
  "medium", "kept", "FY2024 margin -44bp y/y with S&M % of revenue +157bp; the pull-back was real and smaller than the floor allowed. Known 13 Feb 2025.",
  "FY24 margin pull-back is deliberate reinvestment", "reinvestment_rule"),
 ("V012", "conf:GS24", "Ellie Mertz", "sm_field", "FY2025", "full-year", "-", "no", "", "",
  "We'll give a more clear view in coming quarters in terms of, you know, the net level of investment for 2025 and beyond.",
  "medium", "kept", "The 4Q24 letter (13 Feb 2025) sized FY2025 new-business investment at $200-250m. Known 13 Feb 2025.",
  "FY25 investment to be sized at 4Q24", "new_business_investment"),
 ("V013", "conf:GS25", "Brian Chesky", "sm_brand", "FY2026", "full-year", "+", "no", "", "",
  "We're not going to do a lot of independent marketing of service and experiences.",
  "medium", "open", "1H26 10-Q attributes the +$258m marketing increase to 'paid growth marketing initiatives in emerging markets and partnerships', not to services/experiences campaigns - consistent so far.",
  "no standalone marketing budget for services/experiences", "new_business_investment"),
 ("V014", "conf:GS25", "Brian Chesky", "other", "FY2025", "structural", "+", "yes", 10, "pct of services bookings by locals",
  "already 10% of bookings for services are locals without marketing",
  "medium", "unverifiable", "Not disclosed in any filing; the only quantified services demand datum outside the letters.",
  "services demand without marketing", "new_business_investment"),
 ("V015", "conf:GS25", "Brian Chesky", "capex", "structural", "structural", "+", "no", "", "",
  "It's not like other businesses where you have to deal with this huge capital investment.",
  "medium", "kept", "Capex $33m FY2025, 0.3% of revenue (abnb_capital_return / 10-K); $21m 1H26.",
  "capital-light new businesses", "capex"),
 ("V016", "conf:GS25", "Brian Chesky", "sm_brand", "structural", "structural", "-", "no", "", "",
  "You got to localize the marketing.",
  "medium", "kept", "16 local campaigns in 1Q26 alone (S193); expansion-market marketing is the stated driver of the 1H26 S&M increase (10-Q 2Q26).",
  "localized marketing in expansion markets", "expansion_markets"),
 ("V017", "conf:GS26", "Brian Chesky", "margin_total", "FY2026", "structural", "0", "yes", 35, "pct adj. EBITDA margin",
  "We basically have remained pretty steady, 35% margins.",
  "medium", "open", "FY23 36.84, FY24 36.40, FY25 35.10, FY26 guided >=35.5 (S159). Chesky rounds the band to 35; the CFO's floor is 35.5.",
  "margin steady around 35%", "floor_rule"),
 ("V018", "conf:GS26", "Brian Chesky", "margin_total", "structural", "structural", "+", "no", "", "",
  "It's really actually hard to invest a lot of money in this business because you're kind of building supply, building demand, building supply, building demand.",
  "medium", "open", "A mechanism for the floor: the marketplace cannot absorb a step-change in spend. Contrast S&M +30% y/y in 1H26 (10-Q 2Q26).",
  "structural limit on how fast spend can rise", "floor_rule"),
 ("V019", "conf:GS26", "Brian Chesky", "ops", "3Q26", "next-quarter", "+", "yes", 50, "pct of support tickets handled by AI (approx)",
  "Nearly half our customer service tickets are now handled by AI.",
  "medium", "kept", "2Q26 call: 'Nearly 45% of issues that start with our AI assistant are now resolved without a human agent' (S161). Consistent; a slight rounding up five weeks later.",
  "AI share of support ~45-50%", "ai_support"),
 ("V020", "conf:GS26", "Brian Chesky", "ops", "FY2026+", "multi-year", "0", "no", "", "",
  "It means we're now taking those people, training them to do more premium customer service because the AI can do more self-serve.",
  "medium", "open", "Signals AI support savings are partly reinvested in service levels (the 3Q24 reinvestment rule, S097), not taken as headcount reduction. 2Q26 10-Q: third-party support -$15m, payroll +$41m in ops & support 1H26.",
  "AI savings reinvested in premium support, not cut", "ai_support"),
 ("V021", "conf:GS26", "Brian Chesky", "sm_perf", "structural", "structural", "+", "yes", 90, "pct of traffic direct/organic",
  "Nearly 90% of our traffic is direct or organic.",
  "medium", "kept", "Letters have said ~90% direct or unpaid since 2021; unchanged.",
  "performance marketing a small share of traffic", "performance_marketing"),
 ("V022", "conf:GS26", "Brian Chesky", "take_rate", "FY2027+", "multi-year", "+", "yes", 1000, "usd_m incremental high-margin revenue (host services)",
  "That is a pretty easy straight shot to $1 billion incremental high margin revenue, based on what other brands have done.",
  "low", "open", "No product, price or date given; the 2023 'few percentage points of take rate' claim (S171) is the precedent and it has not materialised.",
  "host/seller services as a $1bn revenue pool", "monetisation"),
 ("V023", "conf:GS26", "Brian Chesky", "other", "FY2027", "full-year", "0", "no", "", "",
  "We're going to have some major announcements next year.",
  "medium", "open", "FY2027 product launches flagged; each prior launch (May 2025 services/experiences) carried unbudgeted field-ops and marketing cost.",
  "FY27 launches -> launch cost", "new_business_investment"),
 ("V024", "conf:GS26", "Brian Chesky", "ai", "structural", "structural", "+", "no", "", "",
  "We are not going to be a company that develops AI, but we're going to be a company that applies AI.",
  "medium", "kept", "No AI capex (capex 0.3% of revenue); inference/API spend is opex and is rising (S162 'material increase'). The statement is about capex, not opex.",
  "no model building; AI is opex", "ai_spend"),
 ("V025", "conf:GS26", "Brian Chesky", "take_rate", "structural", "structural", "+", "no", "", "",
  "We have a very high margin insurance product, travel insurance, that does quite well.",
  "medium", "kept", "Travel-insurance revenue growth is disclosed in the letters; the 1Q26 letter names insurance programs as a take-rate lift (S154).",
  "insurance is a high-margin take-rate lever", "monetisation"),
 ("V026", "conf:GS26", "Brian Chesky", "take_rate", "FY2027+", "multi-year", "+", "no", "", "",
  "I think from a margin standpoint, it is probably seller services.",
  "low", "open", "Names host/seller services as the highest-margin future line; nothing shipped or priced as of 8 Sep 2026.",
  "highest-margin future line = seller services", "monetisation"),
 # ---- earnings calls (sentences 31a left out) ----------------------------------------------------------------
 ("C001", "call:4Q20", "Dave Stephenson", "sm_total", "1H21 vs 2H21", "full-year", "0", "no", "", "",
  "you're going to see sales and marketing as a percent of revenue higher in the first half of this year than you will in the second half",
  "medium", "kept", "1H21 S&M 24.5% of revenue vs 2H21 17.0% (abnb_quarterly_costlines.csv). Known 15 Feb 2022.",
  "S&M % front-loaded in 2021", "marketing_phasing"),
 ("C002", "call:4Q20", "Brian Chesky", "margin_total", "structural", "structural", "+", "no", "", "",
  "Make no mistake, our efficiencies, we're going to hold to a much higher level than 2019 or years prior.",
  "medium", "kept", "Adj. EBITDA margin -5% (FY2019) -> 26.6 (FY21) -> 34.6 -> 36.8 -> 36.4 -> 35.1 (FY25).",
  "post-2020 cost discipline is permanent", "fixed_cost_discipline"),
 ("C003", "call:4Q21", "Dave Stephenson", "sm_total", "FY2022", "full-year", "0", "no", "", "",
  "We've already achieved that new baseline and likely not to achieve substantial improvement in the marketing expenses as a percentage of revenue this year.",
  "medium", "partly", "FY2022 S&M 18.05% of revenue vs 19.79% FY2021: -174bp, which is a substantial improvement. Cost-favourable miss. Known 14 Feb 2023.",
  "S&M % of revenue roughly flat FY22", "marketing_guide"),
 ("C004", "call:4Q21", "Dave Stephenson", "margin_total", "FY2022", "full-year", "-", "no", "", "",
  "As ADRs may moderate this year, and as mix of our business changes, that will be an offset to some of the further improvements in our fixed cost leverage and variable costs.",
  "medium", "partly", "ADR did not moderate in FY2022 (+5% y/y, KPI panel) and the margin rose 799bp; the mechanism is right, the premise did not occur. Known 14 Feb 2023.",
  "ADR moderation offsets cost leverage", "adr_margin_link"),
 ("C005", "call:4Q21", "Dave Stephenson", "sm_brand", "FY2022", "full-year", "-", "no", "", "",
  "To the extent that we expand into additional countries, there'll be some incremental more brand marketing spend in this year.",
  "medium", "kept", "FY2022 S&M dollars +28% ($1,186m -> $1,516m) while the ratio fell; brand campaign extended to more countries (3Q22 call). Known 14 Feb 2023.",
  "brand spend up in dollars FY22", "marketing_guide"),
 ("C006", "call:2Q22", "Dave Stephenson", "sm_total", "FY2022", "full-year", "0", "no", "", "",
  "we anticipate, you know, marketing as a percentage of revenue in 2022 to be consistent with 2021",
  "medium", "partly", "FY2022 18.05% vs FY2021 19.79%: -174bp, better than 'consistent'. Known 14 Feb 2023.",
  "S&M % flat FY22 (Aug restatement)", "marketing_guide"),
 ("C007", "call:3Q22", "Dave Stephenson", "margin_total", "FY2023", "full-year", "-", "no", "", "",
  "as average daily rates could moderate next year, that does put a little bit of headwind towards our margins",
  "medium", "partly", "FY2023 ADR was roughly flat (+1%), not down; margin rose 228bp. Conditional statement whose condition did not occur. Known 13 Feb 2024.",
  "FY23 ADR moderation = margin headwind", "adr_margin_link"),
 ("C008", "call:3Q22", "Dave Stephenson", "sm_brand", "FY2023", "full-year", "-", "no", "", "",
  "it's been so successful that we're actually expanding to more countries, and so that's what you'll be seeing over the course of this next year is to expand more countries to support our brand advertising",
  "medium", "kept", "FY2023 marketing activities +$168m on the 'Airbnb It' / 'I'm Flexible' / Categories campaigns and search spend (10-Q 3Q23 MD&A); S&M dollars +16%. Known 1 Nov 2023.",
  "brand campaign to more countries FY23", "marketing_guide"),
 ("C009", "call:4Q22", "Dave Stephenson", "sm_total", "FY2023", "full-year", "0", "no", "", "",
  "What we'd see in 2023 is that marketing costs as a percentage of revenue for the full year will be about the same as what it was in 2022.",
  "medium", "kept", "FY2023 S&M 17.78% vs 18.05% FY2022: -27bp. Known 13 Feb 2024.",
  "S&M % flat FY23", "marketing_guide"),
 ("C010", "call:4Q22", "Dave Stephenson", "margin_total", "FY2023", "full-year", "+", "no", "", "",
  "I know that I can also afford with our headcount growth, profitability improvements that can offset the ADR declines, and that's what we'll be investing in this year.",
  "medium", "kept", "FY2023 margin 36.84% vs 34.56%: +228bp. Known 13 Feb 2024.",
  "cost improvements offset ADR risk FY23", "reinvestment_rule"),
 ("C011", "call:4Q22", "Dave Stephenson", "margin_total", "FY2023", "full-year", "-", "no", "", "",
  "The way we've anticipated our EBITDA margins for this year is that one of the headwinds is this anticipated ADR decline that we talked about earlier on the call.",
  "medium", "partly", "The anticipated FY2023 ADR decline did not happen (ADR ~flat); the FY23 guide ('maintain') was beaten by 228bp partly because the headwind never arrived. Known 13 Feb 2024.",
  "FY23 guide built on an ADR decline", "adr_margin_link"),
 ("C012", "call:4Q22", "Dave Stephenson", "other", "FY2023", "full-year", "0", "no", "", "",
  "To the extent that we can return stock, cash to shareholders through share repurchases, that'll be our primary vehicle unit to state this year.",
  "medium", "kept", "FY2023 buybacks $2.25bn (capital-return panel); no dividend. Known 13 Feb 2024.",
  "buybacks the primary return vehicle", "capital_return"),
 ("C013", "call:1Q23", "Dave Stephenson", "sm_total", "FY2023", "full-year", "0", "no", "", "",
  "for the full year, total marketing costs will be roughly the same as they were in the prior year",
  "high", "kept", "Read with the 4Q22 statement (C009) as a %-of-revenue guide: 17.78% vs 18.05%. In dollars S&M rose 16%, so on a dollar reading it would be missed; the basis is ambiguous in this sentence. Known 13 Feb 2024.",
  "marketing flat FY23 (May restatement)", "marketing_guide"),
 ("C014", "call:1Q23", "Dave Stephenson", "margin_total", "structural", "structural", "0", "no", "", "",
  "over time, we'll continue to have opportunities to expand margins but that's not my primary focus right now",
  "high", "kept", "Margin peaked at 36.84% in FY2023 and has been guided flat-to-down since; growth reinvestment is the stated priority (S097, S138).",
  "margin expansion not the priority", "reinvestment_rule"),
 ("C015", "call:2Q23", "Dave Stephenson", "margin_total", "2H2023", "next-quarter", "+", "no", "", "",
  "for the back half of the year, we feel confident we're going to be able to exceed our EBITDA margins over the prior year",
  "high", "kept", "2H2023 margin 45.8% vs 2H2022 41.0% (abnb_quarterly_costlines.csv). Known 13 Feb 2024.",
  "2H23 margin > 2H22", "margin_guide"),
 ("C016", "call:2Q23", "Dave Stephenson", "take_rate", "multi-year", "multi-year", "+", "no", "", "",
  "I think the extent that we'll expand our margins over time, I think the biggest opportunity would be with some of the services that Brian mentioned earlier in the call",
  "high", "open", "Services launched May 2025 and are so far a margin drag (field ops +43% FY25; customer incentives holding take rate flat FY26, S165).",
  "services as the margin-expansion lever", "monetisation"),
 ("C017", "call:4Q23", "Dave Stephenson", "pd", "FY2024", "full-year", "+", "no", "", "",
  "depending on what our product development needs are, but it's not going to be above overall kind of revenue growth",
  "high", "missed", "FY2024 GAAP product development +19.4% vs revenue +12.0% (abnb_quarterly_costlines.csv); PD % of revenue 17.36 -> 18.52. Known 13 Feb 2025.",
  "PD growth <= revenue growth FY24", "pd_guide"),
 ("C018", "call:3Q24", "Ellie Mertz", "sm_field", "FY2025", "full-year", "-", "no", "", "",
  "But we will be adding members to our teams and spending to our marketing to support these growth levers.",
  "high", "kept", "FY2025 field operations cash +43%, S&M total +20%; headcount ~+12%. Known 12 Feb 2026.",
  "FY25 headcount and marketing up for growth levers", "new_business_investment"),
 ("C019", "call:4Q24", "Ellie Mertz", "margin_total", "FY2025", "full-year", "-", "no", "", "",
  "We anticipate that the negative impact to margin from those investments will be heavily weighted in Q1 through Q3, whereas the revenue obviously won't pick up until we've launched those new products at the end of Q2.",
  "high", "missed", "Margin y/y: 1Q25 -1.4, 2Q25 +1.2, 3Q25 -2.4, 4Q25 -2.5pts. Q4 carried as much drag as Q3; the 1Q25 letter had already moved the weight to 2H. Known 12 Feb 2026.",
  "FY25 margin drag front-loaded", "margin_phasing"),
 ("C020", "call:4Q24", "Ellie Mertz", "sm_field", "FY2025", "full-year", "-", "no", "", "",
  "in terms of marketing, we will obviously be spending to build out the teams to drive the supply operations around those new offerings",
  "high", "kept", "FY2025 field-ops payroll +$121m and third-party providers +$102m in S&M (10-K FY2025 MD&A). Known 12 Feb 2026.",
  "supply-ops teams for new offerings", "new_business_investment"),
 ("C021", "call:4Q24", "Ellie Mertz", "margin_total", "structural", "structural", "0", "no", "", "",
  "every year, we will be looking to invest in new growth opportunities, while also finding incremental efficiencies in our core business",
  "high", "kept", "Restates the 3Q24 operating rule (S097); the FY26 guide was raised on 'operating leverage in our core business' (S159).",
  "reinvestment rule restated", "reinvestment_rule"),
 ("C022", "call:1Q25", "Ellie Mertz", "margin_total", "multi-year", "multi-year", "0", "no", "", "",
  "the intent both with the core and the new businesses is to invest in growth upfront and to optimize the margins over time",
  "high", "open", "No margin target for the new businesses has been given; 2Q26 call declined a 2027 guide (S179).",
  "new businesses: invest first, margin later", "new_business_investment"),
 ("C023", "call:1Q25", "Ellie Mertz", "sm_brand", "structural", "structural", "+", "no", "", "",
  "over time, we are able to scale into the marketing load as well as make some efficiencies in terms of the underlying variable costs if they have not already been localized",
  "high", "open", "Expansion-market unit economics: marketing load is front-loaded and scales down per unit as the market matures. Never quantified.",
  "expansion markets scale into marketing load", "expansion_markets"),
 ("C024", "call:2Q25", "Ellie Mertz", "sm_perf", "FY2025", "full-year", "0", "no", "", "",
  "Our overall programmatic marketing for the year is relatively stable from a percent of revenue basis.",
  "high", "unverifiable", "Performance (programmatic) marketing is not disclosed separately; brand+performance grew 10% vs revenue 12.6% in FY2025, consistent but not a test.",
  "performance marketing % of revenue stable FY25", "performance_marketing"),
 ("C025", "call:2Q25", "Ellie Mertz", "sm_brand", "structural", "structural", "0", "no", "", "",
  "put money in a larger allocation of our marketing spend behind brand versus performance",
  "high", "kept", "Consistent with S174 (performance is the minority) and V021 (90% direct/organic traffic).",
  "brand-heavy channel mix", "performance_marketing"),
 ("C026", "call:4Q25", "Ellie Mertz", "pd", "FY2026", "full-year", "-", "no", "", "",
  "we will also continue to grow our investments in product development to allow for a greater accelerated pace of innovation",
  "high", "open", "1H26 GAAP product development +11% y/y, payroll-driven (10-Q 2Q26 MD&A); PD 20.8% of revenue in 1H26.",
  "PD investment keeps growing FY26", "pd_guide"),
 ("C027", "call:1Q25", "Ellie Mertz", "sm_brand", "structural", "structural", "0", "no", "", "",
  "Obviously, we start the year with a full year marketing plan, and yet every month, we're looking at the relative efficiencies by channel, by market and adjusting accordingly.",
  "high", "kept", "Describes the marketing budget as a plan with monthly reallocation; explains why FY marketing guides are given as ratios and why they drift (FY24 +157bp miss).",
  "marketing plan reallocated monthly", "marketing_guide"),
 ("C028", "call:4Q24", "Brian Chesky", "sm_brand", "FY2025", "full-year", "-", "no", "", "",
  "And I think this time, we're going to be a bit more aggressive in marketing them because we're really proud of the quality product we have.",
  "high", "kept", "FY2025 S&M +20% ($2,148m -> $2,588m); the May 2025 launch was supported by a global campaign. Known 12 Feb 2026.",
  "more aggressive marketing of the 2025 launches", "new_business_investment"),
 # ---- filings: 10-K ---------------------------------------------------------------------------------------------
 ("K001", "10k:FY2023", "10-K", "headcount", "FY2023", "structural", "0", "yes", 6907, "employees at 31 Dec",
  "As of December 31, 2023, we had 6,907 employees.", "high", "kept", "Filed number.", "headcount", "headcount"),
 ("K002", "10k:FY2024", "10-K", "headcount", "FY2024", "structural", "0", "yes", 7300, "employees at 31 Dec (approx)",
  "As of December 31, 2024, we had approximately 7,300 employees.", "high", "kept", "Filed number: +5.7% y/y.", "headcount", "headcount"),
 ("K003", "10k:FY2025", "10-K", "headcount", "FY2025", "structural", "0", "yes", 8200, "employees at 31 Dec (approx)",
  "As of December 31, 2025, we had approximately 8,200 employees.", "high", "kept", "Filed number: +12.3% y/y, the base the 4Q25 'lower than 2025' headcount-growth guide (S144) is measured against.", "headcount", "headcount"),
 ("K004", "10k:FY2023", "10-K", "hosting", "through 2027", "multi-year", "-", "yes", 842, "usd_m minimum commitment",
  "We have a commercial agreement with a data hosting services provider to spend or incur an aggregate of at least $842 million for vendor services through 2027.",
  "high", "kept", "Commitment schedule; $842m over 2024-27 = ~$210m/yr floor on hosting spend.", "hosting commitment floor", "hosting"),
 ("K005", "10k:FY2024", "10-K", "hosting", "through 2027", "multi-year", "-", "yes", 672, "usd_m minimum commitment",
  "We have a commercial agreement with a data hosting services provider to spend or incur an aggregate of at least $672 million for vendor services through 2027.",
  "high", "kept", "$672m remaining over 2025-27 (~$224m/yr).", "hosting commitment floor", "hosting"),
 ("K006", "10k:FY2025", "10-K", "hosting", "through 2031", "multi-year", "-", "yes", 1700, "usd_m minimum commitment",
  "We have a commercial agreement with a data hosting services provider to spend or incur an aggregate of at least $1.7 billion for vendor services through 2031.",
  "high", "kept", "New agreement (June 2025, $1.9bn at signing per 10-Q 2Q25); $1.7bn remaining over 2026-31 = ~$283m/yr vs ~$224m/yr under the prior deal: a +25% step in the hosting floor.",
  "hosting commitment floor steps up", "hosting"),
 ("K007", "10k:FY2025", "10-K", "hosting", "FY2026-FY2030", "multi-year", "-", "yes", 1749, "usd_m purchase obligations (219 <1y; 930 1-3y; 600 3-5y)",
  "Purchase obligations | $ | 1,749 | $ | 219 | $ | 930 | $ | 600",
  "high", "kept", "Purchase obligations $1,749m at 31 Dec 2025 (vs $719m a year earlier): $219m due in 2026, $930m in 2027-28, $600m in 2029-30. The 2027-28 tranche (~$465m/yr) is the FY27 hosting floor.",
  "purchase-obligation schedule", "hosting"),
 ("K008", "10k:FY2023", "10-K", "ops", "FY2023", "structural", "0", "yes", 11000, "third-party contingent support workers (approx)",
  "we relied on a global network of approximately 11,000 third-party contingent workers to handle the vast majority of our community support contacts",
  "high", "kept", "Filed number; the human-support base AI deflection works against.", "outsourced support headcount", "ai_support"),
 ("K009", "10k:FY2023", "10-K", "ops", "multi-year", "multi-year", "-", "no", "", "",
  "A robust community support effort is costly, and we expect such cost to continue to rise in the future as we grow our business.",
  "high", "kept", "Ops & support dollars rose every year FY21-FY25 ($847m -> $1,239m GAAP) while falling as % of revenue; risk-factor language, kept in dollars.",
  "support cost rises in dollars", "ops_guide"),
 ("K010", "10k:FY2025", "10-K", "sbc", "FY2026-28", "multi-year", "-", "yes", 114, "usd_m unrecognized option cost",
  "As of December 31, 2025, there was $ 114 million of total unrecognized compensation cost related to stock option awards granted under the Plans.",
  "high", "kept", "Options only; the RSU unrecognized balance is in the equity note table, not a sentence (WS02/M7 to tabulate from XBRL).", "unrecognized SBC (options)", "sbc"),
 # ---- filings: 10-Q forward sentences (2021 filings carried explicit expectations by line; dropped from 2022) ----
 ("Q001", "10q:1Q21", "10-Q", "ops", "multi-year", "multi-year", "+", "no", "", "",
  "We are also investing in the near-term in initiatives to reduce customer contact rates and improve the operational efficiency of our operations and support organization, which we expect will decrease operations and support expense as a percentage of revenue over the longer term.",
  "high", "kept", "Ops & support 14.1% of revenue FY2021 -> 10.1% FY2025 (GAAP). Known 12 Feb 2026.", "ops % of revenue falls long term", "ops_guide"),
 ("Q002", "10q:1Q21", "10-Q", "sm_total", "multi-year", "multi-year", "+", "no", "", "",
  "We expect our sales and marketing expense will vary from period to period as a percentage of revenue for the foreseeable future, and over the long term, we expect it will decline as a percentage of revenue relative to 2019.",
  "high", "kept", "S&M 33.7% of revenue FY2019; 17.8-21.1% FY2023-25; 25.9% 1H26. Still below 2019 but rising since 2023.", "S&M % below 2019 long term", "marketing_guide"),
 ("Q003", "10q:1Q21", "10-Q", "sm_total", "1H21 vs 2H21", "full-year", "0", "no", "", "",
  "We expect that sales and marketing expense as a percentage of revenue in the first half of 2021 will be higher than that of the second half.",
  "high", "kept", "1H21 24.5% vs 2H21 17.0%. Known 15 Feb 2022.", "S&M front-loaded 2021", "marketing_phasing"),
 ("Q004", "10q:1Q21", "10-Q", "capex", "FY2021", "full-year", "0", "no", "", "",
  "We expect our capital expenditures in 2021 will be higher than that of 2020, but significantly lower than 2019.",
  "high", "missed", "FY2021 capex $25m vs FY2020 $37m and FY2019 $125m (cash-flow statements; abnb_fcf_bridge.csv FY2021 capex 25.3). Lower than 2020, not higher. Cost-favourable miss. Known 15 Feb 2022.",
  "capex 2021 > 2020", "capex"),
 ("Q005", "10q:1Q21", "10-Q", "pd", "multi-year", "multi-year", "-", "no", "", "",
  "We expect that our product development expense will increase on an absolute dollar basis and will vary from period to period as a percentage of revenue for the foreseeable future",
  "high", "kept", "PD dollars rose every year FY2021-25; the ratio fell to FY2023 then rose. Deliberately unfalsifiable on the ratio.", "PD up in dollars", "pd_guide"),
 ("Q006", "10q:1Q21", "10-Q", "cor", "multi-year", "multi-year", "-", "no", "", "",
  "We expect our cost of revenue will continue to increase on an absolute dollar basis for the foreseeable future to the extent that we continue to see growth on our platform.",
  "high", "kept", "Cost of revenue dollars rose every year FY2021-25.", "CoR up in dollars", "cor_guide"),
 ("Q007", "10q:2Q25", "10-Q", "hosting", "through 2031", "multi-year", "-", "yes", 1900, "usd_m minimum commitment at signing",
  "In June 2025, we signed a new enterprise agreement with a web-hosting service company for cloud hosting and related services to spend or incur an aggregate of at least $1.9 billion, which extends through 2031.",
  "high", "kept", "$1.9bn over mid-2025 to 2031 (~$300m/yr) vs the prior $672m-through-2027 deal (~$224m/yr). The hosting floor stepped up ~35% at signing; $1.7bn remained at 31 Dec 2025 (K006).",
  "new hosting agreement", "hosting"),
 # ---- 8-Ks --------------------------------------------------------------------------------------------------------
 ("E001", "8k:2023-12-13", "8-K Item 8.01", "ga", "FY2023", "full-year", "0", "yes", 576, "eur_m settlement (taxes, interest, penalties, 2017-21)",
  "Airbnb Ireland signed an agreement with the Italian Revenue Agency in settlement of the Audited Periods for an aggregate payment of 576 million euros.",
  "high", "kept", "Booked in FY2023 G&A (non-income taxes) and added back to adjusted EBITDA; the reason FY2023 GAAP G&A is distorted (31a) and FY2024 non-income taxes fell $656m.",
  "Italian withholding settlement", "non_income_tax"),
 ("E002", "8k:2023-12-13", "8-K Item 8.01", "ga", "FY2024+", "multi-year", "-", "no", "", "",
  "The settlement does not include any tax withholding assessments for 2022 and 2023, which amounts could be material.",
  "high", "open", "No further material Italian charge disclosed through the 2Q26 10-Q (non-income taxes -$38m y/y in 1H26); gross unrecognized tax benefits $835m at 31 Dec 2025 (10-K).",
  "residual Italian exposure", "non_income_tax"),
 ("E003", "8k:2026-03-16", "8-K Item 1.01", "interest", "FY2026-36", "multi-year", "-", "yes", 2500, "usd_m senior notes; blended coupon ~4.76% = ~$119m/yr",
  "$2.5 billion aggregate principal amount of senior notes, consisting of $850.0 million aggregate principal amount of its 4.400% Senior Notes due 2029",
  "high", "kept", "Coupons 4.400% (2029), 4.650% (2031), 5.250% (2036): $37.4m + $39.5m + $42.0m = ~$119m/yr of interest expense below adjusted EBITDA from 2Q26 ($37m booked in 2Q26). Replaces the 0% converts that matured 15 Mar 2026 (E004).",
  "new interest expense line", "interest"),
 ("E004", "8k:2021-03-08", "8-K Item 1.01", "interest", "FY2021-26", "multi-year", "0", "yes", 2000, "usd_m 0% convertible notes due 15 Mar 2026",
  "issued $2,000,000,000 principal amount of its 0% Convertible Senior Notes due 2026",
  "high", "kept", "Zero-coupon; matured March 2026 and was refinanced with the $2.5bn IG notes, so FY2026 is the first year with cash interest expense (~$90m for 9.5 months, ~$119m in FY2027).",
  "converts matured, replaced by coupon debt", "interest"),
]

# ------------------------------------------------------------------------------------------------ 10-Q MD&A auto rows
MDA_LINES = [  # (regex on the paragraph start, spec line)
    (r"^Cost of revenue (increased|decreased)", "cor"),
    (r"^Operations and support expense (increased|decreased)", "ops"),
    (r"^Product development expense (increased|decreased)", "pd"),
    (r"^Sales and marketing expense (increased|decreased)", "sm_total"),
    (r"^General and administrative expense (increased|decreased)", "ga"),
    (r"^Interest income (increased|decreased)", "interest"),
    (r"^Other income \(expense\), net (changed|increased|decreased)", "other"),
    (r"^(Provision for|Benefit from) income taxes", "tax"),
]
MONEY = re.compile(r"\$\s?([\d,]+(?:\.\d+)?)\s*(million|billion)?")
PCT = re.compile(r"or\s+([\d.]+)%")


def mda_rows(docs):
    rows = []
    for tag, date in TENQ_DATE.items():
        doc = docs.get(f"10q:{tag}")
        if doc is None:
            continue
        for pat, line in MDA_LINES:
            for pp in doc["paras"]:
                if re.match(pat, pp) and re.search(r"(increased|decreased|changed|primarily|due to)", pp):
                    m = MONEY.search(pp)
                    val = ""
                    if m:
                        val = float(m.group(1).replace(",", ""))
                        if m.group(2) == "billion":
                            val *= 1000
                    pc = PCT.search(pp)
                    direction_word = "up" if re.search(r"^\S.*?\bincreased\b", pp[:80]) else ("down" if "decreased" in pp[:80] else "changed")
                    margin_dir = {"up": "-", "down": "+", "changed": "0"}[direction_word]
                    if line in ("interest",):
                        margin_dir = {"up": "+", "down": "-", "changed": "0"}[direction_word]  # income, not cost
                    rows.append({
                        "statement_id": f"F{tag}_{line}", "date": date, "event_type": "filing", "event": f"10-Q {tag} MD&A",
                        "source_detail": "10-Q MD&A three-month comparison", "speaker": "10-Q", "line": line, "line_31a": "",
                        "period_referenced": tag, "horizon": "reported-quarter", "direction": margin_dir, "quantified": "yes",
                        "value": val, "unit": f"usd_m y/y change ({direction_word}; {pc.group(1) + '%' if pc else 'n/a'})",
                        "verbatim": pp[:300], "quote_verified": "yes", "source_path_or_url": doc["raw"], "locator": "MD&A results of operations",
                        "confidence": "high", "verdict": "n/a", "kept_or_missed": "n/a (backward-looking explanation of the reported quarter)",
                        "implied_metric": f"{line} y/y $ change and drivers", "theme": "mda_component", "origin": "10q_mda",
                    })
                    break  # first match = three-month paragraph
    return rows


# ------------------------------------------------------------------------------------------------ pattern of the FY sentence
# print: (fy, sentence, type, level_or_delta, q_rev_low, q_rev_high, q_sentence, q_type, q_level, fy1_statement, fy1_ids)
#   type: floor | point | approx | floor_yoy | point_yoy | none;  level_or_delta is absolute % for floor/point/approx, pts for *_yoy
FY_SENTENCE = {
 "3Q21": ("FY2021", "", "none", None, 1390, 1480,
          "we expect to deliver greater year-over-year and year-over-two year margin expansion in Q4 2021 than we delivered in Q3 2021", "floor_yoy", 11.9,
          "none on margin; ADR moderation flagged for 2022 (S021)", "S021"),
 "4Q21": ("FY2022", "we would expect Adjusted EBITDA margin to be directionally in-line with 2021", "point_yoy", 0.0, 1410, 1480,
          "we expect to achieve our first positive Q1 Adjusted EBITDA in Airbnb history", "floor", 0.0, "", ""),
 "1Q22": ("FY2022", "We currently anticipate delivering modest Adjusted EBITDA margin expansion for the full-year 2022 relative to 2021", "floor_yoy", 0.0, 2030, 2130,
          "driving a low double-digit EBITDA margin percentage improvement on a year-over-year basis", "floor_yoy", 10.0, "", ""),
 "2Q22": ("FY2022", "We continue to forecast delivering Adjusted EBITDA margin expansion for the full-year 2022 relative to 2021", "floor_yoy", 0.0, 2780, 2880,
          "We expect Q3 2022 Adjusted EBITDA margin to be at or slightly below last year's all-time high margin of 49%", "ceiling", 49.0, "", ""),
 "3Q22": ("FY2022", "", "none", None, 1800, 1880,
          "expect quarterly Adjusted EBITDA margin to be in-line to modestly higher than last year's margin of 22%", "floor", 22.0,
          "similar marketing as a percentage of revenue in 2023 (S038); ADR moderation next year a margin headwind (C007)", "S038;C007"),
 "4Q22": ("FY2023", "For the full year 2023, we expect to maintain the strong Adjusted EBITDA margin we delivered in 2022", "point_yoy", 0.0, 1750, 1820,
          "In Q1 2023, we expect Adjusted EBITDA margin to be slightly down on a year-over-year basis", "ceiling_yoy", 0.0, "", ""),
 "1Q23": ("FY2023", "We continue to anticipate a full year Adjusted EBITDA margin that is broadly in-line with full-year 2022", "point_yoy", 0.0, 2350, 2450,
          "we expect Adjusted EBITDA to be similar to Adjusted EBITDA in Q2 2022 on a nominal basis, but lower on a margin basis", "ceiling_yoy", 0.0, "", ""),
 "2Q23": ("FY2023", "For the full-year 2023, we expect an Adjusted EBITDA margin that is modestly higher than the full-year 2022", "floor_yoy", 0.0, 3300, 3400,
          "an Adjusted EBITDA margin that exceeds Q3 2022", "floor_yoy", 0.0, "", ""),
 "3Q23": ("FY2023", "we expect an Adjusted EBITDA margin for full-year 2023 that is approximately 150 bps higher than full-year 2022", "approx_yoy", 1.5, 2130, 2170,
          "an Adjusted EBITDA margin that exceeds Q4 2022", "floor_yoy", 0.0,
          "We anticipate a similar year-over-year growth rate for SBC expense in 2024 (letter); no FY24 margin statement until 4Q23", "S063"),
 "4Q23": ("FY2024", "For the full-year 2024, we expect to maintain an Adjusted EBITDA Margin of at least 35%", "floor", 35.0, 2030, 2070,
          "We expect Adjusted EBITDA Margin in Q1 2024 to expand relative to Q1 2023", "floor_yoy", 0.0, "", ""),
 "1Q24": ("FY2024", "...to deliver an Adjusted EBITDA Margin of at least 35%", "floor", 35.0, 2680, 2740,
          "down on an Adjusted EBITDA Margin basis, relative to Q2 2023", "ceiling_yoy", 0.0, "", ""),
 "2Q24": ("FY2024", "...to deliver an Adjusted EBITDA Margin of at least 35%", "floor", 35.0, 3670, 3730,
          "for Adjusted EBITDA Margin to decline relative to Q3 2023", "ceiling_yoy", 0.0, "", ""),
 "3Q24": ("FY2024", "For the full-year 2024, we now expect to deliver an Adjusted EBITDA Margin of approximately 35.5%", "approx", 35.5, 2390, 2440,
          "Q4 2024 Adjusted EBITDA Margin is expected to decline relative to the same time period last year", "ceiling_yoy", 0.0,
          "We're excited to share more about our 2025 growth and investment plans early next year (letter); investment will front-run revenue (S100); capital light (S099)", "S099;S100"),
 "4Q24": ("FY2025", "we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%", "floor", 34.5, 2230, 2270,
          "we expect Adjusted EBITDA and Adjusted EBITDA Margin to decline compared to Q1 2024", "ceiling_yoy", 0.0, "", ""),
 "1Q25": ("FY2025", "...to deliver a full-year Adjusted EBITDA Margin of at least 34.5%", "floor", 34.5, 2990, 3050,
          "Adjusted EBITDA Margin to be flat to down slightly compared to Q2 2024", "ceiling_yoy", 0.0, "", ""),
 "2Q25": ("FY2025", "...to deliver a full-year Adjusted EBITDA Margin of at least 34.5%", "floor", 34.5, 4020, 4100,
          "Adjusted EBITDA Margin during Q3 2025 will be lower than in Q3 2024", "ceiling_yoy", 0.0, "", ""),
 "3Q25": ("FY2025", "For the full-year 2025, we now expect to deliver an Adjusted EBITDA Margin of approximately 35%", "approx", 35.0, 2660, 2720,
          "We expect Adjusted EBITDA in Q4 2025 to be flat- to-down slightly on a year-over-year basis and for Adjusted EBITDA Margin to decline", "ceiling_yoy", 0.0,  # "flat- to-down": letter PDF hyphenation, kept verbatim
          "As we look forward to 2026, we are focused on maintaining strong margins while continuing to invest in growth initiatives (letter, S133); OBBBA cuts the ETR from 2026 (S134)", "S133;S134;S136"),
 "4Q25": ("FY2026", "For 2026, we expect our Adjusted EBITDA Margin to be stable year-over-year", "point_yoy", 0.0, 2590, 2630,
          "We expect Adjusted EBITDA Margin to be approximately flat year-over-year", "point_yoy", 0.0, "", ""),
 "1Q26": ("FY2026", "For 2026, we now expect our Adjusted EBITDA Margin to be at least 35%", "floor", 35.0, 3540, 3600,
          "We expect Adjusted EBITDA and Adjusted EBITDA Margin to be up year-over-year in Q2 2026", "floor_yoy", 0.0, "", ""),
 "2Q26": ("FY2026", "For 2026, we now expect to deliver a full-year Adjusted EBITDA Margin of at least 35.5%", "floor", 35.5, 4690, 4770,
          "Adjusted EBITDA Margin to be down slightly compared to Q3 2025, due to timing of investments", "ceiling_yoy", 0.0,
          "I'm not going to give you a specific guide for 2027 and beyond (S179); AI spend 'material increase' (S162); headcount growth lower (S163)", "S179;S162;S163"),
}


def qkey(tag):
    return (int(tag[2:]), int(tag[0]))


def pattern_rows(panel):
    """panel: DataFrame quarter, revenue_musd, adjusted_ebitda_musd."""
    p = panel.set_index("quarter")
    quarters = sorted(p.index, key=qkey)
    fy = {}
    for q in quarters:
        y = 2000 + int(q[2:])
        fy.setdefault(y, []).append(q)
    fy_margin = {y: 100 * p.loc[qs, "adjusted_ebitda_musd"].sum() / p.loc[qs, "revenue_musd"].sum() for y, qs in fy.items() if len(qs) == 4}
    rows = []
    for tag, (fyt, sent, typ, lvl, rl, rh, qsent, qtyp, qlvl, fy1, fy1_ids) in FY_SENTENCE.items():
        y = 2000 + int(tag[2:]); qn = int(tag[0]); fy_year = int(fyt[2:])
        ytd = [f"{i}Q{tag[2:]}" for i in range(1, qn + 1)]
        ytd_rev = p.loc[ytd, "revenue_musd"].sum(); ytd_e = p.loc[ytd, "adjusted_ebitda_musd"].sum()
        py = [f"{i}Q{(y - 1) % 100:02d}" for i in range(1, qn + 1)]
        py_rev = p.loc[py, "revenue_musd"].sum(); py_e = p.loc[py, "adjusted_ebitda_musd"].sum()
        prior_fy = fy_margin.get(fy_year - 1)
        level = None
        if typ in ("floor", "point", "approx"):
            level = lvl
        elif typ in ("floor_yoy", "point_yoy", "approx_yoy") and prior_fy is not None:
            level = prior_fy + lvl
        actual_fy = fy_margin.get(fy_year)
        nxt = f"{NEXT_Q[tag[:2]]}{(y + 1) % 100:02d}" if qn == 4 else f"{NEXT_Q[tag[:2]]}{tag[2:]}"
        nq_rev = p.loc[nxt, "revenue_musd"] if nxt in p.index else None
        nq_margin = 100 * p.loc[nxt, "adjusted_ebitda_musd"] / nq_rev if nxt in p.index else None
        nq_ly = f"{nxt[:2]}{(int(nxt[2:]) - 1):02d}"
        nq_ly_margin = 100 * p.loc[nq_ly, "adjusted_ebitda_musd"] / p.loc[nq_ly, "revenue_musd"] if nq_ly in p.index else None
        r = {
            "print": tag, "date": PRINT_DATE[tag], "month": PRINT_DATE[tag][5:7], "is_november": qn == 3, "fy_target": fyt,
            "fy_sentence": sent, "fy_sentence_type": typ, "fy_guide_level_pct": None if level is None else round(level, 2),
            "fy_guide_delta_pts": lvl if typ.endswith("_yoy") else None, "prior_fy_margin_pct": None if prior_fy is None else round(prior_fy, 2),
            "ytd_revenue_musd": round(ytd_rev, 1), "ytd_adj_ebitda_musd": round(ytd_e, 1), "ytd_margin_pct": round(100 * ytd_e / ytd_rev, 2),
            "prior_ytd_margin_pct": round(100 * py_e / py_rev, 2), "ytd_margin_yoy_pts": round(100 * ytd_e / ytd_rev - 100 * py_e / py_rev, 2),
            "next_q": nxt, "next_q_revenue_guide_low": rl, "next_q_revenue_guide_high": rh, "next_q_revenue_guide_mid": (rl + rh) / 2,
            "next_q_margin_sentence": qsent, "next_q_margin_sentence_type": qtyp,
            "next_q_margin_guide_level_pct": (qlvl if qtyp in ("floor", "ceiling", "point") else (None if nq_ly_margin is None else round(nq_ly_margin + qlvl, 2))),
            "next_q_actual_revenue_musd": nq_rev, "next_q_actual_margin_pct": None if nq_margin is None else round(nq_margin, 2),
            "next_q_ly_margin_pct": None if nq_ly_margin is None else round(nq_ly_margin, 2),
            "implied_fy_revenue_musd": None, "implied_q4_adj_ebitda_musd": None, "implied_q4_margin_pct": None, "implied_q4_margin_source": "",
            "q4_actual_minus_implied_pts": None, "actual_fy_margin_pct": None if actual_fy is None else round(actual_fy, 2),
            "actual_minus_guide_bp": None if (actual_fy is None or level is None) else round(100 * (actual_fy - level), 0),
            "first_fy_plus1_statement": fy1, "fy_plus1_statement_ids": fy1_ids,
        }
        if qn == 3 and level is not None:
            imp_rev = ytd_rev + (rl + rh) / 2
            imp_q4_e = level / 100 * imp_rev - ytd_e
            imp_q4_m = 100 * imp_q4_e / ((rl + rh) / 2)
            r.update({"implied_fy_revenue_musd": round(imp_rev, 1), "implied_q4_adj_ebitda_musd": round(imp_q4_e, 1),
                      "implied_q4_margin_pct": round(imp_q4_m, 2), "implied_q4_margin_source": "FY sentence minus 9M actual, over the Q4 revenue guide mid",
                      "q4_actual_minus_implied_pts": None if nq_margin is None else round(nq_margin - imp_q4_m, 2)})
        elif qn == 3 and r["next_q_margin_guide_level_pct"] is not None:
            # 3Q21 and 3Q22: no full-year number was given; the Q4 sentence itself is the floor (3Q21: Q4 y/y expansion > Q3's
            # +11.9 pts on a -2.4% base; 3Q22: "in-line to modestly higher than last year's 22%")
            q4l = r["next_q_margin_guide_level_pct"]
            r.update({"implied_fy_revenue_musd": round(ytd_rev + (rl + rh) / 2, 1), "implied_q4_adj_ebitda_musd": round(q4l / 100 * (rl + rh) / 2, 1),
                      "implied_q4_margin_pct": round(q4l, 2), "implied_q4_margin_source": f"Q4 sentence ({qtyp}); no FY number given",
                      "q4_actual_minus_implied_pts": None if nq_margin is None else round(nq_margin - q4l, 2)})
        rows.append(r)
    return rows, fy_margin


def nov2026_scenarios(panel):
    """What each candidate FY sentence on 5 Nov 2026 implies for the 4Q26 margin, given 1H26 actuals, the 3Q26 guide
    and a 4Q26 revenue guide. 3Q26 margin assumption: 'down slightly' vs 50.1% -> 49.5% (stated, not fitted)."""
    p = panel.set_index("quarter")
    h1_rev = p.loc[["1Q26", "2Q26"], "revenue_musd"].sum(); h1_e = p.loc[["1Q26", "2Q26"], "adjusted_ebitda_musd"].sum()
    q3_rev, q3_m = 4730.0, 49.5   # 2Q26 letter guide mid; margin 'down slightly' from 50.1
    q4_ly_m = 100 * p.loc["4Q25", "adjusted_ebitda_musd"] / p.loc["4Q25", "revenue_musd"]
    rows = []
    for q4_rev, q4_src in ((3059.0, "bridge v3 implied guide mid (00_BRIEF)"), (2980.0, "4Q25 x 1.073 (guide at +7-8%)"), (3178.0, "bridge v3 revenue forecast")):
        for label, lvl in (("at least 35.5% (unchanged floor)", 35.5), ("approximately 35.5%", 35.5), ("approximately 36%", 36.0),
                           ("at least 36%", 36.0), ("approximately 36.5%", 36.5)):
            for q3m in (49.0, 49.5, 50.1):
                nine_rev = h1_rev + q3_rev; nine_e = h1_e + q3_rev * q3m / 100
                imp_rev = nine_rev + q4_rev; imp_q4_e = lvl / 100 * imp_rev - nine_e; imp_q4_m = 100 * imp_q4_e / q4_rev
                rows.append({"fy_sentence_candidate": label, "fy_level_pct": lvl, "q3_margin_assumed_pct": q3m,
                             "nine_month_margin_pct": round(100 * nine_e / nine_rev, 2), "nine_month_margin_yoy_pts": round(100 * nine_e / nine_rev - 37.10, 2),
                             "q4_revenue_guide_mid_musd": q4_rev, "q4_revenue_source": q4_src, "implied_fy_revenue_musd": round(imp_rev, 0),
                             "implied_q4_adj_ebitda_musd": round(imp_q4_e, 0), "implied_q4_margin_pct": round(imp_q4_m, 2),
                             "implied_q4_margin_yoy_pts": round(imp_q4_m - q4_ly_m, 2)})
    return rows


# ------------------------------------------------------------------------------------------------ FY27 hints
FY27 = [
 # (hint_id, date, ids, line, direction_for_fy27_margin, quantified, value, unit, what_was_said, implication_for_fy27, confidence)
 ("H01", "2026-08-06", "S179", "margin_total", "0", "no", "", "", "No 2027 margin guide; 'looking at our track record, you can even see a couple of things'", "Expect the FY27 margin sentence only on 12 Feb 2027, as a floor set 0-50bp below the FY26 print (pattern file). Nothing quantified for FY27 costs today.", "high"),
 ("H02", "2026-08-06", "S162;S155", "ai", "-", "no", "", "", "FY26 guide 'assumes a material increase in terms of the AI spend over the course of the year'; 'an expense that will ramp over the course of the year' (1Q26)", "The 2H26 run-rate of AI/inference opex, not the FY26 average, is the FY27 base: a ramp in 2H26 means FY27 carries a full year of it. Size undisclosed; sits in cost of revenue (hosting) and product development.", "medium"),
 ("H03", "2026-02-12", "K006;K007;Q007", "hosting", "-", "yes", 465, "usd_m/yr purchase obligations due 2027-28 (930/2)", "$1.7bn hosting commitment through 2031; purchase obligations $930m due in 1-3 years", "Hosting floor ~$283m/yr under the new agreement vs ~$224m/yr before; the 2027-28 tranche of purchase obligations (~$465m/yr incl. non-hosting) is roughly double the 2026 tranche ($219m). Cost of revenue ex-payments steps up in FY27.", "high"),
 ("H04", "2026-08-06", "S163;S144;K003", "pd", "+", "no", "", "", "'we don't need to grow our head count at levels that we did in the past'; 2026 headcount and SBC growth 'lower than 2025' (+12.3% to ~8,200)", "FY27 product-development cash growth below the +11-12% of FY25/1H26 if the headcount claim holds; the FY24 'not above revenue growth' guide (C017) missed by 7pts, so discount to +8-10%.", "medium"),
 ("H05", "2026-08-06", "S160;S188;V019;V020", "ops", "+", "yes", -16, "pct y/y support cost per booking (2Q26)", "Support cost per booking -10% (1Q26), -16% (2Q26), 'we expect those costs to continue to decline'; AI handles ~45-50% of tickets; freed agents retrained for premium support", "Ops & support keeps falling per night through FY27 (the one line with a track record: 100% kept, n 13), but savings are partly reinvested (V020) and payroll/insurance/customer-relations components are rising ($41m/$9m/$14m in 1H26, 10-Q). Model -4 to -5%/yr per night, not -16%.", "high"),
 ("H06", "2026-08-06", "S165;S166", "take_rate", "-", "no", "", "", "FY26 take rate 'relatively flat' after customer incentives for new businesses; would have been slightly higher without them", "Incentives are contra-revenue and unsized; if they persist into FY27 the ex-incentive take-rate lift never reaches revenue. FY27 take rate: flat is the base, +10-20bp only if incentives roll off.", "medium"),
 ("H07", "2026-09-08", "V023;V022;V026", "sm_field", "-", "no", "", "", "'major announcements next year'; seller/host services named as the high-margin pool ($1bn 'straight shot')", "New launches in FY27 mean field-ops and launch marketing before revenue (the S100 pattern: investment front-runs revenue). No budget given; FY25's launch cost $200-250m.", "medium"),
 ("H08", "2026-02-12", "S147;S153;V013;F2Q26_sm_total", "sm_brand", "-", "yes", 30, "pct y/y S&M 1H26 (+$372m; $258m marketing spend in emerging markets and partnerships)", "Incremental investment 'in sales and marketing... programmatic marketing, but more so go-to-market'; 1H26 S&M +30% with $258m of paid growth marketing in emerging markets and partnerships", "The expansion-market marketing load is structural (C023: scales down per unit only as markets mature). FY27 S&M growth above revenue growth is the base case; brand statements are 63% kept (n 35).", "medium"),
 ("H09", "2026-02-12", "S148;S157;S134", "tax", "+", "yes", 17.5, "pct long-term ETR (mid-to-high teens)", "OBBBA: long-term ETR mid-to-high teens; FY26 high teens vs 20% FY25", "FY27 ETR 17-19%; below-EBITDA benefit to EPS, not margin.", "high"),
 ("H10", "2026-03-16", "E003;E004", "interest", "-", "yes", 119, "usd_m/yr coupon on $2.5bn notes", "$2.5bn notes at 4.40/4.65/5.25% replaced the 0% converts", "FY27 carries a full year of ~$119m interest expense (FY26 ~9.5 months); first full year of cash interest since IPO. Below EBITDA; hits EPS and FCF.", "high"),
 ("H11", "2026-08-06", "2Q26 letter capital allocation", "other", "0", "yes", 3400, "usd_m buyback authorization remaining at 30 Jun 2026", "$1.1bn repurchased in 2Q26; $3.4bn authorization left; diluted count -10% since 3Q22", "At ~$1.0-1.1bn/quarter the authorization runs out around 1Q27; a new authorization is the FY27 base case (each prior one was renewed before exhaustion).", "high"),
 ("H12", "2026-08-06", "S164;S097;S138;C021", "margin_total", "+", "no", "", "", "'there's a relative floor in our ability to continue to invest against that'; reinvest most efficiencies every year", "The FY27 guide will be a floor at or slightly below the FY26 print, not a step down: four years of 35-37% and every floor beaten (60-140bp). A step-change in AI opex is the one stated risk to that.", "high"),
 ("H13", "2025-08-06", "S127;S182", "sm_field", "-", "no", "", "", "'some of the investments this year will carry into next year as fixed head count'; hotels to exit 2026 'meaningfully larger'", "FY25-26 field-ops headcount is sticky into FY27; hotels supply expansion adds go-to-market cost with single-digit-% revenue.", "medium"),
 ("H14", "2026-08-06", "F2Q26_cor", "cor", "-", "yes", 15, "usd_m 1H26 server-cost increase (reserved-instance amortisation)", "Server costs +$15m in 1H26 'primarily driven by higher amortization related to reserved instance purchases and increased infrastructure spend'; chargeback rate 'slight increase'", "Reserved-instance amortisation is the accounting form of the hosting step (H03); it grows into FY27 as the commitment schedule ramps. Merchant fees stay ~1.8% of GBV.", "high"),
 ("H15", "2026-08-06", "F2Q26_ga", "ga", "+", "yes", -38, "usd_m 1H26 non-income taxes y/y", "G&A +1% in 1H26: payroll +$38m offset by non-income taxes -$38m", "Underlying G&A (ex non-income taxes) is growing ~+8%; the tax-reserve offset is one-off. FY27 G&A growth mid-to-high single digits.", "medium"),
 ("H16", "2026-02-12", "K010;S144", "sbc", "0", "no", "", "", "SBC growth 'lower than 2025' (FY25 +9.9% XBRL / +13.1% letters); unrecognized RSU cost recognised over ~2.9 years", "FY27 SBC growth high single digits; the RSU unrecognized balance sets a floor for FY27 expense (WS02/M7 to tabulate).", "medium"),
]

# ------------------------------------------------------------------------------------------------ misses with a number
MISSES = [  # (line, target, guide, actual, miss_in_units, unit, ids, sign convention: actual - guide)
 ("margin_total", "FY2023", 36.06, 36.84, 78, "bp (actual - 'approx' point)", "S061"),
 ("margin_total", "FY2024", 35.0, 36.40, 140, "bp (actual - Feb floor)", "4Q23 letter"),
 ("margin_total", "FY2024", 35.5, 36.40, 90, "bp (actual - Nov point)", "S095"),
 ("margin_total", "FY2025", 34.5, 35.10, 60, "bp (actual - Feb floor)", "S133 ledger"),
 ("margin_total", "FY2025", 35.0, 35.10, 10, "bp (actual - Nov point)", "S132"),
 ("sm_total", "FY2022", 19.79, 18.05, -174, "bp of revenue (actual - 'flat' guide)", "C003;C006;S038"),
 ("sm_total", "FY2023", 18.05, 17.78, -27, "bp of revenue", "C009;C013"),
 ("sm_total", "FY2024", 17.78, 19.35, 157, "bp of revenue", "S071;S072"),
 ("take_rate", "FY2025", 13.77, 13.41, -36, "bp (guide +20bp on 13.57)", "S110"),
 ("sbc", "FY2023", 20.0, 18.3, -1.7, "pts y/y growth (XBRL)", "S062"),
 ("sbc", "FY2024", 25.0, 30.8, 5.8, "pts y/y growth (XBRL, Nov guide)", "S096"),
 ("sbc", "FY2024", 20.0, 30.8, 10.8, "pts y/y growth (XBRL, May guide)", "1Q24 letter"),
 ("pd", "FY2024", 12.0, 19.4, 7.4, "pts (PD growth - revenue growth)", "C017"),
 ("capex", "FY2021", 37.0, 25.3, -11.7, "usd_m (guide: above 2020's $37m)", "Q004"),
]


# ------------------------------------------------------------------------------------------------ main
def main():
    docs = build_corpus()
    print(f"corpus: {len(docs)} documents: " + ", ".join(f"{k}={sum(1 for d in docs if d.startswith(k))}" for k in ("letter", "call", "conf", "10k", "10q", "8k")))

    rows = load_31a()
    print(f"31a rows carried: {len(rows)}")
    ids31 = {r["statement_id"] for r in rows}

    failures = []
    for (sid, doc_id, speaker, line, period, horizon, direction, quantified, value, unit, verbatim, conf, verdict, outcome, metric, theme) in NEW:
        assert sid not in ids31
        doc = docs.get(doc_id)
        if doc is None:
            failures.append((sid, doc_id, "DOC MISSING")); continue
        q = norm(verbatim)
        ok = q in doc["text"]
        if not ok:
            failures.append((sid, doc_id, verbatim[:80]))
        kind, tag = doc_id.split(":", 1)
        if kind == "conf":
            date, et, ev = CONF_DATE[tag], "conference", CONF_NAME[tag]
        elif kind == "call":
            date, et, ev = PRINT_DATE[tag], "earnings_call", tag
        elif kind == "10k":
            date, et, ev = TENK_DATE[tag], "filing", f"10-K {tag}"
        elif kind == "10q":
            date, et, ev = TENQ_DATE[tag], "filing", f"10-Q {tag}"
        else:
            date, et, ev = tag, "filing", f"8-K {tag}"
        if len(verbatim) > 300:
            failures.append((sid, doc_id, f"verbatim {len(verbatim)} chars > 300"))
        rows.append({
            "statement_id": sid, "date": date, "event_type": et, "event": ev,
            "source_detail": {"conf": "conference-sa", "call": "call-QA" + ("-sa" if "transcripts/web" in doc["raw"] else ""), "10k": "10-K", "10q": "10-Q", "8k": "8-K"}[kind],
            "speaker": speaker, "line": line, "line_31a": "", "period_referenced": period, "horizon": horizon, "direction": direction,
            "quantified": quantified, "value": value, "unit": unit, "verbatim": verbatim, "quote_verified": "yes" if ok else "NO",
            "source_path_or_url": doc["raw"], "locator": "substring of normalised document", "confidence": conf, "verdict": verdict,
            "kept_or_missed": f"{verdict}: {outcome}" if verdict in ("kept", "partly", "missed") else f"{verdict}: {outcome}",
            "implied_metric": metric, "theme": theme, "origin": "v2_hand",
        })
    n_hand = len(rows) - len(ids31)
    auto = mda_rows(docs)
    rows.extend(auto)
    print(f"new hand rows: {n_hand}; 10-Q MD&A rows: {len(auto)}; total {len(rows)}")

    cols = ["statement_id", "date", "event_type", "event", "source_detail", "speaker", "line", "line_31a", "period_referenced", "horizon",
            "direction", "quantified", "value", "unit", "verbatim", "source_path_or_url", "locator", "quote_verified", "confidence",
            "verdict", "kept_or_missed", "implied_metric", "theme", "origin"]
    df = pd.DataFrame(rows)[cols].sort_values(["date", "statement_id"], kind="stable")
    df.to_csv(OUT / "05_statements.csv", index=False, encoding="utf-8")
    print(f"wrote 05_statements.csv ({len(df)} rows)")

    # ---- pattern -------------------------------------------------------------------------------------------------
    panel = pd.read_csv(ROOT / "data/processed/abnb_quarterly_costlines.csv")[["quarter", "revenue_musd", "adjusted_ebitda_musd"]]
    prow, fy_margin = pattern_rows(panel)
    pdf = pd.DataFrame(prow)
    pdf.to_csv(OUT / "05_guide_language_pattern.csv", index=False, encoding="utf-8")
    print(f"wrote 05_guide_language_pattern.csv ({len(pdf)} rows); FY margins from panel: " + ", ".join(f"{y}: {m:.2f}" for y, m in sorted(fy_margin.items()) if y >= 2021))

    stats = []
    def add(name, sub, col):
        v = sub[col].dropna().astype(float)
        if len(v):
            stats.append({"statistic": name, "n": len(v), "mean": round(v.mean(), 1), "min": round(v.min(), 1), "max": round(v.max(), 1),
                          "rows": ";".join(sub.loc[v.index, "print"])})
    closed = pdf[pdf.actual_fy_margin_pct.notna()]
    # one observation per fiscal year for the February floor (first numeric floor of the year) and for the November point
    feb_floor = closed[(closed.fy_sentence_type == "floor")].drop_duplicates("fy_target", keep="first")
    add("beat vs numeric FY floor (bp, one obs per FY: FY24, FY25)", feb_floor, "actual_minus_guide_bp")
    add("beat vs November point/approx (bp): FY23, FY24, FY25", closed[closed.is_november & closed.fy_sentence_type.isin(["approx", "approx_yoy"])], "actual_minus_guide_bp")
    add("beat vs February qualitative y/y guide (bp): FY22 'in-line', FY23 'maintain'", closed[closed.fy_sentence_type == "point_yoy"].drop_duplicates("fy_target"), "actual_minus_guide_bp")
    add("Q4 actual minus implied-by-November-FY-sentence (pts): FY23, FY24, FY25", closed[closed.is_november & closed.implied_q4_margin_source.str.startswith("FY")], "q4_actual_minus_implied_pts")
    add("Q4 actual minus November Q4-sentence floor (pts): FY21, FY22 (no FY number those years)", closed[closed.is_november & closed.implied_q4_margin_source.str.startswith("Q4")], "q4_actual_minus_implied_pts")
    add("Q4 actual minus November-implied Q4 margin (pts), all five Novembers", closed[closed.is_november & closed.implied_q4_margin_pct.notna()], "q4_actual_minus_implied_pts")
    add("YTD (9M) margin y/y at the November print (pts), all Novembers", pdf[pdf.is_november], "ytd_margin_yoy_pts")
    pd.DataFrame(stats).to_csv(OUT / "05_guide_language_stats.csv", index=False, encoding="utf-8")
    print("wrote 05_guide_language_stats.csv")

    sc = pd.DataFrame(nov2026_scenarios(panel))
    sc.to_csv(OUT / "05_nov2026_scenarios.csv", index=False, encoding="utf-8")
    print(f"wrote 05_nov2026_scenarios.csv ({len(sc)} rows)")

    # ---- FY27 hints ---------------------------------------------------------------------------------------------
    h = pd.DataFrame(FY27, columns=["hint_id", "date", "statement_ids", "line", "direction_for_fy27_margin", "quantified", "value", "unit",
                                    "what_was_said", "implication_for_fy27", "confidence"])
    known = set(df.statement_id)
    h["ids_resolved"] = h.statement_ids.map(lambda s: all((i in known) or (not i.startswith(("S", "V", "C", "K", "Q", "E", "F"))) for i in s.split(";")))
    h.to_csv(OUT / "05_fy27_hints.csv", index=False, encoding="utf-8")
    print(f"wrote 05_fy27_hints.csv ({len(h)} rows; ids resolved: {int(h.ids_resolved.sum())}/{len(h)})")

    # ---- reliability --------------------------------------------------------------------------------------------
    fwd = df[(df.origin != "10q_mda")]
    closedv = fwd[fwd.verdict.isin(["kept", "partly", "missed"])]
    rel = []
    miss = pd.DataFrame(MISSES, columns=["line", "target", "guide", "actual", "miss", "unit", "ids"])
    for line, g in closedv.groupby("line"):
        c = Counter(g.verdict)
        n = len(g)
        m = miss[miss.line == line]
        rel.append({"line": line, "n_closed": n, "kept": c["kept"], "partly": c["partly"], "missed": c["missed"],
                    "kept_rate_pct": round(100 * c["kept"] / n, 0), "kept_or_partly_rate_pct": round(100 * (c["kept"] + c["partly"]) / n, 0),
                    "n_open": int((fwd.line == line).sum() - n), "n_31a": int((g.origin == "31a").sum()), "n_new": int((g.origin != "31a").sum()),
                    "n_numeric_misses": len(m), "mean_signed_miss": None if not len(m) else round(m.miss.mean(), 1),
                    "mean_abs_miss": None if not len(m) else round(m.miss.abs().mean(), 1), "miss_unit": "" if not len(m) else m.unit.iloc[0].split(" (")[0],
                    "miss_ids": ";".join(m.ids)})
    rel = pd.DataFrame(rel).sort_values("n_closed", ascending=False)
    rel.to_csv(OUT / "05_reliability_by_line.csv", index=False, encoding="utf-8")
    ev = []
    for (et, sp), g in closedv.groupby(["event_type", "speaker"]):
        c = Counter(g.verdict); n = len(g)
        ev.append({"event_type": et, "speaker": sp, "n_closed": n, "kept": c["kept"], "partly": c["partly"], "missed": c["missed"], "kept_rate_pct": round(100 * c["kept"] / n, 0)})
    for et, g in closedv.groupby("event_type"):
        c = Counter(g.verdict); n = len(g)
        ev.append({"event_type": et, "speaker": "ALL", "n_closed": n, "kept": c["kept"], "partly": c["partly"], "missed": c["missed"], "kept_rate_pct": round(100 * c["kept"] / n, 0)})
    pd.DataFrame(ev).sort_values(["event_type", "n_closed"], ascending=[True, False]).to_csv(OUT / "05_reliability_by_event.csv", index=False, encoding="utf-8")
    print("wrote 05_reliability_by_line.csv, 05_reliability_by_event.csv")

    # ---- pass line ----------------------------------------------------------------------------------------------
    new = df[df.origin != "31a"]
    non_earn = new[~new.event_type.isin(["earnings_call", "letter"])]
    novs = pdf[pdf.is_november & (pdf.fy_target >= "FY2021")]
    nov_ok = novs.implied_q4_margin_pct.notna().all() and novs.q4_actual_minus_implied_pts.notna().all()
    print(f"\nPASS LINE: new dated statements {len(new)} (>=40: {'ok' if len(new) >= 40 else 'FAIL'}); "
          f"from non-earnings events {len(non_earn)} across {non_earn.event.nunique()} events (>=6: {'ok' if len(non_earn) >= 6 else 'FAIL'}); "
          f"November rows {len(novs)} ({', '.join(novs.print)}), implied Q4 margin computed and checked against the actual for all: {'ok' if nov_ok else 'FAIL'} "
          f"(3Q21/3Q22 from the Q4 sentence: no FY number was given those years; 3Q23-3Q25 from the FY sentence)")
    # the pattern table's sentences must also be exact substrings of the letter (or, failing that, the call transcript)
    for tag, row in FY_SENTENCE.items():
        for label, sent in (("FY", row[1]), ("Q", row[6])):
            s2 = norm(sent.replace("...", "").strip())
            if s2 and s2 not in docs[f"letter:{tag}"]["text"] and s2 not in docs.get(f"call:{tag}", {}).get("text", ""):
                failures.append((f"pattern:{tag}:{label}", f"letter:{tag}", sent[:80]))
    print("by event_type (all rows):", dict(Counter(df.event_type)))
    print("by line (all rows):", dict(Counter(df.line)))
    if failures:
        print(f"\n{len(failures)} VERIFICATION FAILURES:")
        for f in failures:
            print("  ", f)
        sys.exit(1)
    print("\nall new verbatims verified as exact substrings of their source documents")


if __name__ == "__main__":
    main()
