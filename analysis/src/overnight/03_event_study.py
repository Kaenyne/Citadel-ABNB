"""Workstream 03: event study of the five best and five worst ABNB earnings reactions.

For each of the ten prints: the sentence management actually said (verbatim, <= 30 words) that carried the
driver the press led with, plus the call-language features from 03_call_features.csv for that print, plus a
driver classification.

Reads
  data/processed/abnb_earnings_reactions.csv            1/5/20-session excess returns vs QQQ
  data/processed/abnb_major_moves_events.csv            same-day press attribution for every move >= 7%
                                                        (compiled from CNBC / Reuters / Skift / Seeking Alpha
                                                        same-day coverage; see research/notes/2026-09-05_abnb-major-moves.md)
  data/processed/overnight/03_call_features.csv         language features for the same print
  transcripts and letters, via 03_call_features.load_calls() and data/raw/letters/*.htm, to verify each quote

Writes
  data/processed/overnight/03_event_study.csv
  analysis/figures/overnight/03_event_study.png

Press caveat: this session's WebSearch budget was exhausted by other overnight workstreams before this step,
and Reuters/CNBC are not fetchable from this environment. The press attribution column is therefore taken from
`abnb_major_moves_events.csv` / `research/notes/2026-09-05_abnb-major-moves.md`, which was itself built from
same-day coverage on 5 Sep 2026, rather than re-fetched here. The quotes are primary-source and verified.

Run: py -3.13 analysis/src/overnight/03_event_study.py
"""
import csv
import html
import importlib.util
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "processed" / "overnight"
FIG = ROOT / "analysis" / "figures" / "overnight"
FIG.mkdir(parents=True, exist_ok=True)
LETTERS = ROOT / "data" / "raw" / "letters"

_spec = importlib.util.spec_from_file_location("cf03e", Path(__file__).with_name("03_call_features.py"))
cf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cf)

# quarter, rank, source_of_quote, speaker, quote (verbatim, <=30 words), driver class, press-cited driver
EVENTS = [
 # ---------------- five best day-1 excess reactions ----------------
 ("2026Q2", "best", "letter", "shareholder letter",
  "we now expect year-over-year revenue growth to improve to at least mid teens, supported by the accelerated pace of Nights and Seats Booked we've observed",
  "guide",
  "Beat on every KPI and a second consecutive raise to the FY26 revenue and margin guide; nights accelerating to +10%, GBV +16%, EBITDA margin guide to at least 35.5%."),
 ("2024Q4", "best", "letter", "shareholder letter",
  "Q4 was our highest nights and bookings growth quarter of 2024 and we are excited by the continued strong demand we are seeing in 2025.",
  "KPI",
  "Nights 111.0m (+12%) vs 108.7m expected; EPS $0.73 vs $0.58. The Q1 revenue guide of $2.23-2.27bn was below the Street and was ignored. Best day on record."),
 ("2021Q3", "best", "letter", "shareholder letter",
  "looking forward to a strong Q4 with accelerating GBV growth, continued revenue strength, and further Adjusted EBITDA margin expansion, compared to Q3 2021",
  "guide",
  "Record quarter: revenue $2.24bn (+67%), net income $834m, adj. EBITDA $1.1bn (49% margin), plus an accelerating Q4 GBV guide. Expedia rose 15.6% the same day on its own beat."),
 ("2020Q4", "best", "call_qa", "Dave Stephenson",
  "And what we would expect to achieve over time is 30% EBITDA margins or greater.",
  "margin",
  "First print as a public company. Revenue $859m (-22%) beat ~$748m; recovery narrative. The 30% margin ambition was the first long-term financial framework the company had given."),
 ("2022Q4", "best", "letter", "shareholder letter",
  "We expect revenue of $1.75 billion to $1.82 billion in Q1 2023. This represents year-over-year growth of between 16% and 21%",
  "guide",
  "First profitable full year (net income $1.9bn, FCF $3.4bn) and a Q1 guide of $1.75-1.82bn against a $1.68bn Street. Nights 88.2m came in slightly light and was ignored."),
 # ---------------- five worst day-1 excess reactions ----------------
 ("2024Q2", "worst", "letter", "shareholder letter",
  "However, we are seeing shorter booking lead times globally and some signs of slowing demand from U.S. guests.",
  "macro",
  "EPS $0.86 vs $0.92; nights +9%. The lead-time and US-demand sentence in the outlook, not the reported quarter, drove the fall. Worst reaction since the IPO at the time."),
 ("2023Q1", "worst", "letter", "shareholder letter",
  "We expect year-over-year growth in Nights and Experiences Booked in Q2 2023 to be lower than our revenue growth during the quarter.",
  "KPI",
  "Revenue +20% and the first GAAP-profitable Q1, but the Q2 nights guide sat below the revenue guide for the first time. Read as the end of the volume recovery."),
 ("2022Q3", "worst", "letter", "shareholder letter",
  "On a year-over-year basis, we expect Nights and Experiences Booked growth will moderate slightly relative to Q3 2022",
  "KPI",
  "Beat on revenue ($2.88bn, +29%) and a 51% EBITDA margin, but Q4 nights guided to moderate from +25% and ADR guided flat. The Fed hiked 75bp the same day (QQQ -3.4%)."),
 ("2024Q3", "worst", "call_qa", "Ellie Mertz",
  "Obviously, the guide does imply several point margin compression relative to last Q4. You should see that most specifically in terms of both the product development line item as well as marketing.",
  "investment spend",
  "Revenue beat but EPS $2.13 vs $2.17; S&M +27.5% and product development +25% year over year; Q4 EBITDA margin guided down. The market re-rated the cost base, not the demand."),
 ("2025Q2", "worst", "letter", "shareholder letter",
  "we expect a tougher year-over-year comparison toward the end of the quarter. This dynamic will continue into Q4, putting pressure on growth rates later in the year.",
  "macro",
  "Beat on revenue, EPS and nights, but the 2H caution plus $200-250m of Services/Experiences investment weighing on margin. Nights growth then accelerated in Q3 and Q4 2025."),
]

