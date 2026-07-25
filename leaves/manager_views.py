from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from employees.models import Employee, EmployeeRole, Department
from .models import LeaveRequest, LeaveComment
from attendance.models import WorkFromHomeRequest


def get_manager_employee(request):
    try:
        emp = Employee.objects.select_related('role', 'department').get(user=request.user)
        return emp
    except Employee.DoesNotExist:
        return None


def has_leave_access(employee):
    """Check if employee can approve leaves."""
    try:
        return employee.role.can_approve_leave
    except:
        return employee.user.is_staff


def get_manageable_leaves(manager_emp):
    """Get leaves that this manager can approve."""
    try:
        role = manager_emp.role
    except:
        if manager_emp.user.is_staff:
            return LeaveRequest.objects.select_related(
                'employee', 'leave_type', 'employee__department'
            ).filter(status='pending').order_by('-created_at')
        return LeaveRequest.objects.none()

    if manager_emp.user.is_staff:
        # Super admin sees all
        return LeaveRequest.objects.select_related(
            'employee', 'leave_type', 'employee__department'
        ).filter(status='pending').order_by('-created_at')

    if role.role == 'ceo':
        # CEO sees all
        return LeaveRequest.objects.select_related(
            'employee', 'leave_type', 'employee__department'
        ).filter(status='pending').order_by('-created_at')

    elif role.manages_department:
        # Department head sees their dept
        return LeaveRequest.objects.select_related(
            'employee', 'leave_type', 'employee__department'
        ).filter(
            status='pending',
            employee__department=role.manages_department
        ).order_by('-created_at')

    return LeaveRequest.objects.none()


# ── Manager Leave Dashboard ───────────────────────────────────────────────────
@login_required
def manager_leave_dashboard(request):
    manager = get_manager_employee(request)
    if not manager:
        messages.error(request, 'Employee profile not found.')
        return redirect('dashboard')

    if not has_leave_access(manager):
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('dashboard')

    # Filters
    status_filter = request.GET.get('status', 'pending')
    dept_filter   = request.GET.get('department', '')
    search        = request.GET.get('search', '')

    try:
        role = manager.role
        is_ceo_or_admin = manager.user.is_staff or (hasattr(manager, 'role') and role.role == 'ceo')
    except:
        is_ceo_or_admin = manager.user.is_staff

    # Base queryset
    if is_ceo_or_admin:
        leaves = LeaveRequest.objects.select_related(
            'employee', 'leave_type', 'employee__department', 'employee__designation'
        ).all()
    else:
        try:
            managed_dept = manager.role.manages_department
            leaves = LeaveRequest.objects.select_related(
                'employee', 'leave_type', 'employee__department', 'employee__designation'
            ).filter(employee__department=managed_dept)
        except:
            leaves = LeaveRequest.objects.none()

    if status_filter:
        leaves = leaves.filter(status=status_filter)
    if dept_filter:
        leaves = leaves.filter(employee__department_id=dept_filter)
    if search:
        leaves = leaves.filter(
            Q(employee__first_name__icontains=search) |
            Q(employee__last_name__icontains=search)
        )

    leaves = leaves.order_by('-created_at')

    # Stats
    all_base = LeaveRequest.objects.all() if is_ceo_or_admin else leaves
    pending  = all_base.filter(status='pending').count() if is_ceo_or_admin else LeaveRequest.objects.filter(
        employee__department=manager.role.manages_department if hasattr(manager, 'role') and manager.role.manages_department else None,
        status='pending'
    ).count()

    departments = Department.objects.all() if is_ceo_or_admin else Department.objects.filter(id=manager.department_id)

    # WFH pending
    if is_ceo_or_admin:
        wfh_pending = WorkFromHomeRequest.objects.filter(status='pending').select_related('employee', 'employee__department').count()
    else:
        try:
            wfh_pending = WorkFromHomeRequest.objects.filter(
                status='pending',
                employee__department=manager.role.manages_department
            ).count()
        except:
            wfh_pending = 0

    return render(request, 'leaves/manager_dashboard.html', {
        'manager':        manager,
        'leaves':         leaves,
        'pending':        pending,
        'departments':    departments,
        'status_filter':  status_filter,
        'dept_filter':    dept_filter,
        'search':         search,
        'is_ceo_or_admin': is_ceo_or_admin,
        'wfh_pending':    wfh_pending,
    })


