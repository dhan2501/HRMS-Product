from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import date, timedelta, datetime
import calendar
from employees.models import Employee
# from .models import AttendanceRecord, Holiday,WorkFromHomeRequest
from .models import AttendanceRecord, Holiday, WorkFromHomeRequest, PunchLog, ShiftTiming, BiometricDevice, BiometricRawLog
# from .models import AttendanceRecord, Holiday, WorkFromHomeRequest



from functools import wraps
from django.shortcuts import redirect
from employees.models import Employee


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if not (request.user.is_staff or request.user.is_superuser):
            try:
                Employee.objects.get(user=request.user)
                return redirect('portal_dashboard')
            except Employee.DoesNotExist:
                return redirect('employee_login')
        return view_func(request, *args, **kwargs)
    return wrapper


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


# ── Employee-wise Attendance History (Super Admin) ─────────────────────────────
@admin_required
def employee_attendance_history(request):
    """
    Super Admin ke liye: Employee ID ya Name se search karke employee dhundo,
    aur koi bhi date range (past days sahit) dekho — daily punch in/out,
    breaks, aur working hours sab ek jagah.
    """
    search_query = request.GET.get('search', '').strip()

    employees = Employee.objects.select_related('department', 'designation').order_by('first_name', 'last_name')
    if search_query:
        employees = employees.filter(
            Q(employee_id__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    emp_id     = request.GET.get('employee') or ''
    start_str  = request.GET.get('start_date') or ''
    end_str    = request.GET.get('end_date') or ''

    today = date.today()
    try:
        start_date = date.fromisoformat(start_str) if start_str else today - timedelta(days=6)
    except ValueError:
        start_date = today - timedelta(days=6)
    try:
        end_date = date.fromisoformat(end_str) if end_str else today
    except ValueError:
        end_date = today

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    selected_employee = None
    rows = []
    totals = {'present': 0, 'absent': 0, 'late': 0, 'half_day': 0, 'wfh': 0, 'break_minutes': 0, 'working_hours': 0}

    if emp_id:
        selected_employee = get_object_or_404(Employee, pk=emp_id)

        records = AttendanceRecord.objects.filter(
            employee=selected_employee, date__gte=start_date, date__lte=end_date
        )
        record_map = {r.date: r for r in records}

        punches = PunchLog.objects.filter(
            employee=selected_employee, date__gte=start_date, date__lte=end_date
        ).order_by('date', 'timestamp')
        punch_map = {}
        for p in punches:
            punch_map.setdefault(p.date, []).append(p)

        day = start_date
        while day <= end_date:
            # Employee ki joining date se pehle koi row mat dikhao
            if selected_employee.date_joined and day < selected_employee.date_joined:
                day += timedelta(days=1)
                continue
            rec = record_map.get(day)
            rows.append({
                'date':    day,
                'record':  rec,
                'punches': punch_map.get(day, []),
            })
            if rec:
                if rec.status in ('present', 'late', 'work_from_home'):
                    totals['present'] += 1
                if rec.status == 'absent':
                    totals['absent'] += 1
                if rec.status == 'late':
                    totals['late'] += 1
                if rec.status == 'half_day':
                    totals['half_day'] += 1
                if rec.status == 'work_from_home':
                    totals['wfh'] += 1
                totals['break_minutes'] += rec.total_break_minutes or 0
                totals['working_hours'] += float(rec.working_hours or 0)
            day += timedelta(days=1)
        rows.reverse()  # latest date first

    attendance_pct = round((totals['present'] / len(rows)) * 100) if rows else 0

    return render(request, 'attendance/employee_history.html', {
        'employees':         employees,
        'search_query':      search_query,
        'selected_employee': selected_employee,
        'selected_emp_id':   emp_id,
        'start_date':        start_date,
        'end_date':          end_date,
        'rows':              rows,
        'totals':            totals,
        'attendance_pct':    attendance_pct,
        'today':             today,
    })


# ═══════════════════════════════════════════════════════════════════════════
# Biometric Device Integration (ADMS / Push protocol)
#
# Most budget fingerprint machines (ZKTeco, eSSL, Realtime, etc.) support a
# "Cloud Server / ADMS" mode where you type this server's URL into the
# device once, and it pushes attendance logs here automatically over the
# internet/LAN — no SDK, no polling script needed on our side.
#
# Device settings screen usually asks for:
#   Server Address / IP : <this server's IP or domain>
#   Server Port         : 80 (or 8000 if running the Django dev server)
#   Enable Domain Name  : ON (if using a domain)
#
# The device then talks to:
#   GET  /attendance/device/iclock/cdata/?SN=<serial>              (handshake)
#   GET  /attendance/device/iclock/getrequest/?SN=<serial>         (polling for commands)
#   POST /attendance/device/iclock/cdata/?SN=<serial>&table=ATTLOG (actual punches)
# ═══════════════════════════════════════════════════════════════════════════
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .services import record_device_punch


def _touch_device(serial, request):
    if not serial:
        return
    ip = request.META.get('REMOTE_ADDR')
    device, _ = BiometricDevice.objects.get_or_create(serial_number=serial)
    device.last_seen_at = timezone.now()
    device.last_ip = ip
    device.save(update_fields=['last_seen_at', 'last_ip'])


@csrf_exempt
def device_cdata(request):
    """
    Handshake (GET) + attendance upload (POST) endpoint. Device-facing —
    no login required (the device can't authenticate like a browser), so
    this URL should only be exposed on a trusted network/VPN, or behind a
    reverse-proxy IP allowlist in production.
    """
    serial = request.GET.get('SN', '')
    _touch_device(serial, request)

    if request.method == 'GET':
        table = request.GET.get('table', '')
        if table:
            # Device asking whether there's anything new to upload for this
            # table — we don't queue anything server-side, so always "none".
            return HttpResponse('OK', content_type='text/plain')
        # Initial handshake — standard ADMS option string.
        body = (
            f"GET OPTION FROM: {serial}\n"
            "Stamp=9999\n"
            "OpStamp=9999\n"
            "ErrorDelay=30\n"
            "Delay=10\n"
            "TransTimes=00:00;14:05\n"
            "TransInterval=1\n"
            "TransFlag=1111000000\n"
            "Realtime=1\n"
            "Encrypt=None\n"
        )
        return HttpResponse(body, content_type='text/plain')

    # POST — actual attendance log upload
    table = request.GET.get('table', 'ATTLOG')
    raw_body = request.body.decode('utf-8', errors='ignore')

    if table != 'ATTLOG' or not raw_body.strip():
        return HttpResponse('OK', content_type='text/plain')

    lines = [ln for ln in raw_body.strip().splitlines() if ln.strip()]
    parsed = []
    for line in lines:
        cols = line.split('\t')
        if len(cols) < 2:
            continue
        device_user_id = cols[0].strip()
        time_str = cols[1].strip()
        raw_state = cols[2].strip() if len(cols) > 2 else None
        try:
            ts = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
            ts = timezone.make_aware(ts, timezone.get_current_timezone())
        except ValueError:
            continue
        parsed.append((device_user_id, ts, raw_state, line))

    # Process oldest-first so in/out toggling comes out in the right order
    parsed.sort(key=lambda p: p[1])

    processed = 0
    for device_user_id, ts, raw_state, line in parsed:
        employee = Employee.objects.filter(biometric_id=device_user_id).first()

        raw_log = BiometricRawLog.objects.create(
            device_user_id=device_user_id,
            device_serial=serial,
            timestamp=ts,
            raw_line=line[:255],
            employee=employee,
        )

        if employee:
            punch, _record = record_device_punch(
                employee, ts, device_serial=serial, raw_state=raw_state
            )
            if punch:
                raw_log.punch_log = punch
                raw_log.save(update_fields=['punch_log'])
        processed += 1

    return HttpResponse(f'OK: {processed}', content_type='text/plain')


@csrf_exempt
def device_getrequest(request):
    """Device polls this periodically asking for pending commands — we have none."""
    serial = request.GET.get('SN', '')
    _touch_device(serial, request)
    return HttpResponse('OK', content_type='text/plain')


# ── Biometric Devices — Admin page ──────────────────────────────────────────
@login_required
@admin_required
def biometric_devices(request):
    """
    Shows connected devices + recent raw punch pushes, and lets HR map an
    unmapped device PIN to an Employee (retroactively creating the missed
    PunchLog + recalculating attendance for that day too).
    """
    devices = BiometricDevice.objects.all()
    raw_logs = BiometricRawLog.objects.select_related('employee').order_by('-timestamp')[:100]
    unmapped_pins = (
        BiometricRawLog.objects.filter(employee__isnull=True)
        .values_list('device_user_id', flat=True).distinct()
    )
    employees = Employee.objects.filter(status='active').order_by('first_name')

    if request.method == 'POST':
        pin = request.POST.get('device_user_id', '').strip()
        emp_id = request.POST.get('employee', '').strip()
        if pin and emp_id:
            employee = get_object_or_404(Employee, pk=emp_id)
            if Employee.objects.filter(biometric_id=pin).exclude(pk=employee.pk).exists():
                messages.error(request, f'PIN {pin} is already mapped to another employee.')
            else:
                employee.biometric_id = pin
                employee.save(update_fields=['biometric_id'])

                # Retroactively turn previously-unmatched raw logs for this
                # PIN into real punches.
                backlog = BiometricRawLog.objects.filter(
                    device_user_id=pin, employee__isnull=True
                ).order_by('timestamp')
                count = 0
                for entry in backlog:
                    punch, _record = record_device_punch(
                        employee, entry.timestamp, device_serial=entry.device_serial
                    )
                    entry.employee = employee
                    if punch:
                        entry.punch_log = punch
                        count += 1
                    entry.save(update_fields=['employee', 'punch_log'])

                messages.success(
                    request,
                    f'PIN {pin} mapped to {employee.full_name}. {count} past punch(es) recovered.'
                )
        return redirect('biometric_devices')

    return render(request, 'attendance/biometric_devices.html', {
        'devices':       devices,
        'raw_logs':      raw_logs,
        'unmapped_pins': unmapped_pins,
        'employees':     employees,
    })