from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from probe_listing_archives import capture_timing
from index_listing_archives import indexed_rows


class ArchiveTimingTests(unittest.TestCase):
    def test_nearest_capture_can_be_before_a_requested_after_date(self):
        self.assertEqual(capture_timing("20251018073623", "2026-01-05", "2026-01-23"),
                         "on_or_before_last_airbnb_presence")

    def test_exit_interval_and_boundaries(self):
        for timestamp, expected in [
            ("20250925235959", "on_or_before_last_airbnb_presence"),
            ("20251101000000", "inside_airbnb_exit_interval"),
            ("20251212000000", "on_or_after_first_airbnb_absence"),
        ]:
            with self.subTest(timestamp=timestamp):
                self.assertEqual(capture_timing(timestamp, "2025-09-25", "2025-12-12"), expected)

    def test_invalid_dates_fail(self):
        for timestamp, last, first in [
            ("2025", "2025-09-25", "2025-12-12"),
            ("20250230000000", "2025-09-25", "2025-12-12"),
            ("20250901000000", "2025-12-12", "2025-09-25"),
        ]:
            with self.subTest(timestamp=timestamp, last=last):
                with self.assertRaises(ValueError):
                    capture_timing(timestamp, last, first)

    def test_empty_index_does_not_invent_a_negative_observation(self):
        self.assertEqual(indexed_rows([], "test", "SD-07", {}), [])

    def test_indexed_page_stays_unverified_and_preserves_actual_date(self):
        payload = [["timestamp", "original", "statuscode"],
                   ["20250908175841", "https://example.com/unit", "200"]]
        sample = {"last_present": "2025-09-25", "first_terminal_absence": "2025-12-12"}
        rows = indexed_rows(payload, "test", "SD-07", sample)
        self.assertEqual(rows[0]["archived_timestamp"], "20250908175841")
        self.assertIn("requires separate inspection", rows[0]["interpretation"])
        self.assertEqual(rows[0]["actual_timing"], "on_or_before_last_airbnb_presence")

    def test_malformed_index_fails(self):
        for payload in ([["original"], ["https://example.com"]],
                        [["timestamp", "original", "statuscode"], ["20250908175841"]]):
            with self.assertRaises(ValueError):
                indexed_rows(payload, "test", "SD-07", {})


if __name__ == "__main__":
    unittest.main()
