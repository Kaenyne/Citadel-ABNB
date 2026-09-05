# Theo's historical ABNB research

This package is a reviewable historical snapshot of Theo Machado's ABNB
research. It keeps three complementary streams together:

- `abnb_alt_data`: alternative-data source controls, point-in-time evidence,
  and import-policy helpers.
- `abnb_forecasting`: macro-to-guidance forecast packets and baselines.
- `abnb_guidance`: guidance contracts, normalized data, and market-reaction
  research.

This historical research does not replace the team thesis, model, or shared research folders.

## Setup and validation

Run commands from this directory:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pytest
python scripts/validate_project.py --root . --expected-transcripts 23 --metadata-only
python scripts/validate_import.py
```

The `metadata-only` validation checks the tracked inventory and checksum
metadata without requiring licensed transcript text in Git.

## Review outputs

| Location | Contents |
| --- | --- |
| `outputs/reports/` | Final macro-to-equity IC brief PDF and the editable Overleaf source bundle. |
| `outputs/workbooks/` | Three review workbooks, two clean workbook-inspection records, and the blank `ABNB_consensus_data_request_template.xlsx`. |
| `outputs/figures/README.md` | Pointer to figure PDFs retained only in the report source bundle. |
| `outputs/reproducibility/us-europe-guidance/` | Compact U.S./Europe guidance inputs and the portable workbook-generation script. |

The request workbook is a blank template for an approved Bloomberg request; it
does not contain vendor-returned consensus data. Its contents are preserved
unchanged under the neutral review filename above.

The static final PDF and its figure PDFs are retained as the historical rendered
report. Editable report sources and audit references use the normalized named
locations above for this team checkout; the PDF and figure binaries are not
rebuilt as part of that path normalization.

## Provenance and restricted inputs

This snapshot records source `main` at
`cebd7f3a3fca93dd92f7a04ee3692ec809990505` and
`abnb-guidance-intelligence` at
`580b7b9b981b1c8fab617eaae63f52692e3f180b`.

`research/provenance/restricted-data-manifest.csv` describes each omitted
licensed FactSet CallStreet PDF and generated full-text transcript. Authorized
teammates should obtain those inputs through an approved institutional or
private channel, keep them in the ignored local directories documented in
`data/README.md`, and validate their checksums against the manifest.

`research/provenance/omitted-data-manifest.csv` records oversized, raw,
archive, Parquet, and machine-local artifacts excluded from the Git snapshot,
including their logical paths, checksums, and replacement or rebuild guidance.
Never add raw downloads, vendor output, local paths, credentials, or licensed
transcript text to this package.

## Reproducing the review boundary

The tracked CSV inputs and MJS script support inspection of the U.S./Europe
guidance workbooks. The script is portable within this package: run it only
after supplying its documented local source inputs and approved public-market
responses beside the script. It writes any transient previews beside the script
and those files remain untracked. Review the source-permissions CSV before
acquiring or refreshing any input.
