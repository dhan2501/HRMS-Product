from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
import calendar
from datetime import date
from employees.models import Employee
from .models import LeaveType, LeaveBalance, LeaveRequest


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

from employees.models import Employee

def get_current_employee(request):
    try:
        return Employee.objects.select_related('department', 'role').get(user=request.user)
    except:
        return None

def is_manager_or_above(employee):
    """HR, PMO, CEO, Team Lead, Super Admin check."""
    if not employee:
        return False
    if employee.user.is_superuser or employee.user.is_staff:
        return True
    try:
        return employee.role.can_approve_leave
    except:
        return False


@login_required
def leave_requests(request):
    current_emp = get_current_employee(request)

    # ✅ Super admin / HR / Manager — saare leaves dekhe
    if request.user.is_superuser or request.user.is_staff or is_manager_or_above(current_emp):
        leaves = LeaveRequest.objects.select_related(
            'employee', 'leave_type', 'approved_by'
        ).order_by('-created_at')
    else:
        # ✅ Normal employee — SIRF APNA
        if current_emp:
            leaves = LeaveRequest.objects.filter(
                employee=current_emp
            ).select_related('leave_type').order_by('-created_at')
        else:
            leaves = LeaveRequest.objects.none()

    # Filters
    status_filter = request.GET.get('status', '')
    search        = request.GET.get('search', '')
    if status_filter:
        leaves = leaves.filter(status=status_filter)
    if search and (request.user.is_staff or request.user.is_superuser):
        leaves = leaves.filter(
            Q(employee__first_name__icontains=search) |
            Q(employee__last_name__icontains=search)
        )

    pending  = LeaveRequest.objects.filter(status='pending').count() if request.user.is_staff else leaves.filter(status='pending').count()
    approved = leaves.filter(status='approved').count()
    rejected = leaves.filter(status='rejected').count()
    total    = leaves.count()

    return render(request, 'leaves/requests.html', {
        'leaves':        leaves,
        'pending':       pending,
        'approved':      approved,
        'rejected':      rejected,
        'total':         total,
        'status_filter': status_filter,
        'search':        search,
        'is_manager':    request.user.is_staff or is_manager_or_above(current_emp),
    })


# ── Leave Requests List ───────────────────────────────────────────────────────
@login_required
def leave_requests(request):
    status_filter = request.GET.get('status', '')
    search        = request.GET.get('search', '')

    leaves = LeaveRequest.objects.select_related(
        'employee', 'leave_type', 'approved_by'
    ).order_by('-created_at')

    if status_filter:
        leaves = leaves.filter(status=status_filter)
    if search:
        leaves = leaves.filter(
            Q(employee__first_name__icontains=search) |
            Q(employee__last_name__icontains=search)
        )

    pending  = LeaveRequest.objects.filter(status='pending').count()
    approved = LeaveRequest.objects.filter(status='approved').count()
    rejected = LeaveRequest.objects.filter(status='rejected').count()
    total    = LeaveRequest.objects.count()

    return render(request, 'leaves/requests.html', {
        'leaves':        leaves,
        'pending':       pending,
        'approved':      approved,
        'rejected':      rejected,
        'total':         total,
        'status_filter': status_filter,
        'search':        search,
    })


# ── Apply Leave ───────────────────────────────────────────────────────────────
@login_required
def apply_leave(request):
    employees   = Employee.objects.filter(status='active').order_by('first_name')
    leave_types = LeaveType.objects.all()

    if request.method == 'POST':
        emp_id      = request.POST.get('employee')
        lt_id       = request.POST.get('leave_type')
        start_date  = request.POST.get('start_date')
        end_date    = request.POST.get('end_date')
        reason      = request.POST.get('reason', '').strip()

        if not all([emp_id, lt_id, start_date, end_date, reason]):
            messages.error(request, 'All fields are required.')
        else:
            from datetime import datetime
            s = datetime.strptime(start_date, '%Y-%m-%d').date()
            e = datetime.strptime(end_date, '%Y-%m-%d').date()

            if e < s:
                messages.error(request, 'End date cannot be before start date.')
            else:
                days = (e - s).days + 1
                employee   = get_object_or_404(Employee, pk=emp_id)
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
                messages.success(request, f'Leave request for {employee.full_name} submitted successfully!')
                return redirect('leave_requests')

    return render(request, 'leaves/apply.html', {
        'employees':   employees,
        'leave_types': leave_types,
    })


