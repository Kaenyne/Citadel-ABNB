"""Compare full-precision identities with references published to 0.001 pp.

Do not round an already-rounded reference a second time: 12.325 can represent
12.325497, whose correct two-decimal display is 12.33.
"""
import math

EXPECTED = {
    "2024Q1":13.034, "2025Q1":12.325, "2026Q1":12.612,
    "2024Q2":13.449, "2025Q2":13.946, "2026Q2":13.736,
    "2023Q3":17.391, "2024Q3":17.145, "2025Q3":17.182,
    "2023Q4":11.946, "2024Q4":12.117, "2025Q4":12.026,
}


def within_reference_precision(value, reference):
    return math.isfinite(value) and abs(value-reference) <= 0.0005+1e-12
