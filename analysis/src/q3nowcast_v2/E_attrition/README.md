# E_attrition: reviews attrition ladder from the 2015-2019 Inside Airbnb archives

Build B of the GitHub alt-data catalogue. Extends the E note's survivorship wedge (table 2.2, 1 to 36 months, pooled about 15 percent a year) with an independent era (Barcelona 2015-2019, 33 vintages) and a decade horizon (30 cities at a 2015 vintage vs the held 2025/2026 dumps). Nothing enters the harness; the pre-registered lines are corroborations of a mechanism. Note: `docs/revenue-forecast-strategy/05_backtests/WPK_reviews-attrition-ladder-2015-2019.md`.

## Command

From the worktree root:

```
python analysis/src/q3nowcast_v2/E_attrition/run.py
```

Exit code 0. Wall time about 2 minutes on the first run (counts 64 archive reviews files, cached as csv.gz under `data/processed/q3nowcast_v2/E_attrition/cache/`, not committed); seconds afterwards.

## Inputs

Raw (outside git, pulled 2026-09-14, manifest with sha256 in `data/processed/q3nowcast_v2/E_attrition/raw_manifest.csv`):

- `C:/Users/krish/abnb_ia_capture/montera34_barcelona/<YYMMDD>/{listings_summary,reviews_summary}_barcelona_insideairbnb.csv`, 33 Inside Airbnb dates 150430..190308 (folder 180619 is DataHippo, excluded), from https://github.com/montera34/airbnb.barcelona (raw.githubusercontent.com, one curl per file; the sparse partial clone in the plan fails on missing promisor blobs).
- `C:/Users/krish/abnb_ia_capture/chicagobooth_2015/<city-slug>_reviews.csv.gz` for 30 cities plus `new-york-city_listings.csv.gz` and `barcelona_listings.csv.gz`, from https://github.com/ChicagoBoothML/DATA___InsideAirBnB (scrape dates per city from the commit messages).
- `C:/Users/krish/abnb_ia_capture/joeydejager_nyc_2015/nyc_reviews_20150101184336.csv` and `nyc_listings_20150101184336.csv`, from https://github.com/JoeyDeJager/inside-airbnb-data.

Held (read only): `data/processed/q3nowcast/E/market_vintage_monthly.csv` (latest dump per market), `market_geo.csv`, `survivorship_wedge.csv`.

## Outputs (`data/processed/q3nowcast_v2/E_attrition/`)

- `survivorship_ladder.csv`: one row per market x archive vintage x review month: n_archive, n_held, ratio, age_months (archive vs held latest vintage).
- `survivorship_ladder_intra_montera34.csv`: the same for every early < late pair inside the 33 Barcelona vintages (ages 1 to 47 months).
- `survivorship_pooled_by_age.csv`: pooled table by 12-month age bucket, four samples, n and review-weighted ratio.
- `L1_montera34_12m_pairs.csv`, `L1_by_early_year.csv`, `L2_chicagobooth_2014_by_city.csv`, `prereg_results.csv`: the pre-registered lines.
- `per_market_decade_attrition.csv`: 2012-2014 review months, 2015 vintage vs held, beside the E note's own 12-month wedge per market.
- `barcelona_supply_2015_2019.csv`: listing count, entire-home share, multi-listing share, median quoted price (EUR, no FX) per montera34 dump.
- `archive_vintage_inventory.csv`, `city_market_mapping.csv`, `raw_manifest.csv`, `run_summary.json`.

Data: Inside Airbnb (https://insideairbnb.com/get-the-data/), CC BY 4.0, redistributed on GitHub by the three repositories above.
