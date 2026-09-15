"""Read-only committed-payload publication scan; emits paths/types, never match values."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter

ROOT = Path(__file__).resolve().parents[6]
REV = "b1e8885a6c294e1b212f9b908a9ce5fbeb3c1ec4"
BASE = "8821961853e4068febbfe2712f9a4e1036c9e629"
SCOPES = [p + "/quant_thesis_validation_v1" for p in (
    "analysis/src/forecast_methods", "data/processed/forecast_methods",
    "docs/revenue-forecast-strategy")]


def git(*args, input_bytes=None):
    return subprocess.check_output(["git", *args], cwd=ROOT, input=input_bytes)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9_]+", args.run_id):
        raise ValueError("Use a plain immutable run id")
    out = ROOT / SCOPES[1] / "publication_audit_v1/content_review" / args.run_id
    if out.exists():
        raise FileExistsError(out)
    entries = []
    for item in git("ls-tree", "-r", "-l", "-z", REV, "--", *SCOPES).split(b"\0"):
        if not item:
            continue
        meta, path = item.split(b"\t", 1)
        mode, kind, oid, size = meta.split()
        assert kind == b"blob"
        entries.append({"path": path.decode(), "git_blob": oid.decode(),
                        "bytes": int(size), "mode": mode.decode()})
    batch = git("cat-file", "--batch", input_bytes=("\n".join(x["git_blob"] for x in entries) + "\n").encode())
    cursor = 0
    findings = []
    keywords = []
    inventory = []
    patterns = {
        "private_key": rb"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        "aws_access_id": rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
        "github_token": rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b",
        "slack_token": rb"\bxox[baprs]-[A-Za-z0-9-]{20,}\b",
        "openai_token": rb"\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}\b",
        "jwt_token": rb"\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\b",
        "email_address": rb"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "url_embedded_credentials": rb"https?://[^\s/:@]{2,}:[^\s/@]{3,}@",
        "literal_credential_assignment": rb"(?i)[\"']?(?:api[_-]?key|password|access[_-]?token|client[_-]?secret)[\"']?\s*[:=]\s*[\"'][A-Za-z0-9_+/=-]{16,}[\"']",
        "restricted_content_label": rb"(?i)(?:confidential and proprietary|not for distribution|strictly confidential|third bridge group|bloomberg terminal export)",
    }
    forbidden_extensions = {".xlsx", ".xls", ".xlsm", ".xlsb", ".parquet", ".zip", ".gz", ".7z", ".har", ".pem", ".p12", ".pfx", ".key", ".sqlite", ".db", ".env"}
    for entry in entries:
        end = batch.index(b"\n", cursor)
        oid, kind, size = batch[cursor:end].split()
        assert oid.decode() == entry["git_blob"] and int(size) == entry["bytes"]
        payload = batch[end+1:end+1+int(size)]
        cursor = end + 2 + int(size)
        ext = Path(entry["path"]).suffix.lower()
        magic = "png" if payload.startswith(b"\x89PNG") else "pdf" if payload.startswith(b"%PDF") else "zip" if payload.startswith(b"PK\x03\x04") else "text"
        entry.update(sha256=hashlib.sha256(payload).hexdigest(), extension=ext or "(none)", content_type=magic)
        inventory.append(entry)
        if entry["bytes"] > 50_000_000:
            findings.append({"path": entry["path"], "type": "over_50MB", "count": 1})
        if ext in forbidden_extensions or magic == "zip":
            findings.append({"path": entry["path"], "type": "raw_export_or_secret_container_candidate", "count": 1})
        for label, pattern in patterns.items():
            count = len(re.findall(pattern, payload))
            if count:
                findings.append({"path": entry["path"], "type": label, "count": count})
        for label, pattern in {"licensed_source_reference": rb"(?i)Bloomberg|Third[ -]?Bridge|LSEG export|Refinitiv Workspace", "personal_record_header": rb"(?i)(?:^|,)(?:email|phone|ssn|social_security_number|bank_account|routing_number|credit_card|customer_name|guest_name)(?:,|\r?$)"}.items():
            count = len(re.findall(pattern, payload, re.MULTILINE))
            if count:
                keywords.append({"path": entry["path"], "type": label, "count": count})
    assert cursor == len(batch)
    changes = git("diff", "--name-status", BASE, REV, "--", *SCOPES).decode().splitlines()
    status = Counter(line.split("\t", 1)[0] for line in changes)
    assert len(changes) == len(inventory) and status == {"A": len(inventory)}
    out.mkdir(parents=True)
    for name, rows, cols in [("inventory.csv", inventory, list(inventory[0])), ("sensitive_candidates.csv", findings, ["path", "type", "count"]), ("reference_candidates.csv", keywords, ["path", "type", "count"])]:
        with (out/name).open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            writer.writerows(rows)
    receipt = {"scan": "Committed quant payload only; heuristic screening plus separate human content review", "commit": REV, "baseline": BASE, "scopes": SCOPES, "files": len(inventory), "bytes": sum(x["bytes"] for x in inventory), "max_file_bytes": max(x["bytes"] for x in inventory), "changes": dict(status), "extension_counts": dict(Counter(x["extension"] for x in inventory)), "content_type_counts": dict(Counter(x["content_type"] for x in inventory)), "sensitive_candidates": len(findings), "reference_candidates": len(keywords), "secret_values_emitted": False, "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "outputs_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}}
    (out/"scan_receipt.json").write_text(json.dumps(receipt, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
