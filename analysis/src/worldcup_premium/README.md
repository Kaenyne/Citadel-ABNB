# worldcup_premium — the World Cup price premium inside the 2Q26 ADR core

Pre-registration `docs/worldcup-premium/PREREG.md`; results `docs/worldcup-premium/RESULTS.md`; outputs
`data/processed/worldcup_premium/`.

```bash
PYTHONPATH=analysis/src py -3.13 -m worldcup_premium.run        # pre-registered run, exit 0, ~12.5 min
PYTHONPATH=analysis/src py -3.13 -m worldcup_premium.posthoc    # post-hoc checks (event study, bounded translation), exit 0, ~4 min
```

Raw inputs: `data/raw/inside_airbnb/` (monthly 2026 listings parquet), `data/raw/inside_airbnb_reviews/` (June/July
2026 snapshots), `data/raw/inside_airbnb_calendar/`. These are gitignored; the code reads this tree's `data/raw`,
then `$ABNB_RAW`, then the main worktree's. The match schedule (`wc2026_matches_by_venue.csv`, 104 matches) was
parsed from Wikipedia raw wikitext on 22 Sep 2026.

| module | what |
|---|---|
| `config.py` | frozen constants: venues, 75/200 km rule, windows, samples, rounds, translation inputs |
| `fe.py` | OLS with absorbed fixed effects (alternating projections), CR1 cluster SEs |
| `quotes.py` | geography; P1 same-listing quote panel; P2 match-night cross-section; P3 |
| `availability.py` | V1–V3b calendar booked share and timing; A1 Paris 2024 analog |
| `translate.py` | V4 realised stays; §8 translation (invalid: its timing input failed — see RESULTS §2) |
| `run.py` | the pre-registered pipeline |
| `posthoc.py` | post-hoc checks, labelled as such |
