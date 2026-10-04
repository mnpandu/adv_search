"""Oracle connection settings, supplied through environment variables."""
import os
from pathlib import Path

from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError

load_dotenv(Path(__file__).with_name(".env"))

DEFAULT_DB = "oracle"

TABLE_DEFAULTS = {
    "saved_search_table": "saved_searches",
    "case_table": "case_header",
    "case_details_table": "case_details",
    "claim_table": "claim_details",
    "decision_table": "claim_decision",
    "provider_table": "provider_details",
    "focus_table": "focus_code_details",
}


def _setting(name, default=None):
    environment_value = os.getenv(name)
    if environment_value is not None:
        return environment_value
    try:
        import streamlit as st
        return st.secrets.get(name, default)
    except StreamlitSecretNotFoundError:
        return default


def get_settings(backend=None):
    selected_backend = (backend or DEFAULT_DB).lower()
    if selected_backend != "oracle":
        raise ValueError("Only Oracle is supported")

    settings = {
        "backend": "oracle",
        "dsn": _setting("ORACLE_DSN"),
        "user": _setting("ORACLE_USER"),
        "password": _setting("ORACLE_PASSWORD"),
        "schema": _setting("ORACLE_SCHEMA") or _setting("ORACLE_USER"),
    }
    settings.update({
        key: _setting("ORACLE_" + key.upper(), default)
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
