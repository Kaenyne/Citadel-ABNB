# chicagoboothml-insideairbnb-2015-30cities — sample

Source: https://github.com/ChicagoBoothML/DATA___InsideAirBnB (single commit set, 3 Dec 2015, no licence file; ~840 MB repo).
Full Inside Airbnb dumps (listings.csv, listings.csv.gz, calendar.csv.gz, reviews.csv, reviews.csv.gz, neighbourhoods.csv/.geojson)
for 30 cities at Jun–Nov 2015 vintages (scrape date per city is in the commit message, e.g. NYC 01 Sep 2015, Barcelona 02 Oct 2015).

Pulled 2026-09-14 with `curl -sL` from raw.githubusercontent.com (paths contain spaces: `New%20York%20City/...`):
- nyc_listings.csv (30,483 rows, summary 16-col listings), nyc_neighbourhoods.csv (230)
- bcn_listings.csv (14,539 rows), bcn_neighbourhoods.csv (73)
- nyc_calendar_head.csv: first 50,000 rows decompressed from a 2 MB byte-range (`curl -r 0-1999999`) of NYC calendar.csv.gz;
  confirms the calendar horizon 2015-09-01 to 2016-08-30 with daily quoted prices.

Caps applied: 8.4 MB written, 5 files, all .gz and .geojson skipped, no clone.
Full dataset: `git clone --depth 1 https://github.com/ChicagoBoothML/DATA___InsideAirBnB` (~840 MB, 30 cities x 7 files);
or pull single files from raw.githubusercontent.com/ChicagoBoothML/DATA___InsideAirBnB/master/<City>/<file>.
