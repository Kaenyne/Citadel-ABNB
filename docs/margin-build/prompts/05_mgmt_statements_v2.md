# WS05: Management statements v2 (all events, incl. conferences and filings) and the 5 Nov guide-language pattern

Read `docs/margin-build/00_BRIEF.md` first. Slug: `05_mgmt_statements_v2`.

## Goal

WS31a catalogued 194 margin statements from 23 earnings calls and letters. Extend it to every management event that is reachable
(investor conferences, the 2023 investor update, 10-K/10-Q MD&A cost commentary, interviews with quantified claims), pull any transcripts
the repo lacks, and build the pattern of how management words its margin guide each November, so M3 can forecast the 5 Nov 2026 sentence.

## Sources

- Repo: `data/raw/transcripts/`, `data/raw/regulatory/transcripts/` (1Q23-2Q26 IR transcripts), `data/raw/letters/` (4Q20-2Q26),
  `data/raw/theo_onedrive/AIRBNB DATA/raw_expansion_licensed/v2_2026-09-05/transcripts_factset/` (pre-2023 FactSet transcripts; licensed,
  read locally, never copy), `data/processed/overnight/31a_mgmt_margin_statements.csv` (the existing 194), `02_guidance_ledger.csv`,
  `abnb_call_topics.csv`, `abnb_declined_to_quantify.csv`, `docs/q3nowcast/` (Sep 2026 conference commentary already collected by WS-G).
- New pulls: earnings-call transcripts 2021-2022 Q&A from stockanalysis.com (browser UA; see `analysis/src/download_abnb_transcripts.py`),
  conference transcripts (Morgan Stanley TMT, Goldman Communacopia, JPMorgan, Bernstein, etc.): try LSEG (`ld.news` headlines / StreetEvents
  if the desktop session exposes them; log the outcome), fool.com (rate-limited), seekingalpha is NOT reachable, IR site webcasts via archives.
  EDGAR full-text search for 8-K Items 7.01/8.01 with cost or margin language. Investor Day 2023 / any "Winter/Summer release" event
  materials with cost implications (hosting, AI spend).

## Deliverables

1. `data/processed/margin_build/05_mgmt_statements_v2/05_statements.csv`: superset of the 31a rows (keep their IDs) plus new rows with
   `statement_id, date, event_type (earnings_call | letter | conference | filing | interview | investor_day), speaker, line (cor | ops | pd | sm_brand |
   sm_perf | sm_total | ga | sbc | da | tax | interest | capex | fcf | headcount | ai | hosting | margin_total | take_rate | other), period_referenced,
   direction, quantified (yes/no), value, unit, verbatim (<= 300 chars), source_path_or_url, confidence, kept_or_missed (filled where the period
   is now reported, with the actual)`.
2. `05_guide_language_pattern.csv`: for every November print since 2021 (and each Feb/May/Aug for context): the exact FY margin sentence,
   the Q4 revenue guide, the implied Q4 margin (FY floor minus 9M actual, computed), the YTD margin vs prior-year YTD, the eventual actual FY
   margin and Q4 margin, whether the sentence was a floor, a point, a range, or "approximately", and the first FY+1 statement given at that
   print. Then the same pattern for the February FY guide (floor size vs eventual beat). Compute the beat-versus-floor distribution (n, mean,
   min, max) and the relation between YTD over-delivery and the wording chosen.
3. `05_fy27_hints.csv`: everything management has said that bears on FY27 costs (AI spend "material increase", hosting obligations, new
   businesses field investment, brand marketing "relative floor", headcount plans, buyback pace, tax), with dates and confidence.
4. `05_reliability_by_line.csv`: update of 31a's kept/missed scoring with the new statements (n per line, kept rate, mean miss).
5. Script `analysis/src/margin_build/05_mgmt_statements_v2/run.py` (rebuilds CSVs from the raw texts; exit 0), README, manifest of new pulls.
6. Note `docs/margin-build/notes/05_mgmt_statements_v2.md`: bottom line (the operating profile management is describing for 2H26 and FY27, by
   line, with confidence), the guide-language pattern table, what the 5 Nov sentence is most likely to look like given the pattern (hand this
   to M3 as a prior, not a forecast), corrections to 31a if any, "For the model", "For the 5 Nov card", RESUME.

## Pass line (pre-registered)

At least 40 new dated statements beyond the 31a 194, at least 6 from non-earnings events; every November since 2021 has its full row in the
pattern file with the implied Q4 margin computed and checked against the actual.
