from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('holiday', 'Holiday'),
        ('event', 'Event'),
    ]

    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type  = models.CharField(max_length=10, choices=EVENT_TYPE_CHOICES, default='event')
    date        = models.DateField(help_text='Start date')
    end_date    = models.DateField(null=True, blank=True, help_text='Leave blank for a single-day event')
    is_active   = models.BooleanField(default=True)
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()}) - {self.date}"

    @property
    def is_multi_day(self):
        return self.end_date and self.end_date != self.date

    @property
    def is_past(self):
        from datetime import date
        last_day = self.end_date or self.date
        return last_day < date.today()