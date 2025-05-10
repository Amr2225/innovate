from django.urls import path
from .views import (
    CodingQuestionListView,
    CodingQuestionDetailView,
    CodeSubmissionView,
)

urlpatterns = [
    path('questions/', CodingQuestionListView.as_view(), name='question-list'),
    path('questions/<int:pk>/', CodingQuestionDetailView.as_view(), name='question-detail'),
    path('questions/<str:question_id>/submit/', CodeSubmissionView.as_view(), name='submit-code'),
]
