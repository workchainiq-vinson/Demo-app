from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.deduction import DeductionType, EmployeeDeduction, PayslipDeduction
from app.models.employee import Employee
from app.schemas.deduction import DeductionCreate, DeductionRead, DeductionUpdate

router = APIRouter(prefix="/deductions", tags=["deductions"])

ZERO = Decimal("0")


def _get_or_404(db: Session, deduction_id: int) -> EmployeeDeduction:
    deduction = db.query(EmployeeDeduction).filter(EmployeeDeduction.id == deduction_id).first()
    if not deduction:
        raise HTTPException(status_code=404, detail="Deduction not found")
    return deduction


@router.get("", response_model=list[DeductionRead])
def list_deductions(employee_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(EmployeeDeduction)
    if employee_id is not None:
        query = query.filter(EmployeeDeduction.employee_id == employee_id)
    return query.order_by(EmployeeDeduction.employee_id, EmployeeDeduction.id).all()


@router.post("", response_model=DeductionRead, status_code=201)
def create_deduction(payload: DeductionCreate, db: Session = Depends(get_db)):
    if not db.query(Employee).filter(Employee.id == payload.employee_id).first():
        raise HTTPException(status_code=404, detail="Employee not found")
    if payload.amount_per_cutoff <= ZERO:
        raise HTTPException(status_code=400, detail="Amount per cutoff must be greater than zero")

    if payload.deduction_type == DeductionType.MP2:
        # MP2 is an open-ended savings contribution: no total, no balance, no payoff.
        total_amount = None
        remaining_balance = None
    else:
        if payload.total_amount is None or payload.total_amount <= ZERO:
            raise HTTPException(status_code=400, detail="Total amount is required and must be greater than zero")
        total_amount = payload.total_amount
        remaining_balance = payload.total_amount

    deduction = EmployeeDeduction(
        employee_id=payload.employee_id,
        deduction_type=payload.deduction_type,
        total_amount=total_amount,
        amount_per_cutoff=payload.amount_per_cutoff,
        remaining_balance=remaining_balance,
        start_date=payload.start_date,
        is_active=payload.is_active,
    )
    db.add(deduction)
    db.commit()
    db.refresh(deduction)
    return deduction


@router.put("/{deduction_id}", response_model=DeductionRead)
def update_deduction(deduction_id: int, payload: DeductionUpdate, db: Session = Depends(get_db)):
    deduction = _get_or_404(db, deduction_id)
    changes = payload.model_dump(exclude_unset=True)

    if deduction.deduction_type == DeductionType.MP2 and (
        changes.get("total_amount") is not None or changes.get("remaining_balance") is not None
    ):
        raise HTTPException(status_code=400, detail="MP2 has no total or balance")
    if "amount_per_cutoff" in changes and changes["amount_per_cutoff"] <= ZERO:
        raise HTTPException(status_code=400, detail="Amount per cutoff must be greater than zero")
    if changes.get("remaining_balance") is not None and changes["remaining_balance"] < ZERO:
        raise HTTPException(status_code=400, detail="Remaining balance cannot be negative")

    for field, value in changes.items():
        setattr(deduction, field, value)

    if (
        changes.get("is_active") is True
        and deduction.remaining_balance is not None
        and Decimal(deduction.remaining_balance) <= ZERO
    ):
        raise HTTPException(status_code=400, detail="This deduction is fully paid. Raise the remaining balance before resuming it")

    db.commit()
    db.refresh(deduction)
    return deduction


@router.delete("/{deduction_id}", status_code=204)
def delete_deduction(deduction_id: int, db: Session = Depends(get_db)):
    deduction = _get_or_404(db, deduction_id)
    if db.query(PayslipDeduction).filter(PayslipDeduction.employee_deduction_id == deduction_id).first():
        raise HTTPException(
            status_code=400,
            detail="This deduction has already been applied on a payslip and cannot be deleted. Pause it instead to preserve payroll history.",
        )
    db.delete(deduction)
    db.commit()
    return None
