# H1/H2 bridge v3 — nights and ex-FX ADR re-based to the team baseline and the ADR v3 card

Built 12 Sep 2026 by `analysis/src/h1_to_h2_bridge_v3.py` (a copy of the v2 script; v1, v2 and their
output folders are untouched). Rebuild with:

```
python analysis/src/h1_to_h2_bridge_v3.py data/raw/fred
```

What changed against v2, and nothing else:

- `nights_yoy_pct` 3Q26 / 4Q26: team baseline +9.9% (146.8mm; band 8.5 to 11.0 from the reviews stays
  index) and +8.1% (131.8mm; ADR v3 N memo case B, with case A +8.9% as the top of the band) replace the
  pattern plus the unfitted RNPL-lap and World Cup overlays. The old overlays are kept as retired rows.
- `adr_yoy_exfx_pct` 3Q26 / 4Q26: the ADR v3 card's ex-FX line (variant `v3_with_K`, midpoint FX;
  `data/processed/adrv3/P/adr_card_v3.csv`) replaces the pattern plus the seats-dilution overlay. The
  card already carries new-business dilution inside its ex-FX, so the seats overlay is retired.
- FX lines unchanged from v2 (ADR v3 midpoint; fx_lag_v2 kernel +1.0pp for 4Q26 revenue FX).
- `h2_bridge_v3_card_check.csv` shows the bridge reproduces the card's nights, reported ADR and GBV to
  rounding. `h2_bridge_v3_rebased_lines.csv`, `h2_bridge_v3_vs_v2_delta.csv` and
  `h2_bridge_v3_vs_v1_delta.csv` show what moved.

All FX inputs are on FRED data through **2026-09-04**. Read the note
`docs/revenue-forecast-strategy/05_backtests/REBASE_h2_bridge_v3_nights_adr.md` before quoting anything;
the v1 interpretation notice in `docs/RNPL_HANDOFF.md` still applies to the pattern layer.
