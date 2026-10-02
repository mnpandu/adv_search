-- Replaces only case_header, including its data. No CASCADE.
BEGIN;
DROP TABLE IF EXISTS pic_master1.case_header;
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
CREATE INDEX case_header_case_id_idx ON pic_master1.case_header (case_id);
CREATE INDEX case_header_case_details_id_idx ON pic_master1.case_header (case_details_id);
INSERT INTO pic_master1.case_header (
    case_id, revision, case_details_id, lob, mac, is_act_ind, case_type_id, case_status, case_substatus, assigned_to, status, created_by, created_dts, updated_by, updated_dts, case_number, assigned_to_name, adr_ltr_sent_dt, original_due_dt, new_due_dt, bill_type, adr_ltr_rcvd_dt, closed_dts, rvsn_reason, assigned_dt, reference_case_number, informatics_case_type, ref_demand_bill, timeliness_dt, adjudication_process, ovrd_closed_dts, smpl_met_dt, language, adjudication_date
) VALUES
(1, 1, 101, 'Part B', 'MAC01', 'Y', 1, 'Closed', 'Review complete', 'demo1', 'Active', 'demo', TIMESTAMP '2026-09-01 09:00:00', 'demo', TIMESTAMP '2026-10-01 10:00:00', '5001001', 'Demo Reviewer 1', DATE '2026-09-02', DATE '2026-09-20', DATE '2026-09-25', '131', DATE '2026-09-10', TIMESTAMP '2026-10-01 10:00:00', 'Initial review', DATE '2026-09-01', 'REF-001', 'Review', 'DEMAND-001', DATE '2026-09-20', 'Manual', 'No', DATE '2026-09-15', 'English', TIMESTAMP '2026-10-01 09:30:00'),
(2, 1, 102, 'Part B', 'MAC01', 'Y', 1, 'Closed', 'Review complete', 'demo2', 'Active', 'demo', TIMESTAMP '2026-09-01 09:00:00', 'demo', TIMESTAMP '2026-10-01 10:00:00', '5001002', 'Demo Reviewer 2', DATE '2026-09-02', DATE '2026-09-20', DATE '2026-09-25', '131', DATE '2026-09-10', TIMESTAMP '2026-10-01 10:00:00', 'Initial review', DATE '2026-09-01', 'REF-002', 'Review', 'DEMAND-002', DATE '2026-09-20', 'Manual', 'No', DATE '2026-09-15', 'English', TIMESTAMP '2026-10-01 09:30:00'),
(3, 1, 103, 'Part B', 'MAC01', 'Y', 1, 'Closed', 'Review complete', 'demo3', 'Active', 'demo', TIMESTAMP '2026-09-01 09:00:00', 'demo', TIMESTAMP '2026-10-01 10:00:00', '5001003', 'Demo Reviewer 3', DATE '2026-09-02', DATE '2026-09-20', DATE '2026-09-25', '131', DATE '2026-09-10', TIMESTAMP '2026-10-01 10:00:00', 'Initial review', DATE '2026-09-01', 'REF-003', 'Review', 'DEMAND-003', DATE '2026-09-20', 'Manual', 'No', DATE '2026-09-15', 'English', TIMESTAMP '2026-10-01 09:30:00');
COMMIT;
