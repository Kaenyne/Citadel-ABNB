# Data handling

The user-provided FactSet CallStreet PDFs remain in `EARNING-TRANSCRIPTS/` and
are the canonical local source. Do not move, rewrite, redistribute, or commit
them.

Cleaned Markdown transcripts are generated under
`data/licensed/earnings_transcripts/clean_md/`. They are local licensed working
data and are ignored by Git. Their compact metadata index, source checksums, and
derived fact tables may be tracked because they do not reproduce the full
licensed text.

Before collecting any other dataset, record its provider, economic mechanism,
source URL, license and collection restrictions, geographic and historical
coverage, frequency, publication lag, revisions, cost, collection timestamp,
point-in-time evidence, and leakage risk in `research/source_registry.csv`.
Approval is required for paid data, Bloomberg requests, new source families,
or unclear collection permission. Never commit credentials or restricted raw
data.
