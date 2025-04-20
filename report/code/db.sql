--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2
-- Dumped by pg_dump version 17.4

-- Started on 2025-04-20 14:05:30

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
-- TOC entry 8 (class 2615 OID 56329)
-- Name: onj; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA onj;


ALTER SCHEMA onj OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 232 (class 1259 OID 56331)
-- Name: article_pieces; Type: TABLE; Schema: onj; Owner: postgres
--

CREATE TABLE onj.article_pieces (
    id integer NOT NULL,
    piece_type text NOT NULL,
    content text NOT NULL,
    embedding crawldb.vector(384),
    article_id integer
);


ALTER TABLE onj.article_pieces OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 56330)
-- Name: article_pieces_id_seq; Type: SEQUENCE; Schema: onj; Owner: postgres
--

CREATE SEQUENCE onj.article_pieces_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE onj.article_pieces_id_seq OWNER TO postgres;

--
-- TOC entry 5117 (class 0 OID 0)
-- Dependencies: 231
-- Name: article_pieces_id_seq; Type: SEQUENCE OWNED BY; Schema: onj; Owner: postgres
--

ALTER SEQUENCE onj.article_pieces_id_seq OWNED BY onj.article_pieces.id;


--
-- TOC entry 234 (class 1259 OID 56340)
-- Name: articles; Type: TABLE; Schema: onj; Owner: postgres
--

CREATE TABLE onj.articles (
    id integer NOT NULL,
    title text NOT NULL,
    subtitle text,
    recap text,
    published_at timestamp without time zone NOT NULL,
    url text NOT NULL,
    author text,
    subcategory text,
    section text
);


ALTER TABLE onj.articles OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 56339)
-- Name: articles_id_seq; Type: SEQUENCE; Schema: onj; Owner: postgres
--

CREATE SEQUENCE onj.articles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE onj.articles_id_seq OWNER TO postgres;

--
-- TOC entry 5118 (class 0 OID 0)
-- Dependencies: 233
-- Name: articles_id_seq; Type: SEQUENCE OWNED BY; Schema: onj; Owner: postgres
--

ALTER SEQUENCE onj.articles_id_seq OWNED BY onj.articles.id;


--
-- TOC entry 4962 (class 2604 OID 56334)
-- Name: article_pieces id; Type: DEFAULT; Schema: onj; Owner: postgres
--

ALTER TABLE ONLY onj.article_pieces ALTER COLUMN id SET DEFAULT nextval('onj.article_pieces_id_seq'::regclass);


--
-- TOC entry 4963 (class 2604 OID 56343)
-- Name: articles id; Type: DEFAULT; Schema: onj; Owner: postgres
--

ALTER TABLE ONLY onj.articles ALTER COLUMN id SET DEFAULT nextval('onj.articles_id_seq'::regclass);


--
-- TOC entry 4965 (class 2606 OID 56338)
-- Name: article_pieces article_pieces_pkey; Type: CONSTRAINT; Schema: onj; Owner: postgres
--

ALTER TABLE ONLY onj.article_pieces
    ADD CONSTRAINT article_pieces_pkey PRIMARY KEY (id);


--
-- TOC entry 4967 (class 2606 OID 56347)
-- Name: articles articles_pkey; Type: CONSTRAINT; Schema: onj; Owner: postgres
--

ALTER TABLE ONLY onj.articles
    ADD CONSTRAINT articles_pkey PRIMARY KEY (id);


--
-- TOC entry 4968 (class 2606 OID 56348)
-- Name: article_pieces article_pieces_article_id_fkey; Type: FK CONSTRAINT; Schema: onj; Owner: postgres
--

ALTER TABLE ONLY onj.article_pieces
    ADD CONSTRAINT article_pieces_article_id_fkey FOREIGN KEY (article_id) REFERENCES onj.articles(id) ON DELETE CASCADE;


-- Completed on 2025-04-20 14:05:30

--
-- PostgreSQL database dump complete
--

