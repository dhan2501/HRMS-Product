# from django.db import models
# from employees.models import Employee


# class SalaryComponent(models.Model):
#     COMPONENT_TYPE = [
#         ('earning', 'Earning'),
#         ('deduction', 'Deduction'),
#     ]
#     name = models.CharField(max_length=100, unique=True)
#     code = models.CharField(max_length=20, unique=True)
#     component_type = models.CharField(max_length=20, choices=COMPONENT_TYPE)
#     is_taxable = models.BooleanField(default=True)
#     is_fixed = models.BooleanField(default=True)
#     description = models.TextField(blank=True)

#     def __str__(self):
#         return f"{self.name} ({self.component_type})"


# class SalaryStructure(models.Model):
#     employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='salary_structure')
#     basic = models.DecimalField(max_digits=10, decimal_places=2)
#     hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     pf_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     effective_from = models.DateField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     @property
#     def gross_salary(self):
#         return self.basic + self.hra + self.special_allowance

#     @property
#     def net_salary(self):
#         return self.gross_salary - self.pf_deduction - self.professional_tax

#     def __str__(self):
#         return f"{self.employee.full_name} - ₹{self.gross_salary}"


# class Payslip(models.Model):
#     STATUS_CHOICES = [('draft', 'Draft'), ('generated', 'Generated'), ('paid', 'Paid')]

#     employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payslips')
#     month = models.PositiveSmallIntegerField()
#     year = models.PositiveSmallIntegerField()
#     basic = models.DecimalField(max_digits=10, decimal_places=2)
#     hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     pf_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     tds = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     lop_days = models.DecimalField(max_digits=4, decimal_places=1, default=0)
#     lop_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     gross_salary = models.DecimalField(max_digits=10, decimal_places=2)
#     net_salary = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
#     payment_date = models.DateField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ['employee', 'month', 'year']
#         ordering = ['-year', '-month']

#     def __str__(self):
#         return f"{self.employee.full_name} - {self.month}/{self.year}"


from django.db import models
from employees.models import Employee
from .tax_utils import calculate_tax


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
    TAX_REGIME_CHOICES = [
        ('new', 'New Regime'),
        ('old', 'Old Regime'),
    ]

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='salary_structure')
    basic = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    special_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pf_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # ── Taxation Policy ────────────────────────────────────────────────
    tax_regime = models.CharField(max_length=10, choices=TAX_REGIME_CHOICES, default='new')
    deduction_80c = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text='Section 80C investments (PF, ELSS, LIC, etc.) — applicable under Old Regime only.'
    )
    deduction_80d = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text='Section 80D health insurance premium — applicable under Old Regime only.'
    )

    effective_from = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def gross_salary(self):
        return self.basic + self.hra + self.special_allowance

    @property
    def annual_gross_salary(self):
        return self.gross_salary * 12

    @property
    def tax_breakup(self):
        """Full annual tax breakup as per the employee's chosen tax regime."""
        return calculate_tax(
            regime=self.tax_regime,
            annual_gross=self.annual_gross_salary,
            deduction_80c=self.deduction_80c,
            deduction_80d=self.deduction_80d,
            professional_tax_annual=self.professional_tax * 12,
        )

    @property
    def monthly_tds(self):
        return self.tax_breakup['monthly_tds']

    @property
    def net_salary(self):
        return self.gross_salary - self.pf_deduction - self.professional_tax - self.monthly_tds

    def __str__(self):
        return f"{self.employee.full_name} - ₹{self.gross_salary}"


class Payslip(models.Model):
    STATUS_CHOICES = [('draft', 'Draft'), ('generated', 'Generated'), ('paid', 'Paid')]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payslips')
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField()
    tax_regime = models.CharField(
        max_length=10,
        choices=[('new', 'New Regime'), ('old', 'Old Regime')],
        default='new',
    )
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