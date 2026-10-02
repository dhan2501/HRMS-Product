# ============================================================================
# FILE: employees/dashboard_analytics.py
# ============================================================================
from datetime import date, timedelta
from calendar import month_abbr

from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth

from .models import Employee, EmployeeStatusLog
from attendance.models import AttendanceRecord, Holiday
from leaves.models import LeaveRequest
from payroll.models import Payslip, SalaryStructure


def get_late_today(today=None):
    """Aaj kitne employees 'late' status ke saath check-in hue."""
    today = today or date.today()
    return AttendanceRecord.objects.filter(date=today, status='late').count()


def get_attendance_percentage(present_count, total_employees):
    """
    Attendance % = (Present + Late + WFH + Half Day) / Total Active Employees * 100
    """
    if not total_employees:
        return 0.0
    return round((present_count / total_employees) * 100, 1)


def get_payroll_cost(today=None):
    """Current month ka payroll cost — payslip se, warna estimate se."""
    today = today or date.today()

    payslip_total = Payslip.objects.filter(
        month=today.month, year=today.year
    ).aggregate(total=Sum('net_salary'))['total']

    if payslip_total:
        return {'amount': float(payslip_total), 'source': 'payslip'}

    estimated_full = SalaryStructure.objects.filter(employee__status='active')
    total_estimated = 0
    for s in estimated_full:
        total_estimated += float(s.basic) + float(s.hra) + float(s.special_allowance)

    return {'amount': round(total_estimated, 2), 'source': 'estimated'}


def get_attrition_rate(today=None):
    """Is mahine attrition % = terminated/inactive employees / avg headcount * 100"""
    today = today or date.today()

    left_this_month = EmployeeStatusLog.objects.filter(
        new_status__in=['terminated', 'inactive'],
        changed_at__year=today.year,
        changed_at__month=today.month,
    ).values('employee_id').distinct().count()

    active_now = Employee.objects.filter(status='active').count()
    avg_headcount = active_now + left_this_month

    rate = 0.0 if avg_headcount == 0 else round((left_this_month / avg_headcount) * 100, 2)

    return {'left_this_month': left_this_month, 'rate_percent': rate}


def get_overtime_summary(today=None):
    """Current month ka overtime — Payslip se sum karke."""
    today = today or date.today()

    agg = Payslip.objects.filter(
        month=today.month, year=today.year
    ).aggregate(
        total_hours=Sum('overtime_hours'),
        total_amount=Sum('overtime_amount'),
    )

    return {
        'hours': float(agg['total_hours'] or 0),
        'amount': float(agg['total_amount'] or 0),
    }


def get_leave_trends(months_back=6, today=None):
    """
    Pichle N mahino mein har mahine ki approved leave requests aur days.
    Return: [{'label': 'Mar', 'year': 2026, 'count': 12, 'days': 18.5}, ...]
    """
    today = today or date.today()

    year = today.year
    month = today.month - (months_back - 1)
    while month <= 0:
        month += 12
        year -= 1
    start_date = date(year, month, 1)

    qs = (
        LeaveRequest.objects
        .filter(status='approved', start_date__gte=start_date)
        .annotate(month_bucket=TruncMonth('start_date'))
        .values('month_bucket')
        .annotate(count=Count('id'), days=Sum('days'))
        .order_by('month_bucket')
    )

    data_by_month = {
        (row['month_bucket'].year, row['month_bucket'].month): row
        for row in qs
    }

    trends = []
    y, m = year, month
    for _ in range(months_back):
        row = data_by_month.get((y, m))
        trends.append({
            'label': f"{month_abbr[m]}",
            'year': y,
            'count': row['count'] if row else 0,
            'days': float(row['days']) if row and row['days'] else 0.0,
        })
        m += 1
        if m > 12:
            m = 1
            y += 1

    return trends


def get_attendance_overview(range_key='week', today=None):
    """
    Din-wise attendance breakdown (Present / Late / On Leave / Absent) —
    dashboard ke "Attendance Overview" chart ke liye.

    range_key:
        'week'  -> pichhle 7 working days
        'month' -> pichhle 22 working days (~1 mahina)

    Weekends aur company holidays skip kar diye jaate hain (unmein
    attendance track hi nahi hoti), isliye sirf working days count hote hain.

    Return: purane se naye din ke order mein list of dicts —
        [{'day': 'Mon', 'date': '2026-08-31',
          'present': 42, 'late': 3, 'on_leave': 2, 'absent': 1}, ...]
    """
    today = today or date.today()
    target_days = 22 if range_key == 'month' else 7
    label_fmt = '%d %b' if range_key == 'month' else '%a'

    total_active = Employee.objects.filter(status='active').count()

    holiday_dates = set(
        Holiday.objects.filter(date__lte=today)
        .order_by('-date')[: target_days * 3]
        .values_list('date', flat=True)
    )

    working_days = []
    cursor = today
    while len(working_days) < target_days:
        if cursor.weekday() not in (5, 6) and cursor not in holiday_dates:
            working_days.append(cursor)
        cursor -= timedelta(days=1)
    working_days.reverse()

    overview = []
    for day in working_days:
        present = AttendanceRecord.objects.filter(
            date=day, status__in=['present', 'work_from_home', 'half_day']
        ).count()
        late = AttendanceRecord.objects.filter(date=day, status='late').count()
        on_leave = LeaveRequest.objects.filter(
            status='approved',
            start_date__lte=day,
            end_date__gte=day,
            employee__status='active',
        ).distinct().count()
        absent = max(total_active - present - late - on_leave, 0)

        overview.append({
            'day': day.strftime(label_fmt),
            'date': day.isoformat(),
            'present': present,
            'late': late,
            'on_leave': on_leave,
            'absent': absent,
        })

    return overview


def get_attendance_range_label(range_key='week'):
    """Attendance Overview card ke subtitle ke liye chhota sa label."""
    return 'Last 22 working days' if range_key == 'month' else 'Last 7 working days'


def get_dashboard_analytics(today=None, present_count=0, total_employees=0):
    """Convenience wrapper — dashboard() view mein ek hi call se sab naye metrics."""
    today = today or date.today()

    return {
        'late_today':        get_late_today(today),
        'attendance_pct':    get_attendance_percentage(present_count, total_employees),
        'payroll_cost':      get_payroll_cost(today),
        'attrition':         get_attrition_rate(today),
        'overtime':          get_overtime_summary(today),
        'leave_trends':      get_leave_trends(months_back=6, today=today),
    }