import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import relationship

from app.database import Base


class EmploymentType(str, enum.Enum):
    REGULAR = "REGULAR"
    PAKYAW = "PAKYAW"
    MIXED = "MIXED"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    department = Column(String, nullable=True)
    employment_type = Column(Enum(EmploymentType), nullable=False, default=EmploymentType.REGULAR)
    daily_rate = Column(Numeric(10, 2), nullable=False, default=0)
    rest_day_of_week = Column(Integer, nullable=True)  # 0=Monday ... 6=Sunday
    default_shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    default_shift = relationship("Shift", back_populates="employees")
    attendances = relationship("Attendance", back_populates="employee")
    pakyaw_logs = relationship("PakyawLog", back_populates="employee")
    payslips = relationship("PayrollPayslip", back_populates="employee")
