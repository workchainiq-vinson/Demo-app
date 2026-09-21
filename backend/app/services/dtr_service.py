"""
Aggregates raw Attendance data into the per-employee totals used by the DTR
(Daily Time Record) Summary Report — a pre-payroll time-and-attendance audit
in hours/days, distinct from the payroll pay-amount reports.

Two figures are explicit approximations, documented here rather than
presented as exact:
  - "Over" (over-break minutes) is always 0 — Attendance has no break-time
    tracking in this system.
  - "NDO" (Night Differential Overtime) is approximated as
    min(nsd_minutes, approved_ot_minutes) per day: the largest amount of
    that day's OT that could plausibly overlap with the night window, since
    the schema doesn't record the actual OT time window to compute a true
    overlap.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.models.employee import Employee
from app.services.holiday_service import classify_day

CLASSIFICATIONS = ["regular", "rest_day", "rest_day_special", "rest_day_legal", "legal_holiday", "special_holiday"]
HOLIDAY_CLASSIFICATIONS = {"rest_day_special", "rest_day_legal", "legal_holiday", "special_holiday"}

TWO_PLACES = Decimal("0.01")


def _hours(minutes: int) -> Decimal:
    return (Decimal(minutes) / Decimal(60)).quantize(TWO_PLACES)


def _empty_bucket() -> dict:
    return {"days": 0, "nd_hours": Decimal("0.00"), "ot_hours": Decimal("0.00"), "ndo_hours": Decimal("0.00")}


def compute_dtr_summary(db: Session, date_from: date, date_to: date) -> list[dict]:
    employees = db.query(Employee).order_by(Employee.department, Employee.last_name, Employee.first_name).all()

    rows = []
    for employee in employees:
        records = (
            db.query(Attendance)
            .filter(
                Attendance.employee_id == employee.id,
                Attendance.date >= date_from,
                Attendance.date <= date_to,
                Attendance.time_in.isnot(None),
                Attendance.time_out.isnot(None),
            )
            .all()
        )
        if not records:
            continue

        buckets = {key: _empty_bucket() for key in CLASSIFICATIONS}
        total_late_minutes = 0
        holiday_days = 0

        for record in records:
            holiday_type = record.holiday.holiday_type if record.holiday else None
            classification = classify_day(holiday_type, record.is_rest_day_worked)

            bucket = buckets[classification]
            bucket["days"] += 1
            bucket["nd_hours"] += _hours(record.nsd_minutes)
            bucket["ot_hours"] += _hours(record.approved_ot_minutes)
            bucket["ndo_hours"] += _hours(min(record.nsd_minutes, record.approved_ot_minutes))

            total_late_minutes += record.late_minutes
            if classification in HOLIDAY_CLASSIFICATIONS:
                holiday_days += 1

        rows.append(
            {
                "employee_id": employee.id,
                "employee_code": employee.employee_code,
                "name": f"{employee.first_name} {employee.last_name}",
                "department": employee.department or "Unassigned",
                "holiday_days": holiday_days,
                "late_minutes": total_late_minutes,
                "over_break_minutes": 0,
                "buckets": buckets,
            }
        )

    return rows


def group_by_department(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["department"], []).append(row)
    return grouped
