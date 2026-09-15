export const meta = {
  name: 'github-altdata-reviews-triage',
  description: 'Opus triages the high/medium GitHub candidates from scout metadata, 25 per agent, few fetches (batch ids via args from state.py --batches)',
  phases: [{ title: 'Review', detail: 'Opus, 25 candidates per batch, metadata triage', model: 'opus' }],
}

const WT = 'C:/Users/krish/citadel-abnb-ghcat'
const CONTEXT = `${WT}/docs/github-altdata/CONTEXT.md`
const REVIEW_DIR = `${WT}/data/processed/github_altdata/reviews`
const CATS = ['str_airbnb_direct','competitor_ota','hotel_lodging','travel_volume_transport','housing_rental','macro_consumer_spend','fx_rates','web_app_engagement','social_text_news','regulatory_legal','company_filings_estimates','markets_options_positioning','events_weather_shocks','geospatial_poi_mobility','methods_tooling','academic_replication','other']

// args.opus_batch_ids (high tier) and args.sonnet_batch_ids (medium tier); each batch's candidates live in
// reviews/pending/batch_NNN.json (written by state.py --batches). Legacy args.batch_ids -> opus.
const opusIds = (args && Array.isArray(args.opus_batch_ids)) ? args.opus_batch_ids : ((args && Array.isArray(args.batch_ids)) ? args.batch_ids : [])
const sonnetIds = (args && Array.isArray(args.sonnet_batch_ids)) ? args.sonnet_batch_ids : []
if (!opusIds.length && !sonnetIds.length) return { error: 'no ids passed (run state.py --batches and pass opus_batch_ids / sonnet_batch_ids)' }
const batches = [
  ...opusIds.map(b => ({ b, model: 'opus', file: `${REVIEW_DIR}/pending/batch_${String(b).padStart(3, '0')}.json` })),
  ...sonnetIds.map(b => ({ b, model: 'sonnet', file: `${REVIEW_DIR}/pending/batch_${String(b).padStart(3, '0')}.json` })),
]
log(`Review triage: ${opusIds.length} Opus batches (high tier) + ${sonnetIds.length} Sonnet batches (medium tier), up to 25 each`)

const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    verdicts: { type: 'array', items: { type: 'object', properties: {
      url: { type: 'string' },
      slug: { type: 'string', description: 'short filesystem-safe slug, e.g. insideairbnb-archive-2015-2019' },
      usefulness: { type: 'string', enum: ['possibly_useful', 'unlikely', 'none'] },
      verdict: { type: 'string', enum: ['sample', 'catalog_only', 'discard'] },
      priority: { type: 'integer', description: '1 = pull a sample now (fills a numbered gap or is a substantial dataset we lack); 2 = sample only if budget allows; 3 = catalogue is enough' },
      source_family: { type: 'string', description: 'the underlying data source, so near-duplicates can be collapsed: e.g. "insideairbnb-nyc", "bts-t100", "eurostat-tour_occ", "zillow-zori", "opportunity-insights-tracker", "kaggle-ab-nyc-2019"' },
      category: { type: 'string', enum: CATS },
      data_kind: { type: 'string', enum: ['stored_dataset', 'acquisition_method', 'both', 'pointer_to_external_host'] },
      one_line: { type: 'string', description: 'catalogue line: what it is, coverage, size, licence' },
      abnb_use: { type: 'string', description: 'which KPI / gap it could inform and how' },
      sample_plan: { type: 'string', description: 'if verdict=sample: files/paths or the keyless pull command, and the row/byte cap (<= 25 MB total, prefer <= 5 MB)' },
      tos_or_license_flag: { type: 'boolean' },
      duplicate_of_existing: { type: 'string' },
      reasoning: { type: 'string', description: 'one sentence' },
    }, required: ['url', 'slug', 'usefulness', 'verdict', 'priority', 'source_family', 'category', 'data_kind', 'one_line', 'abnb_use', 'sample_plan', 'tos_or_license_flag', 'reasoning'] } },
  },
  required: ['verdicts'],
}

function reviewPrompt(b, file) {
  return `You are triage batch ${b} of an alt-data cataloguing run for an Airbnb (ABNB) stock pitch. First Read ${CONTEXT} (what we hold, the 20 numbered gaps, the rules). Then Read ${file}: a JSON array of up to 25 candidate GitHub repositories that Sonnet scouts flagged as high or medium potential (fields: url, category, data_kind, what_it_holds, why_all, potential, hits, themes, geography, time_coverage, size_hint, license, duplicate_of_holding). The scouts already opened most of these pages; treat their what_it_holds as reasonably reliable.

This is a BUDGET-CONSCIOUS triage, not a verification pass. Decide from the metadata. You may WebFetch a repository page (https://github.com/<owner>/<repo>) or its raw README for AT MOST 6 candidates in this batch, and only when the decision between 'sample' and 'catalog_only' genuinely turns on what is committed. No \`gh api\` calls. No cloning.

Per candidate decide:
- usefulness: 'possibly_useful' if ANY plausible route to an ABNB KPI, a numbered gap, a regional read, a method we lack, or a longer/older/finer version of something we hold; 'unlikely' if marginal; 'none' if irrelevant, dead, or a re-analysis of the standard Kaggle NYC-2019 / Seattle-2016 Airbnb files with nothing new.
- verdict: 'sample' = a Fable agent should pull a SMALL sample (committed data files, release assets, Zenodo/Dataverse/S3/GitHub-release links, or a keyless pull against a PUBLIC statistical source); 'catalog_only' = useful but not for an agent to pull (scrapers of third-party sites — running them is a human terms-of-service call; API keys or logins; anything touching airbnb.com; restrictive licences; Kaggle-only hosting; too large to sample sensibly; a pure method/tooling repo whose value is the code, not stored data); 'discard' = usefulness none.
- priority (only meaningful for 'sample'): 1 = fills a numbered gap in CONTEXT.md or is a substantial dataset we do not hold (pull now); 2 = nice to have; 3 = the catalogue line is enough. Be strict: we can afford roughly one priority-1 per five 'sample' verdicts.
- source_family: name the underlying source so that ten repos mirroring the same file collapse to one sample (e.g. every repo that just re-hosts Inside Airbnb NYC gets "insideairbnb-nyc"; every BTS T-100 loader gets "bts-t100").
- sample_plan: for 'sample', the concrete files/paths or command and the cap; otherwise a short reason.
- reasoning: one sentence.

Every candidate in the file must get a verdict, in the same order. Write the full JSON ({"verdicts": [...]}) to ${REVIEW_DIR}/review_${String(b).padStart(3, '0')}.json before returning the structured output.`
}

const reviews = await pipeline(batches,
  (batch) => agent(reviewPrompt(batch.b, batch.file), { label: `review:${batch.b}:${batch.model}`, phase: 'Review', schema: REVIEW_SCHEMA, model: batch.model, effort: 'medium' })
)
const verdicts = reviews.filter(Boolean).flatMap(r => r.verdicts || [])
const counts = {}
for (const v of verdicts) counts[v.verdict] = (counts[v.verdict] || 0) + 1
const p1 = verdicts.filter(v => v.verdict === 'sample' && v.priority === 1).length
log(`Review triage done: ${verdicts.length} verdicts ${JSON.stringify(counts)}, priority-1 samples ${p1}`)
return { batches: batches.length, returned: reviews.filter(Boolean).length, verdicts: verdicts.length, counts, priority1_samples: p1 }
