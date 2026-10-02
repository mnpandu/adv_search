"""Edit defaults here, or override them using environment variables."""
import os

DEFAULT_DB = "postgres"

PROFILES = {
    "postgres": {
        "host": "localhost", "port": "5432", "database": "postgres",
        "user": "postgres", "schema": "pic_master1",
        "case_table": "case_header", "case_details_table": "case_details", "claim_table": "claim_details",
        "decision_table": "claim_decision",
        "provider_table": "provider_details", "focus_table": "focus_code_details",
    },

}


def get_settings(backend=None):
    backend = (backend or os.getenv("DB_TYPE") or DEFAULT_DB).lower()
    if backend not in PROFILES:
        raise ValueError("Only postgres is supported")
    prefix = "PG"
    names = {"database": "DATABASE"}
    settings = {
        key: os.getenv(prefix + names.get(key, key.upper()), value)
        for key, value in PROFILES[backend].items()
    }
    settings["backend"] = backend
    settings["password"] = os.getenv(prefix + "PASSWORD")
    return settings
