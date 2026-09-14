# L4 independent financial-model and memo review

Codex revenue/reconciliation subagent reviewing the other agents' model and memo · 13 September 2026 · `codex/lane4-full`. Read-only review; no model, workbook, memo or card file was edited. Parent separately owns final OOXML audit, scorer invariance and PDF visual QA. This review used the spreadsheet skill's read-only workflow and bundled Python for extraction and independent arithmetic.

## Verdict

**No quantitative or economic-consistency blocker found in the reviewed snapshots.** The workbook correctly connects the fixed-K0 benchmark revenue to inherited costs, cash and valuation, while the memo labels conversion validation and cohort FX/RNPL integration as separate pending inputs. The displayed $184.66/share is a conditional FY27-end valuation, not an adopted target. Two nonblocking terminology improvements were sent to the owners: replace “like-for-like prior-year comparison” in the ADR card with a comparison of prior-year blended ADR, and label generic ±1% consolidated-revenue scenarios “net revenue sensitivity” rather than “incremental timing.” The nearby explanations already state the correct economic meaning.

This verdict is implementation review, not an independent validation of the conversion model, ADR residual, inherited cash-flow assumptions or investment thesis. I authored the revenue package and therefore do **not** present this as an independent audit of my own revenue research. The independent scope here is the financial model, saved workbook formulas, and memo/card interpretation of those inputs.

## Reviewed artifacts and frozen identities

The model is `model/lane4_v1/outputs/lane4_model/snapshot_v2/ABNB_L4_review.xlsx`, using its matching `data/processed/forecast_methods/lane4_model_v1/snapshot_v2/` inputs/results. The memo/card/decision package reviewed is `deck/drafts/lane4_v1/review_v2/`. Relevant SHA-256 values at review:

| Artifact | SHA-256 |
|---|---|
| Workbook snapshot_v2 | `9f382f89e44cfc5d53f856ce4c0aafd580d1c1cc2596a3f05a1a7a65d1e6ccba` |
| Model input JSON | `efb0124251dadbd5df5c5e66bb5de99a6e75a5730d135c4c12e34893a0b83c15` |
| Model scenario summary CSV | `b3431a7683e57762ce17c01628efee39c6dfffbc8e12cc11c08c3df983e882e2` |
| Memo Markdown review_v2 | `eab3cfdb3dafa09a7035e8336d9ae844f2718e4263c0df4992635415bf8738e7` |
| Memo PDF review_v2 | `d40a28d041efdf37fe3707f6cb0ad33cfae24d9616fd2eac7ba7c1c2a2e9b859` |
| Unsigned card Markdown | `b7721ba54460a25314c8ae25f33f4b8550f6f8806ce7e2db0f20d98d52eca224` |
| Decision register CSV | `4a8b4bcd8cb5cda7734e44471c7f937da5cdafbad74e390f1fbfd082a0f1e97c` |

Any later output version requires a scoped follow-up check; this note does not certify changing files.

## What I checked

Read `lane4_model_v1/run.py`, the builder's active-assumption, revenue, cost, cash, valuation and capture formulas, its tests, the exact saved workbook XML/cached values, model input JSON, annual/scenario/valuation CSVs, and the final memo/card/decisions. Extraction used the bundled interpreter at `C:\Users\wille\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`, with standard-library `zipfile`, XML parsing, JSON and arithmetic. No new fit, workbook export or recalculation mutation was performed by this reviewer.

Independent arithmetic started from the June cash/share anchor and the recorded annual flow inputs rather than calling the model's calculation functions. It reproduced the annual cash and share roll through FY2028, then independently recalculated the FY2027 EV/EBITDA equity value. I also traced saved workbook formulas at `Revenue!H15:H20`, `Cash!F24:F28`, `Cash!G28`, `Cash!G36:G37`, and `Valuation!E14/E23/E38/E45`; checked actual saved provisional/missing-input labels; and compared the memo's operating/guide and valuation table values with their source rows.

The owner's separate recalculation receipt has 84 scenario/metric comparisons across seven cases, maximum absolute difference 3.64×10⁻¹⁰ in the underlying output units, and passing input-perturbation checks. That is reviewed owner evidence, not 84 new independent simulations performed by me. My separate saved-file arithmetic agrees within $0.001M/$0.001 per share.

## Financial and accounting findings

