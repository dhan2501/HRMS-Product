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
from datetime import date
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