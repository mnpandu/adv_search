-- Run in Oracle SQL Developer as the intended table owner (Oracle 12.2+).
-- Creates a shared saved-search catalog; no existing tables are changed.
CREATE TABLE saved_searches (
    saved_search_id NUMBER GENERATED ALWAYS AS IDENTITY,
    search_name VARCHAR2(240 CHAR) NOT NULL,
    match_mode VARCHAR2(20 CHAR) NOT NULL,
    criteria_json CLOB NOT NULL,
    criteria_hash VARCHAR2(64 CHAR) NOT NULL,
    created_by VARCHAR2(128 CHAR) DEFAULT USER NOT NULL,
    created_dts TIMESTAMP(6) DEFAULT SYSTIMESTAMP NOT NULL,
    updated_dts TIMESTAMP(6) DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT saved_searches_pk PRIMARY KEY (saved_search_id),
    CONSTRAINT saved_searches_name_uq UNIQUE (search_name),
    CONSTRAINT saved_searches_hash_uq UNIQUE (criteria_hash),
    CONSTRAINT saved_searches_mode_ck CHECK (
        match_mode IN ('Match all (AND)', 'Match any (OR)')
    ),
    CONSTRAINT saved_searches_json_ck CHECK (criteria_json IS JSON)
);

-- Application contract:
-- search_name: normalized uppercase name with underscores.
-- criteria_json: JSON array of {field, operator, value} filter objects.
-- criteria_hash: SHA-256 hex digest of canonical match_mode + sorted criteria;
--                computed by the app to prevent duplicate filters under new names.
-- updated_dts: must be set by the app on UPDATE (default applies only on INSERT).
-- created_by records the database login, not an authenticated application user.

SELECT table_name FROM user_tables WHERE table_name = 'SAVED_SEARCHES';
