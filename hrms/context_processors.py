from django.utils import timezone


def notifications(request):
    """
    Site-wide notification context (bell icon + sidebar badge).
    Only computed for authenticated admin/staff users so it stays cheap
    and doesn't leak leave data to regular employees on the portal side.

    notification_list is a list of dicts (not raw model objects) so the
    template can safely do {% url n.url_name %} for any notification type
    without needing to know what kind of object produced it.
    """
    if not request.user.is_authenticated:
        return {}

    if not (request.user.is_staff or request.user.is_superuser):
        return {}

    combined = []

    # Pending leave requests
    try:
        from leaves.models import LeaveRequest
        leave_qs = LeaveRequest.objects.filter(status='pending').select_related(
            'employee', 'leave_type'
        ).order_by('-created_at')[:10]
        for lv in leave_qs:
            combined.append({
                'type':        'leave',
                'title':       f"{lv.employee.full_name} applied for leave",
                'subtitle':    f"{lv.leave_type.name} · {lv.days} day{'s' if lv.days != 1 else ''}",
                'url_name':    'leave_requests',
                'created_at':  lv.created_at,
                'icon':        'fa-umbrella-beach',
                'color':       'amber',
            })
        pending_leaves_count = LeaveRequest.objects.filter(status='pending').count()
    except Exception:
        pending_leaves_count = 0

    # Pending WFH requests
    wfh_pending_count = 0
    try:
        from attendance.models import WorkFromHomeRequest
        wfh_qs = WorkFromHomeRequest.objects.filter(status='pending').select_related('employee')[:10]
        for wfh in wfh_qs:
            combined.append({
                'type':        'wfh',
                'title':       f"{wfh.employee.full_name} requested WFH",
                'subtitle':    wfh.date.strftime('%d %b %Y'),
                'url_name':    'wfh_requests',
                'created_at':  wfh.created_at,
                'icon':        'fa-house-laptop',
                'color':       'blue',
            })
        wfh_pending_count = WorkFromHomeRequest.objects.filter(status='pending').count()
    except Exception:
        pass

    combined.sort(key=lambda n: n['created_at'], reverse=True)
    notification_list = combined[:6]

    total_notifications = pending_leaves_count + wfh_pending_count

    return {
        'pending_leaves': pending_leaves_count,
        'notification_list': notification_list,
        'wfh_pending_count': wfh_pending_count,
        'total_notifications': total_notifications,
        'notifications_generated_at': timezone.now(),
    }


def unread_messages(request):
    """
    Unread chat-message count for the sidebar/navbar "Team Chat" badge.
    Available to EVERY logged-in user (HR staff and employees alike),
    unlike notifications() above which is staff-only.
    """
    if not request.user.is_authenticated:
        return {}

    try:
        from messaging.models import Message
    except Exception:
        return {}

    count = Message.objects.filter(
        conversation__participants=request.user,
        is_read=False,
    ).exclude(sender=request.user).count()

    return {'unread_messages_count': count}


def team_requests(request):
    """
    Portal-side context: if the logged-in employee is someone's Reporting
    Manager, expose how many pending Leave/WFH requests from their direct
    reports are waiting on them — used for the "Team Requests" sidebar
    badge in the employee portal.
    """
    if not request.user.is_authenticated:
        return {}

    try:
        from employees.models import Employee
        from leaves.models import LeaveRequest
        from attendance.models import WorkFromHomeRequest
        current_employee = Employee.objects.get(user=request.user)
    except Exception:
        return {}

    is_reporting_manager = current_employee.team_members.exists()
    if not is_reporting_manager:
        return {'is_reporting_manager': False, 'team_requests_pending_count': 0}

    reportee_ids = current_employee.team_members.values_list('id', flat=True)
    pending_leave = LeaveRequest.objects.filter(
        employee_id__in=reportee_ids, status='pending'
    ).count()
    pending_wfh = WorkFromHomeRequest.objects.filter(
        employee_id__in=reportee_ids, status='pending'
    ).count()

    return {
        'is_reporting_manager':        True,
        'team_requests_pending_count': pending_leave + pending_wfh,
    }