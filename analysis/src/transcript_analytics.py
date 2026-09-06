"""Transcript analytics on the 23 Airbnb earnings calls (Q4 2020 to Q2 2026).

Inputs (data/raw/transcripts/, gitignored; copy them in before running):
  ir/<q>Q<yy>.txt   Text extracted (pdftotext -layout) from the official FactSet corrected
                    transcripts on the Airbnb IR CDN, Q1 2023 onward:
                    https://s26.q4cdn.com/656283129/files/doc_financials/{yyyy}/q{n}/Airbnb-Q{n}-{yy}-Earnings-Call-Transcript.pdf
                    plus the Q4 2021 corrected transcript:
                    https://s26.q4cdn.com/656283129/files/doc_financials/2021/q4/CORRECTED-TRANSCRIPT-Airbnb,-Inc.(ABNB-US),-Q4-2021-Earnings-Call-15-Feb-22.pdf
                    The PDFs sit next to the .txt files. 15 calls: 4Q21, 1Q23 to 2Q26.
  sa/<q>Q<yy>.txt   Paragraph text saved from https://stockanalysis.com/stocks/abnb/transcripts/
                    for Q4 2020 to Q4 2022 (8 calls). These carry no speaker tags, so speaker
                    attribution inside Q&A is heuristic (see parse_sa). Roster comes from the
                    operator's hand-off lines, which are reliable.

Outputs (data/processed/):
  abnb_call_roster.csv             one row per analyst per call (Q&A only)
  abnb_call_roster_churn.csv       per-call analyst count, firms new and dropped vs prior call,
                                   cumulative firm list; then a block with top firms by appearances
  abnb_call_topics.csv             topic mentions per call, split management prepared remarks /
                                   management Q&A answers / analyst questions, plus per-1,000-word rates
  abnb_declined_to_quantify.csv    hand-verified list of analyst requests for a number that management
                                   declined or answered qualitatively. The rule-based candidate pass is
                                   in candidate_declines(); the kept set is the DECLINED table below,
                                   and every excerpt is checked verbatim against the transcript at build time.

Run: python analysis/src/transcript_analytics.py
     python analysis/src/transcript_analytics.py --candidates   (dump the rule-based decline candidates for review)
"""
import csv
import re
import sys
from collections import Counter, OrderedDict, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "transcripts"
OUT = ROOT / "data" / "processed"

# (quarter label, file stem, source) in call order
CALLS = [
    ("2020Q4", "4Q20", "sa"), ("2021Q1", "1Q21", "sa"), ("2021Q2", "2Q21", "sa"), ("2021Q3", "3Q21", "sa"),
    ("2021Q4", "4Q21", "ir"), ("2022Q1", "1Q22", "sa"), ("2022Q2", "2Q22", "sa"), ("2022Q3", "3Q22", "sa"),
    ("2022Q4", "4Q22", "sa"), ("2023Q1", "1Q23", "ir"), ("2023Q2", "2Q23", "ir"), ("2023Q3", "3Q23", "ir"),
    ("2023Q4", "4Q23", "ir"), ("2024Q1", "1Q24", "ir"), ("2024Q2", "2Q24", "ir"), ("2024Q3", "3Q24", "ir"),
    ("2024Q4", "4Q24", "ir"), ("2025Q1", "1Q25", "ir"), ("2025Q2", "2Q25", "ir"), ("2025Q3", "3Q25", "ir"),
    ("2025Q4", "4Q25", "ir"), ("2026Q1", "1Q26", "ir"), ("2026Q2", "2Q26", "ir"),
]

MGMT_NAMES = {"Brian Chesky", "Ellie Mertz", "David E. Stephenson", "Dave Stephenson", "Ian Lee"}

# ----------------------------------------------------------------------------------------------
# Firm normalisation: any stated form -> one canonical name
# ----------------------------------------------------------------------------------------------
FIRM_MAP = OrderedDict([
    (r"bofa|bank of america", "Bank of America"),
    (r"^td cowen|^cowen", "TD Cowen"),
    (r"citizens|jmp", "Citizens JMP"),
    (r"morgan stanley", "Morgan Stanley"),
    (r"evercore|\bisi\b", "Evercore ISI"),
    (r"j\.?\s?p\.?\s?morgan", "JPMorgan"),
    (r"goldman", "Goldman Sachs"),
    (r"oppenheimer", "Oppenheimer"),
    (r"mizuho", "Mizuho"),
    (r"citi", "Citi"),
    (r"bernstein|sanford", "Bernstein"),
    (r"ubs", "UBS"),
    (r"barclays", "Barclays"),
    (r"jefferies", "Jefferies"),
    (r"deutsche", "Deutsche Bank"),
    (r"wells fargo", "Wells Fargo"),
    (r"keybanc", "KeyBanc"),
    (r"baird", "Baird"),
    (r"melius", "Melius Research"),
    (r"credit suisse", "Credit Suisse"),
    (r"needham", "Needham"),
    (r"b\. riley", "B. Riley"),
    (r"truist", "Truist"),
    (r"wolfe", "Wolfe Research"),
    (r"piper", "Piper Sandler"),
    (r"redburn", "Redburn Atlantic"),
    (r"d\.?\s?a\.? davidson", "D.A. Davidson"),
    (r"bnp", "BNP Paribas"),
    (r"cantor", "Cantor Fitzgerald"),
    (r"canaccord", "Canaccord Genuity"),
    (r"rbc", "RBC Capital Markets"),
    (r"cowen", "TD Cowen"),
])


