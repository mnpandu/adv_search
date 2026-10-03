# Advanced Search

Run `streamlit run app.py` after installing requirements and configuring the existing Oracle connection in `.env`.

Edit only these two search queries:
- `search_case_details.sql`: Case Details filters and results.
- `search_claim_details.sql`: Claim Details filters and results.

SELECT expressions define columns from left to right. Use unique quoted aliases for readable names:

```sql
SELECT c.case_number AS "Case Number", c.case_status AS "Case Status"
FROM {schema}.{case_table} c
```

Add/remove a SELECT expression to add/remove a field and result column. Change its alias to rename it. Reorder SELECT expressions to reorder columns. No JSON, seq, or ignore settings are needed. Database metadata supplies field types, even for empty results. Refresh the app after SQL edits. Renaming fields may invalidate saved session searches.

Each query returns its own results; filters apply to the corresponding query independently. Joins may produce multiple rows per case/claim. Adjust joins in SQL to control the row granularity. No Python aggregation is applied. The app filters fetched records in Python and refuses over 10,000 source rows per query.

The query files are trusted local SQL. The app never runs schema creation or table deletion.
