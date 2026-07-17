import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
st.set_page_config(page_title="Login · FinTrack", page_icon="₹")

from streamlit_app.components.theme import apply_theme, render_sidebar_brand
apply_theme()
render_sidebar_brand()

from src.auth.auth import register_user, authenticate_user, login_user, logout_user, is_authenticated

st.markdown(
    """
    <style>
    [data-testid="stAppViewBlockContainer"] { max-width: 420px !important; padding-top: 6rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div style="text-align:center; margin-bottom: 2rem;">
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
            Logged in as <strong>{st.session_state['name']}</strong> (@{st.session_state['username']})
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Log out"):
        logout_user()
        st.rerun()
    st.stop()

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