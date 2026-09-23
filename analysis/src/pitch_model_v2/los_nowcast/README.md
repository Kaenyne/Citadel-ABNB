# los_nowcast

Measures the change in the ADR length-of-stay (LOS) mix term between 2Q26 and 3Q26 bookings, from the Inside Airbnb
calendars already in the main tree. This replaces `adr_engine_v3`'s flat LOS carry (fix k). The package also tests
whether the World Cup shortened host-city stays, and writes the seats and hotel receipt.

- **Pre-registration:** `docs/pitch-model-v2/lines/los_nowcast_prereg.md`. The blob hashes are in
  `data/processed/pitch_model_v2/los_nowcast/00_prereg_hash.txt`.
- **Note:** `docs/pitch-model-v2/lines/los_nowcast.md`.

## Run

```
PYTHONPATH=analysis/src py -3.13 -m pitch_model_v2.los_nowcast.run --workers 3
PYTHONPATH=analysis/src py -3.13 -m pytest analysis/src/pitch_model_v2/los_nowcast/tests -q
```

- **Inputs:** the raw calendars and listings are read, read-only, from `C:\Users\krish\citadel-abnb\data\raw\`. Nothing
  is downloaded.
- **Runtime:** about 10 minutes cold. The per-vintage and per-pair runs are cached as parquet under
  `data/processed/pitch_model_v2/los_nowcast/cache/`. The cache is gitignored and rebuilds.
- **Exit codes:** 0 on success, 2 if construction S fails to reproduce I2 (the reproduction gate).

## Constructions

| | what a run is | dates | status |
|---|---|---|---|
| **F, flow** | nights available in the earlier dump and blocked in the later one: bookings made between the dumps | 2Q26 = Mar→Jun 2026 dumps, 3Q26 = Jun→Aug; 2025 pairs matched by dates (±31 days) and length (±14 days) | booking-dated, like ADR |
| **S, stock** | I2b's lead-matched blocked runs, starting 7–97 days after the dump | Jun and Aug 2026 dumps against 2025 | reproduces I2 |

Each construction is computed two ways:
- **W1:** occupancy-weighted, following 14c;
- **W0:** unweighted.

The LOS term is the change in nights shares by bucket (under 7, 7–27, 28–90), times the 14a price ratio less one.
Regions pool their markets. The global figure uses the 10-K FY25 nights weights. NYC and LA are excluded, because of
their regulatory night minimums.

## Outputs (`data/processed/pitch_model_v2/los_nowcast/`)

| file | what |
|---|---|
| `los_nowcast_result.csv` | forward LOS for 3Q26 and 4Q26, with its band; read by `adr_engine_v3` |
| `delta_by_construction.csv` | the 2Q26 and 3Q26 LOS terms and their change, by construction × weighting, with regional columns |
| `reproduction_I2.csv` | the gate: S against `data/processed/adrq3/I/I2_los_term.csv` |
| `market_stats.csv` | per market × quarter × side: runs, nights by bucket, weighted nights |
| `pairs_S.csv`, `pairs_F.csv` | the vintage pairs used |
| `worldcup_los_ddd.csv`, `worldcup_los_translation.csv`, `worldcup_los_market_windows.csv` | the World Cup test and its translation to the global term |
| `seats_check.csv` | Inside Airbnb "Hotel room" listings and reviews, 2025–26 |
| `summary.json` | the headline numbers |
