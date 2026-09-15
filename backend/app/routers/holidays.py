from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.holiday import Holiday
from app.schemas.holiday import HolidayCreate, HolidayRead

router = APIRouter(prefix="/holidays", tags=["holidays"])


@router.get("", response_model=list[HolidayRead])
def list_holidays(db: Session = Depends(get_db)):
    return db.query(Holiday).order_by(Holiday.date).all()


@router.post("", response_model=HolidayRead, status_code=201)
def create_holiday(payload: HolidayCreate, db: Session = Depends(get_db)):
    if db.query(Holiday).filter(Holiday.date == payload.date).first():
        raise HTTPException(status_code=400, detail="A holiday already exists on this date")
    holiday = Holiday(**payload.model_dump())
    db.add(holiday)
    db.commit()
    db.refresh(holiday)
    return holiday


@router.delete("/{holiday_id}", status_code=204)
def delete_holiday(holiday_id: int, db: Session = Depends(get_db)):
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    db.delete(holiday)
    db.commit()
    return None
