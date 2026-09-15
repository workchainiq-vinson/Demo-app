"""
calculate_payroll_for_cutoff: composes attendance, overtime, NSD, holiday,
and statutory services into one gross-to-net payroll computation for a
single employee over a date-range cutoff.
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy.orm import Session

from app.models.attendance import Attendance
from app.models.employee import Employee, EmploymentType
from app.models.holiday import Holiday
from app.models.pakyaw import PakyawLog
from app.services import holiday_service, nsd_service, overtime_service, statutory_service

TWO_PLACES = Decimal("0.01")


def _q(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES)


def _is_rest_day(employee: Employee, the_date: date, attendance: Attendance) -> bool:
    if attendance.is_rest_day_worked:
        return True
    if employee.rest_day_of_week is None:
        return False
    return the_date.weekday() == employee.rest_day_of_week


def calculate_payroll_for_cutoff(
    db: Session,
    employee_id: int,
    cutoff_start: date,
    cutoff_end: date,
    apply_statutory: bool = True,
) -> dict:
    employee = db.query(Employee).filter(Employee.id == employee_id).one()
    daily_rate = Decimal(employee.daily_rate)
    hourly_rate = daily_rate / Decimal(8)

    attendances = (
        db.query(Attendance)
        .filter(
            Attendance.employee_id == employee_id,
            Attendance.date >= cutoff_start,
            Attendance.date <= cutoff_end,
        )
        .all()
    )

    holidays_by_date = {
        h.date: h for h in db.query(Holiday).filter(Holiday.date >= cutoff_start, Holiday.date <= cutoff_end).all()
    }

    days_worked = 0
    base_pay_at_100 = Decimal("0.00")  # for statutory basic-salary purposes
    holiday_premium_pay = Decimal("0.00")
    lateness_deduction = Decimal("0.00")
    ot_pay = Decimal("0.00")
    nsd_pay = Decimal("0.00")

    for attendance in attendances:
        if attendance.time_in is None or attendance.time_out is None:
            continue

        days_worked += 1
        holiday: Optional[Holiday] = attendance.holiday or holidays_by_date.get(attendance.date)
        holiday_type = holiday.holiday_type if holiday else None
        is_rest_day = _is_rest_day(employee, attendance.date, attendance)

        day_base_pay = holiday_service.compute_day_base_pay(daily_rate, holiday_type, is_rest_day)
        base_pay_at_100 += daily_rate
        holiday_premium_pay += _q(day_base_pay - daily_rate)

        day_lateness_deduction = _q(
            (Decimal(attendance.late_minutes + attendance.undertime_minutes) / Decimal(60)) * hourly_rate
        )
        lateness_deduction += day_lateness_deduction

        ot_pay += overtime_service.compute_ot_pay(hourly_rate, attendance.approved_ot_minutes)
        nsd_pay += nsd_service.compute_nsd_pay(hourly_rate, attendance.nsd_minutes)

    regular_pay = _q(base_pay_at_100 + holiday_premium_pay - lateness_deduction)

    pakyaw_logs = (
        db.query(PakyawLog)
        .filter(
            PakyawLog.employee_id == employee_id,
            PakyawLog.date >= cutoff_start,
            PakyawLog.date <= cutoff_end,
        )
        .all()
    )
    pakyaw_pay = _q(sum((Decimal(log.units_completed) * Decimal(log.task.rate_per_unit) for log in pakyaw_logs), Decimal("0.00")))

    # PAKYAW-type employees earn no daily-rate wage; MIXED/REGULAR do.
    if employee.employment_type == EmploymentType.PAKYAW:
        regular_pay = Decimal("0.00")
        base_pay_at_100 = Decimal("0.00")
        holiday_premium_pay = Decimal("0.00")
        lateness_deduction = Decimal("0.00")

    gross_pay = _q(regular_pay + ot_pay + nsd_pay + pakyaw_pay)

    breakdown = {
        "days_worked": days_worked,
        "base_pay": _q(base_pay_at_100),
        "holiday_premium_pay": _q(holiday_premium_pay),
        "lateness_undertime_deduction": _q(lateness_deduction),
        "regular_pay": regular_pay,
        "ot_pay": _q(ot_pay),
        "nsd_pay": _q(nsd_pay),
        "pakyaw_pay": pakyaw_pay,
        "gross_pay": gross_pay,
    }

    statutory = {"sss": Decimal("0.00"), "philhealth": Decimal("0.00"), "pagibig": Decimal("0.00"), "total": Decimal("0.00")}
    if apply_statutory:
        basic_salary_for_cutoff = regular_pay + pakyaw_pay
        statutory = statutory_service.compute_statutory_deductions(basic_salary_for_cutoff)

    total_deductions = statutory["total"]
    net_pay = _q(gross_pay - total_deductions)

    return {
        "employee_id": employee_id,
        "cutoff_start": cutoff_start,
        "cutoff_end": cutoff_end,
        "breakdown": breakdown,
        "sss_deduction": statutory["sss"],
        "philhealth_deduction": statutory["philhealth"],
        "pagibig_deduction": statutory["pagibig"],
        "total_deductions": total_deductions,
        "gross_pay": gross_pay,
        "net_pay": net_pay,
    }
