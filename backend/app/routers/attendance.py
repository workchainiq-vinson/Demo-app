from datetime import date as date_type
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.schemas.attendance import AttendanceApproveOT, AttendanceCreate, AttendanceRead, AttendanceUpdate
from app.services import attendance_service, nsd_service

router = APIRouter(prefix="/attendance", tags=["attendance"])


def _recompute_derived_fields(attendance: Attendance, employee: Employee):
    """Recomputes late/undertime/nsd/actual_ot from the employee's shift and punches."""
    shift = employee.default_shift
    if shift and attendance.time_in and attendance.time_out:
        late, undertime = attendance_service.compute_late_undertime_minutes(
            shift.start_time,
            shift.end_time,
            shift.grace_period_minutes,
            attendance.date,
            attendance.time_in,
            attendance.time_out,
        )
        attendance.late_minutes = late
        attendance.undertime_minutes = undertime

        scheduled_end_date = (
            attendance.date + timedelta(days=1) if shift.end_time <= shift.start_time else attendance.date
        )
        from datetime import datetime as dt

        scheduled_end = dt.combine(scheduled_end_date, shift.end_time)
        worked_past_shift = (attendance.time_out - scheduled_end).total_seconds() / 60
        attendance.actual_ot_minutes = max(0, int(worked_past_shift))
    else:
        attendance.late_minutes = 0
        attendance.undertime_minutes = 0
        attendance.actual_ot_minutes = 0

    attendance.nsd_minutes = nsd_service.compute_nsd_minutes(attendance.time_in, attendance.time_out)


@router.get("", response_model=list[AttendanceRead])
def list_attendance(
    employee_id: Optional[int] = None,
    date_from: Optional[date_type] = None,
    date_to: Optional[date_type] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Attendance)
    if employee_id is not None:
        query = query.filter(Attendance.employee_id == employee_id)
    if date_from is not None:
        query = query.filter(Attendance.date >= date_from)
    if date_to is not None:
        query = query.filter(Attendance.date <= date_to)
    return query.order_by(Attendance.date.desc()).all()


@router.post("", response_model=AttendanceRead, status_code=201)
def create_attendance(payload: AttendanceCreate, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == payload.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    attendance = Attendance(**payload.model_dump())
    _recompute_derived_fields(attendance, employee)
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.put("/{attendance_id}", response_model=AttendanceRead)
def update_attendance(attendance_id: int, payload: AttendanceUpdate, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(attendance, field, value)
    _recompute_derived_fields(attendance, attendance.employee)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.put("/{attendance_id}/approve-ot", response_model=AttendanceRead)
def approve_ot(attendance_id: int, payload: AttendanceApproveOT, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    attendance.approved_ot_minutes = payload.approved_ot_minutes
    db.commit()
    db.refresh(attendance)
    return attendance


@router.delete("/{attendance_id}", status_code=204)
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    db.delete(attendance)
    db.commit()
    return None
