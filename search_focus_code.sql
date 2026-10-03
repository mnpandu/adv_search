SELECT
    f.focus_code_details_id AS f__focus_code_details_id,
    f.case_details_id AS f__case_details_id,
    f.focus_cd_desc AS f__focus_cd_desc,
    f.focus_cd_type AS f__focus_cd_type,
    f.modifier AS f__modifier,
    f.cart_cd AS f__cart_cd,
    f.cart_topic AS f__cart_topic,
    f.rec_clms_review AS f__rec_clms_review,
    f.smpl_clm_cnt AS f__smpl_clm_cnt,
    f.focus_code AS focus_code,
    f.status AS f__status,
    f.created_by AS f__created_by,
    f.created_dts AS f__created_dts,
    f.updated_by AS f__updated_by,
    f.updated_dts AS f__updated_dts
FROM {schema}.{table} f
