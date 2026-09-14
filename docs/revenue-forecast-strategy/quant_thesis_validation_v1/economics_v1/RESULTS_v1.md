# Q7 — earnings, cash and horizon materiality

2026-09-14 · worker E `/root/test_designer` · `codex/quant-thesis-validation-v1`. Exclusive new code/data/docs `quant_thesis_validation_v1/economics_v1`. Immutable L4 source commit `29b2d9ae2d66da5f1f5086ba7dc36e4c2d96ab70`, exact-byte extraction `evidence_v3/l4`.

## Verdict

The inherited financial equations reconcile, but the observed same-basis Q4 revenue difference supplies a small isolated cash/value effect. Own Q4 review revenue exceeds the captured LSEG-family revenue estimate by **$18.322164m**. Under fixed-dollar compensation, a one-quarter difference is worth approximately **-$0.001 to +$0.031 per share** at the twelve-month endpoint across the three disclosed cash-cost responses. A larger **$0.008 to $2.771 per share** difference requires sustaining the same fractional revenue contrast through all of FY27; that persistence is a scenario, not observed consensus disagreement or validated forecast performance.

The inherited **$184.662755** EBITDA lens belongs to **31 December 2027**, beyond the three-to-twelve-month decision horizon. Keeping its FY27 EBITDA and16.5x multiple but aligning the conditional cash/share balances to13 September2027 gives **$182.867016**. Its **$1.795739** timing difference and roughly **$10.032807 per multiple turn** are larger than the isolated operating contrast. This arithmetic supports no automatic long, short, price target, probability or current-market return.

Research arithmetic checks pass; economic investability remains conditional. Reviewer A independently reviews this package; the author's tests are not a substitute for that review.

## What ran and reproduced

Read the parent `CHAIN_PROTOCOL_v1.md`; saved `ASSUMPTIONS_v1.md` before new sensitivities. No full L4 operating model or workbook was duplicated. The runner independently reconstructs downstream identities from committed annual components, quarterly sums and explicit financial parameters. Outputs are transparent analytical CSV tables.

From the quant-validation worktree root:

```powershell
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B analysis/src/forecast_methods/quant_thesis_validation_v1/economics_v1/run.py --out data/processed/forecast_methods/quant_thesis_validation_v1/economics_v1/results_v1
& 'C:/Users/wille/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -B -m unittest discover -s analysis/src/forecast_methods/quant_thesis_validation_v1/economics_v1 -p 'test_*.py' -v
```

Runner exit0, shell wall time1.401s. Seven tests pass, exit0, shell wall time1.338s (test framework0.041s). The output directory now exists and must not be overwritten; use a new suffix to reproduce. Source hashes, exact output hashes and comparator identity are in `results_v1/receipt.json` and `source_hashes.json`.

| Independent reconciliation | Source sample | Checks | Maximum difference |
|---|---:|---:|---:|
| Annual income, cash/share roll, source quarter sums and FY27 valuation | 7 scenarios x3 years =21 scenario-years |567|1.819e-12 in the corresponding units|

These are dependent deterministic model checks, not567 observations or21 independent economic regimes. There are zero newly estimated parameters and zero empirical validation observations for the economic scenarios.

## What the annual model actually says

All dollar figures USD millions; shares millions; one deterministic `review_with_k` case per year (n=1 each). Earnings per share uses ending modeled shares and is a proxy, not weighted-average GAAP EPS.

| Field | FY26 | FY27 |
|---|---:|---:|
| Revenue |14,273.706584|15,952.233241|
| Cash-cost component sum |9,192.351307|10,288.270818|
| Total EBITDA addbacks |128.463359|143.570099|
| Adjusted EBITDA |5,209.818636|5,807.532522|
| SBC |1,786.530000|1,965.183000|
| D&A, already within total addbacks |99.915946|111.665633|
| Operating income proxy |3,294.825277|3,698.779422|
| Net income proxy |3,106.208474|3,355.023538|
| FCF before an economic SBC deduction |5,178.870373|5,536.825326|
| SBC-adjusted FCF |3,392.340373|3,571.642326|
| Annual buybacks |4,200.000000|4,000.000000|
| Annual withholding |625.285500|687.814050|
| Ending corporate net cash |9,433.584873|10,282.596149|
| Ending share proxy |588.850030|574.598178|

The tested accounting identities are:

`Adjusted EBITDA = min(revenue - cash_costs + total_addbacks, 38%*revenue)`.

`Operating income = adjusted EBITDA - SBC - total_addbacks`; D&A is not deducted again. `Net income = (operating income + interest income - interest expense)*(1-effective_tax_rate)`.

`FCF = adjusted EBITDA + interest income - interest expense - cash taxes + change in unearned fees + other working-capital cash - capex`. Cash taxes are an inherited percentage of revenue, distinct from the income-statement effective rate. The zero unearned-fee cash term is an inherited assumption and does not measure RNPL migration.

