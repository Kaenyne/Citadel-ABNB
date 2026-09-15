export const meta = {
  name: 'github-altdata-samples',
  description: 'Fable agents pull a small sample of each repo Opus marked "sample" (jobs passed via args from state.py --jobs)',
  phases: [{ title: 'Sample', detail: 'one Fable agent per repo, <= 25 MB each, manifest.json per sample', model: 'fable' }],
}

const WT = 'C:/Users/krish/citadel-abnb-ghcat'
const CONTEXT = `${WT}/docs/github-altdata/CONTEXT.md`
const SAMPLE_DIR = `${WT}/data/processed/github_altdata/samples`
const SCRATCH = 'C:/Users/krish/AppData/Local/Temp/claude/C--Users-krish-citadel-abnb/fed6ec60-0618-4506-8d5e-dfd74f10c375/scratchpad/ghcat'

// args.slugs = ['slug', ...]; each job's details live in samples/_jobs/<slug>.json (written by state.py --jobs)
const slugs = (args && Array.isArray(args.slugs)) ? args.slugs : []
if (!slugs.length) return { error: 'no slugs passed in args.slugs (run state.py --jobs)' }
const jobs = slugs.map(slug => ({ slug, file: `${SAMPLE_DIR}/_jobs/${slug}.json` }))
log(`Sampling: ${jobs.length} Fable agents`)

const SAMPLE_SCHEMA = {
  type: 'object',
  properties: {
    slug: { type: 'string' },
    url: { type: 'string' },
    sampled: { type: 'boolean' },
    total_bytes: { type: 'integer' },
    files: { type: 'array', items: { type: 'string' } },
    rows: { type: 'string', description: 'row counts per file or a total; "n/a" for non-tabular' },
    columns: { type: 'string', description: 'column names of the main table(s), abbreviated' },
    date_range: { type: 'string', description: 'earliest and latest dates observed in the sample' },
    geography: { type: 'string' },
    how_pulled: { type: 'string', description: 'the exact commands used' },
    full_dataset_size: { type: 'string', description: 'what the full dataset would be (files, GB, rows) if we wanted all of it' },
    description: { type: 'string', description: 'three or four sentences: what this data is, its grain, its source, and what an analyst would do with it for ABNB' },
    issues: { type: 'string', description: 'failures, licence concerns, dead links, anything a human must decide' },
  },
  required: ['slug', 'url', 'sampled', 'total_bytes', 'files', 'rows', 'columns', 'date_range', 'how_pulled', 'full_dataset_size', 'description', 'issues'],
}

function samplePrompt(j) {
  const dir = `${SAMPLE_DIR}/${j.slug}`
  return `You are pulling a SAMPLE of one open dataset for an Airbnb (ABNB) alt-data catalogue. Read ${CONTEXT} first (short). Then Read ${j.file}: the job card (url, slug, category, data_kind, one_line, abnb_use, sample_plan, tos_or_license_flag). SLUG: ${j.slug}.

Do this:
1. Work in a scratch folder ${SCRATCH}/${j.slug} (create it). Follow the sample plan; adapt if paths have moved (check the repo tree with WebFetch on the GitHub page, \`gh api repos/<owner>/<repo>/contents/<path>\`, or \`git ls-remote\`). Good tools: \`curl -L -o\` for raw files and release assets (raw.githubusercontent.com/<owner>/<repo>/HEAD/<path>), \`curl -r 0-4999999\` for the head of a big file, \`git clone --depth 1 --filter=blob:none --sparse <url>\` + \`git sparse-checkout set <dir>\` for a data directory, Python (pandas/duckdb/pyarrow via \`python\`) to open and describe. For parquet/zip, extract or read a slice and save a CSV head (the repo gitignores *.zip and *.parquet).
2. HARD CAPS: ≤ 25 MB written under ${dir}; prefer ≤ 5 MB; take heads (first ~50k rows) of large tables; never clone a repo without --depth 1 --filter=blob:none; never pull more than ~10 files. Never touch airbnb.com. Never log into anything, never use an API key, never run a scraper against a third-party website — if the plan needs a scraper, do NOT run it: record sampled=false with the reason. Keyless GET requests to public statistical-agency APIs and archive hosts (Zenodo, Dataverse, data.gov, Eurostat, FRED-without-key endpoints, archive.org) are fine.
3. Copy the sample files into ${dir}/ (create it). Open every table you saved and record row counts, columns, and the min/max of any date-like column.
4. Write ${dir}/manifest.json with exactly the fields of your structured output plus "source_urls" (list of the exact URLs fetched) and "pulled_at" (ISO date; use \`date\` in Bash). Write ${dir}/README.md: 5-10 lines — what it is, how it was pulled, caps applied, and how to get the full dataset.
5. If nothing could be pulled, still write manifest.json with sampled=false and a specific "issues" explanation. Do not spend more than ~30 tool calls. Do not commit anything to git.
Return the structured output.`
}

const results = await pipeline(jobs,
  (j) => agent(samplePrompt(j), { label: `sample:${j.slug}`, phase: 'Sample', schema: SAMPLE_SCHEMA, model: 'fable', effort: 'medium' })
)
const ok = results.filter(Boolean)
const sampled = ok.filter(r => r.sampled)
log(`Sampling done: ${ok.length}/${jobs.length} returned, ${sampled.length} sampled, ${ok.length - sampled.length} could not be sampled`)
return {
  jobs: jobs.length, returned: ok.length, sampled: sampled.length,
  failed: ok.filter(r => !r.sampled).map(r => ({ slug: r.slug, issues: (r.issues || '').slice(0, 200) })),
  sampled_list: sampled.map(r => ({ slug: r.slug, bytes: r.total_bytes, rows: r.rows, date_range: r.date_range })),
}
