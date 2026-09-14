# FXSWAP — the H1/H2 bridge's FX lines swapped to the programme's adopted estimators

Package: `analysis/src/h1_to_h2_bridge_v2.py` (a COPY of `h1_to_h2_bridge.py`, modified; v1 untouched)
Data: `data/processed/h2_bridge_v2/` (v1 `data/processed/h2_bridge/` untouched)
Registry: nothing new. The FX objects consumed here are already registered (`fx-lag-v2__fx_pts_revenue_2026q4_v2`); `harness/score.py` NOT run, nothing to score.
Run date 2026-09-12. FX inputs all on FRED data through **2026-09-04** (FRED raw, ADR v3 N1 card, fx_lag_v2 agree; the script warns if they ever diverge).
Author: Krish (with Claude). Branch `krish/fx-line-swap`.

## Verdict first

**Done, and the swap is worth about 1.0pp on the 4Q26 revenue-FX line and about $31M on the bridge's 4Q26 revenue dollars.** The bridge's two FX lines were the last place in Krish's Q3/Q4 arithmetic still carrying the constructions the FX programme rejected: a single-factor broad-USD fit for ADR FX (+1.1 / +2.1pp for 3Q26 / 4Q26) and an assumed 2.0pp (range 1 to 3) for 4Q26 revenue FX. They are now the ADR v3 midpoint estimator (−0.4 / +0.2pp) and the fx_lag_v2 kernel output (+1.0pp, CS +0.3 to +2.2). 3Q26 revenue FX stays at management's stated ~3 after hedging, which the kernel reproduces (+2.9). Every replaced number and every rejected construction is kept as a labelled comparison column, the way consensus is carried.

**One inconsistency surfaced and is left visible rather than smoothed over** (§4): the bridge's revenue-dollar path pushes the ADR v3 midpoint through the ⅔/⅓ GBV lag, which implies about **+0.15pp** of 4Q26 FX, while the adopted kernel line on the currency basket says **+1.0pp**. The 0.8pp gap is the 3Q26 ADR-FX estimator disagreement (basket-contemporaneous fit +0.4 vs midpoint −0.4) carried two-thirds forward, worth about $24M of 4Q26 revenue. The 3Q26 ADR-FX print on 5 Nov settles it.

## Exact commands

```bash
cd "<repo root>"
python analysis/src/h1_to_h2_bridge_v2.py data/raw/fred     # exit 0, ~5 s, 12 CSVs to data/processed/h2_bridge_v2/
```

## 1. What was swapped (pre-registered as the task, not a test)

| line | quarter | v1 (10 Sep) | v1 source | **v2 adopted** | v2 source |
|---|---|---|---|---|---|
| ADR FX, pp | 3Q26 | +1.12 | broad-USD fit `0.5 − 0.72 × USD y/y` | **−0.43** | ADR v3 midpoint of EUR fit (−1.12) and regional baskets (+0.26); RMSE 0.33pp on 1Q24–2Q26 (n 10) vs 0.46 EUR / 0.42 baskets |
| ADR FX, pp | 4Q26 | +2.10 | same | **+0.15** | same (EUR −0.66, baskets +0.97) |
| Revenue FX, pp | 3Q26 | 3.0 | management ~3 after hedging | **3.0** (unchanged) | management; kernel Φ × 0.851 gives +2.9 on the same basis |
| Revenue FX, pp | 4Q26 | 2.0 | assumed, range 1–3 | **+0.98** | fx_lag_v2 kernel: Φ (0, ⅔, ⅓) × 0.851 on the revenue-weighted basket, spot held from 4 Sep; CS +0.3 to +2.2; 80% band −0.6 to +2.1 |

The 1H26 reconciliation of the ADR-FX estimators against the disclosed points, carried in `h2_bridge_fx.csv`: 1Q26 disclosed +5.0, midpoint +4.75, broad-USD fit +5.34; 2Q26 disclosed +1.3, midpoint +1.14, broad-USD fit +2.33. The broad-USD fit overshoots the most recent quarter by a point; the midpoint misses by 0.16.

## 2. Comparison columns carried in `h2_bridge_v2_fx_line.csv` (4Q26 revenue FX, pp)

| construction | 4Q26 | status per B4 §5 |
|---|---|---|
| **kernel Φ × 0.851 on the basket (adopted)** | **+0.98** | adopted as an output |
| kernel Φ × 0.653 (scale fitted to the Φ shape) | +0.75 | shown beside the adopted, never hidden |
| Φ lag on the ADR v3 midpoint ADR-FX points (what the dollar path implicitly carries) | +0.15 | new here; see §4 |
| free fit (Object A, stated series) | +0.89 | the registered fx-lag spec; in-sample winner, worse PIT |
| v1 bridge assumption | 2.0 | replaced |
| guide-anchored (hold +3.0 flat) | +2.6 | REJECTED (imports a tailwind the spot path removed) |
| EUR-only `05_fx_schedule` fit | −0.43 | REJECTED (EURUSD is not the basket; re-applies a lag already in the GBV base) |

Spread across the live constructions excluding the rejected ones: +0.15 to +0.98, about $23M of 4Q26 revenue at $27.8M per pp.

## 3. What moved (`h2_bridge_v2_vs_v1_delta.csv`)

