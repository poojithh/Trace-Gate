"""Application review workspace with auditable recommendations (not status overrides)."""

from contextlib import closing
import streamlit as st

from database import repositories
from ui import hero, section, pill, safe, info_card

hero("PROCUREMENT REVIEW", "A more confident review desk.",
     "Inspect the latest validation findings, supporting documents and reviewer history before recording a procurement recommendation.", "◇")

apps = repositories.list_applications()
if not apps:
    st.info("No applications yet. Register a vendor and submit an application first.")
else:
    labels = {f"{a['company_name']} · {a['application_id']}":a for a in apps}
    selection = st.selectbox("Application to review", list(labels))
    app = labels[selection]
    app_id = app["application_id"]
    latest = repositories.get_latest_version(app_id)
    st.markdown(f"<p>Current automated status: {pill(app['current_status'])}</p>", unsafe_allow_html=True)
    if not latest:
        st.warning("This application has no submitted version yet.")
    else:
        vid = latest["version_id"]
        results = repositories.get_validation_results(vid)
        corrections = repositories.get_correction_items(vid)
        docs = repositories.get_documents(vid)
        failures = [x for x in results if x["outcome"] == "FAIL"]
        reviews = [x for x in results if x["outcome"] == "REVIEW"]
        a,b,c,d = st.columns(4)
        a.metric("Version", latest["version_number"])
        b.metric("Failed rules", len(failures))
        c.metric("Manual review flags", len(reviews))
        d.metric("Document records", len(docs))
        section("Evidence and validation")
        t1,t2,t3 = st.tabs(["Validation checks","Correction requests","Documents"])
        with t1:
            if results:
                st.dataframe([{"Rule":r["rule_id"],"Category":r["category"],"Result":r["outcome"],"Finding":r["reason"]} for r in results], hide_index=True, use_container_width=True)
            else:
                st.warning("No validation results stored for this version.")
        with t2:
            if corrections:
                st.dataframe([{"Field":c["field_name"],"Issue":c["issue"],"Action":c["requested_action"],"Resolution":c["resolution_status"]} for c in corrections], hide_index=True, use_container_width=True)
            else:
                st.success("No vendor correction requests for this version.")
        with t3:
            if docs:
                st.dataframe([{"Type":x["document_type"],"Filename":x["filename"],"Status":x["validation_status"]} for x in docs], hide_index=True, use_container_width=True)
            else:
                st.warning("No uploaded document records exist for this version.")
            st.caption("NOT_CHECKED does not mean verified. The engine's existing decision does not automatically incorporate later uploads.")

        section("Record a reviewer recommendation")
        st.info("Demo workflow: review actions are logged as records and audit events, but do not override the automated application status. There is no reviewer authentication in this version.")
        with st.form("tg_reviewer_form"):
            action = st.selectbox("Recommendation", ["REQUEST_CORRECTION","ESCALATE","APPROVE","REJECT"], format_func=lambda x: x.replace("_"," ").title())
            notes = st.text_area("Internal notes", placeholder="Summarize findings and rationale (avoid confidential data in this demo)", height=125)
            confirmation = st.checkbox("I understand this records a recommendation and does not change the application status.")
            submit = st.form_submit_button("Record recommendation", type="primary")
        if submit:
            if not confirmation:
                st.error("Confirm the review action before saving.")
            elif not notes.strip():
                st.error("Add an internal review note.")
            else:
                try:
                    # Both writes participate in one database transaction.
                    with closing(repositories.get_connection()) as conn:
                        with conn:
                            conn.execute("BEGIN IMMEDIATE")
                            review_id = repositories.create_review_record(
                                app_id, vid, action, notes.strip(), conn=conn
                            )
                            repositories.log_event(
                                app_id, "REVIEW_RECOMMENDATION_RECORDED",
                                {"review_id":review_id, "reviewer_action":action},
                                version_id=vid, conn=conn,
                            )
                    st.success(f"Recommendation saved · {review_id}")
                except TypeError:
                    st.error("Your create_review_record repository function needs optional conn=None support before atomic review logging. No review was saved by this action.")
                except Exception as exc:
                    st.error(f"Could not save review: {exc}")
        section("Review timeline")
        try:
            records = repositories.get_review_records(app_id)
            if records:
                st.dataframe([{"Action":r["reviewer_action"],"Notes":r.get("internal_notes", ""),"Date":r["reviewed_at"],"Version ID":r["version_id"]} for r in records], hide_index=True, use_container_width=True)
            else:
                st.caption("No recorded reviewer recommendations.")
        except Exception as exc:
            st.error(f"Could not load review records: {exc}")