# ── Approve Leave ─────────────────────────────────────────────────────────────
@login_required
def approve_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        leave.status      = 'approved'
        leave.approved_at = timezone.now()
        leave.save()
        messages.success(request, f'Leave approved for {leave.employee.full_name}.')
    return redirect('leave_requests')


# ── Reject Leave ──────────────────────────────────────────────────────────────
@login_required
def reject_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        reason = request.POST.get('rejection_reason', '').strip()
        leave.status           = 'rejected'
        leave.rejection_reason = reason
        leave.save()
        messages.success(request, f'Leave rejected for {leave.employee.full_name}.')
    return redirect('leave_requests')


# ── Cancel Leave ──────────────────────────────────────────────────────────────
@login_required
def cancel_leave(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        leave.status = 'cancelled'
        leave.save()
        messages.success(request, 'Leave request cancelled.')
    return redirect('leave_requests')


# ── Leave Types ───────────────────────────────────────────────────────────────
@login_required
def leave_types(request):
    types = LeaveType.objects.all()
    return render(request, 'leaves/types.html', {'types': types})


# ── Add Leave Type ────────────────────────────────────────────────────────────
@login_required
def add_leave_type(request):
    if request.method == 'POST':
        name         = request.POST.get('name', '').strip()
        code         = request.POST.get('code', '').strip().upper()
        days_allowed = request.POST.get('days_allowed', 0)
        is_paid      = request.POST.get('is_paid') == 'on'
        carry_forward = request.POST.get('carry_forward') == 'on'
        max_cf_days  = request.POST.get('max_carry_forward_days', 0)
        description  = request.POST.get('description', '').strip()

        if not name or not code:
            messages.error(request, 'Name and Code are required.')
        elif LeaveType.objects.filter(code=code).exists():
            messages.error(request, f'Code "{code}" already exists.')
        else:
            LeaveType.objects.create(
                name=name, code=code,
                days_allowed=days_allowed,
                is_paid=is_paid,
                carry_forward=carry_forward,
                max_carry_forward_days=max_cf_days,
                description=description,
            )
            messages.success(request, f'Leave type "{name}" created!')
            return redirect('leave_types')

    return render(request, 'leaves/add_type.html')


# ── Edit Leave Type ───────────────────────────────────────────────────────────
@login_required
def edit_leave_type(request, pk):
    lt = get_object_or_404(LeaveType, pk=pk)

    if request.method == 'POST':
        lt.name                  = request.POST.get('name', '').strip()
        lt.code                  = request.POST.get('code', '').strip().upper()
        lt.days_allowed          = request.POST.get('days_allowed', 0)
        lt.is_paid               = request.POST.get('is_paid') == 'on'
        lt.carry_forward         = request.POST.get('carry_forward') == 'on'
        lt.max_carry_forward_days = request.POST.get('max_carry_forward_days', 0)
        lt.description           = request.POST.get('description', '').strip()
        lt.save()
        messages.success(request, f'Leave type "{lt.name}" updated!')
        return redirect('leave_types')

    return render(request, 'leaves/add_type.html', {'lt': lt, 'is_edit': True})


# ── Delete Leave Type ─────────────────────────────────────────────────────────
@login_required
def delete_leave_type(request, pk):
    lt = get_object_or_404(LeaveType, pk=pk)
    if request.method == 'POST':
        lt.delete()
        messages.success(request, f'Leave type deleted.')
    return redirect('leave_types')


# ── Leave Reports ─────────────────────────────────────────────────────────────
@login_required
def leave_reports(request):
    today = date.today()
    month = int(request.GET.get('month', today.month))
    year  = int(request.GET.get('year', today.year))

    leaves = LeaveRequest.objects.filter(
        start_date__month=month,
        start_date__year=year,
    ).select_related('employee', 'leave_type')

    by_type = {}
    for lt in LeaveType.objects.all():
        by_type[lt.name] = leaves.filter(leave_type=lt).count()

    return render(request, 'leaves/reports.html', {
        'leaves':     leaves,
        'by_type':    by_type,
        'month':      month,
        'year':       year,
        'month_name': calendar.month_name[month],
        'total':      leaves.count(),
        'approved':   leaves.filter(status='approved').count(),
        'pending':    leaves.filter(status='pending').count(),
        'rejected':   leaves.filter(status='rejected').count(),
    })