def norm_firm(raw):
    s = raw.lower()
    for pat, name in FIRM_MAP.items():
        if re.search(pat, s):
            return name
    return raw.strip()


# Analyst-name fixes where transcripts disagree with themselves (surname spelling, nickname)
NAME_FIX = {
    "Richard Clark": "Richard Clarke", "Richard J. Clarke": "Richard Clarke",
    "Eric J. Sheridan": "Eric Sheridan", "Ronald Josey": "Ron Josey", "Nicholas Jones": "Nick Jones",
    "Colin Alan Sebastian": "Colin Sebastian", "Kenneth James Gawrelski": "Ken Gawrelski",
    "Kenneth J. Gawrelski": "Ken Gawrelski", "Dae K. Lee": "Dae Lee", "Thomas Champion": "Tom Champion",
    "Alexander Robert Lyon Brignall": "Alex Brignall", "Jacob Seed": "Jake Seed",
    "Bernard McTernan": "Bernie McTernan",
}


def norm_name(n):
    n = re.sub(r"\s+", " ", n).strip()
    return NAME_FIX.get(n, n)


# ----------------------------------------------------------------------------------------------
# Parsing
# ----------------------------------------------------------------------------------------------
def turn(section, role, speaker, firm, text):
    return {"section": section, "role": role, "speaker": speaker, "firm_raw": firm,
            "text": re.sub(r"\s+", " ", text).strip()}


IR_FURNITURE = re.compile(
    r"^(Airbnb, Inc\. \(ABNB\)|Q[1-4] 20\d\d Earnings Call|1-877-FACTSET|\s*Copyright|\s*Corrected Transcript|\.{10,}|\s*\d{1,2}-[A-Z][a-z]{2}-20\d\d\s*$|\s*Total Pages)"
)
IR_SPEAKER = re.compile(r"^([A-Z][A-Za-z.'\-]+(?: [A-Z][A-Za-z.'\-]+){1,4})\s*(?:\s{3,}([QA]))?\s*$")
IR_TITLE = re.compile(r"(Airbnb, Inc\.\s*$|^Analyst, |Officer|President|Founder)")


def parse_ir(text):
    lines = [l.rstrip() for l in text.splitlines()]
    turns, section, i = [], "front", 0
    date = None
    m = re.search(r"\b(\d{2}-[A-Z][a-z]{2}-20\d\d)\b", text)
    if m:
        date = datetime.strptime(m.group(1), "%d-%b-%Y").date().isoformat()
    cur = None
    buf = []

    def flush():
        nonlocal buf, cur
        if cur is not None and buf:
            turns.append(turn(cur[0], cur[1], cur[2], cur[3], " ".join(buf)))
        buf = []

    while i < len(lines):
        l = lines[i]
        s = l.strip()
        if "MANAGEMENT DISCUSSION SECTION" in s:
            flush(); cur = None; section = "prepared"; i += 1; continue
        if "QUESTION AND ANSWER SECTION" in s:
            flush(); cur = None; section = "qa"; i += 1; continue
        if section == "front" or not s or IR_FURNITURE.match(l):
            i += 1; continue
        if s.startswith("Operator:"):
            flush()
            cur = (section, "operator", "Operator", "")
            buf = [s[len("Operator:"):]]
            i += 1; continue
        sm = IR_SPEAKER.match(l)
        if sm:
            # look ahead to a title line
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and IR_TITLE.search(lines[j].strip()) and not lines[j].strip().endswith("?"):
                flush()
                name, title = sm.group(1).strip(), lines[j].strip()
                if title.startswith("Analyst,"):
                    cur = (section, "analyst", norm_name(name), title[len("Analyst,"):].strip())
                else:
                    cur = (section, "mgmt", name, "Airbnb")
                i = j + 1; continue
        buf.append(s)
        i += 1
    flush()
    return date, turns


SA_INTRO = re.compile(
    r"(?:question|next|move|go|first)\b[^.?]*?\b(?:(?:from|to)\s+(?:the\s+)?(?:line of\s+)?|line of\s+)(?:Mr\.\s+)?"
    r"(?P<name>[A-Z][a-zA-Z.'\-]+(?: [A-Z][a-zA-Z.'\-]+){0,3}?)\s+(?:with|at|from|of)\s+"
    r"(?P<firm>[A-Za-z&'\- .]+?)(?=\.(?:\s+(?:Your|Please|[A-Z]\w+, (?:please|your))|\s*$)|,)"
)
SA_OPERATOR_HINT = re.compile(r"press star|Operator Instructions|conclude|question-and-answer|Q&A roster|compile the roster|remind everyone|hand the call over|turn the call", re.I)
HANDOFF = re.compile(r"^(?:Yeah|Yes|Sure|Okay|All right|Alright)?[,.]?\s*(?:Dave|Brian|Ellie)\b.*\b(?:take|answer|go ahead|want)", re.I)
# Phrases only management uses inside a Q&A block (hand-offs between Chesky and the CFO, thanking the asker)
MGMT_SIG = re.compile(
    r"\b(?:hand (?:it |this )?over to|I'll (?:let|hand|turn)|why don't (?:you|I) (?:take|start|give)|(?:do )?you (?:want|wanna) to take|you can take|"
    r"take the (?:first|second|next|other|last) (?:one|question|part|two)|take (?:these|this one|that one|the question)|I'll take|let me (?:start|take)|"
    r"great question|good question|thanks? for the question|thank you for the question|thanks for asking|"
    r"\b(?:Dave|Brian|Ellie)\b[^.?]{0,60}\b(?:take|answer|hand|go ahead|jump in|add|start|elaborate|round out|handle|cover|feel free))", re.I)


def parse_sa(text):
    paras = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    date = None
    m = re.match(r"([A-Z][a-z]{2}) (\d{1,2}), (20\d\d)", paras[0])
    if m:
        date = datetime.strptime(paras[0].split("\n")[0].strip()[:12].strip(), "%b %d, %Y").date().isoformat()
    paras = [p for p in paras if len(p) > 40]
    turns = []
    section = "prepared"
    block = []  # analyst Q&A block paragraphs after an operator intro
    analyst = None

    def flush_block():
        nonlocal block
        if analyst is None:
            block = []
            return
        first = analyst[0].split()[0]
        prev = "analyst"
        for k, p in enumerate(block):
            addressed = re.match(r"^(?:\w+[,.!]?\s+){0,4}" + re.escape(first) + r"\b", p) is not None
            mg = MGMT_SIG.search(p) is not None or addressed
            clean = re.sub(r"\byou know\b", "", p, flags=re.I)
            n_you = len(re.findall(r"\b(?:you|your|you're|you've|you'd|yours|you guys|guys)\b", clean, re.I))
            n_we = len(re.findall(r"\b(?:we|we're|we've|we'd|we'll|our|ours|us)\b", clean, re.I))
            if k == 0:
                role = "analyst"
            elif mg:
                role = "mgmt"
            elif n_you > n_we:
                role = "analyst"
            elif n_we > n_you:
                role = "mgmt"
            elif p.endswith("?") and len(p) < 1200:
                role = "analyst"
            elif len(p) < 140 and re.search(r"thank|great|got it|okay|perfect|appreciate|helpful", p, re.I):
                mt = re.match(r"^(?:Thanks?|Thank you)[,]? (\w+)\.?$", p)
                if mt and mt.group(1) not in ("Brian", "Dave", "Ellie", "guys", "both", "all"):
                    role = "mgmt"
                elif re.match(r"^(?:Okay|Yeah|Yes|Sure)[,.]? (?:thank you|thanks)\.? (?:Hi|Hey|So|Well)", p, re.I):
                    role = "mgmt"
                else:
                    role = "analyst"
            else:
                role = "mgmt"
            if role == "analyst":
                turns.append(turn("qa", "analyst", analyst[0], analyst[1], p))
            else:
                turns.append(turn("qa", "mgmt", "Management", "Airbnb", p))
            prev = role
        block = []

    for idx, p in enumerate(paras):
        im = SA_INTRO.search(p) if (len(p) < 700 and (SA_OPERATOR_HINT.search(p) or re.search(r"question|next|move|go", p))) else None
        is_operator = bool(im) or (len(p) < 500 and SA_OPERATOR_HINT.search(p) and idx < 3) or bool(re.search(r"conclude(s)? (today's|the) (question|conference|call)", p, re.I))
        if im:
            flush_block()
            section = "qa"
            analyst = (norm_name(im.group("name")), im.group("firm").strip())
            # operator text preceding the intro may hold a prepared-remarks tail; ignore
            turns.append(turn("qa", "operator", "Operator", "", p))
            continue
        if is_operator:
            flush_block()
            turns.append(turn(section, "operator", "Operator", "", p))
            continue
        if section == "prepared":
            if idx < 3 or re.search(r"forward-looking statements|non-GAAP", p):
                turns.append(turn("prepared", "ir", "IR", "Airbnb", p))
            else:
                turns.append(turn("prepared", "mgmt", "Management", "Airbnb", p))
        else:
            block.append(p)
    flush_block()
    return date, turns


def load_calls():
    calls = []
    for q, stem, src in CALLS:
        path = RAW / src / f"{stem}.txt"
        text = path.read_text(encoding="utf-8", errors="replace")
        date, turns = (parse_ir if src == "ir" else parse_sa)(text)
        # drop safe-harbour boilerplate from management prepared remarks
        for t in turns:
            if t["section"] == "prepared" and t["role"] == "mgmt" and re.search(r"forward-looking statements|non-GAAP financial measures", t["text"]):
                t["role"] = "ir"
        calls.append({"quarter": q, "stem": stem, "source": src, "date": date, "turns": turns})
    return calls


# ----------------------------------------------------------------------------------------------
# Roster and churn
# ----------------------------------------------------------------------------------------------
def build_roster(calls):
    rows = []
    for c in calls:
        order, seen = 0, OrderedDict()
        for t in c["turns"]:
            if t["section"] != "qa" or t["role"] != "analyst":
                continue
            key = t["speaker"]
            if key not in seen:
                order += 1
                seen[key] = {"quarter": c["quarter"], "call_date": c["date"], "source": c["source"],
                             "analyst": key, "firm_as_stated": t["firm_raw"], "firm": norm_firm(t["firm_raw"]),
                             "order_asked": order, "n_turns": 0, "n_questions": 0}
            seen[key]["n_turns"] += 1
            seen[key]["n_questions"] += t["text"].count("?")
        rows.extend(seen.values())
    return rows


def build_churn(roster):
    by_q = defaultdict(list)
    for r in roster:
        by_q[r["quarter"]].append(r)
    prev, cum = None, OrderedDict()
    rows = []
    for q, _, src in CALLS:
        firms = OrderedDict((r["firm"], None) for r in by_q[q])
        fs = set(firms)
        new = [f for f in firms if prev is not None and f not in prev]
        dropped = [f for f in prev if f not in fs] if prev is not None else []
        never_before = [f for f in firms if f not in cum]
        for f in firms:
            cum.setdefault(f, q)
        rows.append({"quarter": q, "call_date": by_q[q][0]["call_date"] if by_q[q] else "", "source": src,
                     "n_analysts": len(by_q[q]), "n_firms": len(fs),
                     "n_questions": sum(r["n_questions"] for r in by_q[q]),
                     "new_vs_prior_call": "; ".join(new), "dropped_vs_prior_call": "; ".join(dropped),
                     "first_ever_appearance": "; ".join(never_before),
                     "cumulative_firms": len(cum), "cumulative_firm_list": "; ".join(cum)})
        prev = fs
    appearances = Counter(r["firm"] for r in roster)
    first = {}
    last = {}
    for r in roster:
        first.setdefault(r["firm"], r["quarter"])
        last[r["firm"]] = r["quarter"]
    top = [{"firm": f, "appearances": n, "first_call": first[f], "last_call": last[f],
            "analysts": "; ".join(sorted({r["analyst"] for r in roster if r["firm"] == f}))}
           for f, n in appearances.most_common()]
    return rows, top


# ----------------------------------------------------------------------------------------------
# Topics
# ----------------------------------------------------------------------------------------------
TOPICS = OrderedDict([
    ("margin_ebitda", r"\b(margins?|ebitda|profitab\w+|operating leverage|free cash flow|fcf)\b"),
    ("take_rate_fees", r"\b(take[- ]rates?|service fees?|host[- ]only fee|guest fees?|host fees?|monetiz\w+|fee structure|cross[- ]currency fee|fx fee)\b"),
    ("adr_pricing", r"\b(adrs?|average daily rates?|pricing|prices?|affordab\w+|discount\w*|total price|price display|cleaning fees?)\b"),
    ("nights_demand", r"\b(nights?|demand|bookings?|gross booking value|gbv|booked|lead times?|booking window|length of stay|room nights?|seats?)\b"),
    ("supply_hosts", r"\b(supply|hosts?|hosting|listings?|co-host\w*|superhost\w*|active listings?)\b"),
    ("marketing", r"\b(marketing|brand campaign|brand spend|performance marketing|advertis\w+|paid search|sem|search engine|brand awareness)\b"),
    ("ai", r"\b(ai|artificial intelligence|generative|llms?|agentic|machine learning|chatgpt|openai|large language|ai[- ]native|ai agents?|copilot|gpt)\b"),
    ("international_expansion", r"\b(international|expansion markets?|global markets?|cross[- ]border|japan|brazil|germany|korea|latin america|latam|asia|apac|europe|emea|india|china|mexico|spain|italy|france|australia|switzerland|netherlands|belgium|argentina|colombia|chile)\b"),
    ("services_experiences", r"\b((?<!customer )(?<!guest )(?<!community )(?<!host )(?<!hosts and )services|(?<!nights and )(?<!guest )experiences|icons|beyond (?:the core|stays|homes)|new businesses|new business lines?|extend(?:ing)? the brand|summer release|may release|originals)\b"),
    ("hotels", r"\b(hotels?|hoteltonight|boutique|hoteliers?)\b"),
    ("regulation", r"\b(regulat\w+|regulators?|new york|nyc|local law|legislat\w+|ordinances?|registration|barcelona|bans?|banned|short[- ]term rental (?:rules|laws?|restrictions?)|policymakers?|lawmakers?)\b"),
    ("buyback_capital", r"\b(buybacks?|repurchases?|repurchased|capital return|return(?:ing)? capital|capital allocation|dividends?|m&a|acquisitions?|balance sheet|cash balance|share count|dilution)\b"),
    ("fx", r"\b(fx|foreign exchange|currency|currencies|(?:strong|weak|strengthening|weakening|us) dollar|euro|hedg\w+|constant currency|ex[- ]fx)\b"),
    ("guidance", r"\b(guidance|guide|guided|guiding|outlook|consensus|the street|street estimates?|expectations|implied|full[- ]year (?:margin|revenue|growth)|low end|high end)\b"),
])
TOPIC_RE = OrderedDict((k, re.compile(v, re.I)) for k, v in TOPICS.items())


