from datetime import date
from src.reports.pdf_export import generate_pdf_report
from src.reports.excel_export import generate_excel_report
from src.reports.report_builder import ReportData
import pandas as pd

def _sample_report():
    return ReportData(
        start_date=date(2026, 4, 1),
        end_date=date(2026, 4, 30),
        summary={"total_income": 50000, "total_expense": 32000, "net_savings": 18000},
        category_breakdown=pd.DataFrame([
            {"category": "Shopping", "amount": 15000},
            {"category": "Food", "amount": 8000},
        ]),
        top_merchants=pd.DataFrame([
            {"merchant": "Amazon", "amount": 6000},
        ]),
        budget_vs_actual=pd.DataFrame([
            {"category": "Shopping", "budget": 12000, "actual": 15000, "status": "Over"},
        ]),
        recurring_payments=[],
    )

def test_pdf_generation_produces_bytes():
    report = _sample_report()
    pdf_bytes = generate_pdf_report(report)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF")

def test_excel_generation_produces_bytes():
    report = _sample_report()
    excel_bytes = generate_excel_report(report)
    assert isinstance(excel_bytes, bytes)
    assert len(excel_bytes) > 0