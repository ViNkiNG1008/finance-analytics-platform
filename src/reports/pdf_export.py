"""
Builds a PDF summary report from a ReportData object.
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from src.reports.report_builder import ReportData


def generate_pdf_report(report: ReportData) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom", parent=styles["Title"], fontSize=18, spaceAfter=6
    )
    heading_style = ParagraphStyle(
        "HeadingCustom", parent=styles["Heading2"], spaceBefore=14, spaceAfter=8
    )

    elements = []

    elements.append(Paragraph("Personal Finance Report", title_style))
    elements.append(Paragraph(
        f"{report.start_date.strftime('%d %b %Y')} – {report.end_date.strftime('%d %b %Y')}",
        styles["Normal"]
    ))
    elements.append(Spacer(1, 12))

    # --- Summary section ---
    elements.append(Paragraph("Summary", heading_style))
    summary_rows = [["Metric", "Amount"]]
    for key, value in report.summary.items():
        label = key.replace("_", " ").title()
        formatted = f"₹{value:,.2f}" if isinstance(value, (int, float)) else str(value)
        summary_rows.append([label, formatted])

    summary_table = Table(summary_rows, colWidths=[8 * cm, 8 * cm])
    summary_table.setStyle(_default_table_style())
    elements.append(summary_table)

    # --- Category breakdown ---
    if report.category_breakdown is not None and not report.category_breakdown.empty:
        elements.append(Paragraph("Category Breakdown", heading_style))
        elements.append(_df_to_table(report.category_breakdown))

    # --- Top merchants ---
    if report.top_merchants is not None and not report.top_merchants.empty:
        elements.append(Paragraph("Top Merchants", heading_style))
        elements.append(_df_to_table(report.top_merchants))

    # --- Budget vs actual ---
    if report.budget_vs_actual is not None and not report.budget_vs_actual.empty:
        elements.append(Paragraph("Budget vs Actual", heading_style))
        elements.append(_df_to_table(report.budget_vs_actual))

    # --- Recurring payments ---
    if report.recurring_payments:
        elements.append(Paragraph("Recurring Payments", heading_style))
        rows = [["Merchant", "Avg Amount", "Frequency", "Next Expected"]]
        for r in report.recurring_payments:
            rows.append([
                r.merchant_name,
                f"₹{r.avg_amount:,.2f}",
                r.frequency,
                r.next_expected_date.strftime("%d %b %Y"),
            ])
        table = Table(rows, colWidths=[5 * cm, 4 * cm, 4 * cm, 4 * cm])
        table.setStyle(_default_table_style())
        elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def _default_table_style() -> TableStyle:
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
    ])


def _df_to_table(df) -> Table:
    data = [list(df.columns)] + df.astype(str).values.tolist()
    col_width = 16 * cm / max(len(df.columns), 1)
    table = Table(data, colWidths=[col_width] * len(df.columns))
    table.setStyle(_default_table_style())
    return table