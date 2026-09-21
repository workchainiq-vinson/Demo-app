"""
Determines the pay multiplier for a worked day based on whether it falls on
the employee's rest day and/or a holiday.

Multipliers (per business rules):
  - Ordinary day worked:                      100%
  - Rest day worked:                          130%
  - Regular holiday worked:                   200%
  - Regular holiday worked AND on rest day:   260%

Special non-working days are not covered by the given business rules but the
Holiday model supports them, so standard DOLE treatment is applied as a
reasonable extension: 130% worked, 150% if also on a rest day.
"""
from decimal import Decimal
from typing import Optional

from app.models.holiday import HolidayType

ORDINARY = Decimal("1.00")
REST_DAY = Decimal("1.30")
REGULAR_HOLIDAY = Decimal("2.00")
REGULAR_HOLIDAY_ON_REST_DAY = Decimal("2.60")
SPECIAL_NON_WORKING = Decimal("1.30")
SPECIAL_NON_WORKING_ON_REST_DAY = Decimal("1.50")


def classify_day(holiday_type: Optional[HolidayType], is_rest_day: bool) -> str:
    """
    Buckets a worked day into one of the six classifications used across the
    payroll engine and the DTR summary report: regular, rest_day,
    rest_day_special, rest_day_legal, legal_holiday, special_holiday.
    """
    if holiday_type == HolidayType.REGULAR:
        return "rest_day_legal" if is_rest_day else "legal_holiday"
    if holiday_type == HolidayType.SPECIAL_NON_WORKING:
        return "rest_day_special" if is_rest_day else "special_holiday"
    if is_rest_day:
        return "rest_day"
    return "regular"


def get_day_multiplier(holiday_type: Optional[HolidayType], is_rest_day: bool) -> Decimal:
    classification = classify_day(holiday_type, is_rest_day)
    return {
        "rest_day_legal": REGULAR_HOLIDAY_ON_REST_DAY,
        "legal_holiday": REGULAR_HOLIDAY,
        "rest_day_special": SPECIAL_NON_WORKING_ON_REST_DAY,
        "special_holiday": SPECIAL_NON_WORKING,
        "rest_day": REST_DAY,
        "regular": ORDINARY,
    }[classification]


def compute_day_base_pay(daily_rate: Decimal, holiday_type: Optional[HolidayType], is_rest_day: bool) -> Decimal:
    multiplier = get_day_multiplier(holiday_type, is_rest_day)
    return (daily_rate * multiplier).quantize(Decimal("0.01"))
