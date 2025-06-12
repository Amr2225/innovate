from django.urls import path
from .views import (
    GenerateCodingQuestionsView,
    SubmitCodingAnswerView,
    CodingQuestionListView,
    CodingQuestionDetailView
)

urlpatterns = [
    path('generate/', GenerateCodingQuestionsView.as_view(), name='generate-coding-questions'),
    path('submit/<uuid:question_id>/', SubmitCodingAnswerView.as_view(), name='submit-coding-answer'),
    path('list/', CodingQuestionListView.as_view(), name='coding-question-list'),
    path('detail/<uuid:pk>/', CodingQuestionDetailView.as_view(), name='coding-question-detail'),
] 