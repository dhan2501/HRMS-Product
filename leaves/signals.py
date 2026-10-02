from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import LeaveRequest
from . import services


@receiver(pre_save, sender=LeaveRequest)
def _capture_previous_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._previous_status = LeaveRequest.objects.only('status').get(pk=instance.pk).status
        except LeaveRequest.DoesNotExist:
            instance._previous_status = None
    else:
        instance._previous_status = None


@receiver(post_save, sender=LeaveRequest)
def _sync_balance_on_status_change(sender, instance, created, **kwargs):
    previous_status = getattr(instance, '_previous_status', None)
    if created:
        if instance.status != 'approved':
            return
        previous_status = 'pending'
    services.apply_leave_status_change(instance, previous_status)