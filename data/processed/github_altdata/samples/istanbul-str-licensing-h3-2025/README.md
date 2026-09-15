# istanbul-str-licensing-h3-2025 — sample

Source: https://github.com/eda-yilmaz/DI722_Istanbul_Airbnb (METU DI722 graduate project, May-Jun 2026, no LICENSE file).
What it is: H3 resolution-8 cell aggregates of a single Inside Airbnb Istanbul cross-section (pulled 29-30 Sep 2025, 24,992 cleaned
listings) classifying each listing as licensed/unlicensed under Turkey's Law No. 7464 (national STR permit regime, in force 1 Jan 2024),
plus GWR/MGWR price-regression outputs and a booking-occupancy first/last-month change from the Sep 2025-Sep 2026 calendar.
Files: mgwr_summary.csv (311 cells x 10), istanbul_airbnb_h3.geojson (1,262 cells x 17 props; flattened to istanbul_airbnb_h3_properties.csv),
mgwr_bandwidths.txt, Spatial_Final_Version.py (pipeline), README_upstream.md (the author's 45 KB write-up with district-level tables).
How pulled: curl -sL from raw.githubusercontent.com/eda-yilmaz/DI722_Istanbul_Airbnb/main/ on 2026-09-14; ~1.2 MB total, well under the 25 MB cap.
Skipped: six standalone Folium HTML maps (0.3-4.3 MB each) and four PNG figures (presentation only). Raw Inside Airbnb listings/calendar are not in the repo.
Full dataset: same files plus the HTML/PNG (8.9 MB repo); regenerate from Inside Airbnb Istanbul dump (Sep 2025) with Spatial_Final_Version.py.
Prices are in TRY. Licence: none declared; Inside Airbnb derivative (CC BY 4.0 upstream) - human decision before quoting.
