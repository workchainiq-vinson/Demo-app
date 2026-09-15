from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class PayrollRun(Base):
    __tablename__ = "payroll_runs"

    id = Column(Integer, primary_key=True, index=True)
    cutoff_start = Column(Date, nullable=False)
    cutoff_end = Column(Date, nullable=False)
    apply_statutory_deductions = Column(Boolean, nullable=False, default=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, nullable=False, default="COMPLETED")

    payslips = relationship("PayrollPayslip", back_populates="payroll_run")


class PayrollPayslip(Base):
    __tablename__ = "payroll_payslips"

    id = Column(Integer, primary_key=True, index=True)
    payroll_run_id = Column(Integer, ForeignKey("payroll_runs.id"), nullable=False, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)

    gross_pay = Column(Numeric(10, 2), nullable=False, default=0)
    sss_deduction = Column(Numeric(10, 2), nullable=False, default=0)
    philhealth_deduction = Column(Numeric(10, 2), nullable=False, default=0)
    pagibig_deduction = Column(Numeric(10, 2), nullable=False, default=0)
    total_deductions = Column(Numeric(10, 2), nullable=False, default=0)
    net_pay = Column(Numeric(10, 2), nullable=False, default=0)

    # JSON-encoded line-item breakdown (regular pay, OT pay, NSD pay, pakyaw pay,
    # holiday premium, lateness deduction) so the PDF generator can render
    # a detailed payslip without recomputing figures.
    breakdown = Column(Text, nullable=True)

    payroll_run = relationship("PayrollRun", back_populates="payslips")
    employee = relationship("Employee", back_populates="payslips")
