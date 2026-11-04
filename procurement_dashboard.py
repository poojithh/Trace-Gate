"""Procurement operations overview. Read-only except navigation links."""

from collections import Counter
import pandas as pd
import streamlit as st

from database import repositories
from ui import hero, section, pill, info_card, safe

hero("OPERATIONS OVERVIEW", "Procurement, at a glance.",
     "A clear view of onboarding throughput, applications that need attention, and your vendor portfolio.", "◉")

vendors = repositories.list_vendors()
applications = repositories.list_applications()
counts = Counter(a["current_status"] for a in applications)

m1,m2,m3,m4 = st.columns(4)
m1.metric("Total vendors", len(vendors))
m2.metric("Applications", len(applications))
m3.metric("Pending review", counts.get("PENDING",0))
m4.metric("Approved", counts.get("APPROVED",0))

section("Workflow health")
left,right = st.columns([1.55,1], gap="large")
with left:
    with st.container(border=True):
        st.markdown("**Application decision distribution**")
        if applications:
            distribution = pd.DataFrame({"Status":["DRAFT","SUBMITTED","PENDING","APPROVED","REJECTED","WITHDRAWN"],
                                         "Applications":[counts.get(s,0) for s in ["DRAFT","SUBMITTED","PENDING","APPROVED","REJECTED","WITHDRAWN"]]})
            st.bar_chart(distribution.set_index("Status"), y="Applications", color="#6B62E9", height=250)
        else:
            st.info("No application data yet. Create a vendor and submit an application to see the dashboard.")
with right:
    info_card("Needs attention", f"{counts.get('PENDING',0)} application(s) are pending corrections or review.")
    info_card("Verified in the engine", f"{counts.get('APPROVED',0)} application(s) have an APPROVED automated decision. This is not government verification.")
    info_card("Review notes", "The review queue stores procurement actions separately. No role-based authentication is configured in this demo.")

section("Application register")
if not applications:
    st.info("Your application register is empty. Start from Vendor onboarding.")
    st.page_link("pages/vendor_portal.py", label="Open vendor onboarding", icon=":material/arrow_forward:")
else:
    a,b = st.columns([1,2])
    with a:
        status_filter = st.selectbox("Filter by status", ["All statuses","PENDING","APPROVED","REJECTED","DRAFT","SUBMITTED","WITHDRAWN"])
    with b:
        query = st.text_input("Search vendor or application ID", placeholder="Search all applications…")
    filtered = [item for item in applications if
                (status_filter == "All statuses" or item["current_status"] == status_filter) and
                (not query or query.lower() in (item["company_name"] + " " + item["application_id"]).lower())]
    rows = [{"Vendor":a["company_name"],"Application ID":a["application_id"],"Status":a["current_status"],
             "Country":a.get("country",""), "Updated":a.get("updated_at","")} for a in filtered]
    if rows:
        st.dataframe(rows, hide_index=True, use_container_width=True)
    else:
        st.info("No applications match these filters.")
    st.caption("Choose Review queue to inspect validations, or Audit & history to inspect versions and events.")
