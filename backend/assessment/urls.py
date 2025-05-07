from django.urls import path
from .views import (
    AssessmentListCreateAPIView,
    AssessmentDetailAPIView,
    AssessmentScoreListCreateAPIView,
    AssessmentScoreRetrieveUpdateDestroyAPIView,
)

urlpatterns = [
    # Assessment endpoints
    path('', AssessmentListCreateAPIView.as_view(), name='assessment-list-create'),
    path('<uuid:pk>/', AssessmentDetailAPIView.as_view(), name='assessment-detail'),

    # AssessmentScore endpoints
    path('assessment-scores/', AssessmentScoreListCreateAPIView.as_view(), name='assessment-score-list-create'),
    path('assessment-scores/<uuid:pk>/', AssessmentScoreRetrieveUpdateDestroyAPIView.as_view(), name='assessment-score-detail'),
]
