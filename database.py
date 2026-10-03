"""Read Oracle records for advanced search."""
import re
from pathlib import Path

from db_config import get_settings
QUERY_FILES = {"Case Details": "search_case_details.sql", "Claim Details": "search_claim_details.sql"}

ROOT = Path(__file__).resolve().parent
MAX_RECORDS = 10000


def build_query(settings, group_name):
    identifiers = {key: value for key, value in settings.items()
                   if key == "schema" or key.endswith("_table")}
    for key, value in identifiers.items():
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
            raise ValueError(f"Invalid database identifier: {key}")
    return (ROOT / QUERY_FILES[group_name]).read_text(encoding="utf-8").strip().rstrip(";").format(**identifiers)


def describe_columns(description, group):
    columns = []
    seen = set()
    for column in description:
        label = column[0]
        if label in seen:
            raise ValueError(f'{group}: duplicate SELECT alias "{label}". Use unique aliases.')
        seen.add(label)
        type_name = str(column[1]).upper()
        kind = "date" if any(t in type_name for t in ("DATE", "TIMESTAMP")) else (
            "number" if any(t in type_name for t in ("NUMBER", "INT", "FLOAT", "DECIMAL", "DOUBLE")) else "text")
        columns.append((group + "::" + label, label, kind))
    return columns


def fetch_field_groups(backend=None):
    settings = get_settings(backend)
    groups = {}
    with connect_db(settings) as connection:
        with connection.cursor() as cursor:
            for group in QUERY_FILES:
                cursor.execute("SELECT * FROM (" + build_query(settings, group) + ") query_columns WHERE 1=0")
                groups[group] = describe_columns(cursor.description, group)
    return groups


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
    selected_groups = list(group_names or QUERY_FILES)
    unknown_groups = set(selected_groups) - set(QUERY_FILES)
    if unknown_groups:
        raise ValueError("Unknown query categories: " + ", ".join(sorted(unknown_groups)))
    records_by_group = {}
    with connect_db(settings) as connection:
        with connection.cursor() as cursor:
            for group_name in selected_groups:
                cursor.execute(build_query(settings, group_name))
                fields = [key for key, _, _ in describe_columns(cursor.description, group_name)]
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
