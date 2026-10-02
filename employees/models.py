from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# How long after the last request we still treat a user as "online".
# Kept generous because presence is refreshed by page/AJAX activity,
# not a permanent socket connection.
ONLINE_THRESHOLD_SECONDS = 90

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

     # ✅ Bank & Government ID details — added by Super Admin at creation time,
    # and from then on can ONLY be updated by the employee themselves
    # (via a dedicated, restricted portal form — see EmployeeBankDetailsForm).
    bank_account_holder_name = models.CharField(max_length=100, blank=True)
    bank_account_number      = models.CharField(max_length=30, blank=True)
    bank_name                = models.CharField(max_length=100, blank=True)
    bank_ifsc_code           = models.CharField(max_length=15, blank=True)
    aadhar_number            = models.CharField(max_length=20, blank=True, help_text="12-digit Aadhaar number")
    pan_number                = models.CharField(max_length=10, blank=True, help_text="10-character PAN")

    # is_primary_admin = models.BooleanField(
    #     default=False,
    #     help_text="Full Access Super Admin — can grant/revoke Super Admin access for others."
    # )

    is_primary_admin = models.BooleanField(
        default=False,
        help_text="Full Access Super Admin — can grant/revoke Super Admin access for others."
    )

    # ✅ Presence tracking — updated on every authenticated request by
    # employees.middleware.UpdateLastSeenMiddleware. Used to show real
    # Online/Offline status in chat instead of a hardcoded label.
    last_seen = models.DateTimeField(
        null=True, blank=True,
        help_text="Last time this employee's account made an authenticated request."
    )

    @property
    def is_online(self):
        """True only if the employee is actually logged in and was recently active."""
        if not self.last_seen:
            return False
        return (timezone.now() - self.last_seen) < timedelta(seconds=ONLINE_THRESHOLD_SECONDS)


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
    def bank_account_masked(self):
        """Shows only the last 4 digits — e.g. •••••••1234."""
        num = self.bank_account_number
        if not num:
            return ''
        return '•' * max(len(num) - 4, 0) + num[-4:]

    @property
    def aadhar_masked(self):
        """Shows only the last 4 digits — e.g. XXXX XXXX 1234."""
        num = self.aadhar_number.replace(' ', '') if self.aadhar_number else ''
        if not num:
            return ''
        return f"XXXX XXXX {num[-4:]}" if len(num) >= 4 else num

    @property
    def pan_masked(self):
        """Shows first 2 and last 2 characters only — e.g. AB••••••XY."""
        num = self.pan_number
        if not num:
            return ''
        if len(num) <= 4:
            return num
        return num[:2] + '•' * (len(num) - 4) + num[-2:]

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


    # ── System Settings (theme, branding) ─────────────────────────────────────────
class SiteSettings(models.Model):
    """
    Singleton row (always pk=1) that controls company branding shown
    across the whole HRMS — logo, primary color, text color.
    """
    company_name  = models.CharField(max_length=150, default="My Company")
    company_code  = models.CharField(max_length=20, blank=True, help_text="Short internal code for the company, e.g. ABC001")
    logo          = models.ImageField(upload_to='company/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default="#4338ca", help_text="Sidebar / buttons / accents. Hex, e.g. #4338ca")
    text_color    = models.CharField(max_length=7, default="#1e293b", help_text="Default heading/body text color. Hex, e.g. #1e293b")
    updated_at    = models.DateTimeField(auto_now=True)
    updated_by    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def save(self, *args, **kwargs):
        self.pk = 1  # force singleton
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # never allow deleting the singleton row

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Site Settings"


# ── Audit Log (who changed what, when) ─────────────────────────────────────────
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create',     'Created'),
        ('update',     'Updated'),
        ('delete',     'Deleted'),
        ('login',      'Login'),
        ('permission', 'Permission Change'),
        ('settings',   'Settings Change'),
    ]

    user        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    employee    = models.ForeignKey('Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    department  = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action      = models.CharField(max_length=20, choices=ACTION_CHOICES, default='update')
    module      = models.CharField(max_length=100, blank=True, help_text="e.g. Employee, Settings, Shift Timing, Superadmin")
    field_name  = models.CharField(max_length=100, blank=True)
    old_value   = models.CharField(max_length=255, blank=True)
    new_value   = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Audit Log"

    def __str__(self):
        return f"{self.user} · {self.get_action_display()} · {self.module} @ {self.timestamp:%d %b %Y %H:%M}"





# ── Announcements (Super Admin broadcast — High/Medium/Low priority) ───────────
class AnnouncementQuerySet(models.QuerySet):
    def active(self):
        """Only announcements that haven't crossed their 24-hour expiry yet."""
        return self.filter(expires_at__gt=timezone.now())

    def cleanup_expired(self):
        """Hard-delete anything past its 24-hour window. Called opportunistically
        from views, and also available for a cron/management-command sweep."""
        return self.filter(expires_at__lte=timezone.now()).delete()


class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('high',   'High'),
        ('medium', 'Medium'),
        ('low',    'Low'),
    ]

    title       = models.CharField(max_length=200)
    message     = models.TextField()
    priority    = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_by  = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='announcements_posted'
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    expires_at  = models.DateTimeField(editable=False)  # auto-set to created_at + 24h

    objects = AnnouncementQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def priority_rank(self):
        return {'high': 0, 'medium': 1, 'low': 2}.get(self.priority, 3)

    def __str__(self):
        return f"[{self.get_priority_display()}] {self.title}"

# employees/models.py — add this BEFORE the "# ── Audit Log" section

class Notification(models.Model):
    """
    Simple in-app notification for an employee — used right now to tell a
    project teammate that someone they work with is on approved leave, but
    generic enough (title/message/link_name) to reuse for other alerts later.
    """
    recipient   = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='notifications')
    title       = models.CharField(max_length=200)
    message     = models.TextField(blank=True)
    link_name   = models.CharField(
        max_length=100, blank=True,
        help_text="Optional Django url name to link this notification to (e.g. 'portal_my_projects')."
    )
    

    announcement = models.ForeignKey(
        'Announcement', on_delete=models.CASCADE, null=True, blank=True, related_name='notifications',
        help_text="If set, clicking this notification opens the announcement in a popup instead of navigating."
    )
    is_read     = models.BooleanField(default=False)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.full_name} · {self.title}"