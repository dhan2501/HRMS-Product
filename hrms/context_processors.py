# # from django.utils import timezone

# # def site_settings(request):
# #     """
# #     Makes company branding (logo, primary/text color) available in
# #     EVERY template — used to theme the sidebar/header and show the
# #     company logo.
# #     """
# #     try:
# #         from employees.models import SiteSettings
# #         site = SiteSettings.load()
# #     except Exception:
# #         return {}
# #     return {'site_settings': site}


# # def notifications(request):
# #     """
# #     Site-wide notification context (bell icon + sidebar badge).
# #     Only computed for authenticated admin/staff users so it stays cheap
# #     and doesn't leak leave data to regular employees on the portal side.

# #     notification_list is a list of dicts (not raw model objects) so the
# #     template can safely do {% url n.url_name %} for any notification type
# #     without needing to know what kind of object produced it.
# #     """
# #     if not request.user.is_authenticated:
# #         return {}

# #     if not (request.user.is_staff or request.user.is_superuser):
# #         return {}

# #     combined = []

# #     # Pending leave requests
# #     try:
# #         from leaves.models import LeaveRequest
# #         leave_qs = LeaveRequest.objects.filter(status='pending').select_related(
# #             'employee', 'leave_type'
# #         ).order_by('-created_at')[:10]
# #         for lv in leave_qs:
# #             combined.append({
# #                 'type':        'leave',
# #                 'title':       f"{lv.employee.full_name} applied for leave",
# #                 'subtitle':    f"{lv.leave_type.name} · {lv.days} day{'s' if lv.days != 1 else ''}",
# #                 'url_name':    'leave_requests',
# #                 'created_at':  lv.created_at,
# #                 'icon':        'fa-umbrella-beach',
# #                 'color':       'amber',
# #             })
# #         pending_leaves_count = LeaveRequest.objects.filter(status='pending').count()
# #     except Exception:
# #         pending_leaves_count = 0

# #     # Pending WFH requests
# #     wfh_pending_count = 0
# #     try:
# #         from attendance.models import WorkFromHomeRequest
# #         wfh_qs = WorkFromHomeRequest.objects.filter(status='pending').select_related('employee')[:10]
# #         for wfh in wfh_qs:
# #             combined.append({
# #                 'type':        'wfh',
# #                 'title':       f"{wfh.employee.full_name} requested WFH",
# #                 'subtitle':    wfh.date.strftime('%d %b %Y'),
# #                 'url_name':    'wfh_requests',
# #                 'created_at':  wfh.created_at,
# #                 'icon':        'fa-house-laptop',
# #                 'color':       'blue',
# #             })
# #         wfh_pending_count = WorkFromHomeRequest.objects.filter(status='pending').count()
# #     except Exception:
# #         pass

# #     # Pending Finance-Approval expense claims (this is the stage Finance/
# #     # Super Admin actually needs to act on; pending_manager claims sit with
# #     # the reporting manager first, so they're not surfaced here).
# #     expense_pending_count = 0
# #     try:
# #         from expenses.models import ExpenseClaim
# #         expense_qs = ExpenseClaim.objects.filter(status='pending_finance').select_related('employee')[:10]
# #         for exp in expense_qs:
# #             combined.append({
# #                 'type':        'expense',
# #                 'title':       f"{exp.employee.full_name} submitted an expense claim",
# #                 'subtitle':    f"{exp.get_category_display()} · Rs.{exp.amount}",
# #                 'url_name':    'expense_requests',
# #                 'created_at':  exp.updated_at,
# #                 'icon':        'fa-receipt',
# #                 'color':       'blue',
# #             })
# #         expense_pending_count = ExpenseClaim.objects.filter(status='pending_finance').count()
# #     except Exception:
# #         pass

# #     combined.sort(key=lambda n: n['created_at'], reverse=True)
# #     notification_list = combined[:6]

# #     total_notifications = pending_leaves_count + wfh_pending_count + expense_pending_count

# #     return {
# #         'pending_leaves': pending_leaves_count,
# #         'notification_list': notification_list,
# #         'wfh_pending_count': wfh_pending_count,
# #         'expense_pending_count': expense_pending_count,
# #         'total_notifications': total_notifications,
# #         'notifications_generated_at': timezone.now(),
# #     }


# # def unread_messages(request):
# #     """
# #     Unread chat-message count for the sidebar/navbar "Team Chat" badge.
# #     Available to EVERY logged-in user (HR staff and employees alike),
# #     unlike notifications() above which is staff-only.
# #     """
# #     if not request.user.is_authenticated:
# #         return {}

