"""Reproduce RNPL cancellation materiality sensitivities, not an estimated forecast.

Run from any directory: .venv/Scripts/python.exe analysis/src/rnpl_materiality.py
No network or dependencies. Existing forecast outputs are only read.
"""

import csv
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data/processed/overnight/02_kpi_panel_quarterly.csv"
OUT = ROOT / "outputs/rnpl-audit-20260910"
PRIMARY_URL = "https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm"


def main():
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    # Denominators are the rounded published Nights and Seats Booked figures.
    denominators = {"2026Q3": 133.6, "2026Q4": 121.9}
    nights_column = "nights_m"
    for quarter, expected in [("3Q25", 133.6), ("4Q25", 121.9)]:
        actual = float(next(row for row in rows if row["quarter"] == quarter)[nights_column])
        if not math.isclose(actual, expected, abs_tol=0.051):
            raise ValueError(f"Published denominator mismatch: {quarter}: {actual}")

    thresholds = []
    for quarter, denominator in denominators.items():
        for haircut in [0.5, 1.0, 1.5, 2.0, 3.0]:
            lost = denominator * haircut / 100
            thresholds.append({"quarter": quarter, "haircut_pp": haircut,
                               "net_lost_nights_m": lost})

    required_hazards = []
    for quarter, denominator in denominators.items():
        for haircut in [1.0, 2.0]:
            for exposure in [10.0, 20.0, 40.0, 60.0]:
                for replacement_offset in [0.0, 0.25, 0.50]:
                    loss = denominator * haircut / 100
                    excess_cancellations = loss / (1 - replacement_offset)
                    hazard = excess_cancellations / exposure
                    assert math.isclose(exposure * hazard * (1 - replacement_offset), loss)
                    required_hazards.append({
                        "quarter": quarter, "haircut_pp": haircut,
                        "live_rnpl_nights_m_assumed": exposure,
                        "incremental_same_quarter_net_rebooking_offset_assumed": replacement_offset,
                        "required_incremental_quarter_cancellation_probability_pp": hazard * 100,
                        "net_lost_nights_m": loss,
                    })

    payload = {
        "status": "illustrative materiality thresholds; no exposure or hazard is estimated",
        "units": "nights in millions; growth and probability changes in percentage points",
        "denominator_source": PRIMARY_URL,
        "local_validation_source": str(SOURCE.relative_to(ROOT)),
        "local_source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "definitions": {
            "haircut": "reduction versus an existing reported-net-nights forecast with prior-year denominator fixed",
            "exposure": "unique RNPL nights still live at a specified forecast date; hypothetical",
            "hazard": "revision versus forecast to conditional probability of cancellation during target quarter, not lifetime rate",
            "rebooking": "incremental net nights from replacement bookings recognized in the same quarter; excludes later-quarter offsets",
            "scope": "opening-backlog sensitivity only; future booking flow, its cancellations, product uplift and pull-forward modeled separately",
            "identification": "does not prove RNPL causality; comparison to a no-RNPL counterfactual requires modeling both years",
        },
        "thresholds": thresholds,
        "required_hazards": required_hazards,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "materiality.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# RNPL materiality sensitivities", "",
             "Illustrative thresholds, not fitted forecasts. Rebuild with `analysis/src/rnpl_materiality.py`.", "",
             "## Net nights needed", "",
             "| Growth reduction (points) | Q3 net loss (million nights) | Q4 net loss (million nights) |",
             "|---|---:|---:|"]
    for haircut in [0.5, 1, 1.5, 2, 3]:
        lines.append(f"| {haircut:g} | {133.6 * haircut / 100:.3f} | {121.9 * haircut / 100:.3f} |")
    lines += ["", "## Required remaining cancellation-risk revision", "",
              "A one-point growth reduction; exposures are assumptions. Offsets are incremental net replacement bookings within the same quarter.", "",
              "| Live RNPL nights (millions) | Q3: no offset | Q3: 25% offset | Q4: no offset | Q4: 25% offset |",
              "|---|---:|---:|---:|---:|"]
    for exposure in [10, 20, 40, 60]:
        values = [denom / exposure / (1 - offset) for denom, offset in
                  [(133.6, 0), (133.6, .25), (121.9, 0), (121.9, .25)]]
        lines.append(f"| {exposure} | " + " | ".join(f"{value:.2f} pp" for value in values) + " |")
    lines += ["", "Double these probability revisions for a two-point growth reduction.", "",
              "These are revisions to conditional cancellation probability during the target quarter, beyond risk already in the forecast. They are not comparisons of lifetime RNPL versus non-RNPL cancellation rates.", "",
              "The JSON also includes 50% rebooking offsets. A scenario is feasible only if the revised total probability remains at most 100%; baseline probabilities are not available here.", "",
              f"Denominators: [Airbnb quarterly summary]({PRIMARY_URL}). Local KPI denominators verified; loss-to-growth and hazard-to-loss identities checked during generation."]
    (OUT / "materiality.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}: {len(thresholds)} thresholds, {len(required_hazards)} exposure scenarios.")


if __name__ == "__main__":
    main()
