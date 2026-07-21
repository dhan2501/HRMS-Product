from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
import calendar
from employees.models import Employee
from .models import AttendanceRecord, Holiday,WorkFromHomeRequest
# from .models import AttendanceRecord, Holiday, WorkFromHomeRequest


# ── Daily Attendance ──────────────────────────────────────────────────────────
@login_required
def daily_attendance(request):
    selected_date = request.GET.get('date', str(date.today()))
    try:
        selected_date = date.fromisoformat(selected_date)
    except ValueError:
        selected_date = date.today()

    employees   = Employee.objects.filter(status='active').select_related('department', 'designation')
    records     = AttendanceRecord.objects.filter(date=selected_date).select_related('employee')
    record_map  = {r.employee_id: r for r in records}

    attendance_data = []
    for emp in employees:
        attendance_data.append({
            'employee': emp,
            'record':   record_map.get(emp.id),
        })

    # Summary counts
    present  = records.filter(status__in=['present', 'late', 'work_from_home']).count()
    absent   = records.filter(status='absent').count()
    on_leave = records.filter(status='half_day').count()
    total    = employees.count()
    not_marked = total - records.count()

    return render(request, 'attendance/daily.html', {
        'attendance_data': attendance_data,
        'selected_date':   selected_date,
        'present':         present,
        'absent':          absent,
        'on_leave':        on_leave,
        'not_marked':      not_marked,
        'total':           total,
        'prev_date':       selected_date - timedelta(days=1),
        'next_date':       selected_date + timedelta(days=1),
        'today':           date.today(),
    })


# ── Mark / Update Attendance ──────────────────────────────────────────────────
@login_required
def mark_attendance(request):
    if request.method == 'POST':
        emp_id      = request.POST.get('employee_id')
        att_date    = request.POST.get('date')
        status      = request.POST.get('status')
        check_in    = request.POST.get('check_in') or None
        check_out   = request.POST.get('check_out') or None
        notes       = request.POST.get('notes', '')

        employee = get_object_or_404(Employee, pk=emp_id)
        record, created = AttendanceRecord.objects.update_or_create(
            employee=employee,
            date=att_date,
            defaults={
                'status':    status,
                'check_in':  check_in,
                'check_out': check_out,
                'notes':     notes,
            }
        )
        action = 'Marked' if created else 'Updated'
        messages.success(request, f'{action} attendance for {employee.full_name}')
        return redirect(f'/attendance/?date={att_date}')

    return redirect('daily_attendance')


# ── Bulk Mark Attendance ──────────────────────────────────────────────────────
@login_required
def bulk_attendance(request):
    if request.method == 'POST':
        att_date   = request.POST.get('date')
        emp_ids    = request.POST.getlist('employee_ids')
        status     = request.POST.get('bulk_status', 'present')

        count = 0
        for emp_id in emp_ids:
            employee = get_object_or_404(Employee, pk=emp_id)
            AttendanceRecord.objects.update_or_create(
                employee=employee,
                date=att_date,
                defaults={'status': status}
            )
            count += 1

        messages.success(request, f'{count} employees marked as {status}.')
        return redirect(f'/attendance/?date={att_date}')

    return redirect('daily_attendance')


