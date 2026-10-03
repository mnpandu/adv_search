# Advanced Search

## Run

Install dependencies and configure an Oracle account that can read the required tables:

```powershell
python -m pip install -r requirements.txt
$env:ORACLE_USER = '<oracle username>'
$env:ORACLE_PASSWORD = '<oracle password>'
$env:ORACLE_DSN = 'db-host:1521/service_name'
$env:ORACLE_SCHEMA = $env:ORACLE_USER
python -m streamlit run app.py
```

For a local Streamlit secrets file, copy `.streamlit/secrets.toml.example` to
`.streamlit/secrets.toml` and replace the placeholders. The real file is ignored by
Git. On the target environment, provide the same keys through Streamlit secrets or
environment variables; environment variables take precedence.

`ORACLE_SCHEMA` is optional when the table owner is the same as `ORACLE_USER`. The
tables must already exist and be readable by that account. This application only runs
`SELECT` queries; it does not create, seed, alter, or drop tables.

For local development, fill in the ignored `.env` file. `.env.example` lists the
required keys without credentials. For deployment, provide those same keys through
environment variables or Streamlit secrets; explicit environment variables override
`.env` values.

The environment settings are:

| Setting | Environment variable / Streamlit secret | Purpose |
| --- | --- | --- |
| Username | `ORACLE_USER` | Oracle login |
| Password | `ORACLE_PASSWORD` | Oracle login password |
| DSN | `ORACLE_DSN` | Easy Connect string or Oracle connect descriptor |
| Schema | `ORACLE_SCHEMA` | Table owner; defaults to `ORACLE_USER` |
| Case table | `ORACLE_CASE_TABLE` | Defaults to `case_header` |
| Case details table | `ORACLE_CASE_DETAILS_TABLE` | Defaults to `case_details` |
| Claim table | `ORACLE_CLAIM_TABLE` | Defaults to `claim_details` |
| Decision table | `ORACLE_DECISION_TABLE` | Defaults to `claim_decision` |
| Provider table | `ORACLE_PROVIDER_TABLE` | Defaults to `provider_details` |
| Focus table | `ORACLE_FOCUS_TABLE` | Defaults to `focus_code_details` |

## Search Configuration

Each category has its own JSON file in `search_fields/` and its own single-table SQL
file, such as `case_fields.json` with `search_case.sql`. The JSON `query` object maps
the category to its SQL file and Oracle table setting. Its `result_key` identifies the
category's field-result group. Edit a category file to add, remove, or rename fields
and change their operators. The `order` value controls category order. Field
`result_groups` controls whether that field appears in the result view; an empty list
keeps it selectable but hides it from results. Removing the field entry removes it
from both filters and results. Each field key must match an alias in its category's
SQL file. Restart the app to reload the files.

The app runs five independent queries for Case Fields, Claim Details, Provider,
Claim Decision, and Focus. Results are grouped into two top-level views: **Case
Details** combines Case Fields, Provider, and Focus data by case details ID; multiple
provider/focus values are aggregated to avoid duplicate case rows. **Claim Details**
combines Claims and Decisions by claim details ID, with one row per decision. Filters
apply only to their source query category. The separate Case Details table definition
remains in the catalog but is not queried or shown. Each query returns up to 10,000
rows and performs no DDL.

Text `In` filters accept comma-separated values, such as `222, 2111`. Quote a value
containing a comma, for example `"Clinic, Inc", Other`. Date fields support a rolling
`Within last (days)` range such as 90 days. Named saved searches are kept in the
active Streamlit session and are cleared when that session ends.

Search results appear in the **Case Details** and **Claim Details** tabs.
