from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(
        'Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='managed_department'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Designation(models.Model):
    title = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='designations')
    level = models.PositiveSmallIntegerField(default=1)  # 1=junior, 5=senior

    def __str__(self):
        return f"{self.title} ({self.department.name})"

    class Meta:
        ordering = ['title']

class Employee(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
        ('terminated', 'Terminated'),
    ]
    EMPLOYMENT_TYPE = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    photo = models.ImageField(upload_to='employee_photos/', null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, related_name='employees')
    date_joined = models.DateField()
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE, default='full_time')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)

    # ✅ Deactivate / Hold tracking
    status_reason = models.TextField(
        blank=True,
        help_text="Reason for the current status (resignation, long leave, termination, etc.)"
    )
    status_changed_at = models.DateTimeField(null=True, blank=True)
    hold_until = models.DateField(
        null=True, blank=True,
        help_text="Expected return / reactivation date — for employees on long leave (6 months, 1 year, etc.)"
    )

    # ✅ Reporting hierarchy — connects an employee to their reporting senior / manager
    reporting_manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='team_members',
        help_text="The senior / manager this employee reports to."
    )

    # ✅ Punch In/Out — Shift & working hours (Super Admin configurable)
    shift = models.ForeignKey(
        'attendance.ShiftTiming', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='employees',
        help_text="Assigned shift timing — controls the expected start time and late marking."
    )
    standard_working_hours = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        help_text="Working hours required per day for this employee. Leave blank to use the shift's default."
    )
    biometric_id = models.CharField(
        max_length=30, null=True, blank=True, unique=True,
        help_text="User ID / PIN configured for this employee on the fingerprint/biometric punch machine."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def effective_working_hours(self):
        """Employee's own override if set, else their shift's working_hours, else a default of 8."""
        if self.standard_working_hours:
            return self.standard_working_hours
        if self.shift:
            return self.shift.working_hours
        return 8

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"

    class Meta:
        ordering = ['first_name', 'last_name']


class EmployeeRole(models.Model):
    """Defines what access each department/designation has."""
    ROLE_CHOICES = [
        ('hr_manager', 'HR Manager'),
        ('ceo', 'CEO'),
        ('pmo', 'Product Manager Officer'),
        ('team_leader', 'Team Leader'),
        ('employee', 'Employee'),
    ]
    employee    = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='role')
    role        = models.CharField(max_length=30, choices=ROLE_CHOICES, default='employee')
    can_approve_leave    = models.BooleanField(default=False)
    can_approve_wfh      = models.BooleanField(default=False)
    can_view_team_salary = models.BooleanField(default=False)
    can_assign_project   = models.BooleanField(default=False)
    manages_department   = models.ForeignKey(
        'Department', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='managers'
    )

    def __str__(self):
        return f"{self.employee.full_name} - {self.role}"


class Project(models.Model):
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
    ]
    name        = models.CharField(max_length=200)
    code        = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    department  = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, related_name='projects')
    manager     = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='managed_projects')
    members     = models.ManyToManyField(Employee, related_name='projects', blank=True)
    start_date  = models.DateField()
    end_date    = models.DateField(null=True, blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        ordering = ['-created_at']


class EmployeeStatusLog(models.Model):
    """
    Audit trail every time an employee is deactivated, put on hold
    (long leave), terminated, or reactivated. Keeps the reason and
    who did it, so HR always has a record of why someone's data
    changed state.
    """
    employee        = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='status_logs')
    previous_status = models.CharField(max_length=20)
    new_status      = models.CharField(max_length=20)
    reason          = models.TextField()
    hold_until      = models.DateField(null=True, blank=True)
    changed_by      = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.employee.full_name}: {self.previous_status} → {self.new_status} ({self.changed_at:%d %b %Y})"


# ── Performance Management ──────────────────────────────────────────────────

class PerformanceReview(models.Model):
    """
    A periodic performance review/appraisal for an employee, usually filled
    by the employee's reporting manager. Shows up in the 'Performance'
    section of the employee's admin/profile page.
    """
    PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half Yearly'),
        ('annual', 'Annual'),
    ]
    RATING_CHOICES = [
        (1, '1 - Needs Improvement'),
        (2, '2 - Below Expectations'),
        (3, '3 - Meets Expectations'),
        (4, '4 - Exceeds Expectations'),
        (5, '5 - Outstanding'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('acknowledged', 'Acknowledged by Employee'),
    ]

    employee   = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='performance_reviews')
    reviewer   = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reviews_given',
        help_text="Usually the employee's reporting manager."
    )
    review_period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='quarterly')
    period_start = models.DateField()
    period_end   = models.DateField()

    overall_rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    goals_achieved        = models.TextField(blank=True, help_text="Key goals/targets achieved in this period.")
    strengths              = models.TextField(blank=True)
    areas_of_improvement   = models.TextField(blank=True)
    reviewer_comments      = models.TextField(blank=True)
    employee_comments      = models.TextField(blank=True, help_text="Employee's self-remarks / acknowledgement notes.")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-period_end', '-created_at']

    def __str__(self):
        return f"{self.employee.full_name} — {self.get_review_period_type_display()} ({self.period_start} to {self.period_end})"


class PerformanceGoal(models.Model):
    """
    Individual, trackable goal/KPI tied to a performance review — lets
    a manager set a target and record how much of it was achieved.
    """
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('missed', 'Missed'),
    ]

    review = models.ForeignKey(PerformanceReview, on_delete=models.CASCADE, related_name='goals')
    title  = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_value    = models.CharField(max_length=100, blank=True, help_text="e.g. '95% attendance', '10 modules'")
    achieved_value  = models.CharField(max_length=100, blank=True)
    weightage       = models.PositiveSmallIntegerField(default=0, help_text="% weight of this goal in the overall rating (0-100).")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.title} ({self.review.employee.full_name})"