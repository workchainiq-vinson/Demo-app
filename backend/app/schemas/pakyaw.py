from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PakyawCatalogBase(BaseModel):
    task_name: str
    unit_of_measure: str
    rate_per_unit: Decimal


class PakyawCatalogCreate(PakyawCatalogBase):
    pass


class PakyawCatalogRead(PakyawCatalogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class PakyawLogCreate(BaseModel):
    """Individual pakyaw entry: one employee logs their own output."""

    employee_id: int
    pakyaw_catalog_id: int
    date: date
    units_completed: Decimal


class PakyawGroupEntryCreate(BaseModel):
    """Group pakyaw entry: total output is divided equally among the team."""

    employee_ids: list[int]
    pakyaw_catalog_id: int
    date: date
    total_units: Decimal


class PakyawLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    pakyaw_catalog_id: int
    date: date
    units_completed: Decimal
    group_batch_id: Optional[str] = None
    computed_pay: Decimal
