# L4 v2 independent financial and decision review

14 September 2026; `/root/l4_reconciliation`, reviewing worker C without editing C's packages. Candidate model `lane4_model_v2/snapshot_v1`; candidate memo/card `deck/drafts/lane4_v2/review_v1`. Revenue dependency is frozen `lane4_revenue_v2/snapshot_v1`. Parent separately owns raw OOXML/cache and PDF visual checks. This review does not repeat L3 estimation or make an investment decision.

## Mathematical and economic result

**No numerical blocker found.** An independent calculation, without importing production model functions, reproduced 759 financial checks across all nine cases and 27 annual rows, with maximum absolute difference $2.91e−11 million. All 81 model input manifest hashes matched current immutable inputs. The receipt is `data/processed/forecast_methods/lane4_revenue_v2/independent_model_review_v1.json`.

The checks covered kernel-supported revenue/guide inputs, isolated net sensitivity factors, subsequent same-quarter inherited growth, annual revenue/nights/GBV sums, processing/support/fixed costs, EBITDA/addbacks/SBC, operating/net income, cash taxes/unearned fees/working capital/capex, FCF, repurchases/withholding/issuance, ending cash/shares, and September/December value. No second new-business revenue line is added to kernel consolidated revenue; inherited new-initiative costs remain separately labelled assumptions. Historical D&A is included in total addbacks and is not subtracted twice. Zero change in unearned fees remains an inherited cash assumption, not measured RNPL.

| Reference result | Independently reproduced |
|---|---:|
| FY27 revenue, $m | 15,952.233241 |
| FY27 adjusted EBITDA, $m | 5,807.532522 |
| FY27 net income proxy, $m | 3,355.023538 |
| FY27 FCF, $m | 5,536.825326 |
| FY27 end net cash, $m | 10,282.596149 |
| FY27 end diluted share proxy, m | 574.598178 |
| 13 September 2027 cash, $m | 10,029.055795 |
| 13 September 2027 diluted share proxy, m | 578.854211 |
| Conditional September value per share | $182.867016 |
| Later 31 December 2027 value per share | $184.662755 |
| Date-only balance/share difference | $1.795739 |

The exact date fraction is `(13 Sep 2027 − 31 Dec 2026)/(31 Dec 2027 − 31 Dec 2026) = 256/365`. Cash and shares use that fraction of FY27 net flows from FY26 end. Full FY27 EBITDA and the inherited 16.5x multiple remain visible conditional assumptions; no false discounting or unlabelled change of EBITDA horizon is introduced. Cash begins at 30 June 2026, and the first year rolls only H2 cash/share flows, preventing H1 duplication. Customer funds are excluded from net cash. The $181.94 price anchor is used for assumed issuance/repurchase mechanics; it is not presented as a current return denominator. Shares and EPS remain disclosed proxies.

The joint soft/firm cases use fixed 2/3, full operating replacements, seasonal lambda ±0.10pp and explicit cushions. Net factors are exactly 1. The generic ±1% net-after-hedge revenue cases are isolated; they are not combined with lambda stresses or labelled estimated FX. The all22 free-weight result and intact source draws appear only in a rejected-model descriptive exhibit. Future quarterly growth beyond Q1 2027 remains inherited and is labelled; no re-estimation or mechanical extrapolation of one unseasonal quarter creates FY27.

## Memo/card claims

The candidate memo correctly leads with own revenue $3,179.343654m versus captured Yahoo/LSEG revenue $3,161.021490m, +$18.322164m/+0.579628%. Own guide minus Street revenue −$37.602375m is labelled a different-object diagnostic. The transformed Street guide is explicitly hypothetical; direct guide expectations remain unavailable. No adopted direction, target, probability, +0.48 growth-to-multiple relation or executable guide-surprise claim is asserted.

Conversion acceptance and adoption are distinct: W1/W2 free-weight promotion failed, fixed operational seasonal policy is retained, fitted all22 coefficients do not replace it, and letter-close validation does not establish before-release guide skill. FX implementation acceptance does not imply measured exposure or financial application: matching pre-hedge reference, signed H/H_new and recognized RNPL exposure remain unresolved; Q4/Q1 target inputs are absent. The card preserves conservative rounding intervals, missing=ABSENT, exact management wording and the fixed Q3 denominator. Its ADR definition is reported blended ADR versus prior reported blended ADR, without relabelling it like-for-like.

