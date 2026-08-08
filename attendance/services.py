"""
Punch In/Out core logic.

Ek hi button employee ke liye "Punch In" / "Punch Out" dono kaam karta hai:
- Din ka pehla punch      -> Punch In   (check_in / shift ke against late check)
- Uske baad har Punch Out -> break shuru
- Uske baad wapas Punch In -> break khatam (break_count ++, break minutes add)
- Jo bhi aakhri punch OUT hota hai wahi din ka check_out maana jata hai

Har punch ke baad AttendanceRecord us date ke saare PunchLog se dubara
calculate (recompute) hoti hai, isliye data hamesha punch history se
consistent rehta hai.
"""
from datetime import timedelta
from django.utils import timezone

from .models import AttendanceRecord, PunchLog


class PunchError(Exception):
    """Raised for any invalid punch attempt (bad date, already punched, etc.)."""
    pass


def get_day_punches(employee, for_date):
    return list(
        PunchLog.objects.filter(employee=employee, date=for_date).order_by('timestamp')
    )


def get_punch_state(employee, for_date):
    """
    Returns a dict describing where the employee currently stands for a
    given date, built from PunchLog rows only (used for live dashboard UI).
    """
    punches = get_day_punches(employee, for_date)
    is_punched_in = bool(punches) and punches[-1].punch_type == 'in'

    first_in = punches[0].timestamp if punches and punches[0].punch_type == 'in' else None
    last_out = punches[-1].timestamp if punches and punches[-1].punch_type == 'out' else None

    break_minutes, break_count = _compute_breaks(punches)

    return {
        'punches': punches,
        'has_punched_today': bool(punches),
        'is_punched_in': is_punched_in,
        'on_break': (not is_punched_in) and bool(punches),
        'first_in': first_in,
        'last_out': last_out,
        'break_count': break_count,
        'break_minutes': break_minutes,
    }


def _compute_breaks(punches):
    """
    Breaks = every (Out -> next In) gap, EXCLUDING a trailing Out that has
    no following In yet (that trailing Out is just 'currently on break' or
    'punched out for the day' — not a completed break).
    """
    break_minutes = 0
    break_count = 0
    pending_out = None
    for p in punches:
        if p.punch_type == 'out':
            pending_out = p.timestamp
        elif p.punch_type == 'in' and pending_out is not None:
            delta = p.timestamp - pending_out
            break_minutes += max(0, int(delta.total_seconds() // 60))
            break_count += 1
            pending_out = None
    return break_minutes, break_count


def toggle_punch(employee, at=None):
    """
    Main entry point called by the dashboard Punch In/Out button.
    Decides In vs Out automatically based on the last punch of the day.
    """
    now = at or timezone.localtime()
    today = now.date()

    if employee.date_joined and today < employee.date_joined:
        raise PunchError("Punch not allowed before your date of joining.")

    if employee.status in ('terminated', 'inactive'):
        raise PunchError("Your account is inactive. Contact HR.")

    punches = get_day_punches(employee, today)
    next_type = 'in' if (not punches or punches[-1].punch_type == 'out') else 'out'

    PunchLog.objects.create(
        employee=employee, date=today, punch_type=next_type, timestamp=now
    )

    record = recalculate_attendance(employee, today)
    return next_type, record


def record_device_punch(employee, at, device_serial='', raw_state=None):
    """
    Same as toggle_punch(), but for punches coming from a biometric
    machine: the timestamp is whatever the device reported (not "now"),
    and we guard against a device re-sending the same scan (common with
    ZKTeco/eSSL ADMS retries) by ignoring a punch within 60 seconds of the
    employee's last recorded punch.

    raw_state: device's own in/out flag if it sent one (0=in, 1=out on
    most ZKTeco-compatible machines). If not usable, we fall back to the
    same auto-toggle logic as the web Punch button.
    """
    at = timezone.localtime(at)
    today = at.date()

    last_punch = PunchLog.objects.filter(employee=employee).order_by('-timestamp').first()
    if last_punch and abs((at - timezone.localtime(last_punch.timestamp)).total_seconds()) < 60:
        return None, None  # duplicate scan, ignore

    if raw_state == '0':
        next_type = 'in'
    elif raw_state == '1':
        next_type = 'out'
    else:
        todays = get_day_punches(employee, today)
        next_type = 'in' if (not todays or todays[-1].punch_type == 'out') else 'out'

    punch = PunchLog.objects.create(
        employee=employee, date=today, punch_type=next_type, timestamp=at,
        source='device', device_serial=device_serial,
    )
    record = recalculate_attendance(employee, today)
    return punch, record


def recalculate_attendance(employee, for_date):
    """
    Rebuilds the AttendanceRecord for one employee/date from PunchLog rows.
    Called after every punch, and safe to re-run any time (idempotent).
    """
    punches = get_day_punches(employee, for_date)

    record, _ = AttendanceRecord.objects.get_or_create(
        employee=employee, date=for_date, defaults={'status': 'absent'}
    )

    if not punches:
        return record

    first_in = punches[0].timestamp if punches[0].punch_type == 'in' else None
    last_out = punches[-1].timestamp if punches[-1].punch_type == 'out' else None
    is_punched_in = punches[-1].punch_type == 'in'

    break_minutes, break_count = _compute_breaks(punches)

    record.check_in = timezone.localtime(first_in).time() if first_in else record.check_in
    if last_out:
        record.check_out = timezone.localtime(last_out).time()
    record.break_count = break_count
    record.total_break_minutes = break_minutes
    record.is_punched_in = is_punched_in

    # Working hours: from first punch-in to (last punch-out OR now if still
    # punched in / on break) minus total break minutes.
    end_point = last_out if last_out else timezone.now()
    if first_in:
        gross_minutes = max(0, int((end_point - first_in).total_seconds() // 60))
        net_minutes = max(0, gross_minutes - break_minutes)
        record.working_hours = round(net_minutes / 60, 2)

    # Status: Late if first punch-in is after shift start + grace.
    if first_in:
        shift = employee.shift
        if shift:
            grace = timedelta(minutes=shift.grace_minutes)
            shift_start_dt = timezone.localtime(first_in).replace(
                hour=shift.start_time.hour, minute=shift.start_time.minute,
                second=0, microsecond=0
            )
            if timezone.localtime(first_in) > shift_start_dt + grace:
                record.status = 'late'
            else:
                record.status = 'present'
        else:
            record.status = 'present'

    record.save()
    return record