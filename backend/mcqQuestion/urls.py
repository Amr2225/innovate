from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    McqQuestionListCreateAPIView,
    McqQuestionRetrieveUpdateDestroyAPIView,
    SaveGeneratedMCQsView
)

from .ai_views import (
    GenerateMCQsFromTextView,
    GenerateMCQsFromPDFView,
    GenerateMCQsFromLecturesView,
)

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(
        '<uuid:assessment_id>/',
        McqQuestionListCreateAPIView.as_view(),
        name='mcq-question-list-create'
    ),
    path(
        'mcq-questions/<str:pk>/',
        McqQuestionRetrieveUpdateDestroyAPIView.as_view(),
        name='mcq-question-detail'
    ),
    path(
        'assessments/<str:assessment_id>/generate-from-text/',
        GenerateMCQsFromTextView.as_view(),
        name='mcq-generate-from-text'
    ),
    path(
        'assessments/<str:assessment_id>/generate-from-pdf/',
        GenerateMCQsFromPDFView.as_view(),
        name='mcq-generate-from-pdf'
    ),
    path(
        'generate-from-lectures/',
        GenerateMCQsFromLecturesView.as_view(),
        name='mcq-generate-from-lectures'
    ),
    path(
        'save-generated-mcqs/<uuid:assessment_id>/',
        SaveGeneratedMCQsView.as_view(),
        name='save-generated-mcqs'
    ),
]
