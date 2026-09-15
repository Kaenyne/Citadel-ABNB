# qin-yang-earningscall-multimodal-2017 — sample

Replication data for Qin & Yang, "What You Say and How You Say It Matters: Predicting Stock Volatility Using Verbal and Vocal Cues" (ACL 2019). Source: https://github.com/GeminiLn/EarningsCall_Dataset (last commit 2022-08-04, no LICENSE).
Grain: one sentence of the most-spoken executive per 2017 S&P 500 earnings call, each line aligned 1:1 with a segmented audio clip `Audio/<Speaker>_<paragraph>_<sentence>.mp3`.

Pulled 2026-09-14 with `git clone --depth 1 --filter=blob:none --sparse` + `git sparse-checkout set --no-cone` on the three `Text.txt` files and `README.md`; Audio (351 mp3 blobs) was not fetched. Files here: the three transcripts renamed without spaces, `README_upstream.md`, and `ceo_sentences.csv` (349 rows: company, call_date, sentence_idx, sentence) built with pandas. Total ~106 KB, far under the 25 MB cap.

Full dataset: 559 calls (text + audio) as a five-part split zip `ACL19_Release.zip` on Google Drive folder `1BKCANORbcmUJKkOkBOghw6uNHPqS_az1` (linked from the upstream README; merge with `zip -s0 ... --out` then unzip). Not downloaded: unstated size and no licence — a human decides.

ABNB relevance: method/benchmark template only (Gap #17, call-tone / implied-move). 2017 vintage predates the ABNB IPO; no travel names.
