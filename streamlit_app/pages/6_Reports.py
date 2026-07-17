"""
Reports page: export summary/breakdowns as CSV, PDF, or Excel.
"""
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
st.set_page_config(page_title="Reports · FinTrack", page_icon="₹", layout="wide")

from src.auth.auth import require_auth
require_auth()

from streamlit_app.components.theme import apply_theme, render_sidebar_brand
apply_theme()
render_sidebar_brand()

import pandas as pd
from datetime import date

from src.db.connection import engine
from src.reports.report_builder import build_report
from src.reports.pdf_export import generate_pdf_report
from src.reports.excel_export import generate_excel_report

st.title("Reports")

user_id = st.session_state["user_id"]

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date", value=date.today().replace(day=1))
with col2:
    end_date = st.date_input("End date", value=date.today())

if start_date > end_date:
    st.error("Start date must be before end date.")
    st.stop()

report = build_report(engine, user_id, start_date=start_date, end_date=end_date)

st.subheader("Summary")
s = report.summary
sc1, sc2, sc3, sc4 = st.columns(4)
metric_html = lambda label, value: f"""
    <div style="background:#171F28; border-radius:10px; padding:10px 12px;">
        <div style="color:#7C8894; font-size:0.7rem; margin-bottom:4px;">{label}</div>
        <div style="color:#EDF1F5; font-family:'IBM Plex Mono', monospace; font-size:0.95rem;">{value}</div>
    </div>
"""
with sc1:
    st.markdown(metric_html("Income", f"₹{s.get('total_income', 0):,.0f}"), unsafe_allow_html=True)
with sc2:
    st.markdown(metric_html("Expense", f"₹{s.get('total_expense', 0):,.0f}"), unsafe_allow_html=True)
with sc3:
    st.markdown(metric_html("Net savings", f"₹{s.get('net_savings', 0):,.0f}"), unsafe_allow_html=True)
with sc4:
    st.markdown(metric_html("Savings rate", f"{s.get('savings_rate', 0):.1f}%"), unsafe_allow_html=True)

st.write("")

if report.category_breakdown is not None and not report.category_breakdown.empty:
    st.write("**Category breakdown**")
    st.dataframe(report.category_breakdown, width="stretch", hide_index=True)

if report.top_merchants is not None and not report.top_merchants.empty:
    st.write("**Top merchants**")
    st.dataframe(report.top_merchants, width="stretch", hide_index=True)

if report.budget_vs_actual is not None and not report.budget_vs_actual.empty:
    st.write("**Budget vs actual**")
    st.dataframe(report.budget_vs_actual, width="stretch", hide_index=True)

if report.recurring_payments:
    st.write("**Recurring payments**")
    recurring_df = pd.DataFrame([{
        "Merchant": r.merchant_name,
        "Avg Amount": r.avg_amount,
        "Frequency": r.frequency,
        "Next Expected": r.next_expected_date,
    } for r in report.recurring_payments])
    st.dataframe(recurring_df, width="stretch", hide_index=True)

st.divider()
st.subheader("Download")
dl_col1, dl_col2, dl_col3 = st.columns(3)

with dl_col1:
    csv_parts = ["SUMMARY\n"]
    csv_parts.append(pd.DataFrame(
        [{"Metric": k, "Value": v} for k, v in report.summary.items()]
    ).to_csv(index=False))

    if report.category_breakdown is not None and not report.category_breakdown.empty:
        csv_parts.append("\nCATEGORY BREAKDOWN\n")
        csv_parts.append(report.category_breakdown.to_csv(index=False))

    if report.top_merchants is not None and not report.top_merchants.empty:
        csv_parts.append("\nTOP MERCHANTS\n")
        csv_parts.append(report.top_merchants.to_csv(index=False))

    if report.budget_vs_actual is not None and not report.budget_vs_actual.empty:
        csv_parts.append("\nBUDGET VS ACTUAL\n")
        csv_parts.append(report.budget_vs_actual.to_csv(index=False))

    csv_data = "".join(csv_parts)
    st.download_button(
        "Download CSV",
        data=csv_data,
        file_name=f"finance_report_{start_date}_{end_date}.csv",
        mime="text/csv",
        use_container_width=True,
    )

with dl_col2:
    pdf_bytes = generate_pdf_report(report)
    st.download_button(
        "Download PDF",
        data=pdf_bytes,
        file_name=f"finance_report_{start_date}_{end_date}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

with dl_col3:
    excel_bytes = generate_excel_report(report)
    st.download_button(
        "Download Excel",
        data=excel_bytes,
        file_name=f"finance_report_{start_date}_{end_date}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )