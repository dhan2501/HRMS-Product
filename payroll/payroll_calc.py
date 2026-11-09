"""
Attendance → Payroll automatic calculation.

Reads an employee's Attendance records for a given month/year and works
out the variable, attendance-driven parts of their payslip:

    * payable_days / present_days   – how many days they worked
    * lop_days / lop_amount         – Loss-of-Pay for unapproved absences
    * overtime_hours / overtime_amount – hours worked beyond the
      employee's standard shift, paid at the salary structure's
      overtime rate.

This keeps the "Generate Payslips" action from payroll/views.py in sync
with real attendance data instead of always paying the full fixed
salary regardless of who actually showed up.
"""
import calendar
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone


from attendance.models import AttendanceRecord

# Attendance statuses that count as a fully paid day worked.
FULL_PAID_STATUSES = {'present', 'late', 'work_from_home'}
# Attendance statuses that count as a paid non-working day (no LOP).
PAID_NON_WORKING_STATUSES = {'holiday'}
# Attendance status that counts as half a paid day (0.5 LOP for the other half).
HALF_DAY_STATUS = 'half_day'
# Attendance status that counts as a Short Leave — day is still mostly
# worked, only a partial deduction applies (see SHORT_LEAVE_LOP_FRACTION).
SHORT_LEAVE_STATUS = 'short_leave'
SHORT_LEAVE_LOP_FRACTION = Decimal('0.25')  # quarter-day deduction per short leave
# Attendance statuses that result in a FULL day's Loss-of-Pay:
#   'absent'     -> no punch at all for the day
#   'PA'         -> punched in, but working hours were incomplete AND no
#                   leave was applied for that day — full day deducted
LOP_STATUSES = {'absent', 'PA'}


def _round(value):
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_attendance_payroll(employee, salary_structure, month, year):
    """
    Returns a dict of attendance-derived payroll figures for one
    employee for the given month/year, ready to feed into a Payslip.
    """
    days_in_month = calendar.monthrange(year, month)[1]

    records = AttendanceRecord.objects.filter(
        employee=employee, date__year=year, date__month=month
    )

    full_present = records.filter(status__in=FULL_PAID_STATUSES).count()
    half_days = records.filter(status=HALF_DAY_STATUS).count()
    holidays = records.filter(status__in=PAID_NON_WORKING_STATUSES).count()
    absents = records.filter(status__in=LOP_STATUSES).count()
    short_leaves = records.filter(status=SHORT_LEAVE_STATUS).count()

    present_days = Decimal(full_present) + (Decimal(half_days) * Decimal('0.5')) + Decimal(short_leaves)
    lop_days = (
        Decimal(absents)
        + (Decimal(half_days) * Decimal('0.5'))
        + (Decimal(short_leaves) * SHORT_LEAVE_LOP_FRACTION)
    )

    # Per-day rate is the fixed gross salary spread across the calendar
    # days in the month — the standard Indian payroll convention.
    payable_days = Decimal(days_in_month)
    per_day_salary = (salary_structure.gross_salary / payable_days) if payable_days else Decimal('0')
    lop_amount = _round(per_day_salary * lop_days)

    # ── Overtime: sum of hours worked beyond the employee's standard
    # shift length, on days they actually attended. ──────────────────
    standard_hours = Decimal(str(employee.effective_working_hours or 8))
    overtime_hours = Decimal('0')
    for rec in records.filter(status__in=FULL_PAID_STATUSES, working_hours__isnull=False):
        worked = Decimal(str(rec.working_hours))
        if worked > standard_hours:
            overtime_hours += (worked - standard_hours)

    overtime_rate = getattr(salary_structure, 'overtime_rate_per_hour', Decimal('0')) or Decimal('0')
    overtime_amount = _round(overtime_hours * overtime_rate)

    return {
        'payable_days': payable_days,
        'present_days': present_days + Decimal(holidays),
        'lop_days': lop_days,
        'lop_amount': lop_amount,
        'overtime_hours': _round(overtime_hours),
        'overtime_amount': overtime_amount,
    }


