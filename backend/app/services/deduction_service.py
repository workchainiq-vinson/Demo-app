"""
Recurring per-cutoff deductions (loans, MP2 savings, petty cash advances).

compute_applicable_deductions is pure: it only reads. The payroll router is
responsible for persisting PayslipDeduction rows and decrementing balances in
the same transaction as the payslip itself.
"""
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.deduction import DeductionType, EmployeeDeduction

TWO_PLACES = Decimal("0.01")

DEDUCTION_LABELS = {
    DeductionType.SSS_LOAN: "SSS Loan",
    DeductionType.PAGIBIG_LOAN: "Pag-IBIG Loan",
    DeductionType.MP2: "MP2",
    DeductionType.CALAMITY_LOAN: "Calamity Loan",
    DeductionType.PETTY_CASH: "Petty Cash",
}

# Fixed column order used by every report that breaks deductions out by type.
DEDUCTION_ORDER = [
    DeductionType.SSS_LOAN,
    DeductionType.PAGIBIG_LOAN,
    DeductionType.MP2,
    DeductionType.CALAMITY_LOAN,
    DeductionType.PETTY_CASH,
]


def compute_applicable_deductions(db: Session, employee_id: int, cutoff_end: date) -> list[dict]:
    rows = (
        db.query(EmployeeDeduction)
        .filter(
            EmployeeDeduction.employee_id == employee_id,
            EmployeeDeduction.is_active == True,  # noqa: E712
            EmployeeDeduction.start_date <= cutoff_end,
        )
        .order_by(EmployeeDeduction.id)
        .all()
    )

    applicable = []
    for deduction in rows:
        per_cutoff = Decimal(deduction.amount_per_cutoff)
        # MP2 has no balance and runs until paused; loans never overshoot what's left.
        if deduction.remaining_balance is None:
            amount = per_cutoff
        else:
            amount = min(per_cutoff, Decimal(deduction.remaining_balance))
        if amount <= 0:
            continue
        applicable.append(
            {
                "employee_deduction_id": deduction.id,
                "deduction_type": deduction.deduction_type,
                "label": DEDUCTION_LABELS[deduction.deduction_type],
                "amount": amount.quantize(TWO_PLACES),
            }
        )
    return applicable
