from django.db import models
from employees.models import Employee


class LeaveType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    days_allowed = models.PositiveSmallIntegerField(default=0)
    is_paid = models.BooleanField(default=True)
    carry_forward = models.BooleanField(default=False)
    max_carry_forward_days = models.PositiveSmallIntegerField(default=0)
    description = models.TextField(blank=True)
    is_short_leave = models.BooleanField(
        default=False,
        help_text=(
            "Mark this leave type as a 'Short Leave' (a few hours off, not a full day). "
            "When a request of this type is approved, the day is recorded in Attendance as "
            "'Short Leave' and a partial (not full-day) deduction is applied in payroll, "
            "instead of being skipped like a normal full-day leave."
        ),
    )

    def __str__(self):
        return self.name


class LeaveBalance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField()
    total_days = models.DecimalField(max_digits=5, decimal_places=1)
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    pending_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    @property
    def available_days(self):
        return self.total_days - self.used_days - self.pending_days

    class Meta:
        unique_together = ['employee', 'leave_type', 'year']


# class LeaveRequest(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#         ('cancelled', 'Cancelled'),
#     ]

#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
#     leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
#     start_date = models.DateField()
#     end_date = models.DateField()
#     days = models.DecimalField(max_digits=4, decimal_places=1)
#     reason = models.TextField()
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     approved_by = models.ForeignKey(
#         Employee, on_delete=models.SET_NULL, null=True, blank=True,
#         related_name='approved_leaves'
#     )
#     approved_at = models.DateTimeField(null=True, blank=True)
#     rejection_reason = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.DecimalField(max_digits=4, decimal_places=1)
    is_half_day = models.BooleanField(default=False)
    half_day_session = models.CharField(
        max_length=12,
        choices=[('first_half', 'First Half'), ('second_half', 'Second Half')],
        blank=True, null=True
    )
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_leaves'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type.name} ({self.start_date})"


# Existing models ke neeche add karo

class LeaveComment(models.Model):
    leave      = models.ForeignKey(LeaveRequest, on_delete=models.CASCADE, related_name='comments')
    commented_by = models.ForeignKey('employees.Employee', on_delete=models.CASCADE)
    comment    = models.TextField()
    action     = models.CharField(max_length=20, choices=[
        ('comment', 'Comment'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('forwarded', 'Forwarded'),
    ], default='comment')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.commented_by.full_name} - {self.action}"

class LeaveBalance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField()
    total_days = models.DecimalField(max_digits=5, decimal_places=1)
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    pending_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    # EL (Earned Leave) ke liye monthly auto-accrual track karne ke liye.
    last_accrual_date = models.DateField(null=True, blank=True)

    @property
    def available_days(self):
        return self.total_days - self.used_days - self.pending_days

    class Meta:
        unique_together = ['employee', 'leave_type', 'year']