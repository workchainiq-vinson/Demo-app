from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.employee import EmploymentType


class EmployeeBase(BaseModel):
    employee_code: str
    first_name: str
    last_name: str
    employment_type: EmploymentType = EmploymentType.REGULAR
    daily_rate: Decimal = Decimal("0.00")
    rest_day_of_week: Optional[int] = None
    default_shift_id: Optional[int] = None
    is_active: bool = True


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    employee_code: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    employment_type: Optional[EmploymentType] = None
    daily_rate: Optional[Decimal] = None
    rest_day_of_week: Optional[int] = None
    default_shift_id: Optional[int] = None
    is_active: Optional[bool] = None


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
