"""
Seeds the database with:
  - PakyawCatalog manufacturing tasks
  - 2026 Philippine regular & special non-working holidays

Run from the `backend/` directory:
    python seeder.py

Note: 2026 special non-working holiday dates below follow the typical annual
pattern (Chinese New Year, EDSA anniversary, Ninoy Aquino Day, All Saints'/
Souls' Day, Immaculate Conception, Christmas Eve, Last Day of the Year) and
movable Holy Week dates computed from the 2026 Easter date. Confirm against
the official Malacañang proclamation once published, as exact special-day
declarations can shift year to year.
"""
from datetime import date

from app.database import Base, SessionLocal, engine
from app.models import Holiday, HolidayType, PakyawCatalog

PAKYAW_TASKS = [
    {"task_name": "Sorting - Raw Materials", "unit_of_measure": "kg", "rate_per_unit": "0.50"},
    {"task_name": "Washing - Raw Materials", "unit_of_measure": "kg", "rate_per_unit": "0.35"},
    {"task_name": "Peeling / Trimming", "unit_of_measure": "kg", "rate_per_unit": "0.75"},
    {"task_name": "Slicing / Cutting", "unit_of_measure": "kg", "rate_per_unit": "0.90"},
    {"task_name": "Weighing & Portioning", "unit_of_measure": "pack", "rate_per_unit": "0.60"},
    {"task_name": "Sealing / Packing", "unit_of_measure": "pack", "rate_per_unit": "0.45"},
    {"task_name": "Labeling", "unit_of_measure": "pack", "rate_per_unit": "0.20"},
    {"task_name": "Boxing / Casing", "unit_of_measure": "box", "rate_per_unit": "2.00"},
    {"task_name": "Loading to Delivery Truck", "unit_of_measure": "box", "rate_per_unit": "1.50"},
    {"task_name": "Quality Inspection", "unit_of_measure": "pack", "rate_per_unit": "0.30"},
]

HOLIDAYS_2026 = [
    # Regular Holidays
    {"name": "New Year's Day", "date": date(2026, 1, 1), "holiday_type": HolidayType.REGULAR},
    {"name": "Araw ng Kagitingan", "date": date(2026, 4, 9), "holiday_type": HolidayType.REGULAR},
    {"name": "Maundy Thursday", "date": date(2026, 4, 2), "holiday_type": HolidayType.REGULAR},
    {"name": "Good Friday", "date": date(2026, 4, 3), "holiday_type": HolidayType.REGULAR},
    {"name": "Labor Day", "date": date(2026, 5, 1), "holiday_type": HolidayType.REGULAR},
    {"name": "Independence Day", "date": date(2026, 6, 12), "holiday_type": HolidayType.REGULAR},
    {"name": "National Heroes Day", "date": date(2026, 8, 31), "holiday_type": HolidayType.REGULAR},
    {"name": "Bonifacio Day", "date": date(2026, 11, 30), "holiday_type": HolidayType.REGULAR},
    {"name": "Christmas Day", "date": date(2026, 12, 25), "holiday_type": HolidayType.REGULAR},
    {"name": "Rizal Day", "date": date(2026, 12, 30), "holiday_type": HolidayType.REGULAR},
    # Special Non-Working Days
    {"name": "Chinese New Year", "date": date(2026, 2, 17), "holiday_type": HolidayType.SPECIAL_NON_WORKING},
    {"name": "EDSA People Power Anniversary", "date": date(2026, 2, 25), "holiday_type": HolidayType.SPECIAL_NON_WORKING},
    {"name": "Black Saturday", "date": date(2026, 4, 4), "holiday_type": HolidayType.SPECIAL_NON_WORKING},
    {"name": "Ninoy Aquino Day", "date": date(2026, 8, 21), "holiday_type": HolidayType.SPECIAL_NON_WORKING},
    {"name": "All Saints' Day", "date": date(2026, 11, 1), "holiday_type": HolidayType.SPECIAL_NON_WORKING},
    {"name": "Feast of the Immaculate Conception", "date": date(2026, 12, 8), "holiday_type": HolidayType.SPECIAL_NON_WORKING},
    {"name": "Christmas Eve", "date": date(2026, 12, 24), "holiday_type": HolidayType.SPECIAL_NON_WORKING},
    {"name": "Last Day of the Year", "date": date(2026, 12, 31), "holiday_type": HolidayType.SPECIAL_NON_WORKING},
]


def seed_pakyaw_catalog(db):
    if db.query(PakyawCatalog).count() > 0:
        print("PakyawCatalog already seeded, skipping.")
        return
    for task in PAKYAW_TASKS:
        db.add(PakyawCatalog(**task))
    db.commit()
    print(f"Seeded {len(PAKYAW_TASKS)} PakyawCatalog tasks.")


def seed_holidays(db):
    if db.query(Holiday).count() > 0:
        print("Holidays already seeded, skipping.")
        return
    for holiday in HOLIDAYS_2026:
        db.add(Holiday(**holiday))
    db.commit()
    print(f"Seeded {len(HOLIDAYS_2026)} holidays for 2026.")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_pakyaw_catalog(db)
        seed_holidays(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
