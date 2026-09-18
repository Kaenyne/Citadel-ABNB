"""Load and validate model/pitch_model_v2/spec/lines.yaml.

A line is either an input (values per scenario and period, provenance with grade A/B)
or a formula (an expression in other line ids). Expressions: ids, ids with a relative
period shift `ID[-n]`, ids with an absolute period `ID@PERIOD`, numbers, + - * / and
parentheses. Nothing else, so every cell in the workbook is traceable by name.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
import yaml

ID_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
TOKEN_RE = re.compile(r"\s*(?:(?P<num>\d+\.?\d*)|(?P<id>[A-Z][A-Z0-9_]*)(?:\[(?P<shift>-\d+)\]|@(?P<abs>[0-9A-Z]+))?|(?P<op>[-+*/()]))")

class SpecError(ValueError):
    pass

@dataclass
class Token:
    kind: str            # "num" | "id" | "op"
    text: str
    shift: int = 0
    abs_period: str | None = None

@dataclass
class Line:
    id: str
    label: str
    unit: str
    block: str
    kind: str
    periods: list[str]
    values: dict[str, dict[str, float]] = field(default_factory=dict)
    expr: str = ""
    provenance: dict = field(default_factory=dict)

@dataclass
class Spec:
    meta: dict
    lines: dict[str, Line]
    order: list[str]

def parse_expr(expr: str) -> list[Token]:
    pos, out = 0, []
    while pos < len(expr):
        m = TOKEN_RE.match(expr, pos)
        if not m or m.end() == pos:
            raise SpecError(f"cannot parse expression at {expr[pos:]!r}")
        pos = m.end()
        if m.group("num"):
            out.append(Token("num", m.group("num")))
        elif m.group("id"):
            out.append(Token("id", m.group("id"), int(m.group("shift") or 0), m.group("abs")))
        else:
            out.append(Token("op", m.group("op")))
    return out

def ref_period(tok: Token, period: str, periods: list[str]) -> str:
    if tok.abs_period:
        if tok.abs_period not in periods:
            raise SpecError(f"unknown period {tok.abs_period} in reference {tok.text}@{tok.abs_period}")
        return tok.abs_period
    i = periods.index(period) + tok.shift
    if i < 0 or i >= len(periods):
        raise SpecError(f"reference {tok.text}[{tok.shift}] from {period} falls outside the period list")
    return periods[i]

def to_excel(expr: str, period: str, periods: list[str]) -> str:
    parts = []
    for t in parse_expr(expr):
        if t.kind == "id":
            parts.append(f"{t.text}_{ref_period(t, period, periods)}")
        else:
            parts.append(t.text)
    return "".join(parts)

def _line(d: dict) -> Line:
    for k in ("id", "label", "unit", "block", "kind", "periods"):
        if k not in d:
            raise SpecError(f"line {d.get('id','?')}: missing {k}")
    if not ID_RE.match(d["id"]):
        raise SpecError(f"bad id {d['id']!r}")
    if d["kind"] not in ("input", "formula"):
        raise SpecError(f"{d['id']}: kind must be input or formula")
    return Line(d["id"], d["label"], d["unit"], d["block"], d["kind"], list(d["periods"]),
                d.get("values", {}), d.get("expr", ""), d.get("provenance", {}))

def load(path: str | Path, check_paths: bool = True) -> Spec:
    raw = yaml.safe_load(Path(path).read_text())
    meta = raw["meta"]; periods = list(meta["periods"]); scenarios = list(meta["scenarios"])
    lines: dict[str, Line] = {}
    for d in raw["lines"]:
        ln = _line(d)
        if ln.id in lines:
            raise SpecError(f"duplicate id {ln.id}")
        for p in ln.periods:
            if p not in periods:
                raise SpecError(f"{ln.id}: period {p} not in meta.periods")
        if ln.kind == "input":
            if ln.expr:
                raise SpecError(f"{ln.id}: input may not carry expr")
            prov = ln.provenance
            if prov.get("grade") not in ("A", "B"):
                raise SpecError(f"{ln.id}: input needs grade A or B, got {prov.get('grade')!r}")
            for k in ("dossier", "receipt", "decision", "tolerance"):
                if k not in prov:
                    raise SpecError(f"{ln.id}: provenance missing {k}")
            if check_paths:
                root = Path(path).resolve().parents[3]   # <repo>/model/pitch_model_v2/spec/lines.yaml
                for k in ("dossier", "receipt"):
                    if not (root / prov[k]).exists():
                        raise SpecError(f"{ln.id}: {k} not found at {prov[k]}")
            for sc in scenarios:
                for p in ln.periods:
                    if p not in ln.values.get(sc, {}):
                        raise SpecError(f"{ln.id}: missing value for scenario {sc} period {p}")
        else:
            if not ln.expr:
                raise SpecError(f"{ln.id}: formula needs expr")
        lines[ln.id] = ln
    # resolve references and order
    deps: dict[str, set[str]] = {}
    for ln in lines.values():
        deps[ln.id] = set()
        if ln.kind == "formula":
            for p in ln.periods:
                for t in parse_expr(ln.expr):
                    if t.kind != "id":
                        continue
                    if t.text not in lines:
                        raise SpecError(f"{ln.id}: references unknown id {t.text}")
                    try:
                        rp = ref_period(t, p, periods)
                    except SpecError as e:
                        raise SpecError(f"{ln.id}: {e}") from e
                    if rp not in lines[t.text].periods:
                        raise SpecError(f"{ln.id}: {t.text} has no period {rp}")
                    deps[ln.id].add(t.text)
    order, seen, temp = [], set(), set()
    def visit(n: str):
        if n in seen:
            return
        if n in temp:
            raise SpecError(f"cycle through {n}")
        temp.add(n)
        for m in sorted(deps[n]):
            visit(m)
        temp.discard(n); seen.add(n); order.append(n)
    for n in lines:
        visit(n)
    return Spec(meta, lines, order)
