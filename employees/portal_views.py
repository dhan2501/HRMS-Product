# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.utils import timezone
# from datetime import date, timedelta
# import calendar
# from .models import Employee
# # from attendance.models import AttendanceRecord
# from leaves.models import LeaveRequest, LeaveType, LeaveBalance
# from payroll.models import Payslip, SalaryStructure
# from attendance.models import AttendanceRecord, WorkFromHomeRequest
# from functools import wraps


# def employee_required(view_func):
#     """Custom decorator: sirf employees access kar sakein."""
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return redirect('employee_login')
#         # Super admin/staff ko dashboard pe bhejo
#         if request.user.is_superuser or request.user.is_staff:
#             return redirect('dashboard')
#         # Employee profile check
#         try:
#             from employees.models import Employee
#             emp = Employee.objects.get(user=request.user)
#             if emp.status in ['terminated', 'inactive']:
#                 from django.contrib.auth import logout
#                 logout(request)
#                 messages.error(request, 'Your account is inactive. Contact HR.')
#                 return redirect('employee_login')
#         except Employee.DoesNotExist:
#             return redirect('employee_login')
#         return view_func(request, *args, **kwargs)
#     return wrapper


# def get_employee(request):
#     try:
#         return Employee.objects.select_related(
#             'department', 'designation'
#         ).get(user=request.user)
#     except:
#         return None

# # def get_employee(request):
# #     """Get employee linked to logged-in user."""
# #     try:
# #         return Employee.objects.select_related(
# #             'department', 'designation'
# #         ).get(user=request.user)
# #     except Employee.DoesNotExist:
# #         return None


# # ── Portal Dashboard ──────────────────────────────────────────────────────────
# @login_required
# def portal_dashboard(request):
#     employee = get_employee(request)
#     if not employee:
#         messages.error(request, 'No employee profile linked to your account. Contact HR.')
#         return redirect('dashboard')

#     today   = date.today()
#     month   = today.month
#     year    = today.year

#     # Today attendance
#     today_att = AttendanceRecord.objects.filter(
#         employee=employee, date=today
#     ).first()

#     # This month attendance summary
#     month_records = AttendanceRecord.objects.filter(
#         employee=employee, date__month=month, date__year=year
#     )
#     present_days = month_records.filter(status__in=['present', 'late', 'work_from_home']).count()
#     absent_days  = month_records.filter(status='absent').count()
#     late_days    = month_records.filter(status='late').count()

#     # Leave balance
#     leave_balances = LeaveBalance.objects.filter(
#         employee=employee, year=year
#     ).select_related('leave_type')

#     # Recent leave requests
#     recent_leaves = LeaveRequest.objects.filter(
#         employee=employee
#     ).order_by('-created_at')[:5]

#     # Latest payslip
#     latest_payslip = Payslip.objects.filter(
#         employee=employee
#     ).order_by('-year', '-month').first()

#     # Salary structure
#     try:
#         salary = SalaryStructure.objects.get(employee=employee)
#     except SalaryStructure.DoesNotExist:
#         salary = None

#     # Attendance this week
#     week_start = today - timedelta(days=today.weekday())
#     week_records = AttendanceRecord.objects.filter(
#         employee=employee,
#         date__gte=week_start,
#         date__lte=today
#     ).order_by('date')

#     return render(request, 'portal/dashboard.html', {
#         'employee':       employee,
#         'today':          today,
#         'today_att':      today_att,
#         'present_days':   present_days,
#         'absent_days':    absent_days,
#         'late_days':      late_days,
#         'leave_balances': leave_balances,
#         'recent_leaves':  recent_leaves,
#         'latest_payslip': latest_payslip,
#         'salary':         salary,
#         'week_records':   week_records,
#         'month_name':     calendar.month_name[month],
#     })


# # ── Portal Attendance ─────────────────────────────────────────────────────────
# @login_required
# def portal_attendance(request):
#     employee = get_employee(request)
#     if not employee:
#         return redirect('dashboard')

#     today = date.today()
#     month = int(request.GET.get('month', today.month))
#     year  = int(request.GET.get('year', today.year))

#     _, days_in_month = calendar.monthrange(year, month)
#     all_days = [date(year, month, d) for d in range(1, days_in_month + 1)]

#     records = AttendanceRecord.objects.filter(
#         employee=employee, date__month=month, date__year=year
#     )
#     record_map = {r.date: r for r in records}

