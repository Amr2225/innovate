from django.urls import path
from .views import (
    CodingQuestionListView,
    CodingQuestionDetailView,
    # CodeSubmissionView,
    # CodequestionScoreListView
    GenerateCodingQuestionsView,
    GenerateCodingContextQuestionsView,
    TestCaseCreateView,
    CodingQuestionDeleteView
)

urlpatterns = [
    path('questions/', CodingQuestionListView.as_view(), name='question-list'),
    path('questions/<uuid:id>/', CodingQuestionDetailView.as_view(), name='question-detail'),
    # path('questions/<str:question_id>/submit/', CodeSubmissionView.as_view(), name='submit-code'),
    # path('score', CodequestionScoreListView.as_view(), name='quesiton-score')
    path('ai/questions/', GenerateCodingQuestionsView.as_view(), name='generate-questions'),
    path('ai/questions/context/', GenerateCodingContextQuestionsView.as_view(), name='generate-context-questions'),
    path('test-cases/', TestCaseCreateView.as_view(), name='test-case-create'),
    path('questions/delete/<uuid:question_id>/', CodingQuestionDeleteView.as_view(), name='delete-question')
]