| object | v1 | v2 | delta |
|---|---|---|---|
| ADR y/y reported, 3Q26 adjusted | 4.14% | 2.58% | −1.55 |
| ADR y/y reported, 4Q26 adjusted | 5.44% | 3.50% | −1.95 |
| GBV y/y reported, 3Q26 adjusted | 12.98% | 11.29% | −1.69 |
| GBV y/y reported, 4Q26 adjusted | 14.00% | 11.90% | −2.10 |
| Revenue FX, 4Q26 | 2.00 | 0.98 | −1.02 |
| Revenue y/y reported (pattern path), 4Q26 | 12.83% | 11.81% | −1.02 |
| 3Q26 GBV assumed for the Q4 lag, $bn | 25.87 | 25.49 | −0.39 |
| 4Q26 lagged GBV base, $bn | 26.32 | 26.06 | −0.26 |
| **4Q26 revenue dollars (GBV-lag path), $M** | **3,165.6** | **3,134.7** | **−31.0** |
| 4Q26 implied guide midpoint if the Q4 cushion holds, $M | 3,047 | 3,018 | −30 |
| 3Q26 revenue dollars, $M | 4,804.0 | 4,804.0 | 0 (base is printed GBV) |

n for the transitions and base rates is unchanged from v1 (three clean years, 2023–2025); nothing in the pattern layer was touched.

## 4. The inconsistency, stated

The bridge has two routes to revenue. The **pattern route** adds `fx_pts_revenue` to an ex-FX growth rate; that line is now the kernel's +1.0. The **dollar route** is `conversion × (⅔ GBV_3Q26 + ⅓ GBV_2Q26)`, where GBV_3Q26 is built from the bridge's nights and reported ADR, and reported ADR now carries the midpoint ADR FX of −0.43. Push that through the same Φ lag and the dollar route is carrying `⅔ × (−0.43) + ⅓ × 1.3 = +0.15pp` of 4Q26 FX, not +1.0.

Why they differ: B4's kernel line is Φ on the **currency basket** (3Q26 basket +0.6%, 2Q26 +2.3%, scaled 0.851), while the dollar route is Φ on **ADR-FX points** (3Q26 midpoint −0.43, 2Q26 disclosed +1.3). B4's own reading A (disclosed ADR-FX through Φ, with the 3Q26 point fitted from the contemporaneous basket at +0.4) gives +0.7; substituting the midpoint's −0.43 for that +0.4 is what takes it to +0.15. So the whole gap is the 3Q26 ADR-FX estimator: basket-contemporaneous +0.4 vs EUR/baskets midpoint −0.43, a 0.8pp disagreement on a quarter that is 71% printed.

Which one to believe is exactly the ADR v3 N memo's open question, and the pitch should carry the range rather than pick silently: **4Q26 revenue FX +0.15 to +1.0pp**, adopted +1.0 because it is the registered, verified object, with the caveat that the dollar path sits at the low end. This is a smaller version of B4's "which end you believe is the whole of the lag argument."

## 5. What failed or was not done

1. **No new registration, so no scorer run.** The swap consumes registered objects; it does not create one. If the bridge's 4Q26 revenue dollars are ever to be scored they need a `revenue_next_q` registration of their own, which is WP-K0's job, not this note's.
2. **The nights and ex-FX ADR lines in the bridge are stale and were not touched** (out of scope, stated in the script docstring). Bridge nights 3Q26 8.49% (RNPL lap −1.5, World Cup +0.5) against the 10 Sep team baseline 9.9%; bridge ex-FX ADR 3Q26 +3.0% against the ADR v3 card's +3.9%. That is why the bridge's 3Q26 GBV ($25.5bn) sits below the frozen card ($26.2bn) and the Q3 nowcast ($25.9bn). The −$31M FX effect on 4Q26 dollars is the swap's contribution alone and is additive to whatever re-basing those lines would do.
3. **The FRED raw files end 2026-09-04.** Nothing here is as of 12 Sep.
4. **The 0.95-vs-0.56 basket-scale caveat from B4 carries into the adopted +1.0.** The judgement currency weights understate exposure; WP-X (regional origin–destination exposure) is the fix and has not run.
5. **The pattern-route revenue y/y (11.8% for 4Q26) is not a forecast**; the v1 note already says the H1→H2 transition for revenue growth is useless. It is reported because the swap changes it, not because anyone should quote it.

## 6. Parameter count

Zero new free parameters. The script imports point estimates and intervals from two registered or verified packages (ADR v3 N1: 2 estimators averaged; fx_lag_v2: 2-parameter H2 spec) and applies arithmetic.

## 7. Files written (all new)

`analysis/src/h1_to_h2_bridge_v2.py` · `data/processed/h2_bridge_v2/` (the 10 v1-format CSVs rebuilt under v2 plus `h2_bridge_v2_fx_line.csv`, `h2_bridge_v2_vs_v1_delta.csv`, `README.md`) · this note · one WORKBOARD row.

## RESUME

The next agent should (a) re-base the bridge's nights and ex-FX ADR overlays to the team baseline and the ADR v3 card in a `_v3` copy, since those two stale lines now move 3Q26 GBV more than the FX line does; (b) when the September Inside Airbnb dumps land and `fx_lag_v2/fetch_fx_v2.py` is refreshed, re-run `h1_to_h2_bridge_v2.py` so the three FX data-through dates stay aligned (the script warns if not); (c) on 5 Nov, read the printed 3Q26 ADR-FX point against +0.4 (basket) and −0.43 (midpoint) and the printed revenue-FX integer against B4's decision rule (+3 kernel, 0/+1 short lag, +2 ambiguous), then collapse the +0.15 to +1.0 range in §4 to whichever survived. Do not add any FX pp on top of the GBV-lag dollar path; it already carries booking-date FX.
