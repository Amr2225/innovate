from django.urls import path
from .views import AssessmentSubmissionAPIView

urlpatterns = [
    path('<uuid:pk>/', AssessmentSubmissionAPIView.as_view(), name='assessment-submission'),
] 