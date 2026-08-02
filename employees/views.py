# # from django.shortcuts import render, get_object_or_404, redirect
# # from django.contrib.auth.decorators import login_required
# # from django.contrib import messages
# # from django.db.models import Count, Q
# # from django import forms
# # from .models import Employee, Department, Designation
# # from attendance.models import AttendanceRecord
# # from leaves.models import LeaveRequest
# # from datetime import date

# # from django.contrib.auth.decorators import login_required
# # from django.core.exceptions import PermissionDenied


# # from django.shortcuts import render, get_object_or_404, redirect
# # from django.contrib.auth.decorators import login_required
# # from django.contrib import messages
# # from django.db.models import Count, Q
# # from django import forms
# # from functools import wraps
# # from .models import Employee, Department, Designation
# # from attendance.models import AttendanceRecord
# # from leaves.models import LeaveRequest
# # from datetime import date

# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.db.models import Count, Q
# from django import forms
# from functools import wraps
# from .models import Employee, Department, Designation, EmployeeStatusLog
# from attendance.models import AttendanceRecord
# from leaves.models import LeaveRequest
# from datetime import date
# from django.utils import timezone



# # def admin_required(view_func):
# #     """Sirf staff/superadmin access kar sake."""
# #     @wraps(view_func)
# #     def wrapper(request, *args, **kwargs):
# #         if not request.user.is_authenticated:
# #             return redirect('admin_login')
# #         if not (request.user.is_staff or request.user.is_superuser):
# #             try:
# #                 Employee.objects.get(user=request.user)
# #                 return redirect('portal_dashboard')
# #             except Employee.DoesNotExist:
# #                 return redirect('employee_login')
# #         return view_func(request, *args, **kwargs)
# #     return wrapper

# def admin_required(view_func):
#     @wraps(view_func)
#     def wrapper(request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return redirect('admin_login')  # employee-login nahi
#         if request.user.is_staff or request.user.is_superuser:
#             return view_func(request, *args, **kwargs)
#         # Employee ko portal pe bhejo — dashboard nahi dikhega
#         try:
#             Employee.objects.get(user=request.user)
#             return redirect('portal_dashboard')
#         except Employee.DoesNotExist:
#             return redirect('employee_login')
#     return wrapper


# # ── Form ────────────────────────────────────────────────────────────────────
# class EmployeeForm(forms.ModelForm):
#     class Meta:
#         model = Employee
#         fields = [
#             'employee_id', 'first_name', 'last_name', 'email', 'phone',
#             'date_of_birth', 'gender', 'photo',
#             'department', 'designation', 'date_joined',
#             'employment_type', 'status',
#             'address', 'emergency_contact_name', 'emergency_contact_phone',
#         ]
#         widgets = {
#             'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
#             'date_joined':   forms.DateInput(attrs={'type': 'date'}),
#             'address':       forms.Textarea(attrs={'rows': 3}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Required fields
#         self.fields['employee_id'].required = True
#         self.fields['first_name'].required  = True
#         self.fields['last_name'].required   = True
#         self.fields['email'].required       = True
#         self.fields['date_joined'].required = True
#         self.fields['department'].required  = True
#         # Optional fields
#         self.fields['phone'].required                  = False
#         self.fields['date_of_birth'].required          = False
#         self.fields['gender'].required                 = False
#         self.fields['photo'].required                  = False
#         self.fields['designation'].required            = False
#         self.fields['address'].required                = False
#         self.fields['emergency_contact_name'].required = False
#         self.fields['emergency_contact_phone'].required= False
#         self.fields['designation'].queryset = Designation.objects.select_related('department').all()


# # ── Dashboard ────────────────────────────────────────────────────────────────
# # @login_required
# # def dashboard(request):
# #     today = date.today()
# #     total_employees = Employee.objects.filter(status='active').count()
# #     today_present   = AttendanceRecord.objects.filter(
# #         date=today, status__in=['present', 'late', 'work_from_home']
# #     ).count()
# #     pending_leaves  = LeaveRequest.objects.filter(status='pending').count()
# #     departments     = Department.objects.annotate(
# #         emp_count=Count('employees', filter=Q(employees__status='active'))
# #     )
# #     recent_employees = Employee.objects.filter(status='active').order_by('-date_joined')[:5]
# #     recent_leaves    = LeaveRequest.objects.filter(status='pending').order_by('-created_at')[:5]

