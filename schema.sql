-- Column definitions transcribed from the six supplied screenshots.

-- NUMBER(p) -> NUMERIC(p,0); VARCHAR2(n) -> VARCHAR(n).

-- case_header uses DATE for pictured DATE fields; other tables retain TIMESTAMP(0).

-- No primary/foreign keys inferred from DESC output.

CREATE SCHEMA IF NOT EXISTS pic_master1;

CREATE TABLE pic_master1.case_details (
    case_details_id numeric(38,0) NOT NULL,
    first_rcrd_rcvd varchar(20),
    last_clm_reviewed varchar(20),
    closed_date timestamp(0),
    edit_impl_dt timestamp(0),
    edit_term_dt timestamp(0),
    smpl_clm_cnt numeric(10,0),
    review_clm_cnt numeric(10,0),
    review_result_code varchar(200),
    close_actn_code varchar(200),
    status varchar(100),
    created_by varchar(100),
    created_dts timestamp(6),
    updated_by varchar(100),
    updated_dts timestamp(6),
    dept varchar(50),
    billing_ptan varchar(20),
    rendering_ptan varchar(20),
    state_cd varchar(20),
    edit_number varchar(10),
    contract_id varchar(20),
    case_file_comment varchar(2000),
    mip_cntrl_nbr varchar(100),
    adhoc_name varchar(500),
    cost_center varchar(20),
    case_file_status varchar(20),
    mip_mtg_date timestamp(0),
    mip_priority_score varchar(20),
    npi varchar(20),
    activity_code varchar(20),
    referral_dept varchar(200),
    referral_desc varchar(4000)
);

CREATE TABLE pic_master1.case_header (
    case_id numeric(38,0) NOT NULL,
    revision numeric(10,0) NOT NULL,
    case_details_id numeric(38,0) NOT NULL,
    lob varchar(10),
    mac varchar(10),
    is_act_ind char(1),
    case_type_id numeric NOT NULL,
    case_status varchar(100),
    case_substatus varchar(2000),
    assigned_to varchar(100),
    status varchar(100),
    created_by varchar(100),
    created_dts timestamp(6),
    updated_by varchar(100),
    updated_dts timestamp(6),
    case_number varchar(50),
    assigned_to_name varchar(100),
    adr_ltr_sent_dt date,
    original_due_dt date,
    new_due_dt date,
    bill_type varchar(50),
    adr_ltr_rcvd_dt date,
    closed_dts timestamp(6),
    rvsn_reason varchar(50),
    assigned_dt date,
    reference_case_number varchar(100),
    informatics_case_type varchar(10),
    ref_demand_bill varchar(50),
    timeliness_dt date,
    adjudication_process varchar(20),
    ovrd_closed_dts varchar(3),
    smpl_met_dt date,
    language varchar(45),
    adjudication_date timestamp(6)
);

CREATE TABLE pic_master1.provider_details (
    provider_details_id numeric(38,0) NOT NULL,
    ptan varchar(20) NOT NULL,
    npi varchar(50),
    lob varchar(10),
    jurisdiction varchar(2),
    contract_id varchar(20),
    state_cd varchar(10),
    provider_type varchar(10),
    status varchar(100),
    created_by varchar(100),
    created_dts timestamp(6),
    updated_by varchar(100),
    updated_dts timestamp(6),
    provider_name varchar(200),
    specialty varchar(100),
    case_details_id numeric
);

CREATE TABLE pic_master1.focus_code_details (
    focus_code_details_id numeric(38,0) NOT NULL,
    case_details_id numeric(28,0) NOT NULL,
    focus_cd_desc varchar(4000),
    focus_cd_type varchar(200),
    modifier varchar(100),
    cart_cd varchar(100),
    cart_topic varchar(100),
    rec_clms_review varchar(4000),
    smpl_clm_cnt numeric(10,0),
    focus_code varchar(200),
    status varchar(20),
    created_by varchar(100),
    created_dts timestamp(6),
    updated_by varchar(100),
    updated_dts timestamp(6)
);

CREATE TABLE pic_master1.claim_details (
    claim_details_id numeric(38,0) NOT NULL,
    bene_first_name varchar(100),
    bene_last_name varchar(100),
    bene_middle_name varchar(100),
    bene_dob timestamp(0),
    mbi varchar(50),
    claim_number varchar(50),
    lob varchar(20),
    hcpc_code varchar(20),
    dos_from timestamp(0),
    dos_to timestamp(0),
    status varchar(100),
    created_by varchar(100),
    created_dts timestamp(6),
    updated_by varchar(100),
    updated_dts timestamp(6),
    case_id numeric(38,0),
    ptan varchar(20),
    npi varchar(20),
    hic varchar(50),
    appeals_case_re_open varchar(2),
    post_mr_actual_reimb_amount numeric(20,2),
    pre_mr_actual_reimb_amount numeric(20,2),
    error_indicator varchar(2),
    mcs_or_fiss_update varchar(50),
    over_payment numeric(20,2),
    paid_dt timestamp(0),
    ract_dt timestamp(0),
    mcs_or_fiss_err_msg varchar(4000),
    mcs_or_fiss_update_dt timestamp(6),
    type_of_bill varchar(1000),
    adjustment_claim_number varchar(50),
    patient_status numeric,
    place_of_service_zip_code varchar(10),
    claim_refresh varchar(20),
    claim_refresh_dt timestamp(0),
    place_of_service_state_code varchar(20),
    mcs_snap_claims_ovr_txn_number numeric,
    mcs_snap_claims_ovr_txn_status varchar(50)
);

CREATE TABLE pic_master1.claim_decision (
    claim_decision_id numeric(38,0) NOT NULL,
    claim_details_id numeric(10,0) NOT NULL,
    decision_type varchar(50),
    decision_date timestamp(0),
    associated_dcn varchar(50),
    denial_reason varchar(50),
    decision_remarks varchar(4000),
    status varchar(100),
    created_by varchar(100),
    created_dts timestamp(6),
    updated_by varchar(100),
    updated_dts timestamp(6),
    qc_review varchar(200),
    qc_review_comments varchar(4000),
    qc_review_dts timestamp(6),
    denial_remarks varchar(4000),
    demand_bill varchar(50),
    generic_reason_code varchar(10),
    decision_pretext varchar(2000),
    decision_comments varchar(2000)
);

CREATE INDEX case_header_case_id_idx ON pic_master1.case_header (case_id);

CREATE INDEX case_header_case_details_id_idx ON pic_master1.case_header (case_details_id);

CREATE INDEX claim_details_case_id_idx ON pic_master1.claim_details (case_id);

CREATE INDEX claim_details_claim_details_id_idx ON pic_master1.claim_details (claim_details_id);

CREATE INDEX claim_decision_claim_details_id_idx ON pic_master1.claim_decision (claim_details_id);

CREATE INDEX provider_details_case_details_id_idx ON pic_master1.provider_details (case_details_id);

CREATE INDEX focus_code_details_case_details_id_idx ON pic_master1.focus_code_details (case_details_id);