def estimate_live_salary(employee, salary_structure, reference_date=None):
    """
    Month-to-date, attendance-driven ESTIMATE of this employee's take-home
    for the current month — recomputed fresh from real Attendance data
    every time it's called (e.g. on every dashboard page load), NOT a
    stored/generated Payslip.

    Only days from the 1st of the month up to `reference_date` (today, by
    default) are looked at. The remaining days in the month are assumed to
    go as fully-present (best case), since their attendance doesn't exist
    yet — so this is a live "if today were the last day counted" projection,
    not a guarantee of the final payslip amount.
    """
    today = reference_date or timezone.localdate()
    year, month = today.year, today.month
    days_in_month = calendar.monthrange(year, month)[1]

    records = AttendanceRecord.objects.filter(
        employee=employee, date__year=year, date__month=month, date__lte=today
    )

    full_present = records.filter(status__in=FULL_PAID_STATUSES).count()
    half_days = records.filter(status=HALF_DAY_STATUS).count()
    holidays = records.filter(status__in=PAID_NON_WORKING_STATUSES).count()
    absents = records.filter(status__in=LOP_STATUSES).count()
    short_leaves = records.filter(status=SHORT_LEAVE_STATUS).count()

    present_days_so_far = (
        Decimal(full_present) + Decimal(holidays)
        + (Decimal(half_days) * Decimal('0.5')) + Decimal(short_leaves)
    )
    lop_days_so_far = (
        Decimal(absents)
        + (Decimal(half_days) * Decimal('0.5'))
        + (Decimal(short_leaves) * SHORT_LEAVE_LOP_FRACTION)
    )

    per_day_salary = (
        salary_structure.gross_salary / Decimal(days_in_month)
    ) if days_in_month else Decimal('0')
    lop_amount_so_far = _round(per_day_salary * lop_days_so_far)

    projected_net = (
        salary_structure.gross_salary
        + salary_structure.standard_bonus
        + salary_structure.standard_incentive
        - salary_structure.pf_deduction
        - salary_structure.esi_deduction
        - salary_structure.professional_tax
        - salary_structure.monthly_tds
        - lop_amount_so_far
    )

    days_elapsed = (today - date(year, month, 1)).days + 1

    return {
        'days_elapsed': days_elapsed,
        'days_in_month': days_in_month,
        'present_days_so_far': present_days_so_far,
        'absent_days_so_far': absents,
        'half_days_so_far': half_days,
        'short_leaves_so_far': short_leaves,
        'lop_days_so_far': lop_days_so_far,
        'lop_amount_so_far': lop_amount_so_far,
        'projected_net_salary': _round(projected_net),
    }


