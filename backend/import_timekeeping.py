"""
Imports a "Daily Timekeeping Logs Report" (.xls) into employees, shifts and attendance.

    python import_timekeeping.py REPORT.xls                # dry run: counts + anomalies, writes nothing
    python import_timekeeping.py REPORT.xls --apply        # backs up the DB, then imports in one transaction

Safe to re-run for later cutoffs: shifts are found by (start, end), employees by
code, and attendance by (employee, date); existing rows are never touched.
Run from the backend/ directory (the default database path is relative).
"""
import argparse
import re
import shutil
import sys
import tempfile
from collections import defaultdict
from datetime import datetime, time, timedelta
from decimal import Decimal
from pathlib import Path

import xlrd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, run_additive_migrations
from app.models import attendance, deduction, employee, holiday, pakyaw, payroll, shift  # noqa: F401  (register tables)
from app.models.attendance import Attendance
from app.models.employee import Employee, EmploymentStatus, EmploymentType
from app.models.shift import Shift
from app.services import attendance_service

DEFAULT_DB = "bio_green.db"
DAILY_RATE = Decimal("485.00")
DEPARTMENT = "Production"
START_ONLY_HOURS = 8
GRACE_MINUTES = 0

# Column positions in the report's day rows.
COL_NAME, COL_DATE, COL_SHIFT, COL_IN, COL_BREAK_OUT, COL_BREAK_IN, COL_OUT = 0, 1, 3, 6, 8, 10, 22

HEADER_RE = re.compile(r"^(.+?) - (\d+)$")
RANGE_RE = re.compile(r"(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})")
START_RE = re.compile(r"(\d{1,2}):(\d{2})\s*time\s*in", re.IGNORECASE)
CLOCK_RE = re.compile(r"^(\d{1,2}):(\d{2})$")


def serial_to_dt(value: float) -> datetime:
    # Excel serials carry float noise (12:38:00.0001), so round to the nearest minute.
    d = xlrd.xldate_as_datetime(value, 0)
    return (d + timedelta(seconds=30)).replace(second=0, microsecond=0)


def parse_shift_label(label: str) -> tuple[time, time] | None:
    m = RANGE_RE.search(label)
    if m:
        return time(int(m[1]), int(m[2])), time(int(m[3]), int(m[4]))
    m = START_RE.search(label)
    if m:
        start = time(int(m[1]), int(m[2]))
        end_hour = (start.hour + START_ONLY_HOURS) % 24
        return start, time(end_hour, start.minute)
    return None


def anchor_clock(text: str, reference: datetime) -> datetime | None:
    """Places an 'HH:MM' on the first moment at/after `reference` that shows that clock time."""
    m = CLOCK_RE.match(text.strip())
    if not m:
        return None
    candidate = datetime.combine(reference.date(), time(int(m[1]), int(m[2])))
    return candidate if candidate >= reference else candidate + timedelta(days=1)


def parse_report(path: str):
    """Returns ({code: {"first","last","days": {logdate: row}}}, problems)."""
    sheet = xlrd.open_workbook(path).sheet_by_index(0)
    cell = sheet.cell_value
    people: dict[str, dict] = {}
    problems: list[str] = []
    current = None
    for r in range(sheet.nrows):
        head = str(cell(r, COL_NAME)).strip()
        m = HEADER_RE.match(head) if head else None
        if m:
            last, _, first = m[1].partition(",")
            person = people.setdefault(m[2], {"first": first.strip(), "last": last.strip(), "days": {}})
            current = person
            continue
        if current is None or not isinstance(cell(r, COL_DATE), float):
            continue
        log_date = xlrd.xldate_as_datetime(cell(r, COL_DATE), 0).date()
        if cell(r, COL_IN) == "" and cell(r, COL_OUT) == "":
            continue  # no punches: not a worked day
        if log_date in current["days"]:
            problems.append(f"{current['last']}, {current['first']}: duplicate row for {log_date}")
            continue
        current["days"][log_date] = {
            "shift": str(cell(r, COL_SHIFT)).strip(),
            "in": cell(r, COL_IN),
            "out": cell(r, COL_OUT),
            "break_out": str(cell(r, COL_BREAK_OUT)).strip(),
            "break_in": str(cell(r, COL_BREAK_IN)).strip(),
        }
    return people, problems


