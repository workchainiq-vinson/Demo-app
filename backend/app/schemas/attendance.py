from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AttendanceCreate(BaseModel):
    employee_id: int
    date: date
    shift_id: Optional[int] = None
    time_in: Optional[datetime] = None
    time_out: Optional[datetime] = None
    break_out: Optional[datetime] = None
    break_in: Optional[datetime] = None
    mid_break_out: Optional[datetime] = None
    mid_break_in: Optional[datetime] = None
    second_break_out: Optional[datetime] = None
    second_break_in: Optional[datetime] = None
    is_rest_day_worked: bool = False
    holiday_id: Optional[int] = None


class AttendanceUpdate(BaseModel):
    shift_id: Optional[int] = None
    time_in: Optional[datetime] = None
    time_out: Optional[datetime] = None
    break_out: Optional[datetime] = None
    break_in: Optional[datetime] = None
    mid_break_out: Optional[datetime] = None
    mid_break_in: Optional[datetime] = None
    second_break_out: Optional[datetime] = None
    second_break_in: Optional[datetime] = None
    is_rest_day_worked: Optional[bool] = None
    holiday_id: Optional[int] = None


class AttendanceApproveOT(BaseModel):
    approved_ot_minutes: int


class AttendanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    date: date
    shift_id: Optional[int] = None
    time_in: Optional[datetime] = None
    time_out: Optional[datetime] = None
    break_out: Optional[datetime] = None
    break_in: Optional[datetime] = None
    mid_break_out: Optional[datetime] = None
    mid_break_in: Optional[datetime] = None
    second_break_out: Optional[datetime] = None
    second_break_in: Optional[datetime] = None
    actual_ot_minutes: int
    approved_ot_minutes: int
    nsd_minutes: int
    late_minutes: int
    undertime_minutes: int
    is_rest_day_worked: bool
    holiday_id: Optional[int] = None