| Review area | n / scope | Finding |
|---|---|---|
| Covered revenue replacement | 3 quarters | Q3/Q4 2026 and Q1 2027 use the imported benchmark seasonal coefficients and two lagged GBV values. No old take-rate wedge, full FX factor or additional new-business revenue is added. |
| Operating timing | 2 forecast GBV cohorts | Q3 nights/ADR affect Q4 revenue; Q4 GBV first affects Q1 2027. Q3 implied guide is labelled an issued-guide diagnostic. |
| K0 cost-volume assumption | 2 quarters | K0's unsupported nights/ADR decomposition is not invented as revenue evidence. Reference-case nights are explicitly disclosed as a support-cost proxy; K0's independent GBV drives its revenue and processing costs. |
| Costs and D&A | 3 annual periods | New-initiative costs remain a separately labelled inherited dollar assumption. D&A is disclosed within total addbacks and is not deducted twice when converting adjusted EBITDA to operating income. |
| Cash/share roll | 3 annual periods | The June 30 2026 anchor uses $9,593M net cash and a 597M diluted-share proxy. Only H2 flows affect FY2026; H1 FCF, buybacks, RSU withholding and SBC issuance inputs are subtracted once. Customer funds are excluded. |
| Valuation convention | 1 horizon / 6 lenses | The new convention is December 31 2027, paired with FY27-end cash/shares. FY28 EBITDA value is discounted one year. EPS uses ending shares and is explicitly labelled a proxy. The six-lens mean is arithmetic, not six independent observations. |
| Legacy reproduction | 2 headline objects | Original annual-CSV equations produce $180.876286 for the EBITDA lens and $156.786845 for the six-lens mean. Saved workbook values differ by less than $0.00001/share from source precision, well inside $0.001. |
| Pending FX and sensitivity | 2 distinct roles | Real FX/RNPL adjustment stays “Unestimated.” The ±1% cases are explicitly generic net after-hedge consolidated-revenue perturbations, not a pre-hedge translation multiplier or accepted L3 coefficient. |

The independent FY27 cash roll gives **$10,282.596149M**, with **574.598178M shares**. Using **$5,807.532522M adjusted EBITDA ×16.5 + net cash**, divided by shares, gives **$184.662755/share**. Saved `Valuation!E14` agrees. The new six-lens arithmetic mean is $160.478870; it is distinct from the single-lens $184.66 and the legacy $156.79 mean.

The cash-flow equation retains the legacy convention: adjusted EBITDA plus net interest, less cash taxes/capex, plus unearned-fee change and other working-capital residual. The workbook explicitly says that zero unearned-fee change is an inherited cash assumption, not an RNPL estimate. The DCF's cash-flow definition and discounting convention are inherited; its label says it is not a newly underwritten unlevered enterprise DCF. I therefore do not interpret its result as independently validating enterprise value. The December 2027 horizon is explicit and remains an adoption choice; it is not silently converted into a nearer-term trade target.

## Memo and card consistency

The six-row Q4 guide exhibit agrees with the benchmark snapshot: review $3,123.4M, without-K $3,120.1M, residual reversion $3,074.8M, K0 conditional $3,158.2M, mean-cushion $3,121.4M and legacy-cushion $3,060.6M. Its $37.6M/1.19% review gap is correctly against Yahoo/LSEG-family **revenue consensus**, with the explicit qualification that this is not management-guide consensus. LSEG is timestamped September 13 15:20 UTC; S&P September 10 and Zacks September 11 remain older anchors. Yahoo and Alpha Vantage are not counted as separate panels.

The four-row valuation exhibit matches model snapshot_v2. Its ±1% note states exactly which covered quarters change and that FY27 Q3/Q4 inherit the altered 2026 bases while Q2 stays unchanged. The displayed FCF, cash taxes, capex and SBC-adjusted FCF agree with the financial inputs. The memo preserves A2 PARTIAL, B2 FAIL, nested windows, ADRv3's distinct windows/post-hoc selection and failed integer-fair result, unobserved residual, unidentified RNPL migration, and the absence of an adopted direction, target or probabilities.

The unsigned card has 11 diagnostic items and the decision register has 23 alternative rows. Original D-01's already-guided Q3 revenue choice is preserved as L4-D09. The conversion methodology choice is separate from cohort FX/RNPL. Fixed lambda thresholds use the exact inherited denominator and conservative rounding intervals; missing evidence is absent, not support for the opposite thesis. Card scoring does not authorize a trade. These checks review definitions and numerical coherence; they do not newly validate the diagnostic thresholds or research claims.

## Nonblocking follow-ups sent to owners

