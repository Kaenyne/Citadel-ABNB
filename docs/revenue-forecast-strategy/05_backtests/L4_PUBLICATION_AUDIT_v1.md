# L4 publication audit

14 September 2026. Parent with two independent reviewers. Audited analytical
commit `3da2903e2c78f6beea358819e7c561b07a5f49a3` on `codex/lane4-full`.
**PASS: no blocking numerical, economic, source or publication-payload finding.**
The user explicitly requested an audit followed by a Git push. That request
supersedes the earlier local-only publication notes, which remain preserved.

Destination is the configured public repository
`https://github.com/Kaenyne/Citadel-ABNB.git`, branch `codex/lane4-full`.
The remote branch was absent at the pre-push check. Only an ordinary non-force
branch push is authorized here; no merge, teammate outreach or investment
decision is part of this task. This audit commit adds records and a reusable
audit runner without changing any previously committed artifact or forecast.

## Fresh verification

| Check | Scope | Result |
|---|---|---|
| Source implementation tests | 18 tests | PASS |
| Revenue integration tests | 49 tests | PASS |
| Financial model tests | 9 tests | PASS |
| Memo/card/source tests | 18 tests | PASS |
| Independent revenue arithmetic | 21,252 checks, 30 source and 30 output hashes | PASS; maximum difference $1.275e-11 million |
| Exported workbook audit | 316 cached-value/cash/share/expectations checks, 1,875 formulas | PASS; zero formula errors or external links |
| Original protected bytes | 4,381 tracked files, 76 registry files, 135 external FX files | Unchanged |
| Accepted L3 bundle | 108 manifest files, 104 research lineage objects, 32 acceptance bindings | Verified |
| Independent financial publication review | Eight final artifact hashes, 45 fresh horizon checks | PASS; prior 759 unchanged financial checks remain applicable |
| Independent publication payload review | 1,056 added files across four L4 commits; 11 earlier blob versions | No detected credential material, licensed raw exports, runtime payloads or oversized files |

All 94 focused tests passed again. Test wall times were approximately 5.03s
(source), 9.28s (revenue), 0.53s (model) and 1.58s (review), run independently.
Both numeric audit commands exit 0. The workbook's maximum cache difference
is $0.000007376 per share in rounded legacy replication inputs, below $0.001.
The 108-file bundle and original source bytes were rechecked successfully.
No registry/scored output changed, so the historical scorers were not rerun.

Receipts and complete command logs are under
`data/processed/forecast_methods/lane4_publish_audit_v1/publication_20260914/`.
The first parallel preservation invocation did not produce a retained final
receipt; no success is attributed to it. The separate
`publication_preservation_20260914/preservation.json` and final runner-guard
check `publication_guard_20260914/preservation.json` both pass (about 2.5s each).
All old failed/development logs remain intact.

The prior rendered views and all final visual-review bindings are unchanged,
so no cosmetic rebuild or additional workbook version was produced. The
preview process's documented exit 1 after valid PNG output remains a known
nonblocking runtime limitation; this is not reported as a clean renderer exit.
Strict Git whitespace findings in preserved source SVG/text serialization
also remain documented rather than changing accepted bytes.

## Source and publication scope

The full L4 payload from committed L1/L2 base
`1c87628cedbc94ab8a0e8552743c94485ef353b8` comprises 1,056 additions totaling
71,557,331 bytes. The largest file is 2,020,842 bytes; all 11 workbook files
are generated L4 review outputs. The source reviewer checked current files
and 11 historical blob versions because those versions also travel with the
branch. No secrets or restricted raw exports were detected by that review.

Of 575 committed hash-binding occurrences, 571 match exactly. Four occurrences
refer to two protected inherited notes, `LANE2_MEMO_READY_CLAIMS.md` and
`ALPHA_F_RNPL.md`, whose Git blobs use LF and captured worktree hashes use CRLF.
LF-to-CRLF conversion reproduces those captured hashes exactly; there are zero
substantive differences. Their frozen captured copies and all new bundle,
model, workbook, chart, source-copy and QA bytes match exactly. This caveat is
explicit and does not relax financial or new-artifact hash checks.

Independent source signoff:
`L4_PUBLICATION_SOURCE_AUDIT_v2.md`. Independent financial/claims signoff:
`L4_PUBLICATION_FINANCIAL_AUDIT_v1.md`. Both bind the analytical commit above;
the additional audit-only commit leaves those conclusions applicable.

## Financial conclusions remain conditional

Own Q4 revenue $3,179.343654 million exceeds the frozen Yahoo/LSEG revenue
estimate $3,161.021490 million by $18.322164 million. The implied guide is
$3,123.419115 million under its separate cushion assumption. The guide-minus-
revenue diagnostic is not a measured guide surprise. The same-cushion Street
guide and its $17.999878 million gap remain explicitly hypothetical.

The conditional September 2027 value remains $182.867016 per share, using
256/365 of FY27 cash/share flows and full FY27 EBITDA at inherited 16.5x.
All source dates, uncertain later-quarter assumptions, declined free-weight
promotion, unidentified central FX/RNPL adjustment and unsigned team decisions
remain visible. Publication does not convert these assumptions into an
investment recommendation or an established executable edge.

## Reproduction

`analysis/src/forecast_methods/lane4_publish_audit_v1/README.md` lists the six
audit commands. Each accepts a new run ID and preserves existing receipts.
The runner permits the audited commit or an additions-only descendant, which
allows these audit records to be committed without altering analytical inputs.

## RESUME

Use the published L4 branch and the final versions in `L4_CLOSE_HANDOFF_v2.md`.
Keep this publication authorization distinct from signing the pitch, adopting
targets/probabilities or merging to main. Future source or model changes need
focused revalidation and new artifacts; unchanged inherited assumptions and
documented source-normalization/runtime limitations remain explicit.