def build_plan(people):
    """Resolves each worked day into concrete datetimes and collects anomalies."""
    shifts_needed: dict[tuple[time, time], str] = {}
    rows = []
    anomalies: list[str] = []
    for code, person in people.items():
        who = f"{person['last']}, {person['first']} ({code})"
        for log_date, day in sorted(person["days"].items()):
            rng = parse_shift_label(day["shift"]) if day["shift"] else None
            if day["shift"] and rng is None:
                anomalies.append(f"{who} {log_date}: unreadable shift label {day['shift']!r}; imported without a shift")
            if rng:
                shifts_needed.setdefault(rng, f"{rng[0]:%H:%M}-{rng[1]:%H:%M}")
            time_in = serial_to_dt(day["in"]) if day["in"] != "" else None
            time_out = serial_to_dt(day["out"]) if day["out"] != "" else None
            if time_in is None or time_out is None:
                anomalies.append(f"{who} {log_date}: missing {'log-in' if time_in is None else 'log-out'}")
            if time_in and not (log_date <= time_in.date() <= log_date + timedelta(days=1)):
                anomalies.append(f"{who} {log_date}: log-in {time_in:%Y-%m-%d %H:%M} is outside the log date")
            break_out = break_in = None
            if time_in and day["break_out"]:
                break_out = anchor_clock(day["break_out"], time_in)
                if break_out is None:
                    anomalies.append(f"{who} {log_date}: unreadable break-out {day['break_out']!r}")
            if break_out and day["break_in"]:
                break_in = anchor_clock(day["break_in"], break_out)
                if break_in is None:
                    anomalies.append(f"{who} {log_date}: unreadable break-in {day['break_in']!r}")
            if day["break_out"] and not day["break_in"]:
                anomalies.append(f"{who} {log_date}: break-out {day['break_out']} has no break-in")
            if break_in and time_out and break_in > time_out:
                anomalies.append(f"{who} {log_date}: break-in {break_in:%H:%M} is after log-out {time_out:%m-%d %H:%M}")
            if time_in and time_out:
                span = (time_out - time_in).total_seconds() / 3600
                if span > 14:
                    anomalies.append(f"{who} {log_date}: {span:.1f}h between log-in and log-out (missed punch?)")
                if rng:
                    start = datetime.combine(log_date, rng[0])
                    end = datetime.combine(log_date + timedelta(days=int(rng[1] <= rng[0])), rng[1])
                    if (time_out - end).total_seconds() / 60 > 240:
                        anomalies.append(f"{who} {log_date}: log-out {(time_out - end).total_seconds() / 3600:.1f}h after shift end")
                    elif (end - time_out).total_seconds() / 60 > 120:
                        anomalies.append(f"{who} {log_date}: log-out {(end - time_out).total_seconds() / 3600:.1f}h before shift end")
                    if abs((time_in - start).total_seconds()) / 3600 > 4:
                        anomalies.append(f"{who} {log_date}: log-in {abs((time_in - start).total_seconds()) / 3600:.1f}h from shift start")
            rows.append(
                {"code": code, "date": log_date, "shift": rng, "in": time_in, "out": time_out, "bo": break_out, "bi": break_in}
            )
    return shifts_needed, rows, anomalies


