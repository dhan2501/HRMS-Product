from django.contrib import admin
from .models import JobOpening, Candidate, Interview

@admin.register(JobOpening)
class JobOpeningAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'vacancies', 'status', 'posted_on']

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'job', 'status', 'applied_on']

admin.site.register(Interview)
