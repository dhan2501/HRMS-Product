from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from datetime import date, timedelta, datetime
import calendar
from functools import wraps
from payroll.models import Payslip, SalaryStructure
from employees.models import Employee, Project
from leaves.models import LeaveRequest, LeaveType, LeaveBalance
from leaves import services as leave_services

# imports me ye add/update karo:
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from attendance.models import AttendanceRecord, WorkFromHomeRequest, PunchLog, FaceEncoding, Holiday, AttendanceDispute
from attendance import services as attendance_services
from attendance import face_utils
from django import forms


# ── Employee-only form: "My Profile" self-service edit (Portal) ───────────────
# Defined here (not in employees/views.py) so portal_profile below never
# depends on employees/views.py being on a matching version.
class EmployeeSelfProfileForm(forms.ModelForm):
    """
    Employee self-service edit — the "Profile Details" tab on the portal's
    My Profile page. Deliberately excludes department/designation/salary/
    reporting-manager/status (admin-only) and bank/Aadhaar/PAN (their own
    dedicated, more tightly-restricted form) so an employee can only ever
    touch the plain personal-details fields listed here.
    """
    class Meta:
        model = Employee
        fields = [
            'photo', 'first_name', 'last_name', 'email', 'phone',
            'date_of_birth', 'gender', 'address',
            'emergency_contact_name', 'emergency_contact_phone',
        ]
        widgets = {
            # Plain FileInput instead of Django's default ClearableFileInput —
            # skips the ugly "Currently: <path> ☐ Clear  Change:" text, since
            # the template already shows the current photo as a preview above
            # this field.
            'photo': forms.FileInput(),
        }

    TEXT_CSS = (
        'w-full border border-slate-200 rounded-xl px-3 py-2.5 text-slate-700 text-sm '
        'focus:outline-none focus:border-brand-400 focus:ring-2 focus:ring-brand-100'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ('first_name', 'last_name', 'email'):
                field.required = False
            if name == 'photo':
                field.widget.attrs.update({
                    'class': 'text-sm text-slate-600 file:mr-3 file:py-2 file:px-3 file:rounded-lg '
                             'file:border-0 file:bg-brand-50 file:text-brand-700 file:text-sm '
                             'file:font-medium hover:file:bg-brand-100'
                })
            elif name == 'gender':
                field.widget.attrs.update({'class': self.TEXT_CSS + ' bg-white'})
            elif name == 'address':
                field.widget.attrs.update({'class': self.TEXT_CSS + ' resize-none', 'rows': 2})
            else:
                field.widget.attrs.update({'class': self.TEXT_CSS})
            if name == 'date_of_birth':
                field.widget.input_type = 'date'

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        if Employee.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email is already in use by another employee.')
        return email


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
            'department', 'designation', 'shift'
        ).get(user=request.user)
    except Employee.DoesNotExist:
        return None


# ── Portal Dashboard ──────────────────────────────────────────────────────────
@employee_required
def portal_dashboard(request):
    employee = get_employee(request)
    today    = timezone.localdate()
    month    = today.month
    year     = today.year
    today_att = AttendanceRecord.objects.filter(
        employee=employee,
        date=today
    ).first()

    # Punch In/Out live state (today)
    punch_state = attendance_services.get_punch_state(employee, today)
    # Target working hours for today's progress ring (employee override -> shift -> default 8)
    target_working_hours = float(employee.effective_working_hours or 8)

    #Show Current date punch in/out
    today_punch_logs = PunchLog.objects.filter(
        employee=employee, date=today
    ).order_by('timestamp')
    today_punch_ins  = today_punch_logs.filter(punch_type='in')
    today_punch_outs = today_punch_logs.filter(punch_type='out')

    # Self-heal: is month ke ab tak ke (kal tak ke) din jinme punch nahi hua
    # unke liye asli 'Absent' AttendanceRecord bana do, taaki neeche ka
    # present/absent count aur % hamesha real saved data se aaye.
    attendance_services.backfill_absentees(
        date(year, month, 1), today - timedelta(days=1), employees=[employee]
    )

    # Show current months and previous month record
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
    marked_days  = present_days + absent_days
    attendance_pct = round((present_days / marked_days) * 100) if marked_days else 0

    # Sirf is employee ki leave balance
    # leave_balances = LeaveBalance.objects.filter(
    #     employee=employee,
    #     year=year
    # ).select_related('leave_type')
    # Sirf is employee ki leave balance (balances auto-create + EL monthly accrual yahin ho jaata hai)
    leave_services.sync_leave_balances_for_employee(employee, year)
    leave_balances = LeaveBalance.objects.filter(
        employee=employee,
        year=year
    ).select_related('leave_type')

    # Only employee current leave
    recent_leaves = LeaveRequest.objects.filter(
        employee=employee
    ).order_by('-created_at')[:5]

    # only employee lated payslip
    latest_payslip = Payslip.objects.filter(
        employee=employee
    ).order_by('-year', '-month').first()  
    try:
        salary = SalaryStructure.objects.get(employee=employee)
    except SalaryStructure.DoesNotExist:
        salary = None

    # ── Live, attendance-driven salary estimate for THIS month (recomputed
    # fresh on every dashboard load — not a stored/generated Payslip) ─────
    live_salary = None
    if salary:
        from payroll.payroll_calc import estimate_live_salary
        live_salary = estimate_live_salary(employee, salary, reference_date=today)

