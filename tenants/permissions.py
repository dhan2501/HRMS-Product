from rest_framework.permissions import BasePermission


class IsTenantActive(BasePermission):
    """
    Add to DRF's DEFAULT_PERMISSION_CLASSES, or per-view permission_classes —
    blocks API calls from an expired/suspended tenant right here.
    """
    message = "Your subscription has expired. Contact your admin to renew."

    def has_permission(self, request, view):
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            return True  # non-tenant context (e.g. superadmin API)
        return tenant.is_active()


def has_module(module_name):
    """
    Factory — builds a permission class for a specific module.

    Usage (DRF view):
        permission_classes = [IsAuthenticated, IsTenantActive, has_module('payroll')]
    """
    class _HasModule(BasePermission):
        message = f"The '{module_name}' module is not enabled on this plan."

        def has_permission(self, request, view):
            tenant = getattr(request, 'tenant', None)
            if tenant is None:
                return True
            return tenant.module_enabled(module_name)

    return _HasModule