def bucket(t):
    if t["role"] == "analyst":
        return "analyst"
    if t["role"] == "mgmt":
        return "mgmt_prepared" if t["section"] == "prepared" else "mgmt_qa"
    return None


def build_topics(calls):
    rows = []
    for c in calls:
        words = Counter()
        counts = defaultdict(Counter)
        for t in c["turns"]:
            b = bucket(t)
            if not b:
                continue
            words[b] += len(t["text"].split())
            for k, rx in TOPIC_RE.items():
                counts[k][b] += len(rx.findall(t["text"]))
        for k in TOPICS:
            r = {"quarter": c["quarter"], "call_date": c["date"], "source": c["source"], "topic": k}
            for b in ("mgmt_prepared", "mgmt_qa", "analyst"):
                r[f"{b}_mentions"] = counts[k][b]
                r[f"{b}_words"] = words[b]
                r[f"{b}_per_1k_words"] = round(1000 * counts[k][b] / words[b], 2) if words[b] else 0
            rows.append(r)
    return rows


# ----------------------------------------------------------------------------------------------
# Declined to quantify
# ----------------------------------------------------------------------------------------------
QUANT_ASK = re.compile(
    r"how much|how many|quantif\w*|\bsiz(?:e|ing)\b|what percent\w*|what kind of percent|how big|how large|how material|how meaningful|how significant|"
    r"give us a (?:number|sense|feel|range|framework)|any (?:way|color|colour|sense|number|numbers|metrics?|data|detail|specifics?|framework|help) (?:to|on|around|of|in) (?:siz|quantif|the (?:size|magnitude|number|impact|contribution|mix|share|percent|economics|margin|profitab|take rate|dollar|spend|headcount|ADR|penetration|attach|payback))|"
    r"magnitude|basis points|\bbps\b|contribution (?:margin|profit)|order of magnitude|what portion|what share|what fraction|what(?:'s| is) the mix|mix of|penetration|attach rate|"
    r"dollar|\bpercent(?:age)? of\b|unit economics|how profitable|payback|break[- ]?even|dilut\w+|accretive|"
    r"how should we think about the (?:margin|profitability|economics|contribution|take rate|spend|investment|dollars|size)|"
    r"(?:margin|economics|profitability|profit|take rate|monetization) (?:of|on|for|from|in) (?:the |these |those |your |that )?(?:hotel|experience|service|new|expansion|international|emerging|these|co-host|rooms|long-term|icons|business)|"
    r"long[- ]term (?:margin|target|model|EBITDA|profitab)|margin target|target margin|"
    r"headcount|hiring|capex|capital expenditure|spend(?:ing)? on AI|AI (?:spend|investment|cost|capex)|cost of (?:AI|compute)|"
    r"break (?:out|down)|breakdown|split (?:out|between)|disclose|guidance (?:embed|assume|include|contemplate|bake)|(?:embedded|baked|assumed) in (?:the )?guid|"
    r"what(?:'s| is) (?:the |your )?(?:take rate|ADR|share|number|revenue|GBV|EBITDA|margin|run[- ]rate|growth rate|impact)|"
    r"(?:the |an )?impact (?:on|to|of) (?:margin|EBITDA|revenue|take rate|ADR|nights|GBV|growth)|"
    r"head ?count|implying|implied|what(?:'s| is) (?:embedded|baked|assumed)|budget|run[- ]rate|"
    r"(?:color|colour|details?) on (?:the |your )?(?:take rate|margins?|ADR|mix|growth|spend|investment|guidance|guide|outlook|economics|contribution|number)|"
    r"how (?:are|should|do) (?:we|you) think(?:ing)? about (?:the )?(?:size|spend|investment|margin|take rate|contribution|economics|dollars|budget)", re.I)

