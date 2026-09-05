#!/usr/bin/env python3
"""Read-only validation for the permission-resolution continuation."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse


RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
OUT = RUN / "permission_resolution"
EXPECTED_LEDGER_SHA = "17a531de7ac9e29c1709923462f7b088a932ffefe638c790ba9aa91538e9cc8e"


def rows(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


candidate_ids = {r["source_id"] for r in csv.DictReader((RUN / "candidate_edge_registry.csv").open())}
assert len(candidate_ids) == 15

manifest = rows("permission_recon_manifest.csv")
results = rows("permission_recon_results.csv")
audit = rows("request_level_audit.csv")
gates = rows("data_path_gate_results.csv")
sources = rows("source_permission_resolution.csv")
assert len(manifest) == 83 and len({r["request_id"] for r in manifest}) == 83
assert len(results) == 83 and len({r["request_id"] for r in results}) == 83
assert len(audit) == 84 and len({r["request_id"] for r in audit}) == 84
assert len(gates) == 15 and {r["source_id"] for r in gates} == candidate_ids
assert len(sources) == 15 and {r["source_id"] for r in sources} == candidate_ids
assert all(r["assessment_allowed"] == "false" for r in gates)
assert all(r["final_data_path_allowed"] == "false" for r in sources)
assert all(r["strict_pit_eligible_feature_count"] == "0" for r in sources)
assert not any(r["updated_decision"] == "PROMOTE" for r in sources)

permission = [r for r in audit if r["request_class"] == "permission_only"]
payloads = [r for r in audit if r["request_class"] == "data_payload"]
assert len(permission) == 83 and len(payloads) == 1
assert sum(r["request_sent"] == "true" for r in permission) == 68
provider = [r for r in permission if r["provider_http_reached"] == "true"]
assert len(provider) == 35
assert Counter(r["http_status"] for r in provider) == Counter({"200": 29, "403": 5, "404": 1})
assert all(r["registration_precedes_request"] == "true" for r in audit if r["request_sent"] == "true")
assert all(r["no_auth"] == "true" and r["no_cookies"] == "true" and r["no_personal_data"] == "true" for r in manifest)

# The provider-facing cadence never exceeds ten requests in any rolling minute
# for one host; all requests used the truthful lane user agent in the manifest.
by_host: dict[str, list[datetime]] = {}
for r in provider:
    host = urlparse(r["requested_url"]).netloc
    by_host.setdefault(host, []).append(datetime.fromisoformat(r["requested_at_utc"].replace("Z", "+00:00")))
for times in by_host.values():
    times.sort()
    for i, start in enumerate(times):
        assert sum(start <= t < start + timedelta(minutes=1) for t in times[i:]) <= 10

lane_dir = {
    "physical_world_activity_edge": RUN / "physical_world_activity_edge" / "permission_resolution",
    "supply_scarcity_web_edge": RUN / "supply_scarcity_web_edge" / "permission_resolution",
}
for r in provider:
    assert r["cache_path"] and r["sha256"]
    path = lane_dir[r["lane"]] / r["cache_path"]
    assert path.is_file(), path
    assert digest(path) == r["sha256"]
    assert path.stat().st_size == int(r["bytes"])

payload = payloads[0]
assert payload["request_id"] == "DP-PW-001"
assert payload["source_ids"] == "NYC_311_TOURISM_STRESS"
assert payload["outcome"] == "unauthorized_under_final_gate_then_quarantined"
assert payload["final_lead_gate_allowed"] == "false"
assert payload["strict_pit_eligible"] == "false"
assert payload["http_status"] == "200" and payload["bytes"] == "28"
assert payload["sha256"] == "c84303069da97fd855fdf52d7a7814ce717976b358f439e21136eb4ffb60714e"
payload_path = RUN / payload["cache_path"]
assert digest(payload_path) == payload["sha256"] and payload_path.stat().st_size == 28
parsed = json.loads(payload_path.read_text(encoding="utf-8"))
assert isinstance(parsed, list) and len(parsed) == 1 and set(parsed[0]) == {"request_count"}
assert "personal" in payload["personal_data_scan"] and "no row-level" in payload["personal_data_scan"]
with (RUN / "physical_world_activity_edge" / "permission_resolution" / "data_probe_results.csv").open(newline="", encoding="utf-8") as handle:
    assert [r["probe_id"] for r in csv.DictReader(handle)] == ["DP-PW-001"]
with (RUN / "supply_scarcity_web_edge" / "permission_resolution" / "data_probe_manifest.csv").open(newline="", encoding="utf-8") as handle:
    assert list(csv.DictReader(handle)) == []
assert len(list((RUN / "physical_world_activity_edge" / "permission_resolution" / "cache" / "data_probe").glob("*"))) == 1

lane_only = {"TFL_CYCLE_HIRE", "CDOT_CONTINUOUS_COUNTS", "AUSTIN_ACTIVE_STR", "HAWAII_TAT_DISTRICT", "RECREATION_GOV_AVAILABILITY"}
assert not any(lane_only & set(r["source_ids"].split("|")) for r in audit)

with (RUN / "phase_e1" / "event_level_replay.csv").open(newline="", encoding="utf-8") as handle:
    replay = [r for r in csv.DictReader(handle) if r["hypothesis_id"] in {"H-004", "H-005", "H-006"}]
assert len(replay) == 138 and not any(r["eligible"] == "true" for r in replay)
assert Counter(r["hypothesis_id"] for r in replay) == Counter({"H-004": 46, "H-005": 46, "H-006": 46})

assert digest(ROOT / "research" / "hypothesis_ledger.csv") == EXPECTED_LEDGER_SHA
with (ROOT / "research" / "scraping_audit.csv").open(newline="", encoding="utf-8") as handle:
    canonical = list(csv.DictReader(handle))
ids = [r["audit_id"] for r in canonical]
assert len(ids) == len(set(ids))
continuation = [r for r in canonical if r["audit_id"].startswith("SA-20260903-PR-")]
assert len(continuation) == 15 and {r["source_id"] for r in continuation} == candidate_ids
assert all(r["collection_allowed"] == "false" for r in continuation)
exception = [r for r in continuation if r["source_id"] == "NYC_311_TOURISM_STRESS"]
assert len(exception) == 1 and exception[0]["status"] == "compliance_exception_payload_quarantined"

for line in (OUT / "checksums.sha256").read_text(encoding="utf-8").splitlines():
    expected, name = line.split("  ", 1)
    assert digest(OUT / name) == expected

print("PERMISSION_RESOLUTION_VALIDATION_OK")
