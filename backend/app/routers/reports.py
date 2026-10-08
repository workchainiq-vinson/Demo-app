import csv
import io
from datetime import date as date_type
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee, EmploymentStatus
from app.models.pakyaw import PakyawLog
from app.models.payroll import PayrollPayslip, PayrollRun
from app.pdf.common import STATUS_LABELS
from app.pdf.dtr_report_generator import generate_dtr_summary_pdf
from app.pdf.payroll_summary_generator import generate_payroll_summary_pdf
from app.services.deduction_service import DEDUCTION_LABELS, DEDUCTION_ORDER
from app.services.dtr_service import compute_dtr_summary, group_by_department

router = APIRouter(prefix="/reports", tags=["reports"])


def _status_label(employment_status: Optional[EmploymentStatus]) -> Optional[str]:
    return STATUS_LABELS[employment_status.value] if employment_status else None


def _filename_suffix(employment_status: Optional[EmploymentStatus]) -> str:
    return f"_{employment_status.value.lower()}" if employment_status else ""


def _run_payslips(run: PayrollRun, employment_status: Optional[EmploymentStatus]) -> list[PayrollPayslip]:
    payslips = [p for p in run.payslips if employment_status is None or p.employee.employment_status == employment_status]
    if not payslips:
        raise HTTPException(status_code=404, detail="No payslips found for this employment status in this payroll run")
    return payslips


def _other_deductions_by_type(payslip: PayrollPayslip) -> dict:
    sums = {deduction_type: Decimal("0.00") for deduction_type in DEDUCTION_ORDER}
    for applied in payslip.applied_deductions:
        sums[applied.deduction_type] += Decimal(applied.amount)
    return sums


def _csv_response(rows: list[list], header: list[str], filename: str) -> StreamingResponse:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/payroll-summary/{run_id}/csv")
def payroll_summary_csv(
    run_id: int,
    employment_status: Optional[EmploymentStatus] = None,
    db: Session = Depends(get_db),
):
    run = db.query(PayrollRun).filter(PayrollRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    payslips = _run_payslips(run, employment_status)

    rows = []
    for p in payslips:
        other = _other_deductions_by_type(p)
        rows.append(
            [
                p.employee.employee_code,
                f"{p.employee.first_name} {p.employee.last_name}",
                STATUS_LABELS[p.employee.employment_status.value],
                str(p.gross_pay),
                str(p.sss_deduction),
                str(p.philhealth_deduction),
                str(p.pagibig_deduction),
                *[str(other[t]) for t in DEDUCTION_ORDER],
                str(p.total_deductions),
                str(p.net_pay),
            ]
        )
    header = (
        ["Employee Code", "Employee Name", "Employment Status", "Gross Pay", "SSS", "PhilHealth", "Pag-IBIG"]
        + [DEDUCTION_LABELS[t] for t in DEDUCTION_ORDER]
        + ["Total Deductions", "Net Pay"]
    )
    filename = f"payroll_summary_{run.cutoff_start}_{run.cutoff_end}{_filename_suffix(employment_status)}.csv"
    return _csv_response(rows, header, filename)


@router.get("/payroll-summary/{run_id}/pdf")
def payroll_summary_pdf(
    run_id: int,
    employment_status: Optional[EmploymentStatus] = None,
    db: Session = Depends(get_db),
):
    run = db.query(PayrollRun).filter(PayrollRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Payroll run not found")
    payslips = _run_payslips(run, employment_status)

    payslips_with_names = [(p, f"{p.employee.first_name} {p.employee.last_name}") for p in payslips]
    pdf_buffer = generate_payroll_summary_pdf(run, payslips_with_names, _status_label(employment_status))
    filename = f"payroll_summary_{run.cutoff_start}_{run.cutoff_end}{_filename_suffix(employment_status)}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/attendance/csv")
def attendance_csv(
    date_from: Optional[date_type] = None,
    date_to: Optional[date_type] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Attendance)
    if date_from is not None:
        query = query.filter(Attendance.date >= date_from)
    if date_to is not None:
        query = query.filter(Attendance.date <= date_to)
    if employee_id is not None:
        query = query.filter(Attendance.employee_id == employee_id)
    records = query.order_by(Attendance.date).all()

    rows = [
        [
            a.employee.employee_code,
            f"{a.employee.first_name} {a.employee.last_name}",
            str(a.date),
            a.time_in.isoformat() if a.time_in else "",
            a.time_out.isoformat() if a.time_out else "",
            a.late_minutes,
            a.undertime_minutes,
            a.approved_ot_minutes,
            a.nsd_minutes,
            "Yes" if a.is_rest_day_worked else "No",
        ]
        for a in records
    ]
    header = [
        "Employee Code",
        "Employee Name",
        "Date",
        "Time In",
        "Time Out",
        "Late Minutes",
        "Undertime Minutes",
        "Approved OT Minutes",
        "NSD Minutes",
        "Rest Day Worked",
    ]
    filename = "attendance_report.csv"
    return _csv_response(rows, header, filename)


@router.get("/pakyaw/csv")
def pakyaw_csv(
    date_from: Optional[date_type] = None,
    date_to: Optional[date_type] = None,
    employee_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(PakyawLog)
    if date_from is not None:
        query = query.filter(PakyawLog.date >= date_from)
    if date_to is not None:
        query = query.filter(PakyawLog.date <= date_to)
    if employee_id is not None:
        query = query.filter(PakyawLog.employee_id == employee_id)
    records = query.order_by(PakyawLog.date).all()

    rows = [
        [
            log.employee.employee_code,
            f"{log.employee.first_name} {log.employee.last_name}",
            log.task.task_name,
            str(log.date),
            str(log.units_completed),
            str(log.computed_pay),
            log.group_batch_id or "",
        ]
        for log in records
    ]
    header = ["Employee Code", "Employee Name", "Task", "Date", "Units Completed", "Computed Pay", "Group Batch ID"]
    filename = "pakyaw_production_report.csv"
    return _csv_response(rows, header, filename)


@router.get("/employees/csv")
def employees_csv(db: Session = Depends(get_db)):
    records = db.query(Employee).order_by(Employee.last_name, Employee.first_name).all()

    rows = [
        [
            e.employee_code,
            f"{e.first_name} {e.last_name}",
            e.department or "",
            STATUS_LABELS[e.employment_status.value],
            e.employment_type.value,
            str(e.daily_rate),
            str(e.rest_day_of_week) if e.rest_day_of_week is not None else "",
            e.default_shift.name if e.default_shift else "",
            "Active" if e.is_active else "Inactive",
        ]
        for e in records
    ]
    header = [
        "Employee Code",
        "Employee Name",
        "Department",
        "Employment Status",
        "Pay Type",
        "Daily Rate",
        "Rest Day (0=Mon)",
        "Default Shift",
        "Active",
    ]
    filename = "employee_directory.csv"
    return _csv_response(rows, header, filename)


@router.get("/dtr-summary/pdf")
def dtr_summary_pdf(
    date_from: date_type,
    date_to: date_type,
    department: Optional[str] = None,
    employment_status: Optional[EmploymentStatus] = None,
    db: Session = Depends(get_db),
):
    rows = compute_dtr_summary(db, date_from, date_to, employment_status)
    if department:
        rows = [r for r in rows if r["department"] == department]
    if not rows:
        raise HTTPException(status_code=404, detail="No attendance records found for this period")

    rows_by_department = group_by_department(rows)
    pdf_buffer = generate_dtr_summary_pdf(date_from, date_to, rows_by_department, _status_label(employment_status))
    filename = f"dtr_summary_{date_from}_{date_to}{_filename_suffix(employment_status)}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
