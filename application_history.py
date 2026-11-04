"""Submission version comparison and audit history browser."""

import pandas as pd
import streamlit as st
from database import repositories
from core.version_comparison import compare_versions, identify_affected_categories
from ui import hero, section, pill

hero("AUDIT & TRACEABILITY", "Every change. Fully visible.",
     "Explore immutable submissions, compare revisions and trace the decisions made throughout the onboarding lifecycle.", "↺")

apps = repositories.list_applications()
if not apps:
    st.info("No application history yet. Create and submit a vendor application first.")
else:
    labels = {f"{a['company_name']} · {a['application_id']}":a for a in apps}
    selected = st.selectbox("Select application", list(labels))
    app = labels[selected]
    app_id = app["application_id"]
    versions = repositories.list_versions(app_id)
    events = repositories.get_audit_history(app_id)
    m1,m2,m3 = st.columns(3)
    m1.metric("Submission versions", len(versions))
    m2.metric("Audit events", len(events))
    m3.metric("Current status", app["current_status"])

    section("Version explorer")
    if versions:
        versions_by_number = {int(v["version_number"]):v for v in versions}
        number = st.selectbox("Inspect version", list(versions_by_number))
        version = versions_by_number[number]
        st.caption(f"Version ID: {version['version_id']}  ·  Submitted: {version['submitted_at']}")
        with st.expander("Submitted data (contains financial details)"):
            st.warning("These records may contain bank account information. This demo lacks access controls.")
            st.json(version["submitted_data"])
        st.markdown("**Recorded validations**")
        results = repositories.get_validation_results(version["version_id"])
        if results:
            st.dataframe([{"Rule":r["rule_id"],"Outcome":r["outcome"],"Reason":r["reason"]} for r in results], hide_index=True, use_container_width=True)
        else:
            st.caption("No validation records available.")
        section("Compare revisions")
        if len(versions) < 2:
            st.info("Submit a second version to unlock comparisons.")
        else:
            cols = st.columns(2)
            with cols[0]:
                older = st.selectbox("From version", sorted(versions_by_number)[:-1], index=0)
            with cols[1]:
                newer_choices = [k for k in sorted(versions_by_number) if k > older]
                newer = st.selectbox("To version", newer_choices, index=len(newer_choices)-1)
            comparison = compare_versions(versions_by_number[older]["submitted_data"], versions_by_number[newer]["submitted_data"])
            affected = identify_affected_categories(comparison)
            st.markdown("**Affected validation categories**")
            st.write(", ".join(map(str, affected)) if affected else "No mapped categories")
            with st.expander("Detailed version difference", expanded=True):
                st.json(comparison)
    else:
        st.info("No submitted version exists for this application.")

    section("Audit event timeline")
    if events:
        st.dataframe([{"Event":e["event_type"],"Timestamp":e["timestamp"],"Version ID":e.get("version_id") or "—", "Details":str(e.get("event_details",{}))} for e in events], hide_index=True, use_container_width=True)
    else:
        st.caption("No audit events recorded.")
