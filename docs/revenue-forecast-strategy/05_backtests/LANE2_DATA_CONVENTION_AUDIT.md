# Lane 2 — source-driven audit of the all-letter convention

Codex parent · 13 Sep 2026 · `codex/lane2-full`. Written during A2 input audit, before its results.

## Finding

The claim that every W1 letter is evaluable unless the kernel is undefined is contradicted by an explicit quarantine in the committed L0 source. The guide-date convention makes same-day **stamped** pre-guide consensus admissible; it cannot supply a missing timestamp or override `pit_usable=False`.

`data/processed/forecast_methods/L0/L0_vintage_register.csv`, `PG-2024Q3-revenue`: LSEG, revenue 3840.0 musd, timestamp null, `role=pre_guide`, `pit_usable=False`, `vendor_attributed=True`. Its note reads:

> vintage_unknown: this value appears only in 16_consensus_at_print_merged.csv, is absent from 04_consensus_at_print.csv, carries no as-of timestamp or url, and the same row's notes column says NEXT-QUARTER CONSENSUS NOT FOUND. Registered for audit; excluded from every PIT use.

The `print_quarter=2024Q2` row in `data/processed/overnight/16_consensus_at_print_merged.csv` contains the same 3840.0 and the note:

> NEXT-QUARTER CONSENSUS NOT FOUND. CNBC quotes only the $3.67-3.73bn guide; no other contemporaneous source retrievable. This is the single next-quarter gap in the sample.

`harness/targets.csv` propagates that value with the letter date, but propagation is not independent timestamp evidence. Using it as a fallback would bypass the explicit quarantine. No L0 or source row is changed. No new external data is acquired for the offline A2/B2 packages.

## Operational decision

Every one of the 14 W1 / 10 W2 candidate letters must remain in the output, with distinct flags for kernel availability and admissible consensus availability. The 2024Q3 target is consensus-unavailable unless a genuinely timestamped admissible row already exists. The aggregate result uses only evaluable rows and publishes both denominators. Other kernel exclusions must independently state their reason. A zero-cell result is not assumed or accepted without audit.

This is a source-integrity correction to the brief's denominator assumption, not a change to the economic hypothesis, pass line, sign threshold, return horizon, or timestamp convention. The user requested accurate infrastructure that actually works and authorized auditing the previous stop. A clean negative or limited sample is a valid result; invented source availability is not.

## RESUME

Check A2 and B2 notes against these raw rows. Keep the unavailable candidate visible, publish both window counts, and let refuters examine the exclusion. A human or future public-source task may resolve the missing historical consensus with real contemporaneous evidence; this run does not relabel or backdate it.
