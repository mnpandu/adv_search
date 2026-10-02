import unittest

from app import SAMPLE_RECORDS, filter_records, matches


class SearchFilterTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
