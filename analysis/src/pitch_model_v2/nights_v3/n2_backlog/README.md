# N2 — backlog identity term (booked-not-yet-stayed nights)

Line N2 of the nights v3 pre-registration (`docs/pitch-model-v2/lines/nights_v3_prereg.md`, DEC-0033).
Judge's question: *how many nights sit booked but not yet stayed at each quarter end, how did Reserve
Now Pay Later change that, and how many growth points does the change in that backlog contribute to
reported nights?*

## Run

```
python3 analysis/src/pitch_model_v2/nights_v3/n2_backlog/run.py
```

Reproduction receipt (restores the tree afterwards, so run the line above once more to persist outputs):

```
PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id N2 \
  --watch data/processed/pitch_model_v2/nights_v3/N2 \
  --cmd "python3 analysis/src/pitch_model_v2/nights_v3/n2_backlog/run.py"
```

Python 3 standard library only (`csv`, `statistics`). No pandas, no network, no writes outside
`data/processed/pitch_model_v2/nights_v3/N2/`.

## Identity

```
N(t) = S(t) + K(t) - K(t-1)                      reported nights = stays + backlog build
b(t) = [dK(t) - dK(t-4)] / N(t-4)                the backlog's contribution, in growth points
K(t) = K_UF(t) + U(t)
K_UF(t) = UF(t) / fee_share / ADR_eff(t)         paid, fee-bearing backlog
U(t)    = u(t) * X_gbv(t) / (ADR_eff(t) * r)     unpaid RNPL backlog, zero before 3Q25
X_gbv(t)= B(t) * norm_s * revenue(t+1) / fee_share
u(t)    = 1 - [UF(t)/revenue(t+1)] / (norm_s * B(t))
```

`fee_share` is the guest **and** host service fee collected at booking as a share of GBV, recognised in
revenue at check-in (FY2025 10-K Note 2: "Host and guest fees are recorded as cash with a corresponding
amount in unearned fees"; Item 7 p.45). The grid is the registered {0.124, 0.133, 0.151, 0.155};
**0.133 is central** — it is the realised LTM revenue / LTM GBV ratio (13.2–13.6%, lag-corrected
13.55–13.89%, see `fee_share_evidence.csv`). 0.124 is the guest fee alone and is the divisor error the
audit flags; 0.151 / 0.155 are *posted list* rates on the booking subtotal, which the realised take
rate has never reached.

`ADR_eff` is **the quarter's own ADR**: ADR is a booking-period metric, so the backlog's dollars already
carry the prices at which those nights were booked. Forward ADR (ADR(t+1)) and a 2/3–1/3 kernel-weighted
ADR are both computed and reported in `backlog_uf.csv`; neither reduces the term's historical scatter.

## What governs

`docs/rnpl-short-audit/04_balance-sheet-verification.md` (11 Sep, adversarial audit) **supersedes**
`research/notes/2026-09-11_rnpl-balance-sheet-and-q3-bridge.md` wherever they differ:

* unearned fees is the FX-clean, **migration-neutral** line; funds payable carries an ±8.7pt annual FX
  swing and is not scoreable un-adjusted;
* the single-fee migration share `m` is **not identified** (the joint solve returns −1.4% for 3Q25,
  before the migration existed) and is set to **0** here;
* `u` is solved on unearned fees alone, reproducing `verify_bs_uf_only_solve.csv` ("note baseline");
* the 0.124 divisor in `analysis/src/rnpl_balance_sheet_bridge.py` overstates the backlog 7–25%.

## Outputs (`data/processed/pitch_model_v2/nights_v3/N2/`)

| file | contents |
|---|---|
| `backlog_uf.csv` | K_UF by quarter (4Q20–2Q26) × fee share × ADR basis, with K/N and the implied mean lead |
| `backlog_total.csv` | K = K_UF + U over the full registered grid (fee × ADR basis × B × B-path × r), `band_role=central` marks the central cell |
| `identity_term.csv` | b(t) central / low / high, plus dK/N(t−4), K/N, the same-season pre-RNPL mean of b, the rolling 4-quarter sum, and the identity-implied stays level |
| `identity_term_grid.csv` | every cell behind that band |
| `forward_band.csv` | 3Q26 from the bridge §4 score sheet, and 4Q26–2Q27 with the RNPL GBV share stabilised at 21 / 24 / 27%, over the full grid and both forward nights paths |
| `forward_band_committed.csv` | one row per forward period: b central, band over the whole grid, and band holding the fee share at 0.133 |
| `fee_share_evidence.csv` | LTM revenue / LTM GBV, raw and lag-corrected — the evidence for the 0.133 divisor |
| `norm_sensitivity.csv` | the same series under a same-quarter-GBV norm and under ±5% on the assumed 3Q26 revenue |
| `stays_crosscheck.csv` | identity-implied stays growth vs the reviews stays index (`q3nowcast/E`, `yoy_vmatch` GLOBAL) |
| `diagnostics.csv` | pre-RNPL scatter of b by season, implied vs stated RNPL GBV share, and the two correlation tests |
| `summary.txt` | the printed run summary |

## Read this before using any number

1. **b is noisy.** Its pre-RNPL same-season scatter is sd 1.9–2.6pp in Q1–Q3 (only Q4 is tight, sd 0.1pp,
   n = 3). That is as large as the RNPL effect being measured.
2. **It fails its one validity test.** `corr(reviews index, g_nights)` = 0.863 over 1Q23–2Q26 (n 14);
   `corr(reviews index, g_nights − b)` = 0.503. Removing the backlog term makes the residual *less* like
   measured stays, not more. The best of all 72 registered cells reaches only 0.603.
3. **Splitting b into paid and unpaid halves is meaningless on its own.** RNPL moves nights from the
   fee-bearing pool to the unpaid pool; it does not by itself change the total backlog. At r = 1.00 the
   backlog is exactly invariant to u. Only B (lead-time lengthening) and r (the RNPL ADR premium) move K.
4. **The level depends on an assumed revenue.** The registered norm divides by *next-quarter* revenue, so
   2Q26 inherits the team's $4,800M 3Q26 point; ±5% on it moves b(2Q26) from −0.10 to +7.95. The
   same-quarter-GBV norm removes that dependence entirely and lands at +4.25 vs +3.92 (see §8 of the dossier).