#     calendar_data = []
#     for d in all_days:
#         rec = record_map.get(d)
#         calendar_data.append({
#             'date':    d,
#             'record':  rec,
#             'status':  rec.status if rec else None,
#             'is_today': d == today,
#             'is_weekend': d.weekday() >= 5,
#         })

#     present  = records.filter(status__in=['present', 'late', 'work_from_home']).count()
#     absent   = records.filter(status='absent').count()
#     late     = records.filter(status='late').count()
#     wfh      = records.filter(status='work_from_home').count()
#     half_day = records.filter(status='half_day').count()

#     if month == 1:
#         prev_month, prev_year = 12, year - 1
#     else:
#         prev_month, prev_year = month - 1, year
#     if month == 12:
#         next_month, next_year = 1, year + 1
#     else:
#         next_month, next_year = month + 1, year

#     return render(request, 'portal/attendance.html', {
#         'employee':      employee,
#         'calendar_data': calendar_data,
#         'month':         month,
#         'year':          year,
#         'month_name':    calendar.month_name[month],
#         'prev_month':    prev_month,
#         'prev_year':     prev_year,
#         'next_month':    next_month,
#         'next_year':     next_year,
#         'present':       present,
#         'absent':        absent,
#         'late':          late,
#         'wfh':           wfh,
#         'half_day':      half_day,
#         'today':         today,
#     })


# # ── Portal Apply Leave ────────────────────────────────────────────────────────
# @login_required
# def portal_apply_leave(request):
#     employee    = get_employee(request)
#     if not employee:
#         return redirect('dashboard')

#     leave_types = LeaveType.objects.all()
#     today       = date.today()
#     year        = today.year

#     leave_balances = LeaveBalance.objects.filter(
#         employee=employee, year=year
#     ).select_related('leave_type')

#     my_leaves = LeaveRequest.objects.filter(
#         employee=employee
#     ).order_by('-created_at')[:10]

#     if request.method == 'POST':
#         lt_id      = request.POST.get('leave_type')
#         start_date = request.POST.get('start_date')
#         end_date   = request.POST.get('end_date')
#         reason     = request.POST.get('reason', '').strip()

#         if not all([lt_id, start_date, end_date, reason]):
#             messages.error(request, 'All fields are required.')
#         else:
#             from datetime import datetime
#             s = datetime.strptime(start_date, '%Y-%m-%d').date()
#             e = datetime.strptime(end_date, '%Y-%m-%d').date()

#             if e < s:
#                 messages.error(request, 'End date cannot be before start date.')
#             elif s < today:
#                 messages.error(request, 'Cannot apply leave for past dates.')
#             else:
#                 days       = (e - s).days + 1
#                 leave_type = get_object_or_404(LeaveType, pk=lt_id)

#                 LeaveRequest.objects.create(
#                     employee=employee,
#                     leave_type=leave_type,
#                     start_date=s,
#                     end_date=e,
#                     days=days,
#                     reason=reason,
#                     status='pending',
#                 )
#                 messages.success(request, f'Leave request submitted for {days} day(s)! HR will review it.')
#                 return redirect('portal_apply_leave')

#     return render(request, 'portal/apply_leave.html', {
#         'employee':      employee,
#         'leave_types':   leave_types,
#         'leave_balances': leave_balances,
#         'my_leaves':     my_leaves,
#         'today':         today,
#     })


# # ── Portal Cancel Leave ───────────────────────────────────────────────────────
# @login_required
# def portal_cancel_leave(request, pk):
#     employee = get_employee(request)
#     leave    = get_object_or_404(LeaveRequest, pk=pk, employee=employee)
#     if request.method == 'POST' and leave.status == 'pending':
#         leave.status = 'cancelled'
#         leave.save()
#         messages.success(request, 'Leave request cancelled.')
#     return redirect('portal_apply_leave')


# # ── Portal Payslips ───────────────────────────────────────────────────────────
# @login_required
# def portal_payslips(request):
#     employee = get_employee(request)
#     if not employee:
#         return redirect('dashboard')

#     payslips = Payslip.objects.filter(
#         employee=employee
#     ).order_by('-year', '-month')

#     try:
#         salary = SalaryStructure.objects.get(employee=employee)
#     except SalaryStructure.DoesNotExist:
#         salary = None

#     return render(request, 'portal/payslips.html', {
#         'employee': employee,
#         'payslips': payslips,
#         'salary':   salary,
#     })


# # ── Portal Payslip Detail ─────────────────────────────────────────────────────
# @login_required
# def portal_payslip_detail(request, pk):
#     employee = get_employee(request)
#     slip     = get_object_or_404(Payslip, pk=pk, employee=employee)
#     return render(request, 'portal/payslip_detail.html', {
#         'employee': employee,
#         'slip':     slip,
#     })


