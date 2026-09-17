# B15 web/API log (2026-09-17)

WebSearch (1 of 5 budget used):
1. "CoStar U.S. hotel results week ending 12 September 2026 RevPAR" -> no result for the week ending 12 Sep (CoStar publishes Thursday/Friday; the Lodging Magazine reprint was not yet up at 08:40Z on 17 Sep). Results carried the week ending 5 Sep (occupancy 63.0%, +9.4%; ADR $159.19, +6.1%; RevPAR $100.31, +16.1%, Labor Day mirror) via asianhospitality.com, and the CoStar/TE forecast pages (hoteldive 821683; costar.com forecast-assumptions Q2 2026).

Direct fetches (curl, saved here):
- lodging_search_costar_20260917.html: lodgingmagazine.com/?s=costar listing; newest CoStar reprint is the week ending 5 Sep (posted 11 Sep). No August monthly yet (expected ~25 Sep).
- hotelnewsresource_front_20260917.html: front page; no CoStar weekly or monthly item newer than 11 Sep.
- hoteldive_perf_20260917.html: topic page fetched; no item newer than the 5 Sep weekly.

All other inputs are repo files or the R11 log (see the research log's claims ledger). costar.com and str.com return 403 to fetchers (R11 log claim 13).
