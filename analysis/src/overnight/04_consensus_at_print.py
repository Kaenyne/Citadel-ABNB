# 04_consensus_at_print.py
#
# Reconstructs Street consensus at each of the 23 ABNB prints (4Q20 .. 2Q26) from
# contemporaneous public previews/recaps, and pairs it with the reported actuals.
#
# READS
#   data/processed/abnb_quarterly_kpis_from_study.csv     (actual revenue / adj EBITDA / nights / GBV)
#   data/processed/abnb_revenue_guidance_vs_actual.csv    (next-quarter guide low/high/mid)
#   data/processed/abnb_earnings_reactions.csv            (reaction dates, 1/5/20d excess returns)
#   SOURCES below: literal transcriptions of consensus sentences from archived articles.
#     The archived HTML lives in the session scratchpad (04/cnbc, 04/other, 04/current);
#     every number here carries its publisher, URL, publication timestamp and verbatim quote
#     in data/processed/overnight/04_consensus_sources.csv so a reviewer can re-check it.
#
# WRITES
#   data/processed/overnight/04_consensus_at_print.csv
#   data/processed/overnight/04_consensus_sources.csv
#   data/processed/overnight/04_current_consensus.csv
#
# NOTE ON VENDORS. CNBC quotes LSEG (Refinitiv before Sep-2023) for revenue and EPS and
# StreetAccount/FactSet for the operating KPIs (nights, GBV, adj EBITDA). Zacks runs its own
# panel and disagrees by 0-3%. Both are kept; the LSEG/Refinitiv line is the primary series
# because it is the only vendor quoted consistently across all 23 prints.

import os
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if not os.path.isdir(os.path.join(ROOT, "data")):
    ROOT = r"C:\Users\krish\citadel-abnb-overnight"
DP = os.path.join(ROOT, "data", "processed")
OUT = os.path.join(DP, "overnight")
os.makedirs(OUT, exist_ok=True)

CNBC = {
    "2020Q4": "https://www.cnbc.com/2021/02/25/airbnb-abnb-earnings-q4-2020.html",
    "2021Q1": "https://www.cnbc.com/2021/05/13/airbnb-abnb-earnings-q1-2021.html",
    "2021Q2": "https://www.cnbc.com/2021/08/12/airbnb-abnb-earnings-q2-2021.html",
    "2021Q3": "https://www.cnbc.com/2021/11/04/airbnb-abnbearnings-q3-2021.html",
    "2021Q4": "https://www.cnbc.com/2022/02/15/airbnb-abnb-earnings-q4-2021.html",
    "2022Q1": "https://www.cnbc.com/2022/05/03/airbnb-abnb-earnings-q1-2022.html",
    "2022Q2": "https://www.cnbc.com/2022/08/02/airbnb-abnb-earnings-q2-2022.html",
    "2022Q3": "https://www.cnbc.com/2022/11/02/shares-of-airbnb-tumble-9percent-on-low-fourth-quarter-guidance.html",
    "2022Q4": "https://www.cnbc.com/2023/02/14/airbnb-abnb-earnings-q4-2022-.html",
    "2023Q1": "https://www.cnbc.com/2023/05/09/airbnb-abnb-q1-earnings-report-2023.html",
    "2023Q2": "https://www.cnbc.com/2023/08/03/airbnb-abnb-q2-earnings-report-2023.html",
    "2023Q3": "https://www.cnbc.com/2023/11/01/airbnb-abnb-q3-earnings-report.html",
    "2023Q4": "https://www.cnbc.com/2024/02/13/airbnb-abnb-q4-earnings-2023.html",
    "2024Q1": "https://www.cnbc.com/2024/05/08/airbnb-beats-earnings-expectations-for-first-quarter-but-offers-weaker-than-expected-guidance.html",
    "2024Q2": "https://www.cnbc.com/2024/08/06/airbnb-shares-drop-14percent-on-earnings-miss-as-company-warns-of-slowing-us-demand.html",
    "2024Q3": "https://www.cnbc.com/2024/11/07/airbnb-abnb-q3-earnings-report-2024.html",
    "2024Q4": "https://www.cnbc.com/2025/02/13/airbnb-abnb-q4-earnings-2024.html",
    "2025Q1": "https://www.cnbc.com/2025/05/01/airbnb-q1-earnings-report-2025-.html",
    "2025Q2": "https://www.cnbc.com/2025/08/06/airbnb-beats-on-top-and-bottom-lines-for-second-quarter.html",
    "2025Q3": "https://www.cnbc.com/2025/11/06/airbnb-abnb-q3-results-2025.html",
    "2025Q4": "https://www.cnbc.com/2026/02/12/q4-airbnb-abnb-earnings-2025.html",
    "2026Q1": "https://www.cnbc.com/2026/05/07/airbnb-abnb-earnings-q1-2026.html",
    "2026Q2": "https://www.cnbc.com/2026/08/06/airbnb-abnb-q2-earningsreport.html",
}
YF_Q420 = "https://finance.yahoo.com/news/airbnb-reports-q-4-2020-first-earnings-results-ipo-190849653.html"
ZK_PRE420 = "https://www.nasdaq.com/articles/airbnb-abnb-to-report-q4-earnings:-whats-in-the-cards-2021-02-23"
ZK_1Q22 = "https://www.nasdaq.com/articles/airbnb-inc.-abnb-reports-q1-loss-tops-revenue-estimates"
ZK_3Q22 = "https://www.nasdaq.com/articles/airbnb-abnb-q3-earnings-beat-mark-revenues-increase-y-y"
ZK_2Q25 = "https://www.nasdaq.com/articles/airbnb-inc-abnb-q2-earnings-and-revenues-top-estimates"
RT_3Q21 = "https://www.nasdaq.com/articles/airbnb-forecasts-fourth-quarter-revenue-below-estimates-on-demand-slowdown-fears-2021-11-04"
SS_4Q24 = "https://stockstory.org/us/stocks/nasdaq/abnb/news/earnings/airbnb-nasdaqabnb-exceeds-q4-expectations-stock-jumps-138percent"
SS_2Q26 = "https://stockstory.org/us/stocks/nasdaq/abnb"
TIKR_2Q26 = "https://www.tikr.com/blog/airbnbs-q2-earnings-show-hotels-growing-3x-faster-than-homes"
ZK_DET = "https://www.zacks.com/stock/quote/ABNB/detailed-earnings-estimates"
SA_FC = "https://stockanalysis.com/stocks/abnb/forecast/"

