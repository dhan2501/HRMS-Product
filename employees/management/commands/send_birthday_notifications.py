# employees/management/commands/send_birthday_notifications.py — NEW FILE
"""
Run this once a day (via cron / Railway Scheduled Job / Celery beat) to wish
every active employee whose birthday is today:

    python manage.py send_birthday_notifications

For each employee whose date_of_birth's day+month matches today:
  - creates an in-app Notification: "🎂 Happy Birthday, <n>!"
  - emails them a nicely formatted "Happy Birthday" message

Safe to run more than once on the same day — it checks whether a birthday
notification has already gone out to that employee today before sending
again, so a duplicate cron trigger won't spam them twice.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone

from employees.birthdays import get_todays_birthday_employees, send_birthday_wishes
from employees.models import Notification


class Command(BaseCommand):
    help = "Send Happy Birthday notifications + emails to employees whose birthday is today."

    def handle(self, *args, **options):
        today = timezone.localdate()
        todays_birthdays = get_todays_birthday_employees(reference_date=today)

        if not todays_birthdays:
            self.stdout.write("No employee birthdays today.")
            return

        sent_count = 0
        for employee in todays_birthdays:
            already_sent = Notification.objects.filter(
                recipient=employee,
                title__startswith="🎂 Happy Birthday",
                created_at__date=today,
            ).exists()
            if already_sent:
                self.stdout.write(f"Skipped {employee.full_name} — already wished today.")
                continue

            send_birthday_wishes(employee, reference_date=today)
            sent_count += 1
            self.stdout.write(self.style.SUCCESS(f"Wished {employee.full_name} ({employee.email})"))

        self.stdout.write(self.style.SUCCESS(f"Done. {sent_count} birthday wish(es) sent."))