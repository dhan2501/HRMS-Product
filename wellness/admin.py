from django.contrib import admin
from .models import WellnessResource


@admin.register(WellnessResource)
class WellnessResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'duration_minutes', 'is_active', 'created_by', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['title', 'description']