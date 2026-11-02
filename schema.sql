PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS vendors (
    vendor_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    country TEXT NOT NULL,
    business_type TEXT NOT NULL,
    vendor_category TEXT NOT NULL,
    contact_person TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS applications (
    application_id TEXT PRIMARY KEY,
    vendor_id TEXT NOT NULL,
    current_status TEXT NOT NULL DEFAULT 'DRAFT'
        CHECK (current_status IN ('DRAFT','SUBMITTED','APPROVED','PENDING','REJECTED','WITHDRAWN')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS submission_versions (
    version_id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    version_number INTEGER NOT NULL CHECK (version_number >= 1),
    submitted_data TEXT NOT NULL CHECK (json_valid(submitted_data)),
    submitted_at TEXT NOT NULL,
    UNIQUE (application_id, version_number),
    FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL,
    document_type TEXT NOT NULL,
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    validation_status TEXT NOT NULL DEFAULT 'NOT_CHECKED'
        CHECK (validation_status IN ('NOT_CHECKED','VALID','INVALID','REVIEW_REQUIRED')),
    uploaded_at TEXT NOT NULL,
    FOREIGN KEY (version_id) REFERENCES submission_versions(version_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS validation_results (
    result_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    rule_name TEXT NOT NULL,
    category TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK (outcome IN ('PASS','FAIL','REVIEW','NOT_APPLICABLE')),
    reason TEXT NOT NULL,
    checked_at TEXT NOT NULL,
    FOREIGN KEY (version_id) REFERENCES submission_versions(version_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS correction_items (
    correction_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL,
    field_name TEXT NOT NULL,
    issue TEXT NOT NULL,
    requested_action TEXT NOT NULL,
    resolution_status TEXT NOT NULL DEFAULT 'OPEN'
        CHECK (resolution_status IN ('OPEN','RESOLVED','CARRIED_FORWARD','CANCELLED')),
    created_at TEXT NOT NULL,
    resolved_at TEXT,
    FOREIGN KEY (version_id) REFERENCES submission_versions(version_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS review_records (
    review_id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    version_id TEXT NOT NULL,
    reviewer_action TEXT NOT NULL
        CHECK (reviewer_action IN ('APPROVE','REQUEST_CORRECTION','REJECT','ESCALATE')),
    internal_notes TEXT,
    reviewed_at TEXT NOT NULL,
    FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE RESTRICT,
    FOREIGN KEY (version_id) REFERENCES submission_versions(version_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS audit_logs (
    event_id TEXT PRIMARY KEY,
    application_id TEXT NOT NULL,
    version_id TEXT,
    event_type TEXT NOT NULL,
    event_details TEXT NOT NULL DEFAULT '{}'
        CHECK (json_valid(event_details)),
    timestamp TEXT NOT NULL,
    FOREIGN KEY (application_id) REFERENCES applications(application_id) ON DELETE RESTRICT,
    FOREIGN KEY (version_id) REFERENCES submission_versions(version_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_applications_vendor ON applications(vendor_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(current_status);
CREATE INDEX IF NOT EXISTS idx_versions_application ON submission_versions(application_id, version_number);
CREATE INDEX IF NOT EXISTS idx_documents_version ON documents(version_id);
CREATE INDEX IF NOT EXISTS idx_validation_version ON validation_results(version_id);
CREATE INDEX IF NOT EXISTS idx_corrections_version ON correction_items(version_id);
CREATE INDEX IF NOT EXISTS idx_reviews_application ON review_records(application_id);
CREATE INDEX IF NOT EXISTS idx_audit_application_time ON audit_logs(application_id, timestamp);

CREATE TRIGGER IF NOT EXISTS prevent_submission_version_update
BEFORE UPDATE ON submission_versions
BEGIN
    SELECT RAISE(ABORT, 'Submission versions are immutable; create a new version.');
END;

CREATE TRIGGER IF NOT EXISTS prevent_submission_version_delete
BEFORE DELETE ON submission_versions
BEGIN
    SELECT RAISE(ABORT, 'Submission versions cannot be deleted.');
END;
