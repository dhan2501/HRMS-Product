from django.utils import timezone
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from employees.models import Employee
from .models import ExpenseClaim, ExpenseComment
from .serializers import ExpenseClaimSerializer, ExpenseCommentSerializer


def _hr_employee(request):
    try:
        return Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return None


def _log(expense, action_name, by_employee, comment=''):
    ExpenseComment.objects.create(
        expense=expense, action=action_name, by_employee=by_employee, comment=comment
    )


class ExpenseClaimViewSet(viewsets.ModelViewSet):
    queryset = ExpenseClaim.objects.select_related('employee').all()
    serializer_class = ExpenseClaimSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['employee__first_name', 'employee__last_name', 'description']

    def get_queryset(self):
        qs = super().get_queryset()
        employee = self.request.query_params.get('employee')
        status_param = self.request.query_params.get('status')
        category = self.request.query_params.get('category')
        if employee:
            qs = qs.filter(employee_id=employee)
        if status_param:
            qs = qs.filter(status=status_param)
        if category:
            qs = qs.filter(category=category)
        return qs

    def perform_create(self, serializer):
        claim = serializer.save()
        _log(claim, 'submitted', claim.employee)

    @action(detail=True, methods=['post'])
    def manager_approve(self, request, pk=None):
        claim = self.get_object()
        if claim.status != 'pending_manager':
            return Response({'detail': 'Claim is not pending manager approval.'}, status=400)
        hr_employee = _hr_employee(request)
        claim.status = 'pending_finance'
        claim.manager_reviewed_by = hr_employee
        claim.manager_reviewed_at = timezone.now()
        claim.save()
        _log(claim, 'manager_approved', hr_employee, request.data.get('comment', ''))
        return Response(self.get_serializer(claim).data)

    @action(detail=True, methods=['post'])
    def manager_reject(self, request, pk=None):
        claim = self.get_object()
        if claim.status != 'pending_manager':
            return Response({'detail': 'Claim is not pending manager approval.'}, status=400)
        hr_employee = _hr_employee(request)
        reason = request.data.get('reason', '')
        claim.status = 'rejected'
        claim.rejected_by = hr_employee
        claim.rejected_at = timezone.now()
        claim.rejection_reason = reason
        claim.save()
        _log(claim, 'manager_rejected', hr_employee, reason)
        return Response(self.get_serializer(claim).data)

    @action(detail=True, methods=['post'])
    def finance_approve(self, request, pk=None):
        claim = self.get_object()
        if claim.status != 'pending_finance':
            return Response({'detail': 'Claim is not pending finance approval.'}, status=400)
        hr_employee = _hr_employee(request)
        claim.status = 'approved'
        claim.finance_reviewed_by = hr_employee
        claim.finance_reviewed_at = timezone.now()
        claim.save()
        _log(claim, 'finance_approved', hr_employee, request.data.get('comment', ''))
        return Response(self.get_serializer(claim).data)

    @action(detail=True, methods=['post'])
    def finance_reject(self, request, pk=None):
        claim = self.get_object()
        if claim.status != 'pending_finance':
            return Response({'detail': 'Claim is not pending finance approval.'}, status=400)
        hr_employee = _hr_employee(request)
        reason = request.data.get('reason', '')
        claim.status = 'rejected'
        claim.rejected_by = hr_employee
        claim.rejected_at = timezone.now()
        claim.rejection_reason = reason
        claim.save()
        _log(claim, 'finance_rejected', hr_employee, reason)
        return Response(self.get_serializer(claim).data)

    @action(detail=True, methods=['post'])
    def reimburse(self, request, pk=None):
        claim = self.get_object()
        if claim.status != 'approved':
            return Response({'detail': 'Claim is not approved yet.'}, status=400)
        txn_ref = request.data.get('transaction_reference', '').strip()
        if not txn_ref:
            return Response({'detail': 'transaction_reference is required.'}, status=400)
        hr_employee = _hr_employee(request)
        claim.status = 'reimbursed'
        claim.reimbursed_by = hr_employee
        claim.reimbursed_at = timezone.now()
        claim.transaction_reference = txn_ref
        claim.save()
        _log(claim, 'reimbursed', hr_employee, f'Transaction Ref: {txn_ref}')
        return Response(self.get_serializer(claim).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        claim = self.get_object()
        if claim.status != 'pending_manager':
            return Response({'detail': 'Only claims pending manager approval can be cancelled.'}, status=400)
        claim.status = 'cancelled'
        claim.save()
        _log(claim, 'cancelled', claim.employee)
        return Response(self.get_serializer(claim).data)


class ExpenseCommentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExpenseComment.objects.select_related('by_employee').all()
    serializer_class = ExpenseCommentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        expense = self.request.query_params.get('expense')
        if expense:
            qs = qs.filter(expense_id=expense)
        return qs