import uuid
from datetime import date as date_type
from decimal import ROUND_DOWN, Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.pakyaw import PakyawCatalog, PakyawLog
from app.schemas.pakyaw import (
    PakyawCatalogCreate,
    PakyawCatalogRead,
    PakyawGroupEntryCreate,
    PakyawLogCreate,
    PakyawLogRead,
)

router = APIRouter(prefix="/pakyaw", tags=["pakyaw"])

TWO_PLACES = Decimal("0.01")


@router.get("/catalog", response_model=list[PakyawCatalogRead])
def list_catalog(db: Session = Depends(get_db)):
    return db.query(PakyawCatalog).order_by(PakyawCatalog.task_name).all()


@router.post("/catalog", response_model=PakyawCatalogRead, status_code=201)
def create_catalog_item(payload: PakyawCatalogCreate, db: Session = Depends(get_db)):
    item = PakyawCatalog(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/logs", response_model=list[PakyawLogRead])
def list_logs(
    employee_id: Optional[int] = None,
    date_from: Optional[date_type] = None,
    date_to: Optional[date_type] = None,
    db: Session = Depends(get_db),
):
    query = db.query(PakyawLog)
    if employee_id is not None:
        query = query.filter(PakyawLog.employee_id == employee_id)
    if date_from is not None:
        query = query.filter(PakyawLog.date >= date_from)
    if date_to is not None:
        query = query.filter(PakyawLog.date <= date_to)
    return query.order_by(PakyawLog.date.desc()).all()


@router.post("/logs", response_model=PakyawLogRead, status_code=201)
def create_individual_log(payload: PakyawLogCreate, db: Session = Depends(get_db)):
    task = db.query(PakyawCatalog).filter(PakyawCatalog.id == payload.pakyaw_catalog_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Pakyaw catalog task not found")

    computed_pay = (payload.units_completed * task.rate_per_unit).quantize(TWO_PLACES)
    log = PakyawLog(
        employee_id=payload.employee_id,
        pakyaw_catalog_id=payload.pakyaw_catalog_id,
        date=payload.date,
        units_completed=payload.units_completed,
        computed_pay=computed_pay,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.post("/logs/group", response_model=list[PakyawLogRead], status_code=201)
def create_group_log(payload: PakyawGroupEntryCreate, db: Session = Depends(get_db)):
    """Divides total_units equally among employee_ids and creates one PakyawLog
    per employee, all sharing the same group_batch_id. Any remainder from the
    equal division (due to 2-decimal rounding) is added to the last employee's
    share so the sum of individual shares always equals total_units exactly.
    """
    if not payload.employee_ids:
        raise HTTPException(status_code=400, detail="employee_ids must not be empty")

    task = db.query(PakyawCatalog).filter(PakyawCatalog.id == payload.pakyaw_catalog_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Pakyaw catalog task not found")

    count = len(payload.employee_ids)
    per_share = (payload.total_units / count).quantize(TWO_PLACES, rounding=ROUND_DOWN)
    remainder = payload.total_units - (per_share * count)

    group_batch_id = str(uuid.uuid4())
    logs = []
    for index, employee_id in enumerate(payload.employee_ids):
        share = per_share + remainder if index == count - 1 else per_share
        computed_pay = (share * task.rate_per_unit).quantize(TWO_PLACES)
        log = PakyawLog(
            employee_id=employee_id,
            pakyaw_catalog_id=payload.pakyaw_catalog_id,
            date=payload.date,
            units_completed=share,
            group_batch_id=group_batch_id,
            computed_pay=computed_pay,
        )
        db.add(log)
        logs.append(log)

    db.commit()
    for log in logs:
        db.refresh(log)
    return logs
