import secrets

from django.db import models
from django.utils import timezone


# Modules that can be enabled/disabled per tenant.
# This list should match the tenant-specific apps in INSTALLED_APPS.
AVAILABLE_MODULES = [
    ('attendance', 'Attendance'),
    ('leaves', 'Leaves'),
    ('payroll', 'Payroll'),
    ('recruitment', 'Recruitment'),
    ('wellness', 'Wellness'),
    ('events', 'Events'),
    ('messaging', 'Messaging'),
    ('helpcenter', 'Help Center'),
]

PLAN_CHOICES = [
    ('basic', 'Basic'),
    ('pro', 'Pro'),
    ('enterprise', 'Enterprise'),
]

STATUS_CHOICES = [
    ('active', 'Active'),
    ('expired', 'Expired'),
    ('suspended', 'Suspended'),  # manually disabled by you (e.g. non-payment, abuse)
]


def generate_activation_key():
    return secrets.token_hex(16)


class Tenant(models.Model):
    """
    One row = one customer/company you're selling the HRMS to.
    Each tenant has its own database (identified by db_name), holding its
    own employees, attendance, leaves, payroll, etc.

    This model's own data always lives in the 'default' database (never in a
    tenant database), so all customers can be managed from one place.
    """
    name = models.CharField(max_length=255, help_text="Company name, e.g. 'Acme Pvt Ltd'")
    subdomain = models.SlugField(
        unique=True,
        help_text="e.g. 'acme' -> acme.yourhrms.com. For local testing, ?tenant=acme also works.",
    )
    db_name = models.CharField(max_length=100, unique=True, editable=False)

    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='basic')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='suspended')
    activation_key = models.CharField(max_length=64, unique=True, default=generate_activation_key)

    expiry_date = models.DateField(
        null=True, blank=True,
        help_text="After this date the dashboard locks until the tenant is recharged.",
    )
    employee_limit = models.PositiveIntegerField(default=25)
    enabled_modules = models.JSONField(
        default=list, blank=True,
        help_text="Which modules are enabled for this customer, e.g. ['attendance','leaves']",
    )

    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.subdomain})"

    def save(self, *args, **kwargs):
        if not self.db_name:
            self.db_name = f"tenant_{self.subdomain}".replace('-', '_')
        super().save(*args, **kwargs)

    def is_active(self):
        """Whether to grant access — the single source of truth for this."""
        if self.status != 'active':
            return False
        if self.expiry_date and self.expiry_date < timezone.now().date():
            return False
        return True

    def days_remaining(self):
        if not self.expiry_date:
            return None
        delta = self.expiry_date - timezone.now().date()
        return delta.days

    def module_enabled(self, module_name):
        return module_name in (self.enabled_modules or [])

    def current_employee_count(self):
        """Reads the employee count from this tenant's own database."""
        from tenants.db_router import set_current_tenant_db
        from tenants.utils import register_tenant_database
        try:
            from employees.models import Employee
            alias = register_tenant_database(self)
            prev = set_current_tenant_db(alias)
            try:
                return Employee.objects.using(alias).count()
            finally:
                set_current_tenant_db(prev)
        except Exception:
            return None


class RechargeLog(models.Model):
    """
    Record of every payment/recharge — the core of 'how recharging works'.
    Each recharge extends tenant.expiry_date.
    """
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='recharges')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    days_added = models.PositiveIntegerField(default=30)
    payment_reference = models.CharField(
        max_length=100, blank=True,
        help_text="Razorpay/Stripe payment ID, or a manual note",
    )
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tenant.name} — ₹{self.amount} (+{self.days_added} days)"