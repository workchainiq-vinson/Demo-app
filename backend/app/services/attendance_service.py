"""
Computes lateness and undertime minutes by comparing actual punches
(Attendance.time_in / time_out) against the employee's assigned Shift.

These are "raw minute" calculations meant to be run once at data-entry time
(e.g. when an attendance record is created/edited) and stored on the
Attendance row. The payroll engine (payroll_service.py) then consumes the
stored minutes directly rather than recomputing them.
"""
from datetime import date, datetime, time, timedelta

from app.services import nsd_service


def _combine(the_date: date, the_time: time) -> datetime:
    return datetime.combine(the_date, the_time)


def compute_late_undertime_minutes(
    shift_start: time,
    shift_end: time,
    grace_period_minutes: int,
    attendance_date: date,
    time_in: datetime | None,
    time_out: datetime | None,
) -> tuple[int, int]:
    """
    Returns (late_minutes, undertime_minutes).

    Handles shifts that cross midnight (shift_end <= shift_start means the
    shift ends on the calendar day after attendance_date).
    """
    if time_in is None or time_out is None:
        return 0, 0

    scheduled_start = _combine(attendance_date, shift_start)
    crosses_midnight = shift_end <= shift_start
    end_date = attendance_date + timedelta(days=1) if crosses_midnight else attendance_date
    scheduled_end = _combine(end_date, shift_end)

    grace_deadline = scheduled_start + timedelta(minutes=grace_period_minutes)

    late_minutes = 0
    if time_in > grace_deadline:
        late_minutes = int((time_in - scheduled_start).total_seconds() // 60)

    undertime_minutes = 0
    if time_out < scheduled_end:
        undertime_minutes = int((scheduled_end - time_out).total_seconds() // 60)

    return max(late_minutes, 0), max(undertime_minutes, 0)


def recompute_derived_fields(attendance, employee) -> None:
    """
    Recomputes late/undertime/actual OT/NSD on an Attendance from its punches.
    Uses the record's own shift (employees can rotate daily), falling back to
    the employee's default shift for records that predate per-day shifts.
    """
    shift = attendance.shift or employee.default_shift
    if shift and attendance.time_in and attendance.time_out:
        late, undertime = compute_late_undertime_minutes(
            shift.start_time,
            shift.end_time,
            shift.grace_period_minutes,
            attendance.date,
            attendance.time_in,
            attendance.time_out,
        )
        attendance.late_minutes = late
        attendance.undertime_minutes = undertime

        scheduled_end_date = (
            attendance.date + timedelta(days=1) if shift.end_time <= shift.start_time else attendance.date
        )
        scheduled_end = datetime.combine(scheduled_end_date, shift.end_time)
        worked_past_shift = (attendance.time_out - scheduled_end).total_seconds() / 60
        attendance.actual_ot_minutes = max(0, int(worked_past_shift))
    else:
        attendance.late_minutes = 0
        attendance.undertime_minutes = 0
        attendance.actual_ot_minutes = 0

    attendance.nsd_minutes = nsd_service.compute_nsd_minutes(attendance.time_in, attendance.time_out)
