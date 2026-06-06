from rest_framework import viewsets, filters
from .models import AttendanceRecord, Holiday
from .serializers import AttendanceSerializer, HolidaySerializer


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.select_related('employee').all()
    serializer_class = AttendanceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['employee__first_name', 'employee__last_name']

    def get_queryset(self):
        qs = super().get_queryset()
        date = self.request.query_params.get('date')
        employee = self.request.query_params.get('employee')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if date:
            qs = qs.filter(date=date)
        if employee:
            qs = qs.filter(employee_id=employee)
        if month and year:
            qs = qs.filter(date__month=month, date__year=year)
        return qs


class HolidayViewSet(viewsets.ModelViewSet):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
