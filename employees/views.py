from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import Employee, Department, Designation
from attendance.models import AttendanceRecord
from leaves.models import LeaveRequest
from datetime import date


@login_required
def dashboard(request):
    today = date.today()
    total_employees = Employee.objects.filter(status='active').count()
    today_present = AttendanceRecord.objects.filter(date=today, status__in=['present', 'late', 'work_from_home']).count()
    pending_leaves = LeaveRequest.objects.filter(status='pending').count()
    departments = Department.objects.annotate(emp_count=Count('employees', filter=Q(employees__status='active')))
    recent_employees = Employee.objects.filter(status='active').order_by('-date_joined')[:5]
    recent_leaves = LeaveRequest.objects.filter(status='pending').order_by('-created_at')[:5]

    context = {
        'total_employees': total_employees,
        'today_present': today_present,
        'pending_leaves': pending_leaves,
        'departments': departments,
        'recent_employees': recent_employees,
        'recent_leaves': recent_leaves,
        'today': today,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def employee_list(request):
    employees = Employee.objects.select_related('department', 'designation').all()
    departments = Department.objects.all()
    dept_filter = request.GET.get('department')
    status_filter = request.GET.get('status')
    search = request.GET.get('search', '')
    if dept_filter:
        employees = employees.filter(department_id=dept_filter)
    if status_filter:
        employees = employees.filter(status=status_filter)
    if search:
        employees = employees.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(employee_id__icontains=search))
    return render(request, 'employees/list.html', {'employees': employees, 'departments': departments})


@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/detail.html', {'employee': employee})


@login_required
def department_list(request):
    departments = Department.objects.annotate(emp_count=Count('employees', filter=Q(employees__status='active')))
    return render(request, 'employees/departments.html', {'departments': departments})


@login_required
def designation_list(request):
    designations = Designation.objects.select_related('department').all()
    return render(request, 'employees/designations.html', {'designations': designations})
