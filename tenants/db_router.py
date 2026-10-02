import threading

_thread_locals = threading.local()

# Django apps whose data lives in a separate database per tenant.
# 'tenants' itself is NOT in this set — Tenant/RechargeLog always stay in the
# 'default' database so you can manage all customers from one place.
TENANT_APPS = {
    'employees', 'attendance', 'leaves', 'payroll',
    'recruitment', 'wellness', 'events', 'messaging', 'helpcenter',
    # auth/contenttypes must also live in the tenant DB so each tenant's own
    # users (employees) stay inside that tenant's database.
    'auth', 'contenttypes', 'admin', 'sessions', 'authtoken',
}


def set_current_tenant_db(db_alias):
    """Sets the active tenant DB for the current request/thread.
    Returns the previous value so the caller can restore it if needed."""
    previous = getattr(_thread_locals, 'tenant_db', None)
    _thread_locals.tenant_db = db_alias
    return previous


def get_current_tenant_db():
    return getattr(_thread_locals, 'tenant_db', None)


def clear_current_tenant_db():
    _thread_locals.tenant_db = None


class TenantDatabaseRouter:
    """
    Whatever the tenant middleware has set (via set_current_tenant_db) for
    this request routes all TENANT_APPS queries to that database.

    The 'tenants' app (Tenant, RechargeLog) always stays on the 'default' DB —
    this is what lets the superadmin dashboard work without any tenant context.
    """

    def _route(self, app_label):
        if app_label in TENANT_APPS:
            return get_current_tenant_db()
        return None  # None => Django falls back to its default routing ('default' DB)

    def db_for_read(self, model, **hints):
        return self._route(model._meta.app_label)

    def db_for_write(self, model, **hints):
        return self._route(model._meta.app_label)

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'tenants':
            # tenants app migrations only run on the default DB
            return db == 'default'
        if app_label in TENANT_APPS:
            # tenant apps can migrate on any tenant DB, and on default too
            # (so plain `manage.py migrate` works without a tenant flag)
            return True
        # everything else (Django built-ins like sites, staticfiles, etc.) -> default only
        return db == 'default'