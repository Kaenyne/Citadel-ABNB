# B14 web/API log (2026-09-17)

WebSearch (1 of 5 budget used):
1. "Atlantic hurricane season outlook late September 2026 tropics" -> weather.com 2026-09-10 "Atlantic hurricane season peak: a record hurricane delay" (five tropical storms, none a hurricane; 2026 "will smash the satellite-era record for the longest wait for the season's first Atlantic hurricane", previous record Sep 11 in 2002 and 2013); noaa.gov Aug outlook (7-13 NS, 2-6 H, 0-2 MH; 75% below-normal, 20% near, 5% above); tropical.colostate.edu 2026-07.pdf; wikipedia 2026 season.

Direct fetches (curl, saved here):
- nhc_tcr_2026_20260917.html: NHC 2026 season summary as of 03 UTC 17 Sep 2026: 5 named storms (-4 vs normal), 0 hurricanes (-4), 0 major (-1), ACE 4.4 (-94%); storms Arthur, Bertha, Cristobal, Dolly, Edouard (all TS, max 50 kt).
- nhc_twoat_20260917.html: NHC Tropical Weather Outlook 2 AM EDT 17 Sep 2026: one disturbance (AL98) east of Bermuda, 40%/48h and 40%/7d, subtropical Atlantic, no other areas.
- csu_2026-08.pdf (+ csu_2026-08_text_first12pages.txt): CSU 5 Aug 2026 forecast: 9 NS / 4 H / 1 MH; P(>=1 MH landfall after 4 Aug) entire US coast 16% (avg 43%), East Coast incl. peninsula FL 7% (avg 21%), Gulf Coast FL panhandle to Brownsville 9% (avg 27%); Caribbean 17% (avg 47%).
- noaa_aug_outlook_2026.html: CloudFront 403 (content taken from the WebSearch result and the Fall Cup log claim 14).
- Kalshi API (2026-09-17T08:41-08:43Z): KXHURCTOTMAJ-26DEC01 T0 (>0 major hurricanes in 2026) bid 0.32 / ask 0.36 / last 0.33; T1 0.13/0.16; T2 0.02/0.04. KXHURCTOT (>4 hurricanes) 0.04/0.07. KXHURPATHNC-26DEC (any hurricane landfall NC) 0.03/0.12. Series KXHURPATHFLA, KXHURPATHGENERALMAJOR, KXHURPATHGULFCOAST, KXHURCOASTTEX, KXHURPATHSCAROLINA, KXHURTB, KXHURMIA: no 2026 markets returned (files kalshi_markets_*.json).
- Polymarket public-search "hurricane landfall" / "hurricane Florida" (2026-09-17T08:42Z): "Will any Category 4 hurricane make landfall in the US before 2027?" yes 0.055 (vol24 $133); Hawaii landfall 0.065. No Florida or Cat-3 market.
- hurdat2-1851-2025.txt: copied from the forecasting repo clone (NHC HURDAT2 best track, https://www.nhc.noaa.gov/data/hurdat/).
