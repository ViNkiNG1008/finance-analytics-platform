"""
Upload page: drag-and-drop a statement file, run the ETL pipeline
(extract -> transform -> categorize -> load) against PostgreSQL.
"""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
st.set_page_config(page_title="Upload · FinTrack", page_icon="₹")

from src.auth.auth import require_auth
require_auth()

from streamlit_app.components.theme import apply_theme, render_sidebar_brand
apply_theme()
render_sidebar_brand()

import tempfile
from pathlib import Path as PathLib

from src.etl.extract import extract_statement
from src.etl.transform import clean_transactions
from src.etl.categorize import categorize_transactions
from src.etl.load import load_transactions
from src.db.connection import SessionLocal

st.title("Upload statement")
st.caption("CSV, XLSX or XLS · up to 200MB")

st.markdown(
    """
    <div style="border:1.5px dashed #2E3A46; border-radius:12px; padding:28px; text-align:center; margin-bottom:1rem;">
        <div style="font-size:26px; color:#4C8DFF; margin-bottom:8px;">⬆</div>
        <div style="font-size:0.85rem; color:#EDF1F5;">Drag and drop your statement here, or use the picker below</div>
    </div>
    """,
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Statement file",
    type=["csv", "xlsx", "xls"],
    label_visibility="collapsed",
)

if uploaded_file is not None:
    st.success(f"Received: {uploaded_file.name}")

    if st.button("Process & update", type="primary"):
        with st.spinner("Running pipeline..."):
            try:
                suffix = PathLib(uploaded_file.name).suffix
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                raw_df = extract_statement(tmp_path)
                cleaned_df = clean_transactions(raw_df)
                categorized_df = categorize_transactions(cleaned_df)

                session = SessionLocal()
                try:
                    inserted = load_transactions(
                        categorized_df,
                        session,
                        source_file=uploaded_file.name,
                        user_id=st.session_state["user_id"],
                    )
                finally:
                    session.close()

                st.success(
                    f"Done — {len(categorized_df)} transactions processed, "
                    f"{inserted} new rows added (duplicates skipped)."
                )
                st.dataframe(
                    categorized_df[["date", "merchant", "category", "amount", "transaction_type"]],
                    width="stretch",
                )

            except Exception as e:
                st.error(f"Pipeline failed: {e}")
else:
    st.caption("Expected columns: date, description, amount (matched flexibly).")