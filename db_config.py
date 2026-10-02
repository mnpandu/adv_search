"""Oracle connection settings, supplied through environment variables."""
import os

DEFAULT_DB = "oracle"

TABLE_DEFAULTS = {
    "case_table": "case_header",
    "case_details_table": "case_details",
    "claim_table": "claim_details",
    "decision_table": "claim_decision",
    "provider_table": "provider_details",
    "focus_table": "focus_code_details",
}


def get_settings(backend=None):
    selected_backend = (backend or DEFAULT_DB).lower()
    if selected_backend != "oracle":
        raise ValueError("Only Oracle is supported")

    settings = {
        "backend": "oracle",
        "dsn": os.getenv("ORACLE_DSN"),
        "user": os.getenv("ORACLE_USER"),
        "password": os.getenv("ORACLE_PASSWORD"),
        "schema": os.getenv("ORACLE_SCHEMA") or os.getenv("ORACLE_USER"),
    }
    settings.update({
        key: os.getenv("ORACLE_" + key.upper(), default)
        for key, default in TABLE_DEFAULTS.items()
    })

    missing = [key for key in ("dsn", "user", "password") if not settings[key]]
    if missing:
        required = {"dsn": "ORACLE_DSN", "user": "ORACLE_USER", "password": "ORACLE_PASSWORD"}
        raise ValueError("Set the Oracle connection environment variables: " + ", ".join(
            required[key] for key in missing
        ))
    if not settings["schema"]:
        raise ValueError("Set ORACLE_SCHEMA or ORACLE_USER to identify the table owner")
    return settings
