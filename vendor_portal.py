"""Vendor registration, validation, submission and file upload UI."""

import streamlit as st

from database import repositories
from services.application_service import check_readiness, submit_application
from services.document_service import save_uploaded_document
from ui import hero, section, steps, info_card, safe

REQUIRED_DOCS = {
    "business_registration": "Business registration",
    "tax_certificate": "Tax certificate",
    "bank_proof": "Bank account proof",
}

hero("VENDOR ONBOARDING", "Your suppliers, confidently onboarded.",
     "Register companies, validate financial and compliance information, and manage supporting evidence in one place.", "◈")

step_register, step_submit, step_docs = st.tabs([
    "01  Register", "02  Validate & submit", "03  Documents"
])

with step_register:
    steps(1)
    left, right = st.columns([1.8, 1], gap="large")
    with left:
        section("Create a vendor profile")
        with st.form("tg_register_vendor"):
            name = st.text_input("Legal company name *", placeholder="e.g. Acme Components Pvt Ltd")
            a,b = st.columns(2)
            with a:
                country = st.selectbox("Country *", ["India", "United States", "United Kingdom"])
                business = st.text_input("Business type *", placeholder="Private Limited")
                person = st.text_input("Primary contact *", placeholder="Contact name")
            with b:
                category = st.text_input("Vendor category *", placeholder="Manufacturing")
                email = st.text_input("Business email *", placeholder="contact@example.com")
                phone = st.text_input("Phone (optional)")
            clicked = st.form_submit_button("Create vendor profile", type="primary", use_container_width=True)
        if clicked:
            values = [name, business, category, person, email]
            if any(not value.strip() for value in values):
                st.error("Complete every field marked with *.")
            elif "@" not in email or "." not in email.split("@")[-1]:
                st.error("Enter a valid-looking business email.")
            else:
                try:
                    vendor_id = repositories.create_vendor({
                        "company_name":name.strip(), "country":country,
                        "business_type":business.strip(), "vendor_category":category.strip(),
                        "contact_person":person.strip(), "email":email.strip(), "phone":phone.strip(),
                    })
                    st.session_state["tg_vendor_id"] = vendor_id
                    st.success(f"Vendor created · {vendor_id}")
                    st.info("Continue to 'Validate & submit' to begin an application.")
                except Exception as exc:
                    st.error(f"Registration failed: {exc}")
    with right:
        section("What happens next?")
        info_card("01 · Verify details", "Supply tax and banking information. The validator flags incomplete or inconsistent fields.")
        info_card("02 · Create a version", "Each submission is preserved with an immutable application version and an audit event.")
        info_card("03 · Attach evidence", "Upload required files against a specific submission version. Documents begin as NOT_CHECKED.")
        info_card("Demo note", "This local portal has no authentication or vendor access isolation. Use synthetic data only.")

