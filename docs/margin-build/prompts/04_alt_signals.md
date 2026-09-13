# WS04: External and alternative-data signals for each cost line and below-EBITDA item

Read `docs/margin-build/00_BRIEF.md` first. Slug: `04_alt_signals`. If `data/processed/margin_build/01_input_census/01_gaps.csv` exists
when you start (or appears while you work), use it as your pull list; otherwise use the list below and check WS01's file later.

## Goal

Find, pull, and test external series that could explain or lead a cost line, so that M4 (alt-augmented line model) and M7 (below-EBITDA)
have real inputs. Rules: archives and third-party public sources only; no live request to any airbnb.com page; free tiers; no logins; no credentials.
LSEG is available (brief snippet) for macro/rates/FX and for peer financials; EDGAR is available.

## Candidate list (pull what is reachable; log each attempt in the manifest with status)

Product development and G&A (headcount, wages):
- Wayback captures of `careers.airbnb.com` (job listing counts by team/location over time; CDX API for capture list, then fetch captures at
  quarterly spacing 2019-2026; parse counts). Also Wayback of LinkedIn's public Airbnb company page (employee count) and of Glassdoor's
  Airbnb overview (review counts). Common Crawl as a fallback.
- 10-K headcount (annual) and any quarterly headcount statements in transcripts (grep `data/raw/transcripts`, `data/raw/regulatory/transcripts`).
- BLS/FRED wage indices: software publishers and computer systems design (CES), SF-Oakland CPI; layoffs.fyi-style public trackers if archived.
Sales and marketing:
- Google Trends via pytrends (`py -3.13`): "airbnb" worldwide and by key country, monthly 2019-2026, plus competitor terms; interpret as brand-demand,
  test against S&M spend per night and against nights.
- Meta Ad Library (public web UI or API with no token is limited; try the public report pages for advertiser spend in the EU transparency report
  and the US political-free spend report; log if not reachable). Google Ads transparency centre (archives). App-store rank history from
  third-party trackers via Wayback.
- Repo: fee panels, host acquisition / new listings (Inside Airbnb supply panel, CC listing panel), supply churn as a marketing-need proxy.
Operations and support:
- Trustpilot / BBB / Sitejabber review and complaint counts over time (public pages, Wayback for history); Downdetector archives; app-store
  review counts and ratings (public pages of Apple/Google via archives).
- AI support statements timeline (from 31a) as a step-dummy series.
Cost of revenue:
- Payment processing: Visa/Mastercard interchange and cross-border fee changes (public announcements), Adyen/Stripe published pricing changes;
  share of cross-border nights (repo regional/O-D FX work, Lane 1 X package) as the driver of FX conversion cost; AWS/hosting price indices
  (public price announcements), the contracted hosting obligations from the 10-K (31 note); AirCover claims proxies (any public data: insurer
  filings, news); chargeback/fraud indices if public.
Below EBITDA:
- Rates for interest income on funds held: FRED 3-month T-bill (DTB3), 1-year, Fed funds; funds held on behalf of guests from WS02/XBRL.
- Tax: statutory and effective tax commentary; share count: buyback authorisations and cadence from `abnb_capital_return_quarterly.csv`.
Macro cycle (for M6):
- Consumer sentiment (UMich), real disposable income, air passenger counts (TSA throughput daily, public), hotel RevPAR (repo), EUR/USD.

## For every series you obtain

- Save raw under `data/raw/margin_build/04_alt_signals/`, a cleaned monthly/quarterly CSV under `data/processed/margin_build/04_alt_signals/`,
  and a manifest row (URL, capture timestamp, sha256, licence/terms note).
- Record `knowable_from` for each observation (Wayback capture date, publication date), so M4 can respect PIT.
- Quick test, pre-registered: correlation of the series' y/y change with the matching cost line's y/y change (cash, per night where a per-unit
  line makes sense) over 1Q21-2Q26, contemporaneous and led by 1-2 quarters, n stated; plus the same against the margin. A |r| above 0.5 with
  n >= 14 and the right sign is "candidate"; anything else is "logged, not promising". Report every test; count them; expect most to fail.

## Deliverables

1. `data/processed/margin_build/04_alt_signals/04_signal_panel_quarterly.csv` (quarter x series, aligned to fiscal quarters) and
   `04_signal_tests.csv` (series, line, lead, r, n, sign_expected, verdict).
2. `04_signal_catalogue.csv`: every series attempted with status (pulled | partial | unreachable | out_of_rules), coverage, and the target line.
3. Script `analysis/src/margin_build/04_alt_signals/run.py` (rebuilds the panel and tests from raw; pulls are separate scripts with a
   `--pull` flag), README, manifest.
4. Note `docs/margin-build/notes/04_alt_signals.md`: bottom line (which 3-6 series deserve a place in M4/M7, and why), the catalogue, the test
   table, what was unreachable and why, "For the model", RESUME. Budget: this is a wide net; stop pulling after ~2.5 hours and write up.
