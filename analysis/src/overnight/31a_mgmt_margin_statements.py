"""Workstream 31a: every forward-looking statement Airbnb management has made about margin
structure and cost lines (Q4 2020 print through Q2 2026 print), and the operating profile those
statements imply by cost line for FY2026-FY2028.

Reads (raw text only - the CSVs below are rebuilt from these on every run)
  data/raw/letters/<q>Q<yy>_*.htm                23 shareholder letters (8-K Ex. 99.1), 4Q20..2Q26.
  data/raw/regulatory/transcripts/<yyyy>-Q<n>.pdf FactSet corrected transcripts, 1Q23..1Q26 (14 files).
  data/raw/transcripts/ir/{4Q21,2Q26}.pdf         FactSet corrected transcripts fetched from the IR CDN
                                                  (4Q21 and 2Q26 are not in the regulatory folder).
  data/raw/transcripts/web/<tag>.html             stockanalysis.com speaker-tagged transcripts. Used as the
                                                  quote source for the 8 calls with no FactSet copy on this
                                                  machine (4Q20, 1Q21, 2Q21, 3Q21, 1Q22, 2Q22, 3Q22, 4Q22)
                                                  and for 5 investor-conference appearances.
  data/processed/abnb_quarterly_costlines.csv     realised cost lines, for the outcome columns.
  data/processed/overnight/03_forward_claims.csv  the 83 curated claims of workstream 03; this script keeps
                                                  their ids in claim_id_03 where a statement overlaps.

Writes
  data/processed/overnight/31a_mgmt_margin_statements.csv  one row per forward-looking statement
  data/processed/overnight/31a_margin_algorithm_quotes.csv the structural "how we think about margin" set
  data/processed/overnight/31a_mgmt_implied_profile.csv    cost line x FY2026/27/28 implied trajectory

Quote discipline
  Every `quote` is checked to be an exact substring of the source document after whitespace
  normalisation (runs of whitespace -> one space; curly quotes/dashes -> ASCII). The `quote_verified`
  column carries the result and the script prints every failure. Nothing here is paraphrased unless the
  theme column says `paraphrase`. Quotes are capped at 45 words.
  The 8 pre-2023 calls and the 5 conferences are quoted from stockanalysis.com transcripts, which are
  audio-aligned rather than FactSet-corrected; `source` carries the suffix `-sa` for those rows so a
  reader can discount the wording by a word or two. Everything from 1Q23 on is FactSet corrected.

Point-in-time
  `date` is the day the statement was made (letter 16:05 ET / call ~17:30 ET on print day).
  `outcome_if_closed` names the number that settled it and the print at which it became known.

Run: py -3.13 analysis/src/overnight/31a_mgmt_margin_statements.py
"""
import csv
import html
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MAIN = ROOT.parent / "citadel-abnb"
OUT = ROOT / "data" / "processed" / "overnight"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "analysis" / "src"))
from transcript_analytics import parse_ir  # noqa: E402


def data_dir(rel):
    """Raw data is git-ignored and lives in the main tree; prefer a local copy if there is one."""
    for base in (ROOT, MAIN):
        p = base / rel
        if p.exists():
            return p
    raise FileNotFoundError(rel)


# ------------------------------------------------------------------------------------------------
# Text normalisation and corpus
# ------------------------------------------------------------------------------------------------
TAGRE = re.compile(r"<[^>]+>")


def norm(s):
    s = s.replace(" ", " ")
    s = (s.replace("’", "'").replace("‘", "'").replace("“", '"')
          .replace("”", '"').replace("–", "-").replace("—", "-").replace("�", "-"))
    return re.sub(r"\s+", " ", s).strip()


