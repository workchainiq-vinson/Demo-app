from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.pakyaw import PakyawLog
from app.models.payroll import PayrollPayslip
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeRead])
def list_employees(is_active: Optional[bool] = None, db: Session = Depends(get_db)):
    query = db.query(Employee)
    if is_active is not None:
        query = query.filter(Employee.is_active == is_active)
    return query.order_by(Employee.last_name, Employee.first_name).all()


@router.post("", response_model=EmployeeRead, status_code=201)
def create_employee(payload: EmployeeCreate, db: Session = Depends(get_db)):
    if db.query(Employee).filter(Employee.employee_code == payload.employee_code).first():
        raise HTTPException(status_code=400, detail="employee_code already exists")
    employee = Employee(**payload.model_dump())
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


@router.get("/{employee_id}", response_model=EmployeeRead)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee


@router.put("/{employee_id}", response_model=EmployeeRead)
def update_employee(employee_id: int, payload: EmployeeUpdate, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    db.commit()
    db.refresh(employee)
    return employee


@router.delete("/{employee_id}", status_code=204)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    has_history = (
        db.query(Attendance).filter(Attendance.employee_id == employee_id).first() is not None
        or db.query(PakyawLog).filter(PakyawLog.employee_id == employee_id).first() is not None
        or db.query(PayrollPayslip).filter(PayrollPayslip.employee_id == employee_id).first() is not None
    )
    if has_history:
        raise HTTPException(
            status_code=400,
            detail=(
                "Cannot delete an employee with existing attendance, pakyaw, or payroll records. "
                "Set the employee to Inactive instead to preserve payroll history."
            ),
        )

    db.delete(employee)
    db.commit()
    return None
