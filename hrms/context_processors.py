from django.utils import timezone


def notifications(request):
    """
    Site-wide notification context (bell icon + sidebar badge).
    Only computed for authenticated admin/staff users so it stays cheap
    and doesn't leak leave data to regular employees on the portal side.
    """
    if not request.user.is_authenticated:
        return {}

    if not (request.user.is_staff or request.user.is_superuser):
        return {}

    items = []

    # Pending leave requests
    pending_leaves_count = 0
    try:
        from leaves.models import LeaveRequest
        leave_qs = LeaveRequest.objects.filter(status='pending').select_related(
            'employee', 'leave_type'
        ).order_by('-created_at')
        pending_leaves_count = leave_qs.count()
        for lr in leave_qs[:8]:
            items.append({
                'type': 'leave',
                'icon': 'fa-umbrella-beach',
                'color': 'amber',
                'employee': lr.employee.full_name,
                'title': f"{lr.employee.full_name} applied for {lr.leave_type.name}",
                'subtitle': f"{lr.start_date:%d %b} – {lr.end_date:%d %b} · {lr.days} day(s)",
                'created_at': lr.created_at,
                'url_name': 'leave_requests',
                'object_id': lr.id,
            })
    except Exception:
        pass

    # Pending WFH requests
    wfh_pending_count = 0
    try:
        from attendance.models import WorkFromHomeRequest
        wfh_qs = WorkFromHomeRequest.objects.filter(status='pending').select_related(
            'employee'
        ).order_by('-created_at')
        wfh_pending_count = wfh_qs.count()
        for wfh in wfh_qs[:8]:
            items.append({
                'type': 'wfh',
                'icon': 'fa-house-laptop',
                'color': 'blue',
                'employee': wfh.employee.full_name,
                'title': f"{wfh.employee.full_name} requested Work From Home",
                'subtitle': f"{wfh.date:%d %b %Y}",
                'created_at': wfh.created_at,
                'url_name': 'wfh_requests',
                'object_id': wfh.id,
            })
    except Exception:
        pass

    # Any other future "request" type models can be appended here the same way,
    # each contributing {type, icon, color, employee, title, subtitle, created_at, url_name}.

    # Merge everything into one feed, newest first.
    items.sort(key=lambda i: i['created_at'], reverse=True)
    notification_list = items[:8]
    total_notifications = pending_leaves_count + wfh_pending_count

    return {
        'pending_leaves': pending_leaves_count,
        'wfh_pending_count': wfh_pending_count,
        'notification_list': notification_list,
        'total_notifications': total_notifications,
        'notifications_generated_at': timezone.now(),
    }