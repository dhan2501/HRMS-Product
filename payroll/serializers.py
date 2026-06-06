from rest_framework import serializers
from .models import SalaryStructure, Payslip, SalaryComponent


class SalaryComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryComponent
        fields = '__all__'


class SalaryStructureSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    gross_salary = serializers.ReadOnlyField()
    net_salary = serializers.ReadOnlyField()

    class Meta:
        model = SalaryStructure
        fields = '__all__'


class PayslipSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = Payslip
        fields = '__all__'
