from django.urls import path
from . import views
from .views import MCQQuestionListCreateView, SubmitAssessmentAnswersView

urlpatterns = [
    path(
        'assessments/<str:assessment_id>/mcq-questions/',
        views.McqQuestionListCreateAPIView.as_view(),
        name='mcq-question-list-create'
    ),
    path(
        'mcq-questions/<str:pk>/',
        views.McqQuestionRetrieveUpdateDestroyAPIView.as_view(),
        name='mcq-question-detail'
    ),
    path(
        'generate-mcqs/',
        views.GenerateMCQsView.as_view(),
        name='mcq-generate'
    ),
    path('', MCQQuestionListCreateView.as_view(), name='mcq-question-list-create'),
    path('assessment/<uuid:assessment_id>/submit/', SubmitAssessmentAnswersView.as_view(), name='submit-assessment-answers'),
]
