import unittest
from datetime import date

from app import (
    FIELD_GROUPS,
    SAMPLE_RECORDS,
    SIDEBAR_FIELD_GROUPS,
    _delete_saved_search,
    _load_saved_search,
    _normalize_saved_search,
    _restore_saved_search,
    _run_saved_search,
    _save_current_search,
    _save_search,
    _within_last_days,
    filter_records,
    matches,
)
from search_fields import FIELD_OPERATORS


class SearchFilterTests(unittest.TestCase):
    def test_field_operators_are_loaded_per_json_field(self):
        self.assertIn("Within last (days)", FIELD_OPERATORS["c__created_dts"])
        self.assertIn("Greater than", FIELD_OPERATORS["c__case_id"])
        self.assertIn("Contains", FIELD_OPERATORS["provider_name"])
        self.assertNotIn("In", FIELD_OPERATORS["c__case_id"])

    def test_saved_search_is_validated_and_named_searches_replace_case_insensitively(self):
        saved = _save_search([], "Open cases", "Match all (AND)", ["case_number"],
                             ["Equals", "5001001"])
        replaced = _save_search(saved, "open cases", "Match any (OR)", ["qc_status"],
                                ["Equals", "Completed"])
        self.assertEqual(len(replaced), 1)
        self.assertEqual(replaced[0]["name"], "open cases")
        self.assertEqual(replaced[0]["match_mode"], "Match any (OR)")
        self.assertEqual(replaced[0]["criteria"][0]["field"], "qc_status")
        self.assertIsNone(_normalize_saved_search({"name": "Broken", "criteria": []}))

    def test_saved_search_restore_reselects_fields_and_returns_criteria(self):
        saved = {
            "name": "Recent claims",
            "match_mode": "Match any (OR)",
            "criteria": [
                {"field": "case_number", "operator": "Equals", "value": "5001001"},
                {"field": "qc_status", "operator": "Contains", "value": "Complete"},
            ],
        }
        restored = _restore_saved_search(saved)
        self.assertEqual(restored[-2], "Match any (OR)")
        self.assertEqual(restored[-1], saved)
        self.assertIn("case_number", [key for group in restored[:-2] for key in group])
        self.assertIn("qc_status", [key for group in restored[:-2] for key in group])
        self.assertEqual(len(restored[:-2]), len(SIDEBAR_FIELD_GROUPS))

    def test_case_details_is_hidden_only_from_sidebar(self):
        self.assertNotIn("Case Details", SIDEBAR_FIELD_GROUPS)
        self.assertIn("Case Fields", SIDEBAR_FIELD_GROUPS)
        self.assertIn("Case Details", FIELD_GROUPS)

    def test_load_and_delete_target_one_named_search(self):
        saved = [
            _save_search([], "Open cases", "Match all (AND)", ["c__case_status"],
                         ["Equals", "Open"])[0],
            _save_search([], "Recent claims", "Match any (OR)", ["claim_number"],
                         ["Contains", "CLM"])[0],
        ]
        loaded = _load_saved_search(saved, {"revision": 4}, "Open cases")
        self.assertEqual(loaded[-2]["revision"], 5)
        self.assertEqual(loaded[-2]["search"]["name"], "Open cases")
        self.assertEqual(loaded[-1], "Open cases")
        self.assertEqual([key for group in loaded[:-3] for key in group], ["c__case_status"])
        self.assertEqual([item["name"] for item in _delete_saved_search(saved, "Open cases")],
                         ["Recent claims"])

    def test_save_current_search_rejects_invalid_relative_day_value(self):
        saved, message = _save_current_search(
            [],
            "Recent cases",
            "Match all (AND)",
            [["c__created_dts"]],
            ["Within last (days)", "Open"],
        )
        self.assertEqual(saved, [])
        self.assertIn("Check each filter", message)
        saved, message = _save_current_search(
            [],
            "Recent cases",
            "Match all (AND)",
            [["c__created_dts"]],
            ["Within last (days)", "90"],
        )
        self.assertEqual(saved[0]["criteria"][0]["value"], 90)
        self.assertIn("Saved", message)

    def test_saved_search_runs_with_its_own_criteria_and_mode(self):
        saved = {
            "name": "Pending sample",
            "match_mode": "Match all (AND)",
            "criteria": [
                {"field": "claim_number", "operator": "Contains", "value": "1002"},
                {"field": "qc_review", "operator": "Equals", "value": "Action Required"},
            ],
        }
        with unittest.mock.patch("app.fetch_records", return_value=SAMPLE_RECORDS):
            summary, rows, _query = _run_saved_search(saved)
        self.assertEqual(summary, "1 matching records")
        self.assertEqual(rows[0][4], "CLM-1002")

    def test_in_with_and_and_or(self):
        criteria = [
            ("case_number", "Equals", "5001001"),
            ("claim_number", "In", "CLM-1002, CLM-2044"),
        ]
        self.assertEqual(
            [r["claim_number"] for r in filter_records(SAMPLE_RECORDS, criteria)],
            ["CLM-1002"],
        )
        self.assertEqual(len(filter_records(SAMPLE_RECORDS, criteria, "Match any (OR)")), 3)

    def test_in_exact_case_insensitive_values(self):
        record = {"provider_name": "2111"}
        self.assertTrue(matches(record, "provider_name", "In", "222, 2111"))
        self.assertFalse(matches(record, "provider_name", "In", "211, 222"))
        self.assertTrue(matches({"provider_name": "Clinic, Inc"}, "provider_name", "In", '"clinic, inc", Other'))
        self.assertFalse(matches(record, "provider_name", "In", " , , "))
        self.assertFalse(matches({"provider_name": None}, "provider_name", "In", "222"))

    def test_in_matches_individual_focus_code(self):
        self.assertTrue(matches({"focus_code": ["Coding", "Other"]},
                                "focus_code", "In", "Clinical, coding"))

    def test_case_number_equals(self):
        results = filter_records(
            SAMPLE_RECORDS,
            [("case_number", "Equals", "5001001")],
        )
        self.assertEqual([row["claim_number"] for row in results], ["CLM-1001", "CLM-1002"])

    def test_claim_contains_and_decision_filter_match_all(self):
        results = filter_records(
            SAMPLE_RECORDS,
            [
                ("claim_number", "Contains", "1002"),
                ("qc_review", "Equals", "Action Required"),
            ],
        )
        self.assertEqual([row["claim_number"] for row in results], ["CLM-1002"])

    def test_or_mode_matches_either_condition(self):
        results = filter_records(
            SAMPLE_RECORDS,
            [
                ("case_number", "Equals", "5002007"),
                ("qc_review", "Equals", "Action Required"),
            ],
            "Match any (OR)",
        )
        self.assertEqual([row["claim_number"] for row in results], ["CLM-1002", "CLM-2044"])

    def test_numeric_and_date_operators(self):
        results = filter_records(
            SAMPLE_RECORDS,
            [
                ("over_payment", "Greater than", 2.5),
                ("reviewed_dts", "After", "2026-04-11"),
            ],
        )
        self.assertEqual([row["claim_number"] for row in results], ["CLM-1002"])

    def test_within_last_days_uses_rolling_inclusive_window(self):
        today = date(2026, 10, 1)
        self.assertTrue(_within_last_days(date(2026, 7, 3), 90, today))
        self.assertTrue(_within_last_days(today, 90, today))
        self.assertFalse(_within_last_days(date(2026, 7, 2), 90, today))
        self.assertFalse(_within_last_days(date(2026, 10, 2), 90, today))
        self.assertFalse(_within_last_days(date(2026, 10, 1), "invalid", today))


if __name__ == "__main__":
    unittest.main()