with step_submit:
    steps(2)
    section("Application details")
    vendors = repositories.list_vendors()
    if not vendors:
        st.info("No vendor profiles yet. Register a vendor in the first tab.")
    else:
        vendor_map = {f"{v['company_name']} · {v['vendor_id']}":v for v in vendors}
        current_key = next((k for k,v in vendor_map.items() if v['vendor_id'] == st.session_state.get('tg_vendor_id')), next(iter(vendor_map)))
        choice = st.selectbox("Choose a vendor", list(vendor_map), index=list(vendor_map).index(current_key))
        vendor = vendor_map[choice]
        vendor_id = vendor["vendor_id"]
        existing = [x for x in repositories.list_applications() if x["vendor_id"] == vendor_id]
        options = {"New application":None}
        options.update({f"Resubmit {item['application_id']} ({item['current_status']})":item['application_id'] for item in existing})
        app_choice = st.selectbox("Submission mode", list(options))
        application_id = options[app_choice]
        defaults = {}
        if application_id:
            old = repositories.get_latest_version(application_id)
            defaults = old["submitted_data"] if old else {}
        st.caption("Resubmission creates a new immutable version. Previously uploaded files are not automatically carried into the new version.")
        with st.form("tg_application_form"):
            section("Company information")
            a,b = st.columns(2)
            with a:
                company_name = st.text_input("Company name", value=defaults.get("company_name", vendor["company_name"]))
                country = st.text_input("Country", value=defaults.get("country", vendor["country"]))
            with b:
                business_type = st.text_input("Business type", value=defaults.get("business_type",vendor["business_type"]))
                category = st.text_input("Vendor category", value=defaults.get("vendor_category",vendor["vendor_category"]))
            section("Tax & banking information")
            c,d = st.columns(2)
            with c:
                tax_id = st.text_input("Tax identifier", value=defaults.get("tax_id",""), placeholder="Format-valid synthetic ID for demo")
                bank_name = st.text_input("Bank account holder", value=defaults.get("bank_account_name",""))
            with d:
                bank_number = st.text_input("Bank account number", value=defaults.get("bank_account_number",""))
                bank_country = st.text_input("Bank country", value=defaults.get("bank_country",vendor["country"]))
            st.info("Document evidence isn't considered present until the document workflow is integrated with verification. This submission declares no attached documents, so it normally remains PENDING.")
            preview, submit = st.columns(2)
            with preview:
                validate_click = st.form_submit_button("Run readiness checks", use_container_width=True)
            with submit:
                submit_click = st.form_submit_button("Submit application", type="primary", use_container_width=True)

        data = {
            "company_name":company_name.strip(), "country":country.strip(),
            "business_type":business_type.strip(), "vendor_category":category.strip(),
            "tax_id":tax_id.strip(), "bank_account_name":bank_name.strip(),
            "bank_account_number":bank_number.strip(), "bank_country":bank_country.strip(),
            "documents":[],
        }
        if validate_click or submit_click:
            try:
                result = submit_application(vendor_id, data, application_id=application_id) if submit_click else check_readiness(data)
                if submit_click:
                    st.session_state["tg_last_application"] = result["application_id"]
                    st.session_state["tg_last_version"] = result["version_id"]
                    st.success(f"Application version {result['version_number']} saved successfully.")
                section("Validation summary")
                m1,m2,m3 = st.columns(3)
                m1.metric("Engine decision", result["decision"]["decision"])
                m2.metric("Vendor corrections", result["corrections"]["total_corrections"])
                m3.metric("Rules evaluated", len(result["validation_results"]))
                if submit_click:
                    st.code(result["application_id"], language=None)
                blockers = [r for r in result["validation_results"] if r["outcome"] in ("FAIL", "REVIEW")]
                if blockers:
                    st.dataframe([{"Rule":r["rule_id"], "Outcome":r["outcome"], "Reason":r["reason"]} for r in blockers], hide_index=True, use_container_width=True)
                else:
                    st.success("No validation blockers in the submitted metadata.")
                with st.expander("Full validation details"):
                    st.dataframe(result["validation_results"], hide_index=True, use_container_width=True)
                if submit_click:
                    st.info("Continue to Documents to attach files to this exact submission version. Uploading files won't automatically recompute the engine decision.")
            except Exception as exc:
                st.error(f"Could not complete the operation: {exc}")

with step_docs:
    steps(3)
    section("Attach supporting evidence")
    st.caption("Choose any existing application version. File metadata is stored separately from the submitted form payload.")
    applications = repositories.list_applications()
    if not applications:
        st.info("Create an application before uploading documents.")
    else:
        labels = {f"{a['company_name']} · {a['application_id']}":a for a in applications}
        preferred = st.session_state.get("tg_last_application")
        initial = next((k for k,v in labels.items() if v["application_id"] == preferred), next(iter(labels)))
        app_key = st.selectbox("Application", list(labels), index=list(labels).index(initial), key="tg_doc_app")
        target_app = labels[app_key]["application_id"]
        versions = repositories.list_versions(target_app)
        if not versions:
            st.warning("No submitted versions exist for this application.")
        else:
            vmap = {f"Version {v['version_number']} · {v['version_id']}":v for v in versions}
            v_key = st.selectbox("Submission version", list(vmap), key="tg_doc_version")
            version_id = vmap[v_key]["version_id"]
            st.info("File uploads use a basic signature check and are registered as NOT_CHECKED. Never upload real confidential documents to this unauthenticated demo.")
            for doc_type, label in REQUIRED_DOCS.items():
                with st.container(border=True):
                    left, right = st.columns([2.5,1], gap="large")
                    with left:
                        st.markdown(f"**{label}**")
                        upload = st.file_uploader(f"Select {label}", type=["pdf","png","jpg","jpeg"], key=f"tg_upload_{version_id}_{doc_type}", label_visibility="collapsed")
                    with right:
                        st.write("")
                        if st.button(f"Save {label}", key=f"tg_save_{version_id}_{doc_type}", use_container_width=True):
                            if upload is None:
                                st.warning("Choose a file first.")
                            else:
                                try:
                                    saved = save_uploaded_document(version_id, doc_type, upload)
                                    st.success(f"Stored · {saved['document_id']}")
                                except Exception as exc:
                                    st.error(f"Upload failed: {exc}")
            section("Registered files")
            docs = repositories.get_documents(version_id)
            if docs:
                st.dataframe([{"Type":d["document_type"],"Filename":d["filename"],"Verification":d["validation_status"],"Uploaded at":d["uploaded_at"]} for d in docs], hide_index=True, use_container_width=True)
            else:
                st.caption("No files have been uploaded to this version.")
            st.warning("Document status and application approval are not yet synchronized. This is a document intake demonstration, not document verification.")
