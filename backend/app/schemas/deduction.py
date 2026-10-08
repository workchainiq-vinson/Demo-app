from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.deduction import DeductionType


class DeductionCreate(BaseModel):
    employee_id: int
    deduction_type: DeductionType
    total_amount: Optional[Decimal] = None  # required for everything except MP2
    amount_per_cutoff: Decimal
    start_date: date
    is_active: bool = True


class DeductionUpdate(BaseModel):
    total_amount: Optional[Decimal] = None
    amount_per_cutoff: Optional[Decimal] = None
    remaining_balance: Optional[Decimal] = None
    start_date: Optional[date] = None
    is_active: Optional[bool] = None


class DeductionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    deduction_type: DeductionType
    total_amount: Optional[Decimal] = None
    amount_per_cutoff: Decimal
    remaining_balance: Optional[Decimal] = None
    start_date: date
    is_active: bool


class AppliedDeductionRead(BaseModel):
    deduction_type: DeductionType
    label: str
    amount: Decimal
