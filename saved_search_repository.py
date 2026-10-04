"""Committed Oracle storage for the shared saved-search catalog."""
import hashlib
import json
import re

from database import connect_db
from db_config import get_settings


def _table(settings):
    schema = settings["schema"]
    table = settings.get("saved_search_table", "saved_searches")
    if any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) for name in (schema, table)):
        raise ValueError("Invalid saved-search schema or table name")
    return f"{schema}.{table}"


def criteria_hash(search):
    criteria = sorted(search["criteria"], key=lambda item: json.dumps(item, sort_keys=True))
    canonical = json.dumps({"match_mode": search["match_mode"], "criteria": criteria},
                           sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_saved_searches():
    settings = get_settings()
    with connect_db(settings) as connection:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT search_name, match_mode, criteria_json FROM {_table(settings)} ORDER BY saved_search_id")
            searches = []
            for name, mode, criteria in cursor:
                if hasattr(criteria, "read"):
                    criteria = criteria.read()
                if isinstance(criteria, (str, bytes, bytearray)):
                    criteria = json.loads(criteria)
                searches.append({"name": name, "match_mode": mode, "criteria": criteria})
            return searches


def insert_saved_search(search):
    import oracledb
    settings = get_settings()
    with connect_db(settings) as connection:
        try:
            with connection.cursor() as cursor:
                cursor.setinputsizes(p_criteria=oracledb.DB_TYPE_CLOB)
                cursor.execute(
                    f"INSERT INTO {_table(settings)} (search_name, match_mode, criteria_json, criteria_hash) "
                    "VALUES (:p_name, :p_match_mode, :p_criteria, :p_digest)",
                    p_name=search["name"], p_match_mode=search["match_mode"],
                    p_criteria=json.dumps(search["criteria"], ensure_ascii=False), p_digest=criteria_hash(search),
                )
            connection.commit()
        except Exception as exc:
            connection.rollback()
            if getattr(exc.args[0] if exc.args else None, "code", None) == 1:
                raise ValueError("This search name or these filters are already saved.") from exc
            raise


def remove_saved_search(name):
    settings = get_settings()
    with connect_db(settings) as connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {_table(settings)} WHERE search_name = :name", name=name)
            connection.commit()
        except Exception:
            connection.rollback()
            raise
