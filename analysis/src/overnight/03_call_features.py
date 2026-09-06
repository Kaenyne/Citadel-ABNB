"""Workstream 03: per-print language features from the 23 Airbnb earnings calls (Q4 2020 to Q2 2026).

Reads
  Transcripts, in this order of preference (first directory found wins per file):
    data/raw/transcripts/ir/<q>Q<yy>.txt        pdftotext of the FactSet corrected transcripts on the IR CDN
                                                (4Q21, 1Q23..2Q26; 15 calls). Parsed with parse_ir() from
                                                analysis/src/transcript_analytics.py (speaker-tagged).
    <scratch>/03/fool/<q>Q<yy>.html             Motley Fool web transcripts for 4Q20..3Q21, 1Q22..4Q22 (8 calls),
                                                fetched 2026-09-06 from
                                                https://www.fool.com/earnings/call-transcripts/<yyyy>/<mm>/<dd>/airbnb-inc-abnb-q<n>-<yyyy>-earnings-call-transcript/
                                                These carry <p><strong>Speaker</strong> -- Title</p> tags and
                                                "Prepared Remarks:" / "Questions & Answers:" headers, so speaker
                                                attribution is exact (the stockanalysis.com copies used by the
                                                transcript-analytics note have no speaker tags).
    The sibling worktree ../citadel-abnb-transcripts/data/raw/transcripts is also searched for the IR files.
  data/processed/abnb_declined_to_quantify.csv  hand-verified declines (transcript-analytics note), counted per call.
  Loughran-McDonald master dictionary (2018 vintage) shipped inside the pysentiment2 package
  (static/LM.csv; columns Positive, Negative, Uncertainty, Modal). `py -3.13 -m pip install pysentiment2`.

Writes
  data/processed/overnight/03_call_features.csv   one row per call, ~90 columns (see FEATURE_DOC at the bottom)
  data/processed/overnight/03_call_turns.csv      one row per speaker turn (section, role, speaker, words,
                                                  LM counts) so a reviewer can audit any feature
  data/processed/overnight/03_theme_lexicon.csv   the theme regexes used

Point-in-time: everything here is known only when the call ends (about 17:30 ET on print day, after the
letter at 16:05 ET). These features can explain the next-day reaction; they cannot forecast the print.

Run: py -3.13 analysis/src/overnight/03_call_features.py
"""
import csv
import html
import os
import re
import sys
from collections import Counter, OrderedDict, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "analysis" / "src"))
from transcript_analytics import parse_ir, norm_firm, norm_name, DECLINE_HINT  # noqa: E402

SCRATCH = Path(os.environ.get("ABNB_SCRATCH", r"C:\Users\krish\AppData\Local\Temp\claude\C--Users-krish-citadel-abnb"
                              r"\fe93ae72-a37b-4547-991f-690c32a0f6a0\scratchpad")) / "03"
OUT = ROOT / "data" / "processed" / "overnight"
OUT.mkdir(parents=True, exist_ok=True)

IR_DIRS = [ROOT / "data" / "raw" / "transcripts" / "ir",
           ROOT.parent / "citadel-abnb-transcripts" / "data" / "raw" / "transcripts" / "ir",
           SCRATCH / "transcripts" / "ir"]
FOOL_DIR = SCRATCH / "fool"

