# Harness FORMAT 1.1 — the frozen harness with one rule relaxed

**Status:** additive copy of `../harness/` (FORMAT 1.0, frozen 2026-09-11, still authoritative for every W1 / W2 result).
Nothing in `harness/` was touched. Use 1.1 **only** when 1.0 refuses a LIVE row because of its date.

## The one change

| | FORMAT 1.0 (`harness/`) | FORMAT 1.1 (`harness_v1_1/`) |
|---|---|---|
| `vintage_date` for **W1 / W2** rows | a guide date from `calendar.csv` | **same** |
| `vintage_date` for **LIVE** rows | a guide date or the constant `2026-09-11` | a guide date **or any real date in `[2026-08-07, RUN_DATE]`** |
| LIVE target quarters | `2026Q3` only | any quarter ≥ `2026Q3` (so 5 Nov scenarios for 2026Q4 / 1Q27 can be recorded) |
| `RUN_DATE` | n/a | `CITADEL_ABNB_RUN_DATE` (ISO) if set, else the real calendar date |
| registry directory | `data/processed/forecast_methods/registry/` | **same directory** — one registry, both scorers read it |
| scoreboard | `harness/scoreboard.csv` (authoritative) | `harness_v1_1/scoreboard_v1_1.csv` (adds nothing for W1/W2; exists so LIVE rows can be kept and scored on 5 Nov) |
| spine (calendar / targets / windows) | built by `harness/run.py` | **read from the frozen files, never rewritten** |

Everything else — required columns, PIT rule (`vintage_date` strictly before the target's print), `street_as_of <= vintage_date`,
quantile monotonicity, the two-replay rule, coverage checks, every metric — is the 1.0 code, copied verbatim.
`test_historical_scores_are_identical_to_the_frozen_scoreboard` proves the 276 frozen rows score identically.

## Use

```python
import sys; sys.path.insert(0, "analysis/src/forecast_methods")
from harness_v1_1 import registry as R, RUN_DATE
R.register(df)            # df built exactly as the 1.0 README describes; LIVE rows may use vintage_date=RUN_DATE
```
```bash
python analysis/src/forecast_methods/harness_v1_1/score.py          # -> data/processed/forecast_methods/harness_v1_1/scoreboard_v1_1.{csv,md}
python analysis/src/forecast_methods/harness/score.py               # still run the frozen scorer after any registration
python -m pytest analysis/src/forecast_methods/harness_v1_1/tests -q
```

Why this exists: in the Lane 1 run (12–13 Sep 2026) every package abstained from registering because its real forecast date
(12 Sep) was neither a guide date nor `2026-09-11`. Backdating to the constant would have misstated the information set;
forcing 5 Nov would have asserted future information. 1.1 records the true date and changes no historical score.
