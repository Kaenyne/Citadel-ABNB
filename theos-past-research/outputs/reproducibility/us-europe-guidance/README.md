# U.S./Europe guidance workbook reproducibility

This directory contains every policy-safe input required by
`build_abnb_edge_guidance_reaction.mjs`. The generator resolves all inputs from
the checkout, accepts an explicit output path, and can run without previews.
It does not need the omitted licensed transcript bodies.

## Runtime setup

The runtime is pinned in `.node-version`, `package.json`, and
`package-lock.json`: Node 24.19.0 and `@oai/artifact-tool 2.8.59`. Artifact Tool
is a private host-provided package, not a public npm-registry dependency. The
repository-local `scripts/artifact_tool_runtime.mjs` resolver validates both
versions and loads the approved Codex workspace bundle without copying that
package, its cache, or a machine-local path into Git.

In Codex Desktop, load the workspace dependencies and assign the reported Node
executable and Artifact Tool package directory to these shell variables. In an
approved equivalent environment, use its corresponding pinned paths:

```bash
export ABNB_WORKSPACE_NODE="<Node.js executable reported for this workspace>"
export ARTIFACT_TOOL_PACKAGE_ROOT="<approved @oai/artifact-tool package directory>"
test "$($ABNB_WORKSPACE_NODE -p 'process.versions.node')" = "24.19.0"
npm ci --ignore-scripts --offline
```

When the standard Codex bundle is present, `ARTIFACT_TOOL_PACKAGE_ROOT` may be
unset because the repository-local resolver locates it. The generator fails
with a version-specific diagnostic if neither approved location is available;
it never silently substitutes another spreadsheet library.

## Inputs and lineage

- `abnb_us_europe_guidance_panel.csv`, the other `abnb_us_*` CSVs, and the
  tracked readiness/edge-discovery tables are normalized outputs of the two
  preserved substantive forecasting runs.
- `nasdaq_public_market_history.csv` is a mechanical row-for-row normalization
  of the reviewed workbook's `Price History` sheet: 1,402 observations from
  2021-02-01 through 2026-08-31, provider label
  `Nasdaq public historical table`, SHA-256
  `d1e02503ff1d01f69a60f86f4b8246b2a4f54ca37daa81d5d0a7c79cf55cb728`.
  It replaces the two absent, legacy JSON response files; no prices were
  invented or refreshed during import.
- `abnb_us_europe_source_permissions.csv` is the acquisition-policy gate. Any
  future refresh must first update that review, retain the provider response in
  an approved private/raw location, normalize the same six-column CSV schema,
  and record the new checksum and as-of date. There is intentionally no command
  here that bypasses provider terms or fabricates an unavailable response.

## Build and verify

Run from the package root. A temporary output avoids overwriting the preserved
review workbook:

```bash
: "${ABNB_WORKSPACE_NODE:?set to the pinned Node 24.19.0 executable}"
mkdir -p /tmp/abnb-workbook-verification
"$ABNB_WORKSPACE_NODE" outputs/reproducibility/us-europe-guidance/build_abnb_edge_guidance_reaction.mjs \
  --output /tmp/abnb-workbook-verification/ABNB_edge_guidance_stock_reaction.xlsx \
  --skip-previews
```

For an intentional canonical rebuild, omit `--output`; the generator writes
`outputs/workbooks/ABNB_edge_guidance_stock_reaction.xlsx`. Omit
`--skip-previews` only when transient preview PNGs are wanted; they are written
under the ignored reproducibility preview directory.
