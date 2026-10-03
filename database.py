"""Read Oracle records for advanced search."""
import re
from pathlib import Path

from db_config import get_settings
from search_fields import FIELD_GROUP_QUERIES

ROOT = Path(__file__).resolve().parent
MAX_RECORDS = 10000


def build_query(settings, group_name):
    query_config = FIELD_GROUP_QUERIES[group_name]
    identifiers = {
        "schema": settings["schema"],
        "table": settings[query_config["table_setting"]],
    }
    for key, value in identifiers.items():
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
            raise ValueError(f"Invalid database identifier: {key}")
    query_path = ROOT / query_config["file"]
    return query_path.read_text(encoding="utf-8").format(**identifiers)


def connect_db(settings):
    import oracledb
    return oracledb.connect(
        dsn=settings["dsn"],
        user=settings["user"],
        password=settings["password"],
        tcp_connect_timeout=5,
    )


def fetch_records_by_group(backend=None, group_names=None):
    settings = get_settings(backend)
    selected_groups = list(group_names or FIELD_GROUP_QUERIES)
    unknown_groups = set(selected_groups) - set(FIELD_GROUP_QUERIES)
    if unknown_groups:
        raise ValueError("Unknown query categories: " + ", ".join(sorted(unknown_groups)))
    records_by_group = {}
    with connect_db(settings) as connection:
        with connection.cursor() as cursor:
            for group_name in selected_groups:
                cursor.execute(build_query(settings, group_name))
                fields = [column[0].lower() for column in cursor.description]
                rows = cursor.fetchmany(MAX_RECORDS + 1)
                if len(rows) > MAX_RECORDS:
                    raise ValueError(
                        f"{group_name} exceeds the 10,000-row POC limit; database-side filtering is required."
                    )
                records_by_group[group_name] = [dict(zip(fields, row)) for row in rows]
    return records_by_group


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Check Oracle connection and search query (read only)")
    parser.add_argument("--db", choices=["oracle"], default="oracle")
    args = parser.parse_args()
    records = fetch_records_by_group(args.db)
    counts = ", ".join(f"{group}: {len(rows)}" for group, rows in records.items())
    print(f"Connection and separate table queries succeeded ({counts})")
