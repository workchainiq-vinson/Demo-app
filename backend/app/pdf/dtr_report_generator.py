"""
Generates the DTR (Daily Time Record) Summary Report: a pre-payroll
time-and-attendance audit in hours/days, grouped by department, with a
signature block. See app/pdf/common.py for the peso-formatting /
Unicode-safety notes shared across PDF generators (not applicable to the
figures in this report, which are hours/days, not currency).

See app/services/dtr_service.py for what "Over" and "NDO" mean here and
why they are approximations rather than exact figures.
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

BUCKET_ORDER = ["regular", "rest_day", "rest_day_special", "rest_day_legal", "legal_holiday", "special_holiday"]
BUCKET_LABELS = {
    "regular": "Regular Working Days",
    "rest_day": "Rest Day",
    "rest_day_special": "Rest Day Special",
    "rest_day_legal": "Rest Day Legal",
    "legal_holiday": "Legal Holiday",
    "special_holiday": "Special Holiday",
}
# "regular" shows Days/ND/OT (no 1st8/NDO); "rest_day" shows 1st8/ND/OT (no NDO);
# the four holiday-related buckets show 1st8/ND/OT/NDO. Matches the sample report.
BUCKET_SUBCOLS = {
    "regular": ["ND", "Days", "OT"],
    "rest_day": ["1st8", "ND", "OT"],
    "rest_day_special": ["1st8", "ND", "OT", "NDO"],
    "rest_day_legal": ["1st8", "ND", "OT", "NDO"],
    "legal_holiday": ["1st8", "ND", "OT", "NDO"],
    "special_holiday": ["1st8", "ND", "OT", "NDO"],
}


def _num(value) -> str:
    if isinstance(value, int):
        return str(value)
    return f"{value:.2f}" if isinstance(value, Decimal) else str(value)


def _bucket_value(bucket: dict, subcol: str):
    if subcol == "Days":
        return bucket["days"]
    if subcol == "1st8":
        return bucket["days"]
    if subcol == "ND":
        return bucket["nd_hours"]
    if subcol == "OT":
        return bucket["ot_hours"]
    if subcol == "NDO":
        return bucket["ndo_hours"]
    return ""


def _build_header_rows() -> tuple[list, list, list]:
    """Returns (group_row, sub_row, span_commands) for the two-row table header."""
    group_row = ["ID Nbr", "Employee Name", "Hol.\nDays", "Lates/Over Break", ""]
    sub_row = ["", "", "", "LT", "Over"]
    spans = [("SPAN", (3, 0), (4, 0))]

    col = 5
    for bucket_key in BUCKET_ORDER:
        subcols = BUCKET_SUBCOLS[bucket_key]
        group_row.append(BUCKET_LABELS[bucket_key])
        group_row.extend([""] * (len(subcols) - 1))
        sub_row.extend(subcols)
        spans.append(("SPAN", (col, 0), (col + len(subcols) - 1, 0)))
        col += len(subcols)

    return group_row, sub_row, spans


def generate_dtr_summary_pdf(date_from, date_to, rows_by_department: dict[str, list[dict]]) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch,
        leftMargin=0.35 * inch,
        rightMargin=0.35 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("DtrTitle", parent=styles["Heading2"], alignment=1, fontSize=12, spaceAfter=2)
    subtitle_style = ParagraphStyle("DtrSubtitle", parent=styles["Normal"], alignment=1, fontSize=9, spaceAfter=2)
    dept_style = ParagraphStyle("DtrDept", parent=styles["Heading4"], fontSize=9, spaceBefore=10, spaceAfter=4)
    note_style = ParagraphStyle("DtrNote", parent=styles["Normal"], fontSize=6.5, textColor=colors.grey, spaceBefore=8)

    elements = []
    if os.path.exists(LOGO_PATH):
        logo_width = 2.5 * inch
        elements.append(Image(LOGO_PATH, width=logo_width, height=logo_width / LOGO_ASPECT_RATIO))
        elements.append(Spacer(1, 0.05 * inch))
    elements.append(Paragraph("Employees DTR Summary Report", title_style))
    elements.append(Paragraph(f"For the period of {date_from} to {date_to}", subtitle_style))
    elements.append(Spacer(1, 0.15 * inch))

    group_row, sub_row, header_spans = _build_header_rows()
    n_cols = len(group_row)

    # Landscape letter usable width is 11in - 2*0.35in margins = 10.3in; with
    # n_cols columns (27 for the standard 6-bucket layout) this must fit
    # exactly, or ReportLab silently clips columns past the page edge.
    usable_width = landscape(letter)[0] - 0.7 * inch
    id_w, name_w, hol_w = 0.45 * inch, 1.05 * inch, 0.35 * inch
    small_w = (usable_width - id_w - name_w - hol_w) / (n_cols - 3)
    col_widths = [id_w, name_w, hol_w] + [small_w] * (n_cols - 3)

    header_style_cmds = [
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2f5233")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("SPAN", (0, 0), (0, 1)),
        ("SPAN", (1, 0), (1, 1)),
        ("SPAN", (2, 0), (2, 1)),
        *header_spans,
    ]

    for department, employee_rows in rows_by_department.items():
        elements.append(Paragraph(f"{department} Employees", dept_style))

        table_data = [group_row, sub_row]
        for row in employee_rows:
            data_row = [row["employee_code"], row["name"], str(row["holiday_days"]), str(row["late_minutes"]), str(row["over_break_minutes"])]
            for bucket_key in BUCKET_ORDER:
                bucket = row["buckets"][bucket_key]
                for subcol in BUCKET_SUBCOLS[bucket_key]:
                    data_row.append(_num(_bucket_value(bucket, subcol)))
            table_data.append(data_row)

        table = Table(table_data, colWidths=col_widths, repeatRows=2)
        row_style_cmds = list(header_style_cmds)
        row_style_cmds += [
            ("BACKGROUND", (0, 2), (-1, -1), colors.white),
            ("TEXTCOLOR", (0, 2), (-1, -1), colors.black),
            ("FONTNAME", (0, 2), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 2), (-1, -1), 6.5),
            ("ALIGN", (0, 2), (1, -1), "LEFT"),
            ("ALIGN", (2, 2), (-1, -1), "CENTER"),
            ("GRID", (0, 2), (-1, -1), 0.4, colors.HexColor("#cccccc")),
        ]
        table.setStyle(TableStyle(row_style_cmds))
        elements.append(table)

    elements.append(
        Paragraph(
            "Note: \"Over\" (over-break minutes) is not tracked by this system and always shows 0. "
            "\"NDO\" (Night Differential Overtime) is an approximation — the smaller of that day's "
            "night-differential minutes and approved overtime minutes — since exact OT time windows "
            "are not recorded.",
            note_style,
        )
    )

    elements.append(Spacer(1, 0.4 * inch))
    signature_table = Table(
        [["Prepared By", "Checked By", "Noted By"], ["", "", ""]],
        colWidths=[3 * inch, 3 * inch, 3 * inch],
    )
    signature_table.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("LINEABOVE", (0, 1), (-1, 1), 0.5, colors.black),
                ("TOPPADDING", (0, 1), (-1, 1), 20),
            ]
        )
    )
    elements.append(signature_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