# week Attendance
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

    # Active Announcements (Super Admin broadcasts) — High → Medium → Low
    from employees.models import Announcement
    Announcement.objects.cleanup_expired()
    active_announcements = sorted(
        Announcement.objects.active().select_related('created_by'),
        key=lambda a: (a.priority_rank, -a.created_at.timestamp())
    )

    # Birthdays — this month's list (for the widget) + today's celebrants (for the banner)
    from employees.birthdays import get_birthdays_this_month
    birthdays_this_month = get_birthdays_this_month(reference_date=today)
    todays_birthday_people = [e for e in birthdays_this_month if e.is_today]
    other_birthday_people = [e for e in todays_birthday_people if not employee or e.id != employee.id]

    return render(request, 'portal/dashboard.html', {
        'employee':        employee,
        'today':           today,
        'today_att':       today_att,
        'present_days':    present_days,
        'absent_days':     absent_days,
        'late_days':       late_days,
        'attendance_pct':  attendance_pct,
        'leave_balances':  leave_balances,
        'recent_leaves':   recent_leaves,
        'latest_payslip':  latest_payslip,
        'salary':          salary,
        'live_salary':     live_salary,
        'week_records':    week_records,
        'month_name':      calendar.month_name[month],
        'upcoming_events': upcoming_events,
        'punch_state':     punch_state,
        'today_punch_ins':  today_punch_ins,
        'today_punch_outs': today_punch_outs,
        'target_working_hours': target_working_hours,
        'active_announcements': active_announcements,
        'birthdays_this_month': birthdays_this_month,
        'todays_birthday_people': todays_birthday_people,
        'other_birthday_people': other_birthday_people,
        
    })

# ── Punch In / Punch Out ───────────────────────────────────────────────────────
@employee_required
def portal_punch(request):
    """One toggle button: Punch In if not currently punched in, Punch Out otherwise."""
    employee = get_employee(request)

    if request.method == 'POST':
        # Browser se geolocation (agar employee ne allow ki ho) - hidden fields se aata hai
        raw_lat = request.POST.get('latitude', '').strip()
        raw_lng = request.POST.get('longitude', '').strip()
        location_name = request.POST.get('location_name', '').strip()
        try:
            latitude = float(raw_lat) if raw_lat else None
            longitude = float(raw_lng) if raw_lng else None
        except ValueError:
            latitude = longitude = None

        try:
            punch_type, record = attendance_services.toggle_punch(
                employee, latitude=latitude, longitude=longitude, location_name=location_name
            )
            if punch_type == 'in':
                messages.success(request, f'Punched In at {timezone.localtime().strftime("%I:%M %p")}')
            else:
                messages.success(request, f'Punched Out at {timezone.localtime().strftime("%I:%M %p")}')
        except attendance_services.PunchError as e:
            messages.error(request, str(e))

    return redirect('portal_dashboard')


# ── Portal Attendance ─────────────────────────────────────────────────────────
@employee_required
def portal_attendance(request):
    employee = get_employee(request)
    today    = timezone.localdate()

    # request.GET.get('month', today.month) khali string '' bhi return kar
    # sakta hai (e.g. link me ?month=&year= aa jaaye), aur int('') crash
    # karta hai -- isliye khali/invalid value par bhi today ka month/year
    # fallback use karo.
    month_raw = request.GET.get('month', '').strip()
    year_raw  = request.GET.get('year', '').strip()
    try:
        month = int(month_raw) if month_raw else today.month
    except ValueError:
        month = today.month
    try:
        year = int(year_raw) if year_raw else today.year
    except ValueError:
        year = today.year

    # ── Date-wise history filter (from_date - to_date) ─────────────────────
    from_date_str = request.GET.get('from_date', '')
    to_date_str   = request.GET.get('to_date', '')
    filtered_records = None
    filter_applied    = False

    if from_date_str and to_date_str:
        try:
            from_date = date.fromisoformat(from_date_str)
            to_date   = date.fromisoformat(to_date_str)
            if from_date > to_date:
                from_date, to_date = to_date, from_date
                from_date_str, to_date_str = to_date_str, from_date_str
                messages.info(request, 'From date To date ke baad tha, isliye swap kar diya.')

            filtered_records = AttendanceRecord.objects.filter(
                employee=employee,
                date__gte=from_date,
                date__lte=to_date
            ).order_by('-date')
            filter_applied = True
        except ValueError:
            messages.error(request, 'Date galat format mein hai. Date picker use karein.')

    # ── Single-day punch log (In/Out times for any selected date) ──────────
    punch_date_str = request.GET.get('punch_date', today.isoformat())
    try:
        punch_date = date.fromisoformat(punch_date_str)
    except ValueError:
        punch_date = today
        punch_date_str = today.isoformat()

    day_punch_logs = PunchLog.objects.filter(
        employee=employee, date=punch_date
    ).order_by('timestamp')
    day_punch_ins  = day_punch_logs.filter(punch_type='in')
    day_punch_outs = day_punch_logs.filter(punch_type='out')

    _, days_in_month = calendar.monthrange(year, month)
    all_days = [date(year, month, d) for d in range(1, days_in_month + 1)]

    # Self-heal: calendar khulte hi is month ke bina-punch wale beete hue
    # din ke liye asli 'Absent' AttendanceRecord bana do (condition check:
    # weekend/holiday/approved-leave/already-marked din skip ho jaate hain
    # attendance_services.auto_mark_absent() ke andar). Isse calendar aur
    # neeche ki summary counts hamesha DB me saved status se aate hain.
    attendance_services.backfill_absentees(
        all_days[0], min(all_days[-1], today - timedelta(days=1)), employees=[employee]
    )

    # Sirf is employee ki attendance
    records    = AttendanceRecord.objects.filter(
        employee=employee,
        date__month=month,
        date__year=year
    )
    record_map = {r.date: r for r in records}

    # Is month ki holidays — calendar me weekday-record-missing din ko
    # holiday se galti se "Absent" na dikha de, isliye pehle hi le lo.
    holiday_dates = set(
        Holiday.objects.filter(
            date__month=month, date__year=year
        ).values_list('date', flat=True)
    )

    calendar_data = []
    for d in all_days:
        rec = record_map.get(d)
        if rec:
            status = rec.status
        elif d in holiday_dates:
            status = 'holiday'
        elif (
            d.weekday() < 5 and d < today
            and (not employee.date_joined or d >= employee.date_joined)
        ):
            # Weekday beet chuka hai, employee joining ke baad ka hai, aur
            # koi record nahi bana (backfill_absentees() upar se safety-net
            # ke roop me — normally yahan record already ban chuka hoga).
            status = 'absent'
        else:
            # Weekend, joining se pehle ka din, ya aane wala din — status nahi
            status = None

        calendar_data.append({
            'date':       d,
            'record':     rec,
            'status':     status,
            'is_today':   d == today,
            'is_weekend': d.weekday() >= 5,
        })

    present  = records.filter(status__in=['present', 'late', 'work_from_home']).count()
    absent   = records.filter(status='absent').count() + sum(
        1 for c in calendar_data if c['status'] == 'absent' and c['record'] is None
    )
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
        'from_date_str':    from_date_str,
        'to_date_str':      to_date_str,
        'filtered_records': filtered_records,
        'filter_applied':   filter_applied,
        'punch_date_str':   punch_date_str,
        'day_punch_ins':    day_punch_ins,
        'day_punch_outs':   day_punch_outs,
    })