CALLS = [
    ("2020Q4", "4Q20", "fool"), ("2021Q1", "1Q21", "fool"), ("2021Q2", "2Q21", "fool"), ("2021Q3", "3Q21", "fool"),
    ("2021Q4", "4Q21", "ir"), ("2022Q1", "1Q22", "fool"), ("2022Q2", "2Q22", "fool"), ("2022Q3", "3Q22", "fool"),
    ("2022Q4", "4Q22", "fool"), ("2023Q1", "1Q23", "ir"), ("2023Q2", "2Q23", "ir"), ("2023Q3", "3Q23", "ir"),
    ("2023Q4", "4Q23", "ir"), ("2024Q1", "1Q24", "ir"), ("2024Q2", "2Q24", "ir"), ("2024Q3", "3Q24", "ir"),
    ("2024Q4", "4Q24", "ir"), ("2025Q1", "1Q25", "ir"), ("2025Q2", "2Q25", "ir"), ("2025Q3", "3Q25", "ir"),
    ("2025Q4", "4Q25", "ir"), ("2026Q1", "1Q26", "ir"), ("2026Q2", "2Q26", "ir"),
]
CALL_DATES = {  # call date (ET), from the transcripts
    "2020Q4": "2021-02-25", "2021Q1": "2021-05-13", "2021Q2": "2021-08-12", "2021Q3": "2021-11-04",
    "2021Q4": "2022-02-15", "2022Q1": "2022-05-03", "2022Q2": "2022-08-02", "2022Q3": "2022-11-01",
    "2022Q4": "2023-02-14", "2023Q1": "2023-05-09", "2023Q2": "2023-08-03", "2023Q3": "2023-11-01",
    "2023Q4": "2024-02-13", "2024Q1": "2024-05-08", "2024Q2": "2024-08-06", "2024Q3": "2024-11-07",
    "2024Q4": "2025-02-13", "2025Q1": "2025-05-01", "2025Q2": "2025-08-06", "2025Q3": "2025-11-06",
    "2025Q4": "2026-02-12", "2026Q1": "2026-05-07", "2026Q2": "2026-08-06",
}


# ----------------------------------------------------------------------------------------------
# Speaker roles
# ----------------------------------------------------------------------------------------------
def exec_role(speaker, quarter):
    s = speaker.lower()
    if "chesky" in s:
        return "ceo"
    if "stephenson" in s:
        return "cfo"
    if "mertz" in s:
        # Ellie Mertz was VP Finance (IR host) until she became CFO on 1 Mar 2024; first call as CFO was 1Q24
        return "cfo" if quarter >= "2024Q1" else "ir"
    if "ian lee" in s or s in ("ir",):
        return "ir"
    if s in ("management",):
        return "mgmt_unknown"
    return "other_mgmt"


# ----------------------------------------------------------------------------------------------
# Fool.com parser
# ----------------------------------------------------------------------------------------------
TAG = re.compile(r"<[^>]+>")


def parse_fool(raw):
    body = raw
    m = re.search(r"Prepared Remarks:</h2>(.*?)<h2[^>]*>Call participants:", raw, re.S)
    if m:
        body = m.group(1)
    section = "prepared"
    turns = []
    cur = None
    buf = []

    def flush():
        nonlocal buf
        if cur and buf:
            txt = re.sub(r"\s+", " ", " ".join(buf)).strip()
            if txt:
                turns.append({"section": cur[0], "role": cur[1], "speaker": cur[2], "firm_raw": cur[3], "text": txt})
        buf = []

    for piece in re.split(r"(?=<p>|<h2)", body):
        if piece.startswith("<h2") and "Questions" in piece:
            flush(); section = "qa"; continue
        sm = re.match(r"<p><strong>([^<]+)</strong>\s*(?:--\s*(?:<em>)?([^<]*)(?:</em>)?)?\s*</p>", piece)
        if sm:
            flush()
            name = html.unescape(sm.group(1)).strip()
            title = html.unescape(sm.group(2) or "").strip()
            if name.lower().startswith("operator"):
                cur = (section, "operator", "Operator", "")
            elif name.lower().startswith("duration"):
                cur = None
            elif re.search(r"analyst", title, re.I) or (title and not re.search(r"airbnb|officer|founder|investor|finance", title, re.I) and section == "qa"):
                cur = (section, "analyst", norm_name(name), re.sub(r"\s*--\s*Analyst\s*$", "", title, flags=re.I))
            else:
                cur = (section, "mgmt", norm_name(name), "Airbnb")
            continue
        if piece.startswith("<p>") and cur:
            txt = html.unescape(TAG.sub("", piece))
            if re.search(r"This article is a transcript|More ABNB analysis|All earnings call transcripts", txt):
                continue
            buf.append(txt)
    flush()
    # safe-harbour paragraph from the IR host is not management language
    for t in turns:
        if t["section"] == "prepared" and t["role"] == "mgmt" and re.search(r"forward-looking statements|non-GAAP", t["text"]):
            t["role"] = "ir"
    return turns


