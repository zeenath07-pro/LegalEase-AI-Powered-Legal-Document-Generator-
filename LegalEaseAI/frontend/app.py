
import html
import os
from io import BytesIO

import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from backend.formatters.documents import (
    format_txt,
    format_docx,
    format_pdf,
)


load_dotenv()

st.set_page_config(
    page_title="LegalEase | Legal Draft Generator",
    page_icon="⚖️",
    layout="wide",
)


# -------------------------------------------------
# PAGE STYLING
# -------------------------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background: #0b1220;
        color: #edf2ff;
    }

    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
    }

    .preview {
        background: #17243b;
        border: 1px solid #3c526f;
        border-radius: 12px;
        padding: 20px;
        white-space: pre-wrap;
        overflow-wrap: anywhere;
        max-height: 550px;
        overflow-y: auto;
        line-height: 1.65;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------------
# HEADER
# -------------------------------------------------

st.title("⚖️ LegalEase")

st.caption(
    "AI-powered legal document drafting | "
    "Preview | Edit | Export"
)

st.warning(
    "Drafting assistant only, not legal advice. "
    "Verify all details and obtain jurisdiction-specific "
    "legal review before using generated documents."
)


# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

with st.sidebar:
    st.header("Branding & Settings")

    logo_file = st.file_uploader(
        "Optional company logo",
        type=["png", "jpg", "jpeg"],
    )

    logo = None

    if logo_file:
        try:
            image = Image.open(logo_file)
            image.verify()

            logo_file.seek(0)

            image = Image.open(logo_file).convert("RGBA")

            if image.width * image.height > 8_000_000:
                st.error(
                    "Logo image dimensions are too large."
                )
            else:
                buffer = BytesIO()

                image.save(
                    buffer,
                    format="PNG",
                )

                logo = buffer.getvalue()

        except Exception:
            st.error(
                "Invalid logo. Upload a PNG or JPG image."
            )

    if logo and len(logo) > 2_000_000:
        st.error(
            "Logo must be smaller than 2 MB."
        )
        logo = None

    if logo:
        st.image(
            logo,
            width=100,
        )

    backend_url = st.text_input(
        "Backend URL",
        value=os.getenv(
            "BACKEND_URL",
            "http://127.0.0.1:8000",
        ),
    )


# -------------------------------------------------
# DOCUMENT INPUT FORM
# -------------------------------------------------

with st.form("draft_form"):
    left, right = st.columns(2)

    with left:
        doc_type = st.selectbox(
            "Document Type",
            [
                "Non-Disclosure Agreement",
                "Employment Contract",
                "Lease Agreement",
                "Freelance Work Contract",
                "Employment Offer Letter",
                "Other",
            ],
        )

        if doc_type == "Other":
            doc_type = st.text_input(
                "Custom Document Type"
            )

        parties = st.text_area(
            "Parties and Roles",
            placeholder=(
                "Jane Doe (Service Provider), "
                "TechNova Inc. (Client)"
            ),
            height=110,
        )

        dates = st.text_input(
            "Effective Date / Relevant Dates",
            placeholder="April 15, 2027",
        )

    with right:
        terms = st.text_area(
            "Terms and Conditions",
            placeholder=(
                "Payment within 30 days; "
                "Confidentiality for 2 years; "
                "15 days notice"
            ),
            help="Separate individual terms with semicolons.",
            height=145,
        )

        jurisdiction = st.text_input(
            "Jurisdiction (Optional)",
            placeholder="Tamil Nadu, India",
        )

        additional = st.text_area(
            "Additional Drafting Preferences",
            height=75,
        )

    submitted = st.form_submit_button(
        "Generate Document",
        type="primary",
        use_container_width=True,
    )


# -------------------------------------------------
# GENERATE DOCUMENT
# -------------------------------------------------

if submitted:
    payload = {
        "document_type": doc_type,
        "parties": parties,
        "terms": terms,
        "dates": dates,
        "jurisdiction": (
            jurisdiction or "Not specified"
        ),
        "additional_instructions": additional,
    }

    required_fields = (
        "document_type",
        "parties",
        "terms",
        "dates",
    )

    if not all(
        str(payload[field]).strip()
        for field in required_fields
    ):
        st.error(
            "Complete the document type, parties, "
            "terms and dates before generating."
        )

    else:
        try:
            with st.spinner(
                "Generating your legal document..."
            ):
                response = requests.post(
                    backend_url.rstrip("/") + "/generate",
                    json=payload,
                    timeout=120,
                )

                response.raise_for_status()

            st.session_state.document = (
                response.json()["document"]
            )

            st.session_state.doc_type = doc_type
            st.session_state.terms = terms
            st.session_state.editing = False

            st.success(
                "Document generated successfully!"
            )

        except requests.exceptions.HTTPError:
            try:
                message = response.json().get(
                    "detail",
                    response.text,
                )
            except ValueError:
                message = response.text

            st.error(
                f"Generation failed: {message}"
            )

        except requests.exceptions.RequestException as exc:
            st.error(
                "Cannot connect to the backend. "
                "Start FastAPI first and check the URL. "
                f"Details: {exc}"
            )


# -------------------------------------------------
# PREVIEW AND EDIT DOCUMENT
# -------------------------------------------------

if st.session_state.get("document"):
    st.divider()

    st.subheader("Document Preview")

    editing = st.toggle(
        "Edit Document",
        value=st.session_state.get(
            "editing",
            False,
        ),
    )

    st.session_state.editing = editing

    if editing:
        st.session_state.document = st.text_area(
            "Edit Your Generated Draft",
            value=st.session_state.document,
            height=450,
        )

    else:
        safe_document = html.escape(
            st.session_state.document
        )

        st.markdown(
            (
                '<div class="preview">'
                f"{safe_document}"
                "</div>"
            ),
            unsafe_allow_html=True,
        )

    text = st.session_state.document

    filename = "".join(
        character if character.isalnum() else "_"
        for character in st.session_state.doc_type
    ).strip("_").lower()

    if not filename:
        filename = "legal_document"


    # ---------------------------------------------
    # DOWNLOAD BUTTONS
    # ---------------------------------------------

    st.subheader("Download Your Document")

    col1, col2, col3 = st.columns(3)

    col1.download_button(
        label="Download TXT",
        data=format_txt(text),
        file_name=f"{filename}.txt",
        mime="text/plain",
        use_container_width=True,
    )

    try:
        docx_data = format_docx(
            text,
            st.session_state.doc_type,
            st.session_state.terms,
            logo,
        )

        col2.download_button(
            label="Download DOCX",
            data=docx_data,
            file_name=f"{filename}.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"
            ),
            use_container_width=True,
        )

    except Exception as exc:
        col2.error(
            f"DOCX export failed: {exc}"
        )

    try:
        pdf_data = format_pdf(
            text,
            st.session_state.doc_type,
            st.session_state.terms,
            logo,
        )

        col3.download_button(
            label="Download PDF",
            data=pdf_data,
            file_name=f"{filename}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    except Exception as exc:
        col3.error(
            f"PDF export failed: {exc}"
        )