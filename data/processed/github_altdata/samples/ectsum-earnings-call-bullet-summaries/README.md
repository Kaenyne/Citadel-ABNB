# ECTSum sample (rajdeep345/ECTSum)

Earnings-call transcripts paired with Reuters-style bullet summaries (EMNLP 2022). This folder holds the full
**test** split of gold summaries (495 files, `test_gt_summaries/`), 10 transcripts (`test_ects_10/`: HLT_q4_2020
plus the 9 alphabetically first test files), and two index CSVs (`test_index.csv` per call: ticker, fiscal
quarter, bullet count; `ects_sample_index.csv` for the 10 transcripts). Fiscal quarters 2019Q3-2022Q4, 354 tickers.
Pulled 2026-09-14 with `git clone --depth 1 --filter=blob:none --sparse` + `git sparse-checkout set
data/final/test/gt_summaries`, then `curl` from raw.githubusercontent.com for the 10 transcripts. ~317 KB total,
well under the 25 MB cap; train/val and `codes/` deliberately not pulled.
Full dataset (2,425 pairs: train 1,681 / val 249 / test 495, ~40 MB text) is one sparse checkout of `data/final`.
Licence: repo GPL-3.0, but transcript text (Motley Fool) and summaries (Reuters) carry no explicit data licence;
research use only, do not commit derived text. No ABNB calls; HLT/H/DRH/MTN are the nearest lodging peers.
