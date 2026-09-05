"""Inside Airbnb index parsing and download planning."""
import re
from typing import NamedTuple


class Snapshot(NamedTuple):
    country: str
    region: str
    city: str
    date: str
    kind: str
    url: str


PAT = re.compile(
    r'https?://data\.insideairbnb\.com/([^/"\'\s]+)/([^/"\'\s]+)/([^/"\'\s]+)/'
    r'(\d{4}-\d{2}-\d{2})/data/(listings|calendar|reviews)\.csv\.gz')


def parse_index(html: str) -> list[Snapshot]:
    out, seen = [], set()
    for m in PAT.finditer(html):
        c, r, city, d, kind = m.groups()
        key = (c, r, city, d, kind)
        if key in seen:
            continue
        seen.add(key)
        out.append(Snapshot(c, r, city, d, kind, m.group(0)))
    return out


def plan_downloads(snapshots, held: set) -> list[Snapshot]:
    return [s for s in snapshots if (s.country, s.region, s.city, s.date, s.kind) not in held]