`Net cash_end = net cash_open + remaining FCF - remaining buybacks - remaining withholding`. FY26 remaining flows subtract actual H1 amounts because the opening balances are June2026. In FY27, FCF less$4,000m repurchases and$687.814050m withholding adds **$849.011276m** corporate net cash. Subtracting full SBC from that cash roll as well would double-count a noncash compensation expense as a cash payment.

`Shares_end = shares_open - remaining_buybacks/transaction_price + 65%*remaining_SBC/transaction_price`. Annual SBC-adjusted FCF less buybacks is **-$428.357674m** in FY27; it is an economic-compensation proxy comparison, not the corporate cash roll. The model can increase net cash while its SBC-adjusted FCF is below repurchases because only modeled withholding is a direct SBC-related cash outflow and the rest issues shares.

Two source-definition limitations matter. Reviewer C separately verified June2026 cash$6,821m plus short-term investments$5,248m less debt carrying value$2,476m = **$9,593m**. Customer-fund assets and matching liabilities of$12,224m each are excluded. Debt principal is$2,500m; a principal-basis net-cash convention would instead be$9,569m, $24m lower. This is a disclosed debt-basis difference, not newly estimated cash. The same source confirms597m is Q2 **weighted-average diluted shares**, not an observed ending diluted count. The annual model rolls that inherited proxy forward. [Airbnb Q2 2026 Form10-Q, balance sheet and Note7](https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm).

The model's FY26 H2 withholding is$625.2855m minus actual H1$305m = **$320.2855m**. In contrast,35% of modeled H2 SBC is **$311.3355m**. The **$8.95m** difference arises because actual H1 withholding was not35% of H1 SBC. This mixed convention reproduces; it is not silently repaired. Refining actual settlement/grant/share timing is necessary before treating the share roll as a measured dilution forecast.

## Same-basis operating contrast

The comparator is captured Yahoo Finance/LSEG-family **revenue** consensus$3,161.021490m, observed **2026-09-13 15:20UTC**. Own conditional Q4 revenue is$3,179.343654m. Their difference is+$18.322164m, +0.579628% of that captured consensus. The corresponding fraction of own revenue is used for the sustained counterfactual, so its Q4 level matches the captured consensus exactly. No new FY27 Street estimate is manufactured. Parent's `expectations_v1/same_basis.csv` retains vendor, timestamp and source URL.

Own guide$3,123.419115m minus that revenue consensus is a different-object subtraction, not observed management-guide surprise. A cushion change by itself changes the guide transformation and no revenue, earnings or cash in this bridge.

Let eta be the cash operating-cost response per revenue dollar, excluding the explicitly inherited AI percentage:0 means fixed costs,0.5 means half the increment is consumed,1 means full core cash-cost offset. These are unit stresses, not fitted margins or probability bounds. Addbacks, AI, cash taxes, capex and other working capital retain the inherited percentage assumptions. SBC is fixed in this central table. Each row n=1 scenario, empirical validation n=0.

| Persistence / eta | Revenue difference | Net income difference | FCF difference | Twelve-month per-share contrast |
|---|---:|---:|---:|---:|
| Q4 only /0 |18.322164|14.840953|17.754177|+$0.030671|
| Q4 only /0.5 |18.322164|7.420477|8.593095|+$0.014845|
| Q4 only /1 |18.322164|0.000000|-0.567987|-$0.000981|
| Same fraction through FY27 /0, **FY27 incremental flows** |91.930747|73.265128|87.996111|+$2.771366|
| Same fraction through FY27 /0.5, **FY27 incremental flows** |91.930747|36.492829|42.030738|+$1.389622|
| Same fraction through FY27 /1, **FY27 incremental flows** |91.930747|-0.279469|-3.934636|+$0.007878|

Sustained per-share contrasts include Q4 retained cash plus the elapsed FY27 cash effect and the full FY27 EBITDA difference valued at the inherited16.5x. A single-quarter contrast has **zero recurring FY27 EBITDA effect** and hence no added enterprise value from capitalizing that one-off outcome. This distinction explains most of the value difference between the two constructions.

Under eta0, FY26 adjusted EBITDA increases by100.9% of the revenue difference because total addbacks mechanically scale at0.9% of revenue. That is a feature of the inherited adjustment convention, not a measured incremental economic margin. Under eta1, profit is zero before the inherited cash-tax/capex/working-capital formulas, yet FCF can fall. The small positive sustained EBITDA-lens value at eta1 likewise reflects addback conventions; it does not establish positive economic cash creation.