# ── Leave Detail + Comment ────────────────────────────────────────────────────
@login_required
def manager_leave_detail(request, pk):
    manager = get_manager_employee(request)
    if not manager or not has_leave_access(manager):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    leave    = get_object_or_404(LeaveRequest, pk=pk)
    comments = leave.comments.select_related('commented_by').all()

    if request.method == 'POST':
        action  = request.POST.get('action')
        comment = request.POST.get('comment', '').strip()

        if action in ['approved', 'rejected', 'comment']:
            # Save comment
            LeaveComment.objects.create(
                leave=leave,
                commented_by=manager,
                comment=comment or f"Leave {action} by {manager.full_name}",
                action=action,
            )

            # Update leave status
            if action == 'approved':
                leave.status      = 'approved'
                leave.approved_by = manager
                leave.approved_at = timezone.now()
                leave.save()
                messages.success(request, f'✅ Leave approved for {leave.employee.full_name}')
            elif action == 'rejected':
                leave.status           = 'rejected'
                leave.rejection_reason = comment
                leave.save()
                messages.success(request, f'❌ Leave rejected for {leave.employee.full_name}')
            else:
                messages.success(request, 'Comment added successfully.')

            return redirect('manager_leave_dashboard')

    return render(request, 'leaves/manager_leave_detail.html', {
        'manager':  manager,
        'leave':    leave,
        'comments': comments,
    })


# ── WFH Management ────────────────────────────────────────────────────────────
@login_required
def manager_wfh_dashboard(request):
    manager = get_manager_employee(request)
    if not manager or not has_leave_access(manager):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    try:
        is_ceo_or_admin = manager.user.is_staff or manager.role.role == 'ceo'
    except:
        is_ceo_or_admin = manager.user.is_staff

    if is_ceo_or_admin:
        wfh_requests = WorkFromHomeRequest.objects.select_related(
            'employee', 'employee__department'
        ).order_by('-created_at')
    else:
        try:
            wfh_requests = WorkFromHomeRequest.objects.filter(
                employee__department=manager.role.manages_department
            ).select_related('employee', 'employee__department').order_by('-created_at')
        except:
            wfh_requests = WorkFromHomeRequest.objects.none()

    status_filter = request.GET.get('status', '')
    if status_filter:
        wfh_requests = wfh_requests.filter(status=status_filter)

    pending  = wfh_requests.filter(status='pending').count()
    approved = wfh_requests.filter(status='approved').count()

    return render(request, 'leaves/manager_wfh.html', {
        'manager':       manager,
        'wfh_requests':  wfh_requests,
        'pending':       pending,
        'approved':      approved,
        'status_filter': status_filter,
        'is_ceo_or_admin': is_ceo_or_admin,
    })


@login_required
def manager_approve_wfh(request, pk):
    manager = get_manager_employee(request)
    if not manager or not has_leave_access(manager):
        return redirect('dashboard')

    wfh = get_object_or_404(WorkFromHomeRequest, pk=pk)
    if request.method == 'POST':
        comment = request.POST.get('comment', '').strip()
        wfh.status      = 'approved'
        wfh.approved_by = manager
        wfh.approved_at = timezone.now()
        wfh.save()

        from attendance.models import AttendanceRecord
        from datetime import date
        AttendanceRecord.objects.update_or_create(
            employee=wfh.employee,
            date=wfh.date,
            defaults={'status': 'work_from_home', 'notes': f'WFH approved by {manager.full_name}. {comment}'}
        )
        messages.success(request, f'WFH approved for {wfh.employee.full_name}')
    return redirect('manager_wfh_dashboard')


