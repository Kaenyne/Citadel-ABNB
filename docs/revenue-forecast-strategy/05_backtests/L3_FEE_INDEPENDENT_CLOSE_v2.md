# L3 fee-panel independent closeout v2

Independent reviewer `adr_hotel` · 2026-09-13 · `codex/lane3-full`. This closes the follow-on issue in `L3_FEE_INDEPENDENT_REVIEW_v1.md`; that original findings record remains unchanged.

**Implementation review PASS; empirical research still pending scheduled captures, causal identification absent.** The final runner loads the September 11 diagnostic using its original frozen `fee_panels/sample_ids.csv`, separately from caller-provided future-wave metadata. The manifest includes both original and supplied metadata paths when distinct. This preserves the repaired per-capture metadata availability guard without making a new admissible pre-wave snapshot incompatible with the old diagnostic.

Independent verification:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/fee_panel_v1/test_fee_panel.py -q -p no:cacheprovider
```

Exit 0; **19/19 tests passed in 7.76 seconds**. The new end-to-end test supplies September 13 metadata at September 19 as-of, invokes the consumer into a new temporary output, and verifies the old diagnostic retains its six residence-known rows and records the frozen metadata manifest entry. The test uses no supplied wave captures; the existing per-capture regression separately verifies that metadata later than an actual pre capture is rejected. Read-through confirmed the original four independent findings remain repaired: all relevant known-residence strata gate; unknown residence remains descriptive; missing fee regime is rejected; capture-specific metadata timing is enforced. The canonical updated empirical output is `data/processed/forecast_methods/fee_panel_v1/reviewed_v3`.

No fee package code or empirical output was altered by this reviewer. No theta was estimated from future or fabricated captures. The original one-pre-observation, residence-proxy, early-migration and October comparator limitations remain. The archival-diagnostic interaction is resolved without weakening any identification rule.

## RESUME

The lead may include reviewed_v3 and the guarded consumer in the immutable L3 handoff after committing the reviewed research sources. Later scheduled captures require a new output directory, dated metadata, the unchanged coverage/precision gates, and a qualified association interpretation. L4 must not treat current null fee rows as zero or as measured uplift.
