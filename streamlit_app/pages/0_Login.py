import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
st.set_page_config(page_title="Login · FinTrack", page_icon="₹", layout="wide")

from streamlit_app.components.theme import apply_theme, render_sidebar_brand
apply_theme()
render_sidebar_brand()

from src.auth.auth import register_user, authenticate_user, login_user, logout_user, is_authenticated

# ---------------------------------------------------------------------------
# NOTE ON THE FIX
# ---------------------------------------------------------------------------
# The old version opened a <div class="panel"> in one st.markdown() call and
# closed it in a later one, with native widgets (st.tabs, st.form,
# st.file_uploader) in between. Streamlit puts every st.markdown() call in
# its own isolated container, so the div never actually wraps the widgets —
# it just self-closes immediately, leaving an empty bordered box at the top
# of each column. It also meant the two branches (logged in / logged out)
# rendered a different number of stray elements, so the right-hand panel
# looked inconsistent between states.
#
# The fix: use st.container(border=True) — Streamlit's real container — and
# style *that* container with a CSS marker + :has() selector, instead of
# trying to hand-wrap raw HTML around widgets.
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    [data-testid="stAppViewBlockContainer"] { max-width: 1000px !important; padding-top: 4rem; }

    /* Style any Streamlit container that contains our invisible marker span */
    div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div > .panel-marker) {
        background: #101820;
        border: 1px solid #1E2A35;
        border-radius: 14px;
        padding: 8px 6px;
    }

    .panel-title {
        font-family:'Space Grotesk', sans-serif;
        font-size: 1.05rem;
        font-weight: 600;
        color: #EDF1F5;
        margin-bottom: 2px;
    }
    .panel-subtitle {
        font-size: 0.8rem;
        color: #7C8894;
        margin-bottom: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

col_login, col_upload = st.columns([1, 1.15], gap="large")

# ---------------- LEFT: LOGIN / SIGNUP ----------------
with col_login:
    with st.container(border=True):
        st.markdown('<span class="panel-marker"></span>', unsafe_allow_html=True)

        st.markdown(
            """
            <div style="text-align:center; margin-bottom: 1.5rem;">
                <div style="width:44px; height:44px; border-radius:10px; background:#C9A227;
                            display:flex; align-items:center; justify-content:center;
                            font-family:'Space Grotesk', sans-serif; font-size:22px; font-weight:600;
                            color:#1A1400; margin: 0 auto 12px auto;">₹</div>
                <div style="font-family:'Space Grotesk', sans-serif; font-size:1.2rem; font-weight:600; color:#EDF1F5;">Welcome back</div>
                <div style="font-size:0.85rem; color:#7C8894; margin-top:4px;">Sign in to manage your finances</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if is_authenticated():
            st.markdown(
                f"""
                <div style="background:#12241C; border-radius:8px; padding:10px 14px; font-size:0.85rem;
                            color:#2FBF8F; margin-bottom:14px;">
                    ✓ Logged in as <strong>{st.session_state['username']}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("Log out", use_container_width=True):
                logout_user()
                st.rerun()
        else:
            tab_login, tab_signup = st.tabs(["Log In", "Sign Up"])

            with tab_login:
                with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)

                    if submitted:
                        success, message, user = authenticate_user(username, password)
                        if success:
                            login_user(user)
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

            with tab_signup:
                with st.form("signup_form"):
                    new_name = st.text_input("Full name")
                    new_username = st.text_input("Choose a username")
                    new_email = st.text_input("Email")
                    new_password = st.text_input("Choose a password", type="password")
                    signup_submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)

                    if signup_submitted:
                        success, message = register_user(new_username, new_email, new_password, new_name)
                        if success:
                            st.success(message + " Switch to the Log In tab.")
                        else:
                            st.error(message)

# ---------------- RIGHT: UPLOAD ----------------
with col_upload:
    with st.container(border=True):
        st.markdown('<span class="panel-marker"></span>', unsafe_allow_html=True)

        st.markdown('<div class="panel-title">Upload statement</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel-subtitle">CSV, XLSX or XLS · up to 200MB</div>', unsafe_allow_html=True)

        if not is_authenticated():
            st.markdown(
                """
                <div style="border:1.5px dashed #2E3A46; border-radius:12px; padding:40px 20px; text-align:center;
                            opacity:0.5; margin-bottom: 1rem;">
                    <div style="font-size:26px; color:#4C8DFF; margin-bottom:8px;">⬆</div>
                    <div style="font-size:0.85rem; color:#EDF1F5;">Drag and drop your statement here</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.caption("🔒 Log in to enable uploads.")
        else:
            import tempfile
            from pathlib import Path as PathLib
            from src.etl.extract import extract_statement
            from src.etl.transform import clean_transactions
            from src.etl.categorize import categorize_transactions
            from src.etl.load import load_transactions
            from src.db.connection import SessionLocal

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