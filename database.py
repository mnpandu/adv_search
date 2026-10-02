"""Read PostgreSQL records for advanced search."""
import re
from pathlib import Path

from db_config import get_settings

ROOT = Path(__file__).resolve().parent
MAX_RECORDS = 10000


def build_query(settings):
    identifiers = {}
    for key in ("schema", "case_table", "case_details_table", "claim_table", "decision_table", "provider_table", "focus_table"):
        value = settings[key]
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
            raise ValueError(f"Invalid database identifier: {key}")
        identifiers[key] = value
    return (ROOT / f"search_{settings['backend']}.sql").read_text().format(**identifiers)


def connect_db(settings):
    import psycopg
    return psycopg.connect(
        host=settings["host"], port=settings["port"],
        dbname=settings["database"], user=settings["user"],
        password=settings["password"], connect_timeout=5,
    )


def fetch_records(backend=None):
    settings = get_settings(backend)
    query = build_query(settings)
    with connect_db(settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            fields = [column[0].lower() for column in cursor.description]
            rows = cursor.fetchmany(MAX_RECORDS + 1)
            if len(rows) > MAX_RECORDS:
                raise ValueError("Search exceeds the 10,000-row POC limit; database-side filtering is required.")
            return [dict(zip(fields, row)) for row in rows]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Check connection and search-table mapping (read only)")
    parser.add_argument("--db", choices=["postgres"])
    args = parser.parse_args()
    records = fetch_records(args.db)
    print(f"Connection and table query succeeded: {len(records)} rows")
