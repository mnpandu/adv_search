-- SELECT order and quoted aliases define result columns and available filters.
SELECT
    c.case_number AS "Case Number",
    c.lob AS "Lob",
    c.case_status AS "Case Status",
    c.case_substatus AS "Case Substatus",
    c.created_dts AS "Created Dts",
    c.assigned_to_name AS "Assigned To Name",
    c.closed_dts AS "Closed Dts",
    p.ptan AS "Provider Number (PTAN)",
    p.provider_name AS "Provider Name",
    f.focus_code AS "Focus Code"
FROM {schema}.{case_table} c
LEFT JOIN {schema}.{case_details_table} cd ON cd.case_details_id = c.case_details_id
LEFT JOIN {schema}.{provider_table} p ON p.case_details_id = c.case_details_id
LEFT JOIN {schema}.{focus_table} f ON f.case_details_id = c.case_details_id