DECLINE_HINT = re.compile(
    r"not (?:going to|gonna) (?:give|share|disclose|quantify|size|break|get into|provide|put|guide)|don't (?:break|disclose|share|provide|give|have a)|"
    r"haven't (?:disclosed|shared|broken|sized)|won't (?:be )?(?:disclos|shar|break|quantif|siz|giv)|not (?:disclos|shar|break|quantif|siz|provid)ing|"
    r"too early|premature|not something we|we don't (?:typically|generally|really) (?:disclose|share|break|talk|give|provide|guide)|"
    r"we're not disclosing|not going to get into|not going to (?:go|put) (?:into|a number)|no (?:new )?(?:long-term )?target|"
    r"don't have a (?:new|specific|long-term)|not ready to|we'll share more|later this year|in due course|at this (?:point|time)|stay tuned|"
    r"directionally|qualitative|high level|not in (?:the )?(?:business|habit) of|rather not|prefer not|I'm not going to", re.I)


def qa_pairs(calls):
    """Yield (call, analyst_turn, [mgmt turns until next analyst/operator turn])."""
    for c in calls:
        ts = [t for t in c["turns"] if t["section"] == "qa"]
        for i, t in enumerate(ts):
            if t["role"] != "analyst":
                continue
            ans = []
            for u in ts[i + 1:]:
                if u["role"] != "mgmt":
                    break
                ans.append(u)
            yield c, t, ans


def candidate_declines(calls):
    for c, q, ans in qa_pairs(calls):
        if not QUANT_ASK.search(q["text"]) or not ans:
            continue
        atext = " ".join(a["text"] for a in ans)
        yield {"quarter": c["quarter"], "analyst": q["speaker"], "firm": norm_firm(q["firm_raw"]),
               "question": q["text"], "answer": atext, "speakers": "; ".join(dict.fromkeys(a["speaker"] for a in ans)),
               "hint": bool(DECLINE_HINT.search(atext))}


