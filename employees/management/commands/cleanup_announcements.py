"""
Deletes Announcement rows whose 24-hour expires_at has passed, along with
their linked Notification rows (CASCADE).

Run manually:
    python manage.py cleanup_announcements

Recommended: schedule this every 15-30 minutes via cron / celery beat so
announcements disappear close to exactly 24h later, even if nobody opens
the app in between (the app also does this lazily on page load, but a
cron job guarantees it).

Example cron entry (every 15 min):
    */15 * * * * cd /path/to/project && /path/to/venv/bin/python manage.py cleanup_announcements
"""
from django.core.management.base import BaseCommand
from employees.models import Announcement


class Command(BaseCommand):
    help = "Delete Announcement rows (and their notifications) past their 24-hour expiry."

    def handle(self, *args, **options):
        deleted_count, _ = Announcement.objects.cleanup_expired()
        if deleted_count:
            self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} expired announcement row(s)."))
        else:
            self.stdout.write("No expired announcements to delete.")