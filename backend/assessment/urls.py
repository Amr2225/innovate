from django.urls import path
from .views import (
    AssessmentListCreateAPIView,
    AssessmentDetailAPIView,
    AssessmentScoreListCreateAPIView,
    AssessmentScoreRetrieveUpdateDestroyAPIView,
    AssessmentQuestionsAPIView,
    StudentGradesAPIView,
    AssessmentAllQuestionsAPIView,
    AssessmentSubmissionAPIView
)

urlpatterns = [
    # Assessment endpoints
    path('', AssessmentListCreateAPIView.as_view(), name='assessment-list-create'),
    path('<uuid:pk>/', AssessmentDetailAPIView.as_view(), name='assessment-detail'),
    path('<uuid:pk>/questions/', AssessmentQuestionsAPIView.as_view(), name='assessment-questions'),
    path('<uuid:pk>/all-questions/', AssessmentAllQuestionsAPIView.as_view(), name='assessment-all-questions'),

    # AssessmentScore endpoints
    path('assessment-scores/', AssessmentScoreListCreateAPIView.as_view(), name='assessment-score-list-create'),
    path('assessment-scores/<uuid:pk>/', AssessmentScoreRetrieveUpdateDestroyAPIView.as_view(), name='assessment-score-detail'),
    
    # Student grades endpoint
    path('student-grades/', StudentGradesAPIView.as_view(), name='student-grades'),

    path('<uuid:pk>/submit/', AssessmentSubmissionAPIView.as_view(), name='assessment-submit'),
]
