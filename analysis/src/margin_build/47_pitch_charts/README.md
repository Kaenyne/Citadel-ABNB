# 47_pitch_charts

Candidate charts for thesis 3 (costs) in the two-pager, drawn in R (ggplot2 + ragg) in an Airbnb palette (Rausch #FF5A5F,
Babu #00A699, Hof #484848, Foggy #767676) with Figtree, the closest open face to Airbnb Cereal (SIL OFL, bundled in `fonts/`).

Run from the repo root (both exit 0):

    py -3.13 analysis/src/margin_build/47_pitch_charts/prepare_data.py   # datasets from committed CSVs (02, 41, 42, 45, 46)
    Rscript analysis/src/margin_build/47_pitch_charts/charts.R          # PNGs, 300 dpi, into deck/figures/thesis3_candidates/

Every plotted number is read from `data/processed/margin_build/47_pitch_charts/`, which `prepare_data.py` builds from
committed outputs; d08 (AI saving vs spending) quotes the 2Q26 10-Q MD&A as in `notes/45_ai_margin.md`.