## Findings sent to the owner

1. **Decision continuity, repair requested:** the v1 register's L4-D09 preserves original D-01, the Q3 revenue-method choice. Candidate v2 consolidates decisions but omits that open choice. Carry forward the kernel $4,808.362929m versus issued $4,730m guide times median/mean cushion: $4,814.690226m (+$6.327296m) and $4,817.823947m (+$9.461017m). These are already-guided-quarter alternatives, not an adopted new Q3 guide or additive overlays. No new model run/scenario is needed.
2. **Minor presentation clarity:** candidate decision D04 says “Nine-scenario model” next to the soft-to-firm range. Clarify that the displayed envelope covers the three main fixed-K0 cases within the nine-case model, excluding the isolated generic net sensitivities and rejected-model draws.

Both findings were sent promptly to worker C and parent. The first preserves an existing unresolved decision; neither changes the model arithmetic. They are resolved in the final artifacts below.

## Final follow-up and signoff

Final model is `model/lane4_v2/outputs/lane4_model/snapshot_v2/ABNB_L4_review.xlsx`, with corresponding data `lane4_model_v2/snapshot_v2`. Final memo/card/register are under `deck/drafts/lane4_v2/review_v2`. Narrow follow-up verified that `annual.csv`, `scenario_summary.csv`, `valuation.csv`, `horizon.json` and `legacy_replication.json` are byte-identical to the independently audited candidate. The 759-check numerical result therefore carries to the final data. No unrelated tests or fits were repeated.

Final D13 explicitly retains original team D-01 with kernel $4,808.362929m and issued-guide median/mean alternatives $4,814.690226m/$4,817.823947m as an **OPEN** choice, never stacked. Final D04 identifies the three main envelope cases within the nine-case model, excludes isolated net sensitivities, and states that cushion changes guide only. The memo also lists all three Q4 implied guides and explicitly separates guide-cushion changes from revenue, earnings and cash. Both review findings are closed.

Parent separately reports final raw OOXML verification of 316 checks and 1,875 formulas passed; this is attributed to parent, not counted among this worker's independent financial checks. PDF visual QA remains the parent/owner responsibility. There is no remaining numerical, accounting-basis or decision-continuity blocker from this review; all stated estimation, FX identification, inherited financial assumption and investment-adoption limitations remain.

Final hash receipt: `data/processed/forecast_methods/lane4_revenue_v2/independent_final_followup_v1.json`.

| Final artifact | SHA-256 |
|---|---|
| Workbook snapshot_v2 | `882b6d7b321d2f791fecc9b1d7ec57265b5e2fdcedd705326ee7bd3ee9ce6f92` |
| Model input JSON snapshot_v2 | `10b1e5713ff4020bdaf1f00743fd8a0e84c6ae388723442ed9578afcfc5afe8f` |
| Scenario summary snapshot_v2 | `c3a640fda7789e23708fdaae8875f7a3cd104d873a14a18ea716ad0d1290a51a` |
| Horizon JSON snapshot_v2 | `eb53770783fe75aec867b6128f17dbad690e2a29e997c4ee016a57c9ff3ae215` |
| Memo PDF review_v2 | `53e102eeca2dcda418368924cacb9a28486f3274332ba0b06fc804a6b1fe0187` |
| Memo Markdown review_v2 | `f7603c8eefe56a2396c56258a946e5e79803eed07729d60391e2cd882739d0ab` |
| Decision CSV review_v2 | `e353b7250c925c3aa46767a8efde368a17f949a333745c8603af518d85fbf69f` |
| Unsigned card CSV review_v2 | `c1026f83f047837cd0e564c4c265b9fd7bfedfa658ea94251369c7d1d37a758c` |

## RESUME

Use the signed-off model snapshot_v2 and review_v2 with this review and the parent OOXML/cache/visual audit. The numerical outputs are unchanged and both requested wording/decision repairs are verified. Parent owns final registration assessment and local commit; no new historical test, investment adoption, public publication or financial FX application follows from this signoff.
