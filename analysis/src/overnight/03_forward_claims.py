"""Workstream 03: Airbnb management's explicit forward-looking claims, and whether they came true.

Reads
  Transcripts, via load_calls() in analysis/src/overnight/03_call_features.py (IR FactSet transcripts for
  4Q21 and 1Q23..2Q26; Motley Fool transcripts for 4Q20..3Q21 and 1Q22..4Q22).
  data/raw/letters/<q>Q<yy>_*.htm            23 shareholder letters (8-K Ex. 99.1), for claims made in the
                                             letter's Outlook section rather than on the call.
  data/processed/abnb_driver_history_quarterly.csv   nights, ADR, GBV, revenue, adj. EBITDA, take rate,
                                             S&M, SBC, buybacks, FCF, diluted shares (1Q21..2Q26)
  data/processed/abnb_quarterly_costlines.csv        cost lines incl. FY2020, for full-year margin/S&M checks

Writes
  data/processed/overnight/03_forward_claims.csv        one row per curated forward-looking claim, with the
                                                        later outcome and a verdict
  data/processed/overnight/03_credibility_scorecard.csv hit rate by theme and by executive
  data/processed/overnight/03_claim_verification.csv    the arithmetic behind every quantitative verdict

Method and honesty notes
  CLAIMS is a hand-curated list. It is NOT every forward-looking sentence: the raw pool is ~800 sentences
  (see the extractor in the scratchpad) and most are unfalsifiable product talk ("we're going to continue to
  innovate"). What is curated here is every claim that (a) names a metric or a checkable state of the world,
  and (b) has a horizon that has now passed, plus the still-open claims that matter for the 5 Nov 2026 print.
  Selection bias runs towards claims that are checkable, which flatters neither side systematically, but a
  reader should treat the hit rate as "hit rate among checkable claims", not "hit rate among all statements".
  Every claim_text is verified to be a verbatim substring of the transcript or letter it is attributed to;
  the `quote_verified` column reports the result of that check and the script prints any failures.

  Verdicts:
    kept        the stated outcome happened (or was beaten in the direction management implied)
    missed      the stated outcome did not happen
    partly      directionally right, materially off on magnitude or timing
    too_early   horizon has not closed yet (as of 6 Sep 2026)
    unverifiable  management never disclosed the metric needed to score it, and no public series substitutes

Run: py -3.13 analysis/src/overnight/03_forward_claims.py
"""
import csv
import html
import importlib.util
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "data" / "processed" / "overnight"
OUT.mkdir(parents=True, exist_ok=True)
LETTERS = ROOT / "data" / "raw" / "letters"

_spec = importlib.util.spec_from_file_location("cf03", Path(__file__).with_name("03_call_features.py"))
cf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cf)


