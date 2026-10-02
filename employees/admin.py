# from django.contrib import admin
# from .models import Employee, Department, Designation


# @admin.register(Department)
# class DepartmentAdmin(admin.ModelAdmin):
#     list_display = ['name', 'code', 'created_at']
#     search_fields = ['name', 'code']


# @admin.register(Designation)
# class DesignationAdmin(admin.ModelAdmin):
#     list_display = ['title', 'department', 'level']
#     list_filter = ['department']


# @admin.register(Employee)
# class EmployeeAdmin(admin.ModelAdmin):
#     list_display = ['employee_id', 'full_name', 'department', 'designation', 'status', 'date_joined']
#     list_filter = ['status', 'department', 'employment_type']
#     search_fields = ['first_name', 'last_name', 'email', 'employee_id']

from django.contrib import admin
from .models import (
    Employee, Department, Designation,
    PerformanceReview, PerformanceGoal,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'level']
    list_filter = ['department']
    search_fields = ['title']


class PerformanceGoalInline(admin.TabularInline):
    model = PerformanceGoal
    extra = 1


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'reviewer', 'review_period_type',
        'period_start', 'period_end', 'overall_rating', 'status',
    ]
    list_filter = ['review_period_type', 'status', 'overall_rating', 'period_end']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    autocomplete_fields = ['employee', 'reviewer']
    inlines = [PerformanceGoalInline]
    date_hierarchy = 'period_end'


# ── Performance section inline inside the Employee admin page ──────────────
class PerformanceReviewInline(admin.TabularInline):
    """
    Lets HR/Admin see and add Performance reviews directly from the
    Employee edit page in Django admin — this is the 'Performance section'
    inside the employee admin.
    """
    model = PerformanceReview
    fk_name = 'employee'
    extra = 0
    fields = ['review_period_type', 'period_start', 'period_end', 'reviewer', 'overall_rating', 'status']
    show_change_link = True


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id', 'full_name', 'department', 'designation',
        'reporting_manager', 'status', 'date_joined',
    ]
    list_filter = ['status', 'department', 'employment_type']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']
    autocomplete_fields = ['reporting_manager', 'department', 'designation']
    inlines = [PerformanceReviewInline]

    fieldsets = (
        ('Basic Info', {
            'fields': (
                'user', 'employee_id', 'first_name', 'last_name', 'email',
                'phone', 'date_of_birth', 'gender', 'photo',
            )
        }),
        ('Job Details', {
            'fields': (
                'department', 'designation', 'reporting_manager',
                'date_joined', 'employment_type', 'status',
            )
        }),
        ('Status Tracking', {
            'fields': ('status_reason', 'status_changed_at', 'hold_until'),
        }),
        ('Other', {
            'fields': (
                'address', 'emergency_contact_name', 'emergency_contact_phone',
            )
        }),
    )