from datetime import date

from pydantic import BaseModel, ConfigDict

from app.models.holiday import HolidayType


class HolidayBase(BaseModel):
    name: str
    date: date
    holiday_type: HolidayType = HolidayType.REGULAR


class HolidayCreate(HolidayBase):
    pass


class HolidayRead(HolidayBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
