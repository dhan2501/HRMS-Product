from django.core.management.base import BaseCommand, CommandError

from tenants.models import Tenant
from tenants.provisioning import provision_tenant_database


class Command(BaseCommand):
    help = "Create a new tenant (customer) and provision its database."

    def add_arguments(self, parser):
        parser.add_argument('--name', required=True, help="Company name")
        parser.add_argument('--subdomain', required=True, help="e.g. acme")
        parser.add_argument('--plan', default='basic', choices=['basic', 'pro', 'enterprise'])
        parser.add_argument('--employee-limit', type=int, default=25)
        parser.add_argument(
            '--modules', default='attendance,leaves',
            help="Comma-separated: attendance,leaves,payroll,recruitment,wellness,events,messaging,helpcenter",
        )

    def handle(self, *args, **options):
        if Tenant.objects.filter(subdomain=options['subdomain']).exists():
            raise CommandError(f"Subdomain '{options['subdomain']}' is already in use.")

        tenant = Tenant.objects.create(
            name=options['name'],
            subdomain=options['subdomain'],
            plan=options['plan'],
            employee_limit=options['employee_limit'],
            enabled_modules=[m.strip() for m in options['modules'].split(',') if m.strip()],
            status='suspended',
        )
        provision_tenant_database(tenant)

        self.stdout.write(self.style.SUCCESS(
            f"Tenant '{tenant.name}' created (id={tenant.id}, subdomain={tenant.subdomain}).\n"
            f"Activate it via the superadmin console (Recharge), or set status='active' "
            f"and an expiry_date directly in Django admin."
        ))