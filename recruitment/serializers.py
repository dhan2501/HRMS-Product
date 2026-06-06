from rest_framework import serializers
from .models import JobOpening, Candidate, Interview


class JobOpeningSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    candidate_count = serializers.SerializerMethodField()

    class Meta:
        model = JobOpening
        fields = '__all__'

    def get_candidate_count(self, obj):
        return obj.candidates.count()


class CandidateSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Candidate
        fields = '__all__'


class InterviewSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)

    class Meta:
        model = Interview
        fields = '__all__'
