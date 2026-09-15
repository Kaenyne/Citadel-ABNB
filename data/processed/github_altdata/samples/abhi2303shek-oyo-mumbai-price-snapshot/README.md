# Abhi2303shek/OYO - OYO budget-hotel price snapshot (India)

- What: single undated scrape of OYO listing cards (791 rows: hotel, location, INR price, discount %, review count) from https://github.com/Abhi2303shek/OYO (MIT, pushed 2026-02-27). Despite the slug it spans Bangalore, Delhi, Kolkata and Mumbai.
- Files here: oyo.csv (whole file, 73.8 KB), Insights.txt (author's list of analysis questions). oyo.sql, Cleaning.ipynb skipped.
- How pulled (2026-09-14): curl -sL from raw.githubusercontent.com/Abhi2303shek/OYO/HEAD/<file>; repo metadata via gh api. No scraper run, no login.
- Caps: 77 KB written, well under the 25 MB cap; nothing truncated.
- Full dataset: this IS the full dataset; `git clone --depth 1 https://github.com/Abhi2303shek/OYO` gets the remaining ~45 KB (SQL, notebook).
- Caveats: no date column, id NaN on 331 rows, 'rating' is a review count; data scraped by the author from oyorooms.com (ToS question is theirs, not ours).
