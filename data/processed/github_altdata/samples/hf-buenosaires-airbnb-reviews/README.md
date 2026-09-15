# hf-buenosaires-airbnb-reviews — sample

Source: https://huggingface.co/datasets/alujjdnd/Airbnb-Mar-2022-2023 (HF card licence MIT; underlying data is Inside Airbnb, CC BY 4.0).
Despite the job-card name, this is a mirror of Inside Airbnb `reviews.csv.gz` for ~116 markets worldwide, each the Mar-May 2023 dump
(`raw_dl/` keeps original names + dump dates, 4.88 GB gz; `natural_compressed/` is a renamed duplicate). Reviews go back to 2009-2010.
Pulled 2026-09-14 with keyless `curl -r 0-1999999` range requests on two files (Buenos Aires 2023-03-29, NYC 2023-03-06), partially
gunzipped with Python zlib, and cut to the first 8,000 complete rows each (~70-75 listings, sorted by listing_id, not random).
Caps: 6.4 MB written, 2 data files + 1 file index; nothing cloned. `hf_raw_dl_file_index.csv` lists all 116 files with gz size and dump date.
Full dataset: `curl -L -o <name> https://huggingface.co/datasets/alujjdnd/Airbnb-Mar-2022-2023/resolve/main/raw_dl/<file>` per market
(URL-encode spaces/accents), or `huggingface_hub.snapshot_download('alujjdnd/Airbnb-Mar-2022-2023', repo_type='dataset', allow_patterns='raw_dl/*')`.
Value: pre-CDN-window Inside Airbnb vintage incl. pre-Local-Law-18 NYC; extends the reviews stays index back to 2010 and to LatAm/APAC markets. No listings/calendar/price files.
