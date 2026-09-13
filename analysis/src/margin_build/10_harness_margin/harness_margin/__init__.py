"""Margin harness (WS10, margin build Sep 2026). Reuses the FROZEN revenue harness
(analysis/src/forecast_methods/harness): calendar, W1/W2/LIVE guide dates, FORMAT 1.0 registry
validator, metric primitives, revenue baselines. Nothing there is modified.

    import sys; sys.path.insert(0, "<repo>/analysis/src/margin_build/10_harness_margin")
    from harness_margin import (load_targets, history_as_of, register, load_registry, score_registry,
                                GUIDE_DATES_W1, GUIDE_DATES_W2, GUIDE_DATE_LIVE, TODAY,
                                revenue_forecast_pit, fy_guide_in_force, q_guide_in_force, load_street)
"""
from .paths import (REPO_ROOT, OUT_DIR, REGISTRY_DIR, BASELINE_METHOD, ensure_dirs)  # noqa: F401
from .frozen import (  # noqa: F401
    Q, W, M, GUIDE_EVENTS_ALL, GUIDE_DATES_ALL, GUIDE_DATES_W1, GUIDE_DATES_W2, GUIDE_DATE_LIVE,
    W1_TARGETS, W2_TARGETS, WINDOW_MEMBERSHIP, TODAY, LIVE_DATE, LIVE_VINTAGES, FORMAT_VERSION,
    REGISTRY_COLUMNS, REQUIRED_COLUMNS, OPTIONAL_COLUMNS, QUANTILE_COLUMNS, QUANTILE_LEVELS,
    RegistryError, StreetVintageError, load_frozen_calendar, load_frozen_targets,
)
from .panel import (  # noqa: F401
    build_targets, load_targets, history_as_of, series_as_of, full_series, TARGET_METRICS, UNITS,
    LINES, FIRST_TARGET_Q, LAST_ACTUAL_Q, LAST_FORWARD_Q,
)
from .guides import build_guides, load_guides, fy_guide_in_force, q_guide_in_force, fy_actual_margin_as_of  # noqa: F401
from .street import build_street, load_street  # noqa: F401
from .registry import (  # noqa: F401
    register, load_registry, validate_margin_frame, registry_path, windows_for, window_ok,
    check_horizon_coverage,
)
from .baselines import (  # noqa: F401
    revenue_forecast_pit, build_revenue_leg, seasonal_ebitda_shares, build_seasonal_shares,
    rule_seasonal_naive, rule_seasonal_naive_drift, rule_trailing4, rule_pct_rev_last4,
    rule_guide_implied, rule_q_guide_implied, build_grid, build_all_baselines,
    RATIO_METRICS, LEVEL_METRICS, COST_LEVEL_METRICS, H_BACKTEST, H_LIVE,
)
from .score import score_registry, scoreboard_md, recency_weights, BASELINE_OBJECTS, HALF_LIFE_Q  # noqa: F401

__all__ = [n for n in dir() if not n.startswith("_")]