# #     return render(request, 'dashboard/index.html', {
# #         'total_employees': total_employees,
# #         'today_present':   today_present,
# #         'pending_leaves':  pending_leaves,
# #         'departments':     departments,
# #         'recent_employees': recent_employees,
# #         'recent_leaves':   recent_leaves,
# #         'today':           today,
# #     })



# # from django.db.models import Count, Q


# # @login_required
# # def dashboard(request):

# #     # Employee ko admin dashboard access na do
# #     if not request.user.is_staff:
# #         return redirect('/portal/')

# #     # Agar custom User model me role field hai to ye check rakho
# #     if hasattr(request.user, "role"):
# #         if request.user.role not in ["SUPER_ADMIN", "HR"]:
# #             return redirect('/portal/')

# #     today = date.today()

# #     total_employees = Employee.objects.filter(status='active').count()

# #     today_present = AttendanceRecord.objects.filter(
# #         date=today,
# #         status__in=['present', 'late', 'work_from_home']
# #     ).count()

# #     pending_leaves = LeaveRequest.objects.filter(
# #         status='pending'
# #     ).count()

# #     departments = Department.objects.annotate(
# #         emp_count=Count(
# #             'employees',
# #             filter=Q(employees__status='active')
# #         )
# #     )

# #     recent_employees = Employee.objects.filter(
# #         status='active'
# #     ).order_by('-date_joined')[:5]

# #     recent_leaves = LeaveRequest.objects.filter(
# #         status='pending'
# #     ).order_by('-created_at')[:5]

# #     return render(request, 'dashboard/index.html', {
# #         'total_employees': total_employees,
# #         'today_present': today_present,
# #         'pending_leaves': pending_leaves,
# #         'departments': departments,
# #         'recent_employees': recent_employees,
# #         'recent_leaves': recent_leaves,
# #         'today': today,
# #     })


# # new code


# from django.db.models import Count, Q



# @login_required
# def dashboard(request):
#     # ── Access Control ─────────────────────────────────────────────
#     # Sirf superadmin ya staff access kar sakta hai
#     # Employee ko portal pe redirect karo
#     if not request.user.is_authenticated:
#         return redirect('/admin-login/')

#     if not (request.user.is_staff or request.user.is_superuser):
#         return redirect('/portal/')

#     # ── Dashboard Data ─────────────────────────────────────────────
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

# # ── Employee List ─────────────────────────────────────────────────────────────
# @login_required
# def employee_list(request):
#     employees   = Employee.objects.select_related('department', 'designation').all()
#     departments = Department.objects.all()

#     dept_filter   = request.GET.get('department')
#     status_filter = request.GET.get('status')
#     search        = request.GET.get('search', '')

#     if dept_filter:
#         employees = employees.filter(department_id=dept_filter)
#     if status_filter:
#         employees = employees.filter(status=status_filter)
#     if search:
#         employees = employees.filter(
#             Q(first_name__icontains=search)  |
#             Q(last_name__icontains=search)   |
#             Q(employee_id__icontains=search)
#         )

#     return render(request, 'employees/list.html', {
#         'employees':   employees,
#         'departments': departments,
#     })


# # ── Add Employee ──────────────────────────────────────────────────────────────
# # @login_required
# # def add_employee(request):
# #     departments  = Department.objects.all()
# #     designations = Designation.objects.select_related('department').all()

# #     if request.method == 'POST':
# #         form = EmployeeForm(request.POST, request.FILES)
# #         if form.is_valid():
# #             employee = form.save()
# #             messages.success(
# #                 request,
# #                 f'✅ Employee {employee.full_name} ({employee.employee_id}) added successfully!'
# #             )
# #             return redirect('employee_list')
# #         else:
# #             messages.error(request, '❌ Please fix the errors below.')
# #     else:
# #         form = EmployeeForm()

# #     return render(request, 'employees/add.html', {
# #         'form':         form,
# #         'departments':  departments,
# #         'designations': designations,
# #     })

