-- Initial research agent schema. Forward-only migration.

CREATE TABLE project (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    domain TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'archived')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    settings_json TEXT NOT NULL
);

CREATE TABLE research_question (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    normalized_question TEXT,
    scope_json TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    parent_id TEXT REFERENCES research_question(id) ON DELETE SET NULL,
    created_at TEXT NOT NULL,
    UNIQUE (project_id, version)
);

CREATE TABLE run (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    question_id TEXT NOT NULL REFERENCES research_question(id) ON DELETE RESTRICT,
    status TEXT NOT NULL CHECK (
        status IN (
            'CREATED', 'PLANNED', 'RUNNING', 'WAITING_CONFIRMATION',
            'PAUSED', 'COMPLETED', 'FAILED', 'CANCELLED'
        )
    ),
    "trigger" TEXT NOT NULL CHECK ("trigger" IN ('cli', 'web', 'evaluation')),
    config_hash TEXT NOT NULL,
    config_json TEXT NOT NULL,
    system_version TEXT NOT NULL,
    environment_json TEXT,
    started_at TEXT,
    finished_at TEXT,
    error_code TEXT,
    summary_json TEXT
);

CREATE TABLE plan (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES run(id) ON DELETE CASCADE,
    version INTEGER NOT NULL CHECK (version > 0),
    strategy TEXT NOT NULL CHECK (strategy IN ('template', 'llm', 'hybrid')),
    status TEXT NOT NULL CHECK (
        status IN ('draft', 'validated', 'active', 'superseded')
    ),
    plan_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (run_id, version)
);

CREATE TABLE plan_step (
    id TEXT PRIMARY KEY,
    plan_id TEXT NOT NULL REFERENCES plan(id) ON DELETE CASCADE,
    step_key TEXT NOT NULL,
    step_type TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('PENDING', 'READY', 'RUNNING', 'RETRYING', 'SUCCEEDED', 'FAILED', 'SKIPPED')
    ),
    depends_on_json TEXT NOT NULL,
    input_json TEXT,
    output_json TEXT,
    attempt_count INTEGER NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
    started_at TEXT,
    finished_at TEXT,
    error_code TEXT,
    checkpoint_json TEXT,
    UNIQUE (plan_id, step_key)
);

CREATE TABLE query (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES run(id) ON DELETE CASCADE,
    plan_step_id TEXT NOT NULL REFERENCES plan_step(id) ON DELETE CASCADE,
    query_text TEXT NOT NULL,
    variants_json TEXT,
    filters_json TEXT NOT NULL,
    query_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE source_call (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES run(id) ON DELETE CASCADE,
    query_id TEXT REFERENCES query(id) ON DELETE SET NULL,
    source TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    request_hash TEXT NOT NULL,
    request_json TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('success', 'partial', 'failed')),
    retry_count INTEGER NOT NULL DEFAULT 0 CHECK (retry_count >= 0),
    http_status INTEGER,
    elapsed_ms INTEGER CHECK (elapsed_ms IS NULL OR elapsed_ms >= 0),
    response_hash TEXT,
    error_code TEXT,
    error_details_json TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT
);

CREATE TABLE source_call_attempt (
    id TEXT PRIMARY KEY,
    source_call_id TEXT NOT NULL REFERENCES source_call(id) ON DELETE CASCADE,
    attempt_no INTEGER NOT NULL CHECK (attempt_no > 0),
    status TEXT NOT NULL CHECK (
        status IN ('running', 'succeeded', 'failed', 'retrying')
    ),
    http_status INTEGER,
    elapsed_ms INTEGER CHECK (elapsed_ms IS NULL OR elapsed_ms >= 0),
    retry_after_ms INTEGER CHECK (retry_after_ms IS NULL OR retry_after_ms >= 0),
    error_code TEXT,
    error_details_json TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    UNIQUE (source_call_id, attempt_no)
);

