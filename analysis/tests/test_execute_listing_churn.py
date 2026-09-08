from datetime import date
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
from execute_listing_churn import terminal_state, license_id, compatible, build_market


def obs(*items):
    return [(date.fromisoformat(d), state) for d, state in items]


class PersistenceTests(unittest.TestCase):
    def test_exact_90_day_boundary(self):
        result = terminal_state(obs(("2025-01-01", True), ("2025-02-01", False), ("2025-05-02", False)))
        self.assertEqual(result["status"], "persistent_absence")
        self.assertEqual(result["terminal_absence_days"], 90)

    def test_89_days_remains_pending(self):
        result = terminal_state(obs(("2025-01-01", True), ("2025-02-01", False), ("2025-05-01", False)))
        self.assertEqual(result["status"], "pending_persistence")

    def test_absence_duration_starts_at_first_absence_not_last_live(self):
        result = terminal_state(obs(("2025-01-01", True), ("2025-10-01", False)))
        self.assertEqual(result["status"], "pending_persistence")

    def test_unknown_is_not_a_negative_observation(self):
        result = terminal_state(obs(("2025-01-01", True), ("2025-02-01", None), ("2025-05-02", False)))
        self.assertEqual(result["status"], "pending_persistence")
        self.assertEqual(result["negative_observations"], 1)

    def test_positive_resets_clock_even_between_partial_snapshots(self):
        result = terminal_state(obs(("2025-01-01", True), ("2025-02-01", False), ("2025-03-01", True), ("2025-05-02", False)))
        self.assertEqual(result["status"], "pending_persistence")
        self.assertTrue(result["ever_reobserved"])

    def test_return_is_not_terminal_exit(self):
        result = terminal_state(obs(("2025-01-01", True), ("2025-02-01", False), ("2025-06-01", False), ("2025-07-01", True)))
        self.assertEqual(result["status"], "present")
        self.assertTrue(result["ever_reobserved"])

    def test_unknown_endpoint_remains_unknown(self):
        result = terminal_state(obs(("2025-01-01", True), ("2025-02-01", False), ("2025-06-01", None)))
        self.assertEqual(result["status"], "endpoint_unknown")

    def test_out_of_order_or_duplicate_dates_fail(self):
        for series in (obs(("2025-03-01", True), ("2025-02-01", False)), obs(("2025-01-01", True), ("2025-01-01", False))):
            with self.assertRaises(ValueError):
                terminal_state(series)

    def test_initial_presence_required(self):
        with self.assertRaises(ValueError):
            terminal_state(obs(("2025-01-01", False)))

    def test_actual_completion_dates_prevent_false_confirmation(self):
        # May 27 nominal start to Aug 30 is >=90; June 6 completion to Aug 30 is 85.
        result = terminal_state(obs(("2025-09-25", True), ("2026-06-06", False), ("2026-08-30", False)))
        self.assertEqual(result["status"], "pending_persistence")
        self.assertEqual(result["terminal_absence_days"], 85)


class LicenseTests(unittest.TestCase):
    def test_unique_license_with_tot_number(self):
        self.assertEqual(license_id("STR-00123L, 98765"), "STR-00123L")

    def test_conflicting_or_missing_license_not_matched(self):
        for value in ("Exempt", "", "STR-00123L STR-00124L"):
            self.assertEqual(license_id(value), "")

    def test_different_room_or_far_coordinates_reject_link(self):
        row = {"room_type":"Entire home/apt", "latitude":"32.8", "longitude":"-117.2"}
        self.assertTrue(compatible(row, row))
        self.assertFalse(compatible(row, {**row, "room_type":"Private room"}))
        self.assertFalse(compatible(row, {**row, "latitude":"33.8"}))


class MarketIntegrationTests(unittest.TestCase):
    def record(self, identifier, token="STR-00123L"):
        return dict(id=identifier, license=token, room_type="Entire home/apt",
                    latitude="32.8", longitude="-117.2", number_of_reviews_ltm="10",
                    minimum_nights="2", name="Test unit", description="",
                    picture_url="", host_id="1")

    def snapshot(self, day, rows, partial=False):
        from collections import defaultdict
        licenses = defaultdict(list)
        for r in rows:
            licenses[license_id(r["license"])].append(r)
        return dict(start=date.fromisoformat(day), complete=date.fromisoformat(day),
                    rows={r["id"]:r for r in rows}, licenses=licenses, source_partial=partial)

    def test_replacement_keeps_property_observed_when_old_id_is_missing(self):
        snapshots = [self.snapshot("2025-09-01", [self.record("1")]),
                     self.snapshot("2025-12-01", [self.record("2")]),
                     self.snapshot("2026-08-01", [self.record("2")])]
        rows, aliases = build_market("san-diego", snapshots, "conservative")
        self.assertEqual(rows[0]["id_status"], "persistent_absence")
        self.assertEqual(rows[0]["linked_status"], "present")
        self.assertEqual(rows[0]["replacement_id_at_endpoint"], "2")
        self.assertEqual(len(aliases), 2)

    def test_ambiguous_license_does_not_resolve_property(self):
        snapshots = [self.snapshot("2025-09-01", [self.record("1")]),
                     self.snapshot("2025-12-01", []),
                     self.snapshot("2026-08-01", [self.record("2"), self.record("3")])]
        rows, aliases = build_market("san-diego", snapshots, "conservative")
        self.assertEqual(rows[0]["linked_status"], "persistent_absence")
        self.assertFalse(aliases)

    def test_positive_in_partial_file_resets_persistence(self):
        snapshots = [self.snapshot("2025-09-01", [self.record("1")]),
                     self.snapshot("2025-12-01", []),
                     self.snapshot("2026-04-01", [self.record("1")], partial=True),
                     self.snapshot("2026-08-01", [])]
        rows, _ = build_market("san-diego", snapshots, "conservative")
        self.assertEqual(rows[0]["id_status"], "pending_persistence")
        self.assertEqual(rows[0]["last_present"], "2026-04-01")

    def test_partial_baseline_and_unknown_policy_fail(self):
        snapshots = [self.snapshot("2025-09-01", [self.record("1")], partial=True)]
        with self.assertRaises(ValueError):
            build_market("san-diego", snapshots, "conservative")
        with self.assertRaises(ValueError):
            build_market("san-diego", snapshots, "typo")


if __name__ == "__main__":
    unittest.main()