# # ── Portal Profile ────────────────────────────────────────────────────────────
# @login_required
# def portal_profile(request):
#     employee = get_employee(request)
#     if not employee:
#         return redirect('dashboard')
#     return render(request, 'portal/profile.html', {'employee': employee})





# # ── Portal WFH ────────────────────────────────────────────────────────────────
# @login_required
# def portal_wfh(request):
#     employee = get_employee(request)
#     if not employee:
#         return redirect('dashboard')

#     today    = date.today()
#     my_wfh   = WorkFromHomeRequest.objects.filter(
#         employee=employee
#     ).order_by('-created_at')

#     pending  = my_wfh.filter(status='pending').count()
#     approved = my_wfh.filter(status='approved').count()

#     if request.method == 'POST':
#         wfh_date = request.POST.get('date')
#         reason   = request.POST.get('reason', '').strip()

#         if not wfh_date or not reason:
#             messages.error(request, 'Date and reason are required.')
#         else:
#             from datetime import datetime
#             req_date = datetime.strptime(wfh_date, '%Y-%m-%d').date()

#             if req_date < today:
#                 messages.error(request, 'Cannot apply WFH for past dates.')
#             elif WorkFromHomeRequest.objects.filter(employee=employee, date=req_date).exists():
#                 messages.error(request, f'WFH already applied for {req_date}.')
#             else:
#                 WorkFromHomeRequest.objects.create(
#                     employee=employee,
#                     date=req_date,
#                     reason=reason,
#                     status='pending',
#                 )
#                 messages.success(request, f'WFH request submitted for {req_date}. Waiting for approval.')
#                 return redirect('portal_wfh')

#     return render(request, 'portal/wfh.html', {
#         'employee': employee,
#         'my_wfh':   my_wfh,
#         'today':    today,
#         'pending':  pending,
#         'approved': approved,
#     })


# @login_required
# def portal_cancel_wfh(request, pk):
#     employee = get_employee(request)
#     wfh      = get_object_or_404(WorkFromHomeRequest, pk=pk, employee=employee)
#     if request.method == 'POST' and wfh.status == 'pending':
#         wfh.status = 'cancelled'
#         wfh.save()
#         messages.success(request, 'WFH request cancelled.')
#     return redirect('portal_wfh')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from datetime import date, timedelta
import calendar
from functools import wraps
from employees.models import Employee
from attendance.models import AttendanceRecord, WorkFromHomeRequest
from leaves.models import LeaveRequest, LeaveType, LeaveBalance
from payroll.models import Payslip, SalaryStructure


