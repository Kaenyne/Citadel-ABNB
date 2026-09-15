# EDGAR-CORPUS sample (10-K sections, 1993-2020)

- What: EDGAR-CORPUS (https://huggingface.co/datasets/eloukas/edgar-corpus), all SEC 10-K filings 1993-2020 split into 23 named Item sections, one JSON record per filing (filename, cik, year, section_1 ... section_15).
- Sample here: the first ~2 MB of `1993/test.jsonl` (9 filings) and `2020/test.jsonl` (7 filings), fetched with `curl -L -r 0-2000000` HTTP Range requests, final truncated line dropped, re-saved as `*_clean.jsonl`. `records_index.csv` lists each filing with per-section character counts.
- Caps applied: 3.45 MB total written; no full year pulled (smallest year file is 114 MB, largest 1.06 GB, 40.7 GB total).
- Date coverage in sample: year 1993 and year 2020 only. Older years lack Items 1A/7A/9A (introduced 2005), so those sections are empty strings there.
- Use for ABNB: peer text panel (BKNG, EXPE, MAR, HLT and all lodging/travel filers) for MD&A / risk-factor tone back to 1993. Airbnb has no 10-K in the corpus (first 10-K is FY2020, filed 2021).
- Full dataset: `huggingface-cli download eloukas/edgar-corpus --repo-type dataset` (40.7 GB) or per-year `curl -L -o 2019_train.jsonl https://huggingface.co/datasets/eloukas/edgar-corpus/resolve/main/2019/train.jsonl`; Zenodo mirror https://zenodo.org/record/5528490 (per-year zips 39-525 MB, CC-BY-4.0). Filter by CIK for the peer set.
- Pulled 2026-09-14; see manifest.json.
