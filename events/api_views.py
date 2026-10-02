from django.utils import timezone
from rest_framework import viewsets, filters
from .models import Event
from .serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        qs = super().get_queryset()
        event_type = self.request.query_params.get('event_type')
        upcoming = self.request.query_params.get('upcoming')
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        if event_type:
            qs = qs.filter(event_type=event_type)
        if upcoming and upcoming.lower() in ('1', 'true', 'yes'):
            qs = qs.filter(date__gte=timezone.now().date())
        if year:
            qs = qs.filter(date__year=year)
        if month:
            qs = qs.filter(date__month=month)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)