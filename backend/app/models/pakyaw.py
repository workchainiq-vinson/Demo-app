from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.database import Base


class PakyawCatalog(Base):
    __tablename__ = "pakyaw_catalog"

    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String, nullable=False)
    unit_of_measure = Column(String, nullable=False)
    rate_per_unit = Column(Numeric(10, 4), nullable=False)

    logs = relationship("PakyawLog", back_populates="task")


class PakyawLog(Base):
    __tablename__ = "pakyaw_logs"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    pakyaw_catalog_id = Column(Integer, ForeignKey("pakyaw_catalog.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    units_completed = Column(Numeric(10, 2), nullable=False)
    group_batch_id = Column(String, nullable=True, index=True)
    computed_pay = Column(Numeric(10, 2), nullable=False, default=0)

    employee = relationship("Employee", back_populates="pakyaw_logs")
    task = relationship("PakyawCatalog", back_populates="logs")
