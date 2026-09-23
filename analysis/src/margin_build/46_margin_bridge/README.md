# 46_margin_bridge

Adjusted EBITDA margin bridge from Street consensus to the official model for 3Q26, 4Q26 and FY27: a revenue step (our revenue,
Street costs flexed at k 0.364), then cost-line steps (our line build vs the Street's cost plan spread across lines at one uniform
growth rate, since no Street cost lines are published), ending exactly on the official income statement's margin.

Run from the repo root (exit 0):

    py -3.13 analysis/src/margin_build/46_margin_bridge/run.py
    py -3.13 analysis/src/margin_build/46_margin_bridge/build_page.py [extra_copy.html]

Outputs: `data/processed/margin_build/46_margin_bridge/` and the page `docs/explainers/2026-09-23_abnb_margin_bridge.html`
(published as a private claude.ai artifact on 23 Sep 2026). The page's two-pager text lives in `build_page.py` (COPY).