CREATE TABLE source_record (
    id TEXT PRIMARY KEY,
    source_call_id TEXT NOT NULL REFERENCES source_call(id) ON DELETE RESTRICT,
    source TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    api_endpoint TEXT NOT NULL,
    source_version TEXT,
    raw_json TEXT NOT NULL,
    mapping_version TEXT NOT NULL,
    retrieved_at TEXT NOT NULL,
    query_hash TEXT,
    query_snapshot_json TEXT,
    response_hash TEXT,
    content_hash TEXT NOT NULL,
    UNIQUE (source, source_record_id, content_hash)
);

CREATE TABLE paper (
    id TEXT PRIMARY KEY,
    canonical_key TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    title_normalized TEXT NOT NULL,
    abstract TEXT,
    year INTEGER,
    publication_date TEXT,
    venue TEXT,
    type TEXT,
    language TEXT,
    open_access_status TEXT,
    citation_count INTEGER CHECK (citation_count IS NULL OR citation_count >= 0),
    merge_confidence REAL CHECK (
        merge_confidence IS NULL OR (merge_confidence >= 0 AND merge_confidence <= 1)
    ),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE paper_identifier (
    id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES paper(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    value TEXT NOT NULL,
    normalized_value TEXT NOT NULL,
    source_record_id TEXT REFERENCES source_record(id) ON DELETE SET NULL,
    is_primary INTEGER NOT NULL DEFAULT 0 CHECK (is_primary IN (0, 1)),
    UNIQUE (type, normalized_value)
);

CREATE TABLE author (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    name_normalized TEXT NOT NULL,
    orcid TEXT,
    source_author_id TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE paper_author (
    paper_id TEXT NOT NULL REFERENCES paper(id) ON DELETE CASCADE,
    author_id TEXT NOT NULL REFERENCES author(id) ON DELETE CASCADE,
    position INTEGER NOT NULL CHECK (position >= 0),
    is_corresponding INTEGER CHECK (
        is_corresponding IS NULL OR is_corresponding IN (0, 1)
    ),
    PRIMARY KEY (paper_id, author_id, position)
);

CREATE TABLE paper_source_record (
    paper_id TEXT NOT NULL REFERENCES paper(id) ON DELETE CASCADE,
    source_record_id TEXT NOT NULL REFERENCES source_record(id) ON DELETE RESTRICT,
    match_score REAL CHECK (
        match_score IS NULL OR (match_score >= 0 AND match_score <= 1)
    ),
    merge_reason TEXT NOT NULL,
    is_primary_metadata INTEGER NOT NULL DEFAULT 0 CHECK (is_primary_metadata IN (0, 1)),
    PRIMARY KEY (paper_id, source_record_id)
);

CREATE TABLE file (
    id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES paper(id) ON DELETE RESTRICT,
    kind TEXT NOT NULL CHECK (kind IN ('pdf', 'html', 'text')),
    sha256 TEXT NOT NULL,
    path TEXT NOT NULL,
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    content_type TEXT NOT NULL,
    source_url TEXT NOT NULL,
    final_url TEXT,
    retrieved_at TEXT NOT NULL,
    license TEXT,
    status TEXT NOT NULL CHECK (
        status IN ('stored', 'quarantined', 'missing', 'deleted')
    ),
    created_at TEXT NOT NULL,
    UNIQUE (paper_id, sha256)
);

CREATE TABLE document (
    id TEXT PRIMARY KEY,
    file_id TEXT NOT NULL REFERENCES file(id) ON DELETE CASCADE,
    parser TEXT NOT NULL,
    parser_version TEXT NOT NULL,
    text_path TEXT NOT NULL,
    text_sha256 TEXT NOT NULL,
    locator_scheme TEXT NOT NULL,
    parse_status TEXT NOT NULL CHECK (
        parse_status IN ('success', 'partial', 'failed')
    ),
    created_at TEXT NOT NULL
);

CREATE TABLE evidence_span (
    id TEXT PRIMARY KEY,
    paper_id TEXT NOT NULL REFERENCES paper(id) ON DELETE RESTRICT,
    source_record_id TEXT NOT NULL REFERENCES source_record(id) ON DELETE RESTRICT,
    document_id TEXT REFERENCES document(id) ON DELETE RESTRICT,
    file_id TEXT REFERENCES file(id) ON DELETE RESTRICT,
    quote TEXT NOT NULL,
    quote_hash TEXT NOT NULL,
    locator_json TEXT NOT NULL,
    evidence_level TEXT NOT NULL CHECK (
        evidence_level IN ('metadata', 'abstract', 'full_text', 'external')
    ),
    extraction_method TEXT NOT NULL CHECK (
        extraction_method IN ('rule', 'pdf_parser', 'llm', 'human')
    ),
    extractor_version TEXT,
    confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    verified INTEGER NOT NULL DEFAULT 0 CHECK (verified IN (0, 1)),
    created_at TEXT NOT NULL,
    CHECK (
        evidence_level != 'full_text'
        OR (document_id IS NOT NULL AND file_id IS NOT NULL)
    )
);

CREATE TABLE report (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES run(id) ON DELETE CASCADE,
    version INTEGER NOT NULL CHECK (version > 0),
    format TEXT NOT NULL CHECK (format IN ('markdown', 'json', 'csv')),
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'validated', 'published')),
    created_at TEXT NOT NULL,
    UNIQUE (run_id, version, format)
);

CREATE TABLE claim (
    id TEXT PRIMARY KEY,
    report_id TEXT NOT NULL REFERENCES report(id) ON DELETE CASCADE,
    claim_text TEXT NOT NULL,
    claim_type TEXT NOT NULL,
    support_status TEXT NOT NULL CHECK (
        support_status IN ('supported', 'partially_supported', 'unsupported', 'disputed')
    ),
    confidence REAL NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    created_at TEXT NOT NULL
);

CREATE TABLE claim_evidence (
    claim_id TEXT NOT NULL REFERENCES claim(id) ON DELETE CASCADE,
    evidence_span_id TEXT NOT NULL REFERENCES evidence_span(id) ON DELETE RESTRICT,
    relation_type TEXT NOT NULL CHECK (
        relation_type IN ('supports', 'refutes', 'context')
    ),
    rank INTEGER NOT NULL CHECK (rank >= 0),
    PRIMARY KEY (claim_id, evidence_span_id, relation_type)
);

CREATE TABLE export (
    id TEXT PRIMARY KEY,
    report_id TEXT NOT NULL REFERENCES report(id) ON DELETE CASCADE,
    format TEXT NOT NULL CHECK (format IN ('bibtex', 'zotero', 'csv', 'json')),
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE audit_event (
    id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES run(id) ON DELETE SET NULL,
    actor TEXT NOT NULL CHECK (actor IN ('system', 'user', 'mcp_server')),
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT,
    decision TEXT CHECK (decision IS NULL OR decision IN ('allowed', 'denied', 'confirmed')),
    details_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE model_call (
    id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES run(id) ON DELETE SET NULL,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    purpose TEXT NOT NULL,
    prompt_hash TEXT NOT NULL,
    prompt_version TEXT,
    response_hash TEXT,
    input_tokens INTEGER CHECK (input_tokens IS NULL OR input_tokens >= 0),
    output_tokens INTEGER CHECK (output_tokens IS NULL OR output_tokens >= 0),
    cost REAL CHECK (cost IS NULL OR cost >= 0),
    latency_ms INTEGER CHECK (latency_ms IS NULL OR latency_ms >= 0),
    status TEXT NOT NULL CHECK (status IN ('success', 'failed')),
    error_code TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE step_attempt (
    id TEXT PRIMARY KEY,
    step_id TEXT NOT NULL REFERENCES plan_step(id) ON DELETE CASCADE,
    attempt_no INTEGER NOT NULL CHECK (attempt_no > 0),
    status TEXT NOT NULL CHECK (
        status IN ('running', 'succeeded', 'failed', 'cancelled')
    ),
    input_json TEXT,
    output_json TEXT,
    checkpoint_json TEXT,
    error_code TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    UNIQUE (step_id, attempt_no)
);

CREATE TABLE note (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES project(id) ON DELETE CASCADE,
    paper_id TEXT REFERENCES paper(id) ON DELETE SET NULL,
    run_id TEXT REFERENCES run(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    body_text TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE evaluation_run (
    id TEXT PRIMARY KEY,
    dataset_version TEXT NOT NULL,
    dataset_hash TEXT NOT NULL,
    system_version TEXT NOT NULL,
    config_json TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN ('created', 'running', 'completed', 'failed')
    ),
    started_at TEXT,
    finished_at TEXT,
    summary_json TEXT
);

CREATE TABLE evaluation_case (
    id TEXT PRIMARY KEY,
    evaluation_run_id TEXT NOT NULL REFERENCES evaluation_run(id) ON DELETE CASCADE,
    question_id TEXT NOT NULL,
    system_id TEXT NOT NULL,
    run_number INTEGER NOT NULL CHECK (run_number > 0),
    research_run_id TEXT REFERENCES run(id) ON DELETE SET NULL,
    status TEXT NOT NULL CHECK (
        status IN ('pending', 'running', 'completed', 'failed')
    ),
    metrics_json TEXT,
    error_code TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (evaluation_run_id, question_id, system_id, run_number)
);

CREATE TABLE evaluation_result (
    id TEXT PRIMARY KEY,
    evaluation_case_id TEXT NOT NULL REFERENCES evaluation_case(id) ON DELETE CASCADE,
    metric_name TEXT NOT NULL,
    metric_value REAL,
    metric_unit TEXT,
    details_json TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (evaluation_case_id, metric_name)
);

CREATE INDEX idx_research_question_project ON research_question(project_id);
CREATE INDEX idx_run_project_status ON run(project_id, status, started_at);
CREATE INDEX idx_run_question ON run(question_id);
CREATE INDEX idx_plan_run ON plan(run_id);
CREATE INDEX idx_plan_step_plan ON plan_step(plan_id);
CREATE INDEX idx_query_run ON query(run_id);
CREATE INDEX idx_source_call_run ON source_call(run_id);
CREATE INDEX idx_source_call_query ON source_call(query_id);
CREATE INDEX idx_source_call_attempt_call ON source_call_attempt(source_call_id);
CREATE INDEX idx_source_record_source ON source_record(source, source_record_id);
CREATE INDEX idx_paper_title_year ON paper(title_normalized, year);
CREATE INDEX idx_paper_identifier_paper ON paper_identifier(paper_id);
CREATE INDEX idx_paper_author_paper ON paper_author(paper_id);
CREATE INDEX idx_paper_source_record_source ON paper_source_record(source_record_id);
CREATE INDEX idx_file_paper ON file(paper_id);
CREATE INDEX idx_document_file ON document(file_id);
CREATE INDEX idx_evidence_paper ON evidence_span(paper_id);
CREATE INDEX idx_evidence_source_record ON evidence_span(source_record_id);
CREATE INDEX idx_evidence_document ON evidence_span(document_id);
CREATE INDEX idx_claim_report ON claim(report_id);
CREATE INDEX idx_claim_evidence_evidence ON claim_evidence(evidence_span_id);
CREATE INDEX idx_audit_run ON audit_event(run_id);
CREATE INDEX idx_model_call_run ON model_call(run_id);
CREATE INDEX idx_step_attempt_step ON step_attempt(step_id);
CREATE INDEX idx_note_project ON note(project_id);
CREATE INDEX idx_evaluation_case_run ON evaluation_case(evaluation_run_id);
CREATE INDEX idx_evaluation_case_status ON evaluation_case(status, system_id);
CREATE INDEX idx_evaluation_result_case ON evaluation_result(evaluation_case_id);

CREATE VIRTUAL TABLE paper_fts USING fts5(
    title,
    abstract,
    venue,
    authors_text,
    content = '', contentless_delete = 1
);

CREATE TRIGGER paper_fts_ai AFTER INSERT ON paper BEGIN
    INSERT INTO paper_fts(rowid, title, abstract, venue, authors_text)
    VALUES (
        new.rowid,
        new.title,
        COALESCE(new.abstract, ''),
        COALESCE(new.venue, ''),
        ''
    );
END;

CREATE TRIGGER paper_fts_ad AFTER DELETE ON paper BEGIN
    DELETE FROM paper_fts WHERE rowid = old.rowid;
END;

CREATE TRIGGER paper_fts_au AFTER UPDATE ON paper BEGIN
    DELETE FROM paper_fts WHERE rowid = old.rowid;
    INSERT INTO paper_fts(rowid, title, abstract, venue, authors_text)
    VALUES (
        new.rowid,
        new.title,
        COALESCE(new.abstract, ''),
        COALESCE(new.venue, ''),
        ''
    );
END;

CREATE VIRTUAL TABLE evidence_fts USING fts5(
    quote,
    section,
    paper_title,
    content = '', contentless_delete = 1
);

CREATE TRIGGER evidence_fts_ai AFTER INSERT ON evidence_span BEGIN
    INSERT INTO evidence_fts(rowid, quote, section, paper_title)
    SELECT
        new.rowid,
        new.quote,
        COALESCE(json_extract(new.locator_json, '$.section'), ''),
        COALESCE(paper.title, '')
    FROM paper
    WHERE paper.id = new.paper_id;
END;

CREATE TRIGGER evidence_fts_ad AFTER DELETE ON evidence_span BEGIN
    DELETE FROM evidence_fts WHERE rowid = old.rowid;
END;

CREATE TRIGGER evidence_fts_au AFTER UPDATE ON evidence_span BEGIN
    DELETE FROM evidence_fts WHERE rowid = old.rowid;
    INSERT INTO evidence_fts(rowid, quote, section, paper_title)
    SELECT
        new.rowid,
        new.quote,
        COALESCE(json_extract(new.locator_json, '$.section'), ''),
        COALESCE(paper.title, '')
    FROM paper
    WHERE paper.id = new.paper_id;
END;

CREATE VIRTUAL TABLE note_fts USING fts5(
    title,
    body_text,
    content = '', contentless_delete = 1
);

CREATE TRIGGER note_fts_ai AFTER INSERT ON note BEGIN
    INSERT INTO note_fts(rowid, title, body_text)
    VALUES (new.rowid, new.title, COALESCE(new.body_text, ''));
END;

CREATE TRIGGER note_fts_ad AFTER DELETE ON note BEGIN
    DELETE FROM note_fts WHERE rowid = old.rowid;
END;

CREATE TRIGGER note_fts_au AFTER UPDATE ON note BEGIN
    DELETE FROM note_fts WHERE rowid = old.rowid;
    INSERT INTO note_fts(rowid, title, body_text)
    VALUES (new.rowid, new.title, COALESCE(new.body_text, ''));
END;

CREATE TRIGGER source_record_no_update
BEFORE UPDATE ON source_record
BEGIN
    SELECT RAISE(ABORT, 'source_record is immutable');
END;

CREATE TRIGGER source_record_no_delete
BEFORE DELETE ON source_record
BEGIN
    SELECT RAISE(ABORT, 'source_record is immutable');
END;

CREATE TRIGGER audit_event_no_update
BEFORE UPDATE ON audit_event
BEGIN
    SELECT RAISE(ABORT, 'audit_event is immutable');
END;

CREATE TRIGGER audit_event_no_delete
BEFORE DELETE ON audit_event
BEGIN
    SELECT RAISE(ABORT, 'audit_event is immutable');
END;