# @login_required
# def add_employee(request):
#     departments  = Department.objects.all()
#     designations = Designation.objects.select_related('department').all()

#     if request.method == 'POST':
#         form = EmployeeForm(request.POST, request.FILES)
#         if form.is_valid():
#             employee = form.save()

#             # Auto-create login credentials
#             from employees.auth_views import create_employee_user
#             user, username, password = create_employee_user(employee)

#             if username:
#                 messages.success(
#                     request,
#                     f'✅ Employee {employee.full_name} added! '
#                     f'Login: Username = "{username}" | Password = "{password}"'
#                 )
#             else:
#                 messages.success(request, f'✅ Employee {employee.full_name} added!')

#             return redirect('employee_list')
#         else:
#             messages.error(request, 'Please fix the errors below.')
#     else:
#         form = EmployeeForm()

#     return render(request, 'employees/add.html', {
#         'form':         form,
#         'departments':  departments,
#         'designations': designations,
#     })

# # ── Edit Employee ─────────────────────────────────────────────────────────────
# @login_required
# def edit_employee(request, pk):
#     employee     = get_object_or_404(Employee, pk=pk)
#     departments  = Department.objects.all()
#     designations = Designation.objects.select_related('department').all()

#     if request.method == 'POST':
#         form = EmployeeForm(request.POST, request.FILES, instance=employee)
#         if form.is_valid():
#             form.save()
#             messages.success(request, f'✅ {employee.full_name} updated successfully!')
#             return redirect('employee_detail', pk=pk)
#         else:
#             messages.error(request, '❌ Please fix the errors below.')
#     else:
#         form = EmployeeForm(instance=employee)

#     return render(request, 'employees/add.html', {
#         'form':         form,
#         'employee':     employee,
#         'departments':  departments,
#         'designations': designations,
#         'is_edit':      True,
#     })


# # ── Employee Detail ───────────────────────────────────────────────────────────
# # @login_required
# # def employee_detail(request, pk):
# #     employee = get_object_or_404(Employee, pk=pk)
# #     return render(request, 'employees/detail.html', {'employee': employee})

# # ── Employee Detail ───────────────────────────────────────────────────────────
# @login_required
# def employee_detail(request, pk):
#     employee = get_object_or_404(Employee, pk=pk)
#     status_logs = employee.status_logs.select_related('changed_by')[:10]
#     return render(request, 'employees/detail.html', {
#         'employee': employee,
#         'status_logs': status_logs,
#     })


# # ── Deactivate / Hold / Reactivate Employee ─────────────────────────────────────
# @login_required
# def update_employee_status(request, pk):
#     """
#     HR/Admin-only action to deactivate an employee (resigned/left the
#     company), put them on hold (long leave — 6 months, 1 year, etc. with
#     an expected return date), terminate them, or reactivate them.
#     Every change is written to EmployeeStatusLog with a mandatory reason,
#     so there is always a record of why and when the status changed.
#     """
#     if not (request.user.is_staff or request.user.is_superuser):
#         messages.error(request, 'You do not have permission to change employee status.')
#         return redirect('employee_detail', pk=pk)

#     employee = get_object_or_404(Employee, pk=pk)

#     if request.method == 'POST':
#         new_status = request.POST.get('new_status', '').strip()
#         reason     = request.POST.get('reason', '').strip()
#         hold_until = request.POST.get('hold_until', '').strip() or None

#         valid_statuses = dict(Employee.STATUS_CHOICES)
#         if new_status not in valid_statuses:
#             messages.error(request, 'Invalid status selected.')
#             return redirect('employee_detail', pk=pk)

#         if not reason:
#             messages.error(request, 'A reason is required to change employee status.')
#             return redirect('employee_detail', pk=pk)

#         if new_status == 'on_leave' and not hold_until:
#             messages.error(request, 'Please provide an expected return date for "On Leave / Hold".')
#             return redirect('employee_detail', pk=pk)

#         previous_status = employee.status

#         # Log the change first (keeps a full audit trail)
#         EmployeeStatusLog.objects.create(
#             employee=employee,
#             previous_status=previous_status,
#             new_status=new_status,
#             reason=reason,
#             hold_until=hold_until if new_status == 'on_leave' else None,
#             changed_by=request.user,
#         )

