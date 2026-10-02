from rest_framework import serializers
from .models import PolicyCategory, PolicyDocument


class PolicyDocumentSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    file_ext = serializers.ReadOnlyField()
    uploaded_by_name = serializers.CharField(source='uploaded_by.get_full_name', read_only=True)

    class Meta:
        model = PolicyDocument
        fields = [
            'id', 'category', 'category_name', 'title', 'file', 'file_ext',
            'extracted_text', 'extraction_note', 'notes',
            'uploaded_by', 'uploaded_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['extracted_text', 'extraction_note', 'uploaded_by']


class PolicyCategorySerializer(serializers.ModelSerializer):
    document_count = serializers.SerializerMethodField()

    class Meta:
        model = PolicyCategory
        fields = ['id', 'name', 'icon', 'order', 'document_count', 'created_at']

    def get_document_count(self, obj):
        return obj.documents.count()