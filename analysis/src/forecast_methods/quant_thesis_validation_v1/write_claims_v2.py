"""Additive publication repair; no new empirical inference or numerical change."""
from pathlib import Path
import argparse
import json
import write_claims as original

REPAIRS = {
    'C02': {'source': 'l3_bundle_v1/payload/conversion; uncertainty_audit_v1/results_v2'},
    'C04': {'source': 'uncertainty_audit_v1/results_v2'},
    'C05': {
        'source_vintage': 'Final protocol SHA256 dd010ed6d158f1003b9ec55147e16a3f9464010c571b20fe25dad254202cb8ec; reconstructed 2026-09-14',
        'period': 'W1 2023Q1-2026Q2; W2 2024Q1-2026Q2'},
    'C07': {'permitted_sentence': 'RNPL changes payment timing; incremental demand, cancellation behavior and revenue-flow magnitude remain unidentified.'},
    'C13': {'verdict': 'refuted'},
    'C17': {'sample_n': 'Primary passenger-ticket-revenue W1/W2 14/10 nested; metric-matched guide/Street 0'},
    'C18': {'verdict': 'refuted'},
}

def main(out):
    for row in original.ROWS:
        for field, value in REPAIRS.get(row[0], {}).items():
            row[original.FIELDS.index(field)] = value
    original.main(out)
    (out / 'publication_metadata.json').write_text(json.dumps({
        'version': 2, 'claims': 18, 'verdict_definition': 'Verdict evaluates tested_claim; permitted_sentence states the bounded conclusion that may be used.',
        'changes': REPAIRS, 'numerical_claims_changed': False,
        'source_precision_limit': 'The Q2 2026 illustrative display envelope is not a universal bound. See source_audit_v1/ADDITIONAL_Q2_2025_SOURCE_DISCREPANCY_v1.md.'
    }, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    main(p.parse_args().out)
