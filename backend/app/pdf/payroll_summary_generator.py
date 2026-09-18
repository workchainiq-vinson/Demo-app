"""
Generates a one-page-per-run payroll summary PDF listing every employee's
gross/deductions/net for that cutoff, with a totals row. See
app/pdf/common.py for the peso-formatting / Unicode-safety notes shared
across PDF generators.
"""
import io
import os
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.pdf.common import LOGO_ASPECT_RATIO, LOGO_PATH
from app.pdf.common import php as _php


def generate_payroll_summary_pdf(payroll_run, payslips_with_names: list[tuple]) -> io.BytesIO:
    """
    payslips_with_names: list of (payslip, employee_name) tuples.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()
    subtitle_style = ParagraphStyle("SubtitleStyle", parent=styles["Normal"], fontSize=10, textColor=colors.grey)

    logo_width = 3.5 * inch
    logo_height = logo_width / LOGO_ASPECT_RATIO

    elements = []
    if os.path.exists(LOGO_PATH):
        elements.append(Image(LOGO_PATH, width=logo_width, height=logo_height))
    elements.append(
        Paragraph(
            f"Payroll Summary Report &mdash; {payroll_run.cutoff_start} to {payroll_run.cutoff_end}",
            subtitle_style,
        )
    )
    elements.append(Spacer(1, 0.2 * inch))

    rows = [["Employee", "Gross Pay", "SSS", "PhilHealth", "Pag-IBIG", "Total Deductions", "Net Pay"]]
    totals = {"gross": Decimal("0"), "sss": Decimal("0"), "philhealth": Decimal("0"), "pagibig": Decimal("0"), "deductions": Decimal("0"), "net": Decimal("0")}

    for payslip, employee_name in payslips_with_names:
        rows.append(
            [
                employee_name,
                _php(payslip.gross_pay),
                _php(payslip.sss_deduction),
                _php(payslip.philhealth_deduction),
                _php(payslip.pagibig_deduction),
                _php(payslip.total_deductions),
                _php(payslip.net_pay),
            ]
        )
        totals["gross"] += Decimal(payslip.gross_pay)
        totals["sss"] += Decimal(payslip.sss_deduction)
        totals["philhealth"] += Decimal(payslip.philhealth_deduction)
        totals["pagibig"] += Decimal(payslip.pagibig_deduction)
        totals["deductions"] += Decimal(payslip.total_deductions)
        totals["net"] += Decimal(payslip.net_pay)

    rows.append(
        [
            "TOTAL",
            _php(totals["gross"]),
            _php(totals["sss"]),
            _php(totals["philhealth"]),
            _php(totals["pagibig"]),
            _php(totals["deductions"]),
            _php(totals["net"]),
        ]
    )

    table = Table(
        rows,
        colWidths=[1.7 * inch, 0.95 * inch, 0.75 * inch, 0.85 * inch, 0.75 * inch, 1.05 * inch, 0.95 * inch],
        repeatRows=1,
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f5233")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f0f0f0")),
                ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ]
        )
    )
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
