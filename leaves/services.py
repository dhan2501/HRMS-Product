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
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from attendance.models import AttendanceRecord, PunchLog, Holiday
from .models import LeaveType, LeaveBalance


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


# def toggle_punch(employee, at=None):
#     """
#     Main entry point called by the dashboard Punch In/Out button.
#     Decides In vs Out automatically based on the last punch of the day.
#     """
#     now = at or timezone.localtime()
#     today = now.date()

#     if employee.date_joined and today < employee.date_joined:
#         raise PunchError("Punch not allowed before your date of joining.")

#     if employee.status in ('terminated', 'inactive'):
#         raise PunchError("Your account is inactive. Contact HR.")

#     punches = get_day_punches(employee, today)
#     next_type = 'in' if (not punches or punches[-1].punch_type == 'out') else 'out'

#     PunchLog.objects.create(
#         employee=employee, date=today, punch_type=next_type, timestamp=now
#     )

#     record = recalculate_attendance(employee, today)
#     return next_type, record

def toggle_punch(employee, at=None, source='web', latitude=None, longitude=None, location_name=''):
    now = at or timezone.localtime()
    today = now.date()

    if employee.date_joined and today < employee.date_joined:
        raise PunchError("Punch not allowed before your date of joining.")
    if employee.status in ('terminated', 'inactive'):
        raise PunchError("Your account is inactive. Contact HR.")

    punches = get_day_punches(employee, today)
    next_type = 'in' if (not punches or punches[-1].punch_type == 'out') else 'out'

    PunchLog.objects.create(
        employee=employee, date=today, punch_type=next_type, timestamp=now,
        source=source,
        latitude=latitude, longitude=longitude, location_name=location_name or '',
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

    # ── Status decision ────────────────────────────────────────────────
    # Rule (business requirement):
    #   1) Full working hours completed  -> full day's salary (Present/Late)
    #   2) Hours incomplete BUT an approved leave covers this day
    #      -> salary follows the leave rules (Short Leave = partial
    #         deduction, any other leave = Half Day / partial-paid)
    #   3) Hours incomplete AND no leave applied for this day
    #      -> 'PA' (full day's salary deducted, same as Absent)
    # While the employee is still punched in / the day hasn't finished yet,
    # we keep the old provisional Present/Late status — the Hours-Complete
    # check only finalises once the day is actually over.
    if first_in:
        shift = employee.shift
        is_late = False
        if shift:
            grace = timedelta(minutes=shift.grace_minutes)
            shift_start_dt = timezone.localtime(first_in).replace(
                hour=shift.start_time.hour, minute=shift.start_time.minute,
                second=0, microsecond=0
            )
            is_late = timezone.localtime(first_in) > shift_start_dt + grace

        day_finished = bool(last_out) or for_date < timezone.localdate()

        if not day_finished:
            # Day still in progress — provisional status only.
            record.status = 'late' if is_late else 'present'
        else:
            standard_hours = float(employee.effective_working_hours or 8)
            hours_complete = (
                record.working_hours is not None
                and float(record.working_hours) >= standard_hours
            )

            if hours_complete:
                record.status = 'late' if is_late else 'present'
            else:
                from leaves.models import LeaveRequest
                leave_today = LeaveRequest.objects.filter(
                    employee=employee, status='approved',
                    start_date__lte=for_date, end_date__gte=for_date,
                ).select_related('leave_type').first()

                if leave_today:
                    record.status = (
                        'short_leave' if getattr(leave_today.leave_type, 'is_short_leave', False)
                        else 'half_day'
                    )
                else:
                    record.status = 'PA'

    record.save()
    return record


# ── Auto-Absent (missing punch => Absent) ───────────────────────────────────
def auto_mark_absent(employee, for_date):
    """
    Condition check: agar `for_date` ke liye employee ne bilkul punch nahi
    kiya (na In, na Out) aur din khatam ho chuka hai, to AttendanceRecord
    'absent' save kar do — taaki calendar, payroll aur reports sab jagah
    yehi real record dikhe, sirf UI par computed na ho.

    Ye function har case me safe hai (idempotent) — dubara chalane par bhi
    kuch galat overwrite nahi karta. Skip karta hai jab:
      - for_date aaj ya future ka din hai       (din abhi khatam nahi hua, punch ho sakta hai)
      - for_date employee ki joining se pehle ka hai
      - for_date weekend hai (Sat/Sun)
      - for_date par company Holiday hai
      - is date ka AttendanceRecord pehle se maujood hai (present/late/absent/
        wfh/half_day — jo bhi ho, usse touch nahi karte, sirf missing case fill karte hain)
      - is date ke PunchLog maujood hain lekin record kisi wajah se ban nahi
        paya (edge case) — us case me hard-code 'absent' karne ke bajaye
        asli punch logs se recompute karte hain
      - is date par employee ki Leave approved hai (leave apna alag flow
        se track hoti hai, use 'Absent' se overwrite nahi karna)

    Returns the AttendanceRecord if one was created/recomputed, else None.
    """
    today = timezone.localdate()

    if for_date >= today:
        return None  # day abhi chal raha hai / future hai, punch ka mauka hai

    if employee.date_joined and for_date < employee.date_joined:
        return None

    if for_date.weekday() >= 5:  # Saturday=5, Sunday=6 -> weekly off
        return None

    if Holiday.objects.filter(date=for_date).exists():
        return None

    if AttendanceRecord.objects.filter(employee=employee, date=for_date).exists():
        return None  # already has a record (kisi bhi status ka) -> touch mat karo

    if PunchLog.objects.filter(employee=employee, date=for_date).exists():
        # Punches maujood hain par record miss ho gaya tha -> asli logic se banao
        return recalculate_attendance(employee, for_date)

    # Approved leave wale din ko 'Absent' se overwrite mat karo
    from leaves.models import LeaveRequest
    on_approved_leave = LeaveRequest.objects.filter(
        employee=employee, status='approved',
        start_date__lte=for_date, end_date__gte=for_date,
    ).exists()
    if on_approved_leave:
        return None

    return AttendanceRecord.objects.create(
        employee=employee, date=for_date, status='absent',
        notes='Auto-marked Absent: no punch-in/out recorded for this day.',
    )


def backfill_absentees(start_date, end_date=None, employees=None):
    """
    Bulk helper: `auto_mark_absent()` chalata hai har employee x har date
    ke liye [start_date, end_date] range me. Iska use dono jagah hota hai:
      1) Employee portal / Admin calendar jab load ho -> us screen ke
         visible date-range ke liye "self-heal" (missing Absent bhar do).
      2) Daily cron / management command (`mark_absentees`) se poore system
         ke liye ek baar me chalane ke liye.

    Returns the count of AttendanceRecord rows created/recomputed.
    """
    end_date = end_date or start_date
    if employees is None:
        from employees.models import Employee
        employees = Employee.objects.filter(status='active')

    count = 0
    d = start_date
    while d <= end_date:
        for emp in employees:
            rec = auto_mark_absent(emp, d)
            if rec is not None:
                count += 1
        d += timedelta(days=1)
    return count


def sync_leave_balances_for_employee(employee, year=None):
    """
    NOTE: This function was being called from portal_views.py, leaves/views.py
    (apply_leave) and the accrue_leaves management command, but it did not
    exist anywhere in leaves/services.py -- that was the actual bug. Below is
    a reconstruction based on what the LeaveBalance/LeaveType models support.
    Please review the EL accrual amount/logic against what you actually want;
    there was no prior implementation to recover it from.

    For the given employee/year:
      1. Ensure a LeaveBalance row exists for every LeaveType, seeded with
         that type's `days_allowed`.
      2. For the leave type coded 'EL' (Earned Leave), accrue proportionally
         once per completed month, tracked via `last_accrual_date`, instead
         of granting the full year's days_allowed up front.

    Safe to call repeatedly (idempotent) -- it will not accrue twice for the
    same month, and won't touch balances that already exist beyond what's
    needed for accrual.
    """
    today = timezone.localdate()
    year = year or today.year

    for leave_type in LeaveType.objects.all():
        balance, created = LeaveBalance.objects.get_or_create(
            employee=employee,
            leave_type=leave_type,
            year=year,
            defaults={'total_days': leave_type.days_allowed},
        )

        if leave_type.code != 'EL':
            continue

        # Monthly accrual for Earned Leave.
        monthly_accrual = (
            Decimal(leave_type.days_allowed) / Decimal(12)
        ).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

        if balance.last_accrual_date is None:
            # First time we're syncing this employee/year: start counting
            # from the 1st of the year (or hire year), no back-dated accrual
            # beyond the current month.
            from datetime import date as _date
            cursor = _date(year, 1, 1)
        else:
            cursor = balance.last_accrual_date

        months_to_accrue = 0
        # Walk forward one month at a time until we reach the current month,
        # counting how many *new* months have completed since last accrual.
        while True:
            if cursor.month == 12:
                next_month = cursor.replace(year=cursor.year + 1, month=1)
            else:
                next_month = cursor.replace(month=cursor.month + 1)
            if next_month > today or next_month.year > year:
                break
            months_to_accrue += 1
            cursor = next_month

        if months_to_accrue > 0:
            balance.total_days = (
                Decimal(balance.total_days) + monthly_accrual * months_to_accrue
            )
            balance.last_accrual_date = cursor
            balance.save(update_fields=['total_days', 'last_accrual_date'])

def apply_leave_status_change(leave, previous_status):
    """
    Called by leaves/signals.py's post_save receiver on every LeaveRequest
    save, to keep LeaveBalance.used_days / pending_days consistent with the
    request's current status.
    """
    if previous_status == leave.status:
        return

    balance, _ = LeaveBalance.objects.get_or_create(
        employee=leave.employee,
        leave_type=leave.leave_type,
        year=leave.start_date.year,
        defaults={'total_days': leave.leave_type.days_allowed},
    )

    days = Decimal(leave.days)

    if previous_status == 'pending':
        balance.pending_days = max(Decimal('0'), balance.pending_days - days)
    elif previous_status == 'approved':
        balance.used_days = max(Decimal('0'), balance.used_days - days)

    if leave.status == 'pending':
        balance.pending_days += days
    elif leave.status == 'approved':
        balance.used_days += days

    balance.save(update_fields=['pending_days', 'used_days'])