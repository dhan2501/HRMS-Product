from django.contrib import admin
from .models import PolicyCategory, PolicyDocument


@admin.register(PolicyCategory)
class PolicyCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'order')
    ordering = ('order',)


@admin.register(PolicyDocument)
class PolicyDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_by', 'updated_at')
    list_filter = ('category',)