# #     try:
# #         from messaging.models import Message
# #     except Exception:
# #         return {}

# #     count = Message.objects.filter(
# #         conversation__participants=request.user,
# #         is_read=False,
# #     ).exclude(sender=request.user).count()

# #     return {'unread_messages_count': count}


# # def team_requests(request):
# #     """
# #     Portal-side context: if the logged-in employee is someone's Reporting
# #     Manager, expose how many pending Leave/WFH/Expense requests from their
# #     direct reports are waiting on them — used for the "Team Requests" and
# #     "Team Expenses" sidebar badges in the employee portal.
# #     """
# #     if not request.user.is_authenticated:
# #         return {}

# #     try:
# #         from employees.models import Employee
# #         from leaves.models import LeaveRequest
# #         from attendance.models import WorkFromHomeRequest
# #         current_employee = Employee.objects.get(user=request.user)
# #     except Exception:
# #         return {}

# #     is_reporting_manager = current_employee.team_members.exists()
# #     if not is_reporting_manager:
# #         return {
# #             'is_reporting_manager': False,
# #             'team_requests_pending_count': 0,
# #             'team_expenses_pending_count': 0,
# #         }

# #     reportee_ids = list(current_employee.team_members.values_list('id', flat=True))
# #     pending_leave = LeaveRequest.objects.filter(
# #         employee_id__in=reportee_ids, status='pending'
# #     ).count()
# #     pending_wfh = WorkFromHomeRequest.objects.filter(
# #         employee_id__in=reportee_ids, status='pending'
# #     ).count()

# #     try:
# #         from expenses.models import ExpenseClaim
# #         pending_expenses = ExpenseClaim.objects.filter(
# #             employee_id__in=reportee_ids, status='pending_manager'
# #         ).count()
# #     except Exception:
# #         pending_expenses = 0

# #     return {
# #         'is_reporting_manager':        True,
# #         'team_requests_pending_count': pending_leave + pending_wfh,
# #         'team_expenses_pending_count': pending_expenses,
# #     }


# # # hrms/context_processors.py

# # def team_notifications(request):
# #     """
# #     Portal-side bell icon: unread count of Notification rows for the
# #     logged-in employee — used to alert them e.g. "your teammate is on
# #     leave today". Staff/admin users don't get this (they use the
# #     admin-side notifications() processor above instead).
# #     """
# #     if not request.user.is_authenticated:
# #         return {}
# #     if request.user.is_staff or request.user.is_superuser:
# #         return {}

# #     try:
# #         from employees.models import Employee, Notification, Announcement
# #         emp = Employee.objects.get(user=request.user)
# #         Announcement.objects.cleanup_expired()   # keep the badge count honest
# #     except Exception:
# #         return {}

# #     unread = Notification.objects.filter(recipient=emp, is_read=False)
# #     return {
# #         'team_notification_unread_count': unread.count(),
# #         'team_notification_list': unread.order_by('-created_at')[:6],
# #     }


# # def current_employee(request):
# #     """
# #     Makes `employee` available in EVERY template (navbar avatar/name in
# #     portal/base_portal.html relies on it) even on pages whose view forgot
# #     to pass it explicitly — e.g. chat_home, help_home. If a view already
# #     passes its own `employee` in the render() context, that value wins
# #     (view context overrides context-processor context of the same name),
# #     so this is purely a safe fallback.
# #     """
# #     if not request.user.is_authenticated:
# #         return {}

# #     try:
# #         from employees.models import Employee
# #         emp = Employee.objects.select_related('department', 'designation').get(user=request.user)
# #     except Exception:
# #         return {}

# #     return {'employee': emp}


# from django.utils import timezone

# def site_settings(request):
#     """
#     Makes company branding (logo, primary/text color) available in
#     EVERY template — used to theme the sidebar/header and show the
#     company logo.
#     """
#     try:
#         from employees.models import SiteSettings
#         site = SiteSettings.load()
#     except Exception:
#         return {}
#     return {'site_settings': site}


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
#                 'color':       'amber',
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
#                 'color':       'blue',
#             })
#         wfh_pending_count = WorkFromHomeRequest.objects.filter(status='pending').count()
#     except Exception:
#         pass

