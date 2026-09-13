# WS04 alt signals: external and alternative-data series for each cost line and below-EBITDA item

Rebuild the panel, the tests, the catalogue and the manifest from raw (no network):

```
python analysis/src/margin_build/04_alt_signals/run.py
```

Exit code 0; writes `data/processed/margin_build/04_alt_signals/04_signal_panel_quarterly.csv`, `04_signal_knowable_from.csv`,
`04_signal_tests.csv`, `04_signal_catalogue.csv`, `04_interest_income_yield_diagnostic.csv`, the parsed Wayback tables
(`04_appstore_parsed.csv`, `04_playstore_parsed.csv`, `04_trustpilot_parsed.csv`, `04_sitejabber_parsed.csv`) and the manifest
`data/manifests/margin_build/04_alt_signals.csv` (sha256 of every raw file).

Pulls (network; each writes under `data/raw/margin_build/04_alt_signals/`, gitignored):

```
python  analysis/src/margin_build/04_alt_signals/pull_fred.py --pull                     # FRED keyless CSVs (rates, wages, PPIs, macro, FX)
python  analysis/src/margin_build/04_alt_signals/pull_wayback.py --pull [page_key ...]   # one Wayback capture per quarter per page (CDX lists must exist)
py -3.13 analysis/src/margin_build/04_alt_signals/pull_lseg_peers.py --pull              # LSEG Workspace: peer opex lines (licensed raw)
py -3.13 analysis/src/margin_build/04_alt_signals/pull_lseg_peers_sm.py --pull           # LSEG Workspace: peer SG&A, advertising, FTE (licensed raw)
```

The CDX capture lists (`wayback/cdx_*.json`) and the TSA year pages (`tsa/tsa_*.html`) were pulled with curl on 13 Sep 2026; the
exact commands are in the note (`docs/margin-build/notes/04_alt_signals.md`, section "What ran"). `tsa/tsa_daily_parsed.csv`,
`wayback/_careers_parse_raw.csv` and `xbrl/abnb_xbrl_below_ebitda_facts.csv` are derived from those raw files by the one-off
snippets recorded in the note. `misc/events_step_dummies.csv` and `misc/tenk_annual_drivers.csv` are hand-built tables with a
source per row.

Rules followed: no live request to any airbnb.com page (careers pages come from Internet Archive captures only); no logins; free tiers;
LSEG output stays under `data/raw/` and only derived y/y series reach `data/processed/`.
