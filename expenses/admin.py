from django.contrib import admin
from .models import ExpenseClaim, ExpenseComment


class ExpenseCommentInline(admin.TabularInline):
    model = ExpenseComment
    extra = 0
    readonly_fields = ['action', 'comment', 'by_employee', 'created_at']
    can_delete = False


@admin.register(ExpenseClaim)
class ExpenseClaimAdmin(admin.ModelAdmin):
    list_display = [
        'employee', 'category', 'amount', 'expense_date', 'status',
        'manager_reviewed_by', 'finance_reviewed_by', 'reimbursed_by', 'created_at',
    ]
    list_filter = ['status', 'category']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id', 'description']
    date_hierarchy = 'expense_date'
    inlines = [ExpenseCommentInline]


@admin.register(ExpenseComment)
class ExpenseCommentAdmin(admin.ModelAdmin):
    list_display = ['expense', 'action', 'by_employee', 'created_at']
    list_filter = ['action']