# ── Portal Apply Leave ────────────────────────────────────────────────────────
@employee_required
def portal_apply_leave(request):
    employee    = get_employee(request)
    leave_types = LeaveType.objects.all()
    today       = timezone.localdate()
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
        lt_id       = request.POST.get('leave_type')
        start_date  = request.POST.get('start_date')
        end_date    = request.POST.get('end_date')
        reason      = request.POST.get('reason', '').strip()
        is_half_day = request.POST.get('is_half_day') == 'on'
        half_session = request.POST.get('half_day_session', '')

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
            elif is_half_day and s != e:
                messages.error(request, 'Half day leave can only be applied for a single date (start date = end date).')
            elif is_half_day and half_session not in ('first_half', 'second_half'):
                messages.error(request, 'Please select First Half or Second Half for a half day leave.')
            else:
                if is_half_day:
                    days = 0.5
                else:
                    days = (e - s).days + 1
                    half_session = ''

                leave_type = get_object_or_404(LeaveType, pk=lt_id)

                LeaveRequest.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    start_date=s,
                    end_date=e,
                    days=days,
                    is_half_day=is_half_day,
                    half_day_session=half_session or None,
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
    today    = timezone.localdate()

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


# ── Portal: Team Requests (Reporting Manager approves their team's leaves/WFH) ──
@employee_required
def portal_team_requests(request):
    """
    Employee jinke neeche log report karte hain (unke reporting_manager),
    unke saare Leave requests (SL/EL/CL/etc) aur WFH requests yahan dikhte
    hain — approve/reject sirf apni team ke liye.
    """
    employee = get_employee(request)
    reportee_ids = employee.team_members.values_list('id', flat=True)

    status_filter = request.GET.get('status', 'pending')

    leave_qs = LeaveRequest.objects.filter(
        employee_id__in=reportee_ids
    ).select_related('employee', 'leave_type').order_by('-created_at')
    wfh_qs = WorkFromHomeRequest.objects.filter(
        employee_id__in=reportee_ids
    ).select_related('employee').order_by('-created_at')

    if status_filter and status_filter != 'all':
        leave_qs = leave_qs.filter(status=status_filter)
        wfh_qs   = wfh_qs.filter(status=status_filter)

    leave_pending_count = LeaveRequest.objects.filter(employee_id__in=reportee_ids, status='pending').count()
    wfh_pending_count    = WorkFromHomeRequest.objects.filter(employee_id__in=reportee_ids, status='pending').count()

    return render(request, 'portal/team_requests.html', {
        'employee':            employee,
        'team_members':        employee.team_members.select_related('department', 'designation').all(),
        'leave_requests':      leave_qs,
        'wfh_requests':        wfh_qs,
        'status_filter':       status_filter,
        'status_options':      [
            ('pending', 'Pending'), ('approved', 'Approved'),
            ('rejected', 'Rejected'), ('all', 'All'),
        ],
        'leave_pending_count': leave_pending_count,
        'wfh_pending_count':   wfh_pending_count,
    })


