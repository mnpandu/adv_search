-- Destructive replacement, run together with schema.sql and seed_data.sql in one transaction.
-- No CASCADE: dependencies outside this set cause rollback rather than being removed.
DROP TABLE IF EXISTS pic_master1.claim_decision_details, pic_master1.claim_decision,
    pic_master1.claim_details, pic_master1.provider_details, pic_master1.focus_code_details,
    pic_master1.case_header, pic_master1.case_details;
