from django.db import models
from employees.models import Department, Designation


class JobOpening(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('on_hold', 'On Hold'),
        ('filled', 'Filled'),
    ]
    EXPERIENCE_LEVEL = [
        ('fresher', 'Fresher'),
        ('junior', '1-3 Years'),
        ('mid', '3-5 Years'),
        ('senior', '5+ Years'),
    ]

    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True)
    vacancies = models.PositiveSmallIntegerField(default=1)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL)
    description = models.TextField()
    requirements = models.TextField()
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    deadline = models.DateField(null=True, blank=True)
    posted_on = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.department.name}"


class Candidate(models.Model):
    APPLICATION_STATUS = [
        ('applied', 'Applied'),
        ('screening', 'Screening'),
        ('interview', 'Interview Scheduled'),
        ('offer', 'Offer Extended'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    job = models.ForeignKey(JobOpening, on_delete=models.CASCADE, related_name='candidates')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    years_of_experience = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    current_company = models.CharField(max_length=200, blank=True)
    current_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='applied')
    notes = models.TextField(blank=True)
    applied_on = models.DateTimeField(auto_now_add=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} - {self.job.title}"


class Interview(models.Model):
    INTERVIEW_TYPE = [
        ('phone', 'Phone Screening'),
        ('technical', 'Technical Round'),
        ('hr', 'HR Round'),
        ('final', 'Final Round'),
    ]
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='interviews')
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveSmallIntegerField(default=60)
    interviewer = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1-5
    feedback = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_at']

    def __str__(self):
        return f"{self.candidate.full_name} - {self.interview_type} ({self.scheduled_at.date()})"
