"""
Small helper to write AuditLog rows from anywhere in the codebase
without repeating the same boilerplate every time.

Usage:
    from employees.audit import log_action

    log_action(
        request,
        action='update',
        module='Employee',
        field_name='department',
        old_value=str(old_dept),
        new_value=str(new_dept),
        description=f'Changed department for {employee.full_name}',
        target_employee=employee,
    )
"""
from .models import AuditLog, Employee


def _client_ip(request):
    if request is None:
        return None
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(request, action, module, field_name='', old_value='',
                new_value='', description='', target_employee=None):
    """
    Writes one AuditLog row.

    - `request.user` is stored as the actor (who made the change).
    - `target_employee` is the employee the change is ABOUT (e.g. whose
      profile was edited). If not given, falls back to the acting
      user's own employee profile (e.g. for settings/superadmin changes).
    - Department is auto-filled from target_employee for easy filtering.
    """
    user = getattr(request, 'user', None)
    if user is not None and not user.is_authenticated:
        user = None

    employee = target_employee
    if employee is None and user is not None:
        employee = Employee.objects.filter(user=user).first()

    department = employee.department if employee else None

    AuditLog.objects.create(
        user=user,
        employee=employee,
        department=department,
        action=action,
        module=module,
        field_name=field_name,
        old_value=str(old_value)[:255] if old_value not in (None, '') else '',
        new_value=str(new_value)[:255] if new_value not in (None, '') else '',
        description=description,
        ip_address=_client_ip(request),
    )