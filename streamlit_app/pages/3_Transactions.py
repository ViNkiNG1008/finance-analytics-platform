"""
Transactions page: full searchable/filterable transaction table.
"""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
st.set_page_config(page_title="Transactions · FinTrack", page_icon="₹")

from src.auth.auth import require_auth
require_auth()

from streamlit_app.components.theme import apply_theme, render_sidebar_brand, style_category
apply_theme()
render_sidebar_brand()

from src.db.connection import engine
from src.db.queries import get_transactions

st.title("Transactions")
st.caption("All transactions from your uploaded statements")

user_id = st.session_state["user_id"]

col1, col2 = st.columns([2, 2])
with col1:
    search = st.text_input("Search description or merchant", placeholder="e.g. Swiggy")
with col2:
    categories = st.multiselect(
        "Filter by category",
        options=["Food & Dining", "Shopping", "Transport", "Bills & Utilities", "Entertainment", "Others", "Income"],
    )

date_col1, date_col2 = st.columns(2)
with date_col1:
    start_date = st.date_input("From", value=None)
with date_col2:
    end_date = st.date_input("To", value=None)

df = get_transactions(
    engine,
    user_id,
    search=search or None,
    categories=categories or None,
    start_date=start_date if start_date else None,
    end_date=end_date if end_date else None,
)

st.caption(f"{len(df)} transaction(s)")

display_df = df.rename(columns={
    "date": "Date", "merchant": "Merchant", "category": "Category",
    "amount": "Amount", "transaction_type": "Type", "description": "Description",
})

if display_df.empty:
    st.dataframe(display_df, width="stretch", hide_index=True)
else:
    st.dataframe(
        display_df.style.map(style_category, subset=["Category"]),
        width="stretch",
        hide_index=True,
    )