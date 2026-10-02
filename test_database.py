import os
import unittest
from unittest.mock import MagicMock, patch

from db_config import get_settings
from database import build_query, connect_db, fetch_records


class DatabaseTests(unittest.TestCase):
    def test_default_and_override_precedence(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(get_settings()["backend"], "postgres")
        with patch.dict(os.environ, {"DB_TYPE": "postgres", "PGSCHEMA": "EXISTING"}):
            self.assertEqual(get_settings()["schema"], "EXISTING")
            self.assertEqual(get_settings("postgres")["backend"], "postgres")

    def test_reject_unknown_backend_and_unsafe_identifier(self):
        with self.assertRaises(ValueError):
            get_settings("invalid")
        settings = get_settings("postgres")
        settings["schema"] = "public; DROP TABLE x"
        with self.assertRaises(ValueError):
            build_query(settings)

    def test_postgres_uses_table_configuration(self):
        settings = get_settings("postgres")
        settings.update(schema="OWNER", case_table="CASES", password="test-only")
        self.assertIn("FROM OWNER.CASES", build_query(settings))
        driver = MagicMock()
        with patch.dict("sys.modules", {"psycopg": driver}):
            connect_db(settings)
        driver.connect.assert_called_once_with(
            host=settings["host"], port=settings["port"], dbname=settings["database"],
            user=settings["user"], password="test-only", connect_timeout=5
        )

    def test_json_arrays_preserved_and_aliases_normalized(self):
        connection = MagicMock()
        cursor = connection.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.description = [("CASE_NUMBER",), ("REVIEW_CATEGORIES",)]
        cursor.fetchmany.return_value = [("123", ["Coding"])]
        with patch("database.connect_db", return_value=connection):
            self.assertEqual(fetch_records("postgres"), [
                {"case_number": "123", "review_categories": ["Coding"]}
            ])

    def test_row_limit_does_not_silently_truncate(self):
        connection = MagicMock()
        cursor = connection.__enter__.return_value.cursor.return_value.__enter__.return_value
        cursor.description = [("case_number",)]
        cursor.fetchmany.return_value = [("123",)] * 3
        with patch("database.connect_db", return_value=connection), patch("database.MAX_RECORDS", 2):
            with self.assertRaisesRegex(ValueError, "limit"):
                fetch_records("postgres")


if __name__ == "__main__":
    unittest.main()
