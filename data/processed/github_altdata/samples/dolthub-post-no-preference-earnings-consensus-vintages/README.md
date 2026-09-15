# DoltHub post-no-preference/earnings - consensus vintages sample (ABNB, BKNG)

What: public Dolt database of weekly analyst-consensus snapshots (revenue = sales_estimate, EPS = eps_estimate;
columns date/act_symbol/period/period_end_date/consensus/count/high/low/year_ago) plus earnings_calendar. Zacks-style; no licence stated.
Pulled 2026-09-14 via keyless GET to https://www.dolthub.com/api/v1alpha1/post-no-preference/earnings/master?q=<sql>
(branch is `master`), one ticker per query, LIMIT/OFFSET pagination, JSON rows converted to CSV with pandas.
Files: sales_estimate_ABNB_BKNG_EXPE.csv (ABNB complete 1,160 rows 2021-02-07..2026-09-13; BKNG first 1,000 rows only, 2018-04-08..2023-02-05;
EXPE not pulled - timeouts), eps_estimate_ABNB_BKNG_EXPE.csv (ABNB head, 200 rows), earnings_calendar_ABNB_BKNG_EXPE.csv (ABNB, 23 dates). 228 KB total, well under the 25 MB cap.
Caps/limits hit: multi-ticker queries, aggregates and larger offsets return 'context deadline exceeded'; one HTTP 403 after ~40 requests. Rest a few minutes between batches.
Full dataset: rerun the per-ticker paginated queries for BKNG (offset 1000+), EXPE, eps_estimate, eps_history (~1-2 MB CSV for the three tickers), or `dolt clone post-no-preference/earnings` for every US ticker (multi-GB, not attempted).
Licence question open: consensus values appear to be redistributed Zacks data - human decision before quoting externally.