def verified_backup(db_path: Path, backup_dir: Path) -> Path:
    """Copies the database and proves the copy is complete. Raises if anything is off."""
    if not db_path.is_file():
        raise RuntimeError(f"database {db_path} does not exist; nothing to back up")
    target = backup_dir / f"{db_path.name}.bak-{datetime.now():%Y%m%d-%H%M%S}"
    shutil.copy2(db_path, target)
    if not target.is_file() or target.stat().st_size != db_path.stat().st_size:
        raise RuntimeError(f"backup {target} failed verification")
    return target


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report", help="path to the .xls timekeeping report")
    ap.add_argument("--apply", action="store_true", help="write to the database (default is a dry run)")
    ap.add_argument("--db", default=DEFAULT_DB, help=f"SQLite file (default {DEFAULT_DB})")
    ap.add_argument("--backup-dir", help="where to put the pre-import backup (default: next to the database)")
    args = ap.parse_args()

    people, problems = parse_report(args.report)
    shifts_needed, rows, anomalies = build_plan(people)
    anomalies = problems + anomalies
    split_rows = defaultdict(int)
    for row in rows:
        split_rows[row["code"]] += 1

    print(f"Report: {len(people)} employees, {len(shifts_needed)} distinct shifts, {len(rows)} worked days")

    db_path = Path(args.db)
    scratch = None
    if args.apply:
        backup = verified_backup(db_path, Path(args.backup_dir) if args.backup_dir else db_path.parent)
        print(f"Backup verified: {backup} ({backup.stat().st_size} bytes)")
        work_path = db_path
    else:
        # Dry run executes the real import against a throwaway copy, so the
        # real database is never migrated or written.
        scratch = tempfile.TemporaryDirectory()
        work_path = Path(scratch.name) / "dry-run.db"
        if db_path.is_file():
            shutil.copy2(db_path, work_path)

    engine = create_engine(f"sqlite:///{work_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    run_additive_migrations(engine)

    session = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    created = {"employees": 0, "shifts": 0, "attendance": 0}
    skipped = 0
    try:
        shift_by_range: dict[tuple[time, time], Shift] = {(s.start_time, s.end_time): s for s in session.query(Shift)}
        emp_by_code: dict[str, Employee] = {e.employee_code: e for e in session.query(Employee)}

        for rng, name in sorted(shifts_needed.items()):
            if rng not in shift_by_range:
                s = Shift(name=name, start_time=rng[0], end_time=rng[1], grace_period_minutes=GRACE_MINUTES)
                session.add(s)
                shift_by_range[rng] = s
                created["shifts"] += 1

        for code, person in sorted(people.items()):
            if code not in emp_by_code:
                e = Employee(
                    employee_code=code,
                    first_name=person["first"],
                    last_name=person["last"],
                    department=DEPARTMENT,
                    employment_type=EmploymentType.REGULAR,
                    employment_status=EmploymentStatus.REGULAR,
                    daily_rate=DAILY_RATE,
                    rest_day_of_week=None,
                    is_active=True,
                )
                session.add(e)
                emp_by_code[code] = e
                created["employees"] += 1
        session.flush()

        seen = {(a.employee_id, a.date) for a in session.query(Attendance.employee_id, Attendance.date)}
        for row in rows:
            emp = emp_by_code[row["code"]]
            key = (emp.id, row["date"])
            if key in seen:
                skipped += 1
                continue
            seen.add(key)
            a = Attendance(
                employee_id=emp.id,
                date=row["date"],
                shift=shift_by_range.get(row["shift"]) if row["shift"] else None,
                time_in=row["in"],
                time_out=row["out"],
                break_out=row["bo"],
                break_in=row["bi"],
            )
            attendance_service.recompute_derived_fields(a, emp)
            session.add(a)
            created["attendance"] += 1

        session.commit()
    except Exception:
        session.rollback()
        print("Import failed; nothing was written.", file=sys.stderr)
        raise
    finally:
        session.close()
        engine.dispose()
        if scratch:
            scratch.cleanup()

    verb = "Created" if args.apply else "Would create"
    print(
        f"{verb}: {created['employees']} employees, {created['shifts']} shifts, {created['attendance']} attendance rows"
        f" (skipped {skipped} already present)"
    )
    print(f"\nAnomalies ({len(anomalies)}), imported as recorded:")
    for line in anomalies:
        print(f"  - {line}")
    if not args.apply:
        print("\nDry run only. Re-run with --apply to write (a verified backup is taken first).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
