# MAEC multimodal earnings-call corpus — sample (pulled 2026-09-14)

**What it is.** CC BY-SA 4.0 corpus (CIKM 2020, Li/Yang/Smyth/Dong) of S&P 1500 earnings calls, Feb 2015–Jun 2018, one folder per call (`YYYYMMDD_TICKER`) holding a sentence-per-line `text.txt` and a per-sentence low-level audio `features.csv` (29 Praat-style columns: pitch, intensity, jitter, shimmer, HNR, audio length). A parallel `MAEC_Dataset_Person_Label` tree adds anonymised speaker ids. No ABNB (pre-IPO); travel peers BKNG, EXPE, MAR, HLT, TRIP, NCLH, RCL, CCL, airlines and timeshares are present.

**What is here.** `maec_call_index.csv` — all 3,443 call folders (date, ticker, blob sha) built from the GitHub trees API without downloading bodies; `maec_person_label_index.csv` — the 2,388 speaker-labelled folders; six full call folders under `calls/` (BKNG 2016-05-04, NCLH 2016-05-10, EXPE 2016-07-28, MAR 2016-07-28, HLT 2016-10-26, TRIP 2017-11-07) plus the speaker-labelled version of the EXPE call; the repo README, LICENSE and the forced-alignment script `code/alignmentCore.py`.

**How it was pulled.** `gh api .../git/trees/<sha>` for the index; `git clone --depth 1 --filter=blob:none --sparse` then `git sparse-checkout set --no-cone` on the six call folders and code. ~0.6 MB written; the ~147.7 MB `MAEC_Dataset` tree and the 59 GB Google Drive MFCC archive were not pulled.

**Caveat.** Sampled transcripts run 59–172 sentences / 8–22 minutes of aligned audio, so they look like Q&A excerpts, not whole calls; no timestamps, roles, or Q/A markers.

**Full dataset.** `git clone https://github.com/Earnings-Call-Dataset/MAEC-A-Multimodal-Aligned-Earnings-Conference-Call-Dataset-for-Financial-Risk-Prediction.git` (~150 MB); MFCC `.npy` features via the Google Drive link in the repo README.
