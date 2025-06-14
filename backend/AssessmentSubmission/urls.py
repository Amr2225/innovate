from django.urls import path
from .views import AssessmentSubmissionAPIView

urlpatterns = [
    path('<uuid:assessmentId>/', AssessmentSubmissionAPIView.as_view(),
         name='assessment-submission'),
]
