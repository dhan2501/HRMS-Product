from django.db import models
from django.contrib.auth.models import User


class PolicyCategory(models.Model):
    """A tab in the Help & Policies section, e.g. 'Leave Policy', 'Code of Conduct'."""
    name        = models.CharField(max_length=100, unique=True)
    icon        = models.CharField(
        max_length=40, default='fa-file-lines',
        help_text="Font Awesome icon class, e.g. 'fa-umbrella-beach', 'fa-scale-balanced'"
    )
    order       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Policy categories'

    def __str__(self):
        return self.name


class PolicyDocument(models.Model):
    """
    A single policy document within a category. The person just uploads a
    PDF or DOCX; the text is auto-extracted on save so nothing needs to be
    retyped, and is shown directly on the Help page (with the original
    file also downloadable).
    """
    category        = models.ForeignKey(PolicyCategory, on_delete=models.CASCADE, related_name='documents')
    title           = models.CharField(max_length=200)
    file            = models.FileField(upload_to='policy_docs/', blank=True, null=True)
    extracted_text  = models.TextField(blank=True)
    extraction_note = models.CharField(max_length=255, blank=True)  # e.g. error message if extraction failed
    notes           = models.TextField(blank=True, help_text="Optional manual summary/notes shown above the extracted text")
    uploaded_by     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.category.name} — {self.title}"

    @property
    def file_ext(self):
        if not self.file:
            return ''
        return self.file.name.rsplit('.', 1)[-1].lower() if '.' in self.file.name else ''