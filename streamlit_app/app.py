"""
Finance Analytics Portal — Streamlit entry point.
Run with: streamlit run streamlit_app/app.py
"""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st

st.set_page_config(
    page_title="FinTrack",
    page_icon="₹",
    layout="wide",
    initial_sidebar_state="expanded",
)

from streamlit_app.components.theme import apply_theme, render_sidebar_brand
apply_theme()
render_sidebar_brand()

col_left, col_right = st.columns([2, 1])

with col_left:
    st.title("Finance analytics portal")
    st.caption("Upload a statement, run the pipeline, and explore your finances.")

    st.markdown(
        """
        ### Get started
        Use the sidebar to navigate:
        - **Upload** — drop in a bank/UPI statement (CSV or Excel)
        - **Dashboard** — income, expenses, savings rate, trends
        - **Transactions** — full searchable transaction table
        - **Budget** — budget vs actual by category
        - **Insights** — auto-generated observations and forecasts
        - **Reports** — export as CSV, PDF, or Excel
        """
    )

with col_right:
    gif_path = ROOT_DIR / "streamlit_app" / "assets" / "money_save.gif"

    if gif_path.exists():
        from PIL import Image
        import base64

        # Check whether the GIF is actually animated
        img = Image.open(gif_path)

        # Display GIF using HTML (often more reliable for animation)
        with open(gif_path, "rb") as f:
            gif_bytes = f.read()

        gif_base64 = base64.b64encode(gif_bytes).decode()

        st.markdown(
            f"""
            <div style="text-align:center;">
                <img src="data:image/gif;base64,{gif_base64}" width="280">
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning(f"GIF not found at: {gif_path}")