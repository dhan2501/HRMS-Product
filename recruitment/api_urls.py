from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'job-openings', api_views.JobOpeningViewSet)
router.register(r'candidates', api_views.CandidateViewSet)
router.register(r'interviews', api_views.InterviewViewSet)
urlpatterns = router.urls
