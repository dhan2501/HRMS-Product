from functools import wraps

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from employees.models import Employee
from .models import WellnessResource


def admin_required(view_func):
    """Only HR staff/superusers can manage wellness content; employees get bounced to the portal."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_login')
        if not (request.user.is_staff or request.user.is_superuser):
            try:
                Employee.objects.get(user=request.user)
                return redirect('portal_dashboard')
            except Employee.DoesNotExist:
                return redirect('employee_login')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── Wellness Resource List (Admin) ──────────────────────────────────────────────
@login_required
@admin_required
def wellness_list(request):
    category = request.GET.get('category', '')

    resources = WellnessResource.objects.all()
    if category:
        resources = resources.filter(category=category)

    active_count = WellnessResource.objects.filter(is_active=True).count()

    return render(request, 'wellness/wellness_list.html', {
        'resources':        resources,
        'selected_category': category,
        'active_count':     active_count,
        'category_choices': WellnessResource.CATEGORY_CHOICES,
    })


# ── Add Wellness Resource ───────────────────────────────────────────────────────
@login_required
@admin_required
def add_wellness(request):
    if request.method == 'POST':
        title       = request.POST.get('title')
        description = request.POST.get('description', '')
        category    = request.POST.get('category', 'tip')
        resource_url = request.POST.get('resource_url', '')
        duration    = request.POST.get('duration_minutes') or None

        if not title:
            messages.error(request, 'Title is required.')
        else:
            WellnessResource.objects.create(
                title=title,
                description=description,
                category=category,
                resource_url=resource_url,
                duration_minutes=duration,
                created_by=request.user,
            )
            messages.success(request, f'"{title}" added and is now visible to all employees.')
            return redirect('wellness_list')

    return render(request, 'wellness/add_wellness.html', {
        'category_choices': WellnessResource.CATEGORY_CHOICES,
    })


# ── Edit Wellness Resource ──────────────────────────────────────────────────────
@login_required
@admin_required
def edit_wellness(request, pk):
    resource = get_object_or_404(WellnessResource, pk=pk)

    if request.method == 'POST':
        resource.title            = request.POST.get('title')
        resource.description      = request.POST.get('description', '')
        resource.category         = request.POST.get('category', 'tip')
        resource.resource_url     = request.POST.get('resource_url', '')
        resource.duration_minutes = request.POST.get('duration_minutes') or None
        resource.is_active        = request.POST.get('is_active') == 'on'
        resource.save()
        messages.success(request, f'"{resource.title}" updated.')
        return redirect('wellness_list')

    return render(request, 'wellness/add_wellness.html', {
        'resource': resource,
        'is_edit':  True,
        'category_choices': WellnessResource.CATEGORY_CHOICES,
    })


# ── Delete Wellness Resource ────────────────────────────────────────────────────
@login_required
@admin_required
def delete_wellness(request, pk):
    resource = get_object_or_404(WellnessResource, pk=pk)
    if request.method == 'POST':
        title = resource.title
        resource.delete()
        messages.success(request, f'"{title}" removed.')
    return redirect('wellness_list')