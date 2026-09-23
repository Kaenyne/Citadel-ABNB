**PRs 39-44 audit package**

Start with [AUDIT.md](AUDIT.md) for the findings, priorities, exact GitHub commit references, numerical effects and proposed fixes. This package publishes the review and evidence; it does not implement the proposed production changes or revise the financial model.

The `snapshot/` and component `source/`, `data/` and `fixture/` directories preserve the small historical code/data inputs used by the checks. They are audit evidence, not additional production pipelines. These are partial source snapshots: some historical documents retain personal paths and links to omitted background files from the original PRs. The audit wrappers explicitly point calculations at the included fixtures.

Run from the repository root with Python and the repository's pandas, numpy and scipy dependencies:

```text
python outputs/pr_39_44_audit/reproduce_root_findings.py
python outputs/pr_39_44_audit/reviews/reproduce_reviews_findings.py
python outputs/pr_39_44_audit/external/reproduce.py
python outputs/pr_39_44_audit/adr/reproduce_adr_findings.py
python outputs/pr_39_44_audit/39/check_pr39.py
```

The checks use the included committed aggregates and synthetic cases without network calls or large raw archive downloads. They write results inside this audit directory. Generated scratch files, synthetic placeholder archives and Python caches are ignored. Machine-readable results accompany each script; separate component findings explain the verification scope and limits.
