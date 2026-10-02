--
-- PostgreSQL database dump
--

\restrict di82U6hv9Jffv9l0Y1Dchm0ZVn5asDsWqL729nz3OYoZlXalxMMb5eB3x4r57oQ

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: case_header; Type: TABLE; Schema: pic_master1; Owner: postgres
--

CREATE TABLE pic_master1.case_header (
    case_id numeric(38,0) NOT NULL,
    revision numeric(10,0) NOT NULL,
    case_details_id numeric(38,0) NOT NULL,
    lob character varying(10),
    mac character varying(10),
    is_act_ind character(1),
    case_type_id numeric NOT NULL,
    case_status character varying(100),
    case_substatus character varying(2000),
    assigned_to character varying(100),
    status character varying(100),
    created_by character varying(100),
    created_dts timestamp(6) without time zone,
    updated_by character varying(100),
    updated_dts timestamp(6) without time zone,
    case_number character varying(50),
    assigned_to_name character varying(100),
    adr_ltr_sent_dt timestamp(0) without time zone,
    original_due_dt timestamp(0) without time zone,
    new_due_dt timestamp(0) without time zone,
    bill_type character varying(50),
    adr_ltr_rcvd_dt timestamp(0) without time zone,
    closed_dts timestamp(6) without time zone,
    rvsn_reason character varying(50),
    assigned_dt timestamp(0) without time zone,
    reference_case_number character varying(100),
    informatics_case_type character varying(10),
    ref_demand_bill character varying(50),
    timeliness_dt timestamp(0) without time zone,
    adjudication_process character varying(20),
    ovrd_closed_dts character varying(3),
    smpl_met_dt timestamp(0) without time zone,
    language character varying(45),
    adjudication_date timestamp(6) without time zone
);


ALTER TABLE pic_master1.case_header OWNER TO postgres;

--
-- Data for Name: case_header; Type: TABLE DATA; Schema: pic_master1; Owner: postgres
--

COPY pic_master1.case_header (case_id, revision, case_details_id, lob, mac, is_act_ind, case_type_id, case_status, case_substatus, assigned_to, status, created_by, created_dts, updated_by, updated_dts, case_number, assigned_to_name, adr_ltr_sent_dt, original_due_dt, new_due_dt, bill_type, adr_ltr_rcvd_dt, closed_dts, rvsn_reason, assigned_dt, reference_case_number, informatics_case_type, ref_demand_bill, timeliness_dt, adjudication_process, ovrd_closed_dts, smpl_met_dt, language, adjudication_date) FROM stdin;
1	1	101	Part B	\N	Y	1	Open	\N	\N	\N	demo	2026-10-01 19:45:38.082551	\N	\N	5001001	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
2	1	102	Part B	\N	Y	1	In Review	\N	\N	\N	demo	2026-10-01 19:45:38.082551	\N	\N	5001002	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
3	1	103	Part A	\N	Y	1	Closed	\N	\N	\N	demo	2026-10-01 19:45:38.082551	\N	\N	5001003	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N	\N
\.


--
-- Name: case_header_case_details_id_idx; Type: INDEX; Schema: pic_master1; Owner: postgres
--

CREATE INDEX case_header_case_details_id_idx ON pic_master1.case_header USING btree (case_details_id);


--
-- Name: case_header_case_id_idx; Type: INDEX; Schema: pic_master1; Owner: postgres
--

CREATE INDEX case_header_case_id_idx ON pic_master1.case_header USING btree (case_id);


--
-- PostgreSQL database dump complete
--

\unrestrict di82U6hv9Jffv9l0Y1Dchm0ZVn5asDsWqL729nz3OYoZlXalxMMb5eB3x4r57oQ

