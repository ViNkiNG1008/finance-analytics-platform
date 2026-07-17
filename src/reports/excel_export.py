"""
Builds an Excel (.xlsx) summary report from a ReportData object,
with one sheet per section.
"""
from io import BytesIO
import pandas as pd

from src.reports.report_builder import ReportData


def generate_excel_report(report: ReportData) -> bytes:
    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        # Summary sheet
        summary_df = pd.DataFrame(
            [{"Metric": k.replace("_", " ").title(), "Value": v}
             for k, v in report.summary.items()]
        )
        summary_df.to_excel(writer, sheet_name="Summary", index=False)

        if report.category_breakdown is not None and not report.category_breakdown.empty:
            report.category_breakdown.to_excel(writer, sheet_name="Category Breakdown", index=False)

        if report.top_merchants is not None and not report.top_merchants.empty:
            report.top_merchants.to_excel(writer, sheet_name="Top Merchants", index=False)

        if report.budget_vs_actual is not None and not report.budget_vs_actual.empty:
            report.budget_vs_actual.to_excel(writer, sheet_name="Budget vs Actual", index=False)

        if report.recurring_payments:
            recurring_df = pd.DataFrame([{
                "Merchant": r.merchant_name,
                "Category": r.category_name,
                "Avg Amount": r.avg_amount,
                "Frequency": r.frequency,
                "Occurrences": r.occurrences,
                "Next Expected": r.next_expected_date,
                "Confidence": r.confidence,
            } for r in report.recurring_payments])
            recurring_df.to_excel(writer, sheet_name="Recurring Payments", index=False)

        # Auto-width columns on each sheet
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for col_cells in worksheet.columns:
                length = max(len(str(cell.value)) if cell.value is not None else 0 for cell in col_cells)
                worksheet.column_dimensions[col_cells[0].column_letter].width = min(length + 4, 40)

    buffer.seek(0)
    return buffer.getvalue()