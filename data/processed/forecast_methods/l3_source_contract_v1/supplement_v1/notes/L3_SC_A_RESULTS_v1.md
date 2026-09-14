# SC-A source precision results

2026-09-14 · author `adr_hotel`; independent reviewer assigned `nclh`. Bounded additive source audit under `WORKBOARD_L3_SOURCE_CONTRACT_v1.md` and `L3_SC_A_PREREG_v1.md`. No forecast selection, coefficients fitted, registry writes, historical rewrites or production adoption.

Exactly **24 quarters, 2020Q3–2026Q2; four metrics; 96 cells**. The scope is GBV (`gbv_musd`), GAAP revenue (`revenue_musd`), booked aggregate units (`nights_m`) and ADR (`adr_usd`). Every other wide-panel column is explicitly out of scope. Reading all quarters does not certify all columns.

The bounded search covered 23 original SEC shareholder-letter exhibits and 24 periodic/IPO documents. Primary text was checked for 46 of 47; the original IPO body remained unavailable although its SEC filing index was accessible. Four original 2020Q3 values therefore remain unavailable. The other 92 original cells were checked against the original quarterly summary and, where available, finer appendix values. Direct Python network retrieval failed in this environment; tool-based primary SEC text retrieval supplied the successful checks. No licensed material, Airbnb consumer endpoints or expanded raw stores were used. Compact numeric facts and paraphrases are frozen, not raw HTML.

| Main cell classification | n |
|---|---:|
| Exact to selected checked source value |67|
| Rounding-compatible difference |18|
| Later document supplies finer value |4|
| Definition/derivation difference |2|
| Unresolved |5|
| Total |96|

The five unresolved are three IPO cells without original evidence plus 2020Q4 revenue and 2025Q2 GBV. The remaining IPO ADR cell is classified by its demonstrated derivation difference but still explicitly has original status unavailable. Categories concern source agreement, not a count of company reporting errors. No revision or transcription is claimed without supporting evidence.

Material and decision-useful findings:

| Item | Frozen | Checked primary evidence | Treatment |
|---|---:|---:|---|
|2026Q2 GBV, USDm|27,200|27,247; H1 56,434|Original Q2 filing precision, inherited filed-date basis 2026-08-06; exact acceptance time unavailable|
|2026Q1 GBV, USDm|29,200|29,187|Already in original Q1 10-Q filed 2026-05-07. Q2 H1−Q2 subtraction later corroborates it; it is not the first disclosure|
|2025Q2 GBV, USDm|23,500|23,447|Original letter says 23.5B, original 10-Q says 23,447m: 53m gap exceeds the headline ±50m interval. Preserve unresolved presentation inconsistency|
|2020Q4 GAAP revenue, USDm|859.1|859.264|Original statement reports 859,264 thousand. Difference +0.164m exceeds frozen ±0.05m precision; costline pipeline origin identified, revision not demonstrated|
|2020Q3 ADR, USD|129.92|129.95 in later Q4 2020 letter|Frozen writer explicitly calculates 8029.3/61.8 rounded to cents. Direct reported ADR uses underlying precision; original IPO value unavailable|
|2020Q4 ADR, USD|127.55|127.56 in original letter|Frozen writer calculates 5905.7/46.3 rounded to cents; calculated ratio and disclosed ADR differ|
|2022Q2 GBV later history, USDb|17.0|Original appendix 16,980.6m; later Q4 2023 summary 16.9B|Supplemental unresolved display inconsistency; no unexplained revision promoted|