#     # Pending Finance-Approval expense claims (this is the stage Finance/
#     # Super Admin actually needs to act on; pending_manager claims sit with
#     # the reporting manager first, so they're not surfaced here).
#     expense_pending_count = 0
#     try:
#         from expenses.models import ExpenseClaim
#         expense_qs = ExpenseClaim.objects.filter(status='pending_finance').select_related('employee')[:10]
#         for exp in expense_qs:
#             combined.append({
#                 'type':        'expense',
#                 'title':       f"{exp.employee.full_name} submitted an expense claim",
#                 'subtitle':    f"{exp.get_category_display()} · Rs.{exp.amount}",
#                 'url_name':    'expense_requests',
#                 'created_at':  exp.updated_at,
#                 'icon':        'fa-receipt',
#                 'color':       'blue',
#             })
#         expense_pending_count = ExpenseClaim.objects.filter(status='pending_finance').count()
#     except Exception:
#         pass

#     # Security alerts — e.g. "an employee changed their password".
#     # These come from the generic Notification model (recipient = this
#     # admin's own Employee record), unlike the three blocks above which
#     # read straight from the business models. Shown once, then marked
#     # read so the badge doesn't stay stuck forever.
#     security_alert_count = 0
#     try:
#         from employees.models import Employee, Notification
#         current_emp = Employee.objects.filter(user=request.user).first()
#         if current_emp and current_emp.is_primary_admin:
#             sec_qs = Notification.objects.filter(
#                 recipient=current_emp,
#                 link_name='security_password_change',
#                 is_read=False,
#             ).order_by('-created_at')[:10]
#             sec_list = list(sec_qs)
#             for note in sec_list:
#                 combined.append({
#                     'type':        'security',
#                     'title':       note.title,
#                     'subtitle':    note.message[:80],
#                     'url_name':    'employee_list',
#                     'created_at':  note.created_at,
#                     'icon':        'fa-key',
#                     'color':       'rose',
#                 })
#             security_alert_count = len(sec_list)
#             if sec_list:
#                 Notification.objects.filter(
#                     id__in=[n.id for n in sec_list]
#                 ).update(is_read=True)
#     except Exception:
#         security_alert_count = 0

#     combined.sort(key=lambda n: n['created_at'], reverse=True)
#     notification_list = combined[:6]

#     total_notifications = (
#         pending_leaves_count + wfh_pending_count
#         + expense_pending_count + security_alert_count
#     )

#     return {
#         'pending_leaves': pending_leaves_count,
#         'notification_list': notification_list,
#         'wfh_pending_count': wfh_pending_count,
#         'expense_pending_count': expense_pending_count,
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


# def team_requests(request):
#     """
#     Portal-side context: if the logged-in employee is someone's Reporting
#     Manager, expose how many pending Leave/WFH/Expense requests from their
#     direct reports are waiting on them — used for the "Team Requests" and
#     "Team Expenses" sidebar badges in the employee portal.
#     """
#     if not request.user.is_authenticated:
#         return {}

#     try:
#         from employees.models import Employee
#         from leaves.models import LeaveRequest
#         from attendance.models import WorkFromHomeRequest
#         current_employee = Employee.objects.get(user=request.user)
#     except Exception:
#         return {}

#     is_reporting_manager = current_employee.team_members.exists()
#     if not is_reporting_manager:
#         return {
#             'is_reporting_manager': False,
#             'team_requests_pending_count': 0,
#             'team_expenses_pending_count': 0,
#         }

#     reportee_ids = list(current_employee.team_members.values_list('id', flat=True))
#     pending_leave = LeaveRequest.objects.filter(
#         employee_id__in=reportee_ids, status='pending'
#     ).count()
#     pending_wfh = WorkFromHomeRequest.objects.filter(
#         employee_id__in=reportee_ids, status='pending'
#     ).count()

#     try:
#         from expenses.models import ExpenseClaim
#         pending_expenses = ExpenseClaim.objects.filter(
#             employee_id__in=reportee_ids, status='pending_manager'
#         ).count()
#     except Exception:
#         pending_expenses = 0

#     return {
#         'is_reporting_manager':        True,
#         'team_requests_pending_count': pending_leave + pending_wfh,
#         'team_expenses_pending_count': pending_expenses,
#     }


# # hrms/context_processors.py

# def team_notifications(request):
#     """
#     Portal-side bell icon: unread count of Notification rows for the
#     logged-in employee — used to alert them e.g. "your teammate is on
#     leave today". Staff/admin users don't get this (they use the
#     admin-side notifications() processor above instead).
#     """
#     if not request.user.is_authenticated:
#         return {}
#     if request.user.is_staff or request.user.is_superuser:
#         return {}

