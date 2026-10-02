from rest_framework import viewsets, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone

from .models import Tenant, RechargeLog
from .serializers import TenantSerializer, RechargeLogSerializer
from .provisioning import provision_tenant_database


class IsPlatformStaff(permissions.BasePermission):
    """This app manages customers of the platform itself — staff/superuser only,
    never exposed to a regular tenant's own users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class TenantViewSet(viewsets.ModelViewSet):
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsPlatformStaff]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'subdomain', 'contact_email']

    def get_queryset(self):
        qs = super().get_queryset()
        status_param = self.request.query_params.get('status')
        plan = self.request.query_params.get('plan')
        if status_param:
            qs = qs.filter(status=status_param)
        if plan:
            qs = qs.filter(plan=plan)
        return qs

    def perform_create(self, serializer):
        tenant = serializer.save()
        provision_tenant_database(tenant)

    @action(detail=True, methods=['post'])
    def recharge(self, request, pk=None):
        tenant = self.get_object()
        amount = request.data.get('amount')
        days_added = int(request.data.get('days_added', 30))
        if amount is None:
            return Response({'detail': 'amount is required.'}, status=400)

        RechargeLog.objects.create(
            tenant=tenant,
            amount=amount,
            days_added=days_added,
            payment_reference=request.data.get('payment_reference', ''),
            note=request.data.get('note', ''),
        )
        base = tenant.expiry_date if tenant.expiry_date and tenant.expiry_date > timezone.now().date() else timezone.now().date()
        tenant.expiry_date = base + timedelta(days=days_added)
        tenant.status = 'active'
        tenant.save()
        return Response(self.get_serializer(tenant).data)

    @action(detail=True, methods=['post'])
    def suspend(self, request, pk=None):
        tenant = self.get_object()
        tenant.status = 'suspended'
        tenant.save()
        return Response(self.get_serializer(tenant).data)


class RechargeLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RechargeLog.objects.select_related('tenant').all()
    serializer_class = RechargeLogSerializer
    permission_classes = [IsPlatformStaff]

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = self.request.query_params.get('tenant')
        if tenant:
            qs = qs.filter(tenant_id=tenant)
        return qs