# ── Monthly Attendance ────────────────────────────────────────────────────────
@login_required
def monthly_attendance(request):
    today     = date.today()
    month     = int(request.GET.get('month', today.month))
    year      = int(request.GET.get('year', today.year))
    dept_id   = request.GET.get('department')

    employees = Employee.objects.filter(status='active').select_related('department')
    if dept_id:
        employees = employees.filter(department_id=dept_id)

    _, days_in_month = calendar.monthrange(year, month)
    all_days = [date(year, month, d) for d in range(1, days_in_month + 1)]

    records = AttendanceRecord.objects.filter(
        date__month=month, date__year=year
    ).select_related('employee')

    # Build lookup: {emp_id: {date: record}}
    record_map = {}
    for r in records:
        record_map.setdefault(r.employee_id, {})[r.date] = r

    monthly_data = []
    for emp in employees:
        emp_records = record_map.get(emp.id, {})
        days_data   = []
        present = absent = late = wfh = half = 0
        for d in all_days:
            rec = emp_records.get(d)
            if rec:
                days_data.append({'date': d, 'status': rec.status, 'record': rec})
                if rec.status == 'present':    present += 1
                elif rec.status == 'absent':   absent  += 1
                elif rec.status == 'late':     late    += 1
                elif rec.status == 'work_from_home': wfh += 1
                elif rec.status == 'half_day': half    += 1
            else:
                days_data.append({'date': d, 'status': None, 'record': None})

        monthly_data.append({
            'employee': emp,
            'days':     days_data,
            'present':  present,
            'absent':   absent,
            'late':     late,
            'wfh':      wfh,
            'half':     half,
        })

    # Month navigation
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    from employees.models import Department
    departments = Department.objects.all()

    return render(request, 'attendance/monthly.html', {
        'monthly_data': monthly_data,
        'all_days':     all_days,
        'month':        month,
        'year':         year,
        'month_name':   calendar.month_name[month],
        'prev_month':   prev_month,
        'prev_year':    prev_year,
        'next_month':   next_month,
        'next_year':    next_year,
        'departments':  departments,
        'selected_dept': dept_id,
    })


# ── Attendance Reports ────────────────────────────────────────────────────────
@login_required
def attendance_reports(request):
    today  = date.today()
    month  = int(request.GET.get('month', today.month))
    year   = int(request.GET.get('year', today.year))

    records = AttendanceRecord.objects.filter(
        date__month=month, date__year=year
    )
    total_present = records.filter(status__in=['present', 'late', 'work_from_home']).count()
    total_absent  = records.filter(status='absent').count()
    total_late    = records.filter(status='late').count()
    total_wfh     = records.filter(status='work_from_home').count()

    return render(request, 'attendance/reports.html', {
        'total_present': total_present,
        'total_absent':  total_absent,
        'total_late':    total_late,
        'total_wfh':     total_wfh,
        'month':         month,
        'year':          year,
        'month_name':    calendar.month_name[month],
    })





# ── WFH Requests (Admin) ──────────────────────────────────────────────────────
@login_required
def wfh_requests(request):
    status_filter = request.GET.get('status', '')
    requests_list = WorkFromHomeRequest.objects.select_related(
        'employee', 'employee__department', 'approved_by'
    ).all()

    if status_filter:
        requests_list = requests_list.filter(status=status_filter)

    pending  = WorkFromHomeRequest.objects.filter(status='pending').count()
    approved = WorkFromHomeRequest.objects.filter(status='approved').count()
    rejected = WorkFromHomeRequest.objects.filter(status='rejected').count()

    return render(request, 'attendance/wfh_requests.html', {
        'requests_list':  requests_list,
        'pending':        pending,
        'approved':       approved,
        'rejected':       rejected,
        'status_filter':  status_filter,
    })


@login_required
def approve_wfh(request, pk):
    wfh = get_object_or_404(WorkFromHomeRequest, pk=pk)
    if request.method == 'POST':
        wfh.status      = 'approved'
        wfh.approved_at = timezone.now()
        wfh.save()

        # Auto mark attendance as WFH
        from employees.models import Employee
        AttendanceRecord.objects.update_or_create(
            employee=wfh.employee,
            date=wfh.date,
            defaults={'status': 'work_from_home', 'notes': 'WFH approved'}
        )
        messages.success(request, f'WFH approved for {wfh.employee.full_name} on {wfh.date}')
    return redirect('wfh_requests')


@login_required
def reject_wfh(request, pk):
    wfh = get_object_or_404(WorkFromHomeRequest, pk=pk)
    if request.method == 'POST':
        wfh.status           = 'rejected'
        wfh.rejection_reason = request.POST.get('reason', '')
        wfh.save()
        messages.success(request, f'WFH rejected for {wfh.employee.full_name}')
    return redirect('wfh_requests')