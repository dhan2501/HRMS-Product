# # # employees/notifications.py — NAYA FILE, is location par banao

# # """
# # Small helpers shared by the Project module and the Leave approval views.

# # Kept in one place so 'who can add a project' and 'who gets notified when a
# # teammate goes on leave' are each defined exactly once.
# # """

# # from .models import Employee, Notification, Announcement, Project


# # # ye 2 functions can_manage_projects() se PEHLE add karo:

# # def is_super_admin(employee):
# #     """Only the Super Admin (is_primary_admin) manages Announcements."""
# #     return bool(employee and employee.is_primary_admin)


# # def notify_all_of_announcement(announcement):
# #     """
# #     Called right after a Super Admin publishes an Announcement. Every active
# #     employee (except the poster) gets a Notification linked to it — clicking
# #     that notification opens the announcement in a popup. The Notification
# #     rows cascade-delete automatically when the Announcement expires (24h).
# #     """
# #     recipients = Employee.objects.filter(status='active')
# #     if announcement.created_by_id:
# #         recipients = recipients.exclude(id=announcement.created_by_id)

# #     Notification.objects.bulk_create([
# #         Notification(
# #             recipient=emp,
# #             title=f"📢 {announcement.get_priority_display()} priority: {announcement.title}",
# #             message=announcement.message[:150],
# #             announcement=announcement,
# #         )
# #         for emp in recipients
# #     ])
    
# # def can_manage_projects(employee):
# #     """
# #     Super Admin (is_primary_admin) or anyone whose EmployeeRole has
# #     can_assign_project=True (typically Reporting Managers / Team Leaders)
# #     can create and edit projects.
# #     """
# #     if not employee:
# #         return False
# #     if employee.is_primary_admin:
# #         return True
# #     role = getattr(employee, 'role', None)
# #     if role and role.can_assign_project:
# #         return True
# #     return False


# # def notify_team_of_leave(leave):
# #     """
# #     Called right after a LeaveRequest is approved. Notifies every teammate
# #     who shares at least one active project with this employee, so the rest
# #     of the team knows this person will be on leave.
# #     """
# #     employee = leave.employee

# #     project_ids = Project.objects.filter(members=employee).values_list('id', flat=True)
# #     if not project_ids:
# #         return

# #     teammates = Employee.objects.filter(
# #         projects__id__in=project_ids, status='active'
# #     ).exclude(id=employee.id).distinct()

# #     if leave.start_date == leave.end_date:
# #         date_str = leave.start_date.strftime('%d %b %Y')
# #     else:
# #         date_str = f"{leave.start_date.strftime('%d %b')} – {leave.end_date.strftime('%d %b %Y')}"

# #     Notification.objects.bulk_create([
# #         Notification(
# #             recipient=mate,
# #             title=f"{employee.full_name} is on leave",
# #             message=f"{employee.full_name} will be on leave ({date_str}). Plan project work accordingly.",
# #             link_name='portal_my_projects',
# #         )
# #         for mate in teammates
# #     ])

# # employees/notifications.py — NAYA FILE, is location par banao

# """
# Small helpers shared by the Project module and the Leave approval views.

# Kept in one place so 'who can add a project' and 'who gets notified when a
# teammate goes on leave' are each defined exactly once.
# """

# from .models import Employee, Notification, Announcement, Project


# # ye 2 functions can_manage_projects() se PEHLE add karo:

# def is_super_admin(employee):
#     """Only the Super Admin (is_primary_admin) manages Announcements."""
#     return bool(employee and employee.is_primary_admin)


# def notify_all_of_announcement(announcement):
#     """
#     Called right after a Super Admin publishes an Announcement. Every active
#     employee (except the poster) gets a Notification linked to it — clicking
#     that notification opens the announcement in a popup. The Notification
#     rows cascade-delete automatically when the Announcement expires (24h).
#     """
#     recipients = Employee.objects.filter(status='active')
#     if announcement.created_by_id:
#         recipients = recipients.exclude(id=announcement.created_by_id)

#     Notification.objects.bulk_create([
#         Notification(
#             recipient=emp,
#             title=f"📢 {announcement.get_priority_display()} priority: {announcement.title}",
#             message=announcement.message[:150],
#             announcement=announcement,
#         )
#         for emp in recipients
#     ])
    
# def notify_admins_of_password_change(employee):
#     """
#     Called right after an employee changes their own portal login password
#     (see portal_views.portal_profile). Every Super Admin (is_primary_admin)
#     gets a Notification so the account-security event is visible even
#     though nobody but the employee themselves triggered it.

