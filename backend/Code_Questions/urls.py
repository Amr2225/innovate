from django.urls import path
from .views import (
    CodingQuestionListView,
    CodingQuestionDetailView,
    CodeSubmissionView,
    CodequestionScoreListView
)

urlpatterns = [
    path('questions/', CodingQuestionListView.as_view(), name='question-list'),
    path('questions/<int:pk>/', CodingQuestionDetailView.as_view(), name='question-detail'),
    path('questions/<str:question_id>/submit/', CodeSubmissionView.as_view(), name='submit-code'),
    path('score', CodequestionScoreListView.as_view(), name='quesiton-score')
]
