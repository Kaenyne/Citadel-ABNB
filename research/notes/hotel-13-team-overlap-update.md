# Hotel research overlap update: September 7, 2026

**No additional hotel source URLs or hotel-specific research files were found in the new commit delta.** The existing 13-market overlap conclusions are unchanged by this bounded update.

Compared complete, non-truncated recursive GitHub trees for the previous frozen review, `e3055e627f4b7952c592939a03849f5fc32b9235`, and the updated main commit, `3de6ec7a2a76e0053d36d2bf124d8b2a7ce1a2ba`. [Immutable commit comparison](https://github.com/Kaenyne/Citadel-ABNB/compare/e3055e627f4b7952c592939a03849f5fc32b9235...3de6ec7a2a76e0053d36d2bf124d8b2a7ce1a2ba).

The old tree contains 1,087 blobs and the new tree 1,089. Exactly three files changed; none was removed:

| File | Change | Bytes | Review decision |
|---|---|---:|---|
| `analysis/src/abnb_historicals_workbook.py` | Added | 49,297 | Downloaded by immutable blob SHA and reviewed as text; never executed. |
| `model/ABNB_historicals.xlsx` | Added | 88,422 | Not downloaded after README and generator scope review. |
| `model/README.md` | Modified | 1,554 | Downloaded by immutable blob SHA and read in full. |

No research notes, source ledgers or hotel processed data changed between the two trees. The README describes an aggregate Airbnb historical workbook covering 1Q21–2Q26: KPIs, revenue and margin decomposition, earnings guidance/consensus comparisons and stock reactions. It contains no hotel-specific claim, city-registry URL or external source URL.

The 49 KB generator was also downloaded and read as text, with a syntax-only `ast.parse` check; it was never imported or executed. Its workbook row definitions and Sources sheet cover aggregate company KPIs, earnings and returns. The entire text contains zero occurrences of hotel, boutique or independent and zero HTTP(S) URLs. All **eight referenced input CSVs have identical Git blob SHAs in both trees**, including the KPI panel, cost lines, guidance, consensus and return series. No new hotel-specific source or row was identified. Collection stopped at that point; the workbook binary was not downloaded. This result is not a full audit or recalculation of the historical model.

Both downloaded text files' Git blob SHAs were recomputed from their bytes using the Git blob header and matched the immutable tree. Their byte lengths also matched, and their SHA-256 hashes are recorded. Both full tree artifact hashes are saved. The previous tree and `team_review/` mirror were preserved.

Outputs are in `data/raw/hotel_13_market_extension/team_update_3de6ec7/`:

- `changed_source_urls.csv`: header-only file with `location,url,sha256`; **zero incremental URLs** to merge with the existing inventory.
- `update_summary.json`: exact commits, changed paths, download decisions, hash checks, findings and limitations.
- `tree_delta.json`, new immutable tree response, README and generator source text, and semantic/input-hash review records.
- `build_overlap_update.py`: reproducible tree comparison, hash validation and URL extraction. CSV inputs, if present, are parsed into cells before URL extraction; this delta required no CSV download.

The review covers these repository versions only. It cannot certify absence of overlap with Jessica's private, off-repository or uncommitted material.
