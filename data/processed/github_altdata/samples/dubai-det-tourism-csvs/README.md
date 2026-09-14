# dubai-det-tourism-csvs — sample

Source: https://github.com/RezaSbu/Dubai-Tourism-Data-Analysis- (student EDA repo, no licence, last push 2026-08-08).
Contents: six Dubai DET / Dubai Pulse-format CSV exports — monthly overseas visitor count 2014-2023 (117 rows, gaps),
hotel establishment performance (only May-Jun 2024: hotels/rooms by class, occupancy, ADR, RevPAR), overnight visitors
by region and by top-20 source market (May-Jun 2024 only), annual visitors by nationality 2016-2022, and annual
per-source-market demographics 2016-2023 (age, gender, length of stay, visit purpose). `SOURCE_README.md` is the repo README.
Pulled 2026-09-14 with `curl -sL -o <file> https://raw.githubusercontent.com/RezaSbu/Dubai-Tourism-Data-Analysis-/HEAD/<file>`
after listing the tree via `gh api repos/RezaSbu/Dubai-Tourism-Data-Analysis-/contents/`. Total 44 KB, well under the 5 MB cap;
no heads were taken (files are complete). Skipped per plan: 12 quarterly Epermit_/Eticketing_ CSVs, the notebook, the PDF.
Full dataset: `git clone --depth 1 https://github.com/RezaSbu/Dubai-Tourism-Data-Analysis-` (~165 KB). Longer monthly hotel
and visitor series exist on the Dubai DET open-data portal (Dubai Pulse); licence/terms there need a human check.
