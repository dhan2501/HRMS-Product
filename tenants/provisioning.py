from django.core.management import call_command

from tenants.db_router import TENANT_APPS
from tenants.utils import register_tenant_database


def provision_tenant_database(tenant):
    """
    Called the moment a new tenant is created (from views.tenant_create):
    1. Registers/creates its database file
    2. Runs migrations for every tenant app (employees, attendance, leaves, ...)
       on that database

    This gives every new customer a fresh, empty, isolated HRMS database.
    """
    alias = register_tenant_database(tenant)

    for app_label in sorted(TENANT_APPS):
        try:
            call_command('migrate', app_label, database=alias, interactive=False, verbosity=0)
        except Exception as exc:  # one app's migration failing shouldn't block the rest
            print(f"[tenants] Warning: '{app_label}' migrate on '{alias}' failed: {exc}")

    return alias