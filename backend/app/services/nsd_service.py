"""
Night Shift Differential: 10% premium of the hourly rate for actual minutes
worked between 22:00 and 06:00. Computed as interval-overlap between the
actual time_in/time_out punches and every 22:00->06:00 night window that
could plausibly intersect them, so midnight-crossing shifts are handled
correctly (e.g. a 22:00-06:00 shift, or a 6:00pm-3am shift).
"""
from datetime import datetime, time, timedelta
from decimal import Decimal

NIGHT_START = time(22, 0)
NIGHT_WINDOW_HOURS = 8  # 22:00 -> 06:00 next day
NSD_MULTIPLIER = Decimal("0.10")


def _overlap_minutes(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> int:
    latest_start = max(start_a, start_b)
    earliest_end = min(end_a, end_b)
    delta = (earliest_end - latest_start).total_seconds()
    return max(0, int(delta // 60))


def compute_nsd_minutes(time_in: datetime | None, time_out: datetime | None) -> int:
    if time_in is None or time_out is None or time_out <= time_in:
        return 0

    total_minutes = 0
    # Check the night window anchored on the day before time_in through the
    # day after time_out, covering any midnight crossover in either direction.
    day_cursor = (time_in - timedelta(days=1)).date()
    last_day = time_out.date()
    while day_cursor <= last_day:
        window_start = datetime.combine(day_cursor, NIGHT_START)
        window_end = window_start + timedelta(hours=NIGHT_WINDOW_HOURS)
        total_minutes += _overlap_minutes(time_in, time_out, window_start, window_end)
        day_cursor += timedelta(days=1)

    return total_minutes


def compute_nsd_pay(hourly_rate: Decimal, nsd_minutes: int) -> Decimal:
    if nsd_minutes <= 0:
        return Decimal("0.00")
    hours = Decimal(nsd_minutes) / Decimal(60)
    return (hourly_rate * NSD_MULTIPLIER * hours).quantize(Decimal("0.01"))
