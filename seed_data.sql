-- Fictional sample records; run once after creating the tables.
INSERT INTO pic_master1.case_details
(case_details_id, billing_ptan, rendering_ptan, state_cd, status, dept, created_by, created_dts)
VALUES (101,'222','222','NY','Active','Review','demo',CURRENT_TIMESTAMP),
(102,'2111','2111','NJ','Active','Review','demo',CURRENT_TIMESTAMP),
(103,'333','333','CA','Closed','Review','demo',CURRENT_TIMESTAMP);
INSERT INTO pic_master1.case_header (
    case_id, revision, case_details_id, lob, mac, is_act_ind, case_type_id, case_status, case_substatus, assigned_to, status, created_by, created_dts, updated_by, updated_dts, case_number, assigned_to_name, adr_ltr_sent_dt, original_due_dt, new_due_dt, bill_type, adr_ltr_rcvd_dt, closed_dts, rvsn_reason, assigned_dt, reference_case_number, informatics_case_type, ref_demand_bill, timeliness_dt, adjudication_process, ovrd_closed_dts, smpl_met_dt, language, adjudication_date
) VALUES
(1, 1, 101, 'Part B', 'MAC01', 'Y', 1, 'Closed', 'Review complete', 'demo1', 'Active', 'demo', TIMESTAMP '2026-09-01 09:00:00', 'demo', TIMESTAMP '2026-10-01 10:00:00', '5001001', 'Demo Reviewer 1', DATE '2026-09-02', DATE '2026-09-20', DATE '2026-09-25', '131', DATE '2026-09-10', TIMESTAMP '2026-10-01 10:00:00', 'Initial review', DATE '2026-09-01', 'REF-001', 'Review', 'DEMAND-001', DATE '2026-09-20', 'Manual', 'No', DATE '2026-09-15', 'English', TIMESTAMP '2026-10-01 09:30:00'),
(2, 1, 102, 'Part B', 'MAC01', 'Y', 1, 'Closed', 'Review complete', 'demo2', 'Active', 'demo', TIMESTAMP '2026-09-01 09:00:00', 'demo', TIMESTAMP '2026-10-01 10:00:00', '5001002', 'Demo Reviewer 2', DATE '2026-09-02', DATE '2026-09-20', DATE '2026-09-25', '131', DATE '2026-09-10', TIMESTAMP '2026-10-01 10:00:00', 'Initial review', DATE '2026-09-01', 'REF-002', 'Review', 'DEMAND-002', DATE '2026-09-20', 'Manual', 'No', DATE '2026-09-15', 'English', TIMESTAMP '2026-10-01 09:30:00'),
(3, 1, 103, 'Part B', 'MAC01', 'Y', 1, 'Closed', 'Review complete', 'demo3', 'Active', 'demo', TIMESTAMP '2026-09-01 09:00:00', 'demo', TIMESTAMP '2026-10-01 10:00:00', '5001003', 'Demo Reviewer 3', DATE '2026-09-02', DATE '2026-09-20', DATE '2026-09-25', '131', DATE '2026-09-10', TIMESTAMP '2026-10-01 10:00:00', 'Initial review', DATE '2026-09-01', 'REF-003', 'Review', 'DEMAND-003', DATE '2026-09-20', 'Manual', 'No', DATE '2026-09-15', 'English', TIMESTAMP '2026-10-01 09:30:00');
INSERT INTO pic_master1.provider_details
(provider_details_id,ptan,provider_name,case_details_id,state_cd,status,created_by,created_dts)
VALUES (201,'222','Demo North Clinic',101,'NY','Active','demo',CURRENT_TIMESTAMP),
(202,'2111','Demo South Clinic',102,'NJ','Active','demo',CURRENT_TIMESTAMP),
(203,'333','Demo West Clinic',103,'CA','Active','demo',CURRENT_TIMESTAMP);
INSERT INTO pic_master1.focus_code_details
(focus_code_details_id,case_details_id,focus_code,focus_cd_desc,focus_cd_type,status,created_by,created_dts)
VALUES (301,101,'99213','Sample office visit','HCPCS','Active','demo',CURRENT_TIMESTAMP),
(302,102,'99214','Sample review visit','HCPCS','Active','demo',CURRENT_TIMESTAMP),
(303,103,'99215','Sample extended visit','HCPCS','Active','demo',CURRENT_TIMESTAMP);
INSERT INTO pic_master1.claim_details
(claim_details_id,case_id,claim_number,bene_first_name,bene_last_name,mbi,ptan,status,hcpc_code,pre_mr_actual_reimb_amount,post_mr_actual_reimb_amount,created_by,created_dts)
VALUES (401,1,'CLM-1001','Sample','One','DEMO-001','222','Finalized','99213',100,100,'demo',CURRENT_TIMESTAMP),
(402,2,'CLM-1002','Sample','Two','DEMO-002','2111','Pending','99214',200,150,'demo',CURRENT_TIMESTAMP),
(403,3,'CLM-1003','Sample','Three','DEMO-003','333','Finalized','99215',300,250,'demo',CURRENT_TIMESTAMP);
INSERT INTO pic_master1.claim_decision
(claim_decision_id,claim_details_id,decision_type,decision_date,status,qc_review,qc_review_comments,qc_review_dts,created_by,created_dts)
VALUES (501,401,'Approved',CURRENT_DATE,'Completed','Agree','Sample completed review',CURRENT_TIMESTAMP,'demo',CURRENT_TIMESTAMP),
(502,402,'Pending',CURRENT_DATE,'In Progress','Action Required','Sample correction request',CURRENT_TIMESTAMP,'demo',CURRENT_TIMESTAMP),
(503,403,'Partial',CURRENT_DATE,'Completed','Agree','Sample partial approval',CURRENT_TIMESTAMP,'demo',CURRENT_TIMESTAMP);
