from rest_framework import viewsets, filters

from .extraction import extract_text_from_file
from .models import PolicyCategory, PolicyDocument
from .serializers import PolicyCategorySerializer, PolicyDocumentSerializer


class PolicyCategoryViewSet(viewsets.ModelViewSet):
    queryset = PolicyCategory.objects.all()
    serializer_class = PolicyCategorySerializer


class PolicyDocumentViewSet(viewsets.ModelViewSet):
    queryset = PolicyDocument.objects.select_related('category').all()
    serializer_class = PolicyDocumentSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'notes']

    def get_queryset(self):
        qs = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)
        return qs

    def _extract_and_save(self, serializer):
        uploaded_file = self.request.FILES.get('file')
        extracted_text, note = '', ''
        if uploaded_file:
            extracted_text, note = extract_text_from_file(uploaded_file)
        serializer.save(
            uploaded_by=self.request.user,
            extracted_text=extracted_text,
            extraction_note=note,
        )

    def perform_create(self, serializer):
        self._extract_and_save(serializer)

    def perform_update(self, serializer):
        if self.request.FILES.get('file'):
            self._extract_and_save(serializer)
        else:
            serializer.save()