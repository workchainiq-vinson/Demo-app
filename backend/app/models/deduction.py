import enum

from sqlalchemy import Boolean, Column, Date, Enum, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from app.database import Base


class DeductionType(str, enum.Enum):
    SSS_LOAN = "SSS_LOAN"
    PAGIBIG_LOAN = "PAGIBIG_LOAN"
    MP2 = "MP2"
    CALAMITY_LOAN = "CALAMITY_LOAN"
    PETTY_CASH = "PETTY_CASH"


class EmployeeDeduction(Base):
    """A recurring per-cutoff payroll deduction for one employee.

    total_amount / remaining_balance are NULL for MP2, which is an open-ended
    voluntary savings contribution with no payoff.
    """

    __tablename__ = "employee_deductions"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    deduction_type = Column(Enum(DeductionType), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=True)
    amount_per_cutoff = Column(Numeric(10, 2), nullable=False)
    remaining_balance = Column(Numeric(10, 2), nullable=True)
    start_date = Column(Date, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    employee = relationship("Employee", back_populates="deductions")
    applications = relationship("PayslipDeduction", back_populates="employee_deduction")


class PayslipDeduction(Base):
    """One row per deduction actually applied on a payslip, so payslips stay
    auditable and reports can sum by type."""

    __tablename__ = "payslip_deductions"

    id = Column(Integer, primary_key=True, index=True)
    payslip_id = Column(Integer, ForeignKey("payroll_payslips.id"), nullable=False, index=True)
    employee_deduction_id = Column(Integer, ForeignKey("employee_deductions.id"), nullable=False, index=True)
    deduction_type = Column(Enum(DeductionType), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)

    payslip = relationship("PayrollPayslip", back_populates="applied_deductions")
    employee_deduction = relationship("EmployeeDeduction", back_populates="applications")
