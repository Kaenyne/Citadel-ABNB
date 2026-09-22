"""Seed model/pitch_model_v2/spec/lines.yaml from mapping.yaml and the dossiers' 2a tables.

mapping.yaml is human-authored: ids, kinds, blocks, units, periods, provenance entries
(dossier, receipt, grade, decision, tolerance, and per-entry `item` / `scenario_map` /
`periods`), and formula `expr`. It carries no values. This module reads it, resolves each
input line's `values` from the dossiers' `### 2a.` tables (via qa._dossier_points, the
same parser qa.check uses), and writes the complete lines.yaml. Formula lines pass through
unchanged. Nothing here invents a number: any (item, scenario, period) the mapping needs
that is not stated in a dossier's 2a table raises SpecSeedError.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
import yaml
from . import qa as qamod

DEFAULT_MAPPING = "model/pitch_model_v2/spec/mapping.yaml"
DEFAULT_OUT = "model/pitch_model_v2/spec/lines.yaml"


class SpecSeedError(ValueError):
    pass


def _entries(raw_provenance) -> list[dict]:
    if isinstance(raw_provenance, dict):
        return [raw_provenance] if raw_provenance else []
    if isinstance(raw_provenance, list):
        return list(raw_provenance)
    return []


def _dossier_points(dossier: str, root: Path, cache: dict[str, dict]) -> dict:
    pts = cache.get(dossier)
    if pts is None:
        msgs: list[str] = []
        path = root / dossier
        if not path.exists():
            raise SpecSeedError(f"NEEDS_CONTEXT: dossier not found: {dossier}")
        pts = qamod._dossier_points(path, dossier, msgs)
        if msgs:
            raise SpecSeedError(f"NEEDS_CONTEXT: {dossier}: {'; '.join(msgs)}")
        cache[dossier] = pts
    return pts


def _lookup(pts: dict, item: str, dossier_sc: str, period: str,
            lid: str, sc: str, p: str, dossier: str) -> float:
    """Look up (item, dossier_sc, period) in the dossier's 2a points, falling back
    from the literal period to "all" -- the same fallback order qa.check uses."""
    key = (item, dossier_sc, period)
    if key in pts:
        return pts[key]
    key_all = (item, dossier_sc, "all")
    if key_all in pts:
        return pts[key_all]
    raise SpecSeedError(
        f"NEEDS_CONTEXT: {lid} scenario {sc!r} period {p!r} needs dossier item "
        f"{item!r} scenario {dossier_sc!r} period {period!r} (or 'all') in {dossier}, "
        f"but no such row is in its 2a table"
    )


def _seed_line(d: dict, scenarios: list[str], root: Path, cache: dict[str, dict]) -> dict:
    out = dict(d)
    if d.get("kind") != "input":
        return out
    line_periods = list(d["periods"])
    entries = _entries(d.get("provenance", {}))
    values: dict[str, dict[str, float]] = {sc: {} for sc in scenarios}
    for entry in entries:
        entry_periods = entry.get("periods", line_periods)
        item = entry.get("item", "")
        scenario_map = entry.get("scenario_map", {})
        dossier = entry["dossier"]
        pts = _dossier_points(dossier, root, cache)
        for sc in scenarios:
            dossier_sc = scenario_map.get(sc, sc)
            for p in entry_periods:
                values[sc][p] = _lookup(pts, item, dossier_sc, p, d["id"], sc, p, dossier)
    out["values"] = values
    return out


def generate(mapping_path: str | Path, root: str | Path | None = None) -> dict:
    mapping_path = Path(mapping_path)
    if root is None:
        # model/pitch_model_v2/spec/mapping.yaml -> repo root, same depth spec.load uses.
        root = mapping_path.resolve().parents[3]
    root = Path(root)
    raw = yaml.safe_load(mapping_path.read_text())
    scenarios = list(raw["meta"]["scenarios"])
    cache: dict[str, dict] = {}
    lines = [_seed_line(d, scenarios, root, cache) for d in raw["lines"]]
    return {"meta": raw["meta"], "lines": lines}


def write(mapping_path: str | Path, out_path: str | Path, root: str | Path | None = None) -> Path:
    doc = generate(mapping_path, root=root)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(yaml.safe_dump(doc, sort_keys=False, width=100, allow_unicode=True))
    return out_path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", default=DEFAULT_MAPPING)
    ap.add_argument("--out", default=DEFAULT_OUT)
    a = ap.parse_args(argv)
    out = write(a.mapping, a.out)
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
