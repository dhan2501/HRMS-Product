from rest_framework import viewsets, filters
from .models import WellnessResource
from .serializers import WellnessResourceSerializer


class WellnessResourceViewSet(viewsets.ModelViewSet):
    queryset = WellnessResource.objects.all()
    serializer_class = WellnessResourceSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description']

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        is_active = self.request.query_params.get('is_active')
        if category:
            qs = qs.filter(category=category)
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() in ('1', 'true', 'yes'))
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)