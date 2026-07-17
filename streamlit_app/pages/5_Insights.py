"""
Insights page: auto-generated observations + spending forecast. Phase 6.
"""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
st.set_page_config(page_title="Insights · FinTrack", page_icon="₹")

from src.auth.auth import require_auth
require_auth()

from streamlit_app.components.theme import apply_theme, render_sidebar_brand, style_chart, render_observation
apply_theme()
render_sidebar_brand()

import pandas as pd
import plotly.graph_objects as go

from src.db.connection import engine
from src.analytics.insights import generate_insights
from src.analytics.forecast import forecast_next_month_expense
from src.analytics.recurring import detect_recurring
from src.db.queries import get_transactions_for_recurring_check

st.title("Insights & forecast")

user_id = st.session_state["user_id"]

st.subheader("Observations")
for insight in generate_insights(engine, user_id):
    render_observation(insight, kind="neutral")

st.divider()
st.subheader("Next month's expense forecast")

result = forecast_next_month_expense(engine, user_id, months_history=12)

if result["forecast_expense"] is None:
    st.caption("Not enough monthly history yet to forecast — need at least 2 months of transactions.")
else:
    history = result["history"]
    forecast_month = result["forecast_month"]
    forecast_expense = result["forecast_expense"]
    confidence = result["trend_confidence"]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div style="background:#171F28; border-radius:10px; padding:14px 16px;">
                <div style="color:#7C8894; font-size:0.75rem; margin-bottom:4px;">Forecast for {forecast_month.strftime('%B %Y')}</div>
                <div style="color:#EDF1F5; font-family:'IBM Plex Mono', monospace; font-size:1.4rem; font-weight:500;">₹{forecast_expense:,.0f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div style="background:#2A2114; border-radius:10px; padding:14px 16px; display:flex; align-items:center; height:100%;">
                <span style="color:#E8A33D; font-size:0.85rem; font-weight:500;">{confidence.capitalize()} confidence</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    fig = go.Figure()
    fig.add_scatter(x=history["month"], y=history["expense"], mode="lines+markers", name="Actual",
                     line=dict(color="#2FBF8F"))
    fig.add_scatter(
        x=[forecast_month], y=[forecast_expense], mode="markers", name="Forecast",
        marker=dict(size=12, symbol="star", color="#C9A227"),
    )
    fig = style_chart(fig, height=280)
    st.plotly_chart(fig, width="stretch")

    st.caption(
        "This is a simple linear trend fit on monthly totals — a lightweight "
        "baseline, not a production forecasting model. Confidence reflects how "
        "many months of history are available."
    )

st.subheader("Recurring payments")

txn_df = get_transactions_for_recurring_check(engine, user_id)
recurring = detect_recurring(txn_df)

if not recurring:
    st.info("No recurring payments detected yet — needs more transaction history.")
else:
    display_df = pd.DataFrame([{
        "Merchant": r.merchant_name,
        "Category": r.category_name,
        "Avg Amount": f"₹{r.avg_amount:,.2f}",
        "Frequency": r.frequency,
        "Occurrences": r.occurrences,
        "Next Expected": r.next_expected_date.strftime("%d %b %Y"),
        "Confidence": r.confidence,
    } for r in recurring])
    st.dataframe(display_df, width="stretch", hide_index=True)