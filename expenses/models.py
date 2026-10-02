from django.db import models
from employees.models import Employee


class ExpenseClaim(models.Model):
    CATEGORY_CHOICES = [
        ('travel', 'Travel'),
        ('food', 'Food'),
        ('cab', 'Cab'),
        ('hotel', 'Hotel'),
        ('other', 'Other'),
    ]

    # ── Workflow: pending_manager → pending_finance → approved → reimbursed ──
    # Either stage can instead end in 'rejected'. The employee can 'cancel'
    # their own claim only while it's still pending_manager.
    STATUS_CHOICES = [
        ('pending_manager', 'Pending Manager Approval'),
        ('pending_finance', 'Pending Finance Approval'),
        ('approved', 'Approved'),
        ('reimbursed', 'Reimbursed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='expense_claims')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    expense_date = models.DateField()
    description = models.TextField()
    bill = models.FileField(
        upload_to='expense_bills/', blank=True, null=True,
        help_text='Scanned bill / receipt for this expense.'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_manager')

    # ── Reporting Manager stage ────────────────────────────────────────────
    manager_reviewed_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='manager_reviewed_expenses'
    )
    manager_reviewed_at = models.DateTimeField(null=True, blank=True)

    # ── Finance / HR stage ──────────────────────────────────────────────────
    finance_reviewed_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='finance_reviewed_expenses'
    )
    finance_reviewed_at = models.DateTimeField(null=True, blank=True)

    # ── Rejection (can happen at either stage) ──────────────────────────────
    rejected_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='rejected_expenses'
    )
    rejected_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # ── Reimbursement ────────────────────────────────────────────────────────
    reimbursed_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reimbursed_expenses'
    )
    reimbursed_at = models.DateTimeField(null=True, blank=True)
    transaction_reference = models.CharField(
        max_length=100, blank=True,
        help_text='Bank transaction / UTR reference for the reimbursement payout.'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_category_display()} - Rs.{self.amount}"

    @property
    def is_pending(self):
        return self.status in ('pending_manager', 'pending_finance')

    @property
    def status_color(self):
        """Tailwind color token used consistently across all expense templates."""
        return {
            'pending_manager': 'amber',
            'pending_finance': 'blue',
            'approved': 'emerald',
            'reimbursed': 'brand',
            'rejected': 'red',
            'cancelled': 'slate',
        }.get(self.status, 'slate')


class ExpenseComment(models.Model):
    """Audit trail entry — one row per action taken on an ExpenseClaim."""
    ACTION_CHOICES = [
        ('submitted', 'Submitted'),
        ('manager_approved', 'Approved by Manager'),
        ('manager_rejected', 'Rejected by Manager'),
        ('finance_approved', 'Approved by Finance'),
        ('finance_rejected', 'Rejected by Finance'),
        ('reimbursed', 'Marked Reimbursed'),
        ('cancelled', 'Cancelled'),
        ('note', 'Note'),
    ]

    expense = models.ForeignKey(ExpenseClaim, on_delete=models.CASCADE, related_name='comments')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    comment = models.TextField(blank=True)
    by_employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='expense_comments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        who = self.by_employee.full_name if self.by_employee else 'System'
        return f"{self.expense_id} - {self.get_action_display()} by {who}"