#         # Apply the change
#         employee.status = new_status
#         employee.status_reason = reason
#         employee.status_changed_at = timezone.now()
#         employee.hold_until = hold_until if new_status == 'on_leave' else None
#         employee.save()

#         # Deactivating/terminating an employee also locks their portal login;
#         # reactivating restores it.
#         if employee.user:
#             employee.user.is_active = (new_status not in ('inactive', 'terminated'))
#             employee.user.save(update_fields=['is_active'])

#         status_labels = {
#             'active':     'reactivated',
#             'inactive':   'deactivated',
#             'on_leave':   'put on hold / long leave',
#             'terminated': 'terminated',
#         }
#         messages.success(
#             request,
#             f'{employee.full_name} has been {status_labels.get(new_status, "updated")}.'
#         )

#     return redirect('employee_detail', pk=pk)


# # ── Department List ───────────────────────────────────────────────────────────
# @login_required
# def department_list(request):
#     departments = Department.objects.annotate(
#         emp_count=Count('employees', filter=Q(employees__status='active'))
#     )
#     return render(request, 'employees/departments.html', {'departments': departments})


# # ── Add Department ────────────────────────────────────────────────────────────
# @login_required
# def add_department(request):
#     if request.method == 'POST':
#         name        = request.POST.get('name', '').strip()
#         code        = request.POST.get('code', '').strip().upper()
#         description = request.POST.get('description', '').strip()

#         if not name or not code:
#             messages.error(request, 'Department name and code are required.')
#         elif Department.objects.filter(name=name).exists():
#             messages.error(request, f'Department "{name}" already exists.')
#         elif Department.objects.filter(code=code).exists():
#             messages.error(request, f'Code "{code}" already used.')
#         else:
#             Department.objects.create(name=name, code=code, description=description)
#             messages.success(request, f'Department "{name}" added successfully!')
#             return redirect('department_list')

#     return render(request, 'employees/add_department.html')


# # ── Edit Department ───────────────────────────────────────────────────────────
# @login_required
# def edit_department(request, pk):
#     dept = get_object_or_404(Department, pk=pk)

#     if request.method == 'POST':
#         name        = request.POST.get('name', '').strip()
#         code        = request.POST.get('code', '').strip().upper()
#         description = request.POST.get('description', '').strip()

#         if not name or not code:
#             messages.error(request, 'Name and code are required.')
#         elif Department.objects.filter(name=name).exclude(pk=pk).exists():
#             messages.error(request, f'Department "{name}" already exists.')
#         elif Department.objects.filter(code=code).exclude(pk=pk).exists():
#             messages.error(request, f'Code "{code}" already used.')
#         else:
#             dept.name        = name
#             dept.code        = code
#             dept.description = description
#             dept.save()
#             messages.success(request, f'Department "{name}" updated!')
#             return redirect('department_list')

#     return render(request, 'employees/add_department.html', {'dept': dept})


# # ── Delete Department ─────────────────────────────────────────────────────────
# @login_required
# def delete_department(request, pk):
#     dept = get_object_or_404(Department, pk=pk)
#     if request.method == 'POST':
#         name = dept.name
#         dept.delete()
#         messages.success(request, f'Department "{name}" deleted.')
#     return redirect('department_list')

# # ── Designation List ──────────────────────────────────────────────────────────
# @login_required
# def designation_list(request):
#     designations = Designation.objects.select_related('department').all()
#     return render(request, 'employees/designations.html', {'designations': designations})

# # ── Add Designation ───────────────────────────────────────────────────────────
# @login_required
# def add_designation(request):
#     departments = Department.objects.all()

#     if request.method == 'POST':
#         title      = request.POST.get('title', '').strip()
#         dept_id    = request.POST.get('department')
#         level      = request.POST.get('level', 1)

#         if not title or not dept_id:
#             messages.error(request, 'Title and Department are required.')
#         elif Designation.objects.filter(title=title).exists():
#             messages.error(request, f'Designation "{title}" already exists.')
#         else:
#             dept = get_object_or_404(Department, pk=dept_id)
#             Designation.objects.create(title=title, department=dept, level=level)
#             messages.success(request, f'Designation "{title}" added successfully!')
#             return redirect('designation_list')

