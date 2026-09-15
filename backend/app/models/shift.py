from sqlalchemy import Column, Integer, String, Time
from sqlalchemy.orm import relationship

from app.database import Base


class Shift(Base):
    __tablename__ = "shifts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    grace_period_minutes = Column(Integer, nullable=False, default=0)

    employees = relationship("Employee", back_populates="default_shift")
