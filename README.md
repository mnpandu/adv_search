# QC tasks

## Advanced Search POC

Run the Gradio search builder with:

```powershell
python -m pip install -r requirements.txt
python app.py
```

Select case, claim, or decision fields to add filter rows. Each row has a field-specific
operator and value. Search supports combining filters with AND or OR and now reads
from PostgreSQL. Empty databases return no results; there is no sample fallback.
Name and save complete searches, including fields, operators, values, and AND/OR mode.
Saved searches stay in the current browser and can be loaded or run separately. Date
filters support a rolling `Within last (days)` range, such as 90 days.

`search_fields.json` is the field catalog. Each entry defines its group, result key,
display label, data type, and allowed operators. Edit this file to rename fields or
change their operators; restart the app to reload it. New field keys must match aliases
returned by `search_postgres.sql`; add a SQL mapping there if the alias is not already
selected. Supported types are `text`, `number`, and `date`, with operators validated
by the JSON loader in `search_fields.py`.

`schema.sql` defines the separate `pic_master1` PostgreSQL schema. The six tables use typed relational columns transcribed from the supplied screenshots. The app does not run DDL automatically.

## PostgreSQL configuration

For multiple text values, select **In** and enter `222, 2111` (no SQL parentheses
or single quotes). Values match exactly, ignoring case and whitespace around
each entered value. Use double quotes around a value containing a comma:
`"Clinic, Inc", Other`. Empty entries are ignored; an empty list matches nothing.
For list-valued fields, any individual value can match. Combine the filter with
other fields using the existing AND/OR selector. Filtering runs in Python.

Edit defaults in `db_config.py`, or use environment variables. Selection priority:
`--db` > `DB_TYPE` environment variable > `DEFAULT_DB` (postgres).

```powershell
$env:PGPASSWORD = '<your PostgreSQL password>'
python app.py
```

| Setting | Default | Environment variable |
| --- | --- | --- |
| Host | localhost | PGHOST |
| Port | 5432 | PGPORT |
| Database | postgres | PGDATABASE |
| User | postgres | PGUSER |
| Password | Use environment or pgpass | PGPASSWORD |
| Schema | pic_master1 | PGSCHEMA |
| Case table | case_header | PGCASE_TABLE |
| Claim table | claim_details | PGCLAIM_TABLE |
| Decision table | claim_decision | PGDECISION_TABLE |

`search_postgres.sql` maps relational columns to UI fields. Only unquoted schema/table
identifiers are supported. Passwords are not stored in code.

The query returns one row per decision, retaining claims without decisions and
cases without claims. This POC refuses more than 10,000 source rows rather than
silently returning partial results; larger datasets need database-side filtering
and pagination.

Check the connection and query without opening the UI:

```powershell
python database.py
```

Run the focused search tests with:

```powershell
python -m unittest -v
```

## Final tables and sample data

The tables are case_header, case_details, provider_details, focus_code_details,
claim_details, and claim_decision. Each has three fictional sample rows.
The screenshots specify columns and NOT NULL flags, not primary/foreign keys;
no such constraints were inferred. Numeric precision and string lengths are
preserved. case_header uses DATE for the DATE fields shown in its reference image. Other tables retain their existing TIMESTAMP(0) mapping.

`schema.sql` creates the tables; `seed_data.sql` inserts sample data.
`replace_tables.sql` explicitly drops the old/new table set. To intentionally
replace all these tables and their data atomically:

```powershell
psql -X -h localhost -U postgres -d postgres -v ON_ERROR_STOP=1 --single-transaction -f replace_tables.sql -f schema.sql -f seed_data.sql
```

The previous schema/data backup is `pic_master1_before_replacement.sql`.
The search joins case ID and case details ID with claim details ID for decisions.
Multiple revisions, providers, focus codes, or decisions can produce multiple
result rows per claim. Decision Created By reports the decision creator, not an
inferred reviewer. Provider Number uses provider_details.ptan.

`recreate_case_header.sql` recreates only case_header and inserts three complete sample rows in one transaction. Its prior backup is `case_header_before_recreation.sql`.
