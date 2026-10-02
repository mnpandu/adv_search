--
-- PostgreSQL database dump
--

\restrict lRnQDKdDcdx37T3rvGaNA34czCeve9IBcgeDTIOQFrYQ6esa4sWtDrFeMLS2h7j

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

--
-- Name: pic_master1; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA pic_master1;


ALTER SCHEMA pic_master1 OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: case_header; Type: TABLE; Schema: pic_master1; Owner: postgres
--

CREATE TABLE pic_master1.case_header (
    case_id numeric(10,0) NOT NULL,
    case_data jsonb DEFAULT '{}'::jsonb NOT NULL,
    created_dts timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_dts timestamp with time zone
);


ALTER TABLE pic_master1.case_header OWNER TO postgres;

--
-- Name: claim_decision_details; Type: TABLE; Schema: pic_master1; Owner: postgres
--

CREATE TABLE pic_master1.claim_decision_details (
    decision_id bigint NOT NULL,
    case_id numeric(10,0) NOT NULL,
    claim_number text NOT NULL,
    task_id bigint,
    qc_review_status text,
    qc_review text,
    qc_review_comment text,
    review_categories jsonb DEFAULT '[]'::jsonb NOT NULL,
    points numeric(8,2),
    reviewed_by text,
    reviewed_dts timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    decision_data jsonb DEFAULT '{}'::jsonb NOT NULL,
    CONSTRAINT claim_decision_details_review_categories_check CHECK ((jsonb_typeof(review_categories) = 'array'::text))
);


ALTER TABLE pic_master1.claim_decision_details OWNER TO postgres;

--
-- Name: claim_decision_details_decision_id_seq; Type: SEQUENCE; Schema: pic_master1; Owner: postgres
--

ALTER TABLE pic_master1.claim_decision_details ALTER COLUMN decision_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME pic_master1.claim_decision_details_decision_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: claim_details; Type: TABLE; Schema: pic_master1; Owner: postgres
--

CREATE TABLE pic_master1.claim_details (
    case_id numeric(10,0) NOT NULL,
    claim_number text NOT NULL,
    claim_data jsonb NOT NULL,
    qc_status text,
    updated_dts timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE pic_master1.claim_details OWNER TO postgres;

--
-- Data for Name: case_header; Type: TABLE DATA; Schema: pic_master1; Owner: postgres
--

COPY pic_master1.case_header (case_id, case_data, created_dts, updated_dts) FROM stdin;
\.


--
-- Data for Name: claim_decision_details; Type: TABLE DATA; Schema: pic_master1; Owner: postgres
--

COPY pic_master1.claim_decision_details (decision_id, case_id, claim_number, task_id, qc_review_status, qc_review, qc_review_comment, review_categories, points, reviewed_by, reviewed_dts, decision_data) FROM stdin;
\.


--
-- Data for Name: claim_details; Type: TABLE DATA; Schema: pic_master1; Owner: postgres
--

COPY pic_master1.claim_details (case_id, claim_number, claim_data, qc_status, updated_dts) FROM stdin;
\.


--
-- Name: claim_decision_details_decision_id_seq; Type: SEQUENCE SET; Schema: pic_master1; Owner: postgres
--

SELECT pg_catalog.setval('pic_master1.claim_decision_details_decision_id_seq', 1, false);


--
-- Name: case_header case_header_pkey; Type: CONSTRAINT; Schema: pic_master1; Owner: postgres
--

ALTER TABLE ONLY pic_master1.case_header
    ADD CONSTRAINT case_header_pkey PRIMARY KEY (case_id);


--
-- Name: claim_decision_details claim_decision_details_pkey; Type: CONSTRAINT; Schema: pic_master1; Owner: postgres
--

ALTER TABLE ONLY pic_master1.claim_decision_details
    ADD CONSTRAINT claim_decision_details_pkey PRIMARY KEY (decision_id);


--
-- Name: claim_details claim_details_pkey; Type: CONSTRAINT; Schema: pic_master1; Owner: postgres
--

ALTER TABLE ONLY pic_master1.claim_details
    ADD CONSTRAINT claim_details_pkey PRIMARY KEY (case_id, claim_number);


--
-- Name: case_header_case_data_gin_idx; Type: INDEX; Schema: pic_master1; Owner: postgres
--

CREATE INDEX case_header_case_data_gin_idx ON pic_master1.case_header USING gin (case_data jsonb_path_ops);


--
-- Name: claim_decision_details_case_claim_idx; Type: INDEX; Schema: pic_master1; Owner: postgres
--

CREATE INDEX claim_decision_details_case_claim_idx ON pic_master1.claim_decision_details USING btree (case_id, claim_number, reviewed_dts DESC);


--
-- Name: claim_decision_details_data_gin_idx; Type: INDEX; Schema: pic_master1; Owner: postgres
--

CREATE INDEX claim_decision_details_data_gin_idx ON pic_master1.claim_decision_details USING gin (decision_data jsonb_path_ops);


--
-- Name: claim_decision_details_filters_idx; Type: INDEX; Schema: pic_master1; Owner: postgres
--

CREATE INDEX claim_decision_details_filters_idx ON pic_master1.claim_decision_details USING btree (qc_review_status, qc_review, qc_review_comment);


--
-- Name: claim_details_claim_data_gin_idx; Type: INDEX; Schema: pic_master1; Owner: postgres
--

CREATE INDEX claim_details_claim_data_gin_idx ON pic_master1.claim_details USING gin (claim_data jsonb_path_ops);


--
-- Name: claim_details_claim_number_idx; Type: INDEX; Schema: pic_master1; Owner: postgres
--

CREATE INDEX claim_details_claim_number_idx ON pic_master1.claim_details USING btree (claim_number);


--
-- Name: claim_details_qc_status_idx; Type: INDEX; Schema: pic_master1; Owner: postgres
--

CREATE INDEX claim_details_qc_status_idx ON pic_master1.claim_details USING btree (qc_status);


--
-- Name: claim_decision_details claim_decision_details_case_id_claim_number_fkey; Type: FK CONSTRAINT; Schema: pic_master1; Owner: postgres
--

ALTER TABLE ONLY pic_master1.claim_decision_details
    ADD CONSTRAINT claim_decision_details_case_id_claim_number_fkey FOREIGN KEY (case_id, claim_number) REFERENCES pic_master1.claim_details(case_id, claim_number) ON DELETE CASCADE;


--
-- Name: claim_details claim_details_case_id_fkey; Type: FK CONSTRAINT; Schema: pic_master1; Owner: postgres
--

ALTER TABLE ONLY pic_master1.claim_details
    ADD CONSTRAINT claim_details_case_id_fkey FOREIGN KEY (case_id) REFERENCES pic_master1.case_header(case_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict lRnQDKdDcdx37T3rvGaNA34czCeve9IBcgeDTIOQFrYQ6esa4sWtDrFeMLS2h7j