#     return render(request, 'employees/add_designation.html', {
#         'departments': departments,
#     })


# # ── Edit Designation ──────────────────────────────────────────────────────────
# @login_required
# def edit_designation(request, pk):
#     designation = get_object_or_404(Designation, pk=pk)
#     departments = Department.objects.all()

#     if request.method == 'POST':
#         title   = request.POST.get('title', '').strip()
#         dept_id = request.POST.get('department')
#         level   = request.POST.get('level', 1)

#         if not title or not dept_id:
#             messages.error(request, 'Title and Department are required.')
#         elif Designation.objects.filter(title=title).exclude(pk=pk).exists():
#             messages.error(request, f'Designation "{title}" already exists.')
#         else:
#             dept                = get_object_or_404(Department, pk=dept_id)
#             designation.title      = title
#             designation.department = dept
#             designation.level      = level
#             designation.save()
#             messages.success(request, f'Designation "{title}" updated!')
#             return redirect('designation_list')

#     return render(request, 'employees/add_designation.html', {
#         'designation': designation,
#         'departments': departments,
#         'is_edit':     True,
#     })


# # ── Delete Designation ────────────────────────────────────────────────────────
# @login_required
# def delete_designation(request, pk):
#     designation = get_object_or_404(Designation, pk=pk)
#     if request.method == 'POST':
#         title = designation.title
#         designation.delete()
#         messages.success(request, f'Designation "{title}" deleted.')
#     return redirect('designation_list')


# @login_required
# def add_employee(request):
#     departments  = Department.objects.all()
#     designations = Designation.objects.select_related('department').all()

#     if request.method == 'POST':
#         form = EmployeeForm(request.POST, request.FILES)
#         if form.is_valid():
#             employee = form.save()

#             # ✅ Auto username & password generate
#             from django.contrib.auth.models import User
#             first    = employee.first_name.lower().strip().replace(' ', '')
#             last     = employee.last_name.lower().strip().replace(' ', '')
#             username = f"{first}.{last}"

#             if User.objects.filter(username=username).exists():
#                 username = f"{first}.{employee.employee_id.lower()}"

#             password = f"{employee.first_name.capitalize()}@{employee.employee_id}"

#             user = User.objects.create_user(
#                 username=username,
#                 password=password,
#                 email=employee.email,
#                 first_name=employee.first_name,
#                 last_name=employee.last_name,
#                 is_staff=False,
#                 is_superuser=False,
#             )
#             employee.user = user
#             employee.save()

#             messages.success(
#                 request,
#                 f'✅ Employee added! Login — Username: "{username}" | Password: "{password}"'
#             )
#             return redirect('employee_list')
#         else:
#             messages.error(request, 'Please fix the errors below.')
#     else:
#         form = EmployeeForm()

#     return render(request, 'employees/add.html', {
#         'form':         form,
#         'departments':  departments,
#         'designations': designations,
#     })

# @login_required
# def employee_credentials(request):
#     """Admin page — all employees with login details."""
#     from django.contrib.auth.models import User

#     employees = Employee.objects.select_related(
#         'user', 'department', 'designation'
#     ).all().order_by('first_name')

#     return render(request, 'employees/credentials.html', {
#         'employees': employees,
#     })


# @login_required
# def create_employee_login(request, pk):
#     """Create login for employee who doesn't have one."""
#     from django.contrib.auth.models import User
#     employee = get_object_or_404(Employee, pk=pk)

#     if employee.user:
#         messages.warning(request, f'{employee.full_name} already has login: {employee.user.username}')
#         return redirect('employee_credentials')

#     first    = employee.first_name.lower().strip().replace(' ', '')
#     last     = employee.last_name.lower().strip().replace(' ', '')
#     username = f"{first}.{last}"

#     if User.objects.filter(username=username).exists():
#         username = f"{first}.{employee.employee_id.lower()}"

#     password = f"{employee.first_name.capitalize()}@{employee.employee_id}"