#     try:
#         from employees.models import Employee, Notification, Announcement
#         emp = Employee.objects.get(user=request.user)
#         Announcement.objects.cleanup_expired()   # keep the badge count honest
#     except Exception:
#         return {}

#     unread = Notification.objects.filter(recipient=emp, is_read=False)
#     return {
#         'team_notification_unread_count': unread.count(),
#         'team_notification_list': unread.order_by('-created_at')[:6],
#     }


# def current_employee(request):
#     """
#     Makes `employee` available in EVERY template (navbar avatar/name in
#     portal/base_portal.html relies on it) even on pages whose view forgot
#     to pass it explicitly — e.g. chat_home, help_home. If a view already
#     passes its own `employee` in the render() context, that value wins
#     (view context overrides context-processor context of the same name),
#     so this is purely a safe fallback.
#     """
#     if not request.user.is_authenticated:
#         return {}

#     try:
#         from employees.models import Employee
#         emp = Employee.objects.select_related('department', 'designation').get(user=request.user)
#     except Exception:
#         return {}

#     return {'employee': emp}

from django.utils import timezone

def site_settings(request):
    """
    Makes company branding (logo, primary/text color) available in
    EVERY template — used to theme the sidebar/header and show the
    company logo.
    """
    try:
        from employees.models import SiteSettings
        site = SiteSettings.load()
    except Exception:
        return {}
    return {'site_settings': site}


