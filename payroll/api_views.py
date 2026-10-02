from rest_framework import viewsets
from .models import SalaryStructure, Payslip, SalaryComponent
from .serializers import SalaryStructureSerializer, PayslipSerializer, SalaryComponentSerializer


class SalaryStructureViewSet(viewsets.ModelViewSet):
    queryset = SalaryStructure.objects.select_related('employee').all()
    serializer_class = SalaryStructureSerializer


class PayslipViewSet(viewsets.ModelViewSet):
    queryset = Payslip.objects.select_related('employee').all()
    serializer_class = PayslipSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        employee = self.request.query_params.get('employee')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if employee:
            qs = qs.filter(employee_id=employee)
        if month and year:
            qs = qs.filter(month=month, year=year)
        return qs
