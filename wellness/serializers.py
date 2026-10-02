from rest_framework import serializers
from .models import WellnessResource


class WellnessResourceSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = WellnessResource
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'resource_url', 'duration_minutes', 'is_active',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by']