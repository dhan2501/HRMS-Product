from django.contrib import admin
from .models import Employee, Department, Designation


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'level']
    list_filter = ['department']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'department', 'designation', 'status', 'date_joined']
    list_filter = ['status', 'department', 'employment_type']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']
