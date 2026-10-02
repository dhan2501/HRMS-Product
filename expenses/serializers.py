from rest_framework import serializers
from .models import ExpenseClaim, ExpenseComment


class ExpenseCommentSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    by_employee_name = serializers.CharField(source='by_employee.full_name', read_only=True)

    class Meta:
        model = ExpenseComment
        fields = [
            'id', 'expense', 'action', 'action_display', 'comment',
            'by_employee', 'by_employee_name', 'created_at',
        ]


class ExpenseClaimSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_color = serializers.ReadOnlyField()
    is_pending = serializers.ReadOnlyField()
    comments = ExpenseCommentSerializer(many=True, read_only=True)

    class Meta:
        model = ExpenseClaim
        fields = [
            'id', 'employee', 'employee_name', 'category', 'category_display',
            'amount', 'expense_date', 'description', 'bill',
            'status', 'status_display', 'status_color', 'is_pending',
            'manager_reviewed_by', 'manager_reviewed_at',
            'finance_reviewed_by', 'finance_reviewed_at',
            'rejected_by', 'rejected_at', 'rejection_reason',
            'reimbursed_by', 'reimbursed_at', 'transaction_reference',
            'comments', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'status', 'manager_reviewed_by', 'manager_reviewed_at',
            'finance_reviewed_by', 'finance_reviewed_at',
            'rejected_by', 'rejected_at',
            'reimbursed_by', 'reimbursed_at',
        ]