#     link_name is set to a marker string (not a real Django url name) —
#     hrms.context_processors.notifications() looks for this exact marker
#     to surface these rows in the admin bell dropdown; it is never passed
#     to {% url %} directly.
#     """
#     admins = Employee.objects.filter(
#         is_primary_admin=True, status='active'
#     ).exclude(id=employee.id)

#     if not admins.exists():
#         return

#     Notification.objects.bulk_create([
#         Notification(
#             recipient=admin,
#             title=f"🔐 {employee.full_name} changed their password",
#             message=f"{employee.full_name} ({employee.employee_id}) updated their portal login password just now.",
#             link_name='security_password_change',
#         )
#         for admin in admins
#     ])


# def can_manage_projects(employee):
#     """
#     Super Admin (is_primary_admin) or anyone whose EmployeeRole has
#     can_assign_project=True (typically Reporting Managers / Team Leaders)
#     can create and edit projects.
#     """
#     if not employee:
#         return False
#     if employee.is_primary_admin:
#         return True
#     role = getattr(employee, 'role', None)
#     if role and role.can_assign_project:
#         return True
#     return False


# def notify_team_of_leave(leave):
#     """
#     Called right after a LeaveRequest is approved. Notifies every teammate
#     who shares at least one active project with this employee, so the rest
#     of the team knows this person will be on leave.
#     """
#     employee = leave.employee

#     project_ids = Project.objects.filter(members=employee).values_list('id', flat=True)
#     if not project_ids:
#         return

#     teammates = Employee.objects.filter(
#         projects__id__in=project_ids, status='active'
#     ).exclude(id=employee.id).distinct()

#     if leave.start_date == leave.end_date:
#         date_str = leave.start_date.strftime('%d %b %Y')
#     else:
#         date_str = f"{leave.start_date.strftime('%d %b')} – {leave.end_date.strftime('%d %b %Y')}"

#     Notification.objects.bulk_create([
#         Notification(
#             recipient=mate,
#             title=f"{employee.full_name} is on leave",
#             message=f"{employee.full_name} will be on leave ({date_str}). Plan project work accordingly.",
#             link_name='portal_my_projects',
#         )
#         for mate in teammates
#     ])


# employees/notifications.py — NAYA FILE, is location par banao

from django.db.models import Q

from .models import Employee, Notification, Announcement, Project


def _admin_and_hr_recipients(employee):
    """
    Shared recipient list for password-related security notifications:
    every active Super Admin (is_primary_admin) PLUS every active employee
    in an HR department (Department.code starting with 'HR' — covers
    'Human Resource(HR)' / HR001 and 'HR Head' / HR002), excluding the
    employee who triggered the event themselves. De-duplicated in case
    someone is both.
    """
    return Employee.objects.filter(
        Q(is_primary_admin=True) | Q(department__code__startswith='HR'),
        status='active',
    ).exclude(id=employee.id).distinct()


# ye 2 functions can_manage_projects() se PEHLE add karo:

def is_super_admin(employee):
    """Only the Super Admin (is_primary_admin) manages Announcements."""
    return bool(employee and employee.is_primary_admin)


def notify_all_of_announcement(announcement):
    """
    Called right after a Super Admin publishes an Announcement. Every active
    employee (except the poster) gets a Notification linked to it — clicking
    that notification opens the announcement in a popup. The Notification
    rows cascade-delete automatically when the Announcement expires (24h).
    """
    recipients = Employee.objects.filter(status='active')
    if announcement.created_by_id:
        recipients = recipients.exclude(id=announcement.created_by_id)

    Notification.objects.bulk_create([
        Notification(
            recipient=emp,
            title=f"📢 {announcement.get_priority_display()} priority: {announcement.title}",
            message=announcement.message[:150],
            announcement=announcement,
        )
        for emp in recipients
    ])
    
# def notify_admins_of_password_change(employee):
#     """
#     Called right after an employee changes their own portal login password
#     (see portal_views.portal_profile). Every Super Admin (is_primary_admin)
#     gets a Notification so the account-security event is visible even
#     though nobody but the employee themselves triggered it.

#     link_name is set to a marker string (not a real Django url name) —
#     hrms.context_processors.notifications() looks for this exact marker
#     to surface these rows in the admin bell dropdown; it is never passed
#     to {% url %} directly.
#     """
#     admins = Employee.objects.filter(
#         is_primary_admin=True, status='active'
#     ).exclude(id=employee.id)

