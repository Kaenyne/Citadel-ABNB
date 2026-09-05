# Data handling

The user-provided FactSet CallStreet PDFs remain in `EARNING-TRANSCRIPTS/` and
are the canonical local source. Do not move, rewrite, redistribute, or commit
them.

Cleaned Markdown transcripts are generated under
`data/licensed/earnings_transcripts/clean_md/`. They are local licensed working
data and are ignored by Git. Their compact metadata index, source checksums, and
derived fact tables may be tracked because they do not reproduce the full
licensed text.

Authorized teammates should acquire the underlying material through an approved
institutional or private team channel, placing PDFs in `EARNING-TRANSCRIPTS/`
and any derived full-text files only in
`data/licensed/earnings_transcripts/clean_md/`. Do not add either directory to
Git. Validate the public metadata without licensed bodies with:

```bash
python scripts/validate_project.py --root . --expected-transcripts 23 --metadata-only
```

`research/provenance/restricted-data-manifest.csv` records every excluded
licensed asset with its expected checksum; the compact transcript index and
derived facts remain the reviewable, trackable boundary. Metadata-only mode
validates that boundary but does not hash absent PDFs or Markdown.

To hash all acquired private inputs, set `ABNB_PRIVATE_INPUT_ROOT` to the root
containing both ignored directory trees and run:

```bash
: "${ABNB_PRIVATE_INPUT_ROOT:?set to the approved licensed-input root}"
python scripts/validate_project.py --root . --expected-transcripts 23 --private-checksums --private-input-root "$ABNB_PRIVATE_INPUT_ROOT"
```

The command reports each missing body and each checksum mismatch separately.

Before collecting any other dataset, record its provider, economic mechanism,
source URL, license and collection restrictions, geographic and historical
coverage, frequency, publication lag, revisions, cost, collection timestamp,
point-in-time evidence, and leakage risk in `research/source_registry.csv`.
Approval is required for paid data, Bloomberg requests, new source families,
or unclear collection permission. Never commit credentials or restricted raw
data.