# ---------------------------------------------------------------------------
# SOURCES: one row per consensus quote actually found in a contemporaneous article.
# fields: quarter, publisher, url, published_utc, metric, vendor, value, unit, quote
# ---------------------------------------------------------------------------
SOURCES = [
 ("2020Q4","Yahoo Finance",YF_Q420,"2021-02-25","revenue","unattributed 'Wall Street'",739.7,"musd",
  "Revenue: $859 million vs. $739.7 million expected"),
 ("2020Q4","Yahoo Finance",YF_Q420,"2021-02-25","adj_ebitda","unattributed 'Wall Street'",-132.8,"musd",
  "Adjusted EBIDTA loss: $21 million vs. $132.8 expected"),
 ("2020Q4","Zacks via Nasdaq",ZK_PRE420,"2021-02-23","revenue","Zacks",735.1,"musd",
  "The Zacks Consensus Estimate for revenues currently stands at $735.1 million."),
 ("2020Q4","Zacks via Nasdaq",ZK_PRE420,"2021-02-23","eps","Zacks",-9.18,"usd",
  "the consensus mark for loss has improved by a penny to $9.18 per share over the past 30 days (pre-IPO share count; not comparable)"),
 ("2020Q4","CNBC",CNBC["2020Q4"],"2021-02-25","eps","n/a",None,"usd",
  "CNBC does not compare reported earnings to Wall Street estimates for a company's first report as a public company, as uncertain share counts can skew expectations."),
 ("2020Q4","CNBC",CNBC["2020Q4"],"2021-02-25","positioning","",None,"",
  "Airbnb's stock bounced around, up as much as 4% and down as much as 1%, in after-hours trading"),

 ("2021Q1","CNBC",CNBC["2021Q1"],"2021-05-13","revenue","Refinitiv",714.4,"musd",
  "Revenue: $886.9 million, vs. $714.4 million as expected by analysts, according to Refinitiv."),
 ("2021Q1","CNBC",CNBC["2021Q1"],"2021-05-13","nights","FactSet",62.5,"m",
  "Analysts polled by FactSet had expected 62.5 million nights and experiences booked."),
 ("2021Q1","CNBC",CNBC["2021Q1"],"2021-05-13","gbv","FactSet",7.87,"busd",
  "Gross booking value ... totaled $10.3 billion, up 52% year over year and above the $7.87 billion FactSet consensus."),
 ("2021Q1","Benzinga",
  "https://www.benzinga.com/news/earnings/21/05/21109858/disney-alibaba-coinbase-airbnb-earnings-expected-moves-and-more-ways-to-trade",
  "2021-05-13","positioning","Options AI",None,"",
  "Benzinga/Options AI expected-move preview covering Airbnb's 13-May-2021 print (article gives the method and Disney's ~4% move; ABNB's own implied move is not stated in the retrievable text)."),

 ("2021Q2","CNBC",CNBC["2021Q2"],"2021-08-12","revenue","Refinitiv",1260.0,"musd",
  "Revenue: $1.34 billion vs. $1.26 billion forecast by Refinitiv"),
 ("2021Q2","CNBC",CNBC["2021Q2"],"2021-08-12","nights","StreetAccount",79.2,"m",
  "Analysts polled by StreetAccount had expected 79.2 million nights and experiences booked."),
 ("2021Q2","CNBC",CNBC["2021Q2"],"2021-08-12","gbv","FactSet",11.56,"busd",
  "Gross booking value ... totaled $13.4 billion, up 320% year over year and above the $11.56 billion FactSet consensus."),
 ("2021Q2","CNBC",CNBC["2021Q2"],"2021-08-12","positioning","",None,"",
  "Airbnb's stock on Thursday fell more than 4% after the company reported its second-quarter earnings."),

 ("2021Q3","CNBC",CNBC["2021Q3"],"2021-11-04","revenue","Refinitiv",2050.0,"musd",
  "Revenue: $2.24 billion vs. $2.05 billion estimated by Refinitiv"),
 ("2021Q3","CNBC",CNBC["2021Q3"],"2021-11-04","eps","Refinitiv",None,"usd",
  "Earnings per share: $1.22, which is not comparable to estimates"),
 ("2021Q3","CNBC",CNBC["2021Q3"],"2021-11-04","nights","StreetAccount",80.8,"m",
  "Analysts had estimated 80.8 million nights and experiences for the quarter, according to StreetAccount."),
 ("2021Q3","CNBC",CNBC["2021Q3"],"2021-11-04","gbv","StreetAccount",12.31,"busd",
  "Gross booking value ... totaled $11.89 billion ... fell slightly below a StreetAccount forecast of $12.31 billion."),
 ("2021Q3","CNBC",CNBC["2021Q3"],"2021-11-04","next_q_revenue","unquoted",None,"musd",
  "Airbnb expects revenue between $1.39 billion and $1.48 billion in the fourth quarter, in line with analyst expectations."),
 ("2021Q3","Reuters via Nasdaq",RT_3Q21,"2021-11-04","next_q_revenue_sign","Refinitiv",-1,"sign",
  "Headline: 'Airbnb forecasts fourth-quarter revenue below estimates on demand slowdown fears' (article body not retrievable; direction taken from headline only)."),
 ("2021Q3","CNBC",CNBC["2021Q3"],"2021-11-04","positioning","",None,"",
  "Shares briefly rose more than 3% in after-hours trading before paring gains."),

 ("2021Q4","CNBC",CNBC["2021Q4"],"2022-02-15","revenue","Refinitiv",1460.0,"musd",
  "Revenue: $1.53 billion vs. $1.46 billion expected by Refinitiv"),
 ("2021Q4","CNBC",CNBC["2021Q4"],"2022-02-15","eps","Refinitiv",0.03,"usd",
  "Earnings per share: 8 cents vs. 3 cents expected in a Refinitiv survey of analysts"),
 ("2021Q4","CNBC",CNBC["2021Q4"],"2022-02-15","nights","StreetAccount",74.96,"m",
  "Analysts were expecting 74.96 million nights and experiences for the quarter, according to StreetAccount."),
 ("2021Q4","CNBC",CNBC["2021Q4"],"2022-02-15","gbv","StreetAccount",11.08,"busd",
  "Gross booking value ... totaled $11.3 billion in the fourth quarter, slightly over Wall Street estimates of $11.08 billion, according to StreetAccount."),
 ("2021Q4","CNBC",CNBC["2021Q4"],"2022-02-15","next_q_revenue","unattributed",1240.0,"musd",
  "It estimates revenue to fall between $1.41 billion and $1.48 billion in the first quarter of 2022, topping analyst estimates of $1.24 billion."),
 ("2021Q4","CNBC",CNBC["2021Q4"],"2022-02-15","positioning","",None,"",
  "The company's stock was up around 4% in after hours trading."),

 ("2022Q1","CNBC",CNBC["2022Q1"],"2022-05-03","revenue","Refinitiv",1450.0,"musd",
  "Revenue: $1.51 billion vs $1.45 billion expected, according to Refinitiv."),
 ("2022Q1","CNBC",CNBC["2022Q1"],"2022-05-03","eps","Refinitiv",-0.29,"usd",
  "Loss per share: 3 cents vs 29 cents expected by analysts, according to Refinitiv."),
 ("2022Q1","Zacks via Nasdaq",ZK_1Q22,"2022-05-03","eps","Zacks",-0.28,"usd",
  "came out with a quarterly loss of $0.03 per share versus the Zacks Consensus Estimate of a loss of $0.28"),
 ("2022Q1","Zacks via Nasdaq",ZK_1Q22,"2022-05-03","revenue","Zacks",1452.6,"musd",
  "posted revenues of $1.51 billion for the quarter ended March 2022, surpassing the Zacks Consensus Estimate by 3.88% (implies $1,452.6m)"),
 ("2022Q1","CNBC",CNBC["2022Q1"],"2022-05-03","nights","StreetAccount",100.87,"m",
  "Analysts expected the number to come in at 100.87 million, according to StreetAccount."),
 ("2022Q1","CNBC",CNBC["2022Q1"],"2022-05-03","gbv","StreetAccount",16.54,"busd",
  "Gross booking value ... totaled $17.2 billion in the first quarter, exceeding Wall Street's estimate of $16.54 billion, per StreetAccount."),
 ("2022Q1","CNBC",CNBC["2022Q1"],"2022-05-03","next_q_revenue","unattributed",1960.0,"musd",
  "Airbnb said revenue will be between $2.03 billion and $2.13 billion, topping analysts' average estimate of $1.96 billion."),
 ("2022Q1","Zacks via Nasdaq",ZK_1Q22,"2022-05-03","next_q_revenue","Zacks",1980.0,"musd",
  "The current consensus EPS estimate is $0.31 on $1.98 billion in revenues for the coming quarter (measured immediately after the print, i.e. post-guide)."),
 ("2022Q1","CNBC",CNBC["2022Q1"],"2022-05-03","positioning","",None,"",
  "The shares rose more than 6% in after-hours trading."),

 ("2022Q2","CNBC",CNBC["2022Q2"],"2022-08-02","revenue","Refinitiv",2110.0,"musd",
  "Revenue: $2.10 billion vs. $2.11 billion expected by analysts, according to Refinitiv."),
 ("2022Q2","CNBC",CNBC["2022Q2"],"2022-08-02","eps","Refinitiv",0.43,"usd",
  "Earnings per share: $0.56 vs. $0.43 expected by analysts, according to Refinitiv."),
 ("2022Q2","CNBC",CNBC["2022Q2"],"2022-08-02","nights","StreetAccount",106.4,"m",
  "reported more than 103 million nights and experiences booked ... fell short StreetAccount estimates of 106.4 million"),
 ("2022Q2","CNBC",CNBC["2022Q2"],"2022-08-02","next_q_revenue","StreetAccount",2770.0,"musd",
  "It guided third quarter revenue to land between $2.78 billion and $2.88 billion, ahead of StreetAccount's $2.77 billion estimate."),
 ("2022Q2","CNBC",CNBC["2022Q2"],"2022-08-02","positioning","",None,"",
  "Shares were down about 9% after hours, despite what appeared to be a strong report, suggesting Wall Street was looking for faster growth and a revenue beat."),

 ("2022Q3","CNBC",CNBC["2022Q3"],"2022-11-02","revenue","Refinitiv",2800.0,"musd",
  "The company posted revenue of $2.9 billion ... and topped analysts' estimates of $2.8 billion, according to Refinitiv."),
 ("2022Q3","Zacks via Nasdaq",ZK_3Q22,"2022-11-02","revenue","Zacks",2852.6,"musd",
  "Revenues of $2.9 billion ... surpassed the Zacks Consensus Estimate by 1.1% (implies $2,852.6m)"),
 ("2022Q3","Zacks via Nasdaq",ZK_3Q22,"2022-11-02","eps","Zacks",1.4229,"usd",
  "reported earnings of $1.79 per share for third-quarter 2022, which beat the Zacks Consensus Estimate by 25.8% (implies $1.4229)"),
 ("2022Q3","CNBC",CNBC["2022Q3"],"2022-11-02","next_q_revenue","Refinitiv",1850.0,"musd",
  "Airbnb provided fourth-quarter revenue guidance of $1.80 billion and $1.88 billion, below the midpoint of $1.85 billion as expected by analysts, according to Refinitiv."),
 ("2022Q3","Zacks via Nasdaq",ZK_3Q22,"2022-11-02","next_q_revenue","Zacks",1900.0,"musd",
  "For fourth-quarter 2022 ... The Zacks Consensus Estimate for revenues is pegged at $1.90 billion."),
 ("2022Q3","CNBC",CNBC["2022Q3"],"2022-11-02","positioning","",None,"",
  "Shares of Airbnb fell more than 13% Wednesday, a day after the company released third-quarter earnings that beat Wall Street's estimates but fell short on fourth-quarter guidance. Evercore ISI called the strong-dollar ADR comment the 'key negative'."),

 ("2022Q4","CNBC",CNBC["2022Q4"],"2023-02-14","revenue","Refinitiv",1860.0,"musd",
  "Revenue: $1.90 billion vs. $1.86 billion expected by analysts, according to Refinitiv."),
 ("2022Q4","CNBC",CNBC["2022Q4"],"2023-02-14","eps","Refinitiv",0.25,"usd",
  "EPS: 48 cents vs. 25 cents expected by analysts, according to Refinitiv."),
 ("2022Q4","CNBC",CNBC["2022Q4"],"2023-02-14","adj_ebitda","StreetAccount",432.0,"musd",
  "adjusted earnings before interest, taxes, depreciation, and amortization of $506 million, surpassing the $432 million expected by analysts, according to StreetAccount."),
 ("2022Q4","CNBC",CNBC["2022Q4"],"2023-02-14","nights","StreetAccount",89.7,"m",
  "reported 88.2 million nights and experiences booked in the fourth quarter, up 20% year over year, but below the 89.7 million expected by analysts, according to StreetAccount."),
 ("2022Q4","CNBC",CNBC["2022Q4"],"2023-02-14","next_q_revenue","Refinitiv",1690.0,"musd",
  "revenue in the first quarter will be between $1.75 billion and $1.82 billion, above the $1.69 billion expected by analysts polled by Refinitiv."),
 ("2022Q4","CNBC",CNBC["2022Q4"],"2023-02-14","positioning","",None,"",
  "Shares of Airbnb rose about 9% in extended trading Tuesday."),

 ("2023Q1","CNBC",CNBC["2023Q1"],"2023-05-09","revenue","Refinitiv",1790.0,"musd",
  "Revenue: $1.82 billion vs. $1.79 billion expected"),
 ("2023Q1","CNBC",CNBC["2023Q1"],"2023-05-09","eps","Refinitiv",0.09,"usd",
  "EPS: 18 cents vs. 9 cents expected"),
 ("2023Q1","CNBC",CNBC["2023Q1"],"2023-05-09","nights","StreetAccount",None,"m",
  "121.1 million nights and experiences booked in the first quarter, up 19% year over year, in line with estimates by analysts, according to StreetAccount. (no number quoted)"),
 ("2023Q1","CNBC",CNBC["2023Q1"],"2023-05-09","next_q_revenue","Refinitiv",2420.0,"musd",
  "forecast second-quarter revenue between $2.35 billion and $2.45 billion. Analysts polled by Refinitiv expected $2.42 billion."),
 ("2023Q1","CNBC",CNBC["2023Q1"],"2023-05-09","positioning","",None,"",
  "Shares of Airbnb fell as much as 10% in extended trading Tuesday despite first-quarter earnings that beat analyst estimates on the top and bottom lines."),

 ("2023Q2","CNBC",CNBC["2023Q2"],"2023-08-03","revenue","Refinitiv",2420.0,"musd",
  "Revenue: $2.48 billion, vs. $2.42 billion as expected by analysts, according to Refinitiv"),
 ("2023Q2","CNBC",CNBC["2023Q2"],"2023-08-03","eps","Refinitiv",0.78,"usd",
  "Earnings: 98 cents per share, vs. 78 cents per share as expected by analysts, according to Refinitiv"),
 ("2023Q2","CNBC",CNBC["2023Q2"],"2023-08-03","nights","StreetAccount",117.6,"m",
  "115.1 million nights and experiences booked during the quarter, up almost 11%, but less than the 117.6 million StreetAccount consensus."),
 ("2023Q2","CNBC",CNBC["2023Q2"],"2023-08-03","gbv","StreetAccount",18.99,"busd",
  "$19.1 billion in gross booking value for the quarter ... above the $18.99 billion consensus among analysts surveyed by StreetAccount."),
 ("2023Q2","CNBC",CNBC["2023Q2"],"2023-08-03","next_q_revenue","Refinitiv",3220.0,"musd",
  "Airbnb called for $3.3 billion to $3.4 billion in third-quarter revenue ... Analysts polled by Refinitiv had been looking for $3.22 billion."),
 ("2023Q2","CNBC",CNBC["2023Q2"],"2023-08-03","positioning","",None,"",
  "Airbnb shares slid as much as 6% in extended trading Thursday ... Notwithstanding the after-hours move, Airbnb shares have risen about 64% so far this year."),

 ("2023Q3","CNBC",CNBC["2023Q3"],"2023-11-01","revenue","LSEG",3370.0,"musd",
  "Revenue: $3.40 billion, vs. $3.37 billion expected"),
 ("2023Q3","CNBC",CNBC["2023Q3"],"2023-11-01","eps","LSEG",2.10,"usd",
  "Earnings: $6.63 per share. That may not be comparable to the $2.10 expected by analysts, according to LSEG"),
 ("2023Q3","CNBC",CNBC["2023Q3"],"2023-11-01","nights","StreetAccount",112.9,"m",
  "Total nights and experiences bookings came in at 113.2 million for the quarter ... beating a StreetAccount consensus estimate of 112.9 million."),
 ("2023Q3","CNBC",CNBC["2023Q3"],"2023-11-01","next_q_revenue","LSEG",2180.0,"musd",
  "The company guided to $2.13 billion to $2.17 billion in fourth-quarter revenue ... That was less than the $2.18 billion that analysts polled by LSEG had been expecting."),
 ("2023Q3","CNBC",CNBC["2023Q3"],"2023-11-01","positioning","",None,"",
  "Airbnb shares slipped about 3% in after-hours trading Wednesday."),

 ("2023Q4","CNBC",CNBC["2023Q4"],"2024-02-13","revenue","LSEG",2170.0,"musd",
  "Revenue: $2.22 billion vs. $2.17 billion expected by analysts, according to LSEG"),
 ("2023Q4","CNBC",CNBC["2023Q4"],"2024-02-13","eps","LSEG",0.62,"usd",
  "Loss per share: 55 cents. It's not immediately clear if that's comparable to the profit estimate of 62 cents, according to LSEG"),
 ("2023Q4","CNBC",CNBC["2023Q4"],"2024-02-13","adj_ebitda","StreetAccount",645.0,"musd",
  "Airbnb posted adjusted earnings of $738 million in the fourth quarter. Analysts were expecting $645 million, according to StreetAccount."),
 ("2023Q4","CNBC",CNBC["2023Q4"],"2024-02-13","nights","StreetAccount",98.0,"m",
  "reported 98.8 million nights and experiences booked, up 12% from a year ago, and above the 98 million expected by analysts, according to StreetAccount."),
 ("2023Q4","CNBC",CNBC["2023Q4"],"2024-02-13","next_q_revenue","LSEG",2030.0,"musd",
  "Airbnb said revenue in the first quarter will be between $2.03 billion and $2.07 billion, while Wall Street was expecting $2.03 billion, according to LSEG."),
 ("2023Q4","CNBC",CNBC["2023Q4"],"2024-02-13","positioning","",None,"",
  "The stock fell more than 4% in extended trading."),

 ("2024Q1","CNBC",CNBC["2024Q1"],"2024-05-08","revenue","LSEG",2060.0,"musd",
  "Revenue: $2.14 billion vs. $2.06 billion expected"),
 ("2024Q1","CNBC",CNBC["2024Q1"],"2024-05-08","eps","LSEG",0.24,"usd",
  "Earnings per share: 41 cents vs. 24 cents expected"),
 ("2024Q1","CNBC",CNBC["2024Q1"],"2024-05-08","adj_ebitda","StreetAccount",326.0,"musd",
  "adjusted EBITDA for the first quarter was $424 million, up 62% year over year. Analysts polled by StreetAccount were expecting $326 million."),
 ("2024Q1","CNBC",CNBC["2024Q1"],"2024-05-08","nights","StreetAccount",132.1,"m",
  "reported 132.6 million nights and experiences booked, up 9.5% from a year ago, and higher than the 132.1 million expected by analysts, according to StreetAccount."),
 ("2024Q1","CNBC",CNBC["2024Q1"],"2024-05-08","next_q_revenue","LSEG",2740.0,"musd",
  "revenue in its second quarter will come in between $2.68 billion and $2.74 billion. Analysts were expecting $2.74 billion for the period, according to LSEG."),
 ("2024Q1","CNBC",CNBC["2024Q1"],"2024-05-08","positioning","",None,"",
  "Shares fell more than 6% in extended trading."),

 ("2024Q2","CNBC",CNBC["2024Q2"],"2024-08-06","revenue","LSEG",2740.0,"musd",
  "Revenue: $2.75 billion vs. $2.74 billion expected"),
 ("2024Q2","CNBC",CNBC["2024Q2"],"2024-08-06","eps","LSEG",0.92,"usd",
  "Earnings per share: 86 cents vs. 92 cents expected"),
 ("2024Q2","CNBC",CNBC["2024Q2"],"2024-08-06","next_q_revenue","not found",None,"musd",
  "CNBC quotes the guide ($3.67-3.73bn) but no Street number; no other contemporaneous source with a Q3-2024 consensus figure was retrievable (WebSearch budget exhausted, DuckDuckGo/Reuters blocked). LEFT BLANK."),
 ("2024Q2","CNBC",CNBC["2024Q2"],"2024-08-06","positioning","",None,"",
  "Airbnb shares dropped 14% in after-hours trading ... warned it was 'seeing shorter booking lead times globally and some signs of slowing demand from U.S. guests.'"),

 ("2024Q3","CNBC",CNBC["2024Q3"],"2024-11-07","revenue","LSEG",3720.0,"musd",
  "Revenue: $3.73 billion vs. $3.72 billion expected by LSEG"),
 ("2024Q3","CNBC",CNBC["2024Q3"],"2024-11-07","eps","LSEG",2.14,"usd",
  "Earnings per share: $2.13 vs. $2.14 expected by LSEG"),
 ("2024Q3","CNBC",CNBC["2024Q3"],"2024-11-07","adj_ebitda","StreetAccount",1860.0,"musd",
  "adjusted EBITDA for the third quarter was $2 billion, up 7% year over year. Analysts polled by StreetAccount were expecting $1.86 billion."),
 ("2024Q3","CNBC",CNBC["2024Q3"],"2024-11-07","nights","StreetAccount",121.4,"m",
  "reported 123 million nights and experiences booked, up 8% from a year ago and higher than the 121.4 million expected by StreetAccount."),
 ("2024Q3","CNBC",CNBC["2024Q3"],"2024-11-07","gbv","StreetAccount",19.9,"busd",
  "Gross booking value ... totaled $20.1 billion ... That's above the $19.9 billion expected by analysts, according to StreetAccount."),
 ("2024Q3","CNBC",CNBC["2024Q3"],"2024-11-07","next_q_revenue","LSEG",2420.0,"musd",
  "expects to report revenue between $2.39 billion and $2.44 billion during its fourth quarter. Analysts were expecting $2.42 billion for the period, according to LSEG."),
 ("2024Q3","CNBC",CNBC["2024Q3"],"2024-11-07","positioning","",None,"",
  "The stock fell about 3% in after-hours trading."),

 ("2024Q4","CNBC",CNBC["2024Q4"],"2025-02-13","revenue","LSEG",2420.0,"musd",
  "Revenue: $2.48 billion vs. $2.42 billion expected"),
 ("2024Q4","CNBC",CNBC["2024Q4"],"2025-02-13","eps","LSEG",0.58,"usd",
  "Earnings per share: 73 cents vs. 58 cents expected"),
 ("2024Q4","CNBC",CNBC["2024Q4"],"2025-02-13","adj_ebitda","StreetAccount",653.5,"musd",
  "adjusted profit for the fourth quarter was $765 million, up 4% year over year. Analysts were expecting $653.5 million, according to StreetAccount."),
 ("2024Q4","CNBC",CNBC["2024Q4"],"2025-02-13","nights","StreetAccount",108.7,"m",
  "reported 111 million nights and experiences booked, up 12% from a year ago and above the 108.7 million expected by StreetAccount."),
 ("2024Q4","CNBC",CNBC["2024Q4"],"2025-02-13","gbv","StreetAccount",17.2,"busd",
  "Gross booking value ... totaled $17.6 billion ... That is above the $17.2 billion expected by analysts polled by StreetAccount."),
 ("2024Q4","CNBC",CNBC["2024Q4"],"2025-02-13","next_q_revenue","LSEG",2300.0,"musd",
  "In the first quarter, Airbnb expects to report revenue between $2.23 billion and $2.27 billion. Analysts were expecting $2.3 billion for the period, according to LSEG."),
 ("2024Q4","StockStory",SS_4Q24,"2025-02-13","next_q_revenue","S&P Global / Visible Alpha",2301.0,"musd",
  "next quarter's revenue guidance of $2.25 billion was less impressive, coming in 2.2% below analysts' estimates (implies $2,301m)"),
 ("2024Q4","CNBC",CNBC["2024Q4"],"2025-02-13","positioning","",None,"",
  "Airbnb shares jumped 15% in extended trading on Thursday."),

 ("2025Q1","CNBC",CNBC["2025Q1"],"2025-05-01","revenue","LSEG",2260.0,"musd",
  "Revenue: $2.27 billion vs. $2.26 billion expected"),
 ("2025Q1","CNBC",CNBC["2025Q1"],"2025-05-01","eps","LSEG",0.24,"usd",
  "Earnings per share: 24 cents vs. 24 cents expected"),
 ("2025Q1","Zacks via Nasdaq",ZK_2Q25,"2025-08-06","eps","Zacks",0.25,"usd",
  "A quarter ago, it was expected that this company would post earnings of $0.25 per share when it actually produced earnings of $0.24, delivering a surprise of -4%."),
 ("2025Q1","CNBC",CNBC["2025Q1"],"2025-05-01","nights","StreetAccount",143.4,"m",
  "Nights and experiences booked rose 8% from a year ago and totaled 143.1 million, compared to the 143.4 million estimate from analysts."),
 ("2025Q1","CNBC",CNBC["2025Q1"],"2025-05-01","next_q_revenue","LSEG",3040.0,"musd",
  "expects revenue of between $2.99 billion and $3.05 billion, or $3.02 billion at the middle of the range. Analysts had forecast $3.04 billion in revenue for the current period."),
 ("2025Q1","CNBC",CNBC["2025Q1"],"2025-05-01","positioning","",None,"",
  "results ... mostly in line with estimates, but the company issued a disappointing revenue forecast for the current period."),

 ("2025Q2","CNBC",CNBC["2025Q2"],"2025-08-06","revenue","LSEG",3040.0,"musd",
  "Revenue: $3.10 billion vs. $3.04 billion expected"),
 ("2025Q2","CNBC",CNBC["2025Q2"],"2025-08-06","eps","LSEG",0.93,"usd",
  "Earnings per share: $1.03 vs. 93 cents expected"),
 ("2025Q2","Zacks via Nasdaq",ZK_2Q25,"2025-08-06","revenue","Zacks",3038.9,"musd",
  "posted revenues of $3.1 billion for the quarter ended June 2025, surpassing the Zacks Consensus Estimate by 2.01% (implies $3,038.9m)"),
 ("2025Q2","CNBC",CNBC["2025Q2"],"2025-08-06","nights","StreetAccount",133.35,"m",
  "reported 134.4 million nights and seats booked, up 7% from a year ago and above the 133.35 million expected by StreetAccount."),
 ("2025Q2","CNBC",CNBC["2025Q2"],"2025-08-06","gbv","StreetAccount",22.66,"busd",
  "Gross booking value ... totaled $23.5 billion in the second quarter. That figure is above the $22.66 billion expected by analysts polled by StreetAccount."),
 ("2025Q2","CNBC",CNBC["2025Q2"],"2025-08-06","next_q_revenue","LSEG",4050.0,"musd",
  "In the third quarter, Airbnb expects to report revenue of $4.02 billion to $4.10 billion, or $4.06 billion in the middle of the range. Analysts were expecting $4.05 billion for the period, according to LSEG."),
 ("2025Q2","Zacks via Nasdaq",ZK_2Q25,"2025-08-06","next_q_revenue","Zacks",4040.0,"musd",
  "The current consensus EPS estimate is $2.26 on $4.04 billion in revenues for the coming quarter (post-guide snapshot)."),

 ("2025Q3","CNBC",CNBC["2025Q3"],"2025-11-06","revenue","LSEG",4080.0,"musd",
  "Revenue: $4.10 billion vs. $4.08 billion expected"),
 ("2025Q3","CNBC",CNBC["2025Q3"],"2025-11-06","eps","LSEG",2.34,"usd",
  "Earnings per share: $2.21 vs. $2.34 cents expected (CNBC typo; $2.34 per share)"),
 ("2025Q3","Zacks",ZK_DET,"2026-09-04","eps","Zacks",2.29,"usd",
  "Surprise table, quarter ending 9/2025: Reported 2.21, Estimate 2.29, Surprise -3.49%."),
 ("2025Q3","CNBC",CNBC["2025Q3"],"2025-11-06","nights","StreetAccount",131.75,"m",
  "reported 133.6 million nights and seats booked, up 9% from a year ago and above the 131.75 million expected by StreetAccount."),
 ("2025Q3","CNBC",CNBC["2025Q3"],"2025-11-06","gbv","StreetAccount",21.9,"busd",
  "Gross booking value ... totaled $22.9 billion in the third quarter, up 14% year over year. That figure is above the $21.9 billion expected by analysts polled by StreetAccount."),
 ("2025Q3","CNBC",CNBC["2025Q3"],"2025-11-06","next_q_revenue","LSEG",2670.0,"musd",
  "For the fourth quarter, Airbnb said it expects to report revenue of $2.66 billion to $2.72 billion. Analysts were expecting $2.67 billion for the period, according to LSEG."),
 ("2025Q3","CNBC",CNBC["2025Q3"],"2025-11-06","positioning","",None,"",
  "Shares of Airbnb rose as much as 5% in extended trading on Thursday."),

 ("2025Q4","CNBC",CNBC["2025Q4"],"2026-02-12","revenue","LSEG",2720.0,"musd",
  "Revenue: $2.78 billion vs. $2.72 billion expected"),
 ("2025Q4","CNBC",CNBC["2025Q4"],"2026-02-12","eps","LSEG",0.66,"usd",
  "Earnings per share: 56 cents vs. 66 cents expected"),
 ("2025Q4","Zacks",ZK_DET,"2026-09-04","eps","Zacks",0.66,"usd",
  "Surprise table, quarter ending 12/2025: Reported 0.56, Estimate 0.66, Surprise -15.15%."),
 ("2025Q4","CNBC",CNBC["2025Q4"],"2026-02-12","nights","StreetAccount",117.6,"m",
  "reported 121.9 million nights and seats booked in the fourth quarter, up 10% from a year ago and above the 117.6 million expected by StreetAccount."),
 ("2025Q4","CNBC",CNBC["2025Q4"],"2026-02-12","gbv","StreetAccount",19.4,"busd",
  "Gross booking value ... totaled $20.4 billion in the fourth quarter, up 16% year over year. That figure is above the $19.4 billion expected by analysts polled by StreetAccount."),
 ("2025Q4","CNBC",CNBC["2025Q4"],"2026-02-12","next_q_revenue","LSEG",2530.0,"musd",
  "For the current period, Airbnb said it expects to report revenue of $2.59 billion to $2.63 billion. Analysts were expecting $2.53 billion for the quarter, according to LSEG."),
 ("2025Q4","CNBC",CNBC["2025Q4"],"2026-02-12","fy_growth","LSEG",10.2,"pct",
  "The company said it expects full-year revenue growth of 'at least low double digits.' Analysts were expecting 10.2% growth."),
 ("2025Q4","CNBC",CNBC["2025Q4"],"2026-02-12","positioning","FactSet",None,"",
  "Shares ... up about 2% in extended trading. 'Airbnb has beat Wall Street's revenue expectations for 20 of the past 21 quarters, according to FactSet.'"),

 ("2026Q1","CNBC",CNBC["2026Q1"],"2026-05-07","revenue","LSEG",2620.0,"musd",
  "Revenue: $2.68 billion vs. $2.62 billion expected"),
 ("2026Q1","CNBC",CNBC["2026Q1"],"2026-05-07","eps","LSEG",0.29,"usd",
  "Earnings per share: 26 cents vs. 29 cents expected"),
 ("2026Q1","Zacks",ZK_DET,"2026-09-04","eps","Zacks",0.31,"usd",
  "Surprise table, quarter ending 3/2026: Reported 0.26, Estimate 0.31, Surprise -16.13%."),
 ("2026Q1","CNBC",CNBC["2026Q1"],"2026-05-07","adj_ebitda","LSEG",485.0,"musd",
  "Airbnb reported $519 million in adjusted EBITDA, which surpassed a $485 million estimate from LSEG."),
 ("2026Q1","CNBC",CNBC["2026Q1"],"2026-05-07","nights","LSEG",155.77,"m",
  "Nights and seats booked grew 9% to 156.2 million, surpassing LSEG's 155.77 million estimate."),
 ("2026Q1","CNBC",CNBC["2026Q1"],"2026-05-07","gbv","unattributed",27.82,"busd",
  "Gross booking value ... increased 19% to $29.2 billion, topping a $27.82 billion estimate from analysts."),
 ("2026Q1","CNBC",CNBC["2026Q1"],"2026-05-07","next_q_revenue","LSEG",3460.0,"musd",
  "For the current quarter, Airbnb issued an upbeat forecast, calling for revenue between $3.54 billion and $3.60 billion. Analysts expected $3.46 billion in revenue."),
 ("2026Q1","CNBC",CNBC["2026Q1"],"2026-05-07","positioning","",None,"",
  "The company lifted revenue guidance for the year to 'low to mid teens' growth from a 12% forecast; flagged a 100bp nights headwind in Q2 from the war."),

 ("2026Q2","CNBC",CNBC["2026Q2"],"2026-08-06","revenue","LSEG",3580.0,"musd",
  "Revenue: $3.61 billion vs. $3.58 billion expected"),
 ("2026Q2","CNBC",CNBC["2026Q2"],"2026-08-06","eps","LSEG",1.25,"usd",
  "Earnings per share: $1.37 vs. $1.25 expected"),
 ("2026Q2","TIKR",TIKR_2Q26,"2026-08-07","revenue","S&P Global Capital IQ",3576.0,"musd",
  "Revenue climbed to $3.608 billion ... 0.90% above Street estimates (implies $3,576m)"),
 ("2026Q2","TIKR",TIKR_2Q26,"2026-08-07","adj_ebitda","S&P Global Capital IQ",1225.6,"musd",
  "adjusted EBITDA reached $1.261 billion, a 2.89% beat (implies $1,225.6m)"),
 ("2026Q2","TIKR",TIKR_2Q26,"2026-08-07","eps","S&P Global Capital IQ",1.25,"usd",
  "Adjusted EPS of $1.37 cleared the $1.25 estimate by 10.04%"),
 ("2026Q2","Zacks",ZK_DET,"2026-09-04","eps","Zacks",1.20,"usd",
  "Surprise table, quarter ending 6/2026: Reported 1.37, Estimate 1.20, Surprise 14.17%."),
 ("2026Q2","StockStory",SS_2Q26,"2026-08-06","revenue","S&P Global / Visible Alpha",3579.0,"musd",
  "its $3.61 billion of revenue exceeded Wall Street's estimates by 0.8% (implies $3,579m)"),
 ("2026Q2","CNBC",CNBC["2026Q2"],"2026-08-06","next_q_revenue","LSEG",4610.0,"musd",
  "it expects revenue of between $4.69 billion and $4.77 billion, while analysts had been projecting sales of $4.61 billion, according to LSEG."),
 ("2026Q2","CNBC",CNBC["2026Q2"],"2026-08-06","positioning","",None,"",
  "The stock jumped 9% in extended trading on Thursday; it closed the next session +17% near $178, a four-year high (TIKR)."),
]

