# usamaislam70/Viator-and-GYG-Scraper — sample

Committed scraper output (early Jul 2026 snapshot, no licence) of GetYourGuide and Viator activity listings for Japan, Spain, Thailand, Vietnam, UK and Pakistan: one row per activity with USD list price, rating, review count, category, cancellation policy and the operator's legal/registration details, plus a GYG supplier master file by country.

Pulled 2026-09-14 with `curl -L` from raw.githubusercontent.com (paths in manifest.json). No scraper was run. Caps applied: only the two tiny xlsx files, the two seed-URL lists, and 1.0-1.5 MB range heads of the three large CSVs (Suppliers Master File 4.9 MB, vietnam_iternaery_data 13.2 MB, Viator Vietnam 33.6 MB); the eight 5-10 MB country xlsx files were not fetched. Total 3.5 MB.

Files: gyg_uk.xlsx (5 rows), viator_pakistan.xlsx (5 rows), suppliers_master_head.csv (5,257 rows), vietnam_itinerary_head.csv (770 rows), viator_vietnam_head.csv (588 rows), viator_input_urls.txt, gyg_input_urls.txt. No date columns anywhere; single snapshot.

Full dataset (~95 MB of data, ~113 MB repo): `git clone --depth 1 --filter=blob:none --sparse https://github.com/usamaislam70/Viator-and-GYG-Scraper && git sparse-checkout set supplier_activites/supplier_activites/output`, or fetch individual files by raw URL.

Caveats: scraped from sites whose ToS forbid scraping and no licence declared — cataloguing only until a human decides; contains operator contact details (phone/email); numeric columns are dirty.
