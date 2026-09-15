# L4 review package — final artifact close

As of 13 September 2026. This close note supersedes the delivery paths in
`L4_REVIEW_v1.md`; all prior runs and notes are preserved. The definitive review
run is `review_v4`, sourced from revenue `snapshot_v1` and financial-model
`snapshot_v4`. No investment direction, target, probability or November card
has been adopted. Free fitted parameters in this package: **0**.

## Final deliverables

All document paths below are relative to the L4 worktree root.

- Exactly two-page PDF: `deck/drafts/lane4_v1/review_v4/review_memo.pdf`.
- Editable source: `deck/drafts/lane4_v1/review_v4/review_memo.md`.
- Unsigned November card: `deck/drafts/lane4_v1/review_v4/unsigned_november_card.md`,
  with corresponding `unsigned_card.csv` and `unsigned_card.json`.
- Quantified decisions: `deck/drafts/lane4_v1/review_v4/decision_register.md`
  and `decision_register.csv` (23 alternatives, distinct L4-Dxx IDs).
- Source/assumption ledger: `deck/drafts/lane4_v1/review_v4/source_assumption_ledger.csv`.
- Frozen input copies, 29-record hash manifest, consistency checks and rendering
  receipt: `data/processed/forecast_methods/lane4_review_v1/review_v4/`.
- Final visual verification: the same data directory's `visual_QA.json` and
  `page-1.png` / `page-2.png`.

## Final changes and review

The final model snapshot clarifies its +/-1% scenarios as illustrative net
after-hedge consolidated revenue sensitivities. They are not measured RNPL,
conversion or FX coefficients. Numerical results are unchanged across financial
model snapshots v1-v4. The final memo explains the directly affected quarters
and the growth propagation; it does not describe a uniform full-FY27 shock.

The independent economics reviewer accepted the reported values and evidence
qualifications, then requested one card wording repair. C05 now reads:
"Company reported blended ADR and its year-over-year comparison with prior-year
reported blended ADR." This avoids implying a composition-controlled pricing
measurement. `review_v4` preserves `review_v3` and makes only that card wording
repair. No memo content or numerical output changed.

Both final PDF pages were visually inspected. Body text is 10.5 points, with
smaller readable table/source text. There is no clipping, overflow or overlap.
Parent independently approved both `review_v3` pages; the final `review_v4`
page PNGs are byte-identical to those approved pages. Poppler's Symbol and
ArialUnicode fallback warnings did not affect the visually checked output.

## Commands and checks

Run from the L4 worktree root. These exact commands produced the final run;
the builder refuses an existing run ID, so a future rebuild must use a new ID.

```powershell
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' analysis/src/forecast_methods/lane4_review_v1/run.py --revenue-dir data/processed/forecast_methods/lane4_revenue_v1/snapshot_v1 --model-dir data/processed/forecast_methods/lane4_model_v1/snapshot_v4 --run-id review_v4
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/Library/bin/pdftoppm.exe' -r 120 -png 'deck/drafts/lane4_v1/review_v4/review_memo.pdf' 'data/processed/forecast_methods/lane4_review_v1/review_v4/page'
```

Both commands exited 0. The package tests were run with:

```powershell
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -m unittest discover -s analysis/src/forecast_methods/lane4_review_v1/tests -v
```

All **16 tests passed**: 11 interval/card-scoring cases and 5 integrity cases.
The tests cover missing/nonfinite data, interval boundaries and rounding,
strict conjunction conditions, immutable snapshot handling, malformed scenario
sets and financial identities. No test was repeated after the final wording-only
card repair; the final builder reran its cross-file consistency checks.

| Final check | n | Result |
|---|---:|---|
| PDF page count | 2 | PASS |
| Valuation identities | 7 scenario rows | PASS, within USD0.001m / USD0.001 per share |
| EBITDA-to-FCF and FCF-less-SBC identities | 21 scenario/year rows | PASS, within USD0.001m |
| Model-to-revenue guide reconciliation | 1 reference scenario | PASS |
| Q4 dollar contribution conservation | 2 lag rows | Sum 1.0000000000000009 |
| November card | 11 rows | All unsigned, future observations absent |
| Quantified decision register | 23 alternatives | Original D-01 separately preserved in L4-D09 |
| Reference Q4 guide | 1 scenario | USD3,123.41911517339m |
| Reference EBITDA valuation lens | 1 scenario | USD184.662755252916/share; 31 Dec 2027 convention |

Final PDF SHA256:
`8bfe0b07dc66b92de8be424e37a557363cf33eb989a6938c6303376d89c8e641`.

Page image SHA256 values:

- Page 1: `7d56681208cad5d6caa3e49c9df5a66302c1afe7d7f1e8e3d19fd42ba788771a`.
- Page 2: `7505cf25bb3758d408fa707cd0eba624b54ee0260defdeccf217548032f4df15`.

## Limits and remaining dependencies

Fixed 2/3 K0 remains a **provisional benchmark**, awaiting accepted L3 conversion
estimation and validation. Separate L3 FX/RNPL inputs are also pending. Neither
dependency has been filled with zero, an invented coefficient or a claim of
completed seasonal fitting. Existing A2 PARTIAL, B2 FAIL and ADRv3 identification
and validation limits remain explicit. Revenue consensus is not called
management-guide consensus. The revised 31 December 2027 valuation convention
is distinguished from the inherited approximate September 2027 label.

No tests or final builder checks failed. The pending L3 inputs prevent final
conversion/FX-dependent claims and adoption, but do not prevent review of this
labelled benchmark package. This subagent has made no registrations, scorer
runs, commits or changes to pre-existing protected sources. Parent owns those
integration and publication steps.

## RESUME

Use only `review_v4` for final L4 artifact links. The earlier runs remain audit
history. Confirm the corrected C05 definition in the unsigned card and retain
the independent review alongside the final hashes. Parent's accepted visual
review carries through because both final page images match exactly. Accepted
L3 conversion or FX/RNPL inputs require explicit source versions and hashes,
a reviewed integration change and a fresh run; do not relabel this benchmark
as integrated. Keep direction, valuation adoption and card decisions unsigned
until the team makes those choices.