1. **ADR language:** `unsigned_november_card.md`, C05 definition says “blended ADR and its like-for-like prior-year comparison.” A blended ADR comparison includes composition. Prefer “reported blended ADR and its year-over-year comparison with prior-year blended ADR.” The numerical ADR target and its band do not change. Sent to the review owner.
2. **Sensitivity labels:** the model's scenario names/short labels retain “Incremental timing −1%/+1%,” while its nearby notes correctly define generic net after-hedge consolidated-revenue perturbations. Prefer “Net revenue −1%/+1%” in a future label revision. The current memo uses the clearer “revenue sensitivity” label and explicitly rejects interpretation as an L3 timing estimate. Sent to the model owner.

No numerical repair, new research, source rewrite or changed investment recommendation is requested by this review.

## RESUME

Parent should combine this economic/claim review with the separately owned PDF visual inspection, saved-workbook structural audit and scorer invariance receipts. Preserve the reviewed hashes and any subsequent output versions. The two wording suggestions are small and do not change the calculations; if owners publish replacements, check those exact lines and that affected numerical values remain unchanged. Before promoting conversion or FX/RNPL claims, obtain the user's explicit L3 handoff, verify commit contents/checksums and apply only inputs whose baseline and accounting treatment reconcile. Passing this integration review does not resolve those research dependencies or sign the card.

## Final follow-up — definitive model snapshot_v4 and review_v4

The model and review owners issued their definitive final artifacts after the initial review. I performed only the affected comparisons, without rerunning unrelated tests or editing their files. **Both terminology suggestions are resolved; no numerical changes were found.**

- `snapshot_v4/annual.csv` and `valuation.csv` are byte-identical to snapshot_v2.
- All **91 numeric fields** in the seven-row scenario summary are exactly unchanged as serialized CSV values; scenario identifiers are unchanged. The two short labels now read **“Illustrative revenue −1%”** and **“Illustrative revenue +1%.”** Those labels are also present in the saved snapshot_v4 workbook XML.
- The final review_v4 memo Markdown and decision-register CSV are byte-identical to review_v2. No scenario, consensus gap, valuation or diagnostic threshold changed.
- Card C05 now says **“Company reported blended ADR and its year-over-year comparison with prior-year reported blended ADR.”** The old like-for-like phrase is absent. This is the sole change in the unsigned-card Markdown relative to review_v2.
- Parent separately reports that both the final snapshot_v4 workbook and its saved recapture pass **91 cached checks**, with **1,576 formulas, zero errors and zero external links**. This is parent verification, not a new execution claimed by this reviewer. The review owner confirms final review_v4 page renders are byte-identical to the parent-approved review_v3 renders.

Definitive locations are `model/lane4_v1/outputs/lane4_model/snapshot_v4/ABNB_L4_review.xlsx`, matching model data `snapshot_v4/`, and `deck/drafts/lane4_v1/review_v4/`. The revenue input remains `lane4_revenue_v1/snapshot_v1/`.

| Final artifact | SHA-256 |
|---|---|
| Workbook snapshot_v4 | `7301722b233041baca2738c76a6aeaa239dda712f43fc42e5d28efcadacf7e4a` |
| Model input JSON snapshot_v4 | `7d9b725b8e4a9f81b4eacb5d70f02857c2b9ca01ee76477dff7b09bb96333bb2` |
| Scenario summary CSV snapshot_v4 | `9f46b8f88351b48753373149548cdaac7180c7a05fa29e839caa87fcfdca4d0a` |
| Memo Markdown review_v4 | `eab3cfdb3dafa09a7035e8336d9ae844f2718e4263c0df4992635415bf8738e7` |
| Memo PDF review_v4 | `8bfe0b07dc66b92de8be424e37a557363cf33eb989a6938c6303376d89c8e641` |
| Unsigned card Markdown review_v4 | `665e49fb6e221d2e7e14cea123b0414a6589eb299ac99d42310c2715019abd71` |
| Decision register CSV review_v4 | `4a8b4bcd8cb5cda7734e44471c7f937da5cdafbad74e390f1fbfd082a0f1e97c` |

### Final RESUME

The two independent-review wording findings are closed on the definitive versions above. No quantitative blocker remains from this review. Parent may complete its integration/publication workflow using these exact files and its own final checks. Conversion validation, cohort FX/RNPL integration and team adoption remain open research/decision dependencies; none is resolved merely by these unchanged numerical results or corrected labels.
