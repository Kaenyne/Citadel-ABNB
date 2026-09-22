def test_prereg_lines_are_the_specs():
    import config as C
    assert C.PREREG["B1_ratio_max"] == 0.75 and C.PREREG["A5_median_ratio_max"] == 0.75
    assert C.PREREG["C1_mean_gap_min_bands"] == 1.0 and C.PREREG["C1_quarters_min"] == 3
    assert C.FREEZE_QI == 2025 * 4 + 1 and C.POST_QIS == [8102, 8103, 8104, 8105]
    assert C.WINDOWS == {"W1": (2022 * 4, 2023 * 4), "W2": (2023 * 4, 2024 * 4)}
    assert abs(sum(C.FY25_NIGHTS_SHARE.values()) - 100.1) < 0.2
