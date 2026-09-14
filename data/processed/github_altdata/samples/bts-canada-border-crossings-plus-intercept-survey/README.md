# bts-canada-border-crossings-plus-intercept-survey - sample

Source repo: https://github.com/AlexBogden/canadian-border-crossings-analysis (MIT, code only). The repo commits NO data:
data/raw, data/processed and figures/ are gitignored. It is a SQL + Python recipe over BTS Border Crossing Entry Data,
a private BPRI Whatcom County intercept survey (n=31,208, not public) and a hand-exported NTTO I-92 air-arrivals table.
Sample here was pulled 2026-09-14 straight from the upstream BTS Socrata dataset keg4-3bc2 (public domain, keyless GET):
- bts_border_crossings_us_canada_2018plus.csv: port x month x measure, US-Canada border, 2018-01..2026-07, 37,950 rows (complete).
- bts_us_canada_monthly_by_measure_1996plus.csv: month x measure totals, 1996-01..2026-07, 2,933 rows.
- README_repo.md and bts_update_data_clean.py copied from the repo for the recipe and findings.
Caps: <=25 MB, $limit=50000 per query; US-Mexico rows and pre-2018 port detail omitted. Total ~4.9 MB.
Full dataset: curl "https://data.bts.gov/resource/keg4-3bc2.csv?\$limit=300000" (275,901 rows, ~35 MB) or the
data.bts.gov export page https://data.bts.gov/stories/s/Border-Crossing-Entry-Data/jswi-2e7b/ . Survey: not obtainable.
