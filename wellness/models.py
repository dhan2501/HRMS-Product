from django.db import models
from django.contrib.auth.models import User


class WellnessResource(models.Model):
    CATEGORY_CHOICES = [
        ('breathing', 'Breathing Exercise'),
        ('music', 'Relaxing Music'),
        ('video', 'Relaxation Video'),
        ('quote', 'Motivational Quote'),
        ('tip', 'Wellness Tip'),
        ('game', 'Mind Game / Puzzle'),
    ]

    title           = models.CharField(max_length=200)
    description     = models.TextField(blank=True)
    category        = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='tip')
    resource_url    = models.URLField(
        blank=True,
        help_text='External link — YouTube video, Spotify playlist, article, etc. (optional)'
    )
    duration_minutes = models.PositiveSmallIntegerField(
        null=True, blank=True,
        help_text='Approx. time to complete/listen (optional)'
    )
    is_active   = models.BooleanField(default=True)
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"