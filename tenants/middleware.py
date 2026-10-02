from django.shortcuts import render

from tenants.db_router import set_current_tenant_db, clear_current_tenant_db
from tenants.models import Tenant
from tenants.utils import register_tenant_database


class TenantMiddleware:
    """
    Identifies the customer (tenant) on every request and activates its
    database connection for the duration of that request.

    Identification order:
      1. Subdomain — acme.yourhrms.com  (production)
      2. ?tenant=acme query param        (local/dev testing)
      3. X-Tenant: acme header           (mobile app / API clients)

    request.tenant is available in every view/template afterward.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        parts = host.split('.')

        subdomain = None
        # only treat it as a subdomain when there are 3+ parts (acme.yourhrms.com)
        # so localhost / 127.0.0.1 / *.railway.app etc. don't break
        if len(parts) >= 3:
            subdomain = parts[0]

        subdomain = request.GET.get('tenant') or request.headers.get('X-Tenant') or subdomain

        tenant = None
        if subdomain:
            tenant = Tenant.objects.filter(subdomain=subdomain).first()

        request.tenant = tenant

        if tenant:
            db_alias = register_tenant_database(tenant)
            set_current_tenant_db(db_alias)
        else:
            clear_current_tenant_db()

        try:
            response = self.get_response(request)
        finally:
            clear_current_tenant_db()  # next request/thread starts with a clean state

        return response


class SubscriptionAccessMiddleware:
    """
    If a tenant is identified but its subscription has expired/is suspended,
    blocks the dashboard/API and shows a 'please renew' page instead.

    NOTE: this is a page-level lock only. For API endpoints also add the
    'tenants.permissions.IsTenantActive' permission class to your DRF views.
    """

    # These paths always stay accessible, even if the subscription has expired:
    ALLOWED_PREFIXES = (
        '/admin/',            # your (superadmin) Django admin
        '/tenants/',          # console + billing/recharge pages
        '/static/', '/media/',
        '/employee-login/', '/employee-logout/',
        '/admin-login/', '/admin-logout/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tenant = getattr(request, 'tenant', None)

        if tenant and not any(request.path.startswith(p) for p in self.ALLOWED_PREFIXES):
            if not tenant.is_active():
                return render(
                    request,
                    'tenants/subscription_expired.html',
                    {'tenant': tenant},
                    status=402,  # Payment Required
                )

        return self.get_response(request)