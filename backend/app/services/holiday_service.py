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


def get_day_multiplier(holiday_type: Optional[HolidayType], is_rest_day: bool) -> Decimal:
    if holiday_type == HolidayType.REGULAR:
        return REGULAR_HOLIDAY_ON_REST_DAY if is_rest_day else REGULAR_HOLIDAY
    if holiday_type == HolidayType.SPECIAL_NON_WORKING:
        return SPECIAL_NON_WORKING_ON_REST_DAY if is_rest_day else SPECIAL_NON_WORKING
    if is_rest_day:
        return REST_DAY
    return ORDINARY


def compute_day_base_pay(daily_rate: Decimal, holiday_type: Optional[HolidayType], is_rest_day: bool) -> Decimal:
    multiplier = get_day_multiplier(holiday_type, is_rest_day)
    return (daily_rate * multiplier).quantize(Decimal("0.01"))