# ═════════════════════════════════════════════════════════════════════════
#  EARNED-TO-DATE SALARY  (daily, hours-based, grows day by day)
# ═════════════════════════════════════════════════════════════════════════
def _live_hours_today(employee, today):
    """
    Today's net working hours, computed READ-ONLY from PunchLog rows.
    Counts the running clock if the employee is still punched in, and
    subtracts break time. Returns Decimal hours.
    """
    from attendance import services as att_services

    punches = att_services.get_day_punches(employee, today)
    if not punches or punches[0].punch_type != 'in':
        return Decimal('0')

    first_in = punches[0].timestamp
    last_out = punches[-1].timestamp if punches[-1].punch_type == 'out' else None
    end_point = last_out or timezone.now()

    break_minutes, _ = att_services._compute_breaks(punches)
    gross_minutes = max(0, int((end_point - first_in).total_seconds() // 60))
    net_minutes = max(0, gross_minutes - break_minutes)
    return Decimal(net_minutes) / Decimal(60)


def _approved_unpaid_leave_dates(employee, start, end):
    """Set of dates in [start, end] covered by an approved UNPAID leave."""
    from leaves.models import LeaveRequest

    dates = set()
    qs = LeaveRequest.objects.filter(
        employee=employee, status='approved',
        start_date__lte=end, end_date__gte=start,
        leave_type__is_paid=False,
    )
    for lr in qs:
        d = max(lr.start_date, start)
        while d <= min(lr.end_date, end):
            dates.add(d)
            d += timedelta(days=1)
    return dates


def estimate_earned_salary_to_date(employee, salary_structure, reference_date=None):
    """
    Salary EARNED SO FAR this month (1st -> today). Starts near 0 on day 1
    and increases every day; today's portion grows with the hours the
    employee has actually worked today (live, including the running clock).
    """
    today = reference_date or timezone.localdate()
    year, month = today.year, today.month
    days_in_month = calendar.monthrange(year, month)[1]
    month_start = date(year, month, 1)

    # Don't count days before joining
    start = month_start
    if employee.date_joined and employee.date_joined > month_start:
        start = employee.date_joined

    gross = Decimal(salary_structure.gross_salary)
    per_day = gross / Decimal(days_in_month)
    standard_hours = Decimal(str(employee.effective_working_hours or 8))
    if standard_hours <= 0:
        standard_hours = Decimal('8')

    from attendance.models import Holiday
    records = {
        r.date: r for r in AttendanceRecord.objects.filter(
            employee=employee, date__gte=start, date__lte=today
        )
    }
    holidays = set(
        Holiday.objects.filter(date__gte=start, date__lte=today).values_list('date', flat=True)
    )
    unpaid_leave = _approved_unpaid_leave_dates(employee, start, today)

    paid_days = Decimal('0')
    overtime_hours = Decimal('0')
    d = start
    while d <= today:
        rec = records.get(d)
        is_today = (d == today)
        is_off = d.weekday() >= 5 or d in holidays

        if is_today:
            hours = _live_hours_today(employee, today)
            if hours > 0:
                paid_days += min(Decimal('1'), hours / standard_hours)
                if hours > standard_hours:
                    overtime_hours += (hours - standard_hours)
            elif is_off:
                paid_days += Decimal('1')
            # weekday + no punch yet -> 0 so far today
        elif rec is not None:
            if rec.status in FULL_PAID_STATUSES or rec.status in PAID_NON_WORKING_STATUSES:
                paid_days += Decimal('1')
                if rec.status in FULL_PAID_STATUSES and rec.working_hours:
                    w = Decimal(str(rec.working_hours))
                    if w > standard_hours:
                        overtime_hours += (w - standard_hours)
            elif rec.status == HALF_DAY_STATUS:
                paid_days += Decimal('0.5')
            elif rec.status == SHORT_LEAVE_STATUS:
                paid_days += Decimal('1') - SHORT_LEAVE_LOP_FRACTION
            # absent / PA -> 0
        elif d in unpaid_leave:
            pass
        elif is_off:
            paid_days += Decimal('1')          # weekly off / holiday, no record
        else:
            # Weekday with no record: approved paid leave -> paid.
            from leaves.models import LeaveRequest
            if LeaveRequest.objects.filter(
                employee=employee, status='approved', leave_type__is_paid=True,
                start_date__lte=d, end_date__gte=d,
            ).exists():
                paid_days += Decimal('1')
        d += timedelta(days=1)

    earned_gross = _round(per_day * paid_days)
    ot_rate = getattr(salary_structure, 'overtime_rate_per_hour', Decimal('0')) or Decimal('0')
    overtime_amount = _round(overtime_hours * ot_rate)

    ratio = (earned_gross / gross) if gross else Decimal('0')
    deductions_full = (
        salary_structure.pf_deduction + salary_structure.esi_deduction
        + salary_structure.professional_tax + salary_structure.monthly_tds
    )
    deductions_so_far = _round(Decimal(deductions_full) * ratio)
    earned_net = _round(earned_gross + overtime_amount - deductions_so_far)

    today_hours = _live_hours_today(employee, today)
    today_earned = _round(per_day * min(Decimal('1'), today_hours / standard_hours))

    return {
        'days_elapsed': (today - month_start).days + 1,
        'days_in_month': days_in_month,
        'paid_days': _round(paid_days),
        'per_day_salary': _round(per_day),
        'today_hours': _round(today_hours),
        'standard_hours': standard_hours,
        'today_earned': today_earned,
        'earned_gross': earned_gross,
        'overtime_hours': _round(overtime_hours),
        'overtime_amount': overtime_amount,
        'deductions_so_far': deductions_so_far,
        'earned_net': max(earned_net, Decimal('0')),
        'full_month_net': _round(salary_structure.net_salary),
    }