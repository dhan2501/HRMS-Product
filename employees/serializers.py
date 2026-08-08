from rest_framework import serializers
from .models import Employee, Department, Designation


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'employee_count', 'created_at']

    def get_employee_count(self, obj):
        return obj.employees.filter(status='active').count()


class DesignationSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Designation
        fields = ['id', 'title', 'department', 'department_name', 'level']


class EmployeeListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    designation_title = serializers.CharField(source='designation.title', read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'first_name', 'last_name',
            'email', 'phone', 'department', 'department_name',
            'designation', 'designation_title', 'status', 'employment_type',
            'date_joined', 'photo'
        ]


# class EmployeeDetailSerializer(serializers.ModelSerializer):
#     department_name = serializers.CharField(source='department.name', read_only=True)
#     designation_title = serializers.CharField(source='designation.title', read_only=True)
#     full_name = serializers.ReadOnlyField()

#     class Meta:
#         model = Employee
#         fields = '__all__'
#         extra_kwargs = {'user': {'read_only': True}}


class EmployeeDetailSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    designation_title = serializers.CharField(source='designation.title', read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Employee
        # NOTE: bank_account_number, aadhar_number, and pan_number are
        # deliberately excluded — these are sensitive and must never be
        # exposed unmasked over this general-purpose API. They're only
        # ever read/written through the dedicated, permission-scoped
        # admin form and the employee's own restricted portal form.
        exclude = ['bank_account_number', 'aadhar_number', 'pan_number']
        extra_kwargs = {'user': {'read_only': True}}