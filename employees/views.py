from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django import forms
from .models import Employee, Department, Designation
from attendance.models import AttendanceRecord
from leaves.models import LeaveRequest
from datetime import date


# ── Form ────────────────────────────────────────────────────────────────────
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'email', 'phone',
            'date_of_birth', 'gender', 'photo',
            'department', 'designation', 'date_joined',
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
        # Required fields
        self.fields['employee_id'].required = True
        self.fields['first_name'].required  = True
        self.fields['last_name'].required   = True
        self.fields['email'].required       = True
        self.fields['date_joined'].required = True
        self.fields['department'].required  = True
        # Optional fields
        self.fields['phone'].required                  = False
        self.fields['date_of_birth'].required          = False
        self.fields['gender'].required                 = False
        self.fields['photo'].required                  = False
        self.fields['designation'].required            = False
        self.fields['address'].required                = False
        self.fields['emergency_contact_name'].required = False
        self.fields['emergency_contact_phone'].required= False
        self.fields['designation'].queryset = Designation.objects.select_related('department').all()


# ── Dashboard ────────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    today = date.today()
    total_employees = Employee.objects.filter(status='active').count()
    today_present   = AttendanceRecord.objects.filter(
        date=today, status__in=['present', 'late', 'work_from_home']
    ).count()
    pending_leaves  = LeaveRequest.objects.filter(status='pending').count()
    departments     = Department.objects.annotate(
        emp_count=Count('employees', filter=Q(employees__status='active'))
    )
    recent_employees = Employee.objects.filter(status='active').order_by('-date_joined')[:5]
    recent_leaves    = LeaveRequest.objects.filter(status='pending').order_by('-created_at')[:5]

    return render(request, 'dashboard/index.html', {
        'total_employees': total_employees,
        'today_present':   today_present,
        'pending_leaves':  pending_leaves,
        'departments':     departments,
        'recent_employees': recent_employees,
        'recent_leaves':   recent_leaves,
        'today':           today,
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
            messages.success(
                request,
                f'✅ Employee {employee.full_name} ({employee.employee_id}) added successfully!'
            )
            return redirect('employee_list')
        else:
            messages.error(request, '❌ Please fix the errors below.')
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
    return render(request, 'employees/detail.html', {'employee': employee})


# ── Department List ───────────────────────────────────────────────────────────
@login_required
def department_list(request):
    departments = Department.objects.annotate(
        emp_count=Count('employees', filter=Q(employees__status='active'))
    )
    return render(request, 'employees/departments.html', {'departments': departments})


# ── Designation List ──────────────────────────────────────────────────────────
@login_required
def designation_list(request):
    designations = Designation.objects.select_related('department').all()
    return render(request, 'employees/designations.html', {'designations': designations})