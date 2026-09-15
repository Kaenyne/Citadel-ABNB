# GE-SOURCE — reviewed source and arithmetic handoff

15 September 2026. Additive closure of `GE_SOURCE_RESULTS_v1.md`; the first note, first inventory attempt and failed public fetches remain preserved. Evidence base: `2dfe0c2a1852181a246f4b6b9072e05e844d52d5`. No forecast fit, statistical refit, registry, scorer or original source mutation.

**Source verdict: PARTIAL.** The held data support daily earnings gaps and regular-session legs for all 23 ledger events. Zero real timestamped ABNB/QQQ intraday event panels were found. No direct market forecast of management's guide was identified in the structured expectation register. Proceed with the explicitly conditional four-quarter model and daily-leg exhibits; no call-only or established trading-edge claim follows.

Canonical source inventory: `data/processed/forecast_methods/gbv_event_v1/sources_v1/run_v2/`. It contains 23 event-date records, five held price/return inventories, the 20 original pre-guide expectation rows, dated current expectations, the catalogue's one relevant intraday-method reference, and exact input hashes. The register contains 1,330 rows, including 1,159 DoltHub observations; 16 original pre-guide rows have a positive value, usable flag and attributed vendor. The other four are two missing/quarantined and two unattributed observations. Missing rows remain missing.

The public Yahoo five-minute probe for the latest event produced no data. The first socket-restricted attempt is in `run_v1/`; the permitted-network attempt returned HTTP 429 and is in `run_v2/`. No retry or access workaround followed. Provider documentation and primary-release checks are in `sources_v1/primary_web_checks.json`. A suitable historical intraday export and exact release/call-start/call-end clocks are the remaining objects needed for actual call-leg charts; these are not prerequisites for the daily-leg deliverable.

## Byte-hash clarification

The first note quoted the retained returns_v1 manifest's price-file SHA256 as the file hash without spelling out line-ending normalization. The current worktree CSV uses CRLF and hashes to **`a94c35e2c70f5bc9ce4b5bd85343fed199ac1e941b94d287bb3ee7780b799286`**. Converting CRLF to LF, without changing any data, produces **`5b03005c30b1793e2d146e6a76fc352ecee56b7fbaf0e9f737bd479652b7a253`**, exactly the retained source-manifest hash. The canonical source inventory and independent review bind the actual CRLF bytes. No numerical discrepancy is implied.

## Primary clocks and expectations

The [August 6 SEC letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm) confirms the issued Q3 revenue range of $4,690-4,770m, low-double-digit Nights and Seats Booked guidance and a scheduled 17:00 New York call. Q3's guide is an observed comparator, not an unknown future target. November 5, 2026 remains a project expected/planning date here; a company announcement was not found in the bounded search, which is not proof of absence. No future call time is assigned.

The 2025Q3 inherited L3 webcast proxy of 21:30Z differs from the [official scheduled 17:00 ET / 22:00Z call](https://investors.airbnb.com/press-releases/news-details/2025/Airbnb-to-Announce-Third-Quarter-2025-Results/default.aspx). Do not use inherited public-by proxies as call boundaries. Daily event dates are unaffected. First-public minutes and call ends remain uncertified.

September 13 Yahoo/LSEG-family revenue expectations are $4,744.88187m for Q3 and $3,161.02149m for Q4, n=36, captured at 15:20:58Z. Preserve the dated S&P Q4 $3,160m and Zacks Q4 $3,200m anchors separately; neither was newly refreshed in this source audit. DoltHub mirrors Zacks, and Yahoo/Alpha Vantage distribute the same LSEG-family information. Do not count channels as independent panels or infer a revision from different display precision. Q1/Q2 2027 quarterly Street observations are absent from the reviewed register.

These are expectations of realised revenue. Dividing by a common assumed cushion makes an **implied guide proxy**, not an observed forecast of management's guide. With the same cushion on both sides, the guide-gap percentage equals the revenue-gap percentage by construction; it supplies no independent confirmation. Consensus divided by our weighted GBV is **break-even conversion conditional on our GBV**, not a directly observed Street conversion forecast. Dollar midpoint ±$0.5m scoring remains a project convention; retain raw errors.

## Independent review of integration and events

`analysis/src/forecast_methods/gbv_event_v1/sources/review.py` imports no integration, event or candidate functions. It independently checks deterministic arithmetic and source joins, not the event regression results or a new predictor. Its first reviewed inputs are `integration_v1/model.json` and `events_v1/run_v2`.

**316/316 checks passed**, maximum absolute difference **3.63798e-12**. These cover all four revenue/guide conversion rows, the fixed same-season EWM arithmetic, comparison gaps, all 23 events' gap/session/close-to-close/+5/+20-day daily returns, strict-prior median cushions, primary source values and all 21 earlier-origin DoltHub joins. Receipt and cell-level results: `sources_v1/review_v1/`.

Q2 2027 is a real lagged-GBV conversion extension: conditional Q1 2027 GBV $32,424.358476m feeds revenue $4,048.395308m and implied guide $3,977.184182m. This confirms the arithmetic, not forecast promotion. The first three revenue/guide rows preserve the earlier L4 working scenario. No second RNPL haircut, duplicate FX/fee overlay or margin/FY2028 extension was found.

Issues communicated before workbook creation:

- The original integration's all-vendor comparison included the August 6 historical `pre_guide` LSEG row alongside current September observations. Selected Yahoo was correct; the historical row must be filtered or explicitly separated.
- Label the comparison's conversion as conditional break-even conversion. Keep the Q3 derived guide diagnostic distinct from its issued guide and from current revenue expectations.
- Bind K0's directly read KPI panel/calendar and cushion provenance, not only engine.py. A common conservative information date is not an original source release date.
- Event run_v2 normalized explicit intraday source timestamps to dates. Current original PG/AP observations are date-only and the numerical source joins passed, but an additive guard must distinguish the documented morning convention from explicit times, rejecting naive, exact-close and post-close timestamps.

The owning agents retain responsibility for their additive repairs. This note does not mark unreviewed replacement outputs as reviewed; later receipts must bind their exact hashes.

## Reproduce / resume

From the worktree root, choose a new output name:

```text
python -B analysis/src/forecast_methods/gbv_event_v1/sources/run_v2.py --name inventory_review_new
python -B analysis/src/forecast_methods/gbv_event_v1/sources/review.py --name arithmetic_review_new
```

Both commands refuse existing output directories and use only held inputs. The arithmetic review accepts `--model` and `--events` for an explicitly identified additive replacement. No network is needed; omit the optional public probe. Parent should finish the editable workbook and two-page memo using the conditional wording, missing-data markers and independently checked daily legs, then request exact-version closure for the owning agents' repairs.
