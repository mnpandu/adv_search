import unittest
from unittest.mock import patch
import app


class CaseClaimScopeTests(unittest.TestCase):
    def setUp(self):
        app.configure_fields({
            "Case Details": [("Case Details::Case Number", "Case Number", "text")],
            "Claim Details": [("Claim Details::Case Number", "Case Number", "text"),
                              ("Claim Details::Status", "Status", "text")],
        })
        self.rows = {
            "Case Details": [{"Case Details::Case Number": "100"}],
            "Claim Details": [
                {"Claim Details::Case Number": "100", "Claim Details::Status": "Open"},
                {"Claim Details::Case Number": "100", "Claim Details::Status": "Closed"},
                {"Claim Details::Case Number": "200", "Claim Details::Status": "Open"},
            ],
        }

    def search(self, keys, values, mode="Match all (AND)"):
        with patch("app.fetch_records_by_group", return_value=self.rows):
            return app._search(keys, mode, values)[1]["Claim Details"]

    def test_case_number_scopes_all_related_claims(self):
        self.assertEqual(len(self.search(["Case Details::Case Number"], ["Equals", "100"])), 2)

    def test_multiple_case_numbers(self):
        self.assertEqual(len(self.search(["Case Details::Case Number"], ["In", "100, 200"])), 3)

    def test_no_matching_case(self):
        self.assertEqual(self.search(["Case Details::Case Number"], ["Equals", "999"]), [])

    def test_claim_filter_cannot_escape_case_scope_with_or(self):
        rows = self.search(["Case Details::Case Number", "Claim Details::Status"],
                           ["Equals", "100", "Equals", "Open"], "Match any (OR)")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Claim Details::Case Number"], "100")

    def test_no_case_filter_keeps_claim_search_independent(self):
        self.assertEqual(len(self.search(["Claim Details::Status"], ["Equals", "Open"])), 2)
