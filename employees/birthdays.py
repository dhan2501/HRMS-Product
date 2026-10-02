# employees/birthdays.py — FULL FILE (replace existing)
"""
Birthday module.

Small, self-contained set of helpers used by:
  - portal_views.portal_dashboard        -> "Birthdays this month" widget + today's banner
  - portal_views.portal_birthday_calendar -> full calendar of all employee birthdays
  - management/commands/send_birthday_notifications.py -> the daily cron job that
    creates the in-app Notification + sends the "Happy Birthday" email

Kept in one place so 'who counts as having a birthday today/this month' and
'what the birthday message looks like' are each defined exactly once.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone

from .models import Employee, Notification


def _active_employees_with_dob():
    return Employee.objects.filter(
        status='active'
    ).exclude(date_of_birth__isnull=True)


def get_month_birthdays(month, reference_date=None):
    """
    All active employees whose date_of_birth falls in the given month
    (1-12), sorted by day of month. Each employee gets two extra
    (non-DB) attributes attached for template convenience:
      - bday_day   : the day-of-month of their birthday (int)
      - is_today   : True if their birthday is today
    """
    today = reference_date or timezone.localdate()
    employees = list(_active_employees_with_dob().filter(date_of_birth__month=month))
    for emp in employees:
        emp.bday_day = emp.date_of_birth.day
        emp.is_today = (emp.date_of_birth.month == today.month and emp.date_of_birth.day == today.day)
    employees.sort(key=lambda e: e.bday_day)
    return employees


def get_birthdays_this_month(reference_date=None):
    """Convenience wrapper: this calendar month's birthdays, today first-ish (sorted by day)."""
    today = reference_date or timezone.localdate()
    return get_month_birthdays(today.month, reference_date=today)


def get_todays_birthday_employees(reference_date=None):
    """Active employees whose birthday is exactly today."""
    today = reference_date or timezone.localdate()
    return _active_employees_with_dob().filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day,
    )


def turning_age(employee, reference_date=None):
    """How old `employee` is turning on their next/current birthday."""
    today = reference_date or timezone.localdate()
    if not employee.date_of_birth:
        return None
    return today.year - employee.date_of_birth.year


def get_next_upcoming_birthday(reference_date=None):
    """
    Across ALL active employees, find whoever's birthday is soonest from
    today (today counts as 0 days away). Wraps around the year-end.
    Returns (employee_or_None, days_away_or_None).
    """
    today = reference_date or timezone.localdate()
    best_emp, best_days = None, None

    for emp in _active_employees_with_dob():
        dob = emp.date_of_birth
        try:
            this_year_bday = dob.replace(year=today.year)
        except ValueError:
            this_year_bday = dob.replace(year=today.year, day=28)  # Feb 29 fallback

        if this_year_bday >= today:
            next_bday = this_year_bday
        else:
            try:
                next_bday = dob.replace(year=today.year + 1)
            except ValueError:
                next_bday = dob.replace(year=today.year + 1, day=28)

        days_away = (next_bday - today).days
        if best_days is None or days_away < best_days:
            best_days = days_away
            best_emp = emp

    return best_emp, best_days


def send_birthday_wishes(employee, reference_date=None):
    """
    Sends the 🎉 Happy Birthday wish to a single employee:
      1. An in-app Notification (shows in their bell icon + notifications page).
      2. A nicely formatted email to their registered email address.

    Idempotent-ish: caller (the management command) is responsible for making
    sure this only runs once per employee per day.
    """
    today = reference_date or timezone.localdate()
    age = turning_age(employee, today)

    # 1. In-app notification
    Notification.objects.create(
        recipient=employee,
        title=f"🎂 Happy Birthday, {employee.first_name}!",
        message=(
            f"Wishing you a fantastic birthday, {employee.first_name}! "
            f"May your day be filled with joy, cake, and well-deserved celebration. "
            f"Have a wonderful year ahead! 🎉"
        ),
        link_name='portal_dashboard',
    )

    # 2. Email
    if employee.email:
        subject = f"🎉 Happy Birthday, {employee.first_name}!"
        html_message = render_to_string('emails/birthday_wish.html', {
            'employee': employee,
            'age': age,
        })
        plain_message = strip_tags(html_message)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', None),
            recipient_list=[employee.email],
            html_message=html_message,
            fail_silently=True,
        )

    return True