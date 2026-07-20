from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
import calendar
from .models import Employee
from attendance.models import AttendanceRecord
from leaves.models import LeaveRequest, LeaveType, LeaveBalance
from payroll.models import Payslip, SalaryStructure


def get_employee(request):
    """Get employee linked to logged-in user."""
    try:
        return Employee.objects.select_related(
            'department', 'designation'
        ).get(user=request.user)
    except Employee.DoesNotExist:
        return None


# ── Portal Dashboard ──────────────────────────────────────────────────────────
@login_required
def portal_dashboard(request):
    employee = get_employee(request)
    if not employee:
        messages.error(request, 'No employee profile linked to your account. Contact HR.')
        return redirect('dashboard')

    today   = date.today()
    month   = today.month
    year    = today.year

    # Today attendance
    today_att = AttendanceRecord.objects.filter(
        employee=employee, date=today
    ).first()

    # This month attendance summary
    month_records = AttendanceRecord.objects.filter(
        employee=employee, date__month=month, date__year=year
    )
    present_days = month_records.filter(status__in=['present', 'late', 'work_from_home']).count()
    absent_days  = month_records.filter(status='absent').count()
    late_days    = month_records.filter(status='late').count()

    # Leave balance
    leave_balances = LeaveBalance.objects.filter(
        employee=employee, year=year
    ).select_related('leave_type')

    # Recent leave requests
    recent_leaves = LeaveRequest.objects.filter(
        employee=employee
    ).order_by('-created_at')[:5]

    # Latest payslip
    latest_payslip = Payslip.objects.filter(
        employee=employee
    ).order_by('-year', '-month').first()

    # Salary structure
    try:
        salary = SalaryStructure.objects.get(employee=employee)
    except SalaryStructure.DoesNotExist:
        salary = None

    # Attendance this week
    week_start = today - timedelta(days=today.weekday())
    week_records = AttendanceRecord.objects.filter(
        employee=employee,
        date__gte=week_start,
        date__lte=today
    ).order_by('date')

    return render(request, 'portal/dashboard.html', {
        'employee':       employee,
        'today':          today,
        'today_att':      today_att,
        'present_days':   present_days,
        'absent_days':    absent_days,
        'late_days':      late_days,
        'leave_balances': leave_balances,
        'recent_leaves':  recent_leaves,
        'latest_payslip': latest_payslip,
        'salary':         salary,
        'week_records':   week_records,
        'month_name':     calendar.month_name[month],
    })


# ── Portal Attendance ─────────────────────────────────────────────────────────
@login_required
def portal_attendance(request):
    employee = get_employee(request)
    if not employee:
        return redirect('dashboard')

    today = date.today()
    month = int(request.GET.get('month', today.month))
    year  = int(request.GET.get('year', today.year))

    _, days_in_month = calendar.monthrange(year, month)
    all_days = [date(year, month, d) for d in range(1, days_in_month + 1)]

    records = AttendanceRecord.objects.filter(
        employee=employee, date__month=month, date__year=year
    )
    record_map = {r.date: r for r in records}

    calendar_data = []
    for d in all_days:
        rec = record_map.get(d)
        calendar_data.append({
            'date':    d,
            'record':  rec,
            'status':  rec.status if rec else None,
            'is_today': d == today,
            'is_weekend': d.weekday() >= 5,
        })

    present  = records.filter(status__in=['present', 'late', 'work_from_home']).count()
    absent   = records.filter(status='absent').count()
    late     = records.filter(status='late').count()
    wfh      = records.filter(status='work_from_home').count()
    half_day = records.filter(status='half_day').count()

    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    return render(request, 'portal/attendance.html', {
        'employee':      employee,
        'calendar_data': calendar_data,
        'month':         month,
        'year':          year,
        'month_name':    calendar.month_name[month],
        'prev_month':    prev_month,
        'prev_year':     prev_year,
        'next_month':    next_month,
        'next_year':     next_year,
        'present':       present,
        'absent':        absent,
        'late':          late,
        'wfh':           wfh,
        'half_day':      half_day,
        'today':         today,
    })


# ── Portal Apply Leave ────────────────────────────────────────────────────────
@login_required
def portal_apply_leave(request):
    employee    = get_employee(request)
    if not employee:
        return redirect('dashboard')

    leave_types = LeaveType.objects.all()
    today       = date.today()
    year        = today.year

    leave_balances = LeaveBalance.objects.filter(
        employee=employee, year=year
    ).select_related('leave_type')

    my_leaves = LeaveRequest.objects.filter(
        employee=employee
    ).order_by('-created_at')[:10]

    if request.method == 'POST':
        lt_id      = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date   = request.POST.get('end_date')
        reason     = request.POST.get('reason', '').strip()

        if not all([lt_id, start_date, end_date, reason]):
            messages.error(request, 'All fields are required.')
        else:
            from datetime import datetime
            s = datetime.strptime(start_date, '%Y-%m-%d').date()
            e = datetime.strptime(end_date, '%Y-%m-%d').date()

            if e < s:
                messages.error(request, 'End date cannot be before start date.')
            elif s < today:
                messages.error(request, 'Cannot apply leave for past dates.')
            else:
                days       = (e - s).days + 1
                leave_type = get_object_or_404(LeaveType, pk=lt_id)

                LeaveRequest.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    start_date=s,
                    end_date=e,
                    days=days,
                    reason=reason,
                    status='pending',
                )
                messages.success(request, f'Leave request submitted for {days} day(s)! HR will review it.')
                return redirect('portal_apply_leave')

    return render(request, 'portal/apply_leave.html', {
        'employee':      employee,
        'leave_types':   leave_types,
        'leave_balances': leave_balances,
        'my_leaves':     my_leaves,
        'today':         today,
    })


# ── Portal Cancel Leave ───────────────────────────────────────────────────────
@login_required
def portal_cancel_leave(request, pk):
    employee = get_employee(request)
    leave    = get_object_or_404(LeaveRequest, pk=pk, employee=employee)
    if request.method == 'POST' and leave.status == 'pending':
        leave.status = 'cancelled'
        leave.save()
        messages.success(request, 'Leave request cancelled.')
    return redirect('portal_apply_leave')


# ── Portal Payslips ───────────────────────────────────────────────────────────
@login_required
def portal_payslips(request):
    employee = get_employee(request)
    if not employee:
        return redirect('dashboard')

    payslips = Payslip.objects.filter(
        employee=employee
    ).order_by('-year', '-month')

    try:
        salary = SalaryStructure.objects.get(employee=employee)
    except SalaryStructure.DoesNotExist:
        salary = None

    return render(request, 'portal/payslips.html', {
        'employee': employee,
        'payslips': payslips,
        'salary':   salary,
    })


# ── Portal Payslip Detail ─────────────────────────────────────────────────────
@login_required
def portal_payslip_detail(request, pk):
    employee = get_employee(request)
    slip     = get_object_or_404(Payslip, pk=pk, employee=employee)
    return render(request, 'portal/payslip_detail.html', {
        'employee': employee,
        'slip':     slip,
    })


# ── Portal Profile ────────────────────────────────────────────────────────────
@login_required
def portal_profile(request):
    employee = get_employee(request)
    if not employee:
        return redirect('dashboard')
    return render(request, 'portal/profile.html', {'employee': employee})