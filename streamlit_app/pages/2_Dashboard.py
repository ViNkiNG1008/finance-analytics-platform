"""
Dashboard page: executive overview — total income, expenses, savings,
category breakdown, monthly trend, top merchants. Phase 5.
"""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
st.set_page_config(page_title="Dashboard · FinTrack", page_icon="₹")

from src.auth.auth import require_auth
require_auth()

from streamlit_app.components.theme import (
    apply_theme, render_sidebar_brand, render_metric, format_inr,
    style_chart, empty_state, CATEGORY_HEX,
)
apply_theme()
render_sidebar_brand()

from datetime import date
import plotly.express as px

from src.db.connection import engine
from src.db.queries import (
    get_summary_metrics,
    get_category_breakdown,
    get_monthly_trend,
    get_top_merchants,
)

st.title("Dashboard")
st.caption("Overview of your finances")

user_id = st.session_state["user_id"]

with st.sidebar:
    st.subheader("Filters")
    range_choice = st.selectbox(
        "Date range", ["All time", "Last 3 months", "Last 6 months", "Last 12 months"], index=0
    )

months_map = {"Last 3 months": 3, "Last 6 months": 6, "Last 12 months": 12}
start_date = None
if range_choice in months_map:
    months_back = months_map[range_choice]
    today = date.today()
    from dateutil.relativedelta import relativedelta
    start_date = today - relativedelta(months=months_back)

metrics = get_summary_metrics(engine, user_id, start_date=start_date)

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric("Total income", format_inr(metrics['total_income']), "income")
with col2:
    render_metric("Total expenses", format_inr(metrics['total_expense']), "expense")
with col3:
    render_metric("Net savings", format_inr(metrics['net_savings']), "savings")
with col4:
    render_metric("Savings rate", f"{metrics['savings_rate']:.1f}%", "rate")

st.divider()

left, mid, right = st.columns(3)

with left:
    st.subheader("Expense breakdown by category")
    cat_df = get_category_breakdown(engine, user_id, start_date=start_date)
    if cat_df.empty:
        empty_state("No expense data yet — upload a statement first.")
    else:
        fig = px.pie(
            cat_df, names="category_name", values="total", hole=0.55,
            color="category_name", color_discrete_map=CATEGORY_HEX,
        )
        fig = style_chart(fig, height=320)
        st.plotly_chart(fig, width="stretch")

trend_df = get_monthly_trend(engine, user_id, months=12)

with mid:
    st.subheader("Monthly expense trend")
    if trend_df.empty:
        st.caption("No transaction history yet.")
    else:
        fig = px.line(trend_df, x="month", y="expense", markers=True)
        fig = style_chart(fig, height=320)
        fig.update_traces(line_color="#E8734D")
        fig.update_layout(yaxis_title="₹")
        st.plotly_chart(fig, width="stretch")

with right:
    st.subheader("Income vs expense trend")
    if trend_df.empty:
        st.caption("No transaction history yet.")
    else:
        fig = px.line(trend_df, x="month", y=["income", "expense"], markers=True,
                       color_discrete_sequence=["#2FBF8F", "#E8734D"])
        fig = style_chart(fig, height=320)
        fig.update_layout(yaxis_title="₹")
        st.plotly_chart(fig, width="stretch")

st.divider()

st.subheader("Top merchants")
top_df = get_top_merchants(engine, user_id, start_date=start_date, limit=10)
if top_df.empty:
    st.caption("No expense data yet.")
else:
    fig = px.bar(
        top_df.sort_values("total_spent"),
        x="total_spent",
        y="merchant_name",
        orientation="h",
        text="total_spent",
        color_discrete_sequence=["#C9A227"],
    )
    fig.update_traces(texttemplate="₹%{text:,.0f}", textposition="outside")
    fig = style_chart(fig, height=380)
    fig.update_layout(xaxis_title="₹ spent", yaxis_title="")
    st.plotly_chart(fig, width="stretch")