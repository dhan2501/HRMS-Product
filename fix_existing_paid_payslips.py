"""
Multi-tenant aware fix + verify script.

This project routes 'tenant apps' (employees, payroll, etc.) to whichever
database tenants.db_router.set_current_tenant_db() has set for the current
thread. A plain `manage.py shell` session has no tenant set, so we loop
through every tenant, register its database, and set it as current before
touching Payslip — exactly like the request middleware does for a normal
web request.

Run from your project root (same folder as manage.py):
    python manage.py shell < fix_and_verify_payslips.py
"""
from django.utils import timezone
from tenants.models import Tenant
from tenants.utils import register_tenant_database
from tenants.db_router import set_current_tenant_db, clear_current_tenant_db
from payroll.models import Payslip

tenants = Tenant.objects.all()
print(f"Found {tenants.count()} tenant(s).\n")

total_fixed = 0

for tenant in tenants:
    alias = register_tenant_database(tenant)
    set_current_tenant_db(alias)

    try:
        locked = Payslip.objects.filter(status='paid', is_approved=False)
        n = locked.count()

        print(f"[{tenant.db_name}] locked paid payslips: {n}")
        for p in locked:
            print(f"    - {p.employee.full_name} | {p.month}/{p.year} | Rs.{p.net_salary}")

        updated = locked.update(is_approved=True, approved_at=timezone.now())
        total_fixed += updated

        still_locked = Payslip.objects.filter(status='paid', is_approved=False).count()
        print(f"    -> approved {updated}, remaining locked: {still_locked}\n")
    finally:
        clear_current_tenant_db()

print(f"DONE. Total payslips approved & released across all tenants: {total_fixed}")