# ---------------------------------------------------------------------------
# PRIMARY consensus series (LSEG/Refinitiv where quoted; vendor noted otherwise)
# quarter -> dict of primary consensus values + confidence
# ---------------------------------------------------------------------------
PRIMARY = {
 #            rev_cons  rev_vendor  eps_cons  eps_comp  ebitda   nights  gbv    nextq   nextq_vendor  conf
 "2020Q4": dict(rev=739.7, rev_v="Yahoo/unattributed", eps=None,  eps_comp=0, ebitda=-132.8, nights=None,  gbv=None,  nq=None,   nq_v="", conf="medium",
                note="First post-IPO print; CNBC declined to compare EPS (share count). Zacks rev $735.1m agrees within 0.6%. No numeric next-quarter revenue guide was given."),
 "2021Q1": dict(rev=714.4, rev_v="Refinitiv", eps=None, eps_comp=0, ebitda=None, nights=62.5, gbv=7.87, nq=None, nq_v="", conf="high",
                note="No numeric next-quarter revenue guide (qualitative only)."),
 "2021Q2": dict(rev=1260.0, rev_v="Refinitiv", eps=None, eps_comp=0, ebitda=None, nights=79.2, gbv=11.56, nq=None, nq_v="", conf="high",
                note="No numeric next-quarter revenue guide. EPS consensus not quoted by CNBC."),
 "2021Q3": dict(rev=2050.0, rev_v="Refinitiv", eps=None, eps_comp=0, ebitda=None, nights=80.8, gbv=12.31, nq=None, nq_v="", conf="high",
                note="EPS 'not comparable to estimates'. First numeric revenue guide ($1.39-1.48bn); CNBC called it in line, Reuters headline called it below estimates -> sign recorded as -1, magnitude unknown."),
 "2021Q4": dict(rev=1460.0, rev_v="Refinitiv", eps=0.03, eps_comp=1, ebitda=None, nights=74.96, gbv=11.08, nq=1240.0, nq_v="CNBC unattributed", conf="medium",
                note="Next-quarter consensus of $1.24bn is unattributed and implies a 16% guide-above-Street, far outside every other observation; treat as low-confidence."),
 "2022Q1": dict(rev=1450.0, rev_v="Refinitiv", eps=-0.29, eps_comp=1, ebitda=None, nights=100.87, gbv=16.54, nq=1960.0, nq_v="CNBC unattributed", conf="high",
                note="Zacks EPS -0.28 and revenue $1,452.6m corroborate. Zacks post-print next-quarter revenue $1.98bn vs the $1.96bn pre-guide number."),
 "2022Q2": dict(rev=2110.0, rev_v="Refinitiv", eps=0.43, eps_comp=1, ebitda=None, nights=106.4, gbv=None, nq=2770.0, nq_v="StreetAccount", conf="high",
                note="Only revenue MISS vs consensus in the sample. $2bn buyback announced same day."),
 "2022Q3": dict(rev=2800.0, rev_v="Refinitiv", eps=1.4229, eps_comp=1, ebitda=None, nights=None, gbv=None, nq=1850.0, nq_v="Refinitiv", conf="medium",
                note="EPS consensus derived from the Zacks +25.8% surprise (Zacks panel, not LSEG). Zacks revenue $2,852.6m vs Refinitiv $2.80bn - a 1.9% vendor gap that flips the size of the beat."),
 "2022Q4": dict(rev=1860.0, rev_v="Refinitiv", eps=0.25, eps_comp=1, ebitda=432.0, nights=89.7, gbv=None, nq=1690.0, nq_v="Refinitiv", conf="high", note=""),
 "2023Q1": dict(rev=1790.0, rev_v="Refinitiv", eps=0.09, eps_comp=1, ebitda=None, nights=None, gbv=None, nq=2420.0, nq_v="Refinitiv", conf="high",
                note="Nights described as 'in line' with StreetAccount but no number quoted."),
 "2023Q2": dict(rev=2420.0, rev_v="Refinitiv", eps=0.78, eps_comp=1, ebitda=None, nights=117.6, gbv=18.99, nq=3220.0, nq_v="Refinitiv", conf="high", note=""),
 "2023Q3": dict(rev=3370.0, rev_v="LSEG", eps=2.10, eps_comp=0, ebitda=None, nights=112.9, gbv=None, nq=2180.0, nq_v="LSEG", conf="high",
                note="GAAP EPS $6.63 includes the deferred-tax valuation-allowance release; CNBC flags it as not comparable, so the EPS surprise is dropped."),
 "2023Q4": dict(rev=2170.0, rev_v="LSEG", eps=0.62, eps_comp=0, ebitda=645.0, nights=98.0, gbv=None, nq=2030.0, nq_v="LSEG", conf="high",
                note="GAAP loss per share -$0.55 (one-off tax); CNBC flags not comparable. Adj EBITDA surprise is clean."),
 "2024Q1": dict(rev=2060.0, rev_v="LSEG", eps=0.24, eps_comp=1, ebitda=326.0, nights=132.1, gbv=None, nq=2740.0, nq_v="LSEG", conf="high", note=""),
 "2024Q2": dict(rev=2740.0, rev_v="LSEG", eps=0.92, eps_comp=1, ebitda=None, nights=None, gbv=None, nq=None, nq_v="", conf="medium",
                note="NEXT-QUARTER CONSENSUS NOT FOUND. CNBC quotes only the $3.67-3.73bn guide; no other contemporaneous source retrievable. This is the single next-quarter gap in the sample."),
 "2024Q3": dict(rev=3720.0, rev_v="LSEG", eps=2.14, eps_comp=1, ebitda=1860.0, nights=121.4, gbv=19.9, nq=2420.0, nq_v="LSEG", conf="high", note=""),
 "2024Q4": dict(rev=2420.0, rev_v="LSEG", eps=0.58, eps_comp=1, ebitda=653.5, nights=108.7, gbv=17.2, nq=2300.0, nq_v="LSEG", conf="high",
                note="StockStory (S&P Global/Visible Alpha) independently puts the next-quarter consensus at $2,301m - agrees with LSEG to 0.04%."),
 "2025Q1": dict(rev=2260.0, rev_v="LSEG", eps=0.24, eps_comp=1, ebitda=None, nights=143.4, gbv=None, nq=3040.0, nq_v="LSEG", conf="high",
                note="Zacks EPS consensus 0.25 vs LSEG 0.24 - the same print is a small miss on Zacks and a dead-in-line on LSEG."),
 "2025Q2": dict(rev=3040.0, rev_v="LSEG", eps=0.93, eps_comp=1, ebitda=None, nights=133.35, gbv=22.66, nq=4050.0, nq_v="LSEG", conf="high", note=""),
 "2025Q3": dict(rev=4080.0, rev_v="LSEG", eps=2.34, eps_comp=1, ebitda=None, nights=131.75, gbv=21.9, nq=2670.0, nq_v="LSEG", conf="high",
                note="Zacks EPS consensus 2.29 vs LSEG 2.34: miss of -3.5% vs -5.6%."),
 "2025Q4": dict(rev=2720.0, rev_v="LSEG", eps=0.66, eps_comp=1, ebitda=None, nights=117.6, gbv=19.4, nq=2530.0, nq_v="LSEG", conf="high",
                note="FY26 growth guide 'at least low double digits' vs 10.2% consensus growth."),
 "2026Q1": dict(rev=2620.0, rev_v="LSEG", eps=0.29, eps_comp=1, ebitda=485.0, nights=155.77, gbv=27.82, nq=3460.0, nq_v="LSEG", conf="high", note=""),
 "2026Q2": dict(rev=3580.0, rev_v="LSEG", eps=1.25, eps_comp=1, ebitda=1225.6, nights=None, gbv=None, nq=4610.0, nq_v="LSEG", conf="high",
                note="EBITDA consensus derived from TIKR's '+2.89% beat'. Zacks EPS consensus 1.20 vs LSEG 1.25."),
}

