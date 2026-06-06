from django.db import models
from employees.models import Employee


class SalaryComponent(models.Model):
    COMPONENT_TYPE = [
        ('earning', 'Earning'),
        ('deduction', 'Deduction'),
    ]
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPE)
    is_taxable = models.BooleanField(default=True)
    is_fixed = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.component_type})"


class SalaryStructure(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='salary_structure')
    basic = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pf_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    effective_from = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def gross_salary(self):
        return self.basic + self.hra + self.special_allowance

    @property
    def net_salary(self):
        return self.gross_salary - self.pf_deduction - self.professional_tax

    def __str__(self):
        return f"{self.employee.full_name} - ₹{self.gross_salary}"


class Payslip(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('generated', 'Generated'), ('paid', 'Paid')]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payslips')
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    basic = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pf_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tds = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lop_days = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    lop_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    payment_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['employee', 'month', 'year']
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.employee.full_name} - {self.month}/{self.year}"
