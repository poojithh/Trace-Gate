# Trace-Gate UI v2 — light procurement workspace

## Install

The package overlays the UI files only. It intentionally does not include your backend, database or uploads.

From your Codespaces `tracegate` directory:

1. Back up any customized frontend files (`app.py`, `pages/*.py`, `ui.py`, `.streamlit/config.toml`).
2. Extract this zip into that directory, keeping the internal folder structure.
3. Ensure Streamlit and pandas are available; your Streamlit 1.66.1 environment already has them.
4. **Review the repository compatibility note below.**
5. Run `python -m compileall -q app.py ui.py pages` and `python -m pytest tests/ -q`.
6. Run `python -m streamlit run app.py --server.address 0.0.0.0` and use Codespaces forwarded port 8501.

## Compatibility note for procurement review

The review page records reviewer recommendations atomically with their audit events. Its `create_review_record` call requires this repository signature:

```python
def create_review_record(application_id, version_id, reviewer_action, internal_notes=None, conn=None):
```

And inside it, the SQL write should use `with write_connection(conn) as db:` followed by `db.execute(...)`, instead of opening its own connection. Your `log_event` already accepts `conn`.

If you have not added that optional connection, the review page displays a compatibility error and does not save the recommendation. The rest of the UI remains usable.

## Critical scope notes

- This is a **local prototype**, not a production vendor portal. No sign-in, access control or secrets handling is implemented.
- Vendor-created submissions declare `documents: []`; this conservatively leaves them `PENDING` until document status and validation are integrated.
- Files uploaded after submission are associated with the chosen version, but they **do not trigger revalidation or automatic approval**.
- `NOT_CHECKED` means that upload metadata exists, **not** that a document has been verified.
- `APPROVE` and `REJECT` in the review UI are **recommendations recorded in review_records**, not actions that change the automated application status.
- The frontend intentionally does not display potentially sensitive internal compliance reasons in vendor corrections beyond what the existing correction engine already exposes.
- Avoid entering real company financial information or confidential documents while this prototype is unauthenticated.

## Files

- `app.py` — app shell and navigation
- `ui.py` — light theme and reusable UI primitives
- `.streamlit/config.toml` — Streamlit theme
- `pages/vendor_portal.py` — registration, submission, document intake
- `pages/procurement_dashboard.py` — metrics and application register
- `pages/application_review.py` — review workspace and recommendation logging
- `pages/application_history.py` — versions, comparisons, audit