Primary references: [Q2 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm), [Q1 2026 10-Q](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000014/abnb-20260331.htm), [Q1 SEC filing index](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000014/0001559720-26-000014-index.html), [Q2 2025 10-Q](https://www.sec.gov/Archives/edgar/data/1559720/000155972025000025/abnb-20250630.htm), [Q2 2025 letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312525174438/d17531dex991.htm), [Q4 2020 letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312521056952/d147144dex991.htm), [Q2 2022 letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312522210001/d353427dex991.htm), [Q4 2023 letter, Quarterly Summary](https://www.sec.gov/Archives/edgar/data/1559720/000119312524033706/d646462dex991.htm). All47 document attempts and relevant sections are in the machine-readable manifest/ledger.

Finer or later corroborating GBV was located for **18/24 quarters**. Original letter appendices supply million-dollar values for 2020Q4 through 2022Q2; the 2021Q3 comparative supplies 2020Q3 corroboration. No finer quarter value was confirmed for 2022Q3–2023Q4; annual totals and coarsely rounded narratives cannot fill those six gaps. The original precision distinction matters: the frozen early 2020 GBV values already agree with appendix precision even though the headline summaries use tenths of billions.

The four 2024 quarters obtain finer values only through later documents: Q1 22,925m (2025-05-01), Q2 21,213m (2025-08-06), Q3 20,085m (2025-11-06), and calculated Q4 17,561m (FY81,784 less later comparative nine-month64,223, joint availability2025-11-06). Calculated Q4 2025 GBV20,418m uses FY91,273 less stated nine-month70,855, available2026-02-12. Each subtraction inherits up to ±1m from its two rounded inputs. Summing separately rounded 2025 Q1–Q3 amounts produces70,854 rather than the stated70,855; this 1m aggregation difference is retained, not silently forced to reconcile. No calculated value is described as a directly disclosed quarter or dollar-exact amount.

Dates: original SEC URLs currently served are not proof of archived historical bytes. The inherited shareholder-letter timestamps represent webcast starts and are certainly-public-by proxies, not exact release times. SEC index clocks for IPO, Q2 2025 and Q1 2026 are recorded as displayed; the pages do not print their timezone, so no timezone is invented. The Q2 2026 index request failed; its filed date remains inherited calendar metadata, without a verified acceptance clock. The frozen IPO calendar uses an approximate2020-11-15 date while the [SEC index](https://www.sec.gov/Archives/edgar/data/1559720/000119312520294801/0001193125-20-294801-index.html) reports filed2020-11-16 and displayed acceptance16:23:52. Original same-day value availability remains unvalidated. Both dates precede every W1 guide origin (earliest2023-02-14); no refit or performance effect is claimed from this date-only observation.

Denominators: original labels are **Nights and Experiences Booked** through2025Q1 and **Nights and Seats Booked** from2025Q2. They count stay nights plus participant seats for experiences, and the latter includes services. They are not pure hotel room nights. Direct letter ADR is GBV per aggregate booked unit. Whole-million 10-Q counts such as156 and148 are coarser than original156.2/148.3; they are explicitly excluded as precision upgrades. Subtracting coarse H1 and Q2 counts cannot manufacture a more precise Q1 count.

Held-fixed arithmetic only: `dR/dGBV_lag1=lambda*2/3`, `dR/dGBV_lag2=lambda*1/3`. The inherited current Q3 coefficient is17.2548908953%, ewm, five seasonal observations, from `cohort_fx_v2/results_v2/kernel_inputs.csv`, information date2026-09-13. Applying +47m Q2 and −13m Q1 differences gives `(2/3)*47+(1/3)*(-13)=27m` in the weighted denominator, hence **+4.658820541731m implied revenue**. This is one local sensitivity, n=1, with zero fitted parameters. The other48 rows provide normalized derivatives across24GBV quarters, retaining missing deltas where finer evidence is unavailable. Revenue precision affects historical outcomes or any future refit, so its effect is expressly not quantified by a held-lambda GBV derivative. No revised forecast series is emitted. Fixed policy retained; free-w FAIL in both windows unchanged.

Exact commands, from lane3-full:

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/l3_source_contract_v1/precision/test_precision.py -q -p no:cacheprovider
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/l3_source_contract_v1/precision/run.py --out data/processed/forecast_methods/l3_source_contract_v1/precision/results_v1
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B analysis/src/forecast_methods/l3_source_contract_v1/precision/run.py --out data/processed/forecast_methods/l3_source_contract_v1/precision/results_verify_v1
```

23 tests passed in0.58s. Both runners exit0; all9 files byte-identical. Tests reject missing/duplicate coverage, incompatible units, backdated later and derived precision, falsely finer whole-million counts, incorrect derived bounds/arithmetic, changed inherited weights/units/lambda, checksum mutation, and existing destinations. Negative source findings and the IPO gap have explicit regressions. Reusing either output directory intentionally fails.

SHA256 anchors: `run.py`73b1e52d02b795f57d8bebe71d1ce3254cc306478d9f7421445a04d96309f5cc; compact input manifest af137faedf8df00513234e500b265b6809b1a595d6c4a87329f245614f4e5a80; output manifest abdf39efbffb97a93e8896de4247859aebc4dd92d3c8cab68a539dc3d102829a. Package `.gitattributes` preserves bytes through Git. Independent reviewer closure remains a separate new note.

## RESUME

Use `precision/results_v1` as descriptive provenance, subject to the assigned independent SC-C review. The lead should integrate the compact facts, scope/coverage and sensitivity with SC-B accounting and SC-C consumption; reconcile definitions, preserve original L3 and prohibit direct forecast adoption. Do not convert later precision into earlier data, “repair” the source panel, refit a model, or interpret 2/3–1/3 as physical booking shares. Unavailable IPO originals, six precision gaps and unresolved source inconsistencies remain explicit future evidence needs.