# ── Decorator ─────────────────────────────────────────────────────────────────
def employee_required(view_func):
    """Sirf active employees access kar sakein. Admin/staff ko dashboard pe bhejo."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('employee_login')

        # Admin/superuser ko admin dashboard pe bhejo
        if request.user.is_superuser or request.user.is_staff:
            return redirect('dashboard')

        # Employee profile check
        try:
            emp = Employee.objects.get(user=request.user)
            if emp.status in ['terminated', 'inactive']:
                logout(request)
                messages.error(request, 'Your account is inactive. Contact HR.')
                return redirect('employee_login')
        except Employee.DoesNotExist:
            logout(request)
            messages.error(request, 'No employee profile found. Contact HR.')
            return redirect('employee_login')

        return view_func(request, *args, **kwargs)
    return wrapper


# ── Helper ────────────────────────────────────────────────────────────────────
def get_employee(request):
    """Logged-in user ka employee object return karo."""
    try:
        return Employee.objects.select_related(
            'department', 'designation'
        ).get(user=request.user)
    except Employee.DoesNotExist:
        return None


# ── Portal Dashboard ──────────────────────────────────────────────────────────
@employee_required
def portal_dashboard(request):
    employee = get_employee(request)
    today    = date.today()
    month    = today.month
    year     = today.year

    # Sirf is employee ki aaj ki attendance
    today_att = AttendanceRecord.objects.filter(
        employee=employee,
        date=today
    ).first()

    # Is mahine ki attendance summary
    month_records = AttendanceRecord.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year
    )
    present_days = month_records.filter(
        status__in=['present', 'late', 'work_from_home']
    ).count()
    absent_days  = month_records.filter(status='absent').count()
    late_days    = month_records.filter(status='late').count()

    # Sirf is employee ki leave balance
    leave_balances = LeaveBalance.objects.filter(
        employee=employee,
        year=year
    ).select_related('leave_type')

    # Sirf is employee ke recent leave requests
    recent_leaves = LeaveRequest.objects.filter(
        employee=employee
    ).order_by('-created_at')[:5]

    # Sirf is employee ki latest payslip
    latest_payslip = Payslip.objects.filter(
        employee=employee
    ).order_by('-year', '-month').first()

    # Sirf is employee ki salary structure
    try:
        salary = SalaryStructure.objects.get(employee=employee)
    except SalaryStructure.DoesNotExist:
        salary = None

# Is hafte ki attendance
    week_start   = today - timedelta(days=today.weekday())
    week_records = AttendanceRecord.objects.filter(
        employee=employee,
        date__gte=week_start,
        date__lte=today
    ).order_by('date')

    # Upcoming events & holidays (next 3)
    from events.models import Event
    upcoming_events = Event.objects.filter(
        is_active=True, date__gte=today
    ).order_by('date')[:3]

    return render(request, 'portal/dashboard.html', {
        'employee':        employee,
        'today':           today,
        'today_att':       today_att,
        'present_days':    present_days,
        'absent_days':     absent_days,
        'late_days':       late_days,
        'leave_balances':  leave_balances,
        'recent_leaves':   recent_leaves,
        'latest_payslip':  latest_payslip,
        'salary':          salary,
        'week_records':    week_records,
        'month_name':      calendar.month_name[month],
        'upcoming_events': upcoming_events,
    })


# ── Portal Attendance ─────────────────────────────────────────────────────────
@employee_required
def portal_attendance(request):
    employee = get_employee(request)
    today    = date.today()
    month    = int(request.GET.get('month', today.month))
    year     = int(request.GET.get('year', today.year))

    _, days_in_month = calendar.monthrange(year, month)
    all_days = [date(year, month, d) for d in range(1, days_in_month + 1)]

    # Sirf is employee ki attendance
    records    = AttendanceRecord.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year
    )
    record_map = {r.date: r for r in records}

    calendar_data = []
    for d in all_days:
        rec = record_map.get(d)
        calendar_data.append({
            'date':       d,
            'record':     rec,
            'status':     rec.status if rec else None,
            'is_today':   d == today,
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
@employee_required
def portal_apply_leave(request):
    employee    = get_employee(request)
    leave_types = LeaveType.objects.all()
    today       = date.today()
    year        = today.year

    # Sirf is employee ki leave balance
    leave_balances = LeaveBalance.objects.filter(
        employee=employee,
        year=year
    ).select_related('leave_type')

    # Sirf is employee ke leave requests
    my_leaves = LeaveRequest.objects.filter(
        employee=employee
    ).order_by('-created_at')[:15]

    if request.method == 'POST':
        lt_id      = request.POST.get('leave_type')
        start_date = request.POST.get('start_date')
        end_date   = request.POST.get('end_date')
        reason     = request.POST.get('reason', '').strip()

        if not all([lt_id, start_date, end_date, reason]):
            messages.error(request, 'All fields are required.')
        else:
            from datetime import datetime as dt
            s = dt.strptime(start_date, '%Y-%m-%d').date()
            e = dt.strptime(end_date, '%Y-%m-%d').date()

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
                messages.success(
                    request,
                    f'Leave request submitted for {days} day(s)! HR will review it.'
                )
                return redirect('portal_apply_leave')

    return render(request, 'portal/apply_leave.html', {
        'employee':       employee,
        'leave_types':    leave_types,
        'leave_balances': leave_balances,
        'my_leaves':      my_leaves,
        'today':          today,
    })


# ── Portal Cancel Leave ───────────────────────────────────────────────────────
@employee_required
def portal_cancel_leave(request, pk):
    employee = get_employee(request)
    # Sirf is employee ka leave cancel ho sakta hai
    leave = get_object_or_404(LeaveRequest, pk=pk, employee=employee)
    if request.method == 'POST' and leave.status == 'pending':
        leave.status = 'cancelled'
        leave.save()
        messages.success(request, 'Leave request cancelled.')
    return redirect('portal_apply_leave')


# ── Portal WFH ────────────────────────────────────────────────────────────────
@employee_required
def portal_wfh(request):
    employee = get_employee(request)
    today    = date.today()

    # Sirf is employee ke WFH requests
    my_wfh  = WorkFromHomeRequest.objects.filter(
        employee=employee
    ).order_by('-created_at')

    pending  = my_wfh.filter(status='pending').count()
    approved = my_wfh.filter(status='approved').count()

    if request.method == 'POST':
        wfh_date = request.POST.get('date')
        reason   = request.POST.get('reason', '').strip()

        if not wfh_date or not reason:
            messages.error(request, 'Date and reason are required.')
        else:
            from datetime import datetime as dt
            req_date = dt.strptime(wfh_date, '%Y-%m-%d').date()

            if req_date < today:
                messages.error(request, 'Cannot apply WFH for past dates.')
            elif WorkFromHomeRequest.objects.filter(
                employee=employee, date=req_date
            ).exists():
                messages.error(request, f'WFH already applied for {req_date}.')
            else:
                WorkFromHomeRequest.objects.create(
                    employee=employee,
                    date=req_date,
                    reason=reason,
                    status='pending',
                )
                messages.success(
                    request,
                    f'WFH request submitted for {req_date}. Waiting for approval.'
                )
                return redirect('portal_wfh')

    return render(request, 'portal/wfh.html', {
        'employee': employee,
        'my_wfh':   my_wfh,
        'today':    today,
        'pending':  pending,
        'approved': approved,
    })


# ── Portal Cancel WFH ─────────────────────────────────────────────────────────
@employee_required
def portal_cancel_wfh(request, pk):
    employee = get_employee(request)
    # Sirf is employee ka WFH cancel ho sakta hai
    wfh = get_object_or_404(WorkFromHomeRequest, pk=pk, employee=employee)
    if request.method == 'POST' and wfh.status == 'pending':
        wfh.status = 'cancelled'
        wfh.save()
        messages.success(request, 'WFH request cancelled.')
    return redirect('portal_wfh')


# ── Portal Payslips ───────────────────────────────────────────────────────────
@employee_required
def portal_payslips(request):
    employee = get_employee(request)

    # Sirf is employee ke payslips
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
@employee_required
def portal_payslip_detail(request, pk):
    employee = get_employee(request)
    # Sirf is employee ka payslip — dusre ka nahi
    slip = get_object_or_404(Payslip, pk=pk, employee=employee)
    return render(request, 'portal/payslip_detail.html', {
        'employee': employee,
        'slip':     slip,
    })


# ── Portal Profile ────────────────────────────────────────────────────────────
@employee_required
def portal_profile(request):
    employee = get_employee(request)
    return render(request, 'portal/profile.html', {'employee': employee})

# ── Portal Events & Holidays ──────────────────────────────────────────────────
@employee_required
def portal_events(request):
    from events.models import Event

    employee   = get_employee(request)
    event_type = request.GET.get('type', '')
    today      = date.today()

    events = Event.objects.filter(is_active=True)
    if event_type in ['holiday', 'event']:
        events = events.filter(event_type=event_type)

    upcoming = events.filter(date__gte=today).order_by('date')
    past     = events.filter(date__lt=today).order_by('-date')[:10]

    upcoming_holiday_count = upcoming.filter(event_type='holiday').count()
    upcoming_event_count   = upcoming.filter(event_type='event').count()

    return render(request, 'portal/events.html', {
        'employee':               employee,
        'upcoming':                upcoming,
        'past':                    past,
        'selected_type':           event_type,
        'upcoming_holiday_count':  upcoming_holiday_count,
        'upcoming_event_count':    upcoming_event_count,
        'today':                   today,
    })

# ── Portal Performance (My Performance) ─────────────────────────────────────
@employee_required
def portal_performance(request):
    """
    Lets the logged-in employee see their own performance reviews
    (read-only) — this is the 'Employee ko bhi dikhana hai' part.
    """
    employee = get_employee(request)

    reviews = employee.performance_reviews.select_related('reviewer').prefetch_related('goals')

    return render(request, 'portal/performance.html', {
        'employee': employee,
        'reviews': reviews,
    })


# ── Portal Performance — Employee Acknowledge / Comment ─────────────────────
@employee_required
def portal_performance_acknowledge(request, pk):
    """
    Employee reads a submitted review and adds their own remark, marking
    it 'acknowledged'. Employee can only touch their own reviews.
    """
    from employees.models import PerformanceReview
    employee = get_employee(request)
    review   = get_object_or_404(PerformanceReview, pk=pk, employee=employee)

    if request.method == 'POST':
        employee_comments = request.POST.get('employee_comments', '').strip()
        review.employee_comments = employee_comments
        review.status = 'acknowledged'
        review.save()
        messages.success(request, 'Thanks — your review has been acknowledged.')

    return redirect('portal_performance')

