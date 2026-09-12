# fx_lag — how far ahead does today's FX hit Airbnb revenue?

Run (rebuilds every output, exit code 0):

```bash
cd "/Users/theomachado/Library/CloudStorage/OneDrive-UniversityofFlorida/Young, Willem K.'s files - Citadel - ABNB/Citadel-ABNB"
python analysis/src/forecast_methods/fx_lag/run.py
```

Runtime ~25 s. All paths resolve from `__file__`, so the script also runs from
anywhere. Outputs are written progressively: a crash mid-run still leaves every
completed stage on disk.

| file | what it does |
|---|---|
| `common.py` | paths, quarter helpers, the **interval log-likelihood** (the only admissible likelihood for letter-rounded integers) |
| `baskets.py` | stage (a): daily FRED bilaterals -> quarterly currency y/y -> regional baskets -> global revenue-weighted basket |
| `panel.py` | the analysis panel: disclosed FX points, hedge disclosures, basket lags 0-3, the Phi kernel base and `lambda` |
| `pit_fx.py` | point-in-time basket: QTD actual + spot held constant; L0 revenue shares filtered on `knowable_from <= vintage` |
| `fits.py` | stage (b) ADR contemporaneous fits and the `05_fx_fits.csv` reproduction; **Object A** (lag confidence set + H0 test), **Object B** (wedge), **Object C** (falsification) |
| `stages.py` | hypothesis horse-race (H0/H1/H2/H3) with LOO, PIT expanding-window replay, block bootstrap, determined share, forward schedule, kernel-carried FX, the four-way reconciliation, hedges |
| `registry_out.py` | writes the three registry objects in the FROZEN v1.0 harness format |
| `run.py` | entry point; also emits `00_pit_caveats.csv` and asserts the two prior replays are distinct |

**Two prior replays (fixed round 2).** `stages.full_sample_coefficients()` fits each spec once on
the whole sample; `stages.pit_forecasts(d, coef_override=...)` re-applies those weights at every
guide date with the drivers still point-in-time. `09d`/`09e`/`09f` hold the full-sample replay,
its window scores and the PIT-vs-full delta table. `run.py` fails the run if the two replays ever
produce identical points again (the round-1 bug).

Data outputs: `data/processed/forecast_methods/fx_lag/`.
Registry objects: `fx-lag__fx_rev_next_q_h2`, `fx-lag__fx_rev_next_q_h3`,
`fx-lag__live_fx_schedule`.

**This package emits no additive FX pp adjustment to revenue.** Every FX pp it
reports is an *output* of the lagged-GBV arithmetic. The forward hedge file
`28_fx_hedge_forward.csv` is never added on top of the letter-stated (already
after-hedge) FX points. FX pp are never quoted to two decimals in the note.
