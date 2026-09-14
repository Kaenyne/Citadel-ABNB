"""Shared point-in-time backtest harness for the ABNB revenue-forecast programme.

Format version 1.0, frozen 2026-09-11. See README.md (authoritative).
"""
from .paths import (REPO_ROOT, HARNESS_OUT, REGISTRY_DIR, TODAY, ensure_dirs)  # noqa: F401
from . import quarters  # noqa: F401
from .windows import (  # noqa: F401
    GUIDE_EVENTS_ALL, GUIDE_DATES_ALL, GUIDE_DATES_W1, GUIDE_DATES_W2, GUIDE_DATE_LIVE,
    W1_TARGETS, W2_TARGETS, LIVE_TARGETS, WINDOWS, WINDOW_MEMBERSHIP,
    TARGET_TO_GUIDE_DATE, GUIDE_DATE_TO_TARGET, window_of_target, windows_frame,
    assert_matches_ledger,
)
from .registry import (  # noqa: F401
    FORMAT_VERSION, REGISTRY_COLUMNS, REQUIRED_COLUMNS, OPTIONAL_COLUMNS,
    QUANTILE_COLUMNS, QUANTILE_LEVELS, RegistryError, StreetVintageError,
    register, load_registry, validate_registry_frame, registry_path,
    check_replays, check_window_coverage,
)
from .loaders import load_calendar, load_targets, history_as_of, clear_cache  # noqa: F401
from .baselines import (  # noqa: F401
    baseline_naive, baseline_naive_seasonal, baseline_ar1, baseline_trailing4,
    baseline_guide_cushion, baseline_street, BASELINE_SPECS, build_all_baselines,
)
from .metrics import (  # noqa: F401
    crps_from_quantiles, pit_from_quantiles, pinball_loss,
    rolling_split_conformal, attainable_coverage_grid, EXCHANGEABILITY_CAVEAT,
)
from .score import score_registry  # noqa: F401

__all__ = [n for n in dir() if not n.startswith("_")]