def detag(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</(p|div|h\d|li|tr)>", "\n", s, flags=re.I)
    s = TAGRE.sub(" ", s)
    s = html.unescape(s)
    return s


def pdf_text(path):
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as fh:
        tmp = Path(fh.name)
    # -enc UTF-8 matters: without it poppler drops the FactSet en-dashes to U+FFFD and
    # quotes that span a dash stop matching.
    subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", str(path), str(tmp)], check=True)
    txt = tmp.read_text(encoding="utf-8", errors="replace")
    tmp.unlink(missing_ok=True)
    return txt


def parse_sa(raw):
    """stockanalysis.com transcript -> [(speaker, title, text)]."""
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


CALL_ORDER = ["4Q20", "1Q21", "2Q21", "3Q21", "4Q21", "1Q22", "2Q22", "3Q22", "4Q22",
              "1Q23", "2Q23", "3Q23", "4Q23", "1Q24", "2Q24", "3Q24", "4Q24",
              "1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26"]
IR_FROM_REGULATORY = {f"{q}Q{yy}": f"20{yy}-Q{q}" for yy in ("23", "24", "25", "26") for q in "1234"}
CONFS = ["MS23", "MS24", "BERN24", "GS24", "GS25"]

PRINT_DATE = {  # call date == letter date (letter 16:05 ET, call ~17:30 ET)
    "4Q20": "2021-02-25", "1Q21": "2021-05-13", "2Q21": "2021-08-12", "3Q21": "2021-11-04",
    "4Q21": "2022-02-15", "1Q22": "2022-05-03", "2Q22": "2022-08-02", "3Q22": "2022-11-01",
    "4Q22": "2023-02-14", "1Q23": "2023-05-09", "2Q23": "2023-08-03", "3Q23": "2023-11-01",
    "4Q23": "2024-02-13", "1Q24": "2024-05-08", "2Q24": "2024-08-06", "3Q24": "2024-11-07",
    "4Q24": "2025-02-13", "1Q25": "2025-05-01", "2Q25": "2025-08-06", "3Q25": "2025-11-06",
    "4Q25": "2026-02-12", "1Q26": "2026-05-07", "2Q26": "2026-08-06",
    "MS23": "2023-03-07", "MS24": "2024-03-05", "BERN24": "2024-05-30",
    "GS24": "2024-09-10", "GS25": "2025-09-09",
}


def build_corpus():
    """doc_id -> {"raw": <path relative to repo root>, "text": normalised text, "turns": [(hdr, text)]}"""
    docs = {}

    # --- shareholder letters -------------------------------------------------------------------
    ldir = data_dir("data/raw/letters")
    for p in sorted(ldir.glob("*.htm")):
        tag = p.name.split("_")[0]
        body = detag(p.read_text(encoding="utf-8", errors="replace"))
        paras = [norm(x) for x in body.split("\n") if len(x.split()) > 3]
        docs[f"letter:{tag}"] = {"raw": f"data/raw/letters/{p.name}",
                                 "text": norm(body),
                                 "turns": [(f"para {i}", t) for i, t in enumerate(paras)]}

    # --- FactSet corrected transcripts ---------------------------------------------------------
    reg = data_dir("data/raw/regulatory/transcripts")
    ir_extra = ROOT / "data" / "raw" / "transcripts" / "ir"
    ir_paths = {}
    for tag, per in IR_FROM_REGULATORY.items():
        p = reg / f"{per}.pdf"
        if p.exists():
            ir_paths[tag] = (p, f"data/raw/regulatory/transcripts/{per}.pdf")
    for tag in ("4Q21", "2Q26"):
        p = ir_extra / f"{tag}.pdf"
        if p.exists():
            ir_paths[tag] = (p, f"data/raw/transcripts/ir/{tag}.pdf")
    for tag, (p, rel) in ir_paths.items():
        _date, turns = parse_ir(pdf_text(p))
        tt = [(f"{t['section']}|{t['role']}|{t['speaker']}", norm(t["text"])) for t in turns]
        docs[f"call:{tag}"] = {"raw": rel, "text": " ".join(t[1] for t in tt), "turns": tt}

    # --- stockanalysis.com transcripts (pre-2023 calls and the conferences) --------------------
    wdir = ROOT / "data" / "raw" / "transcripts" / "web"
    for p in sorted(wdir.glob("*.html")):
        tag = p.stem
        key = f"conf:{tag}" if tag in CONFS else f"call:{tag}"
        if key in docs:  # a FactSet copy already won
            continue
        turns = parse_sa(p.read_text(encoding="utf-8", errors="replace"))
        tt = [(f"{sp}|{ti}", tx) for sp, ti, tx in turns]
        docs[key] = {"raw": f"data/raw/transcripts/web/{p.name}",
                     "text": " ".join(t[1] for t in tt), "turns": tt}
    return docs


def locate(doc, quote):
    """Return (verified, locator). Locator names the turn / paragraph the quote sits in."""
    q = norm(quote)
    for i, (hdr, txt) in enumerate(doc["turns"]):
        if q in txt:
            return True, f"turn {i} [{hdr}]"
    if q in doc["text"]:
        return True, "spans turns"
    return False, "NOT FOUND"


# ------------------------------------------------------------------------------------------------
# The catalogue.
# Each row: (sid, doc_id, source, speaker, quote, theme, cost_line, horizon, quantified,
#            implied_metric, implied_direction_for_margin, outcome_if_closed, verdict, claim_id_03)
#   doc_id      "letter:<tag>" | "call:<tag>" | "conf:<tag>"
#   source      letter | call-prepared | call-QA | conference   (a "-sa" suffix is added automatically
#               for documents quoted from stockanalysis.com rather than a FactSet corrected transcript)
#   cost_line   cost_of_revenue | ops_support | product_dev | brand_marketing | field_ops | g_and_a |
#               sbc | take_rate | fx | total_margin | other
#   horizon     next-quarter | full-year | multi-year | structural
#   verdict     kept | partly | missed | open | unverifiable
# ------------------------------------------------------------------------------------------------
S = [
 # ============================== 4Q20 print, 25 Feb 2021 =====================================
 ("S001", "call:4Q20", "call-QA", "Dave Stephenson",
  "What we would expect to achieve over time is 30% EBITDA margins or greater.",
  "margin_algorithm", "total_margin", "multi-year", "yes",
  "adj. EBITDA margin >=30% at some future date", "+",
  "FY2022 adj. EBITDA margin 34.56% (abnb_quarterly_costlines.csv), cleared in the second year after the claim; FY2023 36.84%, FY2024 36.40%, FY2025 35.10%. Known 14 Feb 2023.",
  "kept", "C001"),
 ("S002", "call:4Q20", "call-QA", "Dave Stephenson",
  "Our sales and marketing expenses as a percentage of revenue in 2021 will be below that of 2019. The absolute dollars in 2021 will be below that of 2019.",
  "marketing", "brand_marketing", "full-year", "yes",
  "FY21 S&M % of revenue < FY19 33.7%; FY21 S&M $ < FY19 $1,621m", "+",
  "FY2021 S&M 19.79% of revenue (abnb_quarterly_costlines.csv) and ~$1.19bn of spend, both far below 2019's 33.7% and $1,622m. Known 15 Feb 2022.",
  "kept", "C002"),
 ("S003", "call:4Q20", "call-QA", "Brian Chesky",
  "We don't intend to ever again spend the amount of money as a percentage of revenue on marketing in the future as we did in 2019.",
  "marketing", "brand_marketing", "structural", "yes",
  "S&M % of revenue permanently < 33.7%", "+",
  "Still true: the peak since is 1H2026 at 25.87% of revenue against 33.7% in 2019. But S&M % has risen every year since 2022 (18.05 -> 17.78 -> 19.35 -> 21.14 -> 25.87 in 1H26). Open-ended claim.",
  "kept", "C003"),
 ("S004", "call:4Q20", "call-QA", "Dave Stephenson",
  "We've made substantial reductions in our fixed costs. We will not be having to add back fixed costs to support a business that will, again, approach 2019 levels and beyond.",
  "fixed_cost_discipline", "product_dev", "structural", "no",
  "fixed cost base does not scale back with volume recovery", "+",
  "Headcount at 2Q24 was 'essentially the same amount of employees as before the pandemic and double the revenue' (Chesky, 2Q24 call). Kept through 2024; head count then grew again for the new businesses in 2025.",
  "kept", ""),
 ("S005", "call:4Q20", "call-QA", "Dave Stephenson",
  "It's that discipline of variable expenses, things like cost of payments, community support expenses, infrastructure expenses, all the way down, that we're proud of.",
  "margin_algorithm", "cost_of_revenue", "structural", "no",
  "names the three variable-cost levers used ever since: payments, support, infrastructure", "+",
  "The same three lines are named in 1Q23, 2Q23, 3Q23 and 4Q24. Cost of revenue fell from 24.5% of revenue in FY2021 to ~18.4% in FY2025.",
  "kept", ""),
 ("S006", "call:4Q20", "call-QA", "Dave Stephenson",
  "I'd love to give you specific targets for 2021, but it's just too hard to know what our revenue is going to be",
  "declined_to_quantify", "total_margin", "full-year", "no",
  "no FY2021 margin guide given", "0",
  "No FY2021 margin guide was ever given; the first FY margin guide is the 4Q21 letter (Feb 2022).",
  "kept", "C005"),
 ("S007", "call:4Q20", "call-QA", "Brian Chesky",
  "We are very focused on reducing the need for people to call us or message us because they have a problem. If they do have to call us or message us, we are going to focus on making our agents significantly more efficient.",
  "support_cost", "ops_support", "structural", "no",
  "contact rate down and cost per contact down", "+",
  "Ops & support fell from 25.98% of revenue in FY2020 and 14.13% in FY2021 to 10.84% in FY2025; contact-rate reduction is quantified only from 1Q24 (Guest Favorites) and cost per booking only from 1Q26 (-10% y/y) and 2Q26 (-16% y/y).",
  "kept", ""),
 ("S008", "call:4Q20", "call-QA", "Dave Stephenson",
  "With the relatively lower revenue in the first half than the second half, our operations support expenses percent of revenue will be a little bit higher in the first half than the second half.",
  "seasonality", "ops_support", "full-year", "no",
  "1H21 ops&support % of revenue > 2H21", "0",
  "1H21 ops & support ran well above the 2H21 rate on a much smaller revenue base (FY2021 line 14.13% of revenue, abnb_quarterly_costlines.csv). Known 15 Feb 2022.",
  "kept", ""),
 ("S009", "letter:4Q20", "letter", "shareholder letter",
  "We expect that sales and marketing expenses as a percentage of revenue in the first half of 2021 will be higher than that of the second half.",
  "seasonality", "brand_marketing", "full-year", "no",
  "1H21 S&M % of revenue > 2H21", "0",
  "1H21 S&M ran well above 2H21 as a share of revenue, with the Made Possible by Hosts campaign in the first half (FY2021 line 19.79%). Known 15 Feb 2022.",
  "kept", ""),
 ("S010", "letter:4Q20", "letter", "shareholder letter",
  "We plan to invest in our community support and trust platforms in the first half of 2021, ensuring that we are ready for the rebound in travel when it comes.",
  "support_cost", "ops_support", "full-year", "no",
  "ops&support spend front-loaded into 1H21", "-",
  "1H21 ops & support ran materially above the 2H21 rate; the FY2021 line was 14.13% of revenue. Kept.",
  "kept", ""),
 ("S011", "call:4Q20", "call-QA", "Brian Chesky",
  "We're starting this year with investing more in brand marketing. We're going to be doing digital advertising all over the world, and I expect in the coming years, we're going to be targeting key countries that are emerging opportunities for us.",
  "marketing", "brand_marketing", "multi-year", "no",
  "brand marketing extends country by country over several years", "-",
  "Held exactly: expansion-market brand campaigns are named as a marketing driver in 4Q21, 1Q23, 4Q23, 3Q24, 4Q24, 1Q26.",
  "kept", ""),
 ("S012", "call:4Q20", "call-QA", "Dave Stephenson",
  "we could see opportunities for further increases of take rate. We would always want to give more back to the community before we would increase that take rate.",
  "take_rate", "take_rate", "structural", "no",
  "take rate only rises after new services ship", "+",
  "Held: the only take-rate increases since are the cross-currency fee (Apr 2024, ~+20bp annualised) and paid guest travel insurance; the 2023 change was a cut for stays over 3 months.",
  "kept", ""),

 # ============================== 1Q21 print, 13 May 2021 =====================================
 ("S013", "call:1Q21", "call-QA", "Dave Stephenson",
  "We're not going to have to add back a significant number of fixed resources in order to accommodate the business that's back to the size of 2019 and beyond. We're just going to be very disciplined in any additions to our expenses.",
  "fixed_cost_discipline", "product_dev", "structural", "no",
  "fixed cost growth decoupled from revenue growth", "+",
  "Held through 2024: headcount ~flat 2020-2024 while revenue doubled. Reversed at the margin in 2025 for services/experiences field ops.",
  "kept", ""),
 ("S014", "letter:1Q21", "letter", "shareholder letter",
  "Consistent with last quarter, we expect that sales and marketing expenses as a percentage of revenue in the first half of 2021 will be higher than that of the second half.",
  "seasonality", "brand_marketing", "full-year", "no",
  "1H21 S&M % of revenue > 2H21", "0",
  "1H21 S&M % of revenue above 2H21. Kept.",
  "kept", ""),
 ("S015", "call:1Q21", "call-QA", "Dave Stephenson",
  "The majority of the ADR that we're seeing is from mix.",
  "adr", "other", "next-quarter", "no",
  "ADR strength is mix, not price - so it is reversible", "0",
  "By 2Q22 management had reversed this: 'about 2/3 of that increase has been price appreciation and about 1/3 due to mix' (2Q22 call).",
  "partly", ""),

 # ============================== 2Q21 print, 12 Aug 2021 =====================================
 ("S016", "call:2Q21", "call-QA", "Dave Stephenson",
  "We've stated that we could achieve 30% or more EBITDA margins over time. Clearly, we've accelerated our rate there.",
  "margin_algorithm", "total_margin", "multi-year", "yes",
  "30%+ adj. EBITDA margin reaffirmed", "+",
  "FY2021 26.57%, FY2022 34.56%. Cleared in FY2022. Known 14 Feb 2023.",
  "kept", ""),
 ("S017", "call:2Q21", "call-QA", "Dave Stephenson",
  "Over time, we will see some variation in our EBITDA margins over time. I think what we've demonstrated is the capability to dramatically expand those margins.",
  "margin_algorithm", "total_margin", "multi-year", "no",
  "no straight-line margin path promised", "0",
  "Realised FY adj. EBITDA margins: 26.57 (21), 34.56 (22), 36.84 (23), 36.40 (24), 35.10 (25). Roughly a 2pt band around a 35-37% plateau since 2022.",
  "kept", ""),
 ("S018", "letter:2Q21", "letter", "shareholder letter",
  "we expect that sales and marketing expense as a percentage of revenue in the second half of 2021 will be lower than that of the first half",
  "seasonality", "brand_marketing", "full-year", "no",
  "2H21 S&M % of revenue < 1H21", "0",
  "2H21 S&M % of revenue below 1H21. Kept.",
  "kept", ""),
 ("S019", "call:2Q21", "call-QA", "Dave Stephenson",
  "Over time, I think there are opportunities for us to increase our monetization through new opportunities, whether that be guest travel insurance, maybe promoted listings, or other things that we could do, but we don't see those as perishable opportunities.",
  "take_rate", "take_rate", "multi-year", "no",
  "take rate expansion comes from new products, not fee rises", "+",
  "Guest travel insurance shipped 2022 and is still being extended (12 largest countries as of 4Q24). Promoted listings/advertising still not shipped as of 2Q26 - Chesky said in 3Q25 that ads wait for AI search.",
  "partly", ""),

 # ============================== 3Q21 print, 4 Nov 2021 ======================================
 ("S020", "call:3Q21", "call-QA", "Dave Stephenson",
  "On a relative basis, our marketing expenses as a percentage of revenue are down from levels we had in 2019, and we should anticipate that it'll be in this kind of range for the foreseeable future.",
  "marketing", "brand_marketing", "multi-year", "yes",
  "S&M % of revenue holds near the FY2021 level (19.8%)", "0",
  "FY22 18.05, FY23 17.78, FY24 19.35, FY25 21.14, 1H26 25.87. Held for three years then broke to the upside once services/experiences field ops entered the line.",
  "partly", ""),
 ("S021", "call:3Q21", "call-QA", "Dave Stephenson",
  "What we do anticipate as urban comes back and more markets like Asia and Latin America, which have lower average daily rates, we anticipate the overall ADR to moderate some.",
  "adr", "other", "multi-year", "no",
  "geographic mix pulls ADR down as international scales", "-",
  "ADR did not fall: it kept rising through 2022 on price appreciation, was roughly flat 2023-2024, and rose again in 2025-26 on bedroom-night mix and FX. The mix drag exists but has been outweighed.",
  "missed", ""),

 # ============================== 4Q21 print, 15 Feb 2022 =====================================
 ("S022", "letter:4Q21", "letter", "shareholder letter",
  "Adjusted EBITDA margin to be directionally in-line with 2021 as sales and marketing expense as a percent of revenue is expected to remain relatively flat and incremental variable cost improvements and fixed cost discipline is potentially offset by lower ADR",
  "fy_margin_guide", "total_margin", "full-year", "no",
  "FY22 adj. EBITDA margin ~= FY21 26.8%; S&M % flat; variable-cost gains offset by ADR", "0",
  "FY2022 came in at 34.56%, +799bp on FY2021's 26.57% (02_fy_guide_revisions.csv scores the y/y guide of 0.0pts against an actual of +7.99pts) - the largest FY margin guide beat in the record. ADR rose instead of falling. Known 14 Feb 2023.",
  "missed", ""),
 ("S023", "call:4Q21", "call-QA", "David E. Stephenson",
  "we've already achieved that new baseline and likely not to achieve substantial improvement in the marketing expense as a percentage of revenue this year",
  "marketing", "brand_marketing", "full-year", "yes",
  "FY22 S&M % of revenue ~= FY21 19.8%", "0",
  "FY2022 S&M 18.05% of revenue, 175bp better than FY2021 (02_guidance_ledger.csv scores the 'relatively flat' guide against an actual of -174.66bp). Known 14 Feb 2023.",
  "partly", ""),
 ("S024", "call:4Q21", "call-QA", "David E. Stephenson",
  "on the product development expenses, again, we're growing our product development expenses more slowly than we're growing revenue. So, we're going to continue to get leverage and discipline on our focused, kind of, product development efforts",
  "headcount", "product_dev", "full-year", "no",
  "product development grows slower than revenue", "+",
  "FY2022 product development 17.88% of revenue vs 23.78% in FY2021: leverage delivered. Reversed from FY2024 (18.52%) and FY2025 (19.23%) as the new businesses were staffed.",
  "kept", ""),
 ("S025", "call:4Q21", "call-QA", "David E. Stephenson",
  "we're continuing to focus more of our spend on brand marketing and less on the search engine marketing. And you are right that the brand marketing then should be more fixed. It's more of a fixed investment.",
  "marketing", "brand_marketing", "structural", "no",
  "brand is a fixed cost per market; performance is variable", "+",
  "Restated verbatim by Mertz in 4Q24: 'effectively a fixed amount of spend for each market'. The claim is the load-bearing assumption behind every marketing guide since.",
  "kept", ""),
 ("S026", "call:4Q21", "call-QA", "David E. Stephenson",
  "Once we're penetrated in most of the countries around the world, we can see more leverage because it becomes more of a fixed cost, and as you grow revenue, we can kind of grow revenue out above the marketing.",
  "marketing", "brand_marketing", "multi-year", "no",
  "S&M % of revenue falls from 2023 as market coverage completes", "+",
  "FY2023 17.78% (-27bp, a token gain), then FY2024 19.35%, FY2025 21.14%, 1H26 25.87%. The promised post-2023 marketing leverage never arrived; the opposite happened.",
  "missed", ""),
 ("S027", "call:4Q21", "call-QA", "David E. Stephenson",
  "we anticipate our marketing expense as percentage of revenue in 2022 to be relatively consistent with that in 2021. So, I'm not anticipating further deleverage and also not anticipating a lot of incremental leverage.",
  "marketing", "brand_marketing", "full-year", "yes",
  "FY22 S&M % of revenue ~= 19.8%", "0",
  "FY2022 18.05%, a 175bp beat on a flat guide. Known 14 Feb 2023.",
  "partly","C014"),
 ("S028", "call:4Q21", "call-QA", "David E. Stephenson",
  "If ADRs remain higher and stronger, that's a tailwind to EBITDA. As the business rebounds more urban, more lower ADR regions and ADRs moderate some, that will be continued headwind for our margins.",
  "adr", "total_margin", "multi-year", "no",
  "ADR is a direct margin driver: +/-1% ADR flows to margin", "0",
  "The mechanism is right and management has repeated it every year since, but the ADR direction they feared never materialised: ADR rose in 2022 and margin expanded 799bp. Workstream 03 scores the same statement missed (C016) - the mechanism survives, the forecast did not.",
  "partly", "C016"),
 ("S029", "call:4Q21", "call-QA", "David E. Stephenson",
  "those lower take rates and ADRs are offset by the fact that they're longer than short- term stays and the costs actually support them, so lower customer support costs, and actually having more nights booked",
  "take_rate", "take_rate", "structural", "no",
  "long stays: lower take rate but lower support cost per night; similar contribution margin", "0",
  "Never disclosed at a level that can be tested; Airbnb has never published contribution margin by stay length.",
  "unverifiable", ""),

 # ============================== 1Q22 print, 3 May 2022 ======================================
 ("S030", "letter:1Q22", "letter", "shareholder letter",
  "For the full year, we currently expect sales and marketing expense as a percent of revenue to remain relatively flat compared to 2021, while continued fixed cost discipline may be offset by the impact of lower ADR.",
  "marketing", "brand_marketing", "full-year", "yes",
  "FY22 S&M % of revenue ~= 19.8%", "0",
  "FY2022 18.05%, a 175bp beat; the ADR offset did not arrive. Known 14 Feb 2023.",
  "partly", ""),
 ("S031", "call:1Q22", "call-QA", "Dave Stephenson",
  "One of the things we noted in the letter is that we're expecting, you know, for the full year, a modest expansion in our overall EBITDA margin rate.",
  "fy_margin_guide", "total_margin", "full-year", "no",
  "FY22 adj. EBITDA margin modestly above FY21 26.8%", "+",
  "FY2022 34.56%: +799bp on FY2021, not 'modest'. The single largest FY margin beat in the record. Known 14 Feb 2023.",
  "kept","C018"),

 # ============================== 2Q22 print, 2 Aug 2022 ======================================
 ("S032", "call:2Q22", "call-QA", "Dave Stephenson",
  "We're growing headcount. You know, maybe high single-digit percentage rates, but that is gonna be able to support us for the very long term, and we're gonna remain very focused and disciplined in our investments.",
  "headcount", "product_dev", "full-year", "yes",
  "headcount growth ~ high single digits", "-",
  "Actual FY2022 headcount growth was well under that; by 4Q23 Stephenson said 'we grew head count last year about 1%'. Management over-guided its own hiring.",
  "missed", ""),
 ("S033", "call:2Q22", "call-QA", "Dave Stephenson",
  "we anticipate, you know, marketing as a percentage of revenue in 2022 to be consistent with 2021. A modest increase in the back half of the year.",
  "marketing", "brand_marketing", "full-year", "yes",
  "FY22 S&M % of revenue ~= 19.8%", "0",
  "FY2022 18.05%, a 175bp beat. Known 14 Feb 2023.",
  "partly","C021"),

 # ============================== 3Q22 print, 1 Nov 2022 ======================================
 ("S034", "call:3Q22", "call-QA", "Dave Stephenson",
  "We're seeing great leverage in our fixed costs. We're being incredibly disciplined in our fixed cost growth, and that will continue going forward.",
  "fixed_cost_discipline", "product_dev", "multi-year", "no",
  "fixed cost growth < revenue growth", "+",
  "Held 2022-2024 (headcount ~+1% in 2023, ~4% guided). Broken at the margin in 2025-26 as field ops headcount was added for services/experiences.",
  "partly", ""),
 ("S035", "call:3Q22", "call-QA", "Dave Stephenson",
  "I think the improvements in our variable costs and the fixed cost leverage should enable us to maintain or even increase free cash flow margins over the longer term.",
  "margin_algorithm", "total_margin", "multi-year", "no",
  "FCF margin held or grown despite ADR headwind", "+",
  "FCF margin: FY2023 ~41%, FY2024 40%, FY2025 ~37%, TTM to 2Q26 37%. Down ~4pts from the peak against a promise to maintain or increase. Workstream 03 scores it missed (C023) and that is the right read; Reserve Now, Pay Later accounts for roughly 2.8pts of the decline (07_ops_initiatives.csv OPS-14).",
  "missed", "C023"),
 ("S036", "call:3Q22", "call-QA", "Dave Stephenson",
  "What will continue to have greater expansion in free cash flow margin would be some of the things that Brian talked about a little bit ago. It would be kinda incremental services or activities that we add for guests or hosts over time.",
  "take_rate", "take_rate", "multi-year", "no",
  "future margin expansion sourced from new monetised services", "+",
  "Repeated in 2Q23, 3Q23, 4Q23. Services/Experiences launched May 2025 and are still a net cost in 2026 (higher customer incentives depress the FY26 take rate, 2Q26 letter). The claim is open and so far cost-negative.",
  "open", ""),
 ("S037", "call:3Q22", "call-QA", "Brian Chesky",
  "We have not had to change anything about our hiring plans. We don't intend to change anything about our hiring plans in the next 12-18 months, regardless of the economy",
  "headcount", "product_dev", "multi-year", "yes",
  "hiring plan unchanged for 12-18 months (7-8% growth)", "0",
  "Actual 2023 headcount growth ~1% (Stephenson, 4Q23 call), i.e. materially below the plan he refused to change. Cost-favourable miss.",
  "missed", ""),
 ("S038", "call:3Q22", "call-QA", "Dave Stephenson",
  "if you look at our actual advertising strategy and the amount of money we're spending on it's gonna be relatively flat from 2022 over 2021, and you should anticipate similar marketing as a percentage of revenue in 2023.",
  "marketing", "brand_marketing", "full-year", "yes",
  "FY23 S&M % of revenue ~= FY22 18.0%", "0",
  "FY2023 17.78%, 27bp better than FY2022. Kept. Known 13 Feb 2024.",
  "kept","C024"),
 ("S039", "call:3Q22", "call-QA", "Brian Chesky",
  "this allows for a very efficient, very dynamic, approach to marketing that should get more efficient every single year",
  "marketing", "brand_marketing", "structural", "no",
  "S&M % of revenue falls every year", "+",
  "False from 2024 onward: 17.78 (23) -> 19.35 (24) -> 21.14 (25) -> 25.87 (1H26). Three consecutive years of marketing deleverage; brand+performance cash marketing alone rose 32% y/y in 1H26 against 17% revenue growth (07_ops_initiatives.csv OPS-19).",
  "missed", ""),
 ("S040", "call:3Q22", "call-QA", "Brian Chesky",
  "We're gonna continue to make improvements every single year, and I want AirCover to be the gold standard for customer service for our category.",
  "insurance", "ops_support", "structural", "no",
  "AirCover / host protection cost grows with the promise", "-",
  "AirCover cost is never disclosed separately; it sits inside operations & support and cost of revenue. Not testable.",
  "unverifiable", ""),

 # ============================== 4Q22 print, 14 Feb 2023 =====================================
 ("S041", "letter:4Q22", "letter", "shareholder letter",
  "For the full year 2023, we expect to maintain the strong Adjusted EBITDA margin we delivered in 2022, as we offset the headwinds from lower ADR with incremental variable cost efficiencies and fixed cost discipline.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY23 adj. EBITDA margin ~= FY22 34.6%", "0",
  "FY2023 36.84%: +228bp on FY2022's 34.56%, against a guide of 'maintain'. Raised twice during the year (2Q23 'modestly higher', 3Q23 '~150bp higher'). Known 13 Feb 2024.",
  "kept","C029"),
 ("S042", "letter:4Q22", "letter", "shareholder letter",
  "Compared to Q1 2022, we expect sales and marketing in Q1 2023 will be approximately 150 basis points higher as a percent of revenue, but flat as a percent of revenue for the full year.",
  "marketing", "brand_marketing", "full-year", "yes",
  "FY23 S&M % of revenue flat vs FY22 18.0%; 1Q23 +150bp y/y", "0",
  "FY2023 17.78% vs 18.05%: -27bp, essentially flat. Kept. Known 13 Feb 2024.",
  "kept", ""),
 ("S043", "letter:4Q22", "letter", "shareholder letter",
  "We expect our implied take rate (defined as revenue divided by GBV) in Q1 2023 to be similar to Q1 2022.",
  "take_rate", "take_rate", "next-quarter", "yes",
  "1Q23 implied take rate ~= 1Q22", "0",
  "Realised 1Q23 take rate close to 1Q22 (abnb_driver_history_quarterly.csv). Kept.",
  "kept","C030"),
 ("S044", "call:4Q22", "call-QA", "Dave Stephenson",
  "we anticipate our EBITDA margins for the full year to be roughly the same as 2022, in that the headwinds from lower ADR rates will be offset by our efficiencies that we kind of drive internally",
  "margin_algorithm", "total_margin", "full-year", "yes",
  "internally-driven efficiencies exactly offset ADR headwind", "0",
  "FY2023 came in 228bp above FY2022 - the efficiencies more than offset, and the feared ADR decline did not appear (FY2023 ADR roughly flat).",
  "kept", ""),
 ("S045", "call:4Q22", "call-QA", "Dave Stephenson",
  "I am not in profit maximization mode. I have a long list of things that we can invest in to drive further profitability, but I know that I can also afford with our headcount growth, profitability improvements that can offset the ADR declines",
  "margin_algorithm", "total_margin", "structural", "no",
  "the reinvestment rule: efficiency found first, then spent", "0",
  "This is the earliest full statement of the algorithm Mertz formalises in 3Q24 ('find incremental efficiencies every year ... and invest some of that').",
  "kept", ""),
 ("S046", "call:4Q22", "call-QA", "Dave Stephenson",
  "I feel confident we can deliver our EBITDA margin neutral in the face of whatever ADR headwinds that we see this year.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY23 margin >= FY22 regardless of ADR", "0",
  "FY2023 36.84% vs FY2022 34.56%. Kept with 228bp to spare. Known 13 Feb 2024.",
  "kept","C028"),

 # ============================== 1Q23 print, 9 May 2023 ======================================
 ("S047", "call:1Q23", "call-QA", "David E. Stephenson",
  "the improvements that we're going to continue to make in community support, infrastructure, cost of payments and our fixed cost leverage will be enough to offset any of the pressures that we're seeing in average daily rates",
  "margin_algorithm", "cost_of_revenue", "full-year", "no",
  "support + infrastructure + payments + fixed leverage >= ADR drag", "+",
  "FY2023 margin +228bp y/y. Offset achieved with room to spare. Known 13 Feb 2024.",
  "kept", ""),
 ("S048", "call:1Q23", "call-QA", "David E. Stephenson",
  "our marketing expenses as a percentage of revenue will remain largely the same in 2023 as it was in 2022. It's just that we're frontloading more of the marketing to get the message out earlier.",
  "marketing", "brand_marketing", "full-year", "yes",
  "FY23 S&M % of revenue ~= 18.0%, phased earlier", "0",
  "FY2023 17.78%. Kept. Known 13 Feb 2024.",
  "kept", ""),
 ("S049", "call:1Q23", "call-QA", "Brian Chesky",
  "I think our employees could easily be, especially our developers, 30% more productive in the short to medium term and this will allow significantly greater throughput through tools like GitHub's Copilot.",
  "ai_productivity", "product_dev", "multi-year", "yes",
  "engineering output per head +30%", "+",
  "Never shown in a filed number. Product development % of revenue was 15.7% in FY2023, 16.5% in FY2024 and rose further in 2025 - i.e. the productivity claim has not converted into product-dev leverage. Restated in 4Q24 as still 'a few years' away.",
  "open", ""),
 ("S050", "letter:1Q23", "letter", "shareholder letter",
  "Compared to Q2 2022, we expect that Sales and Marketing expense in Q2 2023 will be approximately 400 basis points higher as a percent of revenue as we deploy marketing earlier in the year than last year.",
  "marketing", "brand_marketing", "next-quarter", "yes",
  "2Q23 S&M % of revenue +400bp y/y", "-",
  "02_guidance_ledger.csv scores it: guided +400bp, actual +160bp, a 240bp beat - management over-warned on its own marketing phasing. Known 3 Aug 2023.",
  "kept", ""),
 ("S051", "call:1Q23", "call-QA", "David E. Stephenson",
  "over time, we'll continue to have opportunities to expand margins but that's not my primary focus right now. My primary focus is in investing for growth",
  "margin_algorithm", "total_margin", "multi-year", "no",
  "margin expansion deprioritised versus growth", "0",
  "Consistent with what followed: FY2023 was the margin peak (36.84%) and every subsequent FY guide has been a floor at or below it.",
  "kept", ""),
 ("S052", "call:1Q23", "call-QA", "Brian Chesky",
  "we also announced a partnership with Stripe where you can pay by bank account for monthly stays. This is really important because it means you don't have to pay for credit card to pay basically what is essentially rent",
  "payments", "cost_of_revenue", "multi-year", "no",
  "ACH/bank rails cut payment processing cost on long stays", "+",
  "Payment processing cost is not disclosed separately. Merchant fees plus chargebacks fell from 2.51% of GBV in FY2020 to 1.80% in FY2021 and have sat in a 1.82-1.89% band ever since (07_ops_initiatives.csv OPS-04) - the Stripe deal is not visible in it.",
  "unverifiable", ""),

 # ============================== 2Q23 print, 3 Aug 2023 ======================================
 ("S053", "letter:2Q23", "letter", "shareholder letter",
  "For the full-year 2023, we expect an Adjusted EBITDA margin that is modestly higher than the full-year 2022.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY23 margin modestly > 34.6%", "+",
  "FY2023 36.84%, +228bp on FY2022. First upward revision of the FY2023 guide. Known 13 Feb 2024.",
  "kept", ""),
 ("S054", "call:2Q23", "call-QA", "Brian Chesky",
  "I do not expect our take rate to change materially. There may be some segments or trip types or geographies where we would want to the take it down, but that could be offset by other areas that could come up.",
  "take_rate", "take_rate", "multi-year", "yes",
  "implied take rate broadly stable", "0",
  "Implied take rate has moved in a ~50bp band since. Kept in substance through 2026 (2Q26 guide: 'relatively flat').",
  "kept","C035"),
 ("S055", "call:2Q23", "call-QA", "Brian Chesky",
  "the way that we're going to see margin expansion is by launching incremental services for guests and hosts over the coming years",
  "margin_algorithm", "take_rate", "multi-year", "yes",
  "future margin expansion is a revenue-mix story, not a cost story", "+",
  "Services and Experiences launched 13 May 2025. Through 2Q26 they are still net dilutive to take rate (customer incentives) and to margin ($200m+ investment). Open.",
  "open","C036"),
 ("S056", "call:2Q23", "call-QA", "David E. Stephenson",
  "our marketing expense as a percentage of revenue we expect to remain relatively flat year-over-year on a total-year basis from 2023 over 2022",
  "marketing", "brand_marketing", "full-year", "yes",
  "FY23 S&M % of revenue ~= 18.0%", "0",
  "FY2023 17.78%. Kept. Known 13 Feb 2024.",
  "kept","C038"),
 ("S057", "call:2Q23", "call-QA", "Brian Chesky",
  "we'll have pretty consistent marketing spend as a percent of revenue over time because of the strength of the brand",
  "marketing", "brand_marketing", "structural", "yes",
  "S&M % of revenue is a structural constant", "0",
  "Broken: 17.78 (23) -> 19.35 (24) -> 21.14 (25) -> 25.87 (1H26), an 810bp drift in three years.",
  "missed", ""),
 ("S058", "call:2Q23", "call-QA", "David E. Stephenson",
  "we've moderated our head count growth overall. We're growing modestly, and we're investing behind the things that matter most for our guests and our Hosts.",
  "headcount", "product_dev", "full-year", "no",
  "headcount growth well below revenue growth", "+",
  "FY2023 headcount growth ~4% guided (3Q23) after ~1% in 2022, against 18% revenue growth. Kept; revenue per employee rose from $977k in 2021 to $1,521k in 2024 (07_ops_initiatives.csv OPS-03).",
  "kept", ""),
 ("S059", "call:2Q23", "call-QA", "David E. Stephenson",
  "I think we'll see more leverage in our fixed cost base, so needing fewer people to do more work overall.",
  "ai_cost", "ops_support", "multi-year", "no",
  "AI shows up first as fewer heads and automated support contacts", "+",
  "Support automation delivered from 2025 (15% deflection 2Q25, ~40% resolution 1Q26, ~45% 2Q26, cost per booking -10%/-16%). Headcount leverage claimed only from 2Q26 ('we don't need to grow our head count at levels that we did in the past').",
  "kept", ""),
 ("S060", "call:2Q23", "call-QA", "David E. Stephenson",
  "I don't have a new long-term target.",
  "declined_to_quantify", "total_margin", "multi-year", "no",
  "no successor to the 30%+ long-term margin target", "0",
  "Still true as of 2Q26: Airbnb has given no long-term margin target since the 30%+ of 2020-21. Every subsequent commitment is a one-year floor.",
  "kept", ""),

 # ============================== 3Q23 print, 1 Nov 2023 ======================================
 ("S061", "letter:3Q23", "letter", "shareholder letter",
  "we expect an Adjusted EBITDA margin for full-year 2023 that is approximately 150 bps higher than full-year 2022.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY23 margin ~36.1% (34.6% + 150bp)", "+",
  "FY2023 36.84%: beat the raised guide by a further 78bp (02_fy_guide_revisions.csv). Known 13 Feb 2024.",
  "kept", ""),
 ("S062", "letter:3Q23", "letter", "shareholder letter",
  "For full-year 2023, we expect our stock-based compensation (\"SBC\") expense to be approximately 20% higher than in full-year 2022.",
  "sbc", "sbc", "full-year", "yes",
  "FY23 SBC +20% y/y", "-",
  "FY2023 SBC +20.4% on the shareholder-letter series ($1,120m vs $930m) and +18.3% on the XBRL series ($1,100m vs $930m). Kept on either. Known 13 Feb 2024.",
  "kept", ""),
 ("S063", "letter:3Q23", "letter", "shareholder letter",
  "Beyond 2024, after the last of the double-trigger RSUs (which we stopped issuing after our IPO in December 2020) have vested or expired, we anticipate that SBC expense will grow largely in-line with headcount growth.",
  "sbc", "sbc", "multi-year", "yes",
  "SBC growth converges on headcount growth from FY2025", "+",
  "Partly delivered. FY2025 SBC grew +9.9% (XBRL) / +13.1% (letters) against headcount growth of about +12% - close to convergence. But FY2024 (+30.8% XBRL / +25.6% letters) blew through two successive guides first, and the 4Q25 letter has since retreated to the weaker 'lower than 2025' rather than repeating the convergence rule.",
  "partly", ""),
 ("S064", "call:3Q23", "call-QA", "David E. Stephenson",
  "We have our fixed cost growth discipline has been excellent and probably grow our fixed head count this year approximately 4%. So we're growing our head count and fixed expenses less than revenue.",
  "headcount", "product_dev", "full-year", "yes",
  "FY23 headcount +4% vs revenue +18%", "+",
  "Confirmed: FY2023 product development 17.36% of revenue vs 23.78% in FY2021 and 17.88% in FY2022, against +18% revenue growth. Known 13 Feb 2024.",
  "kept", ""),
 ("S065", "call:3Q23", "call-QA", "David E. Stephenson",
  "we're continuing to make good strides in cost of payments, our infrastructure costs, et cetera. That's not our primary driver.",
  "payments", "cost_of_revenue", "full-year", "no",
  "cost of revenue % of revenue keeps falling", "+",
  "Cost of revenue 17.17% of revenue FY2023 -> 16.92% FY2024 -> 17.04% FY2025: a 25bp gain then a 12bp give-back. On like-for-like halves 20.16 (1H24) -> 19.56 (1H25) -> 19.31 (1H26). Slowing, not compounding.",
  "kept", ""),
 ("S066", "call:3Q23", "call-QA", "David E. Stephenson",
  "the way we think about our take rate is that it's been very stable. We've actually made no underlying kind of recent changes to our absolute take rate",
  "take_rate", "take_rate", "multi-year", "no",
  "take rate flat; monetisation via new services only", "0",
  "Held until the Apr 2024 cross-currency fee (+~20bp annualised) and the 2026 single-fee migration and insurance programmes, both of which are fee-structure changes rather than new services.",
  "partly", ""),
 ("S067", "letter:3Q23", "letter", "shareholder letter",
  "We anticipate that our implied take rate (defined as revenue divided by GBV) in Q4 2023 will be slightly higher than Q4 2022.",
  "take_rate", "take_rate", "next-quarter", "yes",
  "4Q23 take rate slightly > 4Q22", "+",
  "Delivered, helped by one-off gift-card breakage which management then flagged as a hard comp in 3Q24. Known 13 Feb 2024.",
  "kept","C043"),

 # ============================== 4Q23 print, 13 Feb 2024 =====================================
 ("S068", "letter:4Q23", "letter", "shareholder letter",
  "For the full-year 2024, we expect to maintain an Adjusted EBITDA Margin of at least 35%, providing us flexibility to invest in incremental growth opportunities over the course of the year.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY24 adj. EBITDA margin >= 35%", "0",
  "FY2024 36.40%: cleared the floor by 140bp (02_guidance_ledger.csv). This is the first 'floor' guide; the floor construction is used at every FY guide since. Known 13 Feb 2025.",
  "kept","C044"),
 ("S069", "call:4Q23", "call-QA", "Ellie Mertz",
  "we are basically giving ourselves a floor in terms of the full-year EBITDA margin guidance. As we said, we will hold by a minimum of 35%, which is slightly down from what we delivered in 2023.",
  "margin_algorithm", "total_margin", "full-year", "yes",
  "the FY guide is deliberately a floor, not a point estimate", "0",
  "Explicit statement of the floor convention. Every FY floor since has been beaten: FY2024 35.0% -> 36.40% (+140bp), FY2025 34.5% -> 35.10% (+60bp), FY2026 raised twice from 'stable' to >=35.5%. Mean cushion across the seven floor rows in 02_guidance_accuracy.csv is 1.51pts.",
  "kept", ""),
 ("S070", "call:4Q23", "call-QA", "Ellie Mertz",
  "there's certainly opportunities at the margin to continue to invest in newer markets. Second, there's always opportunities in terms of looking at our high ROI marketing channels and adding marginally at the top.",
  "marketing", "brand_marketing", "full-year", "no",
  "the floor's flex is spent on expansion markets and performance marketing", "-",
  "Exactly what happened: FY2024 S&M rose to 19.35% of revenue from 17.78%, +157bp, against a guide of 'largely the same'.",
  "kept", ""),
 ("S071", "call:4Q23", "call-QA", "David E. Stephenson",
  "in terms of marketing, largely, we're going to keep marketing costs as a percentage of revenue largely the same as what it was in 2023. In some ways, we probably could see additional leverage on marketing",
  "marketing", "brand_marketing", "full-year", "yes",
  "FY24 S&M % of revenue ~= 17.8%", "0",
  "FY2024 S&M 19.35% of revenue vs 17.78%: MISSED by 157bp, in the deleveraging direction. The largest single-line cost guide miss in the record, and it is absent from 02_guidance_ledger.csv because that file is letter-sourced (it survives only as 03_forward_claims C042). Known 13 Feb 2025.",
  "missed","C042"),
 ("S072", "call:4Q23", "call-QA", "David E. Stephenson",
  "to the extent that there may be any incremental marketing, it's not going to be a materially larger percentage of revenue than it was last year.",
  "marketing", "brand_marketing", "full-year", "yes",
  "FY24 S&M % of revenue not materially above 17.8%", "0",
  "+157bp. Whether that is 'material' is the reader's call; on a 36% margin it is ~4% of EBITDA.",
  "missed", ""),
 ("S073", "call:4Q23", "call-QA", "David E. Stephenson",
  "we grew head count last year about 1%. We're planning to grow at maybe slightly more than that. It could be kind of mid-single digits, low-to-mid single-digit percent.",
  "headcount", "product_dev", "full-year", "yes",
  "FY24 headcount +low-to-mid single digits", "0",
  "Headcount is disclosed only in the 10-K. Product development rose to 18.52% of revenue in FY2024 from 17.36%, consistent with headcount growth matching or exceeding revenue growth rather than trailing it.",
  "partly", ""),
 ("S074", "call:4Q23", "call-QA", "Brian Chesky",
  "Airbnb is not an infrastructure company. Infrastructure would be a large language model or, obviously, GPU. So, we're not going to be investing in infrastructure, so we're not going to be building a large language model.",
  "ai_cost", "cost_of_revenue", "structural", "no",
  "no model training capex; AI cost is inference bought from vendors", "+",
  "Held through 2Q26: Airbnb still buys models. But by 2Q26 Mertz conceded 'a material increase in terms of the AI spend over the course of the year' - i.e. no capex, but a rising opex line.",
  "kept", ""),
 ("S075", "call:4Q23", "call-QA", "David E. Stephenson",
  "in terms of take rates, no, they should be consistent. There's no real reason why they should be going up on kind of a time-adjusted basis.",
  "take_rate", "take_rate", "full-year", "yes",
  "FY24 implied take rate flat on a time-adjusted basis", "0",
  "FY2024 implied take rate rose modestly, helped by the Apr 2024 cross-currency fee. Directionally slightly wrong, magnitude small.",
  "partly", ""),
 ("S076", "call:4Q23", "call-QA", "David E. Stephenson",
  "over a longer period of time, I think our margin expansion will absolutely come from hosting guest services and experiences, but during the short term, there's no real change on a time-adjusted basis towards fees.",
  "margin_algorithm", "take_rate", "multi-year", "yes",
  "long-run margin expansion sourced from services and experiences", "+",
  "Still open. Through 2Q26 services and experiences are a cost, not a margin source; management now attributes the FY26 margin raise to 'operating leverage in our core business'.",
  "open", ""),
 ("S077", "letter:4Q23", "letter", "shareholder letter",
  "With the release of our valuation allowance in 2023, we expect our effective tax rate to approximate the mid-to-high teens in the near-term and approximate the low 20% range in the long term.",
  "tax", "g_and_a", "multi-year", "yes",
  "ETR mid-to-high teens near term, low 20s long term", "0",
  "FY2024 ETR 20.5% and FY2025 19.95% (02_guidance_ledger.csv). The 'near-term mid-to-high teens' did not happen - the 4Q23 letter's own 15-19% FY2024 range printed above its top end - while the 'long-term low 20s' arrived immediately. OBBBA then reset the long-term guide back to mid-to-high teens in 3Q25.",
  "partly", ""),
 ("S078", "letter:4Q23", "letter", "shareholder letter",
  "In 2024, marketing spend will continue to be weighted more towards the first half of the year than the second half of the year.",
  "seasonality", "brand_marketing", "full-year", "no",
  "1H24 marketing % of revenue > 2H24", "0",
  "Wrong in the event: 2Q24 letter said H1 marketing % was flat y/y and the lean-in came in 3Q24-4Q24. Management reversed the phasing mid-year.",
  "missed", ""),

 # ============================== 1Q24 print, 8 May 2024 ======================================
 ("S079", "letter:1Q24", "letter", "shareholder letter",
  "For the full-year 2024, consistent with our prior guidance, we expect to grow Adjusted EBITDA on a nominal basis and to deliver an Adjusted EBITDA Margin of at least 35%, providing us flexibility to invest in incremental growth opportunities over the course of the year.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY24 margin >= 35%", "0",
  "FY2024 36.40%. Kept with 140bp to spare. Known 13 Feb 2025.",
  "kept", ""),
 ("S080", "letter:1Q24", "letter", "shareholder letter",
  "For full-year 2024, we expect our stock-based compensation (\"SBC\") expense to be approximately 20% higher than in full-year 2023.",
  "sbc", "sbc", "full-year", "yes",
  "FY24 SBC +20% y/y", "-",
  "Revised UP to ~25% in the 3Q24 letter within six months, and even that was low: FY2024 SBC grew +25.6% on the letter series ($1,407m) and +30.8% on the XBRL series ($1,439m). The initial +20% guide missed by 5.6pts (letters) or 10.8pts (XBRL).",
  "missed", ""),
 ("S081", "call:1Q24", "call-QA", "Ellie Mertz",
  "One is just some one-time credits that we had in payment processing a year ago that will not recur this year.",
  "payments", "cost_of_revenue", "next-quarter", "no",
  "2Q24 cost of revenue faces a payment-processing comp headwind", "-",
  "2Q24 adj. EBITDA margin 33%, stable with 2Q23 despite the flagged headwind. Absorbed.",
  "kept", ""),
 ("S082", "call:1Q24", "call-QA", "Ellie Mertz",
  "So marketing is one line item you will potentially see some margin compression in order to drive growth.",
  "marketing", "brand_marketing", "full-year", "yes",
  "S&M % of revenue rises in FY24", "-",
  "FY2024 S&M 19.35% of revenue vs 17.78%: +157bp. Kept - and it contradicts Stephenson's 'largely the same' from the same print cycle three months earlier. The two statements cannot both have been the plan.",
  "kept", ""),
 ("S083", "call:1Q24", "call-QA", "Ellie Mertz",
  "The second area, Brian talked about prioritizing our resources and identified that in many cases, our product development team is our kind of scarcest resource.",
  "headcount", "product_dev", "full-year", "yes",
  "product development % of revenue rises in FY24", "-",
  "FY2024 product development 18.52% of revenue vs 17.36% in FY2023: +116bp. Kept.",
  "kept", ""),
 ("S084", "call:1Q24", "call-QA", "Ellie Mertz",
  "there's virtually no change in terms of our underlying take rates by market",
  "take_rate", "take_rate", "structural", "yes",
  "take rate is not a geographic-mix variable", "0",
  "Repeated by Mertz in 1Q25. Never contradicted. But it means international mix cannot be used to explain take-rate drift, which narrows the explanations for any future move.",
  "kept", ""),
 ("S085", "call:1Q24", "call-QA", "Brian Chesky",
  "I think we're going to see the biggest impact is going to be on customer service in the near term. I think more than hotels, probably even more than OTA, Airbnb will benefit from generative AI.",
  "ai_cost", "ops_support", "multi-year", "yes",
  "support is the first and largest AI cost win", "+",
  "Confirmed by 1Q26 (-10% cost per booking) and 2Q26 (-16%). The single AI claim that has shown up in a disclosed number.",
  "kept","C047"),
 ("S086", "call:1Q24", "call-QA", "Brian Chesky",
  "Guest Favorites have between a fifth and a tenth the contact rate as our bottom quartile listing",
  "support_cost", "ops_support", "structural", "yes",
  "quality curation cuts contact rate 5-10x on the affected listings", "+",
  "Corroborated by 3Q24 ('customer service contact rates have decreased') and by the removal of 550,000 listings through 2025 with lower issue and chargeback rates (4Q25 letter).",
  "kept", ""),

 # ============================== 2Q24 print, 6 Aug 2024 ======================================
 ("S087", "letter:2Q24", "letter", "shareholder letter",
  "For the full-year 2024, consistent with our prior guidance, we expect to grow Adjusted EBITDA on a nominal basis and to deliver an Adjusted EBITDA Margin of at least 35%",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY24 margin >= 35%", "0",
  "FY2024 36.40%. Kept with 140bp to spare. Known 13 Feb 2025.",
  "kept", ""),
 ("S088", "call:2Q24", "call-QA", "Ellie Mertz",
  "for H1, marketing as a percent of revenue was effectively flat with where it was in 2023, but we do intend to lean into those growth investments in the back half of the year starting in Q3",
  "marketing", "brand_marketing", "full-year", "yes",
  "2H24 S&M % of revenue rises y/y", "-",
  "4Q24 letter: 'Adjusted EBITDA Margin during Q4 2024 was 31%, down compared to 33% in Q4 2023, due to investments in sales and marketing and product development'. Kept.",
  "kept", ""),
 ("S089", "call:2Q24", "call-QA", "Ellie Mertz",
  "all of our expansions to date have not been very capital-intensive. So, we will use some of the profitability to invest, but we don't anticipate any kind of sea change in the foreseeable future around overall profitability levels.",
  "margin_algorithm", "total_margin", "multi-year", "yes",
  "margin stays in a narrow band; expansions are opex not capex", "0",
  "Held: FY margins 35.8% (24), 35.1% (25), guided >=35.5% (26). A 70bp band over three years.",
  "kept","C049"),
 ("S090", "call:2Q24", "call-QA", "Ellie Mertz",
  "that will be in a gradual investment modestly above the head count growth that we've been targeting over the last couple of years",
  "headcount", "product_dev", "full-year", "yes",
  "FY24-25 headcount growth above the ~1-4% run rate", "-",
  "Confirmed by the 4Q24 call ('slightly increasing our pace of head count growth across our product development organization') and by the FY25 $200-250m programme.",
  "kept", ""),
 ("S091", "call:2Q24", "call-QA", "Brian Chesky",
  "we can do this without a lot of incremental investment, because we can market homes and experiences in the same ad",
  "marketing", "brand_marketing", "multi-year", "yes",
  "experiences relaunch needs no separate marketing budget", "+",
  "Partly kept: Mertz confirmed in 2Q25 that the $200m is 'not an increase in programmatic marketing'. But it did land in S&M, as field operations, go-to-market and supply acquisition.",
  "partly", ""),
 ("S092", "call:2Q24", "call-QA", "Brian Chesky",
  "Most of these new services and offerings, though, are going to not cost very much.",
  "new_business", "field_ops", "multi-year", "yes",
  "new-business cost is de minimis", "0",
  "Contradicted six months later: the 4Q24 letter put the 2025 figure at $200-250m, ~1.8-2.2% of FY2025 revenue and ~2 points of margin. The clearest cost mis-statement in the record.",
  "missed", ""),
 ("S093", "letter:2Q24", "letter", "shareholder letter",
  "partially offset by investments in customer service aimed to enhance the guest and host experience, which impact contra-revenue.",
  "take_rate", "take_rate", "next-quarter", "yes",
  "3Q24 take rate up y/y; support investment is contra-revenue", "+",
  "Delivered. Note the disclosure: some customer-service investment is booked as contra-revenue, not in operations and support - so the ops&support line understates true support cost.",
  "kept", ""),
 ("S094", "call:2Q24", "call-QA", "Ellie Mertz",
  "From a performance marketing standpoint, obviously, the ROI is very specific and relatively short-term. We think about that in terms of weeks and months, not quarters. In terms of brands, we think about that over a longer time horizon.",
  "marketing", "brand_marketing", "structural", "yes",
  "brand payback 6-12 months; performance payback immediate", "0",
  "Never falsifiable from filed data. It is the stated reason marketing cannot be flexed down quickly in a downturn.",
  "unverifiable", ""),

 # ============================== 3Q24 print, 7 Nov 2024 ======================================
 ("S095", "letter:3Q24", "letter", "shareholder letter",
  "For the full-year 2024, we now expect to deliver an Adjusted EBITDA Margin of approximately 35.5%.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY24 margin ~35.5%", "+",
  "FY2024 36.40%: beat even the raised point guide by 90bp (02_guidance_ledger.csv). Known 13 Feb 2025.",
  "kept", ""),
 ("S096", "letter:3Q24", "letter", "shareholder letter",
  "For full-year 2024, we expect our stock-based compensation (\"SBC\") expense to be approximately 25% higher than in full-year 2023.",
  "sbc", "sbc", "full-year", "yes",
  "FY24 SBC +25% y/y (revised up from +20%)", "-",
  "A 5-point upward revision inside six months on a line management had said would converge on headcount growth - and the year still printed above the raised guide (+25.6% letters / +30.8% XBRL). Known 13 Feb 2025.",
  "missed", ""),
 ("S097", "call:3Q24", "call-QA", "Ellie Mertz",
  "the way we do that is to find incremental efficiencies every year across, in particular, variable costs and invest some of that into greater service levels on both sides of the marketplace.",
  "margin_algorithm", "total_margin", "structural", "no",
  "THE ALGORITHM: find variable-cost efficiency every year, spend part of it", "0",
  "The canonical statement of the reinvestment rule. Restated in 4Q24, 1Q25, 4Q25 and 2Q26. It is why FY margin has sat in a 35-37% band for four years (36.84 / 36.40 / 35.10, guided >=35.5) rather than compounding.",
  "kept", ""),
 ("S098", "call:3Q24", "call-QA", "Ellie Mertz",
  "We've been extremely disciplined in terms of delivering over 400 basis points of EBITDA margin expansion since 2020.",
  "margin_algorithm", "total_margin", "structural", "yes",
  "4,000bp of margin expansion 2020-2024 (mis-spoken as 400bp)", "+",
  "The 4Q24 letter and the 4Q23 letter both say 'over 4,000 basis points'. This is a transcript mis-statement of the same fact, not a different claim.",
  "kept", ""),
 ("S099", "call:3Q24", "call-QA", "Ellie Mertz",
  "we will be launching new products with our upcoming 2025 spring release. The good news about these investments is that we intend for them to be relatively capital light",
  "new_business", "field_ops", "full-year", "no",
  "FY25 new-business investment is opex, capital light", "-",
  "Quantified three months later at $200-250m (4Q24 letter). Capital-light held; cost-light did not.",
  "kept", ""),
 ("S100", "call:3Q24", "call-QA", "Ellie Mertz",
  "some of the investment behind those new services will front run the revenue. So you'll begin to see those expenses or those investments, I should say, at the beginning of the year, whereas the revenue will start to scale once we've released a new offering.",
  "new_business", "field_ops", "full-year", "yes",
  "FY25 cost precedes revenue; margin dips before it recovers", "-",
  "Kept: 1Q25 margin 18% vs 20% in 1Q24; FY2025 margin 35.10% vs 36.40%. Revenue and contribution margin from services/experiences are still not disclosed as of 2Q26 - abnb_declined_to_quantify.csv logs six refusals on new-business contribution margin (3Q24, 2Q25 x2, 3Q25, 2Q26 x2).",
  "kept", ""),
 ("S101", "call:3Q24", "call-QA", "Brian Chesky",
  "I do not anticipate very many businesses in the next five years are going to need significant investments. We are certainly nothing like, many other companies where they have a lot of either capital allocation or major technical investments or even major marketing investments.",
  "new_business", "field_ops", "multi-year", "no",
  "no material step-up in investment through 2029", "0",
  "Contradicted within one quarter by the $200-250m FY25 programme, and again in 2Q26 by 'a material increase in terms of the AI spend'.",
  "missed", ""),
 ("S102", "letter:3Q24", "letter", "shareholder letter",
  "Q4 2024 Adjusted EBITDA Margin is expected to decline relative to the same time period last year due to higher marketing and product development expenses.",
  "marketing", "brand_marketing", "next-quarter", "yes",
  "4Q24 margin down y/y on S&M and product dev", "-",
  "4Q24 margin 31% vs 33% in 4Q23: -200bp, exactly as guided and for the stated reason. Known 13 Feb 2025.",
  "kept", ""),
 ("S103", "letter:3Q24", "letter", "shareholder letter",
  "For the full-year 2024, we anticipate our effective tax rate to be approximately 20%, subject to variables including profitability, stock-based compensation deductions, and changes in tax laws.",
  "tax", "g_and_a", "full-year", "yes",
  "FY24 ETR ~20%", "0",
  "FY2024 ETR printed 20.5% - a 50bp miss on the point guide, and 150-550bp above the 'mid-to-high teens near-term' of the 4Q23 letter.",
  "kept", ""),

 # ============================== 4Q24 print, 13 Feb 2025 =====================================
 ("S104", "letter:4Q24", "letter", "shareholder letter",
  "Specifically, we plan to invest $200 million to $250 million towards launching and scaling new businesses to be introduced later this year.",
  "new_business", "field_ops", "full-year", "yes",
  "FY25 incremental new-business spend $200-250m (~1.8-2.2% of revenue)", "-",
  "Re-guided DOWN to 'approximately $200 million' in the 2Q25 letter and held there in 3Q25. Came in at the low end. Known 12 Feb 2026.",
  "kept", ""),
 ("S105", "letter:4Q24", "letter", "shareholder letter",
  "Inclusive of these investments, we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%-maintaining our strong track record of profitability without compromising our growth initiatives.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY25 margin >= 34.5%", "0",
  "FY2025 35.10%: cleared the floor by 60bp, after being raised to 'approximately 35%' in 3Q25 (beaten by a further 10bp). Known 12 Feb 2026.",
  "kept","C056"),
 ("S106", "letter:4Q24", "letter", "shareholder letter",
  "In 2025, we anticipate that the growth rate of SBC will approximate headcount growth.",
  "sbc", "sbc", "full-year", "yes",
  "FY25 SBC growth ~= headcount growth (low single digits)", "+",
  "Broadly delivered on the arithmetic: FY2025 SBC +9.9% (XBRL) / +13.1% (letters) against headcount growth of about +12% (07_ops_initiatives.csv OPS-03). But the 4Q25 letter still retreated to the weaker 'lower than 2025' rather than repeating the convergence rule, which suggests management does not regard it as safe.",
  "kept", ""),
 ("S107", "call:4Q24", "call-QA", "Ellie Mertz",
  "you should see the bulk of that investment hit both our marketing line and our product development line items",
  "new_business", "brand_marketing", "full-year", "yes",
  "the $200-250m lands in S&M and product development, not ops&support", "-",
  "Confirmed. FY2025 S&M 21.14% of revenue (+179bp y/y) and product development 19.23% (+71bp). Ops & support fell to 10.84%, so it was not the vehicle.",
  "kept", ""),
 ("S108", "call:4Q24", "call-QA", "Ellie Mertz",
  "the way to think about brand marketing is that, it is effectively a fixed amount of spend for each market in terms of the minimum amount that you need to spend for that market to be efficient.",
  "marketing", "brand_marketing", "structural", "yes",
  "brand marketing is fixed per market: leverage comes from revenue per market, not from spending less", "+",
  "This is the model-critical claim. It implies S&M % of revenue falls in mature markets and rises while new markets are being seeded - which is exactly the 2024-2026 pattern.",
  "kept", ""),
 ("S109", "call:4Q24", "call-QA", "Ellie Mertz",
  "in particular, in our core markets because they are so heavily reliant on brand, we are not adding dollar for dollar as revenue increases, and therefore, the marketing budget is allowed to expand and be more heavily dedicated to expansion markets.",
  "marketing", "brand_marketing", "multi-year", "yes",
  "core-market marketing grows slower than core revenue; the difference funds expansion markets", "0",
  "Total S&M nonetheless rose from 19.35% to 21.14% of revenue in FY2025 and to 25.87% in 1H26 - the expansion-market and field-ops load outran the core-market leverage.",
  "partly", ""),
 ("S110", "call:4Q24", "call-QA", "Ellie Mertz",
  "for full year 2025, you should assume that the implied take rate gets the full benefit of 20 basis points increase on a year- over-year basis as compared to 2024.",
  "take_rate", "take_rate", "full-year", "yes",
  "FY25 implied take rate +20bp y/y from the cross-currency fee", "+",
  "Did not happen. FY2025 implied take rate 13.41% vs FY2024 13.57% (07_cost_lines_per_night.csv): -16bp y/y against a guide of +20bp, a 36bp miss. The single most specific take-rate guide in the record (03_forward_claims C057, verdict missed).",
  "missed","C057"),
 ("S111", "call:4Q24", "call-QA", "Ellie Mertz",
  "there's incremental opportunities across our variable costs, so areas like payment processing and customer service opportunities to just be, frankly, a little bit more efficient and to deliver some margin expansion there.",
  "margin_algorithm", "cost_of_revenue", "full-year", "yes",
  "FY25 margin expansion from payments, support and G&A - offset by S&M and product dev", "+",
  "Ops & support improved 71bp in FY2025 (11.55 -> 10.84), but cost of revenue gave back 12bp (16.92 -> 17.04) and G&A 29bp; the S&M offset (+179bp) outweighed all of it, so total margin fell 130bp.",
  "kept", ""),
 ("S112", "call:4Q24", "call-QA", "Ellie Mertz",
  "we will be slightly increasing our pace of head count growth across our product development organization, such that we can move more quickly across our road map and support these new businesses.",
  "headcount", "product_dev", "full-year", "yes",
  "FY25 product-dev headcount growth above trend", "-",
  "Kept. Product development rose to 19.23% of revenue in FY2025 from 18.52%.",
  "kept", ""),
 ("S113", "call:4Q24", "call-QA", "Brian Chesky",
  "I don't think it's flowing to like a fundamental step-change in productivity yet. I think a lot of us believe in some kind of medium term of a few years, you could easily see like a 30% increase in technology and engineering productivity.",
  "ai_productivity", "product_dev", "multi-year", "yes",
  "engineering productivity +30% within a few years", "+",
  "Same number Chesky gave in 1Q23 for 'the short to medium term'. Two years on it is still framed as a few years out. Product development has deleveraged every year since: 17.36 (23) -> 18.52 (24) -> 19.23 (25) -> 20.84 (1H26) as a share of revenue.",
  "open", ""),
 ("S114", "call:4Q24", "call-QA", "Brian Chesky",
  "what it's going to lead to is, fewer engineers being able to basically ship features faster.",
  "ai_productivity", "product_dev", "multi-year", "yes",
  "engineer headcount per unit of output falls", "+",
  "Not yet visible in the P&L. Product development cash spend rose from $669m to $749m (+12%) in the most recent comparable period, all of it payroll, while Airbnb reports 60% of code AI-authored and concept-to-launch time down 60% (07_ops_initiatives.csv OPS-08). Output claims, zero cost saving. The first management claim of actual headcount restraint from AI is 2Q26.",
  "open", ""),
 ("S115", "letter:4Q24", "letter", "shareholder letter",
  "For the full-year 2025, we anticipate our effective tax rate to slightly below our long-term effective tax rate of approximately 20%",
  "tax", "g_and_a", "full-year", "yes",
  "FY25 ETR slightly below 20%", "0",
  "FY2025 ETR 19.95% (02_guidance_ledger.csv) - inside the <=20% ceiling by 5bp rather than 'slightly below' it. A $213m CAMT valuation allowance in 3Q25 was the swing item.",
  "partly", ""),
 ("S116", "letter:4Q24", "letter", "shareholder letter",
  "The impact of these investments on our quarterly Adjusted EBITDA Margin will be the most pronounced during the first nine months of 2025 due to the timing of when we introduce these new offerings.",
  "new_business", "field_ops", "full-year", "yes",
  "margin drag concentrated 1Q25-3Q25", "-",
  "Reversed by management within three months: the 1Q25 letter said the drag would be 'most pronounced during the second half of the year'. A phasing guide that flipped 180 degrees in one quarter.",
  "missed", ""),

 # ============================== 1Q25 print, 1 May 2025 ======================================
 ("S117", "letter:1Q25", "letter", "shareholder letter",
  "For full-year 2025, consistent with our prior guidance, we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%, maintaining our strong track record of profitability while making meaningful investments behind future growth levers.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY25 margin >= 34.5%", "0",
  "FY2025 35.10%. Kept with 60bp to spare. Known 12 Feb 2026.",
  "kept","C060"),
 ("S118", "letter:1Q25", "letter", "shareholder letter",
  "We believe that the impact of these investments on our quarterly Adjusted EBITDA Margin will be the most pronounced during the second half of the year due to the timing of when we introduce these new offerings.",
  "new_business", "field_ops", "full-year", "yes",
  "margin drag concentrated 2H25", "-",
  "Kept in the event (3Q25 margin 50% vs 52% in 3Q24; 4Q25 28% vs 31%), but it is the exact opposite of what the 4Q24 letter said one quarter earlier.",
  "kept", ""),
 ("S119", "call:1Q25", "call-QA", "Ellie Mertz",
  "every year what we're seeking to do is strengthen and make more efficient that core business, so that we have incremental room to invest in growth. From year to year, we may choose to invest more in growth relative to the efficiencies that we generate.",
  "margin_algorithm", "total_margin", "structural", "no",
  "the algorithm again, with the explicit admission that spend can exceed efficiency in a given year", "0",
  "This sentence is the licence for FY2025's 130bp margin decline (36.40 -> 35.10). It is also the reason a reader should treat any FY margin guide as a policy choice, not a forecast.",
  "kept", ""),
 ("S120", "call:1Q25", "call-QA", "Ellie Mertz",
  "when we think about investing in a new market, there is some fixed cost upfront in terms of, say, launching brand campaigns, and that does drive margins down. But over time, we are able to scale into the marketing load",
  "marketing", "brand_marketing", "multi-year", "yes",
  "expansion-market marketing is J-curved: margin down first, leverage later", "0",
  "Untested at the market level - Airbnb has never disclosed margin by market or the cohort economics of an expansion market.",
  "unverifiable", ""),
 ("S121", "call:1Q25", "call-QA", "Ellie Mertz",
  "independent of a pretty wide range of ADRs, we're able to deliver very attractive unit economics across the globe",
  "adr", "other", "structural", "yes",
  "contribution margin is ADR-insensitive at the booking level", "0",
  "Directly contradicts the 2021-2023 framing in which ADR moderation was the main margin headwind (4Q21, 4Q22, 1Q23). Management has quietly dropped ADR as a margin driver since 2024.",
  "kept", ""),
 ("S122", "call:1Q25", "call-QA", "Ellie Mertz",
  "we do do some revenue hedging such that the tailwind that some are seeing does not entirely materialize in terms of our hedge portfolio for revenue",
  "fx", "fx", "full-year", "no",
  "hedging damps both FX tailwind and headwind on revenue and therefore margin", "0",
  "Quantified from 3Q25 onward: 'a small foreign exchange tailwind after factoring in our hedges' (3Q25), '~3 percentage point FX tailwind after factoring in our hedging program' (4Q25, 1Q26, 2Q26).",
  "kept", ""),

 # ============================== 2Q25 print, 6 Aug 2025 ======================================
 ("S123", "letter:2Q25", "letter", "shareholder letter",
  "For 2025, consistent with our prior guidance, we expect to deliver a full-year Adjusted EBITDA Margin of at least 34.5%, maintaining our strong track record of profitability while making meaningful investments behind future growth levers.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY25 margin >= 34.5%", "0",
  "FY2025 35.10%. Kept with 60bp to spare. Known 12 Feb 2026.",
  "kept", ""),
 ("S124", "letter:2Q25", "letter", "shareholder letter",
  "This includes investing approximately $200 million towards services and experiences in 2025.",
  "new_business", "field_ops", "full-year", "yes",
  "FY25 new-business spend ~$200m, the low end of the Feb range", "+",
  "Held at ~$200m in 3Q25 too. Management trimmed its own investment guide by up to $50m without changing the margin floor.",
  "kept", ""),
 ("S125", "call:2Q25", "call-QA", "Ellie Mertz",
  "the increase in sales and marketing that you see associated with services and experiences is focused in particular on our field operations, our go-to-market activities and supply acquisition.",
  "new_business", "field_ops", "full-year", "yes",
  "the S&M rise is field ops and supply acquisition, not advertising", "-",
  "The key disaggregation of the S&M line: from 2025 it carries a growing non-advertising component (field ops cash $693m -> $993m, +43%, 07_ops_initiatives.csv OPS-12), so the historical 'marketing % of revenue' series is no longer comparable. Note the 1H26 twist: brand+performance cash itself grew 32% y/y against 17% revenue growth, so 2026 is not only a field-ops story.",
  "kept", ""),
 ("S126", "call:2Q25", "call-QA", "Ellie Mertz",
  "we continue to use performance marketing as a, I would say, surgical topper to the majority of our spend being in brand.",
  "marketing", "brand_marketing", "structural", "yes",
  "performance marketing is a minority topper; brand is the base", "0",
  "Consistent since 4Q20 ('a laser'). 90% of traffic direct or unpaid has been repeated unchanged from 4Q20 through 2Q25.",
  "kept", ""),
 ("S127", "call:2Q25", "call-QA", "Ellie Mertz",
  "some of the investments this year will carry into next year as fixed head count that we've brought on to support these businesses.",
  "new_business", "field_ops", "multi-year", "yes",
  "part of the $200m is permanent fixed cost, not a one-year investment", "-",
  "Confirmed by the 4Q25 guide, which planned for stable rather than recovering FY26 margin. The $200m did not roll off.",
  "kept", ""),
 ("S128", "call:2Q25", "call-QA", "Ellie Mertz",
  "On margins, I'm not going to guide right now to 2026. What you can assume is that we are: one, continuing to invest in our new businesses; and two, continuing to drive efficiencies across the core business.",
  "declined_to_quantify", "total_margin", "full-year", "no",
  "no FY26 margin number six months out", "0",
  "The FY26 guide arrived at 4Q25 as 'stable year-over-year', then was raised to >=35% (1Q26) and >=35.5% (2Q26).",
  "kept", ""),
 ("S129", "call:2Q25", "call-QA", "Brian Chesky",
  "this has reduced, as I mentioned in the opening remarks, 15% of people needing to contact a human agent when they interact instead with this AI agent.",
  "ai_cost", "ops_support", "full-year", "yes",
  "AI deflects 15% of would-be human contacts (US English, mid-2025)", "+",
  "Superseded within two quarters: ~33% at 4Q25, over 40% at 1Q26, nearly 45% at 2Q26. The deflection curve has run ahead of every disclosure.",
  "kept", ""),
 ("S130", "call:2Q25", "call-QA", "Ellie Mertz",
  "the investments we've made across our infrastructure over the last couple of years has really improved the development environment for our team, allowing them to do more and to do more quickly. Obviously, that is increasingly aided by AI as well.",
  "ai_productivity", "product_dev", "structural", "no",
  "developer productivity rising - no number", "+",
  "No metric attached. Product development % of revenue has not fallen.",
  "unverifiable", ""),
 ("S131", "letter:2Q25", "letter", "shareholder letter",
  "We anticipate our implied take rate in Q3 2025 to be flat year-over year.",
  "take_rate", "take_rate", "next-quarter", "yes",
  "3Q25 implied take rate flat y/y", "0",
  "Delivered. Note the contrast with the FY25 +20bp promised at 4Q24 - by mid-2025 the quarterly guides had already given the +20bp up.",
  "kept", ""),

 # ============================== 3Q25 print, 6 Nov 2025 ======================================
 ("S132", "letter:3Q25", "letter", "shareholder letter",
  "For the full-year 2025, we now expect to deliver an Adjusted EBITDA Margin of approximately 35%.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY25 margin ~35% (raised from >=34.5%)", "+",
  "FY2025 35.10%. Beat even the raised point guide by 10bp. Known 12 Feb 2026.",
  "kept","C065"),
 ("S133", "call:3Q25", "call-prepared", "Ellie Mertz",
  "As we look forward to 2026, we're focused on maintaining strong margins while continuing to invest in growth initiatives. We will share more about our 2026 outlook on the next earnings call in February.",
  "declined_to_quantify", "total_margin", "full-year", "no",
  "FY26 margin 'maintained', no number", "0",
  "The February 2026 guide was 'stable year-over-year' (i.e. ~35%), consistent with this language. Then raised twice.",
  "kept", ""),
 ("S134", "call:3Q25", "call-prepared", "Ellie Mertz",
  "On a go forward basis starting in 2026, we anticipate that the One Big Beautiful Bill will materially reduce our effective tax rate due to the preferential changes to tax on foreign earnings.",
  "tax", "g_and_a", "multi-year", "yes",
  "ETR falls from 20% to mid-to-high teens from FY2026", "+",
  "Reaffirmed in 4Q25 and quantified in the 1Q26 letter as 'high teens' for FY2026. Below EBITDA, so it moves EPS and FCF, not adj. EBITDA margin.",
  "open","C066"),
 ("S135", "call:3Q25", "call-QA", "Brian Chesky",
  "our theory is that every incremental new business we launch is going to be more efficient to launch than the prior businesses, especially now that we're going with pilot city by city.",
  "new_business", "field_ops", "multi-year", "yes",
  "marginal launch cost per new business declines", "+",
  "Untested - Airbnb does not disclose per-business launch cost. Note it is a theory, in Chesky's own word.",
  "open", ""),
 ("S136", "call:3Q25", "call-QA", "Ellie Mertz",
  "you obviously noted in the shareholder letter, we said we're focused on maintaining strong margins while continuing to invest in growth initiatives next year. That is the case.",
  "fy_margin_guide", "total_margin", "full-year", "no",
  "FY26 margin roughly held at the FY25 level", "0",
  "FY26 guided stable (4Q25), then >=35% (1Q26), then >=35.5% (2Q26). Beaten in the raising direction twice.",
  "kept", ""),

 # ============================== 4Q25 print, 12 Feb 2026 =====================================
 ("S137", "letter:4Q25", "letter", "shareholder letter",
  "For 2026, we expect our Adjusted EBITDA Margin to be stable year-over-year as we reinvest top-line efficiencies to support growth across the business, primarily in marketing, product, and technology.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY26 margin ~= FY25 35.10%; efficiencies fully reinvested", "0",
  "Raised to >=35% (1Q26) and then >=35.5% (2Q26). Open until Feb 2027, but already tracking ~40bp above the original guide.",
  "open", ""),
 ("S138", "call:4Q25", "call-prepared", "Ellie Mertz",
  "across the full P&L, we're continuing to drive efficiencies in our platform. We plan to reinvest most of these efficiencies into marketing, product and technology to support our growth. As a result, we expect our 2026 adjusted EBITDA margin to be stable year-over-year.",
  "margin_algorithm", "total_margin", "full-year", "yes",
  "reinvestment ratio ~= 100% of efficiencies in FY26", "0",
  "Partly undone by the two 2026 raises: by 2Q26 the reinvestment ratio implied is below 100%, with ~40bp dropping through.",
  "partly", ""),
 ("S139", "call:4Q25", "call-prepared", "Brian Chesky",
  "We expect revenue growth to accelerate to at least low-double digits in 2026. We expect adjusted EBITDA margin to be stable year- over-year. And we'll do all of this without investing billions or tens of billions of dollars.",
  "ai_cost", "total_margin", "full-year", "yes",
  "no AI capex cycle; margin held", "+",
  "Revenue guide raised twice (to low-to-mid teens, then at least mid-teens); margin guide raised twice. Both tracking ahead as of 2Q26.",
  "open", ""),
 ("S140", "call:4Q25", "call-QA", "Brian Chesky",
  "we're not building models. We do not have a huge CapEx cost base. So our investment in AI will not affect the P&L. I don't think you'll see it in the P&L.",
  "ai_cost", "cost_of_revenue", "full-year", "yes",
  "AI spend invisible in the FY26 P&L", "0",
  "CONTRADICTED by his own CFO two quarters later: 'the updated guidance that we've provided obviously does assume a material increase in terms of the AI spend over the course of the year' (Mertz, 2Q26). The claim was already softened by Mertz in 1Q26 ('an expense that will ramp over the course of the year').",
  "missed", ""),
 ("S141", "call:4Q25", "call-QA", "Brian Chesky",
  "Right now, nearly 30% of tickets in North America that are English-based are handled by an AI agent. A year from now, if we're successful, significantly more than 30% of tickets will be handled by a customer service agent in many more languages",
  "ai_cost", "ops_support", "full-year", "yes",
  "AI ticket share >30% and multi-language by Feb 2027", "+",
  "Running ahead at the half-year: more than 50 languages and nearly 45% of issues resolved without a human agent (2Q26 prepared remarks). The stated horizon is a year, so it does not close until Feb 2027 (workstream 03 C071, too_early).",
  "open", "C071"),
 ("S142", "call:4Q25", "call-QA", "Brian Chesky",
  "not only does this reduce the cost base of Airbnb customer service, but the kind of quality of service is going to be a huge step change",
  "ai_cost", "ops_support", "multi-year", "yes",
  "support cost per unit falls structurally", "+",
  "Confirmed: -10% cost per booking in 1Q26, -16% in 2Q26.",
  "kept", ""),
 ("S143", "call:4Q25", "call-QA", "Brian Chesky",
  "More than 80% of engineers are now using AI tools. That soon will be 100%.",
  "ai_productivity", "product_dev", "full-year", "yes",
  "AI tool adoption ~100% of engineers", "+",
  "Adoption is an input, not an output. No corresponding disclosure of engineering output per head or of product-development leverage.",
  "open", ""),
 ("S144", "letter:4Q25", "letter", "shareholder letter",
  "In 2026, we anticipate that the year-over-year growth rate of SBC and headcount will be lower than 2025.",
  "sbc", "sbc", "full-year", "yes",
  "FY26 SBC growth < FY25 SBC growth; FY26 headcount growth < FY25", "+",
  "Open until Feb 2027. Note the retreat: 2023-24 letters promised SBC growth would converge on headcount growth; this only promises deceleration.",
  "open", ""),
 ("S145", "letter:4Q25", "letter", "shareholder letter",
  "We expect to roll out AI customer support globally later this year.",
  "ai_cost", "ops_support", "full-year", "yes",
  "AI support live in all major languages by end-2026", "+",
  "Ahead of plan: 'available in more than 50 languages' by 2Q26.",
  "kept", ""),
 ("S146", "call:4Q25", "call-QA", "Ellie Mertz",
  "the top of our P&L in terms of cost of revenue and ops and support will scale somewhat linearly. We'll have some efficiencies there, but they will scale somewhat linearly with, obviously, the growth in revenue.",
  "margin_algorithm", "cost_of_revenue", "full-year", "yes",
  "FY26 cost of revenue and ops&support roughly flat as % of revenue", "0",
  "This is the single most useful modelling sentence management has given: it says the top two cost lines are NOT the FY26 margin swing factor. Open; 1H26 consistent so far.",
  "open", ""),
 ("S147", "call:4Q25", "call-QA", "Ellie Mertz",
  "Where you will see some incremental investment to drive growth is, obviously, in sales and marketing. This is both in the form of programmatic marketing, but more so in terms of our go-to-market efforts.",
  "marketing", "field_ops", "full-year", "yes",
  "FY26 S&M % of revenue rises again, mostly on go-to-market/field ops", "-",
  "1H2026 S&M 25.87% of revenue against 21.14% for FY2025 and 23.36% in 1H25: +251bp y/y on a like-for-like half. Kept, and by a wide margin.",
  "kept", ""),
 ("S148", "letter:4Q25", "letter", "shareholder letter",
  "we expect our long-term effective tax rate to decline to the mid-to-high teens due to the enactment of the One Big Beautiful Bill Act (\"OBBBA\") on July 4",
  "tax", "g_and_a", "multi-year", "yes",
  "long-run ETR mid-to-high teens, down from ~20%", "+",
  "1Q26 letter: 'For the full-year 2026, we expect our effective tax rate to be in the high teens.' Consistent. Below the EBITDA line.",
  "open", ""),
 ("S149", "letter:4Q25", "letter", "shareholder letter",
  "We expect our implied take rate in Q1 2026 to be up slightly year-over-year.",
  "take_rate", "take_rate", "next-quarter", "yes",
  "1Q26 implied take rate up slightly y/y", "+",
  "Delivered - 1Q26 revenue grew 18% against low-double-digit GBV growth. Known 7 May 2026.",
  "kept", ""),

 # ============================== 1Q26 print, 7 May 2026 ======================================
 ("S150", "letter:1Q26", "letter", "shareholder letter",
  "For 2026, we now expect our Adjusted EBITDA Margin to be at least 35%.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY26 margin >= 35% (up from 'stable')", "+",
  "Raised again to >=35.5% three months later. Open until Feb 2027.",
  "open", ""),
 ("S151", "call:1Q26", "call-prepared", "Brian Chesky",
  "over 40% of issues are now resolved without a human agent, and this is up from about a third in Q4 with significantly faster resolution time. We've seen the cost per booking decrease about 10% year-over-year in Q1",
  "ai_cost", "ops_support", "full-year", "yes",
  "support cost per booking -10% y/y; AI resolution share 40%", "+",
  "First quantified AI cost benefit. Improved to -16% and ~45% by 2Q26. The only AI claim with a disclosed unit metric.",
  "kept", ""),
 ("S152", "letter:1Q26", "letter", "shareholder letter",
  "We saw our cost-per-booking decrease about 10% year-over-year in Q1-a meaningful trajectory we expect to continue as we further improve AI customer support this year.",
  "support_cost", "ops_support", "full-year", "yes",
  "support cost per booking continues to fall through FY26", "+",
  "Confirmed at 2Q26 (-16% y/y). Note this is customer-support cost per booking, not the whole operations & support line.",
  "kept", ""),
 ("S153", "call:1Q26", "call-prepared", "Ellie Mertz",
  "We'll continue to prioritize reinvestment to support further growth across the business, specifically on efficient marketing spend, international expansion, and AI initiatives.",
  "margin_algorithm", "brand_marketing", "full-year", "yes",
  "three named FY26 reinvestment buckets: marketing, international, AI", "-",
  "Consistent with 1H26 S&M at ~25.9% of revenue. Open.",
  "open", ""),
 ("S154", "call:1Q26", "call-prepared", "Ellie Mertz",
  "The upward revision to our revenue outlook reflects meaningful progress across our growth initiatives and improvements to monetization through a simplified fee structure and our insurance programs, which are expected to lift our full year take rate.",
  "take_rate", "take_rate", "full-year", "yes",
  "FY26 implied take rate up y/y on single-fee migration + insurance", "+",
  "Walked back one quarter later: the 2Q26 letter guides FY26 take rate 'relatively flat' because of higher customer incentives on the new businesses. A three-month reversal.",
  "missed", ""),
 ("S155", "call:1Q26", "call-QA", "Ellie Mertz",
  "we anticipate that that is an expense that will ramp over the course of the year. And the way we've managed the P&L and delivered efficiencies over time, we've the ability to absorb that in the strong margin",
  "ai_cost", "cost_of_revenue", "full-year", "yes",
  "AI opex ramps through FY26 but is absorbed inside the margin guide", "0",
  "This is the first admission that AI spend is a real P&L line, three months after Chesky said 'you won't see it in the P&L'. Escalated further at 2Q26 to 'a material increase'.",
  "kept", ""),
 ("S156", "call:1Q26", "call-QA", "Ellie Mertz",
  "you should see modest upside to our take rate from both the migration to the single fee structure as well as our insurance programs. So, you shouldn't see this as a negative to our take rate.",
  "take_rate", "take_rate", "full-year", "yes",
  "single-fee migration + insurance are take-rate accretive in FY26", "+",
  "Contradicted at 2Q26: 'higher customer incentives related to new businesses during 2026' take the FY26 take rate back to flat.",
  "missed","C076"),
 ("S157", "letter:1Q26", "letter", "shareholder letter",
  "For the full-year 2026, we expect our effective tax rate to be in the high teens.",
  "tax", "g_and_a", "full-year", "yes",
  "FY26 ETR high teens vs 20% in FY25", "+",
  "Open until Feb 2027. Worth ~2-3% on net income, nothing on adj. EBITDA margin.",
  "open", ""),
 ("S158", "letter:1Q26", "letter", "shareholder letter",
  "We expect our implied take rate in Q2 2026 to be up slightly year-over-year.",
  "take_rate", "take_rate", "next-quarter", "yes",
  "2Q26 implied take rate up slightly y/y", "+",
  "Delivered. Known 6 Aug 2026.",
  "kept", ""),

 # ============================== 2Q26 print, 6 Aug 2026 ======================================
 ("S159", "letter:2Q26", "letter", "shareholder letter",
  "For 2026, we now expect to deliver a full-year Adjusted EBITDA Margin of at least 35.5%- an improvement from 2025 that reflects stronger topline growth and underlying operating leverage in our core business, while continuing to invest behind opportunities to drive future growth.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY26 margin >= 35.5%, i.e. +40bp y/y", "+",
  "Open until Feb 2027. Note the reason given is 'operating leverage in our core business' - not the new businesses, and not AI.",
  "open","C079"),
 ("S160", "call:2Q26", "call-prepared", "Brian Chesky",
  "customer support costs per booking declined about 16% year-over-year, driven in part by improvements by our AI assistant. We expect those costs to continue to decline as our AI assistant resolves more and more issues",
  "ai_cost", "ops_support", "multi-year", "yes",
  "support cost per booking keeps falling; voice is the next leg", "+",
  "Open. The run rate implies roughly a further -10 to -15% per year if voice deflects at the chat rate.",
  "open", ""),
 ("S161", "call:2Q26", "call-prepared", "Brian Chesky",
  "Our AI assistant is now available in more than 50 languages. Nearly 45% of issues that start with our AI assistant are now resolved without a human agent, while delivering much faster resolution times.",
  "ai_cost", "ops_support", "next-quarter", "yes",
  "AI resolution share ~45%, 50+ languages", "+",
  "Point-in-time fact rather than a forecast; included because it is the base from which the forward claim runs.",
  "kept", ""),
 ("S162", "call:2Q26", "call-QA", "Ellie Mertz",
  "the updated guidance that we've provided obviously does assume a material increase in terms of the AI spend over the course of the year. So, I would note that, yes, we are expanding margins while absorbing that increased cost.",
  "ai_cost", "cost_of_revenue", "full-year", "yes",
  "AI spend materially up y/y in FY26 and absorbed inside a rising margin", "0",
  "The direct reversal of Chesky's 4Q25 'will not affect the P&L'. Size never quantified - one of the largest unquantified items in the FY26 P&L.",
  "open", ""),
 ("S163", "call:2Q26", "call-QA", "Ellie Mertz",
  "we don't need to grow our head count at levels that we did in the past because we're getting so much more output and speed from our existing workforce, which obviously also creates efficiencies over time.",
  "ai_productivity", "product_dev", "multi-year", "yes",
  "headcount growth below the 2025 rate; output per head rising", "+",
  "First management statement that AI productivity is actually restraining hiring. Consistent with the 4Q25 letter's 'growth rate of SBC and headcount will be lower than 2025'. Open until the FY26 10-K.",
  "open", ""),
 ("S164", "call:2Q26", "call-QA", "Ellie Mertz",
  "given the track record and the somewhat steady EBITDA margins that we have delivered, I think you can see there's a relative floor in our ability to continue to invest against that.",
  "margin_algorithm", "total_margin", "structural", "no",
  "the FLOOR language: margin will not be spent below the delivered band", "0",
  "The clearest statement that ~35% is a policy floor rather than an outcome. Consistent with the 35%/34.5%/35%/35.5% guide sequence since FY2024.",
  "kept", ""),
 ("S165", "call:2Q26", "call-prepared", "Ellie Mertz",
  "For the full year, we expect our implied take rate to be relatively flat compared to 2025, accounting for the timing of bookings versus check-in with Reserve Now, Pay Later, as well as higher customer incentives related to new businesses during 2026.",
  "take_rate", "take_rate", "full-year", "yes",
  "FY26 implied take rate ~flat; incentives on new businesses are the offset", "0",
  "Open. It reverses the 1Q26 'expected to lift our full year take rate' in one quarter and names customer incentives as the reason.",
  "open","C080"),
 ("S166", "call:2Q26", "call-prepared", "Ellie Mertz",
  "Absent these incentives, we would have anticipated our implied take rate to be slightly higher during the year, driven by our monetization initiatives and execution across our product roadmap.",
  "take_rate", "take_rate", "full-year", "yes",
  "underlying take rate up; reported take rate flat because of incentives", "0",
  "Open. The size of the incentive drag is not given - a material undisclosed item because it is the difference between a flat and a rising take rate.",
  "open", ""),
 ("S167", "call:2Q26", "call-QA", "Brian Chesky",
  "we do not need to make any major capital investments. We are not buying up a whole bunch of GPUs.",
  "ai_cost", "cost_of_revenue", "structural", "yes",
  "no AI capex; capex stays ~1% of revenue", "+",
  "Consistent with the filed capex history. It does not speak to inference opex, which Mertz says is materially up.",
  "kept", ""),
 ("S168", "call:2Q26", "call-QA", "Brian Chesky",
  "the inference cost is so outweighed by the amount of money we make on that increased ROI",
  "ai_cost", "cost_of_revenue", "structural", "yes",
  "AI inference cost is de minimis relative to incremental revenue", "+",
  "Unfalsifiable as stated - Airbnb discloses neither inference cost nor AI-attributable revenue.",
  "unverifiable", ""),
 ("S169", "call:2Q26", "call-QA", "Ellie Mertz",
  "that component of ADR appreciation that is durable and really a reflection of incremental value delivered, not just rising prices",
  "adr", "other", "multi-year", "no",
  "bedroom-night mix makes ADR growth durable", "+",
  "Open. It is the current management framing of ADR: a value story rather than a margin lever, which is a reversal of the 2021-2023 framing.",
  "open", ""),
 ("S170", "letter:2Q26", "letter", "shareholder letter",
  "We expect Adjusted EBITDA to increase year-over-year and Adjusted EBITDA Margin to be down slightly compared to Q3 2025, due to timing of investments.",
  "fy_margin_guide", "total_margin", "next-quarter", "yes",
  "3Q26 margin slightly below 3Q25's 50%", "-",
  "Open; settles 5 Nov 2026. This is the live guide for the next print.",
  "open", ""),

 # ============================== investor conferences ========================================
 ("S171", "conf:MS23", "conference", "Brian Chesky",
  "I think you could imagine easily adding a few equivalent percentage rates of take rate if you were to scale that over time.",
  "take_rate", "take_rate", "multi-year", "yes",
  "take rate +several hundred bp over a long horizon via advertising/services", "+",
  "Nothing of the kind has happened by 2Q26: implied take rate has moved within a ~50bp band and advertising has not launched. The most aggressive unmet monetisation claim in the record.",
  "missed", ""),
 ("S172", "conf:BERN24", "conference", "Ellie Mertz",
  "there are obviously incremental opportunities to drive higher margins over time in terms of incremental efficiencies of our variable costs as well as the variance of their relative to, to fixed costs.",
  "margin_algorithm", "total_margin", "multi-year", "no",
  "further margin upside exists but is not being taken", "+",
  "FY margins since: 35.8%, 35.1%, guided >=35.5%. The upside has been reinvested, exactly as the algorithm says.",
  "kept", ""),
 ("S173", "conf:BERN24", "conference", "Ellie Mertz",
  "The fact that a portion of that margin expansion comes from higher ADR should also give you confidence that there are incremental efficiencies for us to drive in the core business that we have not yet delivered.",
  "adr", "total_margin", "multi-year", "no",
  "part of 2020-23 margin expansion was ADR, not cost work", "0",
  "Important admission for attribution: management concedes that ADR did some of the work usually credited to cost discipline.",
  "kept", ""),
 ("S174", "conf:BERN24", "conference", "Ellie Mertz",
  "if performance marketing continues to be the minority of our overall marketing spend, so when we talk about, you know, marginally leaving it leaning in, this is not a big portion of either the overall marketing budget or a percent of revenue.",
  "marketing", "brand_marketing", "structural", "yes",
  "performance marketing is a small minority of S&M", "0",
  "Consistent with the 90%-direct-traffic disclosure repeated 4Q20 through 2Q25.",
  "kept", ""),
 ("S175", "conf:GS24", "conference", "Ellie Mertz",
  "we're able to go from negative 5% to nearly 37% EBITDA margins last year, which was well in excess of actually where we had set our long-term margin target at the time of the IPO.",
  "margin_algorithm", "total_margin", "structural", "yes",
  "the 30% IPO target was beaten by ~700bp in three years", "+",
  "Correct, and it explains why no new long-term target has been set: the old one is stale and management has declined to replace it since 2Q23.",
  "kept", ""),
 ("S176", "conf:GS25", "conference", "Brian Chesky",
  "I think this company is not only under-monetized, it almost isn't really monetized, essentially. We have travel insurance that we offer, but we keep every year offering services for hosts for free.",
  "take_rate", "take_rate", "multi-year", "no",
  "paid host services are the next take-rate leg", "+",
  "Open. No paid host-services product had shipped as of 2Q26; the 2026 take-rate lift instead comes from the single-fee migration and insurance.",
  "open", ""),
 ("S177", "conf:GS25", "conference", "Brian Chesky",
  "The way we would charge for this is probably the equivalent of a larger take rate if you use these services.",
  "take_rate", "take_rate", "multi-year", "no",
  "services monetised as an incremental take rate on attached bookings", "+",
  "Open, and running the wrong way so far: FY26 take rate is flat because of customer incentives on those very services (2Q26 letter).",
  "open", ""),
 ("S178", "conf:MS24", "conference", "Ellie Mertz",
  "It could be leaning into, you know, core marketing channels where we see high ROI. It could be adding at the margin some incremental product development resources",
  "marketing", "brand_marketing", "full-year", "no",
  "the FY24 margin flex is marketing plus product dev", "-",
  "Both happened: FY2024 S&M +157bp and product development +116bp as a share of revenue.",
  "kept", ""),

 # ============================== additions: silence, hotels, phasing =========================
 ("S179", "call:2Q26", "call-QA", "Ellie Mertz",
  "I'm not going to give you a specific guide for 2027 and beyond, but I think looking at our track record, you can even see a couple of things.",
  "declined_to_quantify", "total_margin", "multi-year", "no",
  "no FY2027 margin number exists", "0",
  "Still the position as of 6 Aug 2026. abnb_declined_to_quantify.csv logs this alongside the 2Q23 'I don't have a new long-term target'. Any FY2027 margin in a model is the analyst's, not management's.",
  "kept", ""),
 ("S180", "call:2Q26", "call-QA", "Ellie Mertz",
  "And so, where we have those opportunities, we will lean in.",
  "margin_algorithm", "total_margin", "structural", "no",
  "upside is spent, not banked, whenever the opportunity set is good", "-",
  "The other half of the relative-floor sentence. Read together they define the band: management will not go below the delivered range, and will not bank much above it.",
  "kept", ""),
 ("S181", "call:4Q25", "call-prepared", "Brian Chesky",
  "We don't need massive capital investment to grow. We don't own homes, we don't operate experiences, and we're not building data centers.",
  "ai_cost", "cost_of_revenue", "structural", "yes",
  "capex stays de minimis; no data-centre build", "+",
  "Capex has stayed ~1% of revenue. But the FY2025 10-K commitments note shows purchase obligations rising from $719m to $1,749m and the hosting commitment extended from $672m through 2027 to $1.7bn through 2031 (07_ops_initiatives.csv OPS-09): not owned data centres, but a much larger contracted cloud bill.",
  "partly", ""),
 ("S182", "call:4Q25", "call-QA", "Ellie Mertz",
  "we'll be expanding the hotel supply over the course of the year and intend to exit 2026 with hotels being a meaningfully larger percent of the overall business going forward.",
  "new_business", "field_ops", "full-year", "no",
  "hotels a meaningfully larger share of the business by end-2026", "0",
  "Open. Hotels carry a different take rate and a different support-cost profile from homes and Airbnb has never given either. No budget has been disclosed for the hotels build-out (07_ops_initiatives.csv OPS-22).",
  "open", ""),
 ("S183", "letter:2Q22", "letter", "shareholder letter",
  "Our hiring plan to increase headcount is unchanged from the beginning of the year.",
  "headcount", "product_dev", "full-year", "yes",
  "FY22 headcount growth held at the ~7-8% plan", "0",
  "Actual FY2022 headcount growth was about 1% (Stephenson, 4Q23 call). Management's stated plan and its execution diverged by 6-7pts, in the cost-favourable direction.",
  "missed", ""),
 ("S184", "letter:3Q22", "letter", "shareholder letter",
  "Our hiring plan to modestly increase headcount this year is unchanged from the beginning of the year.",
  "headcount", "product_dev", "full-year", "no",
  "FY22 headcount growth modest and unchanged", "0",
  "About +1% actual. Kept in direction, well under-run in magnitude.",
  "partly", ""),
 ("S185", "letter:4Q23", "letter", "shareholder letter",
  "We intend to test and evaluate the application of this increase in guest service fee when it is enabled on April 1, 2024.",
  "take_rate", "take_rate", "full-year", "yes",
  "cross-currency service fee live 1 Apr 2024, ~100bp on ~20% of GBV", "+",
  "Shipped. Mertz sized it at the 4Q24 call as ~20bp of annualised implied take rate; the FY2025 outturn (-16bp y/y) shows other items more than absorbed it.",
  "kept", ""),
 ("S186", "letter:1Q25", "letter", "shareholder letter",
  "Since we launched our updated hosting quality system in 2023, we've removed over 450,000 listings, and have seen a reduction in customer service issue rates and credit card chargeback rates.",
  "support_cost", "ops_support", "structural", "yes",
  "supply curation cuts support contacts and chargebacks", "+",
  "Repeated every quarter with a rising count: 400k (4Q24), 450k (1Q25), 500k (2Q25), 550k (3Q25 and 4Q25). It is the non-AI half of the support-cost story and it predates the AI agent by two years.",
  "kept", ""),
 ("S187", "letter:4Q25", "letter", "shareholder letter",
  "Since launching our updated hosting quality system in 2023, we've removed over 550,000 listings, and we saw a year-over-year reduction in customer service issue rates and credit card chargeback rates during 2025.",
  "payments", "cost_of_revenue", "full-year", "yes",
  "chargeback rate down y/y in FY2025", "+",
  "Consistent with merchant fees plus chargebacks holding in a 1.82-1.89% of GBV band since 2021 (07_ops_initiatives.csv OPS-04) rather than rising with mix.",
  "kept", ""),
 ("S188", "letter:2Q26", "letter", "shareholder letter",
  "We expect this cost to continue declining as our AI assistant resolves a broader range of issues and we introduce new capabilities.",
  "ai_cost", "ops_support", "full-year", "yes",
  "support cost per booking keeps falling through 2H26", "+",
  "Open; the next test is the 5 Nov 2026 print. Ops & support was 10.93% of revenue in 1H26 against 11.83% in 1H25.",
  "open", ""),
 ("S189", "call:2Q25", "call-prepared", "Ellie Mertz",
  "we anticipate that adjusted EBITDA margin will be lower than in Q3 2024, primarily due to investments in new growth and policy initiatives.",
  "fy_margin_guide", "total_margin", "next-quarter", "yes",
  "3Q25 margin below 3Q24's 52%", "-",
  "3Q25 margin 50% vs 52%: -200bp, as guided. Note the phrase 'policy initiatives' - a cost bucket that appears only in 2025 and is never sized.",
  "kept","C063"),
 ("S190", "call:3Q25", "call-prepared", "Ellie Mertz",
  "On profitability, we now expect our full year adjusted EBITDA margin to be approximately 35%, up from the 34.5% floor previously shared.",
  "fy_margin_guide", "total_margin", "full-year", "yes",
  "FY25 margin ~35%, raised from the 34.5% floor", "+",
  "FY2025 35.10%. The raise came at the third-quarter print, the same point in the cycle as the FY2024 raise to 'approximately 35.5%'. Known 12 Feb 2026.",
  "kept","C065"),
 ("S191", "letter:4Q25", "letter", "shareholder letter",
  "We expect Adjusted EBITDA Margin to be approximately flat year-over-year.",
  "fy_margin_guide", "total_margin", "next-quarter", "yes",
  "1Q26 margin ~= 1Q25's 18%", "0",
  "1Q26 margin 19% vs 18%: beat by ~100bp. Known 7 May 2026.",
  "kept", ""),
 ("S192", "letter:1Q26", "letter", "shareholder letter",
  "We expect Adjusted EBITDA and Adjusted EBITDA Margin to be up year-over-year in Q2 2026.",
  "fy_margin_guide", "total_margin", "next-quarter", "yes",
  "2Q26 margin above 2Q25", "+",
  "1H26 margin 28.32% vs 27.20% in 1H25 (abnb_quarterly_costlines.csv). Kept. Known 6 Aug 2026.",
  "kept", ""),
 ("S193", "call:1Q26", "call-QA", "Ellie Mertz",
  "we've been really localizing the marketing messages. As we've said in the letter, in Q1 alone, we had 16 local marketing campaigns that really tried to capture the local zeitgeist of cultural moments to drive awareness and consideration of Airbnb.",
  "marketing", "brand_marketing", "full-year", "yes",
  "campaign count per quarter rising - the unit of marketing spend is the market, not the dollar", "-",
  "Consistent with the fixed-per-market model and with the 1H26 S&M step-up to 25.87% of revenue. 16 campaigns in one quarter is the largest number Airbnb has disclosed.",
  "kept", ""),
 ("S194", "call:1Q23", "call-QA", "David E. Stephenson",
  "We obviously reduced our head count by 25%. We've only grown it moderately since.",
  "headcount", "product_dev", "structural", "yes",
  "the 2020 -25% reset is the base of every subsequent margin claim", "+",
  "Confirmed by Chesky at 2Q24: 'essentially the same amount of employees as before the pandemic and double the revenue'. Revenue per employee then peaked at $1,521k in 2024 and fell to $1,493k in 2025 (07_ops_initiatives.csv OPS-03) - the reset has stopped paying.",
  "kept", ""),
]

# ------------------------------------------------------------------------------------------------
# The structural / algorithm subset (rows referenced by 31a_margin_algorithm_quotes.csv)
# ------------------------------------------------------------------------------------------------
# 25 statements. The wider set of structural statements is theme == "margin_algorithm" in the
# main file (plus the "structural" horizon rows); this is the subset that defines the rule itself.
ALGORITHM_IDS = ["S001", "S004", "S005", "S012", "S025", "S026", "S028", "S039", "S044", "S045",
                 "S055", "S057", "S060", "S069", "S076", "S097", "S108", "S119", "S121", "S125",
                 "S138", "S140", "S146", "S164", "S173"]

ALGORITHM_ROLE = {
    "S001": "the original long-term target: 30% or greater",
    "S003": "the marketing floor promise: never 2019 intensity again",
    "S004": "fixed costs do not come back with volume",
    "S005": "names the three variable-cost levers used ever since",
    "S012": "give value before taking take rate",
    "S016": "30%+ reaffirmed and already being beaten",
    "S020": "marketing settles into a range, not a downward path",
    "S025": "brand is fixed, performance is variable",
    "S026": "the promised post-2023 marketing leverage (never delivered)",
    "S028": "ADR as a direct margin driver",
    "S035": "variable + fixed gains defend FCF margin against ADR",
    "S039": "marketing gets more efficient every single year (falsified)",
    "S044": "efficiencies exactly offset the ADR headwind",
    "S045": "not in profit maximisation mode",
    "S051": "margin expansion deprioritised versus growth",
    "S055": "margin expansion will come from new services, not cost",
    "S057": "marketing % of revenue as a structural constant (falsified)",
    "S060": "no successor long-term margin target",
    "S069": "the FY guide is a floor by construction",
    "S076": "long-run expansion from services and experiences",
    "S089": "no sea change in profitability; expansions are opex",
    "S097": "THE ALGORITHM: find efficiencies every year, reinvest part",
    "S108": "brand marketing is a fixed cost per market",
    "S119": "in a given year spend may exceed efficiency",
    "S121": "core business unit economics are ADR-insensitive",
    "S125": "the S&M line now contains field ops, not just advertising",
    "S138": "FY26: reinvest most of the efficiencies",
    "S140": "AI will not affect the P&L (reversed in 2Q26)",
    "S146": "cost of revenue and ops&support scale linearly with revenue",
    "S164": "the RELATIVE FLOOR: margin will not be spent below the band",
    "S172": "unbanked margin upside exists",
    "S173": "part of past margin expansion was ADR, not cost work",
    "S175": "the IPO target was beaten by ~700bp",
}

# ------------------------------------------------------------------------------------------------
# Implied operating profile FY2026-FY2028
# (cost_line, fy, implied_trajectory, basis_rows, confidence, realised_history_that_tests_it)
# ------------------------------------------------------------------------------------------------
PROFILE = [
 # ---- total margin -------------------------------------------------------------------------
 ("total_margin", "FY2026", "adj. EBITDA margin >=35.5%, i.e. >=+40bp y/y vs FY2025 35.1%",
  "S137;S150;S159;S138;S164",
  "high",
  "FY guides are floors and every floor since FY2024 has been beaten: FY24 floor 35% -> 35.8% (+80bp); FY25 floor 34.5% -> 35.1% (+60bp); FY26 already raised twice, from 'stable' to >=35% to >=35.5%. A 35.8-36.2% print is the natural read of the pattern."),
 ("total_margin", "FY2027", "management has given no number; the algorithm implies stable to modestly up, ~35.5-36%",
  "S097;S119;S164;S172",
  "low",
  "Management has declined a multi-year margin target at every opportunity since 2Q23 ('I don't have a new long-term target'). The only anchor is the relative-floor language of 2Q26. Treat any FY27 margin above ~36.5% as a house view, not a management view."),
 ("total_margin", "FY2028", "no management statement exists; silence, not a forecast",
  "S060;S164",
  "none",
  "SILENT. The longest-dated margin statement outstanding is the 2Q26 'relative floor' remark, which has no year attached. Airbnb has not given a multi-year margin number since the 30%+ of Feb 2021."),
 # ---- cost of revenue ----------------------------------------------------------------------
 ("cost_of_revenue", "FY2026", "roughly flat as % of revenue; 'will scale somewhat linearly' with revenue, with 'some efficiencies'",
  "S146;S111;S065;S162;S167",
  "high",
  "Realised cost of revenue: 19.29% of revenue FY2021 -> 17.85 FY2022 -> 17.17 FY2023 -> 16.92 FY2024 -> 17.04 FY2025; like-for-like halves 20.16 (1H24) -> 19.56 (1H25) -> 19.31 (1H26). The line stopped compounding two years before management said it would. The offsetting new item is cloud and AI inference: purchase obligations went from $719m to $1,749m and the hosting commitment from $672m through 2027 to $1.7bn through 2031 (07_ops_initiatives.csv OPS-09), while Mertz says AI spend is materially up in FY26 and has never sized it."),
 ("cost_of_revenue", "FY2027", "no guide; the linear-scaling framing implies flat % of revenue absent an AI cost step",
  "S146;S162;S167",
  "low",
  "The forward risk is one-sided: management has said there is no capex, but has conceded a material and unquantified opex increase in AI. If inference cost grows faster than bookings, this is the line it lands in."),
 ("cost_of_revenue", "FY2028", "silent",
  "",
  "none",
  "SILENT. No statement extends past FY2026."),
 # ---- operations and support ---------------------------------------------------------------
 ("ops_support", "FY2026", "customer-support cost per booking down 10-16% y/y and still falling; the line as a whole scales 'somewhat linearly'",
  "S146;S151;S152;S160;S141;S145",
  "high",
  "The two disclosed unit numbers are 1Q26 -10% y/y and 2Q26 -16% y/y in customer-support cost per booking, with AI resolution share going a third (4Q25) -> over 40% (1Q26) -> nearly 45% (2Q26) in 50+ languages. Realised line: 14.13% of revenue FY2021 -> 12.39 -> 11.96 -> 11.55 -> 10.84 FY2025, and 10.93% in 1H26 against 11.83% in 1H25. Two caveats: the 2Q24 letter says some customer-service investment is booked as contra-revenue, so this line understates support cost; and the third-party support network grew from 11,000 workers to 13,000 in 2025 (07_ops_initiatives.csv OPS-06)."),
 ("ops_support", "FY2027", "further decline in support cost per booking, driven by AI voice; no percentage given",
  "S160;S142",
  "medium",
  "Chesky's forward statement is qualitative ('continue to decline ... as we bring it to voice'). Extrapolating the 10%/16% cadence gives another -10 to -15% per booking, but that is the analyst's arithmetic, not management's."),
 ("ops_support", "FY2028", "silent",
  "",
  "none",
  "SILENT."),
 # ---- product development ------------------------------------------------------------------
 ("product_dev", "FY2026", "headcount growth below FY2025's rate; SBC growth also below FY2025's; AI-aided output per head rising",
  "S144;S163;S143",
  "medium",
  "The claim is deceleration, not decline. Realised product development: 23.78% of revenue FY2021 -> 17.88 FY2022 -> 17.36 FY2023 (peak leverage) -> 18.52 FY2024 -> 19.23 FY2025 -> 20.84 in 1H26. Chesky's +30% engineering productivity claim (1Q23, restated 4Q24) has never shown up as leverage on this line; headcount grew about 12% in 2025 and revenue per employee fell for the first time, to $1,493k from $1,521k (07_ops_initiatives.csv OPS-03)."),
 ("product_dev", "FY2027", "no number; 2Q26 language implies headcount growth stays below the historical rate",
  "S163;S113;S114",
  "low",
  "Two years of the +30% productivity claim have produced no product-dev leverage. Treat any modelled decline in product development % of revenue as unsupported by disclosure."),
 ("product_dev", "FY2028", "silent",
  "",
  "none",
  "SILENT."),
 # ---- brand and performance marketing ------------------------------------------------------
 ("brand_marketing", "FY2026", "up again as a share of revenue: 'some incremental investment ... obviously, in sales and marketing', with efficient marketing named as one of three reinvestment buckets",
  "S147;S153;S125;S108",
  "high",
  "1H2026 S&M 25.87% of revenue against 21.14% for FY2025 and 17.78% at the FY2023 trough; +251bp y/y on a like-for-like half. Guide history on this line is the worst in the record: FY2024 guided 'largely the same' (17.78%) and printed 19.35%, a 157bp miss worth ~4% of EBITDA; the 4Q21 promise of post-2023 marketing leverage never arrived. From 2025 the line also carries field operations and supply acquisition (2Q25), so it is no longer a clean advertising ratio - but in 1H26 brand+performance cash marketing itself grew 32% y/y against 17% revenue growth, so the field-ops explanation no longer covers it."),
 ("brand_marketing", "FY2027", "no number; the fixed-per-market model implies core-market leverage funding further expansion-market spend",
  "S108;S109;S120",
  "low",
  "The fixed-cost-per-market claim is the load-bearing assumption behind any modelled marketing leverage. It has been true of core markets and false of the total: S&M % of revenue has risen for three consecutive years and is 810bp above the FY2023 trough."),
 ("brand_marketing", "FY2028", "silent",
  "",
  "none",
  "SILENT."),
 # ---- field ops / new business -------------------------------------------------------------
 ("field_ops", "FY2026", "the FY25 ~$200m does not roll off - part is 'fixed head count'; go-to-market spend rises further",
  "S127;S147;S125;S135",
  "medium",
  "FY2025 came in at ~$200m against a $200-250m guide, and field operations cash grew 43% ($693m -> $993m, ~1.9pts of revenue). Chesky's 2Q24 'most of these new services and offerings are going to not cost very much' was contradicted six months later by that guide. No FY26 dollar figure has been given - the single largest unquantified item in the 2026 P&L alongside AI, and management has refused six times to give the contribution margin of the new businesses (abnb_declined_to_quantify.csv)."),
 ("field_ops", "FY2027", "'every incremental new business ... more efficient to launch than the prior businesses' - a theory, in Chesky's own word",
  "S135;S127",
  "low",
  "No per-business launch cost has ever been disclosed. The one testable version - the FY25 $200-250m guide - was met at the low end."),
 ("field_ops", "FY2028", "silent",
  "",
  "none",
  "SILENT."),
 # ---- G&A and taxes ------------------------------------------------------------------------
 ("g_and_a", "FY2026", "G&A held down ('extremely disciplined'); effective tax rate high teens, from 20% in FY2025",
  "S157;S148;S111;S134",
  "high",
  "G&A realised: 11.31% of revenue FY2022, 20.42% FY2023 (inflated ~1,160bp by the Italian withholding and lodging-tax reserves), 10.67% FY2024, 10.96% FY2025, 9.62% in 1H26. Tax guides have been right on level and wrong on timing: the 4Q23 letter promised mid-to-high teens near term and low 20s long term, and the FY2024 15-19% range printed 20.5% before OBBBA reset the long-run guide back to mid-to-high teens. One-off non-income tax items keep appearing: ~$90m in 4Q25, a $213m CAMT allowance in 3Q25, ~$70m of deferred tax in 1Q26. None touch adj. EBITDA."),
 ("g_and_a", "FY2027", "long-term effective tax rate mid-to-high teens under OBBBA",
  "S148;S134",
  "medium",
  "This is the only FY2027-and-beyond quantified statement management has outstanding on any cost line. It sits below the EBITDA line."),
 ("g_and_a", "FY2028", "long-term ETR mid-to-high teens (the same statement, undated)",
  "S148",
  "low",
  "'Long-term' is not defined. Treat as a level, not a schedule."),
 # ---- stock-based compensation -------------------------------------------------------------
 ("sbc", "FY2026", "y/y growth rate of SBC lower than FY2025's; headcount growth also lower",
  "S144;S163",
  "medium",
  "The record depends on which series you use. XBRL (abnb_quarterly_costlines.csv): FY2023 +18.3%, FY2024 +30.8%, FY2025 +9.9%. Shareholder letters (abnb_fcf_bridge.csv): +20.4%, +25.6%, +13.1%. The FY2024 guide moved from +20% (1Q24 letter) to +25% (3Q24 letter) and was missed on either series. FY2025 did roughly converge on headcount (~+12%). The 3Q23-3Q24 letters promised SBC would grow 'largely in-line with headcount growth'; the 4Q25 letter has retreated to merely 'lower than 2025'. Model SBC on its own trend and state which series you use."),
 ("sbc", "FY2027", "silent - the convergence-with-headcount promise has been withdrawn",
  "S063;S106;S144",
  "none",
  "SILENT beyond FY2026. The 2023-24 convergence language no longer appears in the letters."),
 ("sbc", "FY2028", "silent",
  "",
  "none",
  "SILENT."),
 # ---- take rate ----------------------------------------------------------------------------
 ("take_rate", "FY2026", "relatively flat vs FY2025; underlying would have been slightly higher but for customer incentives on the new businesses",
  "S165;S166;S154;S156",
  "high",
  "Guided up at 1Q26 ('expected to lift our full year take rate') and back to flat at 2Q26 in a single quarter. The precedent is FY2025, when the 4Q24 call promised 'the full benefit of 20 basis points increase' and the year printed 13.41% against 13.57% - -16bp y/y and 36bp below the guide. Realised FY implied take rate: 13.27 (22), 13.53 (23), 13.57 (24), 13.41 (25). Of the 13 quarterly take-rate guides in 02_guidance_ledger.csv the two clean misses (3Q25, 1Q26) run the same way: promised up or flat, delivered down."),
 ("take_rate", "FY2027", "no number; the stated sources are paid host services, advertising and services attach - all still unshipped",
  "S176;S177;S055;S076;S171",
  "low",
  "Chesky told Morgan Stanley in Mar 2023 he could 'easily' imagine adding a few percentage points of take rate; three and a half years later the implied take rate has moved within roughly 50bp. Advertising is explicitly deferred behind AI search (3Q25)."),
 ("take_rate", "FY2028", "silent",
  "",
  "none",
  "SILENT."),
 # ---- FX ------------------------------------------------------------------------------------
 ("fx", "FY2026", "~3 percentage points of FX tailwind to revenue in 1H26 after hedges, fading as the year progresses",
  "S122",
  "medium",
  "Management hedges revenue, which damps both directions; it said so explicitly in 1Q25 when asked why a weaker dollar was not lifting the margin guide. Because costs are dollar-heavy and revenue is not, FX moves the margin, and Airbnb has never sized that sensitivity. The 4Q25/1Q26/2Q26 letters all quantify the revenue tailwind at ~3pts and say it fades."),
 ("fx", "FY2027", "silent on FX; hedging policy assumed unchanged",
  "S122",
  "none",
  "SILENT. No FX assumption has ever been given beyond the current fiscal year."),
 ("fx", "FY2028", "silent",
  "",
  "none",
  "SILENT."),
]


# FactSet writes the CFO's name in full, stockanalysis writes the short form. Same person.
SPEAKER_CANON = {"David E. Stephenson": "Dave Stephenson"}


# ------------------------------------------------------------------------------------------------
def main():
    docs = build_corpus()
    print(f"corpus: {len(docs)} documents "
          f"({sum(1 for k in docs if k.startswith('letter:'))} letters, "
          f"{sum(1 for k in docs if k.startswith('call:'))} calls, "
          f"{sum(1 for k in docs if k.startswith('conf:'))} conferences)")

    claims03 = {}
    p03 = MAIN / "data" / "processed" / "overnight" / "03_forward_claims.csv"
    if not p03.exists():
        p03 = ROOT / "data" / "processed" / "overnight" / "03_forward_claims.csv"
    if p03.exists():
        with p03.open(encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                claims03[r["claim_id"]] = r["verdict"]

    rows, failures, longq = [], [], []
    for (sid, doc_id, source, speaker, quote, theme, cost_line, horizon, quantified,
         implied_metric, direction, outcome, verdict, cid03) in S:
        if doc_id not in docs:
            failures.append((sid, doc_id, "DOC MISSING"))
            continue
        doc = docs[doc_id]
        ok, loc = locate(doc, quote)
        if not ok:
            failures.append((sid, doc_id, quote[:70]))
        nwords = len(quote.split())
        if nwords > 45:
            longq.append((sid, nwords))
        kind, tag = doc_id.split(":", 1)
        src = source
        if "stockanalysis" in doc["raw"] or "transcripts/web" in doc["raw"]:
            src = source + "-sa"
        rows.append({
            "statement_id": sid,
            "print": tag,
            "date": PRINT_DATE[tag],
            "source": src,
            "speaker": SPEAKER_CANON.get(speaker, speaker),
            "quote": quote,
            "quote_verified": "yes" if ok else "NO",
            "quote_words": nwords,
            "theme": theme,
            "cost_line": cost_line,
            "horizon": horizon,
            "quantified": quantified,
            "implied_metric": implied_metric,
            "implied_direction_for_margin": direction,
            "outcome_if_closed": outcome,
            "verdict": verdict,
            "claim_id_03": cid03,
            "claim_id_03_verdict": claims03.get(cid03, ""),
            "source_file": doc["raw"],
            "locator": loc,
        })

    fields = list(rows[0].keys())
    p = OUT / "31a_mgmt_margin_statements.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {p} ({len(rows)} rows)")

    # ---- algorithm quotes -------------------------------------------------------------------
    by_id = {r["statement_id"]: r for r in rows}
    algo = []
    for sid in ALGORITHM_IDS:
        r = by_id.get(sid)
        if r is None:
            continue
        algo.append({
            "statement_id": sid,
            "date": r["date"],
            "print": r["print"],
            "speaker": r["speaker"],
            "source": r["source"],
            "structural_role": ALGORITHM_ROLE.get(sid, ""),
            "quote": r["quote"],
            "quote_verified": r["quote_verified"],
            "cost_line": r["cost_line"],
            "verdict": r["verdict"],
            "source_file": r["source_file"],
            "locator": r["locator"],
        })
    algo.sort(key=lambda x: x["date"])
    p = OUT / "31a_margin_algorithm_quotes.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(algo[0].keys()))
        w.writeheader()
        w.writerows(algo)
    print(f"wrote {p} ({len(algo)} rows)")

    # ---- implied profile --------------------------------------------------------------------
    prof = []
    for cost_line, fy, traj, basis, conf, hist in PROFILE:
        ids = [i for i in basis.split(";") if i]
        missing = [i for i in ids if i not in by_id]
        if missing:
            failures.append(("PROFILE", f"{cost_line} {fy}", f"unknown ids {missing}"))
        prof.append({
            "cost_line": cost_line,
            "fiscal_year": fy,
            "mgmt_implied_trajectory": traj,
            "basis_statement_ids": basis,
            "n_statements": len(ids),
            "mgmt_silent": "yes" if conf == "none" else "no",
            "confidence": conf,
            "realised_history_that_tests_it": hist,
        })
    p = OUT / "31a_mgmt_implied_profile.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(prof[0].keys()))
        w.writeheader()
        w.writerows(prof)
    print(f"wrote {p} ({len(prof)} rows)")

    # ---- diagnostics ------------------------------------------------------------------------
    from collections import Counter
    print("\nby verdict:", dict(Counter(r["verdict"] for r in rows)))
    print("by cost_line:", dict(Counter(r["cost_line"] for r in rows)))
    print("by horizon:", dict(Counter(r["horizon"] for r in rows)))
    print("by source:", dict(Counter(r["source"] for r in rows)))
    prints_covered = sorted({r["print"] for r in rows if r["print"] in PRINT_DATE and "Q" in r["print"]})
    print(f"prints covered: {len(prints_covered)} -> {prints_covered}")
    if longq:
        print("\nQUOTES OVER 45 WORDS:", longq)
    if failures:
        print(f"\n{len(failures)} VERIFICATION FAILURES:")
        for f in failures:
            print("  ", f)
    else:
        print("\nall quotes verified as exact substrings of their source documents")


if __name__ == "__main__":
    main()
