from django.contrib import admin
from .models import SalaryComponent, SalaryStructure, Payslip

admin.site.register(SalaryComponent)


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['employee', 'gross_salary', 'tax_regime', 'esi_deduction', 'monthly_tds', 'net_salary', 'effective_from']
    list_filter = ['tax_regime']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']


@admin.register(Payslip)
class PayslipAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'month', 'year', 'tax_regime', 'gross_salary',
        'overtime_amount', 'bonus', 'incentive', 'esi_deduction',
        'tds', 'lop_days', 'net_salary', 'status',
    ]
    list_filter = ['status', 'tax_regime', 'year', 'month']