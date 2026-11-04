"""Trace-Gate multipage Streamlit frontend."""

import streamlit as st
from database.connection import initialize_database
from ui import apply_styles, footer

st.set_page_config(
    page_title="Trace-Gate | Procurement Workspace",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_resource(show_spinner=False)
def setup_database():
    initialize_database()
    return True

setup_database()
apply_styles()

with st.sidebar:
    st.markdown("""
<div class="tg-brand">
  <div class="tg-logo">✦</div>
  <div><div class="tg-brand-name">tracegate<span style="color:#6A5AE6">.</span></div>
  <div class="tg-brand-small">PROCUREMENT OS</div></div>
</div>
""", unsafe_allow_html=True)
    st.caption("WORKSPACE")

pages = [
    st.Page("pages/procurement_dashboard.py", title="Overview", icon=":material/dashboard:", default=True),
    st.Page("pages/vendor_portal.py", title="Vendor onboarding", icon=":material/domain_add:"),
    st.Page("pages/application_review.py", title="Review queue", icon=":material/fact_check:"),
    st.Page("pages/application_history.py", title="Audit & history", icon=":material/history:"),
]

pg = st.navigation(pages, position="sidebar")
with st.sidebar:
    st.markdown('<div class="tg-side-note">● LOCAL DEMO WORKSPACE<br>Versioned submissions · Audit trail<br>No user authentication enabled</div>', unsafe_allow_html=True)
pg.run()
footer()