@login_required
def manager_reject_wfh(request, pk):
    manager = get_manager_employee(request)
    if not manager or not has_leave_access(manager):
        return redirect('dashboard')

    wfh = get_object_or_404(WorkFromHomeRequest, pk=pk)
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        wfh.status           = 'rejected'
        wfh.rejection_reason = reason
        wfh.save()
        messages.success(request, f'WFH rejected for {wfh.employee.full_name}')
    return redirect('manager_wfh_dashboard')


# ── Project Assignment ────────────────────────────────────────────────────────
@login_required
def project_list(request):
    manager = get_manager_employee(request)
    if not manager:
        return redirect('dashboard')

    try:
        can_assign = manager.role.can_assign_project or manager.user.is_staff
    except:
        can_assign = manager.user.is_staff

    try:
        is_admin = manager.user.is_staff or manager.role.role == 'ceo'
    except:
        is_admin = manager.user.is_staff

    if is_admin:
        from employees.models import Project
        projects = Project.objects.select_related('department', 'manager').prefetch_related('members').all()
    else:
        from employees.models import Project
        projects = Project.objects.filter(
            Q(manager=manager) | Q(members=manager)
        ).distinct().select_related('department', 'manager')

    all_employees = Employee.objects.filter(status='active').select_related('department', 'designation')
    departments   = Department.objects.all()

    return render(request, 'leaves/projects.html', {
        'manager':       manager,
        'projects':      projects,
        'can_assign':    can_assign,
        'all_employees': all_employees,
        'departments':   departments,
    })


@login_required
def create_project(request):
    manager = get_manager_employee(request)
    if not manager:
        return redirect('dashboard')

    try:
        can_assign = manager.role.can_assign_project or manager.user.is_staff
    except:
        can_assign = manager.user.is_staff

    if not can_assign:
        messages.error(request, 'You do not have permission to create projects.')
        return redirect('project_list')

    if request.method == 'POST':
        from employees.models import Project
        name       = request.POST.get('name', '').strip()
        code       = request.POST.get('code', '').strip().upper()
        desc       = request.POST.get('description', '').strip()
        dept_id    = request.POST.get('department')
        start_date = request.POST.get('start_date')
        end_date   = request.POST.get('end_date') or None
        member_ids = request.POST.getlist('members')

        if not name or not code or not start_date:
            messages.error(request, 'Name, Code, and Start Date are required.')
        elif Project.objects.filter(code=code).exists():
            messages.error(request, f'Project code "{code}" already exists.')
        else:
            project = Project.objects.create(
                name=name, code=code, description=desc,
                department_id=dept_id or None,
                manager=manager,
                start_date=start_date,
                end_date=end_date,
                status='active',
            )
            for mid in member_ids:
                try:
                    emp = Employee.objects.get(pk=mid)
                    project.members.add(emp)
                except Employee.DoesNotExist:
                    pass

            messages.success(request, f'Project "{name}" created!')
            return redirect('project_list')

    all_employees = Employee.objects.filter(status='active').select_related('department')
    departments   = Department.objects.all()
    return render(request, 'leaves/create_project.html', {
        'all_employees': all_employees,
        'departments':   departments,
    })


@login_required
def assign_project_members(request, pk):
    from employees.models import Project
    manager = get_manager_employee(request)
    project = get_object_or_404(Project, pk=pk)

    if request.method == 'POST':
        member_ids = request.POST.getlist('members')
        project.members.clear()
        for mid in member_ids:
            try:
                emp = Employee.objects.get(pk=mid)
                project.members.add(emp)
            except Employee.DoesNotExist:
                pass
        messages.success(request, f'Members updated for {project.name}')
        return redirect('project_list')

    all_employees = Employee.objects.filter(status='active').select_related('department')
    return render(request, 'leaves/assign_members.html', {
        'project':       project,
        'all_employees': all_employees,
        'current_members': project.members.all(),
    })