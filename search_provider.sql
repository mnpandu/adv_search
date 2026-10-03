SELECT
    p.provider_details_id AS p__provider_details_id,
    p.ptan AS provider_number,
    p.npi AS p__npi,
    p.lob AS p__lob,
    p.jurisdiction AS p__jurisdiction,
    p.contract_id AS p__contract_id,
    p.state_cd AS p__state_cd,
    p.provider_type AS p__provider_type,
    p.status AS p__status,
    p.created_by AS p__created_by,
    p.created_dts AS p__created_dts,
    p.updated_by AS p__updated_by,
    p.updated_dts AS p__updated_dts,
    p.provider_name AS provider_name,
    p.specialty AS p__specialty,
    p.case_details_id AS p__case_details_id
FROM {schema}.{table} p
