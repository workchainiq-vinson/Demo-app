"""
2026 Philippine statutory deductions (employee share only):

  SSS:        5% of Monthly Salary Credit (MSC). MSC floor PHP 5,000,
              cap PHP 35,000 -> max employee deduction PHP 1,750.
  PhilHealth: 2.5% of basic monthly salary. Floor PHP 10,000 (min PHP 250),
              ceiling PHP 100,000 (max PHP 2,500).
  Pag-IBIG:   2% of basic monthly salary, salary capped at PHP 10,000
              -> max deduction PHP 200.

Semi-monthly cutoffs: project the cutoff's basic salary to a full month
(x2), compute the monthly deduction against the brackets above, then divide
by 2 to get the per-cutoff deduction.
"""
from decimal import ROUND_HALF_UP, Decimal

SSS_MSC_FLOOR = Decimal("5000")
SSS_MSC_CAP = Decimal("35000")
SSS_RATE = Decimal("0.05")

PHILHEALTH_FLOOR = Decimal("10000")
PHILHEALTH_CEILING = Decimal("100000")
PHILHEALTH_RATE = Decimal("0.025")

PAGIBIG_CAP = Decimal("10000")
PAGIBIG_RATE = Decimal("0.02")

TWO_PLACES = Decimal("0.01")


def _round(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def compute_sss_monthly(monthly_salary: Decimal) -> Decimal:
    msc = min(max(monthly_salary, SSS_MSC_FLOOR), SSS_MSC_CAP)
    return _round(msc * SSS_RATE)


def compute_philhealth_monthly(monthly_salary: Decimal) -> Decimal:
    base = min(max(monthly_salary, PHILHEALTH_FLOOR), PHILHEALTH_CEILING)
    return _round(base * PHILHEALTH_RATE)


def compute_pagibig_monthly(monthly_salary: Decimal) -> Decimal:
    base = min(monthly_salary, PAGIBIG_CAP)
    return _round(base * PAGIBIG_RATE)


def compute_statutory_deductions(cutoff_basic_salary: Decimal) -> dict:
    """
    cutoff_basic_salary: the employee's basic salary earned for THIS
    semi-monthly cutoff (excludes OT/NSD/holiday premiums and pakyaw
    variable pay is included as basic wage for pakyaw workers).

    Returns per-cutoff (i.e. already halved) deduction amounts.
    """
    monthly_projected = cutoff_basic_salary * 2

    sss_monthly = compute_sss_monthly(monthly_projected)
    philhealth_monthly = compute_philhealth_monthly(monthly_projected)
    pagibig_monthly = compute_pagibig_monthly(monthly_projected)

    sss_cutoff = _round(sss_monthly / 2)
    philhealth_cutoff = _round(philhealth_monthly / 2)
    pagibig_cutoff = _round(pagibig_monthly / 2)

    return {
        "sss": sss_cutoff,
        "philhealth": philhealth_cutoff,
        "pagibig": pagibig_cutoff,
        "total": _round(sss_cutoff + philhealth_cutoff + pagibig_cutoff),
    }
