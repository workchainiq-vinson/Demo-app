"""
Computes lateness and undertime minutes by comparing actual punches
(Attendance.time_in / time_out) against the employee's assigned Shift.

These are "raw minute" calculations meant to be run once at data-entry time
(e.g. when an attendance record is created/edited) and stored on the
Attendance row. The payroll engine (payroll_service.py) then consumes the
stored minutes directly rather than recomputing them.
"""
from datetime import date, datetime, time, timedelta


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
