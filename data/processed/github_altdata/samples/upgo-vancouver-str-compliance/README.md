# upgo-vancouver-str-compliance — sample

Source: https://github.com/UPGo-McGill/vancouver-regulations (MIT, last push 2019-06-23).
The only committed data file is `data/raffle.csv` (7.69 MB, 370,590 rows): a lookup from AirDNA listing ID
(`ab-`/`ha-` prefix) to a StatCan 2016 dissemination-area ID (`winner`), Canada-wide, from a 2019-05-28 AirDNA extract.
It is NOT a compliance/licence dataset; the daily price/status files the analysis needs are AirDNA-licensed and gitignored.

Pulled 2026-09-14 with `curl -sL` from raw.githubusercontent.com; described with pandas.
Caps applied: saved a 50,000-row head (`raffle_head50k.csv`) and a per-DA listing-count aggregate
(`raffle_winner_DA_counts.csv`, 38,377 rows) instead of the full 7.7 MB file; total under 2 MB.
Also saved the repo README and `R/02_first_time_data.R` (documents the AirDNA schema and the Housing property-type filter).

Full dataset: `curl -L -o raffle.csv https://raw.githubusercontent.com/UPGo-McGill/vancouver-regulations/HEAD/data/raffle.csv`.