# Hand-verified declines (rule-based candidates from candidate_declines() plus a manual sweep of the
# margin, take-rate, new-business, AI-spend and guidance questions, all 23 calls, read by hand).
# Each excerpt must appear verbatim (whitespace-normalised) in a turn that follows the named analyst's
# question on that call, before the operator's next hand-off; the build fails otherwise.
# Tuple: (quarter, analyst surname, what was asked, verbatim excerpt <= 300 chars, category[, speaker])
# The optional speaker is used for the 2020 to 2022 web transcripts, where turns are untagged and the
# speaker is inferred from the hand-off ("Dave, do you want to take this?").
# Categories: contribution margin of new businesses | take rate detail | market-level economics |
#             long-term margin target | headcount | capex/AI spend | consensus/guidance detail | other
DECLINED = [
    ("2020Q4", "Post", "Margin target for 2021 to model against",
     "I'd love to give you specific targets for 2021, but it's just too hard to know what our revenue is going to be, and so therefore, kind of the flow through to profitability.",
     "consensus/guidance detail", "Dave Stephenson (inferred)"),
    ("2021Q2", "Fitzgerald", "How much of their calendar new hosts make available; professional vs casual mix",
     "We continue to see 90% of our hosts are individual hosts. That remains to be the case.",
     "other", "Dave Stephenson (inferred)"),
    ("2021Q3", "Kopelman", "Q4-to-date booking growth versus 2019",
     "I don't have a specific percentage that we're sharing on the call today.",
     "consensus/guidance detail", "Dave Stephenson (inferred)"),
    ("2021Q3", "Ju", "Share of users with young unvaccinated children, to size pent-up demand",
     "I don't think we have that data specifically, but I can just share a couple high-level thoughts with you.",
     "other", "Brian Chesky (inferred)"),
    ("2021Q3", "Mahaney", "How significant the APAC short-term-rental restrictions are as a drag",
     "we're not anticipating that any short-term rental regulation changes as being a major negative drag on our business over time.",
     "other", "Dave Stephenson (inferred)"),
    ("2021Q4", "Mahaney", "Size of the long-term-stay effect on ADR (accretive or dilutive, by how much)",
     "On the ADR, long-term stays are dilutive on the ADR as the percentage goes up",
     "other", "David E. Stephenson"),
    ("2022Q2", "Lu", "How large China outbound bookings are",
     "We focused all that on outbound, which we think is the greater prize and the most important part for the long term.",
     "market-level economics", "Dave Stephenson (inferred)"),
    ("2022Q2", "Colantuoni", "Puts and takes behind the higher implied Q3 take rate",
     "The underlying kind of if you shifted take rate is unchanged. You know, any of the variation in take rate is just a timing difference between revenue stays versus timing of bookings.",
     "take rate detail", "Dave Stephenson (inferred)"),
    ("2022Q2", "Kopelman", "Listings growth rate excluding the China domestic shutdown",
     "what we've stated is that we're still well above 6 million active listings, even excluding the takedown of the China domestic.",
     "other", "Dave Stephenson (inferred)"),
    ("2022Q3", "Khan", "ROI on advertising dollars",
     "Our brand marketing results are delivering excellent results overall with a strong rate of return, and it's been so successful that we're actually expanding to more countries",
     "other", "Dave Stephenson (inferred)"),
    ("2022Q3", "Post", "Confirm the operational take rate is above 14% and stable",
     "We do not have an intention to increase take rate.",
     "take rate detail", "Brian Chesky (inferred)"),
    ("2022Q3", "Clarke", "Quantify the ADR headwind as urban mix returns",
     "Urban is strengthening each quarter. That's the trend that we're seeing on the urban side.",
     "other", "Dave Stephenson (inferred)"),
    ("2022Q4", "Nowak", "New-guest growth in 2022 and 2023; adoption metrics for I'm Flexible (a KPI disclosed in 2021 and dropped)",
     "on the new guests, we don't disclose the exact number of the, you know, new guest growth.",
     "other", "Dave Stephenson (inferred)"),
    ("2022Q4", "Lu", "Breakdown of the 900,000 listings added: new versus reactivated",
     "I don't have any other more specific breakout to give to you.",
     "other", "Dave Stephenson (inferred)"),
    ("2022Q4", "Ju", "Aggregate host availability growth versus host-count growth",
     "What we noticed is over time, hosts generally increase the number of days available, and they tend to get more productive every year.",
     "other", "Brian Chesky (inferred)"),
    ("2022Q4", "McTernan", "FX drag on 2022 EBITDA margin",
     "Maybe we can follow up offline on that. I mean, it was a material, you know, probably several hundred million dollars, but we would have to give you the... Maybe we'll work offline on the specific calculation.",
     "other", "Dave Stephenson (inferred)"),
    ("2023Q1", "Lu", "Percent of listings exclusive to Airbnb (not addressed; answer covered loyalty only)",
     "I always believe that the best loyalty program is people loving your product and if they love your products, they come back.",
     "other"),
    ("2023Q2", "Champion", "Long-term EBITDA margin potential",
     "But all of that said, I don't have a new long-term target. I'm just proud of the fact that we've been able to deliver the profitability we have as quickly as we have.",
     "long-term margin target"),
    ("2023Q3", "Nowak", "Confirm the Q4 nights-growth range implied by the guide",
     "In terms of the nights guide, we're just seeing some variability in our nights demand here early in the quarter. And so, we're just being cautious with that guide. And so, we're not being specific on it",
     "consensus/guidance detail"),
    ("2024Q1", "Jones", "Share of supply removed for quality and how many hosts return",
     "I don't have the stats on the top of my head",
     "other"),
    ("2024Q1", "Cunningham", "Take rate, ADR and profit of expansion markets versus the core",
     "what we've been able to achieve over time is very strong economics at the booking level for a wide range of ADRs. So it is not a concern for us to be expanding in markets where the average ADRs are lower.",
     "market-level economics"),
    ("2024Q2", "Patterson", "How long the investment cycle lasts and when returns show (2025 margin)",
     "we obviously have not given a guide for 2025. We'll provide you a view on 2025 as it approaches.",
     "consensus/guidance detail"),
    ("2024Q3", "Colantuoni", "Size of the tech and marketing investment behind the Experiences relaunch",
     "I do not anticipate very many businesses in the next five years are going to need significant investments.",
     "contribution margin of new businesses"),
    ("2025Q1", "Kopelman", "Geo mix versus underlying softness in the Q2 ADR guide, and the FX assumption",
     "One is there is underlying real price appreciation, which is a tailwind in terms of bringing prices up. There is a movement in terms of the FX headwinds.",
     "consensus/guidance detail"),
    ("2025Q1", "White", "Profitability of expansion markets relative to core markets, level and pace",
     "we're able to generate very attractive contribution profit at a variety of ADRs, and that typically is the biggest determinant on the overall level of profitability at a market level",
     "market-level economics"),
    ("2025Q1", "Josey", "Contribution of the May 13 launches included in guidance",
     "the impact from a top line in the current quarter will be relatively modest, whereas as we scale those offerings, they will obviously increasingly contribute to the top line.",
     "consensus/guidance detail"),
    ("2025Q2", "Mahaney", "Target attach rate for Experiences",
     "We don't have any numbers to share as far as what we see for potential attach rate.",
     "contribution margin of new businesses"),
    ("2025Q2", "Young", "Share of Nights and Seats Booked that is seats (1% or zero?)",
     "we have not historically broken out nights booked versus experiences booked. We were not going to do that today. What I can tell you is that the seats booked today are indeed immaterial.",
     "contribution margin of new businesses"),
    ("2025Q2", "Kopelman", "How 2026 margins will be managed given new launches",
     "On margins, I'm not going to guide right now to 2026.",
     "consensus/guidance detail"),
    ("2025Q3", "Clarke", "Percent of the US acceleration that came from Reserve Now, Pay Later",
     "So about 70% of people that we offer Reserve Now, Pay Later, take us up on that offering.",
     "other"),
    ("2025Q3", "Horowitz", "2026 incremental investment plan; how much of the $200M is sticky",
     "Obviously we're not providing explicit guidance for 2026 margins today.",
     "consensus/guidance detail"),
    ("2025Q3", "Post", "Whether experiences contribute yet and the expected contribution next year",
     "The first thing we're seeing is that a large percentage of people that are booking experiences, about half don't have an Airbnb stay associated with the reservation.",
     "contribution margin of new businesses"),
    ("2025Q4", "Nowak", "P&L (gross margin) impact of increased AI investment in 2026 versus 2025",
     "So unlike other companies, we're not building models. We do not have a huge CapEx cost base. So our investment in AI will not affect the P&L. I don't think you'll see it in the P&L.",
     "capex/AI spend"),
    ("2026Q2", "Sheridan", "Long-term incremental margins and how much gets reinvested versus dropping through",
     "So I'm not going to give you a specific guide for 2027 and beyond, but I think looking at our track record, you can even see a couple of things.",
     "long-term margin target"),
    ("2026Q2", "Walmsley", "Timeframe or scale of the hotels opportunity",
     "hotels are only a single- digit percent of nights booked on the platform, so a relatively small segment.",
     "contribution margin of new businesses"),
    ("2026Q2", "Sebastian", "Unit economics of the new service categories relative to expectations",
     "car rentals is going to be the biggest one by far just because of how big the asset is",
     "contribution margin of new businesses"),
    ("2026Q2", "Colantuoni", "Impact of the AI-native transition on product costs",
     "the inference cost of Airbnb are kind of de minimis relative to the ROI of our business model",
     "capex/AI spend"),
]


