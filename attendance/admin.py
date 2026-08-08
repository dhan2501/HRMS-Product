from django.contrib import admin
from .models import AttendanceRecord, Holiday, ShiftTiming, PunchLog


@admin.register(ShiftTiming)
class ShiftTimingAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_time', 'end_time', 'working_hours', 'grace_minutes', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(PunchLog)
class PunchLogAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'punch_type', 'timestamp']
    list_filter = ['punch_type', 'date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    autocomplete_fields = ['employee']
    date_hierarchy = 'date'


@admin.register(AttendanceRecord)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'date', 'status', 'check_in', 'check_out',
        'break_count', 'total_break_minutes', 'working_hours',
    ]
    list_filter = ['status', 'date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    date_hierarchy = 'date'


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'is_optional']