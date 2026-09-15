from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    time_in = Column(DateTime, nullable=True)
    time_out = Column(DateTime, nullable=True)

    actual_ot_minutes = Column(Integer, nullable=False, default=0)
    approved_ot_minutes = Column(Integer, nullable=False, default=0)
    nsd_minutes = Column(Integer, nullable=False, default=0)
    late_minutes = Column(Integer, nullable=False, default=0)
    undertime_minutes = Column(Integer, nullable=False, default=0)

    is_rest_day_worked = Column(Boolean, nullable=False, default=False)
    holiday_id = Column(Integer, ForeignKey("holidays.id"), nullable=True)

    employee = relationship("Employee", back_populates="attendances")
    holiday = relationship("Holiday", back_populates="attendances")