# ── Portal: Team Overview — today's attendance + who's on which project ───────
@employee_required
def portal_team_overview(request):
    """
    Sirf Reporting Managers ke liye: apni team (direct reportees) ka
    aaj ka attendance status (Present/Absent/WFH/On Leave/Not marked yet)
    aur har member kis active project(s) par kaam kar raha hai — dono
    ek hi jagah dikhata hai.
    """
    employee = get_employee(request)
    today = timezone.localdate()

    team_members = employee.team_members.select_related(
        'department', 'designation'
    ).order_by('first_name')

    reportee_ids = team_members.values_list('id', flat=True)

    # Aaj ke attendance records — ek hi query, dict me map kar lo employee_id -> record
    today_attendance = {
        a.employee_id: a
        for a in AttendanceRecord.objects.filter(employee_id__in=reportee_ids, date=today)
    }

    # Aaj approved WFH — agar attendance record na bhi ho, WFH se pata chal jayega
    today_wfh_ids = set(
        WorkFromHomeRequest.objects.filter(
            employee_id__in=reportee_ids, date=today, status='approved'
        ).values_list('employee_id', flat=True)
    )

    # Aaj approved leave par kaun kaun hai
    on_leave_ids = set(
        LeaveRequest.objects.filter(
            employee_id__in=reportee_ids, status='approved',
            start_date__lte=today, end_date__gte=today,
        ).values_list('employee_id', flat=True)
    )

    # Har member ke active projects — ek hi query se sabke liye
    project_map = {}
    projects_qs = Project.objects.filter(
        members__id__in=reportee_ids, status='active'
    ).distinct().prefetch_related('members')
    for proj in projects_qs:
        for member in proj.members.all():
            if member.id in set(reportee_ids):
                project_map.setdefault(member.id, []).append(proj)

    rows = []
    present_count, absent_count, wfh_count, leave_count, not_marked_count = 0, 0, 0, 0, 0

    for member in team_members:
        record = today_attendance.get(member.id)

        if member.id in on_leave_ids:
            today_status, status_color = 'On Leave', 'amber'
            leave_count += 1
        elif record:
            if record.status == 'present':
                today_status, status_color = 'Present', 'emerald'
                present_count += 1
            elif record.status == 'late':
                today_status, status_color = 'Late', 'amber'
                present_count += 1
            elif record.status == 'work_from_home':
                today_status, status_color = 'Work From Home', 'blue'
                wfh_count += 1
            elif record.status == 'half_day':
                today_status, status_color = 'Half Day', 'amber'
                present_count += 1
            elif record.status == 'holiday':
                today_status, status_color = 'Holiday', 'slate'
            else:
                today_status, status_color = 'Absent', 'red'
                absent_count += 1
        elif member.id in today_wfh_ids:
            today_status, status_color = 'Work From Home', 'blue'
            wfh_count += 1
        else:
            today_status, status_color = 'Not Marked Yet', 'slate'
            not_marked_count += 1

        rows.append({
            'member':         member,
            'status':         today_status,
            'status_color':   status_color,
            'check_in':       record.check_in if record else None,
            'projects':       project_map.get(member.id, []),
        })

    return render(request, 'portal/team_overview.html', {
        'employee':          employee,
        'today':             today,
        'rows':              rows,
        'team_count':        team_members.count(),
        'present_count':     present_count,
        'absent_count':      absent_count,
        'wfh_count':         wfh_count,
        'leave_count':       leave_count,
        'not_marked_count':  not_marked_count,
    })


# ── Portal: Approve / Reject a team member's Leave ──────────────────────────────
@employee_required
def portal_team_leave_approve(request, pk):
    employee = get_employee(request)
    leave = get_object_or_404(
        LeaveRequest, pk=pk, employee__reporting_manager=employee
    )
    if request.method == 'POST' and leave.status == 'pending':
        leave.status      = 'approved'
        leave.approved_by = employee
        leave.approved_at = timezone.now()
        leave.save()

        from employees.notifications import notify_team_of_leave   # 👈 NAYI LINE
        notify_team_of_leave(leave) 

        messages.success(request, f'Leave approved for {leave.employee.full_name}.')
    return redirect('portal_team_requests')


@employee_required
def portal_team_leave_reject(request, pk):
    employee = get_employee(request)
    leave = get_object_or_404(
        LeaveRequest, pk=pk, employee__reporting_manager=employee
    )
    if request.method == 'POST' and leave.status == 'pending':
        leave.status           = 'rejected'
        leave.rejection_reason = request.POST.get('rejection_reason', '').strip()
        leave.save()
        messages.success(request, f'Leave rejected for {leave.employee.full_name}.')
    return redirect('portal_team_requests')


# ── Portal: Approve / Reject a team member's WFH ─────────────────────────────────
@employee_required
def portal_team_wfh_approve(request, pk):
    employee = get_employee(request)
    wfh = get_object_or_404(
        WorkFromHomeRequest, pk=pk, employee__reporting_manager=employee
    )
    if request.method == 'POST' and wfh.status == 'pending':
        wfh.status      = 'approved'
        wfh.approved_by = employee
        wfh.approved_at = timezone.now()
        wfh.save()
        messages.success(request, f'WFH approved for {wfh.employee.full_name}.')
    return redirect('portal_team_requests')


