# sumaksharikaa/earnings-call-nlp — sample (pulled 2026-09-14)

What it is: a student FinBERT/Streamlit project (3 commits, last push 2026-06-25, no licence file). Its only data file, `data/sentiment_results.csv`, holds transcript-level FinBERT positive/negative/neutral scores plus risk-keyword counts for 514 earnings calls of 30 large-cap US names across 8 sectors, quarters 2017-Q4 to 2023-Q3. The committed CSV is a join artifact: 4,498 rows but only 282 distinct rows (277 ticker-quarters) — dedupe before use. No ABNB/BKNG/EXPE/MAR/HLT; DIS is the only travel-adjacent ticker.

How pulled: `curl -sL` of the raw CSV and README from raw.githubusercontent.com (exact commands in `manifest.json`); repo tree checked with `gh api repos/.../contents`. The notebook (`notebooks/earnings_nlp`, 487 KB ipynb) was fetched to the scratchpad and grepped for the data source only — it reads a gitignored `data/transcripts.pkl` and never names the Kaggle slug; it was not kept.

Caps applied: this is the whole repo data (720 KB total); nothing truncated. PNG charts and the notebook were not copied.

Full dataset: the underlying corpus (18,755 Motley Fool transcripts, 2,876 tickers, 2017-2022) is on Kaggle behind a login and was NOT downloaded. The figures match Kaggle's "Motley Fool Scraped Earnings Call Transcripts" (tpotterer) but the repo does not say so — a human must confirm the slug and decide on Kaggle/Motley Fool terms before pulling it. That corpus, not this CSV, is the item of interest (peer calls for BKNG/EXPE/MAR/HLT on one basis).