# EPS actuals as reported in the same articles (mixed basis - see eps_basis)
EPS_ACTUAL = {
 "2020Q4": (None, "n/a"), "2021Q1": (None, "n/a"), "2021Q2": (None, "n/a"),
 "2021Q3": (1.22, "GAAP diluted, flagged not comparable"),
 "2021Q4": (0.08, "adjusted"), "2022Q1": (-0.03, "adjusted"), "2022Q2": (0.56, "adjusted"),
 "2022Q3": (1.79, "adjusted (Zacks basis)"), "2022Q4": (0.48, "adjusted"), "2023Q1": (0.18, "adjusted"),
 "2023Q2": (0.98, "adjusted"), "2023Q3": (6.63, "GAAP incl. tax valuation allowance release - not comparable"),
 "2023Q4": (-0.55, "GAAP loss - not comparable"), "2024Q1": (0.41, "adjusted"), "2024Q2": (0.86, "adjusted"),
 "2024Q3": (2.13, "adjusted"), "2024Q4": (0.73, "adjusted"), "2025Q1": (0.24, "adjusted"),
 "2025Q2": (1.03, "adjusted"), "2025Q3": (2.21, "adjusted"), "2025Q4": (0.56, "adjusted"),
 "2026Q1": (0.26, "adjusted"), "2026Q2": (1.37, "adjusted"),
}

