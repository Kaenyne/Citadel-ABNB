# dwh-global-tourism-project sample

Sample of https://github.com/Daniele1388/DWH---Global-Tourism-Project (MIT), which commits 14 UN Tourism (UNWTO)
Compendium of Tourism Statistics CSVs (annual, 1995-2022, ~230 countries) and builds a SQL medallion warehouse on them.
Pulled 2026-09-14: 9 of the 14 CSVs (inbound arrivals/regions/purpose/accommodation/expenditure, outbound departures/expenditure,
tourism industries, domestic accommodation) plus the upstream README, via curl from raw.githubusercontent.com (main branch).
Caps: files are small (1.6 MB total), so each was copied whole; skipped the SQL scripts and the three SDG files and two minor tables to stay near 10 files.
Format: semicolon-delimited, UTF-8 BOM, wide (years as columns), '..' = missing, commas as thousands separators, country codes partly Excel-mangled.
Full dataset: clone the repo (`git clone --depth 1 https://github.com/Daniele1388/DWH---Global-Tourism-Project`, Datasets/ is ~4.3 MB), or take the
current, longer release directly from UN Tourism at https://www.unwto.org/tourism-statistics/key-tourism-statistics (free Excel, runs past 2022).
See manifest.json for per-file row counts and columns.
