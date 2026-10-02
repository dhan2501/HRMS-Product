from rest_framework import viewsets, filters
from .models import JobOpening, Candidate, Interview
from .serializers import JobOpeningSerializer, CandidateSerializer, InterviewSerializer


class JobOpeningViewSet(viewsets.ModelViewSet):
    queryset = JobOpening.objects.select_related('department').all()
    serializer_class = JobOpeningSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'department__name']


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.select_related('job').all()
    serializer_class = CandidateSerializer


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.select_related('candidate').all()
    serializer_class = InterviewSerializer