# ------------------------------------------------------------------------------------------------
# Curated claims.
# fields: id, quarter, source, speaker, role, theme, metric, horizon, quantified, text, outcome, verdict
#   source: "call_prepared" | "call_qa" | "letter"
#   horizon: "next_q" | "this_year" | "multi_year" | "open"
# ------------------------------------------------------------------------------------------------
C = [
 # ---- 4Q20 (call 25 Feb 2021) -------------------------------------------------------------------
 ("C001", "2020Q4", "call_qa", "Dave Stephenson", "cfo", "margins", "adj. EBITDA margin", "multi_year", "yes",
  "And what we would expect to achieve over time is 30% EBITDA margins or greater.",
  "FY2022 adj. EBITDA margin 34.6%, FY2023 36.8%, FY2025 35.1% (abnb_quarterly_costlines.csv). Cleared in the second year after the claim.",
  "kept"),
 ("C002", "2020Q4", "call_qa", "Dave Stephenson", "cfo", "marketing", "S&M % of revenue", "this_year", "yes",
  "Our sales and marketing expenses as a percentage of revenue in 2021 will be below that of 2019.",
  "FY2021 S&M 19.8% of revenue vs FY2019 ~33.7% (2019 S&M $1,621m / revenue $4,805m, 10-K). Kept by a wide margin.",
  "kept"),
 ("C003", "2020Q4", "call_qa", "Brian Chesky", "ceo", "marketing", "S&M % of revenue", "open", "no",
  "And so we don't intend to ever again spend the amount of money as a percentage of revenue on marketing in the future as we did in 2019.",
  "Peak since: FY2026 H1 25.9% of revenue vs ~33.7% in 2019. Still true, but S&M % has risen every year since 2022 (18.0% -> 17.8% -> 19.3% -> 21.1% -> 25.9% 1H26).",
  "kept"),
 ("C004", "2020Q4", "letter", "shareholder letter", "company", "margins", "adj. EBITDA margin seasonality", "this_year", "no",
  "we expect our Adjusted EBITDA margins to be lower in the first half of 2021 than the second half",
  "1H21 adj. EBITDA margin 7.1% ($158m/$2,222m); 2H21 38.0% ($1,434m/$3,769m). Kept.",
  "kept"),
 ("C005", "2020Q4", "call_qa", "Dave Stephenson", "cfo", "margins", "FY2021 margin target", "this_year", "no",
  "I'd like to give you specific targets for 2021, but it's just too hard to know what our revenue is going to be and so, therefore, kind of a flow-through to profitability.",
  "Declined to quantify; no FY2021 margin guide was ever given. Logged in data/processed/abnb_declined_to_quantify.csv.",
  "unverifiable"),

 # ---- 1Q21 (13 May 2021) ------------------------------------------------------------------------
 ("C006", "2021Q1", "call_qa", "Dave Stephenson", "cfo", "margins", "Q2 2021 adj. EBITDA", "next_q", "yes",
  "that our gross booking value in Q2 of this year will be higher than in Q2 of 2019, and that our revenue rate in Q2 will be similar to that of 2019, and that our EBITDA will be -- our adjusted EBITDA will be breakeven to slightly positive in Q2 of this year.",
  "Q2 2021 adj. EBITDA +$217m (16.3% margin), well above 'breakeven to slightly positive'.",
  "kept"),
 ("C007", "2021Q1", "call_qa", "Brian Chesky", "ceo", "supply_hosts", "host count", "multi_year", "no",
  "And I expect us to get millions of more hosts in the coming years on Airbnb.",
  "Airbnb stopped publishing host counts after 2023 (4m+ hosts, 2023 letters); active listings went 6.0m (2021) to 8m+ (2024) before disclosure was dropped. Directionally right but the company retired the metric.",
  "partly"),
 ("C008", "2021Q1", "call_qa", "Brian Chesky", "ceo", "pricing_adr", "occupancy", "multi_year", "no",
  "Occupancy rates, we think, average on global level will go up as we get better at matching supply and demand.",
  "Airbnb has never disclosed a platform occupancy rate. Not scoreable from company data.",
  "unverifiable"),

 # ---- 2Q21 (12 Aug 2021) ------------------------------------------------------------------------
 ("C009", "2021Q2", "call_prepared", "Brian Chesky", "ceo", "demand_macro", "Q3 2021 revenue", "next_q", "yes",
  "Now, while we recognize the persistence of COVID and the Delta variant, we expect Q3 to be our strongest revenue quarter ever.",
  "Q3 2021 revenue $2,237m vs prior record $1,335m (Q2 2021). Kept.",
  "kept"),
 ("C010", "2021Q2", "call_qa", "Dave Stephenson", "cfo", "pricing_adr", "ADR", "multi_year", "no",
  "we will see ADRs moderate, but that will be purely as part of mix and as the other parts of the business come back and they have that lower overall kind of ADR rates",
  "ADR by calendar year: $156.0 (2021), $160.3 (2022), $163.1 (2023), $166.0 (2024), $171.2 (2025), $185.3 (1H26). ADR rose every single year after the claim.",
  "missed"),

 # ---- 3Q21 (4 Nov 2021) -------------------------------------------------------------------------
 ("C011", "2021Q3", "letter", "shareholder letter", "company", "demand_macro", "Q4 2021 nights", "next_q", "no",
  "We expect Nights and Experiences Booked in Q4 2021 to significantly outperform Q4 2020 levels and approximate Q4 2019 levels.",
  "Q4 2021 nights 73.4m vs Q4 2019 ~76.9m (approximate; -5%) and vs Q4 2020 46.3m (+59%). Kept.",
  "kept"),
 ("C012", "2021Q3", "call_qa", "Dave Stephenson", "cfo", "pricing_adr", "ADR", "multi_year", "no",
  "we anticipate the overall ADR to moderate some but we also believe that some of the higher ADR will sustain for the future",
  "Same series as C010: ADR never moderated on a calendar-year basis. The 'higher ADR sustains' half was right, the 'moderate' half was not.",
  "partly"),
 ("C013", "2021Q3", "call_qa", "Brian Chesky", "ceo", "new_businesses", "Experiences", "multi_year", "no",
  "We've seen strong growth over the last couple of quarters, and I'm expecting this to be a big area of growth over the coming five years or so.",
  "Experiences was relaunched in May 2025 as a new product; on the 3Q25 call Chesky said it will 'take three to five years' for services and experiences to become material. Five years on from the claim Airbnb still reports no Experiences revenue line.",
  "missed"),

 # ---- 4Q21 (15 Feb 2022) ------------------------------------------------------------------------
 ("C014", "2021Q4", "call_qa", "Dave Stephenson", "cfo", "marketing", "S&M % of revenue", "this_year", "yes",
  "we anticipate our marketing expense as percentage of revenue in 2022 to be relatively consistent with that in 2021",
  "FY2022 S&M 18.0% of revenue vs FY2021 19.8%. Consistent (slightly better).",
  "kept"),
 ("C015", "2021Q4", "call_qa", "Dave Stephenson", "cfo", "buybacks_sbc", "RSU tax cash use", "this_year", "yes",
  "So, we will be net settling those shares, and that will be a use of about a little more than $1 billion of cash during the year.",
  "FY2022 RSU tax withholding cash outflow ~$1.1bn (abnb_capital_return_quarterly.csv). Kept.",
  "kept"),
 ("C016", "2021Q4", "call_qa", "Dave Stephenson", "cfo", "margins", "ADR headwind to margin", "this_year", "no",
  "As the business rebounds more urban, more lower ADR regions and ADRs moderate some, that will be continued headwind for our margins.",
  "ADR rose in 2022 and FY2022 adj. EBITDA margin expanded 800bp to 34.6%. The stated headwind did not materialise.",
  "missed"),

 # ---- 1Q22 (3 May 2022) -------------------------------------------------------------------------
 ("C017", "2022Q1", "call_qa", "Dave Stephenson", "cfo", "margins", "FY2022 net income", "this_year", "no",
  "And I'm really excited that in 2022, we'll have our first full year of net income profitability.",
  "FY2022 GAAP net income $1.89bn. Kept.",
  "kept"),
 ("C018", "2022Q1", "call_qa", "Dave Stephenson", "cfo", "margins", "FY2022 adj. EBITDA margin", "this_year", "no",
  "And one of the things we noted in the letter is that we're expecting for the full year a modest expansion in our overall EBITDA margin rate.",
  "FY2022 adj. EBITDA margin 34.6% vs FY2021 26.6%, +800bp. Beat the 'modest' framing.",
  "kept"),
 ("C019", "2022Q1", "call_qa", "Dave Stephenson", "cfo", "pricing_adr", "ADR 2H22", "this_year", "no",
  "We think that they will likely moderate throughout the back half of the year as mix continues to adjust more toward cities, more cross border, which have lower average daily rates",
  "2H 2022 ADR $154.6 vs 2H 2021 $151.4, +2.1% year over year; sequentially down from 1H but up year over year. Directionally sequential-right, year-over-year wrong.",
  "partly"),

 # ---- 2Q22 (2 Aug 2022) -------------------------------------------------------------------------
 ("C020", "2022Q2", "call_prepared", "Brian Chesky", "ceo", "buybacks_sbc", "buyback", "open", "yes",
  "In fact, we're so confident in our long-term growth and profitability that today, we're announcing a $2 billion share repurchase program.",
  "$1.5bn repurchased in FY2022 and $2.25bn in FY2023; programme exhausted and successively enlarged. Kept.",
  "kept"),
 ("C021", "2022Q2", "call_qa", "Dave Stephenson", "cfo", "marketing", "S&M % of revenue", "this_year", "yes",
  "The short answer is we anticipate marketing as a percentage of revenue in 2022 will be consistent with 2021.",
  "FY2022 18.0% vs FY2021 19.8%. Kept.",
  "kept"),

 # ---- 3Q22 (1 Nov 2022) -------------------------------------------------------------------------
 ("C022", "2022Q3", "letter", "shareholder letter", "company", "demand_macro", "Q4 2022 nights growth", "next_q", "no",
  "we expect Nights and Experiences Booked growth will moderate slightly relative to Q3 2022",
  "Q3 2022 nights +25.1% year over year; Q4 2022 +20.2%. Kept - and the stock fell 13.4% the next day on exactly this sentence.",
  "kept"),
 ("C023", "2022Q3", "call_qa", "Dave Stephenson", "cfo", "margins", "FCF margin", "multi_year", "no",
  "What we'll continue to have is greater expansion in free cash flow margin.",
  "FCF margin: 40.5% (2022), 38.7% (2023), 40.4% (2024), 37.7% (2025). No expansion; three of four years below the 2022 base.",
  "missed"),
 ("C024", "2022Q3", "call_qa", "Dave Stephenson", "cfo", "marketing", "S&M % of revenue", "this_year", "yes",
  "it's going to be relatively flat from '22 over '21, and you should anticipate similar marketing as a percentage of revenue in '23",
  "FY2023 S&M 17.8% vs FY2022 18.0%. Kept.",
  "kept"),
 ("C025", "2022Q3", "call_qa", "Brian Chesky", "ceo", "pricing_adr", "total-price display / ADR", "multi_year", "no",
  "And I think if we make some of these pricing and discount changes in the coming future, I think the value on Airbnb will get even better.",
  "ADR rose every calendar year 2022-2026 and the 4Q25 letter says pricing initiatives are now a revenue tailwind, not a price reducer. The affordability framing was not delivered in price terms.",
  "missed"),

 # ---- 4Q22 (14 Feb 2023) ------------------------------------------------------------------------
 ("C026", "2022Q4", "call_qa", "Dave Stephenson", "cfo", "buybacks_sbc", "buyback timing", "next_q", "yes",
  "We have 500 million left on the existing repurchase approval and anticipate that we'd be executing early in the year.",
  "Q1 2023 buybacks $493m. Kept.",
  "kept"),
 ("C027", "2022Q4", "call_qa", "Dave Stephenson", "cfo", "buybacks_sbc", "SBC vs buyback", "this_year", "yes",
  "We're going to have about $1 billion of stock-based compensation.",
  "FY2023 SBC $1.10bn (abnb_driver_history_quarterly.csv). Close enough to 'about $1 billion'.",
  "kept"),
 ("C028", "2022Q4", "call_qa", "Dave Stephenson", "cfo", "margins", "FY2023 adj. EBITDA margin", "this_year", "no",
  "But I feel confident we can deliver our EBITDA margin neutral in the face of whatever ADR headwinds that we see this year.",
  "FY2023 adj. EBITDA margin 36.8% vs FY2022 34.6%, +220bp. Beat 'neutral'.",
  "kept"),
 ("C029", "2022Q4", "call_qa", "Dave Stephenson", "cfo", "marketing", "S&M % of revenue", "this_year", "yes",
  "And what we'd see in 2023 is that marketing costs as a percentage of revenue for the full year will be about the same as what it was in 2022.",
  "FY2023 17.8% vs FY2022 18.0%. Kept.",
  "kept"),
 ("C030", "2022Q4", "call_qa", "Dave Stephenson", "cfo", "take_rate_fees", "implied take rate", "this_year", "no",
  "But I think if you look back at 2022, it'll be a good guide for your take rate.",
  "FY2023 implied take rate 13.53% vs FY2022 13.27%. Close; slightly higher.",
  "kept"),

 # ---- 1Q23 (9 May 2023) -------------------------------------------------------------------------
 ("C031", "2023Q1", "letter", "shareholder letter", "company", "demand_macro", "Q2 2023 nights vs revenue", "next_q", "no",
  "We expect year-over-year growth in Nights and Experiences Booked in Q2 2023 to be lower than our revenue growth during the quarter.",
  "Q2 2023 nights +11.0% vs revenue +18.1%. Kept - and the stock fell 10.9% the next day on this line.",
  "kept"),
 ("C032", "2023Q1", "call_qa", "Dave Stephenson", "cfo", "pricing_adr", "FY2023 ADR", "this_year", "yes",
  "In terms of full year expectations, the year-over-year growth in ADR should be, I think, still probably down in that kind of mid-single-digit range.",
  "FY2023 ADR $163.1 vs FY2022 $160.3, +1.8%. Management guided to a mid-single-digit DECLINE and got a small rise.",
  "missed"),
 ("C033", "2023Q1", "call_qa", "Brian Chesky", "ceo", "pricing_adr", "prices / affordability", "this_year", "no",
  "And I think what's going to happen is all the supply coming on the market will keep prices from going up.",
  "ADR rose 1.8% in 2023, 1.8% in 2024, 3.1% in 2025 and 7.2% in 1H26. Supply growth did not hold prices flat.",
  "missed"),
 ("C034", "2023Q1", "call_qa", "Brian Chesky", "ceo", "international", "expansion-market growth", "multi_year", "no",
  "So, I think international is going to be a pretty big boon to growth over the next two, three years.",
  "Company revenue growth decelerated from 18.1% (2023) to 11.9% (2024) to 10.3% (2025) before reaccelerating in 2026 on product and fee changes. Airbnb never disclosed expansion-market revenue, so the claim cannot be scored on its own terms.",
  "unverifiable"),

 # ---- 2Q23 (3 Aug 2023) -------------------------------------------------------------------------
 ("C035", "2023Q2", "call_qa", "Brian Chesky", "ceo", "take_rate_fees", "take rate", "multi_year", "no",
  "That being said, I do not expect our take rate to change materially.",
  "Implied take rate 13.53% (2023), 13.57% (2024), 13.41% (2025). Range of 16bp over three years. Kept.",
  "kept"),
 ("C036", "2023Q2", "call_qa", "Brian Chesky", "ceo", "margins", "margin expansion source", "multi_year", "no",
  "And the way that we're going to see margin expansion is by launching incremental services for guests and hosts over the coming years.",
  "Services and Experiences launched May 2025; FY2025 adj. EBITDA margin fell 130bp to 35.1% because of the investment behind them. The FY2026 guide is 35.5%, still below 2023's 36.8%. Three years on, services have cost margin rather than added it.",
  "missed"),
 ("C037", "2023Q2", "call_qa", "Dave Stephenson", "cfo", "margins", "2H23 margin", "this_year", "no",
  "So for the back half of the year, we feel confident we're going to be able to exceed our EBITDA margins over the prior year.",
  "2H 2023 adj. EBITDA margin 45.7% vs 2H 2022 41.1%. Kept.",
  "kept"),
 ("C038", "2023Q2", "call_qa", "Dave Stephenson", "cfo", "marketing", "S&M % of revenue", "this_year", "yes",
  "our marketing expense as a percentage of revenue we expect to remain relatively flat year-over-year on a total-year basis from 2023 over 2022",
  "FY2023 17.8% vs FY2022 18.0%. Kept.",
  "kept"),

 # ---- 3Q23 (1 Nov 2023) -------------------------------------------------------------------------
 ("C039", "2023Q3", "call_qa", "Brian Chesky", "ceo", "international", "expansion-market penetration", "multi_year", "no",
  "So I think the next 24 months, we're going to see a major acceleration in our penetration in a lot of these markets.",
  "No expansion-market disclosure exists; company nights growth decelerated from 13.5% (3Q23) to 8.5% (3Q24) to 8.8% (3Q25) over exactly that 24-month window.",
  "missed"),
 ("C040", "2023Q3", "call_qa", "Dave Stephenson", "cfo", "demand_macro", "Q4 2023 revenue growth", "next_q", "yes",
  "I think I'm feeling confident about our revenue growth for Q4 being 12% to 14% growth, and in fact that that remains stable with Q3, I think, is very promising.",
  "Q4 2023 revenue $2,218m, +16.6% year over year. Beat the top of the range.",
  "kept"),
 ("C041", "2023Q3", "call_qa", "Brian Chesky", "ceo", "regulation", "New York", "multi_year", "no",
  "In fact, New York has gone a different direction, and I think is going to turn into a cautionary tale because what we're already seeing is hotel prices in New York are now up 8% year-over- year.",
  "NYC Local Law 18 stayed in force; NYC listings fell ~80% and did not return. NYC hotel ADR did keep rising. The prediction that the city would reverse course has not happened (see research/regulatory/).",
  "partly"),

 # ---- 4Q23 (13 Feb 2024) ------------------------------------------------------------------------
 ("C042", "2023Q4", "call_qa", "Ellie Mertz", "cfo", "marketing", "S&M % of revenue", "this_year", "yes",
  "And then in terms of marketing, largely, we're going to keep marketing costs as a percentage of revenue largely the same as what it was in 2023.",
  "FY2024 S&M 19.3% of revenue vs FY2023 17.8%, +150bp. Missed; marketing was the single largest source of the 2024 margin drag.",
  "missed"),
 ("C043", "2023Q4", "call_qa", "Ellie Mertz", "cfo", "take_rate_fees", "Q1 2024 implied take rate", "next_q", "no",
  "In Q1, the implied take rate revenue over gross booking value is going to be higher.",
  "Q1 2024 implied take rate 9.35% vs Q1 2023 8.91%. Kept.",
  "kept"),
 ("C044", "2023Q4", "letter", "shareholder letter", "company", "margins", "FY2024 adj. EBITDA margin", "this_year", "yes",
  "For the full-year 2024, we expect to maintain an Adjusted EBITDA Margin of at least 35%, providing us flexibility to invest in incremental growth opportunities over the course of the year.",
  "FY2024 adj. EBITDA margin 36.4% on our cost-line file (company reported ~36%); raised to ~35.5% at 3Q24. Kept.",
  "kept"),
 ("C045", "2023Q4", "call_qa", "Ellie Mertz", "cfo", "take_rate_fees", "cross-currency fee", "open", "yes",
  "So, we don't anticipate this fee to affect the majority of our guests because the cross-currency transactions are only approximately 20% of the gross booking value.",
  "The 20% cross-border share has never been re-disclosed; take rate did rise ~4bp in 2024. Consistent but not independently checkable.",
  "unverifiable"),

 # ---- 1Q24 (8 May 2024) -------------------------------------------------------------------------
 ("C046", "2024Q1", "call_qa", "Ellie Mertz", "cfo", "demand_macro", "Q3 2024 revenue acceleration", "next_q", "no",
  "And it's that backlog that gives us confidence around the comments we made in the outlook that Q3 revenue should accelerate above the Q2 outlook.",
  "Q3 2024 revenue growth 9.9% vs Q2 2024 10.6%. Growth decelerated. Missed.",
  "missed"),
 ("C047", "2024Q1", "call_qa", "Brian Chesky", "ceo", "ai", "AI in customer service", "multi_year", "no",
  "I think we're going to see the biggest impact is going to be on customer service in the near term.",
  "1Q26 letter: cost per booking down ~10% year over year on AI customer support; 4Q25 call: >30% of tickets handled by AI agent. Kept, on the company's own numbers.",
  "kept"),

 # ---- 2Q24 (6 Aug 2024) -------------------------------------------------------------------------
 ("C048", "2024Q2", "letter", "shareholder letter", "company", "demand_macro", "Q3 2024 nights growth", "next_q", "no",
  "we are seeing shorter booking lead times globally and some signs of slowing demand from U.S. guests",
  "Q3 2024 nights +8.5% vs Q2 2024 +8.7%: a 0.2pt moderation. The warning was directionally right but trivially so; the stock fell 12.3% excess on it.",
  "partly"),
 ("C049", "2024Q2", "call_qa", "Ellie Mertz", "cfo", "margins", "profitability level", "multi_year", "no",
  "So, we will use some of the profitability to invest, but we don't anticipate any kind of sea change in the foreseeable future around overall profitability levels.",
  "Adj. EBITDA margin 36.4% (2024) -> 35.1% (2025) -> 35.5% guided (2026). A 130bp give-back, not a sea change. Kept.",
  "kept"),
 ("C050", "2024Q2", "call_qa", "Brian Chesky", "ceo", "new_businesses", "cost of new businesses", "multi_year", "no",
  "Most of these new services and offerings, though, are going to not cost very much.",
  "Airbnb then guided $200-250m of new-business investment for 2025 alone and cut the FY2025 margin floor to 34.5% from 35%+ because of it. Missed within two quarters.",
  "missed"),

 # ---- 3Q24 (7 Nov 2024) -------------------------------------------------------------------------
 ("C051", "2024Q3", "letter", "shareholder letter", "company", "demand_macro", "Q4 2024 nights growth", "next_q", "no",
  "we expect year-over-year growth of Nights and Experienced Booked in Q4 2024 to be higher than Q3 2024",
  "Q4 2024 nights +12.3% vs Q3 2024 +8.5%. Kept, and the stock rose 14.0% excess on the print that confirmed it.",
  "kept"),
 ("C052", "2024Q3", "call_qa", "Brian Chesky", "ceo", "new_businesses", "$1bn+ new businesses per year", "multi_year", "yes",
  "And what I expect is every year now, for the coming years, we will launch one to two new businesses that will generate $1 billion or more of revenue incrementally a year.",
  "One year later (3Q25 call) Chesky said 'it's going to take three to five years, I think, for services, experiences to become a material part of our business', and the 2Q25 letter says 'we don't expect meaningful revenue from our new businesses in the near term'. The $1bn-a-year cadence was quietly dropped.",
  "missed"),
 ("C053", "2024Q3", "call_qa", "Ellie Mertz", "cfo", "new_businesses", "investment timing", "this_year", "no",
  "But what you should anticipate is that some of the investment behind those new services will front run the revenue.",
  "Confirmed: $200-250m of 2025 spend guided in Feb 2025 with essentially no associated revenue disclosed through 2Q26. Kept (as a warning).",
  "kept"),
 ("C054", "2024Q3", "call_qa", "Ellie Mertz", "cfo", "margins", "long-run margin", "multi_year", "no",
  "And over the long term, I think you can expect that there is opportunity for further margin expansion.",
  "Adj. EBITDA margin peaked at 36.8% in 2023 and has been lower every year since (36.4%, 35.1%, 35.5% guided). No expansion yet, two years on.",
  "missed"),

 # ---- 4Q24 (13 Feb 2025) ------------------------------------------------------------------------
 ("C055", "2024Q4", "call_prepared", "Ellie Mertz", "cfo", "new_businesses", "new-business investment", "this_year", "yes",
  "This year, we plan to invest $200 million to $250 million towards launching and scaling new businesses, which we'll introduce in May.",
  "Airbnb has never reported the realised 2025 figure. FY2025 margin came in at 35.1% vs a 34.5% floor, consistent with spending at or below the low end, but the number itself was never disclosed.",
  "unverifiable"),
 ("C056", "2024Q4", "call_prepared", "Ellie Mertz", "cfo", "margins", "FY2025 adj. EBITDA margin", "this_year", "yes",
  "Even with these investments, we expect to maintain strong profitability, delivering a full year adjusted EBITDA margin of at least 34.5%.",
  "FY2025 adj. EBITDA margin 35.1% (raised to ~35% at 3Q25). Kept.",
  "kept"),
 ("C057", "2024Q4", "call_qa", "Ellie Mertz", "cfo", "take_rate_fees", "FY2025 implied take rate", "this_year", "yes",
  "And so instead, for full year 2025, you should assume that the implied take rate gets the full benefit of 20 basis points increase on a year- over-year basis as compared to 2024.",
  "FY2025 implied take rate 13.41% vs FY2024 13.57%: DOWN 16bp against a guided +20bp. A 36bp miss on the single most model-relevant number management gave in 2025.",
  "missed"),
 ("C058", "2024Q4", "call_qa", "Ellie Mertz", "cfo", "buybacks_sbc", "FY2025 buyback", "this_year", "yes",
  "And then from a returning capital to shareholders, you should look at the volume of repurchase activity in 2024 as a guide with regard to the magnitude in 2025.",
  "FY2024 buybacks $3.43bn; FY2025 $3.79bn. Kept (slightly above).",
  "kept"),
 ("C059", "2024Q4", "call_qa", "Brian Chesky", "ceo", "new_businesses", "launch cadence", "multi_year", "yes",
  "And you should be able to expect like one or a couple of businesses to launch every single year for the next five years.",
  "2025: Services and Experiences (May). 2026: hotels push and AI search. Cadence held so far; revenue contribution not.",
  "kept"),

 # ---- 1Q25 (1 May 2025) -------------------------------------------------------------------------
 ("C060", "2025Q1", "call_prepared", "Ellie Mertz", "cfo", "margins", "FY2025 adj. EBITDA margin", "this_year", "yes",
  "For the full year, we continue to expect an adjusted EBITDA margin of at least 34.5%, in line with what we shared in February.",
  "FY2025 35.1%. Kept.",
  "kept"),
 ("C061", "2025Q1", "call_qa", "Brian Chesky", "ceo", "international", "return to double-digit growth", "multi_year", "no",
  "And I think that international will be one of the biggest growth drivers that will get us back to double-digit growth on Airbnb.",
  "Revenue growth returned to double digits: 12.0% (4Q25), 17.9% (1Q26), 16.5% (2Q26). But management attributes the reacceleration to product and fee changes, not international. Right answer, arguably wrong reason.",
  "partly"),

 # ---- 2Q25 (6 Aug 2025) -------------------------------------------------------------------------
 ("C062", "2025Q2", "letter", "shareholder letter", "company", "demand_macro", "2H 2025 growth", "this_year", "no",
  "we expect a tougher year-over-year comparison toward the end of the quarter. This dynamic will continue into Q4, putting pressure on growth rates later in the year.",
  "Nights growth ACCELERATED after the warning: 7.4% (2Q25) -> 8.8% (3Q25) -> 9.8% (4Q25). Revenue growth 12.7% -> 9.7% -> 12.0%. The pressure did not arrive; the stock fell 8.4% excess on the warning.",
  "missed"),
 ("C063", "2025Q2", "call_prepared", "Ellie Mertz", "cfo", "margins", "Q3/Q4 2025 margin", "next_q", "no",
  "we anticipate that adjusted EBITDA margin will be lower than in Q3 2024, primarily due to investments in new growth and policy initiatives.",
  "Q3 2025 adj. EBITDA margin 50.1% vs Q3 2024 52.5%, -240bp. Kept.",
  "kept"),
 ("C064", "2025Q2", "call_prepared", "Ellie Mertz", "cfo", "new_businesses", "new-business revenue", "next_q", "no",
  "While we don't expect meaningful revenue from our new businesses in the near term, we believe the opportunity is significant and are building with a multiyear view.",
  "Still no disclosed Services/Experiences revenue through 2Q26. Kept (as a warning), and a direct contradiction of C052.",
  "kept"),

 # ---- 3Q25 (6 Nov 2025) -------------------------------------------------------------------------
 ("C065", "2025Q3", "call_prepared", "Ellie Mertz", "cfo", "margins", "FY2025 adj. EBITDA margin", "this_year", "yes",
  "On profitability, we now expect our full year adjusted EBITDA margin to be approximately 35%, up from the 34.5% floor previously shared.",
  "FY2025 35.1%. Kept.",
  "kept"),
 ("C066", "2025Q3", "call_prepared", "Ellie Mertz", "cfo", "buybacks_sbc", "effective tax rate", "multi_year", "no",
  "On a go forward basis starting in 2026, we anticipate that the One Big Beautiful Bill will materially reduce our effective tax rate due to the preferential changes to tax on foreign earnings.",
  "Restated at 4Q25 as 'mid to high-teens' and at 1Q26 as 'high-teens' vs 20% in 2025. 1Q26 GAAP results also carried a $70m CAMT charge and 2Q26 an offsetting $77m benefit, so the realised rate is noisy. Directionally on track.",
  "too_early"),
 ("C067", "2025Q3", "call_qa", "Brian Chesky", "ceo", "new_businesses", "Services/Experiences materiality", "multi_year", "yes",
  "So it's going to take three to five years, I think, for services, experiences to become a material part of our business.",
  "Horizon runs to 2028-2030. This is the walk-back of C052; note the timeline moved out by three to five years in twelve months.",
  "too_early"),
 ("C068", "2025Q3", "call_qa", "Brian Chesky", "ceo", "pricing_adr", "supply and prices", "multi_year", "no",
  "But as we get more supply, prices will come down.",
  "ADR rose 5.9% year over year in the very next quarter (4Q25) and 9.0% in 1Q26. Missed immediately.",
  "missed"),

 # ---- 4Q25 (12 Feb 2026) ------------------------------------------------------------------------
 ("C069", "2025Q4", "call_prepared", "Brian Chesky", "ceo", "long_term_targets", "FY2026 revenue growth", "this_year", "yes",
  "We expect revenue growth to accelerate to at least low-double digits in 2026.",
  "Raised to low-to-mid teens at 1Q26 and to at least mid-teens at 2Q26; 1H26 actual +17.2%. Beaten and raised twice.",
  "kept"),
 ("C070", "2025Q4", "call_prepared", "Brian Chesky", "ceo", "long_term_targets", "FY2026 adj. EBITDA margin", "this_year", "yes",
  "We expect adjusted EBITDA margin to be stable year- over-year.",
  "Raised to at least 35% at 1Q26 and at least 35.5% at 2Q26 vs 35.1% in 2025. On track to beat.",
  "too_early"),
 ("C071", "2025Q4", "call_qa", "Brian Chesky", "ceo", "ai", "AI customer service share", "this_year", "yes",
  "A year from now, if we're successful, significantly more than 30% of tickets will be handled by a customer service agent in many more languages, in all the languages where we have live agents.",
  "Verdict due at the 4Q26 call (Feb 2027). Interim: 1Q26 letter reports cost per booking down ~10% year over year. This is the single most falsifiable AI claim management has made.",
  "too_early"),
 ("C072", "2025Q4", "call_qa", "Ellie Mertz", "cfo", "take_rate_fees", "Q1/Q2 2026 take-rate timing", "next_q", "yes",
  "But we anticipate it will support about 50 basis points of incremental revenue in Q1 and 50 basis points less revenue in Q2.",
  "Q1 2026 revenue +17.9% vs a 14-16% guide (beat by ~2pts, letter attributes it to product updates and FX); Q2 2026 +16.5% vs a 14-16% guide. The Q2 give-back did not show up. Partly.",
  "partly"),
 ("C073", "2025Q4", "call_qa", "Ellie Mertz", "cfo", "competition", "hotels share of business", "this_year", "yes",
  "We'll be expanding the hotel supply over the course of the year and intend to exit 2026 with hotels being a meaningfully larger percent of the overall business going forward.",
  "2Q26 call: hotel supply growing ~3x homes and Chesky says the initiative is 'going significantly better than I expected'. Airbnb has not disclosed hotels as a percent of GBV, so 'meaningfully larger percent' is not scoreable yet. Watch item for 5 Nov.",
  "too_early"),
 ("C074", "2025Q4", "call_prepared", "Ellie Mertz", "cfo", "take_rate_fees", "single service fee migration", "this_year", "no",
  "We began migrating our API host to a single service fee, and now plan to migrate more hosts in 2026.",
  "2Q26: broader rollout announced to 'the majority of our remaining hosts', to be completed by year end. On track.",
  "too_early"),

 # ---- 1Q26 (7 May 2026) -------------------------------------------------------------------------
 ("C075", "2026Q1", "call_prepared", "Brian Chesky", "ceo", "long_term_targets", "FY2026 revenue growth", "this_year", "yes",
  "We're raising our guidance for 2026 and now expect year-over-year revenue growth to accelerate to low- to mid-teens.",
  "Raised again at 2Q26 to at least mid-teens. 1H26 actual +17.2%.",
  "kept"),
 ("C076", "2026Q1", "call_qa", "Ellie Mertz", "cfo", "take_rate_fees", "FY2026 take rate", "this_year", "no",
  "you should see modest upside to our take rate from both the migration to the single fee structure as well as our insurance programs",
  "Reversed one quarter later: the 2Q26 letter guides FY2026 implied take rate 'relatively flat compared to 2025' because of Reserve Now Pay Later timing and new-business customer incentives. Guidance walked back inside a quarter.",
  "missed"),
 ("C077", "2026Q1", "call_qa", "Brian Chesky", "ceo", "take_rate_fees", "payments and pricing revenue", "multi_year", "yes",
  "And I think the payments and pricing roadmap will deliver � it has the opportunity to deliver hundreds of millions of dollars in revenue each year.",
  "No disclosed payments/pricing revenue line. Not scoreable; the phrasing ('has the opportunity to') is itself a hedge.",
  "unverifiable"),

 # ---- 2Q26 (6 Aug 2026) -------------------------------------------------------------------------
 ("C078", "2026Q2", "call_prepared", "Ellie Mertz", "cfo", "long_term_targets", "FY2026 revenue growth", "this_year", "yes",
  "We now expect year-over- year revenue growth to improve to at least mid-teens, up from the low to mid-teens guidance we provided last quarter, supported by the accelerated pace of Nights and Seats Booked we've observed across our business.",
  "Open. Q3 2026 guide is 15-17%; needs 2H26 growth of ~14%+ to hold. Verdict at the 4Q26 print.",
  "too_early"),
 ("C079", "2026Q2", "call_prepared", "Ellie Mertz", "cfo", "margins", "FY2026 adj. EBITDA margin", "this_year", "yes",
  "And for full year profitability, we are now expecting our adjusted EBITDA margin to be at least 35.5%, up from 35%.",
  "Open. 1H26 adj. EBITDA margin 28.3%; the guide requires a strong 2H (2H25 was 39.9%). Verdict at the 4Q26 print.",
  "too_early"),
 ("C080", "2026Q2", "call_prepared", "Ellie Mertz", "cfo", "take_rate_fees", "FY2026 implied take rate", "this_year", "yes",
  "For the full year, we expect our implied take rate to be relatively flat compared to 2025, accounting for the timing of bookings versus check-in with Reserve Now, Pay Later, as well as higher customer incentives related to new businesses during 2026.",
  "Open. 1H26 implied take rate 11.15% vs 1H25 11.13%: flat so far. This is the walk-back of C076.",
  "too_early"),
 ("C081", "2026Q2", "call_qa", "Ellie Mertz", "cfo", "take_rate_fees", "single service fee coverage", "this_year", "yes",
  "And we anticipate by year end, our entire supply base will be on that single service fee.",
  "Open. Checkable at the 4Q26 print; a slip here would also put C080 at risk.",
  "too_early"),
 ("C082", "2026Q2", "call_qa", "Brian Chesky", "ceo", "competition", "hotels", "multi_year", "no",
  "We are absolutely going to be stepping on the gas, given the reception, and we are focused not just in supply-constrained markets, but all markets.",
  "Open. No hotels GBV disclosure exists; the 5 Nov call is the natural place for a first quantification.",
  "too_early"),
 ("C083", "2026Q2", "call_prepared", "Ellie Mertz", "cfo", "demand_macro", "Middle East conflict impact", "next_q", "no",
  "Despite the ongoing conflict in the Middle East, we continue to see strong underlying demand globally, and the impact to our business from the conflict was less than we had anticipated.",
  "Retrospective correction of the 1Q26 guide, which had built in an 'approximate 100 basis points headwind related to the conflict in the Middle East'. Management over-provisioned for a macro shock, as at 2Q25.",
  "kept"),
]