def load_calls():
    calls = []
    for q, stem, src in CALLS:
        if src == "ir":
            path = next((d / f"{stem}.txt" for d in IR_DIRS if (d / f"{stem}.txt").exists()), None)
            if path is None:
                raise FileNotFoundError(f"IR transcript {stem}.txt not found in {IR_DIRS}")
            _, turns = parse_ir(path.read_text(encoding="utf-8", errors="replace"))
            for t in turns:
                if t["section"] == "prepared" and t["role"] == "mgmt" and re.search(r"forward-looking statements|non-GAAP financial measures", t["text"]):
                    t["role"] = "ir"
        else:
            path = FOOL_DIR / f"{stem}.html"
            turns = parse_fool(path.read_text(encoding="utf-8", errors="replace"))
        for t in turns:
            t["exec"] = exec_role(t["speaker"], q) if t["role"] in ("mgmt", "ir") else t["role"]
        calls.append({"quarter": q, "stem": stem, "source": src, "date": CALL_DATES[q], "turns": turns})
    return calls


# ----------------------------------------------------------------------------------------------
# Lexicons
# ----------------------------------------------------------------------------------------------
def load_lm():
    import pysentiment2
    p = Path(pysentiment2.__file__).parent / "static" / "LM.csv"
    pos, neg, unc, weak = set(), set(), set(), set()
    with open(p, encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            w = r["Word"].lower()
            if r["Positive"] not in ("0", ""):
                pos.add(w)
            if r["Negative"] not in ("0", ""):
                neg.add(w)
            if r["Uncertainty"] not in ("0", ""):
                unc.add(w)
            if r["Modal"] == "3":
                weak.add(w)
    return pos, neg, unc, weak


LM_POS, LM_NEG, LM_UNC, LM_WEAK = load_lm()
# call-specific hedges that LM misses (all lower case, whole words)
HEDGE_EXTRA = {"cautious", "cautiously", "caution", "variability", "moderate", "moderating", "moderation",
               "softness", "softer", "softening", "uneven", "choppy", "choppiness", "volatile", "volatility",
               "uncertain", "uncertainty", "unclear", "hard to say", "too early", "wait and see", "prudent"}
NEGATOR = re.compile(r"\b(not|no|never|n't|without|less)\b", re.I)

THEMES = OrderedDict([
    ("demand_macro", r"\b(macro\w*|softness|softer|soften\w*|slow(?:ing|down|er)?|decelerat\w*|moderat\w*|weak\w*|headwinds?|uncertaint\w*|recession\w*|consumer (?:demand|confidence|spending)|tariffs?|inflation\w*|lead times?|booking window|shorter (?:booking|lead)|demand (?:environment|trends?|signals?|is|has|was|remains)|cancellation\w*)\b"),
    ("pricing_adr", r"\b(adrs?|average daily rates?|affordab\w*|total price|price (?:display|transparency|tool\w*|competitiv\w*)|cleaning fees?|discount\w*|pricing|prices?|priced|cheaper|value for money|smart pricing)\b"),
    ("take_rate_fees", r"\b(take[- ]rates?|service fees?|host[- ]only fee|guest fees?|host fees?|monetiz\w*|fee structure|single fee|cross[- ]currency fee|fx fee|unearned fees?)\b"),
    ("marketing", r"\b(marketing|brand campaign\w*|brand (?:spend|awareness|investment)|performance marketing|advertis\w*|paid search|\bsem\b|search engine marketing|s&m|sales and marketing|sales & marketing)\b"),
    ("margins_profitability", r"\b(margins?|ebitda|profitab\w*|profits?|operating leverage|free cash flow|fcf|net income|cost (?:structure|discipline|base)|efficien\w*|leverage in the (?:model|business))\b"),
    ("supply_hosts", r"\b(supply|hosts?|hosting|listings?|superhost\w*|active listings?|co-host\w*|quality (?:listings?|supply|system)|guest favorites?|removed (?:listings?|supply))\b"),
    ("regulation", r"\b(regulat\w*|regulators?|new york|nyc|local law|legislat\w*|ordinances?|registration|barcelona|bans?|banned|short[- ]term rental (?:rules|laws?|restrictions?)|policymakers?|lawmakers?|city (?:officials|governments?)|taxes|tax (?:rate|law))\b"),
    ("ai", r"\b(\bai\b|artificial intelligence|generative|llms?|agentic|machine learning|chatgpt|openai|large language|ai[- ]native|ai (?:agents?|search|models?|spend|investment|infrastructure|compute)|copilot|gpt|gameplanner)\b"),
    ("new_businesses", r"\b((?<!customer )(?<!guest )(?<!community )(?<!host )(?<!hosts and )(?<!financial )(?<!our )services|(?<!nights and )(?<!guest )experiences|icons|beyond (?:the core|stays|homes|travel)|new businesses|new business lines?|new (?:products?|offerings?|verticals?)|summer release|winter release|rooms|hotels?|hoteltonight|extend(?:ing)? the brand|the airbnb trip|one[- ]stop)\b"),
    ("international", r"\b(international\w*|expansion markets?|global markets?|cross[- ]border|japan|brazil|germany|korea|latin america|latam|asia|apac|europe|emea|india|china|mexico|spain|italy|france|australia|switzerland|netherlands|belgium|argentina|less mature markets?|core markets?|under[- ]penetrated)\b"),
    ("buybacks_sbc", r"\b(buybacks?|repurchases?|repurchased|capital return|return(?:ing)? capital|capital allocation|dividends?|share count|dilution|stock[- ]based comp\w*|sbc|m&a|acquisitions?|balance sheet|cash balance|convertible|net cash)\b"),
    ("competition", r"\b(competit\w*|booking\.com|booking holdings|expedia|vrbo|hotels? (?:industry|chains?|are)|marriott|hilton|hyatt|otas?|online travel agenc\w*|google|share (?:gains?|of travel|of wallet)|market share|disintermediat\w*)\b"),
    ("long_term_targets", r"\b(long[- ]term (?:margin|target|model|algorithm|growth|goal|framework|financial)|multi[- ]year|over the next (?:few|several|three|five) years|by 20(?:2[7-9]|30)|(?:2027|2028|2029|2030)|billions? of dollars? (?:of )?(?:incremental|opportunity|business)|north star|ambition|full[- ]year (?:20\d\d )?(?:margin|revenue|growth|outlook|guidance)|at least (?:mid|low|high)[- ]teens|(?:low|mid|high)[- ](?:single|double)[- ]digits?|(?:low|mid|high)[- ]teens|full year)\b"),
])
THEME_RE = OrderedDict((k, re.compile(v, re.I)) for k, v in THEMES.items())

FWD_VERBS = re.compile(r"\b(will|we'll|we will|expect\w*|anticipat\w*|going to|plan(?:s|ned|ning)? to|intend\w*|aim(?:s|ing)? to|target(?:s|ing)?|forecast\w*|project(?:s|ing|ed)? (?:to|that)|on track|outlook|guid(?:e|ance|ed|ing)|look(?:ing)? (?:ahead|forward)|over the coming|in the (?:coming|next) (?:quarter|year|months|quarters|years)|next (?:quarter|year)|second half|back half|for the (?:full )?year|by year[- ]end|throughout 20\d\d|in 20\d\d)\b", re.I)
NUMBER_TOKEN = re.compile(r"(?<![A-Za-z])(?:\$\s?\d[\d,]*(?:\.\d+)?\s*(?:million|billion|m|b|k)?|\d[\d,]*(?:\.\d+)?\s*(?:%|percent|percentage points?|points?|bps|basis points|million|billion|x\b|times\b)|\d[\d,]*(?:\.\d+)?)(?![A-Za-z-])", re.I)
YEAR_OR_QTR = re.compile(r"^(?:20\d\d|Q[1-4]|[1-4]Q|\d{1,2}(?:st|nd|rd|th)?)$", re.I)
ANALYST_NEG = re.compile(r"\b(concern\w*|worr\w*|slow\w*|decelerat\w*|soft\w*|weak\w*|pressure\w*|risks?|headwinds?|disappoint\w*|miss\w*|below|lower than|light|cautio\w*|push ?back|skeptic\w*|why (?:not|isn't|hasn't|can't|didn't)|what went wrong|competit\w*|deteriorat\w*|declin\w*|cut\w*)\b", re.I)
ANALYST_POS = re.compile(r"\b(congrat\w*|great (?:quarter|results?|job|execution)|nice (?:quarter|job)|impressive|strong|solid|encouraging|good to see|well done|record)\b", re.I)
GUIDE_DECLINE = re.compile(r"\b(?:not (?:going to|gonna) (?:give|provide|guide|quantify|size|share|disclose|break out)|(?:don't|do not|won't|will not) (?:guide|provide guidance|quantify|size|disclose|break out|give (?:a|specific|exact) (?:number|guide|target)|have a (?:specific|new) (?:number|target))|haven't (?:guided|quantified|sized|disclosed)|no (?:new )?(?:long-term )?(?:target|guidance)|not (?:providing|giving|disclosing|quantifying|sizing) (?:a |any |specific |the )?(?:number|guide|guidance|target|detail|breakout|breakdown)|too early to (?:say|tell|quantify|size|call)|not something we(?:'re| are) going to (?:disclose|share|quantify|size|break out))\b", re.I)


def sentences(text):
    text = re.sub(r"\b(U\.S\.|U\.K\.|Inc\.|vs\.|Mr\.|Ms\.|Dr\.|e\.g\.|i\.e\.|No\.)", lambda m: m.group(1).replace(".", "§"), text)
    parts = re.split(r"(?<=[.?!])\s+(?=[A-Z\"'(\[$0-9])", text)
    return [p.replace("§", ".").strip() for p in parts if len(p.split()) >= 3]


WORD = re.compile(r"[a-z][a-z'\-]*")


def lm_counts(text):
    toks = WORD.findall(text.lower())
    n = len(toks)
    pos = neg = unc = weak = 0
    for i, w in enumerate(toks):
        w2 = w.strip("'-")
        if w2 in LM_POS:
            # LM convention: a positive word within three words after a negator is counted as negative
            if any(t in ("not", "no", "never", "n't", "without", "less") for t in toks[max(0, i - 3):i]):
                neg += 1
            else:
                pos += 1
        elif w2 in LM_NEG:
            neg += 1
        if w2 in LM_UNC:
            unc += 1
        if w2 in LM_WEAK:
            weak += 1
    low = text.lower()
    hedge_extra = sum(len(re.findall(r"\b" + re.escape(h) + r"\b", low)) for h in HEDGE_EXTRA)
    return n, pos, neg, unc, weak, hedge_extra


def count_numbers(text):
    n = 0
    for m in NUMBER_TOKEN.finditer(text):
        tok = m.group(0).strip()
        if YEAR_OR_QTR.match(tok):
            continue
        n += 1
    return n


# ----------------------------------------------------------------------------------------------
# Features
# ----------------------------------------------------------------------------------------------
def build(calls, declines_per_q):
    rows, turn_rows = [], []
    for c in calls:
        q = c["quarter"]
        f = OrderedDict(quarter=q, call_date=c["date"], source=c["source"])
        f["analyst_neg_kw"] = 0
        f["analyst_pos_kw"] = 0
        words = Counter()
        exec_words = Counter()
        lm = defaultdict(lambda: [0, 0, 0, 0, 0, 0])
        theme_sent = defaultdict(Counter)
        n_sent = Counter()
        fwd = Counter()
        numbers = Counter()
        analysts = OrderedDict()
        n_analyst_turns = n_questions = 0
        a_neg = a_pos = 0
        a_words = 0
        guide_decl = 0
        mgmt_qa_turns = 0
        for t in c["turns"]:
            txt = t["text"]
            n, pos, neg, unc, weak, hx = lm_counts(txt)
            turn_rows.append({"quarter": q, "section": t["section"], "role": t["role"], "exec": t.get("exec", ""),
                              "speaker": t["speaker"], "firm": norm_firm(t["firm_raw"]) if t["role"] == "analyst" else "",
                              "words": n, "lm_pos": pos, "lm_neg": neg, "lm_unc": unc, "lm_weak_modal": weak,
                              "hedge_extra": hx, "n_numbers": count_numbers(txt), "n_fwd": len(FWD_VERBS.findall(txt)),
                              "text_head": txt[:160]})
            if t["role"] == "mgmt":
                b = "prepared" if t["section"] == "prepared" else "qa"
                words[b] += n
                exec_words[(b, t["exec"])] += n
                for i, v in enumerate((n, pos, neg, unc, weak, hx)):
                    lm[b][i] += v
                ss = sentences(txt)
                n_sent[b] += len(ss)
                for s in ss:
                    for k, rx in THEME_RE.items():
                        if rx.search(s):
                            theme_sent[b][k] += 1
                fwd[b] += len(FWD_VERBS.findall(txt))
                numbers[b] += count_numbers(txt)
                if b == "qa":
                    mgmt_qa_turns += 1
                    guide_decl += len(GUIDE_DECLINE.findall(txt))
            elif t["role"] == "analyst" and t["section"] == "qa":
                n_analyst_turns += 1
                n_questions += txt.count("?")
                analysts.setdefault(t["speaker"], 0)
                analysts[t["speaker"]] += 1
                a_words += n
                a_neg += neg
                a_pos += pos
                a_neg_kw = len(ANALYST_NEG.findall(txt))
                a_pos_kw = len(ANALYST_POS.findall(txt))
                f["analyst_neg_kw"] = f.get("analyst_neg_kw", 0) + a_neg_kw
                f["analyst_pos_kw"] = f.get("analyst_pos_kw", 0) + a_pos_kw
        # lengths
        f["prepared_words"] = words["prepared"]
        f["qa_mgmt_words"] = words["qa"]
        f["analyst_words"] = a_words
        f["qa_share_of_mgmt_words"] = round(words["qa"] / max(1, words["prepared"] + words["qa"]), 3)
        f["n_analysts"] = len(analysts)
        f["n_analyst_turns"] = n_analyst_turns
        f["n_analyst_questions"] = n_questions
        f["n_mgmt_qa_turns"] = mgmt_qa_turns
        # speaker share
        for b in ("prepared", "qa"):
            tot = max(1, words[b])
            f[f"ceo_share_{b}"] = round(exec_words[(b, "ceo")] / tot, 3)
            f[f"cfo_share_{b}"] = round(exec_words[(b, "cfo")] / tot, 3)
        tot = max(1, words["prepared"] + words["qa"])
        f["ceo_share_total"] = round((exec_words[("prepared", "ceo")] + exec_words[("qa", "ceo")]) / tot, 3)
        f["cfo_share_total"] = round((exec_words[("prepared", "cfo")] + exec_words[("qa", "cfo")]) / tot, 3)
        # tone
        for b in ("prepared", "qa"):
            n, pos, neg, unc, weak, hx = lm[b]
            n = max(1, n)
            f[f"lm_net_{b}"] = round(1000 * (pos - neg) / n, 2)
            f[f"lm_pos_{b}_per1k"] = round(1000 * pos / n, 2)
            f[f"lm_neg_{b}_per1k"] = round(1000 * neg / n, 2)
            f[f"lm_unc_{b}_per1k"] = round(1000 * unc / n, 2)
            f[f"hedge_{b}_per1k"] = round(1000 * (unc + weak + hx) / n, 2)
        nP, pP, gP, uP, wP, hP = lm["prepared"]
        nQ, pQ, gQ, uQ, wQ, hQ = lm["qa"]
        f["lm_net_total"] = round(1000 * ((pP + pQ) - (gP + gQ)) / max(1, nP + nQ), 2)
        f["tone_gap_qa_minus_prepared"] = round(f["lm_net_qa"] - f["lm_net_prepared"], 2)
        f["hedge_gap_qa_minus_prepared"] = round(f["hedge_qa_per1k"] - f["hedge_prepared_per1k"], 2)
        f["analyst_lm_net_per1k"] = round(1000 * (a_pos - a_neg) / max(1, a_words), 2)
        f["analyst_neg_kw_per_question"] = round(f.get("analyst_neg_kw", 0) / max(1, n_analyst_turns), 3)
        f["analyst_pos_kw_per_question"] = round(f.get("analyst_pos_kw", 0) / max(1, n_analyst_turns), 3)
        # quantification, forward-looking, declines
        f["n_numbers_prepared"] = numbers["prepared"]
        f["n_numbers_qa"] = numbers["qa"]
        f["numbers_prepared_per1k"] = round(1000 * numbers["prepared"] / max(1, words["prepared"]), 2)
        f["numbers_qa_per1k"] = round(1000 * numbers["qa"] / max(1, words["qa"]), 2)
        f["fwd_prepared_per1k"] = round(1000 * fwd["prepared"] / max(1, words["prepared"]), 2)
        f["fwd_qa_per1k"] = round(1000 * fwd["qa"] / max(1, words["qa"]), 2)
        f["n_guide_decline_phrases_qa"] = guide_decl
        f["n_declines_hand_verified"] = declines_per_q.get(q, 0)
        # themes
        f["n_sentences_prepared"] = n_sent["prepared"]
        f["n_sentences_qa"] = n_sent["qa"]
        for k in THEMES:
            cp, cq = theme_sent["prepared"][k], theme_sent["qa"][k]
            f[f"theme_{k}_n_prepared"] = cp
            f[f"theme_{k}_n_qa"] = cq
            f[f"theme_{k}_share_prepared"] = round(cp / max(1, n_sent["prepared"]), 4)
            f[f"theme_{k}_share_qa"] = round(cq / max(1, n_sent["qa"]), 4)
            f[f"theme_{k}_share_total"] = round((cp + cq) / max(1, n_sent["prepared"] + n_sent["qa"]), 4)
        rows.append(f)
    # changes vs prior call
    prev = None
    for f in rows:
        for k in THEMES:
            col = f"theme_{k}_share_total"
            f[f"d_{col}"] = round(f[col] - prev[col], 4) if prev else ""
        for col in ("lm_net_total", "lm_net_prepared", "lm_net_qa", "hedge_prepared_per1k", "hedge_qa_per1k",
                    "numbers_prepared_per1k", "analyst_lm_net_per1k", "n_analyst_questions", "ceo_share_total"):
            f[f"d_{col}"] = round(f[col] - prev[col], 4) if prev else ""
        prev = f
    return rows, turn_rows


def make_figure(rows):
    """analysis/figures/overnight/03_theme_timeline.png - how the narrative rotated across 23 calls."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    qs = [r["quarter"] for r in rows]
    x = range(len(qs))
    show = [("supply_hosts", "Supply / hosts"), ("new_businesses", "New businesses, Services, Experiences"),
            ("ai", "AI"), ("pricing_adr", "Pricing / ADR / affordability"),
            ("international", "International expansion"), ("demand_macro", "Demand softness / macro"),
            ("take_rate_fees", "Take rate / fees"), ("long_term_targets", "Long-term targets / full-year framing")]
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4))
    for k, lab in show:
        axes[0].plot(x, [100 * r[f"theme_{k}_share_total"] for r in rows], marker="o", ms=3, lw=1.4, label=lab)
    axes[0].set_xticks(list(x)); axes[0].set_xticklabels(qs, rotation=90, fontsize=7)
    axes[0].set_ylabel("share of management sentences, %", fontsize=8)
    axes[0].set_title("Theme share of management sentences, 23 calls", fontsize=9)
    axes[0].legend(fontsize=7, ncol=2); axes[0].tick_params(labelsize=8)
    ax2 = axes[1]
    ax2.bar([i - 0.2 for i in x], [r["prepared_words"] for r in rows], width=0.4, label="prepared-remark words", color="#1f5f8b")
    ax2.bar([i + 0.2 for i in x], [r["qa_mgmt_words"] for r in rows], width=0.4, label="management Q&A words", color="#c98b32")
    ax2.set_xticks(list(x)); ax2.set_xticklabels(qs, rotation=90, fontsize=7)
    ax2b = ax2.twinx()
    ax2b.plot(x, [r["n_analyst_questions"] for r in rows], color="#7a2f4f", marker="s", ms=3, lw=1.4, label="analyst questions")
    ax2b.set_ylabel("analyst questions", fontsize=8, color="#7a2f4f")
    ax2.set_ylabel("words", fontsize=8)
    ax2.set_title("Prepared remarks doubled from 3Q25; analyst questions fell to a record low in 2Q26", fontsize=9)
    ax2.legend(fontsize=7, loc="upper left"); ax2.tick_params(labelsize=8)
    fig.tight_layout()
    out = ROOT / "analysis" / "figures" / "overnight"
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / "03_theme_timeline.png", dpi=150)
    print("wrote", out / "03_theme_timeline.png")


def main():
    calls = load_calls()
    declines = Counter()
    p = ROOT / "data" / "processed" / "abnb_declined_to_quantify.csv"
    if p.exists():
        with open(p, encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                declines[r["quarter"]] += 1
    rows, turn_rows = build(calls, declines)
    keys = list(rows[0].keys())
    with open(OUT / "03_call_features.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader(); w.writerows(rows)
    with open(OUT / "03_call_turns.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(turn_rows[0].keys()))
        w.writeheader(); w.writerows(turn_rows)
    with open(OUT / "03_theme_lexicon.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["theme", "regex"])
        for k, v in THEMES.items():
            w.writerow([k, v])
        w.writerow(["_sentiment", "Loughran-McDonald Positive/Negative word lists (pysentiment2 static/LM.csv), negation within 3 words flips positive to negative"])
        w.writerow(["_hedging", "LM Uncertainty + LM weak-modal words + " + ", ".join(sorted(HEDGE_EXTRA))])
        w.writerow(["_forward_verbs", FWD_VERBS.pattern])
        w.writerow(["_guide_decline", GUIDE_DECLINE.pattern])
        w.writerow(["_analyst_neg_kw", ANALYST_NEG.pattern])
    print(f"wrote {len(rows)} calls, {len(turn_rows)} turns, {len(keys)} feature columns")
    for f in rows:
        print(f"{f['quarter']} {f['source']:4} prep={f['prepared_words']:5} qa={f['qa_mgmt_words']:5} analysts={f['n_analysts']:2} "
              f"q={f['n_analyst_questions']:2} ceo={f['ceo_share_total']:.2f} cfo={f['cfo_share_total']:.2f} "
              f"net_prep={f['lm_net_prepared']:6.1f} net_qa={f['lm_net_qa']:6.1f} hedge_qa={f['hedge_qa_per1k']:5.1f} "
              f"nums={f['n_numbers_prepared']:3} macro={f['theme_demand_macro_share_total']:.3f}")
    make_figure(rows)


if __name__ == "__main__":
    main()
