"""Bridge to the FROZEN revenue harness (analysis/src/forecast_methods/harness).

We import, never copy: the calendar, the W1/W2/LIVE guide dates, the quarter helpers,
the registry column set and validator, the metric primitives, and the revenue baselines
(guide-cushion and naive) that the margin baselines use for their revenue leg.
Nothing in the frozen folder is modified.
"""
from __future__ import annotations

import sys

from . import paths as P

if str(P.FROZEN_SRC) not in sys.path:
    sys.path.insert(0, str(P.FROZEN_SRC))

import harness as FZ                                   # noqa: E402
from harness import quarters as Q                      # noqa: E402,F401
from harness import windows as W                       # noqa: E402,F401
from harness import metrics as M                       # noqa: E402,F401
from harness import paths as FZP                       # noqa: E402,F401
from harness.registry import (                         # noqa: E402,F401
    REGISTRY_COLUMNS, REQUIRED_COLUMNS, OPTIONAL_COLUMNS, QUANTILE_COLUMNS, QUANTILE_LEVELS,
    RegistryError, StreetVintageError, validate_registry_frame, check_replays,
    check_window_coverage, slug as slug_part,
)
from harness.loaders import (                          # noqa: E402,F401
    load_calendar as load_frozen_calendar, load_targets as load_frozen_targets,
    history_as_of as frozen_history_as_of,
)
from harness.baselines import (                        # noqa: E402,F401
    baseline_guide_cushion as frozen_revenue_guide_cushion,
    baseline_naive as frozen_revenue_naive,
)

GUIDE_EVENTS_ALL = W.GUIDE_EVENTS_ALL
GUIDE_DATES_ALL = W.GUIDE_DATES_ALL
GUIDE_DATES_W1 = W.GUIDE_DATES_W1
GUIDE_DATES_W2 = W.GUIDE_DATES_W2
GUIDE_DATE_LIVE = W.GUIDE_DATE_LIVE
W1_TARGETS = W.W1_TARGETS
W2_TARGETS = W.W2_TARGETS
WINDOW_MEMBERSHIP = W.WINDOW_MEMBERSHIP
TODAY = FZP.TODAY                 # 2026-09-11: the only non-guide vintage the frozen validator accepts
LIVE_DATE = TODAY
LIVE_VINTAGES = [GUIDE_DATE_LIVE, TODAY]

FORMAT_VERSION = FZ.FORMAT_VERSION

__all__ = [n for n in dir() if not n.startswith("_")]
