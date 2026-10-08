"""
Generates a payroll summary PDF listing every employee's gross/deductions/net
for that cutoff, with a totals row. Loans, MP2 and petty cash are broken out
as one column per type. Landscape, since that is 12 columns. See
app/pdf/common.py for the peso-formatting / Unicode-safety notes shared
across PDF generators.
"""
import io
import os
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.pdf.common import LOGO_ASPECT_RATIO, LOGO_PATH
from app.pdf.common import php as _php
from app.services.deduction_service import DEDUCTION_LABELS, DEDUCTION_ORDER

ZERO = Decimal("0")


def _deductions_by_type(payslip) -> dict:
    sums = {deduction_type: ZERO for deduction_type in DEDUCTION_ORDER}
    for applied in payslip.applied_deductions:
        sums[applied.deduction_type] += Decimal(applied.amount)
    return sums


def generate_payroll_summary_pdf(
    payroll_run,
    payslips_with_names: list[tuple],
    status_label: str | None = None,
) -> io.BytesIO:
    """
    payslips_with_names: list of (payslip, employee_name) tuples.
    """
    buffer = io.BytesIO()
    page_width = landscape(letter)[0]
    side_margin = 0.4 * inch
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=side_margin,
        rightMargin=side_margin,
    )

    styles = getSampleStyleSheet()
    subtitle_style = ParagraphStyle("SubtitleStyle", parent=styles["Normal"], fontSize=10, textColor=colors.grey)

    logo_width = 3.5 * inch
    logo_height = logo_width / LOGO_ASPECT_RATIO

    title = f"Payroll Summary Report &mdash; {payroll_run.cutoff_start} to {payroll_run.cutoff_end}"
    if status_label:
        title += f" &mdash; {status_label}"

    elements = []
    if os.path.exists(LOGO_PATH):
        elements.append(Image(LOGO_PATH, width=logo_width, height=logo_height))
    elements.append(Paragraph(title, subtitle_style))
    elements.append(Spacer(1, 0.2 * inch))

    header = (
        ["Employee", "Gross Pay", "SSS", "PhilHealth", "Pag-IBIG"]
        + [DEDUCTION_LABELS[t] for t in DEDUCTION_ORDER]
        + ["Total Deductions", "Net Pay"]
    )
    # Plain-string table cells don't wrap, so break long labels onto two lines.
    rows = [[label.replace(" ", "\n") if len(label) > 10 else label for label in header]]
    totals = {
        "gross": ZERO,
        "sss": ZERO,
        "philhealth": ZERO,
        "pagibig": ZERO,
        "deductions": ZERO,
        "net": ZERO,
        "other": {t: ZERO for t in DEDUCTION_ORDER},
    }

    for payslip, employee_name in payslips_with_names:
        other = _deductions_by_type(payslip)
        rows.append(
            [
                employee_name,
                _php(payslip.gross_pay),
                _php(payslip.sss_deduction),
                _php(payslip.philhealth_deduction),
                _php(payslip.pagibig_deduction),
                *[_php(other[t]) for t in DEDUCTION_ORDER],
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
        for t in DEDUCTION_ORDER:
            totals["other"][t] += other[t]

    rows.append(
        [
            "TOTAL",
            _php(totals["gross"]),
            _php(totals["sss"]),
            _php(totals["philhealth"]),
            _php(totals["pagibig"]),
            *[_php(totals["other"][t]) for t in DEDUCTION_ORDER],
            _php(totals["deductions"]),
            _php(totals["net"]),
        ]
    )

    # Fit the usable page width exactly, or ReportLab silently clips columns.
    usable_width = page_width - 2 * side_margin
    name_width = 1.5 * inch
    numeric_width = (usable_width - name_width) / (len(header) - 1)
    col_widths = [name_width] + [numeric_width] * (len(header) - 1)

    table = Table(rows, colWidths=col_widths, repeatRows=1)
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
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTSIZE", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
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
