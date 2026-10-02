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

Each category has its own JSON file in `search_fields/` (for example,
`case_fields.json` or `claim_details.json`). Edit that category file to add, remove, or
rename fields and change their operators. The `order` value controls category order.
Restart the app to reload the files. Every field key must match a column alias in
`search_oracle.sql`. Result grid columns are configured separately in `app.py` using
`CASE_RESULT_FIELDS` and `CLAIM_RESULT_FIELDS`. The query joins the configured Oracle
tables and returns up to 10,000 rows for filtering in the application. It does not
perform DDL.

Text `In` filters accept comma-separated values, such as `222, 2111`. Quote a value
containing a comma, for example `"Clinic, Inc", Other`. Date fields support a rolling
`Within last (days)` range such as 90 days. Named saved searches are kept in the
active Streamlit session and are cleared when that session ends.

Search results are shown in separate **Cases** and **Claims** tabs. Cases are listed
once per revision; claims are listed once per decision, so a claim with multiple
decisions can appear more than once.
