from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Decision:
    id: str; line: str; period: str; scenario: str; value: float | str; reason: str; rejected: str; date: str

def load(path: str | Path) -> list[Decision]:
    rows = []
    for ln in Path(path).read_text().splitlines():
        if not ln.startswith("| DEC-"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) != 8:
            raise ValueError(f"bad decision row: {ln}")
        try:
            val: float | str = float(cells[4])
        except ValueError:
            val = cells[4]
        rows.append(Decision(cells[0], cells[1], cells[2], cells[3], val, cells[5], cells[6], cells[7]))
    return rows
