import enum

from sqlalchemy import Column, Date, Enum, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class HolidayType(str, enum.Enum):
    REGULAR = "REGULAR"
    SPECIAL_NON_WORKING = "SPECIAL_NON_WORKING"


class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False, unique=True)
    holiday_type = Column(Enum(HolidayType), nullable=False, default=HolidayType.REGULAR)

    attendances = relationship("Attendance", back_populates="holiday")
