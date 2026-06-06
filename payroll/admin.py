from django.contrib import admin
from .models import SalaryComponent, SalaryStructure, Payslip

admin.site.register(SalaryComponent)
admin.site.register(SalaryStructure)

@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'gross_salary', 'net_salary', 'status']
    list_filter = ['status', 'year', 'month']
