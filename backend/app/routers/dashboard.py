from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee, EmploymentType
from app.models.holiday import Holiday
from app.models.pakyaw import PakyawLog
from app.models.payroll import PayrollPayslip, PayrollRun

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _month_bounds(today: date) -> tuple[date, date]:
    start = today.replace(day=1)
    if today.month == 12:
        end = today.replace(year=today.year + 1, month=1, day=1)
    else:
        end = today.replace(month=today.month + 1, day=1)
    return start, end


def _run_totals(db: Session, run_id: int) -> dict:
    row = (
        db.query(
            func.coalesce(func.sum(PayrollPayslip.gross_pay), 0),
            func.coalesce(func.sum(PayrollPayslip.total_deductions), 0),
            func.coalesce(func.sum(PayrollPayslip.net_pay), 0),
        )
        .filter(PayrollPayslip.payroll_run_id == run_id)
        .one()
    )
    gross, deductions, net = row
    return {"gross_pay": Decimal(gross), "total_deductions": Decimal(deductions), "net_pay": Decimal(net)}


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_employees = db.query(func.count(Employee.id)).scalar() or 0
    active_employees = db.query(func.count(Employee.id)).filter(Employee.is_active == True).scalar() or 0  # noqa: E712
    by_type = dict(
        db.query(Employee.employment_type, func.count(Employee.id)).group_by(Employee.employment_type).all()
    )
    employee_counts = {
        "total": total_employees,
        "active": active_employees,
        "inactive": total_employees - active_employees,
        "by_type": {t.value: by_type.get(t, 0) for t in EmploymentType},
    }

    latest_run = db.query(PayrollRun).order_by(PayrollRun.generated_at.desc()).first()
    latest_payroll_run = None
    if latest_run:
        totals = _run_totals(db, latest_run.id)
        latest_payroll_run = {
            "id": latest_run.id,
            "cutoff_start": latest_run.cutoff_start,
            "cutoff_end": latest_run.cutoff_end,
            **totals,
        }

    recent_runs = db.query(PayrollRun).order_by(PayrollRun.generated_at.desc()).limit(6).all()
    payroll_trend = []
    for run in reversed(recent_runs):
        totals = _run_totals(db, run.id)
        payroll_trend.append(
            {
                "run_id": run.id,
                "cutoff_end": run.cutoff_end,
                "gross_pay": totals["gross_pay"],
                "net_pay": totals["net_pay"],
            }
        )

    today = date.today()
    month_start, month_end = _month_bounds(today)

    attendance_row = (
        db.query(
            func.coalesce(func.sum(Attendance.late_minutes), 0),
            func.coalesce(func.sum(Attendance.approved_ot_minutes), 0),
            func.coalesce(func.sum(Attendance.nsd_minutes), 0),
            func.count(Attendance.id),
        )
        .filter(Attendance.date >= month_start, Attendance.date < month_end)
        .one()
    )
    late_minutes, ot_minutes, nsd_minutes, days_logged = attendance_row
    attendance_summary_this_month = {
        "late_minutes": late_minutes,
        "approved_ot_minutes": ot_minutes,
        "nsd_minutes": nsd_minutes,
        "days_logged": days_logged,
    }

    pakyaw_row = (
        db.query(
            func.coalesce(func.sum(PakyawLog.units_completed), 0),
            func.coalesce(func.sum(PakyawLog.computed_pay), 0),
        )
        .filter(PakyawLog.date >= month_start, PakyawLog.date < month_end)
        .one()
    )
    total_units, total_pay = pakyaw_row
    pakyaw_summary_this_month = {"total_units": Decimal(total_units), "total_pay": Decimal(total_pay)}

    upcoming_holiday_rows = (
        db.query(Holiday).filter(Holiday.date >= today).order_by(Holiday.date).limit(3).all()
    )
    upcoming_holidays = [
        {"id": h.id, "name": h.name, "date": h.date, "holiday_type": h.holiday_type.value}
        for h in upcoming_holiday_rows
    ]

    return {
        "employee_counts": employee_counts,
        "latest_payroll_run": latest_payroll_run,
        "payroll_trend": payroll_trend,
        "attendance_summary_this_month": attendance_summary_this_month,
        "pakyaw_summary_this_month": pakyaw_summary_this_month,
        "upcoming_holidays": upcoming_holidays,
    }