The proportional-SBC alternative subtracts additional compensation from earnings,35% withholding from cash and adds65%/price to shares. At12 months, the single-quarter contrasts become **-$0.004956 to+$0.026697**, and the sustained contrasts **-$0.009438 to+$2.754218** across the same eta grid. Full component rows are in `annual_operating_contrast.csv` and `horizon_operating_contrast.csv`; no SBC-adjusted-FCF multiple is combined with a second deduction for the same compensation.

## Valuation horizon and competing assumptions

The reference decision date is the frozen September13 snapshot, not this September14 execution date. For each endpoint, cash/share flows accrue uniformly by calendar days from the committed June2026 balance and H2/FY27 flows. The underlying FY27 EBITDA and16.5x multiple remain fixed solely to isolate the balance-timing convention. This is not a seasonally modeled cash forecast or a distinct underwritten target at each date. Each row n=1 conditional calculation.

| Endpoint | Horizon | Corporate net cash, $m | Share proxy, m | Fixed-FY27-metric value | Effect of prematurely using Dec27 balances |
|---|---|---:|---:|---:|---:|
|2026-12-13|3 months|9,449.179831|589.647310|$178.536330|+$6.126426|
|2027-03-13|6 months|9,601.061070|586.038706|$179.894854|+$4.767901|
|2027-09-13|12 months|10,029.055795|578.854211|$182.867016|+$1.795739|
|2027-12-31|Outside requested horizon|10,282.596149|574.598178|$184.662755|—|

At the12-month endpoint, a one-turn change in the inherited EBITDA multiple changes value by **$10.032807/share**; $1bn corporate-net-cash change changes it by **$1.727551/share**. The inherited13.5x/16.5x/18.5x choices produce **$152.768596/$182.867016/$202.932630**, holding other inputs fixed. These are multiple sensitivities, not probability-weighted bear/base/bull targets. The prescribed cash/share grid is in `multiple_cash_share_sensitivity.csv`.

The multiple that equates the conditional endpoint value to the inherited **$181.94 reference dated4 September2026** is16.845580x at3 months,16.706376x at6 months and16.407601x at12 months. This is a dated-reference break-even calculation; the current stock price was not fetched and no current expected return is claimed. No growth-to-multiple regression or average of six valuation lenses is used.

Changing the FY27 transaction-price assumption by-/+20%, with fixed repurchase spending and the original SBC convention, produces12-month share proxies576.355256m/580.520181m and fixed-metric values$183.659889/$182.342227. Cash stays unchanged because spending is fixed. Transaction price affects both repurchased shares and the model's SBC issuance proxy; neither is a verified future execution price. A separate1% share-count stress is more appropriate than giving the ending-share proxy false precision.

## Opposing interpretation, falsifiers and limits

The strongest favorable interpretation is that the retained bookings conversion supplies an auditable revenue reference, the captured LSEG-family revenue disagreement is modestly positive, and the inherited model supports substantial cash generation even after investment. On its stated FY27 assumptions, net corporate cash increases while net modeled shares decline. A sustained revenue advantage could have value, particularly when incremental cash costs are low. The negative guide-minus-revenue-consensus arithmetic cannot support a bearish surprise claim.

The strongest objection is that the positive same-basis gap is small and vendor-sensitive, and a Q4-only difference barely affects value. Sustained growth, cash-cost response, future SBC settlement, actual shares, valuation multiple and endpoint conventions are not established by an accurate conversion identity. Model arithmetic does not show expectations will revise, investors will rerate the company, or an executable return exists. A one-turn multiple move overwhelms all operating contrasts in this bounded grid.

Observable falsifiers/updates are: Q3 GBV and the first Q4 guide, with explicit pre-guide expectations where available; subsequent evidence that any revenue difference persists; disclosed cash costs and cash taxes rather than the imposed marginal responses; actual buyback execution, net issuance and share count; and quarterly corporate cash/working-capital reporting. A guide-cushion shift with unchanged revenue cannot be offered as an earnings thesis. Customer-fund flows cannot close missing corporate cash. These observations could change the model's economic inference, but no monitoring or adoption action is scheduled here.

The files preserve all assumed eta/SBC combinations, including negative/no-value outcomes. No outcome-dependent parameter choice was made, no new probabilistic calibration was attempted, and no failed run or test occurred in this package's first execution. Primary limitations are unvalidated persistence and marginal costs, uniform cash timing, a weighted-average starting-share proxy, inherited debt/withholding conventions, and no current price or new forward Street consensus. Reviewer C's separate filing review supplies the cash/debt/share source interpretation; it does not validate this author's full economic calculations.

## RESUME

Reviewer A should rebuild into a new output directory and independently check cash/share endpoints, one-quarter versus sustained enterprise-value treatment, SBC/withholding separation, comparator sign and published values. Parent should bind the review and output hashes, keep these scenarios separate from prospective forecast evidence, and hand L4 only the conditional per-share sensitivities and horizon-corrected wording. No source, model, workbook, forecast registration, scorer, card or investment direction was changed.