FEATS = ["prepared_words", "qa_mgmt_words", "n_analyst_questions", "n_analysts", "ceo_share_total",
         "lm_net_prepared", "lm_net_qa", "tone_gap_qa_minus_prepared", "hedge_qa_per1k",
         "n_numbers_prepared", "n_guide_decline_phrases_qa", "analyst_lm_net_per1k",
         "theme_long_term_targets_share_prepared", "theme_international_share_total",
         "theme_demand_macro_share_total", "theme_margins_profitability_share_total"]


def squash(s):
    s = html.unescape(s).replace("’", "'").replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main():
    rx = pd.read_csv(ROOT / "data" / "processed" / "abnb_earnings_reactions.csv").set_index("quarter")
    ft = pd.read_csv(OUT / "03_call_features.csv").set_index("quarter")
    calls = {c["quarter"]: c for c in cf.load_calls()}
    call_text = {q: squash(" ".join(t["text"] for t in c["turns"])) for q, c in calls.items()}
    letter_text = {}
    for p in sorted(LETTERS.glob("*.htm")):
        stem = p.name.split("_")[0]
        letter_text[f"20{stem[2:]}Q{stem[0]}"] = squash(re.sub(r"<[^>]+>", " ", p.read_text(encoding="utf-8", errors="replace")))

    rows = []
    for q, side, src, spk, quote, driver, press in EVENTS:
        hay = letter_text[q] if src == "letter" else call_text[q]
        ok = squash(quote) in hay
        r = rx.loc[q]
        f = ft.loc[q]
        row = {"quarter": q, "reaction_date": r["reaction_date"], "side": side,
               "excess_1d_pct": r["excess_1d_pct"], "excess_5d_pct": r["excess_5d_pct"],
               "excess_20d_pct": r["excess_20d_pct"],
               "driver_class": driver, "quote_source": src, "quote_speaker": spk,
               "quote_words": len(quote.split()), "management_quote": quote, "quote_verified": "yes" if ok else "NO",
               "press_cited_driver": press}
        row.update({k: f[k] for k in FEATS})
        rows.append(row)
        if not ok:
            print("QUOTE NOT FOUND:", q, quote[:70])

    with open(OUT / "03_event_study.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

    d = pd.DataFrame(rows)
    print(d[["quarter", "side", "excess_1d_pct", "driver_class", "quote_words", "quote_verified",
             "theme_long_term_targets_share_prepared", "theme_international_share_total",
             "n_numbers_prepared", "lm_net_qa"]].to_string(index=False))
    print("\ndriver classification counts:")
    print(d.groupby(["side", "driver_class"]).size().to_string())
    print("\nmean feature by side:")
    print(d.groupby("side")[FEATS].mean().round(3).T.to_string())

    # ---- figure ----
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(14, 5.2))
    d = d.sort_values("excess_1d_pct")
    colors = ["#b3402f" if v < 0 else "#2f6f4e" for v in d.excess_1d_pct]
    axes[0].barh(d.quarter + "  " + d.driver_class, d.excess_1d_pct, color=colors)
    axes[0].axvline(0, color="grey", lw=0.7)
    axes[0].set_title("Day-1 excess vs QQQ, %, and what the press led with", fontsize=9)
    axes[0].tick_params(labelsize=8)
    for ax, feat, title in ((axes[1], "theme_long_term_targets_share_prepared",
                             "Prepared-remark sentences about\nlong-term targets / full-year framing (share)"),
                            (axes[2], "theme_international_share_total",
                             "All management sentences about\ninternational expansion (share)")):
        for _, r in d.iterrows():
            ax.scatter(r[feat], r["excess_1d_pct"], s=45,
                       color="#b3402f" if r["excess_1d_pct"] < 0 else "#2f6f4e")
            ax.annotate(r["quarter"], (r[feat], r["excess_1d_pct"]), fontsize=7, xytext=(4, 2), textcoords="offset points")
        ax.axhline(0, color="grey", lw=0.7)
        ax.set_title(title, fontsize=9)
        ax.set_ylabel("Day-1 excess, %", fontsize=8)
        ax.tick_params(labelsize=8)
    fig.suptitle("ABNB: the five best and five worst earnings reactions, Q4 2020 - Q2 2026", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "03_event_study.png", dpi=150)
    print("wrote", FIG / "03_event_study.png")


if __name__ == "__main__":
    main()
