from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee, Department, Designation
from .serializers import EmployeeListSerializer, EmployeeDetailSerializer, DepartmentSerializer, DesignationSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code']


class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.select_related('department').all()
    serializer_class = DesignationSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('department', 'designation').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'employee_id']
    ordering_fields = ['first_name', 'date_joined', 'department']

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeDetailSerializer

    @action(detail=False, methods=['get'])
    def active(self, request):
        active = Employee.objects.filter(status='active')
        serializer = EmployeeListSerializer(active, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        from attendance.models import AttendanceRecord
        from datetime import date
        employee = self.get_object()
        month = request.query_params.get('month', date.today().month)
        year = request.query_params.get('year', date.today().year)
        records = AttendanceRecord.objects.filter(employee=employee, date__month=month, date__year=year)
        summary = {
            'present': records.filter(status='present').count(),
            'absent': records.filter(status='absent').count(),
            'late': records.filter(status='late').count(),
            'half_day': records.filter(status='half_day').count(),
            'wfh': records.filter(status='work_from_home').count(),
        }
        return Response(summary)
