from django.contrib import admin

from tenants.models import RechargeLog, Tenant


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'subdomain', 'plan', 'status', 'expiry_date', 'employee_limit', 'created_at')
    list_filter = ('plan', 'status')
    search_fields = ('name', 'subdomain', 'contact_email')
    readonly_fields = ('db_name', 'activation_key', 'created_at', 'updated_at')


@admin.register(RechargeLog)
class RechargeLogAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'amount', 'days_added', 'payment_reference', 'created_at')
    list_filter = ('tenant',)
    search_fields = ('tenant__name', 'payment_reference')