def notifications(request):
    """
    Site-wide notification context (bell icon + sidebar badge).
    Only computed for authenticated admin/staff users so it stays cheap
    and doesn't leak leave data to regular employees on the portal side.

    notification_list is a list of dicts (not raw model objects) so the
    template can safely do {% url n.url_name %} for any notification type
    without needing to know what kind of object produced it.
    """
    # if not request.user.is_authenticated:
    #     return {}

    # if not (request.user.is_staff or request.user.is_superuser):
    #     return {}

    # combined = []

    if not request.user.is_authenticated:
        return {}

    if not (request.user.is_staff or request.user.is_superuser):
        from employees.models import Employee
        emp = Employee.objects.filter(user=request.user).select_related('department').first()
        is_hr_dept = bool(
            emp and emp.department and emp.department.code
            and emp.department.code.startswith('HR')
        )
        if not is_hr_dept:
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

    # Pending Finance-Approval expense claims (this is the stage Finance/
    # Super Admin actually needs to act on; pending_manager claims sit with
    # the reporting manager first, so they're not surfaced here).
    expense_pending_count = 0
    try:
        from expenses.models import ExpenseClaim
        expense_qs = ExpenseClaim.objects.filter(status='pending_finance').select_related('employee')[:10]
        for exp in expense_qs:
            combined.append({
                'type':        'expense',
                'title':       f"{exp.employee.full_name} submitted an expense claim",
                'subtitle':    f"{exp.get_category_display()} · Rs.{exp.amount}",
                'url_name':    'expense_requests',
                'created_at':  exp.updated_at,
                'icon':        'fa-receipt',
                'color':       'blue',
            })
        expense_pending_count = ExpenseClaim.objects.filter(status='pending_finance').count()
    except Exception:
        pass

    # Security alerts — password changes and password-reset requests.
    # These come from the generic Notification model (recipient = this
    # admin's own Employee record), unlike the three blocks above which
    # read straight from the business models. Shown once, then marked
    # read so the badge doesn't stay stuck forever.
    # security_alert_count = 0
    # try:
    #     from employees.models import Employee, Notification
    #     current_emp = Employee.objects.filter(user=request.user).first()
    #     if current_emp and current_emp.is_primary_admin:
    #         sec_qs = Notification.objects.filter(
    #             recipient=current_emp,
    #             link_name__in=['security_password_change', 'password_reset_request'],
    #             is_read=False,
    #         ).order_by('-created_at')[:10]
    #         sec_list = list(sec_qs)
    #         for note in sec_list:
    #             is_reset_request = note.link_name == 'password_reset_request'
    #             combined.append({
    #                 'type':        'security',
    #                 'title':       note.title,
    #                 'subtitle':    note.message[:80],
    #                 'url_name':    'employee_credentials' if is_reset_request else 'employee_list',
    #                 'created_at':  note.created_at,
    #                 'icon':        'fa-key' if is_reset_request else 'fa-lock',
    #                 'color':       'rose',
    #             })
    #         security_alert_count = len(sec_list)
    #         if sec_list:
    #             Notification.objects.filter(
    #                 id__in=[n.id for n in sec_list]
    #             ).update(is_read=True)
    # except Exception:
    #     security_alert_count = 0

    security_alert_count = 0
    try:
        from employees.models import Employee, Notification
        current_emp = Employee.objects.filter(user=request.user).select_related('department').first()
        is_hr_dept = bool(
            current_emp and current_emp.department and current_emp.department.code
            and current_emp.department.code.startswith('HR')
        )
        if current_emp and (current_emp.is_primary_admin or is_hr_dept):
            sec_qs = Notification.objects.filter(
                recipient=current_emp,
                link_name__in=['security_password_change', 'password_reset_request'],
                is_read=False,
            ).order_by('-created_at')[:10]
            sec_list = list(sec_qs)
            for note in sec_list:
                is_reset_request = note.link_name == 'password_reset_request'
                combined.append({
                    'type':        'security',
                    'title':       note.title,
                    'subtitle':    note.message[:80],
                    'url_name':    'employee_credentials' if is_reset_request else 'employee_list',
                    'created_at':  note.created_at,
                    'icon':        'fa-key' if is_reset_request else 'fa-lock',
                    'color':       'rose',
                })
            security_alert_count = len(sec_list)
            if sec_list:
                Notification.objects.filter(
                    id__in=[n.id for n in sec_list]
                ).update(is_read=True)
    except Exception:
        security_alert_count = 0

    combined.sort(key=lambda n: n['created_at'], reverse=True)
    notification_list = combined[:6]

    total_notifications = (
        pending_leaves_count + wfh_pending_count
        + expense_pending_count + security_alert_count
    )

    return {
        'pending_leaves': pending_leaves_count,
        'notification_list': notification_list,
        'wfh_pending_count': wfh_pending_count,
        'expense_pending_count': expense_pending_count,
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
    Manager, expose how many pending Leave/WFH/Expense requests from their
    direct reports are waiting on them — used for the "Team Requests" and
    "Team Expenses" sidebar badges in the employee portal.
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
        return {
            'is_reporting_manager': False,
            'team_requests_pending_count': 0,
            'team_expenses_pending_count': 0,
        }

    reportee_ids = list(current_employee.team_members.values_list('id', flat=True))
    pending_leave = LeaveRequest.objects.filter(
        employee_id__in=reportee_ids, status='pending'
    ).count()
    pending_wfh = WorkFromHomeRequest.objects.filter(
        employee_id__in=reportee_ids, status='pending'
    ).count()

    try:
        from expenses.models import ExpenseClaim
        pending_expenses = ExpenseClaim.objects.filter(
            employee_id__in=reportee_ids, status='pending_manager'
        ).count()
    except Exception:
        pending_expenses = 0

    return {
        'is_reporting_manager':        True,
        'team_requests_pending_count': pending_leave + pending_wfh,
        'team_expenses_pending_count': pending_expenses,
    }


# hrms/context_processors.py

def team_notifications(request):
    """
    Portal-side bell icon: unread count of Notification rows for the
    logged-in employee — used to alert them e.g. "your teammate is on
    leave today". Staff/admin users don't get this (they use the
    admin-side notifications() processor above instead).
    """
    if not request.user.is_authenticated:
        return {}
    if request.user.is_staff or request.user.is_superuser:
        return {}

    try:
        from employees.models import Employee, Notification, Announcement
        emp = Employee.objects.get(user=request.user)
        Announcement.objects.cleanup_expired()   # keep the badge count honest
    except Exception:
        return {}

    unread = Notification.objects.filter(recipient=emp, is_read=False)
    return {
        'team_notification_unread_count': unread.count(),
        'team_notification_list': unread.order_by('-created_at')[:6],
    }


def current_employee(request):
    """
    Makes `employee` available in EVERY template (navbar avatar/name in
    portal/base_portal.html relies on it) even on pages whose view forgot
    to pass it explicitly — e.g. chat_home, help_home. If a view already
    passes its own `employee` in the render() context, that value wins
    (view context overrides context-processor context of the same name),
    so this is purely a safe fallback.
    """
    if not request.user.is_authenticated:
        return {}

    try:
        from employees.models import Employee
        emp = Employee.objects.select_related('department', 'designation').get(user=request.user)
    except Exception:
        return {}

    return {'employee': emp}