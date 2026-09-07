from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
from summarize_listing_destinations import reconcile, sample_identity_hash, validate_sample_identity


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.sample = [{"case_id":"SD-01", "first_terminal_absence":"2026-01-01"}]
        self.case = {"case_id":"SD-01", "finding":"sale_reported",
                     "event_date":"2026-07-30", "sources":["https://example.com/evidence"]}

    def test_missing_and_duplicate_case_fail(self):
        for cases in ([], [self.case, self.case]):
            with self.assertRaises(ValueError):
                reconcile(self.sample, cases)

    def test_event_requires_dated_source_after_absence(self):
        for changes in ({"event_date":""}, {"sources":[]}, {"event_date":"2025-12-31"}):
            with self.assertRaises(ValueError):
                reconcile(self.sample, [{**self.case, **changes}])

    def test_unknown_remains_unknown(self):
        case = {"case_id":"SD-01", "finding":"unresolved", "event_date":"", "sources":[]}
        self.assertEqual(reconcile(self.sample, [case])[0]["finding"], "unresolved")

    def test_changed_sample_cannot_inherit_old_labels(self):
        sample = [{**self.sample[0], "listing_id":"111", "license_id":"STR-00123L"}]
        expected_hash = sample_identity_hash(sample)
        validate_sample_identity(sample, expected_hash)
        with self.assertRaises(ValueError):
            validate_sample_identity([{**sample[0], "listing_id":"222"}], expected_hash)


if __name__ == "__main__":
    unittest.main()