@employee_required
def portal_team_wfh_reject(request, pk):
    employee = get_employee(request)
    wfh = get_object_or_404(
        WorkFromHomeRequest, pk=pk, employee__reporting_manager=employee
    )
    if request.method == 'POST' and wfh.status == 'pending':
        wfh.status           = 'rejected'
        wfh.rejection_reason = request.POST.get('rejection_reason', '').strip()
        wfh.save()
        messages.success(request, f'WFH rejected for {wfh.employee.full_name}.')
    return redirect('portal_team_requests')


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
    """
    My Profile — self-service page with two tabs:
      · Profile Details   → EmployeeSelfProfileForm (photo, name, contact, etc.)
      · Login & Security   → username change + password change

    On a successful password change, every Super Admin is notified via
    notify_admins_of_password_change() (bell dropdown on the admin side).
    """
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.models import User
    from .notifications import notify_admins_of_password_change, notify_admins_of_password_reset_request
    from .birthdays import turning_age

    employee = get_employee(request)
    form_type = request.POST.get('form_type')

    details_form = EmployeeSelfProfileForm(instance=employee)

    # ── Birthday card popup: is today this employee's birthday? ─────────
    today = timezone.localdate()
    is_birthday_today = bool(
        employee and employee.date_of_birth
        and employee.date_of_birth.month == today.month
        and employee.date_of_birth.day == today.day
    )
    birthday_age = turning_age(employee, today) if is_birthday_today else None

    if request.method == 'POST':

        # ── Tab 1: Profile Details ──────────────────────────────────────
        if form_type == 'details':
            details_form = EmployeeSelfProfileForm(
                request.POST, request.FILES, instance=employee
            )
            if details_form.is_valid():
                details_form.save()
                messages.success(request, 'Your profile has been updated.')
                return redirect('portal_profile')
            else:
                messages.error(request, 'Please fix the errors below.')

        # ── Tab 2a: Username ────────────────────────────────────────────
        elif form_type == 'username':
            new_username = (request.POST.get('username') or '').strip()
            if not new_username:
                messages.error(request, 'Username cannot be empty.')
            elif User.objects.filter(username__iexact=new_username).exclude(pk=request.user.pk).exists():
                messages.error(request, 'That username is already taken.')
            else:
                request.user.username = new_username
                request.user.save()
                messages.success(request, 'Your login username has been updated.')
            return redirect('portal_profile')

        # ── Tab 2b: Password ─────────────────────────────────────────────
        elif form_type == 'password':
            current_password = request.POST.get('current_password') or ''
            new_password     = request.POST.get('new_password') or ''
            confirm_password = request.POST.get('confirm_password') or ''

            if not request.user.check_password(current_password):
                messages.error(request, 'Your current password is incorrect.')
            elif len(new_password) < 6:
                messages.error(request, 'New password must be at least 6 characters.')
            elif new_password != confirm_password:
                messages.error(request, 'New password and confirmation do not match.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)  # stay logged in
                if employee:
                    notify_admins_of_password_change(employee)
                messages.success(request, 'Your password has been changed successfully.')
            return redirect('portal_profile')

        # ── Tab 2c: "Forgot current password" — notify Admin ────────────
        elif form_type == 'request_reset':
            if employee:
                notify_admins_of_password_reset_request(employee)
                messages.success(
                    request,
                    "Your HR Admin has been notified — they'll reset your password shortly."
                )
            return redirect('portal_profile')

    return render(request, 'portal/profile.html', {
        'employee':           employee,
        'details_form':       details_form,
        'is_birthday_today':  is_birthday_today,
        'birthday_age':       birthday_age,
    })


# ── Portal: Employee updates their OWN Bank / Aadhaar / PAN details ────────────
@employee_required
def portal_edit_bank_details(request):
    """
    Super Admin can set these when the employee is first added. From then
    on, ONLY the employee themselves can update them — using
    EmployeeBankDetailsForm, which is restricted to just these 6 fields
    so nothing else on their Employee record can be changed here.
    """
    from .views import EmployeeBankDetailsForm

    employee = get_employee(request)

    if request.method == 'POST':
        form = EmployeeBankDetailsForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your bank & ID details have been updated.')
            return redirect('portal_profile')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = EmployeeBankDetailsForm(instance=employee)

    return render(request, 'portal/edit_bank_details.html', {
        'employee': employee,
        'form':     form,
    })

# ── Portal Events & Holidays ──────────────────────────────────────────────────
@employee_required
def portal_events(request):
    from events.models import Event

    employee   = get_employee(request)
    event_type = request.GET.get('type', '')
    today      = timezone.localdate()

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

# ── Portal Birthday Calendar ─────────────────────────────────────────────────
# employees/portal_views.py — is function ko purane "portal_birthday_calendar" ki jagah replace karo

# ── Portal Birthday Calendar ─────────────────────────────────────────────────
@employee_required
def portal_birthday_calendar(request):
    """
    Shows a horizontal 'Birthday Path' timeline for the month (every active
    employee's birthday marked as a stop along the path — a deliberately
    different layout from a plain week-grid), plus a countdown hero for
    whoever's birthday is coming up next across the whole company, and a
    horizontally-scrolling 'polaroid' strip of everyone celebrating this
    month. Visible to all employees. Use ?month=&year= to browse other months.
    """
    from employees.birthdays import get_month_birthdays, turning_age, get_next_upcoming_birthday

    employee = get_employee(request)
    today    = timezone.localdate()

    try:
        month = int(request.GET.get('month', today.month))
        year  = int(request.GET.get('year', today.year))
        if month < 1 or month > 12:
            raise ValueError
    except (TypeError, ValueError):
        month, year = today.month, today.year

    month_birthdays = get_month_birthdays(month, reference_date=today)
    # Map day-of-month -> list of employees, used to mark stops on the path
    birthdays_by_day = {}
    for emp in month_birthdays:
        birthdays_by_day.setdefault(emp.bday_day, []).append(emp)
        emp.turning = turning_age(emp, today)

    num_days = calendar.monthrange(year, month)[1]
    days_in_month = range(1, num_days + 1)

    # Sun-Sat week grid, for the "Calendar" view (0 = day outside this month)
    cal = calendar.Calendar(firstweekday=6)  # Sunday-first
    month_weeks = cal.monthdayscalendar(year, month)

    # Prev / next month for navigation
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year
    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    is_current_month = (month == today.month and year == today.year)

    # Company-wide "who's next" countdown hero
    next_birthday_employee, next_birthday_days = get_next_upcoming_birthday(reference_date=today)

    return render(request, 'portal/birthday_calendar.html', {
        'employee':               employee,
        'today':                  today,
        'month':                  month,
        'year':                   year,
        'month_name':             calendar.month_name[month],
        'days_in_month':          days_in_month,
        'month_weeks':            month_weeks,
        'birthdays_by_day':       birthdays_by_day,
        'month_birthdays':        month_birthdays,
        'prev_month':             prev_month,
        'prev_year':              prev_year,
        'next_month':             next_month,
        'next_year':              next_year,
        'is_current_month':       is_current_month,
        'next_birthday_employee': next_birthday_employee,
        'next_birthday_days':     next_birthday_days,
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

# ── Portal Wellness / Mind Relaxation ─────────────────────────────────────────
@employee_required
def portal_wellness(request):
    from wellness.models import WellnessResource

    employee = get_employee(request)
    category = request.GET.get('category', '')

    resources = WellnessResource.objects.filter(is_active=True)
    if category:
        resources = resources.filter(category=category)

    return render(request, 'portal/wellness.html', {
        'employee':          employee,
        'resources':         resources,
        'selected_category': category,
        'category_choices':  WellnessResource.CATEGORY_CHOICES,
    })

# file ke END me ye 4 views add karo:

@employee_required
def portal_face_enroll(request):
    employee = get_employee(request)
    existing = FaceEncoding.objects.filter(employee=employee).first()
    return render(request, 'portal/face_enroll.html', {
        'employee': employee,
        'already_enrolled': bool(existing),
        'enrolled_at': existing.updated_at if existing else None,
    })


@employee_required
@require_POST
def portal_face_enroll_save(request):
    employee = get_employee(request)
    try:
        body = json.loads(request.body.decode('utf-8'))
        descriptor = face_utils.validate_descriptor(body.get('descriptor'))
    except (ValueError, face_utils.FaceDescriptorError) as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    FaceEncoding.objects.update_or_create(
        employee=employee,
        defaults={'encoding': descriptor, 'is_active': True},
    )
    return JsonResponse({'ok': True, 'message': 'Face enrolled successfully.'})


@employee_required
def portal_face_punch(request):
    employee = get_employee(request)
    enrolled = FaceEncoding.objects.filter(employee=employee, is_active=True).first()
    if not enrolled:
        messages.warning(request, 'Face not enrolled yet. Please enroll your face first.')
        return redirect('portal_face_enroll')

    punch_state = attendance_services.get_punch_state(employee, timezone.localdate())
    return render(request, 'portal/face_punch.html', {
        'employee': employee,
        'punch_state': punch_state,
    })


@employee_required
@require_POST
def portal_face_punch_verify(request):
    employee = get_employee(request)
    enrolled = FaceEncoding.objects.filter(employee=employee, is_active=True).first()
    if not enrolled:
        return JsonResponse({'ok': False, 'error': 'Face not enrolled.'}, status=400)

    try:
        body = json.loads(request.body.decode('utf-8'))
        live_descriptor = face_utils.validate_descriptor(body.get('descriptor'))
    except (ValueError, face_utils.FaceDescriptorError) as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    matched, distance = face_utils.is_match(enrolled.encoding, live_descriptor)
    if not matched:
        return JsonResponse({
            'ok': False,
            'error': 'Face not recognized. Please try again in good lighting, facing the camera.',
            'distance': round(distance, 3),
        }, status=401)

    try:
        punch_type, record = attendance_services.toggle_punch(
            employee,
            source='face',
            latitude=body.get('latitude'),
            longitude=body.get('longitude'),
            location_name=(body.get('location_name') or '').strip(),
        )
    except attendance_services.PunchError as e:
        return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    return JsonResponse({
        'ok': True,
        'punch_type': punch_type,
        'message': f"Punch {'In' if punch_type == 'in' else 'Out'} successful for {employee.full_name}.",
        'distance': round(distance, 3),
    })

# employees/portal_views.py — FILE KE END ME add karo

# ── My Projects (employee sees the project(s) they're assigned to + teammates) ──
@employee_required
def portal_my_projects(request):
    employee = get_employee(request)
    from employees.models import Project
    projects = Project.objects.filter(
        members=employee
    ).prefetch_related('members').select_related('manager', 'department').distinct().order_by('-created_at')

    # Only someone who has been made a Reporting Manager for at least one
    # employee (i.e. has direct reports) is allowed to create new projects.
    # Everyone else on the portal can only view the projects they're on.
    is_manager = employee.team_members.exists() if employee else False

    return render(request, 'portal/projects.html', {
        'employee': employee,
        'projects': projects,
        'can_add_project': is_manager,
    })


@employee_required
def portal_project_detail(request, pk):
    employee = get_employee(request)
    from employees.models import Project
    project = get_object_or_404(Project.objects.prefetch_related('members'), pk=pk, members=employee)

    return render(request, 'portal/project_detail.html', {
        'employee': employee,
        'project': project,
        'team_members': project.members.select_related('department', 'designation').all(),
    })


# ── Add Project (Reporting Managers only) ───────────────────────────────────
@employee_required
def portal_add_project(request):
    """
    Only an employee who is set as someone else's Reporting Manager
    (i.e. has direct reports / team_members) can create a project.
    Regular employees never see the "Add Project" button, and even if
    they hit this URL directly they're blocked here too.
    """
    employee = get_employee(request)
    from employees.models import Project

    team = employee.team_members.select_related('department', 'designation').order_by('first_name') if employee else Project.objects.none()

    if not employee or not employee.team_members.exists():
        messages.error(request, "Only Reporting Managers can add new projects.")
        return redirect('portal_my_projects')

    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        code = (request.POST.get('code') or '').strip()
        description = (request.POST.get('description') or '').strip()
        start_date = request.POST.get('start_date') or None
        end_date = request.POST.get('end_date') or None
        status = request.POST.get('status') or 'planning'
        member_ids = request.POST.getlist('members')

        if not name or not code or not start_date:
            messages.error(request, "Project name, code and start date are required.")
        elif Project.objects.filter(code__iexact=code).exists():
            messages.error(request, f"Project code '{code}' is already in use. Please choose another.")
        else:
            project = Project.objects.create(
                name=name,
                code=code,
                description=description,
                department=employee.department,
                manager=employee,
                start_date=start_date,
                end_date=end_date,
                status=status,
            )
            member_ids = set(member_ids)
            member_ids.add(str(employee.id))  # manager is automatically a member
            project.members.set(member_ids)

            messages.success(request, f"Project '{project.name}' created successfully.")
            return redirect('portal_project_detail', pk=project.pk)

    return render(request, 'portal/add_project.html', {
        'employee': employee,
        'team_members': team,
        'status_choices': Project.STATUS_CHOICES,
    })


# ── Notifications (e.g. "your teammate is on leave") ────────────────────────────
# @employee_required
# def portal_notifications(request):
#     employee = get_employee(request)
#     from employees.models import Notification
#     notifications = Notification.objects.filter(recipient=employee).order_by('-created_at')[:100]
#     Notification.objects.filter(recipient=employee, is_read=False).update(is_read=True)

#     return render(request, 'portal/notifications.html', {
#         'employee': employee,
#         'notifications': notifications,
#     })

# employees/portal_views.py — portal_notifications() function replace karo

def portal_notifications(request):
    employee = get_employee(request)
    from employees.models import Notification, Announcement
    Announcement.objects.cleanup_expired()   # expired ones (and their notifications, via CASCADE) go away
    notifications = Notification.objects.filter(recipient=employee).order_by('-created_at')[:100]
    Notification.objects.filter(recipient=employee, is_read=False).update(is_read=True)

    return render(request, 'portal/notifications.html', {
        'employee': employee,
        'notifications': notifications,
    })




@employee_required
def portal_announcements(request):
    """Dedicated 'Announcements' tab in the employee portal — all active broadcasts."""
    from employees.models import Announcement
    Announcement.objects.cleanup_expired()
    announcements = sorted(
        Announcement.objects.active().select_related('created_by'),
        key=lambda a: (a.priority_rank, -a.created_at.timestamp())
    )
    return render(request, 'portal/announcements.html', {
        'announcements': announcements,
    })


@employee_required
def portal_announcement_json(request, pk):
    """Powers the click-to-popup when an employee clicks an announcement notification."""
    from employees.models import Announcement
    Announcement.objects.cleanup_expired()
    announcement = get_object_or_404(Announcement, pk=pk)
    return JsonResponse({
        'title':      announcement.title,
        'message':    announcement.message,
        'priority':   announcement.priority,
        'priority_display': announcement.get_priority_display(),
        'created_by': announcement.created_by.full_name if announcement.created_by else 'Admin',
        'created_at': announcement.created_at.strftime('%d %b %Y, %I:%M %p'),
    })


# ── Portal: Apply / View My Expense Claims ─────────────────────────────────────
@employee_required
def portal_apply_expense(request):
    """Employee submits a new expense claim and sees their own claim history."""
    from expenses.models import ExpenseClaim
    from expenses.views import log_action

    employee = get_employee(request)

    if request.method == 'POST':
        category     = request.POST.get('category', '').strip()
        amount       = request.POST.get('amount', '').strip()
        expense_date = request.POST.get('expense_date', '').strip()
        description  = request.POST.get('description', '').strip()
        bill         = request.FILES.get('bill')

        if category and amount and expense_date and description:
            claim = ExpenseClaim.objects.create(
                employee=employee,
                category=category,
                amount=amount,
                expense_date=expense_date,
                description=description,
                bill=bill,
            )
            log_action(claim, 'submitted', employee)
            messages.success(request, 'Expense claim submitted successfully.')
        else:
            messages.error(request, 'Please fill in all required fields.')
        return redirect('portal_apply_expense')

    my_claims = ExpenseClaim.objects.filter(
        employee=employee
    ).order_by('-created_at')

    return render(request, 'portal/apply_expense.html', {
        'employee':         employee,
        'today':            timezone.localdate(),
        'category_choices': ExpenseClaim.CATEGORY_CHOICES,
        'my_claims':        my_claims,
    })


# ── Portal: Cancel My Own Expense Claim ─────────────────────────────────────────
@employee_required
def portal_cancel_expense(request, pk):
    from expenses.models import ExpenseClaim
    from expenses.views import log_action

    employee = get_employee(request)
    claim = get_object_or_404(ExpenseClaim, pk=pk, employee=employee)

    if request.method == 'POST' and claim.status == 'pending_manager':
        claim.status = 'cancelled'
        claim.save()
        log_action(claim, 'cancelled', employee)
        messages.success(request, 'Expense claim cancelled.')
    return redirect('portal_apply_expense')


# ── Portal: Team Expenses — Reporting Manager reviews their team's claims ──────
@employee_required
def portal_team_expenses(request):
    """
    Employee jinke neeche log report karte hain (unke reporting_manager),
    unke expense claims yahan dikhte hain — sirf pending_manager stage
    par approve/reject kiya ja sakta hai; uske baad Finance handle karta hai.
    """
    from expenses.models import ExpenseClaim

    employee = get_employee(request)
    reportee_ids = list(employee.team_members.values_list('id', flat=True))

    status_filter = request.GET.get('status', 'pending_manager')

    claims_qs = ExpenseClaim.objects.filter(
        employee_id__in=reportee_ids
    ).select_related('employee').order_by('-created_at')

    if status_filter and status_filter != 'all':
        claims_qs = claims_qs.filter(status=status_filter)

    pending_count = ExpenseClaim.objects.filter(
        employee_id__in=reportee_ids, status='pending_manager'
    ).count()

    return render(request, 'portal/team_expenses.html', {
        'employee':        employee,
        'team_members':    employee.team_members.select_related('department', 'designation').all(),
        'expense_claims':  claims_qs,
        'status_filter':   status_filter,
        'status_options':  [
            ('pending_manager', 'Pending'), ('pending_finance', 'With Finance'),
            ('approved', 'Approved'), ('reimbursed', 'Reimbursed'),
            ('rejected', 'Rejected'), ('all', 'All'),
        ],
        'pending_count':   pending_count,
    })


# ── Portal: Approve / Reject a team member's Expense Claim ─────────────────────
# ── Portal: Approve / Reject a team member's Expense Claim ─────────────────────
@employee_required
def portal_team_expense_approve(request, pk):
    from expenses.models import ExpenseClaim
    from expenses.views import log_action, notify_employee

    employee = get_employee(request)
    claim = get_object_or_404(
        ExpenseClaim, pk=pk, employee__reporting_manager=employee
    )
    if request.method == 'POST' and claim.status == 'pending_manager':
        claim.status = 'pending_finance'
        claim.manager_reviewed_by = employee
        claim.manager_reviewed_at = timezone.now()
        claim.save()
        log_action(claim, 'manager_approved', employee)
        notify_employee(
            claim, 'Expense claim approved by manager',
            f'Your {claim.get_category_display()} claim of Rs.{claim.amount} was approved by your manager and sent to Finance for final approval.'
        )
        messages.success(request, f'Expense claim approved for {claim.employee.full_name}. Sent to Finance.')
    return redirect('portal_team_expenses')


@employee_required
def portal_team_expense_reject(request, pk):
    from expenses.models import ExpenseClaim
    from expenses.views import log_action, notify_employee

    employee = get_employee(request)
    claim = get_object_or_404(
        ExpenseClaim, pk=pk, employee__reporting_manager=employee
    )
    if request.method == 'POST' and claim.status == 'pending_manager':
        reason = request.POST.get('rejection_reason', '').strip()
        claim.status = 'rejected'
        claim.rejected_by = employee
        claim.rejected_at = timezone.now()
        claim.rejection_reason = reason
        claim.save()
        log_action(claim, 'manager_rejected', employee, reason)
        notify_employee(
            claim, 'Expense claim rejected by manager',
            f'Your {claim.get_category_display()} claim of Rs.{claim.amount} was rejected by your manager.' + (f' Reason: {reason}' if reason else '')
        )
        messages.success(request, f'Expense claim rejected for {claim.employee.full_name}.')
    return redirect('portal_team_expenses')


# ── Portal: Attendance / Leave Claims ("meri leave nahi thi") ─────────────────
@employee_required
def portal_disputes(request):
    """Employee's own list of raised attendance/leave claims."""
    employee = get_employee(request)
    disputes = AttendanceDispute.objects.filter(employee=employee).order_by('-created_at')
    return render(request, 'portal/disputes.html', {
        'employee': employee,
        'disputes': disputes,
    })


@employee_required
def portal_raise_dispute(request):
    """
    Employee raises a claim against a specific date's attendance status —
    e.g. "yeh din meri leave/absent nahi thi, mai present tha".
    Goes to HR/Super Admin for review before anything changes.
    """
    employee = get_employee(request)
    prefill_date = request.GET.get('date', '')

    if request.method == 'POST':
        claim_date_str = request.POST.get('date', '').strip()
        claimed_status = request.POST.get('claimed_status', '').strip()
        reason = request.POST.get('reason', '').strip()

        if not claim_date_str or not claimed_status or not reason:
            messages.error(request, 'Please fill the date, what it should be, and your reason.')
            return redirect('portal_raise_dispute')

        try:
            claim_date = datetime.strptime(claim_date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date.')
            return redirect('portal_raise_dispute')

        existing_record = AttendanceRecord.objects.filter(employee=employee, date=claim_date).first()

        AttendanceDispute.objects.create(
            employee=employee,
            date=claim_date,
            attendance_record=existing_record,
            current_status=existing_record.get_status_display() if existing_record else 'Not Marked',
            claimed_status=claimed_status,
            reason=reason,
        )
        messages.success(request, 'Your claim has been submitted to HR/Super Admin for review.')
        return redirect('portal_disputes')

    return render(request, 'portal/raise_dispute.html', {
        'employee': employee,
        'prefill_date': prefill_date,
        'status_choices': AttendanceRecord.STATUS_CHOICES,
    })


@employee_required
def portal_cancel_dispute(request, pk):
    employee = get_employee(request)
    dispute = get_object_or_404(AttendanceDispute, pk=pk, employee=employee)
    if request.method == 'POST' and dispute.status == 'pending':
        dispute.delete()
        messages.success(request, 'Claim withdrawn.')
    return redirect('portal_disputes')