# Current (post-2Q26) Street numbers, captured 4-5 Sep 2026
CURRENT = [
 ("2026Q3","revenue","Zacks",4740.0,"musd",7,4720.0,4770.0,"2026-09-04",ZK_DET,
  "Sales Estimates, Current Qtr (9/2026): Zacks Consensus Estimate 4.74B, # of Estimates 7, High 4.77B, Low 4.72B, YoY growth est 15.79%"),
 ("2026Q3","eps_adj","Zacks",2.87,"usd",11,2.52,3.28,"2026-09-04",ZK_DET,
  "Earnings Estimates, Current Qtr (9/2026): Zacks Consensus 2.87, # of Estimates 11, High 3.28, Low 2.52; Most Accurate 2.88, Earnings ESP +0.45%; expected report date 11/5/26"),
 ("2026Q4","revenue","Zacks",3200.0,"musd",10,3050.0,3700.0,"2026-09-04",ZK_DET,
  "Sales Estimates, Next Qtr (12/2026): 3.20B, 10 estimates, High 3.70B, Low 3.05B"),
 ("2026Q4","eps_adj","Zacks",0.82,"usd",10,0.67,0.96,"2026-09-04",ZK_DET,
  "Earnings Estimates, Next Qtr (12/2026): 0.82, 10 estimates, High 0.96, Low 0.67"),
 ("FY2026","revenue","Zacks",14100.0,"musd",8,13960.0,14210.0,"2026-09-04",ZK_DET,
  "Sales Estimates, Current Year (12/2026): 14.10B, 8 estimates, High 14.21B, Low 13.96B, YoY +15.21%"),
 ("FY2026","eps_adj","Zacks",5.23,"usd",13,4.85,5.74,"2026-09-04",ZK_DET,
  "Earnings Estimates, Current Year (12/2026): 5.23, 13 estimates, High 5.74, Low 4.85 (was 4.91 sixty days ago)"),
 ("FY2027","revenue","Zacks",15730.0,"musd",13,14990.0,16290.0,"2026-09-04",ZK_DET,
  "Sales Estimates, Next Year (12/2027): 15.73B, 13 estimates, High 16.29B, Low 14.99B, YoY +11.51%"),
 ("FY2027","eps_adj","Zacks",6.02,"usd",13,5.35,6.80,"2026-09-04",ZK_DET,
  "Earnings Estimates, Next Year (12/2027): 6.02, 13 estimates, High 6.80, Low 5.35"),
 ("FY2026","revenue","S&P Global Market Intelligence",14160.0,"musd",43,13800.0,14300.0,"2026-09-03",SA_FC,
  "Revenue This Year 14.16B from 12.24B (+15.64%); Revenue Forecast 2026 High 14.3B / Avg 14.2B / Low 13.8B; No. Analysts 43"),
 ("FY2026","eps_adj","S&P Global Market Intelligence",5.28,"usd",43,5.00,5.91,"2026-09-03",SA_FC,
  "EPS This Year 5.28 from 4.03 (+31.04%); EPS Forecast 2026 High 5.91 / Avg 5.28 / Low 5.00. 'EPS and Forward PE are based on non-GAAP adjusted numbers.'"),
 ("FY2027","revenue","S&P Global Market Intelligence",15760.0,"musd",None,None,None,"2026-09-03",SA_FC,
  "Revenue Next Year 15.76B from 14.16B (+11.32%)"),
 ("FY2027","eps_adj","S&P Global Market Intelligence",6.14,"usd",None,None,None,"2026-09-03",SA_FC,
  "EPS Next Year 6.14 from 5.28 (+16.27%)"),
 ("FY2026","free_cash_flow","S&P Global Market Intelligence",5350.0,"musd",None,None,None,"2026-09-03",SA_FC,
  "Free Cash Flow FY2026 5.35B (vs 3.54B FY2025)"),
 ("FY2026","operating_income","S&P Global Market Intelligence",3160.0,"musd",None,None,None,"2026-09-03",SA_FC,
  "Operating Income FY2026 3.16B (vs 2.54B FY2025)"),
 ("NTM","price_target","S&P Global / TipRanks",178.96,"usd",46,125.0,220.0,"2026-09-03",SA_FC,
  "46 analysts polled by S&P Global: consensus rating 'Buy', average price target $178.96 (low $125, high $220) vs $181.94 close 4-Sep-2026"),
 ("NTM","price_target","S&P Global / Visible Alpha via StockStory",179.46,"usd",None,None,None,"2026-08-07",SS_2Q26,
  "Wall Street analysts have a consensus one-year price target of $179.46 on the company (compared to the current share price of $182.02)"),
 ("FY2026","eps_adj","S&P Global / Visible Alpha via StockStory",5.37,"usd",None,None,None,"2026-08-07",SS_2Q26,
  "Over the next 12 months, Wall Street expects Airbnb's full-year EPS to grow 22% from $4.40 to $5.37 (NTM basis, not calendar FY26)"),
 ("2026Q3","adj_ebitda","derived",None,"musd",None,None,None,"2026-09-06","",
  "NO published Q3-2026 adjusted-EBITDA or nights consensus was retrievable. Company FY guide: adj EBITDA margin at least 35.5%, revenue growth at least mid-teens."),
]


