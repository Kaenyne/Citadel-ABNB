# aarushisingh-pead-investor-attention - sample

Source: https://github.com/aarushisingh470/Post-Earnings-Announcement-Drift (HEAD 5dfb7db7, 2026-03-10, no LICENSE).
What: PEAD event study for 16 US mega-caps (no ABNB) with a Google-Trends attention panel and earnings-congestion control.
Pulled: `git clone --depth 1 --filter=blob:none --sparse ... && git sparse-checkout set Output/final Output/tables Notebooks`, files copied here on 2026-09-14.
Contents: Output/final (event panel 382 events 2020-01 to 2025-11; weekly Trends attention panel 12 tickers 2020-12 to 2025-12; daily returns 2019-2025; Trends download plan + instructions), Output/tables (drift-by-attention/distraction base rates, strategy summaries), Notebooks (4-step pipeline + report), REPO_README.md.
Caps: 1.9 MB total, well under the 25 MB cap; nothing truncated. Skipped per plan: the 483 KB PDF, Papers/, Output/cache/ (yfinance earnings dates + adjclose panel, ~0.6 MB).
Full dataset: clone the repo without --sparse (~5.5 MB). Raw per-term Google Trends CSVs are not committed - only the merged panels; the Trends notebook was not re-run.
Caveat: attention panel is a single manual Trends vintage with no recorded pull date; drift base rates rest on n=238.
