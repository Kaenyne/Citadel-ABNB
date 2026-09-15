# L4 review memo, unsigned card and quantified decisions

This package is an integration/communication layer. It performs no conversion
estimation, RNPL identification, research collection, registrations or scorer
runs. Every conversion-dependent forecast is the fixed 2/3 K0 **benchmark**,
provisional pending accepted L3 conversion validation. FX/RNPL integration is a
separate pending input and is never silently represented as zero.

From the L4 worktree root, using the bundled Python or a Python with reportlab
and pypdf:

```powershell
python analysis/src/forecast_methods/lane4_review_v1/run.py --revenue-dir data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1 --model-dir data/processed/forecast_methods/lane4_model_v1/snapshot_v1 --run-id review_v1
python -m unittest discover -s analysis/src/forecast_methods/lane4_review_v1/tests -v
```

The model snapshot path must be the actual explicitly verified upstream version;
the example does not select a mutable `latest` directory. Each command creates
new `data/processed/forecast_methods/lane4_review_v1/<run-id>/` and
`deck/drafts/lane4_v1/<run-id>/` directories. An existing run ID is refused.
Input files are copied into immutable per-run snapshots with SHA-256 checks
before and after copying. Numeric final content reads these files, not another
agent's changing research worktree. The runner refuses a non-pending L3 adapter:
accepting conversion or FX inputs requires an explicitly reviewed new version.

Outputs: `review_memo.md` and exactly two-page `review_memo.pdf`, unsigned card
Markdown/CSV/JSON, quantified decision register Markdown/CSV and source/assumption
CSV ledger. Full input hashes, numerical consistency checks and artifact hashes
are in the run receipt. The original team D-01 remains the Q3 revenue decision;
new choices use L4-Dxx IDs, with L4-D09 explicitly mapping to original D-01.

The Markdown is editable. After saving changes to a **new** source file, a new
run may use `--render-source path/to/edited.md`; it copies that source into its
own new output directory. Recheck all changed numbers against the ledger before
delivery. The restricted renderer supports paragraphs, bold, headings, tables
and exactly one `<!-- PAGEBREAK -->` marker. The artifact marker required by the
PDF skill was executed once before this package's first authoring operation.

Render and visually inspect **both** pages before delivery:

```powershell
pdftoppm -r 120 -png deck/drafts/lane4_v1/review_v1/review_memo.pdf data/processed/forecast_methods/lane4_review_v1/review_v1/page
```

`scoring.py` tests half-unit rounding, exact/overlapping lambda boundaries,
growth-ratio denominator uncertainty, missing inputs, invalid ratios, and F's
three-part proposed refutation conjunction. It never converts an ambiguous or
missing observation into support and never emits a trading instruction.

Parameter count: zero newly fitted parameters. Historical performance claims are
qualified excerpts of committed source notes. Current model values, USD units,
guide/revenue distinction, 31 December 2027 horizon and source dates remain
explicit. Scenario probabilities and formal adoption are intentionally absent.

## RESUME

Read the package results note and latest explicit run receipt. Consume only
parent-approved revenue/model snapshots, rerun to a new ID, inspect both PDF
pages, and report any failed render or calculation rather than overwriting its
record. Parent owns integration, registrations and scorer checks. L3 owns
conversion estimation/validation and cohort FX/RNPL research; its results enter
only after an explicit version/commit and checksums are accepted.