def main():
    kpi = pd.read_csv(os.path.join(DP, "abnb_quarterly_kpis_from_study.csv"))
    kpi["quarter"] = kpi["quarter"].str[2:] + "Q" + kpi["quarter"].str[0]   # 1Q21 -> 21Q1
    kpi["quarter"] = "20" + kpi["quarter"]
    kpi = kpi.set_index("quarter")

    guide = pd.read_csv(os.path.join(DP, "abnb_revenue_guidance_vs_actual.csv"))
    guide_by_issuer = guide.set_index("issued_on_call")

    react = pd.read_csv(os.path.join(DP, "abnb_earnings_reactions.csv")).set_index("quarter")

    rows = []
    for q, p in PRIMARY.items():
        rev_act = 859.0 if q == "2020Q4" else float(kpi.at[q, "revenue_musd"])
        eb_act = -21.0 if q == "2020Q4" else (float(kpi.at[q, "adj_ebitda_musd"]) if q in kpi.index else None)
        ni_act = None if q == "2020Q4" else float(kpi.at[q, "nights_m"])
        gb_act = None if q == "2020Q4" else float(kpi.at[q, "gbv_b"])
        eps_act, eps_basis = EPS_ACTUAL[q]

        nq = guide_by_issuer.loc[q] if q in guide_by_issuer.index else None
        nq_q = nq["guided_quarter"] if nq is not None else ""
        nq_mid = float(nq["guide_mid_musd"]) if nq is not None else None

        def sur(a, c, denom=None):
            if a is None or c is None or c == 0:
                return None
            d = abs(c) if denom is None else denom
            return round((a - c) / d * 100.0, 3)

        gvs = sur(nq_mid, p["nq"]) if (nq_mid is not None and p["nq"]) else None
        gvs_sign = None
        if gvs is not None:
            gvs_sign = 1 if gvs > 0 else (-1 if gvs < 0 else 0)
        if q == "2021Q3":
            gvs_sign = -1   # Reuters headline only, magnitude unknown

        rows.append(dict(
            print_quarter=q,
            print_date={
             "2020Q4":"2021-02-25","2021Q1":"2021-05-13","2021Q2":"2021-08-12","2021Q3":"2021-11-04",
             "2021Q4":"2022-02-15","2022Q1":"2022-05-03","2022Q2":"2022-08-02","2022Q3":"2022-11-01",
             "2022Q4":"2023-02-14","2023Q1":"2023-05-09","2023Q2":"2023-08-03","2023Q3":"2023-11-01",
             "2023Q4":"2024-02-13","2024Q1":"2024-05-08","2024Q2":"2024-08-06","2024Q3":"2024-11-07",
             "2024Q4":"2025-02-13","2025Q1":"2025-05-01","2025Q2":"2025-08-06","2025Q3":"2025-11-06",
             "2025Q4":"2026-02-12","2026Q1":"2026-05-07","2026Q2":"2026-08-06"}[q],
            reaction_date=react.at[q, "reaction_date"],
            cons_revenue_musd=p["rev"], cons_revenue_vendor=p["rev_v"],
            actual_revenue_musd=rev_act, revenue_surprise_pct=sur(rev_act, p["rev"]),
            cons_eps_usd=p["eps"], actual_eps_usd=eps_act, eps_basis=eps_basis,
            eps_comparable=p["eps_comp"],
            eps_surprise_pct=(sur(eps_act, p["eps"]) if p["eps_comp"] else None),
            cons_adj_ebitda_musd=p["ebitda"], actual_adj_ebitda_musd=eb_act,
            ebitda_surprise_pct=sur(eb_act, p["ebitda"]),
            cons_nights_m=p["nights"], actual_nights_m=ni_act, nights_surprise_pct=sur(ni_act, p["nights"]),
            cons_gbv_busd=p["gbv"], actual_gbv_busd=gb_act, gbv_surprise_pct=sur(gb_act, p["gbv"]),
            cons_adr=None,
            next_quarter=nq_q,
            next_q_cons_revenue_musd=p["nq"], next_q_cons_vendor=p["nq_v"],
            next_q_guide_mid_musd=nq_mid,
            guide_vs_street_pct=gvs, guide_vs_street_sign=gvs_sign,
            excess_1d_pct=react.at[q, "excess_1d_pct"],
            excess_5d_pct=react.at[q, "excess_5d_pct"],
            excess_20d_pct=react.at[q, "excess_20d_pct"],
            confidence=p["conf"], notes=p["note"],
        ))

    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT, "04_consensus_at_print.csv"), index=False)

    src = pd.DataFrame(SOURCES, columns=[
        "print_quarter","publisher","url","published","metric","vendor","value","unit","quote"])
    src.insert(0, "source_id", ["S%03d" % (i + 1) for i in range(len(src))])
    src.to_csv(os.path.join(OUT, "04_consensus_sources.csv"), index=False)

    cur = pd.DataFrame(CURRENT, columns=[
        "period","metric","vendor","value","unit","n_estimates","low","high","as_of","url","quote"])
    cur.to_csv(os.path.join(OUT, "04_current_consensus.csv"), index=False)

    print("prints:", len(out))
    print("revenue consensus:", out.cons_revenue_musd.notna().sum())
    print("eps consensus (comparable):", int(((out.cons_eps_usd.notna()) & (out.eps_comparable == 1)).sum()))
    print("adj EBITDA consensus:", out.cons_adj_ebitda_musd.notna().sum())
    print("nights consensus:", out.cons_nights_m.notna().sum())
    print("GBV consensus:", out.cons_gbv_busd.notna().sum())
    print("next-quarter consensus:", out.next_q_cons_revenue_musd.notna().sum())
    print("source rows:", len(src), " current-consensus rows:", len(cur))


if __name__ == "__main__":
    main()
