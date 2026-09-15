"""
Overtime pay: 125% of the hourly rate, calculated ONLY on approved_ot_minutes
(actual_ot_minutes is informational/audit data and never used for pay).
"""
from decimal import Decimal

OT_MULTIPLIER = Decimal("1.25")


def compute_ot_pay(hourly_rate: Decimal, approved_ot_minutes: int) -> Decimal:
    if approved_ot_minutes <= 0:
        return Decimal("0.00")
    hours = Decimal(approved_ot_minutes) / Decimal(60)
    return (hourly_rate * OT_MULTIPLIER * hours).quantize(Decimal("0.01"))
