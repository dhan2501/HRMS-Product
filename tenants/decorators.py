from functools import wraps

from django.http import HttpResponseForbidden


def require_module(module_name):
    """
    Put this above a view so only customers whose plan has this module
    (e.g. 'payroll') enabled can access it.

    Usage:
        @require_module('payroll')
        def payroll_dashboard(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            tenant = getattr(request, 'tenant', None)
            if tenant is not None and not tenant.module_enabled(module_name):
                return HttpResponseForbidden(
                    f"The '{module_name}' module is not enabled on your current plan. "
                    f"Contact your account manager to upgrade."
                )
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator