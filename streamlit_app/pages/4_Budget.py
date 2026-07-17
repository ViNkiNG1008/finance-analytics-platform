"""
Budget page: set monthly budgets per category, compare against actual spend.
"""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
st.set_page_config(page_title="Budget · FinTrack", page_icon="₹")

from src.auth.auth import require_auth
require_auth()

from streamlit_app.components.theme import apply_theme, render_sidebar_brand, style_chart, render_budget_bar
apply_theme()
render_sidebar_brand()

from datetime import date
import plotly.graph_objects as go

from src.db.connection import engine
from src.db.queries import get_expense_categories, get_budget_vs_actual, upsert_budget

st.title("Budget tracker")
st.caption("Budget vs actual by category")

user_id = st.session_state["user_id"]

today = date.today()
col1, col2 = st.columns(2)
with col1:
    year = st.number_input("Year", min_value=2000, max_value=2100, value=today.year, step=1)
with col2:
    month = st.selectbox(
        "Month",
        options=list(range(1, 13)),
        index=today.month - 1,
        format_func=lambda m: date(2000, m, 1).strftime("%B"),
    )

st.divider()
st.subheader("Set monthly limits")

cat_df = get_expense_categories(engine)
bva_df = get_budget_vs_actual(engine, user_id, year=int(year), month=int(month))

limit_lookup = dict(zip(bva_df["category_id"], bva_df["monthly_limit"])) if not bva_df.empty else {}

with st.form("budget_form"):
    new_limits = {}
    for _, row in cat_df.iterrows():
        current = float(limit_lookup.get(row["category_id"], 0))
        new_limits[row["category_id"]] = st.number_input(
            row["category_name"], min_value=0.0, value=current, step=500.0, key=f"budget_{row['category_id']}"
        )
    submitted = st.form_submit_button("Save budgets", type="primary")

if submitted:
    for category_id, monthly_limit in new_limits.items():
        upsert_budget(engine, user_id, category_id=int(category_id), monthly_limit=float(monthly_limit))
    st.success("Budgets updated.")
    st.rerun()

st.divider()
st.subheader(f"Budget vs actual — {date(2000, int(month), 1).strftime('%B')} {int(year)}")

if bva_df.empty:
    st.caption("No categories found.")
else:
    bva_df_sorted = bva_df.sort_values("monthly_limit", ascending=True)
    over_budget = bva_df_sorted["actual_spent"] > bva_df_sorted["monthly_limit"]

    fig = go.Figure()
    fig.add_bar(name="Budget", y=bva_df_sorted["category_name"], x=bva_df_sorted["monthly_limit"],
                orientation="h", marker_color="#232D38")
    fig.add_bar(
        name="Actual",
        y=bva_df_sorted["category_name"],
        x=bva_df_sorted["actual_spent"],
        orientation="h",
        marker_color=["#E8734D" if o else "#2FBF8F" for o in over_budget],
    )
    fig = style_chart(fig, height=320)
    st.plotly_chart(fig, width="stretch")

    st.divider()
    st.subheader("Progress by category")
    for _, row in bva_df.sort_values("category_name").iterrows():
        render_budget_bar(row["category_name"], row["actual_spent"], row["monthly_limit"])

    overspent = bva_df[over_budget.reindex(bva_df.index, fill_value=False)] if not bva_df.empty else bva_df
    overspent = bva_df[bva_df["actual_spent"] > bva_df["monthly_limit"]]
    if not overspent.empty:
        for _, row in overspent.iterrows():
            st.warning(
                f"**{row['category_name']}**: ₹{row['actual_spent']:,.0f} spent vs "
                f"₹{row['monthly_limit']:,.0f} budgeted "
                f"(₹{row['actual_spent'] - row['monthly_limit']:,.0f} over)."
            )