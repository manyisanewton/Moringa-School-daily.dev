--
-- PostgreSQL database dump
--

-- Dumped from database version 14.17 (Ubuntu 14.17-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.17 (Ubuntu 14.17-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: contentstatusenum; Type: TYPE; Schema: public; Owner: moringa
--

CREATE TYPE public.contentstatusenum AS ENUM (
    'Draft',
    'Pending',
    'Published',
    'Flagged'
);


ALTER TYPE public.contentstatusenum OWNER TO moringa;

--
-- Name: contenttypeenum; Type: TYPE; Schema: public; Owner: moringa
--

CREATE TYPE public.contenttypeenum AS ENUM (
    'video',
    'audio',
    'article',
    'quote'
);


ALTER TYPE public.contenttypeenum OWNER TO moringa;

--
-- Name: reactiontypeenum; Type: TYPE; Schema: public; Owner: moringa
--

CREATE TYPE public.reactiontypeenum AS ENUM (
    'like',
    'dislike'
);


ALTER TYPE public.reactiontypeenum OWNER TO moringa;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO moringa;

--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    user_id integer,
    action character varying(128) NOT NULL,
    target_type character varying(64),
    target_id integer,
    "timestamp" timestamp without time zone DEFAULT now() NOT NULL,
    details json
);


ALTER TABLE public.audit_logs OWNER TO moringa;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_logs_id_seq OWNER TO moringa;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.categories (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    description character varying(256),
    created_by integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.categories OWNER TO moringa;

--
-- Name: categories_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.categories_id_seq OWNER TO moringa;

--
-- Name: categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.categories_id_seq OWNED BY public.categories.id;


--
-- Name: comments; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.comments (
    id integer NOT NULL,
    post_id integer NOT NULL,
    user_id integer NOT NULL,
    parent_id integer,
    body text NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.comments OWNER TO moringa;

--
-- Name: comments_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.comments_id_seq OWNER TO moringa;

--
-- Name: comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.comments_id_seq OWNED BY public.comments.id;


--
-- Name: content_histories; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.content_histories (
    id integer NOT NULL,
    content_id integer NOT NULL,
    title character varying(256),
    body text,
    media_url character varying(512),
    edited_by integer,
    edited_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.content_histories OWNER TO moringa;

--
-- Name: content_histories_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.content_histories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.content_histories_id_seq OWNER TO moringa;

--
-- Name: content_histories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.content_histories_id_seq OWNED BY public.content_histories.id;


--
-- Name: content_tags; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.content_tags (
    id integer NOT NULL,
    content_id integer NOT NULL,
    tag_id integer NOT NULL
);


ALTER TABLE public.content_tags OWNER TO moringa;

--
-- Name: content_tags_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.content_tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.content_tags_id_seq OWNER TO moringa;

--
-- Name: content_tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.content_tags_id_seq OWNED BY public.content_tags.id;


--
-- Name: contents; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.contents (
    id integer NOT NULL,
    title character varying(256) NOT NULL,
    body text,
    media_url character varying(512),
    content_type public.contenttypeenum NOT NULL,
    status public.contentstatusenum NOT NULL,
    author_id integer NOT NULL,
    category_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.contents OWNER TO moringa;

--
-- Name: contents_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.contents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.contents_id_seq OWNER TO moringa;

--
-- Name: contents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.contents_id_seq OWNED BY public.contents.id;


--
-- Name: email_verification_tokens; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.email_verification_tokens (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token character varying(256) NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    used boolean,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.email_verification_tokens OWNER TO moringa;

--
-- Name: email_verification_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.email_verification_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.email_verification_tokens_id_seq OWNER TO moringa;

--
-- Name: email_verification_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.email_verification_tokens_id_seq OWNED BY public.email_verification_tokens.id;


--
-- Name: flags; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.flags (
    id integer NOT NULL,
    user_id integer NOT NULL,
    content_id integer NOT NULL,
    reason character varying(256),
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.flags OWNER TO moringa;

--
-- Name: flags_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.flags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.flags_id_seq OWNER TO moringa;

--
-- Name: flags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.flags_id_seq OWNED BY public.flags.id;


--
-- Name: likes; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.likes (
    id integer NOT NULL,
    user_id integer NOT NULL,
    post_id integer NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.likes OWNER TO moringa;

--
-- Name: likes_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.likes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.likes_id_seq OWNER TO moringa;

--
-- Name: likes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.likes_id_seq OWNED BY public.likes.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    user_id integer NOT NULL,
    content_id integer,
    message character varying(256) NOT NULL,
    is_read boolean,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notifications OWNER TO moringa;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.notifications_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notifications_id_seq OWNER TO moringa;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: password_reset_tokens; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.password_reset_tokens (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token character varying(256) NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    used boolean,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.password_reset_tokens OWNER TO moringa;

--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.password_reset_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.password_reset_tokens_id_seq OWNER TO moringa;

--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.password_reset_tokens_id_seq OWNED BY public.password_reset_tokens.id;


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.permissions (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    description character varying(256)
);


ALTER TABLE public.permissions OWNER TO moringa;

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.permissions_id_seq OWNER TO moringa;

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- Name: phone_otps; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.phone_otps (
    id integer NOT NULL,
    phone_number character varying(20) NOT NULL,
    otp_code character varying(6) NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.phone_otps OWNER TO moringa;

--
-- Name: phone_otps_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.phone_otps_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.phone_otps_id_seq OWNER TO moringa;

--
-- Name: phone_otps_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.phone_otps_id_seq OWNED BY public.phone_otps.id;


--
-- Name: posts; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.posts (
    id integer NOT NULL,
    category_id integer NOT NULL,
    type character varying(50) NOT NULL,
    title character varying(256) NOT NULL,
    author character varying(128),
    date timestamp without time zone NOT NULL,
    likes integer,
    comment_count integer
);


ALTER TABLE public.posts OWNER TO moringa;

--
-- Name: posts_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.posts_id_seq OWNER TO moringa;

--
-- Name: posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;


--
-- Name: reactions; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.reactions (
    id integer NOT NULL,
    user_id integer NOT NULL,
    content_id integer NOT NULL,
    type public.reactiontypeenum NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.reactions OWNER TO moringa;

--
-- Name: reactions_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.reactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reactions_id_seq OWNER TO moringa;

--
-- Name: reactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.reactions_id_seq OWNED BY public.reactions.id;


--
-- Name: refresh_tokens; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.refresh_tokens (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token character varying(36) NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    revoked boolean,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.refresh_tokens OWNER TO moringa;

--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.refresh_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.refresh_tokens_id_seq OWNER TO moringa;

--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.refresh_tokens_id_seq OWNED BY public.refresh_tokens.id;


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.role_permissions (
    id integer NOT NULL,
    role_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO moringa;

--
-- Name: role_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.role_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.role_permissions_id_seq OWNER TO moringa;

--
-- Name: role_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.role_permissions_id_seq OWNED BY public.role_permissions.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying(64) NOT NULL,
    description character varying(256)
);


ALTER TABLE public.roles OWNER TO moringa;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.roles_id_seq OWNER TO moringa;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.subscriptions (
    user_id integer NOT NULL,
    category_id integer NOT NULL,
    content_id integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.subscriptions OWNER TO moringa;

--
-- Name: tags; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.tags (
    id integer NOT NULL,
    name character varying(64) NOT NULL
);


ALTER TABLE public.tags OWNER TO moringa;

--
-- Name: tags_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.tags_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tags_id_seq OWNER TO moringa;

--
-- Name: tags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.tags_id_seq OWNED BY public.tags.id;


--
-- Name: user_profiles; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.user_profiles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    name character varying(128),
    bio text,
    avatar_url character varying(512),
    social_links character varying(512),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.user_profiles OWNER TO moringa;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.user_profiles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_profiles_id_seq OWNER TO moringa;

--
-- Name: user_profiles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.user_profiles_id_seq OWNED BY public.user_profiles.id;


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.user_roles (
    id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer NOT NULL
);


ALTER TABLE public.user_roles OWNER TO moringa;

--
-- Name: user_roles_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.user_roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_roles_id_seq OWNER TO moringa;

--
-- Name: user_roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.user_roles_id_seq OWNED BY public.user_roles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(128) NOT NULL,
    name character varying(128) NOT NULL,
    password_hash character varying(256) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.users OWNER TO moringa;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO moringa;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: wishlists; Type: TABLE; Schema: public; Owner: moringa
--

CREATE TABLE public.wishlists (
    id integer NOT NULL,
    user_id integer NOT NULL,
    content_id integer NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.wishlists OWNER TO moringa;

--
-- Name: wishlists_id_seq; Type: SEQUENCE; Schema: public; Owner: moringa
--

CREATE SEQUENCE public.wishlists_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.wishlists_id_seq OWNER TO moringa;

--
-- Name: wishlists_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: moringa
--

ALTER SEQUENCE public.wishlists_id_seq OWNED BY public.wishlists.id;


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: categories id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.categories ALTER COLUMN id SET DEFAULT nextval('public.categories_id_seq'::regclass);


--
-- Name: comments id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.comments ALTER COLUMN id SET DEFAULT nextval('public.comments_id_seq'::regclass);


--
-- Name: content_histories id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.content_histories ALTER COLUMN id SET DEFAULT nextval('public.content_histories_id_seq'::regclass);


--
-- Name: content_tags id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.content_tags ALTER COLUMN id SET DEFAULT nextval('public.content_tags_id_seq'::regclass);


--
-- Name: contents id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.contents ALTER COLUMN id SET DEFAULT nextval('public.contents_id_seq'::regclass);


--
-- Name: email_verification_tokens id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.email_verification_tokens ALTER COLUMN id SET DEFAULT nextval('public.email_verification_tokens_id_seq'::regclass);


--
-- Name: flags id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.flags ALTER COLUMN id SET DEFAULT nextval('public.flags_id_seq'::regclass);


--
-- Name: likes id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.likes ALTER COLUMN id SET DEFAULT nextval('public.likes_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: password_reset_tokens id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.password_reset_tokens ALTER COLUMN id SET DEFAULT nextval('public.password_reset_tokens_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- Name: phone_otps id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.phone_otps ALTER COLUMN id SET DEFAULT nextval('public.phone_otps_id_seq'::regclass);


--
-- Name: posts id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);


--
-- Name: reactions id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.reactions ALTER COLUMN id SET DEFAULT nextval('public.reactions_id_seq'::regclass);


--
-- Name: refresh_tokens id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.refresh_tokens ALTER COLUMN id SET DEFAULT nextval('public.refresh_tokens_id_seq'::regclass);


--
-- Name: role_permissions id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.role_permissions ALTER COLUMN id SET DEFAULT nextval('public.role_permissions_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: tags id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.tags ALTER COLUMN id SET DEFAULT nextval('public.tags_id_seq'::regclass);


--
-- Name: user_profiles id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.user_profiles ALTER COLUMN id SET DEFAULT nextval('public.user_profiles_id_seq'::regclass);


--
-- Name: user_roles id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.user_roles ALTER COLUMN id SET DEFAULT nextval('public.user_roles_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: wishlists id; Type: DEFAULT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.wishlists ALTER COLUMN id SET DEFAULT nextval('public.wishlists_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.alembic_version (version_num) FROM stdin;
43dec15310f3
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.audit_logs (id, user_id, action, target_type, target_id, "timestamp", details) FROM stdin;
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.categories (id, name, description, created_by, created_at) FROM stdin;
\.


--
-- Data for Name: comments; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.comments (id, post_id, user_id, parent_id, body, created_at) FROM stdin;
\.


--
-- Data for Name: content_histories; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.content_histories (id, content_id, title, body, media_url, edited_by, edited_at) FROM stdin;
\.


--
-- Data for Name: content_tags; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.content_tags (id, content_id, tag_id) FROM stdin;
\.


--
-- Data for Name: contents; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.contents (id, title, body, media_url, content_type, status, author_id, category_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: email_verification_tokens; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.email_verification_tokens (id, user_id, token, expires_at, used, created_at) FROM stdin;
\.


--
-- Data for Name: flags; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.flags (id, user_id, content_id, reason, created_at) FROM stdin;
\.


--
-- Data for Name: likes; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.likes (id, user_id, post_id, created_at) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.notifications (id, user_id, content_id, message, is_read, created_at) FROM stdin;
\.


--
-- Data for Name: password_reset_tokens; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.password_reset_tokens (id, user_id, token, expires_at, used, created_at) FROM stdin;
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.permissions (id, name, description) FROM stdin;
\.


--
-- Data for Name: phone_otps; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.phone_otps (id, phone_number, otp_code, expires_at, created_at) FROM stdin;
\.


--
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.posts (id, category_id, type, title, author, date, likes, comment_count) FROM stdin;
\.


--
-- Data for Name: reactions; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.reactions (id, user_id, content_id, type, created_at) FROM stdin;
\.


--
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.refresh_tokens (id, user_id, token, expires_at, revoked, created_at) FROM stdin;
1	1	471838f7-cb6c-4dd1-b4b0-ffbbf8959f51	2025-06-13 06:30:19.692153	f	2025-05-14 09:30:19.55101
2	2	0573f6ae-1c3b-49f2-b2d3-6b5a0fe659db	2025-06-13 06:48:12.551641	f	2025-05-14 09:48:12.150362
3	2	32158ae4-338d-49e4-b573-f47bdeb023c9	2025-06-13 09:01:02.291511	f	2025-05-14 12:01:00.756512
4	1	4904a627-1af3-436c-800c-21fa9d27821c	2025-06-13 09:01:44.632804	f	2025-05-14 12:01:44.628331
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.role_permissions (id, role_id, permission_id) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.roles (id, name, description) FROM stdin;
\.


--
-- Data for Name: subscriptions; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.subscriptions (user_id, category_id, content_id, created_at) FROM stdin;
\.


--
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.tags (id, name) FROM stdin;
\.


--
-- Data for Name: user_profiles; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.user_profiles (id, user_id, name, bio, avatar_url, social_links, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.user_roles (id, user_id, role_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.users (id, email, name, password_hash, is_active, created_at, updated_at) FROM stdin;
1	newton.manyisa@student.moringaschool.com	Newton Manyisa	$2b$12$FFA4NK6lLSl55FQV2XLjXuuBFCqCx692pbVlio7I2HPnhAvR3E0/O	t	2025-05-14 09:30:18.990576	2025-05-14 09:30:18.990576
2	lexy1@gmail.com	lexy	$2b$12$4zJfTzBEfcrgrTiOvLGPeukY8XActjSmEOoTX73V9MRKXItU/i.mu	t	2025-05-14 09:47:44.366491	2025-05-14 09:47:44.366491
\.


--
-- Data for Name: wishlists; Type: TABLE DATA; Schema: public; Owner: moringa
--

COPY public.wishlists (id, user_id, content_id, created_at) FROM stdin;
\.


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 1, false);


--
-- Name: categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.categories_id_seq', 1, false);


--
-- Name: comments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.comments_id_seq', 1, false);


--
-- Name: content_histories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.content_histories_id_seq', 1, false);


--
-- Name: content_tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.content_tags_id_seq', 1, false);


--
-- Name: contents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.contents_id_seq', 1, false);


--
-- Name: email_verification_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.email_verification_tokens_id_seq', 1, false);


--
-- Name: flags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.flags_id_seq', 1, false);


--
-- Name: likes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.likes_id_seq', 1, false);


--
-- Name: notifications_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.notifications_id_seq', 1, false);


--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.password_reset_tokens_id_seq', 1, false);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.permissions_id_seq', 1, false);


--
-- Name: phone_otps_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.phone_otps_id_seq', 1, false);


--
-- Name: posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.posts_id_seq', 1, false);


--
-- Name: reactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.reactions_id_seq', 1, false);


--
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.refresh_tokens_id_seq', 4, true);


--
-- Name: role_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.role_permissions_id_seq', 1, false);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.roles_id_seq', 1, false);


--
-- Name: tags_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.tags_id_seq', 1, false);


--
-- Name: user_profiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.user_profiles_id_seq', 1, false);


--
-- Name: user_roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.user_roles_id_seq', 1, false);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: wishlists_id_seq; Type: SEQUENCE SET; Schema: public; Owner: moringa
--

SELECT pg_catalog.setval('public.wishlists_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (id);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- Name: content_histories content_histories_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.content_histories
    ADD CONSTRAINT content_histories_pkey PRIMARY KEY (id);


--
-- Name: content_tags content_tags_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.content_tags
    ADD CONSTRAINT content_tags_pkey PRIMARY KEY (id);


--
-- Name: contents contents_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.contents
    ADD CONSTRAINT contents_pkey PRIMARY KEY (id);


--
-- Name: email_verification_tokens email_verification_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.email_verification_tokens
    ADD CONSTRAINT email_verification_tokens_pkey PRIMARY KEY (id);


--
-- Name: email_verification_tokens email_verification_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.email_verification_tokens
    ADD CONSTRAINT email_verification_tokens_token_key UNIQUE (token);


--
-- Name: flags flags_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.flags
    ADD CONSTRAINT flags_pkey PRIMARY KEY (id);


--
-- Name: likes likes_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.likes
    ADD CONSTRAINT likes_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: password_reset_tokens password_reset_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_pkey PRIMARY KEY (id);


--
-- Name: password_reset_tokens password_reset_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_token_key UNIQUE (token);


--
-- Name: permissions permissions_name_key; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_name_key UNIQUE (name);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: phone_otps phone_otps_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.phone_otps
    ADD CONSTRAINT phone_otps_pkey PRIMARY KEY (id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: reactions reactions_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.reactions
    ADD CONSTRAINT reactions_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_token_key UNIQUE (token);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (id);


--
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (user_id, category_id);


--
-- Name: tags tags_name_key; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_name_key UNIQUE (name);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (id);


--
-- Name: content_tags uq_content_tag; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.content_tags
    ADD CONSTRAINT uq_content_tag UNIQUE (content_id, tag_id);


--
-- Name: role_permissions uq_role_permission; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT uq_role_permission UNIQUE (role_id, permission_id);


--
-- Name: user_roles uq_user_role; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT uq_user_role UNIQUE (user_id, role_id);


--
-- Name: user_profiles user_profiles_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_pkey PRIMARY KEY (id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: wishlists wishlists_pkey; Type: CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.wishlists
    ADD CONSTRAINT wishlists_pkey PRIMARY KEY (id);


--
-- Name: ix_email_verification_token_token; Type: INDEX; Schema: public; Owner: moringa
--

CREATE INDEX ix_email_verification_token_token ON public.email_verification_tokens USING btree (token);


--
-- Name: ix_password_reset_token_token; Type: INDEX; Schema: public; Owner: moringa
--

CREATE INDEX ix_password_reset_token_token ON public.password_reset_tokens USING btree (token);


--
-- Name: ix_refresh_token_token; Type: INDEX; Schema: public; Owner: moringa
--

CREATE INDEX ix_refresh_token_token ON public.refresh_tokens USING btree (token);


--
-- Name: ix_subscriptions_category_id; Type: INDEX; Schema: public; Owner: moringa
--

CREATE INDEX ix_subscriptions_category_id ON public.subscriptions USING btree (category_id);


--
-- Name: ix_subscriptions_user_id; Type: INDEX; Schema: public; Owner: moringa
--

CREATE INDEX ix_subscriptions_user_id ON public.subscriptions USING btree (user_id);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: categories categories_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: comments comments_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.comments(id) ON DELETE CASCADE;


--
-- Name: comments comments_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id) ON DELETE CASCADE;


--
-- Name: comments comments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: content_histories content_histories_content_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.content_histories
    ADD CONSTRAINT content_histories_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.contents(id) ON DELETE CASCADE;


--
-- Name: content_histories content_histories_edited_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.content_histories
    ADD CONSTRAINT content_histories_edited_by_fkey FOREIGN KEY (edited_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: content_tags content_tags_content_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.content_tags
    ADD CONSTRAINT content_tags_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.contents(id) ON DELETE CASCADE;


--
-- Name: content_tags content_tags_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.content_tags
    ADD CONSTRAINT content_tags_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tags(id) ON DELETE CASCADE;


--
-- Name: contents contents_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.contents
    ADD CONSTRAINT contents_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: contents contents_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.contents
    ADD CONSTRAINT contents_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE SET NULL;


--
-- Name: email_verification_tokens email_verification_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.email_verification_tokens
    ADD CONSTRAINT email_verification_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: flags flags_content_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.flags
    ADD CONSTRAINT flags_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.contents(id) ON DELETE CASCADE;


--
-- Name: flags flags_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.flags
    ADD CONSTRAINT flags_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: likes likes_post_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.likes
    ADD CONSTRAINT likes_post_id_fkey FOREIGN KEY (post_id) REFERENCES public.posts(id);


--
-- Name: likes likes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.likes
    ADD CONSTRAINT likes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: notifications notifications_content_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.contents(id) ON DELETE CASCADE;


--
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: password_reset_tokens password_reset_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: posts posts_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id);


--
-- Name: reactions reactions_content_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.reactions
    ADD CONSTRAINT reactions_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.contents(id) ON DELETE CASCADE;


--
-- Name: reactions reactions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.reactions
    ADD CONSTRAINT reactions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: refresh_tokens refresh_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: subscriptions subscriptions_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(id) ON DELETE CASCADE;


--
-- Name: subscriptions subscriptions_content_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.contents(id) ON DELETE CASCADE;


--
-- Name: subscriptions subscriptions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_profiles user_profiles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.user_profiles
    ADD CONSTRAINT user_profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: wishlists wishlists_content_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.wishlists
    ADD CONSTRAINT wishlists_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.contents(id) ON DELETE CASCADE;


--
-- Name: wishlists wishlists_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: moringa
--

ALTER TABLE ONLY public.wishlists
    ADD CONSTRAINT wishlists_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

