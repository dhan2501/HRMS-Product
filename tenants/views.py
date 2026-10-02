from datetime import timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from tenants.forms import RechargeForm, TenantForm
from tenants.models import Tenant
from tenants.provisioning import provision_tenant_database

# NOTE: This entire app is for YOU (the platform owner) only — not for customers.
# Every view below is protected by @staff_member_required, pointed at our own
# console login page (tenants:login) instead of Django's default /admin/login/.

CONSOLE_LOGIN_URL = '/tenants/login/'


def console_login(request):
    """
    Standalone login page for the platform console, styled to match the
    dashboard (dark theme) rather than Django's default admin login screen.
    Only staff/superuser accounts are allowed in.
    """
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('tenants:list')

    error = None
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                return redirect('tenants:list')
            error = "This account does not have console access."
        else:
            error = "Incorrect username or password."
    else:
        form = AuthenticationForm()

    return render(request, 'tenants/console_login.html', {'form': form, 'error': error})


def console_logout(request):
    logout(request)
    return redirect('tenants:login')


@staff_member_required(login_url=CONSOLE_LOGIN_URL)
def tenant_list(request):
    tenants = list(Tenant.objects.all())
    today = timezone.now().date()

    active_count = sum(1 for t in tenants if t.is_active())
    expiring_soon = sum(
        1 for t in tenants
        if t.is_active() and t.expiry_date and 0 <= (t.expiry_date - today).days <= 7
    )
    suspended_count = sum(1 for t in tenants if t.status == 'suspended')

    context = {
        'tenants': tenants,
        'stats': {
            'total': len(tenants),
            'active': active_count,
            'expiring_soon': expiring_soon,
            'suspended': suspended_count,
        },
    }
    return render(request, 'tenants/tenant_list.html', context)


@staff_member_required(login_url=CONSOLE_LOGIN_URL)
def tenant_create(request):
    if request.method == 'POST':
        form = TenantForm(request.POST)
        if form.is_valid():
            tenant = form.save(commit=False)
            tenant.status = 'suspended'  # not active until first recharge
            tenant.save()
            tenant.enabled_modules = form.cleaned_data['enabled_modules']
            tenant.save()

            provision_tenant_database(tenant)

            messages.success(
                request,
                f"'{tenant.name}' created (subdomain: {tenant.subdomain}). "
                f"Its database has been provisioned — activate it with a recharge.",
            )
            return redirect('tenants:list')
    else:
        form = TenantForm()

    return render(request, 'tenants/tenant_form.html', {'form': form})


@staff_member_required(login_url=CONSOLE_LOGIN_URL)
def tenant_edit(request, pk):
    """
    Edit an existing tenant's plan, employee limit, and — importantly —
    toggle modules on/off (this is how you deactivate a module for a
    customer: just uncheck it here and save).
    """
    tenant = get_object_or_404(Tenant, pk=pk)

    if request.method == 'POST':
        form = TenantForm(request.POST, instance=tenant)
        if form.is_valid():
            updated = form.save(commit=False)
            updated.enabled_modules = form.cleaned_data['enabled_modules']
            updated.save()
            messages.success(request, f"'{updated.name}' has been updated.")
            return redirect('tenants:list')
    else:
        form = TenantForm(instance=tenant, initial={'enabled_modules': tenant.enabled_modules})

    return render(request, 'tenants/tenant_form.html', {'form': form, 'tenant': tenant, 'is_edit': True})


@staff_member_required(login_url=CONSOLE_LOGIN_URL)
def tenant_recharge(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)

    if request.method == 'POST':
        form = RechargeForm(request.POST)
        if form.is_valid():
            recharge = form.save(commit=False)
            recharge.tenant = tenant
            recharge.save()

            today = timezone.now().date()
            base_date = tenant.expiry_date if (tenant.expiry_date and tenant.expiry_date > today) else today
            tenant.expiry_date = base_date + timedelta(days=recharge.days_added)
            tenant.status = 'active'
            tenant.save()

            messages.success(
                request,
                f"'{tenant.name}' is now active, valid until {tenant.expiry_date}.",
            )
            return redirect('tenants:list')
    else:
        form = RechargeForm()

    return render(request, 'tenants/recharge_form.html', {'form': form, 'tenant': tenant})


@staff_member_required(login_url=CONSOLE_LOGIN_URL)
def tenant_suspend(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)
    if request.method == 'POST':
        tenant.status = 'suspended'
        tenant.save()
        messages.info(request, f"'{tenant.name}' has been suspended.")
    return redirect('tenants:list')