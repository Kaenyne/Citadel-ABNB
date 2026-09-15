# SC-A source precision — bounded preregistration

2026-09-14. Claimed by `adr_hotel` in `WORKBOARD_L3_SOURCE_CONTRACT_v1.md`; additive follow-up to completed L3, not a restart or forecast contest.

Scope is exactly 24 quarters, 2020Q3–2026Q2, and four frozen KPI fields: `gbv_musd`, `revenue_musd`, `nights_m`, `adr_usd` (96 quarter/metric cells). Other columns of the wide panel are explicitly out of scope. Each cell will carry checked/unavailable status, original release and available higher-precision value with units, source document/URL/section, original publication date/time basis, conservative first-known date, definition and discrepancy classification. A finer number in a later document is never backdated into an earlier forecast information set. A source's lower precision is not a revision, and a derived ratio is not falsely labeled a directly disclosed ADR.

Read original public SEC earnings exhibits and filings, using existing source indices and compact public material. Search is bounded to the 23 original earnings exhibits and 2020Q3 IPO filing, plus at most 24 relevant periodic filing documents or original-source fallbacks. Record failed attempts and unresolved exact timestamps; existing webcast timestamps are certainly-public-by proxies, not exact release times. No consumer/help Airbnb endpoints, licensed sources, raw-store expansion or writes to protected histories.

Classifications are exact/rounding/later precision/revision/transcription/definition difference/unresolved, with separate value and timing status where a single category would conceal ambiguity. Revision requires explicit support; differences within the published precision interval are rounding-compatible. Differences beyond that interval are unresolved unless original transcription or a definition change is demonstrated. All 96 cells and all24 quarters remain in the denominator, including unavailable evidence. No empirical pass line or source-coverage threshold is used to hide gaps.

Sensitivity is algebraic only: at inherited fixed 2/3–1/3 policy, `dR/dGBV_lag1 = lambda_s*2/3`, `dR/dGBV_lag2 = lambda_s*1/3`, holding the explicitly identified inherited lambda fixed. Report normalized `dR/lambda` where no compatible inherited coefficient is available. For the current Q3 illustration, use the unchanged `cohort_fx_v2/results_v2/kernel_inputs.csv` Q3 2026 inherited operational coefficient, not the new full22 OLS fit. Combined input differences are summed linearly. No coefficients are fitted, no corrected forecast series is produced, and the free-weight FAIL/retained fixed policy remains unchanged.

The offline runner reads compact frozen audit facts and existing immutable panel/coefficient inputs, writes only to a new destination, validates exact coverage/units/provenance/date ordering and produces discrepancy, status and held-fixed sensitivity ledgers. Tests must meaningfully reject missing coverage, duplicate cells, false earlier availability, unit mistakes and output overwrite; reproducibility is checked in a new directory. Every unresolved material source finding stays visible.

## RESUME

Complete the bounded original-source audit, freeze compact facts and source manifests, run integrity/sensitivity checks without refitting, and request the assigned independent SC-C review. The lead owns additive source-contract integration and workboard completion.
