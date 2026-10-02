from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django import forms
from functools import wraps


from .models import (
    Employee, Department, Designation, EmployeeStatusLog,
    PerformanceReview, PerformanceGoal, SiteSettings, AuditLog,
    Project, EmployeeRole, Notification, Announcement,
)
from .notifications import can_manage_projects, is_super_admin, notify_all_of_announcement
from attendance.models import AttendanceRecord, ShiftTiming, Holiday
from leaves.models import LeaveRequest
from datetime import date
from django.utils import timezone

# from .dashboard_analytics import get_dashboard_analytics


from .dashboard_analytics import (
    get_dashboard_analytics,
    get_attendance_overview,
    get_attendance_range_label,
)

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if request.user.is_staff or request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        try:
            Employee.objects.get(user=request.user)
            return redirect('portal_dashboard')
        except Employee.DoesNotExist:
            return redirect('employee_login')
    return wrapper


# ── Form ────────────────────────────────────────────────────────────────────
# class EmployeeForm(forms.ModelForm):
#     class Meta:
#         model = Employee
#         fields = [
#             'employee_id', 'first_name', 'last_name', 'email', 'phone',
#             'date_of_birth', 'gender', 'photo',
#             'department', 'designation', 'reporting_manager', 'date_joined',
#             'employment_type', 'status',
#             'shift', 'standard_working_hours', 'biometric_id',
#             'address', 'emergency_contact_name', 'emergency_contact_phone',
#         ]
#         widgets = {
#             'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
#             'date_joined':   forms.DateInput(attrs={'type': 'date'}),
#             'address':       forms.Textarea(attrs={'rows': 3}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['employee_id'].required = True
#         self.fields['first_name'].required  = True
#         self.fields['last_name'].required   = True
#         self.fields['email'].required       = True
#         self.fields['date_joined'].required = True
#         self.fields['department'].required  = True
#         self.fields['phone'].required                  = False
#         self.fields['date_of_birth'].required          = False
#         self.fields['gender'].required                 = False
#         self.fields['photo'].required                  = False
#         self.fields['designation'].required            = False
#         self.fields['shift'].required                  = False
#         self.fields['standard_working_hours'].required = False
#         self.fields['biometric_id'].required            = False
#         self.fields['address'].required                = False
#         self.fields['emergency_contact_name'].required = False
#         self.fields['emergency_contact_phone'].required= False
#         self.fields['designation'].queryset = Designation.objects.select_related('department').all()
#         self.fields['reporting_manager'].required = False
#         managers_qs = Employee.objects.filter(status='active').order_by('first_name', 'last_name')
#         if self.instance and self.instance.pk:
#             # An employee can't report to themselves
#             managers_qs = managers_qs.exclude(pk=self.instance.pk)
#         self.fields['reporting_manager'].queryset = managers_qs

#     def clean_biometric_id(self):
#         # Store blank as None so multiple employees can have "no device ID"
#         # without violating the unique constraint.
#         value = (self.cleaned_data.get('biometric_id') or '').strip()
#         return value or None


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'email', 'phone',
            'date_of_birth', 'gender', 'photo',
            'department', 'designation', 'reporting_manager', 'date_joined',
            'employment_type', 'status',
            'shift', 'standard_working_hours', 'biometric_id',
            'address', 'emergency_contact_name', 'emergency_contact_phone',
            'bank_account_holder_name', 'bank_account_number', 'bank_name', 'bank_ifsc_code',
            'aadhar_number', 'pan_number',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'date_joined':   forms.DateInput(attrs={'type': 'date'}),
            'address':       forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee_id'].required = True
        self.fields['first_name'].required  = True
        self.fields['last_name'].required   = True
        self.fields['email'].required       = True
        self.fields['date_joined'].required = True
        self.fields['department'].required  = True
        self.fields['phone'].required                  = False
        self.fields['date_of_birth'].required          = False
        self.fields['gender'].required                 = False
        self.fields['photo'].required                  = False
        self.fields['designation'].required            = False
        self.fields['shift'].required                  = False
        self.fields['standard_working_hours'].required = False
        self.fields['biometric_id'].required            = False
        self.fields['address'].required                = False
        self.fields['emergency_contact_name'].required = False
        self.fields['emergency_contact_phone'].required= False
        self.fields['bank_account_holder_name'].required = False
        self.fields['bank_account_number'].required      = False
        self.fields['bank_name'].required                = False
        self.fields['bank_ifsc_code'].required            = False
        self.fields['aadhar_number'].required             = False
        self.fields['pan_number'].required                = False
        self.fields['designation'].queryset = Designation.objects.select_related('department').all()
        self.fields['reporting_manager'].required = False
        managers_qs = Employee.objects.filter(status='active').order_by('first_name', 'last_name')
        if self.instance and self.instance.pk:
            # An employee can't report to themselves
            managers_qs = managers_qs.exclude(pk=self.instance.pk)
        self.fields['reporting_manager'].queryset = managers_qs

    def clean_biometric_id(self):
        # Store blank as None so multiple employees can have "no device ID"
        # without violating the unique constraint.
        value = (self.cleaned_data.get('biometric_id') or '').strip()
        return value or None

    def clean_aadhar_number(self):
        value = (self.cleaned_data.get('aadhar_number') or '').replace(' ', '').strip()
        if value and (not value.isdigit() or len(value) != 12):
            raise forms.ValidationError('Aadhaar number must be exactly 12 digits.')
        return value

    def clean_pan_number(self):
        value = (self.cleaned_data.get('pan_number') or '').strip().upper()
        if value and len(value) != 10:
            raise forms.ValidationError('PAN must be exactly 10 characters (e.g. ABCDE1234F).')
        return value

    def clean_bank_ifsc_code(self):
        return (self.cleaned_data.get('bank_ifsc_code') or '').strip().upper()


