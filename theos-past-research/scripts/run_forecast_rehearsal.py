#!/usr/bin/env python3
"""Build or audit a synthetic ABNB forecast workflow-rehearsal packet."""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from abnb_forecasting.packet import audit_packet, build_packet, write_packet  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    forecast = subparsers.add_parser("forecast", help="build a rehearsal packet")
    forecast.add_argument("--input", type=Path, required=True)
    forecast.add_argument("--output", type=Path, required=True)

    audit = subparsers.add_parser("audit", help="verify packet checksums")
    audit.add_argument("--packet-dir", type=Path, required=True)
    return parser


def _forecast(input_path: Path, output_path: Path) -> int:
    with input_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, Mapping):
        raise ValueError("forecast input must be a JSON object")

    packet = build_packet(payload)
    packet_dir = write_packet(output_path, packet).resolve()
    run = packet["run"]
    if not isinstance(run, Mapping):
        raise ValueError("built packet run must be an object")
    print(f"forecast_id: {run['forecast_id']}")
    print(f"research_claim: {packet['research_claim']}")
    print(f"packet_dir: {packet_dir}")
    return 0


def _audit(packet_dir: Path) -> int:
    resolved = packet_dir.resolve()
    findings = audit_packet(resolved)
    if findings:
        for finding in findings:
            print(f"audit failed: {finding}", file=sys.stderr)
        return 1
    print(f"Forecast packet audit passed: {resolved}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "forecast":
            return _forecast(args.input, args.output)
        return _audit(args.packet_dir)
    except FileExistsError:
        print(f"output directory already exists: {args.output}", file=sys.stderr)
        return 1
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(f"forecast rehearsal failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