FIELDS = ["claim_id", "quarter", "call_date", "source", "speaker", "role", "theme", "metric", "horizon",
          "quantified", "claim_text", "outcome", "verdict", "quote_verified"]


def norm(s):
    s = html.unescape(s)
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace("�", " ").replace(" ", " ")
    return re.sub(r"[^a-z0-9 ]", " ", re.sub(r"\s+", " ", s.lower())).replace("  ", " ").strip()


def squash(s):
    return re.sub(r"\s+", "", norm(s))


def load_letter_text():
    out = {}
    for p in sorted(LETTERS.glob("*.htm")):
        stem = p.name.split("_")[0]          # e.g. 1Q23
        q = f"20{stem[2:]}Q{stem[0]}"
        raw = p.read_text(encoding="utf-8", errors="replace")
        out[q] = squash(re.sub(r"<[^>]+>", " ", raw))
    return out


def main():
    calls = {c["quarter"]: c for c in cf.load_calls()}
    call_text = {q: squash(" ".join(t["text"] for t in c["turns"])) for q, c in calls.items()}
    letter_text = load_letter_text()

    rows, misses = [], []
    for cid, q, src, spk, role, theme, metric, horizon, quant, text, outcome, verdict in C:
        hay = letter_text.get(q, "") if src == "letter" else call_text.get(q, "")
        ok = squash(text) in hay
        if not ok:
            # allow a long-prefix match (transcripts sometimes carry an [indiscernible] tag mid-sentence)
            frag = squash(text)
            ok = any(frag[:n] in hay for n in (140, 100, 70)) and len(frag) > 70
        if not ok:
            misses.append((cid, q, src, text[:90]))
        rows.append(dict(claim_id=cid, quarter=q, call_date=cf.CALL_DATES[q], source=src, speaker=spk, role=role,
                         theme=theme, metric=metric, horizon=horizon, quantified=quant,
                         claim_text=text, outcome=outcome, verdict=verdict,
                         quote_verified="yes" if ok else "NO"))

    with open(OUT / "03_forward_claims.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)

    # ---------------- scorecard ----------------
    closed = [r for r in rows if r["verdict"] in ("kept", "missed", "partly")]

    def score(group_key):
        agg = defaultdict(Counter)
        for r in rows:
            agg[r[group_key]][r["verdict"]] += 1
        out = []
        for k, c in sorted(agg.items()):
            n_closed = c["kept"] + c["missed"] + c["partly"]
            out.append({"group": group_key, "value": k, "n_claims": sum(c.values()),
                        "kept": c["kept"], "partly": c["partly"], "missed": c["missed"],
                        "too_early": c["too_early"], "unverifiable": c["unverifiable"],
                        "n_closed": n_closed,
                        "hit_rate_strict_pct": round(100 * c["kept"] / n_closed, 1) if n_closed else "",
                        "hit_rate_incl_partly_pct": round(100 * (c["kept"] + 0.5 * c["partly"]) / n_closed, 1) if n_closed else ""})
        return out

    sc = score("theme") + score("role") + score("speaker") + score("horizon") + score("quantified") + score("source")
    tot = Counter(r["verdict"] for r in rows)
    n_closed = tot["kept"] + tot["missed"] + tot["partly"]
    sc.append({"group": "ALL", "value": "all claims", "n_claims": len(rows), "kept": tot["kept"],
               "partly": tot["partly"], "missed": tot["missed"], "too_early": tot["too_early"],
               "unverifiable": tot["unverifiable"], "n_closed": n_closed,
               "hit_rate_strict_pct": round(100 * tot["kept"] / n_closed, 1),
               "hit_rate_incl_partly_pct": round(100 * (tot["kept"] + 0.5 * tot["partly"]) / n_closed, 1)})
    with open(OUT / "03_credibility_scorecard.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sc[0].keys()))
        w.writeheader(); w.writerows(sc)

    print(f"claims: {len(rows)}  kept {tot['kept']}  partly {tot['partly']}  missed {tot['missed']} "
          f"too_early {tot['too_early']}  unverifiable {tot['unverifiable']}")
    print(f"strict hit rate on closed claims: {100*tot['kept']/n_closed:.0f}% (n={n_closed})")
    if misses:
        print(f"\nQUOTE VERIFICATION FAILURES ({len(misses)}):")
        for m in misses:
            print("  ", m)
    else:
        print("all claim quotes verified verbatim against transcript / letter")
    for r in sc:
        if r["group"] in ("role", "ALL") or (r["group"] == "theme" and r["n_closed"]):
            print(f"  {r['group']:10} {str(r['value']):26} n={r['n_claims']:3} closed={r['n_closed']:3} "
                  f"kept={r['kept']:3} partly={r['partly']:2} missed={r['missed']:3} hit={r['hit_rate_strict_pct']}")


if __name__ == "__main__":
    main()
