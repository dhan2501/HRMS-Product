from rest_framework import serializers
from .models import Tenant, RechargeLog


class RechargeLogSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True)

    class Meta:
        model = RechargeLog
        fields = [
            'id', 'tenant', 'tenant_name', 'amount', 'days_added',
            'payment_reference', 'note', 'created_at',
        ]


class TenantSerializer(serializers.ModelSerializer):
    is_active_now = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    current_employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = [
            'id', 'name', 'subdomain', 'plan', 'status',
            'expiry_date', 'employee_limit', 'enabled_modules',
            'contact_email', 'contact_phone',
            'is_active_now', 'days_remaining', 'current_employee_count',
            'created_at', 'updated_at',
        ]
        # db_name and activation_key are provisioning internals — never
        # exposed for editing over the general-purpose API.
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_is_active_now(self, obj):
        return obj.is_active()

    def get_days_remaining(self, obj):
        return obj.days_remaining()

    def get_current_employee_count(self, obj):
        return obj.current_employee_count()