#     if not admins.exists():
#         return

#     Notification.objects.bulk_create([
#         Notification(
#             recipient=admin,
#             title=f"🔐 {employee.full_name} changed their password",
#             message=f"{employee.full_name} ({employee.employee_id}) updated their portal login password just now.",
#             link_name='security_password_change',
#         )
#         for admin in admins
#     ])


def notify_admins_of_password_change(employee):
    """
    Called right after an employee changes their own portal login password
    (see portal_views.portal_profile). Every Super Admin (is_primary_admin)
    AND every employee in the HR department gets a Notification so the
    account-security event is visible even though nobody but the employee
    themselves triggered it.

    link_name is set to a marker string (not a real Django url name) —
    hrms.context_processors.notifications() looks for this exact marker
    to surface these rows in the admin bell dropdown; it is never passed
    to {% url %} directly.
    """
    admins = _admin_and_hr_recipients(employee)

    if not admins.exists():
        return

    Notification.objects.bulk_create([
        Notification(
            recipient=admin,
            title=f"🔐 {employee.full_name} changed their password",
            message=f"{employee.full_name} ({employee.employee_id}) updated their portal login password just now.",
            link_name='security_password_change',
        )
        for admin in admins
    ])

# def notify_admins_of_password_reset_request(employee):
#     """
#     Called when an employee can't remember their current password and asks
#     HR to reset it for them — either from the "Forgot your current
#     password?" button on the portal's My Profile page (logged in), or from
#     the logged-out "Forgot password?" page on the login screen.

#     Every Super Admin gets a Notification pointing at Employee Credentials,
#     where reset_employee_password() already lets them reset it to the
#     default pattern in one click.
#     """
#     admins = Employee.objects.filter(
#         is_primary_admin=True, status='active'
#     ).exclude(id=employee.id)

#     if not admins.exists():
#         return

#     Notification.objects.bulk_create([
#         Notification(
#             recipient=admin,
#             title=f"🔑 {employee.full_name} requested a password reset",
#             message=(
#                 f"{employee.full_name} ({employee.employee_id}) can't remember "
#                 f"their portal password and asked HR to reset it."
#             ),
#             link_name='password_reset_request',
#         )
#         for admin in admins
#     ])

def notify_admins_of_password_reset_request(employee):
    """
    Called when an employee can't remember their current password and asks
    HR to reset it for them — either from the "Forgot your current
    password?" button on the portal's My Profile page (logged in), or from
    the logged-out "Forgot password?" page on the login screen.

    Every Super Admin AND every employee in the HR department gets a
    Notification pointing at Employee Credentials, where
    reset_employee_password() already lets them reset it to the default
    pattern in one click.
    """
    admins = _admin_and_hr_recipients(employee)

    if not admins.exists():
        return

    Notification.objects.bulk_create([
        Notification(
            recipient=admin,
            title=f"🔑 {employee.full_name} requested a password reset",
            message=(
                f"{employee.full_name} ({employee.employee_id}) can't remember "
                f"their portal password and asked HR to reset it."
            ),
            link_name='password_reset_request',
        )
        for admin in admins
    ])


def can_manage_projects(employee):
    """
    Super Admin (is_primary_admin) or anyone whose EmployeeRole has
    can_assign_project=True (typically Reporting Managers / Team Leaders)
    can create and edit projects.
    """
    if not employee:
        return False
    if employee.is_primary_admin:
        return True
    role = getattr(employee, 'role', None)
    if role and role.can_assign_project:
        return True
    return False


def notify_team_of_leave(leave):
    """
    Called right after a LeaveRequest is approved. Notifies every teammate
    who shares at least one active project with this employee, so the rest
    of the team knows this person will be on leave.
    """
    employee = leave.employee

    project_ids = Project.objects.filter(members=employee).values_list('id', flat=True)
    if not project_ids:
        return

    teammates = Employee.objects.filter(
        projects__id__in=project_ids, status='active'
    ).exclude(id=employee.id).distinct()

    if leave.start_date == leave.end_date:
        date_str = leave.start_date.strftime('%d %b %Y')
    else:
        date_str = f"{leave.start_date.strftime('%d %b')} – {leave.end_date.strftime('%d %b %Y')}"

    Notification.objects.bulk_create([
        Notification(
            recipient=mate,
            title=f"{employee.full_name} is on leave",
            message=f"{employee.full_name} will be on leave ({date_str}). Plan project work accordingly.",
            link_name='portal_my_projects',
        )
        for mate in teammates
    ])