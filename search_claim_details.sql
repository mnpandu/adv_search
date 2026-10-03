-- SELECT order and quoted aliases define result columns and available filters.
SELECT
    cl.claim_number AS "Claim Number",
    c.case_number AS "Case Number",
    cl.mbi AS "Mbi",
    cl.over_payment AS "Over Payment",
    d.decision_type AS "Decision Type",
    d.status AS "Status",
    d.created_by AS "Created By",
    d.qc_review AS "Qc Review",
    d.qc_review_comments AS "Qc Review Comments",
    d.qc_review_dts AS "Qc Review Dts"
FROM {schema}.{claim_table} cl
INNER JOIN {schema}.{case_table} c ON c.case_id = cl.case_id
LEFT JOIN {schema}.{decision_table} d ON d.claim_details_id = cl.claim_details_id
