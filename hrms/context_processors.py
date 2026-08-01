# from django.utils import timezone


# def notifications(request):
#     """
#     Site-wide notification context (bell icon + sidebar badge).
#     Only computed for authenticated admin/staff users so it stays cheap
#     and doesn't leak leave data to regular employees on the portal side.

#     notification_list is a list of dicts (not raw model objects) so the
#     template can safely do {% url n.url_name %} for any notification type
#     without needing to know what kind of object produced it.
#     """
#     if not request.user.is_authenticated:
#         return {}

#     if not (request.user.is_staff or request.user.is_superuser):
#         return {}

#     combined = []

#     # Pending leave requests
#     try:
#         from leaves.models import LeaveRequest
#         leave_qs = LeaveRequest.objects.filter(status='pending').select_related(
#             'employee', 'leave_type'
#         ).order_by('-created_at')[:10]
#         for lv in leave_qs:
#             combined.append({
#                 'type':        'leave',
#                 'title':       f"{lv.employee.full_name} applied for leave",
#                 'subtitle':    f"{lv.leave_type.name} · {lv.days} day{'s' if lv.days != 1 else ''}",
#                 'url_name':    'leave_requests',
#                 'created_at':  lv.created_at,
#                 'icon':        'fa-umbrella-beach',
#             })
#         pending_leaves_count = LeaveRequest.objects.filter(status='pending').count()
#     except Exception:
#         pending_leaves_count = 0

#     # Pending WFH requests
#     wfh_pending_count = 0
#     try:
#         from attendance.models import WorkFromHomeRequest
#         wfh_qs = WorkFromHomeRequest.objects.filter(status='pending').select_related('employee')[:10]
#         for wfh in wfh_qs:
#             combined.append({
#                 'type':        'wfh',
#                 'title':       f"{wfh.employee.full_name} requested WFH",
#                 'subtitle':    wfh.date.strftime('%d %b %Y'),
#                 'url_name':    'wfh_requests',
#                 'created_at':  wfh.created_at,
#                 'icon':        'fa-house-laptop',
#             })
#         wfh_pending_count = WorkFromHomeRequest.objects.filter(status='pending').count()
#     except Exception:
#         pass

#     combined.sort(key=lambda n: n['created_at'], reverse=True)
#     notification_list = combined[:6]

#     total_notifications = pending_leaves_count + wfh_pending_count

#     return {
#         'pending_leaves': pending_leaves_count,
#         'notification_list': notification_list,
#         'wfh_pending_count': wfh_pending_count,
#         'total_notifications': total_notifications,
#         'notifications_generated_at': timezone.now(),
#     }


# def unread_messages(request):
#     """
#     Unread chat-message count for the sidebar/navbar "Team Chat" badge.
#     Available to EVERY logged-in user (HR staff and employees alike),
#     unlike notifications() above which is staff-only.
#     """
#     if not request.user.is_authenticated:
#         return {}

#     try:
#         from messaging.models import Message
#     except Exception:
#         return {}

#     count = Message.objects.filter(
#         conversation__participants=request.user,
#         is_read=False,
#     ).exclude(sender=request.user).count()

#     return {'unread_messages_count': count}

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