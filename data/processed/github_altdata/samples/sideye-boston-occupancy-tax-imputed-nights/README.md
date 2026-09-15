# sideye/airbnb-occupancy-tax — sample (pulled 2026-09-14)

Honours-thesis repo (Boston STR occupancy tax, effective 1 Jan 2019) with committed derived panels: imputed Airbnb booked nights and mean nightly price for Boston + 10 control cities (Asheville, Chicago, DC, Denver, Montreal, Nashville, Quebec City, Rhode Island, SF, Twin Cities) at city-month/bimonth/week grain by reservation date, city x scrape-period by booking date (Jul 2018 - May 2019), listing entries/exits, and a control-city tax-rate sheet (control_cities.xlsx). Also writeup.pdf, the two processing scripts, synth.R and the reviews-validation notebook.

How pulled: `gh api repos/sideye/airbnb-occupancy-tax/contents/` for the tree, then `curl -sL -o` from raw.githubusercontent.com/sideye/airbnb-occupancy-tax/master/ for each file listed in manifest.json. No scraper was run.
Caps: ~0.8 MB total (all data CSVs are complete, ~1,200 rows); skipped Prelim SCM.pptx (12 MB), writeup.pages (9 MB), SCM Analysis.ipynb (1.7 MB), .numbers file and remaining notebooks.
Full dataset: `git clone --depth 1 https://github.com/sideye/airbnb-occupancy-tax` (~43 MB). Raw per-listing calendar scrapes were never committed.
Licence: none in repo; last push 29 Apr 2020. Upstream README saved as README_upstream.md.
