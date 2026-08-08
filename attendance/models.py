# from django.db import models
# from employees.models import Employee


# class AttendanceRecord(models.Model):
#     STATUS_CHOICES = [
#         ('present', 'Present'),
#         ('absent', 'Absent'),
#         ('half_day', 'Half Day'),
#         ('late', 'Late'),
#         ('work_from_home', 'Work From Home'),
#         ('holiday', 'Holiday'),
#     ]

#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance')
#     date = models.DateField()
#     check_in = models.TimeField(null=True, blank=True)
#     check_out = models.TimeField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
#     working_hours = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
#     notes = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ['employee', 'date']
#         ordering = ['-date']

#     def __str__(self):
#         return f"{self.employee.full_name} - {self.date} ({self.status})"


# class Holiday(models.Model):
#     name = models.CharField(max_length=100)
#     date = models.DateField(unique=True)
#     is_optional = models.BooleanField(default=False)
#     description = models.TextField(blank=True)

#     class Meta:
#         ordering = ['date']

#     def __str__(self):
#         return f"{self.name} ({self.date})"


# # Existing models ke neeche add karo

# class WorkFromHomeRequest(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#         ('cancelled', 'Cancelled'),
#     ]

#     employee    = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='wfh_requests')
#     date        = models.DateField()
#     reason      = models.TextField()
#     status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
#     approved_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_wfh')
#     approved_at = models.DateTimeField(null=True, blank=True)
#     rejection_reason = models.TextField(blank=True)
#     created_at  = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-created_at']
#         unique_together = ['employee', 'date']

#     def __str__(self):
#         return f"{self.employee.full_name} - WFH {self.date} ({self.status})"

from django.db import models
from employees.models import Employee


# ── Shift Timing (Super Admin configurable) ────────────────────────────────
class ShiftTiming(models.Model):
    """
    A shift template that Super Admin/HR creates once (e.g. 'General Shift
    9-6', 'Night Shift 10-7') and then assigns to employees. Drives the
    expected working hours and the late/grace-time calculation for punches.
    """
    name = models.CharField(max_length=50, unique=True)
    start_time = models.TimeField(help_text="Shift start time, e.g. 09:00")
    end_time = models.TimeField(help_text="Shift end time, e.g. 18:00")
    working_hours = models.DecimalField(
        max_digits=4, decimal_places=2, default=8.00,
        help_text="Expected/standard working hours per day for this shift."
    )
    grace_minutes = models.PositiveIntegerField(
        default=10,
        help_text="Minutes allowed after start_time before a punch-in is marked Late."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.name} ({self.start_time:%H:%M} - {self.end_time:%H:%M})"


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('half_day', 'Half Day'),
        ('late', 'Late'),
        ('work_from_home', 'Work From Home'),
        ('holiday', 'Holiday'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True, help_text="First punch-in of the day.")
    check_out = models.TimeField(null=True, blank=True, help_text="Last punch-out of the day.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    working_hours = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True,
        help_text="Net working hours = (last punch-out - first punch-in) - total break time."
    )
    break_count = models.PositiveIntegerField(default=0, help_text="Number of breaks taken on this date.")
    total_break_minutes = models.PositiveIntegerField(default=0, help_text="Total break time in minutes.")
    is_punched_in = models.BooleanField(default=False, help_text="True while the employee is currently punched in.")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['employee', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} ({self.status})"


class PunchLog(models.Model):
    """
    Raw log of every Punch In / Punch Out click. AttendanceRecord for the
    day is (re)computed from these logs, so breaks (every Out->In cycle
    before the final Out) and total worked hours are always derived from
    the real punch history rather than being edited by hand.
    """
    PUNCH_TYPE_CHOICES = [
        ('in', 'Punch In'),
        ('out', 'Punch Out'),
    ]
    SOURCE_CHOICES = [
        ('web', 'Web / App'),
        ('device', 'Biometric Device'),
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='punch_logs')
    date = models.DateField(help_text="Attendance date this punch belongs to.")
    punch_type = models.CharField(max_length=3, choices=PUNCH_TYPE_CHOICES)
    timestamp = models.DateTimeField()
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='web')
    device_serial = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_punch_type_display()} @ {self.timestamp:%d %b %Y %H:%M}"


# ── Biometric Device Integration ────────────────────────────────────────────
class BiometricDevice(models.Model):
    """
    Represents one physical fingerprint/biometric punch machine. Devices are
    auto-registered the first time they contact the server (ADMS/push
    protocol used by ZKTeco, eSSL and most budget attendance machines).
    """
    serial_number = models.CharField(max_length=50, unique=True)
    name           = models.CharField(max_length=100, blank=True, help_text="e.g. 'Main Gate', 'Office Entrance'")
    location       = models.CharField(max_length=100, blank=True)
    last_seen_at   = models.DateTimeField(null=True, blank=True)
    last_ip        = models.GenericIPAddressField(null=True, blank=True)
    is_active      = models.BooleanField(default=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_seen_at']

    def __str__(self):
        return self.name or self.serial_number


class BiometricRawLog(models.Model):
    """
    Every raw punch event pushed by a biometric device, kept regardless of
    whether it could be matched to an Employee. Lets HR see and fix
    unmapped device-user-IDs, and gives a full audit trail of what the
    hardware actually sent.
    """
    device_user_id = models.CharField(max_length=30, help_text="Raw PIN/User ID from the device.")
    device_serial  = models.CharField(max_length=50, blank=True)
    timestamp      = models.DateTimeField()
    raw_line       = models.CharField(max_length=255, blank=True)
    employee       = models.ForeignKey(
        Employee, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='biometric_raw_logs',
        help_text="Matched employee, if this device_user_id was mapped at the time of push."
    )
    punch_log      = models.ForeignKey(
        PunchLog, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='raw_source'
    )
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        who = self.employee.full_name if self.employee else f"Unmapped PIN {self.device_user_id}"
        return f"{who} @ {self.timestamp:%d %b %Y %H:%M}"


class Holiday(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(unique=True)
    is_optional = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.name} ({self.date})"


class WorkFromHomeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    employee    = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='wfh_requests')
    date        = models.DateField()
    reason      = models.TextField()
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_wfh')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.full_name} - WFH {self.date} ({self.status})"