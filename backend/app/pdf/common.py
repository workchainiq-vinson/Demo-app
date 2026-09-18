"""
Shared helpers for ReportLab PDF generation.

CRITICAL: Never use the "PHP" peso sign glyph ("₱") anywhere in generated
PDF content. ReportLab's default Helvetica font does not include that
glyph and will crash when it tries to render it. Always use the literal
string "PHP " as a prefix for peso amounts.
"""
import os
from decimal import Decimal

COMPANY_NAME = "Bio Green Processing and Manufacturing Inc."
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
LOGO_ASPECT_RATIO = 961 / 258  # width / height of logo.png (pre-cropped to content)


def php(amount) -> str:
    value = amount if isinstance(amount, Decimal) else Decimal(str(amount))
    return f"PHP {value:,.2f}"
