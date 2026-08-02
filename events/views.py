from functools import wraps
from datetime import date

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from employees.models import Employee
from .models import Event


def admin_required(view_func):
    """Only HR staff/superusers can manage events; employees get bounced to the portal."""
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


# ── Event List (Admin) ─────────────────────────────────────────────────────────
@login_required
@admin_required
def event_list(request):
    event_type = request.GET.get('type', '')
    show       = request.GET.get('show', 'upcoming')  # upcoming | past | all

    events = Event.objects.all()

    if event_type in ['holiday', 'event']:
        events = events.filter(event_type=event_type)

    today = date.today()
    if show == 'upcoming':
        events = events.filter(date__gte=today)
    elif show == 'past':
        events = events.filter(date__lt=today)

    holiday_count = Event.objects.filter(event_type='holiday', date__gte=today).count()
    event_count   = Event.objects.filter(event_type='event', date__gte=today).count()

    return render(request, 'events/event_list.html', {
        'events':          events,
        'selected_type':   event_type,
        'selected_show':   show,
        'holiday_count':   holiday_count,
        'event_count':     event_count,
        'today':           today,
    })


# ── Add Event ──────────────────────────────────────────────────────────────────
@login_required
@admin_required
def add_event(request):
    if request.method == 'POST':
        title       = request.POST.get('title')
        description = request.POST.get('description', '')
        event_type  = request.POST.get('event_type', 'event')
        event_date  = request.POST.get('date')
        end_date    = request.POST.get('end_date') or None

        if not title or not event_date:
            messages.error(request, 'Title and Date are required.')
        else:
            Event.objects.create(
                title=title,
                description=description,
                event_type=event_type,
                date=event_date,
                end_date=end_date,
                created_by=request.user,
            )
            messages.success(request, f'"{title}" added and is now visible to all employees.')
            return redirect('event_list')

    return render(request, 'events/add_event.html', {'today': date.today()})


# ── Edit Event ─────────────────────────────────────────────────────────────────
@login_required
@admin_required
def edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk)

    if request.method == 'POST':
        event.title       = request.POST.get('title')
        event.description = request.POST.get('description', '')
        event.event_type  = request.POST.get('event_type', 'event')
        event.date        = request.POST.get('date')
        event.end_date    = request.POST.get('end_date') or None
        event.is_active   = request.POST.get('is_active') == 'on'
        event.save()
        messages.success(request, f'"{event.title}" updated.')
        return redirect('event_list')

    return render(request, 'events/add_event.html', {'event': event, 'is_edit': True})


# ── Delete Event ───────────────────────────────────────────────────────────────
@login_required
@admin_required
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        title = event.title
        event.delete()
        messages.success(request, f'"{title}" removed.')
    return redirect('event_list')