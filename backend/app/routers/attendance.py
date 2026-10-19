from datetime import date as date_type
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.shift import Shift
from app.schemas.attendance import AttendanceApproveOT, AttendanceCreate, AttendanceRead, AttendanceUpdate
from app.services import attendance_service

router = APIRouter(prefix="/attendance", tags=["attendance"])


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

    data = payload.model_dump()
    if data.get("shift_id") is None:
        # Snapshot the default so history doesn't shift if the default changes.
        data["shift_id"] = employee.default_shift_id
    elif not db.query(Shift).filter(Shift.id == data["shift_id"]).first():
        raise HTTPException(status_code=404, detail="Shift not found")

    attendance = Attendance(**data)
    db.add(attendance)
    db.flush()
    db.refresh(attendance)
    attendance_service.recompute_derived_fields(attendance, employee)
    db.commit()
    db.refresh(attendance)
    return attendance


@router.put("/{attendance_id}", response_model=AttendanceRead)
def update_attendance(attendance_id: int, payload: AttendanceUpdate, db: Session = Depends(get_db)):
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    changes = payload.model_dump(exclude_unset=True)
    if changes.get("shift_id") is not None and not db.query(Shift).filter(Shift.id == changes["shift_id"]).first():
        raise HTTPException(status_code=404, detail="Shift not found")
    for field, value in changes.items():
        setattr(attendance, field, value)
    db.flush()
    db.refresh(attendance)
    attendance_service.recompute_derived_fields(attendance, attendance.employee)
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
