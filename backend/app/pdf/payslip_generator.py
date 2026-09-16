"""
Generates a payslip PDF with ReportLab.

CRITICAL: Never use the "PHP" peso sign glyph ("₱") anywhere in this
file or in generated content. ReportLab's default Helvetica font (used
below) does not include that glyph and will crash when it tries to render
it. Always use the literal string "PHP " as a prefix for peso amounts.
"""
import io
import os
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

COMPANY_NAME = "Bio Green Processing and Manufacturing Inc."
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
LOGO_ASPECT_RATIO = 961 / 258  # width / height of logo.png (pre-cropped to content)


def _php(amount) -> str:
    value = amount if isinstance(amount, Decimal) else Decimal(str(amount))
    return f"PHP {value:,.2f}"


def generate_payslip_pdf(employee, payroll_run, payslip, breakdown: dict) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("TitleStyle", parent=styles["Heading1"], fontSize=16, spaceAfter=4)
    subtitle_style = ParagraphStyle("SubtitleStyle", parent=styles["Normal"], fontSize=10, textColor=colors.grey)
    section_style = ParagraphStyle("SectionStyle", parent=styles["Heading3"], fontSize=11, spaceBefore=10, spaceAfter=4)

    logo_width = 3.5 * inch
    logo_height = logo_width / LOGO_ASPECT_RATIO

    elements = []
    if os.path.exists(LOGO_PATH):
        elements.append(Image(LOGO_PATH, width=logo_width, height=logo_height))
    else:
        elements.append(Paragraph(COMPANY_NAME, title_style))
    elements.append(Paragraph("Employee Payslip", subtitle_style))
    elements.append(Spacer(1, 0.2 * inch))

    info_table = Table(
        [
            ["Employee Name:", f"{employee.first_name} {employee.last_name}", "Employee Code:", employee.employee_code],
            ["Employment Type:", employee.employment_type.value, "Cutoff Period:", f"{payroll_run.cutoff_start} to {payroll_run.cutoff_end}"],
        ],
        colWidths=[1.3 * inch, 2.2 * inch, 1.3 * inch, 2.2 * inch],
    )
    info_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(info_table)

    elements.append(Paragraph("Earnings", section_style))
    earnings_rows = [["Description", "Amount"]]
    earnings_rows.append(["Basic Pay (Days Worked)", _php(breakdown.get("base_pay", 0))])
    earnings_rows.append(["Holiday / Rest Day Premium", _php(breakdown.get("holiday_premium_pay", 0))])
    earnings_rows.append(["Lateness / Undertime Deduction", f"-{_php(breakdown.get('lateness_undertime_deduction', 0))}"])
    earnings_rows.append(["Overtime Pay (Approved OT only)", _php(breakdown.get("ot_pay", 0))])
    earnings_rows.append(["Night Shift Differential", _php(breakdown.get("nsd_pay", 0))])
    earnings_rows.append(["Pakyaw (Piece-Rate) Pay", _php(breakdown.get("pakyaw_pay", 0))])
    earnings_rows.append(["GROSS PAY", _php(payslip.gross_pay)])

    earnings_table = Table(earnings_rows, colWidths=[4 * inch, 2 * inch])
    earnings_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f5233")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ]
        )
    )
    elements.append(earnings_table)

    elements.append(Paragraph("Statutory Deductions", section_style))
    deduction_rows = [
        ["Description", "Amount"],
        ["SSS Employee Share", _php(payslip.sss_deduction)],
        ["PhilHealth Employee Share", _php(payslip.philhealth_deduction)],
        ["Pag-IBIG Employee Share", _php(payslip.pagibig_deduction)],
        ["TOTAL DEDUCTIONS", _php(payslip.total_deductions)],
    ]
    deduction_table = Table(deduction_rows, colWidths=[4 * inch, 2 * inch])
    deduction_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#8c2f2f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ]
        )
    )
    elements.append(deduction_table)

    elements.append(Spacer(1, 0.25 * inch))
    net_pay_table = Table([["NET PAY", _php(payslip.net_pay)]], colWidths=[4 * inch, 2 * inch])
    net_pay_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f0f0f0")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    elements.append(net_pay_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
