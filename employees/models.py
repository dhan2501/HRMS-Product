# from django.db import models
# from django.contrib.auth.models import User


# class Department(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     code = models.CharField(max_length=10, unique=True)
#     description = models.TextField(blank=True)
#     manager = models.ForeignKey(
#         'Employee', on_delete=models.SET_NULL, null=True, blank=True,
#         related_name='managed_department'
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name

#     class Meta:
#         ordering = ['name']


# class Designation(models.Model):
#     title = models.CharField(max_length=100, unique=True)
#     department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='designations')
#     level = models.PositiveSmallIntegerField(default=1)  # 1=junior, 5=senior

#     def __str__(self):
#         return f"{self.title} ({self.department.name})"

#     class Meta:
#         ordering = ['title']


# class Employee(models.Model):
#     GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
#     STATUS_CHOICES = [
#         ('active', 'Active'),
#         ('inactive', 'Inactive'),
#         ('on_leave', 'On Leave'),
#         ('terminated', 'Terminated'),
#     ]
#     EMPLOYMENT_TYPE = [
#         ('full_time', 'Full Time'),
#         ('part_time', 'Part Time'),
#         ('contract', 'Contract'),
#         ('intern', 'Intern'),
#     ]

#     user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
#     employee_id = models.CharField(max_length=20, unique=True)
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     email = models.EmailField(unique=True)
#     phone = models.CharField(max_length=15, blank=True)
#     date_of_birth = models.DateField(null=True, blank=True)
#     gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
#     photo = models.ImageField(upload_to='employee_photos/', null=True, blank=True)
#     department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
#     designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, related_name='employees')
#     date_joined = models.DateField()
#     employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE, default='full_time')
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
#     address = models.TextField(blank=True)
#     emergency_contact_name = models.CharField(max_length=100, blank=True)
#     emergency_contact_phone = models.CharField(max_length=15, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     @property
#     def full_name(self):
#         return f"{self.first_name} {self.last_name}"

#     def __str__(self):
#         return f"{self.employee_id} - {self.full_name}"

#     class Meta:
#         ordering = ['first_name', 'last_name']



# # Existing models ke neeche add karo

# class EmployeeRole(models.Model):
#     """Defines what access each department/designation has."""
#     ROLE_CHOICES = [
#         ('hr_manager', 'HR Manager'),
#         ('ceo', 'CEO'),
#         ('pmo', 'Product Manager Officer'),
#         ('team_leader', 'Team Leader'),
#         ('employee', 'Employee'),
#     ]
#     employee    = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='role')
#     role        = models.CharField(max_length=30, choices=ROLE_CHOICES, default='employee')
#     can_approve_leave    = models.BooleanField(default=False)
#     can_approve_wfh      = models.BooleanField(default=False)
#     can_view_team_salary = models.BooleanField(default=False)
#     can_assign_project   = models.BooleanField(default=False)
#     manages_department   = models.ForeignKey(
#         'Department', on_delete=models.SET_NULL,
#         null=True, blank=True, related_name='managers'
#     )

#     def __str__(self):
#         return f"{self.employee.full_name} - {self.role}"


# class Project(models.Model):
#     STATUS_CHOICES = [
#         ('planning', 'Planning'),
#         ('active', 'Active'),
#         ('on_hold', 'On Hold'),
#         ('completed', 'Completed'),
#     ]
#     name        = models.CharField(max_length=200)
#     code        = models.CharField(max_length=20, unique=True)
#     description = models.TextField(blank=True)
#     department  = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, related_name='projects')
#     manager     = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='managed_projects')
#     members     = models.ManyToManyField(Employee, related_name='projects', blank=True)
#     start_date  = models.DateField()
#     end_date    = models.DateField(null=True, blank=True)
#     status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
#     created_at  = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.code} - {self.name}"

#     class Meta:
#         ordering = ['-created_at']


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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"

    class Meta:
        ordering = ['first_name', 'last_name']



# Existing models ke neeche add karo

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