def find_excerpt(calls, quarter, surname, excerpt):
    """Locate the excerpt in any turn after the analyst's first question, before the next operator hand-off."""
    ex_norm = re.sub(r"\s+", " ", excerpt).strip()
    for c in calls:
        if c["quarter"] != quarter:
            continue
        ts = [t for t in c["turns"] if t["section"] == "qa"]
        for i, t in enumerate(ts):
            if t["role"] != "analyst" or surname.lower() not in t["speaker"].lower():
                continue
            for u in ts[i + 1:]:
                if u["role"] == "operator":
                    break
                if ex_norm in u["text"]:
                    return t, u
    return None, None


def build_declined(calls):
    rows = []
    for item in DECLINED:
        quarter, surname, asked, excerpt, category = item[:5]
        speaker_override = item[5] if len(item) > 5 else None
        q, a = find_excerpt(calls, quarter, surname, excerpt)
        if q is None:
            sys.exit(f"DECLINED excerpt not found verbatim: {quarter} {surname}: {excerpt[:60]}...")
        if len(excerpt) > 300:
            sys.exit(f"DECLINED excerpt over 300 chars: {quarter} {surname}")
        speaker = speaker_override or (a["speaker"] if a["speaker"] != "Management" else "Management (untagged web transcript)")
        rows.append({"quarter": quarter, "analyst": q["speaker"], "firm": norm_firm(q["firm_raw"]),
                     "asked": asked, "management_answer_excerpt": excerpt, "speaker": speaker,
                     "category": category})
    return rows


# ----------------------------------------------------------------------------------------------
def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path.relative_to(ROOT)} ({len(rows)} rows)")


def main():
    calls = load_calls()
    if "--candidates" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--candidates") + 1]) if len(sys.argv) > sys.argv.index("--candidates") + 1 else RAW / "_decline_candidates.txt"
        n = 0
        with open(out, "w", encoding="utf-8") as f:
            for cand in candidate_declines(calls):
                n += 1
                f.write(f"### {n} | {cand['quarter']} | {cand['analyst']} ({cand['firm']}) | A: {cand['speakers']} | hint={cand['hint']}\n")
                f.write("Q: " + cand["question"][:900] + "\n")
                f.write("A: " + cand["answer"][:1400] + "\n\n")
        print(f"{n} candidates -> {out}")
        return
    if "--dump" in sys.argv:
        for c in calls:
            print(f"\n===== {c['quarter']} {c['date']} {c['source']}")
            for t in c["turns"]:
                print(f"[{t['section']}/{t['role']}] {t['speaker']} | {t['firm_raw']} | {t['text'][:110]}")
        return
    roster = build_roster(calls)
    write_csv(OUT / "abnb_call_roster.csv", roster)
    churn, top = build_churn(roster)
    path = OUT / "abnb_call_roster_churn.csv"
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(churn[0].keys()))
        w.writeheader(); w.writerows(churn)
        f.write("\n# top firms by appearances (23 calls)\n")
        w2 = csv.DictWriter(f, fieldnames=list(top[0].keys()))
        w2.writeheader(); w2.writerows(top)
    print(f"wrote {path.relative_to(ROOT)} ({len(churn)} calls + {len(top)} firms)")
    write_csv(OUT / "abnb_call_topics.csv", build_topics(calls))
    declined = build_declined(calls)
    if declined:
        write_csv(OUT / "abnb_declined_to_quantify.csv", declined)


if __name__ == "__main__":
    main()
