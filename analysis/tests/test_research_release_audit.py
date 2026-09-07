"""Regression tests for defects found during the pre-publication code audit."""
from collections import defaultdict
from copy import deepcopy
from datetime import date
from pathlib import Path
import csv
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from audit_hotel_funnel import count
from execute_listing_churn import build_market, terminal_state, write_csv
from model_hotel_funnel import fraction, available_daily_rooms
from summarize_fee_churn import economic_scenarios
from summarize_listing_destinations import reconcile
from verify_hotel_capacity import hotel_category_sum
from research_integrity import validate_selection, verify_frozen_report
from acquire_churn_archive import KEEP, inspect_capture, validate_source_row
import gzip
import hashlib


class PublicationAuditTests(unittest.TestCase):
    def test_equal_length_incomplete_manifest_is_rejected(self):
        expected = [dict(market='a', date='2025-09-01'), dict(market='b', date='2025-09-01')]
        valid = [dict(market=r['market'], snapshot_start=r['date']) for r in expected]
        validate_selection(valid, expected)
        for rows in (valid[:1]*2, [valid[0], dict(market='other', snapshot_start='2025-09-01')]):
            with self.assertRaises(ValueError):
                validate_selection(rows, expected)

    def test_source_paths_cannot_escape_capture_directory(self):
        valid = dict(link='san-diego', publishDate='2025-09-01', dataRoot='https://data.insideairbnb.com/us/ca/san-diego/')
        validate_source_row(valid)
        validate_source_row({**valid, 'link': 'bogotá'})
        for change in ({'link':'../escape'}, {'publishDate':'2025-09-99'},
                       {'dataRoot':'https://data.insideairbnb.com/../../'},
                       {'dataRoot':'https://data.insideairbnb.com.evil.example/'}):
            with self.assertRaises(ValueError):
                validate_source_row({**valid, **change})

    def test_reinspection_preserves_existing_compact_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            source, compact = Path(folder)/'raw.gz', Path(folder)/'compact.gz'
            def write_source(identifier):
                with gzip.open(source, 'wt', encoding='utf-8', newline='') as handle:
                    writer = csv.DictWriter(handle, fieldnames=(*KEEP,'source','last_scraped'))
                    writer.writeheader()
                    writer.writerow(dict(id=identifier, source='city scrape',last_scraped='2025-09-02'))
            write_source('1')
            inspect_capture(source, compact, '2025-09-01')
            frozen = compact.read_bytes()
            inspect_capture(source, compact, '2025-09-01')
            self.assertEqual(compact.read_bytes(), frozen)
            write_source('2')
            with self.assertRaisesRegex(ValueError, 'Existing compact content differs'):
                inspect_capture(source, compact, '2025-09-01')
            self.assertEqual(compact.read_bytes(), frozen)

    def test_dated_report_refuses_changed_input_and_accepts_git_newlines(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'analysis/config').mkdir(parents=True)
            source = root/'input.csv'
            source.write_bytes(b'a\r\n1\r\n')
            config = {'reports': {'example.py': {'input.csv': hashlib.sha256(b'a\n1\n').hexdigest()}}}
            (root/'analysis/config/churn_hotel_report_inputs.json').write_text(json.dumps(config))
            verify_frozen_report(root, 'example.py')
            source.write_bytes(b'a\n2\n')
            with self.assertRaisesRegex(ValueError, 'Frozen report input changed'):
                verify_frozen_report(root, 'example.py')

    def test_zero_credit_exposure_has_no_redemption_threshold(self):
        from model_hotel_funnel import break_even_redemption, validate_config
        root = Path(__file__).resolve().parents[2]
        config = json.loads((root/'analysis/config/hotel_funnel_audit.json').read_text())
        config['assumptions']['credit_eligible_gbv_share'] = 0
        validate_config(config)
        self.assertIsNone(break_even_redemption(config['assumptions']))
        config['assumptions']['adr_usd'] = 0
        with self.assertRaises(ValueError):
            validate_config(config)

    def test_fractional_negative_and_boolean_review_counts_fail(self):
        for value in ('1.9', '-1', True, 'NaN', 'Infinity'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                count({'reviews': value}, 'reviews')
        self.assertIsNone(count({'reviews': ''}, 'reviews'))
        self.assertEqual(count({'reviews': '0.0'}, 'reviews'), 0)

    def test_invalid_observation_states_and_persistence_fail(self):
        for value in (0, 1, 0.0, 1.0):
            with self.subTest(value=value), self.assertRaises(ValueError):
                terminal_state([(date(2025, 1, 1), True), (date(2025, 2, 1), value)])
        for days in (True, float('nan'), float('inf'), 0.5):
            with self.subTest(days=days), self.assertRaises(ValueError):
                terminal_state([(date(2025, 1, 1), True)], days)

    def test_pilot_cannot_reassign_an_existing_baseline_id(self):
        def record(identifier, token):
            return dict(id=identifier, license=token, room_type='Entire home/apt',
                        latitude='32.8', longitude='-117.2', number_of_reviews_ltm='10',
                        minimum_nights='2', name='synthetic', description='', picture_url='', host_id='h')
        def snapshot(day, rows):
            licenses = defaultdict(list)
            for row in rows:
                licenses[row['license']].append(row)
            return dict(start=date.fromisoformat(day), complete=date.fromisoformat(day),
                        rows={r['id']: r for r in rows}, licenses=licenses, source_partial=False)
        snapshots = [snapshot('2025-09-01', [record('1', 'STR-00123L'), record('2', 'STR-00456L')]),
                     snapshot('2025-12-01', [record('2', 'STR-00123L')]),
                     snapshot('2026-08-01', [record('2', 'STR-00123L')])]
        rows, aliases = build_market('san-diego', snapshots, 'conservative')
        self.assertEqual(aliases, [])
        self.assertEqual(rows[0]['linked_status'], 'persistent_absence')

    def test_failed_csv_validation_does_not_damage_previous_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'results.csv'
            target.write_bytes(b'previous,verified\n1,2\n')
            before = target.read_bytes()
            with self.assertRaises(ValueError):
                write_csv(target, [{'a': 1}, {'a': 2, 'unexpected': 3}])
            self.assertEqual(target.read_bytes(), before)

    def test_manual_evidence_cannot_replace_sample_identity(self):
        sample = [dict(case_id='SD-01', listing_id='1', first_terminal_absence='2026-01-01')]
        evidence = [dict(case_id='SD-01', listing_id='2', finding='unresolved')]
        with self.assertRaises(ValueError):
            reconcile(sample, evidence)

    def test_boolean_capacity_assumptions_are_rejected(self):
        for value in (True, False):
            with self.assertRaises(ValueError):
                fraction(value)
        with self.assertRaises(ValueError):
            available_daily_rooms(100, True)
        with self.assertRaises(ValueError):
            hotel_category_sum(True, [True], [])
        with self.assertRaises(ValueError):
            hotel_category_sum(float('inf'), [float('inf')], [])

    def test_economic_scenarios_reject_impossible_inputs(self):
        root = Path(__file__).resolve().parents[2]
        ledger = json.loads((root / 'research/sources/fee_churn_catalyst.json').read_text())
        cases = [('new_host_fee', 1.0, 'economic_example'),
                 ('old_booking_subtotal', -100, 'economic_example'),
                 ('relative_lost_listing_productivity', float('nan'), 'materiality_scenario'),
                 ('booking_value_recaptured_within_airbnb', [1.1], 'materiality_scenario'),
                 ('incremental_churn_rates', [-0.1], 'materiality_scenario')]
        for key, value, section in cases:
            candidate = deepcopy(ledger)
            candidate[section][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                economic_scenarios(candidate)


if __name__ == '__main__':
    unittest.main()