#     user = User.objects.create_user(
#         username=username,
#         password=password,
#         email=employee.email,
#         first_name=employee.first_name,
#         last_name=employee.last_name,
#         is_staff=False,
#         is_superuser=False,
#     )
#     employee.user = user
#     employee.save()

#     messages.success(
#         request,
#         f'✅ Login created for {employee.full_name} — Username: "{username}" | Password: "{password}"'
#     )
#     return redirect('employee_credentials')


# @login_required
# def create_all_logins(request):
#     """Bulk create logins for all employees without user."""
#     from django.contrib.auth.models import User

#     employees_no_user = Employee.objects.filter(user=None)
#     created = 0

#     for employee in employees_no_user:
#         first    = employee.first_name.lower().strip().replace(' ', '')
#         last     = employee.last_name.lower().strip().replace(' ', '')
#         username = f"{first}.{last}"

#         if User.objects.filter(username=username).exists():
#             username = f"{first}.{employee.employee_id.lower()}"

#         password = f"{employee.first_name.capitalize()}@{employee.employee_id}"

#         user = User.objects.create_user(
#             username=username,
#             password=password,
#             email=employee.email,
#             first_name=employee.first_name,
#             last_name=employee.last_name,
#             is_staff=False,
#             is_superuser=False,
#         )
#         employee.user = user
#         employee.save()
#         created += 1

#     messages.success(request, f'✅ {created} employee login(s) created successfully!')
#     return redirect('employee_credentials')


# @login_required  
# def reset_employee_password(request, pk):
#     """Reset password to default."""
#     employee = get_object_or_404(Employee, pk=pk)
    
#     if not employee.user:
#         messages.error(request, 'No login found for this employee.')
#         return redirect('employee_credentials')

#     password = f"{employee.first_name.capitalize()}@{employee.employee_id}"
#     employee.user.set_password(password)
#     employee.user.save()

#     messages.success(
#         request,
#         f'🔑 Password reset for {employee.full_name} — New Password: "{password}"'
#     )
#     return redirect('employee_credentials')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django import forms
from functools import wraps
from .models import (
    Employee, Department, Designation, EmployeeStatusLog,
    PerformanceReview, PerformanceGoal,
)
from attendance.models import AttendanceRecord
from leaves.models import LeaveRequest
from datetime import date
from django.utils import timezone


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
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'email', 'phone',
            'date_of_birth', 'gender', 'photo',
            'department', 'designation', 'reporting_manager', 'date_joined',
            'employment_type', 'status',
            'address', 'emergency_contact_name', 'emergency_contact_phone',
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
        self.fields['address'].required                = False
        self.fields['emergency_contact_name'].required = False
        self.fields['emergency_contact_phone'].required= False
        self.fields['designation'].queryset = Designation.objects.select_related('department').all()
        self.fields['reporting_manager'].required = False
        managers_qs = Employee.objects.filter(status='active').order_by('first_name', 'last_name')
        if self.instance and self.instance.pk:
            # An employee can't report to themselves
            managers_qs = managers_qs.exclude(pk=self.instance.pk)
        self.fields['reporting_manager'].queryset = managers_qs


# ── Dashboard ────────────────────────────────────────────────────────────────
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

    return render(request, 'dashboard/index.html', {
        'total_employees':  total_employees,
        'today_present':    today_present,
        'pending_leaves':   pending_leaves,
        'departments':      departments,
        'recent_employees': recent_employees,
        'recent_leaves':    recent_leaves,
        'today':            today,
    })

# ── Employee List ─────────────────────────────────────────────────────────────
@login_required
def employee_list(request):
    employees   = Employee.objects.select_related('department', 'designation').all()
    departments = Department.objects.all()

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
        'employees':   employees,
        'departments': departments,
    })


# ── Add Employee ──────────────────────────────────────────────────────────────
@login_required
def add_employee(request):
    departments  = Department.objects.all()
    designations = Designation.objects.select_related('department').all()

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
    })

# ── Edit Employee ─────────────────────────────────────────────────────────────
@login_required
def edit_employee(request, pk):
    employee     = get_object_or_404(Employee, pk=pk)
    departments  = Department.objects.all()
    designations = Designation.objects.select_related('department').all()

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