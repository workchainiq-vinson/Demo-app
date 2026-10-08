from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.deduction import AppliedDeductionRead


class PayrollGenerateRequest(BaseModel):
    cutoff_start: date
    cutoff_end: date
    apply_statutory_deductions: bool = True
    apply_other_deductions: bool = True  # loans, MP2, petty cash
    employee_ids: Optional[list[int]] = None  # None = all active employees


class PayslipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payroll_run_id: int
    employee_id: int
    employee_name: str
    gross_pay: Decimal
    sss_deduction: Decimal
    philhealth_deduction: Decimal
    pagibig_deduction: Decimal
    other_deductions: Decimal = Decimal("0.00")  # sum of loans / MP2 / petty cash
    deductions: list[AppliedDeductionRead] = []
    total_deductions: Decimal
    net_pay: Decimal
    breakdown: dict


class PayrollRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cutoff_start: date
    cutoff_end: date
    apply_statutory_deductions: bool
    generated_at: Optional[datetime] = None
    status: str
    payslips: list[PayslipRead] = []