# ── Employee-only form: Bank / Aadhaar / PAN self-update ───────────────────────
class EmployeeBankDetailsForm(forms.ModelForm):
    """
    Deliberately lists ONLY the bank/Aadhaar/PAN fields. Because a
    ModelForm only ever reads/writes the fields named here, an employee
    submitting this form can never touch any other field on their own
    Employee record — even if the POST data were tampered with.
    """
    class Meta:
        model = Employee
        fields = [
            'bank_account_holder_name', 'bank_account_number', 'bank_name', 'bank_ifsc_code',
            'aadhar_number', 'pan_number',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            self.fields[name].required = False

    def clean_aadhar_number(self):
        value = (self.cleaned_data.get('aadhar_number') or '').replace(' ', '').strip()
        if value and (not value.isdigit() or len(value) != 12):
            raise forms.ValidationError('Aadhaar number must be exactly 12 digits.')
        return value

    def clean_pan_number(self):
        value = (self.cleaned_data.get('pan_number') or '').strip().upper()
        if value and len(value) != 10:
            raise forms.ValidationError('PAN must be exactly 10 characters (e.g. ABCDE1234F).')
        return value

    def clean_bank_ifsc_code(self):
        return (self.cleaned_data.get('bank_ifsc_code') or '').strip().upper()

# ── Dashboard ────────────────────────────────────────────────────────────────
# @login_required
# def dashboard(request):
#     if not request.user.is_authenticated:
#         return redirect('/admin-login/')

#     if not (request.user.is_staff or request.user.is_superuser):
#         return redirect('/portal/')

#     today            = date.today()
#     total_employees  = Employee.objects.filter(status='active').count()
#     today_present    = AttendanceRecord.objects.filter(
#         date=today,
#         status__in=['present', 'late', 'work_from_home']
#     ).count()
#     pending_leaves   = LeaveRequest.objects.filter(status='pending').count()
#     departments      = Department.objects.annotate(
#         emp_count=Count('employees', filter=Q(employees__status='active'))
#     )
#     recent_employees = Employee.objects.filter(
#         status='active'
#     ).order_by('-date_joined')[:5]
#     recent_leaves    = LeaveRequest.objects.filter(
#         status='pending'
#     ).order_by('-created_at')[:5]

#     return render(request, 'dashboard/index.html', {
#         'total_employees':  total_employees,
#         'today_present':    today_present,
#         'pending_leaves':   pending_leaves,
#         'departments':      departments,
#         'recent_employees': recent_employees,
#         'recent_leaves':    recent_leaves,
#         'today':            today,
#     })


# employees/views.py — @login_required def dashboard(request): — pura function

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/admin-login/')

    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/portal/')

    today            = date.today()
    total_employees  = Employee.objects.filter(status='active').count()
    today_present    = AttendanceRecord.objects.filter(
        date=today,
        status__in=['present', 'late', 'work_from_home']
    ).count()
    pending_leaves   = LeaveRequest.objects.filter(status='pending').count()
    departments      = Department.objects.annotate(
        emp_count=Count('employees', filter=Q(employees__status='active'))
    )
    recent_employees = Employee.objects.filter(
        status='active'
    ).order_by('-date_joined')[:5]
    recent_leaves    = LeaveRequest.objects.filter(
        status='pending'
    ).order_by('-created_at')[:5]

    # ── Who's absent today? (Super Admin sees everyone, a Reporting
    # Manager only sees their own team) — skipped on weekends/holidays.
    current_emp   = Employee.objects.filter(user=request.user).first()
    is_weekend    = today.weekday() in (5, 6)          # Sat, Sun
    today_holiday = Holiday.objects.filter(date=today).first()
    is_working_day = not is_weekend and not today_holiday

    absent_today   = Employee.objects.none()
    on_leave_today = Employee.objects.none()
    is_super_admin = bool(current_emp and current_emp.is_primary_admin)

    if is_working_day:
        active_employees = Employee.objects.filter(status='active')
        if not is_super_admin and current_emp and current_emp.team_members.exists():
            # Reporting manager: restrict the widget to their own team.
            active_employees = active_employees.filter(
                Q(reporting_manager=current_emp) | Q(id=current_emp.id)
            )

        present_ids = AttendanceRecord.objects.filter(
            date=today, status__in=['present', 'late', 'work_from_home', 'half_day']
        ).values_list('employee_id', flat=True)

        on_leave_today = active_employees.filter(
            leave_requests__status='approved',
            leave_requests__start_date__lte=today,
            leave_requests__end_date__gte=today,
        ).distinct()

        absent_today = active_employees.exclude(
            id__in=present_ids
        ).exclude(
            id__in=on_leave_today.values_list('id', flat=True)
        ).distinct()

    return render(request, 'dashboard/index.html', {
        'total_employees':  total_employees,
        'today_present':    today_present,
        'pending_leaves':   pending_leaves,
        'departments':      departments,
        'recent_employees': recent_employees,
        'recent_leaves':    recent_leaves,
        'today':            today,
        'is_working_day':   is_working_day,
        'today_holiday':    today_holiday,
        'absent_today':     absent_today,
        'on_leave_today':   on_leave_today,
        'is_super_admin':   is_super_admin,
        'can_manage_projects': can_manage_projects(current_emp),
    })

# ── Employee List ─────────────────────────────────────────────────────────────
@login_required
def employee_list(request):
    employees   = Employee.objects.select_related('department', 'designation', 'reporting_manager').all()
    departments = Department.objects.all()
    manager_options = Employee.objects.filter(status='active').order_by('first_name', 'last_name')

    dept_filter   = request.GET.get('department')
    status_filter = request.GET.get('status')
    search        = request.GET.get('search', '')

    if dept_filter:
        employees = employees.filter(department_id=dept_filter)
    if status_filter:
        employees = employees.filter(status=status_filter)
    if search:
        employees = employees.filter(
            Q(first_name__icontains=search)  |
            Q(last_name__icontains=search)   |
            Q(employee_id__icontains=search)
        )

    return render(request, 'employees/list.html', {
        'employees':       employees,
        'departments':     departments,
        'manager_options': manager_options,
    })


# ── Add Employee ──────────────────────────────────────────────────────────────
@login_required
def add_employee(request):
    departments  = Department.objects.all()
    designations = Designation.objects.select_related('department').all()
    shifts       = ShiftTiming.objects.all()

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()

            # Auto-create login credentials
            from employees.auth_views import create_employee_user
            user, username, password = create_employee_user(employee)

            if username:
                messages.success(
                    request,
                    f'✅ Employee {employee.full_name} added! '
                    f'Login: Username = "{username}" | Password = "{password}"'
                )
            else:
                messages.success(request, f'✅ Employee {employee.full_name} added!')

            return redirect('employee_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = EmployeeForm()

    return render(request, 'employees/add.html', {
        'form':         form,
        'departments':  departments,
        'designations': designations,
        'shifts':       shifts,
    })

# ── Edit Employee ─────────────────────────────────────────────────────────────
@login_required
def edit_employee(request, pk):
    employee     = get_object_or_404(Employee, pk=pk)
    departments  = Department.objects.all()
    designations = Designation.objects.select_related('department').all()
    shifts       = ShiftTiming.objects.all()

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ {employee.full_name} updated successfully!')
            return redirect('employee_detail', pk=pk)
        else:
            messages.error(request, '❌ Please fix the errors below.')
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'employees/add.html', {
        'form':         form,
        'employee':     employee,
        'departments':  departments,
        'designations': designations,
        'shifts':       shifts,
        'is_edit':      True,
    })


# ── Employee Detail ───────────────────────────────────────────────────────────
@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    status_logs = employee.status_logs.select_related('changed_by')[:10]

    # ✅ Reporting hierarchy — who they report to, and who reports to them
    team_members = employee.team_members.select_related('department', 'designation')

    # ✅ Performance section data
    performance_reviews = employee.performance_reviews.select_related('reviewer').prefetch_related('goals')[:10]

    return render(request, 'employees/detail.html', {
        'employee': employee,
        'status_logs': status_logs,
        'team_members': team_members,
        'performance_reviews': performance_reviews,
    })


# ── Set Reporting Manager (inline, from Employee List) ──────────────────────────
@login_required
def set_reporting_manager(request, pk):
    """
    Quick-set an employee's Reporting Manager directly from the Employee List
    table (inline dropdown, auto-submits). Admin/HR only.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to set reporting managers.')
        return redirect('employee_list')

    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        manager_id = request.POST.get('reporting_manager', '').strip()

        if not manager_id:
            employee.reporting_manager = None
            employee.save(update_fields=['reporting_manager'])
            messages.success(request, f'Reporting manager cleared for {employee.full_name}.')
        elif str(manager_id) == str(employee.pk):
            messages.error(request, 'An employee cannot report to themselves.')
        else:
            manager = get_object_or_404(Employee, pk=manager_id)
            employee.reporting_manager = manager
            employee.save(update_fields=['reporting_manager'])
            messages.success(request, f'{manager.full_name} set as Reporting Manager for {employee.full_name}.')

    referer = request.META.get('HTTP_REFERER')
    return redirect(referer) if referer else redirect('employee_list')


# ── Deactivate / Hold / Reactivate Employee ─────────────────────────────────────
@login_required
def update_employee_status(request, pk):
    """
    HR/Admin-only action to deactivate an employee (resigned/left the
    company), put them on hold (long leave — 6 months, 1 year, etc. with
    an expected return date), terminate them, or reactivate them.
    Every change is written to EmployeeStatusLog with a mandatory reason,
    so there is always a record of why and when the status changed.
    """
    if not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'You do not have permission to change employee status.')
        return redirect('employee_detail', pk=pk)

    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('new_status', '').strip()
        reason     = request.POST.get('reason', '').strip()
        hold_until = request.POST.get('hold_until', '').strip() or None

        valid_statuses = dict(Employee.STATUS_CHOICES)
        if new_status not in valid_statuses:
            messages.error(request, 'Invalid status selected.')
            return redirect('employee_detail', pk=pk)

        if not reason:
            messages.error(request, 'A reason is required to change employee status.')
            return redirect('employee_detail', pk=pk)

        if new_status == 'on_leave' and not hold_until:
            messages.error(request, 'Please provide an expected return date for "On Leave / Hold".')
            return redirect('employee_detail', pk=pk)

        previous_status = employee.status

        # Log the change first (keeps a full audit trail)
        EmployeeStatusLog.objects.create(
            employee=employee,
            previous_status=previous_status,
            new_status=new_status,
            reason=reason,
            hold_until=hold_until if new_status == 'on_leave' else None,
            changed_by=request.user,
        )

        # Apply the change
        employee.status = new_status
        employee.status_reason = reason
        employee.status_changed_at = timezone.now()
        employee.hold_until = hold_until if new_status == 'on_leave' else None
        employee.save()

        # Deactivating/terminating an employee also locks their portal login;
        # reactivating restores it.
        if employee.user:
            employee.user.is_active = (new_status not in ('inactive', 'terminated'))
            employee.user.save(update_fields=['is_active'])

        status_labels = {
            'active':     'reactivated',
            'inactive':   'deactivated',
            'on_leave':   'put on hold / long leave',
            'terminated': 'terminated',
        }
        messages.success(
            request,
            f'{employee.full_name} has been {status_labels.get(new_status, "updated")}.'
        )

    return redirect('employee_detail', pk=pk)


# ── Department List ───────────────────────────────────────────────────────────
@login_required
def department_list(request):
    departments = Department.objects.annotate(
        emp_count=Count('employees', filter=Q(employees__status='active'))
    )
    return render(request, 'employees/departments.html', {'departments': departments})


# ── Add Department ────────────────────────────────────────────────────────────
@login_required
def add_department(request):
    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        code        = request.POST.get('code', '').strip().upper()
        description = request.POST.get('description', '').strip()

        if not name or not code:
            messages.error(request, 'Department name and code are required.')
        elif Department.objects.filter(name=name).exists():
            messages.error(request, f'Department "{name}" already exists.')
        elif Department.objects.filter(code=code).exists():
            messages.error(request, f'Code "{code}" already used.')
        else:
            Department.objects.create(name=name, code=code, description=description)
            messages.success(request, f'Department "{name}" added successfully!')
            return redirect('department_list')

    return render(request, 'employees/add_department.html')


# ── Edit Department ───────────────────────────────────────────────────────────
@login_required
def edit_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)

    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        code        = request.POST.get('code', '').strip().upper()
        description = request.POST.get('description', '').strip()

        if not name or not code:
            messages.error(request, 'Name and code are required.')
        elif Department.objects.filter(name=name).exclude(pk=pk).exists():
            messages.error(request, f'Department "{name}" already exists.')
        elif Department.objects.filter(code=code).exclude(pk=pk).exists():
            messages.error(request, f'Code "{code}" already used.')
        else:
            dept.name        = name
            dept.code        = code
            dept.description = description
            dept.save()
            messages.success(request, f'Department "{name}" updated!')
            return redirect('department_list')

    return render(request, 'employees/add_department.html', {'dept': dept})


# ── Delete Department ─────────────────────────────────────────────────────────
@login_required
def delete_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = dept.name
        dept.delete()
        messages.success(request, f'Department "{name}" deleted.')
    return redirect('department_list')

# ── Designation List ──────────────────────────────────────────────────────────
@login_required
def designation_list(request):
    designations = Designation.objects.select_related('department').all()
    return render(request, 'employees/designations.html', {'designations': designations})

# ── Add Designation ───────────────────────────────────────────────────────────
@login_required
def add_designation(request):
    departments = Department.objects.all()

    if request.method == 'POST':
        title      = request.POST.get('title', '').strip()
        dept_id    = request.POST.get('department')
        level      = request.POST.get('level', 1)

        if not title or not dept_id:
            messages.error(request, 'Title and Department are required.')
        elif Designation.objects.filter(title=title).exists():
            messages.error(request, f'Designation "{title}" already exists.')
        else:
            dept = get_object_or_404(Department, pk=dept_id)
            Designation.objects.create(title=title, department=dept, level=level)
            messages.success(request, f'Designation "{title}" added successfully!')
            return redirect('designation_list')

    return render(request, 'employees/add_designation.html', {
        'departments': departments,
    })


# ── Edit Designation ──────────────────────────────────────────────────────────
@login_required
def edit_designation(request, pk):
    designation = get_object_or_404(Designation, pk=pk)
    departments = Department.objects.all()

    if request.method == 'POST':
        title   = request.POST.get('title', '').strip()
        dept_id = request.POST.get('department')
        level   = request.POST.get('level', 1)

        if not title or not dept_id:
            messages.error(request, 'Title and Department are required.')
        elif Designation.objects.filter(title=title).exclude(pk=pk).exists():
            messages.error(request, f'Designation "{title}" already exists.')
        else:
            dept                = get_object_or_404(Department, pk=dept_id)
            designation.title      = title
            designation.department = dept
            designation.level      = level
            designation.save()
            messages.success(request, f'Designation "{title}" updated!')
            return redirect('designation_list')

    return render(request, 'employees/add_designation.html', {
        'designation': designation,
        'departments': departments,
        'is_edit':     True,
    })


# ── Delete Designation ────────────────────────────────────────────────────────
@login_required
def delete_designation(request, pk):
    designation = get_object_or_404(Designation, pk=pk)
    if request.method == 'POST':
        title = designation.title
        designation.delete()
        messages.success(request, f'Designation "{title}" deleted.')
    return redirect('designation_list')


@login_required
def employee_credentials(request):
    """Admin page — all employees with login details."""
    employees = Employee.objects.select_related(
        'user', 'department', 'designation'
    ).all().order_by('first_name')

    return render(request, 'employees/credentials.html', {
        'employees': employees,
    })


@login_required
def create_employee_login(request, pk):
    """Create login for employee who doesn't have one."""
    from django.contrib.auth.models import User
    employee = get_object_or_404(Employee, pk=pk)

    if employee.user:
        messages.warning(request, f'{employee.full_name} already has login: {employee.user.username}')
        return redirect('employee_credentials')

    first    = employee.first_name.lower().strip().replace(' ', '')
    last     = employee.last_name.lower().strip().replace(' ', '')
    username = f"{first}.{last}"

    if User.objects.filter(username=username).exists():
        username = f"{first}.{employee.employee_id.lower()}"

    password = f"{employee.first_name.capitalize()}@{employee.employee_id}"

    user = User.objects.create_user(
        username=username,
        password=password,
        email=employee.email,
        first_name=employee.first_name,
        last_name=employee.last_name,
        is_staff=False,
        is_superuser=False,
    )
    employee.user = user
    employee.save()

    messages.success(
        request,
        f'✅ Login created for {employee.full_name} — Username: "{username}" | Password: "{password}"'
    )
    return redirect('employee_credentials')


@login_required
def create_all_logins(request):
    """Bulk create logins for all employees without user."""
    from django.contrib.auth.models import User

    employees_no_user = Employee.objects.filter(user=None)
    created = 0

    for employee in employees_no_user:
        first    = employee.first_name.lower().strip().replace(' ', '')
        last     = employee.last_name.lower().strip().replace(' ', '')
        username = f"{first}.{last}"

        if User.objects.filter(username=username).exists():
            username = f"{first}.{employee.employee_id.lower()}"

        password = f"{employee.first_name.capitalize()}@{employee.employee_id}"

        user = User.objects.create_user(
            username=username,
            password=password,
            email=employee.email,
            first_name=employee.first_name,
            last_name=employee.last_name,
            is_staff=False,
            is_superuser=False,
        )
        employee.user = user
        employee.save()
        created += 1

    messages.success(request, f'✅ {created} employee login(s) created successfully!')
    return redirect('employee_credentials')


@login_required
def reset_employee_password(request, pk):
    """Reset password to default."""
    employee = get_object_or_404(Employee, pk=pk)

    if not employee.user:
        messages.error(request, 'No login found for this employee.')
        return redirect('employee_credentials')

    password = f"{employee.first_name.capitalize()}@{employee.employee_id}"
    employee.user.set_password(password)
    employee.user.save()

    messages.success(
        request,
        f'🔑 Password reset for {employee.full_name} — New Password: "{password}"'
    )
    return redirect('employee_credentials')

# ── Performance Section ─────────────────────────────────────────────────────
class PerformanceReviewForm(forms.ModelForm):
    class Meta:
        model = PerformanceReview
        fields = [
            'reviewer', 'review_period_type', 'period_start', 'period_end',
            'overall_rating', 'goals_achieved', 'strengths',
            'areas_of_improvement', 'reviewer_comments', 'status',
        ]
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end':   forms.DateInput(attrs={'type': 'date'}),
            'goals_achieved':       forms.Textarea(attrs={'rows': 3}),
            'strengths':            forms.Textarea(attrs={'rows': 2}),
            'areas_of_improvement': forms.Textarea(attrs={'rows': 2}),
            'reviewer_comments':    forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, employee=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reviewer'].required = False
        self.fields['reviewer'].queryset = Employee.objects.filter(status='active').order_by('first_name', 'last_name')
        # Default the reviewer to the employee's reporting manager
        if employee and employee.reporting_manager_id and not self.instance.pk:
            self.fields['reviewer'].initial = employee.reporting_manager_id


@login_required
@admin_required
def add_performance_review(request, pk):
    """HR/Admin (or the reporting manager) adds a new performance review for an employee."""
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == 'POST':
        form = PerformanceReviewForm(request.POST, employee=employee)
        if form.is_valid():
            review = form.save(commit=False)
            review.employee = employee
            review.save()
            messages.success(request, f'✅ Performance review added for {employee.full_name}.')
            return redirect('employee_detail', pk=employee.pk)
        else:
            messages.error(request, '❌ Please fix the errors below.')
    else:
        form = PerformanceReviewForm(employee=employee)

    return render(request, 'employees/performance_form.html', {
        'form': form,
        'employee': employee,
        'is_edit': False,
    })


@login_required
@admin_required
def edit_performance_review(request, pk, review_pk):
    """Edit an existing performance review."""
    employee = get_object_or_404(Employee, pk=pk)
    review   = get_object_or_404(PerformanceReview, pk=review_pk, employee=employee)

    if request.method == 'POST':
        form = PerformanceReviewForm(request.POST, instance=review, employee=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'✅ Performance review updated for {employee.full_name}.')
            return redirect('employee_detail', pk=employee.pk)
        else:
            messages.error(request, '❌ Please fix the errors below.')
    else:
        form = PerformanceReviewForm(instance=review, employee=employee)

    return render(request, 'employees/performance_form.html', {
        'form': form,
        'employee': employee,
        'review': review,
        'is_edit': True,
    })


@login_required
@admin_required
def delete_performance_review(request, pk, review_pk):
    employee = get_object_or_404(Employee, pk=pk)
    review   = get_object_or_404(PerformanceReview, pk=review_pk, employee=employee)
    review.delete()
    messages.success(request, '🗑️ Performance review deleted.')
    return redirect('employee_detail', pk=employee.pk)


@login_required
def my_team(request):
    """
    Shows the logged-in employee (if they are a reporting manager) the list
    of team members reporting to them — the manager-side of the
    employee ↔ reporting manager connectivity.
    """
    try:
        manager_employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        manager_employee = None

    team_members = Employee.objects.none()
    if manager_employee:
        team_members = manager_employee.team_members.select_related('department', 'designation').all()

    return render(request, 'employees/my_team.html', {
        'manager_employee': manager_employee,
        'team_members': team_members,
    })


# ── System Settings (theme, logo, superadmins, audit log) ─────────────────────
def superuser_required(view_func):
    """Only real superusers can view/change System Settings — this page can
    grant admin panel access to other people, so it's more sensitive than
    the regular @admin_required (staff) pages."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if not request.user.is_superuser:
            messages.error(request, 'Only a Super Admin can access System Settings.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def user_has_full_admin_access(user):
    """
    Full Access (Primary) Super Admin = can grant/revoke Super Admin
    access for OTHER people. Everyone else who is merely is_superuser
    can use the admin panel normally but can't manage other admins.

    A superuser with NO Employee profile (e.g. created via
    `createsuperuser` directly) is always treated as Full Access —
    they're the root/system account and there's nothing to restrict them
    against.
    """
    if not user.is_superuser:
        return False
    emp = Employee.objects.filter(user=user).first()
    if emp is None:
        return True
    return emp.is_primary_admin


@superuser_required
def system_settings(request):
    from .audit import log_action

    site = SiteSettings.load()
    can_manage_admins = user_has_full_admin_access(request.user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        # ── 1) Theme / branding ────────────────────────────────────────────
        if form_type == 'theme':
            old_primary = site.primary_color
            old_text    = site.text_color
            old_name    = site.company_name
            old_code    = site.company_code

            site.company_name  = request.POST.get('company_name', site.company_name).strip()
            site.company_code  = request.POST.get('company_code', site.company_code).strip()
            site.primary_color = request.POST.get('primary_color', site.primary_color)
            site.text_color    = request.POST.get('text_color', site.text_color)
            if request.FILES.get('logo'):
                site.logo = request.FILES['logo']
            site.updated_by = request.user
            site.save()

            if old_primary != site.primary_color:
                log_action(request, 'settings', 'Theme', 'primary_color', old_primary, site.primary_color,
                           description='Changed primary theme color')
            if old_text != site.text_color:
                log_action(request, 'settings', 'Theme', 'text_color', old_text, site.text_color,
                           description='Changed text color')
            if old_name != site.company_name:
                log_action(request, 'settings', 'Branding', 'company_name', old_name, site.company_name,
                           description='Changed company name')
            if old_code != site.company_code:
                log_action(request, 'settings', 'Branding', 'company_code', old_code, site.company_code,
                           description='Changed company code')
            if request.FILES.get('logo'):
                log_action(request, 'settings', 'Branding', 'logo', 'old logo', 'new logo',
                           description='Uploaded a new company logo')

            messages.success(request, '✅ Theme & branding updated.')
            return redirect('system_settings')

        # ── 2) Grant Super Admin access ─────────────────────────────────────
        elif form_type == 'grant_admin':
            if not can_manage_admins:
                messages.error(request, 'Only a Full Access Super Admin can grant Super Admin access.')
                return redirect('system_settings')

            emp_id = request.POST.get('employee_id')
            give_full_access = request.POST.get('full_access') == 'on'
            employee = get_object_or_404(Employee, pk=emp_id)
            if not employee.user:
                messages.error(request, f'{employee.full_name} has no login account yet — create login credentials first.')
                return redirect('system_settings')

            employee.user.is_staff = True
            employee.user.is_superuser = True
            employee.user.save(update_fields=['is_staff', 'is_superuser'])

            employee.is_primary_admin = give_full_access
            employee.save(update_fields=['is_primary_admin'])

            log_action(
                request, 'permission', 'Superadmin', 'is_superuser', 'False', 'True',
                description=f'Granted Super Admin access to {employee.full_name}'
                            + (' (with Full Access)' if give_full_access else ''),
                target_employee=employee,
            )
            messages.success(request, f'✅ {employee.full_name} is now a Super Admin.')
            return redirect('system_settings')

        # ── 3) Revoke Super Admin access ────────────────────────────────────
        elif form_type == 'revoke_admin':
            if not can_manage_admins:
                messages.error(request, 'Only a Full Access Super Admin can revoke Super Admin access.')
                return redirect('system_settings')

            emp_id = request.POST.get('employee_id')
            employee = get_object_or_404(Employee, pk=emp_id)

            if employee.user == request.user:
                messages.error(request, "You can't revoke your own Super Admin access.")
                return redirect('system_settings')

            if employee.user:
                employee.user.is_superuser = False
                employee.user.is_staff = False
                employee.user.save(update_fields=['is_staff', 'is_superuser'])

                employee.is_primary_admin = False
                employee.save(update_fields=['is_primary_admin'])

                log_action(
                    request, 'permission', 'Superadmin', 'is_superuser', 'True', 'False',
                    description=f'Revoked Super Admin access from {employee.full_name}',
                    target_employee=employee,
                )
                messages.success(request, f'✅ Super Admin access revoked for {employee.full_name}.')
            return redirect('system_settings')

        # ── 4) Toggle Full Access (promote/demote a Super Admin) ────────────
        elif form_type == 'toggle_full_access':
            if not can_manage_admins:
                messages.error(request, 'Only a Full Access Super Admin can change this.')
                return redirect('system_settings')

            emp_id = request.POST.get('employee_id')
            employee = get_object_or_404(Employee, pk=emp_id)

            if employee.user == request.user:
                messages.error(request, "You can't change your own Full Access status.")
                return redirect('system_settings')

            old_value = employee.is_primary_admin
            employee.is_primary_admin = not employee.is_primary_admin
            employee.save(update_fields=['is_primary_admin'])

            log_action(
                request, 'permission', 'Superadmin', 'is_primary_admin',
                str(old_value), str(employee.is_primary_admin),
                description=f'{"Granted" if employee.is_primary_admin else "Removed"} Full Access for {employee.full_name}',
                target_employee=employee,
            )
            messages.success(request, f'✅ Full Access {"granted to" if employee.is_primary_admin else "removed from"} {employee.full_name}.')
            return redirect('system_settings')
                # ── 5) Grant Panel Access (HR/staff — NOT Super Admin) ───────────────
        elif form_type == 'grant_panel_access':
            if not can_manage_admins:
                messages.error(request, 'Only a Full Access Super Admin can grant panel access.')
                return redirect('system_settings')

            emp_id = request.POST.get('employee_id')
            employee = get_object_or_404(Employee, pk=emp_id)
            if not employee.user:
                messages.error(request, f'{employee.full_name} has no login account yet — create login credentials first.')
                return redirect('system_settings')

            employee.user.is_staff = True
            employee.user.save(update_fields=['is_staff'])

            log_action(
                request, 'permission', 'PanelAccess', 'is_staff', 'False', 'True',
                description=f'Granted admin panel access (HR/staff, not Super Admin) to {employee.full_name}',
                target_employee=employee,
            )
            messages.success(request, f'✅ {employee.full_name} can now access the admin panel (notifications, employee list, etc.) without Super Admin rights.')
            return redirect('system_settings')

        # ── 6) Revoke Panel Access ────────────────────────────────────────────
        elif form_type == 'revoke_panel_access':
            if not can_manage_admins:
                messages.error(request, 'Only a Full Access Super Admin can revoke panel access.')
                return redirect('system_settings')

            emp_id = request.POST.get('employee_id')
            employee = get_object_or_404(Employee, pk=emp_id)

            if employee.user == request.user:
                messages.error(request, "You can't revoke your own panel access.")
                return redirect('system_settings')

            if employee.user and not employee.user.is_superuser:
                employee.user.is_staff = False
                employee.user.save(update_fields=['is_staff'])

                log_action(
                    request, 'permission', 'PanelAccess', 'is_staff', 'True', 'False',
                    description=f'Revoked admin panel access from {employee.full_name}',
                    target_employee=employee,
                )
                messages.success(request, f'✅ Panel access revoked for {employee.full_name}.')
            return redirect('system_settings')

    # ── GET: build page context ─────────────────────────────────────────────
    superadmins = Employee.objects.filter(
        user__is_superuser=True
    ).select_related('user', 'department', 'designation').order_by('first_name')

    grantable_employees = Employee.objects.filter(
        user__isnull=False, user__is_superuser=False
    ).select_related('department', 'designation').order_by('first_name')

    panel_access_employees = Employee.objects.filter(
        user__is_staff=True, user__is_superuser=False
    ).select_related('user', 'department', 'designation').order_by('first_name')

    grantable_for_panel = Employee.objects.filter(
        user__isnull=False, user__is_staff=False
    ).select_related('department', 'designation').order_by('first_name')

    logs = AuditLog.objects.select_related('user', 'employee', 'department').all()

    module_filter = request.GET.get('module', '').strip()
    emp_filter    = request.GET.get('employee', '').strip()
    if module_filter:
        logs = logs.filter(module__icontains=module_filter)
    if emp_filter:
        logs = logs.filter(employee_id=emp_filter)

    logs = logs[:200]

    modules = AuditLog.objects.values_list('module', flat=True).distinct().order_by('module')
    all_employees_for_filter = Employee.objects.order_by('first_name')

    # return render(request, 'employees/settings.html', {
    #     'site': site,
    #     'superadmins': superadmins,
    #     'grantable_employees': grantable_employees,
    #     'logs': logs,
    #     'modules': modules,
    #     'all_employees_for_filter': all_employees_for_filter,
    #     'module_filter': module_filter,
    #     'emp_filter': emp_filter,
    #     'can_manage_admins': can_manage_admins,
    # })
    return render(request, 'employees/settings.html', {
        'site': site,
        'superadmins': superadmins,
        'grantable_employees': grantable_employees,
        'panel_access_employees': panel_access_employees,
        'grantable_for_panel': grantable_for_panel,
        'logs': logs,
        'modules': modules,
        'all_employees_for_filter': all_employees_for_filter,
        'module_filter': module_filter,
        'emp_filter': emp_filter,
        'can_manage_admins': can_manage_admins,
    })


# ── My Profile (logged-in admin / Super Admin — own account) ────────────────
# Lets ANY admin-panel user (Super Admin included) update their own login
# username, password, and personal details from one page. Works even for a
# pure `createsuperuser` root account that has no linked Employee profile —
# in that case only the User (login) fields are shown/editable.
@admin_required
def my_profile(request):
    from django.contrib.auth.models import User
    from django.contrib.auth import update_session_auth_hash
    from .audit import log_action

    user = request.user
    employee = Employee.objects.select_related('department', 'designation').filter(user=user).first()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        # ── 1) Personal / profile details ───────────────────────────────
        if form_type == 'details':
            old_snapshot = f'{user.first_name} {user.last_name} / {user.email}'

            first_name = request.POST.get('first_name', '').strip()
            last_name  = request.POST.get('last_name', '').strip()
            email      = request.POST.get('email', '').strip()

            if not first_name or not email:
                messages.error(request, '❌ First name and email are required.')
                return redirect('my_profile')

            user.first_name = first_name
            user.last_name  = last_name
            user.email      = email
            user.save(update_fields=['first_name', 'last_name', 'email'])

            if employee:
                employee.first_name = first_name
                employee.last_name  = last_name
                employee.email      = email
                employee.phone      = request.POST.get('phone', '').strip()
                dob = request.POST.get('date_of_birth')
                employee.date_of_birth = dob or None
                employee.gender = request.POST.get('gender', '').strip()
                employee.address = request.POST.get('address', '').strip()
                employee.emergency_contact_name  = request.POST.get('emergency_contact_name', '').strip()
                employee.emergency_contact_phone = request.POST.get('emergency_contact_phone', '').strip()
                if request.FILES.get('photo'):
                    employee.photo = request.FILES['photo']
                employee.save()

            log_action(
                request, 'update', 'My Profile', 'details',
                old_snapshot, f'{first_name} {last_name} / {email}',
                description='Updated own profile details', target_employee=employee,
            )
            messages.success(request, '✅ Profile details updated successfully.')
            return redirect('my_profile')

        # ── 2) Change username ───────────────────────────────────────────
        elif form_type == 'username':
            new_username = request.POST.get('username', '').strip()

            if not new_username:
                messages.error(request, '❌ Username cannot be empty.')
            elif User.objects.filter(username__iexact=new_username).exclude(pk=user.pk).exists():
                messages.error(request, f'❌ Username "{new_username}" is already taken.')
            else:
                old_username = user.username
                user.username = new_username
                user.save(update_fields=['username'])
                log_action(
                    request, 'update', 'My Profile', 'username', old_username, new_username,
                    description='Changed own login username', target_employee=employee,
                )
                messages.success(request, f'✅ Username updated to "{new_username}".')
            return redirect('my_profile')

        # ── 3) Change password ───────────────────────────────────────────
        elif form_type == 'password':
            current_password = request.POST.get('current_password', '')
            new_password     = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if not user.check_password(current_password):
                messages.error(request, '❌ Current password is incorrect.')
            elif len(new_password) < 6:
                messages.error(request, '❌ New password must be at least 6 characters.')
            elif new_password != confirm_password:
                messages.error(request, '❌ New password and confirm password do not match.')
            else:
                user.set_password(new_password)
                user.save(update_fields=['password'])
                update_session_auth_hash(request, user)  # keeps them logged in after password change
                log_action(
                    request, 'update', 'My Profile', 'password', '••••••••', '••••••••',
                    description='Changed own login password', target_employee=employee,
                )
                messages.success(request, '✅ Password changed successfully.')
            return redirect('my_profile')

    return render(request, 'employees/my_profile.html', {
        'employee': employee,
    })


# employees/views.py — FILE KE END ME add karo

# ── Projects / Assignments ──────────────────────────────────────────────────
# Visible to every staff user on the admin side. Creating/editing a project
# is restricted to the Super Admin (is_primary_admin) and to whoever has been
# made a Reporting Manager with can_assign_project=True on their EmployeeRole.

@login_required
def project_list(request):
    projects = Project.objects.select_related('department', 'manager').prefetch_related('members').all()

    status_filter = request.GET.get('status', '')
    search        = request.GET.get('search', '')
    if status_filter:
        projects = projects.filter(status=status_filter)
    if search:
        projects = projects.filter(Q(name__icontains=search) | Q(code__icontains=search))

    current_emp = Employee.objects.filter(user=request.user).first()

    return render(request, 'employees/projects_list.html', {
        'projects':            projects,
        'status_filter':       status_filter,
        'search':              search,
        'can_manage_projects': can_manage_projects(current_emp),
    })


@login_required
def add_project(request):
    current_emp = Employee.objects.filter(user=request.user).first()
    if not can_manage_projects(current_emp):
        messages.error(request, 'You do not have permission to create projects.')
        return redirect('project_list')

    departments = Department.objects.all()
    # Only active employees can be assigned; managers list = active employees too.
    employees   = Employee.objects.filter(status='active').order_by('first_name', 'last_name')

    if request.method == 'POST':
        name        = request.POST.get('name', '').strip()
        code        = request.POST.get('code', '').strip().upper()
        description = request.POST.get('description', '').strip()
        department_id = request.POST.get('department') or None
        manager_id  = request.POST.get('manager') or None
        start_date  = request.POST.get('start_date') or None
        end_date    = request.POST.get('end_date') or None
        status      = request.POST.get('status', 'planning')
        member_ids  = request.POST.getlist('members')

        if not name or not code or not start_date:
            messages.error(request, 'Project name, code and start date are required.')
        else:
            project = Project.objects.create(
                name=name, code=code, description=description,
                department_id=department_id, manager_id=manager_id,
                start_date=start_date, end_date=end_date or None,
                status=status,
            )
            if member_ids:
                project.members.set(member_ids)
            messages.success(request, f'✅ Project "{project.name}" created!')
            return redirect('project_detail', pk=project.pk)

    return render(request, 'employees/project_form.html', {
        'departments': departments,
        'employees':   employees,
        'is_edit':     False,
    })


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    current_emp = Employee.objects.filter(user=request.user).first()
    if not can_manage_projects(current_emp):
        messages.error(request, 'You do not have permission to edit projects.')
        return redirect('project_detail', pk=pk)

    departments = Department.objects.all()
    employees   = Employee.objects.filter(status='active').order_by('first_name', 'last_name')

    if request.method == 'POST':
        project.name        = request.POST.get('name', '').strip()
        project.code        = request.POST.get('code', '').strip().upper()
        project.description = request.POST.get('description', '').strip()
        project.department_id = request.POST.get('department') or None
        project.manager_id  = request.POST.get('manager') or None
        project.start_date  = request.POST.get('start_date') or project.start_date
        project.end_date    = request.POST.get('end_date') or None
        project.status      = request.POST.get('status', project.status)
        project.save()
        project.members.set(request.POST.getlist('members'))
        messages.success(request, f'✅ Project "{project.name}" updated!')
        return redirect('project_detail', pk=project.pk)

    return render(request, 'employees/project_form.html', {
        'project':     project,
        'departments': departments,
        'employees':   employees,
        'is_edit':     True,
    })


@login_required
def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related('department', 'manager').prefetch_related('members'), pk=pk
    )
    current_emp = Employee.objects.filter(user=request.user).first()

    # Members can see each other + the project; anyone else on the admin
    # side can view read-only, but only managers can edit/delete.
    return render(request, 'employees/project_detail.html', {
        'project':             project,
        'team_members':        project.members.select_related('department', 'designation').all(),
        'can_manage_projects': can_manage_projects(current_emp),
    })


@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    current_emp = Employee.objects.filter(user=request.user).first()
    if not can_manage_projects(current_emp):
        messages.error(request, 'You do not have permission to delete projects.')
        return redirect('project_detail', pk=pk)

    if request.method == 'POST':
        name = project.name
        project.delete()
        messages.success(request, f'🗑️ Project "{name}" deleted.')
        return redirect('project_list')
    return redirect('project_detail', pk=pk)


# employees/views.py — FILE KE END ME add karo

# ── Announcements (Super Admin only — High/Medium/Low, auto-expire in 24h) ──────
from django.http import JsonResponse


# employees/views.py — announcement_list() function ke andar, ye line replace karo

@login_required
def announcement_list(request):
    Announcement.objects.cleanup_expired()

    current_emp = Employee.objects.filter(user=request.user).first()
    is_allowed = request.user.is_superuser or is_super_admin(current_emp)   # 👈 CHANGED

    if not is_allowed:                                                      # 👈 CHANGED
        messages.error(request, 'Only the Super Admin can manage announcements.')
        return redirect('dashboard')

    announcements = Announcement.objects.active().select_related('created_by')

    if request.method == 'POST':
        title    = request.POST.get('title', '').strip()
        message  = request.POST.get('message', '').strip()
        priority = request.POST.get('priority', 'medium')

        if not title or not message:
            messages.error(request, 'Title and message are required.')
        else:
            announcement = Announcement.objects.create(
                title=title, message=message, priority=priority, created_by=current_emp,
            )
            notify_all_of_announcement(announcement)
            messages.success(request, f'📢 Announcement posted — it will auto-expire in 24 hours.')
            return redirect('announcement_list')

    return render(request, 'employees/announcements_list.html', {
        'announcements': announcements,
    })


@login_required
def delete_announcement(request, pk):
    current_emp = Employee.objects.filter(user=request.user).first()
    is_allowed = request.user.is_superuser or is_super_admin(current_emp)   # 👈 CHANGED

    if not is_allowed:                                                      # 👈 CHANGED
        messages.error(request, 'Only the Super Admin can manage announcements.')
        return redirect('announcement_list')

    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'Announcement removed.')
    return redirect('announcement_list')




@login_required
def announcement_detail_json(request, pk):
    """Powers the click-to-popup on a notification (admin side)."""
    Announcement.objects.cleanup_expired()
    announcement = get_object_or_404(Announcement, pk=pk)
    return JsonResponse({
        'title':      announcement.title,
        'message':    announcement.message,
        'priority':   announcement.priority,
        'priority_display': announcement.get_priority_display(),
        'created_by': announcement.created_by.full_name if announcement.created_by else 'Admin',
        'created_at': announcement.created_at.strftime('%d %b %Y, %I:%M %p'),
        'expires_at': announcement.expires_at.strftime('%d %b %Y, %I:%M %p'),
    })



# ============================================================================






# @login_required
# def dashboard(request):
#     if not request.user.is_authenticated:
#         return redirect('/admin-login/')

#     if not (request.user.is_staff or request.user.is_superuser):
#         return redirect('/portal/')

#     today            = date.today()
#     total_employees  = Employee.objects.filter(status='active').count()
#     today_present    = AttendanceRecord.objects.filter(
#         date=today,
#         status__in=['present', 'late', 'work_from_home']
#     ).count()
#     pending_leaves   = LeaveRequest.objects.filter(status='pending').count()
#     departments      = Department.objects.annotate(
#         emp_count=Count('employees', filter=Q(employees__status='active'))
#     )
#     recent_employees = Employee.objects.filter(
#         status='active'
#     ).order_by('-date_joined')[:5]
#     recent_leaves    = LeaveRequest.objects.filter(
#         status='pending'
#     ).order_by('-created_at')[:5]

#     current_emp   = Employee.objects.filter(user=request.user).first()
#     is_weekend    = today.weekday() in (5, 6)
#     today_holiday = Holiday.objects.filter(date=today).first()
#     is_working_day = not is_weekend and not today_holiday

#     absent_today   = Employee.objects.none()
#     on_leave_today = Employee.objects.none()
#     is_super_admin = bool(current_emp and current_emp.is_primary_admin)

#     if is_working_day:
#         active_employees = Employee.objects.filter(status='active')
#         if not is_super_admin and current_emp and current_emp.team_members.exists():
#             active_employees = active_employees.filter(
#                 Q(reporting_manager=current_emp) | Q(id=current_emp.id)
#             )

#         present_ids = AttendanceRecord.objects.filter(
#             date=today, status__in=['present', 'late', 'work_from_home', 'half_day']
#         ).values_list('employee_id', flat=True)

#         on_leave_today = active_employees.filter(
#             leave_requests__status='approved',
#             leave_requests__start_date__lte=today,
#             leave_requests__end_date__gte=today,
#         ).distinct()

#         absent_today = active_employees.exclude(
#             id__in=present_ids
#         ).exclude(
#             id__in=on_leave_today.values_list('id', flat=True)
#         ).distinct()

#     # ------------------------------------------------------------------
#     # <<< NAYA CODE — sirf super admin ke liye extra analytics juta rahe >>>
#     # ------------------------------------------------------------------
#     analytics = {}
#     if is_super_admin or request.user.is_superuser:
#         analytics = get_dashboard_analytics(
#             today=today,
#             present_count=today_present,
#             total_employees=total_employees,
#         )
#     # ------------------------------------------------------------------

#     return render(request, 'dashboard/index.html', {
#         'total_employees':  total_employees,
#         'today_present':    today_present,
#         'pending_leaves':   pending_leaves,
#         'departments':      departments,
#         'recent_employees': recent_employees,
#         'recent_leaves':    recent_leaves,
#         'today':            today,
#         'is_working_day':   is_working_day,
#         'today_holiday':    today_holiday,
#         'absent_today':     absent_today,
#         'on_leave_today':   on_leave_today,
#         'is_super_admin':   is_super_admin,
#         'can_manage_projects': can_manage_projects(current_emp),

#         # <<< NAYE CONTEXT VARIABLES — template mein inhi naamon se use honge >>>
#         'late_today':      analytics.get('late_today'),
#         'attendance_pct':  analytics.get('attendance_pct'),
#         'payroll_cost':    analytics.get('payroll_cost'),
#         'attrition':       analytics.get('attrition'),
#         'overtime':        analytics.get('overtime'),
#         'leave_trends':    analytics.get('leave_trends'),
#     })

@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('/admin-login/')

    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('/portal/')

    today            = date.today()
    total_employees  = Employee.objects.filter(status='active').count()
    today_present    = AttendanceRecord.objects.filter(
        date=today,
        status__in=['present', 'late', 'work_from_home']
    ).count()
    pending_leaves   = LeaveRequest.objects.filter(status='pending').count()
    departments      = Department.objects.annotate(
        emp_count=Count('employees', filter=Q(employees__status='active'))
    )
    recent_employees = Employee.objects.filter(
        status='active'
    ).order_by('-date_joined')[:5]
    recent_leaves    = LeaveRequest.objects.filter(
        status='pending'
    ).order_by('-created_at')[:5]

    current_emp   = Employee.objects.filter(user=request.user).first()
    is_weekend    = today.weekday() in (5, 6)
    today_holiday = Holiday.objects.filter(date=today).first()
    is_working_day = not is_weekend and not today_holiday

    absent_today   = Employee.objects.none()
    on_leave_today = Employee.objects.none()
    is_super_admin = bool(current_emp and current_emp.is_primary_admin)

    if is_working_day:
        active_employees = Employee.objects.filter(status='active')
        if not is_super_admin and current_emp and current_emp.team_members.exists():
            active_employees = active_employees.filter(
                Q(reporting_manager=current_emp) | Q(id=current_emp.id)
            )

        present_ids = AttendanceRecord.objects.filter(
            date=today, status__in=['present', 'late', 'work_from_home', 'half_day']
        ).values_list('employee_id', flat=True)

        on_leave_today = active_employees.filter(
            leave_requests__status='approved',
            leave_requests__start_date__lte=today,
            leave_requests__end_date__gte=today,
        ).distinct()

        absent_today = active_employees.exclude(
            id__in=present_ids
        ).exclude(
            id__in=on_leave_today.values_list('id', flat=True)
        ).distinct()

    # ------------------------------------------------------------------
    # <<< sirf super admin ke liye extra analytics >>>
    # ------------------------------------------------------------------
    analytics = {}
    if is_super_admin or request.user.is_superuser:
        analytics = get_dashboard_analytics(
            today=today,
            present_count=today_present,
            total_employees=total_employees,
        )
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # <<< Attendance Overview chart — sab staff ke liye (super admin tak
    #     limited nahi), week/month toggle GET param se control hota hai >>>
    # ------------------------------------------------------------------
    attendance_range = request.GET.get('attendance_range', 'week')
    if attendance_range not in ('week', 'month'):
        attendance_range = 'week'

    attendance_data = get_attendance_overview(range_key=attendance_range, today=today)
    attendance_range_label = get_attendance_range_label(attendance_range)
    # ------------------------------------------------------------------

    return render(request, 'dashboard/index.html', {
        'total_employees':  total_employees,
        'today_present':    today_present,
        'pending_leaves':   pending_leaves,
        'departments':      departments,
        'recent_employees': recent_employees,
        'recent_leaves':    recent_leaves,
        'today':            today,
        'is_working_day':   is_working_day,
        'today_holiday':    today_holiday,
        'absent_today':     absent_today,
        'on_leave_today':   on_leave_today,
        'is_super_admin':   is_super_admin,
        'can_manage_projects': can_manage_projects(current_emp),

        # <<< Attendance Overview chart ke liye >>>
        'attendance_data':        attendance_data,
        'attendance_range':       attendance_range,
        'attendance_range_label': attendance_range_label,

        # <<< super-admin analytics >>>
        'late_today':      analytics.get('late_today'),
        'attendance_pct':  analytics.get('attendance_pct'),
        'payroll_cost':    analytics.get('payroll_cost'),
        'attrition':       analytics.get('attrition'),
        'overtime':        analytics.get('overtime'),
        'leave_trends':    analytics.get('leave_trends'),
    })