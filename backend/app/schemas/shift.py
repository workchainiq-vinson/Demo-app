from datetime import time

from pydantic import BaseModel, ConfigDict


class ShiftBase(BaseModel):
    name: str
    start_time: time
    end_time: time
    grace_period_minutes: int = 0


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(BaseModel):
    name: str | None = None
    start_time: time | None = None
    end_time: time | None = None
    grace_period_minutes: int | None = None


class ShiftRead(ShiftBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
